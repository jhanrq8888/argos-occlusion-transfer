# Respuesta a la revisión externa del short paper (27/10/2026)

**Informe:** `g1reporte_revision_short_paper_oclusion_sintetica_real_alac35abj0.docx` (veredicto: cambios mayores; 0 críticas, 5 mayores, 3 menores).

**Versión revisada (29/10/2026):** `shortpaper5/main_es.tex` y `main.tex`, de 5 páginas cada uno, más `suplemento_es.tex` y `suplemento.tex`.

**Versión de partida:** `revision_externa_28oct/version_base/`. Es la presentada más seis correcciones de redacción del 27/10.

**Cambios marcados:** `main_es_diff.pdf` y `main_diff.pdf` (latexdiff). Las tablas y el diagrama se marcan como bloque.

**Título nuevo:** «Mejorar sobre oclusión sintética no basta: la transferencia del aumento de oclusión a la oclusión real depende de la dosis en la detección de personas».

---

## 10.4 Matriz de respuesta

| N.º | Observación | Posición | Qué se hizo y por qué | Ubicación en la nueva versión | Evidencia adjunta |
|---|---|---|---|---|---|
| **M1** | El positivo (H15) se juzga con un criterio (t de Welch) que no se aplica a los negativos. Además, el texto contradice la tabla. | Acepto | Se usa un solo criterio de varianza entre semillas en las 54 celdas: el IC jerárquico (marca ° en la tabla I). Se eliminó la t de Welch. Las celdas que «descartan» se recuentan con el mismo IC (9 en lugar de 16). H15 se redacta «pasa la regla, también con el IC jerárquico». Como pedía el revisor, **H15 se repitió con 5 semillas (H18a, preregistro v3.12)**: NO +4,26 [+2,21; +6,32] pasa y CP +1,74 [−0,08; +3,69] no, así que queda en 1 de 3. Por eso la † dice ahora «no se replica con 5 semillas». | Resumen; III «Evaluación»; IV «Detector, dominio y datos»; VI; tabla I (fila H18a y †) | `PREREGISTRO_H18.md`; `informes/veredicto_h18.md`; `resultados_h18/analisis/contrastes_h18.json`; `informes/analisis_final/celdas_con_h18.csv` (columnas pasa, pasa_jer, descarta_2pp y descarta_2pp_jer) |
| **M2** | El indicador de ExDark es posterior, débil y se presenta como fuente real. | Acepto | En III se declara que se adoptó el 13/09/2026, tras H3 y H4, porque la anotación manual no era fiable (κ 0,06–0,60). Se declara su validez (Spearman 0,24; κ 0,24) y que desde H6 estaba fijado antes de entrenar (H9b en adelante incluido). **Sensibilidad sin EX**, exigiendo NO y CP: solo H15 y H18e-alta detectan transferencia. Con la dosis habitual solo queda H15, que no se replica; la conclusión no cambia. | III «Datos»; IV «Análisis posteriores»; V «Limitaciones»; suplemento §«Revisión externa del 27/10» | `CAMBIOS_PROTOCOLO.md` (2026-09-13 15:40); `modelo_mixto_m3.json` → `sin_EX` |
| **M3** | Contar 51 celdas dependientes no estima el efecto, y no se sabe qué IC manda. | Acepto | Modelo mixto REML: Δ por semilla ~ fuente (fijo) + bloque + semilla(bloque). Con la dosis habitual y exposición igual (12 bloques, 114 obs.): NO +0,57 [−0,34; +1,48], CP +1,06 [+0,15; +1,96], EX −1,11 [−2,01; −0,20]. Los tres límites superiores quedan por debajo de +2. La relación con la ganancia en el control (OE5) es +0,16 por DE [−0,46; +0,78]. El recuento queda como descripción. Jerarquía de IC declarada: el modelo mixto para el efecto global; en el texto, el IC jerárquico de cada celda; en la tabla, además, el IC por imágenes que fija la regla preregistrada. Se eliminaron el bootstrap de bloques y la t de Welch. | III «Evaluación»; IV «Estimación global»; suplemento (tablas S de modelo y recuentos) | `informes/modelo_mixto_m3.py`, `.json`, `.md`, `_datos.csv` |
| **M4** | Una sola dosis sin probabilidad informada; alcance no acotado por escala ni por dosis. | Acepto | Se informan la probabilidad y la dosis (p 0,5; 1–3 personas; cobertura 0,30–0,85). **Bloque de dosis-respuesta preregistrado (H18e)**: dosis baja y alta, con Faster R-CNN en lugar de YOLOv11s, porque es el único detector con transferencia y así se pone a prueba el positivo. La dosis alta pasa en 2 de 3 fuentes, pero las personas sin oclusión ganan igual o más (NO +8,87 frente a +8,59; CP *bare* +5,34 frente a *heavy* +3,78) y ExDark empeora (−1,98). El alcance se acota a 1 183 imágenes, ajuste fino desde COCO y tres dosis probadas solo con Faster R-CNN. **H7 sin control:** se ofreció como alternativa al bloque de dosis, que sí se hizo; H7 sigue marcada como «no concluyente (sin control)». | Título; III «Aumento, dosis y control»; IV «Dosis»; V; VI; suplemento (especificidad por dosis) | `configuracion_aumento.yaml`; `35_dos_etapas.py --dosis`; `resultados_h18/resumen_ap.csv` |
| **M5** | Texto demasiado denso. | Acepto en parte | **Hecho:** diagrama del programa adaptativo (fig. 1, de H3 a H18); un solo IC por celda en el texto; análisis posteriores agrupados en un párrafo rotulado; resumen de 186 palabras (ES) y 175 (EN) con cuatro cifras clave; se quitaron H1, H2 y H5 del texto. La fig. de dispersión pasó al suplemento. **No hecho:** renumerar B1–B18. Las etiquetas H son las de los 15 preregistros congelados con huella, los registros de corrida, el repositorio y el suplemento; renumerar rompería esa trazabilidad. En su lugar, la tabla I va en orden cronológico y el diagrama muestra el orden y el motivo de cada bloque. | Resumen; fig. 1; IV; tabla I | `fig_programa_es.tex`, `fig_programa_en.tex` |
| **m1** | «Hipótesis preespecificadas» promete más de lo verificable. | Acepto | El texto dice «registradas internamente con huella criptográfica» en palabras clave, resumen y III. En V se declara que no hay sello de un tercero, y se adopta el compromiso de sellar las huellas futuras con OpenTimestamps antes de entrenar. | Palabras clave; Resumen; III; V | — |
| **m2** | +2 pp solo justificado por el ruido; cifra del INEI de 2015 sin retomar. | Acepto | **Umbral en términos prácticos:** con las detecciones de H18, +2 pp de AP equivalen a unas **17 personas ocluidas más detectadas por cada 1 000**, con 0,1 falsos positivos por imagen (18 pares, r = 0,90). V1 detecta 91 por cada 1 000 en CP *heavy* y 196 en NO. **INEI actualizado:** RENAMU 2023, 14 722 cámaras operativas del serenazgo (nota de prensa del 9/04/2024). La cifra se retoma en la Discusión con su consecuencia práctica. | III «Evaluación»; I; Discusión | `informes/umbral_practico_m2.py` → `analisis_final/umbral_practico_m2.json`; `references.bib` (`INEI2024renamu`) |
| **m3** | Sin DOI, fechas de consulta en dos idiomas, sin licencias, etiquetas de veredicto sin definir, [26] sin localizar. | Acepto | 35 DOI visibles en la bibliografía: IEEEtran no imprime el campo doi, así que van en la nota. Bibliografías `references_es` y `references_en` con las fechas de consulta en el idioma de cada versión. Se restituyó la frase de licencias. La nota de la tabla I define todas las etiquetas («No detectada», «Detectada», «No confirmada», «Refutada», «No concluyente», «Mismo patrón» y el brazo H10-s). [26] (INDICON 2024) lleva su DOI 10.1109/INDICON63790.2024.10958520. | Referencias; III «Datos»; tabla I | `bib_doi.py` |

