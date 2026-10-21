# -*- coding: utf-8 -*-
"""
ARGOS-11 - E11 (PREREGISTRO_H14.md): oclusores pegados con ORDEN DE PROFUNDIDAD.

Las siluetas de E2/E8 se pegan siempre encima de la persona, sin mirar la escena. Aqui el recorte de un
objeto (banco de siluetas, mascara alfa de yolo11s-seg) se coloca como un objeto real que esta DELANTE de
la persona:
  1. Apoyado en el suelo por delante: su base queda entre los pies de la persona y 0,12 de su altura mas
     abajo (en una camara a la altura de las personas, lo que esta mas cerca apoya mas abajo en la imagen).
  2. Su profundidad (Depth Anything V2, profundidad inversa relativa: mayor = mas cerca) es la de la
     escena en su punto de apoyo; si no es mayor que la de la persona (mediana de la mitad inferior de su
     caja) mas un margen, no puede estar delante y se prueba otro lado; si ningun lado sirve, no se pega.
  3. Solo se compone donde la escena esta MAS LEJOS que el oclusor: lo que ya estaba delante (otra
     persona, un poste) sigue tapandolo. La escala se busca, como en las siluetas, hasta cubrir ~f de la
     caja contando solo la parte visible.
Mismo ajuste de luminancia que siluetas.pegar_silueta. Solo objetos (no personas), como la familia
generativa, de modo que no hay que etiquetar nada nuevo.
"""
import numpy as np

MARGEN = 0.02          # profundidad inversa normalizada [0,1]
BAJADA = 0.12          # hasta 0,12 de la altura de la persona por debajo de sus pies
MODELO_PROF = "depth-anything/Depth-Anything-V2-Small-hf"


class EstimadorProfundidad:
    """Depth Anything V2 Small (Hugging Face). Devuelve la profundidad inversa relativa normalizada a [0,1]
    con el tamano de la imagen (mayor = mas cerca)."""

    def __init__(self, device="cuda", modelo=MODELO_PROF):
        import torch
        from transformers import AutoImageProcessor, AutoModelForDepthEstimation
        self.torch, self.device = torch, device
        self.proc = AutoImageProcessor.from_pretrained(modelo)
        self.mod = AutoModelForDepthEstimation.from_pretrained(modelo).to(device).eval()

    def __call__(self, im_bgr):
        import cv2
        from PIL import Image
        H, W = im_bgr.shape[:2]
        x = self.proc(images=Image.fromarray(cv2.cvtColor(im_bgr, cv2.COLOR_BGR2RGB)), return_tensors="pt").to(self.device)
        with self.torch.no_grad():
            d = self.mod(**x).predicted_depth[0].float().cpu().numpy()
        d = cv2.resize(d, (W, H), interpolation=cv2.INTER_LINEAR)
        lo, hi = np.percentile(d, 1), np.percentile(d, 99)
        return np.clip((d - lo) / max(hi - lo, 1e-6), 0, 1).astype(np.float32)


def profundidad_persona(prof, caja):
    H, W = prof.shape
    x1, y1, x2, y2 = (int(round(v)) for v in caja)
    ym = (y1 + y2) // 2
    sub = prof[max(0, ym):min(H, y2), max(0, x1):min(W, x2)]
    return float(np.median(sub)) if sub.size else float("nan")


def _prof_apoyo(prof, xc, yb):
    H, W = prof.shape
    y = int(np.clip(round(yb) - 1, 0, H - 1)); x = int(np.clip(round(xc), 0, W - 1))
    return float(prof[max(0, y - 2):y + 1, max(0, x - 2):x + 3].max())


def _colocar(caja, ow, oh, lado, r, yb):
    x1, y1, x2, y2 = caja
    bw = x2 - x1
    if lado == 0:                                     # centrado, por delante
        x = x1 + (r[0] - 0.5) * 0.6 * bw + (bw - ow) / 2
    elif lado == 1:                                   # entra por la izquierda
        x = x1 - ow * 0.4 * r[1]
    else:                                             # entra por la derecha
        x = x2 - ow * (0.6 + 0.4 * r[1])
    return x, yb - oh


def _visible(a, x, y, prof, d_occ, H, W):
    """alfa recortado a la imagen y anulado donde la escena esta mas cerca que el oclusor."""
    ox, oy = int(round(x)), int(round(y))
    ah, aw = a.shape
    ix1, iy1, ix2, iy2 = max(0, ox), max(0, oy), min(W, ox + aw), min(H, oy + ah)
    if ix2 <= ix1 or iy2 <= iy1:
        return None
    sa = a[iy1 - oy:iy2 - oy, ix1 - ox:ix2 - ox].copy()
    sa[prof[iy1:iy2, ix1:ix2] >= d_occ - MARGEN] = 0
    return sa, (ix1, iy1, ix2, iy2)


