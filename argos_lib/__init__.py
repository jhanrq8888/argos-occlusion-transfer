# -*- coding: utf-8 -*-
"""
ARGOS-11 - biblioteca compartida por los scripts numerados.

Se separa de los scripts por dos motivos: (1) los scripts empiezan por un
numero y no son importables; (2) el DataLoader de Ultralytics en Windows
usa procesos hijos que necesitan importar el transform de oclusion.

Modulos:
    gt         formato comun de ground truth estratificado y utilidades
    ap         AP estilo COCO con regiones ignore (protocolo Seccion 2.4)
    oclusion   generadores de oclusion sintetica (entrenamiento y prueba)
"""
ESTRATOS = ["sin", "ligera", "moderada", "severa"]
LIMITES_ESTRATO = {"sin": (0.0, 0.10), "ligera": (0.10, 0.30),
                   "moderada": (0.30, 0.70), "severa": (0.70, 1.0001)}


def estrato_de_cobertura(f):
    """Asigna estrato a una fraccion cubierta f en [0,1]."""
    for nombre, (a, b) in LIMITES_ESTRATO.items():
        if a <= f < b:
            return nombre
    return "severa" if f >= 1.0 else "sin"
