# ARGOS-11 — Veredicto de H12 (E10, YOLOv11m) y extensión de semillas de E7b y E8

Generado por `30_h12.py`. AP@0.5, media de semillas. IC 95 % por imágenes (1 000 réplicas, criterio) y jerárquico (semillas + imágenes, 2 000 réplicas). Regla literal de `PREREGISTRO_H12.md`, sección 2. *: supera +2 pp con IC por imágenes > 0.

## E10 YOLOv11m, siluetas (H12a)

| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| silueta_severa severa (control) | 1858 | 0.028 | 0.172 | +14.45* | [+12.76; +16.37] | [+12.67; +16.46] |
| nightowls ocluida | 530 | 0.213 | 0.209 | -0.39 | [-1.55; +0.89] | [-3.92; +2.77] |
| citypersons_convencion heavy | 733 | 0.112 | 0.115 | +0.25 | [-0.63; +1.27] | [-1.32; +2.12] |
| test_proxy severa | 101 | 0.266 | 0.296 | +3.04 | [-1.07; +6.63] | [-2.63; +8.31] |

**H12a: SOSTENIDA** (0 de 3 fuentes reales superan +2 pp con IC por imágenes > 0; la regla exige 2 para refutar).

## E10 YOLOv11m, generativa (H12b)

| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| generativa_severa severa (control) | 2018 | 0.029 | 0.219 | +19.04* | [+17.49; +21.03] | [+17.35; +21.21] |
| nightowls ocluida | 530 | 0.213 | 0.220 | +0.78 | [-0.42; +2.16] | [-3.21; +4.28] |
| citypersons_convencion heavy | 733 | 0.112 | 0.123 | +1.11 | [+0.14; +2.16] | [-0.47; +2.89] |
| test_proxy severa | 101 | 0.266 | 0.261 | -0.56 | [-4.07; +3.19] | [-5.77; +5.06] |

**H12b: SOSTENIDA** (0 de 3 fuentes reales superan +2 pp con IC por imágenes > 0; la regla exige 2 para refutar).

## E7b con 5 semillas (YOLOv11s, generativa)

| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| generativa_severa severa (control) | 2018 | 0.028 | 0.179 | +15.10* | [+13.76; +16.76] | [+13.77; +16.90] |
| nightowls ocluida | 530 | 0.167 | 0.163 | -0.45 | [-1.28; +0.60] | [-1.99; +1.23] |
| citypersons_convencion heavy | 733 | 0.082 | 0.085 | +0.22 | [-0.37; +1.02] | [-1.39; +2.00] |
| test_proxy severa | 101 | 0.242 | 0.225 | -1.75 | [-4.79; +1.83] | [-6.80; +3.46] |

Secundario (no decide): 0 de 3 fuentes reales superan +2 pp con IC por imágenes > 0 y 0 con IC jerárquico > 0. Según el pre-registro, solo una celda que supere con el IC jerárquico se reportaría como contraria a la conclusión con 3 semillas.

## E8 siluetas con 5 semillas (YOLOv11s)

| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| silueta_severa severa (control) | 1858 | 0.027 | 0.137 | +11.00* | [+9.66; +12.59] | [+9.64; +12.69] |
| nightowls ocluida | 530 | 0.167 | 0.157 | -1.06 | [-1.89; -0.03] | [-2.36; +0.39] |
| citypersons_convencion heavy | 733 | 0.082 | 0.103 | +2.06* | [+1.40; +2.99] | [+0.26; +4.17] |
| test_proxy severa | 101 | 0.242 | 0.222 | -2.06 | [-5.37; +0.97] | [-7.27; +2.65] |

Secundario (no decide): 1 de 3 fuentes reales superan +2 pp con IC por imágenes > 0 y 1 con IC jerárquico > 0. Según el pre-registro, solo una celda que supere con el IC jerárquico se reportaría como contraria a la conclusión con 3 semillas.

## E7b solo semillas 3-4 (RunPod)

| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| generativa_severa severa (control) | 2018 | 0.027 | 0.176 | +14.89* | [+13.49; +16.43] | [+13.34; +16.54] |
| nightowls ocluida | 530 | 0.165 | 0.154 | -1.13 | [-2.33; +0.05] | [-3.48; +1.61] |
| citypersons_convencion heavy | 733 | 0.085 | 0.068 | -1.74 | [-2.77; -0.75] | [-3.17; -0.23] |
| test_proxy severa | 101 | 0.221 | 0.223 | +0.18 | [-4.55; +4.59] | [-7.02; +6.75] |

Secundario (no decide): 0 de 3 fuentes reales superan +2 pp con IC por imágenes > 0 y 0 con IC jerárquico > 0. Según el pre-registro, solo una celda que supere con el IC jerárquico se reportaría como contraria a la conclusión con 3 semillas.

## E8 siluetas solo semillas 3-4 (RunPod)

| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| silueta_severa severa (control) | 1858 | 0.027 | 0.137 | +11.01* | [+9.61; +12.68] | [+9.44; +12.91] |
| nightowls ocluida | 530 | 0.165 | 0.155 | -0.96 | [-2.22; +0.32] | [-3.16; +1.37] |
| citypersons_convencion heavy | 733 | 0.085 | 0.103 | +1.75 | [+0.71; +2.89] | [-1.84; +5.70] |
| test_proxy severa | 101 | 0.221 | 0.222 | +0.10 | [-3.91; +4.46] | [-6.50; +6.13] |

Secundario (no decide): 0 de 3 fuentes reales superan +2 pp con IC por imágenes > 0 y 0 con IC jerárquico > 0. Según el pre-registro, solo una celda que supere con el IC jerárquico se reportaría como contraria a la conclusión con 3 semillas.

