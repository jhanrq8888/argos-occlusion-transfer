# ARGOS-11 — Pre-registro de H9b (E7b: oclusión generativa con exposición fija)

Pre-registrado el **2026-10-06**. Se escribe **después** de cerrar H9 (veredicto: sostenida) y de su análisis exploratorio con los pesos finales, y **antes** de entrenar ninguna corrida de H9b o de evaluar nada con este diseño. Complementa a `PREREGISTRO_H9.md`: lo que no se menciona no cambia (generador, datos generados `dataset/generativa_train/`, probabilidades de sustitución, validación mixta, hiperparámetros de YOLOv11s, evaluación estratificada con regiones *ignore*, bootstrap por imágenes con 1 000 réplicas como criterio, umbral de +2 pp). Se congelará como **v3.4** antes de la primera época.

**H9b no reformula H9.** El veredicto de H9 (sostenida, protocolo v3.3b) queda como está. H9b es una hipótesis nueva sobre la misma familia de oclusor, motivada por una limitación de H9 que ya se reportó.

## 1. Motivación

En H9 la regla de selección pre-registrada (mejor época según la validación mixta, que contiene siluetas y no oclusión generativa) eligió la **época 2 en las tres corridas** V3ᵍ. Los modelos vieron muy poco del aumento: el control sintético mejoró solo +2,60 pp, frente a +10,6 o más con las otras familias. Las dos revisiones del short paper (6/10/2026; `shortpaper/revision_simulada.md`, objeción 1, y `shortpaper/revision_panel_ars.md`, M1 y DA-1) señalan que, así, el diseño no distingue «la oclusión generativa no se transfiere» de «no se entrenó lo bastante». El análisis exploratorio con `last.pt` (épocas 21–22) no lo resuelve, por tres motivos:

1. No estaba pre-registrado.
2. Las corridas se cortaron por parada temprana con la tasa de aprendizaje todavía alta.
3. V1 y V3ᵍ se detuvieron en épocas distintas.

H9b fija la exposición: V1 y V3ᵍ se entrenan **el mismo número de épocas, completo**, sin parada temprana ni selección por validación.

## 2. Hipótesis (literal; no se reformula después)

- **H9b.** Con exposición fija al aumento generativo, el déficit de transferencia de H9 se mantiene. Las condiciones son:
  - YOLOv11s con el protocolo de H9;
  - **V1 y V3ᵍ entrenados exactamente 30 épocas** con el calendario completo de tasa de aprendizaje, sin parada temprana;
  - evaluación con los **pesos de la última época** (`last.pt`).

  Bajo esas condiciones, el contraste V3ᵍ − V1 (AP@0.5, media de 3 semillas) **no alcanza +2 pp con IC 95 % por imágenes que excluya el cero en al menos 2 de las 3 fuentes reales** (NightOwls ocluida, CityPersons *heavy*, ExDark proxy severa). Esto vale aun cuando el control sintético `generativa_severa` sea ≥ +2 pp con IC que excluya el cero.
  - *Refutaría H9b:* V3ᵍ − V1 ≥ +2 pp con IC 95 % por imágenes que excluya el cero en **al menos 2 de las 3** fuentes reales. Es el mismo criterio de H4, H8 y H9.
  - *No concluyente:* el control `generativa_severa` no alcanza +2 pp con IC que excluya el cero (el aumento no se aprendió).
- **Compromiso de reporte.** Si H9b se refuta, la conclusión del artículo y del short paper sobre la familia generativa cambia, y se reportará así. La transferencia de la familia generativa pasaría a depender de la exposición, y H9 quedaría como resultado de un entrenamiento demasiado corto.
- **Análisis de sensibilidad declarados ahora:**
  - IC jerárquico (semillas + imágenes, `23_ --secundarios`);
  - tasa de pérdida (`24_ --secundarios`);
  - número de fuentes reales cuyo IC por imágenes tiene límite superior < +2 pp (descarta una mejora relevante).

  El veredicto se decide solo con el IC por imágenes.
- **Descriptivo, sin criterio:**
  - V3ᵍ − V1 en `silueta_severa`;
  - comparación de las celdas de H9b con las de H9 y con su análisis exploratorio;
  - curvas de validación por época.

