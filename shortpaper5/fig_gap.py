"""Figura 1 del short paper de 5 paginas: control sintetico (barras) frente a las tres fuentes de oclusion real (marcadores),
en los 13 bloques con control sintetico. Cifras (V3 - V1, AP@0.5, pp) de informes/analisis_final/SINTETICO_VS_REAL.md.
Uso: python fig_gap.py [es]   (es: etiquetas con coma decimal -> fig_gap_es.png)"""
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ES = len(sys.argv) > 1 and sys.argv[1] == 'es'
bloques = ['H3', 'H4', 'H4-Y26', 'H6', 'H8', 'H9', 'H9b', 'H10', 'H10-s', 'H11', 'H12a', 'H12b', 'H14']
control = [60.92, 10.63, 12.01, 23.74, 10.97, 2.60, 15.23, 18.39, 10.99, 24.66, 14.45, 19.04, 7.42]
no = [-3.17, -16.79, -14.31, -1.35, -6.98, -1.93, 0.01, -2.05, -1.12, 1.95, -0.39, 0.78, -1.50]
cp = [-0.36, -3.94, -4.42, 1.82, -3.47, 1.23, 1.52, 2.37, 2.26, 1.31, 0.25, 1.11, -0.16]
ex = [-3.25, -5.02, -3.51, 0.94, -2.21, 2.82, -3.03, -4.88, -3.50, -2.44, 3.04, -0.56, 5.49]

fig, ax = plt.subplots(figsize=(3.5, 2.05), dpi=300)
x = range(len(bloques))
ax.bar(x, control, width=0.55, color='#9a9a9a')
ax.plot(x, no, 's', color='#1f4e9c', ms=3.6)
ax.plot(x, cp, '^', color='#e08a00', ms=4.0)
ax.plot(x, ex, 'D', color='#2e7d32', ms=3.4)
ax.axhline(2, color='#d32f2f', ls='--', lw=0.8)
ax.axhline(0, color='black', lw=0.5)
ax.set_xticks(list(x))
ax.set_xticklabels(bloques, fontsize=5.6, rotation=45, ha='right', rotation_mode='anchor')
ax.set_ylim(-20, 30)
ax.set_ylabel(r'$\Delta$AP@0.5 (pp)', fontsize=6.5)
ax.tick_params(axis='y', labelsize=6.5)
ax.annotate(('+60,9' if ES else '+60.9'), xy=(0, 30), xytext=(0.42, 27.5), fontsize=5.5, ha='left', va='center',
            arrowprops=dict(arrowstyle='-', lw=0.4, color='0.3'))
mano = [Patch(color='#9a9a9a', label='Control'),
        Line2D([], [], marker='s', ls='', color='#1f4e9c', ms=3.6, label='NO'),
        Line2D([], [], marker='^', ls='', color='#e08a00', ms=4.0, label='CP'),
        Line2D([], [], marker='D', ls='', color='#2e7d32', ms=3.4, label='EX'),
        Line2D([], [], color='#d32f2f', ls='--', lw=0.8, label='+2 pp')]
ax.legend(handles=mano, fontsize=5.8, ncol=5, loc='upper center', bbox_to_anchor=(0.5, 1.18), frameon=False,
          columnspacing=0.8, handletextpad=0.3, handlelength=1.4)
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
fig.tight_layout(pad=0.4)
fig.savefig(r'D:/argos11/raw/shortpaper5/fig_gap%s.png' % ('_es' if ES else ''))
print('ok')
