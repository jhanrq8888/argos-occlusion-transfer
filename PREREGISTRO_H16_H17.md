# ARGOS-11 — Pre-registro de H16 y H17 (E13: ¿de qué depende la transferencia de Faster R-CNN?)

Redactado el **2026-10-22** y congelado como **v3.11** antes de entrenar ninguna corrida de este diseño. Antes de congelar solo se hicieron pruebas de humo del código, en `runs/smoke_frcnn/`; se descartan y no entran en ningún contraste:

- 3 iteraciones con el 5 % de las imágenes para cada combinación nueva: RetinaNet con siluetas, y Faster R-CNN con las familias generativa y de profundidad.
- 2 épocas de RetinaNet V1, semilla 0, solo para comprobar que el modelo aprende. Su AP en la prueba de ExDark se anota en `CAMBIOS_PROTOCOLO.md`.
- La tasa de sustitución de los generadores gen y prof en 400 imágenes de train: 0,19 y 0,16 con mosaico, 0,52 y 0,51 sin mosaico, frente a 0,15 y 0,5 configurados.

No se evaluó ninguna V3.

## 0. Contexto (declarado)

- H15 fue refutada el 21/10/2026. Con Faster R-CNN, V3ˢⁱˡ − V1 supera +2 pp con IC > 0 en NightOwls ocluida (+3,28) y en CityPersons *heavy* (+2,33). Es la primera transferencia del programa. Con YOLOv11s, YOLOv11m, YOLO26s y RT-DETR-l, ninguna familia de oclusor se transfirió de forma robusta (H4–H14).
- El artículo debe acotar ese resultado, y quedan dos preguntas abiertas que este bloque responde:
  1. **¿Depende de la familia de oclusor?** H15 usó solo siluetas. ¿Se repite con los oclusores generativos (difusión, H9/H9b) y con los de orden de profundidad (H14)? → **H16**.
  2. **¿Depende de las dos etapas o de la receta?** Faster R-CNN difiere de YOLO a la vez en la arquitectura de dos etapas (RPN + cabeza RoI) y en todo lo demás: columna ResNet-50 FPN, pesos COCO de torchvision, receta SGD y cargador. RetinaNet ResNet-50 FPN v2 es de una etapa y comparte la columna, la familia de pesos, la receta y el cargador de H15 → **H17**.
- Ambas hipótesis se formulan después de conocer el resultado de H15. Por eso la dirección de cada predicción se declara aquí, antes de entrenar.

## 1. Diseño (fijado ahora)

Todo lo que no se menciona es idéntico a `PREREGISTRO_H15.md`, sección 1:

- datos: ExDark-People train, `dataset/data_v2.yaml`, el cargador de Ultralytics 8.4.143 y `config/aumento_base.yaml`;
- 30 épocas fijas, sin validación ni parada temprana, con evaluación de `last.pth`;
- lado mayor 640;
- inferencia con confianza 0,001, 300 detecciones y NMS 0,5;
- semillas {0, 1, 2};
- RunPod con una RTX 4090 y evaluación en la laptop.

| Bloque | Detector | Variantes nuevas | V1 de referencia | Control | Corridas nuevas |
|---|---|---|---|---|---|
| **H16a** | Faster R-CNN (`--detector frcnn`) | V3ᵍᵉⁿ: generador de H9b (`argos_lib.generativa.OclusionGenerativa`, `OCLUSION_CFG_GEN`, `dataset/generativa_train`) | Las 3 V1 de H15 (`runs/argos_frcnn/V1_s{0,1,2}`) | `generativa_severa` | 3 |
| **H16b** | Faster R-CNN | V3ᵖʳᵒᶠ: generador de H14 (`OCLUSION_CFG_PROF`, `dataset/profundidad_train`) | Las 3 V1 de H15 | `profundidad_severa` | 3 |
| **H17** | RetinaNet ResNet-50 FPN v2 (`--detector retina`), pesos COCO oficiales (`retinanet_resnet50_fpn_v2_coco.pth`, sha256 `5905b1c5…`); cabeza de clasificación sustituida por una de 2 clases (`RetinaNetClassificationHead`, GroupNorm 32, como la original) | V1 y V3ˢⁱˡ: siluetas v2, las de H15 | Su propia V1, entrenada en la misma máquina | `silueta_severa` | 6 |
| Réplica (secundario) | Faster R-CNN | V1, semilla 0, entrenada de nuevo en el pod de este bloque (`runs/argos_frcnn_rep/V1_s0`) | — | — | 1 |

- **Receta de RetinaNet.** Es la de Faster R-CNN en H15 (SGD con momento 0,9, decaimiento de pesos 1e-4, 500 iteraciones de calentamiento, ×0,1 en las épocas 20 y 27, AMP, lote 8). Cambia solo la tasa: 0,005, que es la de referencia de torchvision para RetinaNet (0,01 con lote 16) escalada linealmente al lote 8. Lo mismo se hizo con Faster R-CNN: 0,02 con lote 16 → 0,01.
- **V1 de H16.** Se reutilizan las tres V1 de Faster R-CNN de H15, como H12b reutilizó las V1 de H12a. Esas V1 se entrenaron en otro pod del mismo modelo de GPU (RTX 4090) con el mismo código, que no cambia para `--familia sil`. La réplica de V1 semilla 0 mide cuánto cambia el AP entre pods. Es secundaria y no decide nada (sección 3.5).
- **Código.** `35_dos_etapas.py` gana `--detector {frcnn, retina}` y `--familia {sil, gen, prof}`. Los valores por defecto reproducen H15 sin cambios y el autotest pasa de 5 a 8 comprobaciones. El veredicto lo calcula `37_h16_h17.py`, con las mismas funciones `celda()` y `veredicto()` de `30_h12.py` que usó `36_h15.py`.
- **Nombres en la evaluación:**
  - `resultados_h16/det/V3gen_sN` y `V3prof_sN`; la V1 de H16 se lee de `resultados_h15/det/V1_sN`;
  - `resultados_h17/det/V1_sN` y `V3sil_sN`;
  - `resultados_h16/det/V1rep_s0`.

