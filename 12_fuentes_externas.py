#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Paso 10: fuentes externas de oclusion real (Fuentes 4, 5 y 6).

Convierte las anotaciones de NightOwls y CityPersons al formato comun de
argos_lib.gt (dataset/externos/gt_*.json) para que 09 las evalue con el
mismo script y la misma regla de regiones ignore. No descarga nada: ambos
datasets exigen registro (NightOwls: nightowls-dataset.org; CityPersons:
cityscapes-dataset.com, paquetes gtBboxCityPersons + leftImg8bit).

NightOwls (Fuentes 4 y 5; nocturno, captura desde vehiculo)
    Formato COCO-like: images[] y annotations[] con category_id
    (1 pedestrian, 2 bicycledriver, 3 motorbikedriver, 4 ignore) y los
    atributos occluded / truncated / difficult (booleanos).
    Mapeo documentado:  pedestrian & !occluded -> 'sin'
                        pedestrian &  occluded -> 'ocluida'   (el atributo es
                        BINARIO: no permite separar ligera/moderada/severa)
                        ignore, bicycledriver, motorbikedriver -> 'ignorar'
    Se reporta como generalizacion (OE7) y como segunda fuente de oclusion
    real (OE6) al nivel de resolucion que su atributo permite.

CityPersons (Fuente 6; DIURNO: solo contraste frente a oclusion aislada)
    gtBboxCityPersons/<split>/<ciudad>/*_gtBboxCityPersons.json con objects[]
    {label, bbox [x,y,w,h], bboxVis [x,y,w,h]}. La fraccion visible
    vis = area(bboxVis)/area(bbox) da la oclusion 1 - vis, que se mapea:
      (a) a NUESTROS estratos: sin [0,.10) ligera [.10,.30) moderada [.30,.70)
          severa [.70,1]                            -> gt_citypersons.json
      (b) a la CONVENCION de Zhang et al. 2017: bare (vis>=.90), partial
          (.65<=vis<.90), heavy (.20<=vis<.65); vis<.20 -> 'ignorar'; y solo
          con altura >= 50 px (conjunto 'reasonable' ampliado)
                                                   -> gt_citypersons_convencion.json
    label 'pedestrian' -> persona; 'rider', 'sitting person', 'person
    (other)', 'person group', 'ignore' -> 'ignorar'.

Uso:
    python 12_fuentes_externas.py nightowls --anotaciones ruta/nightowls_validation.json \
        --imagenes ruta/nightowls_validation --max-imagenes 2000
    python 12_fuentes_externas.py citypersons --anotaciones ruta/gtBboxCityPersons/val \
        --imagenes ruta/leftImg8bit/val
    python 12_fuentes_externas.py citypersons-mat --anotaciones anno_val.mat \
        --imagenes externos/citypersons/Citypersons/images/val
    python 12_fuentes_externas.py --selftest

Formato .mat oficial (github.com/cvgroup-njust/CityPersons, anno_val.mat):
    celda de structs con im_name, cityname y bbs (n x 10):
    [clase, x1, y1, w, h, instance_id, x1_vis, y1_vis, w_vis, h_vis]
    clase: 0 ignore, 1 pedestrian, 2 rider, 3 sitting person, 4 other
    person, 5 group of people. Mismo mapeo que el JSON: solo 1 es persona.
"""

import argparse
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argos_lib import estrato_de_cobertura                    # noqa: E402
from argos_lib.gt import conteo_por_estrato, guardar_gt      # noqa: E402

RAIZ = os.path.dirname(os.path.abspath(__file__))
NO_CAT = {1: "pedestrian", 2: "bicycledriver", 3: "motorbikedriver", 4: "ignore"}
CP_LIMITES = {"bare": (0.90, 1.01), "partial": (0.65, 0.90), "heavy": (0.20, 0.65)}


def convertir_nightowls(ruta_json, dir_imagenes, salida, max_imagenes=2000,
                        semilla=0, solo_con_personas=True):
    with open(ruta_json, encoding="utf-8") as fh:
        d = json.load(fh)
    imgs = {im["id"]: im for im in d["images"]}
    por_img = {}
    for a in d["annotations"]:
        por_img.setdefault(a["image_id"], []).append(a)
    ids = sorted(por_img if solo_con_personas else imgs)
    if solo_con_personas:
        ids = [i for i in ids if any(a["category_id"] == 1 for a in por_img[i])]
    rnd = np.random.RandomState(semilla)
    if max_imagenes and len(ids) > max_imagenes:
        ids = sorted(rnd.choice(ids, max_imagenes, replace=False).tolist())
    imagenes = {}
    for i in ids:
        im = imgs[i]
        inst = []
        for k, a in enumerate(por_img.get(i, [])):
            x, y, w, h = a["bbox"]
            cat = a.get("category_id")
            if cat == 1:
                est = "ocluida" if a.get("occluded") else "sin"
            else:
                est = "ignorar"
            inst.append({"id": "%s#%d" % (os.path.splitext(im["file_name"])[0], k),
                         "x1": float(x), "y1": float(y), "x2": float(x + w), "y2": float(y + h),
                         "estrato": est, "truncado": int(bool(a.get("truncated"))),
                         "dificil": int(bool(a.get("difficult"))), "cobertura": -1.0,
                         "categoria": NO_CAT.get(cat, str(cat))})
        imagenes[im["file_name"]] = {"ancho": im.get("width"), "alto": im.get("height"),
                                     "luz": "NightOwls", "instancias": inst}
    cnt = conteo_por_estrato(imagenes)
    guardar_gt(salida, "nightowls", dir_imagenes, imagenes,
               extra={"fuente": "NightOwls (Neumann et al. 2019), atributo 'occluded' binario",
                      "mapeo": {"pedestrian & !occluded": "sin", "pedestrian & occluded": "ocluida",
                                "bicycledriver/motorbikedriver/ignore": "ignorar"},
                      "limitacion": "atributo binario: 'ocluida' agrega ligera+moderada+severa; "
                                    "dominio de captura desde vehiculo",
                      "semilla_muestreo": semilla, "conteo": cnt})
    return imagenes, cnt


def _area(b):
    return max(0.0, float(b[2])) * max(0.0, float(b[3]))


CP_CLASES_MAT = {0: "ignore", 1: "pedestrian", 2: "rider", 3: "sitting person",
                 4: "person (other)", 5: "person group"}


def _instancias_cp(objetos, base, min_alto_conv):
    """objetos: lista de (label, bbox[x,y,w,h], bboxVis[x,y,w,h]). Devuelve
    (instancias con estratos propios, instancias con la convencion)."""
    ip, ic_ = [], []
    for k, (label, bbox, vis_box) in enumerate(objetos):
        x, y, w, h = bbox
        caja = {"id": "%s#%d" % (base, k), "x1": float(x), "y1": float(y),
                "x2": float(x + w), "y2": float(y + h), "truncado": 0}
        if label != "pedestrian" or _area(bbox) <= 0:
            ip.append({**caja, "estrato": "ignorar", "cobertura": -1.0, "etiqueta": label})
            ic_.append({**caja, "estrato": "ignorar", "cobertura": -1.0, "etiqueta": label})
            continue
        vis = min(1.0, _area(vis_box) / _area(bbox))
        ocl = 1.0 - vis
        ip.append({**caja, "estrato": estrato_de_cobertura(ocl), "cobertura": round(ocl, 4),
                   "vis": round(vis, 4), "etiqueta": "pedestrian"})
        est = "ignorar"
        if h >= min_alto_conv:
            for nombre, (lo, hi) in CP_LIMITES.items():
                if lo <= vis < hi:
                    est = nombre
        ic_.append({**caja, "estrato": est, "cobertura": round(ocl, 4), "vis": round(vis, 4),
                    "etiqueta": "pedestrian"})
    return ip, ic_


def _guardar_cp(propio, conv, dir_imagenes, salida_propio, salida_conv, fuente, min_alto_conv):
    c1, c2 = conteo_por_estrato(propio), conteo_por_estrato(conv)
    guardar_gt(salida_propio, "citypersons", dir_imagenes, propio,
               extra={"fuente": fuente + ", oclusion = 1 - area(bboxVis)/area(bbox)",
                      "mapeo": "estratos propios por fraccion ocluida", "limitacion": "conjunto DIURNO",
                      "conteo": c1})
    guardar_gt(salida_conv, "citypersons_convencion", dir_imagenes, conv,
               extra={"fuente": fuente,
                      "mapeo": {"bare": "vis>=0.90", "partial": "0.65<=vis<0.90", "heavy": "0.20<=vis<0.65",
                                "vis<0.20 o altura<%d px" % min_alto_conv: "ignorar"},
                      "limitacion": "conjunto DIURNO", "conteo": c2})
    return c1, c2


def convertir_citypersons_mat(ruta_mat, dir_imagenes, salida_propio, salida_conv,
                              min_alto_conv=50):
    """anno_val.mat oficial; las imagenes se buscan por nombre bajo dir_imagenes
    (cualquier subcarpeta), como quedan al extraer la copia de Kaggle."""
    from scipy.io import loadmat
    m = loadmat(ruta_mat, squeeze_me=True, struct_as_record=False)
    clave = next(k for k in m if k.startswith("anno"))
    registros = m[clave]
    try:
        registros = list(registros)
    except TypeError:
        registros = [registros]
    disponibles = {}
    for raiz, _d, fs in os.walk(dir_imagenes):
        for f in fs:
            disponibles[f] = os.path.relpath(os.path.join(raiz, f), dir_imagenes).replace("\\", "/")
    propio, conv, sin_imagen = {}, {}, 0
    for r in registros:
        nombre = str(r.im_name)
        rel = disponibles.get(nombre)
        if rel is None:
            sin_imagen += 1
            continue
        bbs = np.atleast_2d(np.asarray(r.bbs, dtype=float))
        objetos = []
        for fila in bbs:
            if len(fila) < 10:
                continue
            objetos.append((CP_CLASES_MAT.get(int(fila[0]), str(int(fila[0]))),
                            list(fila[1:5]), list(fila[6:10])))
        base = os.path.splitext(nombre)[0]
        ip, ic_ = _instancias_cp(objetos, base, min_alto_conv)
        meta = {"ancho": 2048, "alto": 1024, "luz": "Diurno"}
        propio[rel] = {**meta, "instancias": ip}
        conv[rel] = {**meta, "instancias": ic_}
    if sin_imagen:
        print("AVISO: %d registros del .mat sin imagen en %s" % (sin_imagen, dir_imagenes))
    return _guardar_cp(propio, conv, dir_imagenes, salida_propio, salida_conv,
                       "CityPersons (Zhang et al. 2017), anno_val.mat oficial", min_alto_conv)


def convertir_citypersons(dir_anot, dir_imagenes, salida_propio, salida_conv,
                          min_alto_conv=50):
    ficheros = sorted(glob.glob(os.path.join(dir_anot, "**", "*_gtBboxCityPersons.json"),
                                recursive=True))
    if not ficheros:
        sys.exit("No se encontraron *_gtBboxCityPersons.json en %s" % dir_anot)
    propio, conv = {}, {}
    for f in ficheros:
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        rel = os.path.relpath(f, dir_anot).replace("\\", "/")
        rel_img = rel.replace("_gtBboxCityPersons.json", "_leftImg8bit.png")
        base = os.path.splitext(os.path.basename(rel_img))[0]
        objetos = [(o.get("label"), o["bbox"], o.get("bboxVis", o["bbox"]))
                   for o in d.get("objects", [])]
        ip, ic_ = _instancias_cp(objetos, base, min_alto_conv)
        meta = {"ancho": d.get("imgWidth"), "alto": d.get("imgHeight"), "luz": "Diurno"}
        propio[rel_img] = {**meta, "instancias": ip}
        conv[rel_img] = {**meta, "instancias": ic_}
    return _guardar_cp(propio, conv, dir_imagenes, salida_propio, salida_conv,
                       "CityPersons (Zhang et al. 2017)", min_alto_conv)


def selftest():
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="externos_test_")
    fallos = []

    def comp(desc, obt, esp):
        ok = obt == esp
        print("  [%s] %-50s %s" % ("ok" if ok else "FALLA", desc, obt))
        if not ok:
            fallos.append(desc)

    # NightOwls falso.
    no = {"images": [{"id": 1, "file_name": "a.png", "width": 1024, "height": 640},
                     {"id": 2, "file_name": "b.png", "width": 1024, "height": 640},
                     {"id": 3, "file_name": "c.png", "width": 1024, "height": 640}],
          "annotations": [{"id": 1, "image_id": 1, "category_id": 1, "bbox": [10, 10, 20, 50], "occluded": False},
                          {"id": 2, "image_id": 1, "category_id": 1, "bbox": [100, 10, 20, 50], "occluded": True, "truncated": True},
                          {"id": 3, "image_id": 1, "category_id": 4, "bbox": [200, 10, 20, 50]},
                          {"id": 4, "image_id": 2, "category_id": 2, "bbox": [10, 10, 20, 50], "occluded": False}]}
    rj = os.path.join(tmp, "no.json")
    json.dump(no, open(rj, "w"))
    imgs, cnt = convertir_nightowls(rj, tmp, os.path.join(tmp, "gt_no.json"))
    comp("nightowls: solo imagenes con peatones", sorted(imgs), ["a.png"])
    comp("nightowls: sin/ocluida/ignorar", (cnt.get("sin"), cnt.get("ocluida"), cnt.get("ignorar")), (1, 1, 1))
    comp("nightowls: truncado conservado", imgs["a.png"]["instancias"][1]["truncado"], 1)
    imgs2, _ = convertir_nightowls(rj, tmp, os.path.join(tmp, "gt_no2.json"), solo_con_personas=False)
    comp("nightowls: sin filtro incluye las 3 imagenes", len(imgs2), 3)

    # CityPersons falso.
    da = os.path.join(tmp, "gt", "val", "ciudad")
    os.makedirs(da)
    cp = {"imgHeight": 1024, "imgWidth": 2048, "objects": [
        {"label": "pedestrian", "bbox": [0, 0, 40, 100], "bboxVis": [0, 0, 40, 100]},       # vis 1.0 -> sin / bare
        {"label": "pedestrian", "bbox": [0, 0, 40, 100], "bboxVis": [0, 0, 40, 80]},        # vis .8 -> ligera / partial
        {"label": "pedestrian", "bbox": [0, 0, 40, 100], "bboxVis": [0, 0, 40, 40]},        # vis .4 -> moderada / heavy
        {"label": "pedestrian", "bbox": [0, 0, 40, 100], "bboxVis": [0, 0, 40, 10]},        # vis .1 -> severa / ignorar
        {"label": "pedestrian", "bbox": [0, 0, 20, 40], "bboxVis": [0, 0, 20, 40]},         # h<50 -> sin / ignorar(conv)
        {"label": "rider", "bbox": [0, 0, 40, 100], "bboxVis": [0, 0, 40, 100]}]}
    json.dump(cp, open(os.path.join(da, "x_gtBboxCityPersons.json"), "w"))
    c1, c2 = convertir_citypersons(os.path.join(tmp, "gt", "val"), tmp,
                                   os.path.join(tmp, "gt_cp.json"), os.path.join(tmp, "gt_cpc.json"))
    comp("citypersons: estratos propios", (c1.get("sin"), c1.get("ligera"), c1.get("moderada"), c1.get("severa"), c1.get("ignorar")),
         (2, 1, 1, 1, 1))
    comp("citypersons: convencion bare/partial/heavy", (c2.get("bare"), c2.get("partial"), c2.get("heavy"), c2.get("ignorar")),
         (1, 1, 1, 3))
    gt = json.load(open(os.path.join(tmp, "gt_cp.json")))
    comp("citypersons: ruta de imagen derivada", list(gt["imagenes"])[0], "ciudad/x_leftImg8bit.png")
    # .mat oficial falso con la misma escena.
    from scipy.io import savemat
    from PIL import Image
    os.makedirs(os.path.join(tmp, "img", "lindau"))
    Image.new("RGB", (8, 4)).save(os.path.join(tmp, "img", "lindau", "y_leftImg8bit.png"))
    bbs = np.array([[1, 0, 0, 40, 100, 1, 0, 0, 40, 100], [1, 0, 0, 40, 100, 2, 0, 0, 40, 80],
                    [1, 0, 0, 40, 100, 3, 0, 0, 40, 40], [1, 0, 0, 40, 100, 4, 0, 0, 40, 10],
                    [1, 0, 0, 20, 40, 5, 0, 0, 20, 40], [2, 0, 0, 40, 100, 6, 0, 0, 40, 100]], float)
    savemat(os.path.join(tmp, "anno_val.mat"),
            {"anno_val_aligned": np.array([{"cityname": "lindau", "im_name": "y_leftImg8bit.png", "bbs": bbs}],
                                          dtype=object)})
    c3, c4 = convertir_citypersons_mat(os.path.join(tmp, "anno_val.mat"), os.path.join(tmp, "img"),
                                       os.path.join(tmp, "gt_m.json"), os.path.join(tmp, "gt_mc.json"))
    comp("citypersons .mat: mismos estratos que el JSON", c3, c1)
    comp("citypersons .mat: misma convencion que el JSON", c4, c2)
    gtm = json.load(open(os.path.join(tmp, "gt_m.json")))
    comp("citypersons .mat: imagen localizada en subcarpeta", list(gtm["imagenes"])[0], "lindau/y_leftImg8bit.png")
    shutil.rmtree(tmp)
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO: 10/10 comprobaciones.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - fuentes externas")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--salida", default=os.path.join(RAIZ, "dataset", "externos"))
    sub = ap.add_subparsers(dest="cmd")
    n = sub.add_parser("nightowls")
    n.add_argument("--anotaciones", required=True, help="nightowls_validation.json")
    n.add_argument("--imagenes", required=True, help="carpeta con los PNG")
    n.add_argument("--max-imagenes", type=int, default=2000)
    n.add_argument("--semilla", type=int, default=0)
    n.add_argument("--todas", action="store_true", help="incluir imagenes sin peatones")
    c = sub.add_parser("citypersons")
    c.add_argument("--anotaciones", required=True, help="gtBboxCityPersons/<split>")
    c.add_argument("--imagenes", required=True, help="leftImg8bit/<split>")
    c.add_argument("--min-alto", type=int, default=50)
    cm = sub.add_parser("citypersons-mat")
    cm.add_argument("--anotaciones", required=True, help="anno_val.mat oficial")
    cm.add_argument("--imagenes", required=True, help="carpeta con los PNG de val (subcarpetas ok)")
    cm.add_argument("--min-alto", type=int, default=50)
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    os.makedirs(args.salida, exist_ok=True)
    if args.cmd == "nightowls":
        _, cnt = convertir_nightowls(args.anotaciones, args.imagenes,
                                     os.path.join(args.salida, "gt_nightowls.json"),
                                     args.max_imagenes, args.semilla, not args.todas)
        print("NightOwls -> %s  conteo: %s" % (os.path.join(args.salida, "gt_nightowls.json"), cnt))
    elif args.cmd == "citypersons":
        c1, c2 = convertir_citypersons(args.anotaciones, args.imagenes,
                                       os.path.join(args.salida, "gt_citypersons.json"),
                                       os.path.join(args.salida, "gt_citypersons_convencion.json"),
                                       args.min_alto)
        print("CityPersons -> estratos propios %s | convencion %s" % (c1, c2))
    elif args.cmd == "citypersons-mat":
        c1, c2 = convertir_citypersons_mat(args.anotaciones, args.imagenes,
                                           os.path.join(args.salida, "gt_citypersons.json"),
                                           os.path.join(args.salida, "gt_citypersons_convencion.json"),
                                           args.min_alto)
        print("CityPersons (.mat) -> estratos propios %s | convencion %s" % (c1, c2))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
