# -*- coding: utf-8 -*-
"""
H10 (PREREGISTRO_H10.md): oclusion con la GEOMETRIA de la oclusion real.

Las tres familias probadas (parches, siluetas, generativa) cambian la
apariencia del oclusor, pero no su geometria: el oclusor entra por un lado
de la caja elegido al azar (25 % cada uno) y cubre una fraccion f ~ U[0,30;
0,85]. La oclusion real tiene otra distribucion de posicion, forma y
extension. Esta familia toma esa geometria de anotaciones reales y deja la
apariencia como en la iteracion 2 (mismos recortes con mascara del banco
siluetas_train, misma probabilidad persona/objeto, mismo ajuste de luminancia).

Patrones (de CityPersons TRAIN; nunca de CityPersons val, que es fuente de prueba):
    cada peaton anotado (clase 1, alto >= 50 px) tiene caja completa y caja
    visible. El patron es la caja visible en coordenadas relativas a la caja
    completa (vx1, vy1, vx2, vy2 en [0, 1]); la region oculta es
    H = caja completa menos caja visible, y su cobertura c = 1 - area(visible) / area(caja).
    Se guardan los patrones con c en el rango de cobertura de cada uso.

Colocacion: dado un patron y un recorte, se busca por rejilla (escala x
desplazamiento, sobre una version reducida de la caja) la colocacion cuya
mascara dentro de la caja tenga el mayor IoU con H; el recorte entra desde
fuera por los lados de la caja que toca H, como un oclusor real. El recorte
conserva su silueta natural (no se recorta a la forma rectangular de H), asi
que la cobertura efectiva se mide sobre la mascara, igual que en v2.
"""

import json

import numpy as np

from .siluetas import BancoSiluetas

LADO_RED = 48                          # lado mayor de la rejilla reducida de la caja
ESCALAS = (0.3, 0.4, 0.5, 0.6, 0.7, 0.85, 1.0, 1.2, 1.45, 1.75)   # relativas al lado mayor de R
DESPL = (-0.5, -0.25, 0.0, 0.25, 0.5)  # desplazamientos relativos al tamano del recorte
MAX_TAPA_VISIBLE = 0.35                # como mucho 35 % de la parte que el patron deja visible (calibrado, PREREGISTRO_H10.md)
MAX_ALTO, MAX_ANCHO = 1.5, 2.5         # tamano maximo del recorte, relativo a la caja de la persona


# --- Patrones -----------------------------------------------------------------
def patron_de_cajas(full, vis):
    """full, vis: (x, y, w, h). Devuelve (vx1, vy1, vx2, vy2, cobertura) relativo a
    la caja completa, o None si la anotacion no es usable."""
    x, y, w, h = map(float, full)
    xv, yv, wv, hv = map(float, vis)
    if w <= 1 or h <= 1:
        return None
    a1, b1 = max(x, xv), max(y, yv)
    a2, b2 = min(x + w, xv + wv), min(y + h, yv + hv)
    if a2 <= a1 or b2 <= b1:
        return None
    p = ((a1 - x) / w, (b1 - y) / h, (a2 - x) / w, (b2 - y) / h)
    c = 1.0 - (p[2] - p[0]) * (p[3] - p[1])
    return tuple(round(v, 4) for v in p) + (round(c, 4),)


def extraer_patrones(registros, nombres=None, min_alto=50, rango=(0.30, 0.85)):
    """registros: salida de 20_.leer_mat (dicts con 'nombre' y 'bbs' de 10 columnas:
    clase, x, y, w, h, id, xv, yv, wv, hv). nombres: conjunto de imagenes a usar."""
    out = []
    for r in registros:
        if nombres is not None and r["nombre"] not in nombres:
            continue
        for f in r["bbs"]:
            if int(f[0]) != 1 or f[4] < min_alto:
                continue
            p = patron_de_cajas(f[1:5], f[6:10])
            if p and rango[0] <= p[4] <= rango[1]:
                out.append(p)
    return out


def lados_de(p, tol=0.02):
    """Lados de la caja que toca la region oculta: abajo, izquierda, derecha, arriba."""
    vx1, vy1, vx2, vy2 = p[:4]
    return {"abajo": vy2 < 1 - tol, "izquierda": vx1 > tol, "derecha": vx2 < 1 - tol, "arriba": vy1 > tol}


class BancoPatrones:
    def __init__(self, ruta):
        d = json.load(open(ruta, encoding="utf-8"))
        self.patrones = [tuple(p) for p in d["patrones"]]
        self.ruta = ruta

    def __len__(self):
        return len(self.patrones)

    def tomar(self, rnd, rango=None):
        if rango is None:
            return self.patrones[int(rnd.randint(len(self.patrones)))]
        cand = [p for p in self.patrones if rango[0] <= p[4] <= rango[1]]
        return cand[int(rnd.randint(len(cand)))] if cand else None


