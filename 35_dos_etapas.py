#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Detectores de torchvision (H15, PREREGISTRO_H15.md; H16 y H17, PREREGISTRO_H16_H17.md).

  --detector frcnn   Faster R-CNN ResNet-50 FPN v2 (dos etapas)       [H15, H16]
  --detector retina  RetinaNet ResNet-50 FPN v2 (una etapa, misma columna y misma receta de torchvision)   [H17]
  --familia sil      siluetas v2 (argos_lib.siluetas.OclusionSiluetas, OCLUSION_CFG_V2)   [H15, H17]
  --familia gen      oclusion generativa de H9/H9b (dataset/generativa_train, OCLUSION_CFG_GEN)   [H16a]
  --familia prof     oclusores con orden de profundidad de H14 (dataset/profundidad_train, OCLUSION_CFG_PROF)   [H16b]
Los valores por defecto (frcnn, sil) reproducen exactamente H15.

Entrenamiento: el MISMO cargador de Ultralytics que el resto del proyecto (ExDark-People train de data_v2.yaml,
aumento base de config/aumento_base.yaml, mosaico con cierre en las ultimas 10 epocas) y, en V3, el MISMO generador de
la familia que en los bloques YOLO. V1 y V3 se entrenan exactamente 30 epocas, sin validacion ni parada temprana, y se
evaluan con los pesos de la ultima epoca.

Inferencia: escribe la cache de detecciones en el formato de 09_evaluar_estratificado.py (<resultados>/det/<nombre>__
<conjunto>.json), con confianza minima 0,001, max_det 300 y lado mayor 640. Despues 09_ se ejecuta con el mismo --pesos y
--nombre: encuentra la cache y solo evalua.

Uso:
  python 35_dos_etapas.py entrenar --variante V1|V3 --semilla 0 [--detector frcnn|retina] [--familia sil|gen|prof] [--proyecto argos_frcnn_rep] [--smoke]
  python 35_dos_etapas.py inferir --pesos runs\\argos_frcnn\\V1_s0\\weights\\last.pth --nombre V1_s0 --gt <gt_*.json ...> [--detector ...]
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
PESOS = {"frcnn": os.path.join(RAIZ, "fasterrcnn_resnet50_fpn_v2_coco.pth"),
         "retina": os.path.join(RAIZ, "retinanet_resnet50_fpn_v2_coco.pth")}
PESOS_COCO = PESOS["frcnn"]
PROYECTOS = {("frcnn", "sil"): "argos_frcnn", ("frcnn", "gen"): "argos_frcnn_gen", ("frcnn", "prof"): "argos_frcnn_prof",
             ("retina", "sil"): "argos_retina"}
PROYECTO = os.path.join(RAIZ, "runs", "argos_frcnn")
# Receta fijada antes de entrenar (PREREGISTRO_H15.md, seccion 1): la de referencia de torchvision para ajuste fino
# (SGD, momento 0,9, decaimiento 1e-4, calentamiento lineal y decaimiento x0,1 en dos hitos), con 30 epocas y los hitos
# 20 y 27 (proporcion de la receta 26/16/22). La tasa es la de referencia de cada detector escalada linealmente al lote
# 8: Faster R-CNN 0,02 con lote 16 -> 0,01; RetinaNet 0,01 con lote 16 -> 0,005 (PREREGISTRO_H16_H17.md).
RECETA = {"epochs": 30, "batch": 8, "lr": 0.01, "momentum": 0.9, "weight_decay": 1e-4, "warmup_iters": 500,
          "warmup_factor": 1e-3, "hitos": (20, 27), "gamma": 0.1, "imgsz": 640, "workers": 8, "amp": True}
LR = {"frcnn": 0.01, "retina": 0.005}
CONF, MAX_DET, NMS = 0.001, 300, 0.5      # NMS de torchvision (0,5, su valor por defecto en ambos detectores)


