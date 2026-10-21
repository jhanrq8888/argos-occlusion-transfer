#!/usr/bin/env bash
# ARGOS-11 H12 (PREREGISTRO_H12.md, v3.7): preparar el entorno en el pod de RunPod.
set -uo pipefail
cd /workspace
[ -d raw ] || tar -xf argos_h12.tar --no-same-owner
cd /workspace/raw
# 1) Ficheros identicos a los de la laptop (manifiesto calculado alli)
sha256sum -c ../manifiesto_sha256.txt --quiet && echo "MANIFIESTO_OK" || { echo "FALLO_MANIFIESTO"; exit 1; }
# 2) Ruta de Windows -> Linux en el yaml de datos (sin cambiar los datos)
sed -i 's#^path: .*#path: /workspace/raw/dataset#' dataset/data_v2.yaml
cat dataset/data_v2.yaml
# 3) Entorno aislado con la misma version de Ultralytics que todo el proyecto (PEP 668 bloquea pip global)
python -m venv --system-site-packages /workspace/venv
/workspace/venv/bin/pip install -q "ultralytics==8.4.143" pyyaml pandas scipy
/workspace/venv/bin/python -c "import ultralytics, torch; print('ultralytics', ultralytics.__version__, '| torch', torch.__version__, '| cuda', torch.version.cuda, '|', torch.cuda.get_device_name(0))"
nproc; free -g | head -2
echo "PREPARADO"
