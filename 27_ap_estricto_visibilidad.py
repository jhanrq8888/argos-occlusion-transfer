#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Analisis de sensibilidad (posterior, declarado; 06/10/2026):

1. AP@0.5:0.95 (media de los 10 umbrales de IoU, estilo COCO) para V3 - V1 en las
   mismas celdas del analisis consolidado (control sintetico + 3 fuentes reales),
   con IC 95 % por imagenes y jerarquico (semillas + imagenes), 1 000 replicas.
   El criterio pre-registrado sigue siendo AP@0.5; esto solo comprueba que la
   conclusion no depende de la tolerancia de localizacion.
2. Curva por visibilidad en CityPersons: cada persona tiene su visibilidad
   anotada (vis = area visible / area de la caja completa). Se agrupan en
   tramos y se calcula el AP@0.5 por tramo (las demas personas son regiones
   ignore, la misma regla de los estratos) y el recall a confianza >= 0,25.

No re-infiere nada: usa las detecciones guardadas (det/) y el emparejamiento de
argos_lib.ap (que ya guarda los 10 umbrales). Bootstrap de 23_; cada celda con su propia semilla (semilla*1000 + indice), en paralelo.

Salidas: informes/analisis_final/ap_estricto.csv, visibilidad_citypersons.csv,
fig5_visibilidad.{png,pdf} y AP_ESTRICTO_VISIBILIDAD.md.

Uso:
    python 27_ap_estricto_visibilidad.py
    python 27_ap_estricto_visibilidad.py --selftest
