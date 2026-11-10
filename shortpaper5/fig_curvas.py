"""Figura del suplemento (revision del 10/11/2026, obs. 9): mAP@0.5 de validacion por epoca (ExDark val limpia y ocluida
sinteticamente; o CityPersons en H11) de V1 y V3 en cuatro bloques con epocas fijas, media de semillas. Imprime cuanto sube
V3 entre las epocas 25 y 30 en los bloques YOLO de 30 epocas. Lee runs/<bloque>/<variante>_s<semilla>/results.csv.
Uso: python fig_curvas.py [es]"""
import csv
import glob
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ES = len(sys.argv) > 1 and sys.argv[1] == "es"
AQUI = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(os.path.dirname(AQUI), "runs")
# bloque: (carpeta de V1, carpeta de V3)
BLOQUES = {"H9b": ("argos_gen_fijo", "argos_gen_fijo"), "H10-s": ("argos_gen_fijo", "argos_sil_fijo"),
           "H14": ("argos_prof", "argos_prof"), "H11 (60 ep.)": ("argos_cp_fijo", "argos_cp_fijo")}


def curva(carpeta, var):
    cs = []
    for f in sorted(glob.glob(os.path.join(RUNS, carpeta, "%s_s*" % var, "results.csv"))):
        r = [{k.strip(): v for k, v in x.items()} for x in csv.DictReader(open(f, encoding="utf-8"))]
        cs.append([100 * float(x["metrics/mAP50(B)"]) for x in r])
    n = min(len(c) for c in cs)
    return np.mean([c[:n] for c in cs], axis=0)


def perdida(carpeta, var):
    cs = []
    for f in sorted(glob.glob(os.path.join(RUNS, carpeta, "%s_s*" % var, "results.csv"))):
        cs.append([float(x["loss"]) for x in csv.DictReader(open(f, encoding="utf-8"))])
    n = min(len(c) for c in cs)
    return np.mean([c[:n] for c in cs], axis=0)


fig, axs = plt.subplots(1, 5, figsize=(7.0, 1.9), dpi=300)
subidas = {}
for ax, (nom, (c1, c3)) in zip(axs, BLOQUES.items()):
    v1, v3 = curva(c1, "V1"), curva(c3, "V3")
    ax.plot(range(1, len(v1) + 1), v1, color="#7f7f7f", lw=1, label="V1")
    ax.plot(range(1, len(v3) + 1), v3, color="#1f4e9c", lw=1, label="V3")
    ax.set_title(nom, fontsize=6.5)
    ax.set_xlabel("Época" if ES else "Epoch", fontsize=6)
    ax.tick_params(labelsize=5.5)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    if len(v3) == 30:
        subidas[nom] = round(float(v3[29] - v3[24]), 2)
# Faster R-CNN (H15): torchvision solo registra la perdida de entrenamiento por epoca (tasa x0,1 en las epocas 20 y 27)
ax = axs[4]
for var, col in (("V1", "#7f7f7f"), ("V3", "#1f4e9c")):
    c = perdida("argos_frcnn", var)
    ax.plot(range(1, len(c) + 1), c, color=col, lw=1, label=var)
ax.set_title("H15, Faster R-CNN", fontsize=6.5)
ax.set_xlabel("Época" if ES else "Epoch", fontsize=6)
ax.set_ylabel("Pérdida de entrenamiento" if ES else "Training loss", fontsize=6)
ax.tick_params(labelsize=5.5)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
axs[0].set_ylabel("mAP@0.5 val. (%)", fontsize=6)
axs[0].legend(fontsize=5.5, frameon=False)
fig.tight_layout(pad=0.4)
fig.savefig(os.path.join(AQUI, "fig_curvas%s.png" % ("_es" if ES else "")))
print("subida de V3 entre las epocas 25 y 30 (pp):", subidas)
