"""Figura de bosque del short paper (revisión del 10/11/2026, obs. 1 y 4): estimación global V3 - V1 por fuente con IC del
90 % (prueba unilateral de no superioridad: limite superior frente a +2 pp) en tres especificaciones (modelo mixto del texto, con V1 compartidas y bootstrap de bloques),
con la dosis habitual (azul, círculo) y con los bloques de dosis H18e (naranja, rombo). Lee
informes/analisis_final/revision_10nov.json (informes/revision_10nov.py).
Uso: python fig_bosque.py [es]   (es: etiquetas en español -> fig_bosque_es.png)"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ES = len(sys.argv) > 1 and sys.argv[1] == "es"
AQUI = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(os.path.dirname(AQUI), "informes", "analisis_final", "revision_10nov.json"), encoding="utf-8"))
FUENTES = [("NO", "NightOwls"), ("CP", "CityPersons heavy"), ("EX", "ExDark (indicador)" if ES else "ExDark (proxy)")]
ESPEC = [("mixto_original", "Modelo mixto" if ES else "Mixed model"),
         ("mixto_V1_compartida", "V1 compartidas" if ES else "Shared V1"),
         ("bootstrap_bloques", "Bootstrap de bloques" if ES else "Block bootstrap")]
CORTO = {"NO": "NightOwls", "CP": "CityPersons", "EX": "ExDark (ind.)" if ES else "ExDark (proxy)"}
CONJ = [("dosis_habitual", "#1f4e9c", "o", "Dosis habitual (12 bloques)" if ES else "Usual dose (12 blocks)", -0.14),
        ("con_H18e", "#c26a00", "D", "Con H18e (14 bloques)" if ES else "With H18e (14 blocks)", 0.14)]

fig, ax = plt.subplots(figsize=(3.5, 2.55), dpi=300)
ax.axvspan(-2, 2, color="#f0f0f0", zorder=0)
ax.axvline(0, color="black", lw=0.5, zorder=1)
ax.axvline(2, color="#d32f2f", ls="--", lw=0.8, zorder=1)
etiquetas, y = [], 0
for f, nom in FUENTES:
    for clave, enom in ESPEC:
        for conj, color, marca, _, dy in CONJ:
            r = d[conj][clave][f]
            est = r.get("est", r.get("media"))
            lo, hi = r["IC90"]
            ax.plot([lo, hi], [y + dy, y + dy], color=color, lw=1.2, solid_capstyle="round", zorder=2)
            ax.plot(est, y + dy, marker=marca, color=color, ms=3.6, mec="white", mew=0.4, zorder=3)
        etiquetas.append((y, "%s · %s" % (CORTO[f], enom)))
        y -= 1
    y -= 0.5
ax.set_yticks([p for p, _ in etiquetas])
ax.set_yticklabels([t for _, t in etiquetas], fontsize=5.6)
ax.set_xlabel(("Ganancia real V3$-$V1 (pp), IC del 90 %" if ES else "Real gain V3$-$V1 (pp), 90 % CI"), fontsize=6.2)
ax.tick_params(axis="x", labelsize=5.8)
ax.tick_params(axis="y", length=0)
ax.set_xlim(-3.2, 3.2)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
mano = [Line2D([], [], color=c, marker=m, lw=1.2, ms=3.6, mec="white", mew=0.4, label=t) for _, c, m, t, _ in CONJ] + \
       [Line2D([], [], color="#d32f2f", ls="--", lw=0.8, label="+2 pp")]
ax.legend(handles=mano, fontsize=5.4, loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=2, frameon=False,
          handlelength=1.6, columnspacing=0.9)
fig.tight_layout(pad=0.3)
fig.savefig(os.path.join(AQUI, "fig_bosque%s.png" % ("_es" if ES else "")))
print("ok")
