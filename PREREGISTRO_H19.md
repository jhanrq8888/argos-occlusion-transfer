# ARGOS-11 — Pre-registro de H19 (RT-DETR-l con exposición igual: 30 épocas fijas)

Pre-registrado el **2026-11-11**, **después** de cerrar H1–H18, del short paper de 6 páginas y del reporte de seguimiento
del 11/11/2026 (observación 12), y **antes** de entrenar ninguna corrida de H19. Complementa a `PROTOCOLO.md`,
`PROTOCOLO_v2.md` y `PREREGISTRO_H8.md`: lo que no se menciona no cambia (datos, aumento, validación, evaluación,
métrica y regla). En el artículo largo, este bloque es **E15**.

## 0. Por qué este bloque (declarado)

1. La única evidencia con un detector *transformer* es H8 (RT-DETR-l), que usó parada temprana: V1′ se detuvo en 28–31
   épocas y V3′ llegó a 51–77 (`runs/argos_rtdetr/*/results.csv`), es decir, **exposición desigual**. El propio artículo atribuye a esa desigualdad el daño de los
   primeros bloques, así que H8 no permite concluir nada sobre la familia *transformer*.
2. El reporte de seguimiento del 11/11/2026 (obs. 12) pide cerrar esa alternativa con evidencia primaria: un bloque
   RT-DETR-l con épocas fijas, V1 y V3 en la misma máquina y 3 semillas.
3. Ya se conocen los resultados de H1–H18, incluido H8 (RT-DETR-l, exposición desigual: hipótesis sostenida, sin
   transferencia). No se ha entrenado ni evaluado ninguna corrida de RT-DETR con 30 épocas fijas.

## 1. Hipótesis (literal; no se reformula después)

- **H19.** Con **RT-DETR-l** y exposición igual (30 épocas fijas, sin parada temprana, pesos de la última época), el
  contraste V3 − V1 (AP@0.5, media de 3 semillas) **no alcanza +2 pp con IC 95 % por imágenes que excluya el cero en al
  menos 2 de las 3 fuentes reales** (NightOwls, CityPersons convención, indicador de oclusión de ExDark).
  - *Refutaría H19:* V3 − V1 ≥ +2 pp con IC 95 % por imágenes que excluya el cero en **al menos 2 de las 3** fuentes
    reales (la regla de H4–H18).
  - *No concluyente:* (a) el control `silueta_severa` no alcanza +2 pp con IC que excluya el cero (el aumento no se
    aprendió), o (b) el ajuste no funciona: V1 no supera en ExDark test (global) al RT-DETR-l de COCO sin ajustar.

## 2. Análisis de sensibilidad declarados (no deciden el veredicto)

- **IC jerárquico** (semillas + imágenes, `23_bootstrap_jerarquico.py`), como en todos los bloques.
- **IC t de Welch entre semillas** de la diferencia V3 − V1 por fuente (3 semillas por variante), que recoge la varianza
  entre semillas que el bootstrap jerárquico con 3 semillas subestima (lección de la obs. 11 del mismo reporte).
- **Especificidad:** V3 − V1 en las personas sin oclusión de cada fuente real, descriptivo, como en H18.

El veredicto se decide **solo** con el IC por imágenes, como en todo el protocolo.

## 3. Diseño

| Elemento | Definición |
|---|---|
| Modelo | `rtdetr-l.pt` (Ultralytics, COCO; el mismo fichero congelado en v3.2 para H8) |
| Datos, aumento y validación | Idénticos a H8 y a la iteración 2 (`--protocolo v2`): ExDark-People train (1 183 imágenes), siluetas v2 con banco `siluetas_train`, validación mixta (`data_v2.yaml`) |
| Variantes | **V1** (sin aumento) y **V3** (siluetas v2), semillas {0, 1, 2}: **6 corridas**, todas en **la misma máquina** |
| Hiperparámetros | `config/hiperparametros_rtdetr.yaml` de H8 sin ningún cambio (AdamW, lr0 1e-4, weight decay 1e-4, lr de sesgos en el calentamiento 0,0, lote 8 con lote nominal 64, 640 px, AMP) **salvo la exposición:** `--epochs 30 --patience 0` (30 épocas exactas, sin parada temprana), como H9b–H18 |
| Pesos evaluados | `weights/last.pt` (época 30) de cada corrida; no hay selección por validación |
| Comando | `07_entrenar.py --protocolo v2 --modelo-base rtdetr-l.pt --hiperparametros hiperparametros_rtdetr.yaml --epochs 30 --patience 0 --proyecto argos_rtdetr_fijo --variantes V1 V3 --semillas 0 1 2 --workers 8` (una corrida por proceso, hasta 3 a la vez) |
| Máquina | RunPod, una sola RTX 4090 para las 6 corridas (Ultralytics 8.4.143, torch 2.8.0+cu128), como H11–H18 |
| Evaluación | Igual que H8: `09_evaluar_estratificado.py` con los pesos `last.pt` sobre `silueta_severa` (control), NightOwls, CityPersons convención, indicador de ExDark y ExDark test global; RT-DETR con su propia clase (sin NMS; hasta 300 detecciones, confianza ≥ 0,001) |
| Referencia sin ajustar | La de H8 (`rtdetr-l.pt` de COCO evaluado en los mismos conjuntos), reutilizada |
| Contrastes | V3 − V1 por conjunto y estrato; bootstrap pareado por imágenes, 1 000 réplicas |
| Costo estimado | ~1 min por época en la 4090 → 30–45 min por corrida, 3 en paralelo: **~2–3 h de GPU** |

## 4. Lo que NO se hará

- No se ajustarán optimizador, lr, lote, épocas ni ningún hiperparámetro después de ver ninguna corrida.
- No se añadirán semillas ni se cambiarán la métrica, las fuentes o la regla.
- Si una corrida falla por un error técnico, se repite **la misma corrida** con la misma configuración y se declara.
- Ninguna corrida de H8 se mezcla con las de H19.

## 5. Fecha verificable

Este documento se congela con su SHA-256 (protocolo v3.13) y se sella con **OpenTimestamps antes de subir nada al pod**:
a diferencia de H3–H18, el sello externo de H19 es anterior al entrenamiento.

## 6. Orden de ejecución

1. Congelamiento v3.13 (añade este documento) y sello OpenTimestamps de `PREREGISTRO_H19.md` y `protocolo_congelado.json`.
2. Las 6 corridas en `runs/argos_rtdetr_fijo/rtdetr-l_{V1,V3}_s{0,1,2}/`, lanzadas en el orden V1_s0, V3_s0, V1_s1,
   V3_s1, V1_s2, V3_s2.
3. Descarga de pesos con SHA-256 verificado; verificación del protocolo intacto; evaluación, bootstrap, IC jerárquico,
   IC de Welch e informe `informes/reporte_h19_rtdetr_fijo.md` con el veredicto literal.
