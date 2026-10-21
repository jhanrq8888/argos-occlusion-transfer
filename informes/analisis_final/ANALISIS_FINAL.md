# ARGOS-11 — Análisis final consolidado

Corte: 3 de octubre de 2026 (actualizado con H9, tercera familia de oclusor: oclusión generativa). Actividad del cronograma "Análisis final consolidado y figuras definitivas" (prevista para S5, adelantada a S3). Todo lo que sigue se genera con `22_analisis_final.py` a partir de los ficheros de análisis de cada bloque; no se recalculó ningún resultado previo. La única cifra nueva es el intervalo de confianza propio de la réplica con YOLO26s (antes solo existía mezclado con YOLOv11s, en un análisis marcado como no citable), calculado con el mismo *bootstrap* que el resto (`resultados_v2/analisis_yolo26s/`).

## 1. Resultado en una frase

En **siete bloques experimentales** (tres familias de oclusor sintético: parches, siluetas y oclusores pintados por un modelo de difusión; tres arquitecturas de dos familias de detectores, YOLOv11s y YOLO26s convolucionales y RT-DETR-l *transformer*; y tres dominios de entrenamiento: ExDark, CityPersons y NightOwls), el aumento sintético de oclusión mejora el AP@0.5 entre **+2,6 y +60,9 puntos porcentuales sobre oclusión sintética** (6 de 6 controles superan el umbral de relevancia) y **solo 1 de las 21 mediciones sobre oclusión real** supera ese umbral con el intervalo pre-registrado (H9 en ExDark proxy, +2,8 pp, n = 101), que **no resiste el intervalo jerárquico**: con él, 0 de 21. Las mediciones reales van de −16,8 a +2,8 pp.

## 2. Qué se consolida

| Bloque | Aumento | Arquitectura | Entrenamiento | Corridas | Protocolo |
|---|---|---|---|---|---|
| Experimento 1 | parches (textura, recorte, opaco) | YOLOv11s | ExDark-People, 1 183 imágenes | 14 | v1.1b |
| Iteración 2 | siluetas con máscara | YOLOv11s | ExDark-People | 12 | v2.0 |
| Generalidad | siluetas con máscara | YOLO26s | ExDark-People | 6 | v2.0 |
| H6 | siluetas del dominio | YOLOv11s | CityPersons, 2 675 imágenes | 6 | v3.0 |
| H7 | siluetas del dominio | YOLOv11s | NightOwls, 2 000 a 20 000 imágenes | 12 | v3.1 |
| H8 | siluetas con máscara | **RT-DETR-l** (*transformer*, sin NMS) | ExDark-People | 6 | v3.2b |
| H9 | **oclusión generativa** (Stable Diffusion *inpainting*) | YOLOv11s | ExDark-People (V1′ reutilizada de la iteración 2) | 3 | v3.3b |

**59 corridas, ≈79 h de GPU de entrenamiento** (más ~5,7 h para generar los oclusores de H9), todas con los mismos hiperparámetros congelados (salvo el optimizador de RT-DETR, que sigue su receta de referencia y se declaró en su pre-registro) y evaluadas con el mismo código sobre las mismas tres fuentes de oclusión real: NightOwls (atributo *occluded* de los autores, 530 peatones), CityPersons (visibilidad oficial, 733 *heavy*) y ExDark (oclusión entre personas calculada desde las cajas, 101 severas).

## 3. Tabla consolidada: efecto del aumento (V3 − V1)

