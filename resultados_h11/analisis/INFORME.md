# ARGOS-11 - Informe de analisis estadistico

Corridas analizadas: 6 (V1_s3, V1_s4, V1_s5, V3_s3, V3_s4, V3_s5)
Bootstrap sobre imagenes: B = 1000, percentil, pareado entre corridas.

## 1. Descriptivo (media +- sd entre semillas, AP@0.5)

| conjunto | estrato | n_gt | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|---|
| citypersons_convencion | bare | 769 | 0.900 +- 0.007 | - | 0.907 +- 0.001 | - |
| citypersons_convencion | global | 2312 | 0.800 +- 0.004 | - | 0.804 +- 0.000 | - |
| citypersons_convencion | heavy | 733 | 0.591 +- 0.012 | - | 0.604 +- 0.004 | - |
| citypersons_convencion | partial | 810 | 0.850 +- 0.001 | - | 0.854 +- 0.003 | - |
| cp_silueta_severa | global | 769 | 0.126 +- 0.002 | - | 0.398 +- 0.013 | - |
| cp_silueta_severa | ligera | 12 | 0.429 +- 0.050 | - | 0.415 +- 0.029 | - |
| cp_silueta_severa | moderada | 61 | 0.067 +- 0.010 | - | 0.233 +- 0.024 | - |
| cp_silueta_severa | severa | 684 | 0.095 +- 0.003 | - | 0.342 +- 0.014 | - |
| cp_silueta_severa | sin | 12 | 0.569 +- 0.069 | - | 0.506 +- 0.050 | - |
| nightowls | global | 3293 | 0.436 +- 0.018 | - | 0.468 +- 0.040 | - |
| nightowls | ocluida | 530 | 0.146 +- 0.009 | - | 0.166 +- 0.018 | - |
| nightowls | sin | 2763 | 0.466 +- 0.019 | - | 0.499 +- 0.041 | - |
| test_proxy | global | 2235 | 0.385 +- 0.026 | - | 0.454 +- 0.011 | - |
| test_proxy | ligera | 188 | 0.293 +- 0.018 | - | 0.296 +- 0.008 | - |
| test_proxy | moderada | 190 | 0.268 +- 0.013 | - | 0.256 +- 0.009 | - |
| test_proxy | severa | 101 | 0.109 +- 0.014 | - | 0.085 +- 0.018 | - |
| test_proxy | sin | 1756 | 0.379 +- 0.030 | - | 0.455 +- 0.012 | - |

## 2. Efectos con IC 95 % bootstrap (puntos porcentuales de AP@0.5)

| conjunto | estrato | contraste | delta | IC95 | excluye 0 |
|---|---|---|---|---|---|
| citypersons_convencion | global | V3-V1 | +0.43 | [-0.18, +1.07] | no |
| citypersons_convencion | bare | V3-V1 | +0.72 | [+0.02, +1.41] | si |
| citypersons_convencion | heavy | V3-V1 | +1.31 | [-0.28, +2.78] | no |
| citypersons_convencion | partial | V3-V1 | +0.44 | [-0.36, +1.21] | no |
| cp_silueta_severa | global | V3-V1 | +27.26 | [+24.21, +30.06] | si |
| cp_silueta_severa | sin | V3-V1 | -6.31 | [-17.87, +3.04] | no |
| cp_silueta_severa | ligera | V3-V1 | -1.33 | [-13.90, +6.34] | no |
| cp_silueta_severa | moderada | V3-V1 | +16.59 | [+10.57, +25.49] | si |
| cp_silueta_severa | severa | V3-V1 | +24.66 | [+21.62, +27.47] | si |
| nightowls | global | V3-V1 | +3.27 | [+2.64, +3.92] | si |
| nightowls | sin | V3-V1 | +3.34 | [+2.61, +4.00] | si |
| nightowls | ocluida | V3-V1 | +1.95 | [+0.93, +3.21] | si |
| test_proxy | global | V3-V1 | +6.91 | [+5.69, +8.07] | si |
| test_proxy | sin | V3-V1 | +7.64 | [+6.39, +8.95] | si |
| test_proxy | ligera | V3-V1 | +0.34 | [-2.94, +4.07] | no |
| test_proxy | moderada | V3-V1 | -1.22 | [-3.86, +1.60] | no |
| test_proxy | severa | V3-V1 | -2.44 | [-6.77, +2.36] | no |

## 3. Tamano de efecto entre semillas (Hedges g; indicativo, n=3)

| conjunto | estrato | contraste | g |
|---|---|---|---|
| citypersons_convencion | global | V3-V1 | 1.16 |
| citypersons_convencion | bare | V3-V1 | 1.13 |
| citypersons_convencion | heavy | V3-V1 | 1.15 |
| citypersons_convencion | partial | V3-V1 | 1.53 |
| cp_silueta_severa | global | V3-V1 | 24.31 |
| cp_silueta_severa | sin | V3-V1 | -0.84 |
| cp_silueta_severa | ligera | V3-V1 | -0.26 |
| cp_silueta_severa | moderada | V3-V1 | 7.15 |
| cp_silueta_severa | severa | V3-V1 | 20.23 |
| nightowls | global | V3-V1 | 0.84 |
| nightowls | sin | V3-V1 | 0.83 |
| nightowls | ocluida | V3-V1 | 1.08 |
| test_proxy | global | V3-V1 | 2.72 |
| test_proxy | sin | V3-V1 | 2.68 |
| test_proxy | ligera | V3-V1 | 0.20 |
| test_proxy | moderada | V3-V1 | -0.85 |
| test_proxy | severa | V3-V1 | -1.21 |

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
