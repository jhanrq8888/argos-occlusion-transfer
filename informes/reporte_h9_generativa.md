# ARGOS-11 — Informe de H9: tercera familia de oclusor (oclusión generativa)

3 de octubre de 2026. Pre-registro: `PREREGISTRO_H9.md` (sha256 `6bc81595…`, 2 de octubre, antes de generar datos, entrenar o evaluar). Protocolo de entrenamiento v3.3b; v3.3c y v3.3d solo cambian scripts de informe. Registro completo en `CAMBIOS_PROTOCOLO.md`.

## 1. Qué se probó

Las dos familias anteriores componen el oclusor a partir de algo artificial: un rectángulo (parches, experimento 1) o un recorte con máscara pegado con mezcla alfa (siluetas, iteración 2 y H6–H8). La objeción más previsible era que el déficit de transferencia se deba a que esos oclusores no son realistas. La H9 prueba la forma más realista de fabricar oclusión disponible hoy: **un modelo de difusión (Stable Diffusion 1.5 *inpainting*) pinta un objeto** (auto, bicicleta, motocicleta, banca, maceta, hidrante, maleta, paraguas, silla o camión) dentro de una máscara anclada a un borde de la persona, con la luz, la textura y la perspectiva de la escena y sin bordes de pegado.

- **Detector y datos:** YOLOv11s, ExDark-People train, validación mixta: idénticos a la iteración 2.
- **Línea base:** las V1′ de la iteración 2 (mismas semillas y código), reutilizadas. Solo se entrenaron las 3 corridas V3ᵍ.
- **Generación previa:** dos versiones ocluidas de cada imagen de entrenamiento. El dataset sustituye la imagen leída por una de ellas con probabilidad 0,15 por imagen con mosaico (≈ 0,48 por muestra de 4 imágenes, como el p = 0,5 de las familias 1 y 2) y 0,5 sin mosaico.
- **Control de calidad automático:** un segmentador COCO descarta los casos en que la difusión vuelve a dibujar a la persona (más del 30 % de la máscara sigue siendo persona) y se reintenta hasta 2 veces. La cobertura efectiva descuenta lo que sigue siendo persona.

![Ejemplos del control generativa_severa](figuras/h9_ejemplos_generativa.png)

*Personas de ExDark test antes (izquierda) y después (derecha) de la oclusión generativa. Etiqueta: objeto pedido y cobertura efectiva.*

## 2. Calidad del generador

| | Entrenamiento (2 versiones) | Control `generativa_severa` |
|---|---|---|
| Imágenes | 1 162 de 1 183 con versión ocluida | 841 |
| Oclusiones aceptadas por el control de calidad | 2 989 / 3 487 (**85,7 %**) | 2 150 / 2 235 (**96,2 %**) |
| Intentos medios por persona | 1,56 | 1,20 |
| Estratos efectivos | — | severa 2 018 · moderada 153 · ligera 23 · sin 41 |
| Imágenes con una persona nueva dibujada por la difusión (sin etiquetar) | 4,5 % (105 personas en 2 174 versiones) | 4,5 % (50 personas) |

El criterio de «no concluyente» por fallo del generador (menos del 50 % aceptado) no se activa. Las personas nuevas dibujadas pese al *prompt* negativo son una limitación declarada; su frecuencia es baja (`informes/h9_personas_alucinadas.json`).

Costo: generación ~5,7 h de GPU; entrenamiento 1,2 h (22, 22 y 21 épocas; la mejor época según la validación mixta fue la 2 en las tres corridas).

## 3. Resultado (criterio pre-registrado)

V3ᵍ − V1′, AP@0.5, media de 3 semillas, IC 95 % por bootstrap pareado sobre imágenes (1 000 réplicas):

| Conjunto | V1′ | V3ᵍ | Δ (pp) | IC 95 % | ≥ +2 pp con IC > 0 |
|---|---|---|---|---|---|
| **Control `generativa_severa`** (n = 2 018) | 0,018 | 0,044 | **+2,60** | [+2,12; +3,09] | **sí** |
| `silueta_severa` (descriptivo) | 0,041 | 0,040 | −0,10 | [−0,39; +0,20] | no |
| NightOwls ocluida (n = 530) | 0,306 | 0,287 | −1,93 | [−2,89; −0,88] | no |
| CityPersons *heavy* (n = 733) | 0,153 | 0,165 | +1,23 | [+0,36; +2,11] | no |
| ExDark proxy severa (n = 101) | 0,244 | 0,272 | **+2,82** | [+0,37; +5,99] | **sí** |

**Veredicto literal: H9 SOSTENIDA.** El aumento se aprendió (control ≥ +2 pp con IC > 0) y solo **1 de las 3 fuentes reales** supera el umbral; la regla exigía 2 para refutarla.

