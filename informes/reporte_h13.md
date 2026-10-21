# ARGOS-11 — Informe de H13: realismo medido de cada familia de oclusor

Fecha: 2026-10-17. Pre-registro: `PREREGISTRO_H13.md`, congelado como **v3.8** antes de generar nada. Hubo un re-congelamiento, **v3.9b**, por un error de ejecución en la extracción de CLIP, ocurrido antes de obtener ningún resultado (ver `CAMBIOS_PROTOCOLO.md`). Veredicto literal en `informes/veredicto_h13.md`; datos en `resultados_h13/analisis/realismo_h13.json`.

## 1. Qué se hizo

- **Muestras de CityPersons val:**
  - 400 personas con **oclusión real** (*heavy*, visibilidad 0,20–0,65);
  - 400 personas **visibles** (*bare*), usadas sin tocar como referencia;
  - las mismas 400 personas visibles, ocluidas por cada familia (parches, siluetas, geometría y generativa) con la cobertura de la oclusión real.
- **Medida:** AUC de un clasificador lineal sobre DINOv2 (primaria) y CLIP, con validación cruzada 5 × 5, que distingue la oclusión real de cada conjunto. **0,5 = indistinguible de la oclusión real**; cuanto más alta, menos realista.

## 2. Resultados (AUC frente a oclusión real; IC 95 % por bootstrap de personas)

| Conjunto | DINOv2 | CLIP |
|---|---|---|
| Personas visibles sin ocluir (referencia) | **0,876** [0,852; 0,897] | **0,831** [0,803; 0,859] |
| Parches (E1) | 0,993 [0,989; 0,996] | 0,993 [0,988; 0,997] |
| Siluetas (E2, E4, E8-S) | 0,950 [0,936; 0,963] | 0,916 [0,896; 0,934] |
| Geometría real (E8-G) | 0,953 [0,938; 0,966] | 0,923 [0,904; 0,940] |
| Generativa (E7, E7b) | 0,935 [0,919; 0,950] | 0,925 [0,907; 0,941] |

Diferencias pre-registradas (DINOv2):
- parches − siluetas: **+0,043** [+0,031; +0,057];
- siluetas − generativa: +0,015 [−0,003; +0,034].

**H13: PARCIALMENTE CONFIRMADA.** Los parches son claramente los menos realistas. Las siluetas, la geometría y la generativa no se distinguen entre sí: con DINOv2 la generativa queda algo mejor, pero su IC incluye el cero, y con CLIP no queda mejor. El KID ordena igual: los parches quedan los más lejanos con los dos extractores.

## 3. Lectura

1. **Ninguna familia sintética se parece a la oclusión real más que no ocluir nada.** Las cuatro familias quedan **más lejos** de la oclusión real que las propias personas visibles sin tocar: diferencias con la referencia de −0,060 a −0,117 con DINOv2 y de −0,086 a −0,162 con CLIP, todas con IC < 0.
   - Dicho de otro modo, pegar un oclusor sintético vuelve a la persona **más distinguible** de una persona realmente ocluida, no menos.
   - Esto concuerda con la falta de transferencia: el detector aprende un tipo de oclusión que la oclusión real no comparte.
2. **La «escalera de realismo» existe solo en su primer peldaño.**
   - De parches a recortes reales (siluetas), el realismo medido sube con claridad.
   - De siluetas a geometría real o a oclusores pintados por difusión, no sube de forma detectable.
   - El artículo debe dejar de presentar las tres familias como una escalera ordenada: hay dos niveles, parches y los demás.
3. **Unido a la transferencia** (descriptivo, sección 2.7 del pre-registro):
   - la familia menos realista (parches, E1) y las más realistas (E7b, E8) tienen el mismo resultado: ninguna mejora robusta en la oclusión real;
   - ganar realismo medido de parches a siluetas no trajo transferencia, y con siluetas el daño en NightOwls fue mayor (E2).

## 4. Salvedades declaradas

- **Generativa:**
  - el control de calidad (la difusión no debe dibujar una persona) rechazó la oclusión en **146 de 400** personas, que quedaron sin ocluir;
  - su cobertura media fue 0,32, frente a 0,55 de la oclusión real.
  - Esas personas sin ocluir se parecen a la referencia (AUC 0,876), lo que **favorece** a la generativa. Su realismo real es, si acaso, menor que el medido.
- **Geometría:** cobertura media 0,47, algo menor que la objetivo.
- **Confusor de tamaño:** la altura de la caja sola separa real y base con AUC 0,619. Afecta por igual a todas las familias, que parten de las mismas personas base, y no explica las diferencias entre ellas.
- **Alcance de la medida:** es indistinguibilidad en dos espacios de características (DINOv2 y CLIP), no realismo percibido por personas.
