# -*- coding: utf-8 -*-
"""
Integracion del aumento de oclusion en el entrenador de Ultralytics.

Se define aqui (modulo importable) porque en Windows los workers del
DataLoader reciben el dataset por pickle y necesitan importar su clase.

DatasetOclusion   YOLODataset cuyo build_transforms inserta el transform
                  de oclusion justo antes de Format. Al sobreescribir
                  build_transforms (y no solo insertar tras construir) el
                  aumento sobrevive a close_mosaic, que reconstruye la
                  cadena en las ultimas epocas.
EntrenadorArgos   DetectionTrainer que usa DatasetOclusion en 'train' cuando
                  la clase tiene configurada `oclusion_cfg`; en 'val' nunca
                  (control de fuga de datos, Seccion 2.4).
"""

import os
from copy import copy

from ultralytics.data import build_dataloader
from ultralytics.data.dataset import YOLODataset
from ultralytics.models.yolo.detect import DetectionTrainer
from ultralytics.models.rtdetr.train import RTDETRTrainer
from ultralytics.models.rtdetr.val import RTDETRDataset
from ultralytics.utils import colorstr

from .oclusion import OclusionEntrenamiento


class DatasetOclusion(YOLODataset):
    """Familias 1 y 2: el aumento es un transform (antes de Format).
    Familia 3 (H9, OclusionGenerativa, nivel='imagen'): no hay transform; load_image
    sustituye la imagen leida por una version ocluida generada de antemano."""

    def __init__(self, *args, oclusion=None, **kwargs):
        self.oclusion = oclusion
        self._sin_mosaico = False
        super().__init__(*args, **kwargs)

    def _nivel_imagen(self):
        return self.oclusion is not None and getattr(self.oclusion, "nivel", None) == "imagen"

    def build_transforms(self, hyp=None):
        t = super().build_transforms(hyp)
        if self.augment and self.oclusion is not None and not self._nivel_imagen():
            t.insert(len(t.transforms) - 1, self.oclusion)   # antes de Format
        return t

    def close_mosaic(self, hyp):
        self._sin_mosaico = True
        super().close_mosaic(hyp)

    def load_image(self, i, rect_mode=True, resize_short=False):
        if self.augment and self._nivel_imagen():
            alt = self.oclusion.sustituta(self.im_files[i], con_mosaico=not self._sin_mosaico)
            if alt is not None:
                # El mosaico elige sus otras 3 imagenes del bufer de indices leidos; Ultralytics
                # anade cada indice al leerlo. Se replica aqui (sin guardar la imagen ocluida en
                # la cache) para que el bufer no quede vacio si la primera lectura es sustituida.
                if self.cache != "ram":
                    self.buffer.append(i)
                    if 1 < len(self.buffer) >= self.max_buffer_length:
                        j = self.buffer.pop(0)
                        self.ims[j], self.im_hw0[j], self.im_hw[j] = None, None, None
                return self._leer_sin_cache(alt, rect_mode)
        return super().load_image(i, rect_mode, resize_short)

    def _leer_sin_cache(self, ruta, rect_mode=True):
        """Mismo redimensionado que BaseDataset.load_image (lado mayor = imgsz), sin
        tocar la cache: la version ocluida no debe quedar guardada como la original."""
        import math
        import cv2
        from ultralytics.utils.patches import imread
        im = imread(ruta, flags=self.cv2_flag)
        if im is None:
            raise FileNotFoundError(ruta)
        h0, w0 = im.shape[:2]
        if rect_mode:
            r = self.imgsz / max(h0, w0)
            if r != 1:
                w, h = (min(math.ceil(w0 * r), self.imgsz), min(math.ceil(h0 * r), self.imgsz))
                im = cv2.resize(im, (w, h), interpolation=cv2.INTER_LINEAR)
        elif not (h0 == w0 == self.imgsz):
            im = cv2.resize(im, (self.imgsz, self.imgsz), interpolation=cv2.INTER_LINEAR)
        if im.ndim == 2:
            im = im[..., None]
        return im, (h0, w0), im.shape[:2]


class EntrenadorArgos(DetectionTrainer):
    """oclusion_cfg (atributo de clase): None -> sin aumento de oclusion;
    dict con las claves de `oclusion_clase` -> se aplica en train.
    oclusion_clase: OclusionEntrenamiento (v1, parches) u OclusionSiluetas (v2)."""
    oclusion_cfg = None
    oclusion_clase = OclusionEntrenamiento

    def build_dataset(self, img_path, mode="train", batch=None):
        if mode != "train" or not self.oclusion_cfg:
            return super().build_dataset(img_path, mode, batch)
        gs = max(int(self.model.stride.max() if self.model else 0), 32)
        cfg = self.args
        return DatasetOclusion(
            img_path=img_path, imgsz=cfg.imgsz, batch_size=batch, augment=True,
            hyp=copy(cfg), rect=cfg.rect, cache=cfg.cache or None,
            single_cls=cfg.single_cls or False, stride=gs, pad=0.0,
            prefix=colorstr("train: "), task=cfg.task, classes=cfg.classes,
            data=self.data, fraction=cfg.fraction,
            oclusion=self.oclusion_clase(**self.oclusion_cfg))


class DatasetOclusionRTDETR(RTDETRDataset):
    """Igual que DatasetOclusion, sobre el dataset de RT-DETR (H8): el aumento de
    oclusion se inserta antes del Format final, con el mismo generador."""

    def __init__(self, *args, oclusion=None, **kwargs):
        self.oclusion = oclusion
        super().__init__(*args, **kwargs)

    def build_transforms(self, hyp=None):
        t = super().build_transforms(hyp)
        if self.augment and self.oclusion is not None:
            t.insert(len(t.transforms) - 1, self.oclusion)   # antes de Format
        return t


class EntrenadorArgosRTDETR(RTDETRTrainer):
    """RTDETRTrainer que usa DatasetOclusionRTDETR en 'train' cuando hay oclusion_cfg.
    Replica los argumentos de RTDETRTrainer.build_dataset (rect=False)."""
    oclusion_cfg = None
    oclusion_clase = OclusionEntrenamiento

    def build_dataset(self, img_path, mode="val", batch=None):
        if mode != "train" or not self.oclusion_cfg:
            return super().build_dataset(img_path, mode, batch)
        cfg = self.args
        return DatasetOclusionRTDETR(
            img_path=img_path, imgsz=cfg.imgsz, batch_size=batch, augment=True,
            hyp=cfg, rect=False, cache=cfg.cache or None,
            single_cls=cfg.single_cls or False, prefix=colorstr("train: "),
            classes=cfg.classes, data=self.data, fraction=cfg.fraction,
            oclusion=self.oclusion_clase(**self.oclusion_cfg))


def es_rtdetr(ruta):
    """True si los pesos o el nombre corresponden a RT-DETR."""
    return "rtdetr" in os.path.basename(os.path.dirname(os.path.dirname(str(ruta)))).lower() or         "rtdetr" in os.path.basename(str(ruta)).lower()


def describir_cadena(dataset):
    """Nombres de los transforms del dataset, para el registro de la corrida."""
    try:
        return [type(t).__name__ for t in dataset.transforms.transforms]
    except AttributeError:
        return []
