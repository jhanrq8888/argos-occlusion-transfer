# ARGOS-11 — Análisis de sensibilidad: bootstrap jerárquico (semillas + imágenes)

Corte: 27 de septiembre de 2026 (incluye H8, RT-DETR-l). Análisis **posterior y declarado** (no pre-registrado), registrado en `CAMBIOS_PROTOCOLO.md`. Script: `23_bootstrap_jerarquico.py` (con `--selftest`). Datos: `bootstrap_jerarquico.csv`.

## 1. Por qué se hace

Los intervalos del protocolo se calculan remuestreando **imágenes** y promediando siempre las mismas tres semillas. Responden a «¿cambiaría el resultado con otras imágenes de prueba?», pero no a «¿cambiaría si se volviera a entrenar?». Un revisor exigente puede objetarlo, sobre todo cuando las semillas varían mucho. El bootstrap jerárquico remuestrea **los dos niveles** en cada réplica: imágenes (pareadas entre variantes) y semillas (con reemplazo, de forma independiente para cada variante, porque V1 y V3 con la misma semilla son entrenamientos distintos). El AP de cada corrida se calcula con exactamente el mismo código; la única diferencia es el remuestreo de semillas. Procedimiento análogo al bootstrap estratificado sobre corridas de Agarwal et al. (2021).

Verificación: las 39 diferencias puntuales coinciden con las oficiales con error 0,00, y el autotest comprueba con un caso de respuesta conocida que el método recoge la variación entre semillas y solo esa. Se usaron 2 000 réplicas (semilla 0).

## 2. Resultado: efecto del aumento (V3 − V1)

| Bloque | Conjunto | V3 − V1 (pp) | IC por imágenes (pre-registrado) | IC jerárquico | Ensanchamiento | Estado con el jerárquico |
|---|---|---|---|---|---|---|
| Exp. 1 · parches · YOLOv11s | control: opaco severa | +60.92 | [+58.49; +63.41] | [+56.75; +64.95] | ×1.7 | excluye 0 |
| Exp. 1 · parches · YOLOv11s | NightOwls ocluidos | −3.17 | [−4.64; −1.85] | [−7.94; +2.10] | ×3.6 | **deja de excluir 0** |
| Exp. 1 · parches · YOLOv11s | CityPersons heavy | −0.36 | [−0.97; +0.30] | [−2.42; +1.62] | ×3.2 | incluye 0 |
| Exp. 1 · parches · YOLOv11s | ExDark severa (proxy) | −3.25 | [−5.92; −0.27] | [−7.11; +0.89] | ×1.4 | **deja de excluir 0** |
| Iter. 2 · siluetas · YOLOv11s | control: silueta severa | +10.63 | [+9.28; +12.12] | [+8.95; +12.50] | ×1.2 | excluye 0 |
| Iter. 2 · siluetas · YOLOv11s | NightOwls ocluidos | −16.79 | [−19.64; −13.90] | [−20.41; −12.96] | ×1.3 | excluye 0 |
| Iter. 2 · siluetas · YOLOv11s | CityPersons heavy | −3.94 | [−5.79; −2.36] | [−7.14; −1.02] | ×1.8 | excluye 0 |
| Iter. 2 · siluetas · YOLOv11s | ExDark severa (proxy) | −5.02 | [−10.50; +0.18] | [−11.89; +1.28] | ×1.2 | incluye 0 |
| Generalidad · siluetas · YOLO26s | control: silueta severa | +12.01 | [+10.48; +13.67] | [+10.32; +13.79] | ×1.1 | excluye 0 |
| Generalidad · siluetas · YOLO26s | NightOwls ocluidos | −14.31 | [−17.56; −10.94] | [−18.07; −10.14] | ×1.2 | excluye 0 |
| Generalidad · siluetas · YOLO26s | CityPersons heavy | −4.42 | [−6.07; −2.60] | [−6.89; −1.65] | ×1.5 | excluye 0 |
| Generalidad · siluetas · YOLO26s | ExDark severa (proxy) | −3.51 | [−8.53; +1.24] | [−9.48; +1.86] | ×1.2 | incluye 0 |
| H6 · entrenado en CityPersons | control: silueta severa (CP) | +23.74 | [+20.71; +26.74] | [+20.44; +27.22] | ×1.1 | excluye 0 |
| H6 · entrenado en CityPersons | NightOwls ocluidos | −1.35 | [−2.81; +0.12] | [−3.47; +0.68] | ×1.4 | incluye 0 |
| H6 · entrenado en CityPersons | CityPersons heavy | +1.82 | [+0.30; +3.29] | [−0.86; +4.42] | ×1.8 | **deja de excluir 0** |
| H6 · entrenado en CityPersons | ExDark severa (proxy) | +0.94 | [−2.58; +4.72] | [−4.06; +6.68] | ×1.5 | incluye 0 |
| H7 · entrenado en NightOwls 20k | NightOwls ocluidos | −1.43 | [−3.93; +0.87] | [−4.45; +1.56] | ×1.2 | incluye 0 |
| H7 · entrenado en NightOwls 20k | CityPersons heavy | −3.94 | [−5.72; −2.21] | [−8.15; +0.78] | ×2.5 | **deja de excluir 0** |
| H7 · entrenado en NightOwls 20k | ExDark severa (proxy) | −9.15 | [−14.32; −5.30] | [−17.22; −3.26] | ×1.6 | excluye 0 |
| H8 · siluetas · RT-DETR-l | control: silueta severa | +10.97 | [+9.61; +12.47] | [+9.32; +12.83] | ×1.2 | excluye 0 |
| H8 · siluetas · RT-DETR-l | NightOwls ocluidos | −6.98 | [−8.81; −4.99] | [−11.16; −2.81] | ×2.2 | excluye 0 |
| H8 · siluetas · RT-DETR-l | CityPersons heavy | −3.47 | [−4.96; −1.90] | [−6.27; −0.74] | ×1.8 | excluye 0 |
| H8 · siluetas · RT-DETR-l | ExDark severa (proxy) | −2.21 | [−5.86; +1.51] | [−7.61; +3.39] | ×1.5 | incluye 0 |

