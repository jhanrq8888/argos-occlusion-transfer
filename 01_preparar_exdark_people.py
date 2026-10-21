#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 — Paso 1 (S1): preparacion de ExDark-People.

Convierte el dataset ExDark al formato YOLO monoclase (person), aplica el
split oficial, produce los conteos que exige el hito de control de S4 y
ejecuta control de calidad sobre las anotaciones.

Uso:
    python 01_preparar_exdark_people.py --raiz /ruta/a/ExDark --salida ./dataset
    python 01_preparar_exdark_people.py --selftest      # verifica la logica

Estructura esperada en --raiz:
    ExDark/<Clase>/<imagen>            (12 carpetas de clase)
    ExDark_Annno/<Clase>/<imagen>.txt  (anotaciones bbGt)
    imageclasslist.txt                 (clase, iluminacion, in/out, split)

Salida:
    dataset/images/{train,val,test}/   (enlaces simbolicos, no copias)
    dataset/labels/{train,val,test}/   (.txt en formato YOLO)
    dataset/splits/*.txt               (listas exactas, para reproducibilidad)
    dataset/data.yaml                  (config Ultralytics)
    dataset/reporte_preparacion.json   (conteos y control de calidad)
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
from collections import Counter, defaultdict

# --- Constantes del dataset -------------------------------------------------
# Orden oficial de clases de ExDark en imageclasslist.txt (1-indexado).
CLASES_EXDARK = ["Bicycle", "Boat", "Bottle", "Bus", "Car", "Cat", "Chair",
                 "Cup", "Dog", "Motorbike", "People", "Table"]

# Condiciones de iluminacion de ExDark (1-indexado).
ILUMINACION = {1: "Low", 2: "Ambient", 3: "Object", 4: "Single", 5: "Weak",
               6: "Strong", 7: "Screen", 8: "Window", 9: "Shadow",
               10: "Twilight"}

SPLIT = {1: "train", 2: "val", 3: "test"}

# La etiqueta de persona en los ficheros de anotacion de ExDark.
ETIQUETA_PERSONA = "people"


# --- Lectura de anotaciones bbGt --------------------------------------------
def leer_anotacion_bbgt(ruta):
    """Lee un fichero bbGt de ExDark y devuelve las cajas de la clase People.

    Formato bbGt v3, una caja por linea:
        etiqueta  l  t  w  h  occ  vx vy vw vh  ign  ang

    Devuelve (cajas, incidencias) donde cada caja es un dict con l/t/w/h y
    el valor del campo `occ`, y las incidencias son anomalias detectadas.
    """
    cajas, incidencias = [], []
    try:
        with open(ruta, "r", encoding="utf-8", errors="replace") as fh:
            lineas = fh.read().splitlines()
    except OSError as e:
        return [], ["no_legible: %s" % e]

    for i, linea in enumerate(lineas):
        linea = linea.strip()
        if not linea or linea.startswith("%"):
            continue                      # cabecera "% bbGt version=3"
        campos = linea.split()
        if len(campos) < 5:
            incidencias.append("linea_%d_campos_insuficientes" % i)
            continue
        if campos[0].strip().lower() != ETIQUETA_PERSONA:
            continue                      # otra clase: se descarta
        try:
            l, t, w, h = (float(campos[j]) for j in range(1, 5))
        except ValueError:
            incidencias.append("linea_%d_coordenadas_no_numericas" % i)
            continue
        # El campo `occ` de bbGt puede traer una marca de oclusion. ExDark
        # normalmente lo deja a 0, pero conviene comprobarlo: si viniera
        # informado, reduciria el trabajo de anotacion manual.
        occ = 0
        if len(campos) >= 6:
            try:
                occ = int(float(campos[5]))
            except ValueError:
                pass
        cajas.append({"l": l, "t": t, "w": w, "h": h, "occ": occ})
    return cajas, incidencias


def a_yolo(caja, ancho_img, alto_img):
    """Convierte una caja bbGt (l,t,w,h en pixeles) a YOLO (xc,yc,w,h norm.).

    Devuelve (tupla_yolo, incidencia). Recorta al marco de la imagen; si tras
    recortar el area es nula, la caja se descarta.
    """
    l, t, w, h = caja["l"], caja["t"], caja["w"], caja["h"]
    x1, y1 = max(0.0, l), max(0.0, t)
    x2, y2 = min(float(ancho_img), l + w), min(float(alto_img), t + h)
    if x2 <= x1 or y2 <= y1:
        return None, "caja_fuera_de_marco"
    recortada = (x1 > l or y1 > t or x2 < l + w or y2 < t + h)
    xc = ((x1 + x2) / 2.0) / ancho_img
    yc = ((y1 + y2) / 2.0) / alto_img
    wn = (x2 - x1) / ancho_img
    hn = (y2 - y1) / alto_img
    if wn <= 0 or hn <= 0:
        return None, "caja_area_nula"
    return (xc, yc, wn, hn), ("caja_recortada" if recortada else None)


def dimensiones_imagen(ruta):
    """Devuelve (ancho, alto) usando PIL; None si la imagen no se puede leer."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit("ERROR: falta Pillow. Instalar con: pip install Pillow")
    try:
        with Image.open(ruta) as im:
            return im.size
    except Exception:
        return None


def leer_lista_maestra(ruta):
    """Lee imageclasslist.txt -> {nombre_imagen: {clase, luz, exterior, split}}."""
    registros = {}
    with open(ruta, "r", encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            campos = linea.split()
            if len(campos) < 5 or campos[0].lower().startswith("name"):
                continue                  # cabecera o linea incompleta
            try:
                registros[campos[0]] = {
                    "clase": int(campos[1]),
                    "luz": int(campos[2]),
                    "exterior": int(campos[3]),
                    "split": int(campos[4]),
                }
            except ValueError:
                continue
    return registros


# --- Proceso principal ------------------------------------------------------
def preparar(raiz, salida, enlazar=True):
    preparar._aviso_symlink = getattr(preparar, "_aviso_symlink", False)
    dir_img = os.path.join(raiz, "ExDark")
    dir_ann = os.path.join(raiz, "ExDark_Annno")
    lista = os.path.join(raiz, "imageclasslist.txt")

    for ruta, etiqueta in ((dir_img, "ExDark/"), (dir_ann, "ExDark_Annno/"),
                           (lista, "imageclasslist.txt")):
        if not os.path.exists(ruta):
            sys.exit("ERROR: no se encuentra %s en %s" % (etiqueta, raiz))

    registros = leer_lista_maestra(lista)
    print("Registros en imageclasslist.txt: %d" % len(registros))

    # Indice de imagenes en disco: nombre -> ruta. ExDark mezcla extensiones
    # en mayusculas y minusculas, asi que se indexa de forma insensible.
    indice = {}
    for clase in os.listdir(dir_img):
        d = os.path.join(dir_img, clase)
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            indice[f.lower()] = os.path.join(d, f)
    print("Imagenes halladas en disco: %d" % len(indice))

    for sub in ("images", "labels"):
        for part in SPLIT.values():
            os.makedirs(os.path.join(salida, sub, part), exist_ok=True)
    os.makedirs(os.path.join(salida, "splits"), exist_ok=True)

    conteos = {p: {"imagenes": 0, "instancias": 0} for p in SPLIT.values()}
    por_luz = defaultdict(lambda: {"imagenes": 0, "instancias": 0})
    por_luz_split = defaultdict(lambda: defaultdict(int))
    listas = defaultdict(list)
    incidencias = Counter()
    areas_rel, occ_no_cero = [], 0
    sin_anotacion, sin_imagen, sin_personas = [], [], 0

    for nombre, meta in sorted(registros.items()):
        clase_carpeta = CLASES_EXDARK[meta["clase"] - 1]
        ruta_img = indice.get(nombre.lower())
        if ruta_img is None:
            sin_imagen.append(nombre)
            continue

        ruta_ann = os.path.join(dir_ann, clase_carpeta, nombre + ".txt")
        if not os.path.exists(ruta_ann):     # tolera variantes de extension
            alt = [f for f in os.listdir(os.path.join(dir_ann, clase_carpeta))
                   if f.lower() == (nombre + ".txt").lower()] \
                if os.path.isdir(os.path.join(dir_ann, clase_carpeta)) else []
            if alt:
                ruta_ann = os.path.join(dir_ann, clase_carpeta, alt[0])
            else:
                sin_anotacion.append(nombre)
                continue

        cajas, inc = leer_anotacion_bbgt(ruta_ann)
        for i in inc:
            incidencias[i] += 1
        if not cajas:
            sin_personas += 1
            continue                        # imagen sin personas: se excluye

        dims = dimensiones_imagen(ruta_img)
        if dims is None:
            incidencias["imagen_no_legible"] += 1
            continue
        ancho, alto = dims

        filas = []
        for caja in cajas:
            if caja["occ"] != 0:
                occ_no_cero += 1
            conv, aviso = a_yolo(caja, ancho, alto)
            if aviso:
                incidencias[aviso] += 1
            if conv is None:
                continue
            xc, yc, wn, hn = conv
            areas_rel.append(wn * hn)
            filas.append("0 %.6f %.6f %.6f %.6f" % (xc, yc, wn, hn))

        if not filas:
            sin_personas += 1
            continue

        part = SPLIT.get(meta["split"])
        if part is None:
            incidencias["split_desconocido"] += 1
            continue

        destino_img = os.path.join(salida, "images", part, nombre)
        if not os.path.exists(destino_img):
            # Windows solo permite symlinks con modo desarrollador activo o
            # permisos de administrador. Si falla, se copia y se avisa una vez.
            if enlazar:
                try:
                    os.symlink(os.path.abspath(ruta_img), destino_img)
                except (OSError, NotImplementedError, AttributeError):
                    if not preparar._aviso_symlink:
                        print("AVISO: este sistema no permite enlaces "
                              "simbolicos; se copiaran las imagenes.")
                        preparar._aviso_symlink = True
                    enlazar = False
                    shutil.copy2(ruta_img, destino_img)
            else:
                shutil.copy2(ruta_img, destino_img)

        base = os.path.splitext(nombre)[0]
        with open(os.path.join(salida, "labels", part, base + ".txt"),
                  "w", encoding="utf-8") as fh:
            fh.write("\n".join(filas) + "\n")

        listas[part].append(nombre)
        conteos[part]["imagenes"] += 1
        conteos[part]["instancias"] += len(filas)
        luz = ILUMINACION.get(meta["luz"], "Desconocida")
        por_luz[luz]["imagenes"] += 1
        por_luz[luz]["instancias"] += len(filas)
        por_luz_split[luz][part] += len(filas)

    for part, nombres in listas.items():
        with open(os.path.join(salida, "splits", "%s.txt" % part),
                  "w", encoding="utf-8") as fh:
            fh.write("\n".join(sorted(nombres)) + "\n")

    with open(os.path.join(salida, "data.yaml"), "w", encoding="utf-8") as fh:
        fh.write("# ARGOS-11 - ExDark-People (monoclase)\n")
        fh.write("path: %s\n" % os.path.abspath(salida))
        fh.write("train: images/train\nval: images/val\ntest: images/test\n")
        fh.write("nc: 1\nnames: [person]\n")

    areas_rel.sort()
    def pct(p):
        return areas_rel[int(p * (len(areas_rel) - 1))] if areas_rel else None

    reporte = {
        "conteos_por_split": conteos,
        "total_imagenes": sum(c["imagenes"] for c in conteos.values()),
        "total_instancias": sum(c["instancias"] for c in conteos.values()),
        "instancias_por_condicion_luz": dict(por_luz),
        "instancias_por_luz_y_split": {k: dict(v)
                                       for k, v in por_luz_split.items()},
        "area_relativa_bbox": {
            "p10": pct(0.10), "p50": pct(0.50), "p90": pct(0.90),
            "fraccion_menor_1pct": (
                sum(1 for a in areas_rel if a < 0.01) / len(areas_rel)
                if areas_rel else None),
        },
        "control_calidad": {
            "imagenes_sin_fichero": len(sin_imagen),
            "imagenes_sin_anotacion": len(sin_anotacion),
            "imagenes_sin_personas": sin_personas,
            "campo_occ_no_cero": occ_no_cero,
            "incidencias": dict(incidencias),
        },
    }
    with open(os.path.join(salida, "reporte_preparacion.json"),
              "w", encoding="utf-8") as fh:
        json.dump(reporte, fh, indent=2, ensure_ascii=False)

    # --- Resumen en consola --------------------------------------------------
    print("\n" + "=" * 62)
    print("ExDark-People preparado en: %s" % os.path.abspath(salida))
    print("=" * 62)
    for part in ("train", "val", "test"):
        c = conteos[part]
        print("  %-6s %5d imagenes  %6d instancias"
              % (part, c["imagenes"], c["instancias"]))
    print("  %-6s %5d imagenes  %6d instancias"
          % ("TOTAL", reporte["total_imagenes"], reporte["total_instancias"]))

    print("\nInstancias por condicion de iluminacion:")
    for luz, v in sorted(por_luz.items(), key=lambda x: -x[1]["instancias"]):
        print("  %-10s %5d instancias en %4d imagenes"
              % (luz, v["instancias"], v["imagenes"]))

    if areas_rel:
        print("\nTamano relativo de las cajas (area bbox / area imagen):")
        print("  p10=%.4f  p50=%.4f  p90=%.4f  |  %.1f%% ocupan <1%% de la imagen"
              % (pct(0.10), pct(0.50), pct(0.90),
                 100 * reporte["area_relativa_bbox"]["fraccion_menor_1pct"]))

    print("\nControl de calidad:")
    cc = reporte["control_calidad"]
    print("  imagenes sin fichero    : %d" % cc["imagenes_sin_fichero"])
    print("  imagenes sin anotacion  : %d" % cc["imagenes_sin_anotacion"])
    print("  imagenes sin personas   : %d (excluidas)" % cc["imagenes_sin_personas"])
    for k, v in sorted(cc["incidencias"].items()):
        print("  %-24s: %d" % (k, v))

    print("\n  campo 'occ' distinto de 0: %d" % cc["campo_occ_no_cero"])
    if cc["campo_occ_no_cero"] == 0:
        print("    -> ExDark no informa oclusion. La anotacion manual del")
        print("       subconjunto real (OE6) es imprescindible, como estaba")
        print("       previsto. Arrancar en S1.")
    else:
        print("    -> ATENCION: hay marcas de oclusion en el dataset. Revisar")
        print("       si son aprovechables antes de anotar a mano: podria")
        print("       reducir mucho el trabajo de S1-S4.")

    # --- Chequeo frente al plan ---------------------------------------------
    print("\nContraste con el cronograma:")
    n_test = conteos["test"]["instancias"]
    print("  Instancias en test: %d" % n_test)
    if n_test < 300:
        print("  AVISO: por debajo de las 300 instancias que exige OE6.")
        print("         Revisar la regla de fusion de estratos (Seccion 1.9).")
    elif n_test < 600:
        print("  AVISO: hay margen escaso para la cuota de >=50 por estrato.")
        print("         Vigilar el estrato severo en el conteo de S3.")
    else:
        print("  Suficiente para el objetivo de >=300 instancias y >=50 por")
        print("  estrato, si la distribucion de oclusion acompana.")
    return reporte


# --- Autotest ---------------------------------------------------------------
def selftest():
    """Construye un ExDark falso en miniatura y verifica la conversion."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit("ERROR: falta Pillow. Instalar con: pip install Pillow")

    tmp = tempfile.mkdtemp(prefix="exdark_test_")
    raiz = os.path.join(tmp, "raw")
    os.makedirs(os.path.join(raiz, "ExDark", "People"))
    os.makedirs(os.path.join(raiz, "ExDark", "Car"))
    os.makedirs(os.path.join(raiz, "ExDark_Annno", "People"))
    os.makedirs(os.path.join(raiz, "ExDark_Annno", "Car"))

    # Imagen 1 (200x100, train): una persona valida y un coche a descartar.
    Image.new("RGB", (200, 100)).save(os.path.join(raiz, "ExDark", "People", "a.jpg"))
    with open(os.path.join(raiz, "ExDark_Annno", "People", "a.jpg.txt"), "w") as f:
        f.write("%% bbGt version=3\n")
        f.write("People 20 10 40 50 0 0 0 0 0 0 0\n")
        f.write("Car 0 0 10 10 0 0 0 0 0 0 0\n")

    # Imagen 2 (100x100, test): caja que se sale del marco -> debe recortarse.
    Image.new("RGB", (100, 100)).save(os.path.join(raiz, "ExDark", "People", "b.jpg"))
    with open(os.path.join(raiz, "ExDark_Annno", "People", "b.jpg.txt"), "w") as f:
        f.write("%% bbGt version=3\n")
        f.write("People 80 80 60 60 1 0 0 0 0 0 0\n")

    # Imagen 3 (50x50, train): solo un coche -> imagen sin personas, se excluye.
    Image.new("RGB", (50, 50)).save(os.path.join(raiz, "ExDark", "Car", "c.jpg"))
    with open(os.path.join(raiz, "ExDark_Annno", "Car", "c.jpg.txt"), "w") as f:
        f.write("%% bbGt version=3\nCar 5 5 10 10 0 0 0 0 0 0 0\n")

    with open(os.path.join(raiz, "imageclasslist.txt"), "w") as f:
        f.write("a.jpg 11 1 2 1\n")   # People, Low,     exterior, train
        f.write("b.jpg 11 5 1 3\n")   # People, Weak,    interior, test
        f.write("c.jpg 5 2 2 1\n")    # Car,    Ambient, exterior, train

    salida = os.path.join(tmp, "dataset")
    print("--- ejecutando preparacion sobre dataset sintetico ---\n")
    rep = preparar(raiz, salida, enlazar=False)

    print("\n" + "=" * 62)
    print("VERIFICACION")
    print("=" * 62)
    fallos = []

    def comprobar(desc, obtenido, esperado):
        ok = obtenido == esperado
        print("  [%s] %-46s %s" % ("ok" if ok else "FALLA", desc, obtenido))
        if not ok:
            fallos.append("%s: esperado %r, obtenido %r"
                          % (desc, esperado, obtenido))

    comprobar("imagenes en train (c.jpg excluida)",
              rep["conteos_por_split"]["train"]["imagenes"], 1)
    comprobar("imagenes en test", rep["conteos_por_split"]["test"]["imagenes"], 1)
    comprobar("imagenes sin personas descartadas",
              rep["control_calidad"]["imagenes_sin_personas"], 1)
    comprobar("total de instancias person", rep["total_instancias"], 2)
    comprobar("caja recortada al marco detectada",
              rep["control_calidad"]["incidencias"].get("caja_recortada"), 1)
    comprobar("campo occ no cero detectado",
              rep["control_calidad"]["campo_occ_no_cero"], 1)

    # Conversion exacta: persona en (20,10,40,50) sobre imagen de 200x100.
    # xc=(20+60)/2/200=0.2  yc=(10+60)/2/100=0.35  w=40/200=0.2  h=50/100=0.5
    with open(os.path.join(salida, "labels", "train", "a.txt")) as f:
        got = f.read().strip()
    comprobar("conversion a YOLO exacta", got, "0 0.200000 0.350000 0.200000 0.500000")

    # La caja de b.jpg (80,80,60,60) sobre 100x100 se recorta a (80,80,20,20):
    # xc=90/100=0.9  yc=0.9  w=0.2  h=0.2
    with open(os.path.join(salida, "labels", "test", "b.txt")) as f:
        got_b = f.read().strip()
    comprobar("recorte al marco correcto", got_b,
              "0 0.900000 0.900000 0.200000 0.200000")

    comprobar("iluminacion registrada por instancia",
              rep["instancias_por_condicion_luz"].get("Low", {}).get("instancias"), 1)

    shutil.rmtree(tmp)
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d):" % len(fallos))
        for f_ in fallos:
            print("   - %s" % f_)
        return 1
    print("AUTOTEST SUPERADO: 9/9 comprobaciones.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - preparar ExDark-People")
    ap.add_argument("--raiz", help="Directorio raiz de ExDark")
    ap.add_argument("--salida", default="./dataset", help="Directorio de salida")
    ap.add_argument("--copiar", action="store_true",
                    help="Copiar imagenes en vez de enlazarlas (usa mas disco)")
    ap.add_argument("--selftest", action="store_true",
                    help="Verificar la logica con un dataset sintetico")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())
    if not args.raiz:
        ap.error("se requiere --raiz (o --selftest)")
    preparar(args.raiz, args.salida, enlazar=not args.copiar)


if __name__ == "__main__":
    main()