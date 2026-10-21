# ARGOS-11 — Pre-registro de H6 y H7 (réplica de entrenamiento y escalera de datos)

Pre-registrado el **2026-09-19**, **después** de cerrar y analizar las 32
corridas de los protocolos v1.1b y v2.0 (informe
`informes/reporte_oclusion_real_32_corridas.md`, análisis válido de la
iteración 2 en `resultados_v2/analisis_yolo11s/`) y **antes** de
convertir un solo dato, construir un solo banco o entrenar una sola
corrida de las que aquí se describen. Complementa a `PROTOCOLO.md` y
`PROTOCOLO_v2.md`: lo que no se menciona no cambia (hiperparámetros de
`config/hiperparametros.yaml`, aumento base, generador de siluetas v2,
evaluación estratificada con regiones *ignore*, bootstrap sobre
imágenes con 1 000 réplicas, umbral de relevancia +2 pp).

No se re-congela el protocolo con este documento: el hash v2.0
(`9915d90f1a22594a`) sigue vigente para todo lo ya ejecutado. El
congelamiento v3.0 se hará cuando existan los ficheros de datos y
scripts de H6/H7 y **antes** de la primera corrida; la huella SHA-256 de
este documento queda registrada hoy en `CAMBIOS_PROTOCOLO.md` para que
pueda comprobarse que no se modificó entre el pre-registro y la
ejecución.

## 0. Errata (2026-09-19, antes de convertir datos)

La versión del 19/09 (sha256 `dbed0ac1…3a34a`) describía *heavy* como
"visibilidad ≤ 35 %" y *partial* como "35–65 %". La convención oficial de
CityPersons, que es la implementada y evaluada desde el 11/09 en
`12_fuentes_externas.py` (`CP_LIMITES`), es *heavy* = visibilidad 20–65 %,
*partial* = 65–90 %, *bare* ≥ 90 %. El estrato primario (*heavy*) y el
fichero de evaluación (`gt_citypersons_convencion.json`) no cambian; solo
se corrige el paréntesis. Registrado en `CAMBIOS_PROTOCOLO.md`.

## 1. Motivación

El déficit de transferencia (mejora grande en oclusión sintética, nula o
negativa en oclusión real) se observó en dos familias de oclusor
(parches v1, siluetas v2), dos arquitecturas (YOLOv11s, YOLO26s), tres
semillas y tres fuentes reales (proxy inter-persona sobre ExDark,
NightOwls, CityPersons). Quedan dos explicaciones alternativas que este
diseño no descarta:

- **(A) Artefacto de evaluar sin re-entrenar.** NightOwls y CityPersons se
  evaluaron con modelos ajustados sobre ExDark-People; el déficit podría
  deberse al cambio de dominio (nocturno→diurno, cámara, resolución) y no
  al aumento de oclusión en sí. H6 lo contrasta re-entrenando **sobre**
  CityPersons.
- **(B) Escasez de datos.** ExDark-People tiene 1 183 imágenes de
  entrenamiento; el ajuste fino largo sobreajusta el dominio (el modelo
  COCO sin ajustar supera a todas las variantes en NightOwls ocluida:
  0,387 frente a 0,306 de V1′). El aumento de oclusión podría ayudar solo
  cuando hay datos abundantes del dominio objetivo. H7 lo contrasta con
  una escalera de tamaño de entrenamiento sobre NightOwls.

## 2. Hipótesis (literales; no se reformulan después)

- **H6.** El déficit de transferencia de H3 se replica al **re-entrenar**
  directamente sobre CityPersons: con oclusores de silueta construidos
  desde CityPersons *train*, el contraste V3−V1 (AP@0.5, media de 3
  semillas) sobre CityPersons *val* en la convención oficial **heavy**
  (visibilidad 20–65 %, `CP_LIMITES` de `12_fuentes_externas.py`) **no alcanza +2 pp** o su IC 95 % bootstrap
  **incluye el cero**, aun cuando el mismo contraste sobre el conjunto
  sintético `cp_silueta_severa` sea ≥ +2 pp con IC que excluya el cero.
  - *Refutaría H6:* V3−V1 ≥ +2 pp en *heavy* con IC 95 % que excluya el
    cero, y en la misma dirección en *partial* (visibilidad 65–90 %).
  - *No concluyente:* la mejora sintética sobre `cp_silueta_severa` no se
    reproduce (< +2 pp): el generador no habría funcionado en este
    dominio y el contraste real no sería informativo.
