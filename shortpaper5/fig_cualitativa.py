"""Figura cualitativa del suplemento (revision del 20/10/2026, obs. 13): arriba, oclusion real anotada de las tres fuentes
(NightOwls ocluida, CityPersons heavy, ExDark proxy severa); abajo, la misma persona de ExDark test en el control de cada
familia sintetica (parches, siluetas, generativa, geometria real, orden de profundidad). Recortes con contexto (1,8 x caja).
Las imagenes no se redistribuyen: la figura muestra recortes pequenos con fines de investigacion, como permiten las licencias.
Uso: python fig_cualitativa.py [es]"""
import json
import os
import sys

import cv2
import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ES = len(sys.argv) > 1 and sys.argv[1] == "es"
T = 220  # lado de cada recorte


def gt(r):
    return json.load(open(os.path.join(RAIZ, r), encoding="utf-8"))


def recorte(g, nombre, inst, color=(80, 220, 80)):
    im = cv2.imread(os.path.join(g["dir_imagenes"], nombre))
    h, w = im.shape[:2]
    cx, cy = (inst["x1"] + inst["x2"]) / 2, (inst["y1"] + inst["y2"]) / 2
    lado = 1.8 * max(inst["x2"] - inst["x1"], inst["y2"] - inst["y1"], 24)
    x1, y1 = int(max(0, cx - lado / 2)), int(max(0, cy - lado / 2))
    x2, y2 = int(min(w, cx + lado / 2)), int(min(h, cy + lado / 2))
    c = im[y1:y2, x1:x2].copy()
    cv2.rectangle(c, (int(inst["x1"] - x1), int(inst["y1"] - y1)), (int(inst["x2"] - x1), int(inst["y2"] - y1)), color, 2)
    s = T / max(c.shape[:2])
    c = cv2.resize(c, (max(1, int(c.shape[1] * s)), max(1, int(c.shape[0] * s))))
    out = np.full((T, T, 3), 255, np.uint8)
    oy, ox = (T - c.shape[0]) // 2, (T - c.shape[1]) // 2
    out[oy:oy + c.shape[0], ox:ox + c.shape[1]] = c
    return out


def primera(g, estrato, minimo=40, salto=0):
    vistos = 0
    for n in sorted(g["imagenes"]):
        for o in g["imagenes"][n]["instancias"]:
            if o["estrato"] == estrato and (o["y2"] - o["y1"]) >= minimo:
                if vistos == salto:
                    return n, o
                vistos += 1
    raise ValueError(estrato)


def rotulo(im, texto):
    banda = np.full((26, im.shape[1], 3), 255, np.uint8)
    cv2.putText(banda, texto, (4, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    return np.vstack([banda, im])


def main():
    reales = [("dataset/externos/gt_nightowls.json", "ocluida", "NightOwls (ocluida)" if ES else "NightOwls (occluded)", 0),
              ("dataset/externos/gt_citypersons_convencion.json", "heavy", "CityPersons (heavy)", 3),
              ("dataset/gt_test_proxy.json", "severa", "ExDark (indicador)" if ES else "ExDark (proxy)", 0)]
    fila1 = []
    for r, est, et, salto in reales:
        g = gt(r)
        n, o = primera(g, est, salto=salto)
        fila1.append(rotulo(recorte(g, n, o, (60, 160, 255)), et))
    familias = [("opaco_severa", "Parches" if ES else "Patches"), ("silueta_severa", "Siluetas" if ES else "Silhouettes"),
                ("generativa_severa", "Generativa" if ES else "Generative"), ("geometria_severa", "Geometria real" if ES else "Real geometry"),
                ("profundidad_severa", "Profundidad" if ES else "Depth order")]
    gts = {f: gt("dataset/test_sintetico/%s/gt_%s.json" % (f, f)) for f, _ in familias}
    # una persona severa en los cinco controles (mismo id), con caja de al menos 70 px
    comunes = None
    for f, g in gts.items():
        ids = {o["id"] for v in g["imagenes"].values() for o in v["instancias"] if o["estrato"] == "severa" and (o["y2"] - o["y1"]) >= 70}
        comunes = ids if comunes is None else comunes & ids
    elegido = sorted(comunes)[len(comunes) // 3]
    fila2 = []
    for f, et in familias:
        g = gts[f]
        n = next(k for k, v in g["imagenes"].items() if any(o["id"] == elegido for o in v["instancias"]))
        o = next(o for o in g["imagenes"][n]["instancias"] if o["id"] == elegido)
        fila2.append(rotulo(recorte(g, n, o), et))
    sep = np.full((T + 26, 6, 3), 255, np.uint8)
    a = np.hstack(sum([[c, sep] for c in fila1], [])[:-1])
    b = np.hstack(sum([[c, sep] for c in fila2], [])[:-1])
    pad = np.full((a.shape[0], b.shape[1] - a.shape[1], 3), 255, np.uint8)
    lienzo = np.vstack([np.hstack([a, pad]), np.full((8, b.shape[1], 3), 255, np.uint8), b])
    sal = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig_cualitativa%s.png" % ("_es" if ES else ""))
    cv2.imwrite(sal, lienzo)
    print(sal, elegido)


if __name__ == "__main__":
    main()
