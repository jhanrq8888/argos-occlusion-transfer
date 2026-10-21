#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Paso 8: costo computacional (OE5) y exportacion a ONNX.

Protocolo de FPS (Seccion 1.7 / 2.4): batch 1, FP16, 640x640, 50 imagenes
de warm-up y promedio sobre 500 imagenes del split de prueba. Se reportan
dos pilas en GPU de escritorio:
    - ONNX Runtime (CUDAExecutionProvider) sobre el modelo exportado en FP16;
    - PyTorch FP16 (referencia).
Y para cada una: tiempo del forward puro (lo que compara arquitecturas) y
tiempo extremo a extremo (letterbox + forward + NMS). Ademas: parametros y
GFLOPs (thop / profiler de Ultralytics a 640).

La medicion embebida (RK3588S, RKNN) es opcional (Seccion 3.1); se deja
documentada la conversion desde el ONNX exportado en PLAN_EJECUCION.md.

Salida: resultados/costo/<corrida>.json y resultados/resumen_costo.csv;
ONNX en la carpeta weights/ de cada corrida.

Uso:
    python 10_medir_costo.py --corridas runs/argos
    python 10_medir_costo.py --pesos runs/argos/V1_s0/weights/best.pt --nombre V1_s0
    python 10_medir_costo.py --pesos yolo11s.pt --nombre coco --n 100
    python 10_medir_costo.py --selftest
