# ARGOS-11 — Pre-registro de H8 (réplica con un detector de otra familia: RT-DETR)

Pre-registrado el **2026-09-26**, **después** de cerrar H1–H7, el análisis final consolidado y el bootstrap jerárquico, y **antes** de entrenar ninguna corrida V3 con RT-DETR. Complementa a `PROTOCOLO.md`, `PROTOCOLO_v2.md` y `PREREGISTRO_H6_H7.md`: lo que no se menciona no cambia (datos de la iteración 2, generador de siluetas v2, validación mixta, evaluación estratificada con regiones *ignore*, bootstrap por imágenes con 1 000 réplicas como criterio y umbral de relevancia de +2 pp). Se congelará como **v3.2** antes de la primera corrida.

## 0. Lo que se hizo antes de este documento (declarado)

1. **Prueba de humo** (1 época, 5 % de los datos): el entrenador de RT-DETR con el aumento de siluetas funciona. Se detectó y resolvió un fallo ajeno al experimento: la librería `thop` 0.1.1 (instalada en S1 para medir el costo) deja ganchos colgados al perfilar RT-DETR; en las corridas de RT-DETR se desactiva solo el conteo informativo de GFLOPs del registro de Ultralytics.
2. **Memoria:** con lote 16, RT-DETR-l ocupa 12,3 GB y desborda los 8 GB de la RTX 5050 (ralentización ~50×). Con **lote 8** ocupa 6,6 GB. Ultralytics acumula gradientes hasta un lote nominal de 64, así que el lote efectivo de la optimización es el mismo que con 16.
3. **Piloto de la receta, solo con V1** (sin aumento de oclusión), semilla 0, 5 épocas, en `runs/piloto_rtdetr/`, para comprobar que RT-DETR aprende con su receta de referencia. Como no incluye ninguna corrida con aumento, no puede sesgar el contraste V3 − V1. El piloto **no forma parte** de H8.
4. **Error de configuración detectado en el primer piloto:** con AdamW explícito, Ultralytics mantiene durante el calentamiento el lr de sesgos por defecto de 0,1 (pensado para SGD). En Adam eso destruye los pesos preentrenados (mAP50 en validación 0,021 / 0,055 / 0,060 en las épocas 1–3). Ultralytics usa 0,0 cuando elige Adam automáticamente («no higher than 0.01 for Adam»). Se fijó `warmup_bias_lr: 0.0` en `config/hiperparametros_rtdetr.yaml` y se repitió el piloto (sección 6). Es una corrección de la receta de entrenamiento, aplicada por igual a V1′ y V3′ y decidida solo con la variante sin aumento.

## 1. Motivación

Todos los bloques anteriores usan detectores de la familia YOLO (convolucionales, de una etapa, con NMS). La objeción más previsible a la conclusión del proyecto es que el déficit de transferencia sea propio de YOLO. RT-DETR (Zhao et al., 2024) es un detector de otra familia: decodificador *transformer* con predicción de conjuntos, sin NMS, con atención global. Es plausible que razone mejor sobre personas parcialmente visibles, así que H8 tiene una oportunidad real de ser refutada.

## 2. Hipótesis (literal; no se reformula después)

- **H8.** El déficit de transferencia se replica con un detector de otra familia: con **RT-DETR-l** entrenado con el protocolo de la iteración 2 (ExDark-People train, aumento de siluetas v2, validación mixta), el contraste V3′ − V1′ (AP@0.5, media de 3 semillas) **no alcanza +2 pp con IC 95 % que excluya el cero en al menos 2 de las 3 fuentes reales** (NightOwls ocluida, CityPersons *heavy*, ExDark proxy severa), aun cuando el control sintético `silueta_severa` sea ≥ +2 pp con IC que excluya el cero.
  - *Refutaría H8:* V3′ − V1′ ≥ +2 pp con IC 95 % por imágenes que excluya el cero en **al menos 2 de las 3** fuentes reales (el mismo criterio de H4).
  - *No concluyente:* (a) el control `silueta_severa` no alcanza +2 pp con IC que excluya el cero (el aumento no se aprendió), o (b) el ajuste no funciona: V1′ de RT-DETR no supera en ExDark test (global) al RT-DETR-l de COCO sin ajustar.
