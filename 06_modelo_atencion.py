#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Paso 4: modulo de atencion canal-espacial (Componente 1).

Inserta tres bloques CBAM (Woo et al., 2018; implementacion propia fiel al
articulo, ver argos_lib/atencion.py) en el neck de YOLOv11s, uno por escala
de salida (P3, P4, P5), entre la FPN/PAN y el cabezal Detect. Decisiones
documentadas:

  * Posicion: a la salida de cada rama del neck (capas 16, 19 y 22 del YAML
    oficial), justo antes de Detect. Es el punto donde las tres escalas ya
    integran informacion de arriba y abajo y donde la ponderacion espacial
    puede resaltar siluetas parcialmente visibles antes de la regresion.
  * Numero de bloques: 3 (uno por escala). Un bloque por escala mantiene el
    coste minimo y evita que el factor VI1 se confunda con "mas capacidad".
  * Kernel espacial 7x7 y reduccion r=16 (valores del articulo original).
  * Canales explicitos (128/256/512): CBAM no esta en la lista de modulos
    que Ultralytics escala por 'width', asi que el YAML fija los canales de
    la escala 's'. El YAML es especifico de YOLOv11s, que es la unica
    arquitectura del estudio.

Politica de pesos (Seccion 2.3.1): los pesos COCO de yolo11s.pt se
transfieren a TODAS las capas comunes; como Detect pasa del indice 23 al
26, la transferencia se hace por nombre remapeado para que V2/V4 partan
exactamente de los mismos pesos que V1/V3. Los bloques CBAM (nuevos) se
inicializan al azar. Se guarda weights/yolo11s_cbam_coco.pt.

Uso:
    python 06_modelo_atencion.py                # genera YAML + pesos iniciales
    python 06_modelo_atencion.py --selftest
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argos_lib.atencion import registrar_cbam          # noqa: E402

YAML_CBAM = """# ARGOS-11 - YOLOv11s + CBAM en el neck (V2 / V4)
# Derivado de ultralytics/cfg/models/11/yolo11.yaml (escala s). Los canales
# de CBAM son explicitos porque el modulo no se escala por 'width'.
nc: 1
scales:
  s: [0.50, 0.50, 1024]

backbone:
  - [-1, 1, Conv, [64, 3, 2]] # 0-P1/2
  - [-1, 1, Conv, [128, 3, 2]] # 1-P2/4
  - [-1, 2, C3k2, [256, False, 0.25]]
  - [-1, 1, Conv, [256, 3, 2]] # 3-P3/8
  - [-1, 2, C3k2, [512, False, 0.25]]
  - [-1, 1, Conv, [512, 3, 2]] # 5-P4/16
  - [-1, 2, C3k2, [512, True]]
  - [-1, 1, Conv, [1024, 3, 2]] # 7-P5/32
  - [-1, 2, C3k2, [1024, True]]
  - [-1, 1, SPPF, [1024, 5]] # 9
  - [-1, 2, C2PSA, [1024]] # 10

head:
  - [-1, 1, nn.Upsample, [None, 2, "nearest"]]
  - [[-1, 6], 1, Concat, [1]] # cat backbone P4
  - [-1, 2, C3k2, [512, False]] # 13

  - [-1, 1, nn.Upsample, [None, 2, "nearest"]]
  - [[-1, 4], 1, Concat, [1]] # cat backbone P3
  - [-1, 2, C3k2, [256, False]] # 16 (P3/8-small)

  - [-1, 1, Conv, [256, 3, 2]]
  - [[-1, 13], 1, Concat, [1]] # cat head P4
  - [-1, 2, C3k2, [512, False]] # 19 (P4/16-medium)

  - [-1, 1, Conv, [512, 3, 2]]
  - [[-1, 10], 1, Concat, [1]] # cat head P5
  - [-1, 2, C3k2, [1024, True]] # 22 (P5/32-large)

  # --- Componente 1: atencion canal-espacial (CBAM, kernel 7) -----------
  - [16, 1, CBAMArgos, [128, 7, 16]] # 23  atencion sobre P3 (128 canales en escala s)
  - [19, 1, CBAMArgos, [256, 7, 16]] # 24  atencion sobre P4
  - [22, 1, CBAMArgos, [512, 7, 16]] # 25  atencion sobre P5

  - [[23, 24, 25], 1, Detect, [nc]] # Detect(P3, P4, P5)
"""

# Capa de Detect en el YAML oficial y en el YAML con CBAM.
DETECT_BASE, DETECT_CBAM = 23, 26


