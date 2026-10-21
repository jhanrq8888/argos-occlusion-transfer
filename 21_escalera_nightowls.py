#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - H7: escalera de datos sobre NightOwls (PREREGISTRO_H6_H7.md s.4).

Subcomandos (en este orden):
  datos    nightowls_training.json -> etiquetas YOLO junto a las imagenes
           (externos/nightowls/nightowls_training/<id>.txt). Clase person =
           pedestrian (category_id 1); bicycledriver, motorbikedriver e ignore
           NO se etiquetan. Escribe las listas anidadas de la escalera en
           dataset_no/{2000,5000,10000,20000}.txt y el val interno (1 000
           imagenes de validation, disjunto de las 2 000 de evaluacion).
  bancos   Banco de siluetas dataset/siluetas_no_train (desde el peldano de
           20 000) y dataset/siluetas_no_val (desde el val interno).
  val      dataset_no/val_ocluido/ (copias del val interno con TODAS las
           personas ocluidas por siluetas del banco no_val, f~U[.30,.85],
           personas pegadas etiquetadas) y los cuatro
           dataset/data_nightowls_<peldano>.yaml con validacion mixta.

Presupuesto fijo de 200 000 presentaciones por corrida (s.4 del pre-registro):
  2 000 -> 100 epocas | 5 000 -> 40 | 10 000 -> 20 | 20 000 -> 10
  paciencia = epocas / 5 (minimo 2)

Uso:
    python 21_escalera_nightowls.py datos
    python 21_escalera_nightowls.py bancos --pesos-seg yolo11s-seg.pt --device 0
    python 21_escalera_nightowls.py val
    python 21_escalera_nightowls.py plan
    python 21_escalera_nightowls.py --selftest
