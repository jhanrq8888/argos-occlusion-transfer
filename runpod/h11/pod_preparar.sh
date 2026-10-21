#!/usr/bin/env bash
# ARGOS-11 H11 (PREREGISTRO_H11.md, v3.6b): preparar el entorno en el pod de RunPod.
set -euo pipefail
cd /workspace
[ -d raw ] || tar -xf argos_h11.tar
cd /workspace/raw
# 1) Comprobar que los ficheros llegaron identicos (manifiesto calculado en la laptop)
sha256sum -c ../manifiesto_sha256.txt --quiet && echo "MANIFIESTO_OK"
# 2) Rutas de Windows -> Linux (sin cambiar el contenido de los datos)
for f in dataset_cp/train.txt dataset_cp/val_interno.txt; do
  sed -i 's#^D:/argos11/raw/#/workspace/raw/#' "$f"
done
sed -i 's#^path: .*#path: /workspace/raw/dataset_cp#' dataset/data_citypersons.yaml
grep -c "^/workspace/raw/" dataset_cp/train.txt dataset_cp/val_interno.txt
head -3 dataset/data_citypersons.yaml
# 3) Entorno: la misma version de Ultralytics que en todo el proyecto
pip install -q "ultralytics==8.4.143" pyyaml pandas scipy
python -c "import ultralytics, torch; print('ultralytics', ultralytics.__version__, '| torch', torch.__version__, '| cuda', torch.version.cuda, '|', torch.cuda.get_device_name(0))"
nproc; free -g | head -2
echo "PREPARADO"
