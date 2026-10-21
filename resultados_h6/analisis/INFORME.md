# ARGOS-11 - Informe de analisis estadistico

Corridas analizadas: 6 (V1_s0, V1_s1, V1_s2, V3_s0, V3_s1, V3_s2)
Bootstrap sobre imagenes: B = 1000, percentil, pareado entre corridas.

## 1. Descriptivo (media +- sd entre semillas, AP@0.5)

| conjunto | estrato | n_gt | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|---|
| citypersons | global | 3157 | 0.676 +- 0.002 | - | 0.685 +- 0.004 | - |
| citypersons | ligera | 908 | 0.735 +- 0.005 | - | 0.744 +- 0.005 | - |
| citypersons | moderada | 926 | 0.527 +- 0.013 | - | 0.543 +- 0.011 | - |
| citypersons | severa | 397 | 0.263 +- 0.006 | - | 0.288 +- 0.008 | - |
| citypersons | sin | 926 | 0.800 +- 0.004 | - | 0.810 +- 0.002 | - |
| citypersons_convencion | bare | 769 | 0.900 +- 0.002 | - | 0.904 +- 0.003 | - |
| citypersons_convencion | global | 2312 | 0.796 +- 0.005 | - | 0.802 +- 0.004 | - |
| citypersons_convencion | heavy | 733 | 0.583 +- 0.019 | - | 0.601 +- 0.006 | - |
| citypersons_convencion | partial | 810 | 0.848 +- 0.003 | - | 0.851 +- 0.006 | - |
| cp_silueta_ligera | global | 769 | 0.828 +- 0.001 | - | 0.874 +- 0.003 | - |
| cp_silueta_ligera | ligera | 649 | 0.850 +- 0.000 | - | 0.880 +- 0.004 | - |
| cp_silueta_ligera | moderada | 86 | 0.550 +- 0.016 | - | 0.644 +- 0.018 | - |
| cp_silueta_ligera | severa | 16 | 0.057 +- 0.018 | - | 0.059 +- 0.005 | - |
| cp_silueta_ligera | sin | 18 | 0.413 +- 0.039 | - | 0.513 +- 0.013 | - |
| cp_silueta_moderada | global | 769 | 0.630 +- 0.002 | - | 0.797 +- 0.012 | - |
| cp_silueta_moderada | ligera | 27 | 0.468 +- 0.034 | - | 0.585 +- 0.061 | - |
| cp_silueta_moderada | moderada | 629 | 0.663 +- 0.001 | - | 0.817 +- 0.011 | - |
| cp_silueta_moderada | severa | 108 | 0.249 +- 0.013 | - | 0.349 +- 0.038 | - |
| cp_silueta_moderada | sin | 5 | 0.449 +- 0.054 | - | 0.296 +- 0.059 | - |
| cp_silueta_severa | global | 769 | 0.134 +- 0.006 | - | 0.394 +- 0.012 | - |
| cp_silueta_severa | ligera | 12 | 0.424 +- 0.019 | - | 0.441 +- 0.079 | - |
| cp_silueta_severa | moderada | 61 | 0.089 +- 0.009 | - | 0.195 +- 0.004 | - |
| cp_silueta_severa | severa | 684 | 0.100 +- 0.006 | - | 0.337 +- 0.014 | - |
| cp_silueta_severa | sin | 12 | 0.529 +- 0.083 | - | 0.503 +- 0.051 | - |
| nightowls | global | 3293 | 0.489 +- 0.028 | - | 0.437 +- 0.019 | - |
| nightowls | ocluida | 530 | 0.163 +- 0.006 | - | 0.149 +- 0.010 | - |
| nightowls | sin | 2763 | 0.519 +- 0.029 | - | 0.466 +- 0.024 | - |
| test_proxy | global | 2235 | 0.423 +- 0.003 | - | 0.418 +- 0.003 | - |
| test_proxy | ligera | 188 | 0.298 +- 0.009 | - | 0.250 +- 0.028 | - |
| test_proxy | moderada | 190 | 0.258 +- 0.007 | - | 0.240 +- 0.014 | - |
| test_proxy | severa | 101 | 0.094 +- 0.021 | - | 0.103 +- 0.018 | - |
| test_proxy | sin | 1756 | 0.415 +- 0.004 | - | 0.421 +- 0.003 | - |

## 2. Efectos con IC 95 % bootstrap (puntos porcentuales de AP@0.5)

