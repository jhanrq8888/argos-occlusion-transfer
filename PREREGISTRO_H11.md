# ARGOS-11 — Pre-registro de H11 (E9: ganancia dentro del dominio sobre las personas más ocluidas, con exposición igual)

Borrador redactado el **2026-10-09** y completado y congelado el **2026-10-13** (protocolo **v3.6b**), **antes** de subir los datos al servidor de entrenamiento y de entrenar o evaluar nada con este diseño. Sustituye a una versión v3.6 congelada el mismo día a las 14:21. Esa versión repetía la exposición desigual de E4 y había sobrescrito por error este borrador; se reemplazó antes de cualquier corrida (ver `CAMBIOS_PROTOCOLO.md`).

## 0. Lo que se hizo antes de este documento (declarado)

1. **H6 (E4)** se pre-registró y cerró el 19–20/09: 6 corridas sobre CityPersons (V1 y V3 con siluetas, semillas {0, 1, 2}). Su veredicto pre-registrado (**sostenida**: *heavy* +1,82 pp, bajo el umbral de +2) **no cambia**.
2. El **análisis por visibilidad** (06–07/10, posterior y declarado) mostró que en E4 el efecto se concentra en las personas más ocluidas: +4,30 pp con visibilidad 0,20–0,35 (IC 95 % por imágenes [+0,10; +8,51]), +3,36 con 0,35–0,50 y +2,14 con 0,50–0,65, y casi nulo en las visibles. En los modelos entrenados en ExDark ocurre lo contrario: el efecto crece con la visibilidad.
3. Con las celdas que fija este documento y las mismas semillas 0–2 (`informes/h11_exploratorio_semillas_0_2.md`, calculado antes de congelar):
   - visibilidad 0,20–0,50 (n = 432): **+2,40 pp** [−0,00; +4,75];
   - visibilidad 0,80–1,00 (n = 1 192): +0,42 [−0,13; +0,95];
   - especificidad (diferencia entre ambos tramos): +1,98 [−0,36; +4,23];
   - control `cp_silueta_severa`: +23,74 [+21,09; +26,51].
4. H11 nace de ese análisis exploratorio. Se declara así: **es una prueba confirmatoria de un hallazgo posterior**, no una hipótesis previa a los datos de E4. Esos datos no cuentan para decidirla.

## 1. Motivación y un problema de diseño de E4

En H6 las dos variantes **no tuvieron la misma exposición**: la parada temprana detuvo a V1 en las épocas 58, 65 y 71, mientras que V3 llegó a las 100 en las tres semillas. La ganancia de E4 puede venir del aumento o de haber entrenado más. Es el mismo tipo de confusión que ya se detectó en E2 (V3 37–89 épocas frente a 1–2 de V1) y que se corrigió con E7b y E8 fijando las épocas.

H11 repite el contraste de E4 **igualando la exposición**: V1 y V3 se entrenan el **mismo número de épocas, completo**, sin parada temprana ni selección por validación.

## 2. Hipótesis (literal; no se reformula después)

- **H11.** Con entrenamiento en CityPersons y exposición igual, el aumento con siluetas mejora la detección de las personas más ocluidas de ese dominio. Las condiciones son:
  - YOLOv11s con el protocolo de H6 (`--protocolo cp`);
  - **V1 y V3 entrenados exactamente 60 épocas** con el calendario completo de tasa de aprendizaje, sin parada temprana;
  - evaluación con los **pesos de la última época** (`last.pt`);
  - **semillas nuevas {3, 4, 5}** (no se reutiliza ninguna corrida de H6).

  Bajo esas condiciones, el contraste V3 − V1 (AP@0.5, media de las 3 semillas) en el **tramo de visibilidad anotada 0,20–0,50** de CityPersons *val* (convención oficial; las demás personas son regiones *ignore*) **alcanza +2 pp con IC 95 % por imágenes que excluya el cero** (bootstrap pareado, 1 000 réplicas, semilla 0). Además, el control sintético `cp_silueta_severa` tiene que alcanzar +2 pp con IC que excluya el cero (prueba de que el aumento se aprendió).
  - *Confirmada:* se cumplen las dos condiciones.
  - *No confirmada:* el control se cumple, pero el tramo 0,20–0,50 no alcanza +2 pp con IC > 0.
  - *No concluyente:* el control `cp_silueta_severa` no alcanza +2 pp con IC que excluya el cero.
- **Por qué este tramo.** Reúne los dos tramos más ocluidos (0,20–0,35 y 0,35–0,50; n = 432), donde E4 mostró el efecto. Se prefirió a 0,20–0,35 solo (n = 178, +4,30 en E4) porque su intervalo sería muy ancho y porque elegir el tramo con el mejor número sería ajustar el criterio a los datos. Se fija ahora, antes de ver ningún resultado de H11.
- **Compromiso de reporte.**
  - Si H11 **no se confirma** o es no concluyente, el artículo, el short paper y el PPI retiran «dentro del dominio el aumento las ayudó algo» y reportan que la ganancia de E4 no se confirmó con exposición igual.
  - Si **se confirma**, se reporta como un resultado confirmatorio **acotado a CityPersons**, sin ampliarlo a otros conjuntos.
