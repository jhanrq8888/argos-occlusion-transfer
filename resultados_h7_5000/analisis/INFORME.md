# ARGOS-11 - Informe de analisis estadistico

Corridas analizadas: 2 (V1_s0, V3_s0)
Bootstrap sobre imagenes: B = 1000, percentil, pareado entre corridas.

## 1. Descriptivo (media +- sd entre semillas, AP@0.5)

| conjunto | estrato | n_gt | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|---|
| citypersons_convencion | bare | 769 | 0.732 +- 0.000 | - | 0.477 +- 0.000 | - |
| citypersons_convencion | global | 2312 | 0.535 +- 0.000 | - | 0.336 +- 0.000 | - |
| citypersons_convencion | heavy | 733 | 0.170 +- 0.000 | - | 0.099 +- 0.000 | - |
| citypersons_convencion | partial | 810 | 0.567 +- 0.000 | - | 0.337 +- 0.000 | - |
| nightowls | global | 3293 | 0.852 +- 0.000 | - | 0.824 +- 0.000 | - |
| nightowls | ocluida | 530 | 0.419 +- 0.000 | - | 0.408 +- 0.000 | - |
| nightowls | sin | 2763 | 0.885 +- 0.000 | - | 0.864 +- 0.000 | - |
| test_proxy | global | 2235 | 0.732 +- 0.000 | - | 0.428 +- 0.000 | - |
| test_proxy | ligera | 188 | 0.509 +- 0.000 | - | 0.204 +- 0.000 | - |
| test_proxy | moderada | 190 | 0.418 +- 0.000 | - | 0.164 +- 0.000 | - |
| test_proxy | severa | 101 | 0.247 +- 0.000 | - | 0.035 +- 0.000 | - |
| test_proxy | sin | 1756 | 0.740 +- 0.000 | - | 0.444 +- 0.000 | - |

## 2. Efectos con IC 95 % bootstrap (puntos porcentuales de AP@0.5)

| conjunto | estrato | contraste | delta | IC95 | excluye 0 |
|---|---|---|---|---|---|
| citypersons_convencion | global | V3-V1 | -19.87 | [-22.12, -17.89] | si |
| citypersons_convencion | bare | V3-V1 | -25.45 | [-28.93, -22.41] | si |
| citypersons_convencion | heavy | V3-V1 | -7.07 | [-9.79, -4.39] | si |
| citypersons_convencion | partial | V3-V1 | -22.96 | [-25.88, -20.16] | si |
| nightowls | global | V3-V1 | -2.80 | [-3.72, -1.83] | si |
| nightowls | sin | V3-V1 | -2.04 | [-3.02, -1.26] | si |
| nightowls | ocluida | V3-V1 | -1.12 | [-4.99, +3.10] | no |
| test_proxy | global | V3-V1 | -30.41 | [-32.83, -27.89] | si |
| test_proxy | sin | V3-V1 | -29.59 | [-32.20, -26.93] | si |
| test_proxy | ligera | V3-V1 | -30.56 | [-37.05, -24.19] | si |
| test_proxy | moderada | V3-V1 | -25.35 | [-32.40, -18.48] | si |
| test_proxy | severa | V3-V1 | -21.21 | [-29.46, -14.25] | si |

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