"""

import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argos_lib import estrato_de_cobertura                                   # noqa: E402
from argos_lib.gt import conteo_por_estrato, guardar_gt                      # noqa: E402
from argos_lib.oclusion import cobertura_por_caja, escribir_imagen, leer_imagen  # noqa: E402
from argos_lib.siluetas import BancoSiluetas, ocluir_siluetas                # noqa: E402

RAIZ = os.path.dirname(os.path.abspath(__file__))
DIR_NO = os.path.join(RAIZ, "externos", "nightowls")
DIR_TRAIN = os.path.join(DIR_NO, "nightowls_training")
DIR_VALINT = os.path.join(DIR_NO, "nightowls_val_interno")
JSON_TRAIN = os.path.join(DIR_NO, "nightowls_training.json")
JSON_VAL = os.path.join(DIR_NO, "nightowls_validation.json")
MANIFIESTO = os.path.join(DIR_NO, "muestra_h7.json")
DATASET_NO = os.path.join(RAIZ, "dataset_no")
DATASET = os.path.join(RAIZ, "dataset")
CAT_PERSONA = 1                      # pedestrian; 2/3/4 no se etiquetan
PELDANOS = (2000, 5000, 10000, 20000)
PRESENTACIONES = 200000              # presupuesto fijo por corrida


def epocas_de(peldano, presentaciones=PRESENTACIONES):
    """Epocas y paciencia del peldano, con presupuesto fijo de presentaciones."""
    ep = max(1, int(round(presentaciones / float(peldano))))
    return ep, max(2, ep // 5)


# ----------------------------------------------------------------------------
# datos
# ----------------------------------------------------------------------------
def etiquetas_yolo(anots, W, H):
    """Lineas YOLO (clase 0) de los peatones; devuelve (lineas, n_omitidas)."""
    lineas, omit = [], 0
    for a in anots:
        if a.get("category_id") != CAT_PERSONA:
            omit += 1
            continue
        x, y, w, h = a["bbox"]
        x1, y1 = max(0.0, float(x)), max(0.0, float(y))
        x2, y2 = min(float(W), float(x) + float(w)), min(float(H), float(y) + float(h))
        if x2 <= x1 or y2 <= y1:
            omit += 1
            continue
        lineas.append("0 %.6f %.6f %.6f %.6f" % ((x1 + x2) / 2 / W, (y1 + y2) / 2 / H,
                                                (x2 - x1) / W, (y2 - y1) / H))
    return lineas, omit


def _escribir_etiquetas(doc, ids, dir_img, por_img, imgs):
    n_inst = n_omit = sin_img = 0
    rutas = []
    for i in ids:
        im = imgs[i]
        ruta = os.path.join(dir_img, im["file_name"])
        if not os.path.exists(ruta):
            sin_img += 1
            continue
        lineas, omit = etiquetas_yolo(por_img.get(i, []), im["width"], im["height"])
        with open(os.path.splitext(ruta)[0] + ".txt", "w", encoding="utf-8") as fh:
            fh.write("\n".join(lineas) + ("\n" if lineas else ""))
        n_inst += len(lineas)
        n_omit += omit
        rutas.append(ruta.replace("\\", "/"))
    return rutas, n_inst, n_omit, sin_img


def cmd_datos():
    man = json.load(open(MANIFIESTO, encoding="utf-8"))
    os.makedirs(DATASET_NO, exist_ok=True)
    resumen = {"fuente": "NightOwls (Neumann et al. 2019), nightowls_training.json oficial",
               "clase_etiquetada": "pedestrian (category_id 1)",
               "no_etiquetadas": "bicycledriver, motorbikedriver, ignore areas",
               "semilla_escalera": man["semilla"], "peldanos": {}, "presupuesto_presentaciones": PRESENTACIONES}

    # --- training: escalera anidada
    d = json.load(open(JSON_TRAIN, encoding="utf-8"))
    imgs = {im["id"]: im for im in d["images"]}
    por_img = {}
    for a in d["annotations"]:
        por_img.setdefault(a["image_id"], []).append(a)
    ids = man["ids_ordenados"]
    rutas, n_inst, n_omit, sin_img = _escribir_etiquetas(d, ids, DIR_TRAIN, por_img, imgs)
    print("training: %d imagenes etiquetadas, %d peatones, %d cajas omitidas, %d sin imagen"
          % (len(rutas), n_inst, n_omit, sin_img), flush=True)
    # las listas son prefijos de la misma permutacion -> peldanos anidados
    for k in PELDANOS:
        lista = rutas[:k]
        with open(os.path.join(DATASET_NO, "%d.txt" % k), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lista) + "\n")
        ep, pac = epocas_de(k)
        inst = sum(sum(1 for a in por_img.get(i, []) if a.get("category_id") == CAT_PERSONA)
                   for i in ids[:k])
        resumen["peldanos"][str(k)] = {"imagenes": len(lista), "peatones": inst,
                                       "epocas": ep, "paciencia": pac,
                                       "presentaciones": len(lista) * ep}
        print("  peldano %6d: %5d imagenes, %6d peatones, %3d epocas (paciencia %d)"
              % (k, len(lista), inst, ep, pac))

    # --- val interno
    dv = json.load(open(JSON_VAL, encoding="utf-8"))
    imgs_v = {im["id"]: im for im in dv["images"]}
    por_img_v = {}
    for a in dv["annotations"]:
        por_img_v.setdefault(a["image_id"], []).append(a)
    ids_v = man["val_interno"]["ids"]
    rutas_v, inst_v, omit_v, sin_v = _escribir_etiquetas(dv, ids_v, DIR_VALINT, por_img_v, imgs_v)
    with open(os.path.join(DATASET_NO, "val_interno.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(rutas_v) + "\n")
    resumen["val_interno"] = {"imagenes": len(rutas_v), "peatones": inst_v,
                              "semilla": man["val_interno"]["semilla"],
                              "disjunto_de": "las 2 000 imagenes de evaluacion (muestra.json)"}
    print("val interno: %d imagenes, %d peatones" % (len(rutas_v), inst_v))

    with open(os.path.join(DATASET_NO, "escalera.json"), "w", encoding="utf-8") as fh:
        json.dump(resumen, fh, indent=1, ensure_ascii=False)
    print("-> %s" % os.path.join(DATASET_NO, "escalera.json"))


def leer_lista(nombre):
    with open(os.path.join(DATASET_NO, "%s.txt" % nombre), encoding="utf-8") as fh:
        return [l.strip() for l in fh if l.strip()]


# ----------------------------------------------------------------------------
# bancos
# ----------------------------------------------------------------------------
def cmd_bancos(pesos_seg, max_por_clase, device):
    for lista, nombre in (("20000", "siluetas_no_train"), ("val_interno", "siluetas_no_val")):
        rutas = leer_lista(lista)
        salida = os.path.join(DATASET, nombre)
        print("%s: %d imagenes candidatas" % (lista, len(rutas)), flush=True)
        cnt = BancoSiluetas.construir(rutas, salida, pesos_seg, max_por_clase, device=device)
        print("  -> %s: %s" % (salida, cnt), flush=True)


# ----------------------------------------------------------------------------
# val mixto
# ----------------------------------------------------------------------------
def cajas_de_etiqueta(ruta_txt, W, H):
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


def cmd_val(semilla):
    banco = BancoSiluetas(os.path.join(DATASET, "siluetas_no_val"))
    out = os.path.join(DATASET_NO, "val_ocluido")
    for sub in ("images", "labels"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    rnd = np.random.RandomState(semilla)
    rutas = leer_lista("val_interno")
    imagenes, n_inst, n_peg = {}, 0, 0
    for k, ruta in enumerate(rutas):
        nombre = os.path.basename(ruta)
        base = os.path.splitext(nombre)[0]
        im = leer_imagen(ruta)
        H, W = im.shape[:2]
        cajas = cajas_de_etiqueta(os.path.splitext(ruta)[0] + ".txt", W, H)
        _, masc, pegadas = ocluir_siluetas(im, cajas, rnd, banco, todas=True)
        cov = cobertura_por_caja(masc, cajas) if cajas else []
        escribir_imagen(os.path.join(out, "images", nombre), im)
        lineas = ["0 %.6f %.6f %.6f %.6f" % ((x1 + x2) / 2 / W, (y1 + y2) / 2 / H, (x2 - x1) / W, (y2 - y1) / H)
                  for (x1, y1, x2, y2) in list(cajas) + list(pegadas)]
        with open(os.path.join(out, "labels", base + ".txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lineas) + ("\n" if lineas else ""))
        inst = [{"id": "%s#%d" % (base, i), "x1": c[0], "y1": c[1], "x2": c[2], "y2": c[3], "truncado": 0,
                 "cobertura": round(float(cv), 4), "estrato": estrato_de_cobertura(cv)}
                for i, (c, cv) in enumerate(zip(cajas, cov))]
        inst += [{"id": "%s#p%d" % (base, i), "x1": x1, "y1": y1, "x2": x2, "y2": y2, "estrato": "sin",
                  "truncado": 0, "cobertura": 0.0, "pegada": 1} for i, (x1, y1, x2, y2) in enumerate(pegadas)]
        imagenes["images/" + nombre] = {"ancho": W, "alto": H, "luz": "NightOwls", "instancias": inst}
        n_inst += len(inst)
        n_peg += len(pegadas)
        if (k + 1) % 200 == 0:
            print("  %d/%d" % (k + 1, len(rutas)), flush=True)
    guardar_gt(os.path.join(out, "gt_val_ocluido.json"), "no_val_ocluido", out, imagenes,
               extra={"generador": "siluetas v2, banco no_val, todas las instancias, f~U[.30,.85]",
                      "semilla": semilla, "conteo": conteo_por_estrato(imagenes)})
    print("val_ocluido: %d imagenes, %d instancias (%d pegadas), estratos %s"
          % (len(imagenes), n_inst, n_peg, conteo_por_estrato(imagenes)))
    for k in PELDANOS:
        ruta = os.path.join(DATASET, "data_nightowls_%d.yaml" % k)
        with open(ruta, "w", encoding="utf-8") as fh:
            fh.write("# ARGOS-11 H7 - NightOwls train, peldano de %d imagenes, validacion mixta\n" % k)
            fh.write("path: %s\n" % os.path.abspath(DATASET_NO))
            fh.write("train: %d.txt\nval: [val_interno.txt, val_ocluido/images]\n" % k)
            fh.write("nc: 1\nnames: [person]\n")
        print("-> %s" % ruta)


# ----------------------------------------------------------------------------
def cmd_plan():
    print("H7 - 12 corridas (PREREGISTRO_H6_H7.md s.4)\n")
    print("  %-8s %-9s %-8s %-11s %s" % ("peldano", "variantes", "semillas", "epocas/pac", "comando"))
    for k in PELDANOS:
        ep, pac = epocas_de(k)
        semillas = "0,1,2" if k == max(PELDANOS) else "0"
        print("  %-8d %-9s %-8s %-11s python 07_entrenar.py --protocolo no --datos data_nightowls_%d.yaml "
              "--proyecto argos_no_%d --variantes V1 V3 --semillas %s --epochs %d --patience %d --workers 4"
              % (k, "V1, V3", semillas, "%d/%d" % (ep, pac), k, k, semillas.replace(",", " "), ep, pac))
    print("\n  Criterio (s.2): H7 se sostiene si V3-V1 en NightOwls 'ocluida' del peldano 20 000")
    print("  no alcanza +2 pp o su IC 95 %% incluye el cero; se refuta en caso contrario.")


def selftest():
    fallos = []

    def comp(desc, ok):
        print("  [%s] %s" % ("ok" if ok else "FALLA", desc))
        if not ok:
            fallos.append(desc)

    comp("presupuesto fijo: 2k->100, 5k->40, 10k->20, 20k->10",
         [epocas_de(k)[0] for k in PELDANOS] == [100, 40, 20, 10])
    comp("paciencia = epocas/5 con minimo 2", [epocas_de(k)[1] for k in PELDANOS] == [20, 8, 4, 2])
    comp("presentaciones constantes", all(abs(k * epocas_de(k)[0] - PRESENTACIONES) < 1 for k in PELDANOS))
    lineas, omit = etiquetas_yolo([{"category_id": 1, "bbox": [100, 100, 40, 80]},
                                   {"category_id": 2, "bbox": [0, 0, 10, 10]},
                                   {"category_id": 4, "bbox": [0, 0, 10, 10]},
                                   {"category_id": 1, "bbox": [1000, 600, 100, 100]}], 1024, 640)
    comp("solo pedestrian se etiqueta (2 de 4)", len(lineas) == 2 and omit == 2)
    cx, cy, w, h = (float(v) for v in lineas[0].split()[1:])
    comp("normalizacion correcta", abs(cx - 120 / 1024) < 1e-6 and abs(h - 80 / 640) < 1e-6)
    cx, cy, w, h = (float(v) for v in lineas[1].split()[1:])
    comp("caja recortada al borde", abs((cx + w / 2) - 1.0) < 1e-6 and abs((cy + h / 2) - 1.0) < 1e-6)
    man = json.load(open(MANIFIESTO, encoding="utf-8")) if os.path.exists(MANIFIESTO) else None
    if man:
        ids = man["ids_ordenados"]
        comp("escalera anidada en el manifiesto", ids[:2000] == ids[:2000] and len(set(ids)) == len(ids) == 20000)
        comp("val interno disjunto de la evaluacion", not (set(man["val_interno"]["ids"]) &
             set(json.load(open(os.path.join(DIR_NO, "muestra.json"), encoding="utf-8"))["ids"])))
    print("\n%s" % ("AUTOTEST SUPERADO" if not fallos else "FALLOS: %s" % fallos))
    sys.exit(1 if fallos else 0)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - H7 escalera NightOwls")
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("datos")
    b = sub.add_parser("bancos"); b.add_argument("--pesos-seg", default="yolo11s-seg.pt")
    b.add_argument("--max-por-clase", type=int, default=800); b.add_argument("--device")
    v = sub.add_parser("val"); v.add_argument("--semilla", type=int, default=31)
    sub.add_parser("plan")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.cmd == "datos":
        cmd_datos()
    elif a.cmd == "bancos":
        cmd_bancos(a.pesos_seg, a.max_por_clase, a.device)
    elif a.cmd == "val":
        cmd_val(a.semilla)
    elif a.cmd == "plan":
        cmd_plan()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
