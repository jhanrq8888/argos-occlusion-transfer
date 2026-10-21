# -*- coding: utf-8 -*-
"""
Oclusion sintetica: dos generadores deliberadamente distintos (Seccion 2.3.3).

                     ENTRENAMIENTO (V3, V4)          PRUEBA (Fuente 2a)
  forma del parche   rectangulo interior flotante    banda anclada a un borde
                     (posicion aleatoria dentro de   de la caja (arriba/abajo/
                     la caja)                        izquierda/derecha)
  cobertura f        U[0.30, 0.85] por parche        por estrato: ligera
                                                     U[.10,.30), moderada
                                                     U[.30,.70), severa
                                                     U[.70,1.00]
  seleccion          p=0.5 por imagen; 1-3 personas  todas las instancias
  banco de recortes  objetos no-persona de imagenes  objetos no-persona de
                     SIN personas del split train    imagenes SIN personas del
                                                     split test (nunca vistas
                                                     en entrenamiento)
  textura de fondo   region de la MISMA imagen       region de una imagen del
                     que no solape personas          banco (otra imagen)

Tipos de parche (se reportan desagregados): 'textura', 'recorte', 'opaco'.
Las anotaciones originales no se modifican; la cobertura efectiva (union de
parches sobre la caja) se mide y se guarda por instancia.
"""

import json
import os

import numpy as np

TIPOS = ("textura", "recorte", "opaco")
PROB_TIPO_ENTRENAMIENTO = {"textura": 0.4, "recorte": 0.5, "opaco": 0.1}
RANGO_F_ENTRENAMIENTO = (0.30, 0.85)
RANGO_F_PRUEBA = {"ligera": (0.10, 0.30), "moderada": (0.30, 0.70),
                  "severa": (0.70, 1.00)}
CLASES_EXDARK = ["Bicycle", "Boat", "Bottle", "Bus", "Car", "Cat", "Chair",
                 "Cup", "Dog", "Motorbike", "People", "Table"]
SPLIT = {1: "train", 2: "val", 3: "test"}
MIN_LADO_PARCHE = 2      # px; por debajo no se dibuja


# --- E/S de imagenes (rutas con caracteres no ASCII en Windows) --------------
def leer_imagen(ruta):
    import cv2
    datos = np.fromfile(ruta, dtype=np.uint8)
    im = cv2.imdecode(datos, cv2.IMREAD_COLOR)
    if im is None:
        raise IOError("no se pudo leer %s" % ruta)
    return im


def escribir_imagen(ruta, im, calidad=95):
    import cv2
    ext = os.path.splitext(ruta)[1].lower() or ".jpg"
    if ext in (".jpg", ".jpeg"):
        ok, buf = cv2.imencode(".jpg", im, [cv2.IMWRITE_JPEG_QUALITY, calidad])
    else:
        ok, buf = cv2.imencode(".png", im)
    if not ok:
        raise IOError("no se pudo codificar %s" % ruta)
    buf.tofile(ruta)


def redimensionar(im, w, h):
    import cv2
    return cv2.resize(im, (max(1, int(w)), max(1, int(h))),
                      interpolation=cv2.INTER_AREA)