# --- Colocacion -----------------------------------------------------------------
def mascara_oculta(p, gw, gh):
    """Region oculta H en una rejilla gw x gh de la caja."""
    m = np.ones((gh, gw), dtype=bool)
    x1, y1 = int(round(p[0] * gw)), int(round(p[1] * gh))
    x2, y2 = int(round(p[2] * gw)), int(round(p[3] * gh))
    m[max(0, y1):min(gh, y2), max(0, x1):min(gw, x2)] = False
    return m


def _recorte_en_caja(a, ox, oy, gw, gh):
    """Mascara booleana (gh, gw) de un alpha colocado con esquina (ox, oy) en la rejilla."""
    m = np.zeros((gh, gw), dtype=bool)
    ah, aw = a.shape
    ix1, iy1, ix2, iy2 = max(0, ox), max(0, oy), min(gw, ox + aw), min(gh, oy + ah)
    if ix2 > ix1 and iy2 > iy1:
        m[iy1:iy2, ix1:ix2] = a[iy1 - oy:iy2 - oy, ix1 - ox:ix2 - ox] > 0.5
    return m


def buscar_colocacion(alpha, p, bw, bh):
    """Mejor colocacion del recorte para cubrir H. Devuelve (escala_px, ox_rel, oy_rel, iou):
    alto del recorte en pixeles de la caja real y esquina relativa a (x1, y1) de la caja."""
    import cv2
    k = LADO_RED / max(bw, bh)
    gw, gh = max(4, int(round(bw * k))), max(4, int(round(bh * k)))
    H = mascara_oculta(p, gw, gh)
    if not H.any():
        return None
    ys, xs = np.where(H)
    rx1, ry1, rx2, ry2 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1      # caja de H
    cx, cy = (rx1 + rx2) / 2, (ry1 + ry2) / 2
    lados = lados_de(p)
    # Hacia fuera: el recorte se desplaza hacia los lados de la caja que toca H.
    ux = (1 if lados["derecha"] else 0) - (1 if lados["izquierda"] else 0)
    uy = (1 if lados["abajo"] else 0) - (1 if lados["arriba"] else 0)
    rel = alpha.shape[1] / alpha.shape[0]
    lado_R = max(rx2 - rx1, ry2 - ry1)
    V = ~H
    n_v = max(1.0, float(V.sum()))
    n_h = max(1.0, float(H.sum()))
    mejor = None
    for s in ESCALAS:
        oh = max(2, int(round(lado_R * s)))
        ow = max(2, int(round(oh * rel)))
        if oh > MAX_ALTO * gh or ow > MAX_ANCHO * gw:
            continue
        a = cv2.resize(alpha, (ow, oh), interpolation=cv2.INTER_AREA)
        for dx in DESPL:
            for dy in DESPL:
                ox = int(round(cx - ow / 2 + (dx + 0.3 * ux) * ow))
                oy = int(round(cy - oh / 2 + (dy + 0.3 * uy) * oh))
                M = _recorte_en_caja(a, ox, oy, gw, gh)
                if float((M & V).sum()) / n_v > MAX_TAPA_VISIBLE:
                    continue                      # taparia la parte que en la realidad se ve
                inter = float((M & H).sum())
                union = float((M | H).sum())
                iou = inter / union if union else 0.0
                # Criterio: tapar la mayor parte de la region oculta (desempate por IoU), con la
                # restriccion de arriba sobre la parte visible.
                cubre = inter / n_h
                if mejor is None or (cubre, iou) > (mejor[4], mejor[3]):
                    mejor = (oh / k, ox / k, oy / k, iou, cubre)
    return None if mejor is None else mejor[:4]


def pegar_geometria(im, mascara, caja, bgr, alpha, patron):
    """Compone el recorte con la colocacion de buscar_colocacion. Mismo ajuste de
    luminancia y misma composicion alpha que siluetas.pegar_silueta. Devuelve
    (cobertura, caja_ocl, iou_con_H)."""
    import cv2
    H_, W_ = im.shape[:2]
    x1, y1, x2, y2 = caja
    bw, bh = x2 - x1, y2 - y1
    if bw < 4 or bh < 4:
        return 0.0, None, 0.0
    col = buscar_colocacion(alpha, patron, bw, bh)
    if col is None or col[3] <= 0:
        return 0.0, None, 0.0
    alto, oxr, oyr, iou = col
    oh = max(4, int(round(alto)))
    ow = max(4, int(round(oh * alpha.shape[1] / alpha.shape[0])))
    a = cv2.resize(alpha, (ow, oh), interpolation=cv2.INTER_LINEAR)
    b = cv2.resize(bgr, (ow, oh), interpolation=cv2.INTER_AREA)
    ox, oy = int(round(x1 + oxr)), int(round(y1 + oyr))
    ix1, iy1, ix2, iy2 = max(0, ox), max(0, oy), min(W_, ox + ow), min(H_, oy + oh)
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0, None, 0.0
    sa = a[iy1 - oy:iy2 - oy, ix1 - ox:ix2 - ox][..., None]
    sb = b[iy1 - oy:iy2 - oy, ix1 - ox:ix2 - ox].astype(np.float32)
    region = im[iy1:iy2, ix1:ix2].astype(np.float32)
    vis = sa[..., 0] > 0.5
    if vis.any():
        ganancia = float(np.clip((float(region[vis].mean()) + 1e-3) / (float(sb[vis].mean()) + 1e-3), 0.35, 1.3))
        sb = np.clip(sb * ganancia, 0, 255)
    im[iy1:iy2, ix1:ix2] = (sa * sb + (1 - sa) * region).astype(np.uint8)
    mascara[iy1:iy2, ix1:ix2] = np.maximum(mascara[iy1:iy2, ix1:ix2], vis.astype(np.uint8))
    # cobertura efectiva de esta caja
    bx1, by1, bx2, by2 = (int(round(v)) for v in caja)
    bx1, by1, bx2, by2 = max(0, bx1), max(0, by1), min(W_, bx2), min(H_, by2)
    area = max(1, (bx2 - bx1) * (by2 - by1))
    cov = float(mascara[by1:by2, bx1:bx2].sum()) / area
    ys, xs = np.where(vis)
    if len(xs) == 0:
        return 0.0, None, iou
    caja_ocl = (float(ix1 + xs.min()), float(iy1 + ys.min()), float(ix1 + xs.max() + 1), float(iy1 + ys.max() + 1))
    return cov, caja_ocl, iou


