#!/usr/bin/env bash
# Prueba de humo: 1 epoca con el 5 % de los datos (no forma parte de H11).
set -euo pipefail
cd /workspace/raw
python 07_entrenar.py --protocolo cp --smoke --variantes V3 --semillas 3 --workers 4 --proyecto smoke_h11 2>&1 | tail -25
grep -A12 '"cadena_transforms_train"' runs/smoke_h11/V3_s3_smoke/registro_argos.json | head -12
