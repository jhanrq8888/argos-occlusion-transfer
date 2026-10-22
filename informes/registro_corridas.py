#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Registro de corridas (revision del short paper, 20/10/2026, obs. 3 y 6): una fila por corrida valida con
bloque, hipotesis, variante, detector, semilla, epocas entrenadas, epoca de los pesos evaluados, regla de exposicion,
maquina y horas de GPU (columna `time` de results.csv). La epoca de best.pt es la de maxima mAP50-95 en validacion (la aptitud de Ultralytics 8.4).
Salida: informes/analisis_final/registro_corridas.csv y un resumen por bloque en pantalla.
Uso: python informes/registro_corridas.py
"""
import csv
import glob
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL, NUBE = "RTX 5050 Laptop (local)", "RTX 4090 (RunPod)"
# carpeta de runs, bloque, hipotesis, pesos evaluados, regla de exposicion, maquina, filtro de nombre
BLOQUES = [
    ("argos", "Exp. 1 (parches)", "H1-H3", "best", "parada temprana (paciencia 20, max. 100)", LOCAL, None),
    ("argos_v2", "Iteracion 2 (siluetas)", "H4-H5", "best", "parada temprana (paciencia 20, max. 100)", LOCAL, lambda n: not n.startswith("yolo26s_")),
    ("argos_v2", "Replica YOLO26s", "H4-Y26", "best", "parada temprana (paciencia 20, max. 100)", LOCAL, lambda n: n.startswith("yolo26s_")),
    ("argos_cp", "H6 (CityPersons)", "H6", "best", "parada temprana (paciencia 20, max. 100)", LOCAL, None),
    ("argos_no_2000", "H7 peldano 2 000", "H7", "best", "presupuesto fijo de presentaciones, paciencia 1/5", LOCAL, None),
    ("argos_no_5000", "H7 peldano 5 000", "H7", "best", "presupuesto fijo de presentaciones, paciencia 1/5", LOCAL, None),
    ("argos_no_10000", "H7 peldano 10 000", "H7", "best", "presupuesto fijo de presentaciones, paciencia 1/5", LOCAL, None),
    ("argos_no_20000", "H7 peldano 20 000", "H7", "best", "presupuesto fijo de presentaciones, paciencia 1/5", LOCAL, None),
    ("argos_rtdetr", "H8 (RT-DETR-l)", "H8", "best", "parada temprana (paciencia 20, max. 100)", LOCAL, None),
    ("argos_gen", "H9 (generativa)", "H9", "best", "parada temprana (paciencia 20, max. 100)", LOCAL, None),
    ("argos_gen_fijo", "H9b (generativa, 30 ep.)", "H9b", "last", "30 epocas fijas", LOCAL, None),
    ("argos_geo", "H10 (geometria, 30 ep.)", "H10", "last", "30 epocas fijas", LOCAL, None),
    ("argos_sil_fijo", "H10-s (siluetas, 30 ep.)", "H10", "last", "30 epocas fijas", LOCAL, None),
    ("argos_cp_fijo", "H11 (CityPersons, 60 ep.)", "H11", "last", "60 epocas fijas", NUBE, None),
    ("argos_m_gen", "H12 (YOLOv11m)", "H12a/H12b", "last", "30 epocas fijas", NUBE, None),
    ("argos_m_sil", "H12 (YOLOv11m)", "H12a", "last", "30 epocas fijas", NUBE, None),
    ("argos_gen_fijo_s34", "Extension de semillas", "H9b (sec.)", "last", "30 epocas fijas", NUBE, None),
    ("argos_sil_fijo_s34", "Extension de semillas", "H10 (sec.)", "last", "30 epocas fijas", NUBE, None),
    ("argos_prof", "H14 (profundidad, 30 ep.)", "H14", "last", "30 epocas fijas", NUBE, None),
    ("argos_frcnn", "H15 (Faster R-CNN, 30 ep.)", "H15", "last", "30 epocas fijas", NUBE, None),
    ("argos_frcnn_gen", "H16a (Faster R-CNN, generativa)", "H16a", "last", "30 epocas fijas", NUBE, None),
    ("argos_frcnn_prof", "H16b (Faster R-CNN, profundidad)", "H16b", "last", "30 epocas fijas", NUBE, None),
    ("argos_retina", "H17 (RetinaNet, 30 ep.)", "H17", "last", "30 epocas fijas", NUBE, None),
    ("argos_frcnn_rep", "Replica de V1 entre pods", "H16 (sec.)", "last", "30 epocas fijas", NUBE, None),
]


def detector(nombre, carpeta):
    if carpeta == "argos_rtdetr":
        return "RT-DETR-l"
    if carpeta.startswith("argos_frcnn"):
        return "Faster R-CNN R50-FPN v2"
    if carpeta == "argos_retina":
        return "RetinaNet R50-FPN v2"
    if nombre.startswith("yolo26s_"):
        return "YOLO26s"
    if nombre.startswith("yolo11m_") or carpeta.startswith("argos_m_"):
        return "YOLOv11m"
    return "YOLOv11s" + ("+CBAM" if nombre.split("_")[0] in ("V2", "V4") else "")


def main():
    filas = []
    for carpeta, bloque, hip, pesos, regla, maq, filtro in BLOQUES:
        for d in sorted(glob.glob(os.path.join(RAIZ, "runs", carpeta, "*"))):
            n = os.path.basename(d)
            rc = os.path.join(d, "results.csv")
            if not os.path.isfile(rc) or (filtro and not filtro(n)):
                continue
            r = list(csv.DictReader(open(rc, encoding="utf-8")))
            if not r:
                continue
            r = [{k.strip(): v for k, v in x.items()} for x in r]
            ep = len(r)
            if pesos == "best":
                # Ultralytics 8.4 guarda en best.pt la epoca de maxima aptitud en validacion, y su aptitud es mAP50-95
                # (pesos [0, 0, 0, 1] de Metric.fitness); la primera epoca con el maximo es la de best.pt.
                col = [float(x.get("metrics/mAP50-95(B)", "nan") or "nan") for x in r]
                eleg = int(max(range(ep), key=lambda i: (col[i], -i))) + 1
            else:
                eleg = ep
            partes = n.replace("yolo26s_", "").replace("yolo11m_", "").split("_")
            filas.append({"carpeta": carpeta, "bloque": bloque, "hipotesis": hip, "corrida": n, "variante": partes[0],
                          "detector": detector(n, carpeta), "semilla": partes[-1].lstrip("s"),
                          "epocas_entrenadas": ep, "pesos_evaluados": pesos, "epoca_evaluada": eleg,
                          "regla_de_exposicion": regla, "maquina": maq,
                          "horas_gpu": round(float(r[-1].get("time", 0) or 0) / 3600, 2)})
    sal = os.path.join(RAIZ, "informes", "analisis_final", "registro_corridas.csv")
    with open(sal, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader(); w.writerows(filas)
    from collections import Counter
    c = Counter(f["bloque"] for f in filas)
    for b, k in c.items():
        print("%-32s %d" % (b, k))
    print("TOTAL", len(filas), "| horas GPU", round(sum(f["horas_gpu"] for f in filas), 1))


if __name__ == "__main__":
    main()