| conjunto | estrato | contraste | delta | IC95 | excluye 0 |
|---|---|---|---|---|---|
| citypersons | global | V3-V1 | +0.87 | [+0.21, +1.46] | si |
| citypersons | sin | V3-V1 | +0.98 | [+0.26, +1.69] | si |
| citypersons | ligera | V3-V1 | +0.96 | [+0.03, +1.93] | si |
| citypersons | moderada | V3-V1 | +1.52 | [+0.39, +2.63] | si |
| citypersons | severa | V3-V1 | +2.51 | [-0.01, +5.08] | no |
| citypersons_convencion | global | V3-V1 | +0.63 | [+0.02, +1.25] | si |
| citypersons_convencion | bare | V3-V1 | +0.41 | [-0.32, +1.05] | no |
| citypersons_convencion | heavy | V3-V1 | +1.82 | [+0.31, +3.31] | si |
| citypersons_convencion | partial | V3-V1 | +0.37 | [-0.51, +1.28] | no |
| cp_silueta_ligera | global | V3-V1 | +4.61 | [+3.18, +6.18] | si |
| cp_silueta_ligera | sin | V3-V1 | +10.01 | [-1.16, +20.07] | no |
| cp_silueta_ligera | ligera | V3-V1 | +2.99 | [+1.67, +4.52] | si |
| cp_silueta_ligera | moderada | V3-V1 | +9.40 | [+3.12, +15.90] | si |
| cp_silueta_ligera | severa | V3-V1 | +0.23 | [-2.38, +3.60] | no |
| cp_silueta_moderada | global | V3-V1 | +16.76 | [+14.31, +19.08] | si |
| cp_silueta_moderada | sin | V3-V1 | -15.32 | [-40.08, +11.43] | no |
| cp_silueta_moderada | ligera | V3-V1 | +11.62 | [-1.14, +26.46] | no |
| cp_silueta_moderada | moderada | V3-V1 | +15.38 | [+12.93, +17.97] | si |
| cp_silueta_moderada | severa | V3-V1 | +9.93 | [+3.46, +16.59] | si |
| cp_silueta_severa | global | V3-V1 | +26.00 | [+23.33, +28.82] | si |
| cp_silueta_severa | sin | V3-V1 | -2.59 | [-15.83, +11.16] | no |
| cp_silueta_severa | ligera | V3-V1 | +1.70 | [-7.34, +11.97] | no |
| cp_silueta_severa | moderada | V3-V1 | +10.65 | [+4.41, +19.40] | si |
| cp_silueta_severa | severa | V3-V1 | +23.74 | [+21.09, +26.51] | si |
| nightowls | global | V3-V1 | -5.12 | [-5.85, -4.40] | si |
| nightowls | sin | V3-V1 | -5.27 | [-6.07, -4.52] | si |
| nightowls | ocluida | V3-V1 | -1.35 | [-2.85, +0.20] | no |
| test_proxy | global | V3-V1 | -0.46 | [-1.85, +1.03] | no |
| test_proxy | sin | V3-V1 | +0.55 | [-0.79, +2.05] | no |
| test_proxy | ligera | V3-V1 | -4.79 | [-8.69, -1.16] | si |
| test_proxy | moderada | V3-V1 | -1.83 | [-5.05, +1.76] | no |
| test_proxy | severa | V3-V1 | +0.94 | [-2.53, +4.72] | no |

## 3. Tamano de efecto entre semillas (Hedges g; indicativo, n=3)

| conjunto | estrato | contraste | g |
|---|---|---|---|
| citypersons | global | V3-V1 | 1.97 |
| citypersons | sin | V3-V1 | 2.52 |
| citypersons | ligera | V3-V1 | 1.70 |
| citypersons | moderada | V3-V1 | 1.01 |
| citypersons | severa | V3-V1 | 2.80 |
| citypersons_convencion | global | V3-V1 | 1.16 |
| citypersons_convencion | bare | V3-V1 | 1.36 |
| citypersons_convencion | heavy | V3-V1 | 1.01 |
| citypersons_convencion | partial | V3-V1 | 0.61 |
| cp_silueta_ligera | global | V3-V1 | 16.40 |
| cp_silueta_ligera | sin | V3-V1 | 2.75 |
| cp_silueta_ligera | ligera | V3-V1 | 7.84 |
| cp_silueta_ligera | moderada | V3-V1 | 4.40 |
| cp_silueta_ligera | severa | V3-V1 | 0.14 |
| cp_silueta_moderada | global | V3-V1 | 15.92 |
| cp_silueta_moderada | sin | V3-V1 | -2.18 |
| cp_silueta_moderada | ligera | V3-V1 | 1.89 |
| cp_silueta_moderada | moderada | V3-V1 | 16.04 |
| cp_silueta_moderada | severa | V3-V1 | 2.78 |
| cp_silueta_severa | global | V3-V1 | 21.59 |
| cp_silueta_severa | sin | V3-V1 | -0.30 |
| cp_silueta_severa | ligera | V3-V1 | 0.24 |
| cp_silueta_severa | moderada | V3-V1 | 12.09 |
| cp_silueta_severa | severa | V3-V1 | 17.47 |
| nightowls | global | V3-V1 | -1.71 |
| nightowls | sin | V3-V1 | -1.58 |
| nightowls | ocluida | V3-V1 | -1.33 |
| test_proxy | global | V3-V1 | -1.20 |
| test_proxy | sin | V3-V1 | 1.25 |
| test_proxy | ligera | V3-V1 | -1.85 |
| test_proxy | moderada | V3-V1 | -1.38 |
| test_proxy | severa | V3-V1 | 0.39 |

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
