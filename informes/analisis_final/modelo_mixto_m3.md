# Modelo mixto global (M3) y recuentos uniformes (M1, M2)

Generado por `informes/modelo_mixto_m3.py` (análisis posterior, declarado; no decide hipótesis).

Modelo: Δ = μ_fuente + u_bloque + v_semilla(bloque) + e, REML, Δ = V3 − V1 en AP@0.5 (pp) por semilla.

| Modelo | NightOwls | CityPersons | ExDark | Ganancia sintética (por DE) | Var. bloque | Var. semilla | Var. residual | n |
|---|---|---|---|---|---|---|---|---|
| modelo0_igual_dosis_base | +0.57 [-0.34; +1.48] | +1.06 [+0.15; +1.96] | -1.11 [-2.01; -0.20] | — | 0.05 | 0.81 | 6.83 | 114 obs., 12 bloques |
| modelo0b_todos_dosis_base | -2.08 [-3.61; -0.54] | +0.15 [-1.38; +1.69] | -1.44 [-2.98; +0.10] | — | 7.67 | 0.00 | 10.54 | 167 obs., 18 bloques |
| modelo0c_igual_dosis_base_con_control | +0.57 [-0.27; +1.42] | +1.06 [+0.22; +1.90] | -1.10 [-1.94; -0.26] | +0.16 [-0.46; +0.78] | 0.00 | 1.04 | 6.79 | 114 obs., 12 bloques |
| modelo1_igual | +1.25 [+0.23; +2.27] | +1.27 [+0.25; +2.29] | -1.07 [-2.09; -0.05] | — | 1.52 | 0.07 | 7.05 | 132 obs., 14 bloques |
| modelo1b_todos | -1.31 [-2.81; +0.19] | +0.42 [-1.08; +1.92] | -1.36 [-2.86; +0.15] | — | 8.23 | 0.00 | 10.78 | 185 obs., 20 bloques |
| modelo2_igual_con_control | +1.25 [+0.24; +2.26] | +1.27 [+0.26; +2.28] | -1.07 [-2.08; -0.06] | +0.54 [-0.28; +1.35] | 1.44 | 0.08 | 7.04 | 132 obs., 14 bloques |
| modelo2b_todos_con_control | -1.31 [-2.84; +0.22] | +0.42 [-1.11; +1.95] | -1.36 [-2.89; +0.17] | +0.14 [-1.28; +1.55] | 8.69 | 0.00 | 10.78 | 185 obs., 20 bloques |

## Recuentos

```
{
 "igual_33": {
  "celdas": 42,
  "pasan_img": 9,
  "pasan_jer": 8,
  "descartan_img": 16,
  "descartan_jer": 9,
  "no_concluyentes_img": 17,
  "no_concluyentes_jer": 25,
  "pasan_jer_lista": [
   "H10-CP",
   "H10-s-CP",
   "H15-CP",
   "H15-NO",
   "H18a-NO",
   "H18e-alta-CP",
   "H18e-alta-NO",
   "H18e-baja-NO"
  ]
 },
 "todos_51": {
  "celdas": 60,
  "pasan_img": 10,
  "pasan_jer": 8,
  "descartan_img": 30,
  "descartan_jer": 21,
  "no_concluyentes_img": 20,
  "no_concluyentes_jer": 31,
  "pasan_jer_lista": [
   "H10-CP",
   "H10-s-CP",
   "H15-CP",
   "H15-NO",
   "H18a-NO",
   "H18e-alta-CP",
   "H18e-alta-NO",
   "H18e-baja-NO"
  ]
 },
 "igual_dosis_base": {
  "celdas": 36,
  "pasan_img": 6,
  "pasan_jer": 5,
  "descartan_img": 16,
  "descartan_jer": 9,
  "no_concluyentes_img": 14,
  "no_concluyentes_jer": 22,
  "pasan_jer_lista": [
   "H10-CP",
   "H10-s-CP",
   "H15-CP",
   "H15-NO",
   "H18a-NO"
  ]
 },
 "todos_dosis_base": {
  "celdas": 54,
  "pasan_img": 7,
  "pasan_jer": 5,
  "descartan_img": 30,
  "descartan_jer": 21,
  "no_concluyentes_img": 17,
  "no_concluyentes_jer": 28,
  "pasan_jer_lista": [
   "H10-CP",
   "H10-s-CP",
   "H15-CP",
   "H15-NO",
   "H18a-NO"
  ]
 },
 "sin_EX": {
  "bloques_ambas_img": [
   "H15",
   "H18e-alta"
  ],
  "bloques_ambas_jer": [
   "H15",
   "H18e-alta"
  ],
  "celdas": 40,
  "pasan_img": 8,
  "pasan_jer": 8
 }
}
```
