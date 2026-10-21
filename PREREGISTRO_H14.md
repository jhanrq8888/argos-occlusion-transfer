# ARGOS-11 — Pre-registro de H14 (E11: oclusores con orden de profundidad)

Redactado el **2026-10-17** y congelado como **v3.9** antes de entrenar ninguna corrida. Antes de congelar se calcularon los mapas de profundidad, se revisó una lámina de ejemplos sobre **imágenes de entrenamiento** (sin cambiar ningún parámetro) y se generaron los datos de entrenamiento y el control con el código de este documento, para que su huella quede dentro del congelamiento, igual que en H9 (v3.3).

## 0. Contexto (declarado)

- La discusión del artículo deja una explicación abierta tras E7–E8: la oclusión real guarda **relación con la escena** (orden de profundidad, apoyo en el suelo, lo que ya tapa a la persona), y un pegado en dos dimensiones no la reproduce.
- Las siluetas se pegan siempre encima de la persona, aunque en la escena algo más cercano debería quedar delante.
- E11 pone a prueba esa explicación con un oclusor que se comporta como un objeto real **delante** de la persona.
- Se conocen ya los resultados de todas las familias anteriores (ninguna transfiere de forma robusta). Se pre-registra después de la valoración externa del 13/10.

## 1. Generador (`argos_lib/profundidad.py`, `32_profundidad.py`)

| Elemento | Definición |
|---|---|
| Profundidad | Depth Anything V2 Small (Hugging Face), profundidad inversa relativa normalizada a [0, 1] (1 = cerca); mapas guardados en PNG de 8 bits, con lado mayor de 512 |
| Oclusor | Recorte de un **objeto** del banco de siluetas de ExDark (`siluetas_train`; en el control, `siluetas_test`). Solo objetos, como la familia generativa, para no tener que etiquetar personas pegadas |
| Colocación | Base apoyada en el suelo por delante de la persona: entre sus pies y 0,12 de su altura más abajo. Entra por la izquierda, por la derecha o centrado |
| Orden de profundidad | La profundidad del oclusor es la de la escena en su punto de apoyo. Solo se pega si está más cerca que la persona (mediana de la mitad inferior de su caja) por más de 0,02; si no, se prueban los otros lados y, si ninguno sirve, **no se pega** |
| Composición | Solo donde la escena está **más lejos** que el oclusor, de modo que lo que ya estaba delante sigue tapando. La escala se busca hasta cubrir ~f de la caja contando solo la parte visible. Mismo ajuste de luminancia que las siluetas |
| Entrenamiento | 2 versiones por imagen de train (semillas 0 y 1), 1–3 personas por imagen, f ∈ (0,30; 0,85), en `dataset/profundidad_train/`. Se sustituyen al leer la imagen con la **misma probabilidad que E7b** (0,15 con mosaico, 0,5 sin mosaico): `--protocolo prof` |
| Control | `profundidad_severa` sobre ExDark test: todas las personas válidas, f ∈ (0,70; 1,00) |
| Parámetros fijados ahora | Margen 0,02, bajada 0,12, solo objetos, modelo V2 Small. No se ajustan después de entrenar |

## 2. Hipótesis H14 (literal)

- **H14.** El déficit de transferencia persiste con oclusores colocados con orden de profundidad. Las condiciones son:
  - YOLOv11s, ExDark-People;
  - V1 y V3ᵖʳᵒᶠ entrenados **exactamente 30 épocas** sin parada temprana, evaluados con `last.pt`;
  - semillas {0, 1, 2}.

  Bajo esas condiciones, V3ᵖʳᵒᶠ − V1 (AP@0.5, media de 3 semillas) **no alcanza +2 pp con IC 95 % por imágenes > 0 en al menos 2 de las 3 fuentes reales**: NightOwls ocluida, CityPersons *heavy* y ExDark proxy severa.

  | Veredicto | Condición |
  |---|---|
  | *Sostenida* | Menos de 2 fuentes reales superan +2 pp con IC > 0, y el control sí lo hace |
  | *Refutada* | 2 o 3 fuentes reales superan +2 pp con IC > 0 |
  | *No concluyente* | El control `profundidad_severa` no alcanza +2 pp con IC > 0 |

