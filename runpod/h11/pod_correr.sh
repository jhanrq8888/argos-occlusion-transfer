#!/usr/bin/env bash
# ARGOS-11 H11: las 6 corridas en el orden pre-registrado (V1_s3, V3_s3, V1_s4, V3_s4, V1_s5, V3_s5).
# Reanudable: 07_ omite las corridas terminadas y reanuda la que estaba a medias desde last.pt.
cd /workspace/raw
LOG=/workspace/h11.log
echo "$(date '+%F %T') inicio H11" >> $LOG
for s in 3 4 5; do
  python 07_entrenar.py --protocolo cp --variantes V1 V3 --semillas $s --epochs 60 --patience 0 \
         --proyecto argos_cp_fijo --workers 8 >> $LOG 2>&1 || { echo "FALLO_ENTRENAMIENTO_s$s" >> $LOG; exit 1; }
done
echo "$(date '+%F %T') H11_ENTRENAMIENTO_TERMINADO" >> $LOG