def ocluir_geometria(im, cajas, rnd, banco, patrones, p=0.5, n_min=1, n_max=3, rango_c=(0.40, 0.95),
                     prob_persona=0.5, todas=False, min_lado_caja=8):
    """Analogo a siluetas.ocluir_siluetas, con la geometria tomada de un patron real.
    Devuelve (aplicados, mascara, cajas_personas_pegadas)."""
    H, W = im.shape[:2]
    mascara = np.zeros((H, W), dtype=np.uint8)
    aplicados, pegadas = [], []
    if not len(cajas) or (not todas and rnd.rand() >= p):
        return aplicados, mascara, pegadas
    validas = [i for i, c in enumerate(cajas) if c[2] - c[0] >= min_lado_caja and c[3] - c[1] >= min_lado_caja]
    if not validas:
        return aplicados, mascara, pegadas
    if todas:
        elegidas = validas
    else:
        n = int(min(len(validas), rnd.randint(n_min, n_max + 1)))
        elegidas = rnd.choice(validas, size=n, replace=False)
    for i in elegidas:
        patron = patrones.tomar(rnd, rango_c)
        clase = "persona" if rnd.rand() < prob_persona else "objeto"
        bgr, alpha = banco.tomar(rnd, clase)
        if patron is None:
            continue
        cov, caja_ocl, iou = pegar_geometria(im, mascara, cajas[i], bgr, alpha, patron)
        if cov > 0:
            aplicados.append((int(i), clase, float(patron[4]), cov, iou))
            if clase == "persona" and caja_ocl is not None:
                pegadas.append(caja_ocl)
    return aplicados, mascara, pegadas


class OclusionGeometria:
    """Transform de Ultralytics (H10). Misma interfaz que OclusionSiluetas."""

    def __init__(self, dir_banco, archivo_patrones, p=0.5, n_min=1, n_max=3, rango_c=(0.40, 0.95), prob_persona=0.5):
        self.dir_banco, self.archivo_patrones = dir_banco, archivo_patrones
        self.p, self.n_min, self.n_max = p, n_min, n_max
        self.rango_c, self.prob_persona = tuple(rango_c), prob_persona
        self._banco = self._patrones = None

    @property
    def banco(self):
        if self._banco is None:
            self._banco = BancoSiluetas(self.dir_banco)
        return self._banco

    @property
    def patrones(self):
        if self._patrones is None:
            self._patrones = BancoPatrones(self.archivo_patrones)
        return self._patrones

    def __getstate__(self):
        d = self.__dict__.copy(); d["_banco"] = None; d["_patrones"] = None
        return d

    def __call__(self, labels):
        im = labels["img"]
        inst = labels.get("instances")
        if inst is None or len(inst) == 0:
            return labels
        formato, normalizado = inst._bboxes.format, inst.normalized
        inst.convert_bbox("xyxy")
        H, W = im.shape[:2]
        if normalizado:
            inst.denormalize(W, H)
        cajas = [tuple(map(float, b)) for b in inst.bboxes]
        if not im.flags.writeable:
            im = np.ascontiguousarray(im)
        _, _, pegadas = ocluir_geometria(im, cajas, np.random, self.banco, self.patrones, self.p, self.n_min,
                                         self.n_max, self.rango_c, self.prob_persona)
        labels["img"] = im
        if pegadas:
            from ultralytics.utils.instance import Instances
            nuevas = Instances(np.asarray(pegadas, dtype=np.float32), bbox_format="xyxy", normalized=False)
            inst = Instances.concatenate([inst, nuevas], axis=0)
            labels["cls"] = np.concatenate([labels["cls"], np.zeros((len(pegadas), 1), dtype=labels["cls"].dtype)], 0)
            labels["instances"] = inst
        if normalizado:
            inst.normalize(W, H)
        inst.convert_bbox(formato)
        return labels
