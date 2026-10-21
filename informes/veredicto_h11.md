# ARGOS-11 — Veredicto de H11 (dominio CityPersons, personas muy ocluidas)

Generado por `29_h11_dominio.py`. AP@0.5, media de semillas; IC 95 % bootstrap por imágenes (1 000 réplicas) y, para las 6 semillas, jerárquico (2 000). Regla literal de `PREREGISTRO_H11.md`, sección 2.

| Celda | Semillas | n | V3 − V1 (pp) | IC 95 % |
|---|---|---|---|---|
| bajo (vis 0,20-0,50) | 3,4,5 | 432 | +1.44 | [-0.64; +3.34] |
| alto (vis 0,80-1,00) | 3,4,5 | 1192 | +0.40 | [-0.18; +0.93] |
| especificidad (bajo - alto) | 3,4,5 |  | +1.04 | [-1.11; +2.95] |
| control cp_silueta_severa | 3,4,5 | 684 | +24.66 | [+21.62; +27.47] |
| bajo, 6 semillas (IC jerarquico) | 0,1,2,3,4,5 | 432 | +1.92 | [-0.45; +4.27] |
| bajo, 6 semillas (IC por imagenes) | 0,1,2,3,4,5 | 432 | +1.92 | [+0.26; +3.51] |

## Veredicto H11: **No confirmada**

Regla: confirmada si V3 − V1 en el tramo bajo (semillas 3, 4 y 5) ≥ +2 pp con IC por imágenes > 0, siempre que el control `cp_silueta_severa` lo haga; no concluyente si el control falla. La especificidad y las 6 semillas son análisis secundarios declarados.
