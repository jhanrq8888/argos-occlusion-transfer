# ARGOS-11 — Pre-registro de H11 (E9: ganancia dentro del dominio sobre las personas más ocluidas, con exposición igual)

> **ESTADO: BORRADOR. NO CONGELADO.** Redactado el **2026-10-09**. Este documento solo vale como pre-registro cuando se congele (v3.6) y se anote su huella SHA-256 en `CAMBIOS_PROTOCOLO.md` **antes de la primera época** de H11. Hasta entonces puede editarse. No se ha entrenado ni evaluado nada con este diseño.

## 0. Lo que se hizo antes de este documento (declarado)

1. **H6 (E4)** se pre-registró y cerró el 19–20/09: 6 corridas sobre CityPersons (V1 y V3 con siluetas, semillas {0, 1, 2}). Su veredicto pre-registrado (**sostenida**: *heavy* +1,82 pp, bajo el umbral de +2) **no cambia**.
2. El **análisis por visibilidad** (06–07/10, posterior y declarado) mostró que, en E4, el efecto se concentra en las personas más ocluidas: **+4,30 pp** con visibilidad 0,20–0,35 (IC 95 % por imágenes [+0,10; +8,51]), +3,36 con 0,35–0,50 y +2,14 con 0,50–0,65, y casi nulo en las visibles. En los modelos entrenados en ExDark ocurre lo contrario (el efecto crece con la visibilidad).
3. H11 nace de ese análisis exploratorio. Se declara así: **es una prueba confirmatoria de un hallazgo posterior**, no una hipótesis previa a los datos de E4.

## 1. Motivación y un problema de diseño de E4

En H6 las dos variantes **no tuvieron la misma exposición**: la parada temprana detuvo a V1 en las épocas **58, 65 y 71**, mientras que V3 llegó a las **100** en las tres semillas. La ganancia de E4 puede venir del aumento o de haber entrenado más. Es el mismo tipo de confusión que ya se detectó en E2 (donde V3 entrenó 37–89 épocas frente a 1–2 de V1) y que se corrigió con E7b y E8 fijando las épocas.

H11 repite el contraste de E4 **igualando la exposición**: V1 y V3 se entrenan **el mismo número de épocas, completo**, sin parada temprana ni selección por validación.

## 2. Hipótesis (literal; no se reformula después)

- **H11.** Con entrenamiento en CityPersons y exposición igual al aumento, el aumento con siluetas mejora la detección de las personas más ocluidas de ese dominio. Las condiciones son:
  - YOLOv11s con el protocolo de H6 (`--protocolo cp`);
  - **V1 y V3 entrenados exactamente 60 épocas** con el calendario completo de tasa de aprendizaje, sin parada temprana;
  - evaluación con los **pesos de la última época** (`last.pt`);
  - **semillas nuevas {3, 4}** (no se reutiliza ninguna corrida de H6).

  Bajo esas condiciones, el contraste V3 − V1 (AP@0.5, media de las 2 semillas) en el **tramo de visibilidad anotada 0,20–0,35** de CityPersons *val* (convención oficial, las demás personas como regiones *ignore*) **alcanza +2 pp con IC 95 % por imágenes que excluya el cero**, siempre que el control sintético `cp_silueta_severa` también alcance +2 pp con IC que excluya el cero (el aumento se aprendió).
  - *Sostenida (confirma):* se cumplen las dos condiciones anteriores.
  - *No confirmada:* el control se cumple pero el tramo 0,20–0,35 no alcanza +2 pp con IC > 0.
  - *No concluyente:* el control `cp_silueta_severa` no alcanza +2 pp con IC que excluya el cero.
- **Por qué ese tramo y no *heavy*:** es el tramo donde se observó el efecto en E4, y el estrato *heavy* (visibilidad 0,20–0,65) de E4 quedó bajo el umbral (+1,82 pp). Se fija ahora, antes de ver ningún resultado de H11. Es un tramo pequeño (n = 178 personas): el IC será ancho.
- **Compromiso de reporte.** Si H11 **no se confirma** o es no concluyente, el texto del artículo, el short paper y el PPI retira «dentro del dominio el aumento las ayudó algo» y reporta que la ganancia de E4 no se confirmó con exposición igual. Si **se confirma**, se reporta como un resultado confirmatorio **acotado a CityPersons y a 2 semillas**, sin ampliarlo a otros conjuntos.
- **Descriptivo, sin criterio** (no decide H11):
  - tramos 0,35–0,50 y 0,50–0,65, estratos *bare/partial/heavy* de la convención, AP@0.5:0.95;
  - **transferencia:** V3 − V1 en NightOwls ocluida y en el proxy de ExDark severa; se dirá «no se transfiere» solo si ninguno alcanza +2 pp con IC > 0;
  - V3 − V1 de las 5 semillas {0–4} juntas, **con la advertencia de que las semillas 0–2 tienen exposición desigual**.