def _cargar_07():
    sp = importlib.util.spec_from_file_location("entrenar07", os.path.join(RAIZ, "07_entrenar.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def construir_modelo(pesos_coco=PESOS_COCO, detector="frcnn"):
    """Detector de torchvision preentrenado en COCO; la cabeza de clasificacion se sustituye por una de dos clases
    (fondo y persona). Entrada redimensionada con el lado mayor a 640 (min_size = max_size = 640)."""
    import torch
    if detector == "frcnn":
        from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2
        from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
        m = fasterrcnn_resnet50_fpn_v2(weights=None, weights_backbone=None, min_size=RECETA["imgsz"],
                                       max_size=RECETA["imgsz"], box_score_thresh=CONF, box_nms_thresh=NMS,
                                       box_detections_per_img=MAX_DET)
        if pesos_coco:
            m.load_state_dict(torch.load(pesos_coco, map_location="cpu", weights_only=True))
        m.roi_heads.box_predictor = FastRCNNPredictor(m.roi_heads.box_predictor.cls_score.in_features, 2)
        return m
    from functools import partial
    from torchvision.models.detection import retinanet_resnet50_fpn_v2
    from torchvision.models.detection.retinanet import RetinaNetClassificationHead
    m = retinanet_resnet50_fpn_v2(weights=None, weights_backbone=None, min_size=RECETA["imgsz"], max_size=RECETA["imgsz"],
                                  score_thresh=CONF, nms_thresh=NMS, detections_per_img=MAX_DET)
    if pesos_coco:
        m.load_state_dict(torch.load(pesos_coco, map_location="cpu", weights_only=True))
    na = m.head.classification_head.num_anchors
    m.head.classification_head = RetinaNetClassificationHead(256, na, 2, norm_layer=partial(torch.nn.GroupNorm, 32))
    return m


def oclusion_de(familia):
    e07 = _cargar_07()
    if familia == "sil":
        from argos_lib.siluetas import OclusionSiluetas
        return OclusionSiluetas(**e07.OCLUSION_CFG_V2)
    from argos_lib.generativa import OclusionGenerativa
    return OclusionGenerativa(**(e07.OCLUSION_CFG_GEN if familia == "gen" else e07.OCLUSION_CFG_PROF))


def dataset_ultralytics(variante, semilla, fraccion=1.0, familia="sil"):
    """Dataset de entrenamiento de Ultralytics con el aumento base del proyecto; en V3, con el generador de la familia."""
    import yaml
    from ultralytics.cfg import get_cfg
    from ultralytics.data.utils import check_det_dataset
    from ultralytics.utils import colorstr
    from argos_lib.entrenamiento import DatasetOclusion
    aum = yaml.safe_load(open(os.path.join(RAIZ, "config", "aumento_base.yaml"), encoding="utf-8"))
    cfg = get_cfg(overrides=dict(imgsz=RECETA["imgsz"], seed=semilla, **aum))
    data = check_det_dataset(os.path.join(RAIZ, "dataset", "data_v2.yaml"))
    ocl = oclusion_de(familia) if variante == "V3" else None
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


def entrenar(variante, semilla, epochs=None, smoke=False, device="cuda", detector="frcnn", familia="sil", proyecto=None):
    import torch
    from ultralytics.data import build_dataloader
    epochs = 1 if smoke else (epochs or RECETA["epochs"])
    nombre = "%s_s%d%s" % (variante, semilla, "_smoke" if smoke else "")
    base = proyecto or os.path.join(RAIZ, "runs", PROYECTOS[(detector, familia)])
    d = os.path.join(base if not smoke else os.path.join(RAIZ, "runs", "smoke_frcnn", PROYECTOS[(detector, familia)]), nombre)
    if os.path.exists(os.path.join(d, "weights", "last.pth")) and not smoke:
        print("[omitida] %s ya terminada" % d)
        return d
    os.makedirs(os.path.join(d, "weights"), exist_ok=True)
    fijar_semilla(semilla)
    ds, cfg = dataset_ultralytics(variante, semilla, fraccion=0.05 if smoke else 1.0, familia=familia)
    dl = build_dataloader(ds, RECETA["batch"], 2 if smoke else RECETA["workers"], shuffle=True, rank=-1)
    modelo = construir_modelo(PESOS[detector], detector).to(device)
    params = [p for p in modelo.parameters() if p.requires_grad]
    opt = torch.optim.SGD(params, lr=LR[detector], momentum=RECETA["momentum"], weight_decay=RECETA["weight_decay"])
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
    json.dump({"variante": variante, "semilla": semilla, "detector": detector, "familia": familia,
               "receta": dict(RECETA, lr=LR[detector]), "oclusion_v3": variante == "V3",
               "torch": torch.__version__, "cuda": torch.version.cuda, "gpu": torch.cuda.get_device_name(0),
               "pesos_coco": os.path.basename(PESOS[detector]), "iteraciones": it},
              open(os.path.join(d, "registro_argos.json"), "w", encoding="utf-8"), indent=1)
    return d


def inferir(pesos, nombre, rutas_gt, resultados, device="cuda", detector="frcnn"):
    import cv2
    import torch
    from argos_lib.gt import cargar_gt, guardar_detecciones
    modelo = construir_modelo(pesos_coco=None, detector=detector)
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
                            extra={"max_det": MAX_DET, "imgsz": RECETA["imgsz"],
                                   "detector": {"frcnn": "fasterrcnn_resnet50_fpn_v2", "retina": "retinanet_resnet50_fpn_v2"}[detector],
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
    r = construir_modelo(pesos_coco=None, detector="retina")
    ok.append(r.head.classification_head.num_classes == 2 and r.transform.max_size == 640 and r.score_thresh == CONF)
    ok.append(LR == {"frcnn": 0.01, "retina": 0.005} and RECETA["lr"] == LR["frcnn"])
    ok.append(PROYECTOS[("frcnn", "sil")] == "argos_frcnn")
    print("AUTOTEST %s: %d/%d" % ("SUPERADO" if all(ok) else "FALLIDO", sum(ok), len(ok)))
    return all(ok)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - detectores de torchvision (H15-H17)")
    ap.add_argument("accion", nargs="?", choices=("entrenar", "inferir"))
    ap.add_argument("--variante", choices=("V1", "V3"))
    ap.add_argument("--semilla", type=int)
    ap.add_argument("--epochs", type=int)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--detector", choices=("frcnn", "retina"), default="frcnn")
    ap.add_argument("--familia", choices=("sil", "gen", "prof"), default="sil")
    ap.add_argument("--proyecto", help="carpeta bajo runs/ (por defecto la de detector y familia; la replica de H16 usa argos_frcnn_rep)")
    ap.add_argument("--pesos")
    ap.add_argument("--nombre")
    ap.add_argument("--gt", nargs="+")
    ap.add_argument("--resultados", default=os.path.join(RAIZ, "resultados_h15"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.accion == "entrenar":
        entrenar(a.variante, a.semilla, a.epochs, a.smoke, detector=a.detector, familia=a.familia,
                 proyecto=os.path.join(RAIZ, "runs", a.proyecto) if a.proyecto else None)
    elif a.accion == "inferir":
        inferir(a.pesos, a.nombre, a.gt, a.resultados, detector=a.detector)
    else:
        ap.error("indicar accion o --selftest")


if __name__ == "__main__":
    main()
