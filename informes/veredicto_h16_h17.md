# ARGOS-11 — Veredictos de H16a, H16b y H17 (E13)

Generado por `37_h16_h17.py`. AP@0.5, media de 3 semillas; IC 95 % por imágenes (criterio) y jerárquico; * = supera +2 pp con IC por imágenes > 0. Regla literal de `PREREGISTRO_H16_H17.md`.

## E13 Faster R-CNN, generativa (H16a) — predicción: transferencia

| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| generativa_severa severa | 2018 | 0.022 | 0.225 | +20.35* | [+18.57; +22.33] | [+18.53; +22.26] |
| nightowls ocluida | 530 | 0.150 | 0.159 | +0.92 | [-0.54; +2.26] | [-1.65; +3.58] |
| citypersons_convencion heavy | 733 | 0.151 | 0.144 | -0.76 | [-1.84; +0.50] | [-2.58; +1.16] |
| test_proxy severa | 101 | 0.310 | 0.318 | +0.80 | [-3.54; +5.02] | [-5.12; +6.34] |

**Veredicto H16a: REFUTADA** (0 de 3 fuentes reales superan +2 pp con IC por imágenes > 0; control supera)

Secundario (no decide): controles de otras familias

| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| silueta_severa severa | 1858 | 0.035 | 0.040 | +0.48 | [+0.06; +0.89] | [-0.16; +1.17] |
| geometria_severa severa | 679 | 0.053 | 0.066 | +1.36 | [+0.51; +2.21] | [-0.15; +2.94] |
| profundidad_severa severa | 1629 | 0.012 | 0.018 | +0.56 | [+0.31; +1.11] | [+0.18; +1.20] |

Secundario (no decide): V3 − V1 por estrato (AP@0.5 de `resumen_ap.csv`)

| Fuente | Estrato | n | V1 | V3 | V3 − V1 |
|---|---|---|---|---|---|
| nightowls | sin | 2763 | 0.631 | 0.612 | -1.93 |
| nightowls | ocluida | 530 | 0.150 | 0.159 | +0.92 |
| citypersons_convencion | bare | 769 | 0.649 | 0.616 | -3.34 |
| citypersons_convencion | partial | 810 | 0.499 | 0.466 | -3.32 |
| citypersons_convencion | heavy | 733 | 0.151 | 0.144 | -0.76 |
| test_proxy | sin | 1756 | 0.837 | 0.829 | -0.72 |
| test_proxy | ligera | 188 | 0.595 | 0.601 | +0.63 |
| test_proxy | moderada | 190 | 0.547 | 0.552 | +0.51 |
| test_proxy | severa | 101 | 0.310 | 0.318 | +0.80 |

## E13 Faster R-CNN, profundidad (H16b) — predicción: transferencia

| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| profundidad_severa severa | 1629 | 0.012 | 0.108 | +9.63* | [+8.36; +11.34] | [+8.17; +11.57] |
| nightowls ocluida | 530 | 0.150 | 0.153 | +0.37 | [-1.00; +1.66] | [-2.12; +2.61] |
| citypersons_convencion heavy | 733 | 0.151 | 0.157 | +0.60 | [-0.71; +2.05] | [-1.58; +2.79] |
| test_proxy severa | 101 | 0.310 | 0.305 | -0.45 | [-6.19; +4.64] | [-6.72; +5.63] |

**Veredicto H16b: REFUTADA** (0 de 3 fuentes reales superan +2 pp con IC por imágenes > 0; control supera)

Secundario (no decide): controles de otras familias

| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| silueta_severa severa | 1858 | 0.035 | 0.121 | +8.60* | [+7.31; +10.24] | [+7.30; +10.26] |
| generativa_severa severa | 2018 | 0.022 | 0.049 | +2.67* | [+2.04; +3.29] | [+1.63; +3.67] |
| geometria_severa severa | 679 | 0.053 | 0.193 | +14.05* | [+11.47; +16.97] | [+11.40; +17.36] |

Secundario (no decide): V3 − V1 por estrato (AP@0.5 de `resumen_ap.csv`)

