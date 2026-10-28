# ARGOS-11 — Prerregistro de H18 (E14: réplica de H15 con 5 semillas y dosis del aumento)

Redactado el **2026-10-28**. Se congela como **v3.12** antes de entrenar ninguna corrida de este diseño.

Antes de congelar no se entrenó ni se evaluó nada de este diseño. Solo se comprobó que `35_dos_etapas.py --dosis` construye el generador con los parámetros de la sección 1 (autotest 9/9).

## 0. Contexto (declarado)

**Antecedentes.**
- H1–H17 están cerradas. H15 (Faster R-CNN con siluetas) es el único bloque que cumple la regla en dos fuentes reales (NightOwls +3,28; CityPersons *heavy* +2,33), con 3 semillas.
- El 27/10 un revisor externo del short paper (`Downloads/g1reporte_revision_short_paper_…docx`, observaciones M1 y M4) señaló dos cosas:
  1. **M1.** H15 se trató con un criterio de varianza entre semillas (t de Welch) que no se aplicó al resto de las celdas. Pide un criterio único y, si es posible, repetir H15 con 5 semillas.
  2. **M4.** Todos los bloques usan una sola dosis del aumento (probabilidad 0,5 por imagen, 1–3 personas, cobertura 0,30–0,85). Pide acotar la conclusión a esa dosis o probar otras.
- El borrador de H18 del 24/10 (`D:\argos11\borrador_h18`, sin congelar) incluía además réplicas de H16 y de H17 con tasa 0,01. Se retiran por presupuesto (unos 6 USD de crédito en RunPod) y porque no las pide esta revisión.

**Lo que ya se conoce.** Los resultados de H1–H17 y de los análisis posteriores ya se conocen. Por eso las predicciones se declaran aquí, antes de entrenar.

## 1. Diseño (fijado ahora)

**Lo que no cambia.** Todo lo no mencionado es idéntico a `PREREGISTRO_H15.md`:
- **Detector:** Faster R-CNN ResNet-50 FPN v2 de torchvision, pesos COCO oficiales.
- **Datos:** ExDark-People train, con el cargador de Ultralytics 8.4.143 y el aumento base del proyecto.
- **Receta:** SGD, tasa 0,01, lote 8, 30 épocas fijas, sin validación ni parada temprana; se evalúa `last.pth`.
- **Entrada:** 640 px de lado mayor.
- **Inferencia:** confianza 0,001, 300 detecciones y NMS 0,5.
- **Evaluación:** en la laptop, con `35_dos_etapas.py inferir` y `09_evaluar_estratificado.py`.

**Lo que cambia.** Las **16 corridas** se entrenan en **un solo pod**, con una RTX 4090 y el mismo software, tres a la vez. Así todas las V1 y V3 comparten máquina.

| Bloque | V1 | V3 | Dosis del aumento | Semillas | Carpeta de `runs/` | Corridas |
|---|---|---|---|---|---|---|
| H18a | sí | siluetas | base (la de H15) | 0–4 | `argos_frcnn_r18_sil` | 10 |
| H18e-baja | la de H18a, semillas 0–2 | siluetas | baja | 0–2 | `argos_frcnn_r18_baja` | 3 |
| H18e-alta | la de H18a, semillas 0–2 | siluetas | alta | 0–2 | `argos_frcnn_r18_alta` | 3 |

**Dosis** (`DOSIS` en `35_dos_etapas.py`; solo cambian estos tres parámetros del generador de siluetas v2):

| Dosis | Probabilidad por imagen | Personas ocluidas por imagen | Cobertura de cada persona |
|---|---|---|---|
| baja | 0,25 | 1 | 0,15–0,40 |
| base | 0,50 | 1–3 | 0,30–0,85 |
| alta | 1,00 | 1–6 | 0,50–0,95 |

**Código.**
- `35_dos_etapas.py` gana `--dosis base|baja|alta`. Con `base` (por defecto) el generador es idéntico al de H15 (autotest 9/9).
- `38_h18.py` decide con `celda()` y `veredicto()` de `30_h12.py`, como `36_` y `37_`.
- Resultados en `resultados_h18/det`: `V1_sN`, `V3sil_sN`, `V3baja_sN` y `V3alta_sN`.

## 2. Hipótesis (literal)

**Regla.** Es la de H4–H17. Una fuente real **pasa** si V3 − V1 es ≥ +2 pp con IC 95 % por imágenes > 0. La transferencia se considera **detectada** si pasan 2 o 3 de las tres fuentes:
- NightOwls ocluida;
- CityPersons *heavy*;
- ExDark proxy severa.

Si el control `silueta_severa` no pasa, el bloque es *no concluyente*. Cada hipótesis tiene su propio veredicto, sin corrección conjunta.

- **H18a (réplica de H15 con 5 semillas en una máquina).** Predicción: **no se detecta transferencia**.
  - *Se sostiene* si pasan menos de 2 fuentes, es decir, si H15 **no** se replica.
  - *Se refuta* si pasan 2 o 3, es decir, si H15 se replica.
- **H18e-baja y H18e-alta (dosis del aumento).** Predicción: **no se detecta transferencia con ninguna de las dos dosis**.
  - Cada una *se sostiene* si pasan menos de 2 fuentes y *se refuta* si pasan 2 o 3.

**Criterio uniforme de semillas (declarado ahora; atiende M1).** Junto a la regla, cada celda se informa también con el **IC jerárquico** (remuestreo de semillas e imágenes, 2 000 réplicas), el mismo que se aplica a las 51 celdas de H3–H17. No hay otro criterio de semillas: no se usará la t de Welch para decidir ni para describir.

**Compromiso de reporte.**
- El short paper, el artículo y el suplemento reportarán los tres veredictos tal como salgan, junto a H15 (que no se reescribe).
- Si H18a se refuta, el texto dirá que la transferencia de Faster R-CNN con siluetas se replicó con 5 semillas en una máquina, con las salvedades de especificidad y caja visible que confirmen los análisis secundarios.
- Si H18a se sostiene, dirá que H15 no se replicó con 5 semillas.
- La conclusión se acotará a las dosis probadas, sea cual sea el resultado de H18e.

## 3. Análisis secundarios declarados ahora (no deciden)

1. IC jerárquico de cada celda (sección 2).
2. Dosis-respuesta descriptiva: V3 − V1 en el control y en las tres fuentes para baja, base (H18a, semillas 0–2) y alta.
3. Especificidad: [V3 − V1] en las personas ocluidas menos [V3 − V1] en las personas sin oclusión de la misma fuente.
4. CityPersons *heavy* con la caja visible (`bboxVis`).
5. Variación entre máquinas: V1 y V3sil de H18a frente a las de H15, semillas 0–2.

## 4. Lo que no se hará

- No se ajustará ninguna receta ni dosis después de ver un resultado de V3.
- No se añadirán semillas, épocas ni dosis.
- Si una corrida falla por un error de ejecución, se repetirá con la misma semilla y se registrará en `CAMBIOS_PROTOCOLO.md`.
- Si el crédito se agota antes de terminar, se reportará qué corridas faltan y los bloques incompletos quedarán sin veredicto.
