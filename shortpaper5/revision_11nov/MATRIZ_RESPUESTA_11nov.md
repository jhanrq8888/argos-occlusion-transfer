# Respuesta al reporte de seguimiento del short paper (11/11/2026)

**Reporte:** `Reporte_seguimiento_G1_v3.docx`. Veredicto: cambios mayores acotados a interpretación y alcance. Las 10 observaciones del 10/11 figuran como resueltas o respondidas. Hay 7 observaciones nuevas: 0 críticas, 2 mayores, 4 menores y 1 apreciación.

**Versión revisada.** El revisor leyó `main_es.pdf` compilado el 10/11/2026 a las 20:36 (commit `37b3bf8`), copiado en `version_revisada/`. Los cambios frente a esa versión están marcados en `main_es_diff.pdf` y `main_diff.pdf`.

**Nueva versión:**
- `../main_es.tex` y `../main.tex`: siguen en 6 páginas, sin citas indefinidas ni líneas desbordadas.
- Suplemento: 14 páginas, con dos tablas nuevas (`tab:s-welch` y `tab:s-escalas`) y una nota sobre lo registrado.
- El artículo largo se alineó en los mismos puntos.

**Corrección del depósito del registro (11/11/2026).** Al revisar los artefactos se vio que la versión 1 del registro en Zenodo (10.5281/zenodo.24122872) incluía, en `CAMBIOS_PROTOCOLO.md`, los nombres de pila de dos anotadores del piloto. Se publicó la versión 2 ([10.5281/zenodo.24148406](https://doi.org/10.5281/zenodo.24148406)) con «A-B», igual que en el repositorio público, y se pidió a Zenodo que retire los archivos de la versión 1. El paper, el suplemento, el artículo y los README citan ahora la versión 2. El `CAMBIOS_PROTOCOLO.md` seudonimizado tiene su propio sello OpenTimestamps del 11/11/2026; los demás ficheros y sellos son idénticos.

**Análisis nuevos.** Todos son posteriores y están declarados en `CAMBIOS_PROTOCOLO.md`; ninguno cambia una regla ni un veredicto registrado.
- `informes/revision_11nov.py`: IC de Welch por celda y especificidad en tres escalas. Salidas: `ic_welch_celdas.csv`, `especificidad_escalas.csv` y `revision_11nov.json`.
- `shortpaper5/fig_dosis.py`: Fig. 2 con IC de Welch.
- `shortpaper5/suplemento_revision11nov.py`: tablas del suplemento.

## 10.4 Matriz de respuesta

| N.º | Observación | Posición | Qué se hizo y por qué | Ubicación | Evidencia |
|---|---|---|---|---|---|
| 11 (mayor) | El IC jerárquico con 3 semillas es anticonservador y se usa como corroboración | Acepto | **(a)** III declara que, con 3 semillas, hay solo 10 remuestreos distintos y el IC jerárquico subestima la varianza entre semillas. **(b)** Se quitó «también con el IC jerárquico» como corroboración. Para las celdas que pasan se reporta el IC de la *t* de Welch con los AP por semilla de V1 y V3: H15 NightOwls [−0,14; +6,71] y CityPersons [−0,86; +5,52], que incluyen el cero; H18a NightOwls [+2,63; +5,89], que se sostiene; H18e-a NightOwls [+6,61; +10,56] y CityPersons [−0,85; +8,41]. **(c)** Recuento como sensibilidad en las 36 celdas primarias de dosis habitual: pasan 6 (por imágenes), 5 (jerárquico) y 3 (Welch); descartan +2 pp 9 (jerárquico) y 11 (Welch). Va en IV, en el pie de la Tabla I y en la tabla del suplemento con las 42 celdas. **(d)** IV dice que el paso de H15 estaba dentro del ruido entre semillas, lo que anticipa su réplica. El suplemento advierte que Welch con 2–4 gl también es inestable: ambos IC son sensibilidad. La regla registrada y sus veredictos no cambian. | III «Evaluación»; IV «Estimación global», «Detector», «Dosis»; pie de Tabla I; VI; suplemento `tab:s-welch` | `revision_11nov.py`; `ic_welch_celdas.csv` |
| 12 (mayor) | *Transformer* y volumen de datos solo tienen evidencia exploratoria | Acepto, vía (a) | Se acota el texto. **Resumen:** «el detector (seis; cuatro con exposición igual, de una y dos etapas)». **I:** la brecha (iii) ya no incluye el volumen de datos; OE4 dice «el volumen de datos solo se exploró»; la contribución (1) dice «seis detectores (cuatro con exposición igual)». **III:** «RT-DETR-l y YOLO26s solo tienen bloques con exposición desigual (H8, H4-Y26), así que la evidencia primaria cubre cuatro detectores». La lista de hipótesis de III dice «el detector (H12, H15, H17, y H8 con exposición desigual)» y «el volumen de datos (H7, exploratorio)». **IV:** «con exposición desigual, RT-DETR-l (H8) y YOLO26s muestran el mismo signo, pero esos bloques no permiten concluir». **Fig. 1:** «¿El detector? Un *transformer* (exposición desigual)». **V:** limitación nueva sobre detectores y datos. **Vía (b):** se registró y selló con OpenTimestamps **antes de entrenar** un bloque RT-DETR-l con 30 épocas fijas (H19, `PREREGISTRO_H19.md`, congelamiento v3.13), pero no se ejecutó por falta de presupuesto para la GPU alquilada. Queda declarado en el texto, el suplemento y `CAMBIOS_PROTOCOLO.md`. Se revisaron todas las corridas de RT-DETR: solo existe H8 (V1 en 28–31 épocas y V3 en 51–77, sin pesos intermedios), así que no se puede reevaluar con exposición igual. | Resumen; I; III «Diseño» y «Detectores»; IV; Fig. 1; V «Limitaciones»; suplemento (objetivos y nota H19) | `PREREGISTRO_H19.md` y `.ots`; `CAMBIOS_PROTOCOLO.md` |
| 13 | Los signos de la estimación global no se interpretan; la Fig. 3 se llama «equivalencia» | Acepto | La Fig. 3, el método y el suplemento nombran el contraste como **prueba unilateral de no superioridad** (límite superior del IC del 90 % frente a +2 pp); ya no se habla de equivalencia ni de TOST. En V se añade que la estimación no es nula en todas las fuentes. En CityPersons hay una ganancia pequeña pero distinta de cero (+1,03 [+0,09; +1,97]). En el indicador de ExDark hay un daño (−1,13 [−2,08; −0,19]), negativo en 9 de 12 bloques y con varias familias de oclusor; la lectura tentativa, rotulada como no puesta a prueba, es que el aumento acerca el modelo a la oclusión pegada y lo aleja de la oclusión entre personas. *Nota:* el reporte dice «11 de los 12 bloques», pero el recuento en la Tabla I da 9 de 12 (positivos: H12a, H14 y H16a). | III «Evaluación»; Fig. 3; V; suplemento `tab:s-sens10` | Tabla I |
| 14 | Lo registrado no se reporta como se registró (H1, H2, H5; celda de H11; H13) | Acepto | **(i)** III: «El programa empezó con H1, H2 y H5, sobre un módulo de atención (CBAM, variantes V2 y V4) y la ganancia sintética de las siluetas: H1 y H2 no se sostuvieron, H5 sí». El suplemento da sus reglas, cifras y las 14 corridas, que están entre las 133; el resumen precisa que las 133 incluyen las del planteamiento inicial. **(ii)** El pie de la Tabla I da la celda registrada de H11: visibilidad 0,20–0,50 de CityPersons (n = 432), +1,44 [−0,64; +3,34]. **(iii)** III da la predicción de H13 (parches más distinguibles que siluetas, y estas que difusión), y IV, qué se cumplió: la primera diferencia, +0,043 [+0,031; +0,057], sí; la segunda, +0,015 [−0,003; +0,034], no. | Resumen; III; Tabla I; IV «Realismo»; suplemento (nota) | `veredictos_H1_H7.md`; `veredicto_h13.md`; `CAMBIOS_PROTOCOLO.md` |
| 15 | README y fecha del suplemento desalineados con el artículo | Acepto | Ambos README (ES/EN) usan las cifras del modelo convergido (+0,54 / +1,03 / −1,13) y el lenguaje del artículo: «poco compatible», el límite con H18e, Welch en H15 y la especificidad según la escala. Ya no dicen «*ruled out*» ni «no se replica». Fecha del suplemento: «revisado el 28 de octubre, el 10 y el 11 de noviembre de 2026». Para congelar la versión, los autores crean en GitHub la etiqueta y el *release* `v2026-11-11`, con notas que enlazan los dos DOI de Zenodo (ver «Pendiente de los autores»). | `README.md`, `README.es.md`; portada del suplemento; *release* | *release* `v2026-11-11` sobre el último commit de `main` (lo crean los autores) |
| 16 | +14,8 frente a +14,44; Fig. 2 sin IC; rótulo de H18 en la Fig. 1 | Acepto | En «Dosis»: «+14,8 pp con las semillas 0–2; la tabla da +14,44 con 5». La Fig. 2 tiene ahora barras de IC del 95 % de Welch entre semillas. Fig. 1: «Réplica: 1 de 3 (NO se mantiene); la dosis alta transfiere». | IV «Dosis»; Fig. 1; Fig. 2 | `fig_dosis.py`; `fig_programa_*.tex` |
| 17 (apreciación) | La especificidad depende de la escala | Acepto | Se mantiene la diferencia absoluta. III la justifica («la misma escala de la regla y del umbral de +2 pp») y dice que es posterior. Como el AP base de las ocluidas es mucho menor, el suplemento añade la escala relativa y la tasa de fallos (tabla nueva); el CSV incluye también la diferencia en logit. Resultado con la dosis alta en NightOwls: +8,59 pp en ocluidas y +8,87 pp sin oclusión, pero +60 % frente a +14 % en escala relativa (AP base 0,14 y 0,63) y −10 % frente a −24 % en tasa de fallos. IV y VI dicen ahora que la especificidad depende de la escala: en pp no es específica, en escala relativa la ganancia es mayor en las ocluidas. V añade que una ganancia no específica igual ayuda a detectar personas ocluidas, aunque no sea robustez a la oclusión. | III; IV «Dosis»; V; VI; resumen; suplemento `tab:s-escalas` | `especificidad_escalas.csv` |

## Matriz de coherencia actualizada (paso 7)

Filas que el reporte calificó como «Parcial»:

| Elemento | Antes | Ahora |
|---|---|---|
| Vacío | El punto (iii) incluía detector *transformer* y volumen de datos | (iii) ya no incluye el volumen de datos. El detector se probó con exposición igual en cuatro familias; RT-DETR-l y YOLO26s, solo con exposición desigual, y así se dice |
| Objetivo / hipótesis | H1, H2, H5 y la celda registrada de H11 no se reportaban | III informa H1, H2 y H5; el pie de la Tabla I da la celda registrada de H11; IV da la predicción de H13 y qué parte se cumplió |
| Aporte declarado | «Seis detectores» | «Seis detectores (cuatro con exposición igual)» en el resumen, I y III |
| Diseño y método | IC jerárquico estrecho con 3 semillas | III lo declara; IV, la Tabla I y el suplemento dan el IC de Welch como sensibilidad |
| Conclusiones | «No específica» sin escala | VI: no específica en diferencia absoluta; en escala relativa la ganancia es mayor en las ocluidas |

## Secciones 5 a 9

**Sección 5 (REFORMS):**
- Incertidumbre con la varianza entre semillas: obs. 11.
- Afirmaciones acotadas: obs. 12.
- Correspondencia entre lo registrado y lo reportado: obs. 14.
- Artefactos consistentes: obs. 15.

**Sección 6 (redacción):**
- Se adoptó la frase propuesta del resumen («Solo Faster R-CNN con siluetas mejoró dos fuentes reales…»). Por la obs. 17 dice «mejoró en los mismos pp», en lugar de «en la misma medida».
- «pp de AP@0.5» se define una vez en el resumen y se usa en todo el texto.
- La frase del costo por bloque pasó a III «Detectores y exposición».
- La frase del indicador de ExDark se cambió por la propuesta («concuerda poco con la visibilidad anotada»).
- El pie de la Tabla I aclara que el asterisco puede ir junto a un IC jerárquico que incluye el cero.

**Sección 7 (objeciones):**
- IC estrecho: obs. 11.
- *Transformer* y volumen: obs. 12.
- Escala de la especificidad: obs. 17.
- H1, H2, H5 y H11: obs. 14.
- Escala de datos: ya acotada en el resumen y las limitaciones. La observación práctica (datos anotados del dominio: 0,59 frente a 0,24 en CityPersons *heavy*) ya está en las recomendaciones del suplemento.

**Sección 8 (novedad):** los dos trabajos cercanos (arXiv 2602.18525; Algashev et al., 2026) no se añadieron al short paper por espacio. Se consideran para el artículo extendido. Ninguno combina control positivo, varias fuentes de oclusión real y reglas fijadas antes.

**Sección 9 (material):**

| Material pedido | Dónde está |
|---|---|
| IC por celda con varianza entre semillas | `informes/analisis_final/ic_welch_celdas.csv` y `informes/revision_11nov.py`; suplemento `tab:s-welch` |
| Especificidad en una segunda escala | `informes/analisis_final/especificidad_escalas.csv`; suplemento `tab:s-escalas` |
| Resultado de la celda registrada de H11 | Pie de la Tabla I y nota del suplemento |
| Opcional: bloque RT-DETR-l con 30 épocas fijas | Registrado y sellado (`PREREGISTRO_H19.md`); no ejecutado por presupuesto |

## Pendiente de los autores

1. **Release:** crear en GitHub la etiqueta `v2026-11-11` sobre el último commit de `main`, con las notas que enlazan los dos DOI de Zenodo. Es una acción pública, así que la hacen los autores desde su cuenta.

Opcional: si se consigue presupuesto, se puede ejecutar H19 tal como quedó registrado, sin cambios. Son unas 2–3 h en una RTX 4090 alquilada, o unas 10 h en la laptop.
