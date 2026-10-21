# ARGOS-11 — Pre-registro de H12 (E10: un detector más grande, YOLOv11m) y extensión de semillas de E7b y E8

Redactado y congelado el **2026-10-13** (protocolo **v3.7**), después de cerrar H1–H11 y **antes** de entrenar o evaluar ninguna corrida con este diseño. Ningún resultado con YOLOv11m existe todavía. Las semillas 3 y 4 de YOLOv11s tampoco se han entrenado. **Enmendado como v3.7b** el mismo día, antes de completar ninguna corrida (sección 6).

## 0. Contexto y motivación (declarado)

Todas las conclusiones del proyecto se apoyan en detectores de un solo tamaño por familia: YOLOv11s, YOLO26s y RT-DETR-l. Una valoración externa del artículo (13/10) señala dos objeciones de alcance:

1. **Tamaño del modelo:** podría ser que un detector más grande sí aprovechara el aumento sintético en la oclusión real.
2. **Número de semillas:** solo hay tres por variante.

Este documento pre-registra dos bloques:

- **E10 (H12):** las dos familias más realistas (siluetas y generativa) con **YOLOv11m**, con la exposición fija de E7b y E8 (30 épocas, `last.pt`).
- **Extensión de semillas (secundaria):** las semillas **3 y 4** de YOLOv11s para E7b (V1 y V3ᵍ) y para las siluetas sin cambios de E8 (V3ˢ), con la misma receta que las semillas 0–2 (máquina: ver la enmienda de la sección 6).

**Declaración.** H9b decía «no se añadirán semillas». Esta extensión **no modifica el veredicto de H9b ni el de H10**. Es un análisis secundario nuevo, pre-registrado aquí, sobre la estabilidad de sus celdas.

## 1. E10 — Hipótesis H12 (literal; no se reformula después)

Las condiciones comunes a las dos sub-hipótesis son:

- **YOLOv11m** preentrenado en COCO (`yolo11m.pt`, sha256 `d5ffc1a6…`), con los mismos hiperparámetros, aumento base, datos (ExDark-People train, 1 183 imágenes) y validación mixta que E7b y E8;
- V1 y V3 entrenados **exactamente 30 épocas**, sin parada temprana (`--patience 0`), con el calendario completo de tasa de aprendizaje;
- evaluación con **`last.pt`** (época 30);
- semillas **{0, 1, 2}**.

Las dos sub-hipótesis son:

- **H12a (siluetas).** El déficit de transferencia persiste con YOLOv11m y siluetas (generador v2 de E2 y E8, `--protocolo v2`). El contraste V3ˢⁱˡ − V1 (AP@0.5, media de 3 semillas) **no alcanza +2 pp con IC 95 % por imágenes que excluya el cero en al menos 2 de las 3 fuentes reales**: NightOwls ocluida, CityPersons *heavy* y ExDark proxy severa. Esto vale aun cuando el control `silueta_severa` alcance +2 pp con IC > 0.
- **H12b (generativa).** Lo mismo con la oclusión generativa de E7b (`--protocolo gen`, mismos datos generados en `dataset/generativa_train/`), V3ᵍᵉⁿ − V1, con el control `generativa_severa`.

**Regla (la de H4, H8, H9, H9b y H10):**

| Veredicto | Condición |
|---|---|
| *Sostenida* | Menos de 2 de las 3 fuentes reales superan +2 pp con IC por imágenes > 0, y el control sí lo hace |
| *Refutada* | 2 o 3 fuentes reales superan +2 pp con IC por imágenes > 0 |
| *No concluyente* | El control no alcanza +2 pp con IC > 0 (el aumento no se aprendió) |

**Compromiso de reporte.** Si H12a o H12b se refutan, el artículo dirá que con un detector más grande el aumento **sí** se transfiere en esa familia, y la conclusión general quedará acotada al tamaño pequeño. Si se sostienen, se reportará que el resultado se mantiene con un modelo de mayor tamaño de la misma familia, sin extenderlo a otros tamaños.