- **Análisis secundarios declarados ahora (no deciden H11):**
  1. **Especificidad**, con las semillas 3–5 y los mismos remuestreos de imagen: (V3 − V1) en visibilidad 0,20–0,50 menos (V3 − V1) en 0,80–1,00. Si es > 0 con IC que excluya el cero, la mejora es propia de la oclusión y no un efecto general del aumento.
  2. **Las 6 semillas juntas {0–5}**, con IC jerárquico (semillas + imágenes, 2 000 réplicas). **Advertencia:** las semillas 0–2 tienen exposición desigual y se entrenaron en otra máquina.
  3. Descriptivos: tramo 0,20–0,35 solo, estratos *bare/partial/heavy*, AP@0.5:0.95, tasa de pérdida y transferencia (V3 − V1 en NightOwls ocluida y en el proxy de ExDark severa; se dirá «no se transfiere» solo si ninguno alcanza +2 pp con IC > 0).

## 3. Diseño

| Elemento | Definición |
|---|---|
| Modelo, hiperparámetros, aumento base | Idénticos a H6 (`yolo11s.pt`, `config/hiperparametros.yaml`, `config/aumento_base.yaml`). Única excepción: épocas y paciencia |
| Épocas | **60 fijas** (`--epochs 60 --patience 0`; en Ultralytics, paciencia 0 desactiva la parada temprana), con el calendario completo de tasa de aprendizaje |
| Por qué 60 | Están cerca de las épocas en que la parada temprana detuvo a V1 en H6 (58–71), así que ninguna variante se lleva mucho más allá de su punto de rendimiento. 100 épocas añadirían sobreajuste al dominio a ambas y costarían casi el doble. Se fija antes de ver ningún resultado |
| Pesos evaluados | `last.pt` (época 60). `best.pt` se guarda, pero **no** se usa para el criterio |
| Datos y partición | Los de H6, sin cambios: CityPersons *train* (2 675) y *val_interno* (300), semilla de partición 0, `dataset/data_citypersons.yaml`, banco `siluetas_cp_train`. No se genera nada nuevo |
| Validación | La mixta de H6; solo se registra (curvas), no selecciona nada |
| Variantes y semillas | **V1** y **V3** (siluetas), semillas **{3, 4, 5}**: **6 corridas** en `runs/argos_cp_fijo/`. Orden por pares: V1_s3, V3_s3, V1_s4, V3_s4, V1_s5, V3_s5 |
| Comando | `07_entrenar.py --protocolo cp --variantes V1 V3 --semillas 3 4 5 --epochs 60 --patience 0 --proyecto argos_cp_fijo --workers 8` |
| Hardware (cambio declarado) | Las 6 corridas se entrenan en un servidor alquilado (RunPod, una RTX 4090, 12 vCPU), no en la laptop (RTX 5050) del resto del proyecto. V1 y V3 se entrenan en la **misma** máquina, así que el contraste es interno. Se usan 8 procesos de carga de datos (en la laptop eran 4) por los núcleos disponibles; la receta no cambia. Ultralytics **8.4.143**; las versiones de PyTorch y CUDA del servidor quedan en cada `registro_argos.json` |
| Datos subidos | Solo lo que necesita la receta: código, `yolo11s.pt`, imágenes y etiquetas de CityPersons *train*, partición `dataset_cp/`, banco `siluetas_cp_train` y configuración. Las rutas de Windows se reescriben a Linux en el servidor, sin cambiar el contenido. Nada de CityPersons *val* sale del equipo local |
| Evaluación | En la laptop, con los pesos descargados: `09_evaluar_estratificado.py --pesos runs/argos_cp_fijo/{V1,V3}_sN/weights/last.pt --nombre {V1,V3}_sN --variante {V1,V3} --semilla N --resultados resultados_h11`, sobre `cp_silueta_severa` (control), `gt_citypersons_convencion.json`, `gt_nightowls.json` y `gt_test_proxy.json` |
| Veredicto | `29_h11_dominio.py` (autotest 8/8) aplica la regla literal → `resultados_h11/analisis/contrastes_h11.json` e `informes/veredicto_h11.md` |
| Costo estimado | 6 corridas × 60 épocas; en la 4090, ~4–5 h (~4–5 USD) |

## 4. Lo que NO se hará

- No se cambiarán épocas, paciencia, hiperparámetros, datos, banco de siluetas, semillas ni el tramo después de ver ninguna corrida.
- No se usará `best.pt` para el criterio, ni se elegirá otra época, otro tramo u otro estrato a posteriori.
- No se añadirán semillas, y no se reutilizarán las corridas de H6 en el criterio.
- No se cambiará el veredicto de H6, que sigue siendo el pre-registrado.

## 5. Orden de ejecución

1. Congelamiento **v3.6b** (este documento y `29_h11_dominio.py`), con fecha y huella en `CAMBIOS_PROTOCOLO.md`. **No subir datos ni entrenar antes.**
2. Subida de datos, entorno con Ultralytics 8.4.143 y prueba de humo (1 época, 5 %) en el servidor.
3. Las 6 corridas en el orden de la sección 3.
4. Descarga de pesos y registros; evaluación local, contrastes, veredicto e `informes/reporte_h11.md` con el veredicto literal.
5. Solo después, actualizar el short paper, el artículo, el PPI y el informe general con el resultado, sea cual sea.
