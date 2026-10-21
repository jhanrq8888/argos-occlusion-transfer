#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - H11 (PREREGISTRO_H11.md, E9): con entrenamiento en el dominio (CityPersons, protocolo de E4)
y EXPOSICION IGUAL (V1 y V3, 60 epocas fijas, pesos last.pt, semillas nuevas 3-5, runs/argos_cp_fijo),
el aumento de siluetas mejora el AP@0.5 de las personas MUY OCLUIDAS de CityPersons.

Celdas (CityPersons val, convencion oficial; las demas personas son regiones ignore):
  bajo  = visibilidad anotada en [0,20; 0,50)   <- primaria
  alto  = visibilidad anotada en [0,80; 1,00]   <- para la especificidad
Contrastes (AP@0.5, media de semillas):
  primario       V3 - V1 en 'bajo', SOLO semillas nuevas {3,4,5} (1 000 replicas por imagenes, semilla 0)
  especificidad  (V3 - V1)bajo - (V3 - V1)alto, semillas {3,4,5}, con los mismos pesos de imagen en cada replica
  conjunto       V3 - V1 en 'bajo' con las 6 semillas, IC jerarquico (2 000 replicas)
  control        cp_silueta_severa, semillas {3,4,5}
Modo --exploratorio: los mismos calculos con las semillas {0,1,2} de E4 (los datos que motivaron H11).

Lee detecciones guardadas: resultados_h6/det (semillas 0-2) y resultados_h11/det (semillas 3-5, entrenadas en RunPod).
Escribe resultados_h11/analisis/contrastes_h11.csv e informes/veredicto_h11.md.

Uso:
    python 29_h11_dominio.py [--exploratorio]
    python 29_h11_dominio.py --selftest
