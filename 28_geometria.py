#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - H10 (PREREGISTRO_H10.md): oclusion con la geometria de la oclusion real.

Subcomandos:
  patrones      Extrae de anno_train.mat (CityPersons TRAIN) los patrones caja visible / caja
                completa: dataset/geometria/patrones_train.json (imagenes de dataset_cp/train.txt,
                cobertura 0,30-0,85) y patrones_control.json (imagenes de dataset_cp/val_interno.txt,
                cobertura 0,70-0,95). Ninguna imagen de CityPersons val (fuente de prueba).
  estadisticas  Distribucion de lados y coberturas de la oclusion real frente a la geometria de v2.
  demo          12 imagenes de train ocluidas (dataset/demo_geometria/), para revision visual.
  prueba        Control sintetico geometria_severa: todas las personas de ExDark test, banco
                siluetas_test, patrones_control, semilla 2024; estrato por cobertura efectiva.
  analisis      Contrastes V3G - V1, V3S - V1 y V3G - V3S (bootstrap por imagenes 1 000 y jerarquico 2 000)
                sobre resultados_h10/ y veredicto literal -> informes/veredicto_h10.md.

Uso:
    python 28_geometria.py patrones | estadisticas | demo | prueba | analisis
    python 28_geometria.py --selftest
"""
import argparse
import importlib.util
import json
import os
import sys

import numpy as np

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
from argos_lib import estrato_de_cobertura                                   # noqa: E402
from argos_lib.geometria import (BancoPatrones, buscar_colocacion, extraer_patrones,  # noqa: E402
                                 lados_de, mascara_oculta, ocluir_geometria, patron_de_cajas)

DATASET = os.path.join(RAIZ, "dataset")
DIR_GEO = os.path.join(DATASET, "geometria")
MAT_TRAIN = os.path.join(RAIZ, "externos", "citypersons", "anno_train.mat")
RANGO_TRAIN = (0.30, 0.95)        # patrones guardados; el rango de muestreo se calibra (PREREGISTRO_H10.md)
RANGO_CONTROL = (0.70, 0.95)
RANGO_MUESTREO = (0.40, 0.95)     # entrenamiento: calibrado para una cobertura efectiva media ~0,50 (v2: 0,55)
UMBRAL = 2.0
REALES = [("NightOwls ocluida", "nightowls", "ocluida"), ("CityPersons heavy", "citypersons_convencion", "heavy"),
          ("ExDark proxy severa", "test_proxy", "severa")]
CONTROL = ("geometria_severa", "severa")


def _modulo(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, os.path.join(RAIZ, archivo))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _nombres(lista):
    with open(os.path.join(RAIZ, "dataset_cp", lista), encoding="utf-8") as fh:
        return {os.path.basename(l.strip()) for l in fh if l.strip()}


# ----------------------------------------------------------------------------- patrones
def cmd_patrones():
    regs = _modulo("cp20", "20_replica_citypersons.py").leer_mat(MAT_TRAIN)
    os.makedirs(DIR_GEO, exist_ok=True)
    for nombre, lista, rango in (("patrones_train.json", "train.txt", RANGO_TRAIN),
                                 ("patrones_control.json", "val_interno.txt", RANGO_CONTROL)):
        noms = _nombres(lista)
        pats = extraer_patrones(regs, noms, rango=rango)
        doc = {"fuente": "CityPersons anno_train.mat (Zhang et al. 2017), imagenes de dataset_cp/%s" % lista,
               "criterio": "clase 1 (pedestrian), alto >= 50 px, cobertura 1 - vis en [%.2f, %.2f]" % rango,
               "formato": "vx1, vy1, vx2, vy2 (caja visible relativa a la completa), cobertura",
               "n": len(pats), "patrones": pats}
        json.dump(doc, open(os.path.join(DIR_GEO, nombre), "w", encoding="utf-8"), indent=0)
        print("  %-22s %5d patrones (%d imagenes)" % (nombre, len(pats), len(noms)))


def resumen_lados(pats, tol=0.02):
    cuenta = {"solo abajo": 0, "solo un lado (izq./der.)": 0, "solo arriba": 0, "esquina o varios lados": 0}
    for p in pats:
        l = lados_de(p, tol)
        n = sum(l.values())
        if n >= 2:
            cuenta["esquina o varios lados"] += 1
        elif l["abajo"]:
            cuenta["solo abajo"] += 1
        elif l["izquierda"] or l["derecha"]:
            cuenta["solo un lado (izq./der.)"] += 1
        elif l["arriba"]:
            cuenta["solo arriba"] += 1
    tot = max(1, len(pats))
    return {k: round(100.0 * v / tot, 1) for k, v in cuenta.items()}


def cmd_estadisticas():
    pt = BancoPatrones(os.path.join(DIR_GEO, "patrones_train.json")).patrones
    pc = BancoPatrones(os.path.join(DIR_GEO, "patrones_control.json")).patrones
    L = ["# Geometría de la oclusión real frente a la de las siluetas (v2)", "",
         "Patrones de CityPersons train (caja visible frente a caja completa). En v2 el oclusor entra por un lado elegido "
         "al azar (abajo, izquierda, derecha o arriba, 25 % cada uno) y cubre una fracción f ~ U[0,30; 0,85].", "",
         "| Región oculta | Train (n=%d) | Control (n=%d) | Siluetas v2 |" % (len(pt), len(pc)), "|---|---|---|---|"]
    v2 = {"solo abajo": 25.0, "solo un lado (izq./der.)": 50.0, "solo arriba": 25.0, "esquina o varios lados": 0.0}
    for tol in (0.02, 0.10):
        rt, rc = resumen_lados(pt, tol), resumen_lados(pc, tol)
        L.append("| *Margen mínimo para contar un lado: %d %% de la caja* | | | |" % round(100 * tol))
        for k in rt:
            L.append("| %s | %.1f %% | %.1f %% | %.1f %% (nominal) |" % (k, rt[k], rc[k], v2[k]))
    c = np.array([p[4] for p in pt])
    L += ["", "Cobertura de los patrones de train: media %.2f, mediana %.2f, cuartiles %.2f–%.2f (v2: uniforme, media 0,575)."
          % (c.mean(), np.median(c), np.percentile(c, 25), np.percentile(c, 75))]
    ruta = os.path.join(RAIZ, "informes", "h10_geometria_estadisticas.md")
    open(ruta, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


# ----------------------------------------------------------------------------- demo y prueba
def cmd_demo(n=12, semilla=0):
    import cv2
    from argos_lib.gt import cargar_split_yolo
    from argos_lib.oclusion import cobertura_por_caja, escribir_imagen, leer_imagen
    from argos_lib.siluetas import BancoSiluetas
    banco = BancoSiluetas(os.path.join(DATASET, "siluetas_train"))
    pats = BancoPatrones(os.path.join(DIR_GEO, "patrones_train.json"))
    base = cargar_split_yolo(DATASET, "train")
    rnd = np.random.RandomState(semilla)
    nombres = sorted(base); rnd.shuffle(nombres)
    out = os.path.join(DATASET, "demo_geometria"); os.makedirs(out, exist_ok=True)
    hechos, ious = 0, []
    for rel in nombres:
        if hechos >= n:
            break
        im = leer_imagen(os.path.join(DATASET, "images", rel))
        cajas = [(o["x1"], o["y1"], o["x2"], o["y2"]) for o in base[rel]["instancias"]]
        ap, masc, peg = ocluir_geometria(im, cajas, rnd, banco, pats, p=1.0, rango_c=RANGO_MUESTREO)
        if not ap:
            continue
        cov = cobertura_por_caja(masc, cajas)
        for i, clase, c, ce, iou in ap:
            ious.append(iou)
            x1, y1, x2, y2 = (int(v) for v in cajas[i])
            cv2.rectangle(im, (x1, y1), (x2, y2), (0, 255, 0), 1)
            cv2.putText(im, "%s c=%.2f ef=%.2f iou=%.2f" % (clase[:3], c, cov[i], iou), (x1, max(12, y1 - 3)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 0), 1)
        escribir_imagen(os.path.join(out, os.path.basename(rel)), im)
        hechos += 1
    print("Guardados %d ejemplos en %s; IoU medio recorte-region oculta %.2f" % (hechos, out, float(np.mean(ious))))


def cmd_prueba(semilla=2024):
    from argos_lib.gt import cargar_split_yolo, conteo_por_estrato, guardar_gt, leer_luz_por_imagen
    from argos_lib.oclusion import cobertura_por_caja, escribir_imagen, leer_imagen
    from argos_lib.siluetas import BancoSiluetas
    banco = BancoSiluetas(os.path.join(DATASET, "siluetas_test"))
    pats = BancoPatrones(os.path.join(DIR_GEO, "patrones_control.json"))
    luz = leer_luz_por_imagen(os.path.join(RAIZ, "imageclasslist.txt"))       # igual que 15_ prueba
    base = cargar_split_yolo(DATASET, "test", luz)
    nombre = "geometria_severa"
    dir_out = os.path.join(DATASET, "test_sintetico", nombre)
    os.makedirs(os.path.join(dir_out, "test"), exist_ok=True)
    rnd = np.random.RandomState(semilla + 9000)
    imagenes, ious = {}, []
    for k, (rel, meta) in enumerate(sorted(base.items())):
        im = leer_imagen(os.path.join(DATASET, "images", rel))
        cajas = [(o["x1"], o["y1"], o["x2"], o["y2"]) for o in meta["instancias"]]
        ap, masc, pegadas = ocluir_geometria(im, cajas, rnd, banco, pats, todas=True, rango_c=RANGO_CONTROL)
        ious += [a[4] for a in ap]
        cov = cobertura_por_caja(masc, cajas)
        escribir_imagen(os.path.join(dir_out, rel), im)
        inst = [{**o, "cobertura": round(c, 4), "estrato_nominal": "severa", "estrato": estrato_de_cobertura(c)}
                for o, c in zip(meta["instancias"], cov)]
        inst += [{"id": "%s#p%d" % (os.path.splitext(os.path.basename(rel))[0], j), "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                  "estrato": "ignorar", "truncado": 0, "cobertura": 0.0, "pegada": 1}
                 for j, (x1, y1, x2, y2) in enumerate(pegadas)]
        imagenes[rel] = {**meta, "instancias": inst}
        if (k + 1) % 300 == 0:
            print("  %s: %d/%d" % (nombre, k + 1, len(base)), flush=True)
    cnt = conteo_por_estrato(imagenes)
    guardar_gt(os.path.join(dir_out, "gt_%s.json" % nombre), nombre, dir_out, imagenes,
               extra={"generador": "geometria real (patrones CityPersons train, val_interno) + siluetas v2 (banco test)",
                      "rango_cobertura_patron": list(RANGO_CONTROL), "semilla": semilla,
                      "iou_medio_recorte_region_oculta": round(float(np.mean(ious)), 3), "conteo_estrato_efectivo": cnt})
    print("  %s estratos efectivos: %s; IoU medio %.2f" % (nombre, cnt, float(np.mean(ious))))


# ----------------------------------------------------------------------------- analisis y veredicto
def cmd_analisis(B=1000, B_jer=2000, semilla=0):
    import pandas as pd
    B23 = _modulo("jerarquico23", "23_bootstrap_jerarquico.py")
    A11 = B23.A11
    from argos_lib.ap import emparejar_conjunto
    from argos_lib.gt import cargar_detecciones, cargar_gt
    dir_res = os.path.join(RAIZ, "resultados_h10")
    corr = A11.cargar_corridas(dir_res)
    var_de = {c: d["variante"] for c, d in corr.items()}
    contrastes = ["V3G-V1", "V3S-V1", "V3G-V3S"]
    celdas = [CONTROL, ("silueta_severa", "severa")] + [(c, e) for _, c, e in REALES]
    rnd, rnd_j = np.random.RandomState(semilla), np.random.RandomState(semilla)
    filas = []
    for conj, est in celdas:
        ruta_gt = next((d["conjuntos"][conj] for d in corr.values() if conj in d["conjuntos"]), None)
        if ruta_gt is None:
            continue
        gt = cargar_gt(ruta_gt)
        estr = {}
        for c in corr:
            rd = os.path.join(dir_res, "det", "%s__%s.json" % (c, conj))
            if os.path.exists(rd):
                emp, _ = emparejar_conjunto(gt["imagenes"], cargar_detecciones(rd)["detecciones"], estrato=est)
                estr[c] = A11.APBootstrap(emp)
        n_img = len(gt["imagenes"])
        r_img = B23.bootstrap_dos_niveles(estr, var_de, contrastes, n_img, B, rnd)
        r_jer = B23.bootstrap_dos_niveles(estr, var_de, contrastes, n_img, B_jer, rnd_j)
        full = {c: estr[c].ap() for c in estr}
        m = lambda v: float(np.mean([full[c] for c in estr if var_de[c] == v]))
        n_gt = int(estr[next(iter(estr))].n_gt_img.sum())
        for k in contrastes:
            a, b = k.split("-")
            li, hi = A11.ic(r_img[k][0]); lj, hj = A11.ic(r_jer[k][1])
            filas.append({"conjunto": conj, "estrato": est, "contraste": k, "n_gt": n_gt, "AP_a": round(m(a), 4), "AP_b": round(m(b), 4),
                          "delta_pp": round(100 * (m(a) - m(b)), 2), "IC_imagenes_lo": round(100 * li, 2), "IC_imagenes_hi": round(100 * hi, 2),
                          "IC_jerarquico_lo": round(100 * lj, 2), "IC_jerarquico_hi": round(100 * hj, 2)})
        print("  %-24s %-8s listo" % (conj, est))
    df = pd.DataFrame(filas)
    os.makedirs(os.path.join(dir_res, "analisis"), exist_ok=True)
    df.to_csv(os.path.join(dir_res, "analisis", "contrastes_h10.csv"), index=False)
    md, v = veredicto_md(df)
    open(os.path.join(RAIZ, "informes", "veredicto_h10.md"), "w", encoding="utf-8").write(md)
    print(md)
    print("H10: %s" % v)


def _celda(df, conj, est, k):
    f = df[(df.conjunto == conj) & (df.estrato == est) & (df.contraste == k)]
    return None if f.empty else f.iloc[0]


def relevante(r):
    return r is not None and r.delta_pp >= UMBRAL and r.IC_imagenes_lo > 0


def veredicto(df):
    ctrl = _celda(df, *CONTROL, "V3G-V1")
    mejora = sum(1 for _, c, e in REALES if relevante(_celda(df, c, e, "V3G-V1")))
    geo = sum(1 for _, c, e in REALES if relevante(_celda(df, c, e, "V3G-V3S")))
    if not relevante(ctrl):
        v = "No concluyente"
    elif mejora >= 2:
        v = "Refutada"
    else:
        v = "Sostenida"
    return v, mejora, geo


def veredicto_md(df):
    v, mejora, geo = veredicto(df)
    f = lambda r: "no calculado" if r is None else "%+.2f pp [%+.2f; %+.2f] (jer. [%+.2f; %+.2f])" % (
        r.delta_pp, r.IC_imagenes_lo, r.IC_imagenes_hi, r.IC_jerarquico_lo, r.IC_jerarquico_hi)
    L = ["# ARGOS-11 — Veredicto de H10 (geometría de la oclusión real, 30 épocas fijas)", "",
         "Generado por `28_geometria.py analisis` (AP@0.5, media de 3 semillas, pesos de la época 30; IC 95 % bootstrap por imágenes, "
         "1 000 réplicas, y jerárquico, 2 000). Regla literal de `PREREGISTRO_H10.md`, sección 2.", "",
         "| Celda | V3ᴳ − V1 | V3ˢ − V1 | V3ᴳ − V3ˢ |", "|---|---|---|---|"]
    for nom, c, e in [("Control geometria_severa", *CONTROL), ("Control silueta_severa (descriptivo)", "silueta_severa", "severa")] + REALES:
        L.append("| %s | %s | %s | %s |" % (nom, f(_celda(df, c, e, "V3G-V1")), f(_celda(df, c, e, "V3S-V1")), f(_celda(df, c, e, "V3G-V3S"))))
    L += ["", "**H10 (primaria):** fuentes reales con V3ᴳ − V1 ≥ +2 pp e IC > 0: **%d de 3** (para refutar se requieren 2)." % mejora,
          "", "## Veredicto H10: **%s**" % v, "",
          "**Contraste secundario pre-registrado (efecto de la geometría, V3ᴳ − V3ˢ):** fuentes reales con ≥ +2 pp e IC > 0: "
          "**%d de 3** (la geometría «mejora la transferencia» si son al menos 2)." % geo, "",
          "Declarado en el pre-registro: CityPersons comparte la distribución de la geometría con los patrones de entrenamiento "
          "(que vienen de CityPersons train); NightOwls y ExDark no."]
    return "\n".join(L) + "\n", v


# ----------------------------------------------------------------------------- autotest
def selftest():
    fallos = []

    def comp(desc, ok):
        print("  [%s] %s" % ("OK" if ok else "FALLO", desc))
        if not ok:
            fallos.append(desc)
    p = patron_de_cajas((100, 100, 40, 100), (100, 100, 40, 40))           # visible arriba 40 %
    comp("patron: visible arriba 40 %% -> cobertura 0,60 (%s)" % (p,), p is not None and abs(p[4] - 0.60) < 1e-3)
    comp("lados: solo abajo", lados_de(p) == {"abajo": True, "izquierda": False, "derecha": False, "arriba": False})
    comp("patron: visible fuera de la caja -> None", patron_de_cajas((0, 0, 10, 10), (50, 50, 5, 5)) is None)
    regs = [{"nombre": "a.png", "bbs": [[1, 0, 0, 40, 100, 1, 0, 0, 40, 40], [2, 0, 0, 40, 100, 2, 0, 0, 40, 40],
                                        [1, 0, 0, 10, 30, 3, 0, 0, 10, 10], [1, 0, 0, 40, 100, 4, 0, 0, 40, 95]]}]
    pats = extraer_patrones(regs, {"a.png"}, rango=(0.30, 0.85))
    comp("extraer: solo peatones de >= 50 px dentro del rango (1)", len(pats) == 1)
    H = mascara_oculta(p, 20, 50)
    comp("mascara oculta: 60 %% de la rejilla", abs(H.mean() - 0.60) < 0.03)
    alpha = np.ones((60, 80), dtype=np.float32)                           # recorte rectangular macizo
    col = buscar_colocacion(alpha, p, 40, 100)
    comp("colocacion de un recorte macizo cubre H con IoU > 0,6 (%.2f)" % col[3], col[3] > 0.6)
    im = np.full((300, 300, 3), 60, np.uint8)
    masc = np.zeros((300, 300), np.uint8)
    from argos_lib.geometria import pegar_geometria
    bgr = np.full((60, 80, 3), 200, np.uint8)
    cov, caja_ocl, iou = pegar_geometria(im, masc, (100, 100, 140, 200), bgr, alpha, p)
    comp("pegado: cobertura efectiva cercana a 0,60 (%.2f)" % cov, 0.45 <= cov <= 0.80)
    comp("pegado: la parte de arriba de la caja queda casi intacta", masc[100:130, 100:140].mean() < 0.15)
    import pandas as pd
    def df(ctrl, a, b, c, g=(0, -1, 1)):
        filas = []
        for (cj, es), (d, lo, hi) in zip([CONTROL] + [(x[1], x[2]) for x in REALES], [ctrl, a, b, c]):
            filas.append({"conjunto": cj, "estrato": es, "contraste": "V3G-V1", "delta_pp": d, "IC_imagenes_lo": lo, "IC_imagenes_hi": hi})
            filas.append({"conjunto": cj, "estrato": es, "contraste": "V3G-V3S", "delta_pp": g[0], "IC_imagenes_lo": g[1], "IC_imagenes_hi": g[2]})
        return pd.DataFrame(filas)
    comp("veredicto: control sin aprender -> no concluyente", veredicto(df((1, 0.1, 2), (5, 1, 9), (5, 1, 9), (5, 1, 9)))[0] == "No concluyente")
    comp("veredicto: 2 de 3 -> refutada", veredicto(df((9, 7, 11), (3, 1, 5), (2.1, 0.2, 4), (0, -2, 2)))[0] == "Refutada")
    comp("veredicto: 1 de 3 -> sostenida", veredicto(df((9, 7, 11), (3, 1, 5), (1.9, 0.2, 4), (0, -2, 2)))[0] == "Sostenida")
    comp("geometria: cuenta V3G-V3S", veredicto(df((9, 7, 11), (0, -1, 1), (0, -1, 1), (0, -1, 1), g=(3, 1, 5)))[2] == 3)
    print("\n%s" % ("AUTOTEST SUPERADO" if not fallos else "FALLOS: %s" % fallos))
    sys.exit(1 if fallos else 0)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - H10: geometria de la oclusion real")
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("patrones"); sub.add_parser("estadisticas")
    d = sub.add_parser("demo"); d.add_argument("--n", type=int, default=12); d.add_argument("--semilla", type=int, default=0)
    p = sub.add_parser("prueba"); p.add_argument("--semilla", type=int, default=2024)
    sub.add_parser("analisis")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    {"patrones": cmd_patrones, "estadisticas": cmd_estadisticas, "analisis": cmd_analisis}.get(a.cmd, lambda: None)()
    if a.cmd == "demo":
        cmd_demo(a.n, a.semilla)
    elif a.cmd == "prueba":
        cmd_prueba(a.semilla)
    elif a.cmd is None:
        ap.print_help()


if __name__ == "__main__":
    main()
