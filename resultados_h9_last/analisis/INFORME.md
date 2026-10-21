# ARGOS-11 - Informe de analisis estadistico

Corridas analizadas: 6 (V1_s0, V1_s1, V1_s2, V3_s0, V3_s1, V3_s2)
Bootstrap sobre imagenes: B = 1000, percentil, pareado entre corridas.

## 1. Descriptivo (media +- sd entre semillas, AP@0.5)

| conjunto | estrato | n_gt | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|---|
| citypersons_convencion | bare | 769 | 0.501 +- 0.039 | - | 0.475 +- 0.009 | - |
| citypersons_convencion | global | 2312 | 0.365 +- 0.025 | - | 0.351 +- 0.001 | - |
| citypersons_convencion | heavy | 733 | 0.086 +- 0.015 | - | 0.081 +- 0.005 | - |
| citypersons_convencion | partial | 810 | 0.362 +- 0.034 | - | 0.338 +- 0.009 | - |
| generativa_severa | global | 2235 | 0.070 +- 0.005 | - | 0.167 +- 0.004 | - |
| generativa_severa | ligera | 23 | 0.507 +- 0.060 | - | 0.447 +- 0.078 | - |
| generativa_severa | moderada | 153 | 0.186 +- 0.032 | - | 0.239 +- 0.019 | - |
| generativa_severa | severa | 2018 | 0.024 +- 0.004 | - | 0.106 +- 0.008 | - |
| generativa_severa | sin | 41 | 0.621 +- 0.075 | - | 0.597 +- 0.042 | - |
| nightowls | global | 3293 | 0.543 +- 0.030 | - | 0.525 +- 0.066 | - |
| nightowls | ocluida | 530 | 0.136 +- 0.028 | - | 0.128 +- 0.046 | - |
| nightowls | sin | 2763 | 0.574 +- 0.033 | - | 0.557 +- 0.070 | - |
| silueta_severa | global | 2235 | 0.054 +- 0.003 | - | 0.060 +- 0.003 | - |
| silueta_severa | ligera | 56 | 0.114 +- 0.003 | - | 0.140 +- 0.023 | - |
| silueta_severa | moderada | 295 | 0.042 +- 0.002 | - | 0.049 +- 0.007 | - |
| silueta_severa | severa | 1858 | 0.025 +- 0.002 | - | 0.028 +- 0.002 | - |
| silueta_severa | sin | 26 | 0.254 +- 0.043 | - | 0.345 +- 0.033 | - |
| test_proxy | global | 2235 | 0.776 +- 0.003 | - | 0.785 +- 0.005 | - |
| test_proxy | ligera | 188 | 0.479 +- 0.021 | - | 0.515 +- 0.019 | - |
| test_proxy | moderada | 190 | 0.401 +- 0.030 | - | 0.431 +- 0.009 | - |
| test_proxy | severa | 101 | 0.181 +- 0.042 | - | 0.192 +- 0.033 | - |
| test_proxy | sin | 1756 | 0.791 +- 0.003 | - | 0.799 +- 0.008 | - |

## 2. Efectos con IC 95 % bootstrap (puntos porcentuales de AP@0.5)

