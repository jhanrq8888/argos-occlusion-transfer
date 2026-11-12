# argos-occlusion-transfer

**Mejorar sobre oclusión sintética no basta: estudio controlado de la transferencia a la oclusión real en la detección de personas.** Paquete de replicación de ARGOS-11: experimentos controlados con hipótesis registradas internamente con huella criptográfica (Universidad Peruana Unión, Juliaca, Perú). [English version](README.md).

El aumento sintético de oclusión (pegar parches, siluetas u objetos generados sobre las personas al entrenar) es un remedio habitual para detectar personas ocluidas, y su beneficio suele medirse con la misma oclusión artificial. Este repositorio comprueba si ese beneficio llega a la **oclusión real anotada por humanos**. En cada bloque, un modelo base (V1) y uno aumentado (V3) comparten datos, hiperparámetros, aumento base y máquina (salvo H16, cuyas V1 son las de H15, de otra máquina). Todos los bloques menos uno tienen un control sintético y tres fuentes de oclusión real (peatones ocluidos de NightOwls, CityPersons *heavy* y un indicador de oclusión sobre ExDark, fuente secundaria). Su hipótesis, su regla de decisión y su código se fijaron con una huella SHA-256 antes de entrenar. 21 bloques y 133 corridas (incluidas las de un planteamiento inicial con un módulo de atención, H1, H2 y H5); seis detectores, cuatro de ellos con exposición igual (evidencia primaria: YOLOv11s, YOLOv11m, Faster R-CNN y RetinaNet).

## Resultados principales

| | Resultado |
|---|---|
| Controles sintéticos que pasan (+2 pp de AP@0.5 con IC del 95 % > 0) | **20 de 20** bloques con control (+2,6 a +60,9 pp) |
| Modelo mixto global (bloque y semilla aleatorios), dosis habitual, exposición igual, 12 bloques (posterior) | NightOwls +0,54 [−0,40; +1,48], CityPersons **+1,03** [+0,09; +1,97], ExDark −1,13 [−2,08; −0,19]: poco compatible con una ganancia media de +2 pp (límite superior al 90 %: +1,33, +1,82 y −0,34; CityPersons +1,93 con V1 compartidas y +1,51 con *bootstrap* de bloques); con los bloques de dosis H18e, los límites suben a +2,11 y +2,13 |
| Recuento descriptivo, mismas 36 celdas, IC jerárquico (criterio uniforme de semillas) | pasan 5, 9 descartan +2 pp, 22 no son concluyentes (con el IC de Welch entre semillas: 3, 11 y 22) |
| Faster R-CNN con siluetas (H15) | cumple la regla prerregistrada en NightOwls (+3,28) y CityPersons (+2,33), pero con la varianza entre semillas (Welch) ambos IC incluyen el cero |
| H15 repetida con 5 semillas en otra máquina (H18a) | **1 de 3**: NightOwls +4,26 se mantiene (también con Welch); CityPersons +1,74 [−0,08; +3,69] no |
| Dosis del aumento (H18e, Faster R-CNN, siluetas) | dosis baja 1 de 3; **dosis alta 2 de 3** (NightOwls +8,59, CityPersons +3,78), pero en pp las personas sin oclusión ganan igual o más (+8,87, +5,34) y ExDark baja −1,98; en escala relativa la ganancia es mayor en las ocluidas, así que la especificidad depende de la escala; con Welch solo NightOwls excluye el cero |
| Sin el indicador de ExDark (deben pasar NightOwls y CityPersons) | solo H15 y H18e-alta; con la dosis habitual solo H15, que no vuelve a cumplir la regla con 5 semillas |
| +2 pp en personas (posterior, detecciones de H18) | unas 17 personas ocluidas más detectadas por cada 1 000 con 0,1 falsos positivos por imagen |
| Faster R-CNN con difusión / profundidad (H16a / H16b); RetinaNet con siluetas (H17) | **0 de 3** cada uno, aunque los controles suben +20,35, +9,63 y +6,60 |
| Especificidad y caja visible (posteriores) | de las 6 celdas que pasan en H3–H17, solo las dos del indicador de ExDark son propias de la oclusión; con la caja visible, la ganancia en CityPersons *heavy* no supera +1,3 pp en ningún bloque |

El aumento siempre se aprende, pero pasar un control sintético no basta para afirmar robustez a la oclusión real: con la dosis habitual y exposición igual, el resultado es poco compatible con una ganancia media de +2 pp; el único bloque que pasó la regla no volvió a cumplirla con 5 semillas, y la dosis alta que sí transfiere mejora en los mismos pp a las personas sin oclusión. El trabajo completo está en `shortpaper5/` (short paper y suplemento, en español e inglés; versión del 11/11/2026). Las respuestas a las revisiones están en `shortpaper5/revision_externa_28oct/`, `shortpaper5/revision_10nov/` y `shortpaper5/revision_11nov/` (matrices de respuesta; los PDF con cambios marcados están en el repositorio privado porque llevan los correos de los autores), con los análisis en `informes/modelo_mixto_m3.py`, `informes/revision_10nov.py` e `informes/revision_11nov.py`.

## Qué hay en el repositorio

