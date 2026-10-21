#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Tasa de perdida promedio logaritmica (log-average miss rate, MR-2).

Metrica habitual en deteccion de peatones (Dollar et al., 2012; CityPersons): la
tasa de perdida (1 - recall) promediada en escala logaritmica sobre 9 valores de
falsos positivos por imagen (FPPI) repartidos uniformemente en log entre 10^-2 y
10^0. MENOR ES MEJOR. Se calcula para comprobar que la conclusion del AP@0.5 no
depende de la metrica (analisis posterior y declarado, pedido tipico de revisor).

No recalcula nada del protocolo: usa las mismas detecciones cacheadas (det/),
el mismo emparejamiento con regiones ignore (argos_lib.ap, IoU 0,5) y el mismo
bootstrap pareado por imagenes (y el jerarquico por semillas) que 11_ y 23_;
solo cambia la metrica calculada sobre cada replica.

Detalle del calculo: las detecciones se ordenan por score; FPPI = FP acumulados /
numero de imagenes del conjunto; para cada referencia r se toma el recall del
ultimo punto con FPPI <= r (0 si no hay ninguno); MR-2 = exp(media(log(MR))),
con MR acotada por abajo en 1e-10.

Salida: informes/analisis_final/miss_rate.csv (V3 - V1 en puntos porcentuales;
positivo = el aumento EMPEORA la tasa de perdida).

Uso:
    python 24_miss_rate.py
    python 24_miss_rate.py --replicas 1000 --semilla 0
    python 24_miss_rate.py --selftest
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
_spec = importlib.util.spec_from_file_location("jerarquico23", os.path.join(RAIZ, "23_bootstrap_jerarquico.py"))
B23 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(B23)
A11 = B23.A11

REFS = np.power(10.0, np.linspace(-2, 0, 9))
UMBRAL = 2.0


def mr2(e, pesos=None):
    """MR-2 de una corrida (estructura APBootstrap de 11_) con pesos por imagen."""
    if pesos is None:
        pesos = np.ones(e.n_img)
    n_gt = float(np.dot(pesos, e.n_gt_img)); n_img = float(pesos.sum())
    if n_gt == 0 or n_img == 0:
        return float("nan")
    if len(e.tp) == 0:
        return 1.0
    w = pesos[e.idx]
    rec = np.cumsum(e.tp * w) / n_gt
    fppi = np.cumsum((1.0 - e.tp) * w) / n_img
    j = np.searchsorted(fppi, REFS, side="right") - 1          # ultimo punto con FPPI <= ref
    r = np.where(j >= 0, rec[np.clip(j, 0, None)], 0.0)
    return float(np.exp(np.mean(np.log(np.maximum(1.0 - r, 1e-10)))))


def analizar(B, semilla, verbose=True, bloques=None):
    rnd = np.random.RandomState(semilla)
    filas = []
    for clave, dir_res, filtro, sint in (B23.BLOQUES if bloques is None else bloques):
        if not os.path.isdir(os.path.join(RAIZ, dir_res, "eval")):
            continue
        corridas = A11.cargar_corridas(os.path.join(RAIZ, dir_res), **filtro)
        corridas = {c: d for c, d in corridas.items() if d["variante"] in ("V1", "V3")}
        var_de = {c: d["variante"] for c, d in corridas.items()}
        for conj, est in ([sint] if sint else []) + B23.REALES:
            t0 = time.time()
            estructuras, n_img, n_gt = B23.estructuras_celda(dir_res, corridas, conj, est)
            if not estructuras:
                continue
            por_var = {"V1": [c for c in estructuras if var_de[c] == "V1"], "V3": [c for c in estructuras if var_de[c] == "V3"]}
            full = {c: mr2(estructuras[c]) for c in estructuras}
            m1 = np.mean([full[c] for c in por_var["V1"]]); m3 = np.mean([full[c] for c in por_var["V3"]])
            d_img, d_jer = np.zeros(B), np.zeros(B)
            for b in range(B):
                pesos = np.bincount(rnd.randint(0, n_img, n_img), minlength=n_img).astype(float)
                v = {c: mr2(estructuras[c], pesos) for c in estructuras}
                a = {k: np.array([v[c] for c in cs]) for k, cs in por_var.items()}
                d_img[b] = a["V3"].mean() - a["V1"].mean()
                d_jer[b] = a["V3"][rnd.randint(0, len(a["V3"]), len(a["V3"]))].mean() - \
                           a["V1"][rnd.randint(0, len(a["V1"]), len(a["V1"]))].mean()
            li, hi = A11.ic(d_img); lj, hj = A11.ic(d_jer)
            filas.append({"bloque": clave, "conjunto": conj, "estrato": est,
                          "tipo": "sintetico" if sint and (conj, est) == sint else "real",
                          "n_gt": n_gt, "n_img": n_img, "MR2_V1": round(100 * m1, 2), "MR2_V3": round(100 * m3, 2),
                          "delta_pp": round(100 * (m3 - m1), 2),
                          "IC_imagenes_lo": round(100 * li, 2), "IC_imagenes_hi": round(100 * hi, 2),
                          "IC_jerarquico_lo": round(100 * lj, 2), "IC_jerarquico_hi": round(100 * hj, 2),
                          # mejora relevante = baja la tasa de perdida al menos 2 pp con IC por debajo de cero
                          "mejora_relevante": bool(100 * (m3 - m1) <= -UMBRAL and hi < 0),
                          "empeora_ic": bool(li > 0), "replicas": B})
            if verbose:
                print("  %-8s %-24s %-9s MR-2 V1 %5.1f  V3 %5.1f  (%4.1f s)" % (clave, conj, est, 100 * m1, 100 * m3, time.time() - t0), flush=True)
    return pd.DataFrame(filas)


