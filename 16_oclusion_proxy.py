#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Oclusion real OBJETIVA por solapamiento de cajas (proxy).

Motivo: la anotacion visual del grado de oclusion en baja iluminacion
resulto poco fiable (kappa 0,16-0,60 entre pasadas y anotadores; la
oscuridad se confunde con oclusion). Este proxy usa solo las cajas de
persona anotadas por humanos en el dataset original: para cada instancia,
la fraccion de su caja cubierta por OTRAS cajas de persona de la misma
imagen. Es reproducible, no usa ningun modelo y cubre TODAS las instancias
del test (2 235 en ExDark-People, no 330).

Dos variantes:
  union    cobertura por la union de todas las demas cajas (cota superior:
           no distingue quien esta delante);
  orden    solo cuentan como oclusoras las cajas cuya base (y2) esta MAS
           ABAJO, es decir, mas cerca de la camara (heuristica de plano de
           suelo): la persona de delante no se marca ocluida.
Limitaciones declaradas: solo oclusion persona-persona (no coches, vallas
ni mobiliario) y heuristica de profundidad.

Validacion: en CityPersons la fraccion visible real (bboxVis) permite medir
cuanto se parece el proxy a la oclusion verdadera (correlacion, kappa
ponderado de estratos, matriz de confusion); en NightOwls, con el atributo
binario 'occluded', precision/recall de "proxy >= 10 %".

Uso:
    python 16_oclusion_proxy.py validar                # CityPersons + NightOwls
    python 16_oclusion_proxy.py exdark --variante orden  # -> dataset/gt_test_proxy.json
    python 16_oclusion_proxy.py --selftest