| conjunto | estrato | contraste | delta | IC95 | excluye 0 |
|---|---|---|---|---|---|
| citypersons_convencion | global | V3-V1 | -1.45 | [-2.23, -0.62] | si |
| citypersons_convencion | bare | V3-V1 | -2.51 | [-3.74, -1.31] | si |
| citypersons_convencion | heavy | V3-V1 | -0.50 | [-1.36, +0.34] | no |
| citypersons_convencion | partial | V3-V1 | -2.40 | [-3.59, -1.21] | si |
| generativa_severa | global | V3-V1 | +9.78 | [+8.72, +10.98] | si |
| generativa_severa | sin | V3-V1 | -2.41 | [-9.09, +4.76] | no |
| generativa_severa | ligera | V3-V1 | -5.99 | [-16.84, +5.09] | no |
| generativa_severa | moderada | V3-V1 | +5.28 | [+1.81, +9.22] | si |
| generativa_severa | severa | V3-V1 | +8.25 | [+7.24, +9.46] | si |
| nightowls | global | V3-V1 | -1.79 | [-2.62, -0.89] | si |
| nightowls | sin | V3-V1 | -1.73 | [-2.71, -0.75] | si |
| nightowls | ocluida | V3-V1 | -0.81 | [-1.90, +0.45] | no |
| silueta_severa | global | V3-V1 | +0.65 | [+0.18, +1.14] | si |
| silueta_severa | sin | V3-V1 | +9.09 | [+1.22, +16.71] | si |
| silueta_severa | ligera | V3-V1 | +2.53 | [-1.14, +5.61] | no |
| silueta_severa | moderada | V3-V1 | +0.70 | [-0.66, +1.68] | no |
| silueta_severa | severa | V3-V1 | +0.27 | [+0.01, +0.70] | si |
| test_proxy | global | V3-V1 | +0.94 | [+0.21, +1.76] | si |
| test_proxy | sin | V3-V1 | +0.74 | [-0.11, +1.58] | no |
| test_proxy | ligera | V3-V1 | +3.58 | [-0.10, +6.69] | no |
| test_proxy | moderada | V3-V1 | +2.98 | [-0.39, +6.19] | no |
| test_proxy | severa | V3-V1 | +1.07 | [-3.43, +5.28] | no |

## 3. Tamano de efecto entre semillas (Hedges g; indicativo, n=3)

| conjunto | estrato | contraste | g |
|---|---|---|---|
| citypersons_convencion | global | V3-V1 | -0.67 |
| citypersons_convencion | bare | V3-V1 | -0.70 |
| citypersons_convencion | heavy | V3-V1 | -0.35 |
| citypersons_convencion | partial | V3-V1 | -0.77 |
| generativa_severa | global | V3-V1 | 16.91 |
| generativa_severa | sin | V3-V1 | -0.32 |
| generativa_severa | ligera | V3-V1 | -0.69 |
| generativa_severa | moderada | V3-V1 | 1.62 |
| generativa_severa | severa | V3-V1 | 10.18 |
| nightowls | global | V3-V1 | -0.28 |
| nightowls | sin | V3-V1 | -0.25 |
| nightowls | ocluida | V3-V1 | -0.17 |
| silueta_severa | global | V3-V1 | 1.94 |
| silueta_severa | sin | V3-V1 | 1.90 |
| silueta_severa | ligera | V3-V1 | 1.24 |
| silueta_severa | moderada | V3-V1 | 1.15 |
| silueta_severa | severa | V3-V1 | 1.03 |
| test_proxy | global | V3-V1 | 1.76 |
| test_proxy | sin | V3-V1 | 1.00 |
| test_proxy | ligera | V3-V1 | 1.43 |
| test_proxy | moderada | V3-V1 | 1.07 |
| test_proxy | severa | V3-V1 | 0.23 |

## 4. ANOVA 2x2 (EXPLORATORIO, sin valor confirmatorio)

| conjunto | estrato | factor | F | p |
|---|---|---|---|---|

## 5. Criterios de exito e hipotesis

```
{
 "fuente_real_propia": "test_real",
 "estratos_H1": [
  "moderada",
  "severa"
 ],
 "H1_AP_criterios_a_b": null,
 "criterio_c_fps_ge_30": false,
 "H1_fps_ge_90pct_baseline": null,
 "H2": null,
 "H3": null,
 "nota": "Inferencia basada en semillas: indicativa (n=3). El IC bootstrap sobre imagenes es el ancla del criterio (b)."
}
```

Confirmatorio: marginales por estrato agregando iluminacion. El cruce luz x estrato esta en
resultados/resumen_ap.csv y es exploratorio. Figuras en figuras/.
