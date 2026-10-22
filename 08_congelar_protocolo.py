#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Paso 5: congelamiento verificable del protocolo (Seccion 2.9).

Calcula el SHA-256 de PROTOCOLO.md, de los YAML de configuracion, de las
listas de split, de los pesos iniciales y de los scripts, y lo publica en
protocolo_congelado.json con fecha. `--verificar` recalcula y lista las
diferencias: cualquier cambio posterior al congelamiento debe quedar
registrado en CAMBIOS_PROTOCOLO.md con fecha y justificacion.

Uso:
    python 08_congelar_protocolo.py                # congela (se niega si ya existe)
    python 08_congelar_protocolo.py --verificar    # compara con lo congelado
    python 08_congelar_protocolo.py --forzar       # re-congela (registra el cambio)
    python 08_congelar_protocolo.py --selftest
"""

import argparse
import glob
import hashlib
import json
import os
import sys
import time

RAIZ = os.path.dirname(os.path.abspath(__file__))
PATRONES = [
    "PROTOCOLO.md", "GUIA_DE_ANOTACION.md",
    "config/hiperparametros.yaml", "config/aumento_base.yaml",
    "config/aumento_base_intenso.yaml",
    "dataset/data.yaml", "dataset/splits/*.txt",
    "modelos/yolo11s-cbam.yaml", "weights/yolo11s_cbam_coco.pt", "yolo11s.pt",
    "dataset/banco_train.json", "dataset/banco_test.json",
    "dataset/test_sintetico/resumen_generacion.json",
    # v2.0 (iteracion 2): existen solo tras 15_iteracion2.py
    "PROTOCOLO_v2.md", "dataset/data_v2.yaml", "dataset/siluetas_*/indice.json",
    "dataset/val_ocluido/gt_val_ocluido.json", "dataset/test_sintetico/silueta_*/gt_*.json",
    "yolo11s-seg.pt", "yolo26s.pt",
    # v3.0 (H6, replica CityPersons): existen solo tras 20_replica_citypersons.py
    "PREREGISTRO_H6_H7.md", "dataset/data_citypersons.yaml", "dataset_cp/particion.json",
    "dataset_cp/train.txt", "dataset_cp/val_interno.txt", "dataset_cp/val_ocluido/gt_val_ocluido.json",
    "dataset/siluetas_cp_*/indice.json", "dataset/test_sintetico/cp_silueta_*/gt_*.json",
    "externos/citypersons/anno_train.mat", "externos/citypersons/anno_val.mat",
    # v3.1 (H7, escalera NightOwls): existen solo tras 21_escalera_nightowls.py
    "dataset/data_nightowls_*.yaml", "dataset_no/escalera.json",
    "dataset_no/2000.txt", "dataset_no/5000.txt", "dataset_no/10000.txt", "dataset_no/20000.txt",
    "dataset_no/val_interno.txt", "dataset_no/val_ocluido/gt_val_ocluido.json",
    "dataset/siluetas_no_*/indice.json", "externos/nightowls/muestra_h7.json",
    # v3.2 (H8, replica con RT-DETR-l)
    "PREREGISTRO_H8.md", "config/hiperparametros_rtdetr.yaml", "rtdetr-l.pt",
    # v3.3 (H9, oclusion generativa): existen solo tras 25_oclusion_generativa.py
    "PREREGISTRO_H9.md", "dataset/generativa_train/indice.json",
    "dataset/test_sintetico/generativa_*/gt_*.json", "modelos/sd15_inpaint/model_index.json",
    "modelos/sd15_inpaint/*/diffusion_pytorch_model.fp16.safetensors",
    "modelos/sd15_inpaint/text_encoder/model.fp16.safetensors",
    # v3.4 (H9b, generativa con 30 epocas fijas): solo el pre-registro; datos y codigo ya cubiertos
    "PREREGISTRO_H9b.md",
    # v3.5 (H10, geometria de la oclusion real): patrones de CityPersons train y control geometria_severa
    "PREREGISTRO_H10.md", "dataset/geometria/patrones_*.json", "dataset/test_sintetico/geometria_*/gt_*.json",
    # v3.6 (H11, confirmacion en el dominio CityPersons con semillas 3-5)
    "PREREGISTRO_H11.md",
    # v3.7 (H12: YOLOv11m, y extension de semillas de E7b/E8)
    "PREREGISTRO_H12.md", "yolo11m.pt",
    # v3.8 (H13: realismo medido)
    "PREREGISTRO_H13.md",
    # v3.9 (H14: E11, orden de profundidad; referencia con modelos de fundacion)
    "PREREGISTRO_H14.md", "dataset/profundidad_train/indice.json", "dataset/test_sintetico/profundidad_*/gt_*.json",
    # v3.10 (H15: E12, Faster R-CNN de torchvision, pesos COCO oficiales)
    "PREREGISTRO_H15.md", "fasterrcnn_resnet50_fpn_v2_coco.pth",
    # v3.11 (H16 y H17: E13, Faster R-CNN con las familias generativa y de profundidad; RetinaNet con siluetas)
    "PREREGISTRO_H16_H17.md", "retinanet_resnet50_fpn_v2_coco.pth",
    "argos_lib/*.py", "0?_*.py", "1?_*.py", "2?_*.py", "3?_*.py",
]
SALIDA = "protocolo_congelado.json"
REGISTRO = "CAMBIOS_PROTOCOLO.md"


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def ficheros(raiz, patrones=PATRONES):
    out = []
    for p in patrones:
        out += sorted(glob.glob(os.path.join(raiz, p)))
    return [os.path.relpath(f, raiz).replace("\\", "/") for f in out
            if os.path.isfile(f)]


def calcular(raiz, patrones=PATRONES):
    return {f: sha256(os.path.join(raiz, f)) for f in ficheros(raiz, patrones)}


def hash_global(hashes):
    h = hashlib.sha256()
    for k in sorted(hashes):
        h.update(("%s %s\n" % (k, hashes[k])).encode("utf-8"))
    return h.hexdigest()


def congelar(raiz, forzar=False, patrones=PATRONES, verbose=True):
    ruta = os.path.join(raiz, SALIDA)
    if os.path.exists(ruta) and not forzar:
        sys.exit("Ya existe %s. Usar --verificar, o --forzar para re-congelar "
                 "(y registrar el motivo en %s)." % (SALIDA, REGISTRO))
    hashes = calcular(raiz, patrones)
    faltan = [p for p in patrones if "*" not in p and "?" not in p
              and not os.path.exists(os.path.join(raiz, p))]
    doc = {"fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
           "hash_global": hash_global(hashes), "n_ficheros": len(hashes),
           "ficheros": hashes, "faltantes_en_el_congelamiento": faltan}
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
    reg = os.path.join(raiz, REGISTRO)
    nuevo = not os.path.exists(reg)
    with open(reg, "a", encoding="utf-8") as fh:
        if nuevo:
            fh.write("# ARGOS-11 - Registro de cambios del protocolo\n\n"
                     "Cada entrada: fecha, hash global, motivo. El congelamiento "
                     "inicial es la primera entrada.\n\n")
        fh.write("- %s  hash_global=%s  (%d ficheros)%s\n"
                 % (doc["fecha"], doc["hash_global"][:16], len(hashes),
                    "  RE-CONGELADO: anotar motivo aqui." if forzar and not nuevo else
                    "  Congelamiento inicial."))
    if verbose:
        print("Protocolo congelado: %s" % ruta)
        print("  fecha        : %s" % doc["fecha"])
        print("  ficheros     : %d" % len(hashes))
        print("  hash global  : %s" % doc["hash_global"])
        if faltan:
            print("  AVISO, faltan: %s" % ", ".join(faltan))
        print("  Publicar el hash global junto con el repositorio.")
    return doc


def verificar(raiz, patrones=PATRONES, verbose=True):
    ruta = os.path.join(raiz, SALIDA)
    if not os.path.exists(ruta):
        sys.exit("No existe %s: el protocolo no esta congelado." % SALIDA)
    with open(ruta, encoding="utf-8") as fh:
        cong = json.load(fh)
    actual = calcular(raiz, patrones)
    modificados = [f for f in cong["ficheros"] if f in actual and actual[f] != cong["ficheros"][f]]
    borrados = [f for f in cong["ficheros"] if f not in actual]
    nuevos = [f for f in actual if f not in cong["ficheros"]]
    ok = not (modificados or borrados or nuevos)
    if verbose:
        print("Congelado el %s (hash %s...)" % (cong["fecha"], cong["hash_global"][:16]))
        print("  modificados : %d" % len(modificados))
        for f in modificados:
            print("      %s" % f)
        print("  borrados    : %d %s" % (len(borrados), borrados or ""))
        print("  nuevos      : %d %s" % (len(nuevos), nuevos or ""))
        print("\n  %s" % ("PROTOCOLO INTACTO." if ok else
                          "HAY CAMBIOS: registrarlos en %s con fecha y motivo." % REGISTRO))
    return ok, modificados, borrados, nuevos


def selftest():
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="congelar_test_")
    os.makedirs(os.path.join(tmp, "config"))
    open(os.path.join(tmp, "PROTOCOLO.md"), "wb").write(b"v1\n")
    open(os.path.join(tmp, "config", "a.yaml"), "w").write("x: 1\n")
    pat = ["PROTOCOLO.md", "config/*.yaml"]
    fallos = []

    def comp(desc, obt, esp):
        ok = obt == esp
        print("  [%s] %-46s %s" % ("ok" if ok else "FALLA", desc, obt))
        if not ok:
            fallos.append(desc)

    doc = congelar(tmp, patrones=pat, verbose=False)
    comp("dos ficheros congelados", doc["n_ficheros"], 2)
    comp("sha256 conocido de 'v1\\n'", doc["ficheros"]["PROTOCOLO.md"],
         hashlib.sha256(b"v1\n").hexdigest())
    ok, m, b, n = verificar(tmp, pat, verbose=False)
    comp("verificacion intacta", ok, True)
    open(os.path.join(tmp, "config", "a.yaml"), "w").write("x: 2\n")
    open(os.path.join(tmp, "config", "b.yaml"), "w").write("y: 1\n")
    ok, m, b, n = verificar(tmp, pat, verbose=False)
    comp("detecta modificado", m, ["config/a.yaml"])
    comp("detecta nuevo", n, ["config/b.yaml"])
    comp("registro de cambios creado", os.path.exists(os.path.join(tmp, REGISTRO)), True)
    try:
        congelar(tmp, patrones=pat, verbose=False)
        comp("se niega a re-congelar sin --forzar", False, True)
    except SystemExit:
        comp("se niega a re-congelar sin --forzar", True, True)
    shutil.rmtree(tmp)
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO: 7/7 comprobaciones.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - congelar protocolo")
    ap.add_argument("--verificar", action="store_true")
    ap.add_argument("--forzar", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if args.verificar:
        ok, *_ = verificar(RAIZ)
        sys.exit(0 if ok else 1)
    congelar(RAIZ, forzar=args.forzar)


if __name__ == "__main__":
    main()
