#!/bin/bash
# ARGOS-11 H12 (v3.7b): E10, 9 corridas YOLOv11m, y extension de semillas 3-4 de YOLOv11s (6 corridas).
# 30 epocas fijas; por semilla: V1 y V3gen (prot. gen), V3sil (prot. v2).
cd /workspace/raw
export YOLO_CONFIG_DIR=/workspace/ultra
mkdir -p $YOLO_CONFIG_DIR
PY=/workspace/venv/bin/python
LOG=/workspace/h12.log
echo "$(date '+%F %T') inicio H12" >> $LOG
for s in 0 1 2; do
  $PY 07_entrenar.py --protocolo gen --modelo-base yolo11m.pt --variantes V1 V3 --semillas $s --epochs 30 --patience 0 \
      --proyecto argos_m_gen --workers 8 >> $LOG 2>&1 || { echo "FALLO_ENTRENAMIENTO_GEN_s$s" >> $LOG; exit 1; }
  $PY 07_entrenar.py --protocolo v2 --modelo-base yolo11m.pt --variantes V3 --semillas $s --epochs 30 --patience 0 \
      --proyecto argos_m_sil --workers 8 >> $LOG 2>&1 || { echo "FALLO_ENTRENAMIENTO_SIL_s$s" >> $LOG; exit 1; }
done
echo "$(date '+%F %T') E10_TERMINADO" >> $LOG
for s in 3 4; do
  $PY 07_entrenar.py --protocolo gen --variantes V1 V3 --semillas $s --epochs 30 --patience 0 \
      --proyecto argos_gen_fijo_s34 --workers 8 >> $LOG 2>&1 || { echo "FALLO_ENTRENAMIENTO_S34_GEN_s$s" >> $LOG; exit 1; }
  $PY 07_entrenar.py --protocolo v2 --variantes V3 --semillas $s --epochs 30 --patience 0 \
      --proyecto argos_sil_fijo_s34 --workers 8 >> $LOG 2>&1 || { echo "FALLO_ENTRENAMIENTO_S34_SIL_s$s" >> $LOG; exit 1; }
done
echo "$(date '+%F %T') H12_ENTRENAMIENTO_TERMINADO" >> $LOG
