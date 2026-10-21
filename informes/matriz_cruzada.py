#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Matriz cruzada de controles (revision del short paper, 20/10/2026, obs. 5; analisis posterior declarado).
Cada familia de entrenamiento (filas: parches del experimento 1; siluetas, generativa y geometria con 30 epocas y la V1
de H9b; profundidad con su propia V1) se evalua en el control severo de las cinco familias. Si un modelo solo hubiera
memorizado sus oclusores, ganaria en su propio control y no en los demas. Mismo bootstrap que 23_ (imagenes y jerarquico).
Lee resultados_cruzada/<fila>/; escribe informes/analisis_final/matriz_cruzada.csv.
Uso: python informes/matriz_cruzada.py
"""
import importlib.util
import os
import sys

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
_sp = importlib.util.spec_from_file_location("b23", os.path.join(RAIZ, "23_bootstrap_jerarquico.py"))
B23 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(B23)
FILAS = ["parches", "sil", "gen", "geo", "prof"]
CONTROLES = ["opaco_severa", "silueta_severa", "generativa_severa", "geometria_severa", "profundidad_severa"]


def main():
    B23.REALES = []                                   # solo los controles
    filas = []
    for f in FILAS:
        for c in CONTROLES:
            df = B23.analizar(2000, 0, verbose=False, bloques=[(f, os.path.join("resultados_cruzada", f), {}, (c, "severa"))])
            df = df[df.contraste == "V3-V1"]
            if len(df):
                r = df.iloc[0]
                filas.append({"fila": f, "control": c, "n_gt": r.n_gt, "delta": r.delta_pp, "ic_lo": r.IC_imagenes_lo, "ic_hi": r.IC_imagenes_hi,
                              "jer_lo": r.IC_jerarquico_lo, "jer_hi": r.IC_jerarquico_hi})
    d = pd.DataFrame(filas)
    d.to_csv(os.path.join(RAIZ, "informes", "analisis_final", "matriz_cruzada.csv"), index=False)
    print(d.pivot(index="fila", columns="control", values="delta").loc[FILAS, CONTROLES].to_string())


if __name__ == "__main__":
    main()