### Recomendaciones de la sección 6 (presentación)

| Recomendación | Qué se hizo |
|---|---|
| Resumen legible con pocas cifras | Reescrito, de 186 palabras, sin paréntesis anidados. |
| Redactar H15 sin contradicción | «Pasa la regla, también con el IC jerárquico»; la réplica no lo confirma. |
| Cifras del IC secundario a la tabla | El IC por imágenes queda solo en la tabla I; en el texto, solo el jerárquico. |
| Nota de la tabla I demasiado larga | La potencia de la regla y los criterios pasaron al texto (III «Evaluación»). La nota queda con abreviaturas y definiciones de veredicto, que pidió m3. |
| Fig. 1 con 51 puntos superpuestos | Se sustituyó por el diagrama del programa. La dispersión va en el suplemento, sin la carga del texto. |
| Tabla del modelo mixto y de sensibilidad sin EX | Están en el suplemento (tablas generadas por `suplemento_revision27.py`). En el texto van las cifras clave. |

### Sección 8 (trabajos cercanos no citados)

Por el límite de 5 páginas no se añadieron «Toward robust pedestrian detection with data augmentation» (IEEE Access, 2020) ni la revisión arXiv 2101.08845. Quedan para el artículo largo.

### 10.3 Errores frecuentes: verificación

