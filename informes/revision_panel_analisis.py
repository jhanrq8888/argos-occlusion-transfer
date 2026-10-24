#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Reanalisis pedidos por el panel de revision del 22/10/2026 (shortpaper5/revision_panel_22oct/). Todos son
ANALISIS POSTERIORES declarados: no cambian ninguna regla ni ningun veredicto prerregistrado. Solo leen ficheros
existentes (detecciones cacheadas en resultados_*/det, celdas_completas.csv, resumen_ap.csv, contrastes de H15-H17).

  O14/O4c  especificidad: [V3-V1](personas ocluidas) - [V3-V1](personas sin oclusion) de la misma fuente, con IC por
           imagenes (mismas imagenes remuestreadas para los dos estratos) y jerarquico, en los 18 bloques
  O11      CityPersons repuntuado con la caja VISIBLE (bboxVis de anno_val.mat) en lugar de la caja completa
  O3       recuento primario unico: 33 celdas con exposicion igual (H9b-H17), pasan / descartan +2 / no concluyentes
  O1       rho de Spearman sintetico-real con 17 bloques y solo con exposicion igual, IC bootstrap de bloques
  O10      media por fuente con IC bootstrap de bloques (exposicion igual)
  O6       potencia de la regla «2 de 3» con +2 pp verdaderos y equivalencia agregada por fuente (efectos aleatorios,
           TOST con margenes +-2 pp, IC 90 %)
  O8       IC de H15 y de las celdas que pasan con la varianza entre semillas (t de Welch, pocos gl)
  O9       multiplicidad: pases esperados bajo el nulo y probabilidad de que algun bloque llegue a «2 de 3» por azar
  O7c      H16 frente a la replica de V1 en otra maquina
  O16      matriz cruzada de controles de los detectores de torchvision (H15-H17)
Salida: informes/analisis_final/revision_panel.json, especificidad.csv, citypersons_visible.csv, cruzada_torchvision.csv
Uso: python informes/revision_panel_analisis.py [--replicas 1000] [--procesos 6]   |   --selftest
"""
import argparse
import importlib.util
import json
import os
import sys
from multiprocessing import Pool

import numpy as np
import pandas as pd
from scipy import stats

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
AF = os.path.join(RAIZ, "informes", "analisis_final")
UMBRAL = 2.0
_sp = importlib.util.spec_from_file_location("analisis11", os.path.join(RAIZ, "11_analisis_estadistico.py"))
A11 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(A11)
from argos_lib.ap import emparejar_conjunto                                  # noqa: E402
from argos_lib.gt import cargar_detecciones, cargar_gt                       # noqa: E402

# clave, etiqueta del short paper, carpeta, filtro de corridas (como informes/mr_bloques_recientes.py y 23_)
BLOQUES = [("exp1", "H3", "resultados", dict(excluir_prefijo="yolo26s_")),
           ("iter2", "H4", "resultados_v2", dict(excluir_prefijo="yolo26s_")),
           ("yolo26s", "H4-Y26", "resultados_v2", dict(solo_prefijo="yolo26s_")),
           ("h6", "H6", "resultados_h6", {}), ("h7", "H7", "resultados_h7_20000", {}), ("h8", "H8", "resultados_h8", {}),
           ("h9", "H9", "resultados_h9", {}), ("h9b", "H9b", "resultados_h9b", {}),
           ("h10g", "H10", "resultados_h10", dict(excluir_prefijo="V3S")),
           ("h10s", "H10-s", "resultados_h10", dict(excluir_prefijo="V3G")),
           ("h11", "H11", "resultados_h11", {}),
           ("h12a", "H12a", "resultados_h12m", dict(excluir_prefijo="yolo11m_V3gen")),
           ("h12b", "H12b", "resultados_h12m", dict(excluir_prefijo="yolo11m_V3sil")),
           ("h14", "H14", "resultados_h14", {}), ("h15", "H15", "resultados_h15", {}),
           ("h16a", "H16a", "resultados_h16", dict(excluir_prefijo=("V3prof", "V1rep"))),
           ("h16b", "H16b", "resultados_h16", dict(excluir_prefijo=("V3gen", "V1rep"))),
           ("h17", "H17", "resultados_h17", {})]
# fuente: (conjunto, estrato ocluido, estrato sin oclusion)
PARES = {"NO": ("nightowls", "ocluida", "sin"), "CP": ("citypersons_convencion", "heavy", "bare"),
         "EX": ("test_proxy", "severa", "sin")}
GT_CP = os.path.join(RAIZ, "dataset", "externos", "gt_citypersons_convencion.json")


def corridas_de(carpeta, filtro):
    c = A11.cargar_corridas(os.path.join(RAIZ, carpeta), **filtro)
    out = {}
    for k, d in c.items():
        v = {"V3G": "V3", "V3S": "V3"}.get(d["variante"], d["variante"])
        if v in ("V1", "V3"):
            out[k] = (v, d["conjuntos"])
    return out


def gt_visible():
    """GT de CityPersons (convencion) con la caja VISIBLE (bboxVis de anno_val.mat) para las personas de los estratos
    bare/partial/heavy; las regiones ignorar conservan su caja. Las ids son <imagen>#<fila del .mat> (12_)."""
    from scipy.io import loadmat
    gt = cargar_gt(GT_CP)
    m = loadmat(os.path.join(RAIZ, "externos", "citypersons", "anno_val.mat"), squeeze_me=True, struct_as_record=False)
    reg = m[next(k for k in m if k.startswith("anno"))]
    vis = {}
    for r in reg:
        base = os.path.splitext(str(r.im_name))[0]
        filas = [f for f in np.atleast_2d(np.asarray(r.bbs, dtype=float)) if len(f) >= 10]   # como 12_
        for k, f in enumerate(filas):
            vis["%s#%d" % (base, k)] = (f[6], f[7], f[6] + f[8], f[7] + f[9])
    n = 0
    for im in gt["imagenes"].values():
        for i in im["instancias"]:
            if i.get("estrato") in ("bare", "partial", "heavy"):
                i["x1"], i["y1"], i["x2"], i["y2"] = [float(v) for v in vis[i["id"]]]
                n += 1
    gt["n_cambiadas"] = n
    return gt


