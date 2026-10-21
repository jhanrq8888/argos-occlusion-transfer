# -*- coding: utf-8 -*-
"""
Componente 1: bloque de atencion canal-espacial basado en CBAM (Woo et al.,
2018), y su registro en el parser de modelos de Ultralytics.

Se implementa el bloque tal como lo describe el articulo original, en lugar
de reutilizar `ultralytics.nn.modules.conv.CBAM`, porque esa version omite
dos elementos del diseno original y triplica el coste:
  - rama de canal: el original combina Global Average Pooling y Global Max
    Pooling a traves de un MLP compartido con reduccion r=16; la de
    Ultralytics usa solo GAP y una conv 1x1 sin reduccion (c*c params).
  - rama espacial: identica (media y maximo por canal -> conv 7x7 -> sigmoid).
Con r=16 el bloque anade ~43k parametros a YOLOv11s (0,46 %) frente a los
~345k de la version de Ultralytics. Ajustes respecto al bloque estandar:
ninguno mas alla de la posicion de insercion (ver 06_modelo_atencion.py).

`parse_model` resuelve los nombres del YAML con `globals()` de
ultralytics.nn.tasks, asi que cualquier proceso que construya el modelo
desde YAML (06, 07 y la evaluacion cuando recompone el checkpoint) debe
llamar antes a registrar_cbam().
"""

import torch
import torch.nn as nn


class AtencionCanal(nn.Module):
    """M_c(F) = sigmoid(MLP(AvgPool(F)) + MLP(MaxPool(F)))."""

    def __init__(self, c1, r=16):
        super().__init__()
        oculto = max(1, c1 // r)
        self.mlp = nn.Sequential(nn.Conv2d(c1, oculto, 1, bias=False), nn.ReLU(inplace=True),
                                 nn.Conv2d(oculto, c1, 1, bias=False))

    def forward(self, x):
        a = self.mlp(torch.mean(x, dim=(2, 3), keepdim=True))
        m = self.mlp(torch.amax(x, dim=(2, 3), keepdim=True))
        return x * torch.sigmoid(a + m)


class AtencionEspacial(nn.Module):
    """M_s(F) = sigmoid(conv_kxk([mean_c(F); max_c(F)]))."""

    def __init__(self, k=7):
        super().__init__()
        self.conv = nn.Conv2d(2, 1, k, padding=k // 2, bias=False)

    def forward(self, x):
        s = torch.cat([torch.mean(x, dim=1, keepdim=True),
                       torch.amax(x, dim=1, keepdim=True)], dim=1)
        return x * torch.sigmoid(self.conv(s))


class CBAMArgos(nn.Module):
    """CBAM secuencial: primero canal, despues espacial (Woo et al., 2018).
    Firma (c1, k, r) para el YAML: [-1, 1, CBAMArgos, [128, 7, 16]]."""

    def __init__(self, c1, k=7, r=16):
        super().__init__()
        self.canal = AtencionCanal(c1, r)
        self.espacial = AtencionEspacial(k)

    def forward(self, x):
        return self.espacial(self.canal(x))


def registrar_cbam():
    """Hace visible CBAMArgos para parse_model (idempotente)."""
    import ultralytics.nn.tasks as tasks
    if getattr(tasks, "CBAMArgos", None) is not CBAMArgos:
        tasks.CBAMArgos = CBAMArgos
    return CBAMArgos