| Bloque | Conjunto | Tipo | n | V1 | V3 | V3 − V1 (pp) | IC 95 % | ≥ +2 pp con IC > 0 |
|---|---|---|---|---|---|---|---|---|
| Exp. 1 · parches · YOLOv11s · ExDark | opaco severa | sintético (control) | 2131 | 0,013 | 0,622 | **+60,92** | [+58,50; +63,41] | sí |
| | NightOwls ocluidos | real | 530 | 0,261 | 0,230 | **−3,17** | [−4,58; −1,74] | no |
| | CityPersons *heavy* | real | 733 | 0,138 | 0,135 | **−0,36** | [−1,06; +0,31] | no |
| | ExDark severa | real | 101 | 0,270 | 0,238 | **−3,25** | [−5,81; −0,21] | no |
| Iter. 2 · siluetas · YOLOv11s · ExDark | silueta severa | sintético (control) | 1858 | 0,041 | 0,148 | **+10,63** | [+9,42; +12,15] | sí |
| | NightOwls ocluidos | real | 530 | 0,306 | 0,138 | **−16,79** | [−19,59; −13,96] | no |
| | CityPersons *heavy* | real | 733 | 0,153 | 0,113 | **−3,94** | [−5,66; −2,41] | no |
| | ExDark severa | real | 101 | 0,244 | 0,194 | **−5,02** | [−10,72; +0,50] | no |
| Generalidad · siluetas · YOLO26s · ExDark | silueta severa | sintético (control) | 1858 | 0,035 | 0,155 | **+12,01** | [+10,61; +13,57] | sí |
| | NightOwls ocluidos | real | 530 | 0,312 | 0,169 | **−14,31** | [−17,35; −11,10] | no |
| | CityPersons *heavy* | real | 733 | 0,156 | 0,112 | **−4,42** | [−5,95; −2,63] | no |
| | ExDark severa | real | 101 | 0,271 | 0,235 | **−3,51** | [−8,38; +1,21] | no |
| H6 · siluetas · YOLOv11s · CityPersons | silueta severa (CP) | sintético (control) | 684 | 0,100 | 0,337 | **+23,74** | [+21,09; +26,51] | sí |
| | NightOwls ocluidos | real | 530 | 0,163 | 0,149 | **−1,35** | [−2,85; +0,20] | no |
| | CityPersons *heavy* | real | 733 | 0,583 | 0,601 | **+1,82** | [+0,31; +3,31] | no |
| | ExDark severa | real | 101 | 0,094 | 0,103 | **+0,94** | [−2,53; +4,72] | no |
| H7 · siluetas · YOLOv11s · NightOwls 20k | NightOwls ocluidos | real | 530 | 0,395 | 0,381 | **−1,43** | [−3,98; +1,00] | no |
| | CityPersons *heavy* | real | 733 | 0,155 | 0,115 | **−3,94** | [−5,62; −2,27] | no |
| | ExDark severa | real | 101 | 0,147 | 0,055 | **−9,15** | [−13,94; −5,66] | no |
| H8 · siluetas · RT-DETR-l · ExDark | silueta severa | sintético (control) | 1858 | 0,036 | 0,145 | **+10,97** | [+9,57; +12,36] | sí |
| | NightOwls ocluidos | real | 530 | 0,268 | 0,198 | **−6,98** | [−8,95; −5,11] | no |
| | CityPersons *heavy* | real | 733 | 0,185 | 0,150 | **−3,47** | [−4,86; −1,81] | no |
| | ExDark severa | real | 101 | 0,236 | 0,214 | **−2,21** | [−6,16; +1,59] | no |
| H9 · generativa · YOLOv11s · ExDark | generativa severa | sintético (control) | 2018 | 0,018 | 0,044 | **+2,60** | [+2,12; +3,09] | sí |
| | NightOwls ocluidos | real | 530 | 0,306 | 0,287 | **−1,93** | [−2,89; −0,88] | no |
| | CityPersons *heavy* | real | 733 | 0,153 | 0,165 | **+1,23** | [+0,36; +2,11] | no |
| | ExDark severa | real | 101 | 0,244 | 0,272 | **+2,82** | [+0,37; +5,99] | sí (no con el IC jerárquico) |

Media de 3 semillas por variante. IC 95 % por *bootstrap* pareado sobre imágenes (1 000 réplicas). Umbral de relevancia de +2 pp fijado en el PPI antes de experimentar. H7 no tiene control sintético porque no se pre-registró. Datos en `tabla_consolidada.csv`.

**Recuento:** controles sintéticos que superan el umbral con IC positivo, **6 de 6**; mediciones sobre oclusión real que lo superan, **1 de 21** (H9 en ExDark proxy; 0 de 21 con el IC jerárquico). De esas 21, **17 son negativas** (11 de ellas con IC que excluye el cero) y 4 positivas. La única positiva con IC por imágenes que excluye el cero es H6 en su propio dominio (+1,82 pp), por debajo del umbral, y **deja de excluir el cero al incluir la variación entre semillas** (sección 5).

## 4. Figuras definitivas