**Matiz que se reporta sin reformular la hipótesis:** la celda de ExDark proxy severa es **la primera medición sobre oclusión real del proyecto que supera +2 pp con el IC por imágenes** (1 de 21 en los siete bloques). No es robusta:
- **Por semilla:** +4,7, +4,5 y −0,8 pp; la tercera semilla tampoco aprendió el control (0,020 frente a 0,022).
- **Con el IC jerárquico** (semillas + imágenes, 2 000 réplicas): [−1,23; +7,40], que incluye el cero.
- **Es la fuente más pequeña** (101 personas) y su oclusión es solo entre personas, mientras que el oclusor generativo es siempre un objeto.

## 4. Análisis de sensibilidad declarados

| Conjunto | IC jerárquico (AP@0.5) | Tasa de pérdida MR⁻² V3ᵍ − V1′ (IC imágenes; jerárquico) |
|---|---|---|
| Control `generativa_severa` | [+0,25; +4,33] | −1,17 [−1,43; −0,93]; [−2,13; +0,16] |
| NightOwls ocluida | [−3,87; −0,12] | **+1,38** [+0,78; +2,30]: empeora |
| CityPersons *heavy* | [−1,70; +4,03] | −0,89 [−1,58; −0,30]; [−2,64; +0,83] |
| ExDark proxy severa | [−1,23; +7,40] | −3,24 [−5,18; −0,53]; [−6,43; +1,00] |

Ningún veredicto cambia. En los siete bloques, con el IC jerárquico, **0 de 21** mediciones reales superan el umbral.

**Mecanismo** (NightOwls, 530 peatones ocluidos, confianza ≥ 0,25): el recall baja de 0,387 a 0,352 y los falsos positivos por imagen de 0,215 a 0,176. Es el mismo patrón conservador de las siluetas: menos detecciones, no mejores. En CityPersons *heavy* el recall apenas cambia (0,178 → 0,181) y en ExDark proxy sube (0,548 → 0,574).

## 5. Análisis exploratorio (post hoc, declarado; no cambia el veredicto)

Como la regla pre-registrada eligió la época 2 en las tres corridas, el aumento apenas se entrenó. Se evaluaron también los pesos finales (`last.pt`, épocas 21–22) de V1′ y V3ᵍ (`resultados_h9_last/`):

| Conjunto | V1′ | V3ᵍ | Δ (pp) | IC 95 % |
|---|---|---|---|---|
| Control `generativa_severa` | 0,024 | 0,106 | **+8,25** | [+7,24; +9,46] |
| NightOwls ocluida | 0,136 | 0,128 | −0,81 | [−1,90; +0,45] |
| CityPersons *heavy* | 0,086 | 0,081 | −0,50 | [−1,36; +0,34] |
| ExDark proxy severa | 0,181 | 0,192 | +1,07 | [−3,43; +5,28] |

Con más exposición, el aumento generativo se aprende mucho mejor (+8,25 frente a +2,60) y **la oclusión real no mejora en ninguna fuente**. Es el patrón de las familias 1 y 2: cuanto más se aprende el oclusor sintético, más clara es la brecha. Además, entrenar más tiempo sobre ExDark empeora mucho a ambos modelos fuera de ExDark (NightOwls ocluida 0,306 → 0,136 en V1′): es el sobreajuste de dominio ya documentado.

## 6. Conclusión

La tercera familia, la más realista, repite el resultado de las otras dos: **el aumento se aprende y no se transfiere de forma robusta a la oclusión real**. Deja un único indicio positivo (ExDark proxy, la fuente más pequeña), que no resiste la variación entre semillas, no se repite en NightOwls (donde empeora) ni en CityPersons, y desaparece cuando el aumento se entrena más. El realismo del oclusor no cierra la brecha.

## 7. Ficheros

| Qué | Dónde |
|---|---|
| Pre-registro | `PREREGISTRO_H9.md` |
| Generador | `argos_lib/generativa.py`, `25_oclusion_generativa.py` |
| Datos generados | `dataset/generativa_train/` (índice y registros), `dataset/test_sintetico/generativa_severa/` |
| Corridas | `runs/argos_gen/V3_s{0,1,2}` (V1′: `runs/argos_v2/V1_s{0,1,2}`) |
| Evaluación y bootstrap | `resultados_h9/` (primario), `resultados_h9_last/` (exploratorio) |
| Jerárquico y tasa de pérdida | `informes/analisis_final/bootstrap_jerarquico.csv`, `miss_rate.csv` |
| Calidad del generador | `informes/h9_personas_alucinadas.json`, `informes/figuras/h9_ejemplos_generativa.png` |
| Veredictos H1–H9 | `informes/veredictos_H1_H7.md` |
