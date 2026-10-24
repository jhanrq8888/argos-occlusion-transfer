"""Figura del short paper: ganancia en el control sintetico (eje x) frente a la ganancia en cada fuente de oclusion real
(eje y), un punto por bloque y fuente (17 bloques con control x 3 fuentes = 51 celdas; relleno = exposicion igual, vacio = desigual o temprana), con IC 95 % por imagenes en ambos ejes y los
rho de Spearman con su IC bootstrap de bloques. Lee informes/analisis_final/celdas_completas.csv y revision_sp.json
(informes/revision_sp_analisis.py). Revision del 22/10: se incluyen los 4 bloques de torchvision (H15-H17).
Uso: python fig_dispersion.py [es]   (es: etiquetas en espanol con coma decimal -> fig_dispersion_es.png)"""
import json
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

ES = len(sys.argv) > 1 and sys.argv[1] == 'es'
AQUI = os.path.dirname(os.path.abspath(__file__))
AF = os.path.join(os.path.dirname(AQUI), 'informes', 'analisis_final')
d = pd.read_csv(os.path.join(AF, 'celdas_completas.csv'))
d = d[d.bloque != 'h7']
rho = json.load(open(os.path.join(AF, 'revision_sp.json'), encoding='utf-8'))['rho_ic_bloques']
f2 = (lambda v: ('%+.2f' % v).replace('.', ',').replace('-', '−')) if ES else (lambda v: ('%+.2f' % v).replace('-', '−'))
ESTILO = {'NO': ('s', '#1f4e9c', 3.4), 'CP': ('^', '#e08a00', 3.8), 'EX': ('D', '#2e7d32', 3.1)}

fig, ax = plt.subplots(figsize=(3.5, 1.9), dpi=300)
XMAX = 28
ax.axhspan(-2, 2, color='#f0f0f0', zorder=0)
ax.axhline(0, color='black', lw=0.5, zorder=1)
ax.axhline(2, color='#d32f2f', ls='--', lw=0.8, zorder=1)
ctrl = d[d.fuente == 'control'].set_index('bloque')
for s, (m, c, t) in ESTILO.items():
    g = d[d.fuente == s].set_index('bloque')
    g = g[ctrl.loc[g.index].delta <= XMAX]
    x = ctrl.loc[g.index]
    for igual in (True, False):
        sel = (g.exposicion == 'igual (epocas fijas)') == igual
        gg, xx = g[sel], x[sel]
        ax.errorbar(xx.delta, gg.delta, xerr=[xx.delta - xx.ic_lo, xx.ic_hi - xx.delta], yerr=[gg.delta - gg.ic_lo, gg.ic_hi - gg.delta],
                    fmt=m, color=c, mfc=c if igual else 'white', mec=c, ms=t, lw=0.45, alpha=0.85, capsize=0, zorder=3)
ax.set_xlim(0, XMAX)
ax.set_ylim(-20, 9)
ax.set_xlabel('Ganancia en el control sintético (pp)' if ES else 'Gain on the synthetic control (pp)', fontsize=6.5)
ax.set_ylabel('Ganancia real (pp)' if ES else 'Real gain (pp)', fontsize=6.5)
ax.tick_params(labelsize=6.2)
# H3 (+60,9 en el control) queda fuera de escala; sus valores y los rho con IC van en el pie de figura del texto.
mano = [Line2D([], [], marker=m, ls='', color=c, ms=t, label=s) for s, (m, c, t) in ESTILO.items()] + \
       [Line2D([], [], color='#d32f2f', ls='--', lw=0.8, label='+2 pp')]
ax.legend(handles=mano, fontsize=5.8, ncol=4, loc='upper right', bbox_to_anchor=(1.0, 1.02), frameon=False,
          columnspacing=0.8, handletextpad=0.3, handlelength=1.4)
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
fig.tight_layout(pad=0.4)
fig.savefig(os.path.join(AQUI, 'fig_dispersion%s.png' % ('_es' if ES else '')))
print('ok')
