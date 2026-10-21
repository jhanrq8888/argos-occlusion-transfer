# ARGOS-11 — Referencia descriptiva: ¿qué detecta mejor a las personas realmente ocluidas?

Fecha: 2026-10-17. Declarada en `PREREGISTRO_H14.md`, sección 6, antes de calcularla (v3.9). La corrección de código v3.9c se hizo antes de cualquier resultado. Es descriptiva: no decide ninguna hipótesis. Detecciones en `resultados_ref/`, tabla completa en `informes/REFERENCIA_FUNDACION.md`.

## AP@0.5 en los estratos de oclusión real (mismo evaluador y mismas regiones *ignore* en todas las filas)

| Detector | Ajuste | NightOwls ocluida | CityPersons *heavy* | ExDark proxy severa |
|---|---|---|---|---|
| OWLv2 base (vocabulario abierto) | ninguno | 0,379 | 0,206 | 0,275 |
| Grounding DINO tiny (vocabulario abierto) | ninguno | 0,453 | 0,142 | 0,173 |
| YOLOv11s COCO | ninguno | 0,387 | 0,225 | — |
| RT-DETR-l COCO | ninguno | **0,476** | 0,242 | **0,381** |
| YOLOv11s V1 (E2) | ExDark | 0,309 | 0,154 | 0,255 |
| RT-DETR-l V1 (E6) | ExDark | 0,268 | 0,184 | 0,236 |
| YOLOv11s V1 (E5) | NightOwls, 20 000 imágenes | 0,395 | 0,155 | 0,147 |
| YOLOv11s V1 (E4 / E9) | CityPersons | 0,163 / 0,146 | **0,583 / 0,591** | 0,094 / 0,109 |

Valores medios de 3 semillas en las V1. Los modelos COCO y de vocabulario abierto son de una sola evaluación.

## Lectura

1. **La regla fijada se cumple en sentido negativo:** los detectores de vocabulario abierto **no superan a todos** en las personas ocluidas.
   - En NightOwls, Grounding DINO (0,453) supera a YOLOv11s de COCO, pero no a RT-DETR-l de COCO (0,476).
   - En CityPersons *heavy* y en ExDark quedan por debajo de los modelos de COCO.
   - No se recomendarán como solución, sino como una referencia más.
2. **Lo que más ayuda a las personas muy ocluidas es tener datos reales anotados del dominio.**
   - Entrenar en CityPersons sube su estrato *heavy* de ~0,15–0,24 a **0,58–0,59**, más del doble que cualquier modelo sin ajuste o ajustado en otro dominio.
   - Esa ganancia no se traslada a los otros conjuntos: en NightOwls y ExDark esos modelos quedan por debajo de los de COCO.
   - El aumento sintético añade como mucho +1,4 pp sobre esa base (H11), y nada fuera del dominio.
3. **Los modelos generales sin ajustar son una referencia exigente fuera del dominio de ajuste.** RT-DETR-l de COCO es el mejor en NightOwls ocluida y en ExDark severa, por encima de los modelos ajustados en ExDark y del entrenado con 20 000 imágenes de NightOwls. Confirma la recomendación del artículo de reportar siempre una referencia sin ajuste.

## Recomendación que se desprende (para el artículo)

Para mejorar la detección de personas realmente ocluidas, la evidencia de este estudio apunta, en este orden, a:

1. datos reales anotados del dominio de uso;
2. un detector general con preentrenamiento amplio como referencia;
3. no esperar ganancias del aumento sintético de oclusión.

El banco sintético sirve para comprobar que el aumento se aprendió, no para medir la robustez (ver `informes/analisis_final/SINTETICO_VS_REAL.md`).

## Salvedades

- Una sola consulta de texto por modelo, sin ajuste de umbrales, y un máximo de 300 cajas por imagen.
- Grounding DINO tiny es la variante pequeña.
- CityPersons tiene personas pequeñas (≥ 50 px) en escenas concurridas, que perjudican a los detectores de vocabulario abierto.
