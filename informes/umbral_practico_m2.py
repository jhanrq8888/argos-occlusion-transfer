#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Observacion m2 de la revision externa del 27/10: traducir el umbral de +2 pp de AP@0.5 a personas detectadas.

Analisis posterior declarado (no decide hipotesis). Con las detecciones guardadas de H18 (resultados_h18/det, semillas 0-2,
V1 y las tres V3), calcula en NightOwls ocluidos y CityPersons heavy:
  - AP@0.5 (mismo emparejamiento que 09_evaluar_estratificado.py, regiones ignore incluidas);
  - personas detectadas por cada 1 000 ocluidas a un punto de operacion fijo: 0,1 falsos positivos por imagen (FPPI),
    el punto medio del rango de MR-2.
Despues ajusta, sobre los 24 pares (variante, semilla, fuente) frente a V1 de la misma semilla, la recta
d(personas/1000) = b * d(AP pp) y da cuantas personas mas por cada 1 000 ocluidas equivalen a +2 pp.
Uso: python informes/umbral_practico_m2.py"""
import json
import os
import sys

import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from argos_lib.ap import ap_conjunto, emparejar_conjunto  # noqa: E402

FUENTES = {"NO": ("nightowls", "dataset/externos/gt_nightowls.json", "ocluida"),
           "CP": ("citypersons_convencion", "dataset/externos/gt_citypersons_convencion.json", "heavy")}
VARIANTES = ("V1", "V3sil", "V3baja", "V3alta")
FPPI = 0.1


def detectadas_por_mil(emp, n_img):
    sc = np.concatenate([e["scores"][0] for e in emp]); tp = np.concatenate([e["tp"][0] for e in emp])
    n_gt = sum(e["n_gt"] for e in emp)
    o = np.argsort(-sc, kind="mergesort"); tp = tp[o]
    fppi = np.cumsum(~tp) / n_img
    k = np.searchsorted(fppi, FPPI, side="right")            # detecciones con FPPI <= 0,1
    return 1000.0 * tp[:k].sum() / n_gt


def main():
    filas = []
    for f, (conj, ruta_gt, estr) in FUENTES.items():
        gt = json.load(open(os.path.join(RAIZ, ruta_gt), encoding="utf-8"))["imagenes"]
        for v in VARIANTES:
            for s in (0, 1, 2):
                det = json.load(open(os.path.join(RAIZ, "resultados_h18", "det", "%s_s%d__%s.json" % (v, s, conj)),
                                     encoding="utf-8"))["detecciones"]
                emp, noms = emparejar_conjunto(gt, det, estrato=estr)
                filas.append(dict(fuente=f, var=v, semilla=s, ap=100 * ap_conjunto(emp)["AP50"],
                                  por_mil=detectadas_por_mil(emp, len(noms))))
    base = {(r["fuente"], r["semilla"]): r for r in filas if r["var"] == "V1"}
    dap, dpm = [], []
    for r in filas:
        if r["var"] == "V1":
            continue
        b = base[(r["fuente"], r["semilla"])]
        dap.append(r["ap"] - b["ap"]); dpm.append(r["por_mil"] - b["por_mil"])
    dap, dpm = np.array(dap), np.array(dpm)
    pend = float(np.dot(dap, dpm) / np.dot(dap, dap))             # recta por el origen
    r = float(np.corrcoef(dap, dpm)[0, 1])
    res = {"fppi": FPPI, "pares": int(len(dap)), "personas_por_mil_por_pp": round(pend, 2),
           "personas_por_mil_con_2pp": round(2 * pend, 1), "correlacion": round(r, 3),
           "V1_por_mil": {f: round(float(np.mean([b["por_mil"] for (ff, _), b in base.items() if ff == f])), 1)
                          for f in FUENTES},
           "filas": filas}
    out = os.path.join(RAIZ, "informes", "analisis_final", "umbral_practico_m2.json")
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1)
    print({k: v for k, v in res.items() if k != "filas"})


if __name__ == "__main__":
    main()
