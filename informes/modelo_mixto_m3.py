#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Analisis global pedido por la revision externa del short paper del 27/10 (observacion M3; posterior,
declarado; no decide ninguna hipotesis).

Modelo lineal mixto del cambio V3 - V1 (AP@0.5, pp) por semilla, con la fuente real como efecto fijo y efectos
aleatorios de bloque y de semilla dentro del bloque:
    delta[b, f, s] = mu_f + u_b + v_{b,s} + e
- Datos: para cada bloque y semilla, AP@0.5 de V3 menos AP@0.5 de V1 de la misma semilla (emparejadas por el numero de
  semilla registrado en eval/*.json), en las tres fuentes reales (NightOwls ocluida, CityPersons heavy, ExDark severa).
- Modelo 1 (primario): bloques con exposicion igual (11). Modelo 1b (sensibilidad): los 17 bloques con control.
- Modelo 2: igual que el 1, mas la ganancia del bloque en su control sintetico (estandarizada), para la relacion
  entre ganancia sintetica y real (OE5).
- Sensibilidad M2: recuento con solo NightOwls y CityPersons, exigiendo que pasen ambas.
- Criterio uniforme de semillas (M1): recuento de las 51 celdas con el IC jerarquico de celdas_completas.csv.
Lee resultados_*/eval/*.json, resultados_*/resumen_ap.csv e informes/analisis_final/celdas_completas.csv.
Escribe informes/analisis_final/modelo_mixto_m3.json y modelo_mixto_m3.md.
Uso: python informes/modelo_mixto_m3.py
"""
import importlib.util
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AF = os.path.join(RAIZ, "informes", "analisis_final")
_s = importlib.util.spec_from_file_location("a11", os.path.join(RAIZ, "11_analisis_estadistico.py"))
A11 = importlib.util.module_from_spec(_s); _s.loader.exec_module(A11)

# clave de celdas_completas, etiqueta, carpeta, filtro de corridas, prefijo de V1 en otra carpeta (H16 usa las V1 de H15)
BLOQUES = [("exp1", "H3", "resultados", dict(excluir_prefijo="yolo26s_")),
           ("iter2", "H4", "resultados_v2", dict(excluir_prefijo="yolo26s_")),
           ("yolo26s", "H4-Y26", "resultados_v2", dict(solo_prefijo="yolo26s_")),
           ("h6", "H6", "resultados_h6", {}), ("h8", "H8", "resultados_h8", {}),
           ("h9", "H9", "resultados_h9", {}), ("h9b", "H9b", "resultados_h9b", {}),
           ("h10g", "H10", "resultados_h10", dict(excluir_prefijo="V3S")),
           ("h10s", "H10-s", "resultados_h10", dict(excluir_prefijo="V3G")),
           ("h11", "H11", "resultados_h11", {}),
           ("h12a", "H12a", "resultados_h12m", dict(excluir_prefijo="yolo11m_V3gen")),
           ("h12b", "H12b", "resultados_h12m", dict(excluir_prefijo="yolo11m_V3sil")),
           ("h14", "H14", "resultados_h14", {}), ("h15", "H15", "resultados_h15", {}),
           ("h16a", "H16a", "resultados_h16", dict(excluir_prefijo=("V3prof", "V1rep"))),
           ("h16b", "H16b", "resultados_h16", dict(excluir_prefijo=("V3gen", "V1rep"))),
           ("h17", "H17", "resultados_h17", {}),
           # H18 (PREREGISTRO_H18.md, v3.12): se incluyen si ya estan evaluados
           ("h18a", "H18a", "resultados_h18", dict(excluir_prefijo=("V3baja", "V3alta"))),
           ("h18e_baja", "H18e-baja", "resultados_h18", dict(excluir_prefijo=("V3sil", "V3alta"))),
           ("h18e_alta", "H18e-alta", "resultados_h18", dict(excluir_prefijo=("V3sil", "V3baja")))]
FUENTE = {"nightowls": "NO", "citypersons_convencion": "CP", "test_proxy": "EX"}


def cargar_celdas():
    """celdas_completas.csv mas las celdas de H18 (contrastes_h18.json), con las mismas columnas. Escribe
    celdas_con_h18.csv cuando H18 esta disponible."""
    c = pd.read_csv(os.path.join(AF, "celdas_completas.csv"))
    ruta = os.path.join(RAIZ, "resultados_h18", "analisis", "contrastes_h18.json")
    if not os.path.exists(ruta):
        return c
    clave = {"H18a": "h18a", "H18e-baja": "h18e_baja", "H18e-alta": "h18e_alta"}
    filas = []
    for f in json.load(open(ruta, encoding="utf-8")):
        filas.append(dict(bloque=clave[f["bloque"]], conjunto=f["conjunto"], estrato=f["estrato"], tipo=f["tipo"],
                          delta=f["delta_pp"], ic_lo=f["IC_img_lo"], ic_hi=f["IC_img_hi"], jer_lo=f["IC_jer_lo"],
                          jer_hi=f["IC_jer_hi"], semillas=f["n_V3"], etiqueta=f["bloque"], exposicion="igual (epocas fijas)",
                          fuente=FUENTE.get(f["conjunto"], "control"),
                          pasa=f["delta_pp"] >= 2 and f["IC_img_lo"] > 0, pasa_jer=f["delta_pp"] >= 2 and f["IC_jer_lo"] > 0,
                          descarta_2pp=f["IC_img_hi"] < 2, descarta_2pp_jer=f["IC_jer_hi"] < 2, negativa_ic=f["IC_img_hi"] < 0))
    c = pd.concat([c, pd.DataFrame(filas)], ignore_index=True)
    c.to_csv(os.path.join(AF, "celdas_con_h18.csv"), index=False)
    return c
REALES = {"NO": ("nightowls", "ocluida"), "CP": ("citypersons_convencion", "heavy"), "EX": ("test_proxy", "severa")}


def deltas_por_semilla(carpeta, filtro, conj, est):
    corr = A11.cargar_corridas(os.path.join(RAIZ, carpeta), **filtro)
    ap = pd.read_csv(os.path.join(RAIZ, carpeta, "resumen_ap.csv"))
    if carpeta == "resultados_h16":       # las V1 de H16 son las de H15 (sus detecciones se copiaron, su AP esta en h15)
        h15 = pd.read_csv(os.path.join(RAIZ, "resultados_h15", "resumen_ap.csv"))
        ap = pd.concat([ap, h15[h15.corrida.str.startswith("V1_s")]])
    ap = ap[(ap.conjunto == conj) & (ap.estrato == est) & (ap.luz == "todas")].drop_duplicates("corrida").set_index("corrida").AP50
    v = {"V1": {}, "V3": {}}
    for k, d in corr.items():
        var = {"V3G": "V3", "V3S": "V3"}.get(d["variante"], d["variante"])
        if var in v and k in ap.index:
            v[var][int(d["semilla"])] = 100 * float(ap[k])
    comunes = sorted(set(v["V1"]) & set(v["V3"]))
    return {s: v["V3"][s] - v["V1"][s] for s in comunes}


def tabla_semillas(celdas):
    filas = []
    exp = celdas.drop_duplicates("bloque").set_index("bloque").exposicion
    ctrl = celdas[celdas.tipo == "control"].set_index("bloque")
    for clave, etq, carpeta, filtro in BLOQUES:
        if clave not in exp.index:
            continue
        for f, (conj, est) in REALES.items():
            for s, dl in deltas_por_semilla(carpeta, filtro, conj, est).items():
                filas.append(dict(bloque=etq, fuente=f, semilla="%s_s%d" % (etq, s), delta=dl,
                                  igual=exp[clave].startswith("igual"), control=float(ctrl.delta[clave])))
    return pd.DataFrame(filas)


def ajustar(d, con_control=False):
    import statsmodels.formula.api as smf
    d = d.copy()
    form = "delta ~ 0 + C(fuente)"
    if con_control:
        g = d.groupby("bloque").control.first()
        d["z_control"] = (d.control - g.mean()) / g.std(ddof=1)
        form += " + z_control"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = smf.mixedlm(form, d, groups="bloque", re_formula="1", vc_formula={"semilla": "0 + C(semilla)"}).fit(reml=True)
    ci = m.conf_int()
    out = {k: {"est": round(float(m.params[k]), 2), "ic": [round(float(ci.loc[k, 0]), 2), round(float(ci.loc[k, 1]), 2)]}
           for k in m.params.index if k.startswith("C(fuente)") or k == "z_control"}
    out["var_bloque"] = round(float(m.cov_re.iloc[0, 0]), 2)
    out["var_semilla"] = round(float(m.vcomp[0]), 2)
    out["var_residual"] = round(float(m.scale), 2)
    out["n_obs"], out["n_bloques"] = int(len(d)), int(d.bloque.nunique())
    out["convergio"] = bool(m.converged)
    return out


def recuentos(celdas):
    r = celdas[(celdas.tipo == "real") & (celdas.bloque != "h7")].copy()
    igual = r[r.exposicion.str.startswith("igual")]
    out = {}
    base = ~r.etiqueta.astype(str).str.startswith("H18e")
    for nombre, x in (("igual_33", igual), ("todos_51", r), ("igual_dosis_base", igual[base]), ("todos_dosis_base", r[base])):
        out[nombre] = {"celdas": len(x), "pasan_img": int(x.pasa.sum()), "pasan_jer": int(x.pasa_jer.sum()),
                       "descartan_img": int(x.descarta_2pp.sum()), "descartan_jer": int(x.descarta_2pp_jer.sum()),
                       "no_concluyentes_img": int(len(x) - x.pasa.sum() - x.descarta_2pp.sum()),
                       "no_concluyentes_jer": int(len(x) - x.pasa_jer.sum() - x.descarta_2pp_jer.sum()),
                       "pasan_jer_lista": sorted("%s-%s" % (a, b) for a, b in x[x.pasa_jer][["etiqueta", "fuente"]].values)}
    # sensibilidad sin EX (M2): un bloque detecta transferencia si pasan NightOwls y CityPersons
    sin_ex = {}
    for etq, g in r[r.fuente != "EX"].groupby("etiqueta"):
        sin_ex[etq] = {"pasan_img": int(g.pasa.sum()), "pasan_jer": int(g.pasa_jer.sum())}
    out["sin_EX"] = {"bloques_ambas_img": sorted(k for k, v in sin_ex.items() if v["pasan_img"] == 2),
                     "bloques_ambas_jer": sorted(k for k, v in sin_ex.items() if v["pasan_jer"] == 2),
                     "celdas": int((r.fuente != "EX").sum()), "pasan_img": int(r[r.fuente != "EX"].pasa.sum()),
                     "pasan_jer": int(r[r.fuente != "EX"].pasa_jer.sum())}
    return out


def main():
    celdas = cargar_celdas()
    d = tabla_semillas(celdas)
    base_no = d.bloque.str.startswith("H18e")
    res = {"datos": {"observaciones": int(len(d)), "bloques": int(d.bloque.nunique()),
                     "por_bloque": d.groupby("bloque").semilla.nunique().to_dict()},
           # primario: dosis base (las H18e cambian la dosis del aumento, otra manipulacion; van aparte)
           "modelo0_igual_dosis_base": ajustar(d[d.igual & ~base_no]),
           "modelo0b_todos_dosis_base": ajustar(d[~base_no]),
           "modelo0c_igual_dosis_base_con_control": ajustar(d[d.igual & ~base_no], con_control=True),
           "modelo1_igual": ajustar(d[d.igual]), "modelo1b_todos": ajustar(d),
           "modelo2_igual_con_control": ajustar(d[d.igual], con_control=True),
           "modelo2b_todos_con_control": ajustar(d, con_control=True), "recuentos": recuentos(celdas)}
    d.to_csv(os.path.join(AF, "modelo_mixto_m3_datos.csv"), index=False)
    json.dump(res, open(os.path.join(AF, "modelo_mixto_m3.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    L = ["# Modelo mixto global (M3) y recuentos uniformes (M1, M2)", "",
         "Generado por `informes/modelo_mixto_m3.py` (análisis posterior, declarado; no decide hipótesis).", "",
         "Modelo: Δ = μ_fuente + u_bloque + v_semilla(bloque) + e, REML, Δ = V3 − V1 en AP@0.5 (pp) por semilla.", "",
         "| Modelo | NightOwls | CityPersons | ExDark | Ganancia sintética (por DE) | Var. bloque | Var. semilla | Var. residual | n |",
         "|---|---|---|---|---|---|---|---|---|"]
    for k, m in res.items():
        if not k.startswith("modelo"):
            continue
        g = lambda f: "%+.2f [%+.2f; %+.2f]" % (m[f]["est"], *m[f]["ic"]) if f in m else "—"
        L.append("| %s | %s | %s | %s | %s | %.2f | %.2f | %.2f | %d obs., %d bloques |" % (
            k, g("C(fuente)[NO]"), g("C(fuente)[CP]"), g("C(fuente)[EX]"), g("z_control"), m["var_bloque"],
            m["var_semilla"], m["var_residual"], m["n_obs"], m["n_bloques"]))
    L += ["", "## Recuentos", "", "```", json.dumps(res["recuentos"], indent=1, ensure_ascii=False), "```"]
    open(os.path.join(AF, "modelo_mixto_m3.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    print(json.dumps(res["datos"], ensure_ascii=False))


if __name__ == "__main__":
    main()
