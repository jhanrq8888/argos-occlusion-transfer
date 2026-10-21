# ARGOS-11 — Veredicto de H9b (oclusión generativa, 30 épocas fijas)

Generado por `26_veredicto_h9b.py` a partir de `resultados_h9b/analisis/bootstrap.csv` (V3ᵍ − V1, AP@0.5, media de 3 semillas, pesos de la época 30, IC 95 % bootstrap por imágenes, 1 000 réplicas). Regla literal de `PREREGISTRO_H9b.md`, sección 2.

| Celda | V3ᵍ − V1 |
|---|---|
| Control `generativa_severa` | +15.23 pp [+14.00; +17.16] (n=2018) |
| NightOwls ocluida | +0.01 pp [-1.02; +1.20] (n=530) |
| CityPersons heavy | +1.52 pp [+0.79; +2.66] (n=733) |
| ExDark proxy severa | -3.03 pp [-6.77; +0.99] (n=101) |

**Fuentes reales con mejora relevante (≥ +2 pp e IC > 0): 0 de 3** (para refutar se requieren 2).

## Veredicto: **Sostenida**

Sensibilidad declarada: fuentes reales cuyo IC por imágenes descarta una mejora de +2 pp (límite superior < +2): **2 de 3**.

### IC jerárquico (semillas + imágenes)

| Conjunto | Estrato | Δ (pp) | IC |
|---|---|---|---|
| generativa_severa | severa | +15.23 | [+13.81; +17.45] |
| nightowls | ocluida | +0.01 | [-1.60; +1.82] |
| citypersons_convencion | heavy | +1.52 | [-0.02; +3.39] |
| test_proxy | severa | -3.03 | [-8.85; +2.89] |

### Tasa de pérdida MR-2 (menor es mejor)

| Conjunto | Estrato | Δ (pp) | IC |
|---|---|---|---|
| generativa_severa | severa | -6.32 | [-7.37; -5.46] · jerárquico [-7.40; -5.29] |
| nightowls | ocluida | -0.24 | [-1.18; +0.77] · jerárquico [-1.58; +1.11] |
| citypersons_convencion | heavy | -1.19 | [-1.86; -0.59] · jerárquico [-2.45; -0.02] |
| test_proxy | severa | +2.89 | [-0.33; +6.29] · jerárquico [-1.77; +8.03] |
