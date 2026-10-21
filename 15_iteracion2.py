#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Iteracion 2 del Componente 2 (protocolo v2.0): oclusores con
silueta real, validacion con oclusion y conjuntos de prueba de silueta.

Subcomandos:
  bancos   Segmenta (yolo11s-seg, COCO) las imagenes de cada split y guarda
           recortes RGBA de personas y objetos en dataset/siluetas_<split>/.
           Bancos disjuntos por construccion (train/val/test).
  val      Construye dataset/val_ocluido/ (copias del split val con TODAS
           las personas ocluidas por siluetas del banco val, f~U[.30,.85])
           y dataset/data_v2.yaml, cuyo val = val original + val_ocluido.
           Motivo: en v1 el val sin oclusion premiaba al modelo que menos se
           alejaba de COCO (mejor epoca = 2). El test sigue intacto.
  prueba   Conjuntos de prueba silueta_{ligera,moderada,severa} con el
           banco del split test (tercera familia sintetica, disjunta del
           entrenamiento por banco y por rango de f).
  demo     Ejemplos del aumento v2 sobre train en dataset/demo_siluetas/.

Uso:
    python 15_iteracion2.py bancos --pesos-seg yolo11s-seg.pt
    python 15_iteracion2.py val
    python 15_iteracion2.py prueba
    python 15_iteracion2.py demo --n 12
    python 15_iteracion2.py --selftest