def _cobertura(sa, rect, caja, H, W):
    x1, y1, x2, y2 = (int(round(v)) for v in caja)
    x1, y1, x2, y2 = max(0, x1), max(0, y1), min(W, x2), min(H, y2)
    area = max(1, (x2 - x1) * (y2 - y1))
    ix1, iy1, ix2, iy2 = rect
    a, b, c, d = max(x1, ix1), max(y1, iy1), min(x2, ix2), min(y2, iy2)
    if c <= a or d <= b:
        return 0.0
    return float((sa[b - iy1:d - iy1, a - ix1:c - ix1] > 0.5).sum()) / area


def pegar_profundidad(im, mascara, caja, bgr, alpha, rnd, f, prof, iteraciones=8):
    """Devuelve (cobertura, d_persona, d_oclusor); cobertura 0 si el oclusor no puede estar delante."""
    import cv2
    H, W = im.shape[:2]
    x1, y1, x2, y2 = caja
    bw, bh = x2 - x1, y2 - y1
    if bw < 4 or bh < 4:
        return 0.0, None, None
    dp = profundidad_persona(prof, caja)
    r = rnd.uniform(0, 1, 3)
    yb = min(float(H), y2 + r[2] * BAJADA * bh)
    rel = alpha.shape[1] / alpha.shape[0]
    lados = [int(rnd.randint(3))]
    lados += [l for l in (0, 1, 2) if l not in lados]
    for lado in lados:
        mejor = None
        lo, hi = 0.15, 4.0
        for _ in range(iteraciones + 2):
            s_ = (lo + hi) / 2
            oh = max(4, int(round(bh * s_))); ow = max(4, int(round(oh * rel)))
            a = cv2.resize(alpha, (ow, oh), interpolation=cv2.INTER_LINEAR)
            x, y = _colocar(caja, ow, oh, lado, r, yb)
            d_occ = _prof_apoyo(prof, x + ow / 2, yb)
            if not (d_occ > dp + MARGEN):
                break                                  # en este lado el oclusor no estaria delante
            v = _visible(a, x, y, prof, d_occ, H, W)
            if v is None:
                break
            cov = _cobertura(v[0], v[1], caja, H, W)
            if mejor is None or abs(cov - f) < abs(mejor[0] - f):
                mejor = (cov, ow, oh, x, y, d_occ, v)
            if abs(cov - f) < 0.03:
                break
            lo, hi = (s_, hi) if cov < f else (lo, s_)
        if mejor is not None and mejor[0] > 0:
            break
    if mejor is None or mejor[0] <= 0:
        return 0.0, dp, None
    cov, ow, oh, x, y, d_occ, (sa, (ix1, iy1, ix2, iy2)) = mejor
    ox, oy = int(round(x)), int(round(y))
    b = cv2.resize(bgr, (ow, oh), interpolation=cv2.INTER_AREA)[iy1 - oy:iy2 - oy, ix1 - ox:ix2 - ox].astype(np.float32)
    sa = sa[..., None]
    region = im[iy1:iy2, ix1:ix2].astype(np.float32)
    vis = sa[..., 0] > 0.5
    if vis.any():
        ganancia = float(np.clip((float(region[vis].mean()) + 1e-3) / (float(b[vis].mean()) + 1e-3), 0.35, 1.3))
        b = np.clip(b * ganancia, 0, 255)
    im[iy1:iy2, ix1:ix2] = (sa * b + (1 - sa) * region).astype(np.uint8)
    mascara[iy1:iy2, ix1:ix2] = np.maximum(mascara[iy1:iy2, ix1:ix2], vis.astype(np.uint8))
    return cov, dp, d_occ


def ocluir_profundidad(im, cajas, rnd, banco, prof, objetivos):
    """objetivos: [(idx, f)]. Solo objetos. Devuelve (lista de dicts por persona, mascara)."""
    H, W = im.shape[:2]
    mascara = np.zeros((H, W), np.uint8)
    res = []
    for i, f in objetivos:
        bgr, alpha = banco.tomar(rnd, "objeto")
        cov, dp, do = pegar_profundidad(im, mascara, cajas[i], bgr, alpha, rnd, f, prof)
        res.append({"idx": int(i), "f": round(float(f), 4), "cobertura": round(float(cov), 4), "ok": bool(cov > 0),
                    "d_persona": None if dp is None else round(dp, 4), "d_oclusor": None if do is None else round(do, 4)})
    return res, mascara