# --- Banco de recortes ------------------------------------------------------
class BancoRecortes:
    """Recortes de objetos NO persona tomados de imagenes de ExDark que no
    contienen personas (excluidas de ExDark-People, nunca entrenan). Se
    construye una vez por split y se guarda como JSON; los recortes se leen
    bajo demanda, asi que el objeto es ligero y picklable (workers)."""

    def __init__(self, ruta_json):
        with open(ruta_json, encoding="utf-8") as fh:
            d = json.load(fh)
        self.split = d["split"]
        self.raiz = d["raiz"]
        self.items = d["recortes"]
        self._cache = {}

    def __len__(self):
        return len(self.items)

    @staticmethod
    def construir(raiz, split, ruta_json, max_recortes=600, min_lado=24,
                  semilla=0):
        """Explora ExDark_Annno e imageclasslist.txt y guarda el listado."""
        lista = os.path.join(raiz, "imageclasslist.txt")
        dir_ann = os.path.join(raiz, "ExDark_Annno")
        dir_img = os.path.join(raiz, "ExDark")
        indice = {}
        for clase in os.listdir(dir_img):
            d = os.path.join(dir_img, clase)
            if os.path.isdir(d):
                for f in os.listdir(d):
                    indice[f.lower()] = os.path.join(clase, f)
        candidatos = []
        with open(lista, encoding="utf-8", errors="replace") as fh:
            for linea in fh:
                c = linea.split()
                if len(c) < 5 or c[0].lower().startswith("name"):
                    continue
                try:
                    clase_i, split_i = int(c[1]), int(c[4])
                except ValueError:
                    continue
                if SPLIT.get(split_i) != split:
                    continue
                rel = indice.get(c[0].lower())
                if rel is None:
                    continue
                ann = os.path.join(dir_ann, CLASES_EXDARK[clase_i - 1], c[0] + ".txt")
                if not os.path.exists(ann):
                    continue
                cajas, hay_persona = [], False
                with open(ann, encoding="utf-8", errors="replace") as fa:
                    for l in fa:
                        p = l.split()
                        if len(p) < 5 or p[0].startswith("%"):
                            continue
                        if p[0].lower() == "people":
                            hay_persona = True
                            break
                        try:
                            x, y, w, h = (float(v) for v in p[1:5])
                        except ValueError:
                            continue
                        if w >= min_lado and h >= min_lado:
                            cajas.append({"clase": p[0], "imagen": rel,
                                          "l": x, "t": y, "w": w, "h": h})
                if not hay_persona:
                    candidatos.extend(cajas)
        rnd = np.random.RandomState(semilla)
        rnd.shuffle(candidatos)
        sel = candidatos[:max_recortes]
        with open(ruta_json, "w", encoding="utf-8") as fh:
            json.dump({"split": split, "raiz": os.path.abspath(raiz),
                       "n_candidatos": len(candidatos), "recortes": sel},
                      fh, indent=1)
        return len(sel), len(candidatos)

    def _leer(self, k):
        if k in self._cache:
            return self._cache[k]
        it = self.items[k]
        im = leer_imagen(os.path.join(self.raiz, "ExDark", it["imagen"]))
        H, W = im.shape[:2]
        x1, y1 = int(max(0, it["l"])), int(max(0, it["t"]))
        x2, y2 = int(min(W, it["l"] + it["w"])), int(min(H, it["t"] + it["h"]))
        rec = im[y1:y2, x1:x2].copy()
        if len(self._cache) > 64:
            self._cache.clear()
        self._cache[k] = (rec, im)
        return rec, im

    def recorte(self, rnd, w, h):
        rec, _ = self._leer(int(rnd.randint(len(self.items))))
        if rnd.rand() < 0.5:
            rec = rec[:, ::-1]
        return redimensionar(rec, w, h)

    def textura(self, rnd, w, h):
        """Region aleatoria de una imagen del banco (no del objeto)."""
        _, im = self._leer(int(rnd.randint(len(self.items))))
        H, W = im.shape[:2]
        rw, rh = max(2, min(W, int(w))), max(2, min(H, int(h)))
        x = int(rnd.randint(0, W - rw + 1)); y = int(rnd.randint(0, H - rh + 1))
        return redimensionar(im[y:y + rh, x:x + rw], w, h)


# --- Geometria de parches ---------------------------------------------------
def parche_interior(rnd, caja, f):
    """ENTRENAMIENTO: rectangulo de area f*A en posicion aleatoria dentro de
    la caja. La anchura relativa u ~ U[f, 1] garantiza que cabe."""
    x1, y1, x2, y2 = caja
    bw, bh = x2 - x1, y2 - y1
    u = rnd.uniform(f, 1.0)
    pw, ph = bw * u, bh * f / u
    px = x1 + rnd.uniform(0, bw - pw)
    py = y1 + rnd.uniform(0, bh - ph)
    return px, py, px + pw, py + ph


def parche_banda_borde(rnd, caja, f):
    """PRUEBA: banda anclada a uno de los cuatro bordes de la caja (un
    oclusor que entra desde fuera: coche, pared, otra persona)."""
    x1, y1, x2, y2 = caja
    bw, bh = x2 - x1, y2 - y1
    lado = int(rnd.randint(4))
    if lado == 0:                      # desde abajo (piernas)
        return x1, y2 - bh * f, x2, y2
    if lado == 1:                      # desde arriba (cabeza)
        return x1, y1, x2, y1 + bh * f
    if lado == 2:                      # desde la izquierda
        return x1, y1, x1 + bw * f, y2
    return x2 - bw * f, y1, x2, y2     # desde la derecha


