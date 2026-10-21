# ARGOS-11 — H6: réplica de entrenamiento sobre CityPersons

Corte: 20 de septiembre de 2026, 11:34. Protocolo v3.0 (`e971ab8b…`, congelado el 19/09 a las 16:48, antes de la primera corrida); pre-registro `PREREGISTRO_H6_H7.md` (sha256 `4b4b56a1…`, con la errata de *heavy* corregida antes de convertir datos). Fuentes: `resultados_h6/{resumen_ap.csv, analisis/bootstrap.csv, analisis/descriptivo.csv, analisis/diagnostico_transferencia.csv}`.

## 1. Qué se entrenó

6 corridas YOLOv11s (COCO) sobre **CityPersons train, partición interna de 2 675 imágenes** (18 ciudades; 19 199 personas etiquetadas: pedestrian, rider, sitting, other, h ≥ 20 px), validación mixta de 300 imágenes internas + 300 copias ocluidas con siluetas del banco `cp_val`, hiperparámetros congelados (SGD, lr0 0,002, 100 épocas, paciencia 20, batch 16, imgsz 640). V1 = base; V3 = aumento de siluetas v2 con banco `siluetas_cp_train` (800 personas / 800 objetos). Semillas {0,1,2}. Evaluación sobre las 500 imágenes de CityPersons *val* (ciudades disjuntas de *train*).

| Corrida | Épocas | Corrida | Épocas |
|---|---|---|---|
| V1_s0 | 58 | V3_s0 | 100 |
| V1_s1 | 65 | V3_s1 | 100 |
| V1_s2 | 71 | V3_s2 | 100 |

Tiempo de GPU registrado: 18.3 h. Sin incidentes.

## 2. Resultados: V3 − V1 (AP@0.5, media de 3 semillas; IC 95 % bootstrap por imágenes, 1 000 réplicas, pareado)

| Conjunto / estrato (n) | V1 | V3 | Δ V3 − V1 (pp) | IC 95 % | Excluye 0 |
|---|---|---|---|---|---|
| CityPersons convención, *heavy* (vis 20–65 %) — **primario** (733) | 0.583 ± 0.019 | 0.601 ± 0.006 | +1.82 | [+0.31; +3.31] | sí |
| CityPersons convención, *partial* (65–90 %) (810) | 0.848 ± 0.003 | 0.851 ± 0.006 | +0.37 | [−0.51; +1.28] | no |
| CityPersons convención, *bare* (≥ 90 %) (769) | 0.900 ± 0.002 | 0.904 ± 0.003 | +0.41 | [−0.32; +1.05] | no |
| CityPersons convención, global (2312) | 0.796 ± 0.005 | 0.802 ± 0.004 | +0.63 | [+0.02; +1.25] | sí |
| CityPersons estratos propios, moderada (926) | 0.527 ± 0.013 | 0.543 ± 0.011 | +1.52 | [+0.39; +2.63] | sí |
| CityPersons estratos propios, severa (397) | 0.263 ± 0.006 | 0.288 ± 0.008 | +2.51 | [−0.01; +5.08] | no |
| Control sintético cp_silueta_ligera (649) | 0.850 ± 0.000 | 0.880 ± 0.004 | +2.99 | [+1.67; +4.52] | sí |
| Control sintético cp_silueta_moderada (629) | 0.663 ± 0.001 | 0.817 ± 0.011 | +15.38 | [+12.93; +17.97] | sí |
| Control sintético cp_silueta_severa — **control** (684) | 0.100 ± 0.006 | 0.337 ± 0.014 | +23.74 | [+21.09; +26.51] | sí |
| Cruzado: NightOwls ocluida (530) | 0.163 ± 0.006 | 0.149 ± 0.010 | −1.35 | [−2.85; +0.20] | no |
| Cruzado: NightOwls sin oclusión (2763) | 0.519 ± 0.029 | 0.466 ± 0.024 | −5.27 | [−6.07; −4.52] | sí |
| Cruzado: ExDark inter-persona severa (101) | 0.094 ± 0.021 | 0.103 ± 0.018 | +0.94 | [−2.53; +4.72] | no |
| Cruzado: ExDark inter-persona moderada (190) | 0.258 ± 0.007 | 0.240 ± 0.014 | −1.83 | [−5.05; +1.76] | no |

## 3. Veredicto literal de H6

**H6 (texto pre-registrado):** *El déficit de transferencia de H3 se replica al re-entrenar directamente sobre CityPersons: con oclusores de silueta construidos desde CityPersons train, el contraste V3−V1 (AP@0.5, media de 3 semillas) sobre CityPersons val en la convención oficial heavy (visibilidad 20–65 %) no alcanza +2 pp o su IC 95 % bootstrap incluye el cero, aun cuando el mismo contraste sobre el conjunto sintético cp_silueta_severa sea ≥ +2 pp con IC que excluya el cero.*