"""

import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argos_lib import ESTRATOS, estrato_de_cobertura                 # noqa: E402
from argos_lib.gt import cargar_gt, conteo_por_estrato, guardar_gt  # noqa: E402

RAIZ = os.path.dirname(os.path.abspath(__file__))


def cobertura_proxy(cajas, variante="orden", es_persona=None):
    """cajas: lista xyxy. Devuelve la fraccion de cada caja cubierta por
    otras cajas de persona (rasterizado exacto en pixeles)."""
    n = len(cajas)
    if es_persona is None:
        es_persona = [True] * n
    out = []
    for i, (x1, y1, x2, y2) in enumerate(cajas):
        a, b = int(np.floor(x1)), int(np.floor(y1))
        c, d = int(np.ceil(x2)), int(np.ceil(y2))
        w, h = c - a, d - b
        if w <= 0 or h <= 0:
            out.append(0.0)
            continue
        m = np.zeros((h, w), dtype=bool)
        for j, (u1, v1, u2, v2) in enumerate(cajas):
            if j == i or not es_persona[j]:
                continue
            if variante == "orden" and v2 <= y2:
                continue          # su base no esta mas abajo: no esta delante
            ia, ib = max(a, int(np.floor(u1))), max(b, int(np.floor(v1)))
            ic, id_ = min(c, int(np.ceil(u2))), min(d, int(np.ceil(v2)))
            if ic > ia and id_ > ib:
                m[ib - b:id_ - b, ia - a:ic - a] = True
        out.append(float(m.mean()))
    return out


def aplicar_proxy(imagenes, variante, clave_persona=None):
    """Asigna cobertura_proxy y estrato a cada instancia (en sitio). Las
    instancias 'ignorar' no reciben estrato pero SI actuan como oclusoras si
    son personas (riders, grupos...)."""
    for meta in imagenes.values():
        inst = meta["instancias"]
        cajas = [(o["x1"], o["y1"], o["x2"], o["y2"]) for o in inst]
        es_p = [True if clave_persona is None else clave_persona(o) for o in inst]
        cov = cobertura_proxy(cajas, variante, es_p)
        for o, c in zip(inst, cov):
            o["cobertura_proxy"] = round(c, 4)
            if o["estrato"] != "ignorar":
                o["estrato_original"] = o["estrato"]
                o["estrato"] = estrato_de_cobertura(c)
    return imagenes


def kappa_ponderado(a, b, cats):
    from importlib import import_module
    sys.path.insert(0, RAIZ)
    k3 = import_module("03_calcular_kappa")
    return k3.kappa_ponderado(list(zip(a, b)), cats)


def validar(dir_externos, variantes=("orden", "union")):
    res = {}
    rc = os.path.join(dir_externos, "gt_citypersons.json")
    rn = os.path.join(dir_externos, "gt_nightowls.json")
    for variante in variantes:
        r = {}
        if os.path.exists(rc):
            gt = cargar_gt(rc)
            imgs = json.loads(json.dumps(gt["imagenes"]))
            aplicar_proxy(imgs, variante, clave_persona=lambda o: o.get("etiqueta", "") != "ignore")
            real, prox, er, ep = [], [], [], []
            for m in imgs.values():
                for o in m["instancias"]:
                    if o.get("etiqueta") == "pedestrian" and o.get("estrato_original") in ESTRATOS:
                        real.append(o["cobertura"]); prox.append(o["cobertura_proxy"])
                        er.append(o["estrato_original"]); ep.append(o["estrato"])
            real, prox = np.asarray(real), np.asarray(prox)
            kp, mat, n = kappa_ponderado(ep, er, ESTRATOS)
            # Entre las que el proxy llama ocluidas (>=30%), cuantas lo estan de verdad?
            sel = prox >= 0.30
            r["citypersons"] = {
                "n": int(n), "corr_pearson": float(np.corrcoef(real, prox)[0, 1]),
                "corr_spearman": float(_spearman(real, prox)),
                "kappa_ponderado_estratos": float(kp) if kp is not None else None,
                "matriz_confusion(filas=proxy,cols=real)": mat,
                "proxy>=30%: n": int(sel.sum()),
                "proxy>=30%: fraccion realmente >=30%": float((real[sel] >= 0.30).mean()) if sel.any() else None,
                "proxy>=30%: cobertura real media": float(real[sel].mean()) if sel.any() else None,
                "proxy<10%: fraccion realmente <10%": float((real[prox < 0.10] < 0.10).mean()),
                "cobertura real media por estrato proxy": {
                    e: float(real[np.asarray(ep) == e].mean()) for e in ESTRATOS if (np.asarray(ep) == e).any()},
                "cobertura_media_real_de_todas": float(real.mean()),
            }
        if os.path.exists(rn):
            gt = cargar_gt(rn)
            imgs = json.loads(json.dumps(gt["imagenes"]))
            aplicar_proxy(imgs, variante, clave_persona=lambda o: o.get("categoria", "") != "ignore")
            y, p = [], []
            for m in imgs.values():
                for o in m["instancias"]:
                    if o.get("estrato_original") in ("sin", "ocluida"):
                        y.append(o["estrato_original"] == "ocluida"); p.append(o["cobertura_proxy"] >= 0.10)
            y, p = np.asarray(y), np.asarray(p)
            tp = int((y & p).sum()); fp = int((~y & p).sum()); fn = int((y & ~p).sum())
            r["nightowls"] = {"n": int(len(y)), "prevalencia_ocluida": float(y.mean()),
                              "proxy>=10%: precision": tp / (tp + fp) if tp + fp else None,
                              "proxy>=10%: recall": tp / (tp + fn) if tp + fn else None,
                              "nota": "NightOwls incluye oclusion por objetos; el proxy solo ve personas -> recall limitado"}
        res[variante] = r
    return res


def _spearman(a, b):
    from scipy.stats import spearmanr
    return spearmanr(a, b).correlation


def exdark(dataset, variante):
    ruta = os.path.join(dataset, "gt_test_real.json")
    gt = cargar_gt(ruta)
    imgs = json.loads(json.dumps(gt["imagenes"]))
    # Todas las instancias del test son personas (monoclase); se parte de
    # 'sin_anotar' para que ninguna quede como ignore.
    for m in imgs.values():
        for o in m["instancias"]:
            o["estrato"] = "sin_anotar"
    aplicar_proxy(imgs, variante)
    cnt = conteo_por_estrato(imgs)
    salida = os.path.join(dataset, "gt_test_proxy.json")
    guardar_gt(salida, "test_proxy", gt["dir_imagenes"], imgs,
               extra={"fuente": "oclusion persona-persona por solapamiento de cajas anotadas (proxy objetivo, variante %s)" % variante,
                      "variante": variante, "conteo": cnt,
                      "limitaciones": "no captura oclusion por objetos; heuristica de profundidad por base de la caja"})
    return salida, cnt


def selftest():
    fallos = []

    def comp(desc, obt, esp):
        ok = obt == esp
        print("  [%s] %-52s %s" % ("ok" if ok else "FALLA", desc, obt))
        if not ok:
            fallos.append(desc)

    A = (0, 0, 100, 200)          # persona atras (base y2=200)
    B = (50, 100, 150, 300)       # persona delante (base 300), tapa el cuadrante inferior derecho de A
    cov_u = cobertura_proxy([A, B], "union")
    comp("union: A cubierta 25%", round(cov_u[0], 3), 0.25)
    comp("union: B cubierta 25% (simetrico)", round(cov_u[1], 3), 0.25)
    cov_o = cobertura_proxy([A, B], "orden")
    comp("orden: A (atras) cubierta 25%", round(cov_o[0], 3), 0.25)
    comp("orden: B (delante) no ocluida", cov_o[1], 0.0)
    C = (0, 0, 100, 200); D = (0, 0, 100, 200)
    comp("cajas identicas: 100% union", cobertura_proxy([C, D], "union")[0], 1.0)
    comp("no persona no ocluye", cobertura_proxy([A, B], "union", [True, False])[0], 0.0)
    comp("estrato desde cobertura", estrato_de_cobertura(0.25), "ligera")
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO: 7/7 comprobaciones.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - proxy de oclusion por cajas")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dataset", default=os.path.join(RAIZ, "dataset"))
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("validar")
    e = sub.add_parser("exdark"); e.add_argument("--variante", choices=("orden", "union"), default="orden")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if args.cmd == "validar":
        res = validar(os.path.join(args.dataset, "externos"))
        os.makedirs(os.path.join(RAIZ, "resultados", "analisis"), exist_ok=True)
        with open(os.path.join(RAIZ, "resultados", "analisis", "validacion_proxy.json"), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=2, ensure_ascii=False)
        print(json.dumps(res, indent=1, ensure_ascii=False))
    elif args.cmd == "exdark":
        salida, cnt = exdark(args.dataset, args.variante)
        print("GT proxy (%s): %s\n  conteo: %s" % (args.variante, salida, cnt))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