Cada figura se guarda en PNG (220 ppp) y PDF vectorial, con una paleta validada para daltonismo: azul = variante base o control sintético, naranja = aumento u oclusión real.

**Figura 1 · `fig1_bloques_sintetico_vs_real`.** Efecto del aumento en cada uno de los siete bloques (filas) y cada conjunto de evaluación (paneles), con dos intervalos: el pre-registrado por imágenes (trazo grueso) y el jerárquico con semillas (trazo fino). El primer panel (sintético) queda entero a la derecha del umbral; los tres paneles reales quedan a la izquierda o en torno a cero. Es la figura central del trabajo.

**Figura 2 · `fig2_h7_escalera`.** AP de V1 y V3 en NightOwls frente al tamaño del entrenamiento, con el modelo COCO sin ajustar como referencia. Los peatones visibles mejoran claramente con datos del dominio (0,865 → 0,890; COCO 0,764), los ocluidos apenas (0,360–0,419; COCO 0,387), y la diferencia entre V1 y V3 cambia de signo de un peldaño a otro sin tendencia. Solo el peldaño de 20 000 tiene tres semillas.

**Figura 3 · `fig3_mecanismo`.** Recall y falsos positivos sobre peatones ocluidos de NightOwls, de V1 a V3, en seis bloques. El recall **baja en los seis** (de 0,34 a 0,32; de 0,39 a 0,24; de 0,33 a 0,25; de 0,52 a 0,47; de 0,52 a 0,40 con RT-DETR; de 0,39 a 0,35 con oclusión generativa). Los falsos positivos se mueven poco, salvo en H6 y en RT-DETR, donde bajan con el recall: el modelo se vuelve más conservador en conjunto, no más capaz con los ocluidos.

**Figura 4 · `fig4_costo`.** FPS por variante: todas superan con holgura los 30 FPS del criterio (c); el CBAM reduce la velocidad un 15 % (V2) y un 18 % (V4), por debajo del 90 % del baseline que exigía H1.

## 5. Sensibilidad: bootstrap jerárquico (semillas + imágenes)

Los intervalos del protocolo remuestrean imágenes con las semillas fijas. Como análisis de sensibilidad declarado, se recalcularon remuestreando también las semillas (`23_bootstrap_jerarquico.py`, 2 000 réplicas; detalle en `BOOTSTRAP_JERARQUICO.md`). La figura 1 muestra ambos: trazo grueso (pre-registrado) y trazo fino (jerárquico). Los intervalos se ensanchan de media ×1,66.

- **Se mantiene:** 6 de 6 controles sintéticos superan el umbral y 0 de 21 mediciones reales lo hacen (la de H9 en ExDark proxy, +2,82, pasa a [−1,23; +7,40]); el daño con siluetas en NightOwls y CityPersons sigue excluyendo el cero en las tres arquitecturas (YOLOv11s, YOLO26s y RT-DETR-l); **ningún veredicto cambia**, incluido H8.
- **Se debilita:** 4 celdas dejan de excluir el cero: experimento 1 en NightOwls (−3,17) y en ExDark (−3,25), H6 en CityPersons *heavy* (+1,82) y H7 en CityPersons (−3,94, descriptivo). Por tanto, con parches solo se puede afirmar que el aumento **no mejora** la detección real (no que la empeore), y el +1,82 pp de H6 es **indistinguible de cero**.

## 5b. Sensibilidad a la métrica: tasa de pérdida promedio logarítmica (27/09, posterior y declarada)

La *log-average miss rate* (MR⁻², menor es mejor) es la métrica habitual en detección de peatones. `24_miss_rate.py` la calcula con las mismas detecciones, el mismo emparejamiento con regiones *ignore* y el mismo bootstrap (1 000 réplicas; también jerárquico). El umbral de relevancia se trasladó del AP: V3 − V1 ≤ −2 pp con IC < 0. Salida: `miss_rate.csv`.