| Ruta | Contenido |
|---|---|
| `argos_lib/` | Biblioteca: AP con regiones *ignore*, formato de anotaciones, generadores de oclusión (parches, siluetas, difusión, geometría real y orden de profundidad) y enganches para Ultralytics |
| `00_*.py` … `37_*.py` | Scripts de la tubería en orden de ejecución. Cada uno documenta su uso en su encabezado y la mayoría tiene `--selftest` |
| `config/` | Hiperparámetros y aumento base (idénticos en V1 y V3) |
| `PROTOCOLO*.md`, `PREREGISTRO_*.md` | Hipótesis H1–H18, reglas de decisión y diseño, escritos antes de cada bloque |
| `CAMBIOS_PROTOCOLO.md`, `protocolo_congelado.json` | Registro de cada congelamiento (fecha, SHA-256 global y motivo) y huellas por archivo del congelamiento vigente |
| `runs/<bloque>/<corrida>/` | `results.csv`, `args.yaml` y `registro_argos.json` de cada una de las 133 corridas válidas (los pesos no se versionan) |
| `resultados*/` | Evaluación por corrida (`eval/`), resúmenes de AP y análisis *bootstrap* de cada bloque |
| `informes/` | Veredictos (`veredicto_*.md`), informes (`reporte_*.md`), tablas consolidadas (`analisis_final/`) y los scripts que las generan, incluidos los análisis posteriores de la revisión del 22/10 (`revision_panel_analisis.py`, `controles_extra.py`) |
| `dataset/splits`, `dataset_cp/`, `dataset_no/` | Identificadores de las imágenes de cada partición y muestra (sin imágenes) |
| `anotacion_anotador_*.csv`, `consenso.csv` | Gradación manual de la oclusión usada en el estudio de fiabilidad (anotadores seudonimizados) |
| `shortpaper5/` | Short paper y suplemento (LaTeX, PDF y los scripts que generan cada tabla y figura) |
| `runpod/` | Scripts con que se entrenaron H11, H12 y H14–H18 en RTX 4090 alquiladas, y las huellas SHA-256 de los pesos descargados |
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
   - H18: el mismo script con `--dosis base|baja|alta` (`runpod/h18/pod_correr.sh`)

   El comando exacto de cada bloque está en su `PREREGISTRO_*.md`, en su lanzador (`*.bat`, `runpod/*/pod_correr.sh`) y en `runs/*/*/args.yaml`.
4. **Evaluación.** `09_evaluar_estratificado.py --pesos <pesos> --nombre <corrida> --gt <anotaciones>` (en H15–H18, primero `35_dos_etapas.py inferir` y luego `09_`; H18: `h18_evaluar.bat`).
5. **Veredictos y análisis.**
   - Veredictos: `19_veredictos.py` (H1–H8), `26_veredicto_h9b.py`, `28_geometria.py analisis` (H10), `29_h11_dominio.py`, `30_h12.py`, `31_realismo.py` (H13), `34_h14.py`, `36_h15.py`, `37_h16_h17.py` y `38_h18.py`; modelo mixto global: `informes/modelo_mixto_m3.py`.
   - Sensibilidad: `23_bootstrap_jerarquico.py`, `24_miss_rate.py` y `27_ap_estricto_visibilidad.py`.
   - Análisis de la revisión: `informes/revision_sp_analisis.py`, `informes/matriz_cruzada.py`, `informes/kid_oclusor.py` e `informes/registro_corridas.py`.
6. **Tablas y figuras del artículo.** `shortpaper5/suplemento_tablas.py`, `shortpaper5/fig_dispersion.py` y `shortpaper5/fig_gap.py`.

**Comprobar el congelamiento.** `python 08_congelar_protocolo.py --verificar` compara los archivos actuales con `protocolo_congelado.json`. Los archivos derivados de los conjuntos de datos (anotaciones y oclusores generados) no están en el repositorio y aparecerán como ausentes hasta que los reconstruyas. Las huellas prueban que los archivos congelados no cambiaron después de la fecha registrada; esas fechas las registra el propio proyecto, no un tercero.

## Notas

- **No se incluyen imágenes, pesos ni anotaciones de terceros.** ExDark, CityPersons/Cityscapes y NightOwls permiten el uso de investigación no comercial y prohíben redistribuir sus datos. Los pesos de la evidencia primaria (H9b–H18, 67 corridas) están en Zenodo: [10.5281/zenodo.24120199](https://doi.org/10.5281/zenodo.24120199) (CC BY-NC 4.0); su SHA-256, en `informes/analisis_final/pesos_sha256.csv`. El registro de hipótesis, el protocolo congelado y sus sellos OpenTimestamps (`*.ots`) están depositados en Zenodo: [10.5281/zenodo.24148406](https://doi.org/10.5281/zenodo.24148406).
- Los comentarios y los informes están en español; el short paper y el suplemento están en español e inglés.
- El programa es adaptativo: H9b–H18 se diseñaron después de ver resultados anteriores (H18, tras una revisión externa), y cada una se congeló antes de entrenar su propio bloque. Los parámetros del aumento de cada bloque están en `informes/analisis_final/configuracion_aumento.yaml`.

## Licencia y cita

El código está bajo licencia MIT; los textos, las tablas y las figuras, bajo CC BY 4.0 (ver `LICENSE`). Para citar, usa `CITATION.cff`.
