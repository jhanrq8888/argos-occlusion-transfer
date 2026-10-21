# ARGOS-11 — Informe de H11 (E9): ganancia dentro del dominio sobre las personas más ocluidas, con exposición igual

Fecha: 2026-10-13. Pre-registro: `PREREGISTRO_H11.md` (sha256 `6c2b515e…`), congelado como **v3.6b** (`bd2666fd`) antes de subir los datos y de la primera época. `08_congelar_protocolo.py --verificar` dio **PROTOCOLO INTACTO** antes de evaluar. No hubo cambios de protocolo durante la ejecución.

## 1. Qué se hizo

- **Entrenamiento:** 6 corridas de YOLOv11s sobre CityPersons (`--protocolo cp`), V1 y V3 (siluetas) con las semillas {3, 4, 5}.
  - 60 épocas fijas (`--patience 0`), las 6 completas, a 19,1–20,8 s por época. En total fueron ~2 h de GPU, del 13/10 a las 20:38 hasta las 22:35 UTC, sin incidentes.
  - Se entrenó en RunPod (una RTX 4090, 12 vCPU, 8 procesos de carga), con Ultralytics 8.4.143, PyTorch 2.8.0+cu128 y CUDA 12.8.
  - Las huellas de `config/hiperparametros.yaml`, `config/aumento_base.yaml` y `yolo11s.pt` en los 6 `registro_argos.json` coinciden con las congeladas y con las de H6 (`200626226d41`, `ae34f38c9499`, `85a76fe86dd8`). Los argumentos efectivos (batch, imgsz, optimizador, lr0, close_mosaic, aumentos) son idénticos a los de H6; solo cambian épocas, paciencia y workers, como se declaró.
  - Antes, una prueba de humo (1 época, 5 %) comprobó que la cadena de V3 incluye `OclusionSiluetas`.
- **Descarga:** pesos `last.pt` y `best.pt`, `results.csv`, `args.yaml` y `registro_argos.json` en `runs/argos_cp_fijo/`. La suma SHA-256 de los 12 `.pt` coincide con la del servidor. El log del entrenamiento está en `D:\argos11\h11_entrenamiento_runpod.log`.
- **Evaluación (local):** `last.pt` (época 60) sobre `cp_silueta_severa`, CityPersons (convención), NightOwls y el proxy de ExDark, en `resultados_h11/`. Lanzador: `h11_evaluar.bat`.
- **Veredicto:** `29_h11_dominio.py` → `informes/veredicto_h11.md` y `resultados_h11/analisis/contrastes_h11.json`.
- **Descriptivos declarados:**
  - `11_analisis_estadistico.py --resultados resultados_h11` (`resultados_h11/analisis/bootstrap.csv`);
  - `informes/h11_descriptivos.py`, que reutiliza sin cambios `27_` y `24_` (`resultados_h11/analisis/descriptivos_h11_*.csv`).

**Desviación menor, declarada:** el pre-registro decía que las versiones de PyTorch y CUDA quedarían en cada `registro_argos.json`, pero ese registro no las guarda. Se anotan arriba a partir de la salida de la instalación en el servidor (`ultralytics 8.4.143 | torch 2.8.0+cu128 | cuda 12.8 | NVIDIA GeForce RTX 4090`). No afecta a ningún resultado.

## 2. Veredicto literal (AP@0.5, pp; IC 95 % por imágenes, 1 000 réplicas)

| Celda | Semillas | n | V3 − V1 | IC 95 % |
|---|---|---|---|---|
| **Primaria: visibilidad 0,20–0,50** | 3, 4, 5 | 432 | **+1,44** | [−0,64; +3,34] |
| Visibilidad 0,80–1,00 | 3, 4, 5 | 1 192 | +0,40 | [−0,18; +0,93] |
| Especificidad (0,20–0,50 menos 0,80–1,00) | 3, 4, 5 | | +1,04 | [−1,11; +2,95] |
| Control `cp_silueta_severa` | 3, 4, 5 | 684 | +24,66 | [+21,62; +27,47] |
| 0,20–0,50, las 6 semillas (IC jerárquico, 2 000) | 0–5 | 432 | +1,92 | [−0,45; +4,27] |
| 0,20–0,50, las 6 semillas (IC por imágenes) | 0–5 | 432 | +1,92 | [+0,26; +3,51] |

- El control alcanza +2 pp con IC > 0: el aumento se aprendió.
- La celda primaria no alcanza +2 pp y su IC incluye el cero. **H11: NO CONFIRMADA.**
- **Secundario 1 (especificidad):** +1,04 con IC que incluye el cero. No hay evidencia de que la mejora sea propia de la oclusión.
- **Secundario 2 (6 semillas):** +1,92. El IC jerárquico, que es el que tiene en cuenta la variación entre semillas, incluye el cero. Advertencia ya declarada: las semillas 0–2 tienen exposición desigual y se entrenaron en otra máquina.

## 3. Descriptivos declarados (no deciden H11)

**Por semilla, celda primaria (AP@0.5, %):**

| Semilla | V1 | V3 | V3 − V1 |
|---|---|---|---|
| 0 (H6) | 47,08 | 49,86 | +2,78 |
| 1 (H6) | 46,49 | 50,17 | +3,68 |
| 2 (H6) | 49,40 | 50,12 | +0,73 |
| 3 | 50,23 | 51,51 | +1,28 |
| 4 | 48,14 | 49,56 | +1,42 |
| 5 | 47,57 | 49,18 | +1,61 |

