#!/bin/bash
# ARGOS-11 H15 (v3.10), E12: Faster R-CNN, V1 y V3sil, 30 epocas fijas, semillas 0-2; V1 y V3 de cada semilla en paralelo.
cd /workspace/raw
export YOLO_CONFIG_DIR=/workspace/ultra
mkdir -p $YOLO_CONFIG_DIR
PY=/workspace/venv/bin/python
LOG=/workspace/h15.log
echo "$(date '+%F %T') inicio H15" >> $LOG
for s in 0 1 2; do
  $PY 35_dos_etapas.py entrenar --variante V1 --semilla $s > /workspace/h15_V1_s$s.log 2>&1 &
  P1=$!
  $PY 35_dos_etapas.py entrenar --variante V3 --semilla $s > /workspace/h15_V3_s$s.log 2>&1 &
  P3=$!
  wait $P1 || { echo "FALLO_ENTRENAMIENTO_V1_s$s" >> $LOG; exit 1; }
  wait $P3 || { echo "FALLO_ENTRENAMIENTO_V3_s$s" >> $LOG; exit 1; }
  echo "$(date '+%F %T') semilla $s terminada" >> $LOG
done
echo "$(date '+%F %T') H15_ENTRENAMIENTO_TERMINADO" >> $LOG
