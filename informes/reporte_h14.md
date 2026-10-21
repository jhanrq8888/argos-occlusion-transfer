# ARGOS-11 — Informe de H14 (E11: oclusores con orden de profundidad)

Fecha: 2026-10-17.
- **Pre-registro:** `PREREGISTRO_H14.md`, congelado como **v3.9** antes de entrenar. Los re-congelamientos v3.9b y v3.9c afectan solo a los scripts de H13 y de la referencia.
- **Veredicto literal:** `informes/veredicto_h14.md`.

## 1. Qué se hizo

- **Generador** (`argos_lib/profundidad.py`, `32_profundidad.py`, autotest 6/6):
  - recortes de objetos colocados **delante** de la persona, apoyados en el suelo;
  - solo si la profundidad de la escena (Depth Anything V2) permite que estén más cerca que ella;
  - compuestos solo donde la escena está más lejos, de modo que lo que ya tapaba a la persona sigue delante.
- **Datos:** el 89 % de las oclusiones pedidas pudo colocarse delante (3 114 de 3 487), con cobertura media de 0,52. Control `profundidad_severa`: 1 629 personas severas.
- **Entrenamiento:** 6 corridas en RunPod (V1 y V3ᵖʳᵒᶠ, YOLOv11s, semillas 0–2, 30 épocas fijas), con la misma sustitución de imágenes que E7b. Pesos descargados con SHA-256 verificado.
- **Evaluación:** en la laptop, con `34_h14.py`.

## 2. Veredicto (AP@0.5, V3ᵖʳᵒᶠ − V1 en pp)

| Celda | V3 − V1 | IC por imágenes | IC jerárquico |
|---|---|---|---|
| Control `profundidad_severa` | **+7,42** | [+6,40; +8,79] | [+6,13; +9,13] |
| NightOwls ocluida | −1,50 | [−2,75; −0,37] | [−3,40; +0,26] |
| CityPersons *heavy* | −0,16 | [−1,21; +0,75] | [−1,85; +1,31] |
| ExDark proxy severa | +5,49 | [+1,63; +9,30] | [−0,35; +11,14] |

**H14: SOSTENIDA (1 de 3; la regla exige 2).**

## 3. Lectura

1. **El orden de profundidad tampoco cierra la brecha.** El aumento se aprende (+7,42 en su control), pero no mejora NightOwls (−1,50, IC < 0) ni CityPersons (−0,16).
2. **La única celda positiva repite el patrón de E7:**
   - aparece en la fuente más pequeña (ExDark proxy, 101 personas, solo oclusión entre personas);
   - **no resiste el IC jerárquico**;
   - los oclusores de E11 son objetos, no personas.
3. **Con esto se cierra la última explicación que dejaba abierta la discusión del artículo** (la relación del oclusor con la escena).
   - Apariencia (siluetas y generativa), geometría (E8), exposición (E7b, E9), tamaño del modelo (E10) y orden de profundidad (E11) se pusieron a prueba con hipótesis pre-registradas.
   - Ninguna produjo una mejora robusta en la oclusión real.

## 4. Salvedades

- La profundidad es **relativa y monocular** (Depth Anything V2 Small), no métrica.
- El 11 % de las oclusiones no pudo colocarse delante y se omitió.
- El oclusor solo tiene en cuenta el orden de profundidad y el apoyo en el suelo, no la semántica de la escena (por ejemplo, que un coche esté en la calzada).