## 3. Diseño

| Elemento | Definición |
|---|---|
| Modelo, hiperparámetros, aumento base | Idénticos a H9 (`yolo11s.pt`, `config/hiperparametros.yaml`, `config/aumento_base.yaml`). Única excepción: las épocas y la paciencia (fila siguiente) |
| Épocas | **30 épocas fijas** (`--epochs 30 --patience 0`; en Ultralytics, paciencia 0 desactiva la parada temprana). La tasa de aprendizaje baja linealmente de 0,002 a 0,002 × 0,01 a lo largo de las 30 épocas, y las últimas 10 son sin mosaico (`close_mosaic: 10`), donde la sustitución generativa pasa de p = 0,15 a p = 0,5 |
| Por qué 30 | Se fija por presupuesto antes de ver ningún resultado: 6 corridas × 30 épocas × ~70 s ≈ 3,5 h de GPU. Es más que las 21–22 épocas del análisis exploratorio de H9, con el calendario completo, y la misma exposición para V1 y V3ᵍ. No se elige mirando ninguna métrica |
| Pesos evaluados | `last.pt` (época 30) de las 6 corridas. `best.pt` se guarda, pero **no** se usa para el criterio |
| Datos y validación | Iguales a H9: ExDark-People train (1 183 imágenes) y `data_v2.yaml`. La validación mixta solo se registra (curvas); no selecciona nada |
| Datos generados | Los de H9 (`dataset/generativa_train/`, congelados en v3.3). **No se genera nada nuevo** |
| Variantes | **V1** (sin aumento de oclusión) y **V3ᵍ** (aumento generativo), semillas {0, 1, 2}: **6 corridas** en `runs/argos_gen_fijo/`. V1 se entrena de nuevo (no se reutiliza la V1′ de la iteración 2), para que ambas variantes tengan exactamente la misma exposición |
| Orden | V1_s0, V3_s0, V1_s1, V3_s1, V1_s2, V3_s2 (por pares, de modo que una interrupción deje pares completos) |
| Comando | `07_entrenar.py --protocolo gen --variantes V1 V3 --semillas 0 1 2 --epochs 30 --patience 0 --proyecto argos_gen_fijo --workers 4` |
| Evaluación | `09_ --corridas runs/argos_gen_fijo --pesos-tipo last --resultados resultados_h9b --gt` con los mismos 5 conjuntos de H9: `generativa_severa` (control), `silueta_severa` (descriptivo), `externos/gt_nightowls.json`, `externos/gt_citypersons_convencion.json` y `gt_test_proxy.json` |
| Contrastes | `11_ --resultados resultados_h9b`: V3 − V1 por conjunto y estrato; bootstrap pareado por imágenes, 1 000 réplicas, semilla 0 |
| Veredicto | `26_veredicto_h9b.py` aplica la regla literal de la sección 2 y escribe `informes/veredicto_h9b.md` |
| Costo estimado | ~3,5 h de GPU de entrenamiento + ~0,5 h de evaluación y análisis |

## 4. Lo que NO se hará

- No se cambiarán épocas, paciencia, hiperparámetros, generador, datos ni probabilidades de sustitución después de ver ninguna corrida.
- No se usará `best.pt` para el criterio, ni se elegirá otra época a posteriori.
- No se añadirán semillas ni se cambiarán la métrica o las fuentes del criterio.
- No se cambiará el veredicto de H9.

## 5. Orden de ejecución

1. Cambios en los scripts de análisis, solo de informe: `23_` y `24_` ganan `--secundarios`, que analiza solo los bloques secundarios (H9b) y escribe en ficheros aparte, sin tocar los CSV del análisis consolidado. Se crea `26_veredicto_h9b.py` con autotest.
2. Congelamiento **v3.4**: este documento y los scripts; patrón `PREREGISTRO_*.md`.
3. Las 6 corridas en el orden de la sección 3.
4. Evaluación, contrastes, IC jerárquico, tasa de pérdida y veredicto (`informes/veredicto_h9b.md`). Informe `informes/reporte_h9b_exposicion_fija.md` con el veredicto literal.
5. Solo después: actualizar el short paper y el artículo con el resultado, sea cual sea.
