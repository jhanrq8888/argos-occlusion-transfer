#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura de dosis del short paper (H18, Faster R-CNN, siluetas, semillas 0-2): V3 - V1 en AP@0.5 (pp) por dosis,
en personas ocluidas y sin oclusion de NightOwls y CityPersons, con IC del 95 % de la t de Welch entre semillas (3 de V1
y 3 de V3; reporte de seguimiento del 11/11/2026, obs. 16). Lee resultados_h18/resumen_ap.csv; sin cifras a mano.
Paleta: ranuras 1 y 2 de la paleta categorica de referencia (validada para CVD); la forma del marcador repite la serie.
Uso: python fig_dosis.py   -> fig_dosis_es.png y fig_dosis.png"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
from scipy import stats

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
AZUL, NARANJA = "#2a78d6", "#eb6834"
TINTA, TINTA2, REJILLA = "#0b0b0b", "#52514e", "#d9d8d4"
PANELES = (("nightowls", "NightOwls", "ocluida", "sin"), ("citypersons_convencion", "CityPersons", "heavy", "bare"))
DOSIS = ("V3baja", "V3sil", "V3alta")
TXT = {"es": dict(dosis=("baja", "habitual", "alta"), y="V3 $-$ V1 (pp de AP@0.5)", ocl="ocluidas", sin="sin oclusión",
                  umbral="+2 pp", heavy=" (\\emph{heavy})", x="dosis del aumento"),
       "en": dict(dosis=("low", "usual", "high"), y="V3 $-$ V1 (AP@0.5 pp)", ocl="occluded", sin="unoccluded",
                  umbral="+2 pp", heavy="", x="augmentation dose")}


def main():
    d = pd.read_csv(os.path.join(RAIZ, "resultados_h18", "resumen_ap.csv"))
    d = d[(d.luz == "todas") & (d.semilla <= 2)].copy()
    d["var"] = d.corrida.str.replace(r"_s\d+$", "", regex=True)
    m = d.groupby(["conjunto", "estrato", "var"]).AP50.mean().unstack()
    g = d.groupby(["conjunto", "estrato", "var"]).AP50

    def welch(conj, e, v):
        x3, x1 = 100 * g.get_group((conj, e, v)).values, 100 * g.get_group((conj, e, "V1")).values
        a, b = x3.var(ddof=1) / len(x3), x1.var(ddof=1) / len(x1)
        gl = (a + b) ** 2 / (a ** 2 / (len(x3) - 1) + b ** 2 / (len(x1) - 1))
        return stats.t.ppf(0.975, gl) * np.sqrt(a + b)
    plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "font.size": 7,
                         "axes.edgecolor": TINTA2, "axes.labelcolor": TINTA, "xtick.color": TINTA2, "ytick.color": TINTA2})
    for lang, t in TXT.items():
        fig, axs = plt.subplots(1, 2, figsize=(3.45, 1.55), sharey=True)
        for ax, (conj, nombre, e_ocl, e_sin) in zip(axs, PANELES):
            x = range(len(DOSIS))
            for e, col, mk, etq, dx in ((e_ocl, AZUL, "o", t["ocl"], -0.07), (e_sin, NARANJA, "s", t["sin"], 0.07)):
                y = [100 * (m.loc[(conj, e), v] - m.loc[(conj, e), "V1"]) for v in DOSIS]
                err = [welch(conj, e, v) for v in DOSIS]
                xx = [i + dx for i in x]
                ax.errorbar(xx, y, yerr=err, fmt="none", ecolor=col, elinewidth=0.8, capsize=1.5, alpha=0.75, zorder=2)
                ax.plot(xx, y, color=col, lw=1.5, marker=mk, ms=4.5, mec="white", mew=0.8, label=etq, zorder=3)
            ax.axhline(2, color=TINTA2, lw=0.7, ls=(0, (3, 2)), zorder=1)
            ax.axhline(0, color=REJILLA, lw=0.7, zorder=0)
            ax.set_xticks(list(x)); ax.set_xticklabels(t["dosis"])
            ax.set_xlim(-0.3, 2.3)
            ax.set_title(nombre, fontsize=7, color=TINTA, pad=2)
            ax.grid(axis="y", color=REJILLA, lw=0.4); ax.set_axisbelow(True)
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            ax.tick_params(length=2, pad=1.5)
        if lang == "es":
            axs[0].yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: ("%g" % v).replace(".", ",")))
        axs[0].set_ylabel(t["y"], labelpad=1.5)
        axs[0].text(0.5, 2.25, t["umbral"], ha="center", va="bottom", fontsize=6, color=TINTA2)
        h, l = axs[0].get_legend_handles_labels()
        fig.legend(h, l, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.55, 1.03), fontsize=6.5,
                   handlelength=1.6, columnspacing=1.2)
        fig.text(0.55, 0.005, t["x"], ha="center", va="bottom", fontsize=6.5, color=TINTA2)
        fig.subplots_adjust(left=0.14, right=0.99, top=0.80, bottom=0.2, wspace=0.12)
        out = os.path.join(AQUI, "fig_dosis_es.png" if lang == "es" else "fig_dosis.png")
        fig.savefig(out, dpi=400)
        plt.close(fig)
        print(out)


if __name__ == "__main__":
    main()
