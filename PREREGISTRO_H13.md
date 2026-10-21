# ARGOS-11 — Pre-registro de H13: realismo medido de cada familia de oclusor

Redactado y congelado el **2026-10-17** (protocolo **v3.8**), **antes** de generar ninguna imagen o calcular ninguna característica con este diseño. No reformula ninguna hipótesis anterior.

## 0. Contexto (declarado)

- En el artículo, las familias de oclusor están ordenadas por realismo **por construcción**: parches < siluetas < generativa. Ese orden **no se midió**.
- La valoración externa del 13/10 lo señala como debilidad.
- **Ya se conocen los resultados de transferencia de todas las familias:** ninguna mejora la oclusión real de forma robusta. H13 no puede cambiarlos. Solo mide cuánto se parece cada familia a la oclusión real, para saber si «más realismo» se probó de verdad.

## 1. Diseño

Todo dentro de **CityPersons val**, el mismo dominio y las mismas cámaras, para que el clasificador no aprenda a distinguir conjuntos de datos en lugar de tipos de oclusión.

| Elemento | Definición |
|---|---|
| Oclusión real | 400 personas *heavy*: visibilidad anotada 0,20–0,65 y altura ≥ 50 px. Muestreo sin reemplazo, semilla 0 |
| Base | 400 personas *bare* (visibilidad ≥ 0,90, altura ≥ 50 px), semilla 0. Se usan sin tocar, como referencia de «sin oclusión» |
| Cobertura objetivo | Por persona base, 1 − visibilidad de una persona *heavy* tomada al azar (semilla 1), recortada a [0,35; 0,80]. Así las familias ocluyen tanto como la oclusión real |
| Familias | Se aplican a las **mismas** 400 personas base:<br>• **parches** (E1): parche interior; contenido textura 0,4 / recorte de objeto 0,5 / opaco 0,1; banco `banco_train.json`<br>• **siluetas** (E2, E4, E8-S): banco `siluetas_cp_val`, anclado a un lado<br>• **geometría** (E8-G): mismo banco, colocado sobre la región oculta de un patrón real de `patrones_train.json`<br>• **generativa** (E7, E7b): SD1.5 *inpainting*, mismo generador y control de calidad que H9 |
| Recorte | Caja ampliada 20 % por lado, cuadrado con relleno gris (114), 224 × 224 |
| Características | **DINOv2-base** (CLS; primaria) y **CLIP ViT-B/16** (secundaria), pesos públicos de Hugging Face |
| Medida de realismo | **AUC** de una regresión logística (estandarizada, C = 1) que separa la oclusión real de cada conjunto, con validación cruzada estratificada 5 × 5 y puntuación fuera de muestra promediada. AUC = 0,5 significa indistinguible de la oclusión real: **cuanto menor, más realista** |
| IC | Bootstrap de personas (1 000 réplicas, semilla 0), pareado entre familias porque comparten las mismas personas base |
| Secundario | KID (núcleo polinómico de grado 3; 50 subconjuntos de 100) |
| Código | `31_realismo.py` (autotest 10/10): `generar`, `caracteristicas` y `analisis` |

## 2. Hipótesis (literal)

- **H13.** El realismo medido sigue el orden de construcción. Con DINOv2, **AUC(parches) > AUC(siluetas) > AUC(generativa)**, con las dos diferencias con IC 95 % > 0.
  - *Confirmada:* las dos diferencias tienen IC > 0.
  - *Parcialmente confirmada:* solo una de las dos.
  - *No confirmada:* ninguna.
- **Lectura fijada ahora** (descriptiva, con los resultados de transferencia ya conocidos):
  - Si H13 se confirma, el artículo dirá que **el realismo medido aumentó** de parches a generativa **sin que apareciera la transferencia**.
  - Si no se confirma, dirá que el orden por construcción no se refleja en las características, y retirará la afirmación de que las familias forman una escalera de realismo.
- **Secundarios declarados (no deciden H13):**
  1. La geometría frente a las siluetas.
  2. Cada familia frente a la base sin ocluir: si una familia no es más parecida a la oclusión real que no ocluir nada, se dirá.
  3. Réplica con CLIP.
  4. KID.
  5. **Confusor de tamaño:** AUC usando solo la altura de la caja (real frente a base).
  6. Cobertura conseguida por familia y número de personas sin oclusión aplicada.
  7. Tabla descriptiva que cruza el realismo medido con la transferencia de cada familia entrenada en ExDark: E1 (parches), E8-S (siluetas), E8-G (geometría) y E7b (generativa).

## 3. Lo que NO se hará

- No se cambiarán N, semillas, recorte, extractores, clasificador ni métrica después de ver ningún resultado.
- No se ajustarán los generadores para que una familia resulte más o menos realista.

## 4. Orden de ejecución

1. Congelamiento v3.8 (este documento y `31_realismo.py`).
2. `generar` (la familia generativa necesita GPU: SD1.5), `caracteristicas` y `analisis`, que escribe `informes/veredicto_h13.md` y `resultados_h13/analisis/realismo_h13.json`.
3. Informe `informes/reporte_h13.md`; solo después, el texto del artículo.
