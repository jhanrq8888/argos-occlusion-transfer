# ARGOS-11 — Veredicto de H15 (E12, Faster R-CNN, siluetas)

Generado por `36_h15.py`. AP@0.5, media de 3 semillas; IC 95 % por imágenes (criterio) y jerárquico. Regla literal de `PREREGISTRO_H15.md`.

| Celda | n | V1 | V3sil | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| silueta_severa severa | 1858 | 0.035 | 0.183 | +14.72* | [+13.04; +16.66] | [+12.97; +16.63] |
| nightowls ocluida | 530 | 0.150 | 0.182 | +3.28* | [+1.64; +4.79] | [+0.67; +5.81] |
| citypersons_convencion heavy | 733 | 0.151 | 0.175 | +2.33* | [+1.01; +3.69] | [+0.13; +4.92] |
| test_proxy severa | 101 | 0.310 | 0.300 | -1.00 | [-5.61; +3.24] | [-6.71; +4.04] |

## Veredicto H15: **REFUTADA** (2 de 3 fuentes reales superan +2 pp con IC por imágenes > 0; la regla exige 2 para refutar)

## Secundario (no decide): controles de otras familias

| Celda | n | V1 | V3sil | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| generativa_severa severa | 2018 | 0.022 | 0.051 | +2.93* | [+2.22; +3.64] | [+2.11; +3.77] |
| geometria_severa severa | 679 | 0.053 | 0.258 | +20.49* | [+17.70; +23.53] | [+17.47; +23.90] |
| profundidad_severa severa | 1629 | 0.012 | 0.090 | +7.83* | [+6.86; +9.13] | [+6.76; +9.14] |