"""
import argparse
import importlib.util
import json
import os
import sys

import numpy as np

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
_spec = importlib.util.spec_from_file_location("jerarquico23", os.path.join(RAIZ, "23_bootstrap_jerarquico.py"))
B23 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(B23)
A11 = B23.A11
from argos_lib.ap import emparejar_conjunto                                  # noqa: E402
from argos_lib.gt import cargar_detecciones, cargar_gt                       # noqa: E402

UMBRAL = 2.0
BAJO, ALTO = (0.20, 0.50), (0.80, 1.01)
GT_CP = os.path.join(RAIZ, "dataset", "externos", "gt_citypersons_convencion.json")
GT_CTRL = os.path.join(RAIZ, "dataset", "test_sintetico", "cp_silueta_severa", "gt_cp_silueta_severa.json")
DIRS = {0: "resultados_h6", 1: "resultados_h6", 2: "resultados_h6", 3: "resultados_h11", 4: "resultados_h11", 5: "resultados_h11"}


def gt_tramo(gt, lo, hi):
    """Copia del GT: 'objetivo' = personas evaluables con visibilidad en [lo, hi); el resto, ignore."""
    out = {}
    for nombre, meta in gt["imagenes"].items():
        inst = []
        for o in meta["instancias"]:
            o2 = dict(o)
            ok = o["estrato"] not in ("ignorar", "sin_anotar") and lo <= o.get("vis", -1) < hi
            o2["estrato"] = "objetivo" if ok else "ignorar"
            inst.append(o2)
        out[nombre] = dict(meta, instancias=inst)
    return out


def estructuras(imagenes, semillas, conj, estrato):
    estr, var = {}, {}
    for s in semillas:
        for v in ("V1", "V3"):
            ruta = os.path.join(RAIZ, DIRS[s], "det", "%s_s%d__%s.json" % (v, s, conj))
            if not os.path.exists(ruta):
                continue
            emp, _ = emparejar_conjunto(imagenes, cargar_detecciones(ruta)["detecciones"], estrato=estrato)
            c = "%s_s%d" % (v, s)
            estr[c], var[c] = A11.APBootstrap(emp), v
    return estr, var


def delta(estr, var, pesos=None):
    ap = {c: e.ap(pesos) for c, e in estr.items()}
    m = lambda v: np.mean([ap[c] for c in estr if var[c] == v])
    return m("V3") - m("V1")


def boot_imagenes(celdas, n_img, B, semilla):
    """celdas: lista de (estr, var) sobre las MISMAS imagenes. Devuelve (B, len(celdas)) de deltas con pesos comunes."""
    rnd = np.random.RandomState(semilla)
    out = np.zeros((B, len(celdas)))
    for b in range(B):
        w = np.bincount(rnd.randint(0, n_img, n_img), minlength=n_img).astype(float)
        out[b] = [delta(e, v, w) for e, v in celdas]
    return out


def fila(nombre, d, muestras):
    lo, hi = A11.ic(muestras)
    return {"celda": nombre, "delta_pp": round(100 * d, 2), "IC_lo": round(100 * lo, 2), "IC_hi": round(100 * hi, 2)}


def analizar(semillas, B=1000, B_jer=2000, semilla=0, conjunto=True):
    gt = cargar_gt(GT_CP)
    n_img = len(gt["imagenes"])
    eb, vb = estructuras(gt_tramo(gt, *BAJO), semillas, "citypersons_convencion", "objetivo")
    ea, va = estructuras(gt_tramo(gt, *ALTO), semillas, "citypersons_convencion", "objetivo")
    n_bajo = int(eb[next(iter(eb))].n_gt_img.sum()); n_alto = int(ea[next(iter(ea))].n_gt_img.sum())
    m = boot_imagenes([(eb, vb), (ea, va)], n_img, B, semilla)
    db, da = delta(eb, vb), delta(ea, va)
    filas = [dict(fila("bajo (vis 0,20-0,50)", db, m[:, 0]), n=n_bajo),
             dict(fila("alto (vis 0,80-1,00)", da, m[:, 1]), n=n_alto),
             dict(fila("especificidad (bajo - alto)", db - da, m[:, 0] - m[:, 1]), n=None)]
    gc = cargar_gt(GT_CTRL)
    ec, vc = estructuras(gc["imagenes"], semillas, "cp_silueta_severa", "severa")
    mc = boot_imagenes([(ec, vc)], len(gc["imagenes"]), B, semilla)
    filas.append(dict(fila("control cp_silueta_severa", delta(ec, vc), mc[:, 0]), n=int(ec[next(iter(ec))].n_gt_img.sum())))
    for f in filas:
        f["semillas"] = ",".join(map(str, semillas))
    if conjunto:
        todas = [0, 1, 2, 3, 4, 5]
        e5, v5 = estructuras(gt_tramo(gt, *BAJO), todas, "citypersons_convencion", "objetivo")
        if len(e5) == 12:
            r = B23.bootstrap_dos_niveles(e5, v5, ["V3-V1"], n_img, B_jer, np.random.RandomState(semilla))["V3-V1"]
            d5 = delta(e5, v5)
            filas.append(dict(fila("bajo, 6 semillas (IC jerarquico)", d5, r[1]), n=n_bajo, semillas="0,1,2,3,4,5"))
            filas.append(dict(fila("bajo, 6 semillas (IC por imagenes)", d5, r[0]), n=n_bajo, semillas="0,1,2,3,4,5"))
    return filas


def veredicto(filas):
    f = {x["celda"]: x for x in filas}
    rel = lambda x: x["delta_pp"] >= UMBRAL and x["IC_lo"] > 0
    if not rel(f["control cp_silueta_severa"]):
        return "No concluyente"
    return "Confirmada" if rel(f["bajo (vis 0,20-0,50)"]) else "No confirmada"


def informe(filas, exploratorio):
    v = veredicto(filas)
    L = ["# ARGOS-11 — %s de H11 (dominio CityPersons, personas muy ocluidas)" % ("Análisis exploratorio (semillas 0–2)" if exploratorio else "Veredicto"), "",
         "Generado por `29_h11_dominio.py`. AP@0.5, media de semillas; IC 95 %% bootstrap por imágenes (1 000 réplicas) y, para las 6 semillas, jerárquico (2 000). "
         "Regla literal de `PREREGISTRO_H11.md`, sección 2.%s" % (" **Estos datos (E4, semillas 0–2) motivaron H11; no deciden nada.**" if exploratorio else ""), "",
         "| Celda | Semillas | n | V3 − V1 (pp) | IC 95 % |", "|---|---|---|---|---|"]
    for x in filas:
        L.append("| %s | %s | %s | %+.2f | [%+.2f; %+.2f] |" % (x["celda"], x["semillas"], "" if x["n"] is None else x["n"], x["delta_pp"], x["IC_lo"], x["IC_hi"]))
    if not exploratorio:
        L += ["", "## Veredicto H11: **%s**" % v, "",
              "Regla: confirmada si V3 − V1 en el tramo bajo (semillas 3, 4 y 5) ≥ +2 pp con IC por imágenes > 0, siempre que el control "
              "`cp_silueta_severa` lo haga; no concluyente si el control falla. La especificidad y las 6 semillas son análisis secundarios declarados."]
    return "\n".join(L) + "\n", v


def selftest():
    fallos = []

    def comp(desc, ok):
        print("  [%s] %s" % ("OK" if ok else "FALLO", desc))
        if not ok:
            fallos.append(desc)
    gt = {"imagenes": {"a": {"instancias": [{"x1": 0, "y1": 0, "x2": 10, "y2": 30, "estrato": "heavy", "vis": 0.30},
                                            {"x1": 50, "y1": 0, "x2": 60, "y2": 30, "estrato": "bare", "vis": 0.95},
                                            {"x1": 90, "y1": 0, "x2": 99, "y2": 30, "estrato": "ignorar", "vis": 0.30}]}}}
    g = gt_tramo(gt, *BAJO)["a"]["instancias"]
    comp("vis 0,30 evaluable -> objetivo", g[0]["estrato"] == "objetivo")
    comp("vis 0,95 -> ignore en el tramo bajo", g[1]["estrato"] == "ignorar")
    comp("'ignorar' sigue siendo ignore", g[2]["estrato"] == "ignorar")
    comp("vis 0,95 -> objetivo en el tramo alto", gt_tramo(gt, *ALTO)["a"]["instancias"][1]["estrato"] == "objetivo")
    F = lambda b, c: [{"celda": "bajo (vis 0,20-0,50)", "delta_pp": b[0], "IC_lo": b[1], "IC_hi": b[2]},
                      {"celda": "control cp_silueta_severa", "delta_pp": c[0], "IC_lo": c[1], "IC_hi": c[2]}]
    comp("control falla -> no concluyente", veredicto(F((5, 1, 9), (1, 0.2, 2))) == "No concluyente")
    comp("+2 con IC > 0 -> confirmada", veredicto(F((2.0, 0.1, 4), (9, 7, 11))) == "Confirmada")
    comp("+3 con IC que toca el cero -> no confirmada", veredicto(F((3, -0.1, 6), (9, 7, 11))) == "No confirmada")
    comp("+1,9 con IC > 0 -> no confirmada", veredicto(F((1.9, 0.2, 3), (9, 7, 11))) == "No confirmada")
    print("\n%s" % ("AUTOTEST SUPERADO" if not fallos else "FALLOS: %s" % fallos))
    sys.exit(1 if fallos else 0)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - H11: dominio CityPersons, personas muy ocluidas")
    ap.add_argument("--exploratorio", action="store_true", help="semillas 0-2 de E4 (los datos que motivaron H11)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    filas = analizar([0, 1, 2] if a.exploratorio else [3, 4, 5], conjunto=not a.exploratorio)
    md, v = informe(filas, a.exploratorio)
    sal = os.path.join(RAIZ, "informes", "h11_exploratorio_semillas_0_2.md" if a.exploratorio else "veredicto_h11.md")
    open(sal, "w", encoding="utf-8").write(md)
    if not a.exploratorio:
        os.makedirs(os.path.join(RAIZ, "resultados_h11", "analisis"), exist_ok=True)
        json.dump(filas, open(os.path.join(RAIZ, "resultados_h11", "analisis", "contrastes_h11.json"), "w", encoding="utf-8"), indent=1)
    print(md)
    if not a.exploratorio:
        print("H11: %s" % v)


if __name__ == "__main__":
    main()
