# argos-occlusion-transfer

**Las ganancias sobre oclusión sintética no anticipan la robustez a la oclusión real en la detección de personas.** Paquete de replicación de ARGOS-11: experimentos controlados con hipótesis preespecificadas (Universidad Peruana Unión, Juliaca, Perú). [English version](README.md).

El aumento sintético de oclusión (pegar parches, siluetas u objetos generados sobre las personas al entrenar) es un remedio habitual para detectar personas ocluidas, y su beneficio suele medirse con la misma oclusión artificial. Este repositorio comprueba si ese beneficio llega a la **oclusión real anotada por humanos**. En cada bloque, un modelo base (V1) y uno aumentado (V3) comparten datos, hiperparámetros, aumento base y máquina. Cada bloque tiene un control sintético y tres fuentes de oclusión real (peatones ocluidos de NightOwls, CityPersons *heavy* y un indicador de oclusión sobre ExDark). Su hipótesis, su regla de decisión y su código se fijaron con una huella SHA-256 antes de entrenar.

## Resultados principales

| | Resultado |
|---|---|
| Controles sintéticos que pasan (+2 pp de AP@0.5 con IC del 95 % > 0), detectores de una etapa y *transformers* | **13 de 13** (+2,6 a +60,9 pp) |
| Celdas de oclusión real que pasan, mismos detectores | **4 de 39**, ninguna a la vez estable entre semillas y propia de las personas ocluidas (con los cuatro bloques de torchvision: 6 de 51) |
| Celdas reales que descartan una ganancia de +2 pp (unilateral) | 24 de 39 (29 de 51) |
| Efecto real medio con exposición igual al entrenamiento (21 celdas; 33 con torchvision) | **+0,02 pp** (+0,01) |
| Transferencia entre oclusiones sintéticas (matriz cruzada de controles) | pasan 13 de 20 celdas |
| Asociación entre la ganancia sintética y la real (Spearman, 13 bloques) | NO +0,41 [−0,18; +0,85], CP +0,30 [−0,26; +0,71], EX −0,15 [−0,67; +0,54] |
| Faster R-CNN con siluetas (H15) | **Transfiere en 2 de 3 fuentes**: NightOwls +3,28 [+1,64; +4,79], CityPersons +2,33 [+1,01; +3,69] (ambas también con IC jerárquico); en CityPersons la ganancia es mayor en las personas ocluidas, en NightOwls no |
| Faster R-CNN con oclusores por difusión / profundidad (H16a / H16b) | **0 de 3** en ambas, aunque los controles suben +20,35 y +9,63 |
| RetinaNet con siluetas (H17; una etapa, misma red base y receta que H15) | **0 de 3** (control +6,60; todos los estratos reales bajan) |
| La misma V1 de Faster R-CNN re-entrenada en otra máquina | difiere hasta 3,42 pp en una fuente real, del orden de las ganancias de H15 |

El aumento siempre se aprende y pasa de una oclusión sintética a otra, pero solo uno de los 18 bloques (Faster R-CNN con siluetas) llega a la oclusión real, en dos fuentes. El mismo detector con otros oclusores y RetinaNet con siluetas no, y dentro de Faster R-CNN el mayor control sintético (+20,4, difusión) no transfiere y uno menor (+14,7, siluetas) sí: la ganancia sintética no anticipa la real. Los datos anotados del dominio ayudaron a las personas muy ocluidas mucho más que cualquier aumento. El trabajo completo está en `shortpaper5/` (short paper y suplemento, en español e inglés).

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
| `informes/` | Veredictos (`veredicto_*.md`), informes (`reporte_*.md`), tablas consolidadas (`analisis_final/`) y los scripts que las generan |
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