def selftest():
    fallos = []
    def comp(d, ok):
        print("  [%s] %s" % ("ok" if ok else "FALLA", d)); ok or fallos.append(d)

    class E:  # estructura minima con la misma interfaz que APBootstrap
        def __init__(self, tp, idx, n_gt_img):
            self.tp = np.asarray(tp, float); self.idx = np.asarray(idx, int)
            self.n_gt_img = np.asarray(n_gt_img, float); self.n_img = len(n_gt_img)
    perfecto = E([1, 1, 1, 1], [0, 1, 2, 3], [1, 1, 1, 1])
    comp("detector perfecto -> MR-2 ~ 0", mr2(perfecto) < 1e-6)
    comp("sin detecciones -> MR-2 = 1", mr2(E([], [], [1, 1])) == 1.0)
    # 100 imagenes, 1 GT cada una; recall 0,5 antes de cualquier FP y 1,0 tras 100 FP (FPPI 1)
    tp = [1] * 50 + [0] * 100 + [1] * 50
    idx = list(range(50)) + [i % 100 for i in range(100)] + list(range(50, 100))
    e = E(tp, idx, [1] * 100)
    comp("recall 0,5 en todo FPPI < 1 y 1,0 en FPPI = 1 -> MR-2 = 0,5^(8/9)*1e-10^(1/9)", abs(mr2(e) - np.exp((8 * np.log(0.5) + np.log(1e-10)) / 9)) < 1e-9)
    comp("pesos unitarios = sin pesos", abs(mr2(e, np.ones(100)) - mr2(e)) < 1e-12)
    comp("duplicar todas las imagenes no cambia MR-2", abs(mr2(e, 2 * np.ones(100)) - mr2(e)) < 1e-12)
    print("\n%s" % ("AUTOTEST SUPERADO" if not fallos else "FALLOS: %s" % fallos))
    sys.exit(1 if fallos else 0)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - log-average miss rate (MR-2)")
    ap.add_argument("--replicas", type=int, default=1000)
    ap.add_argument("--semilla", type=int, default=0)
    ap.add_argument("--salida", help="def. informes/analisis_final/miss_rate.csv (o miss_rate_secundarios.csv)")
    ap.add_argument("--secundarios", action="store_true",
                    help="analizar solo B23.BLOQUES_SECUNDARIOS (H9b) y escribir miss_rate_secundarios.csv")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    a.salida = a.salida or os.path.join(RAIZ, "informes", "analisis_final", "miss_rate%s.csv"
                                        % ("_secundarios" if a.secundarios else ""))
    df = analizar(a.replicas, a.semilla, bloques=B23.BLOQUES_SECUNDARIOS if a.secundarios else None)
    df.to_csv(a.salida, index=False)
    r = df[df.tipo == "real"]; s = df[df.tipo != "real"]
    print("\nMR-2 (V3 - V1): sinteticos con mejora relevante %d/%d | reales con mejora relevante %d/%d | reales que empeoran con IC>0 %d"
          % (s.mejora_relevante.sum(), len(s), r.mejora_relevante.sum(), len(r), r.empeora_ic.sum()))
    print("-> %s" % a.salida)


if __name__ == "__main__":
    main()