"""
import argparse
import importlib.util
import json
import os
import sys
import time

import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
_spec = importlib.util.spec_from_file_location("jerarquico23", os.path.join(RAIZ, "23_bootstrap_jerarquico.py"))
B23 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(B23)
A11 = B23.A11
from argos_lib.ap import emparejar_conjunto                                  # noqa: E402
from argos_lib.gt import cargar_detecciones, cargar_gt                       # noqa: E402

AF = os.path.join(RAIZ, "informes", "analisis_final")
UMBRAL = 2.0
N_UMBRALES = 10
TRAMOS = [(0.20, 0.35), (0.35, 0.50), (0.50, 0.65), (0.65, 0.80), (0.80, 0.90), (0.90, 1.01)]
CONF_OP = 0.25
EXP = {"exp1": "E1", "iter2": "E2", "yolo26s": "E3", "h6": "E4", "h7": "E5", "h8": "E6", "h9": "E7", "h9b": "E7b"}


class APEstricto:
    """AP@0.5:0.95 con remuestreo por pesos: media de APBootstrap en los 10 umbrales."""

    def __init__(self, emparejados):
        self.por_umbral = [A11.APBootstrap(emparejados, t) for t in range(N_UMBRALES)]

    def ap(self, pesos=None):
        v = [e.ap(pesos) for e in self.por_umbral]
        return float(np.nanmean(v)) if not all(np.isnan(v)) else float("nan")


def bloques():
    return B23.BLOQUES + B23.BLOQUES_SECUNDARIOS


def corridas_v1v3(dir_res, filtro):
    c = A11.cargar_corridas(os.path.join(RAIZ, dir_res), **filtro)
    return {k: d for k, d in c.items() if d["variante"] in ("V1", "V3")}


# ----------------------------------------------------------------------------- 1. AP@0.5:0.95
# Cada celda es una tarea independiente con su propia semilla (semilla * 1000 + indice de la
# tarea en un orden fijo), de modo que se puede repartir entre procesos y cada celda se puede
# recalcular sola con el mismo resultado (v3.5b, CAMBIOS_PROTOCOLO.md).
def tareas_ap():
    t = []
    for clave, dir_res, filtro, sint in bloques():
        if os.path.isdir(os.path.join(RAIZ, dir_res, "eval")):
            for conj, est in ([sint] if sint else []) + B23.REALES:
                t.append(("ap", clave, dir_res, filtro, sint, conj, est))
    return t


def celda_ap(clave, dir_res, filtro, sint, conj, est, B, seed):
    corr = corridas_v1v3(dir_res, filtro)
    var_de = {c: d["variante"] for c, d in corr.items()}
    ruta_gt = next((d["conjuntos"][conj] for d in corr.values() if conj in d["conjuntos"]), None)
    if ruta_gt is None:
        return None
    t0 = time.time()
    gt = cargar_gt(ruta_gt)
    estr = {}
    for c in corr:
        rd = os.path.join(RAIZ, dir_res, "det", "%s__%s.json" % (c, conj))
        if os.path.exists(rd):
            emp, _ = emparejar_conjunto(gt["imagenes"], cargar_detecciones(rd)["detecciones"], estrato=est)
            estr[c] = APEstricto(emp)
    if not estr:
        return None
    n_img = len(gt["imagenes"])
    res = B23.bootstrap_dos_niveles(estr, var_de, ["V3-V1"], n_img, B, np.random.RandomState(seed))["V3-V1"]
    full = {c: estr[c].ap() for c in estr}
    m = lambda v: np.mean([full[c] for c in estr if var_de[c] == v])
    delta = m("V3") - m("V1")
    li, hi = A11.ic(res[0]); lj, hj = A11.ic(res[1])
    print("  %-7s %-24s %-8s dAP50:95 %+6.2f [%+.2f; %+.2f]  (%.0f s)"
          % (clave, conj, est, 100 * delta, 100 * li, 100 * hi, time.time() - t0), flush=True)
    return {"bloque": clave, "exp": EXP.get(clave, clave), "conjunto": conj, "estrato": est,
            "tipo": "sintetico" if sint and (conj, est) == tuple(sint) else "real",
            "AP5095_V1": round(m("V1"), 4), "AP5095_V3": round(m("V3"), 4), "delta_pp": round(100 * delta, 2),
            "IC_imagenes_lo": round(100 * li, 2), "IC_imagenes_hi": round(100 * hi, 2),
            "IC_jerarquico_lo": round(100 * lj, 2), "IC_jerarquico_hi": round(100 * hj, 2),
            "supera_umbral": bool(100 * delta >= UMBRAL and li > 0), "replicas": B, "semilla_celda": seed}


# ----------------------------------------------------------------------------- 2. Visibilidad
def tramo(vis):
    for a, b in TRAMOS:
        if a <= vis < b:
            return "%.2f-%.2f" % (a, min(b, 1.0))
    return None


def gt_por_tramos(gt):
    """Copia del GT con el estrato sustituido por el tramo de visibilidad. Las
    personas no evaluables en la convencion (estrato 'ignorar') siguen siendo ignore."""
    out = {}
    for nombre, meta in gt["imagenes"].items():
        inst = []
        for o in meta["instancias"]:
            o2 = dict(o)
            t = tramo(o.get("vis", -1)) if o["estrato"] not in ("ignorar", "sin_anotar") else None
            o2["estrato"] = t if t else "ignorar"
            inst.append(o2)
        out[nombre] = dict(meta, instancias=inst)
    return out


def recall_op(emp, conf=CONF_OP):
    tp = sum(int(((e["scores"][0] >= conf) & e["tp"][0]).sum()) for e in emp)
    n = sum(e["n_gt"] for e in emp)
    return tp / n if n else float("nan")


def tareas_vis():
    t = []
    for clave, dir_res, filtro, _ in bloques():
        if os.path.isdir(os.path.join(RAIZ, dir_res, "eval")):
            for a, b in TRAMOS:
                t.append(("vis", clave, dir_res, filtro, a, b))
    return t


def celda_vis(clave, dir_res, filtro, a, b, B, seed):
    conj = "citypersons_convencion"
    corr = corridas_v1v3(dir_res, filtro)
    ruta_gt = next((d["conjuntos"][conj] for d in corr.values() if conj in d["conjuntos"]), None)
    if ruta_gt is None:
        return None
    gt = gt_por_tramos(cargar_gt(ruta_gt))
    var_de = {c: d["variante"] for c, d in corr.items()}
    t = "%.2f-%.2f" % (a, min(b, 1.0))
    estr, rec = {}, {}
    for c in corr:
        rd = os.path.join(RAIZ, dir_res, "det", "%s__%s.json" % (c, conj))
        if os.path.exists(rd):
            emp, _ = emparejar_conjunto(gt, cargar_detecciones(rd)["detecciones"], estrato=t)
            estr[c] = A11.APBootstrap(emp)
            rec[c] = recall_op(emp)
    if not estr:
        return None
    n_gt = int(estr[next(iter(estr))].n_gt_img.sum())
    res = B23.bootstrap_dos_niveles(estr, var_de, ["V3-V1"], len(gt), B, np.random.RandomState(seed))["V3-V1"]
    full = {c: estr[c].ap() for c in estr}
    m = lambda dic, v: float(np.mean([dic[c] for c in estr if var_de[c] == v]))
    li, hi = A11.ic(res[0])
    print("  visibilidad %-7s %s listo" % (clave, t), flush=True)
    return {"bloque": clave, "exp": EXP.get(clave, clave), "tramo_vis": t, "vis_centro": round((a + min(b, 1.0)) / 2, 3),
            "n_gt": n_gt, "AP50_V1": round(m(full, "V1"), 4), "AP50_V3": round(m(full, "V3"), 4),
            "delta_pp": round(100 * (m(full, "V3") - m(full, "V1")), 2),
            "IC_imagenes_lo": round(100 * li, 2), "IC_imagenes_hi": round(100 * hi, 2),
            "recall025_V1": round(m(rec, "V1"), 4), "recall025_V3": round(m(rec, "V3"), 4), "replicas": B, "semilla_celda": seed}


def ejecutar_tarea(args):
    tarea, B, seed = args
    if tarea[0] == "ap":
        return ("ap", celda_ap(*tarea[1:], B, seed))
    return ("vis", celda_vis(*tarea[1:], B, seed))


def calcular(B, semilla, procesos):
    """Todas las celdas (AP@0.5:0.95 y visibilidad) repartidas entre `procesos`."""
    tareas = tareas_ap() + tareas_vis()
    args = [(t, B, semilla * 1000 + i) for i, t in enumerate(tareas)]
    if procesos > 1:
        from multiprocessing import Pool
        with Pool(procesos) as pool:
            res = pool.map(ejecutar_tarea, args, chunksize=1)
    else:
        res = [ejecutar_tarea(a) for a in args]
    da = pd.DataFrame([r for k, r in res if k == "ap" and r])
    dv = pd.DataFrame([r for k, r in res if k == "vis" and r])
    return da, dv


# ----------------------------------------------------------------------------- figura e informe
def figura(dv, ruta):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    # Paleta categorica en orden fijo (validada para daltonismo en 22_); texto en tinta neutra.
    COL = {"E1": "#2a78d4", "E2": "#e0782a", "E7": "#1f9e76", "E7b": "#7a5bc7"}
    NOM = {"E1": "E1 parches", "E2": "E2 siluetas", "E7": "E7 generativa (época 2)", "E7b": "E7b generativa (30 épocas)"}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
    # Cada V3 junto a SU propia V1 (E7b tiene su V1 de 30 epocas, distinta de la de E2).
    for e, estilo, base_nom in (("E2", "-", "época 2"), ("E7b", "--", "30 épocas")):
        s = dv[dv.exp == e].sort_values("vis_centro")
        a1.plot(s.vis_centro, s.AP50_V1, estilo + "o", color="#4a4a4a", lw=2, ms=5, label="V1 sin aumento (%s)" % base_nom)
        a1.plot(s.vis_centro, s.AP50_V3, estilo + "o", color=COL[e], lw=2, ms=5, label="V3 " + NOM[e])
    a1.set_xlabel("Visibilidad anotada (fracción visible del cuerpo)"); a1.set_ylabel("AP@0.5")
    a1.set_title("CityPersons: AP@0.5 según la visibilidad real", fontsize=10)
    a2.axhline(0, color="#888", lw=1)
    a2.axhspan(-UMBRAL, UMBRAL, color="#bbb", alpha=0.18, lw=0)
    for e in ("E1", "E2", "E7", "E7b"):
        s = dv[dv.exp == e].sort_values("vis_centro")
        if s.empty:
            continue
        a2.plot(s.vis_centro, s.delta_pp, "-o", color=COL[e], lw=2, ms=6, label=NOM[e])
        a2.fill_between(s.vis_centro, s.IC_imagenes_lo, s.IC_imagenes_hi, color=COL[e], alpha=0.10, lw=0)
    a2.set_xlabel("Visibilidad anotada (fracción visible del cuerpo)"); a2.set_ylabel("V3 − V1 (AP@0.5, pp)")
    a2.set_title("Efecto del aumento según la visibilidad real (banda gris: ±2 pp)", fontsize=10)
    for a in (a1, a2):
        a.grid(alpha=0.25); a.spines[["top", "right"]].set_visible(False); a.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(ruta + ".png", dpi=220); fig.savefig(ruta + ".pdf")
    plt.close(fig)


def informe(da, dv, ruta):
    r = da[da.tipo == "real"]; s = da[da.tipo != "real"]
    prim = r[r.bloque != "h9b"]
    L = ["# AP@0.5:0.95 y curva por visibilidad (análisis de sensibilidad posterior, 06/10/2026)", "",
         "Generado por `27_ap_estricto_visibilidad.py` desde las detecciones guardadas. El criterio pre-registrado sigue siendo AP@0.5; "
         "esto comprueba que la conclusión no depende de la tolerancia de localización ni de cómo se agrupa la oclusión real.", "",
         "## 1. AP@0.5:0.95 (V3 − V1, pp)", "",
         "Controles sintéticos que superan +2 pp con IC > 0: **%d de %d**. Mediciones reales de E1–E7 que lo superan: **%d de %d**; "
         "negativas: %d; con IC por imágenes < 0: %d; con límite superior < +2: %d."
         % (s.supera_umbral.sum(), len(s), prim.supera_umbral.sum(), len(prim), (prim.delta_pp < 0).sum(),
            (prim.IC_imagenes_hi < 0).sum(), (prim.IC_imagenes_hi < UMBRAL).sum()), "",
         "| Exp. | Conjunto | Estrato | V1 | V3 | Δ | IC imágenes | IC jerárquico |", "|---|---|---|---|---|---|---|---|"]
    for _, x in da.iterrows():
        L.append("| %s | %s | %s | %.3f | %.3f | %+.2f | [%+.2f; %+.2f] | [%+.2f; %+.2f] |" % (
            x.exp, x.conjunto, x.estrato, x.AP5095_V1, x.AP5095_V3, x.delta_pp, x.IC_imagenes_lo, x.IC_imagenes_hi,
            x.IC_jerarquico_lo, x.IC_jerarquico_hi))
    L += ["", "## 2. CityPersons por tramos de visibilidad (AP@0.5, V3 − V1, pp)", "",
          "Tramos de la fracción visible anotada; las demás personas son regiones *ignore*. Recall a confianza ≥ 0,25.", "",
          "| Exp. | Tramo | n | AP V1 | AP V3 | Δ | IC imágenes | Recall V1 → V3 |", "|---|---|---|---|---|---|---|---|"]
    for _, x in dv.iterrows():
        L.append("| %s | %s | %d | %.3f | %.3f | %+.2f | [%+.2f; %+.2f] | %.3f → %.3f |" % (
            x.exp, x.tramo_vis, x.n_gt, x.AP50_V1, x.AP50_V3, x.delta_pp, x.IC_imagenes_lo, x.IC_imagenes_hi,
            x.recall025_V1, x.recall025_V3))
    L += ["", "Figura: `fig5_visibilidad.png` / `.pdf`."]
    open(ruta, "w", encoding="utf-8").write("\n".join(L) + "\n")


def selftest():
    fallos = []

    def comp(desc, ok):
        print("  [%s] %s" % ("OK" if ok else "FALLO", desc))
        if not ok:
            fallos.append(desc)
    comp("tramo 0,30 -> 0.20-0.35", tramo(0.30) == "0.20-0.35")
    comp("tramo 1,00 -> 0.90-1.00", tramo(1.0) == "0.90-1.00")
    comp("tramo 0,10 -> fuera", tramo(0.10) is None)
    gt = {"imagenes": {"a": {"instancias": [{"x1": 0, "y1": 0, "x2": 10, "y2": 30, "estrato": "heavy", "vis": 0.4},
                                            {"x1": 50, "y1": 0, "x2": 60, "y2": 30, "estrato": "ignorar", "vis": 0.95}]}}}
    g2 = gt_por_tramos(gt)
    comp("ignorar se mantiene ignore", g2["a"]["instancias"][1]["estrato"] == "ignorar")
    comp("heavy vis 0,4 -> tramo 0.35-0.50", g2["a"]["instancias"][0]["estrato"] == "0.35-0.50")
    det = {"a": [[0, 0, 10, 30, 0.9], [50, 0, 60, 30, 0.8], [100, 0, 110, 30, 0.3]]}
    emp, _ = emparejar_conjunto(g2, det, estrato="0.35-0.50")
    e = APEstricto(emp)
    comp("AP estricto de una deteccion perfecta y un FP posterior = 1", abs(e.ap() - 1.0) < 1e-9)
    comp("recall a 0,25 = 1", abs(recall_op(emp) - 1.0) < 1e-9)
    print("\n%s" % ("AUTOTEST SUPERADO" if not fallos else "FALLOS: %s" % fallos))
    sys.exit(1 if fallos else 0)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - AP@0.5:0.95 y curva por visibilidad (sensibilidad)")
    ap.add_argument("--replicas", type=int, default=1000)
    ap.add_argument("--semilla", type=int, default=0)
    ap.add_argument("--procesos", type=int, default=8, help="procesos en paralelo (cada celda tiene su semilla)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    print("AP@0.5:0.95 y visibilidad en CityPersons (%d procesos)" % a.procesos, flush=True)
    da, dv = calcular(a.replicas, a.semilla, a.procesos)
    da.to_csv(os.path.join(AF, "ap_estricto.csv"), index=False)
    dv.to_csv(os.path.join(AF, "visibilidad_citypersons.csv"), index=False)
    figura(dv, os.path.join(AF, "fig5_visibilidad"))
    informe(da, dv, os.path.join(AF, "AP_ESTRICTO_VISIBILIDAD.md"))
    print("-> %s" % AF)


if __name__ == "__main__":
    main()
