# ARGOS-11 - Informe de analisis estadistico

Corridas analizadas: 6 (V1_s0, V1_s1, V1_s2, V3_s0, V3_s1, V3_s2)
Bootstrap sobre imagenes: B = 1000, percentil, pareado entre corridas.

## 1. Descriptivo (media +- sd entre semillas, AP@0.5)

| conjunto | estrato | n_gt | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|---|
| citypersons_convencion | bare | 769 | 0.671 +- 0.044 | - | 0.692 +- 0.037 | - |
| citypersons_convencion | global | 2312 | 0.522 +- 0.032 | - | 0.533 +- 0.030 | - |
| citypersons_convencion | heavy | 733 | 0.153 +- 0.026 | - | 0.165 +- 0.015 | - |
| citypersons_convencion | partial | 810 | 0.540 +- 0.039 | - | 0.563 +- 0.031 | - |
| generativa_severa | global | 2235 | 0.071 +- 0.006 | - | 0.101 +- 0.027 | - |
| generativa_severa | ligera | 23 | 0.518 +- 0.079 | - | 0.562 +- 0.060 | - |
| generativa_severa | moderada | 153 | 0.184 +- 0.011 | - | 0.222 +- 0.049 | - |
| generativa_severa | severa | 2018 | 0.018 +- 0.003 | - | 0.044 +- 0.022 | - |
| generativa_severa | sin | 41 | 0.700 +- 0.053 | - | 0.726 +- 0.042 | - |
| nightowls | global | 3293 | 0.724 +- 0.009 | - | 0.711 +- 0.011 | - |
| nightowls | ocluida | 530 | 0.306 +- 0.011 | - | 0.287 +- 0.010 | - |
| nightowls | sin | 2763 | 0.759 +- 0.010 | - | 0.748 +- 0.013 | - |
| silueta_severa | global | 2235 | 0.080 +- 0.002 | - | 0.077 +- 0.003 | - |
| silueta_severa | ligera | 56 | 0.204 +- 0.020 | - | 0.189 +- 0.024 | - |
| silueta_severa | moderada | 295 | 0.074 +- 0.010 | - | 0.062 +- 0.001 | - |
| silueta_severa | severa | 1858 | 0.041 +- 0.003 | - | 0.040 +- 0.001 | - |
| silueta_severa | sin | 26 | 0.391 +- 0.103 | - | 0.378 +- 0.075 | - |
| test_proxy | global | 2235 | 0.811 +- 0.009 | - | 0.811 +- 0.007 | - |
| test_proxy | ligera | 188 | 0.548 +- 0.040 | - | 0.567 +- 0.014 | - |
| test_proxy | moderada | 190 | 0.464 +- 0.050 | - | 0.475 +- 0.011 | - |
| test_proxy | severa | 101 | 0.244 +- 0.026 | - | 0.272 +- 0.005 | - |
| test_proxy | sin | 1756 | 0.816 +- 0.013 | - | 0.816 +- 0.010 | - |

## 2. Efectos con IC 95 % bootstrap (puntos porcentuales de AP@0.5)

| conjunto | estrato | contraste | delta | IC95 | excluye 0 |
|---|---|---|---|---|---|
| citypersons_convencion | global | V3-V1 | +1.18 | [+0.61, +1.79] | si |
| citypersons_convencion | bare | V3-V1 | +2.07 | [+1.00, +3.35] | si |
| citypersons_convencion | heavy | V3-V1 | +1.23 | [+0.36, +2.11] | si |
| citypersons_convencion | partial | V3-V1 | +2.32 | [+1.38, +3.34] | si |
| generativa_severa | global | V3-V1 | +3.03 | [+2.59, +3.53] | si |
| generativa_severa | sin | V3-V1 | +2.56 | [-1.63, +6.33] | no |
| generativa_severa | ligera | V3-V1 | +4.39 | [-1.99, +8.46] | no |
| generativa_severa | moderada | V3-V1 | +3.75 | [+1.80, +5.49] | si |
| generativa_severa | severa | V3-V1 | +2.60 | [+2.12, +3.09] | si |
| nightowls | global | V3-V1 | -1.34 | [-1.71, -0.98] | si |
| nightowls | sin | V3-V1 | -1.14 | [-1.51, -0.77] | si |
| nightowls | ocluida | V3-V1 | -1.93 | [-2.89, -0.88] | si |
| silueta_severa | global | V3-V1 | -0.30 | [-0.63, +0.07] | no |
| silueta_severa | sin | V3-V1 | -1.31 | [-6.92, +3.93] | no |
| silueta_severa | ligera | V3-V1 | -1.48 | [-4.30, +1.69] | no |
| silueta_severa | moderada | V3-V1 | -1.17 | [-2.51, -0.20] | si |
| silueta_severa | severa | V3-V1 | -0.10 | [-0.39, +0.20] | no |
| test_proxy | global | V3-V1 | -0.03 | [-0.46, +0.38] | no |
| test_proxy | sin | V3-V1 | +0.06 | [-0.44, +0.52] | no |
| test_proxy | ligera | V3-V1 | +1.89 | [-0.18, +3.74] | no |
| test_proxy | moderada | V3-V1 | +1.15 | [-1.08, +3.26] | no |
| test_proxy | severa | V3-V1 | +2.82 | [+0.37, +5.99] | si |

## 3. Tamano de efecto entre semillas (Hedges g; indicativo, n=3)

| conjunto | estrato | contraste | g |
|---|---|---|---|
| citypersons_convencion | global | V3-V1 | 0.30 |
| citypersons_convencion | bare | V3-V1 | 0.41 |
| citypersons_convencion | heavy | V3-V1 | 0.47 |
| citypersons_convencion | partial | V3-V1 | 0.53 |
| generativa_severa | global | V3-V1 | 1.25 |
| generativa_severa | sin | V3-V1 | 0.43 |
| generativa_severa | ligera | V3-V1 | 0.50 |
| generativa_severa | moderada | V3-V1 | 0.84 |
| generativa_severa | severa | V3-V1 | 1.34 |
| nightowls | global | V3-V1 | -1.07 |
| nightowls | sin | V3-V1 | -0.81 |
| nightowls | ocluida | V3-V1 | -1.52 |
| silueta_severa | global | V3-V1 | -1.02 |
| silueta_severa | sin | V3-V1 | -0.12 |
| silueta_severa | ligera | V3-V1 | -0.54 |
| silueta_severa | moderada | V3-V1 | -1.33 |
| silueta_severa | severa | V3-V1 | -0.41 |
| test_proxy | global | V3-V1 | -0.03 |
| test_proxy | sin | V3-V1 | 0.04 |
| test_proxy | ligera | V3-V1 | 0.50 |
| test_proxy | moderada | V3-V1 | 0.26 |
| test_proxy | severa | V3-V1 | 1.21 |

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
