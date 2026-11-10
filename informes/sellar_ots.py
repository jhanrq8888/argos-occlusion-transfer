#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Sella con OpenTimestamps los registros de hipotesis ya congelados (revision del short paper del 10/11/2026,
obs. 7). Solo se envian a los calendarios publicos los resumenes SHA-256 de los ficheros, no su contenido. Escribe un
fichero .ots junto a cada registro. El sello prueba que el fichero existia en la fecha del sello (11/2026), no antes:
no sustituye a un prerregistro externo hecho antes de entrenar.

En Windows, python-bitcoinlib no encuentra OpenSSL con ctypes.util.find_library; aqui se le indica la libcrypto que
trae la propia instalacion de Python antes de cargar el cliente.
Uso: python informes/sellar_ots.py            (sella)
     python informes/sellar_ots.py --upgrade  (completa los sellos cuando los calendarios los anclan en Bitcoin)
"""
import ctypes.util
import glob
import os
import sys

_orig = ctypes.util.find_library


def _find(name):
    r = _orig(name)
    if r is None and name in ("ssl.35", "ssl", "libeay32"):
        c = glob.glob(os.path.join(sys.base_prefix, "DLLs", "libcrypto-*.dll"))
        return c[0] if c else None
    return r


ctypes.util.find_library = _find

from otsclient.args import parse_ots_args  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHEROS = ["CAMBIOS_PROTOCOLO.md", "protocolo_congelado.json"] + sorted(
    os.path.basename(f) for f in glob.glob(os.path.join(RAIZ, "PREREGISTRO_*.md")))

if __name__ == "__main__":
    os.chdir(RAIZ)
    if "--upgrade" in sys.argv:
        args = parse_ots_args(["upgrade"] + [f + ".ots" for f in FICHEROS if os.path.exists(f + ".ots")])
    else:
        args = parse_ots_args(["stamp"] + [f for f in FICHEROS if not os.path.exists(f + ".ots")])
    args.cmd_func(args)
    print("ficheros:", FICHEROS)
