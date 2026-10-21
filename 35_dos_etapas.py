#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - H15 (PREREGISTRO_H15.md, E12): detector de dos etapas, Faster R-CNN (ResNet-50 FPN v2, torchvision).

Entrenamiento: el MISMO cargador de Ultralytics que el resto del proyecto (ExDark-People train de data_v2.yaml,
aumento base de config/aumento_base.yaml, mosaico con cierre en las ultimas 10 epocas) y, en V3, el MISMO
generador de siluetas v2 (argos_lib.siluetas.OclusionSiluetas con OCLUSION_CFG_V2 de 07_entrenar.py). Solo cambia
el detector. V1 y V3 se entrenan exactamente 30 epocas, sin validacion ni parada temprana, y se evaluan con los
pesos de la ultima epoca, como en H9b, H10, H12 y H14.

Inferencia: escribe la cache de detecciones en el formato de 09_evaluar_estratificado.py
(resultados_h15/det/<nombre>__<conjunto>.json), con el mismo umbral de confianza (0,001), max_det 300 y lado
mayor 640. Despues 09_ se ejecuta con el mismo --pesos y --nombre: encuentra la cache y solo evalua.

Uso:
  python 35_dos_etapas.py entrenar --variante V1|V3 --semilla 0 [--epochs 30] [--smoke]
  python 35_dos_etapas.py inferir --pesos runs\\argos_frcnn\\V1_s0\\weights\\last.pth --nombre V1_s0 --gt <gt_*.json ...>
  python 35_dos_etapas.py --selftest
