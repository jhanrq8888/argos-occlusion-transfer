# AVISO: esta carpeta MEZCLA ARQUITECTURAS — no citar en el informe final

Generada el 2026-09-13 21:11 por `11_analisis_estadistico.py --resultados resultados_v2`
sobre TODAS las corridas de `runs/argos_v2/`, incluidas las 6 de YOLO26s (`yolo26s_*`).
Como las corridas de YOLO26s llevan las etiquetas V1/V3, en estos ficheros:

- V1 y V3 agrupan 6 semillas (3 YOLOv11s + 3 YOLO26s);
- V2 y V4 tienen 3 semillas (solo YOLOv11s, no existe CBAM para YOLO26s).

Por tanto los contrastes V2-V1, V4-V1 y la interaccion (V4-V3)-(V2-V1) comparan
arquitecturas distintas y NO deben usarse. Los ficheros se conservan sin modificar
como registro de lo ejecutado el 13/09 (trazabilidad), pero el analisis valido de la
iteracion 2 esta en `../analisis_yolo11s/` (solo YOLOv11s, 3 semillas por variante),
generado el 2026-09-19 con `--excluir-prefijo yolo26s_ --subdir analisis_yolo11s`.

Ejemplo de la diferencia (NightOwls ocluida, V3-V1):
  aqui (mezcla):        -15.55 pp, IC95 [-18.21, -12.83]
  analisis_yolo11s:     -16.79 pp, IC95 [-19.59, -13.96]

Las cifras de YOLO26s se reportan por separado como medias por arquitectura
(resumen_ap.csv filtrado por prefijo `yolo26s_`).

Actualizacion 2026-09-19: `diagnostico_transferencia.csv` de esta carpeta tambien mezcla
arquitecturas (promedia por etiqueta de variante). Su version valida esta en
`../analisis_yolo11s/diagnostico_transferencia.csv` (solo YOLOv11s). Con ello, TODOS los
ficheros de `analisis_yolo11s/` sustituyen a los de esta carpeta para la iteracion 2.
