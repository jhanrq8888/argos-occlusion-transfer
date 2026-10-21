#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Bootstrap jerarquico (semillas + imagenes).

El bootstrap de 11_analisis_estadistico.py remuestrea IMAGENES y promedia siempre
las mismas semillas: su intervalo no incluye la variacion entre entrenamientos.
Aqui cada replica remuestrea dos niveles:
  1. imagenes con reemplazo (pesos multinomiales, pareados entre variantes);
  2. semillas con reemplazo, de forma INDEPENDIENTE para cada variante
     (V1 y V3 con la misma semilla son entrenamientos distintos, no pares).
El AP de cada corrida se calcula con el mismo codigo (APBootstrap de 11_), de modo
que la unica diferencia con el bootstrap original es el remuestreo de semillas.
Para comparar, en cada replica se calcula tambien el contraste solo-imagenes con
los mismos pesos (intervalos directamente comparables).

Referencia del procedimiento: bootstrap estratificado sobre corridas e instancias
(Agarwal et al., 2021, "Deep RL at the edge of the statistical precipice").

Limitacion declarada: con 3 semillas por variante, el remuestreo de semillas solo
tiene 10 combinaciones distintas por variante; el intervalo es una aproximacion
conservadora, no una estimacion fina de la varianza entre semillas.

Uso:
    python 23_bootstrap_jerarquico.py                  # -> informes/analisis_final/
    python 23_bootstrap_jerarquico.py --replicas 2000 --semilla 0
    python 23_bootstrap_jerarquico.py --selftest