- **Compromiso de reporte.**
  - Si H14 se refuta, el artículo dirá que **el orden de profundidad es el ingrediente que faltaba** y que la oclusión sintética coherente con la escena sí se transfiere.
  - Si se sostiene, dirá que tampoco el orden de profundidad cierra la brecha, y se cerrará así la última explicación que el artículo dejaba abierta.
- **Secundarios declarados (no deciden H14):**
  1. IC jerárquico, tasa de pérdida y AP@0.5:0.95.
  2. Curva por visibilidad en CityPersons.
  3. Comparación descriptiva con E7b (mismo mecanismo de sustitución) y con las siluetas de E8.
  4. Tasa de aceptación del generador: personas para las que el oclusor pudo quedar delante.
  5. Realismo medido de esta familia con el procedimiento de H13 (`32_profundidad.py realismo`), comparado con las cuatro familias de H13.

## 3. Diseño de las corridas

| Elemento | Definición |
|---|---|
| Corridas | 6 en RunPod (RTX 4090, 8 procesos de carga): V1 y V3ᵖʳᵒᶠ, semillas 0–2, en `runs/argos_prof/`. V1 se entrena de nuevo en la misma máquina, para que el contraste sea interno |
| Comando | `07_entrenar.py --protocolo prof --variantes V1 V3 --semillas S --epochs 30 --patience 0 --proyecto argos_prof --workers 8`, por semilla |
| Evaluación | En la laptop, con `last.pt`, sobre `profundidad_severa` (control), `silueta_severa` y `generativa_severa` (descriptivos), NightOwls, CityPersons (convención) y el proxy de ExDark, en `resultados_h14/` |
| Veredicto | Script de veredicto con la regla de la sección 2, con autotest, escrito antes de evaluar |

## 4. Lo que NO se hará

- No se cambiarán el generador, sus parámetros, las épocas, las semillas ni las fuentes después de ver ninguna corrida.
- No se usará `best.pt`, ni se elegirá otra época.

## 5. Orden de ejecución

1. Mapas de profundidad y lámina de demostración, solo con imágenes de entrenamiento.
2. Generación de `profundidad_train` y del control `profundidad_severa`.
3. Congelamiento **v3.9**: este documento, `argos_lib/profundidad.py`, `32_profundidad.py`, `33_fundacion.py`, `34_h14.py`, el protocolo `prof` de `07_entrenar.py` y los índices de los datos generados.
4. Subida, prueba de humo y 6 corridas en RunPod.
5. Evaluación, veredicto e `informes/reporte_h14.md`. Solo después, el texto.

## 6. Referencia descriptiva: detectores de vocabulario abierto sin ajuste

Se declara aquí, antes de calcularla, una referencia que **no decide ninguna hipótesis**. Responde a qué generaliza mejor a la oclusión real, ya que el aumento sintético no lo hace.

- **Modelos:** OWLv2 (`google/owlv2-base-patch16-ensemble`, consulta «a photo of a person») y Grounding DINO tiny (`IDEA-Research/grounding-dino-tiny`, consulta «a person.»), sin ningún ajuste.
- **Datos y evaluación:** las tres fuentes reales (NightOwls, CityPersons con la convención oficial, proxy de ExDark), con el mismo evaluador, las mismas regiones *ignore* y los mismos estratos (`33_fundacion.py`, autotest 4/4). Se guardan hasta 300 cajas por imagen.
- **Lectura fijada:** se compararán, de forma descriptiva, con el YOLOv11s de COCO sin ajustar y con las V1 y V3 ya entrenadas. Si los modelos de fundación superan a todos en las personas ocluidas, el artículo lo recomendará como referencia obligatoria; si no, se dirá así.