"""
import argparse
import importlib.util
import json
import math
import os
import random
import sys
import time

import numpy as np

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
PESOS_COCO = os.path.join(RAIZ, "fasterrcnn_resnet50_fpn_v2_coco.pth")
PROYECTO = os.path.join(RAIZ, "runs", "argos_frcnn")
# Receta fijada antes de entrenar (PREREGISTRO_H15.md, seccion 1): la de referencia de torchvision para ajuste fino
# de Faster R-CNN (SGD, lr 0,02 para lote 16 -> 0,01 para lote 8, momento 0,9, decaimiento 1e-4, calentamiento
# lineal y decaimiento x0,1 en dos hitos), con 30 epocas y los hitos 20 y 27 (proporcion de la receta 26/16/22).
RECETA = {"epochs": 30, "batch": 8, "lr": 0.01, "momentum": 0.9, "weight_decay": 1e-4, "warmup_iters": 500,
          "warmup_factor": 1e-3, "hitos": (20, 27), "gamma": 0.1, "imgsz": 640, "workers": 8, "amp": True}
CONF, MAX_DET, NMS = 0.001, 300, 0.5      # NMS por clase de torchvision (0,5, su valor por defecto)


def _cargar_07():
    sp = importlib.util.spec_from_file_location("entrenar07", os.path.join(RAIZ, "07_entrenar.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def construir_modelo(pesos_coco=PESOS_COCO):
    """Faster R-CNN ResNet-50 FPN v2 preentrenado en COCO; la cabeza de clasificacion se sustituye por una de dos
    clases (fondo y persona). Entrada redimensionada con el lado mayor a 640 (min_size = max_size = 640)."""
    import torch
    from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2
    from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
    m = fasterrcnn_resnet50_fpn_v2(weights=None, weights_backbone=None, min_size=RECETA["imgsz"],
                                   max_size=RECETA["imgsz"], box_score_thresh=CONF, box_nms_thresh=NMS,
                                   box_detections_per_img=MAX_DET)
    if pesos_coco:
        m.load_state_dict(torch.load(pesos_coco, map_location="cpu", weights_only=True))
    m.roi_heads.box_predictor = FastRCNNPredictor(m.roi_heads.box_predictor.cls_score.in_features, 2)
    return m


def dataset_ultralytics(variante, semilla, fraccion=1.0):
    """Dataset de entrenamiento de Ultralytics con el aumento base del proyecto; en V3, con el generador de
    siluetas v2 (el de E2, E8 y H12a)."""
    import yaml
    from ultralytics.cfg import get_cfg
    from ultralytics.data.utils import check_det_dataset
    from ultralytics.utils import colorstr
    from argos_lib.entrenamiento import DatasetOclusion
    from argos_lib.siluetas import OclusionSiluetas
    e07 = _cargar_07()
    aum = yaml.safe_load(open(os.path.join(RAIZ, "config", "aumento_base.yaml"), encoding="utf-8"))
    cfg = get_cfg(overrides=dict(imgsz=RECETA["imgsz"], seed=semilla, **aum))
    data = check_det_dataset(os.path.join(RAIZ, "dataset", "data_v2.yaml"))
    ocl = OclusionSiluetas(**e07.OCLUSION_CFG_V2) if variante == "V3" else None
    return DatasetOclusion(img_path=data["train"], imgsz=RECETA["imgsz"], batch_size=RECETA["batch"], augment=True,
                           hyp=cfg, rect=False, cache=None, single_cls=False, stride=32, pad=0.0,
                           prefix=colorstr("train: "), task="detect", classes=None, data=data, fraction=fraccion,
                           oclusion=ocl), cfg


def objetivos(batch, device):
    """Lote de Ultralytics -> listas de imagenes (RGB, 0-1) y objetivos de torchvision (cajas xyxy en pixeles)."""
    import torch
    imgs = batch["img"].to(device, non_blocking=True).float() / 255.0
    _, _, h, w = imgs.shape
    out = []
    for i in range(imgs.shape[0]):
        sel = batch["batch_idx"] == i
        b = batch["bboxes"][sel].to(device)
        xyxy = torch.stack([(b[:, 0] - b[:, 2] / 2) * w, (b[:, 1] - b[:, 3] / 2) * h,
                            (b[:, 0] + b[:, 2] / 2) * w, (b[:, 1] + b[:, 3] / 2) * h], 1) if len(b) else torch.zeros((0, 4), device=device)
        ok = ((xyxy[:, 2] - xyxy[:, 0]) > 1) & ((xyxy[:, 3] - xyxy[:, 1]) > 1)
        xyxy = xyxy[ok]
        out.append({"boxes": xyxy, "labels": torch.ones(len(xyxy), dtype=torch.int64, device=device)})
    return list(imgs), out


def fijar_semilla(s):
    import torch
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)
    torch.backends.cudnn.benchmark = False


def entrenar(variante, semilla, epochs=None, smoke=False, device="cuda"):
    import torch
    from ultralytics.data import build_dataloader
    epochs = 1 if smoke else (epochs or RECETA["epochs"])
    nombre = "%s_s%d%s" % (variante, semilla, "_smoke" if smoke else "")
    d = os.path.join(PROYECTO if not smoke else os.path.join(RAIZ, "runs", "smoke_frcnn"), nombre)
    if os.path.exists(os.path.join(d, "weights", "last.pth")) and not smoke:
        print("[omitida] %s ya terminada" % d)
        return d
    os.makedirs(os.path.join(d, "weights"), exist_ok=True)
    fijar_semilla(semilla)
    ds, cfg = dataset_ultralytics(variante, semilla, fraccion=0.05 if smoke else 1.0)
    dl = build_dataloader(ds, RECETA["batch"], 2 if smoke else RECETA["workers"], shuffle=True, rank=-1)
    modelo = construir_modelo().to(device)
    params = [p for p in modelo.parameters() if p.requires_grad]
    opt = torch.optim.SGD(params, lr=RECETA["lr"], momentum=RECETA["momentum"], weight_decay=RECETA["weight_decay"])
    nb = len(dl)
    hitos = [h * nb for h in RECETA["hitos"]]

    def factor(it):
        f = RECETA["gamma"] ** sum(it >= h for h in hitos)
        if it < RECETA["warmup_iters"]:
            a = it / RECETA["warmup_iters"]
            f *= RECETA["warmup_factor"] * (1 - a) + a
        return f
    sched = torch.optim.lr_scheduler.LambdaLR(opt, factor)
    scaler = torch.amp.GradScaler("cuda", enabled=RECETA["amp"])
    filas, it, t0 = [], 0, time.time()
    for ep in range(epochs):
        if ep == epochs - int(cfg.close_mosaic) and cfg.close_mosaic and not smoke:
            ds.close_mosaic(hyp=cfg)                      # igual que Ultralytics: sin mosaico en las ultimas 10
            dl.reset()
        modelo.train()
        acum, n = 0.0, 0
        for batch in dl:
            imgs, tg = objetivos(batch, device)
            with torch.autocast("cuda", enabled=RECETA["amp"]):
                perd = modelo(imgs, tg)
                loss = sum(perd.values())
            if not math.isfinite(loss.item()):
                sys.exit("PERDIDA_NO_FINITA en la epoca %d" % ep)
            opt.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            sched.step()
            acum += loss.item(); n += 1; it += 1
            if smoke and n >= 3:
                break
        filas.append({"epoch": ep + 1, "loss": round(acum / max(n, 1), 5), "lr": opt.param_groups[0]["lr"],
                      "time": round(time.time() - t0, 1)})
        print("%s epoca %d/%d  perdida %.4f  lr %.5f  %.0f s" % (nombre, ep + 1, epochs, filas[-1]["loss"],
                                                                 filas[-1]["lr"], filas[-1]["time"]), flush=True)
    torch.save(modelo.state_dict(), os.path.join(d, "weights", "last.pth"))
    with open(os.path.join(d, "results.csv"), "w", encoding="utf-8") as fh:
        fh.write("epoch,loss,lr,time\n" + "".join("%d,%s,%s,%s\n" % (f["epoch"], f["loss"], f["lr"], f["time"]) for f in filas))
    json.dump({"variante": variante, "semilla": semilla, "receta": RECETA, "oclusion_v3": variante == "V3",
               "torch": torch.__version__, "cuda": torch.version.cuda, "gpu": torch.cuda.get_device_name(0),
               "pesos_coco": os.path.basename(PESOS_COCO), "iteraciones": it},
              open(os.path.join(d, "registro_argos.json"), "w", encoding="utf-8"), indent=1)
    return d


def inferir(pesos, nombre, rutas_gt, resultados, device="cuda"):
    import cv2
    import torch
    from argos_lib.gt import cargar_gt, guardar_detecciones
    modelo = construir_modelo(pesos_coco=None)
    modelo.load_state_dict(torch.load(os.path.join(RAIZ, pesos) if not os.path.isabs(pesos) else pesos,
                                      map_location="cpu", weights_only=True))
    modelo.to(device).eval()
    for ruta in rutas_gt:
        gt = cargar_gt(ruta)
        cache = os.path.join(resultados, "det", "%s__%s.json" % (nombre, gt["conjunto"]))
        det, t0 = {}, time.time()
        with torch.no_grad():
            for n in sorted(gt["imagenes"]):
                im = cv2.imread(os.path.join(gt["dir_imagenes"], n))[:, :, ::-1]
                x = torch.from_numpy(np.ascontiguousarray(im)).permute(2, 0, 1).float().div(255).to(device)
                r = modelo([x])[0]
                det[n] = [[float(a), float(b), float(c), float(e), float(s)]
                          for (a, b, c, e), s in zip(r["boxes"].cpu().numpy(), r["scores"].cpu().numpy())]
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        guardar_detecciones(cache, pesos, gt["conjunto"], det, CONF, NMS,
                            extra={"max_det": MAX_DET, "imgsz": RECETA["imgsz"], "detector": "fasterrcnn_resnet50_fpn_v2",
                                   "segundos_inferencia": round(time.time() - t0, 1)})
        print("  %s: %d imagenes, %.0f s" % (gt["conjunto"], len(det), time.time() - t0), flush=True)


def selftest():
    import torch
    ok = []
    m = construir_modelo(pesos_coco=None)
    ok.append(m.roi_heads.box_predictor.cls_score.out_features == 2)
    ok.append(m.transform.min_size == (640,) and m.transform.max_size == 640)
    b = {"img": torch.zeros((2, 3, 640, 640), dtype=torch.uint8), "batch_idx": torch.tensor([0., 0., 1.]),
         "bboxes": torch.tensor([[0.5, 0.5, 0.2, 0.4], [0.1, 0.1, 0.0005, 0.1], [0.5, 0.5, 1.0, 1.0]])}
    _, tg = objetivos(b, "cpu")
    ok.append(len(tg[0]["boxes"]) == 1 and torch.allclose(tg[0]["boxes"][0], torch.tensor([256., 192., 384., 448.])))
    ok.append(tg[1]["boxes"].shape == (1, 4) and int(tg[1]["labels"][0]) == 1)
    hitos = [h * 100 for h in RECETA["hitos"]]
    f = lambda it: RECETA["gamma"] ** sum(it >= h for h in hitos)
    ok.append(f(1999) == 1 and abs(f(2000) - 0.1) < 1e-12 and abs(f(2700) - 0.01) < 1e-12)
    print("AUTOTEST %s: %d/%d" % ("SUPERADO" if all(ok) else "FALLIDO", sum(ok), len(ok)))
    return all(ok)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - H15: Faster R-CNN (dos etapas)")
    ap.add_argument("accion", nargs="?", choices=("entrenar", "inferir"))
    ap.add_argument("--variante", choices=("V1", "V3"))
    ap.add_argument("--semilla", type=int)
    ap.add_argument("--epochs", type=int)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--pesos")
    ap.add_argument("--nombre")
    ap.add_argument("--gt", nargs="+")
    ap.add_argument("--resultados", default=os.path.join(RAIZ, "resultados_h15"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.accion == "entrenar":
        entrenar(a.variante, a.semilla, a.epochs, a.smoke)
    elif a.accion == "inferir":
        inferir(a.pesos, a.nombre, a.gt, a.resultados)
    else:
        ap.error("indicar accion o --selftest")


if __name__ == "__main__":
    main()
