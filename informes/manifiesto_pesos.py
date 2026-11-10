#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Manifiesto SHA-256 de los pesos evaluados de la evidencia primaria (bloques con epocas fijas, H9b-H18), para
que una copia entregada a los revisores pueda verificarse (revision del short paper del 10/11/2026, obs. 8).
Salida: informes/analisis_final/pesos_sha256.csv (bloque, corrida, ruta relativa, bytes, sha256)
Uso: python informes/manifiesto_pesos.py
"""
import csv
import glob
import hashlib
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETAS = {"argos_gen_fijo": "H9b", "argos_geo": "H10", "argos_sil_fijo": "H10-s", "argos_cp_fijo": "H11",
            "argos_m_sil": "H12a", "argos_m_gen": "H12a/H12b", "argos_prof": "H14", "argos_frcnn": "H15",
            "argos_frcnn_gen": "H16a", "argos_frcnn_prof": "H16b", "argos_retina": "H17", "argos_frcnn_r18_sil": "H18a",
            "argos_frcnn_r18_baja": "H18e-b", "argos_frcnn_r18_alta": "H18e-a"}


def sha(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


filas = []
for carpeta, bloque in CARPETAS.items():
    for p in sorted(glob.glob(os.path.join(RAIZ, "runs", carpeta, "*", "weights", "last.pt*"))):
        rel = os.path.relpath(p, RAIZ).replace("\\", "/")
        filas.append({"bloque": bloque, "corrida": rel.split("/")[2], "ruta": rel, "bytes": os.path.getsize(p), "sha256": sha(p)})
sal = os.path.join(RAIZ, "informes", "analisis_final", "pesos_sha256.csv")
with open(sal, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(filas[0]))
    w.writeheader()
    w.writerows(filas)
print(len(filas), "pesos;", round(sum(f["bytes"] for f in filas) / 2 ** 30, 2), "GiB ->", sal)