- **Controles sintéticos:** 5 de 6 con mejora relevante (−4,2 a −35,5 pp); el de H9 mejora poco (−1,17 pp).
- **Oclusión real:** 2 de 21 con mejora relevante (H6 en CityPersons y H9 en ExDark proxy, −3,24 pp, que no resiste el jerárquico), y 13 de 21 empeoran con IC por imágenes > 0 (H9 empeora NightOwls, +1,38).
- **La excepción es H6 en su propio dominio:** CityPersons *heavy* −3,17 pp [−5,16; −0,97]; con el jerárquico [−5,87; −0,50]. Es coherente con su AP (+1,82 pp) y con su recall (0,584 → 0,610). Entrenar en el dominio deja un beneficio pequeño en ese dominio, unas 4 veces menor que su control sintético (−11,73 pp). Ninguna otra combinación mejora.
- **Ningún veredicto cambia**, porque los criterios pre-registrados son de AP@0.5.

## 6. Veredictos de las hipótesis pre-registradas

| H | Qué afirmaba | Veredicto |
|---|---|---|
| H1 | ARGOS-11 (V4) mejora a la base en oclusión moderada y severa, con ≥ 90 % de los FPS | no sostenida |
| H2 | El aumento aporta más que el CBAM en los estratos ocluidos | no sostenida |
| H3 | La dirección del efecto se conserva sobre oclusión real en ≥ 2 de 3 fuentes | no sostenida (0 de 3) |
| H4 | Con siluetas reales, el aumento mejora en ≥ 2 de 3 fuentes reales | refutada |
| H5 | Con siluetas, menor mejora sintética y menor brecha sintético-real | parcialmente sostenida |
| H6 | El déficit se replica al re-entrenar en CityPersons | sostenida |
| H7 | El déficit persiste con 20 000 imágenes del dominio nocturno | sostenida |
| H8 | El déficit se replica con un detector de otra familia (RT-DETR-l) | sostenida (0 de 3 fuentes mejoran) |
| H9 | El déficit se replica con una tercera familia de oclusor (generativa) | sostenida (1 de 3 fuentes mejora; se requerían 2) |

Redacción literal y evidencia celda a celda: `informes/veredictos_H1_H7.md`.

## 7. Conclusión integrada

1. **El aumento sintético de oclusión se aprende, pero no transfiere.** Los cinco controles sintéticos confirman que el aumento funcionó (+10 a +61 pp); la oclusión real no mejora en ningún bloque. Esto se sostiene con los dos métodos de intervalo. Con siluetas, además, la empeora de forma robusta; con parches, el posible daño no es distinguible de cero.
2. **No depende de la forma ni del realismo del oclusor, del tipo de detector ni de la semilla.** Parches, siluetas y oclusores generados por difusión (H9: el control mejora +2,6 pp; en oclusión real, NightOwls −1,9, CityPersons +1,2 y ExDark +2,8, este último no robusto; con los pesos finales, exploratorio, el control sube a +8,3 y ninguna fuente real mejora); YOLOv11s, YOLO26s y RT-DETR-l (dos familias: convolucional con NMS y *transformer* sin NMS); y las tres semillas dan el mismo patrón. Con RT-DETR, el aumento de siluetas empeora la oclusión real (NightOwls −7,0 pp; CityPersons −3,5 pp) igual que con YOLO.
3. **Las dos explicaciones alternativas quedan contrastadas.** Entrenar en el dominio de evaluación (H6) lleva el efecto de negativo a nulo o levemente positivo (+1,8 pp, bajo el umbral, 13 veces menor que el sintético e indistinguible de cero al incluir la variación entre semillas). Tener diez veces más datos del dominio (H7) no cambia el resultado (−1,4 pp).
4. **La oclusión real resiste incluso a los datos.** Más datos del dominio mejoran a los peatones visibles en +12,6 pp sobre el modelo genérico, y a los ocluidos apenas +0,8 pp.
5. **El módulo CBAM no aporta precisión** en ninguna fuente real con ningún método de intervalo, y cuesta un 15–18 % de velocidad. Que la reste solo es robusto en la iteración 2.

## 8. Limitaciones que se declaran

