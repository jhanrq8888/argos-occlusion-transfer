#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Veredicto literal de H9b (PREREGISTRO_H9b.md s.2): oclusion generativa
con exposicion fija (V1 y V3g, 30 epocas, pesos de la ultima epoca).

Lee resultados_h9b/analisis/bootstrap.csv (11_) y, si existen, los analisis de
sensibilidad declarados (23_/24_ --secundarios). Aplica la regla sin interpretar:
  - no concluyente si el control generativa_severa no alcanza +2 pp con IC > 0;
  - refutada si V3g - V1 >= +2 pp con IC por imagenes > 0 en al menos 2 de 3 fuentes reales;
  - sostenida en otro caso.
Escribe informes/veredicto_h9b.md.

Uso:
    python 26_veredicto_h9b.py
    python 26_veredicto_h9b.py --selftest
"""
import argparse
import os
import sys

import pandas as pd

RAIZ = os.path.dirname(os.path.abspath(__file__))
UMBRAL = 2.0
CONTROL = ("generativa_severa", "severa")
FUENTES = [("NightOwls ocluida", "nightowls", "ocluida"),
           ("CityPersons heavy", "citypersons_convencion", "heavy"),
           ("ExDark proxy severa", "test_proxy", "severa")]


def celda(df, conj, est, contraste="V3-V1"):
    f = df[(df.conjunto == conj) & (df.estrato == est) & (df.contraste == contraste)]
    if f.empty:
        return None
    r = f.iloc[0]
    return float(r.delta_AP50_pp), float(r.IC95_lo_pp), float(r.IC95_hi_pp), int(r.n_gt)


def relevante(c):
    return c is not None and c[0] >= UMBRAL and c[1] > 0


def veredicto(df):
    ctrl = celda(df, *CONTROL)
    res = [(n, celda(df, c, e)) for n, c, e in FUENTES]
    mejora = sum(1 for _, r in res if relevante(r))
    if not relevante(ctrl):
        v = "No concluyente"
    elif mejora >= 2:
        v = "Refutada"
    else:
        v = "Sostenida"
    descarta = sum(1 for _, r in res if r is not None and r[2] < UMBRAL)
    return v, ctrl, res, mejora, descarta


def fmt(c):
    return "no calculado" if c is None else "%+.2f pp [%+.2f; %+.2f] (n=%d)" % c


def construir(raiz):
    ruta = os.path.join(raiz, "resultados_h9b", "analisis", "bootstrap.csv")
    if not os.path.exists(ruta):
        sys.exit("ERROR: falta %s (ejecutar 09_ y 11_ sobre resultados_h9b)" % ruta)
    v, ctrl, res, mejora, descarta = veredicto(pd.read_csv(ruta))
    L = ["# ARGOS-11 — Veredicto de H9b (oclusión generativa, 30 épocas fijas)", "",
         "Generado por `26_veredicto_h9b.py` a partir de `resultados_h9b/analisis/bootstrap.csv` "
         "(V3ᵍ − V1, AP@0.5, media de 3 semillas, pesos de la época 30, IC 95 % bootstrap por imágenes, 1 000 réplicas). "
         "Regla literal de `PREREGISTRO_H9b.md`, sección 2.", "",
         "| Celda | V3ᵍ − V1 |", "|---|---|",
         "| Control `generativa_severa` | %s |" % fmt(ctrl)]
    L += ["| %s | %s |" % (n, fmt(r)) for n, r in res]
    L += ["", "**Fuentes reales con mejora relevante (≥ +2 pp e IC > 0): %d de 3** (para refutar se requieren 2)." % mejora, "",
          "## Veredicto: **%s**" % v, ""]
    L.append("Sensibilidad declarada: fuentes reales cuyo IC por imágenes descarta una mejora de +2 pp (límite superior < +2): **%d de 3**." % descarta)
    for nombre, fich, col_lo, col_hi in (("IC jerárquico (semillas + imágenes)", "bootstrap_jerarquico_secundarios.csv", "IC_jerarquico_lo", "IC_jerarquico_hi"),
                                        ("Tasa de pérdida MR-2 (menor es mejor)", "miss_rate_secundarios.csv", "IC_imagenes_lo", "IC_imagenes_hi")):
        p = os.path.join(raiz, "informes", "analisis_final", fich)
        if not os.path.exists(p):
            continue
        d = pd.read_csv(p)
        d = d[d.bloque == "h9b"]
        if "contraste" in d.columns:                  # 23_ incluye otros contrastes; 24_ solo V3 - V1
            d = d[d.contraste == "V3-V1"]
        L += ["", "### %s" % nombre, "", "| Conjunto | Estrato | Δ (pp) | IC |", "|---|---|---|---|"]
        for _, r in d.iterrows():
            extra = " · jerárquico [%+.2f; %+.2f]" % (r.IC_jerarquico_lo, r.IC_jerarquico_hi) if "miss" in fich else ""
            L.append("| %s | %s | %+.2f | [%+.2f; %+.2f]%s |" % (r.conjunto, r.estrato, r.delta_pp, r[col_lo], r[col_hi], extra))
    return "\n".join(L) + "\n", v


def selftest():
    fallos = []

    def comp(desc, obt, esp):
        ok = obt == esp
        print("  [%s] %s" % ("OK" if ok else "FALLO", desc))
        if not ok:
            fallos.append(desc)

    def df(ctrl, a, b, c):
        filas = []
        for (conj, est), (d, lo, hi) in zip([CONTROL] + [(x[1], x[2]) for x in FUENTES], [ctrl, a, b, c]):
            filas.append({"conjunto": conj, "estrato": est, "contraste": "V3-V1", "n_gt": 10,
                          "delta_AP50_pp": d, "IC95_lo_pp": lo, "IC95_hi_pp": hi})
        return pd.DataFrame(filas)

    comp("control sin aprender -> no concluyente", veredicto(df((1.5, 0.2, 2.8), (5, 1, 9), (5, 1, 9), (5, 1, 9)))[0], "No concluyente")
    comp("control con IC que toca el cero -> no concluyente", veredicto(df((3, -0.1, 6), (5, 1, 9), (5, 1, 9), (5, 1, 9)))[0], "No concluyente")
    comp("2 de 3 relevantes -> refutada", veredicto(df((8, 6, 10), (2.5, 0.3, 4), (2.0, 0.1, 3.9), (-1, -3, 1)))[0], "Refutada")
    comp("1 de 3 relevante -> sostenida", veredicto(df((8, 6, 10), (2.5, 0.3, 4), (1.9, 0.5, 3.3), (-1, -3, 1)))[0], "Sostenida")
    comp("delta >= 2 con IC que toca el cero no cuenta", veredicto(df((8, 6, 10), (3, -0.2, 6), (3, -0.2, 6), (3, -0.2, 6)))[3], 0)
    comp("cuenta de IC con limite superior < +2", veredicto(df((8, 6, 10), (-1, -2, 1.9), (0, -1, 2.0), (-3, -5, -1)))[4], 2)
    print("\n%s" % ("AUTOTEST SUPERADO" if not fallos else "FALLOS: %s" % fallos))
    sys.exit(1 if fallos else 0)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - veredicto literal de H9b")
    ap.add_argument("--salida", default=os.path.join(RAIZ, "informes", "veredicto_h9b.md"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    md, v = construir(RAIZ)
    with open(a.salida, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    print("H9b: %s -> %s" % (v, a.salida))


if __name__ == "__main__":
    main()
