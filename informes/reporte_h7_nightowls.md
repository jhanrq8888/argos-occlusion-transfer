# ARGOS-11 — H7: escalera de datos sobre NightOwls

Corte: 26 de septiembre de 2026, 16:09. Protocolo v3.1 (`b0043c89a26000d2`, congelado el 25/09 a las 20:58, antes de la primera corrida); pre-registro `PREREGISTRO_H6_H7.md` (sha256 `4b4b56a1…`). Cambio de procedimiento declarado antes de cualquier resultado: orden de ejecución 20 000 → 2 000 → 5 000 → 10 000 (`CAMBIOS_PROTOCOLO.md`, 25/09 21:20). Fuentes: `resultados_h7_{2000,5000,10000,20000}/`.

## 1. Pregunta

¿El déficit de transferencia del aumento sintético de oclusión se debe a la escasez de datos de ExDark-People (1 183 imágenes, 3 271 personas)? Si fuera así, con muchos más datos reales del dominio nocturno el aumento debería empezar a ayudar sobre la oclusión real.

## 2. Datos y diseño

| Peldaño | Imágenes de NightOwls train | Peatones etiquetados | Épocas / paciencia | Presentaciones | Semillas |
|---|---|---|---|---|---|
| 2000 | 2000 | 3296 | 100 / 20 | 200000 | 0 |
| 5000 | 5000 | 8372 | 40 / 8 | 200000 | 0 |
| 10000 | 10000 | 16569 | 20 / 4 | 200000 | 0 |
| 20000 | 20000 | 33274 | 10 / 2 | 200000 | 0, 1, 2 |

Escalera **anidada** (los 2 000 están dentro de los 5 000, etc.), muestreo con semilla 0 entre las 25 670 imágenes de NightOwls train con al menos un peatón. Presupuesto fijo de **200 000 presentaciones** por corrida para que la comparación mida el tamaño del conjunto y no los pasos de optimización. Validación mixta: 1 000 imágenes de NightOwls validation (disjuntas de las 2 000 de evaluación) + su copia ocluida con siluetas del dominio. Evaluación primaria: las mismas 2 000 imágenes de NightOwls val usadas en todo el proyecto (530 peatones ocluidos según el atributo *occluded* de los autores).

## 3. Corridas

| Peldaño | Corrida | Épocas | Horas GPU | Mejor época (*fitness*) |
|---|---|---|---|---|
| 2000 | V1_s0 | 22 | 0.68 | 2 |
| 2000 | V3_s0 | 63 | 1.85 | 43 |
| 5000 | V1_s0 | 9 | 0.64 | 1 |
| 5000 | V3_s0 | 40 | 2.84 | 35 |
| 10000 | V1_s0 | 6 | 0.85 | 2 |
| 10000 | V3_s0 | 20 | 2.85 | 20 |
| 20000 | V1_s0 | 3 | 0.83 | 1 |
| 20000 | V1_s1 | 4 | 1.09 | 2 |
| 20000 | V1_s2 | 3 | 0.81 | 1 |
| 20000 | V3_s0 | 9 | 2.47 | 7 |
| 20000 | V3_s1 | 4 | 1.09 | 2 |
| 20000 | V3_s2 | 10 | 2.69 | 10 |

12 corridas, 18.7 h de GPU registradas, sin incidentes. La parada temprana usa el *fitness* de Ultralytics (0,1·mAP50 + 0,9·mAP50-95); por eso V3_s1 del peldaño de 20 000 paró en la época 4 (mejor *fitness* en la 2) aunque su mAP50 siguiera subiendo, como exige la paciencia de 2 pre-registrada.

## 4. Veredicto literal (peldaño de 20 000, 3 semillas)

**H7 (texto pre-registrado):** *El déficit de transferencia persiste con datos abundantes del dominio nocturno: en el peldaño de 20 000 imágenes de NightOwls train, V3−V1 sobre NightOwls val estrato ocluida no alcanza +2 pp o su IC 95 % incluye el cero.*

| Contraste V3 − V1 | Δ AP@0.5 (pp) | IC 95 % | Excluye 0 |
|---|---|---|---|
| **NightOwls ocluidos (primario, n = 530)** | −1.43 | [−3.98; +1.00] | no |
| NightOwls sin oclusión (n = 2763) | −1.78 | [−2.31; −1.22] | sí |
| NightOwls global (n = 3293) | −2.02 | [−2.59; −1.45] | sí |

1. Umbral: −1.43 pp **no alcanza +2 pp** y el intervalo **incluye el cero** → se cumple la condición de la hipótesis.
2. Refutación (≥ +2 pp con IC que excluya el cero): no se cumple.
3. Comprobación pre-registrada de que el ajuste en el dominio funciona (V1 debe superar a COCO sin ajustar en ocluidos): V1 = 0.395 frente a 0.387 → **la supera** (+0.80 pp). No procede «no concluyente».

