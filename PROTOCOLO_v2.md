# ARGOS-11 — Protocolo v2.0: iteración 2 del aumento de oclusión

Versión 2.0 — pre-registrada el 2026-09-12, **después** de cerrar y
analizar el experimento 1 (protocolo v1.1b, 14 corridas) y **antes** de
entrenar ninguna corrida bajo este protocolo. Se congela con
`08_congelar_protocolo.py` (v2.0) y todo cambio posterior se registra en
`CAMBIOS_PROTOCOLO.md`. Este documento complementa a `PROTOCOLO.md`: lo
que no se menciona aquí no cambia (datos, split, hiperparámetros, CBAM,
evaluación, criterios de éxito).

## 1. Motivación (resultado del experimento 1, best.pt)

| Conjunto (AP@0.5)                | V1    | V3 (oclusión) | Δ V3−V1 [IC 95 %]   |
|----------------------------------|-------|---------------|---------------------|
| Sintético textura severa         | 0,035 | 0,469         | +43,5 [+41,2; +46,1] |
| Sintético opaco severa           | 0,012 | 0,622         | +60,9 [+58,5; +63,4] |
| NightOwls, ocluida (real)        | 0,261 | 0,230         | −3,2 [−4,6; −1,7]   |
| CityPersons, heavy (real)        | 0,138 | 0,135         | −0,4 [−1,1; +0,3]   |

La mejora sintética no transfiere a oclusión real; el diagnóstico
(`14_diagnostico_transferencia.py`) muestra *recall* real igual y +12–19 %
de falsos positivos: el modelo aprende la firma "caja con parche
rectangular = persona". H3 no sostenida (0 de 3 fuentes). Un modelo que
detecta al 62 % personas tapadas al 70–100 % por un rectángulo opaco no
está reconociendo siluetas parciales.

## 2. Hipótesis de la iteración 2 (pre-registradas)

- **H4.** Con oclusores de silueta real (personas y objetos con máscara,
  sin parches rectangulares ni opacos), el aumento de oclusión (V3′/V4′)
  mejora el AP@0.5 frente a V1′ en los estratos ocluidos de **al menos
  dos de las tres fuentes reales** (NightOwls *ocluida*, CityPersons
  moderada+severa / heavy, subconjunto propio), con IC 95 % bootstrap que
  excluya el cero. Umbral de relevancia: +2 pp (criterio (a) del PPI).
- **H5.** La mejora sintética de la iteración 2 sobre `silueta_*` será
  menor que la de la iteración 1 sobre `opaco_*`/`textura_*` (menos
  "firma" aprendible), y la brecha sintético→real se reducirá.
- Resultado que refutaría H4: ΔAP ≤ 0 o IC que incluya el cero en ≥2
  fuentes reales. Se reportará igualmente.

## 3. Cambios respecto a v1.1b (y solo estos)

1. **Generador de entrenamiento (Componente 2, v2).** `argos_lib/siluetas.py`.
   Por imagen, con p = 0,5 se eligen 1–3 personas; sobre cada una se pega
   un recorte **con máscara alpha** de persona (p = 0,5) u objeto (p = 0,5)
   del banco `dataset/siluetas_train/` (segmentación COCO `yolo11s-seg.pt`,
   conf ≥ 0,4, sobre imágenes del split *train* y las imágenes sin
   personas del banco v1 de *train*). El oclusor se ancla a un borde de la
   caja y se escala hasta cubrir f ~ U[0,30; 0,85] del área (±3 %).
   Sin parches opacos ni de textura.
2. **Selección del modelo con validación mixta.** `dataset/data_v2.yaml`:
   *val* = `images/val` (634 originales) + `val_ocluido/images` (634 copias
   con todas las personas ocluidas por siluetas del banco *val*,
   f ~ U[0,30; 0,85]). Motivo: en v1 el óptimo en *val* sin oclusión fue la
   época 2 en 11 de 12 corridas, es decir, la selección premiaba al modelo
   menos alejado de COCO y truncaba la exposición al aumento. Las
   etiquetas de `val_ocluido` son las originales. El *test* no cambia.
3. **Tercera familia sintética de prueba.** `silueta_{ligera,moderada,severa}`
   con el banco del split *test* (disjunto de *train* y *val*), misma
   regla de estrato efectivo. Los nueve conjuntos v1 se conservan.
4. **Réplica de generalidad.** V1′ y V3′ × semillas {0,1,2} con **YOLO26s**
   (`--modelo-base yolo26s.pt`, mismos hiperparámetros y mismo generador):
   6 corridas. No se implementa CBAM para YOLO26 (fuera de alcance).

Todo lo demás es idéntico: split, lr0 0,002, SGD, 100 épocas con paciencia
20, batch 16, semillas {0,1,2}, aumento base, CBAM, evaluación con regiones
*ignore*, bootstrap sobre imágenes, `best.pt` primario y `last.pt`
secundario.

## 4. Corridas

| Bloque | Corridas | Carpeta |
|---|---|---|
| Iteración 2, YOLOv11s | V1′–V4′ × {0,1,2} = 12 | `runs/argos_v2/` |
| Generalidad, YOLO26s | V1′, V3′ × {0,1,2} = 6 | `runs/argos_v2/yolo26s_*` |

Comandos: `07_entrenar.py --protocolo v2 --variantes V1 V2 V3 V4` y
`07_entrenar.py --protocolo v2 --variantes V1 V3 --modelo-base yolo26s.pt`;
evaluación `09_ --corridas runs/argos_v2 --resultados resultados_v2`
(añade automáticamente `silueta_*`); análisis `11_ --resultados resultados_v2`.

## 5. Riesgo declarado (análisis secundario last.pt, 2026-09-12)

Con más épocas de ajuste fino sobre ExDark la ganancia sintética crece
(textura severa V3 0,47 → 0,70) y la oclusión real empeora incluso en V1
(NightOwls ocluida 0,26 → 0,16; el YOLOv11s COCO sin ajustar da 0,39): hay
sobreajuste de dominio. La selección con *val* mixto elegirá épocas más
tardías; se reportará explícitamente la época seleccionada y el AP sobre
las fuentes reales de `best.pt`, `last.pt` y del modelo COCO sin ajustar.
Si H4 se cumpliera solo por seleccionar épocas tempranas, se declarará.

## 6. Lo que NO se hace

No se retocan hiperparámetros, no se cambia el modelo base principal, no se
añaden módulos, no se repite el experimento 1. El experimento 1 se reporta
íntegro como resultado principal negativo; la iteración 2 se reporta como
segundo experimento pre-registrado, con sus hipótesis fijadas aquí.
