# ARGOS-11 — Reporte breve: aumento sintético de oclusión frente a oclusión real

Corte: 19 de septiembre de 2026. Fuentes: `resultados/resumen_ap.csv`, `resultados/analisis/bootstrap.csv` (experimento 1), `resultados_v2/resumen_ap.csv`, `resultados_v2/analisis_yolo11s/bootstrap.csv` (iteración 2, solo corridas YOLOv11s; recalculado el 19/09 para no mezclar arquitecturas en los contrastes), `resultados/eval/preliminar_coco_person.json`. Todas las cifras son AP@0.5 de `best.pt`, media entre semillas; los IC 95 % son de bootstrap sobre imágenes (1 000 réplicas, percentil, pareado). Diferencias en puntos porcentuales (pp).

Las secciones 1–4 son el reporte original. Las secciones 5–7 son un **hallazgo adicional, exploratorio y posterior al pre-registro v2.0 (12/09/2026)**: se extraen de los contrastes ya calculados por `11_analisis_estadistico.py` (V2−V1, V4−V1 e interacción), no se pre-registraron como hipótesis y **no modifican el veredicto de H1–H5**.

## 1. Qué se entrenó

Las 32 corridas se entrenaron sobre **ExDark-People train**: 1 183 imágenes reales de baja iluminación con 3 271 personas anotadas por humanos (split público). Validación para seleccionar el modelo: ExDark val (634 imágenes), original en el experimento 1 y mixto (original + copia ocluida) en la iteración 2. El test de ExDark (841 imágenes, 2 235 personas) no participó en ningún entrenamiento ni selección.

Lo único sintético es el **aumento de oclusión** aplicado durante el entrenamiento:

| Bloque | Corridas | Variantes con aumento | Aumento (sintético) | Sin aumento |
|---|---|---|---|---|
| Experimento 1 (protocolo v1.1b) | 14 (YOLOv11s) | V3, V4 | v1: parche rectangular interior (textura / recorte / opaco), f ~ U[0,30; 0,85] | V1, V2 (CBAM), C_AUMENTO, C_PESOS |
| Iteración 2 (protocolo v2.0) | 12 (YOLOv11s) | V3′, V4′ | v2: silueta con máscara (persona u objeto), personas pegadas etiquetadas | V1′, V2′ (CBAM) |
| Generalidad (protocolo v2.0) | 6 (YOLO26s) | V3′ | v2: siluetas | V1′ |

## 2. Fuentes reales de oclusión usadas en la evaluación

| Fuente | Dominio | Imágenes evaluadas | Cómo se determina la oclusión | Instancias ocluidas |
|---|---|---|---|---|
| ExDark test, oclusión inter-persona (proxy) | Nocturno (el del estudio) | 841 | Fracción de cada caja de persona cubierta por otras cajas de persona anotadas por humanos en ExDark, con orden de profundidad por base de la caja (`16_oclusion_proxy.py`, variante *orden*). Solo capta oclusión por personas. | ligera 188 · moderada 190 · severa 101 (sin oclusión 1 756) |
| NightOwls val (muestra) | Nocturno, cámara en vehículo | 2 000 | Atributo binario *occluded* anotado por humanos en el dataset original | ocluida 530 (sin oclusión 2 763; ignore 759) |
| CityPersons val | Diurno | 500 | Oclusión = 1 − área(bboxVis)/área(bbox), con la caja visible anotada por humanos (`anno_val.mat` oficial). Estratos propios y convención bare/partial/heavy (h ≥ 50 px) | moderada 926 · severa 397 · *heavy* 733 (sin oclusión 926) |

## 3. Resultados sobre oclusión real: aumento de oclusión (V3 − V1)

### 3.1 Experimento 1 — YOLOv11s, aumento de parches (3 semillas por variante)

| Fuente / estrato (n) | V1 | V3 | Δ V3 − V1 | IC 95 % |
|---|---|---|---|---|
| ExDark inter-persona, moderada (190) | 0,483 | 0,467 | −1,62 | [−4,06; +0,76]** |
| ExDark inter-persona, severa (101) | 0,270 | 0,238 | −3,25 | [−5,81; −0,21]** |
| NightOwls ocluida (530) | 0,261 | 0,230 | −3,17 | [−4,58; −1,74] |
| CityPersons moderada (926) | 0,140 | 0,138 | −0,20 | [−0,85; +0,41] |
| CityPersons severa (397) | 0,014 | 0,012 | −0,27 | [−0,55; +0,08] |
| CityPersons *heavy* (733) | 0,138 | 0,135 | −0,36 | [−1,06; +0,31] |
| *Referencia sintética:* textura severa (2 153) | 0,035 | 0,469 | +43,46 | [+41,23; +46,10] |
| *Referencia sintética:* opaco severa (2 131) | 0,012 | 0,622 | +60,92 | [+58,50; +63,41] |