def _est(emparejar_gt, ruta_det, est):
    emp, _ = emparejar_conjunto(emparejar_gt, cargar_detecciones(ruta_det)["detecciones"], estrato=est)
    return A11.APBootstrap(emp)


def ic(x):
    return float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))


def analizar_bloque(args):
    clave, etq, carpeta, filtro, B = args
    rnd = np.random.RandomState(abs(hash(clave)) % (2 ** 31))
    corr = corridas_de(carpeta, filtro)
    filas = []
    fuentes = dict(PARES)
    fuentes["CPvis"] = PARES["CP"]
    gtv = None
    for f, (conj, eo, ev) in fuentes.items():
        if f == "CPvis":
            gtv = gtv or gt_visible()
            gimg = gtv["imagenes"]
        else:
            ruta_gt = next((d[conj] for _, d in corr.values() if conj in d), None)
            if ruta_gt is None:
                continue
            gimg = cargar_gt(ruta_gt)["imagenes"]
        S = {}
        for c, (v, _) in corr.items():
            ruta = os.path.join(RAIZ, carpeta, "det", "%s__%s.json" % (c, conj))
            if os.path.exists(ruta):
                S[c] = (v, {e: _est(gimg, ruta, e) for e in ((eo, ev, "partial") if f.startswith("CP") else (eo, ev))})
        if not S:
            continue
        estratos = list(next(iter(S.values()))[1])
        por = {v: [c for c, (vv, _) in S.items() if vv == v] for v in ("V1", "V3")}
        n_img = next(iter(S.values()))[1][eo].n_img
        full = {e: {c: S[c][1][e].ap() for c in S} for e in estratos}
        d0 = {e: np.mean([full[e][c] for c in por["V3"]]) - np.mean([full[e][c] for c in por["V1"]]) for e in estratos}
        bi = {e: np.zeros(B) for e in estratos}
        bj = {e: np.zeros(B) for e in estratos}
        for b in range(B):
            w = np.bincount(rnd.randint(0, n_img, n_img), minlength=n_img).astype(float)
            sel = {v: np.array(cs)[rnd.randint(0, len(cs), len(cs))] for v, cs in por.items()}
            for e in estratos:
                a = {c: S[c][1][e].ap(w) for c in S}
                bi[e][b] = np.mean([a[c] for c in por["V3"]]) - np.mean([a[c] for c in por["V1"]])
                bj[e][b] = np.mean([a[c] for c in sel["V3"]]) - np.mean([a[c] for c in sel["V1"]])
        fila = {"bloque": clave, "etiqueta": etq, "fuente": f, "n_V1": len(por["V1"]), "n_V3": len(por["V3"])}
        for e in estratos:
            fila["d_%s" % e] = round(100 * d0[e], 2)
            fila["d_%s_lo" % e], fila["d_%s_hi" % e] = [round(100 * x, 2) for x in ic(bi[e])]
            fila["AP_V1_%s" % e] = round(np.mean([full[e][c] for c in por["V1"]]), 4)
        esp, espj = bi[eo] - bi[ev], bj[eo] - bj[ev]
        fila.update({"especificidad": round(100 * (d0[eo] - d0[ev]), 2),
                     "esp_lo": round(100 * ic(esp)[0], 2), "esp_hi": round(100 * ic(esp)[1], 2),
                     "esp_jer_lo": round(100 * ic(espj)[0], 2), "esp_jer_hi": round(100 * ic(espj)[1], 2)})
        filas.append(fila)
    print("  %-7s listo (%d fuentes)" % (etq, len(filas)), flush=True)
    return filas


