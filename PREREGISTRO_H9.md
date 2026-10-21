# ARGOS-11 — Pre-registro de H9 (tercera familia de oclusor: oclusión generativa)

Pre-registrado el **2026-10-02**, **después** de cerrar H1–H8, el análisis final, el bootstrap jerárquico y la tasa de pérdida, y **antes** de generar ningún dato de H9, entrenar ninguna corrida o evaluar nada. Complementa a `PROTOCOLO.md`, `PROTOCOLO_v2.md`, `PREREGISTRO_H6_H7.md` y `PREREGISTRO_H8.md`: lo que no se menciona no cambia (datos de la iteración 2, validación mixta, hiperparámetros de YOLOv11s, evaluación estratificada con regiones *ignore*, bootstrap por imágenes con 1 000 réplicas como criterio, umbral de relevancia de +2 pp). Se congelará como **v3.3** antes de la primera corrida.

## 0. Lo que se hizo antes de este documento (declarado)

1. Se instalaron `diffusers` 0.40.0, `transformers` 5.18.0 y `accelerate` 1.15.0 en el entorno del proyecto (no cambian `torch` 2.11 ni `ultralytics` 8.4.143).
2. Se descargó el modelo de *inpainting* `stable-diffusion-v1-5/stable-diffusion-inpainting` (pesos fp16, sin el filtro de seguridad) en `modelos/sd15_inpaint/` (no se versiona en git por su tamaño).
3. Se descartó como tercera familia el pegado de objetos de COCO: las siluetas v2 ya pegaban objetos reales la mitad de las veces (en los bancos de CityPersons y NightOwls, 84–87 % autos), así que habría sido una variante de la segunda familia.

## 1. Motivación

Las dos familias probadas son **artificiales en su composición**: parches rectangulares (exp. 1) y recortes con máscara pegados con mezcla alfa (siluetas, iteración 2 y H6–H8). La objeción más previsible a la conclusión del proyecto es que el déficit de transferencia se deba a que esos oclusores no son lo bastante realistas: bordes de pegado, iluminación y perspectiva inconsistentes. La **oclusión generativa** responde a esa objeción: un modelo de difusión *pinta* el oclusor dentro de una máscara sobre la persona, con la luz, la textura y la perspectiva de la escena y sin bordes de pegado. Es la forma más realista de fabricar oclusión disponible hoy, y es la familia que el artículo declaraba como no probada. Si el realismo del oclusor fuese lo que falta, H9 tiene una oportunidad real de ser refutada.

## 2. Hipótesis (literal; no se reformula después)

- **H9.** El déficit de transferencia se replica con una tercera familia de oclusor, la **oclusión generativa**: con YOLOv11s entrenado con el protocolo de la iteración 2 (ExDark-People train, validación mixta) y oclusores pintados por un modelo de difusión (*Stable Diffusion inpainting*) sobre parte de cada persona, el contraste V3ᵍ − V1′ (AP@0.5, media de 3 semillas) **no alcanza +2 pp con IC 95 % que excluya el cero en al menos 2 de las 3 fuentes reales** (NightOwls ocluida, CityPersons *heavy*, ExDark proxy severa), aun cuando el control sintético `generativa_severa` sea ≥ +2 pp con IC que excluya el cero.
  - *Refutaría H9:* V3ᵍ − V1′ ≥ +2 pp con IC 95 % por imágenes que excluya el cero en **al menos 2 de las 3** fuentes reales (el mismo criterio de H4 y H8).
  - *No concluyente:* (a) el control `generativa_severa` no alcanza +2 pp con IC que excluya el cero (el aumento no se aprendió); o (b) el generador falla: menos del 50 % de las oclusiones intentadas en entrenamiento superan el control de calidad de la sección 3.
- **Análisis de sensibilidad declarados:** IC jerárquico (semillas + imágenes, `23_`) y tasa de pérdida (`24_`). El veredicto se decide con el IC por imágenes, como en todo el protocolo.
- **Descriptivo, sin criterio:** V3ᵍ − V1′ en `silueta_severa` y comparación con el V3′ de siluetas de la iteración 2.

## 3. Diseño

