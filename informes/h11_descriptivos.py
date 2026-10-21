#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Descriptivos declarados de H11 (PREREGISTRO_H11.md, seccion 2, analisis secundario 3).
No deciden H11. Reutiliza sin cambios las funciones de 27_ (AP@0.5:0.95 y curva por visibilidad)
y 24_ (tasa de perdida MR-2) sobre resultados_h11 (semillas 3-5, last.pt a 60 epocas).

Salida: resultados_h11/analisis/descriptivos_h11.{csv,json}
Uso: python informes/h11_descriptivos.py
"""
import importlib.util
import json
import os
import sys

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)


def modulo(nombre, fichero):
    spec = importlib.util.spec_from_file_location(nombre, os.path.join(RAIZ, fichero))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


M27 = modulo("ap27", "27_ap_estricto_visibilidad.py")
M24 = modulo("mr24", "24_miss_rate.py")
BLOQUE = ("h11", "resultados_h11", {}, ("cp_silueta_severa", "severa"))
B, SEMILLA = 1000, 0


def main():
    clave, dir_res, filtro, sint = BLOQUE
    filas_ap = []
    for i, (conj, est) in enumerate([sint] + M27.B23.REALES):
        r = M27.celda_ap(clave, dir_res, filtro, sint, conj, est, B, SEMILLA * 1000 + i)
        if r:
            filas_ap.append(r)
    filas_vis = []
    for j, (a, b) in enumerate(M27.TRAMOS):
        r = M27.celda_vis(clave, dir_res, filtro, a, b, B, SEMILLA * 1000 + 100 + j)
        if r:
            filas_vis.append(r)
    dmr = M24.analizar(B, SEMILLA, bloques=[BLOQUE])
    out = os.path.join(RAIZ, dir_res, "analisis")
    da, dv = pd.DataFrame(filas_ap), pd.DataFrame(filas_vis)
    da.to_csv(os.path.join(out, "descriptivos_h11_ap5095.csv"), index=False)
    dv.to_csv(os.path.join(out, "descriptivos_h11_visibilidad.csv"), index=False)
    dmr.to_csv(os.path.join(out, "descriptivos_h11_miss_rate.csv"), index=False)
    with open(os.path.join(out, "descriptivos_h11.json"), "w", encoding="utf-8") as fh:
        json.dump({"ap5095": filas_ap, "visibilidad": filas_vis, "miss_rate": dmr.to_dict("records")},
                  fh, indent=1, ensure_ascii=False, default=float)
    pd.set_option("display.width", 220)
    for nombre, d in (("AP@0.5:0.95", da), ("Visibilidad (AP@0.5)", dv), ("MR-2", dmr)):
        print("\n==", nombre)
        print(d.drop(columns=[c for c in ("replicas", "semilla_celda", "bloque", "exp") if c in d]).to_string(index=False))


if __name__ == "__main__":
    main()
