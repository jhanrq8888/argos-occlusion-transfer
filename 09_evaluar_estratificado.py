#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Paso 7: evaluacion estratificada (Seccion 2.4, script unico).

Para cada corrida (pesos) y cada conjunto de prueba (GT en formato comun):
  1. inferencia una sola vez, cacheada en resultados/det/ (conf 0.001,
     NMS IoU 0.7, max_det 300, 640 px: los valores de validacion de
     Ultralytics), para que el bootstrap (11) no vuelva a inferir;
  2. AP@0.5 y AP@0.5:0.95 GLOBAL (todas las personas validas) y POR ESTRATO
     con la regla de regiones ignore (argos_lib.ap);
  3. AP por condicion de iluminacion (exploratorio) y cruce luz x estrato;
  4. opcionalmente la regla de fusion moderada+severa -> 'ocluida'.

Conjuntos evaluados por defecto:
  - dataset/gt_test_real.json           prueba original (global) + estratos
                                        reales anotados (Fuente 2b)
  - dataset/test_sintetico/*/gt_*.json  estratos sinteticos por tipo de
                                        parche (Fuente 2a)
  - cualquier gt_*.json de fuentes externas (12_fuentes_externas.py)

Salida: resultados/eval/<corrida>.json y resultados/resumen_ap.csv (una
fila por corrida x conjunto x estrato x luz), listo para 11_analisis.

Uso:
    python 09_evaluar_estratificado.py --corridas runs/argos          # todas las corridas
    python 09_evaluar_estratificado.py --pesos runs/detect/piloto_gpu/weights/best.pt --nombre piloto
    python 09_evaluar_estratificado.py --pesos yolo11s.pt --nombre coco_person --clase-coco 0
    python 09_evaluar_estratificado.py --corridas runs/argos --fusion
    python 09_evaluar_estratificado.py --selftest
"""

import argparse
import csv
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argos_lib import ESTRATOS                                  # noqa: E402
from argos_lib.ap import ap_conjunto, emparejar_conjunto        # noqa: E402
from argos_lib.atencion import registrar_cbam                   # noqa: E402
from argos_lib.gt import (cargar_detecciones, cargar_gt,        # noqa: E402
                          guardar_detecciones)

RAIZ = os.path.dirname(os.path.abspath(__file__))
CONF, IOU_NMS, MAX_DET, IMGSZ = 0.001, 0.7, 300, 640
NO_ESTRATO = ("sin_anotar", "ignorar")
FUSION = {"ocluida": ("moderada", "severa")}


def estratos_presentes(imagenes):
    """Los cuatro canonicos primero; despues cualquier otra etiqueta (p. ej.
    'ocluida' de NightOwls o 'bare/partial/heavy' de CityPersons)."""
    pres = {o["estrato"] for m in imagenes.values() for o in m["instancias"]}
    return [e for e in ESTRATOS if e in pres] + sorted(pres - set(ESTRATOS) - set(NO_ESTRATO))


def conjuntos_por_defecto(dataset):
    rutas = []
    real = os.path.join(dataset, "gt_test_real.json")
    if os.path.exists(real):
        rutas.append(real)
    rutas += sorted(glob.glob(os.path.join(dataset, "test_sintetico", "*", "gt_*.json")))
    rutas += sorted(glob.glob(os.path.join(dataset, "externos", "gt_*.json")))
    return rutas


def inferir(pesos, gt, ruta_cache, clase=None, device=None, batch=16):
    """Detecciones de `pesos` sobre las imagenes de `gt`, con cache."""
    if os.path.exists(ruta_cache):
        d = cargar_detecciones(ruta_cache)
        if d.get("pesos") == str(pesos) and len(d["detecciones"]) == len(gt["imagenes"]):
            return d["detecciones"]
    registrar_cbam()
    from ultralytics import RTDETR, YOLO
    from argos_lib.entrenamiento import es_rtdetr
    # RT-DETR (H8) no usa NMS y su salida tiene otro formato: se carga con su clase.
    modelo = RTDETR(pesos) if es_rtdetr(pesos) else YOLO(pesos)
    nombres = sorted(gt["imagenes"])
    rutas = [os.path.join(gt["dir_imagenes"], n) for n in nombres]
    det = {}
    t0 = time.time()
    for i in range(0, len(rutas), batch):
        lote = rutas[i:i + batch]
        res = modelo.predict(lote, conf=CONF, iou=IOU_NMS, max_det=MAX_DET,
                             imgsz=IMGSZ, verbose=False, device=device,
                             classes=[clase] if clase is not None else None)
        for n, r in zip(nombres[i:i + batch], res):
            b = r.boxes
            if b is None or len(b) == 0:
                det[n] = []
                continue
            xyxy = b.xyxy.cpu().numpy()
            sc = b.conf.cpu().numpy()
            det[n] = [[float(x1), float(y1), float(x2), float(y2), float(s)]
                      for (x1, y1, x2, y2), s in zip(xyxy, sc)]
    os.makedirs(os.path.dirname(ruta_cache), exist_ok=True)
    guardar_detecciones(ruta_cache, pesos, gt["conjunto"], det, CONF, IOU_NMS,
                        extra={"max_det": MAX_DET, "imgsz": IMGSZ,
                               "segundos_inferencia": round(time.time() - t0, 1)})
    return det


def evaluar_conjunto(gt, det, fusion=False, por_luz=True):
    """Devuelve lista de filas {estrato, luz, AP50, AP, n_gt, n_img}."""
    imagenes = gt["imagenes"]
    filas = []
    luces = sorted({m["luz"] for m in imagenes.values()}) if por_luz else []

    def fila(estrato, luz, filtro=None, estr=None):
        emp, noms = emparejar_conjunto(imagenes, det, estrato=estr,
                                       filtro_imagen=filtro)
        r = ap_conjunto(emp)
        return {"estrato": estrato, "luz": luz, "AP50": r["AP50"], "AP": r["AP"],
                "n_gt": r["n_gt"], "n_img": len(noms)}

    # Global y por estrato, agregando iluminacion (analisis confirmatorio).
    filas.append(fila("global", "todas"))
    presentes = estratos_presentes(imagenes)
    for e in presentes:
        filas.append(fila(e, "todas", estr=e))
    if fusion:
        # moderada+severa -> 'ocluida': se reetiqueta en una copia del GT.
        for nombre, (a, b) in FUSION.items():
            copia = {k: {**m, "instancias": [
                {**o, "estrato": nombre if o["estrato"] in (a, b) else o["estrato"]}
                for o in m["instancias"]]} for k, m in imagenes.items()}
            emp, noms = emparejar_conjunto(copia, det, estrato=nombre)
            r = ap_conjunto(emp)
            filas.append({"estrato": nombre, "luz": "todas", "AP50": r["AP50"],
                          "AP": r["AP"], "n_gt": r["n_gt"], "n_img": len(noms)})
    # Por iluminacion (exploratorio): global y cruce con estrato.
    for luz in luces:
        f = (lambda n, m, L=luz: m["luz"] == L)
        filas.append(fila("global", luz, filtro=f))
        for e in presentes:
            filas.append(fila(e, luz, filtro=f, estr=e))
    return filas


def evaluar_corrida(nombre, pesos, rutas_gt, dir_res, fusion, clase, device,
                    meta=None, verbose=True):
    salida = {"corrida": nombre, "pesos": str(pesos), "conjuntos": {},
              "conf": CONF, "iou_nms": IOU_NMS, "max_det": MAX_DET, "imgsz": IMGSZ}
    # Fusionar con una evaluacion previa de la misma corrida (otros conjuntos).
    previo = os.path.join(dir_res, "eval", "%s.json" % nombre)
    if os.path.exists(previo):
        try:
            with open(previo, encoding="utf-8") as fh:
                ant = json.load(fh)
            if ant.get("pesos") == str(pesos):
                salida["conjuntos"].update(ant.get("conjuntos", {}))
        except (OSError, ValueError):
            pass
    if meta:
        salida.update(meta)
    for ruta in rutas_gt:
        gt = cargar_gt(ruta)
        cache = os.path.join(dir_res, "det", "%s__%s.json" % (nombre, gt["conjunto"]))
        det = inferir(pesos, gt, cache, clase=clase, device=device)
        filas = evaluar_conjunto(gt, det, fusion=fusion)
        salida["conjuntos"][gt["conjunto"]] = {"gt": os.path.abspath(ruta), "filas": filas}
        if verbose:
            print("  %-20s" % gt["conjunto"], end="")
            for f in filas:
                if f["luz"] == "todas":
                    print("  %s: AP50=%.3f AP=%.3f (n=%d)"
                          % (f["estrato"], f["AP50"], f["AP"], f["n_gt"]), end="")
            print()
    os.makedirs(os.path.join(dir_res, "eval"), exist_ok=True)
    with open(os.path.join(dir_res, "eval", "%s.json" % nombre), "w", encoding="utf-8") as fh:
        json.dump(salida, fh, indent=1, ensure_ascii=False)
    return salida


def escribir_resumen(dir_res):
    """Une todos los eval/*.json en resumen_ap.csv."""
    ruta = os.path.join(dir_res, "resumen_ap.csv")
    campos = ["corrida", "variante", "semilla", "conjunto", "estrato", "luz",
              "AP50", "AP", "n_gt", "n_img"]
    n = 0
    with open(ruta, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        for fe in sorted(glob.glob(os.path.join(dir_res, "eval", "*.json"))):
            with open(fe, encoding="utf-8") as fh2:
                ev = json.load(fh2)
            for conj, d in ev["conjuntos"].items():
                for f in d["filas"]:
                    w.writerow({"corrida": ev["corrida"], "variante": ev.get("variante", ""),
                                "semilla": ev.get("semilla", ""), "conjunto": conj, **f})
                    n += 1
    return ruta, n


def corridas_en(dir_runs, pesos_tipo="best"):
    """pesos_tipo: 'best' (analisis primario: seleccion por val, protocolo) o
    'last' (analisis secundario pre-registrado: epoca final, maxima
    exposicion al aumento; ver CAMBIOS_PROTOCOLO.md 2026-09-11)."""
    out = []
    for d in sorted(glob.glob(os.path.join(dir_runs, "*"))):
        best = os.path.join(d, "weights", "%s.pt" % pesos_tipo)
        reg = os.path.join(d, "registro_argos.json")
        if os.path.exists(best):
            meta = {}
            if os.path.exists(reg):
                with open(reg, encoding="utf-8") as fh:
                    r = json.load(fh)
                meta = {"variante": r.get("variante"), "semilla": r.get("semilla")}
            out.append((os.path.basename(d), best, meta))
    return out


def selftest():
    """GT y detecciones sinteticas: comprueba la logica sin inferir."""
    fallos = []

    def comp(desc, obt, esp):
        ok = obt == esp
        print("  [%s] %-52s %s" % ("ok" if ok else "FALLA", desc, obt))
        if not ok:
            fallos.append(desc)

    gt = {"conjunto": "t", "dir_imagenes": ".", "imagenes": {
        "a.jpg": {"ancho": 100, "alto": 100, "luz": "Low", "instancias": [
            {"id": "a#0", "x1": 0, "y1": 0, "x2": 10, "y2": 10, "estrato": "sin"},
            {"id": "a#1", "x1": 50, "y1": 50, "x2": 60, "y2": 60, "estrato": "severa"},
            {"id": "a#2", "x1": 80, "y1": 80, "x2": 90, "y2": 90, "estrato": "sin_anotar"},
            {"id": "a#3", "x1": 20, "y1": 80, "x2": 30, "y2": 90, "estrato": "ignorar"}]},
        "b.jpg": {"ancho": 100, "alto": 100, "luz": "Strong", "instancias": [
            {"id": "b#0", "x1": 0, "y1": 0, "x2": 10, "y2": 10, "estrato": "moderada"}]}}}
    # Detector que acierta todo salvo la severa, y dispara sobre la 'ignorar'.
    det = {"a.jpg": [[0, 0, 10, 10, .9], [80, 80, 90, 90, .8], [20, 80, 30, 90, .7]],
           "b.jpg": [[0, 0, 10, 10, .95]]}
    filas = evaluar_conjunto(gt, det, fusion=True)
    por = {(f["estrato"], f["luz"]): f for f in filas}
    comp("global: 4 GT validas (sin_anotar cuenta, ignorar no)", por[("global", "todas")]["n_gt"], 4)
    # Interpolacion COCO en 101 puntos: recall 0.75 -> 76/101 puntos con p=1.
    comp("global: AP50 = 76/101 (3 de 4, sin FP)", round(por[("global", "todas")]["AP50"], 4), round(76 / 101, 4))
    comp("estrato sin: n=1, AP50=1", (por[("sin", "todas")]["n_gt"], por[("sin", "todas")]["AP50"]), (1, 1.0))
    comp("estrato severa: n=1, AP50=0", (por[("severa", "todas")]["n_gt"], por[("severa", "todas")]["AP50"]), (1, 0.0))
    comp("fusion ocluida: n=2 (moderada+severa), AP50=51/101",
         (por[("ocluida", "todas")]["n_gt"], round(por[("ocluida", "todas")]["AP50"], 4)), (2, round(51 / 101, 4)))
    comp("por luz: Low global n=3", por[("global", "Low")]["n_gt"], 3)
    comp("por luz: Strong global AP50=1", por[("global", "Strong")]["AP50"], 1.0)
    comp("estrato ausente (ligera) no se reporta", ("ligera", "todas") in por, False)
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO: 8/8 comprobaciones.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - evaluacion estratificada")
    ap.add_argument("--corridas", help="directorio con corridas (runs/argos)")
    ap.add_argument("--pesos-tipo", choices=("best", "last"), default="best",
                    help="best = primario (protocolo); last = secundario pre-registrado")
    ap.add_argument("--pesos", help="un .pt concreto")
    ap.add_argument("--nombre", help="nombre de la corrida para --pesos")
    ap.add_argument("--variante", help="etiqueta de variante para --pesos (p. ej. V1)")
    ap.add_argument("--semilla", type=int, help="semilla para --pesos")
    ap.add_argument("--clase-coco", type=int, default=None,
                    help="filtrar clase (0=person) al evaluar pesos COCO")
    ap.add_argument("--gt", nargs="+", help="GT json (def. todos los conjuntos)")
    ap.add_argument("--dataset", default=os.path.join(RAIZ, "dataset"))
    ap.add_argument("--resultados", default=os.path.join(RAIZ, "resultados"))
    ap.add_argument("--fusion", action="store_true",
                    help="anadir el estrato fusionado moderada+severa")
    ap.add_argument("--device")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())

    rutas_gt = args.gt or conjuntos_por_defecto(args.dataset)
    if not rutas_gt:
        sys.exit("ERROR: no hay GT. Ejecutar 04 (real) y 05 prueba (sintetico).")
    print("Conjuntos: %d\n  " % len(rutas_gt) + "\n  ".join(rutas_gt))

    trabajos = []
    if args.pesos:
        meta = {k: v for k, v in (("variante", args.variante), ("semilla", args.semilla))
                if v is not None}
        trabajos.append((args.nombre or os.path.splitext(os.path.basename(args.pesos))[0],
                         args.pesos, meta))
    if args.corridas:
        trabajos += corridas_en(args.corridas, args.pesos_tipo)
    if not trabajos:
        ap.error("indicar --pesos o --corridas")
    for nombre, pesos, meta in trabajos:
        print("\n== %s  (%s)" % (nombre, pesos))
        evaluar_corrida(nombre, pesos, rutas_gt, args.resultados, args.fusion,
                        args.clase_coco, args.device, meta)
    ruta, n = escribir_resumen(args.resultados)
    print("\nResumen: %s (%d filas)" % (ruta, n))


if __name__ == "__main__":
    main()