Ensanchamiento medio del intervalo: **×1.66** (entre ×1.1 y ×3.6). El mayor está en el experimento 1 sobre NightOwls (×3.6), el bloque cuyas semillas de V1 más variaron (0,214 / 0,283 / 0,286).

## 3. Lo que se mantiene

- **Los 5 controles sintéticos** siguen superando el umbral de +2 pp con intervalo jerárquico positivo (el más bajo: +8.95 pp). El aumento se aprendió, también contando la variación entre entrenamientos.
- **Ninguna de las 18 mediciones sobre oclusión real** supera el umbral (ni con el intervalo original ni con el jerárquico). La conclusión central no depende del método de intervalo.
- **El daño con siluetas es robusto:** en la iteración 2, en YOLO26s y en RT-DETR-l, el efecto en NightOwls (−16.79, −14.31 y −6.98 pp) y en CityPersons (−3.94, −4.42 y −3.47 pp) sigue siendo negativo con intervalo jerárquico que excluye el cero, en las tres arquitecturas.
- **Los ocho veredictos pre-registrados no cambian.** Ningún criterio de H1–H8 dependía de que un intervalo negativo excluyera el cero, y los que exigían «≥ +2 pp con intervalo que excluya el cero» siguen sin cumplirse.

## 4. Lo que se debilita (y se corrige en los informes)

- **Exp. 1 · parches · YOLOv11s, NightOwls ocluidos:** −3.17 pp pasa de [−4.64; −1.85] a [−7.94; +2.10].
- **Exp. 1 · parches · YOLOv11s, ExDark severa (proxy):** −3.25 pp pasa de [−5.92; −0.27] a [−7.11; +0.89].
- **H6 · entrenado en CityPersons, CityPersons heavy:** +1.82 pp pasa de [+0.30; +3.29] a [−0.86; +4.42].
- **H7 · entrenado en NightOwls 20k, CityPersons heavy:** −3.94 pp pasa de [−5.72; −2.21] a [−8.15; +0.78].

Consecuencias para lo que se puede afirmar:

1. **Parches (experimento 1):** ya no se puede afirmar que el aumento de parches *empeore* la detección real; solo que **no la mejora**. La afirmación de daño queda para las siluetas, donde sí es robusta.
2. **H6:** el +1,82 pp en CityPersons *heavy* deja de ser distinguible de cero cuando se incluye la variación entre semillas (sus tres semillas dieron +2,37, +4,02 y −0,93). H6 sigue sostenida, con más motivo; lo que ya no se puede decir es que sea «el primer efecto real positivo con IC que excluye el cero». La lectura correcta: entrenando en el dominio el efecto pasa a ser **nulo o levemente positivo**, en lugar de negativo.
3. **H7, CityPersons (cruzado):** el −3,94 pp deja de excluir el cero; era un contraste descriptivo.

## 5. CBAM (V2 − V1) y ARGOS-11 completo (V4 − V1) sobre oclusión real

| Bloque | Contraste | Conjunto | Δ (pp) | IC por imágenes | IC jerárquico | Estado |
|---|---|---|---|---|---|---|
| Exp. 1 · parches · YOLOv11s | V2−V1 | NightOwls ocluidos | −3.62 | [−4.99; −2.31] | [−8.84; +2.10] | **deja de excluir 0** |
| Exp. 1 · parches · YOLOv11s | V4−V1 | NightOwls ocluidos | −5.81 | [−7.43; −4.34] | [−11.14; −0.19] | excluye 0 |
| Exp. 1 · parches · YOLOv11s | V2−V1 | CityPersons heavy | −1.92 | [−2.87; −0.81] | [−4.42; +0.66] | **deja de excluir 0** |
| Exp. 1 · parches · YOLOv11s | V4−V1 | CityPersons heavy | −1.88 | [−2.88; −0.96] | [−4.94; +0.94] | **deja de excluir 0** |
| Exp. 1 · parches · YOLOv11s | V2−V1 | ExDark severa (proxy) | +1.18 | [−2.03; +4.65] | [−4.06; +6.20] | incluye 0 |
| Exp. 1 · parches · YOLOv11s | V4−V1 | ExDark severa (proxy) | −3.29 | [−6.57; −0.19] | [−10.41; +3.02] | **deja de excluir 0** |
| Iter. 2 · siluetas · YOLOv11s | V2−V1 | NightOwls ocluidos | −5.35 | [−6.88; −3.87] | [−7.86; −2.72] | excluye 0 |
| Iter. 2 · siluetas · YOLOv11s | V4−V1 | NightOwls ocluidos | −17.63 | [−20.32; −14.76] | [−22.75; −11.93] | excluye 0 |
| Iter. 2 · siluetas · YOLOv11s | V2−V1 | CityPersons heavy | −3.62 | [−4.87; −2.51] | [−7.13; −0.57] | excluye 0 |
| Iter. 2 · siluetas · YOLOv11s | V4−V1 | CityPersons heavy | −6.20 | [−7.95; −4.33] | [−9.36; −3.12] | excluye 0 |
| Iter. 2 · siluetas · YOLOv11s | V2−V1 | ExDark severa (proxy) | +0.72 | [−2.91; +4.49] | [−4.02; +6.08] | incluye 0 |
| Iter. 2 · siluetas · YOLOv11s | V4−V1 | ExDark severa (proxy) | −6.83 | [−12.37; −1.85] | [−13.39; −0.96] | excluye 0 |

El CBAM **no mejora** la oclusión real en ninguna celda con ningún método. Que la **empeore** solo se sostiene en la iteración 2 (NightOwls −5,35 y CityPersons −3,62 pp, con intervalo jerárquico que excluye el cero); en el experimento 1 el daño deja de ser distinguible de cero.

## 6. Cómo reportarlo en el artículo

- Presentar como **primarios** los intervalos pre-registrados (por imágenes), porque así lo fija el protocolo congelado, y el jerárquico como **análisis de sensibilidad** en la misma figura (trazo fino) y en una tabla suplementaria.
- Redactar las afirmaciones al nivel que sobrevive a ambos métodos: «el aumento no mejora la oclusión real» (robusto en todos los bloques) y «con siluetas la empeora» (robusto); no «con parches la empeora».
- Declarar la limitación: con tres semillas el remuestreo de semillas es grueso (10 combinaciones distintas por variante); el intervalo jerárquico es una aproximación conservadora. La extensión a cinco semillas, ya pre-registrada, lo afinaría.