1. Control sintético: `cp_silueta_severa` +23.74 [+21.09; +26.51] → ≥ +2 pp con IC que excluye el cero. **El generador funciona en este dominio; el contraste real es informativo.**
2. Primario: *heavy* +1.82 [+0.31; +3.31]. **No alcanza +2 pp** → se cumple la condición de la hipótesis.
3. Condición de refutación (≥ +2 pp con IC que excluya el cero **y** misma dirección en *partial* con IC que excluya el cero): *partial* +0.37 [−0.51; +1.28] → **no se cumple**.

**Veredicto: H6 sostenida.** El déficit de transferencia se replica al re-entrenar en el dominio: +1.82 pp en oclusión real frente a +23.74 pp en la misma oclusión sintética (razón ≈ 13 : 1).

## 4. Matiz obligatorio (no reformula H6; se reporta como hallazgo)

Es la **primera vez en el proyecto que el efecto del aumento sobre oclusión real es positivo con IC que excluye el cero** (*heavy* +1.82 [+0.31; +3.31]; moderada propia +1.52 [+0.39; +2.63]; global +0.63 [+0.02; +1.25]). Al evaluar los modelos ajustados sobre ExDark sin re-entrenar, el mismo estrato daba −0,36 [−1,06; +0,31] (exp. 1) y −3,94 [−5,66; −2,41] (iteración 2). Lectura: el **cambio de dominio explica el signo negativo** observado antes (explicación A del pre-registro, parcialmente confirmada), pero **no explica la brecha**: entrenar en el dominio deja un efecto real pequeño (+1.82 pp, por debajo del umbral de relevancia de +2 pp fijado en el PPI) frente a +23.74 pp sintético. Los contrastes cruzados vuelven a ser nulos o negativos fuera del dominio (NightOwls ocluida −1.35 [−2.85; +0.20]; NightOwls sin oclusión −5.27 [−6.07; −4.52]).

El estrato *severa* propio (+2.51 [−0.01; +5.08], n = 397) roza el umbral y el cero por el lado opuesto: con la cuota de 50 satisfecha pero n moderado, no se puede afirmar ni descartar un efecto ≥ +2 pp en la oclusión más severa. Se deja explícito como límite de potencia, no como evidencia.

## 5. Mecanismo (diagnóstico a conf 0,25, media de 3 semillas)

| Conjunto / estrato | recall V1 → V3 | FP/imagen V1 → V3 | confianza media TP V1 → V3 |
|---|---|---|---|
| cp_silueta_severa, severa | 0.118 → 0.374 | 0.573 → 0.793 | 0.633 → 0.516 |
| CityPersons heavy | 0.584 → 0.610 | 0.768 → 0.905 | 0.631 → 0.643 |
| CityPersons bare | 0.884 → 0.889 | 0.823 → 0.945 | 0.754 → 0.766 |
| NightOwls ocluida | 0.333 → 0.252 | 1.163 → 0.729 | 0.621 → 0.659 |

En el dominio, V3 gana *recall* en *heavy* (+2,6 puntos) a costa de más falsos positivos por imagen (+18 %), también en *bare*; en el control sintético el *recall* se triplica. Fuera del dominio (NightOwls) V3 pierde *recall* y FP a la vez, como en la iteración 2.

## 6. Lo que H6 no responde

- Si el efecto pequeño positivo crece con más datos del dominio: eso es **H7** (escalera NightOwls, pre-registrada, pendiente de autorizar la descarga).
- Si el umbral de +2 pp es el adecuado para un efecto de este tamaño: el umbral es el del PPI (pre-registrado el 11/09) y no se cambia; se reporta el efecto con su IC para que el lector juzgue.
- Nada sobre CBAM: H6 solo compara V1 y V3, como se pre-registró.

Registrado en `CAMBIOS_PROTOCOLO.md` (20/09). Veredicto completo en `informes/veredictos_H1_H7.md`.

---

## Adenda (26/09/2026): análisis de sensibilidad con bootstrap jerárquico

Al remuestrear también las semillas (`23_bootstrap_jerarquico.py`, 2 000 réplicas; `informes/analisis_final/BOOTSTRAP_JERARQUICO.md`), el efecto primario en CityPersons *heavy* (+1,82 pp) pasa de [+0,31; +3,31] a **[−0,86; +4,42]**: deja de excluir el cero. Sus tres semillas dieron +2,37, +4,02 y −0,93 pp.

- **El veredicto no cambia:** H6 se sostenía si el efecto no alcanzaba +2 pp **o** su intervalo incluía el cero; ahora se cumplen las dos condiciones.
- **Se corrige la sección 4 (matiz):** ya no se puede afirmar que sea «el primer efecto real positivo con IC que excluye el cero». La lectura que sobrevive a los dos métodos es que, entrenando en el dominio, el efecto del aumento pasa de negativo a **nulo o levemente positivo**, y sigue muy por debajo del efecto sintético (+23,74 pp, que mantiene su intervalo jerárquico [+20,44; +27,22]).
