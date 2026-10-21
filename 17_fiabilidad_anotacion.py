#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Estudio de fiabilidad de la anotacion manual de oclusion.

La anotacion visual del grado de oclusion en baja iluminacion se intento
con: un piloto de 50 instancias por dos anotadores (A, B) y tres
pasadas de un tercer anotador (anotador C v1: 330; v2: 50 de calibracion; v3: 330
con la interfaz de dos pasos "que objeto la tapa"). Este script calcula el
kappa ponderado (cuadratico) de todas las parejas sobre las instancias
comunes, la distribucion de estratos de cada pasada y las matrices de
confusion, y lo guarda como resultado (no como ground truth).

Uso:
    python 17_fiabilidad_anotacion.py
"""

import csv
import itertools
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module                      # noqa: E402
k3 = import_module("03_calcular_kappa")

RAIZ = os.path.dirname(os.path.abspath(__file__))
PASADAS = {
    "Anotador A (piloto)": "anotacion_anotador_A.csv",
    "Anotador B (piloto)": "anotacion_anotador_B.csv",
    "anotador C v1 (330, un paso)": "anotacion_anotador_C_v1.csv",
    "anotador C v2 (50, calibracion)": "anotacion_anotador_C_v2.csv",
    "anotador C v3 (330, dos pasos)": "anotacion_anotador_C_v3.csv",
}


def leer(ruta):
    with open(ruta, newline="", encoding="utf-8-sig") as fh:
        return {r["id_instancia"]: r for r in csv.DictReader(fh) if r.get("id_instancia")}


def main():
    datos = {k: leer(os.path.join(RAIZ, v)) for k, v in PASADAS.items() if os.path.exists(os.path.join(RAIZ, v))}
    salida = {"distribucion": {}, "parejas": []}
    print("Distribucion de estratos por pasada:")
    for k, d in datos.items():
        c = Counter(r["estrato"] for r in d.values())
        salida["distribucion"][k] = dict(c)
        n = len(d)
        print("  %-26s n=%3d  " % (k, n) + "  ".join("%s %3d (%2.0f%%)" % (e, c[e], 100 * c[e] / n)
                                                    for e in k3.ORDEN + ["no_evaluable"]))
    print("\nKappa ponderado (cuadratico) por pareja, sobre instancias comunes evaluables:")
    for a, b in itertools.combinations(datos, 2):
        A, B = datos[a], datos[b]
        pares = [(A[i]["estrato"], B[i]["estrato"]) for i in set(A) & set(B)
                 if A[i]["estrato"] in k3.ORDEN and B[i]["estrato"] in k3.ORDEN]
        if len(pares) < 10:
            continue
        kp, mat, n = k3.kappa_ponderado(pares)
        acuerdo = sum(mat[i][i] for i in range(4)) / n
        salida["parejas"].append({"a": a, "b": b, "n": n, "kappa_ponderado": kp, "acuerdo_exacto": acuerdo,
                                  "matriz(filas=a,cols=b; sin/lig/mod/sev)": mat})
        print("  %-26s vs %-26s n=%3d  kappa=%.3f  acuerdo exacto=%.2f  [%s]"
              % (a, b, n, kp if kp is not None else float("nan"), acuerdo, k3.interpretar(kp)))
    salida["conclusion"] = ("El acuerdo entre pasadas y anotadores oscila entre 0,16 y 0,60 (solo el piloto A-B "
                            "alcanza 0,82), con desacuerdos sistematicos en la decision 'sin oclusion' frente a "
                            "'ligera' (oscuridad, borde de imagen o ropa oscura interpretados como oclusion) y, tras "
                            "corregir eso, en sentido contrario. El grado de oclusion en baja iluminacion no es "
                            "anotable de forma fiable a ojo; por ello el analisis en dominio usa el proxy objetivo por "
                            "solapamiento de cajas (16_oclusion_proxy.py) y la anotacion manual se reporta como estudio "
                            "de fiabilidad.")
    os.makedirs(os.path.join(RAIZ, "resultados", "analisis"), exist_ok=True)
    ruta = os.path.join(RAIZ, "resultados", "analisis", "fiabilidad_anotacion.json")
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(salida, fh, indent=2, ensure_ascii=False)
    print("\n-> %s" % ruta)


if __name__ == "__main__":
    main()
