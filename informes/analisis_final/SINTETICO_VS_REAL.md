# ¿Predice la ganancia sintética la ganancia real?

Análisis posterior declarado (13/10/2026), solo con resultados ya calculados (`informes/sintetico_predice_real.py`). V3 − V1 en AP@0.5 (pp), media de 3 semillas, IC 95 % por imágenes. No decide ninguna hipótesis.

| Bloque | Control sintético | NightOwls ocluida | CityPersons heavy | ExDark proxy severa |
|---|---|---|---|---|
| E1 parches | +60.92* | -3.17 | -0.36 | -3.25 |
| E2 siluetas | +10.63* | -16.79 | -3.94 | -5.02 |
| E3 siluetas (YOLO26s) | +12.01* | -14.31 | -4.42 | -3.51 |
| E4 siluetas (CityPersons) | +23.74* | -1.35 | +1.82 | +0.94 |
| E6 siluetas (RT-DETR-l) | +10.97* | -6.98 | -3.47 | -2.21 |
| E7 generativa (época 2) | +2.60* | -1.93 | +1.23 | +2.82* |
| E7b generativa (30 épocas) | +15.23* | +0.01 | +1.52 | -3.03 |
| E8 geometría real (30 épocas) | +18.39* | -2.05 | +2.37* | -4.88 |
| E8 siluetas (30 épocas) | +10.99* | -1.12 | +2.26* | -3.50 |
| E9 siluetas (CityPersons, 60 épocas) | +24.66* | +1.95 | +1.31 | -2.44 |
| E10 siluetas (YOLOv11m) | +14.45* | -0.39 | +0.25 | +3.04 |
| E10 generativa (YOLOv11m) | +19.04* | +0.78 | +1.11 | -0.56 |
| E11 orden de profundidad | +7.42* | -1.50 | -0.16 | +5.49* |

\* supera +2 pp con IC > 0.

- **Controles sintéticos que superan el umbral: 13 de 13.** Celdas reales que lo superan: **4 de 39** (24 negativas).
- Si se hubiera decidido solo con el banco sintético, se habría concluido que el aumento funciona en los 13 bloques; con oclusión real, esa conclusión se sostiene en 4 de 39 celdas (valor predictivo 10 %).
- Correlación de Spearman entre la ganancia sintética y la real, por bloque (n = 13):
  - NightOwls ocluida: ρ = +0.41 (p = 0.168)
  - CityPersons heavy: ρ = +0.30 (p = 0.316)
  - ExDark proxy severa: ρ = -0.15 (p = 0.616)
  - media de las 3 fuentes: ρ = -0.05 (p = 0.859)
  - las 39 celdas juntas (no independientes): ρ = +0.13 (p = 0.414)

**Lectura.** No hay una asociación fiable entre la ganancia en el control sintético y la ganancia en oclusión real: las correlaciones por fuente tienen signos distintos y ninguna se distingue de cero (la de la media, cercana a cero, promedia signos opuestos y no es informativa por sí sola). Con 13 bloques no se descarta una asociación positiva moderada en NightOwls y CityPersons (con solo los 7 bloques de exposición igual, NightOwls da ρ = +0,64, p = 0,12). Lo que sí muestran los datos es que ganancias sintéticas de cualquier tamaño vinieron con ganancias reales bajo el umbral en casi todas las celdas: el banco sintético solo no basta para afirmar robustez a la oclusión real.