- **H7.** El déficit de transferencia **persiste** cuando el
  entrenamiento dispone de datos abundantes del dominio nocturno
  objetivo: en el peldaño máximo de la escalera NightOwls (20 000
  imágenes), V3−V1 (AP@0.5, media de 3 semillas) sobre NightOwls *val*
  estrato **ocluida** no alcanza +2 pp o su IC 95 % incluye el cero.
  - *Refutaría H7:* V3−V1 ≥ +2 pp en *ocluida* con IC que excluya el cero
    en el peldaño de 20 000.
  - *Análisis secundario (descriptivo, sin criterio de decisión):*
    tendencia de V3−V1 a lo largo de los peldaños 2 000 / 5 000 /
    10 000 / 20 000 (semilla 0), para distinguir "el déficit se cierra
    con datos" de "el déficit es independiente del tamaño".

Ambas hipótesis se reportan con el veredicto que resulte. Un resultado
que refute H6 o H7 sería **más** interesante que el que las sostenga, y
no se buscará ninguna configuración adicional que cambie el signo.

## 3. H6 — Réplica de entrenamiento sobre CityPersons

| Elemento | Definición |
|---|---|
| Datos de entrenamiento | `externos/citypersons/Citypersons/images/train` (2 975 imágenes) con `anno_train.mat` oficial (Zhang et al., 2017). Se convierten a YOLO con el mismo mapeo que `12_fuentes_externas.py citypersons-mat`: clase *person* (pedestrian, rider, sitting, other); las cajas *ignore* (clase 0) y las de altura < 20 px **no se etiquetan** y sus regiones se anotan como *ignore* en el GT de evaluación (ya implementado). |
| Partición interna | 2 975 → *train* 2 675 / *val_interno* 300, muestreo por imagen estratificado por ciudad (las 18 ciudades de *train*) con semilla 0. El conjunto de evaluación (CityPersons *val*: Frankfurt, Lindau, Münster) no comparte ciudades con *train*, de modo que es disjunto por construcción. |
| Evaluación (primaria) | `dataset/externos/gt_citypersons_convencion.json` (500 imágenes de *val*, estratos bare/partial/heavy por bboxVis oficial) y `gt_citypersons.json` (estratos propios). **Sin cambios.** |
| Evaluación sintética (control del generador) | `cp_silueta_{ligera,moderada,severa}`: las mismas 500 imágenes de *val* ocluidas con el banco de siluetas **de CityPersons *val_interno*** (disjunto de *train* y de las 500), misma regla de estrato efectivo que `silueta_*`. |
| Banco de oclusores | `dataset/siluetas_cp_train/` desde imágenes de *train* (2 675) con `yolo11s-seg.pt`, conf ≥ 0,4, mismo procedimiento de `15_iteracion2.py bancos`; `dataset/siluetas_cp_val/` desde *val_interno* (300). |
| Validación mixta | Como en v2.0: *val_interno* original + copia ocluida con el banco `siluetas_cp_val`. |
| Variantes | **V1** (base) y **V3** (aumento de siluetas), semillas {0,1,2}: **6 corridas**. Sin CBAM (V2/V4): la interacción ya se midió en ExDark y no es objeto de H6. |
| Modelo base | `yolo11s.pt` (COCO). Hiperparámetros de `config/hiperparametros.yaml` sin cambios, `imgsz` 640 (se declara como limitación: los peatones pequeños de CityPersons se ven perjudicados por igual en V1 y V3). |
| Contrastes | V3−V1 en *heavy* (primario), *partial*, *bare*, global; V3−V1 en `cp_silueta_severa` (control); V1 (CP) frente a V1 (ExDark, exp. 1) en *heavy*, descriptivo. Bootstrap por imágenes, 1 000 réplicas, pareado. |
| Contrastes cruzados (secundarios) | Los mismos 6 modelos sobre NightOwls (`gt_nightowls.json`) y ExDark proxy (`gt_test_proxy.json`), solo descriptivo. |
| Costo estimado | 6 corridas × (2 675 img, 100 épocas, paciencia 20) ≈ 1,5–3 h cada una → 10–18 h GPU. |

## 4. H7 — Escalera de datos sobre NightOwls

