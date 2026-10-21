# ARGOS-11 - Informe de analisis estadistico

Corridas analizadas: 2 (V1_s0, V3_s0)
Bootstrap sobre imagenes: B = 1000, percentil, pareado entre corridas.

## 1. Descriptivo (media +- sd entre semillas, AP@0.5)

| conjunto | estrato | n_gt | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|---|
| citypersons_convencion | bare | 769 | 0.707 +- 0.000 | - | 0.542 +- 0.000 | - |
| citypersons_convencion | global | 2312 | 0.515 +- 0.000 | - | 0.379 +- 0.000 | - |
| citypersons_convencion | heavy | 733 | 0.153 +- 0.000 | - | 0.122 +- 0.000 | - |
| citypersons_convencion | partial | 810 | 0.538 +- 0.000 | - | 0.389 +- 0.000 | - |
| nightowls | global | 3293 | 0.865 +- 0.000 | - | 0.849 +- 0.000 | - |
| nightowls | ocluida | 530 | 0.393 +- 0.000 | - | 0.437 +- 0.000 | - |
| nightowls | sin | 2763 | 0.899 +- 0.000 | - | 0.883 +- 0.000 | - |
| test_proxy | global | 2235 | 0.681 +- 0.000 | - | 0.428 +- 0.000 | - |
| test_proxy | ligera | 188 | 0.449 +- 0.000 | - | 0.200 +- 0.000 | - |
| test_proxy | moderada | 190 | 0.284 +- 0.000 | - | 0.151 +- 0.000 | - |
| test_proxy | severa | 101 | 0.121 +- 0.000 | - | 0.034 +- 0.000 | - |
| test_proxy | sin | 1756 | 0.689 +- 0.000 | - | 0.439 +- 0.000 | - |

## 2. Efectos con IC 95 % bootstrap (puntos porcentuales de AP@0.5)

| conjunto | estrato | contraste | delta | IC95 | excluye 0 |
|---|---|---|---|---|---|
| citypersons_convencion | global | V3-V1 | -13.55 | [-15.68, -11.49] | si |
| citypersons_convencion | bare | V3-V1 | -16.53 | [-19.89, -13.22] | si |
| citypersons_convencion | heavy | V3-V1 | -3.14 | [-5.44, -0.67] | si |
| citypersons_convencion | partial | V3-V1 | -14.90 | [-18.33, -11.79] | si |
| nightowls | global | V3-V1 | -1.63 | [-2.65, -0.77] | si |
| nightowls | sin | V3-V1 | -1.57 | [-2.47, -0.67] | si |
| nightowls | ocluida | V3-V1 | +4.38 | [+0.17, +8.06] | si |
| test_proxy | global | V3-V1 | -25.30 | [-27.78, -23.06] | si |
| test_proxy | sin | V3-V1 | -25.06 | [-27.57, -22.63] | si |
| test_proxy | ligera | V3-V1 | -24.84 | [-31.12, -18.68] | si |
| test_proxy | moderada | V3-V1 | -13.29 | [-20.27, -7.23] | si |
| test_proxy | severa | V3-V1 | -8.68 | [-14.85, -4.39] | si |

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
