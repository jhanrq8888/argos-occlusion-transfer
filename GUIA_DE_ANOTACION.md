# ARGOS-11 — Guía de anotación de oclusión real

Versión 1.1 (validada en el piloto de 50 instancias: kappa ponderado = 0,82).
Esta guía forma parte del protocolo congelado (Sección 2.9 del PPI).

## 1. Qué se anota

Cada instancia del lote es **una persona ya anotada en ExDark** (caja verde
en la herramienta). No se corrige la caja ni se añaden personas nuevas: la
única decisión es **qué fracción de esa caja está tapada por otro objeto**.

Definición operativa (Sección 2.7 del PPI): *oclusión = fracción del área
del bounding box cubierta por un objeto físico situado entre la cámara y la
persona*.

## 2. Regla principal: OSCURIDAD NO ES OCLUSIÓN

ExDark es un dataset de baja iluminación. Una persona puede verse mal por
falta de luz, por ruido, por desenfoque o por contraluz. **Nada de eso es
oclusión.** Antes de marcar un estrato distinto de "sin", contesta a la
pregunta que muestra la herramienta: *¿qué objeto la tapa?* Si no puedes
nombrar el objeto (coche, farola, otra persona, mesa, puerta, mochila...),
la respuesta es **sin oclusión**.

- Sombra sobre el cuerpo → sin oclusión.
- Parte del cuerpo en negro por falta de luz → sin oclusión.
- Silueta borrosa por movimiento → sin oclusión.
- Ropa oscura que se confunde con el fondo → sin oclusión.

Si la oscuridad es tan extrema que **no puedes decidir si hay o no un
objeto delante**, usa *no evaluable* (Sección 5), nunca un estrato.

## 3. Estratos (fracción del área de la caja tapada)

| Tecla | Estrato       | Fracción tapada | Cómo reconocerlo                                   |
|-------|---------------|-----------------|----------------------------------------------------|
| 1     | sin           | menos del 10 %  | Todo el cuerpo visible, o solo un borde tapado     |
| 2     | ligera        | 10 % – 29 %     | Falta una parte pequeña: pies, una mano, un hombro |
| 3     | moderada      | 30 % – 69 %     | Falta aproximadamente la mitad: piernas enteras, o medio torso |
| 4     | severa        | 70 % – 100 %    | Solo se ve cabeza/hombros, o una franja del cuerpo |

Ayudas para estimar la fracción:

- Divide mentalmente la caja en **tres bandas horizontales** (cabeza-hombros,
  torso, piernas) de tamaño parecido. Una banda tapada ≈ 30 %; dos ≈ 65 %.
- Piernas tapadas por un coche o una mesa → normalmente **moderada**.
- Solo asoma la cabeza por encima de algo → **severa**.
- Otra persona delante que tapa parte del torso → estima por bandas.

Los límites (10 %, 30 %, 70 %) coinciden con los estratos de evaluación del
protocolo. En caso de duda **entre dos estratos vecinos**, elige el más
bajo (menos oclusión): el sesgo sistemático es preferible al sesgo
aleatorio, y el kappa ponderado penaliza poco el desacuerdo vecino.

## 4. Truncado por borde (tecla T)

Si parte de la persona queda **fuera del encuadre de la imagen**, marca
*truncado*. El truncamiento **no es oclusión** y se registra en un campo
aparte: estima el estrato solo con lo que hay dentro del encuadre. Puede
combinarse con cualquier estrato.

## 5. No evaluable (tecla 0)

Reservado para tres situaciones:

1. La caja no contiene claramente una persona (error de ExDark).
2. La caja es tan pequeña u oscura que **no se puede juzgar** si hay un
   objeto delante.
3. La caja agrupa a varias personas y no se puede decidir sobre una.

Las instancias *no evaluables* se excluyen del kappa y de la evaluación
(se tratan como región *ignore*). No abuses de ella: si puedes decidir,
decide.

## 6. Procedimiento

1. Trabaja **solo**, sin consultar al otro anotador, y sin ver sus
   respuestas. La independencia es lo que da sentido al kappa.
2. Sigue el orden del lote (está fijado por semilla; no lo cambies).
3. Dedica el tiempo necesario, pero no más de ~30 s por instancia: si tras
   ese tiempo no puedes decidir, es *no evaluable*.
4. Exporta el CSV al terminar cada sesión (puede reanudarse cargándolo).
5. Las discrepancias se resuelven después, **por consenso y con esta guía
   delante**, en `discrepancias.csv` (columna `consenso`).

## 7. Casos frecuentes del piloto

Estos casos produjeron desacuerdos en el piloto y se fijan aquí:

- **Persona sentada tras una mesa**: piernas y parte del torso tapadas →
  *moderada* (no severa, salvo que solo asome la cabeza).
- **Persona parcialmente fuera de encuadre y además tras un coche**:
  *truncado* + estrato según lo tapado por el coche dentro del encuadre.
- **Dos personas superpuestas**: la de atrás se anota según lo que tape la
  de delante; la de delante normalmente es *sin*.
- **Objeto sostenido en la mano (bolsa, móvil, bebida)**: no cuenta como
  oclusión salvo que tape una banda entera (raro) → normalmente *sin*.
- **Reflejo, humo o lluvia sobre la lente**: no es un objeto físico
  interpuesto → *sin* o *no evaluable* si impide juzgar.
