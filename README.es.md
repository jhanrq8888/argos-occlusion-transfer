# argos-occlusion-transfer

**Mejorar sobre oclusión sintética no basta: aumento de oclusión y oclusión real en la detección de personas.** Paquete de replicación de ARGOS-11: experimentos controlados con hipótesis preespecificadas (Universidad Peruana Unión, Juliaca, Perú). [English version](README.md).

El aumento sintético de oclusión (pegar parches, siluetas u objetos generados sobre las personas al entrenar) es un remedio habitual para detectar personas ocluidas, y su beneficio suele medirse con la misma oclusión artificial. Este repositorio comprueba si ese beneficio llega a la **oclusión real anotada por humanos**. En cada bloque, un modelo base (V1) y uno aumentado (V3) comparten datos, hiperparámetros, aumento base y máquina (salvo H16, cuyas V1 son las de H15, de otra máquina). Todos los bloques menos uno tienen un control sintético y tres fuentes de oclusión real (peatones ocluidos de NightOwls, CityPersons *heavy* y un indicador de oclusión sobre ExDark). Su hipótesis, su regla de decisión y su código se fijaron con una huella SHA-256 antes de entrenar.

## Resultados principales

| | Resultado |
|---|---|
| Controles sintéticos que pasan (+2 pp de AP@0.5 con IC del 95 % > 0) | **17 de 17** (+2,6 a +60,9 pp) |
| Recuento primario: exposición igual al entrenamiento, 11 bloques, 33 celdas reales | **pasan 5** (4 con el IC jerárquico), 15 descartan +2 pp y 13 no son concluyentes |
| Ganancia real media con exposición igual (IC *bootstrap* de bloques) | CityPersons **+0,96** [+0,34; +1,56], NightOwls +0,01 [−0,92; +0,97], ExDark −0,94 [−2,55; +0,94] |
| Los 17 bloques con control | pasan 6 de 51 celdas reales y 29 descartan +2 pp; sin el indicador de ExDark, 4 de 34 |
| Especificidad (ganancia en las personas ocluidas menos en las no ocluidas; análisis posterior) | de las 6 celdas que pasan, solo las dos del indicador de ExDark son propias de la oclusión, y ninguna con el IC jerárquico |
| CityPersons *heavy* puntuado con la caja visible (análisis posterior) | la ganancia baja en casi todos los bloques y no supera +1,3 pp en ninguno |
| Faster R-CNN con siluetas (H15) | cumple la regla prerregistrada en NightOwls (+3,28) y CityPersons (+2,33), pero con la varianza entre semillas sus IC incluyen el cero, no es propia de la oclusión y con la caja visible CityPersons baja a +0,74 |
| Faster R-CNN con difusión / profundidad (H16a / H16b); RetinaNet con siluetas (H17) | **0 de 3** cada uno, aunque los controles suben +20,35, +9,63 y +6,60 |
| Siluetas pegadas en imágenes de CityPersons, modelos entrenados en ExDark (análisis posterior) | pasan 9 de 15 bloques (mediana +2,4) frente a una mediana de +0,25 en la oclusión real de esas imágenes |
| Control con cobertura 0,35–0,70, como CityPersons *heavy* (análisis posterior) | pasan 15 de 15 (+2,1 a +33,6), sin asociación con la ganancia real |

El aumento siempre se aprende y pasa de una oclusión sintética a otra, pero pasar un control sintético no basta para afirmar robustez a la oclusión real. El único bloque que cumple la regla no resiste la varianza entre semillas, la especificidad ni la caja visible, y el déficit no se debe solo al cambio de dominio. El trabajo completo está en `shortpaper5/` (short paper y suplemento, en español e inglés); los análisis pedidos por el panel de revisión del 22/10 están en `informes/revision_panel_analisis.py` e `informes/controles_extra.py`.

## Qué hay en el repositorio

| Ruta | Contenido |
|---|---|
| `argos_lib/` | Biblioteca: AP con regiones *ignore*, formato de anotaciones, generadores de oclusión (parches, siluetas, difusión, geometría real y orden de profundidad) y enganches para Ultralytics |
| `00_*.py` … `37_*.py` | Scripts de la tubería en orden de ejecución. Cada uno documenta su uso en su encabezado y la mayoría tiene `--selftest` |
| `config/` | Hiperparámetros y aumento base (idénticos en V1 y V3) |
| `PROTOCOLO*.md`, `PREREGISTRO_*.md` | Hipótesis H1–H17, reglas de decisión y diseño, escritos antes de cada bloque |
| `CAMBIOS_PROTOCOLO.md`, `protocolo_congelado.json` | Registro de cada congelamiento (fecha, SHA-256 global y motivo) y huellas por archivo del congelamiento vigente |
| `runs/<bloque>/<corrida>/` | `results.csv`, `args.yaml` y `registro_argos.json` de cada una de las 117 corridas válidas (los pesos no se versionan) |
| `resultados*/` | Evaluación por corrida (`eval/`), resúmenes de AP y análisis *bootstrap* de cada bloque |
| `informes/` | Veredictos (`veredicto_*.md`), informes (`reporte_*.md`), tablas consolidadas (`analisis_final/`) y los scripts que las generan, incluidos los análisis posteriores de la revisión del 22/10 (`revision_panel_analisis.py`, `controles_extra.py`) |
| `dataset/splits`, `dataset_cp/`, `dataset_no/` | Identificadores de las imágenes de cada partición y muestra (sin imágenes) |
| `anotacion_anotador_*.csv`, `consenso.csv` | Gradación manual de la oclusión usada en el estudio de fiabilidad (anotadores seudonimizados) |
| `shortpaper5/` | Short paper y suplemento (LaTeX, PDF y los scripts que generan cada tabla y figura) |
| `runpod/` | Scripts con que se entrenaron H11, H12 y H14–H17 en una RTX 4090 alquilada, y las huellas SHA-256 de los pesos descargados |
| `*.bat` | Lanzadores de Windows usados en la evaluación |

