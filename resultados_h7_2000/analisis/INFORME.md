# ARGOS-11 - Informe de analisis estadistico

Corridas analizadas: 2 (V1_s0, V3_s0)
Bootstrap sobre imagenes: B = 1000, percentil, pareado entre corridas.

## 1. Descriptivo (media +- sd entre semillas, AP@0.5)

| conjunto | estrato | n_gt | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|---|
| citypersons_convencion | bare | 769 | 0.609 +- 0.000 | - | 0.553 +- 0.000 | - |
| citypersons_convencion | global | 2312 | 0.451 +- 0.000 | - | 0.382 +- 0.000 | - |
| citypersons_convencion | heavy | 733 | 0.111 +- 0.000 | - | 0.094 +- 0.000 | - |
| citypersons_convencion | partial | 810 | 0.421 +- 0.000 | - | 0.393 +- 0.000 | - |
| nightowls | global | 3293 | 0.832 +- 0.000 | - | 0.839 +- 0.000 | - |
| nightowls | ocluida | 530 | 0.360 +- 0.000 | - | 0.367 +- 0.000 | - |
| nightowls | sin | 2763 | 0.865 +- 0.000 | - | 0.883 +- 0.000 | - |
| test_proxy | global | 2235 | 0.666 +- 0.000 | - | 0.425 +- 0.000 | - |
| test_proxy | ligera | 188 | 0.375 +- 0.000 | - | 0.187 +- 0.000 | - |
| test_proxy | moderada | 190 | 0.254 +- 0.000 | - | 0.108 +- 0.000 | - |
| test_proxy | severa | 101 | 0.106 +- 0.000 | - | 0.017 +- 0.000 | - |
| test_proxy | sin | 1756 | 0.677 +- 0.000 | - | 0.446 +- 0.000 | - |

## 2. Efectos con IC 95 % bootstrap (puntos porcentuales de AP@0.5)

| conjunto | estrato | contraste | delta | IC95 | excluye 0 |
|---|---|---|---|---|---|
| citypersons_convencion | global | V3-V1 | -6.85 | [-8.99, -4.88] | si |
| citypersons_convencion | bare | V3-V1 | -5.59 | [-9.35, -2.08] | si |
| citypersons_convencion | heavy | V3-V1 | -1.72 | [-4.07, +0.61] | no |
| citypersons_convencion | partial | V3-V1 | -2.78 | [-6.01, +0.19] | no |
| nightowls | global | V3-V1 | +0.71 | [-0.36, +1.73] | no |
| nightowls | sin | V3-V1 | +1.76 | [+0.82, +2.85] | si |
| nightowls | ocluida | V3-V1 | +0.66 | [-3.31, +5.13] | no |
| test_proxy | global | V3-V1 | -24.08 | [-26.53, -21.69] | si |
| test_proxy | sin | V3-V1 | -23.05 | [-25.69, -20.41] | si |
| test_proxy | ligera | V3-V1 | -18.80 | [-25.46, -12.29] | si |
| test_proxy | moderada | V3-V1 | -14.54 | [-20.57, -8.71] | si |
| test_proxy | severa | V3-V1 | -8.85 | [-14.86, -5.24] | si |

## 3. Tamano de efecto entre semillas (Hedges g; indicativo, n=3)

| conjunto | estrato | contraste | g |
|---|---|---|---|
| citypersons_convencion | global | V3-V1 | nd |
| citypersons_convencion | bare | V3-V1 | nd |
| citypersons_convencion | heavy | V3-V1 | nd |
| citypersons_convencion | partial | V3-V1 | nd |
| nightowls | global | V3-V1 | nd |
| nightowls | sin | V3-V1 | nd |
| nightowls | ocluida | V3-V1 | nd |
| test_proxy | global | V3-V1 | nd |
| test_proxy | sin | V3-V1 | nd |
| test_proxy | ligera | V3-V1 | nd |
| test_proxy | moderada | V3-V1 | nd |
| test_proxy | severa | V3-V1 | nd |

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
