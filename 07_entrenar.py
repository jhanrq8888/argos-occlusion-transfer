#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Paso 6: entrenamiento del diseno factorial 2x2 (Seccion 2.1).

Corridas del plan ajustado (Seccion 3.1): 14 en total.

    V1  YOLOv11s base                        semillas {0,1,2}
    V2  YOLOv11s + CBAM                      semillas {0,1,2}
    V3  YOLOv11s + oclusion sintetica        semillas {0,1,2}
    V4  ARGOS-11 completo (CBAM + oclusion)  semillas {0,1,2}
    C_AUMENTO  control V1+ (aumento base intensificado)   semilla 0
    C_PESOS    control V1 sin preentrenamiento (desde cero) semilla 0

Todas comparten config/hiperparametros.yaml y config/aumento_base.yaml
(salvo C_AUMENTO, que usa aumento_base_intenso.yaml). Lo unico que varia
entre V1-V4 es el modelo inicial (con/sin CBAM) y el aumento de oclusion.
La validacion durante el entrenamiento usa SIEMPRE el split val sin
oclusion; el split test no se toca (Seccion 2.4).

Cada corrida deja en runs/argos/<variante>_s<semilla>/:
    weights/best.pt, last.pt, results.csv (Ultralytics) y
    registro_argos.json (configuracion efectiva, hashes, tiempos).

Uso:
    python 07_entrenar.py --smoke                 # 1 epoca, 5% de datos: verifica la cadena
    python 07_entrenar.py                         # las 14 corridas, en orden
    python 07_entrenar.py --variantes V1 V4 --semillas 0
    python 07_entrenar.py --epochs 100 --patience 20
    python 07_entrenar.py --selftest
