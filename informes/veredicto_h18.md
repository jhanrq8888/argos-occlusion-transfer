# ARGOS-11 — Veredictos de H18 (E14, réplica de H15 con 5 semillas y dosis del aumento)

Generado por `38_h18.py`. AP@0.5, media de semillas; IC 95 % por imágenes (regla) y jerárquico (criterio uniforme de semillas); * = pasa (+2 pp con IC > 0). Regla literal de `PREREGISTRO_H18.md`; predicción común: no se detecta transferencia («Refutada» = 2 o 3 fuentes pasan).

## E14 Faster R-CNN, siluetas, dosis base, 5 semillas (replica de H15)

| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| silueta_severa severa | 1858 | 0.032 | 0.176 | +14.44* | [+12.77; +16.30] | [+12.72; +16.43]* |
| nightowls ocluida | 530 | 0.148 | 0.191 | +4.26* | [+2.90; +5.49] | [+2.21; +6.32]* |
| citypersons_convencion heavy | 733 | 0.145 | 0.162 | +1.74 | [+0.50; +2.85] | [-0.08; +3.69] |
| test_proxy severa | 101 | 0.304 | 0.282 | -2.20 | [-6.12; +1.63] | [-6.92; +2.86] |

**Veredicto H18a: SOSTENIDA** (1 de 3 fuentes reales pasan; control pasa)

## E14 Faster R-CNN, siluetas, dosis baja

| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| silueta_severa severa | 1858 | 0.031 | 0.060 | +2.94* | [+2.28; +3.55] | [+2.02; +3.91]* |
| nightowls ocluida | 530 | 0.142 | 0.171 | +2.90* | [+1.69; +4.20] | [+0.82; +4.93]* |
| citypersons_convencion heavy | 733 | 0.142 | 0.159 | +1.74 | [+0.42; +2.77] | [-1.10; +4.10] |
| test_proxy severa | 101 | 0.302 | 0.283 | -1.91 | [-5.08; +2.00] | [-6.56; +3.24] |

**Veredicto H18e-baja: SOSTENIDA** (1 de 3 fuentes reales pasan; control pasa)

## E14 Faster R-CNN, siluetas, dosis alta

| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |
|---|---|---|---|---|---|---|
| silueta_severa severa | 1858 | 0.031 | 0.287 | +25.62* | [+23.41; +27.95] | [+23.13; +28.15]* |
| nightowls ocluida | 530 | 0.142 | 0.228 | +8.59* | [+6.12; +10.63] | [+5.65; +11.27]* |
| citypersons_convencion heavy | 733 | 0.142 | 0.180 | +3.78* | [+2.13; +5.33] | [+0.87; +6.35]* |
| test_proxy severa | 101 | 0.302 | 0.308 | +0.60 | [-4.10; +5.14] | [-5.23; +6.55] |

**Veredicto H18e-alta: REFUTADA** (2 de 3 fuentes reales pasan; control pasa)

## Secundario: dosis-respuesta (semillas 0-2, V3 − V1 en pp)

| Celda | baja | base | alta |
|---|---|---|---|
| silueta_severa severa | +2.94 | +14.77 | +25.62 |
| nightowls ocluida | +2.90 | +5.32 | +8.59 |
| citypersons_convencion heavy | +1.74 | +2.35 | +3.78 |
| test_proxy severa | -1.91 | -1.74 | +0.60 |

## Secundario: H18a frente a H15 (semillas 0-2, AP@0.5 medio en pp)

| Fuente | V1 H15 | V1 H18a | V3 H15 | V3 H18a |
|---|---|---|---|---|
| nightowls ocluida | 14.96 | 14.24 | 18.24 | 19.56 |
| citypersons_convencion heavy | 15.14 | 14.20 | 17.47 | 16.55 |
| test_proxy severa | 31.00 | 30.23 | 30.00 | 28.49 |
