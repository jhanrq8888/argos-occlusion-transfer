#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - H9 (PREREGISTRO_H9.md): tercera familia de oclusor, OCLUSION GENERATIVA.

Subcomandos:
  demo     12 imagenes de TRAIN (original | ocluida) en dataset/demo_generativa/,
           con el tiempo por oclusion. Solo para inspeccion visual del generador.
  train    Dos versiones ocluidas de cada imagen de train (semillas 0 y 1) en
           dataset/generativa_train/v<k>/; en cada version se ocluyen 1-3
           personas al azar con f ~ U[0.30, 0.85]. Indice: indice.json.
  prueba   Control sintetico generativa_severa: todas las personas de ExDark test
           con f ~ U[0.70, 1.00], semilla 2024; GT con cobertura efectiva y
           estrato en dataset/test_sintetico/generativa_severa/.
Los subcomandos train y prueba son reanudables (registro .jsonl por imagen).

Uso:
    python 25_oclusion_generativa.py demo
    python 25_oclusion_generativa.py train
    python 25_oclusion_generativa.py prueba
    python 25_oclusion_generativa.py --selftest
"""

import argparse
import json
import os
import shutil
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argos_lib import estrato_de_cobertura                                    # noqa: E402
from argos_lib.gt import cargar_split_yolo, conteo_por_estrato, guardar_gt    # noqa: E402
from argos_lib.oclusion import RANGO_F_ENTRENAMIENTO, RANGO_F_PRUEBA, cobertura_por_caja, escribir_imagen, leer_imagen  # noqa: E402
from argos_lib import generativa as G                                         # noqa: E402

RAIZ = os.path.dirname(os.path.abspath(__file__))
DIR_MODELO = os.path.join(RAIZ, "modelos", "sd15_inpaint")
SEMILLAS_TRAIN = (0, 1)
SEMILLA_PRUEBA = 2024
TROZO = 24            # imagenes por llamada a GeneradorOclusion.ocluir (memoria)


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def cajas_validas(meta):
    cajas = [(o["x1"], o["y1"], o["x2"], o["y2"]) for o in meta["instancias"]]
    validas = [i for i, c in enumerate(cajas) if c[2] - c[0] >= G.MIN_LADO_CAJA and c[3] - c[1] >= G.MIN_LADO_CAJA]
    return cajas, validas


def leer_hechos(ruta):
    hechos = {}
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as fh:
            for l in fh:
                if l.strip():
                    d = json.loads(l)
                    hechos[d["imagen"]] = d
    return hechos


def resumen_qc(registros):
    pers = [p for r in registros for p in r["personas"]]
    n, ok = len(pers), sum(p["ok"] for p in pers)
    return {"intentadas": n, "aceptadas": ok, "tasa_exito": round(ok / n, 4) if n else None,
            "intentos_medios": round(float(np.mean([p["intentos"] for p in pers])), 3) if n else None}


def cmd_train(dataset, gen):
    base = cargar_split_yolo(dataset, "train")
    out = os.path.join(dataset, "generativa_train")
    for k, sem in enumerate(SEMILLAS_TRAIN):
        dir_v = os.path.join(out, "v%d" % k)
        os.makedirs(dir_v, exist_ok=True)
        reg = os.path.join(out, "registro_v%d.jsonl" % k)
        hechos = leer_hechos(reg)
        rnd = np.random.RandomState(sem)
        plan = []
        for rel, meta in sorted(base.items()):
            cajas, validas = cajas_validas(meta)
            n = int(rnd.randint(1, 4))
            elegidas = list(rnd.choice(validas, size=min(n, len(validas)), replace=False)) if validas else []
            fs = [float(rnd.uniform(*RANGO_F_ENTRENAMIENTO)) for _ in elegidas]
            plan.append((rel, cajas, [(int(i), f) for i, f in zip(elegidas, fs)]))
        pendientes = [p for p in plan if os.path.basename(p[0]) not in hechos]
        log("version v%d (semilla %d): %d imagenes, %d pendientes" % (k, sem, len(plan), len(pendientes)))
        t0 = time.time()
        for a in range(0, len(pendientes), TROZO):
            trozo = pendientes[a:a + TROZO]
            trabajos = [{"im": leer_imagen(os.path.join(dataset, "images", rel)), "cajas": cajas, "objetivo": obj,
                         "semilla": sem * 1000003 + h} for h, (rel, cajas, obj) in enumerate(trozo, start=a)]
            res = gen.ocluir(trabajos)
            with open(reg, "a", encoding="utf-8") as fh:
                for (rel, cajas, obj), t, (personas, efectiva) in zip(trozo, trabajos, res):
                    nombre = os.path.basename(rel)
                    archivo = None
                    if any(p["ok"] for p in personas):
                        archivo = "v%d/%s.jpg" % (k, os.path.splitext(nombre)[0])
                        escribir_imagen(os.path.join(out, archivo), t["im"])
                    cov = cobertura_por_caja(efectiva, cajas)
                    for p in personas:
                        p["cobertura_efectiva"] = round(float(cov[p["idx"]]), 4)
                    fh.write(json.dumps({"imagen": nombre, "archivo": archivo, "personas": personas}) + "\n")
            hechas = a + len(trozo)
            v = (time.time() - t0) / hechas
            log("  v%d: %d/%d imagenes (%.1f s/imagen; faltan ~%.0f min)" % (k, hechas, len(pendientes), v,
                                                                           v * (len(pendientes) - hechas) / 60))
    # Indice: para cada imagen, las versiones con al menos una oclusion aceptada.
    versiones, regs = {}, []
    for k in range(len(SEMILLAS_TRAIN)):
        for nombre, d in leer_hechos(os.path.join(out, "registro_v%d.jsonl" % k)).items():
            regs.append(d)
            versiones.setdefault(os.path.splitext(nombre)[0], [])
            if d["archivo"]:
                versiones[os.path.splitext(nombre)[0]].append(d["archivo"])
    qc = resumen_qc(regs)
    with open(os.path.join(out, "indice.json"), "w", encoding="utf-8") as fh:
        json.dump({"generador": "SD1.5 inpainting fp16, DPM-Solver %d pasos, guia %.1f" % (G.PASOS, G.GUIA),
                   "semillas": SEMILLAS_TRAIN, "rango_f": RANGO_F_ENTRENAMIENTO, "control_calidad": qc,
                   "versiones": versiones}, fh, indent=1)
    log("train listo: %d imagenes con version ocluida; control de calidad %s" %
        (sum(1 for v in versiones.values() if v), qc))


def cmd_prueba(dataset, gen):
    base = cargar_split_yolo(dataset, "test")
    nombre_c = "generativa_severa"
    dir_out = os.path.join(dataset, "test_sintetico", nombre_c)
    os.makedirs(os.path.join(dir_out, "test"), exist_ok=True)
    reg = os.path.join(dir_out, "registro.jsonl")
    hechos = leer_hechos(reg)
    rnd = np.random.RandomState(SEMILLA_PRUEBA)
    lo, hi = RANGO_F_PRUEBA["severa"]
    plan = []
    for rel, meta in sorted(base.items()):
        cajas, validas = cajas_validas(meta)
        plan.append((rel, cajas, [(i, float(rnd.uniform(lo, hi))) for i in validas]))
    pendientes = [p for p in plan if os.path.basename(p[0]) not in hechos]
    log("%s: %d imagenes, %d pendientes" % (nombre_c, len(plan), len(pendientes)))
    t0 = time.time()
    for a in range(0, len(pendientes), TROZO):
        trozo = pendientes[a:a + TROZO]
        trabajos = [{"im": leer_imagen(os.path.join(dataset, "images", rel)), "cajas": cajas, "objetivo": obj,
                     "semilla": SEMILLA_PRUEBA * 1000003 + h} for h, (rel, cajas, obj) in enumerate(trozo, start=a)]
        res = gen.ocluir(trabajos)
        with open(reg, "a", encoding="utf-8") as fh:
            for (rel, cajas, obj), t, (personas, efectiva) in zip(trozo, trabajos, res):
                escribir_imagen(os.path.join(dir_out, rel), t["im"])
                cov = cobertura_por_caja(efectiva, cajas)
                fh.write(json.dumps({"imagen": os.path.basename(rel), "rel": rel, "personas": personas,
                                     "cobertura": [round(float(c), 4) for c in cov]}) + "\n")
        hechas = a + len(trozo)
        v = (time.time() - t0) / hechas
        log("  %s: %d/%d (%.1f s/imagen; faltan ~%.0f min)" % (nombre_c, hechas, len(pendientes), v,
                                                              v * (len(pendientes) - hechas) / 60))
    hechos = leer_hechos(reg)
    imagenes = {}
    for rel, meta in sorted(base.items()):
        d = hechos[os.path.basename(rel)]
        inst = [{**o, "cobertura": c, "estrato_nominal": "severa", "estrato": estrato_de_cobertura(c)}
                for o, c in zip(meta["instancias"], d["cobertura"])]
        imagenes[rel] = {**meta, "instancias": inst}
    cnt = conteo_por_estrato(imagenes)
    qc = resumen_qc(list(hechos.values()))
    guardar_gt(os.path.join(dir_out, "gt_%s.json" % nombre_c), nombre_c, dir_out, imagenes,
               extra={"generador": "oclusion generativa H9 (SD1.5 inpainting)", "tipo_parche": "generativa",
                      "estrato_nominal": "severa", "rango_f": [lo, hi], "semilla": SEMILLA_PRUEBA,
                      "conteo_estrato_efectivo": cnt, "control_calidad": qc})
    log("%s: estratos efectivos %s; control de calidad %s" % (nombre_c, cnt, qc))


def cmd_demo(dataset, gen, n, semilla):
    import cv2
    base = cargar_split_yolo(dataset, "train")
    rnd = np.random.RandomState(semilla)
    nombres = sorted(base); rnd.shuffle(nombres)
    out = os.path.join(dataset, "demo_generativa"); os.makedirs(out, exist_ok=True)
    elegidas = []
    for rel in nombres:
        cajas, validas = cajas_validas(base[rel])
        if validas:
            i = int(max(validas, key=lambda j: (cajas[j][2] - cajas[j][0]) * (cajas[j][3] - cajas[j][1])))
            elegidas.append((rel, cajas, [(i, float(rnd.uniform(*RANGO_F_ENTRENAMIENTO)))]))
        if len(elegidas) >= n:
            break
    trabajos = [{"im": leer_imagen(os.path.join(dataset, "images", rel)), "cajas": c, "objetivo": o, "semilla": 777 + h}
                for h, (rel, c, o) in enumerate(elegidas)]
    origs = [t["im"].copy() for t in trabajos]
    t0 = time.time()
    res = gen.ocluir(trabajos)
    dur = time.time() - t0
    filas = []
    for (rel, cajas, obj), t, o, (personas, efectiva) in zip(elegidas, trabajos, origs, res):
        p = personas[0]
        x1, y1, x2, y2 = (int(v) for v in cajas[p["idx"]])
        x, y, s = G.ventana(cajas[p["idx"]], *o.shape[:2])
        a, b = o[y:y + s, x:x + s].copy(), t["im"][y:y + s, x:x + s].copy()
        for im in (a, b):
            cv2.rectangle(im, (x1 - x, y1 - y), (x2 - x, y2 - y), (0, 255, 0), 1)
        par = np.hstack([cv2.resize(a, (300, 300)), cv2.resize(b, (300, 300))])
        cov = cobertura_por_caja(efectiva, cajas)[p["idx"]]
        cv2.putText(par, "%s f=%.2f ef=%.2f %s x%d" % (p["clase"], p["f"], cov, "OK" if p["ok"] else "FALLO", p["intentos"]),
                    (5, 292), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        filas.append(par)
        escribir_imagen(os.path.join(out, os.path.basename(rel)), par)
    lamina = np.vstack([np.hstack(filas[i:i + 2]) if len(filas[i:i + 2]) == 2 else np.hstack([filas[i], np.zeros_like(filas[i])])
                        for i in range(0, len(filas), 2)])
    escribir_imagen(os.path.join(out, "_lamina.jpg"), lamina)
    intentos = sum(p["intentos"] for r, _ in res for p in r)
    log("demo: %d imagenes, %d inpaintings, %.1f s en total (%.2f s por inpainting); aceptadas %d/%d -> %s" %
        (len(trabajos), intentos, dur, dur / max(1, intentos), sum(p["ok"] for r, _ in res for p in r), len(trabajos), out))


def selftest():
    import pickle
    import tempfile
    fallos = []

    def comp(desc, obt, esp):
        ok = obt == esp
        print("  [%s] %-58s %s" % ("ok" if ok else "FALLA", desc, obt))
        if not ok:
            fallos.append(desc)

    rnd = np.random.RandomState(0)
    errs, lados = [], set()
    for _ in range(200):
        H, W = 400, 500
        bw, bh = rnd.randint(10, 120), rnd.randint(20, 300)
        x1, y1 = rnd.randint(0, W - bw), rnd.randint(0, H - bh)
        caja = (float(x1), float(y1), float(x1 + bw), float(y1 + bh))
        f = rnd.uniform(0.1, 0.95)
        m, lado = G.mascara_oclusor(caja, f, rnd, H, W)
        lados.add(lado)
        errs.append(abs(G.cobertura(m, caja) - f))
    comp("mascara: |cobertura - f| <= 0.05 en 200 casos (p95)", bool(np.percentile(errs, 95) <= 0.05), True)
    comp("mascara: se usan los cuatro lados", sorted(lados), [0, 1, 2, 3])
    x, y, s = G.ventana((5.0, 5.0, 40.0, 100.0), 300, 200)
    comp("ventana dentro de la imagen", (x >= 0, y >= 0, x + s <= 200, y + s <= 300), (True,) * 4)
    comp("ventana: lado minimo 128", s >= 128, True)
    # Sustitucion en el dataset.
    tmp = tempfile.mkdtemp(prefix="gen_test_")
    os.makedirs(os.path.join(tmp, "v0"))
    ruta_val = os.path.join(RAIZ, "dataset", "images", "val")
    f0 = sorted(os.listdir(ruta_val))[0]
    im0 = leer_imagen(os.path.join(ruta_val, f0))
    escribir_imagen(os.path.join(tmp, "v0", os.path.splitext(f0)[0] + ".jpg"), 255 - im0)
    json.dump({"versiones": {os.path.splitext(f0)[0]: ["v0/%s.jpg" % os.path.splitext(f0)[0]]}},
              open(os.path.join(tmp, "indice.json"), "w"))
    oc = G.OclusionGenerativa(tmp, p_mosaico=1.0, p_sin_mosaico=0.0)
    comp("sustituta con p=1 devuelve la version", os.path.basename(str(oc.sustituta(f0, True))),
         os.path.splitext(f0)[0] + ".jpg")
    comp("sustituta sin mosaico con p=0 devuelve None", oc.sustituta(f0, False), None)
    comp("sustituta de imagen sin version -> None", oc.sustituta("no_existe.jpg", True), None)
    comp("picklable", pickle.loads(pickle.dumps(oc)).dir_versiones, tmp)
    try:
        from argos_lib.entrenamiento import DatasetOclusion, describir_cadena
        from ultralytics.cfg import get_cfg
        cfg = get_cfg(overrides={"imgsz": 640, "task": "detect"})
        data = {"names": {0: "person"}, "nc": 1, "channels": 3}
        ds = DatasetOclusion(img_path=ruta_val, imgsz=640, batch_size=4, augment=True, hyp=cfg, rect=False,
                             cache=None, single_cls=False, stride=32, pad=0.0, prefix="", task="detect",
                             classes=None, data=data, fraction=0.02, oclusion=oc)
        comp("sin transform de oclusion en la cadena", "OclusionGenerativa" in describir_cadena(ds), False)
        i = [os.path.basename(f) for f in ds.im_files].index(f0)
        a, hw0, hw = ds.load_image(i)
        b, _, _ = super(DatasetOclusion, ds).load_image(i)
        comp("con mosaico y p=1: imagen sustituida, mismo tamano", (a.shape == b.shape, bool((a != b).any())), (True, True))
        comp("la cache no guarda la version ocluida", ds.ims[i] is None or bool((ds.ims[i] == b).all()), True)
        # Mosaico con bufer vacio y la primera lectura sustituida (fallo del 03/10, corregido).
        ds.buffer.clear()
        idx_con_version = [k for k, f in enumerate(ds.im_files) if os.path.basename(f) == f0]
        muestra = ds[idx_con_version[0]]
        comp("mosaico con bufer vacio y primera lectura sustituida", "img" in muestra, True)
        oc.indice[os.path.splitext(f0)[0]]
        for k in range(min(8, len(ds))):
            ds[k]
        comp("varias muestras con mosaico sin error", True, True)
        ds.close_mosaic(cfg)
        a2, _, _ = ds.load_image(i)
        comp("tras close_mosaic (p=0): imagen original", bool((a2 == b).all()), True)
        comp("muestra con imagen y cajas", "img" in ds[0], True)
    except Exception as e:                                       # pragma: no cover
        print("  [FALLA] dataset: %r" % e)
        fallos.append("dataset")
    shutil.rmtree(tmp, ignore_errors=True)
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - H9 oclusion generativa")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dataset", default=os.path.join(RAIZ, "dataset"))
    ap.add_argument("--lote", type=int, default=4)
    sub = ap.add_subparsers(dest="cmd")
    d = sub.add_parser("demo"); d.add_argument("--n", type=int, default=12); d.add_argument("--semilla", type=int, default=0)
    sub.add_parser("train"); sub.add_parser("prueba")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if args.cmd not in ("demo", "train", "prueba"):
        ap.print_help(); return
    gen = G.GeneradorOclusion(DIR_MODELO, pesos_seg=os.path.join(RAIZ, "yolo11s-seg.pt"), lote=args.lote)
    if args.cmd == "demo":
        cmd_demo(args.dataset, gen, args.n, args.semilla)
    elif args.cmd == "train":
        cmd_train(args.dataset, gen)
    else:
        cmd_prueba(args.dataset, gen)


if __name__ == "__main__":
    main()
