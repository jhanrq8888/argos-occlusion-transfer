#!/bin/bash
# ARGOS-11 H14 (v3.9), E11: V1 y V3prof, YOLOv11s, 30 epocas fijas, semillas 0-2, en la misma 4090.
cd /workspace/raw
export YOLO_CONFIG_DIR=/workspace/ultra
PY=/workspace/venv/bin/python
LOG=/workspace/h14.log
echo "$(date '+%F %T') inicio H14" >> $LOG
for s in 0 1 2; do
  $PY 07_entrenar.py --protocolo prof --variantes V1 V3 --semillas $s --epochs 30 --patience 0 \
      --proyecto argos_prof --workers 8 >> $LOG 2>&1 || { echo "FALLO_ENTRENAMIENTO_s$s" >> $LOG; exit 1; }
done
echo "$(date '+%F %T') H14_ENTRENAMIENTO_TERMINADO" >> $LOG
