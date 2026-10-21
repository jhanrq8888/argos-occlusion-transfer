#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Paso 3: oclusion sintetica (Seccion 2.3.3 y Fuente 2a).

Tres subcomandos:

  bancos     Construye los dos bancos de recortes (objetos no-persona de
             imagenes sin personas): banco_train.json (para el aumento de
             entrenamiento) y banco_test.json (para el generador de prueba).
             Son disjuntos por construccion: proceden de splits distintos y
             ninguna de esas imagenes pertenece a ExDark-People.

  prueba     Genera los subconjuntos de prueba con oclusion controlada por
             estrato (ligera/moderada/severa) y por tipo de parche
             (textura/recorte/opaco) en dataset/test_sintetico/<tipo>_<estrato>/
             junto con su gt_*.json (cobertura efectiva medida por instancia).

  demo       Aplica el aumento de ENTRENAMIENTO sobre N imagenes de train y
             guarda ejemplos en dataset/demo_oclusion/ para inspeccion visual.

Uso:
    python 05_oclusion_sintetica.py bancos --raiz . --dataset ./dataset
    python 05_oclusion_sintetica.py prueba --dataset ./dataset --semilla 2024
    python 05_oclusion_sintetica.py demo --dataset ./dataset --n 12
    python 05_oclusion_sintetica.py --selftest
