#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Arma el paquete de pesos de la evidencia primaria para Zenodo (revision del short paper del 10/11/2026,
obs. 8): un zip por bloque (sin comprimir, los pesos ya lo estan), el manifiesto SHA-256 y un README.
Solo copia los ficheros listados en informes/analisis_final/pesos_sha256.csv y comprueba su SHA-256 antes de empaquetar.
Salida: D:\\argos11\\zenodo_pesos\\ (fuera de los repositorios)
Uso: python informes/paquete_zenodo_pesos.py
"""
import csv
import hashlib
import os
import shutil
import zipfile
from collections import defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(os.path.dirname(RAIZ), "zenodo_pesos")
MAN = os.path.join(RAIZ, "informes", "analisis_final", "pesos_sha256.csv")
NOMBRE = {"H9b": "H9b_yolo11s_difusion", "H10": "H10_yolo11s_geometria", "H10-s": "H10s_yolo11s_siluetas",
          "H11": "H11_yolo11s_citypersons_60ep", "H12a": "H12a_yolo11m_siluetas", "H12a/H12b": "H12_yolo11m_V1_y_difusion",
          "H14": "H14_yolo11s_profundidad", "H15": "H15_fasterrcnn_siluetas", "H16a": "H16a_fasterrcnn_difusion",
          "H16b": "H16b_fasterrcnn_profundidad", "H17": "H17_retinanet_siluetas", "H18a": "H18a_fasterrcnn_siluetas_5semillas",
          "H18e-b": "H18e_fasterrcnn_dosis_baja", "H18e-a": "H18e_fasterrcnn_dosis_alta"}

README = """# ARGOS-11: pesos de la evidencia primaria

Pesos entrenados (V1 sin aumento de oclusión y V3 con aumento) de los bloques con épocas fijas (H9b–H18) del estudio
«Mejorar sobre oclusión sintética no basta: estudio controlado de la transferencia a la oclusión real en la detección de
personas» (Apaza Hilasaca, Condori Quispe y Ramos Quispe, Universidad Peruana Unión, 2026).

Código, protocolos, registros y resultados: https://github.com/jhanrq8888/argos-occlusion-transfer

## Contenido

- Un zip por bloque. Dentro, `<carpeta de la corrida>/<variante>_s<semilla>/weights/last.pt` (YOLO y RT-DETR,
  Ultralytics 8.4.143) o `last.pth` (Faster R-CNN y RetinaNet, torchvision 0.23, ResNet-50 FPN v2).
- `pesos_sha256.csv`: bloque, corrida, ruta, tamaño y SHA-256 de cada fichero.
- Son los pesos de la última época, los mismos que se evaluaron en el artículo.

## Uso

- YOLO: `from ultralytics import YOLO; m = YOLO("last.pt")`.
- torchvision: construir el modelo con `construir_modelo(pesos_coco=None, detector="frcnn")` (o `"retina"`) de
  `35_dos_etapas.py` en el repositorio, que deja la cabeza con 2 clases, y cargar `model.load_state_dict(torch.load("last.pth"))`.
- Verificación: `sha256sum` de cada fichero frente a `pesos_sha256.csv`.

## Licencia y datos

Los modelos se ajustaron a partir de pesos públicos de COCO con ExDark, CityPersons (H11) y otras fuentes de licencia de
investigación no comercial. Por eso los pesos se publican con licencia CC BY-NC 4.0, solo para investigación no
comercial. No se incluye ninguna imagen de los conjuntos.

## Bloques

| Zip | Hipótesis | Detector | Oclusor |
|---|---|---|---|
{filas}
"""


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    os.makedirs(DEST, exist_ok=True)
    filas = list(csv.DictReader(open(MAN, encoding="utf-8")))
    por = defaultdict(list)
    for f in filas:
        por[f["bloque"]].append(f)
    tabla = []
    for bloque, fs in por.items():
        nombre = "argos11_pesos_%s.zip" % NOMBRE[bloque]
        with zipfile.ZipFile(os.path.join(DEST, nombre), "w", compression=zipfile.ZIP_STORED) as z:
            for f in fs:
                p = os.path.join(RAIZ, f["ruta"])
                if sha(p) != f["sha256"]:
                    raise SystemExit("SHA-256 distinto: " + f["ruta"])
                z.write(p, arcname=f["ruta"].replace("runs/", "", 1))
        partes = NOMBRE[bloque].split("_")
        tabla.append("| `%s` | %s | %s | %s |" % (nombre, bloque, partes[1], " ".join(partes[2:])))
        print(nombre, len(fs), "ficheros")
    shutil.copy2(MAN, os.path.join(DEST, "pesos_sha256.csv"))
    open(os.path.join(DEST, "README.md"), "w", encoding="utf-8").write(README.replace("{filas}", "\n".join(tabla)))
    total = sum(os.path.getsize(os.path.join(DEST, x)) for x in os.listdir(DEST))
    print("listo:", DEST, round(total / 2 ** 30, 2), "GiB")


if __name__ == "__main__":
    main()