"""
import argparse
import importlib.util
import os
import sys
import time

import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
_spec = importlib.util.spec_from_file_location("analisis11", os.path.join(RAIZ, "11_analisis_estadistico.py"))
A11 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(A11)
from argos_lib.ap import emparejar_conjunto                                  # noqa: E402
from argos_lib.gt import cargar_detecciones, cargar_gt                       # noqa: E402

UMBRAL = 2.0
REALES = [("nightowls", "ocluida"), ("citypersons_convencion", "heavy"), ("test_proxy", "severa")]
BLOQUES = [  # clave, carpeta de resultados, filtro de corridas, control sintetico
    ("exp1", "resultados", dict(excluir_prefijo="yolo26s_"), ("opaco_severa", "severa")),
    ("iter2", "resultados_v2", dict(excluir_prefijo="yolo26s_"), ("silueta_severa", "severa")),
    ("yolo26s", "resultados_v2", dict(solo_prefijo="yolo26s_"), ("silueta_severa", "severa")),
    ("h6", "resultados_h6", {}, ("cp_silueta_severa", "severa")),
    ("h7", "resultados_h7_20000", {}, None),
    ("h8", "resultados_h8", {}, ("silueta_severa", "severa")),   # RT-DETR-l (PREREGISTRO_H8.md); se omite si no existe
    ("h9", "resultados_h9", {}, ("generativa_severa", "severa")),  # oclusion generativa (PREREGISTRO_H9.md); idem
]
# Bloques secundarios: solo con --secundarios y en ficheros aparte, para no alterar el analisis consolidado.
BLOQUES_SECUNDARIOS = [
    ("h9b", "resultados_h9b", {}, ("generativa_severa", "severa")),  # generativa, 30 epocas fijas (PREREGISTRO_H9b.md)
]


def estructuras_celda(dir_res, corridas, conj, est):
    """{corrida: APBootstrap} y n de imagenes para un conjunto/estrato."""
    ruta_gt = next((d["conjuntos"][conj] for d in corridas.values() if conj in d["conjuntos"]), None)
    if ruta_gt is None:
        return None, 0, 0
    gt = cargar_gt(ruta_gt)
    est_, n_gt = {}, 0
    for c in corridas:
        ruta = os.path.join(RAIZ, dir_res, "det", "%s__%s.json" % (c, conj))
        if not os.path.exists(ruta):
            continue
        emp, _ = emparejar_conjunto(gt["imagenes"], cargar_detecciones(ruta)["detecciones"], estrato=est)
        est_[c] = A11.APBootstrap(emp)
        n_gt = int(sum(e["n_gt"] for e in emp))
    return est_, len(gt["imagenes"]), n_gt


def bootstrap_dos_niveles(estructuras, var_de, contrastes, n_img, B, rnd):
    """Devuelve {contraste: (deltas_solo_imagenes, deltas_jerarquico)} con B replicas cada uno."""
    por_var = {}
    for c, v in var_de.items():
        if c in estructuras:
            por_var.setdefault(v, []).append(c)
    out = {k: (np.zeros(B), np.zeros(B)) for k in contrastes}
    for b in range(B):
        pesos = np.bincount(rnd.randint(0, n_img, n_img), minlength=n_img).astype(float)
        ap = {c: estructuras[c].ap(pesos) for cs in por_var.values() for c in cs}
        media_img, media_jer = {}, {}
        for v, cs in por_var.items():
            vals = np.array([ap[c] for c in cs])
            media_img[v] = vals.mean()
            media_jer[v] = vals[rnd.randint(0, len(vals), len(vals))].mean()   # semillas con reemplazo
        for k in contrastes:
            a, bse = k.split("-")
            out[k][0][b] = media_img[a] - media_img[bse]
            out[k][1][b] = media_jer[a] - media_jer[bse]
    return out


def analizar(B, semilla, verbose=True, bloques=None):
    rnd = np.random.RandomState(semilla)
    filas = []
    for clave, dir_res, filtro, sint in (BLOQUES if bloques is None else bloques):
        if not os.path.isdir(os.path.join(RAIZ, dir_res, "eval")):
            continue
        corridas = A11.cargar_corridas(os.path.join(RAIZ, dir_res), **filtro)
        corridas = {c: d for c, d in corridas.items() if d["variante"] in ("V1", "V2", "V3", "V4")}
        var_de = {c: d["variante"] for c, d in corridas.items()}
        variantes = sorted(set(var_de.values()))
        contrastes = ["%s-V1" % v for v in variantes if v != "V1"]
        celdas = ([sint] if sint else []) + REALES
        for conj, est in celdas:
            t0 = time.time()
            estructuras, n_img, n_gt = estructuras_celda(dir_res, corridas, conj, est)
            if not estructuras:
                continue
            res = bootstrap_dos_niveles(estructuras, var_de, contrastes, n_img, B, rnd)
            ap_full = {c: estructuras[c].ap() for c in estructuras}
            for k, (d_img, d_jer) in res.items():
                a, bse = k.split("-")
                delta = np.mean([ap_full[c] for c in estructuras if var_de[c] == a]) - \
                        np.mean([ap_full[c] for c in estructuras if var_de[c] == bse])
                li, hi = A11.ic(d_img); lj, hj = A11.ic(d_jer)
                ns = sum(1 for c in estructuras if var_de[c] == a)
                filas.append({"bloque": clave, "conjunto": conj, "estrato": est,
                              "tipo": "sintetico" if sint and (conj, est) == sint else "real",
                              "contraste": k, "semillas_por_variante": ns, "n_gt": n_gt,
                              "delta_pp": round(100 * delta, 2),
                              "IC_imagenes_lo": round(100 * li, 2), "IC_imagenes_hi": round(100 * hi, 2),
                              "IC_jerarquico_lo": round(100 * lj, 2), "IC_jerarquico_hi": round(100 * hj, 2),
                              "excluye0_imagenes": bool(li > 0 or hi < 0), "excluye0_jerarquico": bool(lj > 0 or hj < 0),
                              "supera_umbral_jerarquico": bool(100 * delta >= UMBRAL and lj > 0),
                              "ensanchamiento": round((hj - lj) / max(hi - li, 1e-9), 2), "replicas": B})
            if verbose:
                print("  %-8s %-24s %-9s %5.1f s" % (clave, conj, est, time.time() - t0), flush=True)
    return pd.DataFrame(filas)


def selftest():
    fallos = []
    def comp(d, ok):
        print("  [%s] %s" % ("ok" if ok else "FALLA", d)); ok or fallos.append(d)

    class Fijo:  # AP constante por corrida: aisla el nivel de semillas
        def __init__(self, v): self.v = v
        def ap(self, pesos=None): return self.v
    est = {"a0": Fijo(0.50), "a1": Fijo(0.50), "a2": Fijo(0.50), "b0": Fijo(0.40), "b1": Fijo(0.60), "b2": Fijo(0.50)}
    var = {"a0": "V1", "a1": "V1", "a2": "V1", "b0": "V3", "b1": "V3", "b2": "V3"}
    r = bootstrap_dos_niveles(est, var, ["V3-V1"], 10, 2000, np.random.RandomState(0))["V3-V1"]
    comp("solo-imagenes sin variacion de semillas -> IC nulo", np.ptp(r[0]) < 1e-12)
    lo, hi = A11.ic(r[1])
    comp("jerarquico recoge la variacion entre semillas", hi - lo > 0.05)
    comp("jerarquico centrado en la diferencia real", abs(np.mean(r[1])) < 0.02)
    comp("todas las combinaciones de semillas dentro de [min, max]", r[1].min() >= -0.10 - 1e-9 and r[1].max() <= 0.10 + 1e-9)
    print("\n%s" % ("AUTOTEST SUPERADO" if not fallos else "FALLOS: %s" % fallos))
    sys.exit(1 if fallos else 0)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - bootstrap jerarquico (semillas + imagenes)")
    ap.add_argument("--replicas", type=int, default=2000)
    ap.add_argument("--semilla", type=int, default=0)
    ap.add_argument("--salida", help="def. informes/analisis_final/bootstrap_jerarquico.csv (o _secundarios.csv)")
    ap.add_argument("--secundarios", action="store_true",
                    help="analizar solo BLOQUES_SECUNDARIOS (H9b) y escribir bootstrap_jerarquico_secundarios.csv")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    a.salida = a.salida or os.path.join(RAIZ, "informes", "analisis_final", "bootstrap_jerarquico%s.csv"
                                        % ("_secundarios" if a.secundarios else ""))
    df = analizar(a.replicas, a.semilla, bloques=BLOQUES_SECUNDARIOS if a.secundarios else None)
    os.makedirs(os.path.dirname(a.salida), exist_ok=True)
    df.to_csv(a.salida, index=False)
    r = df[df.contraste == "V3-V1"]
    print("\nV3-V1: celdas %d | excluyen 0 (imagenes) %d -> (jerarquico) %d | superan +2 pp con IC>0 (jerarquico): reales %d, sinteticas %d"
          % (len(r), r.excluye0_imagenes.sum(), r.excluye0_jerarquico.sum(),
             r[r.tipo == "real"].supera_umbral_jerarquico.sum(), r[r.tipo == "sintetico"].supera_umbral_jerarquico.sum()))
    print("-> %s" % a.salida)


if __name__ == "__main__":
    main()