# ------------------------------------------------------------------------------------------- analisis sobre tablas
def boot_bloques(x, B=10000, semilla=0, fun=np.mean):
    x = np.asarray(x, float)
    r = np.random.RandomState(semilla)
    return ic(np.array([fun(x[r.randint(0, len(x), len(x))]) for _ in range(B)]))


def spearman_ic(a, b, B=10000, semilla=0):
    a, b = np.asarray(a, float), np.asarray(b, float)
    r = np.random.RandomState(semilla)
    v = []
    for _ in range(B):
        i = r.randint(0, len(a), len(a))
        if len(set(a[i])) > 1 and len(set(b[i])) > 1:
            v.append(stats.spearmanr(a[i], b[i]).statistic)
    return float(stats.spearmanr(a, b).statistic), ic(np.array(v))


def p_pasa(mu, se):
    """P(estimacion >= +2 y limite inferior del IC 95 % > 0) si el efecto verdadero es mu (normal)."""
    return float(1 - stats.norm.cdf((max(UMBRAL, 1.96 * se) - mu) / se))


def dos_de_tres(p):
    p1, p2, p3 = p
    return p1 * p2 + p1 * p3 + p2 * p3 - 2 * p1 * p2 * p3


def efectos_aleatorios(y, se):
    """DerSimonian-Laird. Devuelve media, IC 90 % (para TOST con margenes +-2) e IC 95 %, tau."""
    y, v = np.asarray(y, float), np.asarray(se, float) ** 2
    w = 1 / v
    mf = np.sum(w * y) / np.sum(w)
    q = np.sum(w * (y - mf) ** 2)
    tau2 = max(0.0, (q - (len(y) - 1)) / (np.sum(w) - np.sum(w ** 2) / np.sum(w)))
    ws = 1 / (v + tau2)
    m = np.sum(ws * y) / np.sum(ws)
    s = np.sqrt(1 / np.sum(ws))
    return {"media": round(m, 2), "IC90": [round(m - 1.645 * s, 2), round(m + 1.645 * s, 2)],
            "IC95": [round(m - 1.96 * s, 2), round(m + 1.96 * s, 2)], "tau": round(float(np.sqrt(tau2)), 2),
            "equivalente_2pp": bool(m - 1.645 * s > -UMBRAL and m + 1.645 * s < UMBRAL), "k": len(y)}