- **Tres semillas por variante.** El intervalo pre-registrado (por imágenes) no captura la variación entre semillas, que llegó a ~5 pp en diferencias V3−V1 de una sola semilla; por eso se añadió el bootstrap jerárquico (sección 5) y los peldaños de H7 con una semilla se tratan solo como descriptivos. Con tres semillas, el remuestreo de semillas es grueso (10 combinaciones por variante): la extensión a cinco semillas, ya pre-registrada, lo afinaría.
- **El proxy de oclusión en ExDark es parcial.** Solo capta oclusión entre personas y su correlación con la oclusión real en CityPersons es moderada (Spearman 0,24); las conclusiones descansan sobre todo en NightOwls y CityPersons, anotados por humanos. El estrato severo del proxy tiene n = 101, de ahí sus intervalos anchos.
- **Paciencia corta en los peldaños grandes de H7.** La paciencia pre-registrada (épocas/5, mínimo 2) hizo parar algunas corridas pronto, por diferencias de milésimas en la métrica de selección. Es lo pre-registrado, pero limita cuánto se entrenó en esos casos.
- **Dos familias de detectores, un solo tamaño por arquitectura.** La generalidad está probada en YOLOv11s, YOLO26s y RT-DETR-l; no se probaron detectores de dos etapas (tipo Faster R-CNN) ni tamaños mayores. RT-DETR se entrenó con su receta de referencia (AdamW) y lote 8 por la memoria de la GPU, ambos declarados en su pre-registro.
- **Oclusión generativa con poca exposición.** La regla pre-registrada eligió la época 2 en las tres corridas de H9, así que el aumento apenas se entrenó (control +2,6 pp). El análisis exploratorio con los pesos finales (control +8,3 pp) no cambia la conclusión. Además, en el 4,5 % de las imágenes generadas la difusión dibujó una persona nueva sin etiquetar.
- **Anotación manual descartada.** El plan original usaba oclusión anotada a ojo; resultó no reproducible y no interviene en ningún resultado.

## 9. Trazabilidad

| Qué | Dónde |
|---|---|
| Script de este análisis | `22_analisis_final.py` (con `--selftest`) |
| Tabla consolidada | `informes/analisis_final/tabla_consolidada.{csv,md}` |
| Bootstrap jerárquico | `23_bootstrap_jerarquico.py` → `informes/analisis_final/bootstrap_jerarquico.csv`, `BOOTSTRAP_JERARQUICO.md` |
| Figuras | `informes/analisis_final/fig{1,2,3,4}_*.{png,pdf}` |
| H8 (RT-DETR) | `PREREGISTRO_H8.md`, `resultados_h8/`, `informes/reporte_h8_rtdetr.md` |
| H9 (oclusión generativa) | `PREREGISTRO_H9.md`, `resultados_h9/` (y `resultados_h9_last/`, exploratorio), `informes/reporte_h9_generativa.md` |
| Análisis por bloque | `resultados/analisis/`, `resultados_v2/analisis_yolo11s/`, `resultados_v2/analisis_yolo26s/`, `resultados_h6/analisis/`, `resultados_h7_*/analisis/`, `resultados_h8/analisis/` |
| Informes por bloque | `informes/reporte_oclusion_real_32_corridas.md`, `reporte_h6_citypersons.md`, `reporte_h7_nightowls.md`, `reporte_h8_rtdetr.md` |
| Protocolo y registro | `protocolo_congelado.json` (v3.3d), `CAMBIOS_PROTOCOLO.md` |

## Adenda (06/10/2026): réplica pre-registrada E7b (H9b)

Después de este análisis se pre-registró y corrió **E7b** (`PREREGISTRO_H9b.md`, v3.4): la familia generativa con **30 épocas fijas** para V1 y V3ᵍ, sin parada temprana, evaluada con los pesos finales (6 corridas, 3,6 h de GPU; total del proyecto: **65 corridas, ~83 h**). Resultado V3ᵍ − V1 (AP@0.5, pp; IC por imágenes):

- control `generativa_severa`: **+15,23** [+14,00; +17,16];
- NightOwls ocluida: +0,01 [−1,02; +1,20];
- CityPersons *heavy*: +1,52 [+0,79; +2,66];
- ExDark proxy severa: −3,03 [−6,77; +0,99].

**H9b sostenida (0 de 3).** La única celda real que superaba el umbral (E7, ExDark proxy +2,82) pasa a ser negativa. E7b no se suma a las tablas de este documento ni al recuento de 21 mediciones de E1–E7. Detalle: `informes/reporte_h9b_exposicion_fija.md` y `informes/veredicto_h9b.md`; IC jerárquico y tasa de pérdida en `bootstrap_jerarquico_secundarios.csv` y `miss_rate_secundarios.csv`.