"""

import argparse
import csv
import glob
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argos_lib.atencion import registrar_cbam                   # noqa: E402

RAIZ = os.path.dirname(os.path.abspath(__file__))
IMGSZ, WARMUP, N_IMG = 640, 50, 500


def imagenes_prueba(dataset, n):
    d = os.path.join(dataset, "images", "test")
    fs = sorted(f for f in os.listdir(d) if f.lower().endswith((".jpg", ".jpeg", ".png")))
    return [os.path.join(d, f) for f in fs[:n]]


def letterbox(im, tam=IMGSZ):
    """Redimensiona con relleno gris a tam x tam. Devuelve CHW float32 [0,1]."""
    import cv2
    h, w = im.shape[:2]
    r = min(tam / h, tam / w)
    nh, nw = int(round(h * r)), int(round(w * r))
    im2 = cv2.resize(im, (nw, nh), interpolation=cv2.INTER_LINEAR)
    lienzo = np.full((tam, tam, 3), 114, dtype=np.uint8)
    y0, x0 = (tam - nh) // 2, (tam - nw) // 2
    lienzo[y0:y0 + nh, x0:x0 + nw] = im2
    x = lienzo[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) / 255.0
    return np.ascontiguousarray(x[None])


def sincronizar():
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.synchronize()
    except ImportError:
        pass


def medir(func, entradas, warmup=WARMUP):
    """Ejecuta func(x) sobre las entradas; devuelve ms por imagen (media,
    desviacion) tras el warm-up."""
    for x in entradas[:warmup]:
        func(x)
    sincronizar()
    tiempos = []
    for x in entradas:
        t0 = time.perf_counter()
        func(x)
        sincronizar()
        tiempos.append((time.perf_counter() - t0) * 1000.0)
    t = np.asarray(tiempos)
    return float(t.mean()), float(t.std()), float(np.median(t))


def exportar_onnx(pesos, salida_dir=None):
    from ultralytics import YOLO
    registrar_cbam()
    import torch
    m = YOLO(pesos)
    # FP16 solo se aplica al exportar en GPU (device=0); en CPU sale FP32.
    dev = 0 if torch.cuda.is_available() else "cpu"
    ruta = m.export(format="onnx", imgsz=IMGSZ, quantize=16 if dev == 0 else None,
                    dynamic=False, simplify=True, batch=1, device=dev, verbose=False)
    return str(ruta)


def gflops_thop(modelo):
    """GFLOPs a 640x640 con thop (convencion de Ultralytics: MACs x 2)."""
    import torch
    try:
        import thop
        m = unwrap(modelo)
        im = torch.empty((1, 3, IMGSZ, IMGSZ), device=next(m.parameters()).device)
        return float(thop.profile(m, inputs=[im], verbose=False)[0]) / 1e9 * 2
    except Exception:
        return 0.0


def unwrap(m):
    return m.module if hasattr(m, "module") else m


def costo_pytorch(pesos, rutas_img):
    import torch
    from ultralytics import YOLO
    from ultralytics.utils.torch_utils import get_num_params
    from argos_lib.oclusion import leer_imagen
    registrar_cbam()
    y = YOLO(pesos)
    modelo = y.model
    n_params = get_num_params(modelo)
    gflops = gflops_thop(modelo)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    modelo = modelo.to(dev).eval()
    modelo.fuse() if hasattr(modelo, "fuse") else None
    if dev == "cuda":
        modelo = modelo.half()
    entradas = [torch.from_numpy(letterbox(leer_imagen(r))).to(dev) for r in rutas_img]
    if dev == "cuda":
        entradas = [e.half() for e in entradas]

    @torch.no_grad()
    def fwd(x):
        return modelo(x)
    ms_fwd, sd_fwd, med_fwd = medir(fwd, entradas)

    # Extremo a extremo con el predictor de Ultralytics (pre + forward + NMS).
    for r in rutas_img[:WARMUP]:
        y.predict(r, imgsz=IMGSZ, verbose=False, device=dev, quantize=16 if dev == "cuda" else None)
    t = []
    for r in rutas_img:
        t0 = time.perf_counter()
        y.predict(r, imgsz=IMGSZ, verbose=False, device=dev, quantize=16 if dev == "cuda" else None)
        t.append((time.perf_counter() - t0) * 1000.0)
    return {"backend": "pytorch_fp16" if dev == "cuda" else "pytorch_fp32_cpu",
            "dispositivo": torch.cuda.get_device_name(0) if dev == "cuda" else "cpu",
            "params": int(n_params), "gflops_640": round(float(gflops), 2),
            "ms_forward": round(ms_fwd, 3), "ms_forward_sd": round(sd_fwd, 3),
            "ms_forward_mediana": round(med_fwd, 3),
            "fps_forward": round(1000.0 / ms_fwd, 1),
            "ms_extremo_a_extremo": round(float(np.mean(t)), 3),
            "fps_extremo_a_extremo": round(1000.0 / float(np.mean(t)), 1)}


def costo_onnxruntime(ruta_onnx, rutas_img):
    try:
        import torch  # noqa: F401  carga las DLL de CUDA/cuDNN que ORT reutiliza
        import onnxruntime as ort
    except ImportError:
        return {"backend": "onnxruntime", "error": "onnxruntime no instalado"}
    from argos_lib.oclusion import leer_imagen
    provs = ort.get_available_providers()
    prov = ["CUDAExecutionProvider"] if "CUDAExecutionProvider" in provs else ["CPUExecutionProvider"]
    so = ort.SessionOptions()
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    sesion = ort.InferenceSession(ruta_onnx, so, providers=prov)
    prov = sesion.get_providers()          # el proveedor REALMENTE activo
    ent = sesion.get_inputs()[0]
    fp16 = "float16" in ent.type
    nombre = ent.name
    entradas = [letterbox(leer_imagen(r)).astype(np.float16 if fp16 else np.float32)
                for r in rutas_img]

    def fwd(x):
        return sesion.run(None, {nombre: x})
    ms, sd, med = medir(fwd, entradas)
    return {"backend": "onnxruntime_%s" % ("fp16" if fp16 else "fp32"),
            "proveedor": prov[0], "onnx": ruta_onnx,
            "ms_forward": round(ms, 3), "ms_forward_sd": round(sd, 3),
            "ms_forward_mediana": round(med, 3), "fps_forward": round(1000.0 / ms, 1)}


def medir_corrida(nombre, pesos, rutas_img, dir_res, meta=None, verbose=True):
    doc = {"corrida": nombre, "pesos": str(pesos), "imgsz": IMGSZ,
           "warmup": WARMUP, "n_imagenes": len(rutas_img)}
    if meta:
        doc.update(meta)
    doc["pytorch"] = costo_pytorch(pesos, rutas_img)
    try:
        onnx = exportar_onnx(pesos)
        doc["onnx"] = onnx
        doc["onnxruntime"] = costo_onnxruntime(onnx, rutas_img)
    except Exception as e:                     # la exportacion no debe tumbar la medicion
        doc["onnxruntime"] = {"backend": "onnxruntime", "error": str(e)}
    os.makedirs(os.path.join(dir_res, "costo"), exist_ok=True)
    with open(os.path.join(dir_res, "costo", "%s.json" % nombre), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
    if verbose:
        p, o = doc["pytorch"], doc["onnxruntime"]
        print("  %-14s params %s  GFLOPs %.1f | PyTorch FP16: %.2f ms (%.0f FPS), e2e %.0f FPS | ORT: %s"
              % (nombre, format(p["params"], ","), p["gflops_640"], p["ms_forward"],
                 p["fps_forward"], p["fps_extremo_a_extremo"],
                 ("%.2f ms (%.0f FPS, %s)" % (o["ms_forward"], o["fps_forward"], o["backend"])
                  if "error" not in o else "error: %s" % o["error"])))
    return doc


def escribir_resumen(dir_res):
    ruta = os.path.join(dir_res, "resumen_costo.csv")
    campos = ["corrida", "variante", "semilla", "params", "gflops_640",
              "pt_ms_forward", "pt_fps_forward", "pt_fps_e2e",
              "ort_backend", "ort_ms_forward", "ort_fps_forward"]
    with open(ruta, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        for f in sorted(glob.glob(os.path.join(dir_res, "costo", "*.json"))):
            with open(f, encoding="utf-8") as fh2:
                d = json.load(fh2)
            p, o = d["pytorch"], d.get("onnxruntime", {})
            w.writerow({"corrida": d["corrida"], "variante": d.get("variante", ""),
                        "semilla": d.get("semilla", ""), "params": p["params"],
                        "gflops_640": p["gflops_640"], "pt_ms_forward": p["ms_forward"],
                        "pt_fps_forward": p["fps_forward"], "pt_fps_e2e": p["fps_extremo_a_extremo"],
                        "ort_backend": o.get("backend", ""), "ort_ms_forward": o.get("ms_forward", ""),
                        "ort_fps_forward": o.get("fps_forward", "")})
    return ruta


def selftest():
    fallos = []

    def comp(desc, obt, esp):
        ok = obt == esp
        print("  [%s] %-46s %s" % ("ok" if ok else "FALLA", desc, obt))
        if not ok:
            fallos.append(desc)

    im = np.zeros((300, 500, 3), dtype=np.uint8)
    x = letterbox(im, 640)
    comp("letterbox: forma NCHW 640", x.shape, (1, 3, 640, 640))
    comp("letterbox: relleno 114/255 arriba", round(float(x[0, 0, 0, 0]), 4), round(114 / 255, 4))
    comp("letterbox: contenido negro en el centro", float(x[0, 0, 320, 320]), 0.0)
    cont = {"n": 0}

    def f(_):
        cont["n"] += 1
    ms, sd, med = medir(f, list(range(20)), warmup=5)
    comp("medir: warm-up + 20 medidas", cont["n"], 25)
    comp("medir: tiempos positivos", ms > 0 and med > 0, True)
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO: 5/5 comprobaciones.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - costo computacional")
    ap.add_argument("--corridas")
    ap.add_argument("--pesos")
    ap.add_argument("--nombre")
    ap.add_argument("--n", type=int, default=N_IMG)
    ap.add_argument("--dataset", default=os.path.join(RAIZ, "dataset"))
    ap.add_argument("--resultados", default=os.path.join(RAIZ, "resultados"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    rutas = imagenes_prueba(args.dataset, args.n)
    print("Imagenes de prueba para FPS: %d (warm-up %d)" % (len(rutas), WARMUP))
    trabajos = []
    if args.pesos:
        trabajos.append((args.nombre or os.path.splitext(os.path.basename(args.pesos))[0],
                         args.pesos, {}))
    if args.corridas:
        sys.path.insert(0, RAIZ)
        from importlib import import_module
        ev = import_module("09_evaluar_estratificado")
        trabajos += ev.corridas_en(args.corridas)
    if not trabajos:
        ap.error("indicar --pesos o --corridas")
    for nombre, pesos, meta in trabajos:
        medir_corrida(nombre, pesos, rutas, args.resultados, meta)
    print("\nResumen: %s" % escribir_resumen(args.resultados))


if __name__ == "__main__":
    main()
