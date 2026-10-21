#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Analisis para la revision del short paper (20/10/2026). Declarados como posteriores; no deciden ninguna
hipotesis y no recalculan AP: leen las tablas de resultados ya publicadas.

1. Tabla completa de celdas (13 bloques con control + H7): V3 - V1, IC por imagenes y jerarquico, semillas y regla de
   exposicion (obs. 3, 4 y 6). Para H11 se calcula el IC jerarquico de las celdas estandar con 23_ (no existia).
2. Recuento unico de lo que "pasa" (estimacion >= +2 pp y IC por imagenes > 0), por grupo de exposicion y sin el
   indicador de ExDark (obs. 4 y 7).
3. No superioridad (obs. 8): una celda descarta una ganancia de +2 pp si el limite superior de su IC 95 % es < +2
   (prueba unilateral al 2,5 %, la mitad superior de dos pruebas unilaterales).
4. Justificacion del umbral (obs. 8): desviacion tipica entre semillas del AP@0.5 de V1 en las fuentes reales.
5. IC bootstrap de los rho de Spearman por fuente (remuestreo de bloques) y modelo mixto (obs. 8).
Salidas: informes/analisis_final/celdas_completas.csv y revision_sp.json; resumen en pantalla.
Uso: python informes/revision_sp_analisis.py
"""
import glob
import importlib.util
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
AF = os.path.join(RAIZ, "informes", "analisis_final")
REALES = [("nightowls", "ocluida", "NO"), ("citypersons_convencion", "heavy", "CP"), ("test_proxy", "severa", "EX")]
UMBRAL = 2.0
SEL, FIJA, TEMP = "desigual (seleccion por validacion)", "igual (epocas fijas)", "seleccion temprana en ambas"
# clave, etiqueta del short paper, exposicion, semillas
BLOQUES = [("exp1", "H3", TEMP), ("iter2", "H4", SEL), ("yolo26s", "H4-Y26", SEL), ("h6", "H6", SEL), ("h7", "H7", SEL),
           ("h8", "H8", SEL), ("h9", "H9", TEMP), ("h9b", "H9b", FIJA), ("h10g", "H10", FIJA), ("h10s", "H10-s", FIJA),
           ("h11", "H11", FIJA), ("h12a", "H12a", FIJA), ("h12b", "H12b", FIJA), ("h14", "H14", FIJA), ("h15", "H15", FIJA)]


def _mod(nombre, archivo):
    sp = importlib.util.spec_from_file_location(nombre, os.path.join(RAIZ, archivo))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def jerarquico_h11():
    ruta = os.path.join(AF, "bootstrap_jerarquico_h11.csv")
    if not os.path.exists(ruta):
        B23 = _mod("b23", "23_bootstrap_jerarquico.py")
        B23.analizar(2000, 0, bloques=[("h11", "resultados_h11", {}, ("cp_silueta_severa", "severa"))]).to_csv(ruta, index=False)
    return pd.read_csv(ruta)


def celdas():
    filas = []
    t = pd.read_csv(os.path.join(AF, "tabla_consolidada.csv"))
    j = pd.concat([pd.read_csv(os.path.join(AF, "bootstrap_jerarquico.csv")),
                   pd.read_csv(os.path.join(AF, "bootstrap_jerarquico_secundarios.csv")), jerarquico_h11()])
    j = j[j.contraste == "V3-V1"]

    def de_tablas(clave, b_cons, b_jer, control, sem=3, b_img=None):
        out = []
        for conj, est, tipo in [(control, "severa", "control")] + [(c, e, "real") for c, e, _ in REALES]:
            if conj is None:
                continue
            if b_img is not None:
                r = b_img[(b_img.conjunto == conj) & (b_img.estrato == est)].iloc[0]
                d, lo, hi = r.delta_AP50_pp, r.IC95_lo_pp, r.IC95_hi_pp
            else:
                r = t[(t.bloque == b_cons) & (t.conjunto == conj) & (t.estrato == est)].iloc[0]
                d, lo, hi = r.delta_pp, r.IC95_lo, r.IC95_hi
            rj = j[(j.bloque == b_jer) & (j.conjunto == conj) & (j.estrato == est)]
            jl, jh = (rj.iloc[0].IC_jerarquico_lo, rj.iloc[0].IC_jerarquico_hi) if len(rj) else (np.nan, np.nan)
            out.append(dict(bloque=clave, conjunto=conj, estrato=est, tipo=tipo, delta=round(float(d), 2), ic_lo=round(float(lo), 2),
                            ic_hi=round(float(hi), 2), jer_lo=jl, jer_hi=jh, semillas=sem))
        return out
    ctrl = {"exp1": "opaco_severa", "iter2": "silueta_severa", "yolo26s": "silueta_severa", "h6": "cp_silueta_severa",
            "h7": None, "h8": "silueta_severa", "h9": "generativa_severa"}
    for k, c in ctrl.items():
        filas += de_tablas(k, k, k, c)
    filas += de_tablas("h9b", None, "h9b", "generativa_severa",
                       b_img=pd.read_csv(os.path.join(RAIZ, "resultados_h9b", "analisis", "bootstrap.csv")).query("contraste == 'V3-V1'"))
    filas += de_tablas("h11", None, "h11", "cp_silueta_severa",
                       b_img=pd.read_csv(os.path.join(RAIZ, "resultados_h11", "analisis", "bootstrap.csv")).query("contraste == 'V3-V1'"))
    h10 = pd.read_csv(os.path.join(RAIZ, "resultados_h10", "analisis", "contrastes_h10.csv"))
    for clave, con, control in (("h10g", "V3G-V1", "geometria_severa"), ("h10s", "V3S-V1", "silueta_severa")):
        s = h10[h10.contraste == con]
        for conj, est, tipo in [(control, "severa", "control")] + [(c, e, "real") for c, e, _ in REALES]:
            r = s[(s.conjunto == conj) & (s.estrato == est)].iloc[0]
            filas.append(dict(bloque=clave, conjunto=conj, estrato=est, tipo=tipo, delta=r.delta_pp, ic_lo=r.IC_imagenes_lo,
                              ic_hi=r.IC_imagenes_hi, jer_lo=r.IC_jerarquico_lo, jer_hi=r.IC_jerarquico_hi, semillas=3))
    for clave, ruta, b in (("h12a", "resultados_h12/analisis/contrastes_h12.json", "H12a"),
                           ("h12b", "resultados_h12/analisis/contrastes_h12.json", "H12b"),
                           ("h14", "resultados_h14/analisis/contrastes_h14.json", "H14"),
                           ("h15", "resultados_h15/analisis/contrastes_h15.json", "H15")):
        if not os.path.exists(os.path.join(RAIZ, ruta)):
            continue
        for f in json.load(open(os.path.join(RAIZ, ruta), encoding="utf-8")):
            if f.get("bloque", b) != b or f["tipo"] not in ("control", "real"):
                continue
            filas.append(dict(bloque=clave, conjunto=f["conjunto"], estrato=f["estrato"], tipo=f["tipo"], delta=f["delta_pp"],
                              ic_lo=f["IC_img_lo"], ic_hi=f["IC_img_hi"], jer_lo=f["IC_jer_lo"], jer_hi=f["IC_jer_hi"], semillas=3))
    d = pd.DataFrame(filas)
    meta = {k: (et, ex) for k, et, ex in BLOQUES}
    d["etiqueta"] = d.bloque.map(lambda k: meta[k][0])
    d["exposicion"] = d.bloque.map(lambda k: meta[k][1])
    d["fuente"] = d.apply(lambda r: next((s for c, e, s in REALES if c == r.conjunto and e == r.estrato), "control"), axis=1)
    d["pasa"] = (d.delta >= UMBRAL) & (d.ic_lo > 0)
    d["pasa_jer"] = (d.delta >= UMBRAL) & (d.jer_lo > 0)
    d["descarta_2pp"] = d.ic_hi < UMBRAL
    d["descarta_2pp_jer"] = d.jer_hi < UMBRAL
    d["negativa_ic"] = d.ic_hi < 0
    return d


def main():
    d = celdas()
    d.to_csv(os.path.join(AF, "celdas_completas.csv"), index=False)
    con = d[d.bloque != "h7"]
    base = con[con.bloque != "h15"]
    reales = base[base.tipo == "real"]
    res = {"bloques_con_control": int(base.bloque.nunique()), "controles_pasan": int(base[base.tipo == "control"].pasa.sum()),
           "celdas_reales": len(reales), "pasan": int(reales.pasa.sum()),
           "pasan_lista": reales[reales.pasa][["etiqueta", "fuente", "delta", "ic_lo", "ic_hi", "jer_lo", "jer_hi"]].values.tolist(),
           "pasan_jer": int(reales.pasa_jer.sum()), "negativas": int((reales.delta < 0).sum()), "negativas_ic": int(reales.negativa_ic.sum()),
           "descartan_2pp": int(reales.descarta_2pp.sum()), "descartan_2pp_jer": int(reales.descarta_2pp_jer.sum())}
    por_exp = {}
    for ex, g in reales.groupby("exposicion"):
        por_exp[ex] = {"bloques": sorted(g.etiqueta.unique()), "celdas": len(g), "pasan": int(g.pasa.sum()),
                       "negativas": int((g.delta < 0).sum()), "negativas_ic": int(g.negativa_ic.sum()),
                       "descartan_2pp": int(g.descarta_2pp.sum()), "media_delta": round(float(g.delta.mean()), 2)}
    res["por_exposicion"] = por_exp
    sin_ex = reales[reales.fuente != "EX"]
    veredictos_sin_ex = {b: int(g.pasa.sum()) for b, g in sin_ex.groupby("etiqueta")}
    res["sin_indicador_exdark"] = {"celdas": len(sin_ex), "pasan": int(sin_ex.pasa.sum()),
                                   "bloques_con_2_de_2": [b for b, n in veredictos_sin_ex.items() if n >= 2]}
    # umbral: desviacion tipica entre semillas del AP@0.5 de V1 (pp) en las fuentes reales
    sd = []
    for dres in ["resultados", "resultados_v2", "resultados_h6", "resultados_h8", "resultados_h9b", "resultados_h11", "resultados_h12m", "resultados_h14"]:
        p = os.path.join(RAIZ, dres, "resumen_ap.csv")
        if not os.path.exists(p):
            continue
        r = pd.read_csv(p)
        r = r[(r.variante == "V1") & (r.luz == "todas")]
        for c, e, s in REALES:
            for pref, g in r[(r.conjunto == c) & (r.estrato == e)].groupby(r.corrida.str.extract(r"^(.*)_s\d+$")[0]):
                if len(g) >= 3:
                    sd.append({"resultados": dres, "fuente": s, "grupo": pref, "sd_pp": round(100 * g.AP50.std(ddof=1), 2)})
    sd = pd.DataFrame(sd)
    res["sd_semillas_V1"] = {"n": len(sd), "mediana_pp": round(float(sd.sd_pp.median()), 2), "max_pp": round(float(sd.sd_pp.max()), 2),
                             "por_fuente": sd.groupby("fuente").sd_pp.median().round(2).to_dict()}
    # rho por fuente con IC bootstrap sobre bloques
    piv = con[con.tipo == "control"][["bloque", "delta"]].rename(columns={"delta": "sint"}).set_index("bloque")
    for _, _, s in REALES:
        piv[s] = con[(con.fuente == s)].set_index("bloque").delta
    piv13 = piv.drop(index=[b for b in piv.index if b == "h15"])
    rnd = np.random.RandomState(0)
    rho = {}
    for s in ("NO", "CP", "EX"):
        r0 = spearmanr(piv13.sint, piv13[s]).statistic
        bs = []
        for _ in range(10000):
            i = rnd.randint(0, len(piv13), len(piv13))
            x, y = piv13.sint.values[i], piv13[s].values[i]
            if len(np.unique(x)) > 2 and len(np.unique(y)) > 2:
                bs.append(spearmanr(x, y).statistic)
        rho[s] = {"rho": round(float(r0), 2), "IC95": [round(float(np.percentile(bs, 2.5)), 2), round(float(np.percentile(bs, 97.5)), 2)]}
    res["rho_ic_bloques"] = rho
    # modelo mixto: ganancia real ~ ganancia sintetica (estandarizada) + fuente, intercepto aleatorio por bloque
    import statsmodels.formula.api as smf
    largo = piv13.reset_index().melt(id_vars=["bloque", "sint"], value_vars=["NO", "CP", "EX"], var_name="fuente", value_name="real")
    largo["sint_z"] = (largo.sint - largo.sint.mean()) / largo.sint.std()
    m = smf.mixedlm("real ~ sint_z + C(fuente)", largo, groups=largo["bloque"]).fit(reml=True)
    ci = m.conf_int().loc["sint_z"].tolist()
    res["modelo_mixto"] = {"pendiente_pp_por_DE": round(float(m.params["sint_z"]), 2), "IC95": [round(ci[0], 2), round(ci[1], 2)],
                           "p": round(float(m.pvalues["sint_z"]), 3), "DE_sintetico_pp": round(float(largo.sint.std()), 2)}
    # sin H3 (fuera de escala, +60,9)
    l2 = largo[largo.bloque != "exp1"].copy()
    l2["sint_z"] = (l2.sint - l2.sint.mean()) / l2.sint.std()
    m2 = smf.mixedlm("real ~ sint_z + C(fuente)", l2, groups=l2["bloque"]).fit(reml=True)
    ci2 = m2.conf_int().loc["sint_z"].tolist()
    res["modelo_mixto_sin_H3"] = {"pendiente_pp_por_DE": round(float(m2.params["sint_z"]), 2), "IC95": [round(ci2[0], 2), round(ci2[1], 2)],
                                  "p": round(float(m2.pvalues["sint_z"]), 3)}
    json.dump(res, open(os.path.join(AF, "revision_sp.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
    print(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
