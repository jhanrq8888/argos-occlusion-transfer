# Respuesta a la revisión del short paper (10/11/2026)

**Reporte:** `reporte_revision_g1_jqkka4fd2h.docx`. Veredicto: cambios mayores, con 0 observaciones críticas, 4 mayores, 4 menores y 2 apreciaciones.

**Versión revisada.** El revisor leyó el PDF del 01/11/2026 (commit `88c7ebd`), copiado en `version_revisada/`. Algunas frases que cita ya habían cambiado en las revisiones de estilo del 06/11 y el 09/11. Los cambios frente a esa versión están marcados en `main_es_diff.pdf` y `main_diff.pdf`.

**Nueva versión:**
- `../main_es.tex` y `../main.tex`: 6 páginas cada uno, sin citas indefinidas ni líneas desbordadas. Pasar de 5 a 6 páginas lo aprobaron los autores.
- Suplemento: 13 páginas.

**Análisis nuevos.** Todos son posteriores y ninguno cambia una regla ni un veredicto registrado:
- `informes/revision_10nov.py`: sensibilidad, TOST y comparación con el azar.
- `shortpaper5/fig_bosque.py`: figura de bosque.
- `shortpaper5/fig_curvas.py`: curvas por época.
- `informes/manifiesto_pesos.py`: SHA-256 de los pesos.
- `informes/sellar_ots.py`: sellos OpenTimestamps.

**Corrección de cálculo encontrada al verificar.** El optimizador por defecto de `statsmodels` (BFGS) no convergía en varios modelos mixtos. Ahora `informes/modelo_mixto_m3.py` y `revision_10nov.py` prueban cuatro optimizadores y usan el ajuste convergido de mayor verosimilitud.

| Cifra del modelo principal (dosis habitual) | Antes (BFGS) | Ahora (ajuste convergido) |
|---|---|---|
| NightOwls | +0,57 [−0,34; +1,48] | +0,54 [−0,40; +1,48] |
| CityPersons | +1,06 [+0,15; +1,96] | +1,03 [+0,09; +1,97] |
| ExDark | −1,11 [−2,01; −0,20] | −1,13 [−2,08; −0,19] |

Los recuentos y los veredictos no cambian. El short paper, el suplemento y el artículo largo usan las cifras nuevas.

## 10.4 Matriz de respuesta

