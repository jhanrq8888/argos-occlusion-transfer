# -*- coding: utf-8 -*-
"""
Formato comun de ground truth estratificado (fichero gt_<conjunto>.json).

    {
      "conjunto": "test_real",
      "dir_imagenes": "D:/.../dataset/images",     # raiz de las rutas
      "imagenes": {
        "test/2015_00001.jpg": {
          "ancho": 640, "alto": 480, "luz": "Strong",
          "instancias": [
            {"id": "2015_00001#0", "x1": .., "y1": .., "x2": .., "y2": ..,
             "estrato": "sin|ligera|moderada|severa|sin_anotar|ignorar",
             "truncado": 0, "cobertura": 0.0}
          ]
        }
      }
    }

Un mismo fichero sirve para el subconjunto real anotado, para los
sinteticos por estrato y para las fuentes externas: el script de
evaluacion (09) no distingue de donde salio.

Detecciones (fichero det_<corrida>_<conjunto>.json):

    {"pesos": "...", "conjunto": "...", "conf": 0.001, "iou_nms": 0.7,
     "detecciones": {"test/2015_00001.jpg": [[x1,y1,x2,y2,score], ...]}}
"""

import json
import os

ILUMINACION = {1: "Low", 2: "Ambient", 3: "Object", 4: "Single", 5: "Weak",
               6: "Strong", 7: "Screen", 8: "Window", 9: "Shadow",
               10: "Twilight"}


def leer_luz_por_imagen(ruta_lista):
    """imageclasslist.txt -> {nombre_imagen_minusculas: condicion_de_luz}."""
    luz = {}
    if not ruta_lista or not os.path.exists(ruta_lista):
        return luz
    with open(ruta_lista, "r", encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            c = linea.split()
            if len(c) < 5 or c[0].lower().startswith("name"):
                continue
            try:
                luz[c[0].lower()] = ILUMINACION.get(int(c[2]), "Desconocida")
            except ValueError:
                continue
    return luz


def dimensiones(ruta):
    from PIL import Image
    with Image.open(ruta) as im:
        return im.size


def cargar_split_yolo(dataset, split="test", luz_por_imagen=None):
    """Lee images/<split> y labels/<split> y devuelve el dict de imagenes del
    formato comun, con todas las instancias en estrato 'sin_anotar' (persona
    valida cuyo estrato se desconoce: cuenta en la evaluacion global y es
    ignore en la estratificada) y cobertura 0. 'ignorar' se reserva para las
    no evaluables. Coordenadas en pixeles, xyxy."""
    dir_img = os.path.join(dataset, "images", split)
    dir_lab = os.path.join(dataset, "labels", split)
    luz_por_imagen = luz_por_imagen or {}
    imagenes = {}
    nombres = {os.path.splitext(f)[0]: f for f in os.listdir(dir_img)}
    for fl in sorted(os.listdir(dir_lab)):
        if not fl.endswith(".txt"):
            continue
        base = os.path.splitext(fl)[0]
        nombre = nombres.get(base)
        if nombre is None:
            continue
        try:
            W, H = dimensiones(os.path.join(dir_img, nombre))
        except Exception:
            continue
        inst = []
        with open(os.path.join(dir_lab, fl), encoding="utf-8") as fh:
            for k, linea in enumerate(fh):
                p = linea.split()
                if len(p) != 5:
                    continue
                xc, yc, w, h = (float(v) for v in p[1:])
                inst.append({"id": "%s#%d" % (base, k),
                             "x1": (xc - w / 2) * W, "y1": (yc - h / 2) * H,
                             "x2": (xc + w / 2) * W, "y2": (yc + h / 2) * H,
                             "estrato": "sin_anotar", "truncado": 0,
                             "cobertura": 0.0})
        imagenes["%s/%s" % (split, nombre)] = {
            "ancho": W, "alto": H,
            "luz": luz_por_imagen.get(nombre.lower(), "Desconocida"),
            "instancias": inst}
    return imagenes


def guardar_gt(ruta, conjunto, dir_imagenes, imagenes, extra=None):
    doc = {"conjunto": conjunto, "dir_imagenes": os.path.abspath(dir_imagenes),
           "imagenes": imagenes}
    if extra:
        doc.update(extra)
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
    return doc


def cargar_gt(ruta):
    with open(ruta, encoding="utf-8") as fh:
        return json.load(fh)


def conteo_por_estrato(imagenes):
    from collections import Counter
    c = Counter()
    for im in imagenes.values():
        for o in im["instancias"]:
            c[o["estrato"]] += 1
    return dict(c)


def guardar_detecciones(ruta, pesos, conjunto, detecciones, conf, iou_nms,
                        extra=None):
    doc = {"pesos": str(pesos), "conjunto": conjunto, "conf": conf,
           "iou_nms": iou_nms, "detecciones": detecciones}
    if extra:
        doc.update(extra)
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)


def cargar_detecciones(ruta):
    with open(ruta, encoding="utf-8") as fh:
        return json.load(fh)
