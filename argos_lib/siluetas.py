# -*- coding: utf-8 -*-
"""
Iteracion 2 del Componente 2 (protocolo v2.0): oclusores con SILUETA real.

Motivacion (experimento 1): los parches rectangulares (textura/recorte/
opaco) elevan +30..+60 pp el AP sobre oclusion sintetica pero no
transfieren a oclusion real (NightOwls -3..-6 pp, CityPersons ~0): el
modelo aprende la firma "caja con parche = persona" (mas FP, mismo
recall). Los oclusores reales dominantes son otras personas y objetos con
forma; aqui se pegan recortes con MASCARA (alpha) obtenidos con un modelo
de segmentacion COCO sobre las imagenes de cada split.

Banco de siluetas (uno por split, disjuntos):
    dataset/siluetas_<split>/NNNNN.png   recorte RGBA (alpha = mascara)
    dataset/siluetas_<split>/indice.json  [{archivo, clase, w, h, area}]
  - 'persona': instancias de personas segmentadas en las imagenes del split
    (en train son imagenes de entrenamiento: no hay fuga);
  - 'objeto': coches, bicis, motos, sillas, mochilas, etc.

Pegado con cobertura objetivo f: el oclusor se ancla a un borde de la caja
(entra desde fuera, como un oclusor real), se escala por busqueda binaria
hasta que su mascara cubra f del area de la caja (+-3 %) y se compone con
alpha. La cobertura efectiva se mide sobre la mascara acumulada.
"""

import json
import os

import numpy as np

from .oclusion import escribir_imagen, leer_imagen  # noqa: F401

# Clases COCO usadas como oclusores (id: nombre).
CLASES_OBJETO = {1: "bicycle", 2: "car", 3: "motorcycle", 5: "bus", 7: "truck",
                 13: "bench", 16: "dog", 24: "backpack", 25: "umbrella",
                 26: "handbag", 28: "suitcase", 56: "chair", 58: "potted plant",
                 60: "dining table"}
CLASE_PERSONA = 0


