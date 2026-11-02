"""Figura del suplemento del short paper: ganancia en el control sintetico (eje x) frente a la ganancia en cada fuente de
oclusion real (eje y), un panel por fuente y un punto por bloque (17 bloques con control; relleno = exposicion igual, vacio =
desigual o temprana), con IC 95 % por imagenes en ambos ejes y el rho de Spearman de cada fuente con su IC bootstrap de
bloques en el titulo del panel. Lee informes/analisis_final/celdas_completas.csv y revision_panel.json.
Revision del 27/10 (seccion 6): se separa en tres paneles, uno por fuente, para no superponer las 51 celdas.
Uso: python fig_dispersion.py [es]   (es: etiquetas en espanol con coma decimal -> fig_dispersion_es.png)"""
import json
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ES = len(sys.argv) > 1 and sys.argv[1] == 'es'
AQUI = os.path.dirname(os.path.abspath(__file__))
AF = os.path.join(os.path.dirname(AQUI), 'informes', 'analisis_final')
d = pd.read_csv(os.path.join(AF, 'celdas_completas.csv'))
d = d[d.bloque != 'h7']
rho = json.load(open(os.path.join(AF, 'revision_panel.json'), encoding='utf-8'))['spearman']['17_bloques']
f2 = (lambda v: ('%+.2f' % v).replace('.', ',').replace('-', '−')) if ES else (lambda v: ('%+.2f' % v).replace('-', '−'))
NOMBRE = {'NO': 'NightOwls', 'CP': 'CityPersons heavy', 'EX': 'ExDark (indicador)' if ES else 'ExDark (proxy)'}
ESTILO = {'NO': ('s', '#1f4e9c', 3.4), 'CP': ('^', '#e08a00', 3.8), 'EX': ('D', '#2e7d32', 3.1)}

fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.2), dpi=300, sharey=True)
XMAX = 28
ctrl = d[d.fuente == 'control'].set_index('bloque')
for ax, (s, (m, c, t)) in zip(axs, ESTILO.items()):
    ax.axhspan(-2, 2, color='#f0f0f0', zorder=0)
    ax.axhline(0, color='black', lw=0.5, zorder=1)
    ax.axhline(2, color='#d32f2f', ls='--', lw=0.8, zorder=1)
    g = d[d.fuente == s].set_index('bloque')
    g = g[ctrl.loc[g.index].delta <= XMAX]
    x = ctrl.loc[g.index]
    for igual in (True, False):
        sel = (g.exposicion == 'igual (epocas fijas)') == igual
        gg, xx = g[sel], x[sel]
        ax.errorbar(xx.delta, gg.delta, xerr=[xx.delta - xx.ic_lo, xx.ic_hi - xx.delta],
                    yerr=[gg.delta - gg.ic_lo, gg.ic_hi - gg.delta], fmt=m, color=c, mfc=c if igual else 'white', mec=c,
                    ms=t, lw=0.45, alpha=0.85, capsize=0, zorder=3)
    r = rho[s]
    ax.set_title('%s: ρ = %s [%s; %s]' % (NOMBRE[s], f2(r['rho']), f2(r['IC95'][0]), f2(r['IC95'][1])), fontsize=6.5)
    ax.set_xlim(0, XMAX)
    ax.set_ylim(-20, 9)
    ax.set_xlabel('Ganancia en el control sintético (pp)' if ES else 'Gain on the synthetic control (pp)', fontsize=6.3)
    ax.tick_params(labelsize=6.0)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
axs[0].set_ylabel('Ganancia real (pp)' if ES else 'Real gain (pp)', fontsize=6.5)
# H3 (+60,9 en el control) queda fuera de escala; sus valores van en el pie de figura del suplemento.
fig.tight_layout(pad=0.4)
fig.savefig(os.path.join(AQUI, 'fig_dispersion%s.png' % ('_es' if ES else '')))
print('ok')