Las tres semillas nuevas son positivas y muy parecidas (+1,28 a +1,61): el efecto es pequeño y estable, no nulo, pero queda por debajo del umbral de relevancia fijado. Con exposición igual, V3 queda prácticamente donde estaba en H6 (50,08 frente a 50,05 de media). Lo que cambia es V1, que sube (48,65 frente a 47,66). Esto concuerda con que parte de la ganancia de E4 venía de que V1 se detuvo antes. Es una lectura descriptiva: las semillas y el hardware también cambian.

**Curva por visibilidad en CityPersons (AP@0.5; IC por imágenes):**

| Visibilidad | n | V1 | V3 | V3 − V1 | IC 95 % |
|---|---|---|---|---|---|
| 0,20–0,35 | 178 | 34,27 | 36,25 | +1,98 | [−1,57; +5,34] |
| 0,35–0,50 | 254 | 49,50 | 50,92 | +1,42 | [−0,87; +3,62] |
| 0,50–0,65 | 301 | 61,71 | 63,44 | +1,73 | [−0,13; +3,44] |
| 0,65–0,80 | 387 | 79,30 | 79,96 | +0,65 | [−0,51; +1,76] |
| 0,80–0,90 | 423 | 85,50 | 86,28 | +0,78 | [−0,16; +1,79] |
| 0,90–1,00 | 769 | 90,03 | 90,75 | +0,72 | [+0,05; +1,44] |

La forma se mantiene (algo más de ganancia en las más ocluidas), pero mucho más plana que en E4 (+4,30 / +3,36 / +2,14 en los tres primeros tramos), y ningún tramo ocluido tiene IC por encima de cero.

**Estratos de la convención, AP@0.5:** *bare* +0,72 [+0,02; +1,41]; *partial* +0,44 [−0,36; +1,21]; *heavy* +1,31 [−0,28; +2,78]. En E4 *heavy* daba +1,82.

**AP@0.5:0.95 (IC por imágenes; entre paréntesis, jerárquico):**

| Celda | V3 − V1 |
|---|---|
| Control `cp_silueta_severa` | +9,43 [+8,10; +10,90] |
| NightOwls ocluida | +0,76 [+0,38; +1,22] ([+0,10; +1,60]) |
| CityPersons *heavy* | +0,90 [+0,21; +1,56] ([−0,12; +2,11]) |
| ExDark proxy severa | +0,01 [−1,15; +1,62] |

**Tasa de pérdida MR-2 (pp; negativo = V3 pierde menos personas):**

| Celda | V3 − V1 |
|---|---|
| Control | −12,81 [−14,92; −10,63] |
| NightOwls ocluida | −1,84 [−2,88; −0,87] (jer. [−4,09; +0,31]) |
| CityPersons *heavy* | −0,61 [−2,54; +1,13] |
| ExDark proxy severa | +1,14 [−3,01; +5,41] |

Ninguna celda real alcanza la mejora relevante (−2 pp con IC < 0).

**Transferencia (AP@0.5):**

| Celda | V3 − V1 |
|---|---|
| NightOwls ocluida | +1,95 [+0,93; +3,21] |
| ExDark proxy severa | −2,44 [−6,77; +2,36] |

Según la regla declarada, ninguna alcanza +2 pp con IC > 0, así que **no se transfiere**. NightOwls queda a 0,05 pp del umbral, pero el criterio es el que se fijó antes de ver los datos.

**Rendimiento global en otros dominios (descriptivo, no previsto):**
- Con exposición igual, V3 supera a V1 en el global de NightOwls (+3,27 [+2,64; +3,92]) y del proxy de ExDark (+6,91 [+5,69; +8,07]). En E4 era al revés: −5,12 y −0,46.
- La mejora se concentra en las personas sin oclusión (NightOwls *sin* +3,34; ExDark *sin* +7,64), no en las ocluidas. Además varía entre semillas: en NightOwls global, +5,16, −2,27 y +6,91.
- Una lectura plausible, no contrastada, es que en E4 la selección por validación favorecía a V1 fuera del dominio. Con 60 épocas fijas, el aumento actúa como regularizador contra el sobreajuste a CityPersons.
- No es una hipótesis pre-registrada y no se reporta como hallazgo.

## 4. Lectura

1. **Con la misma exposición, la ganancia de E4 sobre las personas más ocluidas se reduce a +1,44 pp y deja de ser distinguible de cero.** Las tres semillas nuevas son positivas, así que el efecto probablemente existe, pero es pequeño (~1,5 pp) y no alcanza el umbral de relevancia del proyecto. La parte que faltaba hasta los +2,40 de E4 es compatible con la diferencia de épocas entre V1 y V3 en H6.
2. **No hay evidencia de especificidad:** la mejora en las ocluidas no es distinguible de la de las visibles.
3. **No se transfiere a la oclusión real de otros dominios,** igual que en todas las familias anteriores.
4. **El control sintético se aprende con fuerza** (+24,66): la brecha entre la oclusión sintética y la real se mantiene también dentro del dominio de entrenamiento.

## 5. Consecuencias (compromiso de reporte del pre-registro)

- El artículo, el short paper, el PPI y el informe general **retiran** «dentro del dominio (E4) el aumento las ayudó algo». En su lugar reportan que, con exposición igual (H11, semillas nuevas), la ganancia de E4 sobre las personas más ocluidas **no se confirmó**: +1,44 pp [−0,64; +3,34], por debajo de +2 pp y con un IC que incluye el cero.
- El veredicto de H6 no cambia: sostenida, *heavy* +1,82.
- La conclusión general del proyecto se refuerza: en ningún dominio ni familia el aumento sintético produjo una mejora relevante y robusta en la oclusión real anotada.
