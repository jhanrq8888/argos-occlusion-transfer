#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Analisis pedidos por la revision del short paper del 10/11/2026 (reporte_revision_g1_jqkka4fd2h). Todos son
ANALISIS POSTERIORES: no cambian ninguna regla ni ningun veredicto prerregistrado.

  Obs. 1  sensibilidad de la estimacion global por fuente: (a) TOST (IC 90 %, margen +-2 pp) del modelo mixto original con
          y sin H18e; (b) modelo mixto con un componente para las V1 compartidas entre bloques (H9b/H10/H10-s, H12a/H12b,
          H15/H16a/H16b) por semilla; (c) bootstrap de bloques de la media por fuente. Con y sin los bloques de dosis.
  Obs. 6  celdas que pasarian la regla por azar (efecto verdadero 0) en los bloques con control y dosis habitual, con el
          IC por imagenes de cada celda (normal), frente a las observadas.
  Obs. 10 personas pegadas y etiquetadas por imagen de entrenamiento segun la dosis (cota superior analitica).
Salida: informes/analisis_final/revision_10nov.json y revision_10nov.md
Uso: python informes/revision_10nov.py
"""
import json
import os
import warnings

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AF = os.path.join(RAIZ, "informes", "analisis_final")
UMBRAL = 2.0
BASE = ["H9b", "H10", "H10-s", "H11", "H12a", "H12b", "H14", "H15", "H16a", "H16b", "H17", "H18a"]
DOSIS = ["H18e-baja", "H18e-alta"]
# bloques cuyas V1 son las mismas corridas (CAMBIOS_PROTOCOLO.md y suplemento): H10 y H10-s usan la V1 de H9b; H12a y
# H12b comparten V1; H16a y H16b usan la V1 de H15; H18e usa la V1 de H18a (semillas 0-2)
V1 = {"H9b": "g9b", "H10": "g9b", "H10-s": "g9b", "H12a": "g12", "H12b": "g12", "H15": "g15", "H16a": "g15",
      "H16b": "g15", "H18a": "g18", "H18e-baja": "g18", "H18e-alta": "g18"}


def r2(x):
    return float(round(x, 2))


def mixto(df, cruzado):
    df = df.copy()
    df["v1grupo"] = df.bloque.map(lambda b: V1.get(b, b))
    df["semnum"] = df.semilla.str.extract(r"_s(\d+)$")[0]
    df["semv1"] = df.v1grupo + "_" + df.semnum
    if cruzado:
        m = mejor_ajuste(smf.mixedlm("delta ~ 0 + C(fuente)", df, groups="v1grupo", re_formula="1",
                                     vc_formula={"bloque": "0 + C(bloque)", "semv1": "0 + C(semv1)"}))
    else:
        df["bs"] = df.bloque + "_" + df.semnum
        m = mejor_ajuste(smf.mixedlm("delta ~ 0 + C(fuente)", df, groups="bloque", re_formula="1",
                                     vc_formula={"sem": "0 + C(bs)"}))
    out = {}
    for f in ("NO", "CP", "EX"):
        k = "C(fuente)[%s]" % f
        e, se = m.params[k], m.bse[k]
        out[f] = {"est": r2(e), "IC95": [r2(e - 1.96 * se), r2(e + 1.96 * se)],
                  "IC90": [r2(e - 1.645 * se), r2(e + 1.645 * se)],
                  "equivalente_2pp": bool(e - 1.645 * se > -UMBRAL and e + 1.645 * se < UMBRAL),
                  "sup90_bajo_2": bool(e + 1.645 * se < UMBRAL)}
    out["n_obs"], out["n_bloques"], out["convergio"] = int(len(df)), int(df.bloque.nunique()), bool(m.converged)
    out["optimizador"] = m.optimizador
    return out


def mejor_ajuste(modelo):
    """REML con varios optimizadores; devuelve el ajuste convergido de mayor verosimilitud (el BFGS por defecto de
    statsmodels no convergía en varias de estas especificaciones)."""
    ajustes = []
    for met in ("bfgs", "lbfgs", "powell", "nm"):
        try:
            m = modelo.fit(reml=True, method=met, maxiter=5000)
        except Exception:
            continue
        m.optimizador = met
        ajustes.append(m)
    conv = [m for m in ajustes if m.converged]
    return max(conv or ajustes, key=lambda m: m.llf)


def boot_bloques(df, B=10000, semilla=0):
    medias = df.groupby(["bloque", "fuente"]).delta.mean().unstack()
    r = np.random.RandomState(semilla)
    out = {}
    for f in ("NO", "CP", "EX"):
        x = medias[f].dropna().values
        bs = np.array([x[r.randint(0, len(x), len(x))].mean() for _ in range(B)])
        out[f] = {"media": r2(x.mean()), "IC95": [r2(np.percentile(bs, 2.5)), r2(np.percentile(bs, 97.5))],
                  "IC90": [r2(np.percentile(bs, 5)), r2(np.percentile(bs, 95))], "k": int(len(x))}
    return out


def azar(celdas):
    """Celdas que pasarian la regla (delta >= +2 y limite inferior > 0) si el efecto verdadero fuera 0."""
    res = {}
    for nombre, lo, hi in (("imagenes", "ic_lo", "ic_hi"), ("jerarquico", "jer_lo", "jer_hi")):
        se = (celdas[hi] - celdas[lo]) / 3.92
        p = 1 - stats.norm.cdf(np.maximum(UMBRAL, 1.96 * se) / se)
        res[nombre] = {"esperadas_nulo": r2(p.sum()), "observadas": int(celdas["pasa" if nombre == "imagenes" else "pasa_jer"].sum())}
    res["celdas"] = int(len(celdas))
    return res


def main():
    d = pd.read_csv(os.path.join(AF, "modelo_mixto_m3_datos.csv"))
    d = d[d.igual.astype(str) == "True"]
    sal = {}
    orig = json.load(open(os.path.join(AF, "modelo_mixto_m3.json"), encoding="utf-8"))
    tost = {}
    for nombre, clave in (("dosis_habitual", "modelo0_igual_dosis_base"), ("con_H18e", "modelo1_igual")):
        tost[nombre] = {}
        for f in ("NO", "CP", "EX"):
            e = orig[clave]["C(fuente)[%s]" % f]
            se = (e["ic"][1] - e["ic"][0]) / 3.92
            tost[nombre][f] = {"est": e["est"], "IC90": [r2(e["est"] - 1.645 * se), r2(e["est"] + 1.645 * se)],
                               "equivalente_2pp": bool(e["est"] - 1.645 * se > -UMBRAL and e["est"] + 1.645 * se < UMBRAL)}
    sal["tost_modelo_original"] = tost
    for nombre, bloques in (("dosis_habitual", BASE), ("con_H18e", BASE + DOSIS)):
        sub = d[d.bloque.isin(bloques)]
        sal[nombre] = {"mixto_V1_compartida": mixto(sub, True), "mixto_original": mixto(sub, False),
                       "bootstrap_bloques": boot_bloques(sub)}
    c = pd.read_csv(os.path.join(AF, "celdas_con_h18.csv"))
    ctrl = set(c[c.tipo == "control"].etiqueta)
    hab = c[(c.tipo == "real") & c.etiqueta.isin(ctrl) & ~c.etiqueta.str.startswith("H18e")]
    for k in ("pasa", "pasa_jer"):
        hab[k] = hab[k].astype(str) == "True"
    sal["azar_dosis_habitual_con_control"] = azar(hab)
    sal["personas_pegadas_por_imagen_cota"] = {"baja": 0.25 * 1 * 0.5, "habitual": 0.5 * 2 * 0.5, "alta": 1.0 * 3.5 * 0.5,
                                               "nota": "p x E[personas ocluidas] x prob. de silueta de persona (0,5); "
                                                       "cota superior porque no se ocluyen mas personas que las validas"}
    json.dump(sal, open(os.path.join(AF, "revision_10nov.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(AF, "revision_10nov.md"), "w", encoding="utf-8") as fh:
        fh.write("# Analisis posteriores pedidos por la revision del 10/11/2026\n\n```json\n%s\n```\n" % json.dumps(sal, ensure_ascii=False, indent=1))
    print(json.dumps(sal, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