| Elemento | Definición |
|---|---|
| Datos | `nightowls_training.json` (≈ 32 MB) y los fotogramas de *training* correspondientes, descargados por extracción parcial por rango HTTP con `13_descargar_externos.py` (misma técnica que la muestra de validación). Solo se descargan las imágenes muestreadas (≤ 20 000 + val interno). **Requiere autorización explícita del usuario antes de descargar** (≈ 8 GB). |
| Muestreo | Imágenes de *training* con ≥ 1 peatón (clase *pedestrian*), muestreo aleatorio con semilla 0, **anidado**: el peldaño de 2 000 ⊂ 5 000 ⊂ 10 000 ⊂ 20 000, para que la escalera mida solo el efecto del tamaño. Etiqueta YOLO: clase *person* = pedestrian; *bicycledriver*, *motorbikedriver* e *ignore areas* → *ignore* (no se etiquetan; se enmascaran como *ignore* en evaluación). |
| Validación interna | 1 000 imágenes de `nightowls_validation.json` con ≥ 1 peatón, muestreadas con semilla 1 **excluyendo** las 2 000 de `externos/nightowls/muestra.json` (conjunto de evaluación). Validación mixta como en v2.0 con banco `siluetas_no_val`. |
| Evaluación (primaria) | `dataset/externos/gt_nightowls.json` (2 000 imágenes, atributo *occluded* oficial; estratos *sin* / *ocluida*). **Sin cambios.** |
| Banco de oclusores | `dataset/siluetas_no_train/` desde las imágenes del peldaño de 20 000 (mismo procedimiento). |
| Presupuesto de entrenamiento | **Fijo en presentaciones de imagen: 200 000 por corrida** (≈ 100 épocas de 2 000 imágenes, del orden del exp. 1 con 1 183 × 100 ≈ 118 000). Épocas = round(200 000 / n): 2 000 → 100; 5 000 → 40; 10 000 → 20; 20 000 → 10. Paciencia = épocas/5 (mín. 2). Justificación: iguala el costo por corrida (≈ 3 h en RTX 5050) y evita confundir "más datos" con "más pasos de optimización". Se declara que 10 épocas en 20 000 es un ajuste fino corto desde COCO, no un entrenamiento desde cero. |
| Variantes y semillas | V1 y V3 con **semilla 0 en los cuatro peldaños** (8 corridas) más **semillas 1 y 2 en el peldaño de 20 000** (4 corridas): **12 corridas**. El criterio de H7 usa las 3 semillas del peldaño máximo; los peldaños inferiores son descriptivos. |
| Modelo base | `yolo11s.pt`; hiperparámetros sin cambios salvo épocas/paciencia según la tabla anterior. |
| Contrastes | V3−V1 en *ocluida* (primario) y *sin*, global; tendencia por peldaño; V1 de cada peldaño frente a COCO sin ajustar (0,387) para verificar que el re-entrenamiento en dominio supera al modelo genérico (si no lo supera en el peldaño 20 000, se reporta como fallo del ajuste y H7 pasa a *no concluyente*). |
| Contrastes cruzados (secundarios) | Modelos del peldaño 20 000 sobre CityPersons y ExDark proxy, descriptivo. |
| Costo estimado | 12 corridas × ≈ 3 h ≈ 36 h GPU, más descarga. |

## 5. Orden de ejecución y congelamiento v3.0

1. Conversión de datos y bancos de H6 (sin descarga: todo está en disco).
2. Añadir a `08_congelar_protocolo.py` los patrones de H6/H7 (este
   documento, `dataset/data_citypersons.yaml`, `dataset/data_nightowls_*.yaml`,
   índices de bancos, listas de muestreo) y **congelar v3.0** antes de la
   primera corrida de H6.
3. Ejecutar H6 (6 corridas), evaluar y analizar con `09_`, `11_`, `14_`
   sobre `resultados_h6/`.
4. Con autorización de descarga: datos de H7, bancos, re-congelar si los
   patrones nuevos lo exigen (v3.1, solo ficheros de datos H7), ejecutar
   los 12 entrenamientos en orden de peldaño creciente, analizar sobre
   `resultados_h7/`.
5. Informe: `informes/reporte_h6_h7.md`, con veredictos literales de la
   Sección 2 y sección de desviaciones.

## 6. Lo que NO se hará

- No se ajustarán hiperparámetros, probabilidad ni cobertura del oclusor
  por dominio. Si el generador v2 no produce mejora sintética en un
  dominio, se reporta como "no concluyente", no se retoca.
- No se añadirán semillas ni peldaños tras ver resultados.
- No se cambiará el estrato primario (*heavy* en H6, *ocluida* en H7) ni
  la métrica (AP@0.5) después del pre-registro.