**Análisis secundarios declarados ahora (no deciden H12):**

1. IC jerárquico (semillas + imágenes, 2 000 réplicas).
2. Tasa de pérdida (MR-2) y AP@0.5:0.95 en las mismas celdas (funciones de `24_` y `27_`).
3. Curva por visibilidad en CityPersons (función de `27_`).
4. Comparación descriptiva con YOLOv11s (E7b y V3ˢ de E8): V1 de YOLOv11m frente a V1 de YOLOv11s en las fuentes reales, y si los contrastes V3 − V1 cambian de signo.

## 2. Extensión de semillas de E7b y E8 (análisis secundario)

- **Corridas:** YOLOv11s, semillas **{3, 4}**, 30 épocas fijas, `last.pt`, misma receta que E7b y E8:
  - **V1** y **V3ᵍᵉⁿ** con `--protocolo gen`;
  - **V3ˢⁱˡ** con `--protocolo v2`.

  Son **6 corridas**, en RunPod (RTX 4090, 8 procesos de carga) según la enmienda v3.7b (sección 6); las semillas 0–2 se entrenaron en la laptop.
- **Celdas:**
  - V3ᵍᵉⁿ − V1 con 5 semillas, que son la V1 y la V3ᵍ de E7b más las nuevas;
  - V3ˢⁱˡ − V1 con 5 semillas, que son las V3ˢ de E8 más las nuevas, frente a la misma V1.

  En los dos casos se evalúan el control y las 3 fuentes reales, con IC por imágenes y jerárquico.
- **Lectura fijada ahora:**
  - Los veredictos de H9b y H10 no cambian.
  - Si con 5 semillas alguna fuente real supera +2 pp **con IC jerárquico > 0**, se reportará como un resultado que contradice la conclusión obtenida con 3 semillas.
  - En otro caso, se reportará que la conclusión se mantiene con 5 semillas.

## 3. Diseño

| Elemento | Definición |
|---|---|
| Hiperparámetros, aumento base | `config/hiperparametros.yaml` y `config/aumento_base.yaml` (los de E7b y E8). Única excepción: épocas y paciencia |
| Épocas | 30 fijas (`--epochs 30 --patience 0`), como E7b y E8. Se fija antes de ver ningún resultado. No se ajusta al tamaño del modelo, para mantener la exposición de las réplicas |
| Pesos evaluados | `last.pt`. `best.pt` se guarda, pero no se usa |
| E10: corridas | 9 en RunPod (RTX 4090, 8 procesos de carga), Ultralytics 8.4.143. V1, V3ˢⁱˡ y V3ᵍᵉⁿ comparten máquina, así que el contraste es interno |
| E10: proyectos | `runs/argos_m_gen/` (V1 y V3ᵍᵉⁿ, `--protocolo gen`) y `runs/argos_m_sil/` (V3ˢⁱˡ, `--protocolo v2`). Prefijo de corrida `yolo11m_` (`--modelo-base yolo11m.pt`) |
| E10: comandos | `07_entrenar.py --protocolo gen --modelo-base yolo11m.pt --variantes V1 V3 --semillas S --epochs 30 --patience 0 --proyecto argos_m_gen --workers 8` y `07_entrenar.py --protocolo v2 --modelo-base yolo11m.pt --variantes V3 --semillas S --epochs 30 --patience 0 --proyecto argos_m_sil --workers 8`, por semilla S = 0, 1, 2 |
| Extensión: proyectos | `runs/argos_gen_fijo_s34/` (V1 y V3ᵍᵉⁿ) y `runs/argos_sil_fijo_s34/` (V3ˢⁱˡ), con `--workers 8` en RunPod (enmienda v3.7b) |
| Datos subidos al servidor | Solo los necesarios: código, `yolo11m.pt`, imágenes y etiquetas de ExDark train/val, `val_ocluido`, banco `siluetas_train`, `generativa_train` y configuración. Las rutas de Windows se reescriben a Linux sin cambiar el contenido. Los conjuntos de evaluación no salen del equipo local |
| Evaluación | En la laptop, con `09_evaluar_estratificado.py --pesos .../weights/last.pt`, sobre `silueta_severa`, `generativa_severa`, NightOwls, CityPersons (convención) y el proxy de ExDark. Resultados en `resultados_h12m/` (YOLOv11m) y `resultados_h12s/` (semillas 3–4), con nombres `yolo11m_V1_sN`, `yolo11m_V3sil_sN`, `yolo11m_V3gen_sN`, `V1_sN`, `V3gen_sN` y `V3sil_sN` |
| Veredicto | `30_h12.py` (autotest 11/11 tras la enmienda). Aplica la regla de la sección 1 y escribe `informes/veredicto_h12.md` y `resultados_h12/analisis/contrastes_h12.{csv,json}`. Antes de congelar se comprobó que reproduce las diferencias de E7b con sus 3 semillas (+15,23, +0,01, +1,52 y −3,03). Los IC difieren en la segunda cifra decimal porque cada celda usa su propia semilla de remuestreo (índice de la celda) |
| Costo estimado | E10: ~2–3 h de RTX 4090. Extensión: ~1 h de RTX 4090. En total, ~3,5 USD |