"""

import argparse
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argos_lib.atencion import registrar_cbam                 # noqa: E402
from argos_lib.oclusion import (PROB_TIPO_ENTRENAMIENTO,      # noqa: E402
                                RANGO_F_ENTRENAMIENTO)

RAIZ = os.path.dirname(os.path.abspath(__file__))
PESOS_BASE = "yolo11s.pt"
PESOS_CBAM = os.path.join("weights", "yolo11s_cbam_coco.pt")
YAML_BASE = "yolo11s.yaml"                    # arquitectura sin pesos (C_PESOS)

VARIANTES = {
    "V1": {"modelo": PESOS_BASE, "oclusion": False, "aumento": "aumento_base.yaml",
           "pretrained": True, "desc": "YOLOv11s base (baseline)"},
    "V2": {"modelo": PESOS_CBAM, "oclusion": False, "aumento": "aumento_base.yaml",
           "pretrained": True, "desc": "YOLOv11s + CBAM"},
    "V3": {"modelo": PESOS_BASE, "oclusion": True, "aumento": "aumento_base.yaml",
           "pretrained": True, "desc": "YOLOv11s + oclusion sintetica"},
    "V4": {"modelo": PESOS_CBAM, "oclusion": True, "aumento": "aumento_base.yaml",
           "pretrained": True, "desc": "ARGOS-11 completo (CBAM + oclusion)"},
    "C_AUMENTO": {"modelo": PESOS_BASE, "oclusion": False,
                  "aumento": "aumento_base_intenso.yaml", "pretrained": True,
                  "desc": "control V1+: aumento base intensificado"},
    "C_PESOS": {"modelo": YAML_BASE, "oclusion": False, "aumento": "aumento_base.yaml",
                "pretrained": False, "desc": "control: V1 sin preentrenamiento"},
}
ORDEN_POR_DEFECTO = [("V1", 0), ("V2", 0), ("V3", 0), ("V4", 0),
                     ("V1", 1), ("V2", 1), ("V3", 1), ("V4", 1),
                     ("V1", 2), ("V2", 2), ("V3", 2), ("V4", 2),
                     ("C_AUMENTO", 0), ("C_PESOS", 0)]
OCLUSION_CFG = {"p": 0.5, "n_min": 1, "n_max": 3, "rango_f": RANGO_F_ENTRENAMIENTO,
                "prob_tipo": PROB_TIPO_ENTRENAMIENTO}
# Protocolo v2.0 (iteracion 2): oclusores con silueta real, sin parches
# opacos; validacion mixta (val + val_ocluido) para la seleccion del modelo.
OCLUSION_CFG_V2 = {"dir_banco": os.path.join(RAIZ, "dataset", "siluetas_train"), "p": 0.5,
                   "n_min": 1, "n_max": 3, "rango_f": RANGO_F_ENTRENAMIENTO, "prob_persona": 0.5}
# H6 (PREREGISTRO_H6_H7.md s.3): replica de entrenamiento sobre CityPersons train
# (particion interna, 20_replica_citypersons.py) con el generador v2 y el banco
# de siluetas construido desde CityPersons train. Solo V1 y V3.
OCLUSION_CFG_CP = {**OCLUSION_CFG_V2, "dir_banco": os.path.join(RAIZ, "dataset", "siluetas_cp_train")}
OCLUSION_CFG_NO = {**OCLUSION_CFG_V2, "dir_banco": os.path.join(RAIZ, "dataset", "siluetas_no_train")}
# H9 (PREREGISTRO_H9.md): tercera familia, oclusion generativa (Stable Diffusion inpainting), generada
# de antemano por 25_oclusion_generativa.py; el dataset sustituye la imagen leida por una version ocluida
# con p 0.15 por imagen con mosaico (~0.48 por muestra de 4) y 0.5 sin mosaico. Validacion mixta de v2.
OCLUSION_CFG_GEO = {"dir_banco": os.path.join(RAIZ, "dataset", "siluetas_train"),
                    "archivo_patrones": os.path.join(RAIZ, "dataset", "geometria", "patrones_train.json"),
                    "p": 0.5, "n_min": 1, "n_max": 3, "rango_c": (0.40, 0.95), "prob_persona": 0.5}
OCLUSION_CFG_GEN = {"dir_versiones": os.path.join(RAIZ, "dataset", "generativa_train"),
                    "p_mosaico": 0.15, "p_sin_mosaico": 0.5}
# E11 (PREREGISTRO_H14.md): oclusores con orden de profundidad, generados de antemano por 32_profundidad.py y
# sustituidos al leer la imagen con el mismo mecanismo y las mismas probabilidades que la familia generativa.
OCLUSION_CFG_PROF = {**OCLUSION_CFG_GEN, "dir_versiones": os.path.join(RAIZ, "dataset", "profundidad_train")}
PROTOCOLOS = {
    "v1": {"data": "data.yaml", "proyecto": "argos", "oclusion": OCLUSION_CFG, "clase": "OclusionEntrenamiento"},
    "v2": {"data": "data_v2.yaml", "proyecto": "argos_v2", "oclusion": OCLUSION_CFG_V2, "clase": "OclusionSiluetas"},
    "cp": {"data": "data_citypersons.yaml", "proyecto": "argos_cp", "oclusion": OCLUSION_CFG_CP, "clase": "OclusionSiluetas"},
    # H7 (PREREGISTRO_H6_H7.md s.4): escalera de datos sobre NightOwls train.
    # El fichero de datos cambia por peldano: se pasa con --datos.
    "no": {"data": "data_nightowls_20000.yaml", "proyecto": "argos_no", "oclusion": OCLUSION_CFG_NO, "clase": "OclusionSiluetas"},
    "gen": {"data": "data_v2.yaml", "proyecto": "argos_gen", "oclusion": OCLUSION_CFG_GEN, "clase": "OclusionGenerativa"},
    # H10 (PREREGISTRO_H10.md): siluetas v2 colocadas con la geometria de la oclusion real (patrones de CityPersons train).
    "geo": {"data": "data_v2.yaml", "proyecto": "argos_geo", "oclusion": OCLUSION_CFG_GEO, "clase": "OclusionGeometria"},
    "prof": {"data": "data_v2.yaml", "proyecto": "argos_prof", "oclusion": OCLUSION_CFG_PROF, "clase": "OclusionGenerativa"},
}


def leer_yaml(ruta):
    import yaml
    with open(ruta, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as fh:
        for bloque in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def nombre_corrida(variante, semilla, smoke=False):
    return "%s_s%d%s" % (variante, semilla, "_smoke" if smoke else "")


def corrida_terminada(dir_run):
    return os.path.exists(os.path.join(dir_run, "registro_argos.json")) and \
        os.path.exists(os.path.join(dir_run, "weights", "best.pt"))


def entrenar_una(variante, semilla, args):
    from argos_lib.entrenamiento import EntrenadorArgos, EntrenadorArgosRTDETR
    from ultralytics import RTDETR, YOLO

    registrar_cbam()
    v = dict(VARIANTES[variante])
    prot = PROTOCOLOS[args.protocolo]
    prefijo = ""
    if args.modelo_base:                      # generalidad: otra familia (solo V1/V3/C_*)
        if v["modelo"] == PESOS_CBAM:
            sys.exit("ERROR: --modelo-base solo admite variantes sin CBAM (V1, V3, C_*)")
        if v["modelo"] == PESOS_BASE:
            v["modelo"] = args.modelo_base
        prefijo = os.path.splitext(os.path.basename(args.modelo_base))[0] + "_"
    proyecto = os.path.join(RAIZ, "runs", args.proyecto or ("smoke" if args.smoke else prot["proyecto"]))
    nombre = prefijo + nombre_corrida(variante, semilla, args.smoke)
    dir_run = os.path.join(proyecto, nombre)
    if corrida_terminada(dir_run) and not args.forzar:
        print("  [omitida] %s ya terminada (%s)" % (nombre, dir_run))
        return dir_run

    hp = leer_yaml(os.path.join(RAIZ, "config", args.hiperparametros))
    aum = leer_yaml(os.path.join(RAIZ, "config", v["aumento"]))
    if args.epochs:
        hp["epochs"] = args.epochs
    if args.patience is not None:
        hp["patience"] = args.patience
    if args.batch:
        hp["batch"] = args.batch
    if args.workers is not None:
        hp["workers"] = args.workers
    if args.lr0 is not None:
        hp["lr0"] = args.lr0

    ruta_modelo = v["modelo"] if v["modelo"].endswith(".yaml") \
        else os.path.join(RAIZ, v["modelo"])
    if not v["modelo"].endswith(".yaml") and not os.path.exists(ruta_modelo):
        sys.exit("ERROR: falta %s (ejecutar 06_modelo_atencion.py)" % ruta_modelo)

    reanudar = os.path.exists(os.path.join(dir_run, "weights", "last.pt")) \
        and not corrida_terminada(dir_run) and not args.forzar
    kwargs = dict(data=os.path.join(RAIZ, "dataset", args.datos or prot["data"]),
                  project=proyecto, name=nombre, exist_ok=True,
                  seed=semilla, pretrained=v["pretrained"], val=True,
                  plots=True, verbose=True, **hp, **aum)
    if args.smoke:
        kwargs.update(epochs=1, fraction=0.05, batch=min(hp["batch"], 8),
                      workers=min(hp.get("workers", 8), 2), patience=100)
    if args.device is not None:
        kwargs["device"] = args.device

    import argos_lib.oclusion as _oc
    import argos_lib.siluetas as _si
    import argos_lib.generativa as _ge
    import argos_lib.geometria as _gm
    rtdetr = bool(args.modelo_base) and "rtdetr" in os.path.basename(args.modelo_base).lower()
    Entrenador, Modelo = (EntrenadorArgosRTDETR, RTDETR) if rtdetr else (EntrenadorArgos, YOLO)
    if rtdetr:
        # thop 0.1.1 (legado, instalado para 10_medir_costo.py) falla al perfilar RT-DETR y deja
        # ganchos colgados que rompen el entrenamiento. Se desactiva solo el conteo informativo de
        # GFLOPs del registro de Ultralytics (get_flops devuelve 0.0); no afecta al entrenamiento.
        sys.modules["thop"] = None
    Entrenador.oclusion_clase = (getattr(_oc, prot["clase"], None) or getattr(_si, prot["clase"], None)
                                 or getattr(_ge, prot["clase"], None) or getattr(_gm, prot["clase"]))
    Entrenador.oclusion_cfg = dict(prot["oclusion"]) if v["oclusion"] else None
    cfg_ocl = prot["oclusion"]

    print("\n" + "=" * 62)
    print("CORRIDA %s  (%s)" % (nombre, v["desc"]))
    print("=" * 62)
    print("  modelo inicial : %s%s" % (v["modelo"], "" if v["pretrained"] else "  [sin preentrenar]"))
    print("  aumento base   : config/%s" % v["aumento"])
    print("  protocolo      : %s  (datos: %s)" % (args.protocolo, args.datos or prot["data"]))
    print("  oclusion       : %s" % (("%s %s" % (prot["clase"], cfg_ocl)) if v["oclusion"] else "no"))
    print("  epocas/paciencia: %s/%s   batch %s   semilla %d"
          % (kwargs["epochs"], kwargs["patience"], kwargs["batch"], semilla))
    if reanudar:
        print("  reanudando desde last.pt")

    t0 = time.time()
    if reanudar:
        modelo = Modelo(os.path.join(dir_run, "weights", "last.pt"))
        extra = {"workers": args.workers} if args.workers is not None else {}
        modelo.train(trainer=Entrenador, resume=True, **extra)
    else:
        modelo = Modelo(ruta_modelo)
        modelo.train(trainer=Entrenador, **kwargs)
    dur = time.time() - t0

    # Registro de la corrida (para el congelamiento y la trazabilidad).
    tr = modelo.trainer
    epocas_hechas = None
    try:
        import csv
        with open(os.path.join(dir_run, "results.csv"), newline="") as fh:
            epocas_hechas = sum(1 for _ in csv.DictReader(fh))
    except OSError:
        pass
    cadena = []
    try:
        from argos_lib.entrenamiento import describir_cadena
        cadena = describir_cadena(tr.train_loader.dataset)
    except Exception:
        pass
    registro = {
        "variante": variante, "semilla": semilla, "descripcion": v["desc"],
        "smoke": bool(args.smoke), "modelo_inicial": v["modelo"],
        "pretrained": v["pretrained"], "oclusion": cfg_ocl if v["oclusion"] else None,
        "protocolo": args.protocolo, "datos": args.datos or prot["data"],
        "clase_oclusion": prot["clase"] if v["oclusion"] else None,
        "modelo_base": args.modelo_base,
        "aumento_base": v["aumento"],
        "hash_aumento_base": sha256(os.path.join(RAIZ, "config", v["aumento"])),
        "hiperparametros": args.hiperparametros,
        "hash_hiperparametros": sha256(os.path.join(RAIZ, "config", args.hiperparametros)),
        "hash_modelo_inicial": sha256(ruta_modelo) if os.path.exists(ruta_modelo) else None,
        "args_efectivos": {k: (v_ if isinstance(v_, (int, float, str, bool, type(None)))
                              else str(v_)) for k, v_ in vars(tr.args).items()},
        "cadena_transforms_train": cadena,
        "epocas_completadas": epocas_hechas,
        "segundos_totales": round(dur, 1),
        "segundos_por_epoca": round(dur / epocas_hechas, 1) if epocas_hechas else None,
        "mejor_fitness_val": float(getattr(tr, "best_fitness", 0) or 0),
        "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(os.path.join(dir_run, "registro_argos.json"), "w", encoding="utf-8") as fh:
        json.dump(registro, fh, indent=2, ensure_ascii=False)
    print("\n  terminada en %.1f min (%s epocas). Registro: %s"
          % (dur / 60, epocas_hechas, os.path.join(dir_run, "registro_argos.json")))
    return dir_run


def selftest():
    """Comprueba la configuracion sin entrenar: YAMLs, variantes, cadena."""
    fallos = []

    def comp(desc, obt, esp):
        ok = obt == esp
        print("  [%s] %-50s %s" % ("ok" if ok else "FALLA", desc, obt))
        if not ok:
            fallos.append(desc)

    hp = leer_yaml(os.path.join(RAIZ, "config", "hiperparametros.yaml"))
    comp("hiperparametros: SGD lr 0.002 (v1.1) m 0.937 wd 5e-4 batch 16",
         (hp["optimizer"], hp["lr0"], hp["momentum"], hp["weight_decay"], hp["batch"]),
         ("SGD", 0.002, 0.937, 0.0005, 16))
    a = leer_yaml(os.path.join(RAIZ, "config", "aumento_base.yaml"))
    b = leer_yaml(os.path.join(RAIZ, "config", "aumento_base_intenso.yaml"))
    comp("aumento base y V1+ tienen las mismas claves", sorted(a) == sorted(b), True)
    comp("V1+ difiere del base (intensificado)", a != b, True)
    comp("14 corridas en el orden por defecto", len(ORDEN_POR_DEFECTO), 14)
    comp("V1-V4 comparten aumento base",
         len({VARIANTES[k]["aumento"] for k in ("V1", "V2", "V3", "V4")}), 1)
    comp("solo V3 y V4 usan oclusion",
         [k for k in VARIANTES if VARIANTES[k]["oclusion"]], ["V3", "V4"])
    comp("solo C_PESOS entrena desde cero",
         [k for k in VARIANTES if not VARIANTES[k]["pretrained"]], ["C_PESOS"])
    comp("oclusion: p=0.5, 1-3 personas, 30-85%",
         (OCLUSION_CFG["p"], OCLUSION_CFG["n_min"], OCLUSION_CFG["n_max"],
          OCLUSION_CFG["rango_f"]), (0.5, 1, 3, (0.30, 0.85)))
    # La cadena de transforms del dataset con oclusion (sin entrenar).
    try:
        from argos_lib.entrenamiento import DatasetOclusion, describir_cadena
        from argos_lib.oclusion import OclusionEntrenamiento
        from ultralytics.cfg import get_cfg
        cfg = get_cfg(overrides={"imgsz": 640, "task": "detect"})
        data = {"names": {0: "person"}, "nc": 1, "channels": 3}
        ruta = os.path.join(RAIZ, "dataset", "images", "val")
        ds = DatasetOclusion(img_path=ruta, imgsz=640, batch_size=4, augment=True,
                             hyp=cfg, rect=False, cache=None, single_cls=False,
                             stride=32, pad=0.0, prefix="", task="detect",
                             classes=None, data=data, fraction=0.02,
                             oclusion=OclusionEntrenamiento(**OCLUSION_CFG))
        cad = describir_cadena(ds)
        comp("oclusion insertada justo antes de Format",
             (cad[-2], cad[-1]), ("OclusionEntrenamiento", "Format"))
        ds.close_mosaic(cfg)
        cad2 = describir_cadena(ds)
        comp("oclusion sobrevive a close_mosaic", "OclusionEntrenamiento" in cad2, True)
        muestra = ds[0]
        comp("muestra con imagen y cajas", ("img" in muestra and "bboxes" in muestra), True)
    except Exception as e:                       # pragma: no cover
        print("  [FALLA] cadena de transforms: %s" % e)
        fallos.append("cadena")
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - entrenamiento factorial")
    ap.add_argument("--variantes", nargs="+", choices=sorted(VARIANTES),
                    help="subconjunto de variantes (def. las 14 corridas)")
    ap.add_argument("--semillas", nargs="+", type=int)
    ap.add_argument("--epochs", type=int)
    ap.add_argument("--patience", type=int)
    ap.add_argument("--batch", type=int)
    ap.add_argument("--workers", type=int)
    ap.add_argument("--device")
    ap.add_argument("--lr0", type=float, help="sobrescribe lr0 (solo diagnostico; el valor del protocolo esta en config/)")
    ap.add_argument("--protocolo", choices=sorted(PROTOCOLOS), default="v1",
                    help="v1 = parches (exp. 1); v2 = siluetas + val mixto (iter. 2); cp = H6 CityPersons; no = H7 NightOwls; gen = H9 generativa; geo = H10 geometria real")
    ap.add_argument("--hiperparametros", default="hiperparametros.yaml",
                    help="fichero de config/ (H8 RT-DETR: hiperparametros_rtdetr.yaml)")
    ap.add_argument("--datos", help="sobrescribe el yaml de datos del protocolo (p. ej. data_nightowls_5000.yaml)")
    ap.add_argument("--modelo-base", help="pesos alternativos para V1/V3/C_* (p. ej. yolo26s.pt); prefija el nombre")
    ap.add_argument("--proyecto", help="subcarpeta de runs/ (def. argos; smoke con --smoke)")
    ap.add_argument("--smoke", action="store_true",
                    help="1 epoca con el 5%% de los datos, en runs/smoke/")
    ap.add_argument("--forzar", action="store_true", help="repetir corridas terminadas")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())

    if args.variantes or args.semillas:
        vs = args.variantes or ["V1", "V2", "V3", "V4"]
        ss = args.semillas or [0, 1, 2]
        plan = [(v, s) for s in ss for v in vs
                if not (v.startswith("C_") and s != 0)]
    else:
        plan = list(ORDEN_POR_DEFECTO)
    print("Plan: %d corridas -> %s" % (len(plan), ", ".join("%s/s%d" % p for p in plan)))
    for v, s in plan:
        entrenar_una(v, s, args)


if __name__ == "__main__":
    main()
