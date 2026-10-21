# ARGOS-11 — Pre-registro de H10 (E8: la geometría de la oclusión real)

Pre-registrado el **2026-10-06**. Se escribe **después** de cerrar H1–H9b, el análisis final y las revisiones del short paper. Se escribe **antes** de entrenar ninguna corrida de H10 y de evaluar nada con este diseño. Complementa a `PREREGISTRO_H9b.md`: lo que no se menciona no cambia, en particular:
- YOLOv11s, `config/hiperparametros.yaml` y `config/aumento_base.yaml`;
- ExDark-People train y `data_v2.yaml`;
- evaluación estratificada con regiones *ignore*;
- bootstrap por imágenes con 1 000 réplicas como criterio;
- umbral de +2 pp.

Se congelará como **v3.5** antes de la primera época. H10 no reformula ninguna hipótesis anterior.

## 0. Lo que se hizo antes de este documento (declarado)

1. **Código.** `argos_lib/geometria.py` y `28_geometria.py` (autotest 12/12).
2. **Patrones.** Se extrajeron de `anno_train.mat` de CityPersons:
   - 4 186 patrones de las imágenes de `dataset_cp/train.txt`, para entrenamiento;
   - 131 de `dataset_cp/val_interno.txt`, para el control.

   No se usó ninguna imagen ni anotación de CityPersons val, que es fuente de prueba.
3. **Calibración solo con imágenes de entrenamiento de ExDark**, sin entrenar ni evaluar ningún modelo:
   - **Demostración visual** (12 imágenes): con la búsqueda inicial, algunos oclusores tapaban la caja entera. Se añadieron dos límites: el recorte no puede tapar más del 35 % de la parte que el patrón deja visible, y su tamaño no puede superar 1,5 veces el alto ni 2,5 veces el ancho de la caja.
   - **Medición sobre 600 imágenes de train.** La cobertura efectiva media era 0,40 con patrones de cobertura 0,30–0,85, frente a 0,55 de las siluetas v2. Para que la comparación con v2 dependa sobre todo de la geometría, el muestreo de entrenamiento usa patrones de cobertura 0,40–0,95. Con eso la cobertura efectiva media es **0,50** (v2: 0,55), y el IoU medio entre recorte y región oculta, 0,56. La diferencia que queda (0,05) se declara.
4. **Control sintético** `geometria_severa`, generado: ExDark test, banco `siluetas_test`, patrones de control y semilla 2024. Tiene **679** personas en oclusión severa efectiva y un IoU medio de 0,61.
5. **Prueba de humo** (1 época, 5 %, `runs/smoke_geo`): el aumento queda en la cadena de entrenamiento y las personas pegadas se etiquetan.

## 1. Motivación

Las tres familias probadas cambian la **apariencia** del oclusor (rectángulo, silueta real, objeto pintado por difusión), pero no su **geometría**. En las siluetas v2, el oclusor entra por un lado de la caja elegido al azar (abajo, izquierda, derecha o arriba; 25 % cada uno) y cubre f ~ U[0,30; 0,85].

La oclusión real es distinta (`informes/h10_geometria_estadisticas.md`). En CityPersons train, contando un lado cuando la región oculta ocupa al menos el 10 % de la caja:
- el **67 %** de las oclusiones tapa una esquina o varios lados;
- el 14,5 % solo la parte de abajo y el 18 % solo un lado;
- casi ninguna tapa solo la parte de arriba (0,4 %).

Las dos revisiones del short paper (06/10/2026) señalan que el resultado negativo no tiene una causa probada, y que la geometría es la explicación candidata que el propio artículo propone. H10 la contrasta: misma apariencia que v2 y geometría tomada de oclusiones reales.

## 2. Hipótesis (literal; no se reformula después)

- **H10 (primaria).** El déficit de transferencia persiste cuando el oclusor sigue la geometría de la oclusión real. Las condiciones son:
  - YOLOv11s, ExDark-People train;
  - los mismos recortes de v2, colocados para tapar la región oculta de un patrón real de CityPersons train;
  - **30 épocas fijas** sin parada temprana, evaluadas con los pesos de la última época, como en H9b.

  Bajo esas condiciones, el contraste **V3ᴳ − V1** (AP@0.5, media de 3 semillas) no alcanza +2 pp con IC 95 % por imágenes que excluya el cero en al menos 2 de las 3 fuentes reales (NightOwls ocluida, CityPersons *heavy*, proxy severa de ExDark). Esto vale aun cuando el control `geometria_severa` sea ≥ +2 pp con IC que excluya el cero.
  - *Refutaría H10:* V3ᴳ − V1 ≥ +2 pp con IC por imágenes que excluya el cero en **al menos 2 de las 3** fuentes reales (el mismo criterio de H4, H8, H9 y H9b).
  - *No concluyente:* el control `geometria_severa` no alcanza +2 pp con IC que excluya el cero.
