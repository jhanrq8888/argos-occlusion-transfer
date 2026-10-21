# ARGOS-11 - Informe de analisis estadistico

Corridas analizadas: 6 (V1_s0, V1_s1, V1_s2, V3_s0, V3_s1, V3_s2)
Bootstrap sobre imagenes: B = 1000, percentil, pareado entre corridas.

## 1. Descriptivo (media +- sd entre semillas, AP@0.5)

| conjunto | estrato | n_gt | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|---|
| citypersons_convencion | bare | 769 | 0.699 +- 0.020 | - | 0.543 +- 0.070 | - |
| citypersons_convencion | global | 2312 | 0.509 +- 0.023 | - | 0.387 +- 0.049 | - |
| citypersons_convencion | heavy | 733 | 0.155 +- 0.018 | - | 0.115 +- 0.039 | - |
| citypersons_convencion | partial | 810 | 0.538 +- 0.027 | - | 0.376 +- 0.069 | - |
| nightowls | global | 3293 | 0.857 +- 0.004 | - | 0.837 +- 0.004 | - |
| nightowls | ocluida | 530 | 0.395 +- 0.008 | - | 0.381 +- 0.008 | - |
| nightowls | sin | 2763 | 0.890 +- 0.005 | - | 0.872 +- 0.003 | - |
| test_proxy | global | 2235 | 0.686 +- 0.059 | - | 0.512 +- 0.090 | - |
| test_proxy | ligera | 188 | 0.444 +- 0.054 | - | 0.248 +- 0.099 | - |
| test_proxy | moderada | 190 | 0.317 +- 0.051 | - | 0.192 +- 0.070 | - |
| test_proxy | severa | 101 | 0.147 +- 0.040 | - | 0.055 +- 0.034 | - |
| test_proxy | sin | 1756 | 0.700 +- 0.064 | - | 0.523 +- 0.090 | - |

## 2. Efectos con IC 95 % bootstrap (puntos porcentuales de AP@0.5)

| conjunto | estrato | contraste | delta | IC95 | excluye 0 |
|---|---|---|---|---|---|
| citypersons_convencion | global | V3-V1 | -12.15 | [-13.66, -10.81] | si |
| citypersons_convencion | bare | V3-V1 | -15.61 | [-17.89, -13.45] | si |
| citypersons_convencion | heavy | V3-V1 | -3.94 | [-5.62, -2.27] | si |
| citypersons_convencion | partial | V3-V1 | -16.14 | [-18.35, -13.88] | si |
| nightowls | global | V3-V1 | -2.02 | [-2.59, -1.45] | si |
| nightowls | sin | V3-V1 | -1.78 | [-2.31, -1.22] | si |
| nightowls | ocluida | V3-V1 | -1.43 | [-3.98, +1.00] | no |
| test_proxy | global | V3-V1 | -17.47 | [-19.07, -15.87] | si |
| test_proxy | sin | V3-V1 | -17.69 | [-19.32, -15.98] | si |
| test_proxy | ligera | V3-V1 | -19.59 | [-23.73, -15.39] | si |
| test_proxy | moderada | V3-V1 | -12.48 | [-17.86, -7.27] | si |
| test_proxy | severa | V3-V1 | -9.15 | [-13.94, -5.66] | si |

## 3. Tamano de efecto entre semillas (Hedges g; indicativo, n=3)

| conjunto | estrato | contraste | g |
|---|---|---|---|
| citypersons_convencion | global | V3-V1 | -2.56 |
| citypersons_convencion | bare | V3-V1 | -2.44 |
| citypersons_convencion | heavy | V3-V1 | -1.03 |
| citypersons_convencion | partial | V3-V1 | -2.47 |
| nightowls | global | V3-V1 | -3.87 |
| nightowls | sin | V3-V1 | -3.54 |
| nightowls | ocluida | V3-V1 | -1.41 |
| test_proxy | global | V3-V1 | -1.83 |
| test_proxy | sin | V3-V1 | -1.82 |
| test_proxy | ligera | V3-V1 | -1.97 |
| test_proxy | moderada | V3-V1 | -1.63 |
| test_proxy | severa | V3-V1 | -1.98 |

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
