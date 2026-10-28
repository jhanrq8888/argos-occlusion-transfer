#!/bin/bash
# ARGOS-11 H18 (v3.12), E14: 16 entrenamientos de 30 epocas fijas en UNA sola maquina, 3 a la vez en la RTX 4090.
#   H18a       Faster R-CNN V1 y V3 siluetas (dosis base), semillas 0-4 -> runs/argos_frcnn_r18_sil/{V1,V3}_sN
#   H18e-baja  Faster R-CNN V3 siluetas, dosis baja, semillas 0-2      -> runs/argos_frcnn_r18_baja/V3_sN
#   H18e-alta  Faster R-CNN V3 siluetas, dosis alta, semillas 0-2      -> runs/argos_frcnn_r18_alta/V3_sN
# Orden: primero las semillas 0-2 de todo (V1, V3 base, baja y alta), luego las semillas 3-4 de H18a. Si el credito se
# acaba, los bloques de dosis quedan completos antes. Las corridas ya terminadas (weights/last.pth) se omiten, asi que
# relanzar el script es seguro.
cd /workspace/raw
export YOLO_CONFIG_DIR=/workspace/ultra
mkdir -p $YOLO_CONFIG_DIR
PY=/workspace/venv/bin/python
LOG=/workspace/h18.log
MAX=3
TAREAS=()
for s in 0 1 2; do
  TAREAS+=("sil_V1_s$s --variante V1 --semilla $s --proyecto argos_frcnn_r18_sil")
  TAREAS+=("sil_V3_s$s --variante V3 --semilla $s --proyecto argos_frcnn_r18_sil")
  TAREAS+=("baja_V3_s$s --variante V3 --dosis baja --semilla $s --proyecto argos_frcnn_r18_baja")
  TAREAS+=("alta_V3_s$s --variante V3 --dosis alta --semilla $s --proyecto argos_frcnn_r18_alta")
done
for s in 3 4; do
  TAREAS+=("sil_V1_s$s --variante V1 --semilla $s --proyecto argos_frcnn_r18_sil")
  TAREAS+=("sil_V3_s$s --variante V3 --semilla $s --proyecto argos_frcnn_r18_sil")
done
echo "$(date '+%F %T') inicio H18 (${#TAREAS[@]} corridas, $MAX en paralelo)" >> $LOG
for t in "${TAREAS[@]}"; do
  while [ "$(jobs -rp | wc -l)" -ge $MAX ]; do wait -n; done
  set -- $t; n=$1; shift
  echo "$(date '+%F %T') lanzada $n" >> $LOG
  ( $PY 35_dos_etapas.py entrenar "$@" > /workspace/h18_$n.log 2>&1 \
      && echo "$(date '+%F %T') terminada $n" >> $LOG || echo "$(date '+%F %T') FALLO_ENTRENAMIENTO_$n" >> $LOG ) &
  sleep 20
done
wait
grep -q FALLO $LOG && echo "$(date '+%F %T') H18_CON_FALLOS" >> $LOG || echo "$(date '+%F %T') H18_ENTRENAMIENTO_TERMINADO" >> $LOG