- **Contraste secundario pre-registrado (efecto de la geometría):** **V3ᴳ − V3ˢ**, donde V3ˢ son las siluetas v2 con su geometría habitual y la misma exposición (30 épocas). Se dirá que «la geometría mejora la transferencia» si V3ᴳ − V3ˢ ≥ +2 pp con IC por imágenes > 0 en al menos 2 de las 3 fuentes reales. No cambia el veredicto de H10.
- **Compromiso de reporte:** si H10 se refuta, el artículo y el short paper dirán que una parte del déficit se explica por la geometría del oclusor y que la apariencia no basta.
- **Análisis de sensibilidad declarados ahora:**
  - IC jerárquico (semillas + imágenes, 2 000 réplicas);
  - número de fuentes cuyo IC tiene límite superior < +2 pp;
  - V3ˢ − V1, que es la réplica de las siluetas con exposición fija.
- **Descriptivo:** `silueta_severa` como segundo control; AP@0.5:0.95 y curva por visibilidad en CityPersons (`27_`).
- **Declarado:** CityPersons comparte la distribución de la geometría con los patrones de entrenamiento, que vienen de CityPersons train (otras imágenes, mismas ciudades y mismo anotador). NightOwls y ExDark no. Una mejora solo en CityPersons se leerá con esa cautela.

## 3. Diseño

| Elemento | Definición |
|---|---|
| Línea base | **V1 de H9b** (`runs/argos_gen_fijo/V1_s{0,1,2}`), reutilizada: mismo modelo, datos, validación, hiperparámetros, semillas y 30 épocas fijas. Sus detecciones guardadas se reutilizan; solo se infiere sobre `geometria_severa` |
| V3ᴳ (H10) | `07_ --protocolo geo --variantes V3 --epochs 30 --patience 0 --proyecto argos_geo`. `OclusionGeometria`: p = 0,5 por imagen, 1–3 personas, prob. persona 0,5, banco `siluetas_train`, patrones de `dataset/geometria/patrones_train.json` con cobertura 0,40–0,95 |
| V3ˢ (comparación) | `07_ --protocolo v2 --variantes V3 --epochs 30 --patience 0 --proyecto argos_sil_fijo`: siluetas v2 sin ningún cambio, con la misma exposición |
| Semillas y orden | {0, 1, 2}; orden V3ᴳ_s0, V3ˢ_s0, V3ᴳ_s1, V3ˢ_s1, V3ᴳ_s2, V3ˢ_s2: **6 corridas**, ~3,5 h de GPU |
| Colocación | Para cada persona: un patrón real (caja visible relativa a la completa) y un recorte. Búsqueda por rejilla (10 escalas × 25 desplazamientos, sobre la caja reducida a 48 px) de la colocación que tapa la mayor parte de la región oculta, con desempate por IoU. Restricciones: no tapar más del 35 % de la parte visible del patrón; alto ≤ 1,5 y ancho ≤ 2,5 veces la caja. El recorte entra desde fuera por los lados que toca la región oculta y conserva su silueta natural. Mismo ajuste de luminancia y misma composición alpha que v2 |
| Control | `geometria_severa` (679 personas severas efectivas); `silueta_severa`, descriptivo |
| Evaluación | `09_ --pesos <last.pt> --nombre {V1,V3G,V3S}_sN --variante {V1,V3G,V3S} --resultados resultados_h10`, con `geometria_severa`, `silueta_severa`, NightOwls, CityPersons convención y ExDark proxy |
| Contrastes y veredicto | `28_geometria.py analisis`: V3G − V1, V3S − V1 y V3G − V3S; bootstrap por imágenes de 1 000 réplicas (semilla 0) y jerárquico de 2 000. Regla literal → `informes/veredicto_h10.md` |

## 4. Lo que NO se hará

- No se cambiarán patrones, límites, rango de cobertura, banco, épocas ni hiperparámetros después de ver ninguna corrida.
- No se usará `best.pt` para el criterio.
- No se añadirán semillas ni se cambiarán la métrica o las fuentes del criterio.

## 5. Orden de ejecución

1. Congelamiento **v3.5**: este documento, `argos_lib/geometria.py`, `28_`, `27_`, los patrones y `gt_geometria_severa.json`.
2. Las 6 corridas en el orden de la sección 3.
3. Evaluación, contrastes, veredicto e informe `informes/reporte_h10_geometria.md`.
