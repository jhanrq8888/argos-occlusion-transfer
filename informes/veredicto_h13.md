# ARGOS-11 — Veredicto de H13 (realismo medido de cada familia de oclusor)

Generado por `31_realismo.py analisis`. Regla literal de `PREREGISTRO_H13.md`. AUC de un clasificador lineal que separa la oclusión real (CityPersons heavy) de cada conjunto; 0,5 = indistinguible. IC 95 %: bootstrap de personas (1 000).

| Extractor | Conjunto | AUC frente a oclusión real | IC 95 % |
|---|---|---|---|
| dinov2 | base | 0.876 | [0.852; 0.897] |
| dinov2 | parches | 0.993 | [0.989; 0.996] |
| dinov2 | siluetas | 0.950 | [0.936; 0.963] |
| dinov2 | geometria | 0.953 | [0.938; 0.966] |
| dinov2 | generativa | 0.935 | [0.919; 0.950] |
| clip | base | 0.831 | [0.803; 0.859] |
| clip | parches | 0.993 | [0.988; 0.997] |
| clip | siluetas | 0.916 | [0.896; 0.934] |
| clip | geometria | 0.923 | [0.904; 0.940] |
| clip | generativa | 0.925 | [0.907; 0.941] |

| Extractor | Contraste | Diferencia de AUC | IC 95 % |
|---|---|---|---|
| dinov2 | parches - siluetas | +0.043 | [+0.031; +0.057] |
| dinov2 | siluetas - generativa | +0.015 | [-0.003; +0.034] |
| dinov2 | parches - generativa | +0.058 | [+0.043; +0.074] |
| dinov2 | siluetas - geometria | -0.002 | [-0.018; +0.013] |
| dinov2 | geometria - generativa | +0.017 | [+0.001; +0.033] |
| dinov2 | base - parches | -0.117 | [-0.142; -0.096] |
| dinov2 | base - siluetas | -0.074 | [-0.099; -0.049] |
| dinov2 | base - geometria | -0.077 | [-0.100; -0.054] |
| dinov2 | base - generativa | -0.060 | [-0.079; -0.041] |
| clip | parches - siluetas | +0.076 | [+0.059; +0.096] |
| clip | siluetas - generativa | -0.009 | [-0.031; +0.014] |
| clip | parches - generativa | +0.068 | [+0.052; +0.085] |
| clip | siluetas - geometria | -0.007 | [-0.029; +0.016] |
| clip | geometria - generativa | -0.002 | [-0.024; +0.019] |
| clip | base - parches | -0.162 | [-0.190; -0.133] |
| clip | base - siluetas | -0.086 | [-0.115; -0.054] |
| clip | base - geometria | -0.092 | [-0.123; -0.061] |
| clip | base - generativa | -0.094 | [-0.118; -0.069] |

| Extractor | Conjunto | KID frente a oclusión real | IC 95 % |
|---|---|---|---|
| dinov2 | base | 1.7453 | [1.2114; 2.2549] |
| dinov2 | parches | 1.7903 | [1.5305; 2.0699] |
| dinov2 | siluetas | 1.5722 | [1.2464; 1.9668] |
| dinov2 | geometria | 1.4201 | [1.0589; 1.7636] |
| dinov2 | generativa | 1.3280 | [0.9799; 1.6425] |
| clip | base | 0.0286 | [0.0197; 0.0387] |
| clip | parches | 0.0413 | [0.0320; 0.0484] |
| clip | siluetas | 0.0152 | [0.0108; 0.0204] |
| clip | geometria | 0.0149 | [0.0105; 0.0219] |
| clip | generativa | 0.0181 | [0.0114; 0.0238] |

- AUC usando solo la altura de la caja (real frente a base): 0.619.
- Cobertura conseguida por familia: {'parches': {'cobertura_media': 0.56, 'sin_oclusion': 0}, 'siluetas': {'cobertura_media': 0.541, 'sin_oclusion': 1}, 'geometria': {'cobertura_media': 0.465, 'sin_oclusion': 0}, 'generativa': {'cobertura_media': 0.319, 'sin_oclusion': 146}}; oclusión real media: 0.552.

## Veredicto H13: **Parcialmente confirmada**

Regla: confirmada si, con DINOv2, AUC(parches) − AUC(siluetas) y AUC(siluetas) − AUC(generativa) tienen IC 95 % > 0; parcialmente si solo una; no confirmada si ninguna.