\*\* IC añadido el 19/09/2026 al recalcular el bootstrap del experimento 1 con `test_proxy` incluido (`11_analisis_estadistico.py`, misma semilla y 1 000 réplicas; los demás contrastes no cambiaron). Hasta esa fecha el proxy, definido el 13/09, solo tenía medias en este bloque.

### 3.2 Iteración 2 — aumento de siluetas

Medias por arquitectura (3 semillas cada una):

| Fuente / estrato (n) | YOLOv11s V1′ | YOLOv11s V3′ | YOLO26s V1′ | YOLO26s V3′ |
|---|---|---|---|---|
| ExDark inter-persona, moderada (190) | 0,464 | 0,424 | 0,482 | 0,472 |
| ExDark inter-persona, severa (101) | 0,244 | 0,194 | 0,271 | 0,235 |
| NightOwls ocluida (530) | 0,306 | 0,138 | 0,312 | 0,169 |
| NightOwls sin oclusión (2 763) | 0,759 | 0,575 | 0,761 | 0,633 |
| CityPersons moderada (926) | 0,157 | 0,112 | 0,162 | 0,111 |
| CityPersons severa (397) | 0,015 | 0,007 | 0,016 | 0,007 |
| CityPersons *heavy* (733) | 0,153 | 0,113 | 0,156 | 0,112 |
| *Referencia sintética:* silueta severa (1 858) | 0,041 | 0,148 | 0,035 | 0,155 |

IC 95 % del contraste V3′ − V1′, **solo YOLOv11s** (3 semillas por variante):

| Fuente / estrato (n) | Δ V3′ − V1′ | IC 95 % | Excluye 0 |
|---|---|---|---|
| ExDark inter-persona, moderada (190) | −3,96 | [−9,06; +1,19] | no |
| ExDark inter-persona, severa (101) | −5,02 | [−10,72; +0,50] | no |
| NightOwls ocluida (530) | −16,79 | [−19,59; −13,96] | sí |
| CityPersons moderada (926) | −4,54 | [−6,23; −3,19] | sí |
| CityPersons severa (397) | −0,80 | [−1,03; +0,07] | no |
| CityPersons *heavy* (733) | −3,94 | [−5,66; −2,41] | sí |

Nota: el fichero `resultados_v2/analisis/bootstrap.csv` generado el 13/09 agrupaba en V1′/V3′ las 6 semillas de YOLOv11s + YOLO26s (allí, p. ej., ExDark severa −4,41 [−8,89; −0,07] y NightOwls ocluida −15,55 [−18,21; −12,83]). Las tablas de este reporte usan el recálculo con solo YOLOv11s para que V2′/V4′ (que solo existen en YOLOv11s) se comparen con baselines de la misma arquitectura.

## 4. Comparación con YOLOv11s COCO sin ajustar

`preliminar_coco_person`: pesos COCO oficiales de YOLOv11s, clase *person*, sin ningún entrenamiento sobre ExDark, evaluado con el mismo script y los mismos conjuntos.

| Fuente / estrato | COCO sin ajustar | Mejor variante ajustada sobre ExDark | Variante |
|---|---|---|---|
| NightOwls ocluida (530) | **0,387** | 0,312 | YOLO26s V1′ |
| NightOwls sin oclusión (2 763) | 0,764 | 0,761 | YOLO26s V1′ |
| ExDark test, global (2 235) | 0,771 | 0,819 | YOLOv11s V1 (exp. 1) |

Evaluación secundaria con `last.pt` (experimento 1, media de 3 semillas): NightOwls ocluida V1 0,157, V3 0,131, V4 0,107. Todas las variantes ajustadas sobre ExDark quedan por debajo del modelo COCO sin ajustar en NightOwls ocluida (0,387), mientras que lo superan en el test de ExDark (0,771 → 0,819).

---

## 5. Hallazgo adicional (post hoc, 19/09/2026): efecto puro del CBAM, V2 − V1

Contraste V2 − V1 (CBAM sin aumento de oclusión frente al baseline), en las fuentes reales.