def ap_por_semilla(carpeta, prefijos, conj, est):
    d = pd.read_csv(os.path.join(RAIZ, carpeta, "resumen_ap.csv"))
    d = d[(d.conjunto == conj) & (d.estrato == est) & (d.luz == "todas")]
    return {p: d[d.corrida.str.match(p)].AP50.values * 100 for p in prefijos}


def analisis_tablas(esp):
    d = pd.read_csv(os.path.join(AF, "celdas_completas.csv"))
    d = d[d.bloque != "h7"]
    reales = d[d.tipo == "real"].copy()
    reales["se"] = (reales.ic_hi - reales.ic_lo) / 3.92
    igual = reales[reales.exposicion == "igual (epocas fijas)"]
    out = {}
    # O3
    out["recuento_primario"] = {"bloques": int(igual.bloque.nunique()), "celdas": len(igual), "pasan": int(igual.pasa.sum()),
                                "pasan_jer": int(igual.pasa_jer.sum()), "descartan_2pp": int(igual.descarta_2pp.sum()),
                                "descartan_2pp_jer": int(igual.descarta_2pp_jer.sum()),
                                "no_concluyentes": int(len(igual) - igual.pasa.sum() - igual.descarta_2pp.sum()),
                                "pasan_lista": igual[igual.pasa][["etiqueta", "fuente", "delta"]].values.tolist()}
    out["recuento_todas"] = {"bloques": int(reales.bloque.nunique()), "celdas": len(reales), "pasan": int(reales.pasa.sum()),
                             "descartan_2pp": int(reales.descarta_2pp.sum())}
    # O10
    out["media_por_fuente_igual"] = {}
    for s, g in igual.groupby("fuente"):
        lo, hi = boot_bloques(g.delta.values)
        out["media_por_fuente_igual"][s] = {"media": round(g.delta.mean(), 2), "IC_bloques": [round(lo, 2), round(hi, 2)],
                                            "positivas": int((g.delta > 0).sum()), "k": len(g)}
    lo, hi = boot_bloques(igual.groupby("bloque").delta.mean().values)
    out["media_global_igual"] = {"media": round(igual.delta.mean(), 3), "IC_bloques": [round(lo, 2), round(hi, 2)]}
    # O1
    ctrl = d[d.tipo == "control"].set_index("bloque").delta
    out["spearman"] = {}
    for nombre, sub in (("17_bloques", reales), ("exposicion_igual", igual)):
        out["spearman"][nombre] = {}
        for s, g in sub.groupby("fuente"):
            g = g.set_index("bloque")
            r, (lo, hi) = spearman_ic(ctrl[g.index].values, g.delta.values)
            out["spearman"][nombre][s] = {"rho": round(r, 2), "IC95": [round(lo, 2), round(hi, 2)], "n": len(g)}
    # O6
    pot = []
    for b, g in igual.groupby("etiqueta"):
        g = g.set_index("fuente")
        if len(g) == 3:
            pot.append({"bloque": b, "p_2de3_si_+2": round(dos_de_tres([p_pasa(2.0, g.se[s]) for s in ("NO", "CP", "EX")]), 3),
                        "p_2de3_si_+3": round(dos_de_tres([p_pasa(3.0, g.se[s]) for s in ("NO", "CP", "EX")]), 3)})
    pot = pd.DataFrame(pot)
    out["potencia_regla"] = {"mediana_p_detectar_+2": round(pot["p_2de3_si_+2"].median(), 3),
                             "rango_+2": [round(pot["p_2de3_si_+2"].min(), 3), round(pot["p_2de3_si_+2"].max(), 3)],
                             "mediana_p_detectar_+3": round(pot["p_2de3_si_+3"].median(), 3), "por_bloque": pot.to_dict("records")}
    out["equivalencia_por_fuente"] = {s: efectos_aleatorios(g.delta, g.se) for s, g in igual.groupby("fuente")}
    # O9
    p0 = np.array([p_pasa(0.0, s) for s in reales.se])
    blo = [dos_de_tres([p_pasa(0.0, s) for s in g.sort_values("fuente").se]) for _, g in reales.groupby("bloque") if len(g) == 3]
    out["multiplicidad"] = {"celdas": len(reales), "pases_esperados_nulo": round(float(p0.sum()), 2), "pases_observados": int(reales.pasa.sum()),
                            "p_algun_bloque_2de3_nulo": round(float(1 - np.prod(1 - np.array(blo))), 3), "bloques": len(blo)}
    # version conservadora: error tipico del IC jerarquico (incluye la varianza entre semillas)
    sej = (reales.jer_hi - reales.jer_lo) / 3.92
    p0j = np.array([p_pasa(0.0, s) for s in sej])
    reales["sej"] = sej
    bloj = [dos_de_tres([p_pasa(0.0, s) for s in g.sort_values("fuente").sej]) for _, g in reales.groupby("bloque") if len(g) == 3]
    out["multiplicidad"].update({"pases_esperados_nulo_jer": round(float(p0j.sum()), 2),
                                 "p_algun_bloque_2de3_nulo_jer": round(float(1 - np.prod(1 - np.array(bloj))), 3)})
    # O8: t de Welch con los AP por semilla
    casos = [("H15", "resultados_h15", "V1_s", "V3sil_s"), ("H9", "resultados_h9", "V1_s", "V3_s"), ("H14", "resultados_h14", "V1_s", "V3_s"),
             ("H10", "resultados_h10", "V1_s", "V3G_s"), ("H10-s", "resultados_h10", "V1_s", "V3S_s")]
    out["ic_semillas"] = []
    for etq, carp, p1, p3 in casos:
        for s, (conj, eo, _) in PARES.items():
            a = ap_por_semilla(carp, [p1, p3], conj, eo)
            x1, x3 = a[p1], a[p3]
            if len(x1) < 2 or len(x3) < 2:
                continue
            dlt = x3.mean() - x1.mean()
            se = np.sqrt(x3.var(ddof=1) / len(x3) + x1.var(ddof=1) / len(x1))
            gl = se ** 4 / ((x3.var(ddof=1) / len(x3)) ** 2 / (len(x3) - 1) + (x1.var(ddof=1) / len(x1)) ** 2 / (len(x1) - 1))
            t = stats.t.ppf(0.975, gl)
            out["ic_semillas"].append({"bloque": etq, "fuente": s, "delta": round(dlt, 2), "IC_t": [round(dlt - t * se, 2), round(dlt + t * se, 2)],
                                       "gl": round(float(gl), 1), "n": [len(x1), len(x3)]})
    # O7c: H16 frente a la replica de V1 (una semilla) en otra maquina
    rep = []
    for s, (conj, eo, _) in PARES.items():
        a = ap_por_semilla("resultados_h16", ["V1rep_s0", "V3gen_s", "V3prof_s"], conj, eo)
        a.update(ap_por_semilla("resultados_h15", ["V1_s"], conj, eo))       # las V1 de H16 son las de H15
        for v3 in ("V3gen_s", "V3prof_s"):
            rep.append({"bloque": {"V3gen_s": "H16a", "V3prof_s": "H16b"}[v3], "fuente": s,
                        "delta_V1_H15": round(a[v3].mean() - a["V1_s"].mean(), 2),
                        "delta_V1_replica": round(a[v3].mean() - a["V1rep_s0"].mean(), 2),
                        "V1_s0_H15": round(float(a["V1_s"][0]), 2), "V1_replica": round(float(a["V1rep_s0"][0]), 2)})
    out["h16_frente_replica"] = rep
    # O14: recuento de especificidad
    e = esp[(esp.fuente != "CPvis") & (esp.bloque != "h7")].merge(reales[["bloque", "fuente", "pasa", "delta"]], on=["bloque", "fuente"])
    out["especificidad"] = {"celdas": len(e), "especificas_ic": int((e.esp_lo > 0).sum()), "contrarias_ic": int((e.esp_hi < 0).sum()),
                            "pasan": int(e.pasa.sum()), "pasan_y_especificas": int((e.pasa & (e.esp_lo > 0)).sum()),
                            "pasan_lista": e[e.pasa][["etiqueta", "fuente", "delta", "especificidad", "esp_lo", "esp_hi", "esp_jer_lo", "esp_jer_hi"]].values.tolist()}
    return out


