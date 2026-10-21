#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - H6: replica de entrenamiento sobre CityPersons (PREREGISTRO_H6_H7.md s.3).

Subcomandos (en este orden):
  datos    anno_train.mat -> etiquetas YOLO junto a las imagenes de Kaggle
           (externos/citypersons/Citypersons/labels/train/<ciudad>/*.txt),
           particion interna train 2 675 / val_interno 300 estratificada por
           ciudad (semilla 0) y listas dataset_cp/{train,val_interno}.txt.
           Clase person = pedestrian, rider, sitting person, person (other);
           ignore, person group y altura < 20 px NO se etiquetan.
  bancos   Bancos de siluetas (yolo11s-seg, COCO) disjuntos:
           dataset/siluetas_cp_train (train 2 675) y dataset/siluetas_cp_val
           (val_interno 300). Mismo procedimiento que 15_iteracion2.py bancos.
  val      dataset_cp/val_ocluido/ (copias de val_interno con TODAS las
           personas ocluidas por siluetas del banco cp_val, f~U[.30,.85],
           personas pegadas etiquetadas) y dataset/data_citypersons.yaml con
           val = val_interno + val_ocluido (validacion mixta, como v2.0).
  prueba   Conjuntos de control cp_silueta_{ligera,moderada,severa}: las 500
           imagenes de CityPersons val (evaluacion) con las instancias *bare*
           (vis >= 0,90, h >= 50 px) ocluidas por siluetas del banco cp_val;
           las demas instancias y las personas pegadas son ignore. Estrato
           efectivo por cobertura de mascara, como silueta_*.

Uso:
    python 20_replica_citypersons.py datos
    python 20_replica_citypersons.py bancos --pesos-seg yolo11s-seg.pt
    python 20_replica_citypersons.py val
    python 20_replica_citypersons.py prueba
    python 20_replica_citypersons.py --selftest
"""

import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argos_lib import ESTRATOS, estrato_de_cobertura                         # noqa: E402
from argos_lib.gt import cargar_gt, conteo_por_estrato, guardar_gt          # noqa: E402
from argos_lib.oclusion import RANGO_F_PRUEBA, cobertura_por_caja, escribir_imagen, leer_imagen  # noqa: E402
from argos_lib.siluetas import BancoSiluetas, ocluir_siluetas               # noqa: E402

RAIZ = os.path.dirname(os.path.abspath(__file__))
DIR_CP = os.path.join(RAIZ, "externos", "citypersons")
DIR_IMG_TRAIN = os.path.join(DIR_CP, "Citypersons", "images", "train")
DIR_LBL_TRAIN = os.path.join(DIR_CP, "Citypersons", "labels", "train")
MAT_TRAIN = os.path.join(DIR_CP, "anno_train.mat")
DATASET_CP = os.path.join(RAIZ, "dataset_cp")
DATASET = os.path.join(RAIZ, "dataset")
GT_CONV = os.path.join(DATASET, "externos", "gt_citypersons_convencion.json")
GT_PROPIO = os.path.join(DATASET, "externos", "gt_citypersons.json")
W_CP, H_CP = 2048, 1024
CLASES_PERSON = {1, 2, 3, 4}       # pedestrian, rider, sitting person, person (other)
MIN_ALTO_TRAIN = 20
N_VAL_INTERNO = 300


# ----------------------------------------------------------------------------
# datos
# ----------------------------------------------------------------------------
def leer_mat(ruta):
    from scipy.io import loadmat
    m = loadmat(ruta, squeeze_me=True, struct_as_record=False)
    clave = next(k for k in m if k.startswith("anno"))
    regs = m[clave]
    try:
        regs = list(regs)
    except TypeError:
        regs = [regs]
    out = []
    for r in regs:
        bbs = np.atleast_2d(np.asarray(r.bbs, dtype=float))
        out.append({"nombre": str(r.im_name), "ciudad": str(r.cityname),
                    "bbs": [list(f) for f in bbs if len(f) >= 10]})
    return out


def etiquetas_yolo(bbs, W=W_CP, H=H_CP):
    """Lineas YOLO (clase 0) para las cajas de persona; devuelve (lineas, n_omitidas)."""
    lineas, omit = [], 0
    for f in bbs:
        c, x, y, w, h = int(f[0]), f[1], f[2], f[3], f[4]
        if c not in CLASES_PERSON or h < MIN_ALTO_TRAIN or w <= 0 or h <= 0:
            omit += 1
            continue
        x1, y1 = max(0.0, x), max(0.0, y)
        x2, y2 = min(float(W), x + w), min(float(H), y + h)
        if x2 <= x1 or y2 <= y1:
            omit += 1
            continue
        lineas.append("0 %.6f %.6f %.6f %.6f" % ((x1 + x2) / 2 / W, (y1 + y2) / 2 / H,
                                                (x2 - x1) / W, (y2 - y1) / H))
    return lineas, omit


def particion_por_ciudad(registros, n_val, semilla=0):
    """Muestreo por imagen estratificado por ciudad (cuota proporcional)."""
    rnd = np.random.RandomState(semilla)
    por_ciudad = {}
    for r in registros:
        por_ciudad.setdefault(r["ciudad"], []).append(r["nombre"])
    total = sum(len(v) for v in por_ciudad.values())
    val = set()
    cuotas = {c: len(v) * n_val / total for c, v in por_ciudad.items()}
    enteros = {c: int(np.floor(q)) for c, q in cuotas.items()}
    resto = n_val - sum(enteros.values())
    for c in sorted(cuotas, key=lambda c: cuotas[c] - enteros[c], reverse=True)[:resto]:
        enteros[c] += 1
    for c in sorted(por_ciudad):
        nombres = sorted(por_ciudad[c])
        idx = rnd.choice(len(nombres), enteros[c], replace=False)
        val.update(nombres[i] for i in idx)
    return val


def cmd_datos(semilla):
    registros = leer_mat(MAT_TRAIN)
    val = particion_por_ciudad(registros, N_VAL_INTERNO, semilla)
    os.makedirs(DATASET_CP, exist_ok=True)
    listas = {"train": [], "val_interno": []}
    n_inst, n_omit, sin_img = 0, 0, 0
    for r in registros:
        ruta_img = os.path.join(DIR_IMG_TRAIN, r["ciudad"], r["nombre"])
        if not os.path.exists(ruta_img):
            sin_img += 1
            continue
        lineas, omit = etiquetas_yolo(r["bbs"])
        d = os.path.join(DIR_LBL_TRAIN, r["ciudad"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, os.path.splitext(r["nombre"])[0] + ".txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lineas) + ("\n" if lineas else ""))
        n_inst += len(lineas)
        n_omit += omit
        listas["val_interno" if r["nombre"] in val else "train"].append(ruta_img.replace("\\", "/"))
    for k, v in listas.items():
        with open(os.path.join(DATASET_CP, k + ".txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(sorted(v)) + "\n")
    resumen = {"fuente": "anno_train.mat oficial (Zhang et al. 2017)", "n_registros": len(registros),
               "sin_imagen": sin_img, "train": len(listas["train"]), "val_interno": len(listas["val_interno"]),
               "instancias_etiquetadas": n_inst, "cajas_omitidas": n_omit,
               "clases_person": sorted(CLASES_PERSON), "min_alto_px": MIN_ALTO_TRAIN,
               "semilla_particion": semilla, "ciudades": sorted({r["ciudad"] for r in registros})}
    with open(os.path.join(DATASET_CP, "particion.json"), "w", encoding="utf-8") as fh:
        json.dump(resumen, fh, indent=1)
    print(json.dumps(resumen, indent=1))


def leer_lista(nombre):
    with open(os.path.join(DATASET_CP, nombre + ".txt"), encoding="utf-8") as fh:
        return [l.strip() for l in fh if l.strip()]


# ----------------------------------------------------------------------------
# bancos
# ----------------------------------------------------------------------------
def cmd_bancos(pesos_seg, max_por_clase, device):
    for lista, nombre in (("train", "siluetas_cp_train"), ("val_interno", "siluetas_cp_val")):
        rutas = leer_lista(lista)
        salida = os.path.join(DATASET, nombre)
        print("%s: %d imagenes candidatas" % (lista, len(rutas)), flush=True)
        cnt = BancoSiluetas.construir(rutas, salida, pesos_seg, max_por_clase, device=device)
        print("  -> %s: %s" % (salida, cnt), flush=True)


# ----------------------------------------------------------------------------
# val (validacion mixta)
# ----------------------------------------------------------------------------
def cajas_de_etiqueta(ruta_txt, W=W_CP, H=H_CP):
    cajas = []
    if os.path.exists(ruta_txt):
        with open(ruta_txt, encoding="utf-8") as fh:
            for l in fh:
                p = l.split()
                if len(p) != 5:
                    continue
                cx, cy, w, h = (float(v) for v in p[1:])
                cajas.append(((cx - w / 2) * W, (cy - h / 2) * H, (cx + w / 2) * W, (cy + h / 2) * H))
    return cajas


def ruta_etiqueta(ruta_img):
    return ruta_img.replace("/images/", "/labels/").rsplit(".", 1)[0] + ".txt"


def cmd_val(semilla):
    banco = BancoSiluetas(os.path.join(DATASET, "siluetas_cp_val"))
    out = os.path.join(DATASET_CP, "val_ocluido")
    for sub in ("images", "labels"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    rnd = np.random.RandomState(semilla)
    imagenes, n_inst, n_peg = {}, 0, 0
    rutas = leer_lista("val_interno")
    for k, ruta in enumerate(rutas):
        nombre = os.path.basename(ruta)
        base = os.path.splitext(nombre)[0]
        im = leer_imagen(ruta)
        H, W = im.shape[:2]
        cajas = cajas_de_etiqueta(ruta_etiqueta(ruta), W, H)
        _, masc, pegadas = ocluir_siluetas(im, cajas, rnd, banco, todas=True)
        cov = cobertura_por_caja(masc, cajas) if cajas else []
        escribir_imagen(os.path.join(out, "images", nombre), im)
        lineas = ["0 %.6f %.6f %.6f %.6f" % ((x1 + x2) / 2 / W, (y1 + y2) / 2 / H, (x2 - x1) / W, (y2 - y1) / H)
                  for (x1, y1, x2, y2) in list(cajas) + list(pegadas)]
        with open(os.path.join(out, "labels", base + ".txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lineas) + ("\n" if lineas else ""))
        inst = [{"id": "%s#%d" % (base, i), "x1": c[0], "y1": c[1], "x2": c[2], "y2": c[3], "truncado": 0,
                 "cobertura": round(float(cv), 4), "estrato": estrato_de_cobertura(cv)} for i, (c, cv) in enumerate(zip(cajas, cov))]
        inst += [{"id": "%s#p%d" % (base, i), "x1": x1, "y1": y1, "x2": x2, "y2": y2, "estrato": "sin",
                  "truncado": 0, "cobertura": 0.0, "pegada": 1} for i, (x1, y1, x2, y2) in enumerate(pegadas)]
        imagenes["images/" + nombre] = {"ancho": W, "alto": H, "luz": "Diurno", "instancias": inst}
        n_inst += len(inst)
        n_peg += len(pegadas)
        if (k + 1) % 100 == 0:
            print("  %d/%d" % (k + 1, len(rutas)), flush=True)
    guardar_gt(os.path.join(out, "gt_val_ocluido.json"), "cp_val_ocluido", out, imagenes,
               extra={"generador": "siluetas v2, banco cp_val, todas las instancias, f~U[.30,.85]", "semilla": semilla,
                      "conteo": conteo_por_estrato(imagenes)})
    with open(os.path.join(DATASET, "data_citypersons.yaml"), "w", encoding="utf-8") as fh:
        fh.write("# ARGOS-11 H6 - CityPersons train (particion interna) con validacion mixta\n")
        fh.write("path: %s\n" % os.path.abspath(DATASET_CP))
        fh.write("train: train.txt\nval: [val_interno.txt, val_ocluido/images]\n")
        fh.write("nc: 1\nnames: [person]\n")
    print("val_ocluido: %d imagenes, %d instancias (%d pegadas), estratos %s"
          % (len(imagenes), n_inst, n_peg, conteo_por_estrato(imagenes)))
    print("-> %s" % os.path.join(DATASET, "data_citypersons.yaml"))


# ----------------------------------------------------------------------------
# prueba (control del generador sobre las 500 imagenes de evaluacion)
# ----------------------------------------------------------------------------
def cmd_prueba(semilla):
    banco = BancoSiluetas(os.path.join(DATASET, "siluetas_cp_val"))
    conv = cargar_gt(GT_CONV)
    dir_img = conv["dir_imagenes"]
    raiz_out = os.path.join(DATASET, "test_sintetico")
    for estrato in ("ligera", "moderada", "severa"):
        nombre = "cp_silueta_%s" % estrato
        dir_out = os.path.join(raiz_out, nombre)
        rnd = np.random.RandomState(semilla + 9000 + ESTRATOS.index(estrato))
        lo, hi = RANGO_F_PRUEBA[estrato]
        imagenes = {}
        for k, (rel, meta) in enumerate(sorted(conv["imagenes"].items())):
            im = leer_imagen(os.path.join(dir_img, rel))
            bare = [o for o in meta["instancias"] if o["estrato"] == "bare"]
            otras = [o for o in meta["instancias"] if o["estrato"] != "bare"]
            cajas = [(o["x1"], o["y1"], o["x2"], o["y2"]) for o in bare]
            pegadas, cov = [], []
            if cajas:
                _, masc, pegadas = ocluir_siluetas(im, cajas, rnd, banco, todas=True,
                                                   f_fijo=lambda r: r.uniform(lo, hi))
                cov = cobertura_por_caja(masc, cajas)
            os.makedirs(os.path.dirname(os.path.join(dir_out, rel)), exist_ok=True)
            escribir_imagen(os.path.join(dir_out, rel), im)
            inst = [{**o, "cobertura": round(float(c), 4), "estrato_nominal": estrato, "estrato": estrato_de_cobertura(c)}
                    for o, c in zip(bare, cov)]
            inst += [{**o, "estrato": "ignorar"} for o in otras]
            base = os.path.splitext(os.path.basename(rel))[0]
            inst += [{"id": "%s#p%d" % (base, i), "x1": x1, "y1": y1, "x2": x2, "y2": y2, "estrato": "ignorar",
                      "truncado": 0, "cobertura": 0.0, "pegada": 1} for i, (x1, y1, x2, y2) in enumerate(pegadas)]
            imagenes[rel] = {**meta, "instancias": inst}
            if (k + 1) % 100 == 0:
                print("  %s: %d/%d" % (nombre, k + 1, len(conv["imagenes"])), flush=True)
        cnt = conteo_por_estrato(imagenes)
        guardar_gt(os.path.join(dir_out, "gt_%s.json" % nombre), nombre, dir_out, imagenes,
                   extra={"generador": "siluetas v2 (banco cp_val) sobre instancias bare de CityPersons val",
                          "tipo_parche": "silueta", "estrato_nominal": estrato, "rango_f": [lo, hi],
                          "semilla": semilla, "conteo_estrato_efectivo": cnt})
        print("  %-20s estratos efectivos: %s" % (nombre, cnt), flush=True)


# ----------------------------------------------------------------------------
def selftest():
    fallos = []

    def comp(desc, ok):
        print("  [%s] %s" % ("ok" if ok else "FALLA", desc))
        if not ok:
            fallos.append(desc)

    lineas, omit = etiquetas_yolo([[1, 100, 100, 50, 120, 0, 0, 0, 0, 0],   # pedestrian
                                   [0, 0, 0, 50, 50, 0, 0, 0, 0, 0],         # ignore
                                   [5, 0, 0, 50, 50, 0, 0, 0, 0, 0],         # group
                                   [2, 10, 10, 10, 19, 0, 0, 0, 0, 0],       # rider < 20 px
                                   [3, 2000, 900, 100, 200, 0, 0, 0, 0, 0]]) # sitting, recortada al borde
    comp("solo pedestrian y sitting etiquetadas (2)", len(lineas) == 2 and omit == 3)
    cx, cy, w, h = (float(v) for v in lineas[0].split()[1:])
    comp("normalizacion correcta", abs(cx - 125 / 2048) < 1e-6 and abs(h - 120 / 1024) < 1e-6)
    cx, cy, w, h = (float(v) for v in lineas[1].split()[1:])
    comp("caja recortada al borde de la imagen", abs((cx + w / 2) - 1.0) < 1e-6 and abs((cy + h / 2) - 1.0) < 1e-6)
    regs = [{"nombre": "%s_%03d.png" % (c, i), "ciudad": c, "bbs": []}
            for c, n in (("a", 100), ("b", 50), ("c", 10)) for i in range(n)]
    val = particion_por_ciudad(regs, 32, 0)
    comp("particion: tamano exacto", len(val) == 32)
    comp("particion: cuota por ciudad proporcional", sum(1 for v in val if v.startswith("a_")) == 20
         and sum(1 for v in val if v.startswith("b_")) == 10 and sum(1 for v in val if v.startswith("c_")) == 2)
    comp("particion: determinista", particion_por_ciudad(regs, 32, 0) == val)
    comp("ruta de etiqueta", ruta_etiqueta("x/Citypersons/images/train/aachen/a.png") == "x/Citypersons/labels/train/aachen/a.txt")
    print("\n%s" % ("AUTOTEST SUPERADO" if not fallos else "FALLOS: %s" % fallos))
    sys.exit(1 if fallos else 0)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - H6 replica CityPersons")
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    d = sub.add_parser("datos"); d.add_argument("--semilla", type=int, default=0)
    b = sub.add_parser("bancos"); b.add_argument("--pesos-seg", default="yolo11s-seg.pt")
    b.add_argument("--max-por-clase", type=int, default=800); b.add_argument("--device")
    v = sub.add_parser("val"); v.add_argument("--semilla", type=int, default=31)
    p = sub.add_parser("prueba"); p.add_argument("--semilla", type=int, default=2024)
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.cmd == "datos":
        cmd_datos(a.semilla)
    elif a.cmd == "bancos":
        cmd_bancos(a.pesos_seg, a.max_por_clase, a.device)
    elif a.cmd == "val":
        cmd_val(a.semilla)
    elif a.cmd == "prueba":
        cmd_prueba(a.semilla)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