- **Análisis de sensibilidad declarados ahora:** IC jerárquico (con solo 2 semillas es indicativo, no concluyente), tasa de pérdida (`24_`) y AP@0.5:0.95 (`27_`). El veredicto se decide solo con el IC por imágenes.

## 3. Diseño

| Elemento | Definición |
|---|---|
| Modelo, hiperparámetros, aumento base | Idénticos a H6 (`yolo11s.pt`, `config/hiperparametros.yaml`, `config/aumento_base.yaml`). Única excepción: épocas y paciencia |
| Épocas | **60 fijas** (`--epochs 60 --patience 0`; en Ultralytics, paciencia 0 desactiva la parada temprana), con el calendario completo de tasa de aprendizaje |
| Por qué 60 | Se fija por presupuesto y por cercanía a las épocas en que la parada temprana detuvo a V1 en H6 (58–71), antes de ver ningún resultado. 100 épocas costarían ≈ 15 h; 60, ≈ 9 h. **Pendiente de confirmar al congelar** |
| Pesos evaluados | `last.pt` (época 60). `best.pt` se guarda pero **no** se usa para el criterio |
| Datos y partición | Los de H6, sin cambios: CityPersons *train* (2 675) y *val_interno* (300), semilla de partición 0, `dataset/data_citypersons.yaml`, banco de siluetas `siluetas_cp_train`. No se genera nada nuevo |
| Validación | La mixta de H6; solo se registra (curvas), no selecciona nada |
| Variantes y semillas | **V1** y **V3** (siluetas), semillas **{3, 4}**: **4 corridas** en `runs/argos_cp_fijo/`. Orden por pares: V1_s3, V3_s3, V1_s4, V3_s4 |
| Comando (indicativo) | `07_entrenar.py --protocolo cp --variantes V1 V3 --semillas 3 4 --epochs 60 --patience 0 --proyecto argos_cp_fijo --workers 4` |
| Evaluación | `09_evaluar_estratificado.py --corridas runs/argos_cp_fijo --pesos-tipo last --resultados resultados_h11 --gt` sobre `cp_silueta_severa` (control), `gt_citypersons_convencion.json`, `gt_nightowls.json` y `gt_test_proxy.json` |
| Contrastes | `11_` (V3 − V1 por conjunto y estrato; bootstrap pareado por imágenes, 1 000 réplicas, semilla 0) y `27_` para los tramos de visibilidad |
| Veredicto | `29_veredicto_h11.py` (**por escribir, con autotest, antes de congelar**) aplica la regla literal de esta sección y escribe `informes/veredicto_h11.md` |
| Costo estimado | 4 corridas × 60 épocas × ≈ 2,2 min/época (medido en H6: 18,1 h / 494 épocas) ≈ **9 h** de GPU + ≈ 0,5 h de evaluación y análisis |

## 4. Lo que NO se hará

- No se cambiarán épocas, paciencia, hiperparámetros, datos, banco de siluetas ni semillas tras ver ninguna corrida.
- No se usará `best.pt` para el criterio ni se elegirá otra época, otro tramo o otro estrato a posteriori.
- No se añadirán semillas, y no se reutilizarán las corridas de H6 en el criterio.
- No se cambiará el veredicto de H6, que sigue siendo el pre-registrado.

## 5. Orden de ejecución

1. Escribir `29_veredicto_h11.py` con autotest y comprobar que `27_` y `11_` admiten la carpeta `resultados_h11/` (solo scripts de informe).
2. Decidir 60 frente a 100 épocas y confirmar que la GPU está libre unas 10 h.
3. **Congelar v3.6** (`08_congelar_protocolo.py`): este documento (con el estado cambiado a «CONGELADO») y los scripts; anotar fecha y huella en `CAMBIOS_PROTOCOLO.md`. **No empezar a entrenar antes.**
4. Las 4 corridas en el orden de la sección 3.
5. Evaluación, contrastes, veredicto y `informes/reporte_h11.md` con el veredicto literal.
6. Solo después, actualizar el short paper, el artículo, el PPI y el informe general con el resultado, sea cual sea.

## 6. Pendiente antes de congelar

- [ ] Confirmar 60 épocas (o cambiar a 100) y la ventana de GPU.
- [ ] Escribir y probar `29_veredicto_h11.py`.
- [ ] Revisar que `cp_silueta_severa` exista en `dataset/` con el banco de siluetas de H6.
- [ ] Cambiar el estado a «CONGELADO», fechar y anotar la huella SHA-256.
