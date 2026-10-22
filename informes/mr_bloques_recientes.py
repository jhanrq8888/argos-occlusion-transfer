#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Tasa de perdida MR-2 de los bloques con exposicion fija posteriores a H9b (H10, H12, H14 y, si existen, H15-H17).
Era un analisis secundario declarado en PREREGISTRO_H12.md y PREREGISTRO_H14.md que no se habia calculado; se calcula
el 20/10/2026 con el mismo codigo (24_miss_rate.analizar), las mismas detecciones cacheadas y el mismo bootstrap.
No decide ninguna hipotesis. Salida: informes/analisis_final/miss_rate_recientes.csv
Uso: python informes/mr_bloques_recientes.py [--replicas 1000]
"""
import argparse
import importlib.util
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
_sp = importlib.util.spec_from_file_location("mr24", os.path.join(RAIZ, "24_miss_rate.py"))
MR = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(MR)

_cargar = MR.A11.cargar_corridas


def _cargar_v3(dir_res, **kw):
    """En H10 las variantes se etiquetan V3G y V3S; 24_ solo reconoce V1 y V3. Se mapean a V3 (cada bloque ya filtra la suya)."""
    c = _cargar(dir_res, **kw)
    for d in c.values():
        if d["variante"] in ("V3G", "V3S"):
            d["variante"] = "V3"
    return c


MR.A11.cargar_corridas = _cargar_v3

BLOQUES = [
    ("h10_geometria", "resultados_h10", dict(excluir_prefijo="V3S"), ("geometria_severa", "severa")),
    ("h10_siluetas", "resultados_h10", dict(excluir_prefijo="V3G"), ("silueta_severa", "severa")),
    ("h12a", "resultados_h12m", dict(excluir_prefijo="yolo11m_V3gen"), ("silueta_severa", "severa")),
    ("h12b", "resultados_h12m", dict(excluir_prefijo="yolo11m_V3sil"), ("generativa_severa", "severa")),
    ("h14", "resultados_h14", {}, ("profundidad_severa", "severa")),
    ("h15", "resultados_h15", {}, ("silueta_severa", "severa")),
    # H16: las V1 son las de H15; h16_h17_evaluar.bat copia su cache y su eval a resultados_h16 (la replica V1rep no entra)
    ("h16a", "resultados_h16", dict(excluir_prefijo=("V3prof", "V1rep")), ("generativa_severa", "severa")),
    ("h16b", "resultados_h16", dict(excluir_prefijo=("V3gen", "V1rep")), ("profundidad_severa", "severa")),
    ("h17", "resultados_h17", {}, ("silueta_severa", "severa")),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replicas", type=int, default=1000)
    ap.add_argument("--solo", nargs="*", help="claves de bloque a calcular (def. todas las que existan)")
    a = ap.parse_args()
    bl = [b for b in BLOQUES if not a.solo or b[0] in a.solo]
    df = MR.analizar(a.replicas, 0, bloques=bl)
    salida = os.path.join(RAIZ, "informes", "analisis_final", "miss_rate_recientes.csv")
    if a.solo and os.path.exists(salida):
        import pandas as pd
        viejo = pd.read_csv(salida)
        df = pd.concat([viejo[~viejo.bloque.isin(a.solo)], df])
    df.to_csv(salida, index=False)
    print(df.to_string())


if __name__ == "__main__":
    main()