def escribir_yaml(ruta):
    os.makedirs(os.path.dirname(ruta) or ".", exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write(YAML_CBAM)


def remapear(clave):
    """'model.23.xxx' (Detect base) -> 'model.26.xxx' (Detect con CBAM)."""
    partes = clave.split(".")
    if len(partes) > 2 and partes[0] == "model" and partes[1] == str(DETECT_BASE):
        partes[1] = str(DETECT_CBAM)
    return ".".join(partes)


def transferir(modelo_destino, sd_origen, remap=True):
    """Copia por nombre (remapeado si remap) y forma. Devuelve (copiados,
    omitidos)."""
    sd_dst = modelo_destino.state_dict()
    nuevo, copiados, omitidos = {}, 0, []
    for k, v in sd_origen.items():
        k2 = remapear(k) if remap else k
        if k2 in sd_dst and sd_dst[k2].shape == v.shape:
            nuevo[k2] = v
            copiados += 1
        else:
            omitidos.append(k)
    modelo_destino.load_state_dict(nuevo, strict=False)
    return copiados, omitidos


def construir(pesos_coco="yolo11s.pt", ruta_yaml="modelos/yolo11s-cbam.yaml",
              salida="weights/yolo11s_cbam_coco.pt", verbose=True):
    import torch
    from ultralytics import YOLO
    from ultralytics.nn.tasks import DetectionModel

    registrar_cbam()
    escribir_yaml(ruta_yaml)
    base = YOLO(pesos_coco)
    sd_coco = {k: v.float() for k, v in base.model.state_dict().items()}

    # Referencia: cuantos tensores transfiere V1 (misma politica, nc=1).
    ref = DetectionModel("yolo11s.yaml", nc=1, verbose=False)
    cop_ref, om_ref = transferir(ref, sd_coco, remap=False)

    cbam = YOLO(ruta_yaml)
    cop, om = transferir(cbam.model, sd_coco)
    n_cbam = sum(p.numel() for n, p in cbam.model.named_parameters()
                 if n.startswith(tuple("model.%d." % i for i in (23, 24, 25))))
    n_total = sum(p.numel() for p in cbam.model.parameters())
    n_base = sum(p.numel() for p in ref.parameters())

    # Comprobacion funcional: salida con la forma esperada.
    cbam.model.eval()
    with torch.no_grad():
        y = cbam.model(torch.zeros(1, 3, 640, 640))
    forma = tuple(y[0].shape) if isinstance(y, (list, tuple)) else tuple(y.shape)

    os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
    cbam.model.train()
    cbam.save(salida)

    info = {"yaml": ruta_yaml, "salida": salida, "tensores_copiados": cop,
            "tensores_omitidos": om, "referencia_v1_copiados": cop_ref,
            "referencia_v1_omitidos": om_ref, "params_total": n_total,
            "params_cbam": n_cbam, "params_base": n_base, "forma_salida": forma}
    if verbose:
        print("=" * 62)
        print("YOLOv11s + CBAM (Componente 1)")
        print("=" * 62)
        print("  YAML                  : %s" % ruta_yaml)
        print("  parametros base (V1)  : %s" % format(n_base, ","))
        print("  parametros CBAM       : %s  (+%.2f %%)"
              % (format(n_cbam, ","), 100.0 * n_cbam / n_base))
        print("  parametros total (V2) : %s" % format(n_total, ","))
        print("  tensores COCO copiados: %d  (V1 de referencia: %d)" % (cop, cop_ref))
        print("  omitidos (nc 80->1)   : %s" % (om or "-"))
        print("  salida forward 640    : %s" % (forma,))
        print("  pesos iniciales       : %s" % salida)
        if cop != cop_ref or om != om_ref:
            print("\n  AVISO: la transferencia difiere de la de V1. Revisar.")
        else:
            print("\n  Transferencia identica a V1 salvo los bloques CBAM: OK.")
    return info


def selftest():
    print("--- construyendo el modelo con atencion ---\n")
    import tempfile
    tmp = tempfile.mkdtemp(prefix="cbam_test_")
    pesos = "yolo11s.pt" if os.path.exists("yolo11s.pt") else "yolo11s.pt"
    info = construir(pesos, os.path.join(tmp, "yolo11s-cbam.yaml"),
                     os.path.join(tmp, "cbam.pt"))
    print("\n" + "=" * 58 + "\nVERIFICACION\n" + "=" * 58)
    fallos = []

    def comp(desc, obt, esp):
        ok = obt == esp
        print("  [%s] %-46s %s" % ("ok" if ok else "FALLA", desc, obt))
        if not ok:
            fallos.append(desc)

    comp("remapeo de Detect", remapear("model.23.cv2.0.0.conv.weight"),
         "model.26.cv2.0.0.conv.weight")
    comp("remapeo no toca otras capas", remapear("model.2.cv1.conv.weight"),
         "model.2.cv1.conv.weight")
    comp("misma cantidad de tensores COCO que V1",
         info["tensores_copiados"], info["referencia_v1_copiados"])
    comp("mismos tensores omitidos que V1",
         info["tensores_omitidos"], info["referencia_v1_omitidos"])
    comp("CBAM anade parametros", info["params_cbam"] > 0, True)
    comp("CBAM pesa menos del 1% del modelo",
         info["params_cbam"] < 0.01 * info["params_base"], True)
    comp("salida Detect: 1 clase -> 5 canales (4 box + 1 cls)",
         info["forma_salida"][1], 5)
    # El .pt guardado se puede recargar y usar para entrenar.
    from ultralytics import YOLO
    registrar_cbam()
    m = YOLO(os.path.join(tmp, "cbam.pt"))
    tipos = [type(x).__name__ for x in m.model.model]
    comp("checkpoint recargable con 3 CBAM", tipos.count("CBAMArgos"), 3)
    comp("Detect en la capa 26", tipos[DETECT_CBAM], "Detect")
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO: 9/9 comprobaciones.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - modulo de atencion")
    ap.add_argument("--pesos", default="yolo11s.pt", help="pesos COCO base")
    ap.add_argument("--yaml", default="modelos/yolo11s-cbam.yaml")
    ap.add_argument("--salida", default="weights/yolo11s_cbam_coco.pt")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    construir(args.pesos, args.yaml, args.salida)


if __name__ == "__main__":
    main()
