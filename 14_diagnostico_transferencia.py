#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Paso 11 (exploratorio): diagnostico de la brecha sintetico -> real.

Pregunta: por que el aumento de oclusion (V3/V4) mejora +30..+60 pp sobre
oclusion sintetica y no transfiere (o empeora) sobre oclusion real
(NightOwls, CityPersons)? Descompone el AP en recall y falsos positivos a
un umbral fijo de confianza, por estrato y por conjunto, con la misma regla
de regiones ignore que la evaluacion. Usa las detecciones cacheadas por 09.

Salida: resultados/analisis/diagnostico_transferencia.csv y resumen en consola.

Uso:
    python 14_diagnostico_transferencia.py --resultados resultados --conf 0.25
"""

import argparse
import csv
import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argos_lib.ap import _iou_matriz                        # noqa: E402
from argos_lib.gt import cargar_detecciones, cargar_gt      # noqa: E402

RAIZ = os.path.dirname(os.path.abspath(__file__))
CONJUNTOS = ["test_real", "test_proxy", "textura_severa", "recorte_severa", "opaco_severa", "silueta_severa",
             "cp_silueta_severa", "nightowls", "citypersons", "citypersons_convencion"]


def contar(gt, det, conf, estrato, iou_thr=0.5):
    """TP, FN (GT del estrato) y FP (detecciones >= conf no emparejadas con
    ningun GT ni con region ignore) sobre todas las imagenes."""
    tp = fn = fp = 0
    scores_tp = []
    for nombre, meta in gt["imagenes"].items():
        gts = [[o["x1"], o["y1"], o["x2"], o["y2"]] for o in meta["instancias"]]
        objetivo = [o["estrato"] == estrato for o in meta["instancias"]]
        ign = [not t for t in objetivo]                      # todo lo demas es ignore
        dets = [d for d in det.get(nombre, []) if d[4] >= conf]
        dets.sort(key=lambda r: -r[4])
        n_obj = sum(objetivo)
        if not dets:
            fn += n_obj
            continue
        if not gts:
            fp += len(dets)
            continue
        iou = _iou_matriz(dets, gts, ign)
        usado = [False] * len(gts)
        for di, d in enumerate(dets):
            mejor, mejor_iou = -1, iou_thr
            for gi in range(len(gts)):
                if usado[gi] and not ign[gi]:
                    continue
                if mejor > -1 and not ign[mejor] and ign[gi]:
                    break
                if iou[di, gi] >= mejor_iou:
                    mejor, mejor_iou = gi, iou[di, gi]
            if mejor == -1:
                fp += 1
            elif not ign[mejor]:
                usado[mejor] = True
                tp += 1
                scores_tp.append(d[4])
        fn += n_obj - sum(1 for gi in range(len(gts)) if usado[gi] and objetivo[gi])
    n_img = len(gt["imagenes"])
    return {"tp": tp, "fn": fn, "fp": fp, "n_gt": tp + fn,
            "recall": tp / (tp + fn) if tp + fn else float("nan"),
            "fp_por_imagen": fp / n_img if n_img else float("nan"),
            "score_medio_tp": float(np.mean(scores_tp)) if scores_tp else float("nan")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resultados", default=os.path.join(RAIZ, "resultados"))
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--excluir-prefijo", help="descartar corridas con este prefijo (p. ej. yolo26s_)")
    ap.add_argument("--subdir", default="analisis", help="subcarpeta de salida dentro de --resultados")
    args = ap.parse_args()
    corr = {}
    for f in glob.glob(os.path.join(args.resultados, "eval", "*.json")):
        ev = json.load(open(f, encoding="utf-8"))
        if args.excluir_prefijo and ev.get("corrida", "").startswith(args.excluir_prefijo):
            continue
        if ev.get("variante"):
            corr[ev["corrida"]] = ev
    filas = []
    for conj in CONJUNTOS:
        ruta_gt = next((ev["conjuntos"][conj]["gt"] for ev in corr.values() if conj in ev["conjuntos"]), None)
        if not ruta_gt:
            continue
        gt = cargar_gt(ruta_gt)
        estratos = sorted({o["estrato"] for m in gt["imagenes"].values() for o in m["instancias"]}
                          - {"ignorar", "sin_anotar"})
        acum = defaultdict(list)
        for c, ev in sorted(corr.items()):
            ruta = os.path.join(args.resultados, "det", "%s__%s.json" % (c, conj))
            if not os.path.exists(ruta):
                continue
            det = cargar_detecciones(ruta)["detecciones"]
            for e in estratos:
                r = contar(gt, det, args.conf, e)
                acum[(ev["variante"], e)].append(r)
        for (v, e), rs in sorted(acum.items()):
            fila = {"conjunto": conj, "estrato": e, "variante": v, "n_semillas": len(rs),
                    "n_gt": rs[0]["n_gt"], "conf": args.conf}
            for k in ("recall", "fp_por_imagen", "score_medio_tp"):
                fila[k] = float(np.nanmean([r[k] for r in rs]))
            filas.append(fila)
    os.makedirs(os.path.join(args.resultados, args.subdir), exist_ok=True)
    ruta = os.path.join(args.resultados, args.subdir, "diagnostico_transferencia.csv")
    with open(ruta, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        for f in filas:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in f.items()})
    print("Umbral de confianza: %.2f (media de semillas)\n" % args.conf)
    print("%-22s %-9s %5s | %-24s | %-24s | %-24s" % ("conjunto", "estrato", "n", "recall V1/V2/V3/V4",
                                                     "FP por imagen V1/V2/V3/V4", "score medio TP V1..V4"))
    por = {(f["conjunto"], f["estrato"], f["variante"]): f for f in filas}
    for conj in CONJUNTOS:
        for e in sorted({k[1] for k in por if k[0] == conj}):
            vs = ["V1", "V2", "V3", "V4"]
            if not all((conj, e, v) in por for v in vs):
                continue
            g = lambda k: "/".join("%.3f" % por[(conj, e, v)][k] for v in vs)   # noqa: E731
            print("%-22s %-9s %5d | %-24s | %-24s | %-24s" % (conj, e, por[(conj, e, "V1")]["n_gt"],
                                                             g("recall"), g("fp_por_imagen"), g("score_medio_tp")))
    print("\n-> %s" % ruta)


if __name__ == "__main__":
    main()
