# ARGOS-11 — H8: réplica con un detector de otra familia (RT-DETR-l)

Corte: 27 de septiembre de 2026, 10:26. Protocolo v3.2b (`a3f6db62…`, congelado el 26/09 antes de la primera corrida V3). Pre-registro `PREREGISTRO_H8.md`. Fuentes: `resultados_h8/` y `informes/analisis_final/bootstrap_jerarquico.csv`.

## 1. Pregunta

Todos los bloques anteriores usan detectores YOLO. ¿El déficit de transferencia es propio de YOLO, o aparece también en un detector de otra familia? RT-DETR-l (Zhao et al., 2024) es un *transformer* con predicción de conjuntos, atención global y sin NMS: si alguna arquitectura podía aprovechar mejor el aumento de oclusión, era esta.

## 2. Qué se entrenó

Mismo protocolo que la iteración 2 (ExDark-People train, siluetas v2, validación mixta), con RT-DETR-l preentrenado en COCO (32,97 M parámetros). Receta: la del protocolo salvo AdamW lr 1e-4, weight decay 1e-4, lr de sesgos en el calentamiento 0 y lote 8 (todo declarado en el pre-registro, con los pilotos que lo motivaron).

| Corrida | Épocas | Horas GPU | Mejor época (*fitness*) | Mejor mAP50 en validación |
|---|---|---|---|---|
| V1_s0 | 31 | 1.74 | 11 | 0.541 |
| V1_s1 | 29 | 1.61 | 9 | 0.541 |
| V1_s2 | 28 | 1.51 | 8 | 0.542 |
| V3_s0 | 51 | 2.85 | 31 | 0.658 |
| V3_s1 | 77 | 4.20 | 57 | 0.660 |
| V3_s2 | 57 | 3.11 | 37 | 0.652 |

6 corridas, 15.0 h de GPU, sin incidentes (26/09 18:52 → 27/09 09:58).

## 3. Resultados: V3′ − V1′ (AP@0.5, media de 3 semillas)

| Conjunto | n | V1′ | V3′ | V3′ − V1′ (pp) | IC 95 % por imágenes (criterio) | IC jerárquico (sensibilidad) |
|---|---|---|---|---|---|---|
| Control sintético: silueta severa | 1858 | 0.036 | 0.145 | +10.97 | [+9.57; +12.36] | [+9.32; +12.83] |
| **NightOwls ocluidos** | 530 | 0.268 | 0.198 | −6.98 | [−8.95; −5.11] | [−11.16; −2.81] |
| **CityPersons heavy** | 733 | 0.185 | 0.150 | −3.47 | [−4.86; −1.81] | [−6.27; −0.74] |
| **ExDark oclusión severa (proxy)** | 101 | 0.236 | 0.214 | −2.21 | [−6.16; +1.59] | [−7.61; +3.39] |
| NightOwls sin oclusión | 2763 | 0.753 | 0.671 | −8.22 | [−9.17; −7.21] | — |
| CityPersons partial | 810 | 0.589 | 0.502 | −8.71 | [−10.43; −6.76] | — |
| ExDark oclusión moderada (proxy) | 190 | 0.504 | 0.443 | −6.11 | [−9.29; −3.22] | — |
| ExDark test global | 2235 | 0.826 | 0.810 | −1.53 | [−2.38; −0.65] | — |

## 4. Veredicto literal

**H8 (texto pre-registrado):** *El déficit de transferencia se replica con un detector de otra familia: con RT-DETR-l entrenado con el protocolo de la iteración 2, V3′−V1′ no alcanza +2 pp con IC 95 % que excluya el cero en al menos 2 de las 3 fuentes reales (NightOwls ocluida, CityPersons heavy, ExDark proxy severa), aun cuando el control silueta_severa sea ≥ +2 pp con IC que excluya el cero.*

1. **Control sintético:** +10.97 pp [+9.57; +12.36] → el aumento se aprendió; el contraste real es informativo.
2. **Comprobación de que el ajuste funciona:** V1′ obtiene 0.826 en ExDark test global frente a 0.781 del RT-DETR-l de COCO sin ajustar → lo supera; no procede «no concluyente».
3. **Fuentes reales que superan +2 pp con IC positivo: 0 de 3** (se necesitaban al menos 2 para refutar).

**Veredicto: H8 sostenida.** Con un detector de otra familia, el aumento sintético de oclusión se aprende (+11.0 pp en oclusión sintética) y no mejora la oclusión real: en NightOwls y CityPersons la **empeora** con intervalo que excluye el cero, también con el intervalo jerárquico que incluye la variación entre semillas.

## 5. Mecanismo (NightOwls ocluidos, confianza ≥ 0,25)

| Variante | Recall | Falsos positivos por imagen | Confianza media de los aciertos |
|---|---|---|---|
| V1′ | 0.524 | 1.225 | 0.610 |
| V3′ | 0.403 | 0.631 | 0.647 |

El mismo patrón que las siluetas en YOLO: el recall de ocluidos reales baja y el modelo se vuelve más conservador (menos falsos positivos, más confianza en lo que sí detecta).

## 6. Sobreajuste de dominio, también en RT-DETR

| Conjunto | RT-DETR-l COCO sin ajustar | V1′ ajustado en ExDark |
|---|---|---|
| ExDark test global | 0.781 | 0.826 |
| NightOwls ocluidos | 0.476 | 0.268 |
| NightOwls sin oclusión | 0.822 | 0.753 |
| CityPersons heavy | 0.242 | 0.185 |

Como en YOLO, ajustar sobre las 1 183 imágenes de ExDark mejora en ExDark y empeora fuera de él: el RT-DETR-l de COCO sin ajustar es el mejor en NightOwls y CityPersons.

## 7. Qué aporta H8 al trabajo

La conclusión ya no es «propia de YOLO»: se repite en tres arquitecturas de dos familias (YOLOv11s y YOLO26s, convolucionales con NMS; RT-DETR-l, *transformer* sin NMS). El aumento sintético de oclusión se aprende en todas y no mejora la oclusión real en ninguna; con siluetas, la empeora en las tres.

Registrado en `CAMBIOS_PROTOCOLO.md`. Veredicto completo en `informes/veredictos_H1_H7.md` (tabla H1–H8).
