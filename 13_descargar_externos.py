#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Paso 10b: descarga SELECTIVA de las fuentes externas.

NightOwls (https://nightowls-dataset.org, uso academico no comercial): el
ZIP de validacion pesa 53 GB, pero el servidor acepta rangos de bytes, asi
que se lee solo el directorio central del ZIP y se extraen por rango los
PNG de la muestra (por defecto 2 000 imagenes con peatones, semilla 0 =
la misma muestra que 12_fuentes_externas.py). Coste: ~2 GB.

CityPersons: la copia de Kaggle (hakurei/citypersons, 12 GB) exige la
cuenta del usuario; se descarga a mano y este script solo la descomprime
(subcomando `citypersons --zip`), quedandose con el split val.

Uso:
    python 13_descargar_externos.py nightowls --salida externos/nightowls --n 2000
    python 13_descargar_externos.py citypersons --zip <ruta>/archive.zip --salida externos/citypersons
    python 13_descargar_externos.py --selftest
"""

import argparse
import io
import json
import os
import struct
import sys
import zipfile
import zlib

import numpy as np

RAIZ = os.path.dirname(os.path.abspath(__file__))
URL_JSON = "https://thor.robots.ox.ac.uk/nightowls/python/nightowls_validation.json"
URL_ZIP = "https://thor.robots.ox.ac.uk/nightowls/python/nightowls_validation.zip"


# --- Lector de ZIP por rangos ------------------------------------------------
class FuenteRangos:
    """Interfaz minima: tam() y leer(inicio, n). Implementaciones: HTTP y fichero."""


class FuenteHTTP(FuenteRangos):
    def __init__(self, url):
        import urllib.request
        self.url = url
        self._op = urllib.request.build_opener()
        with self._op.open(urllib.request.Request(url, method="HEAD")) as r:
            self._tam = int(r.headers["Content-Length"])
            if r.headers.get("Accept-Ranges", "") != "bytes":
                raise RuntimeError("el servidor no acepta rangos")

    def tam(self):
        return self._tam

    def leer(self, inicio, n):
        import urllib.request
        req = urllib.request.Request(self.url, headers={"Range": "bytes=%d-%d" % (inicio, inicio + n - 1)})
        for intento in range(5):
            try:
                with self._op.open(req, timeout=120) as r:
                    datos = r.read()
                if len(datos) == n:
                    return datos
            except Exception:
                pass
        raise IOError("no se pudo leer el rango %d+%d" % (inicio, n))


class FuenteFichero(FuenteRangos):
    def __init__(self, ruta):
        self.ruta = ruta
        self._tam = os.path.getsize(ruta)

    def tam(self):
        return self._tam

    def leer(self, inicio, n):
        with open(self.ruta, "rb") as fh:
            fh.seek(inicio)
            return fh.read(n)


def directorio_central(fuente):
    """Devuelve {nombre: (offset_cabecera_local, tam_comprimido, tam, metodo)}
    leyendo solo el final del ZIP (soporta ZIP64)."""
    tam = fuente.tam()
    cola = fuente.leer(max(0, tam - 65536 - 22), min(tam, 65536 + 22))
    p = cola.rfind(b"PK\x05\x06")
    if p < 0:
        raise ValueError("no se encontro el fin del directorio central")
    eocd = cola[p:p + 22]
    n_ent = struct.unpack("<H", eocd[10:12])[0]
    tam_cd, off_cd = struct.unpack("<II", eocd[12:20])
    if off_cd == 0xFFFFFFFF or n_ent == 0xFFFF or tam_cd == 0xFFFFFFFF:
        # ZIP64: localizador (20 bytes) justo antes del EOCD.
        loc = cola[p - 20:p]
        if loc[:4] != b"PK\x06\x07":
            raise ValueError("ZIP64 sin localizador")
        off_eocd64 = struct.unpack("<Q", loc[8:16])[0]
        e64 = fuente.leer(off_eocd64, 56)
        n_ent = struct.unpack("<Q", e64[32:40])[0]
        tam_cd = struct.unpack("<Q", e64[40:48])[0]
        off_cd = struct.unpack("<Q", e64[48:56])[0]
    cd = fuente.leer(off_cd, tam_cd)
    entradas, i = {}, 0
    while i < len(cd) and cd[i:i + 4] == b"PK\x01\x02":
        metodo = struct.unpack("<H", cd[i + 10:i + 12])[0]
        comp, tam_ = struct.unpack("<II", cd[i + 20:i + 28])
        ln, le, lc = struct.unpack("<HHH", cd[i + 28:i + 34])
        off = struct.unpack("<I", cd[i + 42:i + 46])[0]
        nombre = cd[i + 46:i + 46 + ln].decode("utf-8", "replace")
        extra = cd[i + 46 + ln:i + 46 + ln + le]
        if 0xFFFFFFFF in (comp, tam_, off):        # campo ZIP64 en el extra
            j = 0
            while j + 4 <= len(extra):
                hid, hl = struct.unpack("<HH", extra[j:j + 4])
                if hid == 1:
                    campos = extra[j + 4:j + 4 + hl]
                    k = 0
                    if tam_ == 0xFFFFFFFF:
                        tam_ = struct.unpack("<Q", campos[k:k + 8])[0]; k += 8
                    if comp == 0xFFFFFFFF:
                        comp = struct.unpack("<Q", campos[k:k + 8])[0]; k += 8
                    if off == 0xFFFFFFFF:
                        off = struct.unpack("<Q", campos[k:k + 8])[0]; k += 8
                    break
                j += 4 + hl
        entradas[nombre] = (off, comp, tam_, metodo)
        i += 46 + ln + le + lc
    return entradas


def extraer_miembro(fuente, entrada):
    off, comp, tam_, metodo = entrada
    cab = fuente.leer(off, 30)
    if cab[:4] != b"PK\x03\x04":
        raise ValueError("cabecera local invalida")
    ln, le = struct.unpack("<HH", cab[26:30])
    datos = fuente.leer(off + 30 + ln + le, comp)
    if metodo == 0:
        return datos
    if metodo == 8:
        return zlib.decompress(datos, -15)
    raise ValueError("metodo de compresion no soportado: %d" % metodo)


# --- NightOwls ---------------------------------------------------------------
def descargar_nightowls(salida, n, semilla, url_json=URL_JSON, url_zip=URL_ZIP, fuente=None, hilos=8):
    import urllib.request
    os.makedirs(salida, exist_ok=True)
    rj = os.path.join(salida, "nightowls_validation.json")
    if not os.path.exists(rj):
        print("Descargando anotaciones (10 MB)...")
        urllib.request.urlretrieve(url_json, rj)
    with open(rj, encoding="utf-8") as fh:
        d = json.load(fh)
    imgs = {im["id"]: im for im in d["images"]}
    con_peaton = sorted({a["image_id"] for a in d["annotations"] if a["category_id"] == 1})
    rnd = np.random.RandomState(semilla)
    ids = sorted(rnd.choice(con_peaton, min(n, len(con_peaton)), replace=False).tolist()) \
        if n and len(con_peaton) > n else con_peaton
    nombres = [imgs[i]["file_name"] for i in ids]
    print("Imagenes de validacion: %d; con peatones: %d; muestra: %d"
          % (len(imgs), len(con_peaton), len(nombres)), flush=True)

    fuente = fuente or FuenteHTTP(url_zip)
    print("Leyendo el directorio del ZIP (%.1f GB en el servidor)..." % (fuente.tam() / 1e9))
    cd = directorio_central(fuente)
    indice = {os.path.basename(k): k for k in cd}
    dir_img = os.path.join(salida, "nightowls_validation")
    os.makedirs(dir_img, exist_ok=True)
    total, hechos, faltan = 0, 0, []
    pendientes = []
    for nombre in nombres:
        destino = os.path.join(dir_img, nombre)
        if os.path.exists(destino):
            hechos += 1
        elif nombre not in indice:
            faltan.append(nombre)
        else:
            pendientes.append((nombre, destino))

    def bajar(par):
        nombre, destino = par
        datos = extraer_miembro(fuente, cd[indice[nombre]])
        with open(destino + ".part", "wb") as fh:
            fh.write(datos)
        os.replace(destino + ".part", destino)
        return len(datos)

    # El servidor limita cada conexion (~0,8 MB/s) pero escala con varias.
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=hilos) as ex:
        for k, n_bytes in enumerate(ex.map(bajar, pendientes), 1):
            total += n_bytes; hechos += 1
            if k % 100 == 0:
                print("  %d/%d  (%.2f GB)" % (k, len(pendientes), total / 1e9), flush=True)
    with open(os.path.join(salida, "muestra.json"), "w", encoding="utf-8") as fh:
        json.dump({"semilla": semilla, "n": len(nombres), "ids": ids, "faltantes": faltan}, fh)
    print("Listo: %d imagenes en %s (%.2f GB descargados; %d no halladas)"
          % (hechos, dir_img, total / 1e9, len(faltan)))
    return dir_img, rj


# --- NightOwls training (H7) -------------------------------------------------
URL_JSON_TRAIN = "https://thor.robots.ox.ac.uk/nightowls/python/nightowls_training.json"
URL_ZIP_TRAIN = "https://thor.robots.ox.ac.uk/nightowls/python/nightowls_training.zip"
PELDANOS_H7 = (2000, 5000, 10000, 20000)


def muestra_anidada(con_peaton, peldanos, semilla):
    """Permutacion unica con semilla: los primeros k ids forman el peldano k, de
    modo que 2k dentro de 5k dentro de 10k dentro de 20k (PREREGISTRO_H6_H7.md s.4)."""
    rnd = np.random.RandomState(semilla)
    perm = rnd.permutation(sorted(con_peaton)).tolist()
    return perm[:max(peldanos)], {str(k): k for k in peldanos if k <= len(perm)}


def _bajar_lote(fuente, cd, nombres, dir_img, hilos):
    indice = {os.path.basename(k): k for k in cd}
    pendientes, hechos, faltan = [], 0, []
    for nombre in nombres:
        destino = os.path.join(dir_img, nombre)
        if os.path.exists(destino):
            hechos += 1
        elif nombre not in indice:
            faltan.append(nombre)
        else:
            pendientes.append((nombre, destino))

    def bajar(par):
        nombre, destino = par
        datos = extraer_miembro(fuente, cd[indice[nombre]])
        with open(destino + ".part", "wb") as fh:
            fh.write(datos)
        os.replace(destino + ".part", destino)
        return len(datos)

    from concurrent.futures import ThreadPoolExecutor
    total = 0
    with ThreadPoolExecutor(max_workers=hilos) as ex:
        for k, n_bytes in enumerate(ex.map(bajar, pendientes), 1):
            total += n_bytes; hechos += 1
            if k % 200 == 0:
                print("  %d/%d  (%.2f GB)" % (k, len(pendientes), total / 1e9), flush=True)
    return hechos, total, faltan


def descargar_nightowls_train(salida, peldanos=PELDANOS_H7, semilla=0, n_val_interno=1000, semilla_val=1,
                              excluir_manifiesto=None, url_json=URL_JSON_TRAIN, url_zip=URL_ZIP_TRAIN,
                              url_json_val=URL_JSON, url_zip_val=URL_ZIP, hilos=8, solo_val=False):
    """H7: escalera anidada de NightOwls training (imagenes con >=1 peaton) y
    val interno de NightOwls validation disjunto de la muestra de evaluacion."""
    import urllib.request
    os.makedirs(salida, exist_ok=True)
    # 1) Escalera de training
    rj = os.path.join(salida, "nightowls_training.json")
    if not os.path.exists(rj):
        print("Descargando anotaciones de training (32 MB)...", flush=True)
        urllib.request.urlretrieve(url_json, rj)
    with open(rj, encoding="utf-8") as fh:
        d = json.load(fh)
    imgs = {im["id"]: im for im in d["images"]}
    con_peaton = sorted({a["image_id"] for a in d["annotations"] if a["category_id"] == 1})
    ids, rungs = muestra_anidada(con_peaton, peldanos, semilla)
    print("Training: %d imagenes; con peatones: %d; escalera %s (semilla %d)"
          % (len(imgs), len(con_peaton), rungs, semilla), flush=True)
    manifiesto = {"semilla": semilla, "peldanos": rungs, "ids_ordenados": ids,
                  "nota": "el peldano k son los primeros k ids_ordenados (muestra anidada)"}
    if not solo_val:
        fuente = FuenteHTTP(url_zip)
        print("Leyendo el directorio del ZIP de training (%.1f GB en el servidor)..." % (fuente.tam() / 1e9), flush=True)
        cd = directorio_central(fuente)
        dir_img = os.path.join(salida, "nightowls_training")
        os.makedirs(dir_img, exist_ok=True)
        hechos, total, faltan = _bajar_lote(fuente, cd, [imgs[i]["file_name"] for i in ids], dir_img, hilos)
        manifiesto["faltantes"] = faltan
        print("Training listo: %d imagenes en %s (%.2f GB descargados; %d no halladas)"
              % (hechos, dir_img, total / 1e9, len(faltan)), flush=True)
    # 2) Val interno desde validation, excluyendo la muestra de evaluacion
    rjv = os.path.join(salida, "nightowls_validation.json")
    if not os.path.exists(rjv):
        urllib.request.urlretrieve(url_json_val, rjv)
    with open(rjv, encoding="utf-8") as fh:
        dv = json.load(fh)
    imgs_v = {im["id"]: im for im in dv["images"]}
    con_peaton_v = sorted({a["image_id"] for a in dv["annotations"] if a["category_id"] == 1})
    excluidos = set()
    if excluir_manifiesto and os.path.exists(excluir_manifiesto):
        with open(excluir_manifiesto, encoding="utf-8") as fh:
            excluidos = set(json.load(fh)["ids"])
    candidatos = [i for i in con_peaton_v if i not in excluidos]
    rnd = np.random.RandomState(semilla_val)
    ids_v = sorted(rnd.choice(candidatos, min(n_val_interno, len(candidatos)), replace=False).tolist())
    print("Validation: con peatones %d, excluidos %d, val interno %d (semilla %d)"
          % (len(con_peaton_v), len(excluidos), len(ids_v), semilla_val), flush=True)
    fuente_v = FuenteHTTP(url_zip_val)
    cd_v = directorio_central(fuente_v)
    dir_v = os.path.join(salida, "nightowls_val_interno")
    os.makedirs(dir_v, exist_ok=True)
    hechos_v, total_v, faltan_v = _bajar_lote(fuente_v, cd_v, [imgs_v[i]["file_name"] for i in ids_v], dir_v, hilos)
    manifiesto["val_interno"] = {"semilla": semilla_val, "n": len(ids_v), "ids": ids_v,
                                 "excluidos_de": excluir_manifiesto, "faltantes": faltan_v}
    print("Val interno listo: %d imagenes en %s (%.2f GB)" % (hechos_v, dir_v, total_v / 1e9), flush=True)
    with open(os.path.join(salida, "muestra_h7.json"), "w", encoding="utf-8") as fh:
        json.dump(manifiesto, fh)
    return manifiesto


# --- CityPersons (zip de Kaggle) ---------------------------------------------
def descomprimir_citypersons(ruta_zip, salida, splits=("val",)):
    os.makedirs(salida, exist_ok=True)
    n = 0
    with zipfile.ZipFile(ruta_zip) as z:
        for m in z.namelist():
            low = m.lower().replace("\\", "/")
            if any("/%s/" % s in low for s in splits) and (
                    low.endswith(".png") or low.endswith(".json")):
                z.extract(m, salida); n += 1
    print("Extraidos %d ficheros del split %s en %s" % (n, ",".join(splits), salida))
    print("Buscar despues gtBboxCityPersons/<split> y leftImg8bit/<split> para 12_fuentes_externas.py")
    return n


def selftest():
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="descarga_test_")
    fallos = []

    def comp(desc, obt, esp):
        ok = obt == esp
        vista = obt if not isinstance(obt, bytes) else "%d bytes" % len(obt)
        print("  [%s] %-46s %s" % ("ok" if ok else "FALLA", desc, vista))
        if not ok:
            fallos.append(desc)

    # ZIP local con 3 "imagenes"; lectura por rangos identica a zipfile.
    rz = os.path.join(tmp, "v.zip")
    contenido = {"nightowls_validation/a.png": b"A" * 1000, "nightowls_validation/b.png": os.urandom(5000),
                 "nightowls_validation/c.png": b"C" * 10}
    with zipfile.ZipFile(rz, "w") as z:
        z.writestr("nightowls_validation/a.png", contenido["nightowls_validation/a.png"], zipfile.ZIP_DEFLATED)
        z.writestr("nightowls_validation/b.png", contenido["nightowls_validation/b.png"], zipfile.ZIP_STORED)
        z.writestr("nightowls_validation/c.png", contenido["nightowls_validation/c.png"], zipfile.ZIP_DEFLATED)
    f = FuenteFichero(rz)
    cd = directorio_central(f)
    comp("directorio central: 3 entradas", len(cd), 3)
    comp("miembro deflate identico", extraer_miembro(f, cd["nightowls_validation/a.png"]), contenido["nightowls_validation/a.png"])
    comp("miembro stored identico", extraer_miembro(f, cd["nightowls_validation/b.png"]), contenido["nightowls_validation/b.png"])
    # ZIP64 forzado.
    rz64 = os.path.join(tmp, "v64.zip")
    with zipfile.ZipFile(rz64, "w", allowZip64=True) as z:
        for i in range(3):
            z.writestr("d%d.png" % i, b"x" * (100 + i), zipfile.ZIP_DEFLATED, )
    # Forzar registros ZIP64 reescribiendo con force_zip64 en cada entrada.
    with zipfile.ZipFile(rz64, "w", allowZip64=True) as z:
        for i in range(3):
            with z.open("d%d.png" % i, "w", force_zip64=True) as w:
                w.write(b"x" * (100 + i))
    cd64 = directorio_central(FuenteFichero(rz64))
    comp("zip64: 3 entradas", len(cd64), 3)
    comp("zip64: miembro identico", extraer_miembro(FuenteFichero(rz64), cd64["d2.png"]), b"x" * 102)
    # Flujo completo de NightOwls con JSON y ZIP locales.
    an = {"images": [{"id": 1, "file_name": "a.png"}, {"id": 2, "file_name": "b.png"}, {"id": 3, "file_name": "c.png"}],
          "annotations": [{"image_id": 1, "category_id": 1, "bbox": [0, 0, 1, 1]},
                          {"image_id": 3, "category_id": 4, "bbox": [0, 0, 1, 1]}]}
    sal = os.path.join(tmp, "no")
    os.makedirs(sal)
    json.dump(an, open(os.path.join(sal, "nightowls_validation.json"), "w"))
    dir_img, _ = descargar_nightowls(sal, 10, 0, fuente=f)
    comp("nightowls: solo imagenes con peatones", sorted(os.listdir(dir_img)), ["a.png"])
    # CityPersons: zip falso con val/ y train/.
    rc = os.path.join(tmp, "cp.zip")
    with zipfile.ZipFile(rc, "w") as z:
        z.writestr("leftImg8bit/val/x/x_leftImg8bit.png", b"p")
        z.writestr("gtBboxCityPersons/val/x/x_gtBboxCityPersons.json", b"{}")
        z.writestr("leftImg8bit/train/y/y_leftImg8bit.png", b"p")
    comp("citypersons: solo val extraido", descomprimir_citypersons(rc, os.path.join(tmp, "cp")), 2)
    shutil.rmtree(tmp)
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO: 7/7 comprobaciones.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - descarga selectiva de fuentes externas")
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    n = sub.add_parser("nightowls")
    n.add_argument("--salida", default=os.path.join(RAIZ, "externos", "nightowls"))
    n.add_argument("--n", type=int, default=2000)
    n.add_argument("--semilla", type=int, default=0)
    n.add_argument("--hilos", type=int, default=8)
    t = sub.add_parser("nightowls-train", help="H7: escalera anidada de training + val interno")
    t.add_argument("--salida", default=os.path.join(RAIZ, "externos", "nightowls"))
    t.add_argument("--semilla", type=int, default=0)
    t.add_argument("--n-val-interno", type=int, default=1000)
    t.add_argument("--semilla-val", type=int, default=1)
    t.add_argument("--excluir", default=os.path.join(RAIZ, "externos", "nightowls", "muestra.json"))
    t.add_argument("--hilos", type=int, default=8)
    t.add_argument("--solo-val", action="store_true")
    c = sub.add_parser("citypersons")
    c.add_argument("--zip", required=True)
    c.add_argument("--salida", default=os.path.join(RAIZ, "externos", "citypersons"))
    c.add_argument("--splits", default="val")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if args.cmd == "nightowls":
        descargar_nightowls(args.salida, args.n, args.semilla, hilos=args.hilos)
    elif args.cmd == "nightowls-train":
        descargar_nightowls_train(args.salida, semilla=args.semilla, n_val_interno=args.n_val_interno,
                                  semilla_val=args.semilla_val, excluir_manifiesto=args.excluir,
                                  hilos=args.hilos, solo_val=args.solo_val)
    elif args.cmd == "citypersons":
        descomprimir_citypersons(args.zip, args.salida, tuple(args.splits.split(",")))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