## 2. Hipótesis (literal)

Todas usan la regla de H4–H15 sobre las mismas cuatro celdas: el control sintético de la familia y las tres fuentes reales, que son NightOwls ocluida, CityPersons *heavy* y ExDark proxy severa. Una fuente **supera** si V3 − V1 (AP@0.5, media de 3 semillas) es ≥ +2 pp y su IC 95 % por imágenes excluye el cero.

- **H16a (predicción: transferencia).** Con Faster R-CNN, el aumento generativo también se transfiere: V3ᵍᵉⁿ − V1 supera +2 pp con IC por imágenes > 0 en **al menos 2 de las 3 fuentes reales**.
- **H16b (predicción: transferencia).** Lo mismo con los oclusores de orden de profundidad, V3ᵖʳᵒᶠ − V1.

  | Veredicto de H16a / H16b | Condición |
  |---|---|
  | *Sostenida* (la transferencia de Faster R-CNN se extiende a esa familia) | El control de la familia supera, y 2 o 3 fuentes reales superan |
  | *Refutada* (la transferencia no se extiende a esa familia) | El control supera, y menos de 2 fuentes reales superan |
  | *No concluyente* | El control de la familia no supera (el aumento no se aprendió) |

- **H17 (predicción: no transferencia; las dos etapas importan).** Con RetinaNet, que es de una etapa pero comparte la columna, los pesos y la receta de H15, V3ˢⁱˡ − V1 **no** supera +2 pp con IC por imágenes > 0 en al menos 2 de las 3 fuentes reales, aunque el control `silueta_severa` supere.

  | Veredicto de H17 | Condición | Lectura fijada |
  |---|---|---|
  | *Sostenida* | El control supera, y menos de 2 fuentes reales superan | La transferencia de H15 está ligada a la arquitectura de dos etapas y no a la columna, la receta o el cargador de torchvision |
  | *Refutada* | 2 o 3 fuentes reales superan | La transferencia no exige dos etapas. Se atribuye a lo que comparten Faster R-CNN y RetinaNet (columna ResNet-50 FPN, pesos COCO de torchvision, receta SGD) frente a YOLO y RT-DETR |
  | *No concluyente* | El control no supera | Sin lectura. RetinaNet no aprendió el aumento con esta receta y no se repite con otra |

- **Multiplicidad.** H16a, H16b y H17 tienen cada una su propio veredicto con su propia regla, sin corrección conjunta, como H12a y H12b. No se combinan en un veredicto global.
- **Compromiso de reporte.**
  - El *short paper* y el artículo reportarán los tres veredictos tal como salgan, en la tabla de hipótesis y en el texto.
  - Si H16a o H16b se refutan, dirán que la transferencia de Faster R-CNN depende de la familia de oclusor.
  - Si H17 se refuta, dejarán de atribuir la transferencia a las dos etapas.
  - El título actual («Las ganancias sobre oclusión sintética no anticipan…») se mantiene sea cual sea el resultado. Se revisará solo si el control y la ganancia real de los tres bloques nuevos hacen falsa esa afirmación, es decir, si ganancias sintéticas parecidas pasan a ir siempre con ganancias reales parecidas.

## 3. Análisis secundarios declarados ahora (no deciden nada)

1. IC jerárquico (semillas e imágenes, 2 000 réplicas) para todas las celdas.
2. **Especificidad de la oclusión.** Para cada bloque se reporta, de forma descriptiva, el V3 − V1 por estrato: NightOwls sin oclusión y ocluida; CityPersons *bare*, *partial* y *heavy*; ExDark proxy por grado. Igual que en H15, la ganancia se considera propia de la oclusión si en la fuente es mayor en los estratos ocluidos que en el visible.
3. MR⁻² en NightOwls y CityPersons (`informes/mr_bloques_recientes.py`).
4. **Controles cruzados.** Cada V3 se evalúa también en los controles de las otras familias (`silueta_severa`, `generativa_severa`, `geometria_severa`, `profundidad_severa`) para la matriz cruzada.
5. **Réplica entre pods.** Diferencia de AP@0.5 entre `V1rep_s0` y `V1_s0` de H15 en las tres fuentes reales y en los cuatro controles. Si alguna supera 2 pp en una fuente real, se reporta como límite de la reutilización de V1 en H16 y H16 se interpreta con esa cautela. El veredicto no se cambia.
6. **Comparación descriptiva entre detectores.** AP de V1 y V3 − V1 de RetinaNet frente a Faster R-CNN (H15) y YOLOv11s y YOLOv11m (E8 y H12a), con siluetas en las cuatro celdas.

## 4. Lo que no se hará

- No se ajustará ninguna receta después de ver un resultado de V3, ni se añadirán semillas o épocas.
- Si H17 resulta no concluyente, RetinaNet no se repetirá con otra tasa ni con otro número de épocas.
- Si una corrida falla por un error de ejecución (no por el resultado), se repetirá con la misma semilla y se registrará en `CAMBIOS_PROTOCOLO.md`.
