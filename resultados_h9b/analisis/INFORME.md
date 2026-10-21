# ARGOS-11 - Informe de analisis estadistico

Corridas analizadas: 6 (V1_s0, V1_s1, V1_s2, V3_s0, V3_s1, V3_s2)
Bootstrap sobre imagenes: B = 1000, percentil, pareado entre corridas.

## 1. Descriptivo (media +- sd entre semillas, AP@0.5)

| conjunto | estrato | n_gt | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|---|
| citypersons_convencion | bare | 769 | 0.473 +- 0.017 | - | 0.526 +- 0.012 | - |
| citypersons_convencion | global | 2312 | 0.347 +- 0.012 | - | 0.378 +- 0.008 | - |
| citypersons_convencion | heavy | 733 | 0.081 +- 0.008 | - | 0.096 +- 0.011 | - |
| citypersons_convencion | partial | 810 | 0.331 +- 0.014 | - | 0.373 +- 0.010 | - |
| generativa_severa | global | 2235 | 0.077 +- 0.003 | - | 0.246 +- 0.004 | - |
| generativa_severa | ligera | 23 | 0.564 +- 0.042 | - | 0.501 +- 0.073 | - |
| generativa_severa | moderada | 153 | 0.209 +- 0.013 | - | 0.309 +- 0.014 | - |
| generativa_severa | severa | 2018 | 0.028 +- 0.005 | - | 0.180 +- 0.006 | - |
| generativa_severa | sin | 41 | 0.657 +- 0.041 | - | 0.695 +- 0.031 | - |
| nightowls | global | 3293 | 0.576 +- 0.010 | - | 0.585 +- 0.007 | - |
| nightowls | ocluida | 530 | 0.169 +- 0.004 | - | 0.169 +- 0.009 | - |
| nightowls | sin | 2763 | 0.607 +- 0.009 | - | 0.619 +- 0.006 | - |
| silueta_severa | global | 2235 | 0.059 +- 0.001 | - | 0.068 +- 0.001 | - |
| silueta_severa | ligera | 56 | 0.185 +- 0.014 | - | 0.164 +- 0.003 | - |
| silueta_severa | moderada | 295 | 0.051 +- 0.010 | - | 0.059 +- 0.006 | - |
| silueta_severa | severa | 1858 | 0.027 +- 0.002 | - | 0.031 +- 0.000 | - |
| silueta_severa | sin | 26 | 0.257 +- 0.033 | - | 0.260 +- 0.027 | - |
| test_proxy | global | 2235 | 0.811 +- 0.004 | - | 0.802 +- 0.007 | - |
| test_proxy | ligera | 188 | 0.561 +- 0.016 | - | 0.529 +- 0.010 | - |
| test_proxy | moderada | 190 | 0.473 +- 0.014 | - | 0.451 +- 0.013 | - |
| test_proxy | severa | 101 | 0.257 +- 0.028 | - | 0.226 +- 0.018 | - |
| test_proxy | sin | 1756 | 0.824 +- 0.005 | - | 0.815 +- 0.007 | - |

## 2. Efectos con IC 95 % bootstrap (puntos porcentuales de AP@0.5)

| conjunto | estrato | contraste | delta | IC95 | excluye 0 |
|---|---|---|---|---|---|
| citypersons_convencion | global | V3-V1 | +3.12 | [+2.32, +3.97] | si |
| citypersons_convencion | bare | V3-V1 | +5.24 | [+3.61, +6.93] | si |
| citypersons_convencion | heavy | V3-V1 | +1.52 | [+0.79, +2.66] | si |
| citypersons_convencion | partial | V3-V1 | +4.13 | [+2.95, +5.40] | si |
| generativa_severa | global | V3-V1 | +16.96 | [+15.57, +18.69] | si |
| generativa_severa | sin | V3-V1 | +3.82 | [-5.40, +11.13] | no |
| generativa_severa | ligera | V3-V1 | -6.34 | [-16.49, +4.84] | no |
| generativa_severa | moderada | V3-V1 | +10.04 | [+5.38, +15.62] | si |
| generativa_severa | severa | V3-V1 | +15.23 | [+14.00, +17.16] | si |
| nightowls | global | V3-V1 | +0.83 | [+0.05, +1.60] | si |
| nightowls | sin | V3-V1 | +1.18 | [+0.32, +2.01] | si |
| nightowls | ocluida | V3-V1 | +0.01 | [-1.02, +1.20] | no |
| silueta_severa | global | V3-V1 | +0.87 | [+0.37, +1.45] | si |
| silueta_severa | sin | V3-V1 | +0.28 | [-7.31, +8.99] | no |
| silueta_severa | ligera | V3-V1 | -2.15 | [-7.07, +2.67] | no |
| silueta_severa | moderada | V3-V1 | +0.75 | [-0.35, +2.30] | no |
| silueta_severa | severa | V3-V1 | +0.40 | [-0.01, +0.88] | no |
| test_proxy | global | V3-V1 | -0.93 | [-1.62, -0.22] | si |
| test_proxy | sin | V3-V1 | -0.99 | [-1.71, -0.23] | si |
| test_proxy | ligera | V3-V1 | -3.14 | [-6.04, +0.37] | no |
| test_proxy | moderada | V3-V1 | -2.18 | [-5.00, +1.68] | no |
| test_proxy | severa | V3-V1 | -3.03 | [-6.77, +0.99] | no |

## 3. Tamano de efecto entre semillas (Hedges g; indicativo, n=3)

| conjunto | estrato | contraste | g |
|---|---|---|---|
| citypersons_convencion | global | V3-V1 | 2.41 |
| citypersons_convencion | bare | V3-V1 | 2.88 |
| citypersons_convencion | heavy | V3-V1 | 1.26 |
| citypersons_convencion | partial | V3-V1 | 2.70 |
| generativa_severa | global | V3-V1 | 39.90 |
| generativa_severa | sin | V3-V1 | 0.84 |
| generativa_severa | ligera | V3-V1 | -0.86 |
| generativa_severa | moderada | V3-V1 | 6.01 |
| generativa_severa | severa | V3-V1 | 22.06 |
| nightowls | global | V3-V1 | 0.81 |
| nightowls | sin | V3-V1 | 1.25 |
| nightowls | ocluida | V3-V1 | 0.01 |
| silueta_severa | global | V3-V1 | 6.26 |
| silueta_severa | sin | V3-V1 | 0.07 |
| silueta_severa | ligera | V3-V1 | -1.66 |
| silueta_severa | moderada | V3-V1 | 0.75 |
| silueta_severa | severa | V3-V1 | 2.06 |
| test_proxy | global | V3-V1 | -1.29 |
| test_proxy | sin | V3-V1 | -1.27 |
| test_proxy | ligera | V3-V1 | -1.91 |
| test_proxy | moderada | V3-V1 | -1.27 |
| test_proxy | severa | V3-V1 | -1.02 |

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
