# ARGOS-11 — Veredicto de H10 (geometría de la oclusión real, 30 épocas fijas)

Generado por `28_geometria.py analisis` (AP@0.5, media de 3 semillas, pesos de la época 30; IC 95 % bootstrap por imágenes, 1 000 réplicas, y jerárquico, 2 000). Regla literal de `PREREGISTRO_H10.md`, sección 2.

| Celda | V3ᴳ − V1 | V3ˢ − V1 | V3ᴳ − V3ˢ |
|---|---|---|---|
| Control geometria_severa | +18.39 pp [+15.61; +21.30] (jer. [+15.57; +21.47]) | +15.84 pp [+13.52; +18.63] (jer. [+13.17; +18.91]) | +2.55 pp [+1.07; +3.93] (jer. [+0.32; +4.64]) |
| Control silueta_severa (descriptivo) | +6.27 pp [+5.24; +7.47] (jer. [+5.19; +7.51]) | +10.99 pp [+9.62; +12.62] (jer. [+9.58; +12.68]) | -4.72 pp [-5.51; -4.01] (jer. [-5.65; -3.93]) |
| NightOwls ocluida | -2.05 pp [-3.26; -0.92] (jer. [-4.62; +0.29]) | -1.12 pp [-2.13; +0.08] (jer. [-2.58; +0.49]) | -0.93 pp [-1.93; -0.18] (jer. [-3.39; +1.09]) |
| CityPersons heavy | +2.37 pp [+1.52; +3.52] (jer. [+0.63; +4.61]) | +2.26 pp [+1.44; +3.47] (jer. [+0.72; +4.04]) | +0.10 pp [-0.77; +1.13] (jer. [-1.76; +2.09]) |
| ExDark proxy severa | -4.88 pp [-9.08; -0.82] (jer. [-11.58; +1.03]) | -3.50 pp [-7.64; +0.08] (jer. [-9.63; +1.86]) | -1.38 pp [-3.79; +1.43] (jer. [-6.29; +3.64]) |

**H10 (primaria):** fuentes reales con V3ᴳ − V1 ≥ +2 pp e IC > 0: **1 de 3** (para refutar se requieren 2).

## Veredicto H10: **Sostenida**

**Contraste secundario pre-registrado (efecto de la geometría, V3ᴳ − V3ˢ):** fuentes reales con ≥ +2 pp e IC > 0: **0 de 3** (la geometría «mejora la transferencia» si son al menos 2).

Declarado en el pre-registro: CityPersons comparte la distribución de la geometría con los patrones de entrenamiento (que vienen de CityPersons train); NightOwls y ExDark no.
