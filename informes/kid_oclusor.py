#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - KID sobre la region del oclusor (revision del short paper, 20/10/2026; analisis posterior declarado, no decide
ninguna hipotesis). H13 midio el realismo sobre el recorte completo de la persona; aqui se compara solo la parte ocluida:
- real: la parte de la caja completa que queda fuera de la caja visible anotada (CityPersons, anno_val.mat), tomando la
  franja mayor (abajo, arriba, izquierda o derecha) dentro del recorte de 224 px de H13;
- cada familia sintetica: el rectangulo que contiene los pixeles que cambian respecto de la MISMA persona sin ocluir
  (los recortes de dataset/realismo/<familia>/ y base/ estan emparejados por indice), dentro de la caja de la persona;
- referencia: la misma region del recorte sin ocluir (persona y fondo, sin oclusor).
Cada region se recorta, se lleva a 224 px y se describe con DINOv2-base (CLS), el mismo extractor de H13; KID con el
estimador de 31_realismo.kid (50 subconjuntos de 100). Salida: informes/analisis_final/kid_oclusor.json
Uso: python informes/kid_oclusor.py
"""
import importlib.util
import json
import os
import sys

import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
_sp = importlib.util.spec_from_file_location("r31", os.path.join(RAIZ, "31_realismo.py"))
R31 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(R31)
SAL = os.path.join(RAIZ, "dataset", "realismo")
FAMILIAS = ["parches", "siluetas", "geometria", "generativa"]
UMBRAL_DIF, MIN_LADO = 30, 12


def transformacion(caja, H, W):
    """Parametros del recorte de 31_realismo.recorte: origen, desplazamiento del lienzo y escala a 224."""
    x1, y1, x2, y2 = caja
    w, h = x2 - x1, y2 - y1
    a, b = int(max(0, x1 - R31.AMPLIA * w)), int(max(0, y1 - R31.AMPLIA * h))
    c, d = int(min(W, x2 + R31.AMPLIA * w)), int(min(H, y2 + R31.AMPLIA * h))
    s = max(d - b, c - a)
    oy, ox = (s - (d - b)) // 2, (s - (c - a)) // 2
    k = R31.TAM / s
    return lambda X, Y: ((X - a + ox) * k, (Y - b + oy) * k)


def visibles_cp():
    from scipy.io import loadmat
    m = loadmat(os.path.join(RAIZ, "externos", "citypersons", "anno_val.mat"))["anno_val_aligned"][0]
    out = {}
    for e in m:
        nombre = str(e[0][0][1][0])
        out[nombre] = e[0][0][2]                     # [clase, x, y, w, h, id, xv, yv, wv, hv]
    return out


def franja_real(caja, vis, t):
    """Mayor franja de la caja completa fuera de la caja visible, en coordenadas del recorte."""
    x1, y1, x2, y2 = caja
    vx1, vy1, vx2, vy2 = max(x1, vis[0]), max(y1, vis[1]), min(x2, vis[2]), min(y2, vis[3])
    cand = [(x1, vy2, x2, y2), (x1, y1, x2, vy1), (x1, y1, vx1, y2), (vx2, y1, x2, y2)]
    cand = [r for r in cand if r[2] - r[0] > 1 and r[3] - r[1] > 1]
    if not cand:
        return None
    r = max(cand, key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))
    (a, b), (c, d) = t(r[0], r[1]), t(r[2], r[3])
    return int(a), int(b), int(np.ceil(c)), int(np.ceil(d))


def main():
    import cv2
    import torch
    from PIL import Image
    from transformers import AutoImageProcessor, AutoModel
    from argos_lib.gt import cargar_gt
    meta = json.load(open(os.path.join(SAL, "indice.json"), encoding="utf-8"))
    gt = cargar_gt(R31.GT_CP)
    dimg = gt["dir_imagenes"]
    vis = visibles_cp()
    parches = {c: [] for c in ["real", "base"] + FAMILIAS}
    descartes = {c: 0 for c in parches}
    # real
    for m in meta["real"]:
        o = gt["imagenes"][m["rel"]]["instancias"][m["idx"]]
        caja = (o["x1"], o["y1"], o["x2"], o["y2"])
        bbs = vis.get(os.path.basename(m["rel"]))
        im = cv2.imread(os.path.join(SAL, "real", "%03d.png" % m["k"]))
        H, W = cv2.imread(os.path.join(dimg, m["rel"])).shape[:2]
        fila = None if bbs is None else min(bbs, key=lambda r: abs(r[1] - caja[0]) + abs(r[2] - caja[1]) + abs(r[1] + r[3] - caja[2]) + abs(r[2] + r[4] - caja[3]))
        rect = None if fila is None else franja_real(caja, (fila[6], fila[7], fila[6] + fila[8], fila[7] + fila[9]), transformacion(caja, H, W))
        if rect is None or rect[2] - rect[0] < MIN_LADO or rect[3] - rect[1] < MIN_LADO:
            descartes["real"] += 1
            continue
        parches["real"].append(im[max(0, rect[1]):rect[3], max(0, rect[0]):rect[2]])
    # familias (region que cambia respecto de la misma persona sin ocluir) y la misma region sin oclusor
    for k, m in enumerate(meta["base"]):
        o = gt["imagenes"][m["rel"]]["instancias"][m["idx"]]
        caja = (o["x1"], o["y1"], o["x2"], o["y2"])
        H, W = cv2.imread(os.path.join(dimg, m["rel"])).shape[:2]
        t = transformacion(caja, H, W)
        (a, b), (c, d) = t(caja[0], caja[1]), t(caja[2], caja[3])
        base = cv2.imread(os.path.join(SAL, "base", "%03d.png" % k))
        for f in FAMILIAS:
            im = cv2.imread(os.path.join(SAL, f, "%03d.png" % k))
            dif = (np.abs(im.astype(int) - base.astype(int)).max(axis=2) > UMBRAL_DIF)
            msk = np.zeros_like(dif); msk[int(b):int(np.ceil(d)), int(a):int(np.ceil(c))] = True
            ys, xs = np.nonzero(dif & msk)
            if len(xs) < MIN_LADO * MIN_LADO:
                descartes[f] += 1
                continue
            r = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
            if r[2] - r[0] < MIN_LADO or r[3] - r[1] < MIN_LADO:
                descartes[f] += 1
                continue
            parches[f].append(im[r[1]:r[3], r[0]:r[2]])
            if f == "parches":
                parches["base"].append(base[r[1]:r[3], r[0]:r[2]])
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    proc, mod = AutoImageProcessor.from_pretrained("facebook/dinov2-base"), AutoModel.from_pretrained("facebook/dinov2-base").to(dev).eval()
    F = {}
    for c, lista in parches.items():
        vec = []
        for i in range(0, len(lista), 32):
            ims = [Image.fromarray(cv2.cvtColor(cv2.resize(x, (224, 224)), cv2.COLOR_BGR2RGB)) for x in lista[i:i + 32]]
            with torch.no_grad():
                vec.append(mod(**proc(images=ims, return_tensors="pt").to(dev)).pooler_output.float().cpu().numpy())
        F[c] = np.concatenate(vec)
    res = {"n": {c: len(v) for c, v in parches.items()}, "descartes": descartes, "kid_frente_a_oclusor_real": {}}
    for c in ["base"] + FAMILIAS:
        m_, lo, hi = R31.kid(F["real"], F[c])
        res["kid_frente_a_oclusor_real"][c] = {"kid": round(m_, 4), "IC95": [round(lo, 4), round(hi, 4)]}
    # escala: dos mitades al azar de los propios oclusores reales (piso de ruido del estimador)
    idx = np.random.RandomState(0).permutation(len(F["real"]))
    m_, lo, hi = R31.kid(F["real"][idx[:200]], F["real"][idx[200:]])
    res["kid_entre_mitades_reales"] = {"kid": round(m_, 4), "IC95": [round(lo, 4), round(hi, 4)]}
    json.dump(res, open(os.path.join(RAIZ, "informes", "analisis_final", "kid_oclusor.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