- **Mismo criterio para positivos y negativos:** sí. El IC jerárquico se aplica a todas las celdas y el recuento de «descartan» se hace con él.
- **Modelo mixto como estimación principal y recuento como descripción:** sí.
- **El resumen conserva las cifras que respaldan la conclusión:** sí (20 controles, +1,1 como máximo, se descarta +2 y dosis alta no específica).
- **Tabla I, fig. 1, resumen y conclusión actualizados juntos:** sí.
- **Cada respuesta dice dónde se cambió:** sí, en la columna «Ubicación».

**Costo de los experimentos nuevos:** 16 corridas y 9,4 h de GPU (3,3 h de pod RTX 4090, unos 3 USD). El total pasa de 117 a 133 corridas y de 99 a 109 h.

**Pendiente para los autores:**
1. Confirmar la cifra del INEI 2023 en el PDF oficial. La página de gob.pe bloqueó la consulta automática; el dato sale del texto indexado de la nota.
2. Publicar en el repositorio público el material nuevo: H18, el modelo mixto, el umbral en personas, el YAML y las tablas.

---

## Paso 9: matriz de coherencia rehecha (rúbrica del curso)

| Elemento (peso) | Lo que dice la nueva versión (ubicación) | Nivel | Puntos |
|---|---|---|---|
| Problema (20 %) | El beneficio se mide con la misma oclusión artificial; si no se traslada, se despliega una robustez que no existe. 14 722 cámaras de serenazgo en el Perú (I). | Coherente | 20,0 |
| Vacío (10 %) | Ningún estudio cumple (i)–(iv), que ahora incluyen la dosis entre las alternativas (I «Brecha»; II). | Coherente | 10,0 |
| Objeto (3 %) | La celda = bloque × fuente; la validez del indicador de ExDark se declara (III «Datos»). | Coherente | 3,0 |
| Objetivo, pregunta e hipótesis (1 %) | Objetivo general y OE1–OE5 (OE2 incluye la dosis); H3–H18 con su predicción (I, III). | Coherente | 1,0 |
| Aporte (5 %) | (1) 21 bloques y tres dosis; (2) modelo mixto y especificidad; (3) protocolo mínimo, que solo H18a cumple entero (I). | Coherente | 5,0 |
| Diseño y método (10 %) | Pares V1–V3, épocas fijas, dosis informada, un criterio de semillas, modelo mixto, umbral justificado en personas (III). | Coherente | 10,0 |
| Resultados (40 %) | 20 controles pasan. Modelo mixto con dosis habitual: +0,57, +1,06 y −1,11, se descarta +2. H15 no se replica. La dosis alta transfiere sin especificidad (IV; tabla I). | Coherente | 40,0 |
| Conclusiones (3 %) | Se descarta +2 pp con la dosis habitual, H15 no se replica y la dosis alta no es específica. El alcance queda acotado a escala, dosis y métrica (VI). Ya no hay contradicción con la tabla. | Coherente | 3,0 |
| Título y resumen (8 %) | El título refleja el hallazgo de la dosis; resumen de 186 palabras con cuatro cifras clave, coherente con VI. | Coherente | 8,0 |

**Lectura de la cadena:** problema → vacío → objetivos → método → resultados → conclusión, sin cortes. El positivo y los negativos se juzgan con el mismo criterio, y la conclusión se sigue del modelo mixto y de la réplica. La nota sugerida es del revisor; la decisión final es del docente.

---

## Segunda vuelta (revisión simulada del 29/10, `REVISION_SIMULADA_2.md`)

| N.º | Qué se hizo |
|---|---|
| N1 (dosis alta y personas pegadas etiquetadas) | En Discusión se declara la segunda lectura: la dosis alta multiplica hasta por 3,5 las personas pegadas y etiquetadas, como un aumento Copy-Paste [13]. Ambas lecturas coinciden en que la ganancia no es específica de la oclusión. Separarlas queda como trabajo futuro (1). |
| n1 | Resumen: «Los 20 bloques con control mejoran en él». |
| n2 | Se mantiene el título elegido por los autores; el resumen matiza el hallazgo. |
| n3 | «+2 pp ≈ 17 personas por cada 1 000» se acota a Faster R-CNN. |
| n4 | Limitaciones: los bloques comparten líneas base y el modelo mixto no modela esa dependencia. |
| n5 | Figura nueva de dosis (`fig_dosis.py`, desde `resultados_h18/resumen_ap.csv`): V3−V1 por dosis en personas ocluidas y sin oclusión, NightOwls y CityPersons. Muestra de un vistazo que la ganancia con dosis alta no es específica. Se recortó texto secundario para mantener 5 páginas. |

**Repositorio público actualizado** el 29/10 (commit e27c00f, escaneo de datos sensibles limpio). Los PDF de cambios marcados no se publican porque contienen los correos de los autores; se entregan aparte.
