#!/bin/bash
# ARGOS-11 H16/H17 (v3.11), E13: 13 entrenamientos de 30 epocas fijas, 3 a la vez en la RTX 4090 (pico ~6 GB cada uno).
#   H17   RetinaNet V1 y V3sil, semillas 0-2                    -> runs/argos_retina/{V1,V3}_sN
#   H16a  Faster R-CNN V3 generativa, semillas 0-2              -> runs/argos_frcnn_gen/V3_sN
#   H16b  Faster R-CNN V3 profundidad, semillas 0-2             -> runs/argos_frcnn_prof/V3_sN
#   rep   Faster R-CNN V1 semilla 0 (replica entre pods)        -> runs/argos_frcnn_rep/V1_s0
# Las corridas ya terminadas (weights/last.pth) se omiten, asi que relanzar el script es seguro.
cd /workspace/raw
export YOLO_CONFIG_DIR=/workspace/ultra
mkdir -p $YOLO_CONFIG_DIR
PY=/workspace/venv/bin/python
LOG=/workspace/h16.log
MAX=3
TAREAS=()
for s in 0 1 2; do
  TAREAS+=("retina_V1_s$s --detector retina --variante V1 --semilla $s")
  TAREAS+=("retina_V3_s$s --detector retina --variante V3 --semilla $s")
done
for s in 0 1 2; do
  TAREAS+=("gen_V3_s$s --familia gen --variante V3 --semilla $s")
  TAREAS+=("prof_V3_s$s --familia prof --variante V3 --semilla $s")
done
TAREAS+=("rep_V1_s0 --variante V1 --semilla 0 --proyecto argos_frcnn_rep")
echo "$(date '+%F %T') inicio H16/H17 (${#TAREAS[@]} corridas, $MAX en paralelo)" >> $LOG
for t in "${TAREAS[@]}"; do
  while [ "$(jobs -rp | wc -l)" -ge $MAX ]; do wait -n; done
  set -- $t; n=$1; shift
  echo "$(date '+%F %T') lanzada $n" >> $LOG
  ( $PY 35_dos_etapas.py entrenar "$@" > /workspace/h16_$n.log 2>&1 \
      && echo "$(date '+%F %T') terminada $n" >> $LOG || echo "$(date '+%F %T') FALLO_ENTRENAMIENTO_$n" >> $LOG ) &
  sleep 20
done
wait
grep -q FALLO $LOG && echo "$(date '+%F %T') H16_CON_FALLOS" >> $LOG || echo "$(date '+%F %T') H16_ENTRENAMIENTO_TERMINADO" >> $LOG