MIN_STD_TEXTURA = 6.0    # por debajo la region es lisa (p. ej. relleno gris del mosaico)


def textura_misma_imagen(rnd, im, cajas_persona, w, h, intentos=20, banco=None):
    """Region de la misma imagen que no solape ninguna persona y que tenga
    textura real (se rechazan regiones lisas: el relleno gris del mosaico o
    zonas negras, que convertirian el parche en uno opaco). Si no se
    encuentra, se recurre al banco; si no hay banco, a cualquier region."""
    H, W = im.shape[:2]
    rw, rh = max(2, min(W, int(w))), max(2, min(H, int(h)))
    for _ in range(intentos):
        x = int(rnd.randint(0, W - rw + 1)); y = int(rnd.randint(0, H - rh + 1))
        solapa = False
        for (a, b, c, d) in cajas_persona:
            if x < c and x + rw > a and y < d and y + rh > b:
                solapa = True
                break
        if solapa:
            continue
        region = im[y:y + rh, x:x + rw]
        if float(region.std()) < MIN_STD_TEXTURA:
            continue
        return redimensionar(region, w, h)
    if banco is not None and len(banco):
        return banco.textura(rnd, w, h)
    x = int(rnd.randint(0, W - rw + 1)); y = int(rnd.randint(0, H - rh + 1))
    return redimensionar(im[y:y + rh, x:x + rw][::-1, ::-1], w, h)