def cruzada_torchvision():
    filas = []
    for ruta, prefijo in (("resultados_h15/analisis/contrastes_h15.json", None), ("resultados_h16/analisis/contrastes_h16_h17.json", None)):
        for f in json.load(open(os.path.join(RAIZ, ruta), encoding="utf-8")):
            if f.get("tipo") in ("control", "secundario") and f["conjunto"].endswith("_severa"):
                filas.append({"bloque": f.get("bloque", "H15"), "control": f["conjunto"], "delta": f["delta_pp"],
                              "ic_lo": f["IC_img_lo"], "ic_hi": f["IC_img_hi"], "propio": f["tipo"] == "control"})
    return pd.DataFrame(filas)


def selftest():
    ok = [abs(dos_de_tres([1, 1, 0]) - 1) < 1e-12, abs(dos_de_tres([0.5] * 3) - 0.5) < 1e-12,
          p_pasa(2.0, 0.5) < 0.6 and p_pasa(10.0, 0.5) > 0.99, p_pasa(0.0, 3.0) < 0.03]
    r = efectos_aleatorios([0.1, -0.2, 0.3, 0.0], [0.5] * 4)
    ok.append(r["equivalente_2pp"] and abs(r["media"] - 0.05) < 1e-9)
    print("AUTOTEST %s: %d/%d" % ("SUPERADO" if all(ok) else "FALLIDO", sum(ok), len(ok)))
    return all(ok)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replicas", type=int, default=1000)
    ap.add_argument("--procesos", type=int, default=6)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--solo-tablas", action="store_true", help="reutiliza especificidad.csv (no repite el bootstrap de detecciones)")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    ruta_esp = os.path.join(AF, "especificidad.csv")
    if a.solo_tablas:
        esp = pd.read_csv(ruta_esp)
    else:
        with Pool(a.procesos) as p:
            res = p.map(analizar_bloque, [(c, e, d, f, a.replicas) for c, e, d, f in BLOQUES])
        esp = pd.DataFrame([f for r in res for f in r])
        esp.to_csv(ruta_esp, index=False)
    esp[esp.fuente.isin(["CP", "CPvis"])].to_csv(os.path.join(AF, "citypersons_visible.csv"), index=False)
    cz = cruzada_torchvision()
    cz.to_csv(os.path.join(AF, "cruzada_torchvision.csv"), index=False)
    out = analisis_tablas(esp)
    cpv = esp[esp.fuente == "CPvis"].set_index("etiqueta")
    cpf = esp[esp.fuente == "CP"].set_index("etiqueta")
    out["citypersons_visible"] = {b: {"heavy_completa": cpf.d_heavy[b], "heavy_visible": cpv.d_heavy[b],
                                      "AP_V1_heavy_completa": cpf.AP_V1_heavy[b], "AP_V1_heavy_visible": cpv.AP_V1_heavy[b]}
                                  for b in cpv.index}
    # comprobacion: el delta ocluido de este script debe coincidir con celdas_completas.csv
    cc = pd.read_csv(os.path.join(AF, "celdas_completas.csv"))
    m = esp[esp.fuente.isin(PARES)].merge(cc[cc.tipo == "real"][["bloque", "fuente", "delta"]], on=["bloque", "fuente"])
    dif = []
    for _, r in m.iterrows():
        eo = PARES[r.fuente][1]
        dif.append(abs(r["d_%s" % eo] - r.delta))
    out["comprobacion_max_dif_pp"] = round(float(max(dif)), 3)
    out["comprobacion_celdas"] = len(dif)
    json.dump(out, open(os.path.join(AF, "revision_panel.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("recuento_primario", "media_por_fuente_igual", "potencia_regla", "multiplicidad",
                                          "especificidad", "comprobacion_max_dif_pp", "comprobacion_celdas")}, indent=1, ensure_ascii=False, default=str)[:6000])


if __name__ == "__main__":
    main()
