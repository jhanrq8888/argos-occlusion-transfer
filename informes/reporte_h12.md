# ARGOS-11 — Informe de H12 (E10: YOLOv11m) y de la extensión de semillas de E7b y E8

Fecha: 2026-10-17.
- **Pre-registro:** `PREREGISTRO_H12.md`, congelado como v3.7 y enmendado como **v3.7b** antes de completar ninguna corrida (la extensión pasó de la laptop a RunPod).
- **Veredicto literal:** `informes/veredicto_h12.md`.
- **Datos:** `resultados_h12/analisis/contrastes_h12.{csv,json}`.

## 1. Qué se hizo

- **Entrenamiento:** 15 corridas en RunPod (RTX 4090), todas con 30 épocas fijas, sin parada temprana y evaluadas con `last.pt`. Pesos descargados con SHA-256 verificado.
  - **E10:** YOLOv11m, V1, V3ˢⁱˡ y V3ᵍᵉⁿ, semillas 0–2. Unos 7–8 min por corrida.
  - **Extensión:** YOLOv11s, V1, V3ᵍᵉⁿ y V3ˢⁱˡ, semillas 3 y 4.
- **Evaluación:** en la laptop, sobre los dos controles y las tres fuentes reales.
- **Análisis:** `30_h12.py` (autotest 11/11), con IC por imágenes (1 000 réplicas, criterio) y jerárquico (2 000).

## 2. Veredictos (AP@0.5, V3 − V1 en pp)

| Celda | H12a: YOLOv11m, siluetas | H12b: YOLOv11m, generativa |
|---|---|---|
| Control | **+14,45** [+12,76; +16,37] | **+19,04** [+17,49; +21,03] |
| NightOwls ocluida | −0,39 [−1,55; +0,89] | +0,78 [−0,42; +2,16] |
| CityPersons *heavy* | +0,25 [−0,63; +1,27] | +1,11 [+0,14; +2,16] |
| ExDark proxy severa | +3,04 [−1,07; +6,63] | −0,56 [−4,07; +3,19] |

- **H12a: SOSTENIDA (0 de 3).**
- **H12b: SOSTENIDA (0 de 3).**
- Con un detector más grande, el aumento se aprende **más** que con YOLOv11s: los controles suben +14,45 y +19,04, frente a +10,99 y +15,23. Aun así **no se transfiere**. La objeción «un solo tamaño de modelo» queda respondida para la familia YOLO.

## 3. Extensión de semillas (análisis secundario; no cambia H9b ni H10)

| Celda | E7b, 5 semillas | E8 siluetas, 5 semillas |
|---|---|---|
| Control | +15,10 [+13,76; +16,76] | +11,00 [+9,66; +12,59] |
| NightOwls ocluida | −0,45 [−1,28; +0,60] | −1,06 [−1,89; −0,03] |
| CityPersons *heavy* | +0,22 [−0,37; +1,02] | **+2,06** [+1,40; +2,99]; jerárquico **[+0,26; +4,17]** |
| ExDark proxy severa | −1,75 [−4,79; +1,83] | −2,06 [−5,37; +0,97] |

- **E7b:** la conclusión se mantiene con 5 semillas. La pequeña ganancia en CityPersons baja de +1,52 (3 semillas) a +0,22.
- **E8, siluetas con 30 épocas fijas, CityPersons *heavy*:** con 5 semillas supera +2 pp **también con el IC jerárquico**. Según la lectura fijada en el pre-registro, **se reporta como un resultado que contradice la conclusión con 3 semillas** para esa celda: con exposición fija, las siluetas entrenadas en ExDark mejoran de forma robusta CityPersons *heavy*.
  - Matiz descriptivo: con las mismas 5 semillas, la mejora es mayor en las personas **sin oclusión** (*bare* +4,27 [+3,07; +5,65]) y **parcialmente ocluidas** (*partial* +4,16 [+3,19; +5,24]) que en las muy ocluidas (+2,06).
  - Es una mejora general del detector en CityPersons, no un efecto propio de la oclusión. Así se había visto ya en H10 con 3 semillas.
  - Sigue siendo **1 fuente de 3**: NightOwls empeora (−1,06, IC < 0) y ExDark no mejora.
- **Solo semillas 3–4 (entrenadas en RunPod):** 0 de 3 fuentes superan +2 pp, con ninguno de los dos IC. El patrón coincide con el de las semillas 0–2; el cambio de máquina no altera la lectura.

## 4. Consecuencias para el artículo

- La conclusión general se mantiene y se amplía: **dos tamaños de YOLO** (s y m) y **5 semillas** en los bloques con exposición fija.
- Hay que reportar con honestidad la celda de CityPersons de las siluetas con exposición fija: es robusta a la variación entre semillas, pero no es propia de la oclusión y no aparece en las otras dos fuentes.
- Con esta celda, la frase «ninguna celda resiste el IC jerárquico» deja de valer para el bloque de 5 semillas. Hay que matizarla.