**Veredicto: H7 sostenida.** Por semilla, V3−V1 en ocluidos fue −2.47, −0.96, −0.88 pp: las tres negativas.

## 5. Lo que H7 añade: más datos ayudan a los visibles, no a los ocluidos

| NightOwls, AP@0.5 de la variante base (V1) | Ocluidos | Sin oclusión |
|---|---|---|
| YOLOv11s COCO sin ajustar | 0.387 | 0.764 |
| Ajustado en 2000 imágenes de NightOwls | 0.360 | 0.865 |
| Ajustado en 5000 imágenes de NightOwls | 0.419 | 0.885 |
| Ajustado en 10000 imágenes de NightOwls | 0.393 | 0.899 |
| Ajustado en 20000 imágenes de NightOwls (media de 3 semillas) | 0.395 | 0.890 |
| Ajustado en ExDark (exp. 1 / iteración 2) | 0.261 / 0.306 | — |

Con datos del propio dominio el detector mejora mucho a los peatones **visibles** (+12.64 pp sobre COCO en el peldaño de 20 000) pero apenas a los **ocluidos** (+0.80 pp): la oclusión real no se resuelve ni con diez veces más datos ni con el aumento sintético. Ajustar en ExDark, en cambio, empeoraba a los ocluidos de NightOwls por debajo de COCO (sobreajuste de dominio).

## 6. Tendencia por peldaño (análisis secundario, descriptivo)

| Peldaño | V1 ocl. | V3 ocl. | V3−V1 ocluidos [IC imágenes] | V3−V1 sin oclusión [IC] |
|---|---|---|---|---|
| 2000 (1 sem.) | 0.360 | 0.367 | +0.66 [−3.31; +5.13] | +1.76 [+0.82; +2.85] * |
| 5000 (1 sem.) | 0.419 | 0.408 | −1.12 [−4.99; +3.10] | −2.04 [−3.02; −1.26] * |
| 10000 (1 sem.) | 0.393 | 0.437 | +4.38 [+0.17; +8.06] * | −1.57 [−2.47; −0.67] * |
| 20000 (3 sem.) | 0.395 | 0.381 | −1.43 [−3.98; +1.00] | −1.78 [−2.31; −1.22] * |

\* IC que excluye el cero. Con la semilla 0 en los cuatro peldaños (lo que el pre-registro fija para la tendencia), V3−V1 en ocluidos es +0.66, −1.12, +4.38 y −2.47 pp.

**Lectura:** no hay tendencia a que el efecto crezca con los datos; la curva oscila y el único peldaño con tres semillas da un efecto negativo. El peldaño de 10 000 muestra +4.38 pp con IC que excluye el cero, pero es **una sola semilla**, y el intervalo por *bootstrap* de imágenes no incluye la variación entre semillas. Esa variación es grande: en el peldaño de 20 000 las tres semillas dieron −2.47, −0.96, −0.88 pp, y en H6 una sola semilla llegó a +4,02 pp con una media de tres de +1,82. Un +4.38 pp con una semilla está dentro de ese ruido; el pre-registro lo trata como descriptivo y así se reporta, sin descartarlo ni sobreinterpretarlo.

## 7. Efecto fuera del dominio de entrenamiento (descriptivo)

| Peldaño | CityPersons *heavy* V3−V1 | ExDark oclusión severa V3−V1 |
|---|---|---|
| 2000 | −1.72 [−4.07; +0.61] | −8.85 [−14.86; −5.24] * |
| 5000 | −7.07 [−9.79; −4.39] * | −21.21 [−29.46; −14.25] * |
| 10000 | −3.14 [−5.44; −0.67] * | −8.68 [−14.85; −4.39] * |
| 20000 | −3.94 [−5.62; −2.27] * | −9.15 [−13.94; −5.66] * |

Fuera del dominio de entrenamiento, el aumento es negativo en todos los peldaños, casi siempre con IC que excluye el cero, igual que en los experimentos anteriores.

## 8. Conclusión de H6 + H7

Las dos explicaciones alternativas que quedaban para el déficit de transferencia están contrastadas:

- **Cambio de dominio (H6):** entrenar en el dominio de evaluación explica el signo negativo, pero deja un efecto de +1,82 pp, bajo el umbral y 13 veces menor que el sintético.
- **Escasez de datos (H7):** con 20 000 imágenes y 33 274 peatones del dominio nocturno, el efecto sobre ocluidos es −1.43 pp [−3.98; +1.00]. Más datos mejoran a los visibles, no a los ocluidos.

El aumento sintético de oclusión, tal como se usa en la literatura, no transfiere a oclusión real en ninguna de las condiciones probadas.

Registrado en `CAMBIOS_PROTOCOLO.md`. Veredicto completo en `informes/veredictos_H1_H7.md`.
