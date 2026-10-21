# ARGOS-11 — Informe de H9b (E7b): oclusión generativa con exposición fija

Fecha: 2026-10-06. Pre-registro: `PREREGISTRO_H9b.md` (sha256 `e6a349f1…`), congelado como **v3.4** (hash global `51786d9d411cbbbb`) antes de la primera época. Sin cambios de protocolo durante la ejecución.

## 1. Qué se hizo

- **Entrenamiento:** 6 corridas de YOLOv11s en `runs/argos_gen_fijo/`: V1 (sin aumento) y V3ᵍ (aumento generativo), semillas 0, 1 y 2.
  - Las 6 corridas completaron **exactamente 30 épocas**, sin parada temprana y con el calendario completo de tasa de aprendizaje.
  - Usaron los mismos datos generados de H9.
  - Duración: 34–38 min por corrida, **3,56 h de GPU** en total (06/10, 09:02 → 12:36), sin incidentes.
- **Evaluación:** con los pesos de la época 30 (`last.pt`) en los 5 conjuntos de H9 (`resultados_h9b/`).
- **Análisis:** bootstrap pareado por imágenes de 1 000 réplicas (`11_`). Los análisis de sensibilidad declarados están en `informes/analisis_final/*_secundarios.csv`.
- **Veredicto:** lo escribe `26_veredicto_h9b.py` en `informes/veredicto_h9b.md`.

## 2. Veredicto literal

| Celda | V3ᵍ − V1 (AP@0.5, pp) | IC 95 % por imágenes | IC jerárquico | Por semilla |
|---|---|---|---|---|
| Control `generativa_severa` | **+15,23** | [+14,00; +17,16] | [+13,81; +17,45] | +15,4 / +15,2 / +15,1 |
| NightOwls ocluida | +0,01 | [−1,02; +1,20] | [−1,60; +1,82] | −0,7 / +1,5 / −0,8 |
| CityPersons *heavy* | +1,52 | [+0,79; +2,66] | [−0,02; +3,39] | +2,8 / +1,5 / +0,3 |
| ExDark proxy severa | −3,03 | [−6,77; +0,99] | [−8,85; +2,89] | +1,7 / −3,3 / −7,5 |

Para refutar H9b hacían falta al menos 2 fuentes reales con mejora relevante; hubo **0 de 3**. El control supera +2 pp con IC > 0, así que el aumento se aprendió y el resultado no es «no concluyente». **H9b: SOSTENIDA.**

**Análisis de sensibilidad declarados:**
- **Equivalencia:** 2 de 3 fuentes reales tienen un IC por imágenes que descarta una mejora de +2 pp (NightOwls y ExDark). CityPersons no la descarta: su límite superior es +2,66.
- **IC jerárquico:** ninguna celda real excluye el cero.
- **Tasa de pérdida (MR-2, menor es mejor):**
  - control −6,32 pp [−7,37; −5,46];
  - NightOwls −0,24 [−1,18; +0,77];
  - CityPersons *heavy* −1,19 [−1,86; −0,59], jerárquico [−2,45; −0,02];
  - ExDark +2,89 [−0,33; +6,29].
  
  Ninguna mejora relevante (≤ −2 pp con IC < 0) y ninguna fuente empeora con IC > 0.

## 3. Lectura

1. **Con exposición completa, el aumento generativo se aprende mucho mejor.**
   - El control pasa de +2,60 pp (H9, época 2) a **+15,23 pp**, por encima de las siluetas (+10,63) y estable entre semillas (15,1–15,4).
   - Esto responde la objeción de las revisiones: ahora no se puede decir que la familia generativa no se aprendió.
2. **La oclusión real sigue sin mejorar.**
   - NightOwls queda en cero.
   - CityPersons *heavy* mejora un poco (+1,5 pp), por debajo del umbral y sin resistir el IC jerárquico.
   - ExDark empeora (−3,0 pp).
3. **La única celda positiva del estudio desaparece.** La celda ExDark proxy de H9 (+2,82 pp, la única medición real que superaba el umbral con el IC por imágenes) pasa a **−3,03 pp** con exposición completa. Era frágil, como ya indicaba su IC jerárquico.
4. **La pequeña ganancia en CityPersons no es específica de la oclusión.** En el mismo conjunto, el aumento mejora más a las personas **sin oclusión** (*bare*: 0,473 → 0,526, **+5,2 pp**) que a las muy ocluidas (*heavy*: +1,5 pp). Parece un efecto general de regularización o de dominio, no robustez frente a la oclusión. *(Descriptivo, sin criterio.)*
5. **El entrenamiento largo agrava el sobreajuste al dominio. Es la advertencia principal.**
   - Con 30 épocas, la V1 cae fuera de ExDark: NightOwls ocluida 0,169, frente a 0,306 de la V1′ de H9 en la época 2; CityPersons *heavy* 0,081 frente a 0,153.
   - V3ᵍ cae igual (0,169 y 0,096).
   - El contraste V3ᵍ − V1 se hace, por tanto, entre dos modelos más sobreajustados a ExDark. Sigue siendo la comparación pre-registrada, con la misma exposición para ambos, pero el AP absoluto fuera del dominio es bajo. Hay que decirlo al reportarlo.
6. **Descriptivo:** sobre `silueta_severa` el aumento generativo apenas mejora (+0,40 pp [−0,01; +0,88]). Lo aprendido con oclusores pintados no se transfiere ni siquiera a la otra familia sintética.

## 4. Consecuencias para el artículo y el short paper

- Desaparece la objeción principal de las revisiones (M1/DA-1, objeción 1 de la revisión simulada): con exposición fija y completa, la familia generativa se aprende con fuerza (+15,2 pp) y sigue sin transferirse.
- Se elimina la única celda positiva del estudio.
- **Totales con E7b:** 65 corridas y 82,8 h de GPU. E7b se reporta como réplica pre-registrada de E7, aparte del recuento de las 21 mediciones de E1–E7, que no cambia.
- **Advertencia que hay que añadir:** el entrenamiento de 30 épocas aumenta el sobreajuste al dominio de ExDark.