"""

import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argos_lib import ESTRATOS, estrato_de_cobertura                  # noqa: E402
from argos_lib.gt import (cargar_split_yolo, conteo_por_estrato,       # noqa: E402
                          guardar_gt, leer_luz_por_imagen)
from argos_lib.oclusion import (TIPOS, RANGO_F_PRUEBA, BancoRecortes,  # noqa: E402
                                cobertura_por_caja, escribir_imagen,
                                leer_imagen, ocluir_entrenamiento,
                                ocluir_prueba)


def cmd_bancos(raiz, dataset, max_recortes, semilla):
    os.makedirs(dataset, exist_ok=True)
    for split in ("train", "test"):
        ruta = os.path.join(dataset, "banco_%s.json" % split)
        n, cand = BancoRecortes.construir(raiz, split, ruta, max_recortes,
                                          semilla=semilla)
        print("  banco_%s.json: %d recortes (de %d candidatos)" % (split, n, cand))
    a = {r["imagen"] for r in json.load(open(os.path.join(dataset, "banco_train.json")))["recortes"]}
    b = {r["imagen"] for r in json.load(open(os.path.join(dataset, "banco_test.json")))["recortes"]}
    print("  imagenes en comun entre bancos: %d (debe ser 0)" % len(a & b))
    if a & b:
        sys.exit("ERROR: los bancos comparten imagenes.")


def cmd_prueba(dataset, raiz, semilla, tipos, estratos, calidad):
    banco = BancoRecortes(os.path.join(dataset, "banco_test.json"))
    luz = leer_luz_por_imagen(os.path.join(raiz, "imageclasslist.txt"))
    base = cargar_split_yolo(dataset, "test", luz)
    print("Imagenes de prueba: %d  (banco de prueba: %d recortes)"
          % (len(base), len(banco)))
    raiz_out = os.path.join(dataset, "test_sintetico")
    resumen = {}
    for tipo in tipos:
        for estrato in estratos:
            nombre = "%s_%s" % (tipo, estrato)
            dir_out = os.path.join(raiz_out, nombre)
            os.makedirs(os.path.join(dir_out, "test"), exist_ok=True)
            # Semilla distinta por conjunto pero determinista.
            rnd = np.random.RandomState(semilla + 1000 * TIPOS.index(tipo)
                                        + ESTRATOS.index(estrato))
            imagenes, nominales_tot = {}, []
            for i, (rel, meta) in enumerate(sorted(base.items())):
                im = leer_imagen(os.path.join(dataset, "images", rel))
                cajas = [(o["x1"], o["y1"], o["x2"], o["y2"]) for o in meta["instancias"]]
                nom, efec = ocluir_prueba(im, cajas, rnd, estrato, tipo, banco)
                escribir_imagen(os.path.join(dir_out, rel), im, calidad)
                inst = []
                for o, f_n, f_e in zip(meta["instancias"], nom, efec):
                    q = dict(o)
                    q["cobertura_nominal"] = round(f_n, 4)
                    q["cobertura"] = round(f_e, 4)
                    q["estrato_nominal"] = estrato
                    q["estrato"] = estrato_de_cobertura(f_e)
                    inst.append(q)
                nominales_tot.extend(nom)
                imagenes[rel] = {"ancho": meta["ancho"], "alto": meta["alto"],
                                 "luz": meta["luz"], "instancias": inst}
                if (i + 1) % 200 == 0:
                    print("  %s: %d/%d" % (nombre, i + 1, len(base)))
            cnt = conteo_por_estrato(imagenes)
            guardar_gt(os.path.join(dir_out, "gt_%s.json" % nombre), nombre,
                       dir_out, imagenes,
                       extra={"generador": "prueba (banda de borde, banco test)",
                              "tipo_parche": tipo, "estrato_nominal": estrato,
                              "rango_f": RANGO_F_PRUEBA[estrato], "semilla": semilla,
                              "conteo_estrato_efectivo": cnt})
            resumen[nombre] = cnt
            print("  %-18s estratos efectivos: %s" % (nombre, cnt))
    with open(os.path.join(raiz_out, "resumen_generacion.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"semilla": semilla, "conjuntos": resumen}, fh, indent=2)
    print("\nGenerado en %s" % raiz_out)
    print("Nota: el estrato EFECTIVO puede diferir del nominal cuando dos")
    print("personas se solapan (el parche de una cubre parte de la otra); la")
    print("evaluacion usa el efectivo, con el protocolo de regiones ignore.")


def cmd_demo(dataset, n, semilla):
    from argos_lib.oclusion import OclusionEntrenamiento
    ruta_banco = os.path.join(dataset, "banco_train.json")
    if not os.path.exists(ruta_banco):
        sys.exit("ERROR: falta banco_train.json; ejecutar antes 'bancos'.")
    base = cargar_split_yolo(dataset, "train")
    rnd = np.random.RandomState(semilla)
    nombres = sorted(base)
    rnd.shuffle(nombres)
    dir_out = os.path.join(dataset, "demo_oclusion")
    os.makedirs(dir_out, exist_ok=True)
    banco = BancoRecortes(ruta_banco)
    import cv2
    hechos = 0
    for rel in nombres:
        if hechos >= n:
            break
        meta = base[rel]
        im = leer_imagen(os.path.join(dataset, "images", rel))
        cajas = [(o["x1"], o["y1"], o["x2"], o["y2"]) for o in meta["instancias"]]
        aplicados, masc = ocluir_entrenamiento(im, cajas, rnd, banco, p=1.0)
        if not aplicados:
            continue
        cov = cobertura_por_caja(masc, cajas)
        for (i, tipo, f), c in zip(aplicados, [cov[a[0]] for a in aplicados]):
            x1, y1, x2, y2 = (int(v) for v in cajas[i])
            cv2.rectangle(im, (x1, y1), (x2, y2), (0, 255, 0), 1)
            cv2.putText(im, "%s f=%.2f ef=%.2f" % (tipo, f, c), (x1, max(12, y1 - 3)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
        escribir_imagen(os.path.join(dir_out, os.path.basename(rel)), im)
        hechos += 1
    print("Guardados %d ejemplos en %s" % (hechos, dir_out))


def selftest():
    import shutil
    import tempfile
    from argos_lib.oclusion import parche_banda_borde, parche_interior
    fallos = []

    def comp(desc, obt, esp):
        ok = obt == esp
        print("  [%s] %-50s %s" % ("ok" if ok else "FALLA", desc, obt))
        if not ok:
            fallos.append(desc)

    rnd = np.random.RandomState(0)
    caja = (10.0, 20.0, 110.0, 220.0)          # 100 x 200, area 20000
    A = 100 * 200
    # 1. Parche interior: area exacta y contenido en la caja.
    ok_area = ok_dentro = True
    for _ in range(500):
        f = rnd.uniform(0.3, 0.85)
        r = parche_interior(rnd, caja, f)
        area = (r[2] - r[0]) * (r[3] - r[1])
        ok_area &= abs(area / A - f) < 1e-9
        ok_dentro &= (r[0] >= caja[0] - 1e-9 and r[1] >= caja[1] - 1e-9
                      and r[2] <= caja[2] + 1e-9 and r[3] <= caja[3] + 1e-9)
    comp("parche interior: area = f * A (500 muestras)", ok_area, True)
    comp("parche interior: contenido en la caja", ok_dentro, True)
    # 2. Banda de borde: area exacta, tocando un borde.
    ok_area = ok_borde = True
    for _ in range(500):
        f = rnd.uniform(0.1, 1.0)
        r = parche_banda_borde(rnd, caja, f)
        area = (r[2] - r[0]) * (r[3] - r[1])
        ok_area &= abs(area / A - f) < 1e-9
        ok_borde &= any(abs(r[k] - caja[k]) < 1e-9 for k in range(4))
    comp("banda de borde: area = f * A", ok_area, True)
    comp("banda de borde: anclada a un borde", ok_borde, True)

    # 3. Cobertura efectiva medida sobre imagen real sintetica.
    im = np.zeros((300, 300, 3), dtype=np.uint8)
    cajas = [(10.0, 20.0, 110.0, 220.0)]
    nom, efec = ocluir_prueba(im, cajas, np.random.RandomState(1), "severa",
                              "opaco", None)
    comp("prueba severa: nominal en [0.70,1.0]", 0.70 <= nom[0] <= 1.0, True)
    comp("prueba severa: efectiva ~ nominal (+-3 pp)", abs(efec[0] - nom[0]) < 0.03, True)
    comp("prueba: estrato efectivo coherente",
         estrato_de_cobertura(efec[0]) in ("moderada", "severa"), True)

    # 4. Entrenamiento: p=0 no toca nada; p=1 toca entre 1 y 3 cajas.
    im0 = np.random.RandomState(2).randint(0, 255, (300, 300, 3)).astype(np.uint8)
    cajas4 = [(10, 10, 60, 110), (100, 10, 150, 110), (200, 10, 250, 110), (10, 150, 60, 250)]
    im1 = im0.copy()
    ap0, _ = ocluir_entrenamiento(im1, cajas4, np.random.RandomState(3), None, p=0.0)
    comp("entrenamiento p=0: sin parches", len(ap0), 0)
    comp("entrenamiento p=0: imagen intacta", bool(np.array_equal(im0, im1)), True)
    ap1, masc = ocluir_entrenamiento(im1, cajas4, np.random.RandomState(3), None, p=1.0)
    comp("entrenamiento p=1: 1..3 parches", 1 <= len(ap1) <= 3, True)
    cov = cobertura_por_caja(masc, cajas4)
    idx = [a[0] for a in ap1]
    comp("cajas elegidas cubiertas >= 25%", all(cov[i] >= 0.25 for i in idx), True)
    comp("cajas no elegidas intactas",
         all(cov[i] == 0.0 for i in range(4) if i not in idx), True)
    comp("tipos validos", all(a[1] in TIPOS for a in ap1), True)

    # 5. Transform de Ultralytics sobre un labels dict real.
    try:
        from ultralytics.utils.instance import Instances
        from argos_lib.oclusion import OclusionEntrenamiento
        bb = np.array([[0.1, 0.2, 0.2, 0.5]], dtype=np.float32)   # xywh norm.
        inst = Instances(bb, bbox_format="xywh", normalized=True)
        labels = {"img": im0.copy(), "instances": inst}
        np.random.seed(0)
        out = OclusionEntrenamiento(p=1.0)(labels)
        comp("transform: formato de cajas restaurado", out["instances"]._bboxes.format, "xywh")
        comp("transform: normalizacion restaurada", out["instances"].normalized, True)
        comp("transform: cajas sin modificar",
             bool(np.allclose(out["instances"].bboxes, bb, atol=1e-6)), True)
        comp("transform: imagen modificada", bool(np.array_equal(out["img"], im0)), False)
        import pickle
        t = OclusionEntrenamiento(ruta_banco="x.json", p=0.5)
        comp("transform picklable (workers)", pickle.loads(pickle.dumps(t)).p, 0.5)
    except ImportError:
        print("  [--] ultralytics no disponible: se omite la prueba del transform")

    # 6. Banco: construccion sobre un ExDark falso.
    tmp = tempfile.mkdtemp(prefix="banco_test_")
    from PIL import Image
    for clase in ("Car", "People"):
        os.makedirs(os.path.join(tmp, "ExDark", clase))
        os.makedirs(os.path.join(tmp, "ExDark_Annno", clase))
    Image.new("RGB", (200, 200), (90, 90, 90)).save(os.path.join(tmp, "ExDark", "Car", "c1.jpg"))
    Image.new("RGB", (200, 200)).save(os.path.join(tmp, "ExDark", "Car", "c2.jpg"))
    Image.new("RGB", (200, 200)).save(os.path.join(tmp, "ExDark", "People", "p1.jpg"))
    open(os.path.join(tmp, "ExDark_Annno", "Car", "c1.jpg.txt"), "w").write(
        "% bbGt version=3\nCar 10 10 80 60 0 0 0 0 0 0 0\nCar 100 100 50 50 0 0 0 0 0 0 0\n")
    open(os.path.join(tmp, "ExDark_Annno", "Car", "c2.jpg.txt"), "w").write(
        "% bbGt version=3\nCar 10 10 80 60 0 0 0 0 0 0 0\nPeople 100 100 50 50 0 0 0 0 0 0 0\n")
    open(os.path.join(tmp, "ExDark_Annno", "People", "p1.jpg.txt"), "w").write(
        "% bbGt version=3\nPeople 10 10 80 60 0 0 0 0 0 0 0\n")
    open(os.path.join(tmp, "imageclasslist.txt"), "w").write(
        "c1.jpg 5 1 1 1\nc2.jpg 5 1 1 1\np1.jpg 11 1 1 1\n")
    rj = os.path.join(tmp, "banco.json")
    n, cand = BancoRecortes.construir(tmp, "train", rj)
    comp("banco: solo objetos de imagenes sin personas", (n, cand), (2, 2))
    bco = BancoRecortes(rj)
    rec = bco.recorte(np.random.RandomState(0), 30, 40)
    comp("banco: recorte redimensionado", rec.shape, (40, 30, 3))
    shutil.rmtree(tmp)

    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - oclusion sintetica")
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    b = sub.add_parser("bancos")
    b.add_argument("--raiz", default=".")
    b.add_argument("--dataset", default="./dataset")
    b.add_argument("--max-recortes", type=int, default=600)
    b.add_argument("--semilla", type=int, default=0)
    p = sub.add_parser("prueba")
    p.add_argument("--dataset", default="./dataset")
    p.add_argument("--raiz", default=".")
    p.add_argument("--semilla", type=int, default=2024)
    p.add_argument("--tipos", default=",".join(TIPOS))
    p.add_argument("--estratos", default="ligera,moderada,severa")
    p.add_argument("--calidad", type=int, default=95)
    d = sub.add_parser("demo")
    d.add_argument("--dataset", default="./dataset")
    d.add_argument("--n", type=int, default=12)
    d.add_argument("--semilla", type=int, default=0)
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if args.cmd == "bancos":
        cmd_bancos(args.raiz, args.dataset, args.max_recortes, args.semilla)
    elif args.cmd == "prueba":
        cmd_prueba(args.dataset, args.raiz, args.semilla, args.tipos.split(","),
                   args.estratos.split(","), args.calidad)
    elif args.cmd == "demo":
        cmd_demo(args.dataset, args.n, args.semilla)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