## 4. Lo que NO se hará

- No se cambiarán épocas, paciencia, hiperparámetros, datos, generadores, semillas ni fuentes después de ver ninguna corrida.
- No se usará `best.pt` para el criterio, ni se elegirá otra época a posteriori.
- No se probarán otros tamaños (l, x) en este bloque, ni se añadirán semillas a E10.
- No se cambiarán los veredictos de H1–H11.

## 5. Orden de ejecución

1. Congelamiento **v3.7** (este documento, `30_h12.py` y `yolo11m.pt`), con fecha y huella en `CAMBIOS_PROTOCOLO.md`. **No entrenar antes.**
2. En RunPod: subida de datos, prueba de humo (1 época, 5 %), las 9 corridas de E10 por semilla (`yolo11m_V1_s0`, `V3gen_s0`, `V3sil_s0`, después s1 y s2) y luego las 6 de la extensión (V1, V3gen y V3sil, semilla 3 y después 4).
3. Descarga de pesos con verificación SHA-256, evaluación local, `30_h12.py` e `informes/reporte_h12.md` con el veredicto literal.
4. Solo después, actualizar el artículo, el short paper, el PPI y el informe general con el resultado, sea cual sea.

## 6. Enmienda v3.7b (2026-10-13, antes de completar ninguna corrida)

- **Qué cambia:** la extensión de semillas (sección 2) se entrena en **RunPod (RTX 4090, 8 procesos de carga)**, la misma máquina que E10, y no en la laptop.
- **Por qué:** por tiempo. En la laptop las 6 corridas tardaban ~4,2 h (84 s por época), y en la RTX 4090 tardan ~1 h.
- **Estado en el momento de la enmienda:** la primera corrida (V1_s3) iba por la época 4 de 30 en la laptop. Se detuvo y se apartó en `runs/descartadas/argos_gen_fijo_s34_laptop_cancelada/`, sin terminar y sin evaluar. No existe ningún resultado de este diseño.
- **Consecuencia declarada:** las semillas 3–4 se entrenan en otra máquina que las 0–2. Dentro de cada semilla, V1 y V3 comparten máquina, así que cada contraste por semilla es interno. Al juntar las 5 semillas, la diferencia de hardware se suma a la variación entre semillas.
- **Análisis adicional declarado ahora:** además de los IC con 5 semillas, se informará V3 − V1 solo con las semillas 3–4, para comparar con las 0–2.
- **Lo que no cambia:** la lectura fijada en la sección 2, las reglas de H12a y H12b, las épocas, los datos y los demás elementos del diseño.
