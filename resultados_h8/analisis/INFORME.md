# ARGOS-11 - Informe de analisis estadistico

Corridas analizadas: 6 (rtdetr-l_V1_s0, rtdetr-l_V1_s1, rtdetr-l_V1_s2, rtdetr-l_V3_s0, rtdetr-l_V3_s1, rtdetr-l_V3_s2)
Bootstrap sobre imagenes: B = 1000, percentil, pareado entre corridas.

## 1. Descriptivo (media +- sd entre semillas, AP@0.5)

| conjunto | estrato | n_gt | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|---|
| citypersons_convencion | bare | 769 | 0.721 +- 0.043 | - | 0.649 +- 0.023 | - |
| citypersons_convencion | global | 2312 | 0.553 +- 0.029 | - | 0.501 +- 0.027 | - |
| citypersons_convencion | heavy | 733 | 0.185 +- 0.020 | - | 0.150 +- 0.011 | - |
| citypersons_convencion | partial | 810 | 0.589 +- 0.042 | - | 0.502 +- 0.036 | - |
| nightowls | global | 3293 | 0.716 +- 0.032 | - | 0.636 +- 0.007 | - |
| nightowls | ocluida | 530 | 0.268 +- 0.035 | - | 0.198 +- 0.022 | - |
| nightowls | sin | 2763 | 0.753 +- 0.036 | - | 0.671 +- 0.009 | - |
| silueta_severa | global | 2235 | 0.068 +- 0.003 | - | 0.212 +- 0.011 | - |
| silueta_severa | ligera | 56 | 0.167 +- 0.056 | - | 0.159 +- 0.031 | - |
| silueta_severa | moderada | 295 | 0.050 +- 0.007 | - | 0.167 +- 0.017 | - |
| silueta_severa | severa | 1858 | 0.036 +- 0.003 | - | 0.145 +- 0.010 | - |
| silueta_severa | sin | 26 | 0.386 +- 0.091 | - | 0.266 +- 0.086 | - |
| test_proxy | global | 2235 | 0.826 +- 0.008 | - | 0.810 +- 0.006 | - |
| test_proxy | ligera | 188 | 0.560 +- 0.041 | - | 0.500 +- 0.017 | - |
| test_proxy | moderada | 190 | 0.504 +- 0.023 | - | 0.443 +- 0.021 | - |
| test_proxy | severa | 101 | 0.236 +- 0.033 | - | 0.214 +- 0.015 | - |
| test_proxy | sin | 1756 | 0.832 +- 0.008 | - | 0.820 +- 0.004 | - |

## 2. Efectos con IC 95 % bootstrap (puntos porcentuales de AP@0.5)

| conjunto | estrato | contraste | delta | IC95 | excluye 0 |
|---|---|---|---|---|---|
| citypersons_convencion | global | V3-V1 | -5.20 | [-6.28, -3.99] | si |
| citypersons_convencion | bare | V3-V1 | -7.20 | [-8.96, -5.32] | si |
| citypersons_convencion | heavy | V3-V1 | -3.47 | [-4.86, -1.81] | si |
| citypersons_convencion | partial | V3-V1 | -8.71 | [-10.43, -6.76] | si |
| nightowls | global | V3-V1 | -8.07 | [-8.96, -7.12] | si |
| nightowls | sin | V3-V1 | -8.22 | [-9.17, -7.21] | si |
| nightowls | ocluida | V3-V1 | -6.98 | [-8.95, -5.11] | si |
| silueta_severa | global | V3-V1 | +14.34 | [+13.01, +15.89] | si |
| silueta_severa | sin | V3-V1 | -11.98 | [-20.79, -2.03] | si |
| silueta_severa | ligera | V3-V1 | -0.78 | [-6.87, +4.96] | no |
| silueta_severa | moderada | V3-V1 | +11.71 | [+8.78, +15.26] | si |
| silueta_severa | severa | V3-V1 | +10.97 | [+9.57, +12.36] | si |
| test_proxy | global | V3-V1 | -1.53 | [-2.38, -0.65] | si |
| test_proxy | sin | V3-V1 | -1.24 | [-2.09, -0.33] | si |
| test_proxy | ligera | V3-V1 | -6.05 | [-8.97, -2.89] | si |
| test_proxy | moderada | V3-V1 | -6.11 | [-9.29, -3.22] | si |
| test_proxy | severa | V3-V1 | -2.21 | [-6.16, +1.59] | no |

## 3. Tamano de efecto entre semillas (Hedges g; indicativo, n=3)

| conjunto | estrato | contraste | g |
|---|---|---|---|
| citypersons_convencion | global | V3-V1 | -1.46 |
| citypersons_convencion | bare | V3-V1 | -1.67 |
| citypersons_convencion | heavy | V3-V1 | -1.69 |
| citypersons_convencion | partial | V3-V1 | -1.78 |
| nightowls | global | V3-V1 | -2.78 |
| nightowls | sin | V3-V1 | -2.49 |
| nightowls | ocluida | V3-V1 | -1.89 |
| silueta_severa | global | V3-V1 | 14.21 |
| silueta_severa | sin | V3-V1 | -1.08 |
| silueta_severa | ligera | V3-V1 | -0.14 |
| silueta_severa | moderada | V3-V1 | 7.13 |
| silueta_severa | severa | V3-V1 | 11.76 |
| test_proxy | global | V3-V1 | -1.80 |
| test_proxy | sin | V3-V1 | -1.66 |
| test_proxy | ligera | V3-V1 | -1.56 |
| test_proxy | moderada | V3-V1 | -2.22 |
| test_proxy | severa | V3-V1 | -0.69 |

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
