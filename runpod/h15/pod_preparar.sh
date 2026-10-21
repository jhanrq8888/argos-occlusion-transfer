#!/usr/bin/env bash
# ARGOS-11 H15 (PREREGISTRO_H15.md, v3.10): preparar el entorno en el pod de RunPod.
set -uo pipefail
cd /workspace
[ -d raw ] || tar -xf argos_h15.tar --no-same-owner
cd /workspace/raw
sha256sum -c ../manifiesto_sha256.txt --quiet && echo "MANIFIESTO_OK" || { echo "FALLO_MANIFIESTO"; exit 1; }
sed -i 's#^path: .*#path: /workspace/raw/dataset#' dataset/data_v2.yaml
cat dataset/data_v2.yaml
python -m venv --system-site-packages /workspace/venv
/workspace/venv/bin/pip install -q "ultralytics==8.4.143" pyyaml pandas scipy
/workspace/venv/bin/python -c "import ultralytics, torch, torchvision; print('ultralytics', ultralytics.__version__, '| torch', torch.__version__, '| torchvision', torchvision.__version__, '| cuda', torch.version.cuda, '|', torch.cuda.get_device_name(0))"
export YOLO_CONFIG_DIR=/workspace/ultra; mkdir -p $YOLO_CONFIG_DIR
/workspace/venv/bin/python 35_dos_etapas.py --selftest
nproc; free -g | head -2
echo "PREPARADO"
