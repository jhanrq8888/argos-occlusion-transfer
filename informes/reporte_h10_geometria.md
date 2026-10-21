# ARGOS-11 — Informe de H10 (E8): la geometría de la oclusión real

Fecha: 2026-10-07. Pre-registro: `PREREGISTRO_H10.md` (sha256 `cad91a0c…`), congelado como **v3.5** (`1489961a`) antes de la primera época. Los congelamientos v3.5b y v3.5c solo tocan el script de informe `27_`. No hubo cambios de protocolo durante la ejecución.

## 1. Qué se hizo

- **Entrenamiento:** 6 corridas de YOLOv11s con 30 épocas fijas, sin parada temprana. Duraron 36,7–39,4 min cada una, unas 3,6 h de GPU en total según `results.csv` (cada corrida duró 36,7–39,4 min de tiempo de pared), del 07/10 a las 05:04 hasta las 08:53, sin incidentes.
  - **V3ᴳ** (`runs/argos_geo/`): los recortes de las siluetas v2, colocados sobre la región que queda oculta en patrones reales de CityPersons train.
  - **V3ˢ** (`runs/argos_sil_fijo/`): las siluetas v2 sin cambios.
  - **Base:** la V1 de H9b, reutilizada. Sus valores coinciden exactamente con los de H9b (NightOwls 0,1685; CityPersons 0,0805; ExDark 0,2568).
- **Evaluación:** pesos de la época 30 en 5 conjuntos (`resultados_h10/`).
- **Contrastes:** bootstrap por imágenes de 1 000 réplicas y jerárquico de 2 000. El veredicto literal lo escribe `28_geometria.py analisis` en `informes/veredicto_h10.md`.

## 2. Veredicto literal (AP@0.5, pp; IC por imágenes; entre paréntesis, el jerárquico)

| Celda | V3ᴳ − V1 | V3ˢ − V1 | V3ᴳ − V3ˢ |
|---|---|---|---|
| Control `geometria_severa` | **+18,39** [+15,61; +21,30] | +15,84 [+13,52; +18,63] | +2,55 [+1,07; +3,93] |
| Control `silueta_severa` (descriptivo) | +6,27 [+5,24; +7,47] | +10,99 [+9,62; +12,62] | −4,72 [−5,51; −4,01] |
| NightOwls ocluida | −2,05 [−3,26; −0,92] ([−4,62; +0,29]) | −1,12 [−2,13; +0,08] | −0,93 [−1,93; −0,18] |
| CityPersons *heavy* | **+2,37 [+1,52; +3,52]** ([+0,63; +4,61]) | +2,26 [+1,44; +3,47] | +0,10 [−0,77; +1,13] |
| ExDark proxy severa | −4,88 [−9,08; −0,82] ([−11,58; +1,03]) | −3,50 [−7,64; +0,08] | −1,38 [−3,79; +1,43] |

- **H10:** 1 de 3 fuentes reales supera +2 pp con IC > 0, y la regla exige 2. El control se aprendió. **H10: SOSTENIDA.**
- **Contraste secundario pre-registrado (efecto de la geometría, V3ᴳ − V3ˢ):** 0 de 3. **La geometría real no mejora la transferencia.**

## 3. Lectura

1. **La geometría se aprende, pero no se transfiere.**
   - V3ᴳ supera a las siluetas en su propio control (+2,55) y pierde en el de las siluetas (−4,72): cada modelo aprende la oclusión con la que se entrenó.
   - En la oclusión real, la geometría no aporta nada frente a las siluetas: −0,93 en NightOwls, +0,10 en CityPersons y −1,38 en ExDark.
2. **La celda de CityPersons *heavy* que supera el umbral no es un efecto de la oclusión.** Datos descriptivos:
   - con la misma exposición, las siluetas sin cambios dan casi lo mismo (+2,26);
   - en CityPersons mejoran más las personas **sin oclusión** (*bare*: +5,25 con V3ᴳ, +5,97 con V3ˢ) y con oclusión parcial (+5,45) que las muy ocluidas (+2,37).

   Es una mejora general del detector en ese dominio, como la que ya se vio en H9b (*bare* +5,2) y en la curva por visibilidad (`5.3`). Además, CityPersons es la fuente cuya geometría coincide con la de los patrones de entrenamiento, como se declaró en el pre-registro.
3. **En las fuentes que no comparten la geometría, el aumento con geometría real empeora:** NightOwls −2,05 y ExDark −4,88, ambos con IC por imágenes por debajo de cero.
4. **Hallazgo sobre E2, descriptivo:** con la misma exposición que V1 (30 épocas), las siluetas sin cambios dañan mucho menos que en E2: −1,12 en NightOwls, frente a −16,79 en E2. Esto apoya lo que el artículo ya planteaba como posibilidad: la regla de selección con validación mixta dejaba entrenar mucho más a V3 que a V1, y eso **inflaba el tamaño del daño**. Lo que no cambia es la ausencia de mejora robusta en la oclusión real.

## 4. Consecuencias para el artículo y el short paper

- **La explicación de la geometría queda contrastada y descartada como causa principal.** Con apariencia real (E2), apariencia de escena (E7 y E7b) o geometría real (E8), el aumento se aprende y no mejora la detección de personas realmente ocluidas fuera del dominio donde se generó.
- **Con la curva por visibilidad, el mecanismo queda así:** el aumento mueve al detector en general, y más sobre las personas casi visibles, pero no sobre las muy ocluidas (con entrenamiento en ExDark; con entrenamiento en CityPersons, E4, el efecto se concentra en las más ocluidas).
- **Hay que matizar el tamaño del daño de E2–E6.** Parte se debe a la regla de selección (punto 3.4). La conclusión principal no cambia.
- **Totales con E7b y E8:** 71 corridas y unas 86,4 h de GPU. E8 se reporta como experimento pre-registrado propio (H10), aparte del recuento de las 21 mediciones de E1–E7.