def pegar(im, mascara, rect, contenido, suavizado=3):
    """Pega `contenido` (h,w,3) en rect xyxy con borde difuminado y marca la
    mascara de cobertura. Devuelve True si se dibujo algo."""
    H, W = im.shape[:2]
    x1, y1 = int(round(max(0, rect[0]))), int(round(max(0, rect[1])))
    x2, y2 = int(round(min(W, rect[2]))), int(round(min(H, rect[3])))
    if x2 - x1 < MIN_LADO_PARCHE or y2 - y1 < MIN_LADO_PARCHE:
        return False
    w, h = x2 - x1, y2 - y1
    if contenido.shape[0] != h or contenido.shape[1] != w:
        contenido = redimensionar(contenido, w, h)
    s = min(suavizado, w // 4, h // 4)
    if s > 0:
        alfa = np.ones((h, w), dtype=np.float32)
        rampa = np.linspace(0.35, 1.0, s, dtype=np.float32)
        alfa[:s, :] *= rampa[:, None]; alfa[-s:, :] *= rampa[::-1][:, None]
        alfa[:, :s] *= rampa[None, :]; alfa[:, -s:] *= rampa[::-1][None, :]
        alfa = alfa[..., None]
        region = im[y1:y2, x1:x2].astype(np.float32)
        im[y1:y2, x1:x2] = (alfa * contenido.astype(np.float32)
                            + (1 - alfa) * region).astype(np.uint8)
    else:
        im[y1:y2, x1:x2] = contenido
    mascara[y1:y2, x1:x2] = 1
    return True


def contenido_parche(rnd, tipo, im, cajas_persona, w, h, banco, textura_propia):
    w, h = max(1, int(round(w))), max(1, int(round(h)))
    if tipo == "opaco":
        g = int(rnd.randint(0, 90))                  # gris oscuro / negro
        return np.full((h, w, 3), g, dtype=np.uint8)
    if tipo == "recorte" and banco is not None and len(banco):
        return banco.recorte(rnd, w, h)
    if textura_propia or banco is None or not len(banco):
        return textura_misma_imagen(rnd, im, cajas_persona, w, h, banco=banco)
    return banco.textura(rnd, w, h)


def cobertura_por_caja(mascara, cajas):
    """Fraccion de cada caja cubierta por la mascara (union de parches)."""
    H, W = mascara.shape
    out = []
    for (x1, y1, x2, y2) in cajas:
        a, b = int(max(0, np.floor(x1))), int(max(0, np.floor(y1)))
        c, d = int(min(W, np.ceil(x2))), int(min(H, np.ceil(y2)))
        if c <= a or d <= b:
            out.append(0.0)
        else:
            out.append(float(mascara[b:d, a:c].mean()))
    return out


# --- Generador de ENTRENAMIENTO --------------------------------------------
def ocluir_entrenamiento(im, cajas, rnd, banco=None, p=0.5, n_min=1, n_max=3,
                         rango_f=RANGO_F_ENTRENAMIENTO,
                         prob_tipo=PROB_TIPO_ENTRENAMIENTO, min_lado_caja=8):
    """Aplica el aumento de entrenamiento in-place. Devuelve lista de
    (indice_caja, tipo, f_nominal) de los parches aplicados (vacia si no se
    aplico) y la mascara."""
    H, W = im.shape[:2]
    mascara = np.zeros((H, W), dtype=np.uint8)
    aplicados = []
    if rnd.rand() >= p or not len(cajas):
        return aplicados, mascara
    validas = [i for i, c in enumerate(cajas)
               if c[2] - c[0] >= min_lado_caja and c[3] - c[1] >= min_lado_caja]
    if not validas:
        return aplicados, mascara
    n = int(min(len(validas), rnd.randint(n_min, n_max + 1)))
    elegidas = rnd.choice(validas, size=n, replace=False)
    tipos, probs = zip(*prob_tipo.items())
    for i in elegidas:
        f = rnd.uniform(*rango_f)
        tipo = str(rnd.choice(tipos, p=probs))
        rect = parche_interior(rnd, cajas[i], f)
        cont = contenido_parche(rnd, tipo, im, cajas, rect[2] - rect[0],
                                rect[3] - rect[1], banco, textura_propia=True)
        if pegar(im, mascara, rect, cont):
            aplicados.append((int(i), tipo, float(f)))
    return aplicados, mascara


# --- Generador de PRUEBA ----------------------------------------------------
def ocluir_prueba(im, cajas, rnd, estrato, tipo, banco):
    """Ocluye TODAS las cajas con una banda de borde del estrato dado.
    Devuelve (f_nominal por caja, cobertura efectiva por caja)."""
    H, W = im.shape[:2]
    mascara = np.zeros((H, W), dtype=np.uint8)
    lo, hi = RANGO_F_PRUEBA[estrato]
    nominales = []
    for c in cajas:
        f = float(rnd.uniform(lo, hi))
        nominales.append(f)
        rect = parche_banda_borde(rnd, c, f)
        cont = contenido_parche(rnd, tipo, im, cajas, rect[2] - rect[0],
                                rect[3] - rect[1], banco, textura_propia=False)
        pegar(im, mascara, rect, cont)
    return nominales, cobertura_por_caja(mascara, cajas)


# --- Transform para el pipeline de Ultralytics ------------------------------
class OclusionEntrenamiento:
    """Se inserta en el Compose del dataset de entrenamiento justo antes de
    Format. Opera sobre labels['img'] (HWC BGR uint8) y labels['instances'].
    Usa np.random, que Ultralytics siembra por worker y por epoca."""

    def __init__(self, ruta_banco=None, p=0.5, n_min=1, n_max=3,
                 rango_f=RANGO_F_ENTRENAMIENTO, prob_tipo=PROB_TIPO_ENTRENAMIENTO):
        self.ruta_banco = ruta_banco
        self.p, self.n_min, self.n_max = p, n_min, n_max
        self.rango_f, self.prob_tipo = tuple(rango_f), dict(prob_tipo)
        self._banco = None
        self.contador = {"imagenes": 0, "ocluidas": 0, "parches": 0}

    @property
    def banco(self):
        if self._banco is None and self.ruta_banco:
            self._banco = BancoRecortes(self.ruta_banco)
        return self._banco

    def __getstate__(self):
        d = self.__dict__.copy()
        d["_banco"] = None            # se reabre en cada worker
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
        aplicados, _ = ocluir_entrenamiento(
            im, cajas, np.random, self.banco, self.p, self.n_min, self.n_max,
            self.rango_f, self.prob_tipo)
        self.contador["imagenes"] += 1
        if aplicados:
            self.contador["ocluidas"] += 1
            self.contador["parches"] += len(aplicados)
        labels["img"] = im
        if normalizado:
            inst.normalize(W, H)
        inst.convert_bbox(formato)
        return labels
