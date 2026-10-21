#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - E11 (PREREGISTRO_H14.md): oclusion con ORDEN DE PROFUNDIDAD (argos_lib/profundidad.py).

  mapas      profundidad inversa relativa (Depth Anything V2 Small) de ExDark-People train y test y de las
             imagenes de CityPersons val de H13; PNG de 8 bits, lado mayor 512 (dataset/profundidad/mapas/)
  train      dos versiones ocluidas por imagen de train (semillas 0 y 1; 1-3 personas, f en (0,30; 0,85),
             solo objetos del banco siluetas_train), como la familia generativa -> dataset/profundidad_train/
  prueba     control sintetico 'profundidad_severa' sobre ExDark test (todas las personas validas, f en
             (0,70; 1,00)) -> dataset/test_sintetico/profundidad_severa/
  demo       lamina de ejemplos (antes / despues) para la comprobacion visual
  realismo   secundario de H14: la familia con profundidad sobre las 400 personas base de H13 (misma cobertura
             objetivo), con las funciones de 31_realismo.py -> resultados_h14/realismo_profundidad.json

Uso:  python 32_profundidad.py {mapas,train,prueba,demo,realismo}   |   python 32_profundidad.py --selftest
"""
import argparse
import importlib.util
import json
import os
import sys
import time

import numpy as np

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
from argos_lib import estrato_de_cobertura                                    # noqa: E402
from argos_lib.gt import cargar_split_yolo, conteo_por_estrato, guardar_gt    # noqa: E402
from argos_lib.oclusion import RANGO_F_ENTRENAMIENTO, RANGO_F_PRUEBA, cobertura_por_caja, escribir_imagen, leer_imagen  # noqa: E402
from argos_lib import profundidad as P                                        # noqa: E402

DATASET = os.path.join(RAIZ, "dataset")
MAPAS = os.path.join(DATASET, "profundidad", "mapas")
BANCO_TRAIN = os.path.join(DATASET, "siluetas_train")
BANCO_TEST = os.path.join(DATASET, "siluetas_test")
SEMILLAS_TRAIN = (0, 1)
SEMILLA_PRUEBA = 2024
MIN_LADO = 8
LADO_MAPA = 512


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def ruta_mapa(grupo, nombre):
    return os.path.join(MAPAS, grupo, os.path.splitext(os.path.basename(nombre))[0] + ".png")


def guardar_mapa(ruta, d):
    import cv2
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    H, W = d.shape
    s = LADO_MAPA / max(H, W)
    cv2.imwrite(ruta, (cv2.resize(d, (max(1, int(W * s)), max(1, int(H * s))), interpolation=cv2.INTER_AREA) * 255).round().astype(np.uint8))


def leer_mapa(ruta, H, W):
    import cv2
    m = cv2.imread(ruta, cv2.IMREAD_GRAYSCALE)
    return cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0


def cajas_validas(meta):
    cajas = [(o["x1"], o["y1"], o["x2"], o["y2"]) for o in meta["instancias"]]
    return cajas, [i for i, c in enumerate(cajas) if c[2] - c[0] >= MIN_LADO and c[3] - c[1] >= MIN_LADO]


def _modulo(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, os.path.join(RAIZ, archivo))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


# ----------------------------------------------------------------------------- comandos
def cmd_mapas():
    est = P.EstimadorProfundidad()
    trabajos = []
    for split in ("train", "test"):
        for rel in sorted(cargar_split_yolo(DATASET, split)):
            trabajos.append(("exdark_" + split, os.path.join(DATASET, "images", rel)))
    R = _modulo("realismo31", "31_realismo.py")
    from argos_lib.gt import cargar_gt
    gt = cargar_gt(R.GT_CP)
    dimg = gt["dir_imagenes"] if os.path.isdir(gt["dir_imagenes"]) else os.path.join(RAIZ, "externos", "citypersons", "Citypersons", "images", "val")
    _, base, _ = R.muestras(gt)
    for rel in sorted({b[0] for b in base}):
        trabajos.append(("cityperson_val", os.path.join(dimg, rel)))
    t0 = time.time()
    for k, (grupo, ruta) in enumerate(trabajos):
        dst = ruta_mapa(grupo, ruta)
        if not os.path.exists(dst):
            guardar_mapa(dst, est(leer_imagen(ruta)))
        if (k + 1) % 200 == 0:
            log("  mapas %d/%d (%.2f s/imagen)" % (k + 1, len(trabajos), (time.time() - t0) / (k + 1)))
    log("mapas listos: %d" % len(trabajos))


def cmd_train():
    from argos_lib.siluetas import BancoSiluetas
    base = cargar_split_yolo(DATASET, "train")
    banco = BancoSiluetas(BANCO_TRAIN)
    out = os.path.join(DATASET, "profundidad_train")
    versiones, regs = {}, []
    for k, sem in enumerate(SEMILLAS_TRAIN):
        os.makedirs(os.path.join(out, "v%d" % k), exist_ok=True)
        rnd = np.random.RandomState(sem)
        for rel, meta in sorted(base.items()):
            cajas, validas = cajas_validas(meta)
            n = int(rnd.randint(1, 4))
            eleg = list(rnd.choice(validas, size=min(n, len(validas)), replace=False)) if validas else []
            obj = [(int(i), float(rnd.uniform(*RANGO_F_ENTRENAMIENTO))) for i in eleg]
            im = leer_imagen(os.path.join(DATASET, "images", rel))
            H, W = im.shape[:2]
            prof = leer_mapa(ruta_mapa("exdark_train", rel), H, W)
            r_img = np.random.RandomState((sem * 1000003 + len(regs)) % (2 ** 31))
            personas, _ = P.ocluir_profundidad(im, cajas, r_img, banco, prof, obj)
            nombre = os.path.splitext(os.path.basename(rel))[0]
            archivo = None
            if any(p["ok"] for p in personas):
                archivo = "v%d/%s.jpg" % (k, nombre)
                escribir_imagen(os.path.join(out, archivo), im)
            versiones.setdefault(nombre, [])
            if archivo:
                versiones[nombre].append(archivo)
            regs.append({"imagen": nombre, "version": k, "archivo": archivo, "personas": personas})
        log("  version v%d lista" % k)
    pers = [p for r in regs for p in r["personas"]]
    qc = {"intentadas": len(pers), "aceptadas": sum(p["ok"] for p in pers),
          "tasa_exito": round(sum(p["ok"] for p in pers) / max(1, len(pers)), 4),
          "cobertura_media_aceptadas": round(float(np.mean([p["cobertura"] for p in pers if p["ok"]] or [0])), 4)}
    with open(os.path.join(out, "registro.jsonl"), "w", encoding="utf-8") as fh:
        for r in regs:
            fh.write(json.dumps(r) + "\n")
    json.dump({"generador": "argos_lib.profundidad (Depth Anything V2 Small, orden de profundidad, solo objetos)",
               "semillas": SEMILLAS_TRAIN, "rango_f": RANGO_F_ENTRENAMIENTO, "control_calidad": qc, "versiones": versiones},
              open(os.path.join(out, "indice.json"), "w", encoding="utf-8"), indent=1)
    log("train: %d imagenes con version ocluida; %s" % (sum(1 for v in versiones.values() if v), qc))


def cmd_prueba():
    from argos_lib.siluetas import BancoSiluetas
    base = cargar_split_yolo(DATASET, "test")
    banco = BancoSiluetas(BANCO_TEST)
    nombre_c = "profundidad_severa"
    dir_out = os.path.join(DATASET, "test_sintetico", nombre_c)
    rnd = np.random.RandomState(SEMILLA_PRUEBA)
    lo, hi = RANGO_F_PRUEBA["severa"]
    imagenes, pers = {}, []
    for h, (rel, meta) in enumerate(sorted(base.items())):
        cajas, validas = cajas_validas(meta)
        obj = [(i, float(rnd.uniform(lo, hi))) for i in validas]
        im = leer_imagen(os.path.join(DATASET, "images", rel))
        H, W = im.shape[:2]
        prof = leer_mapa(ruta_mapa("exdark_test", rel), H, W)
        personas, mascara = P.ocluir_profundidad(im, cajas, np.random.RandomState(SEMILLA_PRUEBA * 1000003 + h), banco, prof, obj)
        pers += personas
        os.makedirs(os.path.dirname(os.path.join(dir_out, rel)), exist_ok=True)
        escribir_imagen(os.path.join(dir_out, rel), im)
        cov = cobertura_por_caja(mascara, cajas)
        imagenes[rel] = {**meta, "instancias": [{**o, "cobertura": float(c), "estrato_nominal": "severa",
                                                 "estrato": estrato_de_cobertura(c)} for o, c in zip(meta["instancias"], cov)]}
    cnt = conteo_por_estrato(imagenes)
    qc = {"intentadas": len(pers), "aceptadas": sum(p["ok"] for p in pers)}
    guardar_gt(os.path.join(dir_out, "gt_%s.json" % nombre_c), nombre_c, dir_out, imagenes,
               extra={"generador": "oclusion con orden de profundidad (E11)", "tipo_parche": "profundidad", "estrato_nominal": "severa",
                      "rango_f": [lo, hi], "semilla": SEMILLA_PRUEBA, "conteo_estrato_efectivo": cnt, "control_calidad": qc})
    log("%s: estratos efectivos %s; %s" % (nombre_c, cnt, qc))


def cmd_demo(n=12, semilla=0):
    import cv2
    from argos_lib.siluetas import BancoSiluetas
    base = cargar_split_yolo(DATASET, "train")
    banco = BancoSiluetas(BANCO_TRAIN)
    rnd = np.random.RandomState(semilla)
    nombres = sorted(base); rnd.shuffle(nombres)
    out = os.path.join(DATASET, "demo_profundidad"); os.makedirs(out, exist_ok=True)
    filas = []
    for rel in nombres:
        cajas, validas = cajas_validas(base[rel])
        if not validas:
            continue
        i = int(max(validas, key=lambda j: (cajas[j][2] - cajas[j][0]) * (cajas[j][3] - cajas[j][1])))
        im = leer_imagen(os.path.join(DATASET, "images", rel)); o = im.copy()
        H, W = im.shape[:2]
        prof = leer_mapa(ruta_mapa("exdark_train", rel), H, W)
        res, _ = P.ocluir_profundidad(im, cajas, np.random.RandomState(777 + len(filas)), banco, prof, [(i, float(rnd.uniform(0.4, 0.8)))])
        if not res[0]["ok"]:
            continue
        x1, y1, x2, y2 = (int(v) for v in cajas[i])
        s = int(max(x2 - x1, y2 - y1) * 1.8); cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        a, b = max(0, cx - s // 2), max(0, cy - s // 2)
        pm = cv2.applyColorMap((prof * 255).astype(np.uint8), cv2.COLORMAP_INFERNO)
        trio = [cv2.resize(z[b:b + s, a:a + s], (240, 240)) for z in (o, pm, im)]
        par = np.hstack(trio)
        cv2.putText(par, "f=%.2f cob=%.2f dp=%.2f do=%.2f" % (res[0]["f"], res[0]["cobertura"], res[0]["d_persona"], res[0]["d_oclusor"]),
                    (5, 232), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
        filas.append(par)
        if len(filas) >= n:
            break
    escribir_imagen(os.path.join(out, "_lamina.jpg"), np.vstack(filas))
    log("demo: %d ejemplos -> %s" % (len(filas), out))


def cmd_realismo():
    import cv2
    from argos_lib.gt import cargar_gt
    from argos_lib.siluetas import BancoSiluetas
    R = _modulo("realismo31", "31_realismo.py")
    gt = cargar_gt(R.GT_CP)
    dimg = gt["dir_imagenes"] if os.path.isdir(gt["dir_imagenes"]) else os.path.join(RAIZ, "externos", "citypersons", "Citypersons", "images", "val")
    _, base, objetivo = R.muestras(gt)
    banco = BancoSiluetas(os.path.join(DATASET, "siluetas_cp_val"))
    dst = os.path.join(R.SAL, "profundidad"); os.makedirs(dst, exist_ok=True)
    filas = []
    for k, (rel, i, caja, _) in enumerate(base):
        im = leer_imagen(os.path.join(dimg, rel)); H, W = im.shape[:2]
        prof = leer_mapa(ruta_mapa("cityperson_val", rel), H, W)
        todas = R.cajas_de(gt["imagenes"][rel])
        res, _ = P.ocluir_profundidad(im, todas, np.random.RandomState(13000 + k), banco, prof, [(i, objetivo[k])])
        cv2.imwrite(os.path.join(dst, "%03d.png" % k), R.recorte(im, caja))
        filas.append({"k": k, **res[0]})
    F = dict(np.load(os.path.join(R.RES, "caracteristicas.npz")))
    import torch
    from PIL import Image
    from transformers import AutoImageProcessor, AutoModel
    proc = AutoImageProcessor.from_pretrained("facebook/dinov2-base")
    mod = AutoModel.from_pretrained("facebook/dinov2-base").to("cuda").eval()
    vec = []
    for a in range(0, R.N, 32):
        ims = [Image.open(os.path.join(dst, "%03d.png" % k)).convert("RGB") for k in range(a, min(R.N, a + 32))]
        with torch.no_grad():
            vec.append(mod(**proc(images=ims, return_tensors="pt").to("cuda")).pooler_output.float().cpu().numpy())
    Xp = np.concatenate(vec)
    s0, s1 = R.puntuaciones_oof(F["dinov2__real"], Xp)
    rnd = np.random.RandomState(0)
    boot = [R.auc(s0[rnd.randint(0, R.N, R.N)], s1[rnd.randint(0, R.N, R.N)]) for _ in range(R.B)]
    out = {"AUC_dinov2": round(float(R.auc(s0, s1)), 4), "IC": [round(float(np.percentile(boot, 2.5)), 4), round(float(np.percentile(boot, 97.5)), 4)],
           "aplicadas": int(sum(f["ok"] for f in filas)), "cobertura_media": round(float(np.mean([f["cobertura"] for f in filas])), 4),
           "KID": R.kid(F["dinov2__real"], Xp)}
    os.makedirs(os.path.join(RAIZ, "resultados_h14"), exist_ok=True)
    json.dump({"resumen": out, "personas": filas}, open(os.path.join(RAIZ, "resultados_h14", "realismo_profundidad.json"), "w", encoding="utf-8"), indent=1)
    log("realismo de la familia con profundidad: %s" % out)


# ----------------------------------------------------------------------------- autotest
def selftest():
    fallos = []

    def comp(desc, ok):
        print("  [%s] %s" % ("OK" if ok else "FALLO", desc))
        if not ok:
            fallos.append(desc)
    H, W = 200, 200
    caja = (80.0, 40.0, 120.0, 160.0)                 # persona de 40 x 120, pies en y = 160
    alpha = np.ones((60, 40), np.float32); bgr = np.full((60, 40, 3), 200, np.uint8)
    # escena: profundidad crece hacia abajo (suelo), persona a 0,5
    prof = np.tile(np.linspace(0.2, 0.9, H, dtype=np.float32)[:, None], (1, W)); prof[40:160, 80:120] = 0.5
    im = np.zeros((H, W, 3), np.uint8); m = np.zeros((H, W), np.uint8)
    cov, dp, do = P.pegar_profundidad(im, m, caja, bgr, alpha, np.random.RandomState(0), 0.4, prof)
    comp("con suelo delante, se pega (cobertura > 0)", cov > 0)
    comp("cobertura cerca del objetivo 0,4", abs(cov - 0.4) < 0.08)
    comp("el oclusor esta mas cerca que la persona", do is not None and do > dp)
    prof2 = np.full((H, W), 0.9, np.float32); prof2[40:160, 80:120] = 0.95   # nada puede estar delante de la persona
    im2 = np.zeros((H, W, 3), np.uint8)
    cov2, _, do2 = P.pegar_profundidad(im2, np.zeros((H, W), np.uint8), caja, bgr, alpha, np.random.RandomState(0), 0.4, prof2)
    comp("si la escena no deja estar delante, no se pega", cov2 == 0 and do2 is None and im2.max() == 0)
    prof3 = prof.copy(); prof3[100:160, 80:100] = 0.99                         # algo ya mas cerca tapa la mitad izquierda inferior
    im3 = np.zeros((H, W, 3), np.uint8)
    cov3, _, _ = P.pegar_profundidad(im3, np.zeros((H, W), np.uint8), caja, bgr, alpha, np.random.RandomState(0), 0.4, prof3)
    comp("lo que ya esta mas cerca no se tapa", im3[100:160, 80:100].max() == 0 and cov3 > 0)
    comp("profundidad de la persona = mediana de su mitad inferior", abs(P.profundidad_persona(prof, caja) - 0.5) < 1e-6)
    print("\n%s" % ("AUTOTEST SUPERADO: %d/%d" % (6 - len(fallos), 6) if not fallos else "FALLOS: %s" % fallos))
    sys.exit(1 if fallos else 0)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - E11 oclusion con orden de profundidad")
    ap.add_argument("paso", nargs="?", choices=["mapas", "train", "prueba", "demo", "realismo"])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    {"mapas": cmd_mapas, "train": cmd_train, "prueba": cmd_prueba, "demo": cmd_demo, "realismo": cmd_realismo}[a.paso]()


if __name__ == "__main__":
    main()