| Elemento | Definición |
|---|---|
| Modelo de detección | YOLOv11s (`yolo11s.pt`, COCO), `config/hiperparametros.yaml` y `config/aumento_base.yaml` sin cambios |
| Datos y validación | Idénticos a la iteración 2: ExDark-People train (1 183 imágenes); validación mixta `data_v2.yaml` (val original + copia ocluida con siluetas del banco de validación) |
| Línea base | **V1′ de la iteración 2** (`runs/argos_v2/V1_s{0,1,2}`), reutilizada: mismos datos, validación, hiperparámetros, semillas y código de entrenamiento sin aumento. Solo se entrenan las V3ᵍ |
| Variantes nuevas | **V3ᵍ** (aumento generativo), semillas {0, 1, 2}: **3 corridas** en `runs/argos_gen/` |
| Generador | `stable-diffusion-v1-5/stable-diffusion-inpainting` (fp16), planificador DPM-Solver multipaso, 20 pasos, escala de guía 7,5. Para cada persona: recorte cuadrado alrededor de su caja (lado = máx(2,2 × lado mayor de la caja, 128 px)), escalado a 512 × 512; máscara anclada a un borde de la caja (abajo 0,5; izquierda 0,2; derecha 0,2; arriba 0,1), que sobresale de la caja como un oclusor que entra desde fuera, escalada por búsqueda binaria hasta cubrir la fracción objetivo *f* de la caja; el resultado se recompone solo dentro de la máscara (borde suavizado), de modo que el resto de la imagen no cambia |
| Oclusores (*prompts*) | Diez clases de COCO que no son personas: auto estacionado, bicicleta, motocicleta, banca, maceta con planta, hidrante, maleta, paraguas, silla y camión, con el sufijo «at night, low light, realistic photo». *Prompt* negativo: «person, people, human, man, woman, child, body, face, legs, clothes, text, watermark». No se generan personas, así que no hay instancias nuevas que etiquetar |
| Control de calidad | Segmentación de instancias COCO (`yolo11s-seg.pt`, clase persona, confianza ≥ 0,25) sobre el recorte generado. Si más del 50 % del área de la máscara dentro de la caja sigue siendo persona, la difusión volvió a dibujar a la persona: se reintenta hasta 2 veces con otra semilla y otro *prompt*; si no, esa persona queda sin ocluir. **Cobertura efectiva** = (máscara ∩ caja − persona segmentada ∩ máscara ∩ caja) / área de la caja |
| Entrenamiento: datos generados | Dos versiones ocluidas de cada imagen de train (semillas de generación 0 y 1); en cada versión se ocluyen de 1 a 3 personas al azar con *f* ~ U[0,30; 0,85] (los mismos parámetros de las familias 1 y 2). Personas con lado menor de 8 px: no se ocluyen |
| Entrenamiento: uso | La difusión es demasiado lenta para aplicarse en línea. El dataset sustituye la imagen leída por una de sus dos versiones ocluidas (al azar) con probabilidad 0,15 por imagen mientras se usa mosaico, y 0,5 sin mosaico (últimas 10 épocas). Con mosaico de 4 imágenes, 1 − 0,85⁴ ≈ 0,48 de las muestras contienen al menos una imagen ocluida, equivalente al p = 0,5 por muestra de las familias 1 y 2. La sustitución ocurre al leer la imagen, antes del mosaico y del resto del aumento base (en las familias 1 y 2 el oclusor se aplicaba después): se declara como diferencia de implementación |
| Control sintético | `generativa_severa`: todas las personas de ExDark test con *f* ~ U[0,70; 1,00], semilla de generación 2024 (disjunta de las de train), mismo generador y control de calidad; estrato por cobertura efectiva |
| Evaluación | `09_evaluar_estratificado.py` sobre `generativa_severa` (control), `silueta_severa` (descriptivo), NightOwls, CityPersons convención y ExDark proxy. Las detecciones cacheadas de V1′ de la iteración 2 se reutilizan; V1′ solo se infiere en `generativa_severa` |
| Contrastes | V3ᵍ − V1′ por conjunto y estrato; bootstrap pareado por imágenes, 1 000 réplicas, semilla 0 |
| Costo estimado | Generación ~4–6 h de GPU (train + control); 3 corridas V3ᵍ ~2 h cada una → **~10–12 h de GPU** |

## 4. Lo que NO se hará

- No se cambiarán *prompts*, máscara, pasos, guía ni control de calidad después de ver ningún resultado de detección. Los parámetros del generador se fijan en el congelamiento v3.3, tras una demostración visual sobre imágenes de **entrenamiento** (sección 5, paso 2), sin entrenar ni evaluar ningún modelo.
- No se ajustarán hiperparámetros, épocas, paciencia ni lote después de ver ninguna corrida V3ᵍ.
- No se añadirán semillas ni se cambiarán la métrica o las fuentes del criterio.

## 5. Orden de ejecución

1. Implementar el generador (`argos_lib/generativa.py`, `25_oclusion_generativa.py`) con autotest.
2. Demostración visual sobre 12 imágenes de train (`dataset/demo_generativa/`); cualquier ajuste del generador en este paso se documenta en `CAMBIOS_PROTOCOLO.md`.
3. Generar las versiones de train (`dataset/generativa_train/`) y el control `generativa_severa`; registrar la tasa de éxito del control de calidad.
4. Prueba de humo (1 época, 5 %) y congelamiento **v3.3** (este documento, generador, datos generados y cambios en `argos_lib/entrenamiento.py`, `07_` y `09_`).
5. Las 3 corridas V3ᵍ en `runs/argos_gen/`, en el orden s0, s1, s2.
6. Evaluación, bootstrap, bootstrap jerárquico, tasa de pérdida, diagnóstico e informe `informes/reporte_h9_generativa.md` con el veredicto literal.