| N.º | Observación | Posición | Qué se hizo y por qué | Ubicación | Evidencia |
|---|---|---|---|---|---|
| 1 | «Descarta» se apoya en un modelo mixto posterior, y el límite de CP llega a +1,96 | Acepto | **(a) Rotulado como posterior** en el resumen, el método y la conclusión. **(b) Dos sensibilidades:** un componente aleatorio para las V1 compartidas entre bloques (H9b/H10/H10-s, H12a/H12b, H15/H16a/H16b, H18a/H18e), que es la dependencia que señaló el revisor, y un bootstrap de bloques. **(c) TOST** con IC del 90 % y margen ±2 pp, con y sin H18e. **Resultado con la dosis habitual:** los límites superiores al 90 % son +1,33 (NO), +1,82 (CP) y −0,34 (EX); CP llega a +1,93 con V1 compartidas y a +1,51 con bootstrap, así que ninguna especificación alcanza +2. **Con H18e:** los límites suben a +2,11 y +2,13. **(d) Redacción:** «descarta» pasa a «poco compatible con una ganancia media de 2 pp», y la conclusión aclara que esto vale también con otras especificaciones, pero no al incluir las dosis. | Resumen; III «Evaluación»; IV «Estimación global» y **Fig. 3 (bosque)**; VI; suplemento, tabla `tab:s-sens10` | `revision_10nov.json`; `tablas_suplemento_*_rev10.tex`; `fig_bosque.py` |
| 2 | «No detectada», con potencia ≈1/3, se lee como prueba de ausencia | Acepto | La Tabla I marca con ‡ las celdas que descartan +2 pp (límite superior jerárquico < 2). El pie dice que, sin ‡, «No detectada» no prueba ausencia. El texto se apoya en el conteo (9 de las 36 celdas primarias descartan +2 pp) y en la estimación global. | Tabla I; IV | `celdas_con_h18.csv` (`descarta_2pp_jer`) |
| 3 | El resumen y el título generalizan | Acepto en parte | El resumen termina acotando el alcance: «Con 1 183 imágenes de ajuste fino desde COCO, aumento a nivel de píxel y AP@0.5, pasar un control sintético no basta…». El título se mantiene: ya dice «estudio controlado» y «detección de personas», y el alcance queda acotado en el resumen y la conclusión. | Resumen; VI | — |
| 4 | La Tabla I es densa y usa dos tipos de IC; se pide un gráfico de bosque | Acepto | La Tabla I usa un solo IC, el jerárquico; la regla registrada se marca con *. Las filas se agrupan en «Exploratorios», «Evidencia primaria» y «Evidencia primaria: réplica de H15 y dosis». El pie explica cómo leer ‡. **Se añadió el gráfico de bosque** (Fig. 3): la estimación global por fuente en las tres especificaciones, con y sin H18e. | Tabla I; Fig. 3 | `fig_bosque.py` |
| 5 | ExDark pesa igual que las fuentes anotadas | Acepto en parte | ExDark se declara fuente secundaria en el resumen («indicador aproximado»), en el pie de la Tabla I, en III y en las limitaciones. **Se mantiene en la regla «2 de 3»** porque así se registró desde H6; cambiar la regla después de ver los datos sería otro análisis posterior. El análisis solo con NightOwls y CityPersons sigue en IV. | Resumen; III; Tabla I; IV; V | — |
| 6 | «5 de 54» sin compararlo con el azar | Acepto | Celdas que pasarían la regla con efecto verdadero 0 (aproximación normal con el IC de cada celda): 1,2 con el IC jerárquico, frente a 5 observadas; 0,6 con el IC por imágenes, frente a 7 observadas. El texto concluye que hay pocas ganancias, pero más que las del azar. | IV; suplemento `tab:s-sens10` | `revision_10nov.json` |
| 7 | Sin sello de tiempo de un tercero; se habla de «hipótesis registradas» | Acepto | El 10/11/2026 se sellaron con OpenTimestamps 15 ficheros: 13 registros de hipótesis, `CAMBIOS_PROTOCOLO.md` y `protocolo_congelado.json`. La palabra clave pasa a «registro interno con huella criptográfica». El texto y el suplemento dicen que la huella prueba la integridad y que el sello prueba la existencia desde el 10/11, no antes de entrenar. Los sellos ya están completos: el mismo 10/11/2026 quedaron anclados en los bloques 975346 y 975350 de Bitcoin, y se verifican con `ots verify <fichero>.ots`. **Depósito con fecha de un tercero:** en lugar de OSF, los registros, el protocolo congelado y sus sellos se depositaron en Zenodo con DOI [10.5281/zenodo.24148406](https://doi.org/10.5281/zenodo.24148406), que da la misma fecha pública de depósito. | III; V; palabras clave; suplemento | `*.ots`; `sellar_ots.py` |
| 8 | Los pesos solo estarán «al publicarse» | Acepto | Los 67 pesos de la evidencia primaria (6,1 GiB, un zip por bloque) están publicados en Zenodo con DOI [10.5281/zenodo.24120199](https://doi.org/10.5281/zenodo.24120199), licencia CC BY-NC 4.0 (los conjuntos de origen solo permiten investigación no comercial). Cada fichero se verifica con el manifiesto SHA-256 del repositorio. | Declaraciones; suplemento (tabla REFORMS y licencias) | `pesos_sha256.csv`; Zenodo |
| 9 | Justificar las 30 épocas | Acepto en parte | Curvas por época en el suplemento: el mAP de validación de V1 y V3 en cuatro bloques YOLO (entre las épocas 25 y 30, V3 sube de 0,24 a 0,52 pp) y la pérdida de entrenamiento de Faster R-CNN en H15, que se estabiliza tras las bajadas de la tasa. H11, entrenado 60 épocas, tampoco transfiere. No hay curvas sobre oclusión real porque no se guardaron pesos intermedios, y así se declara. | III «Detectores»; suplemento `fig:s-curvas` | `fig_curvas.py` |
| 10 | Las siluetas etiquetadas añaden positivos | Acepto | Datos: las siluetas de persona se etiquetan, lo que añade como máximo 0,13, 0,5 y 1,75 personas por imagen según la dosis. La Discusión da las dos lecturas de la dosis alta: regularización o más positivos (hasta ×3,5). Línea futura: no etiquetar las personas pegadas. | III «Datos»; V | `configuracion_aumento.yaml` |

## Secciones 5 a 7 y 9

**Sección 5 (REFORMS).**
- El análisis posterior y la multiplicidad se atienden en las observaciones 1 y 6.
- Los artefactos, en la observación 8.
- La fecha verificable, en la observación 7.
- Métricas secundarias: en IV se añade que, con MR⁻², mejoran 4 de 51 celdas reales (3 en ExDark), y que con AP@0.5:0.95 no mejora ninguna de 24 en los ocho primeros bloques. El suplemento dice lo mismo.

**Sección 6 (redacción, figuras y tablas).**
- Se adoptaron las dos versiones propuestas: la frase de los controles y la de los límites con H18e, que ahora indica que son al 90 % y que quedan «por encima del umbral».
- Los rótulos internos ya no son el sujeto de las frases; por ejemplo, «Faster R-CNN con siluetas (H15) y su dosis alta (H18e-a)».
- La Fig. 1 (programa) se conserva. Vuelve al texto la Fig. 2 (dosis) y se añade la Fig. 3 (bosque).

**Sección 7 (objeciones).**
- Escala: el alcance queda acotado en el resumen y la conclusión. La curva de datos ya está en la Tabla I: H7 entrena con NightOwls hasta 20 000 imágenes, y H6 y H11 entrenan con CityPersons.
- Post hoc: observación 1.
- Potencia: observación 2.
- Bifurcaciones del programa adaptativo: observación 7.
- «Solo AP@0.5»: frase de métricas secundarias en IV.

**Sección 9 (material).**

| Material pedido | Dónde está |
|---|---|
| Resultados por celda y semilla | `modelo_mixto_m3_datos.csv` y `celdas_con_h18.csv` |
| Script del modelo mixto y de la sensibilidad | `modelo_mixto_m3.py` y `revision_10nov.py` |
| Sellos | `*.ots`; depósito en Zenodo, https://doi.org/10.5281/zenodo.24148406 |
| Curvas | `fig_curvas.py` y la figura `fig:s-curvas` |
| Pesos | Zenodo, https://doi.org/10.5281/zenodo.24120199; manifiesto `pesos_sha256.csv` |

## Pendiente de los autores

Ninguno. Las diez observaciones están levantadas.