| Fuente / estrato (n) | Exp. 1 (v1.1b) Δ | IC 95 % | Iter. 2 (v2.0, YOLOv11s) Δ | IC 95 % |
|---|---|---|---|---|
| ExDark inter-persona, sin (1 756) | −1,14 | [−1,77; −0,51] | +0,24 | [−0,44; +0,91] |
| ExDark inter-persona, ligera (188) | −1,44 | [−3,86; +1,16] | +0,66 | [−2,39; +3,27] |
| ExDark inter-persona, moderada (190) | −0,81 | [−3,48; +1,99] | +0,31 | [−3,00; +3,71] |
| ExDark inter-persona, severa (101) | +1,18 | [−1,99; +4,55] | +0,72 | [−2,85; +4,37] |
| NightOwls sin oclusión (2 763) | −3,21 | [−3,70; −2,61] | −1,59 | [−2,11; −1,05] |
| NightOwls ocluida (530) | −3,62 | [−4,96; −2,27] | −5,35 | [−6,90; −3,87] |
| CityPersons moderada (926) | −1,91 | [−2,77; −0,98] | −3,66 | [−4,76; −2,71] |
| CityPersons severa (397) | −0,26 | [−0,68; −0,01] | −0,20 | [−0,64; −0,04] |
| CityPersons *heavy* (733) | −1,92 | [−2,95; −0,86] | −3,62 | [−4,83; −2,63] |

IC del experimento 1 sobre el proxy añadidos el 19/09/2026 (recálculo del bootstrap con `test_proxy`).

Lectura estrictamente descriptiva: el efecto del CBAM es **negativo con IC que excluye el cero en NightOwls y en CityPersons** (las dos fuentes de otro dominio), en los dos bloques y en todos los estratos; y **nulo en el proxy propio de ExDark** (todos los IC de la iteración 2 incluyen el cero; en el experimento 1 solo el estrato *sin* excluye el cero, −1,14 [−1,77; −0,51]; en el experimento 1 las diferencias de medias son de ±1,5 pp con signo mixto). No hay ningún estrato real en el que V2 supere a V1 con IC que excluya el cero.

## 6. Hallazgo adicional (post hoc): interacción (V4 − V3) − (V2 − V1)

Contraste lineal pre-especificado en la Sección 2.6 del PPI (ahí como parte del análisis de H1/H2 sobre estratos sintéticos y reales); aquí se reporta sobre las fuentes reales.

| Fuente / estrato (n) | Exp. 1 (v1.1b) Δ | IC 95 % | Excl. 0 | Iter. 2 (v2.0, YOLOv11s) Δ | IC 95 % | Excl. 0 |
|---|---|---|---|---|---|---|
| ExDark inter-persona, sin (1 756) | −0,01 | [−0,73; +0,70] | no | +0,22 | [−0,79; +1,11] | no |
| ExDark inter-persona, ligera (188) | −0,88 | [−3,66; +1,78] | no | −2,48 | [−6,17; +1,68] | no |
| ExDark inter-persona, moderada (190) | +0,06 | [−3,03; +3,26] | no | −1,12 | [−5,54; +3,54] | no |
| ExDark inter-persona, severa (101) | −1,21 | [−5,10; +2,45] | no | −2,53 | [−7,08; +1,73] | no |
| NightOwls sin oclusión (2 763) | +0,33 | [−0,34; +0,97] | no | −1,73 | [−2,60; −0,72] | sí |
| NightOwls ocluida (530) | +0,98 | [−0,47; +2,45] | no | **+4,51** | [+2,64; +6,47] | sí |
| CityPersons moderada (926) | +0,27 | [−0,56; +0,93] | no | +1,64 | [+0,64; +3,22] | sí |
| CityPersons severa (397) | +0,15 | [−0,15; +0,51] | no | +0,06 | [−0,37; +0,60] | no |
| CityPersons *heavy* (733) | +0,40 | [−0,51; +1,15] | no | +1,36 | [+0,15; +3,05] | sí |
| CityPersons *partial* (810) | −0,37 | [−1,46; +0,86] | no | +3,97 | [+1,89; +5,96] | sí |

Sobre el signo, lo que muestran los datos (y que corrige la formulación solicitada para este apartado):

- **Experimento 1:** ninguna interacción real excluye el cero; los estimadores puntuales son pequeños (de −1,21 en el proxy severa a +0,98 en NightOwls ocluida).
- **Iteración 2:** la interacción es **positiva con IC que excluye el cero en CityPersons** (moderada, *heavy*, *partial*, *bare*, *sin*; no en severa) **y también en NightOwls ocluida (+4,51 [+2,64; +6,47])**. Es **negativa** en NightOwls sin oclusión (−1,73, excluye el cero) y en los estratos ocluidos del proxy de ExDark (−1,1 a −2,5), donde **no** excluye el cero.
- Es decir, el cambio de signo no separa "CityPersons frente a NightOwls/proxy": separa **oclusión real de otros dominios (CityPersons y NightOwls ocluida: positivo)** frente a **ExDark en dominio y NightOwls sin oclusión (negativo o nulo)**. En ninguno de los casos con interacción positiva V4 supera a V1: la interacción positiva significa que la caída de V4 respecto a V3 es menor que la caída de V2 respecto a V1 (V4 − V1 sigue siendo negativo con IC que excluye el cero en todas esas filas: −6,56 a −17,63 pp).

