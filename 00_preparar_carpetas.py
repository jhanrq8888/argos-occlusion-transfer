#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Paso 0: descomprimir y normalizar la estructura de ExDark.

Busca los ZIP y el imageclasslist.txt donde esten dentro de la raiz, los
descomprime y corrige el anidamiento tipico de Windows
(raw/ExDark/ExDark/Bicycle -> raw/ExDark/Bicycle).

Uso:
    python 00_preparar_carpetas.py --raiz .
    python 00_preparar_carpetas.py --selftest

Al terminar deja:
    <raiz>/ExDark/<12 carpetas de clase>
    <raiz>/ExDark_Annno/<12 carpetas de clase>
    <raiz>/imageclasslist.txt
"""

import argparse
import os
import shutil
import sys
import tempfile
import zipfile

CLASES = ["Bicycle", "Boat", "Bottle", "Bus", "Car", "Cat", "Chair",
          "Cup", "Dog", "Motorbike", "People", "Table"]
MIN_CLASES = 8          # cuantas carpetas de clase bastan para reconocer el dir


def buscar(raiz, nombre):
    """Busca un fichero por nombre (sin distinguir mayusculas) bajo la raiz."""
    for base, _dirs, ficheros in os.walk(raiz):
        for f in ficheros:
            if f.lower() == nombre.lower():
                return os.path.join(base, f)
    return None


def localizar_dir_clases(inicio):
    """Devuelve el directorio que contiene las carpetas de clase de ExDark.

    Resuelve el anidamiento: tras descomprimir, las clases pueden estar en
    <inicio>, en <inicio>/ExDark, o mas abajo.
    """
    objetivo = {c.lower() for c in CLASES}
    mejor, mejor_n = None, 0
    for base, dirs, _f in os.walk(inicio):
        hallados = len({d.lower() for d in dirs} & objetivo)
        if hallados > mejor_n:
            mejor, mejor_n = base, hallados
    return (mejor, mejor_n) if mejor_n >= MIN_CLASES else (None, mejor_n)


def ya_correcto(destino):
    """True si el destino ya contiene las carpetas de clase directamente."""
    if not os.path.isdir(destino):
        return False
    presentes = {d.lower() for d in os.listdir(destino)
                 if os.path.isdir(os.path.join(destino, d))}
    return len(presentes & {c.lower() for c in CLASES}) >= MIN_CLASES


def desplegar(raiz, nombre_zip, destino_final, etiqueta):
    """Descomprime un ZIP y deja sus carpetas de clase en destino_final."""
    if ya_correcto(destino_final):
        n = len([d for d in os.listdir(destino_final)
                 if os.path.isdir(os.path.join(destino_final, d))])
        print("  [ya listo] %-16s %d carpetas de clase" % (etiqueta, n))
        return True

    ruta_zip = buscar(raiz, nombre_zip)
    if ruta_zip is None:
        print("  [FALTA]    %-16s no se encuentra %s" % (etiqueta, nombre_zip))
        return False

    tam = os.path.getsize(ruta_zip) / (1024.0 * 1024.0)
    print("  [extrae]   %-16s %s (%.0f MB)"
          % (etiqueta, os.path.relpath(ruta_zip, raiz), tam))

    tmp = tempfile.mkdtemp(prefix="exdark_", dir=raiz)
    try:
        with zipfile.ZipFile(ruta_zip) as z:
            z.extractall(tmp)
    except zipfile.BadZipFile:
        shutil.rmtree(tmp, ignore_errors=True)
        print("  [ERROR]    %-16s el ZIP esta corrupto; volver a descargarlo"
              % etiqueta)
        return False

    origen, n = localizar_dir_clases(tmp)
    if origen is None:
        shutil.rmtree(tmp, ignore_errors=True)
        print("  [ERROR]    %-16s solo se hallaron %d carpetas de clase"
              % (etiqueta, n))
        return False

    # El destino puede existir conteniendo solo el ZIP: se vacia antes.
    if os.path.isdir(destino_final):
        for e in os.listdir(destino_final):
            p = os.path.join(destino_final, e)
            if os.path.isdir(p):
                shutil.rmtree(p, ignore_errors=True)
    else:
        os.makedirs(destino_final)

    for e in os.listdir(origen):
        shutil.move(os.path.join(origen, e), os.path.join(destino_final, e))
    shutil.rmtree(tmp, ignore_errors=True)

    print("  [ok]       %-16s %d carpetas de clase colocadas" % (etiqueta, n))
    return True


def preparar(raiz):
    raiz = os.path.abspath(raiz)
    print("Raiz: %s\n" % raiz)

    ok_img = desplegar(raiz, "ExDark.zip",
                       os.path.join(raiz, "ExDark"), "ExDark")
    ok_ann = desplegar(raiz, "ExDark_Annno.zip",
                       os.path.join(raiz, "ExDark_Annno"), "ExDark_Annno")

    # imageclasslist.txt
    destino_lista = os.path.join(raiz, "imageclasslist.txt")
    if os.path.exists(destino_lista):
        print("  [ya listo] %-16s %s" % ("imageclasslist",
                                         "imageclasslist.txt"))
        ok_lst = True
    else:
        hallado = buscar(raiz, "imageclasslist.txt")
        if hallado:
            shutil.copy2(hallado, destino_lista)
            print("  [ok]       %-16s copiado a la raiz" % "imageclasslist")
            ok_lst = True
        else:
            print("  [FALTA]    %-16s no se encuentra" % "imageclasslist")
            ok_lst = False

    # --- Verificacion final -------------------------------------------------
    print("\n" + "=" * 58)
    print("VERIFICACION")
    print("=" * 58)
    todo = True
    for etiqueta, ruta in (("ExDark/", os.path.join(raiz, "ExDark")),
                           ("ExDark_Annno/", os.path.join(raiz, "ExDark_Annno"))):
        if ya_correcto(ruta):
            faltan = [c for c in CLASES
                      if not os.path.isdir(os.path.join(ruta, c))]
            n_arch = sum(len(f) for _b, _d, f in os.walk(ruta))
            print("  [ok]    %-16s %2d/12 clases, %d ficheros"
                  % (etiqueta, 12 - len(faltan), n_arch))
            if faltan:
                print("          faltan: %s" % ", ".join(faltan))
        else:
            print("  [FALLA] %-16s sin carpetas de clase" % etiqueta)
            todo = False

    if os.path.exists(destino_lista):
        with open(destino_lista, encoding="utf-8", errors="replace") as fh:
            n = sum(1 for _ in fh)
        print("  [ok]    %-16s %d lineas" % ("imageclasslist", n))
        if n < 7000:
            print("          AVISO: se esperaban ~7363 lineas.")
    else:
        print("  [FALLA] %-16s ausente" % "imageclasslist")
        todo = False

    print()
    if todo and ok_img and ok_ann and ok_lst:
        print("Estructura correcta. Siguiente paso:")
        print("    python 01_preparar_exdark_people.py --raiz . --salida dataset")
        return 0
    print("Estructura incompleta: revisar los mensajes de arriba.")
    return 1


def selftest():
    """Verifica la normalizacion con un ZIP anidado, como los de Windows."""
    tmp = tempfile.mkdtemp(prefix="cero_test_")
    raiz = os.path.join(tmp, "raw")
    os.makedirs(os.path.join(raiz, "ExDark"))
    os.makedirs(os.path.join(raiz, "ExDark_Annno"))

    # ZIP con nivel extra (ExDark/ExDark/<clases>), que es el caso problematico.
    origen = os.path.join(tmp, "src")
    for sub, clases in (("img", CLASES), ("ann", CLASES)):
        for c in clases:
            d = os.path.join(origen, sub, "ExDark", c)
            os.makedirs(d)
            open(os.path.join(d, "f.txt"), "w").write("x")

    for sub, nombre, dest in (("img", "ExDark.zip", "ExDark"),
                              ("ann", "ExDark_Annno.zip", "ExDark_Annno")):
        z = os.path.join(raiz, dest, nombre)
        with zipfile.ZipFile(z, "w") as zf:
            base = os.path.join(origen, sub)
            for b, _d, fs in os.walk(base):
                for f in fs:
                    p = os.path.join(b, f)
                    zf.write(p, os.path.relpath(p, base))

    with open(os.path.join(raiz, "lista", ), "w") if False else open(
            os.path.join(origen, "imageclasslist.txt"), "w") as f:
        for i in range(7363):
            f.write("img%05d.jpg 11 1 2 1\n" % i)
    os.makedirs(os.path.join(raiz, "hondo", "mas"))
    shutil.copy2(os.path.join(origen, "imageclasslist.txt"),
                 os.path.join(raiz, "hondo", "mas", "imageclasslist.txt"))

    print("--- normalizando estructura anidada sintetica ---\n")
    rc = preparar(raiz)

    print("=" * 58)
    print("COMPROBACIONES")
    print("=" * 58)
    fallos = []

    def comp(desc, obt, esp):
        ok = obt == esp
        print("  [%s] %-48s %s" % ("ok" if ok else "FALLA", desc, obt))
        if not ok:
            fallos.append(desc)

    comp("codigo de salida correcto", rc, 0)
    comp("anidamiento ExDark/ExDark resuelto",
         os.path.isdir(os.path.join(raiz, "ExDark", "People")), True)
    comp("sin nivel extra sobrante",
         os.path.isdir(os.path.join(raiz, "ExDark", "ExDark")), False)
    comp("anotaciones normalizadas",
         os.path.isdir(os.path.join(raiz, "ExDark_Annno", "People")), True)
    comp("imageclasslist rescatado de subcarpeta",
         os.path.exists(os.path.join(raiz, "imageclasslist.txt")), True)
    comp("las 12 clases presentes",
         sum(1 for c in CLASES
             if os.path.isdir(os.path.join(raiz, "ExDark", c))), 12)

    # Idempotencia: volver a ejecutar no debe romper nada.
    rc2 = preparar(raiz)
    comp("re-ejecucion idempotente", rc2, 0)

    shutil.rmtree(tmp, ignore_errors=True)
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO: 7/7 comprobaciones.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - descomprimir ExDark")
    ap.add_argument("--raiz", default=".", help="carpeta con los ZIP")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    sys.exit(preparar(args.raiz))


if __name__ == "__main__":
    main()