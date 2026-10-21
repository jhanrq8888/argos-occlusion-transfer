#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Referencia descriptiva (PREREGISTRO_H14.md, seccion 6): detectores de vocabulario abierto
SIN AJUSTE sobre las tres fuentes de oclusion real.

  owlv2   google/owlv2-base-patch16-ensemble, consulta "a photo of a person"
  gdino   IDEA-Research/grounding-dino-tiny, consulta "a person."
Se guardan hasta 300 cajas por imagen con puntuacion >= 0,01 (owlv2) o >= 0,05 (gdino, umbral minimo de su
post-proceso) y se evaluan con 09_evaluar_estratificado.evaluar_conjunto: mismas regiones ignore, mismo
emparejamiento y mismos estratos que el resto del estudio. No decide ninguna hipotesis.

Salidas: resultados_ref/det/{modelo}__{conjunto}.json, resultados_ref/resumen_ap.csv e informes/REFERENCIA_FUNDACION.md
Uso:  python 33_fundacion.py [--modelos owlv2 gdino]   |   python 33_fundacion.py --selftest
"""
import argparse
import importlib.util
import os
import sys
import time

import numpy as np

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
from argos_lib.gt import cargar_detecciones, cargar_gt, guardar_detecciones   # noqa: E402

RES = os.path.join(RAIZ, "resultados_ref")
GTS = [os.path.join("dataset", "externos", "gt_nightowls.json"), os.path.join("dataset", "externos", "gt_citypersons_convencion.json"),
       os.path.join("dataset", "gt_test_proxy.json")]
MODELOS = {"owlv2": ("google/owlv2-base-patch16-ensemble", "a photo of a person", 0.01),
           "gdino": ("IDEA-Research/grounding-dino-tiny", "a person.", 0.05)}
MAX_DET = 300


def _e09():
    spec = importlib.util.spec_from_file_location("e09", os.path.join(RAIZ, "09_evaluar_estratificado.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def recortar(cajas, puntos, max_det=MAX_DET):
    o = np.argsort(-np.asarray(puntos))[:max_det]
    return [[float(c) for c in cajas[i]] + [float(puntos[i])] for i in o]


class Detector:
    def __init__(self, clave, device="cuda"):
        import torch
        hf, self.consulta, self.umbral = MODELOS[clave]
        self.torch, self.device, self.clave = torch, device, clave
        if clave == "owlv2":
            from transformers import Owlv2ForObjectDetection, Owlv2Processor
            self.proc, self.mod = Owlv2Processor.from_pretrained(hf), Owlv2ForObjectDetection.from_pretrained(hf)
        else:
            from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor
            self.proc, self.mod = AutoProcessor.from_pretrained(hf), AutoModelForZeroShotObjectDetection.from_pretrained(hf)
        self.mod = self.mod.to(device).eval()

    def __call__(self, im_pil):
        W, H = im_pil.size
        with self.torch.no_grad():
            if self.clave == "owlv2":
                x = self.proc(text=[[self.consulta]], images=im_pil, return_tensors="pt").to(self.device)
                out = self.mod(**x)
                s = max(W, H)                     # OWLv2 rellena a cuadrado: las cajas vienen en el lado mayor
                r = self.proc.post_process_grounded_object_detection(out, threshold=self.umbral, target_sizes=[(s, s)])[0]   # transformers 5
            else:
                x = self.proc(images=im_pil, text=self.consulta, return_tensors="pt").to(self.device)
                out = self.mod(**x)
                r = self.proc.post_process_grounded_object_detection(out, x.input_ids, threshold=self.umbral, text_threshold=self.umbral,
                                                                     target_sizes=[(H, W)])[0]
        cajas = r["boxes"].float().cpu().numpy()
        cajas[:, [0, 2]] = cajas[:, [0, 2]].clip(0, W); cajas[:, [1, 3]] = cajas[:, [1, 3]].clip(0, H)
        return recortar(cajas, r["scores"].float().cpu().numpy())


def main_eval(modelos):
    from PIL import Image
    import pandas as pd
    E = _e09()
    filas = []
    for clave in modelos:
        det_mod = None
        for g in GTS:
            gt = cargar_gt(os.path.join(RAIZ, g))
            cache = os.path.join(RES, "det", "%s__%s.json" % (clave, gt["conjunto"]))
            if os.path.exists(cache) and len(cargar_detecciones(cache)["detecciones"]) == len(gt["imagenes"]):
                det = cargar_detecciones(cache)["detecciones"]
            else:
                det_mod = det_mod or Detector(clave)
                det, t0 = {}, time.time()
                for k, n in enumerate(sorted(gt["imagenes"])):
                    det[n] = det_mod(Image.open(os.path.join(gt["dir_imagenes"], n)).convert("RGB"))
                    if (k + 1) % 200 == 0:
                        print("  %s %s %d/%d (%.2f s/imagen)" % (clave, gt["conjunto"], k + 1, len(gt["imagenes"]), (time.time() - t0) / (k + 1)), flush=True)
                os.makedirs(os.path.dirname(cache), exist_ok=True)
                guardar_detecciones(cache, MODELOS[clave][0], gt["conjunto"], det, MODELOS[clave][2], None,
                                    extra={"consulta": MODELOS[clave][1], "max_det": MAX_DET, "segundos": round(time.time() - t0, 1)})
            for f in E.evaluar_conjunto(gt, det, por_luz=False):
                filas.append({"modelo": clave, "conjunto": gt["conjunto"], **f})
    d = pd.DataFrame(filas)
    d.to_csv(os.path.join(RES, "resumen_ap.csv"), index=False)
    L = ["# Referencia: detectores de vocabulario abierto sin ajuste", "",
         "Generado por `33_fundacion.py`. AP@0.5 por estrato, mismo evaluador y mismas regiones *ignore* que el resto del estudio. "
         "Descriptivo (PREREGISTRO_H14.md, sección 6).", "", "| Modelo | Conjunto | Estrato | AP@0.5 | n |", "|---|---|---|---|---|"]
    L += ["| %s | %s | %s | %.3f | %d |" % (r.modelo, r.conjunto, r.estrato, r.AP50, r.n_gt) for r in d.itertuples()]
    open(os.path.join(RAIZ, "informes", "REFERENCIA_FUNDACION.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


def selftest():
    fallos = []

    def comp(desc, ok):
        print("  [%s] %s" % ("OK" if ok else "FALLO", desc))
        if not ok:
            fallos.append(desc)
    c = np.array([[0, 0, 1, 1], [1, 1, 2, 2], [2, 2, 3, 3]], float)
    r = recortar(c, [0.2, 0.9, 0.5], max_det=2)
    comp("ordena por puntuacion y recorta a max_det", len(r) == 2 and r[0][4] == 0.9 and r[1][4] == 0.5)
    comp("formato [x1, y1, x2, y2, s]", all(len(x) == 5 for x in r))
    comp("dos modelos declarados", sorted(MODELOS) == ["gdino", "owlv2"])
    comp("tres fuentes reales", len(GTS) == 3)
    print("\n%s" % ("AUTOTEST SUPERADO: %d/%d" % (4 - len(fallos), 4) if not fallos else "FALLOS: %s" % fallos))
    sys.exit(1 if fallos else 0)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - referencia con modelos de fundacion")
    ap.add_argument("--modelos", nargs="+", default=list(MODELOS))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    main_eval(a.modelos)


if __name__ == "__main__":
    main()
