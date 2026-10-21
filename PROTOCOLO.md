# ARGOS-11 — Protocolo experimental congelado

Versión 1.1 (v1.0 congelada el 2026-09-11 08:09; cambio de lr0 registrado en `CAMBIOS_PROTOCOLO.md`). Este documento fija, **antes de la primera corrida de
entrenamiento** (hito S4), todo lo que la Sección 2.9 del PPI exige
congelar. Su hash SHA-256, junto con el de los ficheros listados en la
Sección 8, se publica en `protocolo_congelado.json` mediante
`08_congelar_protocolo.py`. Cualquier cambio posterior se registra en
`CAMBIOS_PROTOCOLO.md` con fecha y justificación.

## 1. Diseño

Factorial 2×2 sobre YOLOv11s con pesos COCO idénticos en todas las celdas:

| Variante | Atención CBAM (VI₁) | Aumento de oclusión (VI₂) |
|----------|---------------------|---------------------------|
| V1 (baseline) | no | no |
| V2 | sí | no |
| V3 | no | sí |
| V4 (ARGOS-11) | sí | sí |

Tres semillas fijas {0, 1, 2} por celda, mismo split, mismo script de
evaluación, orden de ejecución V1→V4 para cada semilla. Controles a una
semilla: `C_AUMENTO` (V1 con aumento base intensificado, sin borrado en
bbox) y `C_PESOS` (V1 sin preentrenamiento). Total: 14 corridas. V5
(ELS-YOLO) queda fuera del alcance (Sección 3.1 del PPI).

## 2. Datos

- Marco muestral: ExDark; muestra ExDark-People (imágenes con ≥1 persona),
  split público de Cui et al.: **train 1 183 / val 634 / test 841
  imágenes; 3 271 / 1 954 / 2 235 instancias** (`dataset/reporte_preparacion.json`).
- Listas de split: `dataset/splits/{train,val,test}.txt` (hash en Sección 8).
- Unidad de análisis: la instancia anotada de persona.
- La validación durante el entrenamiento usa el split *val* sin oclusión.
  El split *test* (y sus versiones ocluidas) nunca participa en el
  entrenamiento ni en la selección de modelo.

## 3. Hiperparámetros (idénticos en todas las corridas)

`config/hiperparametros.yaml`: SGD, **lr0 0,002** (v1.0: 0,01), momentum 0,937, weight decay
0,0005, warm-up 3 épocas, batch 16, 640×640, AMP, determinista.
**Épocas: 100 con parada temprana (paciencia 20)**, fijadas a partir de
la corrida piloto de S1 (65 s/época en RTX 5050 Laptop 8 GB; 14 corridas ≈
25 h). Esta cifra sustituye a las 200 de ELS-YOLO por la ventana de 11
semanas, y es la misma en las 14 corridas.

**lr0 = 0,002 (cambio registrado).** El 0,01 del protocolo de ELS-YOLO
corresponde a entrenamiento desde cero. Con pesos COCO y 1 183 imágenes, la
primera corrida (V1_s0, v1.0) mostró en *val* mAP50 0,81 en la época 1 y
colapso a 0,47 al alcanzar lr 0,01, con recuperación lenta (0,69 en la 21)
y parada temprana con el mejor modelo en la época 1. Un piloto de
diagnóstico con 0,002 se mantuvo en 0,83–0,85 sin colapso. El cambio se
aplica por igual a las 14 corridas y se decidió solo con curvas de *val*;
la corrida descartada se conserva en `runs/descartadas/`.

`config/aumento_base.yaml`: mosaico 1,0; HSV (0,015 / 0,7 / 0,4);
traslación 0,1; escala 0,5; volteo horizontal 0,5; sin mixup/cutmix/
copy-paste; `close_mosaic` 10. Idéntico en V1–V4.

## 4. Componentes