"""

import argparse
import json
import os
import shutil
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argos_lib import ESTRATOS, estrato_de_cobertura                         # noqa: E402
from argos_lib.gt import cargar_split_yolo, conteo_por_estrato, guardar_gt, leer_luz_por_imagen  # noqa: E402
from argos_lib.oclusion import RANGO_F_PRUEBA, cobertura_por_caja, escribir_imagen, leer_imagen  # noqa: E402
from argos_lib.siluetas import BancoSiluetas, ocluir_siluetas               # noqa: E402

RAIZ = os.path.dirname(os.path.abspath(__file__))


def imagenes_split(dataset, raiz, split):
    """Imagenes de ExDark-People del split + imagenes SIN personas del mismo
    split (las del banco v1), para que haya objetos suficientes."""
    rutas = [os.path.join(dataset, "images", split, f) for f in os.listdir(os.path.join(dataset, "images", split))]
    bj = os.path.join(dataset, "banco_%s.json" % split)
    if os.path.exists(bj):
        d = json.load(open(bj, encoding="utf-8"))
        vistas = set()
        for r in d["recortes"]:
            if r["imagen"] not in vistas:
                vistas.add(r["imagen"])
                rutas.append(os.path.join(d["raiz"], "ExDark", r["imagen"]))
    return rutas


def cmd_bancos(dataset, raiz, pesos_seg, max_por_clase, device):
    for split in ("train", "val", "test"):
        salida = os.path.join(dataset, "siluetas_%s" % split)
        rutas = imagenes_split(dataset, raiz, split)
        print("%s: %d imagenes candidatas" % (split, len(rutas)), flush=True)
        cnt = BancoSiluetas.construir(rutas, salida, pesos_seg, max_por_clase, device=device)
        print("  -> %s: %s" % (salida, cnt), flush=True)


def cmd_val(dataset, raiz, semilla):
    banco = BancoSiluetas(os.path.join(dataset, "siluetas_val"))
    luz = leer_luz_por_imagen(os.path.join(raiz, "imageclasslist.txt"))
    base = cargar_split_yolo(dataset, "val", luz)
    out = os.path.join(dataset, "val_ocluido")
    for sub in ("images", "labels"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    rnd = np.random.RandomState(semilla)
    imagenes, n_inst, n_peg = {}, 0, 0
    for k, (rel, meta) in enumerate(sorted(base.items())):
        nombre = os.path.basename(rel)
        im = leer_imagen(os.path.join(dataset, "images", rel))
        cajas = [(o["x1"], o["y1"], o["x2"], o["y2"]) for o in meta["instancias"]]
        _, masc, pegadas = ocluir_siluetas(im, cajas, rnd, banco, todas=True)
        cov = cobertura_por_caja(masc, cajas)
        escribir_imagen(os.path.join(out, "images", nombre), im)
        # Etiquetas: las originales + las personas pegadas (personas reales
        # visibles; sin etiqueta el modelo aprenderia a ignorarlas).
        W, H = meta["ancho"], meta["alto"]
        with open(os.path.join(dataset, "labels", "val", os.path.splitext(nombre)[0] + ".txt"), encoding="utf-8") as fh:
            lineas = [l.strip() for l in fh if l.strip()]
        for (x1, y1, x2, y2) in pegadas:
            lineas.append("0 %.6f %.6f %.6f %.6f" % ((x1 + x2) / 2 / W, (y1 + y2) / 2 / H, (x2 - x1) / W, (y2 - y1) / H))
        with open(os.path.join(out, "labels", os.path.splitext(nombre)[0] + ".txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lineas) + "\n")
        inst = [{**o, "cobertura": round(c, 4), "estrato": estrato_de_cobertura(c)} for o, c in zip(meta["instancias"], cov)]
        inst += [{"id": "%s#p%d" % (os.path.splitext(nombre)[0], k), "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                  "estrato": "sin", "truncado": 0, "cobertura": 0.0, "pegada": 1} for k, (x1, y1, x2, y2) in enumerate(pegadas)]
        imagenes["images/" + nombre] = {**meta, "instancias": inst}
        n_inst += len(inst)
        n_peg += len(pegadas)
        if (k + 1) % 200 == 0:
            print("  %d/%d" % (k + 1, len(base)), flush=True)
    guardar_gt(os.path.join(out, "gt_val_ocluido.json"), "val_ocluido", out, imagenes,
               extra={"generador": "siluetas v2, banco val, todas las instancias, f~U[.30,.85]", "semilla": semilla,
                      "conteo": conteo_por_estrato(imagenes)})
    with open(os.path.join(dataset, "data_v2.yaml"), "w", encoding="utf-8") as fh:
        fh.write("# ARGOS-11 v2.0 - ExDark-People con validacion mixta (val + val_ocluido)\n")
        fh.write("path: %s\n" % os.path.abspath(dataset))
        fh.write("train: images/train\nval: [images/val, val_ocluido/images]\ntest: images/test\n")
        fh.write("nc: 1\nnames: [person]\n")
    print("val_ocluido: %d imagenes, %d instancias (%d personas pegadas etiquetadas), estratos %s"
          % (len(imagenes), n_inst, n_peg, conteo_por_estrato(imagenes)))
    print("-> %s" % os.path.join(dataset, "data_v2.yaml"))


def cmd_prueba(dataset, raiz, semilla):
    banco = BancoSiluetas(os.path.join(dataset, "siluetas_test"))
    luz = leer_luz_por_imagen(os.path.join(raiz, "imageclasslist.txt"))
    base = cargar_split_yolo(dataset, "test", luz)
    raiz_out = os.path.join(dataset, "test_sintetico")
    for estrato in ("ligera", "moderada", "severa"):
        nombre = "silueta_%s" % estrato
        dir_out = os.path.join(raiz_out, nombre)
        os.makedirs(os.path.join(dir_out, "test"), exist_ok=True)
        rnd = np.random.RandomState(semilla + 7000 + ESTRATOS.index(estrato))
        lo, hi = RANGO_F_PRUEBA[estrato]
        imagenes = {}
        for k, (rel, meta) in enumerate(sorted(base.items())):
            im = leer_imagen(os.path.join(dataset, "images", rel))
            cajas = [(o["x1"], o["y1"], o["x2"], o["y2"]) for o in meta["instancias"]]
            _, masc, pegadas = ocluir_siluetas(im, cajas, rnd, banco, todas=True, f_fijo=lambda r: r.uniform(lo, hi))
            cov = cobertura_por_caja(masc, cajas)
            escribir_imagen(os.path.join(dir_out, rel), im)
            inst = [{**o, "cobertura": round(c, 4), "estrato_nominal": estrato, "estrato": estrato_de_cobertura(c)}
                    for o, c in zip(meta["instancias"], cov)]
            # Personas pegadas: region ignore (ni FP ni TP), para no alterar
            # el conjunto de instancias evaluadas del test.
            inst += [{"id": "%s#p%d" % (os.path.splitext(os.path.basename(rel))[0], k), "x1": x1, "y1": y1,
                      "x2": x2, "y2": y2, "estrato": "ignorar", "truncado": 0, "cobertura": 0.0, "pegada": 1}
                     for k, (x1, y1, x2, y2) in enumerate(pegadas)]
            imagenes[rel] = {**meta, "instancias": inst}
            if (k + 1) % 300 == 0:
                print("  %s: %d/%d" % (nombre, k + 1, len(base)), flush=True)
        cnt = conteo_por_estrato(imagenes)
        guardar_gt(os.path.join(dir_out, "gt_%s.json" % nombre), nombre, dir_out, imagenes,
                   extra={"generador": "siluetas v2 (banco test)", "tipo_parche": "silueta", "estrato_nominal": estrato,
                          "rango_f": [lo, hi], "semilla": semilla, "conteo_estrato_efectivo": cnt})
        print("  %-18s estratos efectivos: %s" % (nombre, cnt), flush=True)


def cmd_demo(dataset, n, semilla):
    import cv2
    banco = BancoSiluetas(os.path.join(dataset, "siluetas_train"))
    base = cargar_split_yolo(dataset, "train")
    rnd = np.random.RandomState(semilla)
    nombres = sorted(base); rnd.shuffle(nombres)
    out = os.path.join(dataset, "demo_siluetas"); os.makedirs(out, exist_ok=True)
    hechos = 0
    for rel in nombres:
        if hechos >= n:
            break
        meta = base[rel]
        im = leer_imagen(os.path.join(dataset, "images", rel))
        cajas = [(o["x1"], o["y1"], o["x2"], o["y2"]) for o in meta["instancias"]]
        ap, masc, pegadas = ocluir_siluetas(im, cajas, rnd, banco, p=1.0)
        if not ap:
            continue
        cov = cobertura_por_caja(masc, cajas)
        for (x1, y1, x2, y2) in pegadas:
            cv2.rectangle(im, (int(x1), int(y1)), (int(x2), int(y2)), (255, 128, 0), 1)
        for i, clase, f, c in ap:
            x1, y1, x2, y2 = (int(v) for v in cajas[i])
            cv2.rectangle(im, (x1, y1), (x2, y2), (0, 255, 0), 1)
            cv2.putText(im, "%s f=%.2f ef=%.2f" % (clase[:3], f, cov[i]), (x1, max(12, y1 - 3)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
        escribir_imagen(os.path.join(out, os.path.basename(rel)), im)
        hechos += 1
    print("Guardados %d ejemplos en %s" % (hechos, out))


def selftest():
    import tempfile
    import cv2
    from argos_lib.siluetas import pegar_silueta, OclusionSiluetas
    fallos = []

    def comp(desc, obt, esp):
        ok = obt == esp
        print("  [%s] %-50s %s" % ("ok" if ok else "FALLA", desc, obt))
        if not ok:
            fallos.append(desc)

    tmp = tempfile.mkdtemp(prefix="siluetas_test_")
    # Banco falso: dos recortes RGBA (elipse persona, rectangulo objeto).
    rec = []
    for k, clase in enumerate(("persona", "objeto")):
        a = np.zeros((120, 60), np.uint8)
        if clase == "persona":
            cv2.ellipse(a, (30, 60), (28, 58), 0, 0, 360, 255, -1)
        else:
            a[10:110, 5:55] = 255
        bgra = np.dstack([np.full((120, 60, 3), 90 + 60 * k, np.uint8), a])
        cv2.imwrite(os.path.join(tmp, "%05d.png" % k), bgra)
        rec.append({"archivo": "%05d.png" % k, "clase": clase, "w": 60, "h": 120, "area": int((a > 0).sum())})
    json.dump({"recortes": rec, "conteo": {"persona": 1, "objeto": 1}}, open(os.path.join(tmp, "indice.json"), "w"))
    banco = BancoSiluetas(tmp)
    comp("banco: 2 recortes, indice por clase", (len(banco), len(banco.por_clase["persona"])), (2, 1))
    bgr, alpha = banco.tomar(np.random.RandomState(0), "persona")
    comp("tomar: alpha en [0,1] y forma", (alpha.max() <= 1.0, bgr.shape[:2] == alpha.shape), (True, True))
    # Cobertura objetivo.
    rnd = np.random.RandomState(1)
    errs = []
    for _ in range(100):
        im = np.zeros((300, 300, 3), np.uint8); m = np.zeros((300, 300), np.uint8)
        f = rnd.uniform(0.1, 0.95)
        cov, _ = pegar_silueta(im, m, (100.0, 80.0, 160.0, 220.0), bgr, alpha, rnd, f)
        errs.append(abs(cov - f))
    comp("pegado: |cobertura - f| <= 0.05 en 100 casos", bool(max(errs) <= 0.05), True)
    comp("pegado: mascara y cobertura coherentes", cobertura_por_caja(m, [(100.0, 80.0, 160.0, 220.0)])[0] > 0, True)
    # Generacion con todas las cajas y f fijo por estrato.
    im = np.zeros((300, 300, 3), np.uint8)
    cajas = [(10, 10, 60, 110), (200, 150, 250, 250)]
    ap, m, peg = ocluir_siluetas(im, cajas, np.random.RandomState(2), banco, todas=True, f_fijo=lambda r: r.uniform(0.7, 1.0))
    cov = cobertura_por_caja(m, cajas)
    comp("prueba severa: ambas cajas ocluidas >= 0.65", all(c >= 0.65 for c in cov), True)
    comp("personas pegadas devueltas con caja", len(peg) == sum(1 for a in ap if a[1] == "persona"), True)
    comp("p=0 no toca nada", len(ocluir_siluetas(im.copy(), cajas, np.random.RandomState(3), banco, p=0.0)[0]), 0)
    # Transform de Ultralytics.
    from ultralytics.utils.instance import Instances
    bb = np.array([[0.3, 0.4, 0.2, 0.5]], np.float32)
    inst = Instances(bb, bbox_format="xywh", normalized=True)
    im0 = np.random.RandomState(4).randint(0, 255, (300, 300, 3)).astype(np.uint8)
    np.random.seed(0)
    out = OclusionSiluetas(tmp, p=1.0)({"img": im0.copy(), "instances": inst, "cls": np.zeros((1, 1), np.float32)})
    nb = out["instances"].bboxes
    comp("transform: caja original intacta", bool(np.allclose(nb[0], bb[0], atol=1e-6)), True)
    comp("transform: cls y cajas alineadas (persona pegada etiquetada)",
         (len(nb) == len(out["cls"]), len(nb) >= 1), (True, True))
    comp("transform: imagen modificada", bool(np.array_equal(out["img"], im0)), False)
    import pickle
    comp("transform picklable", pickle.loads(pickle.dumps(OclusionSiluetas(tmp))).dir_banco, tmp)
    shutil.rmtree(tmp, ignore_errors=True)
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO: 11/11 comprobaciones.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - iteracion 2 (siluetas)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dataset", default=os.path.join(RAIZ, "dataset"))
    ap.add_argument("--raiz", default=RAIZ)
    sub = ap.add_subparsers(dest="cmd")
    b = sub.add_parser("bancos")
    b.add_argument("--pesos-seg", default="yolo11s-seg.pt")
    b.add_argument("--max-por-clase", type=int, default=800)
    b.add_argument("--device")
    v = sub.add_parser("val"); v.add_argument("--semilla", type=int, default=31)
    p = sub.add_parser("prueba"); p.add_argument("--semilla", type=int, default=2024)
    d = sub.add_parser("demo"); d.add_argument("--n", type=int, default=12); d.add_argument("--semilla", type=int, default=0)
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if args.cmd == "bancos":
        cmd_bancos(args.dataset, args.raiz, args.pesos_seg, args.max_por_clase, args.device)
    elif args.cmd == "val":
        cmd_val(args.dataset, args.raiz, args.semilla)
    elif args.cmd == "prueba":
        cmd_prueba(args.dataset, args.raiz, args.semilla)
    elif args.cmd == "demo":
        cmd_demo(args.dataset, args.n, args.semilla)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
