# ARGOS-11 — Pre-registro de H15 (E12: detector de dos etapas, Faster R-CNN)

Redactado el **2026-10-20** y congelado como **v3.10** antes de entrenar ninguna corrida de este diseño. Antes de congelar solo se hicieron pruebas de humo del código (una de 3 iteraciones con el 5 % de las imágenes y otra de 2 épocas con V1, semilla 0, en `runs/smoke_frcnn/`, que se descartan y no se usan en ningún contraste; la segunda dio AP@0.5 global 0,798 en la prueba de ExDark, solo para comprobar que el modelo aprende). No se evaluó ninguna V3.

## 0. Contexto (declarado)

- Dos revisiones del *short paper* (20/10/2026) piden un detector de dos etapas: todas las conclusiones se apoyan en detectores de una etapa (YOLOv11s, YOLOv11m, YOLO26s) y en un *transformer* (RT-DETR-l).
- Se conocen ya los resultados de H1–H14: ninguna familia de oclusor se transfiere de forma robusta.
- Se elige la familia de **siluetas** (la de E2, E8 y H12a), con exposición fija, porque es la más estudiada del proyecto y tiene control propio (`silueta_severa`).

## 1. Diseño (fijado ahora)

| Elemento | Definición |
|---|---|
| Detector | Faster R-CNN ResNet-50 FPN v2 de torchvision, pesos COCO oficiales (`fasterrcnn_resnet50_fpn_v2_coco.pth`, sha256 `dd69338a…`); la cabeza de clasificación se sustituye por una de 2 clases (fondo y persona) |
| Datos | ExDark-People train (1 183 imágenes, `dataset/data_v2.yaml`), el mismo cargador de Ultralytics 8.4.143 y el mismo aumento base (`config/aumento_base.yaml`, mosaico con cierre en las últimas 10 épocas) |
| Aumento de V3 | El generador de siluetas v2 (`argos_lib.siluetas.OclusionSiluetas` con `OCLUSION_CFG_V2` de `07_entrenar.py`), idéntico al de E2, E8 y H12a |
| Receta | La de referencia de torchvision para ajuste fino: SGD, lr 0,01 con lote 8, momento 0,9, decaimiento de pesos 1e-4, calentamiento lineal de 500 iteraciones (factor inicial 0,001), decaimiento ×0,1 en las épocas 20 y 27; AMP |
| Exposición | V1 y V3 entrenados **exactamente 30 épocas**, sin validación ni parada temprana; evaluación con los pesos de la última época (`last.pth`) |
| Entrada | Lado mayor 640 (min_size = max_size = 640), como `imgsz` 640 en YOLO |
| Inferencia | Confianza mínima 0,001, máximo 300 detecciones, NMS por clase 0,5 (valor por defecto de torchvision) |
| Semillas | {0, 1, 2} |
| Máquina | RunPod, RTX 4090; V1 y V3 de la misma semilla en la misma máquina. Evaluación en la laptop |
| Código | `35_dos_etapas.py` (entrenamiento e inferencia; escribe la caché de detecciones en el formato de `09_evaluar_estratificado.py`) y `36_h15.py` (veredicto) |

## 2. Hipótesis H15 (literal)

- **H15.** El déficit de transferencia persiste con un detector de dos etapas. V3ˢⁱˡ − V1 (Faster R-CNN, AP@0.5, media de 3 semillas) **no alcanza +2 pp con IC 95 % por imágenes que excluya el cero en al menos 2 de las 3 fuentes reales**: NightOwls ocluida, CityPersons *heavy* y ExDark proxy severa. Esto vale aun cuando el control `silueta_severa` alcance +2 pp con IC > 0.

  | Veredicto | Condición |
  |---|---|
  | *Sostenida* (se confirma la predicción de no transferencia) | Menos de 2 fuentes reales superan +2 pp con IC por imágenes > 0, y el control sí lo hace |
  | *Refutada* | 2 o 3 fuentes reales superan +2 pp con IC por imágenes > 0 |
  | *No concluyente* | El control `silueta_severa` no alcanza +2 pp con IC > 0 (el aumento no se aprendió) |

- **Compromiso de reporte.** Si H15 se refuta, el *short paper* y el artículo dirán que con un detector de dos etapas el aumento **sí** se transfiere y que la conclusión queda acotada a detectores de una etapa y *transformers*. Si se sostiene, dirán que el patrón se repite en un detector de dos etapas. Si es no concluyente, se reportará así, sin repetir con otra receta.

## 3. Análisis secundarios declarados ahora (no deciden H15)

1. IC jerárquico (semillas + imágenes, 2 000 réplicas), con las funciones de `30_h12.py`.
2. Comparación descriptiva con YOLOv11s (V3ˢ − V1 de E8 con 30 épocas): AP de V1 de cada detector en las fuentes reales y si los contrastes cambian de signo.
3. Control con otras familias (`generativa_severa`, `geometria_severa`, `profundidad_severa`), para la matriz cruzada de controles.

## 4. Lo que no se hará

- No se ajustará la receta después de ver ningún resultado de V3; no se añadirán semillas ni épocas.
- Si una corrida falla por un error de ejecución (no por el resultado), se repetirá con la misma semilla y se registrará en `CAMBIOS_PROTOCOLO.md`.