- **Componente 1 (CBAM)**: tres bloques (P3, P4, P5) a la salida del neck,
  antes de Detect; implementación fiel a Woo et al. 2018 (GAP+GMP, MLP con
  r = 16, conv espacial 7×7). +43 302 parámetros (+0,46 %).
  `modelos/yolo11s-cbam.yaml`, `weights/yolo11s_cbam_coco.pt` (pesos COCO
  transferidos por nombre; los 493 tensores que transfiere V1).
- **Componente 2 (aumento de oclusión)**: por imagen, con p = 0,5 se
  eligen 1–3 personas y sobre cada una se pega un parche interior
  rectangular que cubre f ~ U[0,30; 0,85] del área de la caja, con tipo
  textura (0,4) / recorte de objeto real (0,5) / opaco (0,1); banco de
  recortes `dataset/banco_train.json`. Las etiquetas no se modifican.

## 5. Conjuntos de prueba estratificados

- **Sintético (Fuente 2a)**: generador distinto del de entrenamiento
  (banda anclada a un borde de la caja, todas las instancias, banco
  `dataset/banco_test.json` disjunto). Nueve conjuntos: {textura, recorte,
  opaco} × {ligera [10,30), moderada [30,70), severa [70,100]} %. La
  cobertura efectiva se mide por instancia y define su estrato.
- **Real (Fuente 2b)**: 330 instancias del test anotadas por dos
  anotadores con `GUIA_DE_ANOTACION.md` (piloto: κ ponderado 0,82 sobre
  50). Cuotas: ≥300 evaluables y ≥50 por estrato ligera/moderada/severa.
- **Regla de fusión (a priori)**: si tras agotar el test el estrato severo
  no alcanza 50 instancias, se fusiona con moderada en *ocluida* ≥30 %,
  se reporta el conteo alcanzado y se declara como limitación.

## 6. Evaluación

Script único `09_evaluar_estratificado.py` (AP COCO 101 puntos, contrastado
con pycocotools): conf 0,001, NMS IoU 0,7, máx. 300 detecciones, 640 px.
Regla de regiones *ignore*: al evaluar un estrato, las instancias de otros
estratos de la misma imagen son *ignore* (no cuentan como FP ni TP); las
instancias sin anotar son *ignore* en la evaluación estratificada y GT en
la global; las no evaluables son *ignore* siempre. Se reporta el número de
instancias efectivas de cada estrato.

FPS (`10_medir_costo.py`): batch 1, FP16, 640, 50 imágenes de warm-up,
promedio sobre 500; ONNX Runtime (CUDA) y PyTorch, ambos reportados.

## 7. Criterios de éxito e hipótesis (Sección 1.9 del PPI)

H1: AP@0.5 de V4 > V1 en moderada y severa, con FPS ≥ 90 % del baseline.
H2: aporte de VI₂ > aporte de VI₁ en los estratos ocluidos.
H3: la dirección del efecto se conserva sobre oclusión real, en ≥2 de 3
fuentes (propia, NightOwls, CityPersons); si discrepan, no concluyente.

Una hipótesis se sostiene cuando conjuntamente: (a) ΔAP@0.5 ≥ +2 pp
frente a V1 (media de 3 semillas) en moderada y severa; (b) el IC 95 %
por bootstrap sobre imágenes (≥1000 réplicas) de ese ΔAP excluye el
cero; (c) FPS ≥ 30 en GPU de escritorio. Confirmatorio: marginales por
estrato agregando la iluminación. Exploratorio: cruce luz × estrato y
ANOVA 2×2. Inferencia basada en semillas: indicativa.

## 8. Ficheros bajo hash

`PROTOCOLO.md`, `config/hiperparametros.yaml`, `config/aumento_base.yaml`,
`config/aumento_base_intenso.yaml`, `dataset/data.yaml`,
`dataset/splits/*.txt`, `modelos/yolo11s-cbam.yaml`,
`weights/yolo11s_cbam_coco.pt`, `yolo11s.pt`, `GUIA_DE_ANOTACION.md`,
`dataset/banco_train.json`, `dataset/banco_test.json`,
`dataset/test_sintetico/resumen_generacion.json`, `argos_lib/*.py` y los
scripts `0?_*.py`, `1?_*.py`.