## Cómo reproducir

1. **Entorno.** Python 3.13 y CUDA 12.8. Instala PyTorch desde el índice de CUDA (ver `requirements.txt`) y luego `pip install -r requirements.txt`. Ultralytics está fijado en la versión 8.4.143.
2. **Datos** (no se redistribuyen; hay que obtener cada conjunto bajo su propia licencia):
   - ExDark: <https://github.com/cs-chan/Exclusively-Dark-Image-Dataset>; luego `python 01_preparar_exdark_people.py --raiz <ExDark> --salida ./dataset`. Los identificadores de la partición están en `dataset/splits/`.
   - CityPersons (imágenes de Cityscapes, con registro): <https://www.cityscapes-dataset.com>; luego `13_descargar_externos.py citypersons` y `12_fuentes_externas.py citypersons-mat`.
   - NightOwls: <https://www.nightowls-dataset.org>; luego `13_descargar_externos.py nightowls` y `12_fuentes_externas.py nightowls`.
   - Conjuntos derivados: `05_oclusion_sintetica.py` (bancos de recortes y controles sintéticos), `16_oclusion_proxy.py exdark` (indicador de ExDark), `20_replica_citypersons.py` y `21_escalera_nightowls.py` (entrenamiento en CityPersons y NightOwls), `25_oclusion_generativa.py` (oclusores por difusión), `28_geometria.py` (patrones de oclusión real) y `32_profundidad.py` (oclusores con orden de profundidad).
3. **Entrenamiento.** `07_entrenar.py` con el protocolo de cada bloque, por ejemplo:
   - H4: `python 07_entrenar.py --protocolo v2 --variantes V1 V2 V3 V4 --semillas 0 1 2`
   - H9b: `python 07_entrenar.py --protocolo gen --variantes V1 V3 --semillas 0 1 2 --epochs 30 --patience 0 --proyecto argos_gen_fijo`
   - H14: `python 07_entrenar.py --protocolo prof --variantes V1 V3 --semillas 0 1 2 --epochs 30 --patience 0 --proyecto argos_prof`
   - H15 (Faster R-CNN): `python 35_dos_etapas.py entrenar --variante V1 --semilla 0` (y V3, semillas 0–2)
   - H16 y H17: el mismo script con `--familia gen|prof` (Faster R-CNN) o `--detector retina`

   El comando exacto de cada bloque está en su `PREREGISTRO_*.md`, en su lanzador (`*.bat`, `runpod/*/pod_correr.sh`) y en `runs/*/*/args.yaml`.
4. **Evaluación.** `09_evaluar_estratificado.py --pesos <pesos> --nombre <corrida> --gt <anotaciones>` (en H15–H17, primero `35_dos_etapas.py inferir` y luego `09_`).
5. **Veredictos y análisis.**
   - Veredictos: `19_veredictos.py` (H1–H8), `26_veredicto_h9b.py`, `28_geometria.py analisis` (H10), `29_h11_dominio.py`, `30_h12.py`, `31_realismo.py` (H13), `34_h14.py`, `36_h15.py` y `37_h16_h17.py`.
   - Sensibilidad: `23_bootstrap_jerarquico.py`, `24_miss_rate.py` y `27_ap_estricto_visibilidad.py`.
   - Análisis de la revisión: `informes/revision_sp_analisis.py`, `informes/matriz_cruzada.py`, `informes/kid_oclusor.py` e `informes/registro_corridas.py`.
6. **Tablas y figuras del artículo.** `shortpaper5/suplemento_tablas.py`, `shortpaper5/fig_dispersion.py` y `shortpaper5/fig_gap.py`.

**Comprobar el congelamiento.** `python 08_congelar_protocolo.py --verificar` compara los archivos actuales con `protocolo_congelado.json`. Los archivos derivados de los conjuntos de datos (anotaciones y oclusores generados) no están en el repositorio y aparecerán como ausentes hasta que los reconstruyas. Las huellas prueban que los archivos congelados no cambiaron después de la fecha registrada; esas fechas las registra el propio proyecto, no un tercero.

## Notas

- **No se incluyen imágenes, pesos ni anotaciones de terceros.** ExDark, CityPersons/Cityscapes y NightOwls permiten el uso de investigación no comercial y prohíben redistribuir sus datos. Los pesos entrenados se depositarán con DOI en Zenodo al publicarse.
- Los comentarios y los informes están en español; el short paper y el suplemento están en español e inglés.
- El programa es adaptativo: H9b–H17 se diseñaron después de ver resultados anteriores, y cada una se preespecificó antes de entrenar su propio bloque.

## Licencia y cita

El código está bajo licencia MIT; los textos, las tablas y las figuras, bajo CC BY 4.0 (ver `LICENSE`). Para citar, usa `CITATION.cff`.