| Fuente | Estrato | n | V1 | V3 | V3 − V1 |
|---|---|---|---|---|---|
| nightowls | sin | 2763 | 0.631 | 0.634 | +0.30 |
| nightowls | ocluida | 530 | 0.150 | 0.153 | +0.37 |
| citypersons_convencion | bare | 769 | 0.649 | 0.633 | -1.66 |
| citypersons_convencion | partial | 810 | 0.499 | 0.475 | -2.49 |
| citypersons_convencion | heavy | 733 | 0.151 | 0.157 | +0.60 |
| test_proxy | sin | 1756 | 0.837 | 0.830 | -0.63 |
| test_proxy | ligera | 188 | 0.595 | 0.594 | -0.09 |
| test_proxy | moderada | 190 | 0.547 | 0.554 | +0.75 |
| test_proxy | severa | 101 | 0.310 | 0.305 | -0.45 |

## E13 RetinaNet, siluetas (H17) — predicción: no transferencia

| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| silueta_severa severa | 1858 | 0.034 | 0.100 | +6.60* | [+5.61; +7.81] | [+5.23; +8.28] |
| nightowls ocluida | 530 | 0.164 | 0.143 | -2.11 | [-3.53; -0.67] | [-7.25; +2.77] |
| citypersons_convencion heavy | 733 | 0.124 | 0.121 | -0.28 | [-1.16; +0.73] | [-2.14; +1.50] |
| test_proxy severa | 101 | 0.250 | 0.212 | -3.77 | [-8.47; +0.82] | [-9.89; +2.78] |

**Veredicto H17: SOSTENIDA** (0 de 3 fuentes reales superan +2 pp con IC por imágenes > 0; control supera)

Secundario (no decide): controles de otras familias

| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| generativa_severa severa | 2018 | 0.048 | 0.067 | +1.84 | [+1.43; +2.58] | [+1.26; +2.73] |
| geometria_severa severa | 679 | 0.060 | 0.142 | +8.15* | [+6.49; +9.85] | [+4.90; +11.34] |
| profundidad_severa severa | 1629 | 0.012 | 0.044 | +3.17* | [+2.61; +3.87] | [+2.34; +4.02] |

Secundario (no decide): V3 − V1 por estrato (AP@0.5 de `resumen_ap.csv`)

| Fuente | Estrato | n | V1 | V3 | V3 − V1 |
|---|---|---|---|---|---|
| nightowls | sin | 2763 | 0.685 | 0.618 | -6.70 |
| nightowls | ocluida | 530 | 0.164 | 0.143 | -2.11 |
| citypersons_convencion | bare | 769 | 0.563 | 0.518 | -4.49 |
| citypersons_convencion | partial | 810 | 0.422 | 0.390 | -3.24 |
| citypersons_convencion | heavy | 733 | 0.124 | 0.121 | -0.28 |
| test_proxy | sin | 1756 | 0.784 | 0.716 | -6.84 |
| test_proxy | ligera | 188 | 0.474 | 0.394 | -7.99 |
| test_proxy | moderada | 190 | 0.451 | 0.407 | -4.44 |
| test_proxy | severa | 101 | 0.250 | 0.212 | -3.77 |

## Secundario (no decide): réplica de V1 semilla 0 de Faster R-CNN entre pods

| Celda | n | V1_s0 de H15 | V1rep_s0 | Diferencia (pp) |
|---|---|---|---|---|
| nightowls ocluida | 530 | 0.160 | 0.151 | -0.87 |
| citypersons_convencion heavy | 733 | 0.164 | 0.145 | -1.92 |
| test_proxy severa | 101 | 0.309 | 0.344 | +3.42 |
| silueta_severa severa | 1858 | 0.036 | 0.030 | -0.61 |
| generativa_severa severa | 2018 | 0.027 | 0.023 | -0.40 |
| geometria_severa severa | 679 | 0.051 | 0.042 | -0.90 |
| profundidad_severa severa | 1629 | 0.015 | 0.014 | -0.05 |

Mayor diferencia en una fuente real: 3.42 pp (umbral declarado 2 pp: SUPERADO, H16 se interpreta con cautela)