- **Análisis de sensibilidad declarado:** se reportará también el IC jerárquico (semillas + imágenes, `23_bootstrap_jerarquico.py`). El veredicto se decide con el IC por imágenes, como en todo el protocolo.

## 3. Diseño

| Elemento | Definición |
|---|---|
| Modelo | `rtdetr-l.pt` (Ultralytics, preentrenado en COCO; 32 970 476 parámetros; sha256 `c1407dcf…`) |
| Datos, aumento y validación | Idénticos a la iteración 2 (`--protocolo v2`): ExDark-People train (1 183 imágenes), siluetas v2 con banco `siluetas_train`, validación mixta (`data_v2.yaml`) |
| Variantes | **V1′** (sin aumento) y **V3′** (aumento de siluetas), semillas {0, 1, 2}: **6 corridas**. Sin CBAM: su integración en RT-DETR no está definida y no es objeto de H8 |
| Hiperparámetros | `config/hiperparametros_rtdetr.yaml`: idénticos al protocolo (100 épocas, paciencia 20, 640 px, AMP, calentamiento 3 épocas, lrf 0,01) salvo **optimizador AdamW, lr0 1e-4, weight decay 1e-4, lr de sesgos en el calentamiento 0,0** (receta de referencia de RT-DETR; imponerle el SGD ajustado para YOLO sesgaría la comparación en su contra) y **lote 8** (sección 0). La misma receta para V1′ y V3′ |
| Comando | `07_entrenar.py --protocolo v2 --modelo-base rtdetr-l.pt --hiperparametros hiperparametros_rtdetr.yaml --proyecto argos_rtdetr --variantes V1 V3 --semillas 0 1 2 --workers 4` |
| Evaluación | `09_evaluar_estratificado.py` sobre `silueta_severa` (control), NightOwls, CityPersons convención, ExDark proxy y ExDark test global. RT-DETR se carga con su propia clase (sin NMS; hasta 300 detecciones por imagen, confianza ≥ 0,001) |
| Referencia sin ajustar | `rtdetr-l.pt` de COCO (clase *person*) evaluado en los mismos conjuntos |
| Contrastes | V3′ − V1′ por conjunto y estrato; bootstrap pareado por imágenes, 1 000 réplicas; IC jerárquico como sensibilidad |
| Costo estimado | ~3,7 min por época: V1′ con parada temprana ~1,5–2 h; V3′ hasta 100 épocas ~6 h → **~20–25 h de GPU** |

## 4. Lo que NO se hará

- No se ajustarán optimizador, lr, épocas, paciencia ni lote después de ver ninguna corrida V3′.
- No se añadirán semillas ni se cambiará la métrica o las fuentes del criterio.
- El piloto de la sección 0 no se usa en ningún contraste.

## 5. Orden de ejecución

1. Congelamiento v3.2 (añade este documento, `config/hiperparametros_rtdetr.yaml`, `rtdetr-l.pt` y los cambios en `argos_lib/entrenamiento.py`, `07_` y `09_`).
2. Las 6 corridas en `runs/argos_rtdetr/`, en el orden V1_s0, V3_s0, V1_s1, V3_s1, V1_s2, V3_s2.
3. Evaluación, bootstrap, bootstrap jerárquico, diagnóstico e informe `informes/reporte_h8_rtdetr.md` con el veredicto literal.

## 6. Resultado de los pilotos de la receta (V1, semilla 0, 5 épocas; no forman parte de H8)

mAP50 sobre la validación mixta (la misma con la que se selecciona el modelo en la iteración 2):

| Época | RT-DETR, calentamiento de sesgos 0,1 (erróneo) | RT-DETR, calentamiento de sesgos 0,0 (receta final) | YOLOv11s V1′ s0 (referencia) |
|---|---|---|---|
| 1 | 0,021 | 0,269 | 0,535 |
| 2 | 0,055 | 0,500 | 0,539 |
| 3 | 0,060 | 0,525 | 0,537 |
| 4 | — (detenido) | 0,527 | 0,527 |
| 5 | — | 0,533 | 0,511 |

Con la receta final, RT-DETR alcanza en validación el nivel de YOLOv11s (0,533 frente a 0,539). Ritmo: ~3,7 min por época con lote 8; memoria 6,6 GB. La receta queda fijada así para las 6 corridas.
