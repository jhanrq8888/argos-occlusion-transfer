#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Analisis secundarios 4 y 5 del pre-registro de H18 (PREREGISTRO_H18.md, seccion 3), que faltaban en el
articulo (revision de integridad del 31/10/2026). No deciden ninguna hipotesis.

  4. CityPersons heavy con la caja VISIBLE (bboxVis) para H18a (V1 y V3sil, 5 semillas) y para las dos dosis de H18e
     (V1 de H18a con las semillas 0-2 frente a V3baja / V3alta), con el mismo calculo que revision_panel_analisis.py.
  5. Variacion entre maquinas: AP@0.5 medio de V1 y de V3sil de H18a frente a los de H15 (semillas 0-2), por fuente.

Salida: informes/analisis_final/h18_secundarios.json
Uso: python informes/h18_secundarios.py [--replicas 1000]
"""
import argparse
import csv
import importlib.util
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.argv = sys.argv[:1] + [a for a in sys.argv[1:]]
_sp = importlib.util.spec_from_file_location("rp", os.path.join(RAIZ, "informes", "revision_panel_analisis.py"))
RP = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(RP)

BLOQUES_H18 = [("h18a", "H18a", "resultados_h18", dict(excluir_prefijo=("V3alta", "V3baja"))),
               ("h18e_baja", "H18e-b", "resultados_h18", dict(excluir_prefijo=("V3alta", "V3sil", "V1_s3", "V1_s4"))),
               ("h18e_alta", "H18e-a", "resultados_h18", dict(excluir_prefijo=("V3baja", "V3sil", "V1_s3", "V1_s4")))]
ESTRATOS = {"NO": ("nightowls", "ocluida"), "CP": ("citypersons_convencion", "heavy"), "EX": ("test_proxy", "severa"),
            "control": ("silueta_severa", "global")}


def ap_medio(carpeta, prefijo, semillas):
    out = {}
    filas = list(csv.DictReader(open(os.path.join(RAIZ, carpeta, "resumen_ap.csv"), encoding="utf-8")))
    for f, (conj, est) in ESTRATOS.items():
        v = [float(r["AP50"]) for r in filas if r["corrida"] in ["%s_s%d" % (prefijo, s) for s in semillas]
             and r["conjunto"] == conj and r["estrato"] == est and r["luz"] == "todas"]
        out[f] = round(100 * sum(v) / len(v), 2) if len(v) == len(semillas) else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replicas", type=int, default=1000)
    a = ap.parse_args()
    vis = []
    for clave, etq, carpeta, filtro in BLOQUES_H18:
        for fila in RP.analizar_bloque((clave, etq, carpeta, filtro, a.replicas)):
            if fila["fuente"] in ("CP", "CPvis"):
                vis.append({k: fila[k] for k in ("etiqueta", "fuente", "n_V1", "n_V3", "d_heavy", "d_heavy_lo", "d_heavy_hi",
                                                 "d_bare", "d_partial")})
    maq = {}
    for var, pre in (("V1", "V1"), ("V3sil", "V3sil")):
        h18 = ap_medio("resultados_h18", pre, [0, 1, 2])
        h15 = ap_medio("resultados_h15", pre, [0, 1, 2])
        maq[var] = {f: {"H18a": h18[f], "H15": h15[f], "dif_pp": round(h18[f] - h15[f], 2)} for f in ESTRATOS}
    sal = {"caja_visible": vis, "maquinas_semillas_0_2": maq, "replicas": a.replicas}
    json.dump(sal, open(os.path.join(RAIZ, "informes", "analisis_final", "h18_secundarios.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps(sal, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