## 7. Hallazgo adicional (post hoc): interacción por tipo de oclusor de prueba × estrato

El entrenamiento no tiene estratos (cobertura continua f ~ U[0,30; 0,85]); la dimensión "de entrenamiento" es la **familia de oclusor** con que se entrenó cada bloque (parches v1 / siluetas v2). Filas: tipo de oclusor del conjunto de prueba; columnas: estrato efectivo del conjunto de prueba. Solo celdas con n ≥ 50. Formato: Δ [IC 95 %]; negrita cuando el IC excluye el cero.

**Experimento 1 (entrenado con parches v1):**

| Tipo de oclusor de prueba | ligera | moderada | severa |
|---|---|---|---|
| opaco | +0,82 [−0,14; +1,72] (n 1 968) | **−1,74 [−2,98; −0,74]** (n 2 031) / **−3,37 [−6,41; −0,87]** (n 236 en `opaco_ligera`) | **−6,82 [−7,78; −5,86]** (n 2 131) / **−5,01 [−8,22; −1,96]** (n 177 en `opaco_moderada`) |
| textura | **+0,92 [+0,08; +1,78]** (n 1 960) | +0,06 [−1,27; +1,18] (n 2 008) | **−2,98 [−4,01; −1,93]** (n 2 153) |
| recorte | +0,06 [−0,73; +0,87] (n 1 945) | **−1,55 [−2,58; −0,38]** (n 2 009) | **−3,22 [−4,27; −2,21]** (n 2 149) |
| silueta | — (conjuntos no existían) | — | — |

**Iteración 2 (entrenado con siluetas v2; solo YOLOv11s):**

| Tipo de oclusor de prueba | ligera | moderada | severa |
|---|---|---|---|
| opaco | −0,57 [−1,68; +0,53] (n 1 968) | **−4,50 [−5,81; −3,21]** (n 2 031) | **−2,33 [−3,14; −1,76]** (n 2 131) / **−0,92 [−1,91; −0,20]** (n 177 en `opaco_moderada`) |
| textura | +0,53 [−0,61; +1,78] (n 1 960) | −1,07 [−2,67; +0,09] (n 2 008) | +0,63 [−0,20; +1,32] (n 2 153) |
| recorte | −0,42 [−1,50; +0,76] (n 1 945) | **−2,03 [−3,19; −0,51]** (n 2 009) | +0,17 [−0,82; +1,21] (n 2 149) |
| silueta | +0,39 [−0,84; +1,55] (n 1 747) | −1,14 [−2,59; +0,14] (n 1 607) | +0,07 [−0,55; +0,73] (n 1 858) |

Lectura descriptiva de la pregunta planteada (¿se concentra la interacción negativa en los oclusores opacos?): **sí, en los dos bloques**. En el experimento 1 la interacción negativa más grande es opaco severa (−6,82) y crece con la severidad para los tres tipos de parche; en la iteración 2 las únicas celdas negativas con IC que excluye el cero son opaco (moderada −4,50; severa −2,33) y recorte moderada (−2,03), mientras que textura y silueta no excluyen el cero en ningún estrato. Con siluetas en entrenamiento, el conjunto de prueba de siluetas —la familia más parecida a la de entrenamiento— es precisamente donde la interacción es nula.

Estas tres secciones se registran como análisis exploratorio posterior en `CAMBIOS_PROTOCOLO.md`; no alteran H1–H5 ni sus veredictos.

---

## Adenda (26/09/2026): análisis de sensibilidad con bootstrap jerárquico

Al remuestrear también las semillas (`23_bootstrap_jerarquico.py`; `informes/analisis_final/BOOTSTRAP_JERARQUICO.md`), los intervalos se ensanchan de media ×1,66. Cambia el estado de estas afirmaciones de este reporte:

- **Experimento 1, aumento de parches (V3 − V1):** NightOwls ocluida −3,17 pp pasa a [−7,94; +2,10] y ExDark severa −3,25 pp a [−7,11; +0,89]; ambos dejan de excluir el cero. Con parches solo se sostiene que el aumento **no mejora** la oclusión real, no que la empeore.
- **Sección 5 (CBAM puro, V2 − V1):** en el experimento 1, NightOwls (−3,62) y CityPersons *heavy* (−1,92) dejan de excluir el cero; en la iteración 2 siguen excluyéndolo (−5,35 [−7,86; −2,72] y −3,62 [−7,13; −0,57]). El CBAM no mejora la oclusión real en ninguna celda; que la empeore solo es robusto en la iteración 2.
- **Se mantiene:** el daño del aumento de siluetas (iteración 2 y YOLO26s) en NightOwls y CityPersons sigue excluyendo el cero, y ningún veredicto de H1–H5 cambia.