class BancoSiluetas:
    def __init__(self, directorio):
        self.dir = directorio
        with open(os.path.join(directorio, "indice.json"), encoding="utf-8") as fh:
            d = json.load(fh)
        self.items = d["recortes"]
        self.por_clase = {"persona": [i for i, r in enumerate(self.items) if r["clase"] == "persona"],
                          "objeto": [i for i, r in enumerate(self.items) if r["clase"] == "objeto"]}
        self._cache = {}

    def __len__(self):
        return len(self.items)

    def __getstate__(self):
        d = self.__dict__.copy(); d["_cache"] = {}
        return d

    def _leer(self, k):
        if k not in self._cache:
            import cv2
            datos = np.fromfile(os.path.join(self.dir, self.items[k]["archivo"]), dtype=np.uint8)
            im = cv2.imdecode(datos, cv2.IMREAD_UNCHANGED)      # BGRA
            if len(self._cache) > 128:
                self._cache.clear()
            self._cache[k] = im
        return self._cache[k]

    def tomar(self, rnd, clase=None):
        """Devuelve (bgr, alpha01) de un recorte aleatorio; volteo horizontal
        con p=0.5."""
        idx = self.por_clase.get(clase) if clase else None
        if not idx:
            idx = list(range(len(self.items)))
        im = self._leer(int(rnd.choice(idx)))
        if rnd.rand() < 0.5:
            im = im[:, ::-1]
        return im[..., :3], im[..., 3].astype(np.float32) / 255.0

    @staticmethod
    def construir(rutas_imagenes, salida, pesos_seg="yolo11s-seg.pt", max_por_clase=800,
                  conf=0.4, min_lado=40, min_relleno=0.30, semilla=0, device=None):
        """Segmenta las imagenes y guarda recortes RGBA. Devuelve conteos."""
        import cv2
        from ultralytics import YOLO
        os.makedirs(salida, exist_ok=True)
        modelo = YOLO(pesos_seg)
        clases = [CLASE_PERSONA] + sorted(CLASES_OBJETO)
        rnd = np.random.RandomState(semilla)
        rutas = list(rutas_imagenes)
        rnd.shuffle(rutas)
        recortes, cnt = [], {"persona": 0, "objeto": 0}
        for i in range(0, len(rutas), 8):
            if cnt["persona"] >= max_por_clase and cnt["objeto"] >= max_por_clase:
                break
            lote = rutas[i:i + 8]
            res = modelo.predict(lote, conf=conf, imgsz=640, classes=clases, retina_masks=True,
                                 verbose=False, device=device)
            for ruta, r in zip(lote, res):
                if r.masks is None:
                    continue
                im = leer_imagen(ruta)
                H, W = im.shape[:2]
                masks = r.masks.data.cpu().numpy()                  # (n, H, W) en retina_masks
                for m, c, b in zip(masks, r.boxes.cls.cpu().numpy(), r.boxes.xyxy.cpu().numpy()):
                    clase = "persona" if int(c) == CLASE_PERSONA else "objeto"
                    if cnt[clase] >= max_por_clase:
                        continue
                    if m.shape != (H, W):
                        m = cv2.resize(m.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
                    x1, y1, x2, y2 = (int(round(v)) for v in b)
                    x1, y1, x2, y2 = max(0, x1), max(0, y1), min(W, x2), min(H, y2)
                    w, h = x2 - x1, y2 - y1
                    if w < min_lado or h < min_lado:
                        continue
                    sub = (m[y1:y2, x1:x2] > 0.5)
                    if sub.mean() < min_relleno:
                        continue
                    alpha = (sub.astype(np.float32) * 255).astype(np.uint8)
                    alpha = cv2.GaussianBlur(alpha, (5, 5), 0)         # borde suave
                    bgra = np.dstack([im[y1:y2, x1:x2], alpha])
                    nombre = "%05d.png" % len(recortes)
                    ok, buf = cv2.imencode(".png", bgra)
                    if not ok:
                        continue
                    buf.tofile(os.path.join(salida, nombre))
                    recortes.append({"archivo": nombre, "clase": clase,
                                     "coco": CLASES_OBJETO.get(int(c), "person"),
                                     "w": int(w), "h": int(h), "area": int(sub.sum()),
                                     "origen": os.path.basename(ruta)})
                    cnt[clase] += 1
        with open(os.path.join(salida, "indice.json"), "w", encoding="utf-8") as fh:
            json.dump({"pesos_seg": pesos_seg, "conf": conf, "n_imagenes": len(rutas),
                       "recortes": recortes, "conteo": cnt}, fh, indent=1)
        return cnt


# --- Pegado con cobertura objetivo -------------------------------------------
def _colocar(caja, ow, oh, lado, r):
    """Posicion (x, y) de un oclusor ow x oh anclado al borde `lado` de la caja.
    r: tres uniformes en [0,1] fijadas de antemano, para que la busqueda de
    escala sea monotona (misma posicion relativa en cada iteracion)."""
    x1, y1, x2, y2 = caja
    bw, bh = x2 - x1, y2 - y1
    desl = (r[0] - 0.5) * 0.6 * bw
    if lado == 0:      # desde abajo: el oclusor pisa la parte inferior
        return x1 + desl + (bw - ow) / 2, y2 - oh * (0.6 + 0.4 * r[1])
    if lado == 1:      # desde la izquierda
        return x1 - ow * 0.4 * r[1], y2 - oh * (0.9 + 0.2 * r[2])
    if lado == 2:      # desde la derecha
        return x2 - ow * (0.6 + 0.4 * r[1]), y2 - oh * (0.9 + 0.2 * r[2])
    return x1 + desl + (bw - ow) / 2, y1 - oh * 0.4 * r[1]          # desde arriba


def _cobertura(alpha, x, y, caja, H, W):
    """Fraccion del area de la caja cubierta por alpha>0.5 colocado en (x,y)."""
    x1, y1, x2, y2 = (int(round(v)) for v in caja)
    x1, y1, x2, y2 = max(0, x1), max(0, y1), min(W, x2), min(H, y2)
    area = max(1, (x2 - x1) * (y2 - y1))
    ox, oy = int(round(x)), int(round(y))
    ah, aw = alpha.shape
    ix1, iy1 = max(x1, ox), max(y1, oy)
    ix2, iy2 = min(x2, ox + aw), min(y2, oy + ah)
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0
    sub = alpha[iy1 - oy:iy2 - oy, ix1 - ox:ix2 - ox]
    return float((sub > 0.5).sum()) / area


def pegar_silueta(im, mascara, caja, bgr, alpha, rnd, f, iteraciones=6):
    """Escala el oclusor hasta cubrir ~f de la caja y lo compone. Devuelve la
    cobertura conseguida (0 si no se pudo)."""
    import cv2
    H, W = im.shape[:2]
    x1, y1, x2, y2 = caja
    bw, bh = x2 - x1, y2 - y1
    if bw < 4 or bh < 4:
        return 0.0
    lado = int(rnd.randint(4))
    r = rnd.uniform(0, 1, 3)
    rel = alpha.shape[1] / alpha.shape[0]                # aspecto del oclusor

    def buscar(lado, r, lo=0.15, hi=4.0):
        mejor = None
        for _ in range(iteraciones + 2):
            s_ = (lo + hi) / 2
            oh = max(4, int(round(bh * s_)))
            ow = max(4, int(round(oh * rel)))
            a = cv2.resize(alpha, (ow, oh), interpolation=cv2.INTER_LINEAR)
            x, y = _colocar(caja, ow, oh, lado, r)
            cov = _cobertura(a, x, y, caja, H, W)
            if mejor is None or abs(cov - f) < abs(mejor[0] - f):
                mejor = (cov, ow, oh, x, y, a)
            if abs(cov - f) < 0.03:
                break
            if cov < f:
                lo = s_
            else:
                hi = s_
        return mejor

    mejor = buscar(lado, r)
    if abs(mejor[0] - f) > 0.05:
        # Coberturas altas: el lado elegido puede no bastar (siluetas con
        # huecos); segundo intento centrado desde abajo, que siempre alcanza.
        mejor = buscar(0, np.array([0.5, 1.0, 0.5]))
    cov, ow, oh, x, y, a = mejor
    if cov <= 0:
        return 0.0, None
    b = cv2.resize(bgr, (ow, oh), interpolation=cv2.INTER_AREA)
    ox, oy = int(round(x)), int(round(y))
    ix1, iy1 = max(0, ox), max(0, oy)
    ix2, iy2 = min(W, ox + ow), min(H, oy + oh)
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0, None
    sa = a[iy1 - oy:iy2 - oy, ix1 - ox:ix2 - ox][..., None]
    sb = b[iy1 - oy:iy2 - oy, ix1 - ox:ix2 - ox].astype(np.float32)
    region = im[iy1:iy2, ix1:ix2].astype(np.float32)
    # Ajuste de luminancia: el recorte se escala hacia el brillo medio de la
    # zona que tapa (escenas de baja iluminacion), con limites para no
    # aplastarlo; evita oclusores "diurnos" sobre fondos nocturnos.
    vis = sa[..., 0] > 0.5
    if vis.any():
        l_rec = float(sb[vis].mean()) + 1e-3
        l_reg = float(region[vis].mean()) + 1e-3
        ganancia = float(np.clip(l_reg / l_rec, 0.35, 1.3))
        sb = np.clip(sb * ganancia, 0, 255)
    im[iy1:iy2, ix1:ix2] = (sa * sb + (1 - sa) * region).astype(np.uint8)
    visible = sa[..., 0] > 0.5
    mascara[iy1:iy2, ix1:ix2] = np.maximum(mascara[iy1:iy2, ix1:ix2], visible.astype(np.uint8))
    # Caja del oclusor tal como queda en la imagen (para etiquetarlo si es persona).
    ys, xs = np.where(visible)
    if len(xs) == 0:
        return 0.0, None
    caja_ocl = (float(ix1 + xs.min()), float(iy1 + ys.min()), float(ix1 + xs.max() + 1), float(iy1 + ys.max() + 1))
    return cov, caja_ocl


def ocluir_siluetas(im, cajas, rnd, banco, p=0.5, n_min=1, n_max=3, rango_f=(0.30, 0.85),
                    prob_persona=0.5, todas=False, f_fijo=None, min_lado_caja=8):
    """Aumento v2 (entrenamiento) o generacion v2 (val/prueba, con todas=True).
    Devuelve (lista de (idx, clase, f_nominal, f_conseguida), mascara,
    cajas_personas_pegadas): las personas pegadas son personas reales
    visibles y deben ETIQUETARSE (train/val) o marcarse como ignore (test);
    de lo contrario el modelo aprenderia a no detectarlas."""
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
        f = float(rnd.uniform(*rango_f)) if f_fijo is None else float(f_fijo(rnd))
        clase = "persona" if rnd.rand() < prob_persona else "objeto"
        bgr, alpha = banco.tomar(rnd, clase)
        cov, caja_ocl = pegar_silueta(im, mascara, cajas[i], bgr, alpha, rnd, f)
        if cov > 0:
            aplicados.append((int(i), clase, f, cov))
            if clase == "persona" and caja_ocl is not None:
                pegadas.append(caja_ocl)
    return aplicados, mascara, pegadas


class OclusionSiluetas:
    """Transform de Ultralytics (v2). Misma interfaz que OclusionEntrenamiento."""

    def __init__(self, dir_banco, p=0.5, n_min=1, n_max=3, rango_f=(0.30, 0.85), prob_persona=0.5):
        self.dir_banco = dir_banco
        self.p, self.n_min, self.n_max = p, n_min, n_max
        self.rango_f, self.prob_persona = tuple(rango_f), prob_persona
        self._banco = None

    @property
    def banco(self):
        if self._banco is None:
            self._banco = BancoSiluetas(self.dir_banco)
        return self._banco

    def __getstate__(self):
        d = self.__dict__.copy(); d["_banco"] = None
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
        _, _, pegadas = ocluir_siluetas(im, cajas, np.random, self.banco, self.p, self.n_min,
                                        self.n_max, self.rango_f, self.prob_persona)
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
