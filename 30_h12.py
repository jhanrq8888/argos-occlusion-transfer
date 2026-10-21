#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - H12 (PREREGISTRO_H12.md, E10) y extension de semillas de E7b/E8.

E10 (YOLOv11m, ExDark-People, 30 epocas fijas, pesos last.pt, semillas 0-2; entrenado en RunPod):
  H12a  V3sil - V1   (siluetas v2, protocolo v2)    control silueta_severa
  H12b  V3gen - V1   (oclusion generativa, prot. gen) control generativa_severa
  Regla (la de H4, H8, H9, H9b y H10): el deficit persiste (H12x SOSTENIDA) si V3 - V1 NO alcanza +2 pp con
  IC 95 % por imagenes > 0 en al menos 2 de las 3 fuentes reales (NightOwls ocluida, CityPersons heavy,
  ExDark proxy severa); REFUTADA si lo alcanza en 2 o 3; NO CONCLUYENTE si el control no alcanza +2 pp con IC > 0.

Extension de semillas (analisis secundario pre-registrado; no cambia los veredictos de H9b ni de H10;
enmienda v3.7b: las semillas 3-4 se entrenan en RunPod y se informan tambien solas):
  E7b con 5 semillas   V3gen - V1   (semillas 0-2 de resultados_h9b + 3-4 nuevas, YOLOv11s, laptop)
  E8 (siluetas) con 5  V3sil - V1   (V3S 0-2 de resultados_h10 + 3-4 nuevas; V1 de E7b)

IC: por imagenes (1 000 replicas, criterio) y jerarquico semillas + imagenes (2 000 replicas, sensibilidad),
con 23_bootstrap_jerarquico.bootstrap_dos_niveles; cada celda con su propia semilla (indice de la celda).

Lee detecciones guardadas (det/); escribe resultados_h12/analisis/contrastes_h12.{csv,json} e informes/veredicto_h12.md.

Uso:
    python 30_h12.py
    python 30_h12.py --selftest
"""
import argparse
import importlib.util
import json
import os
import sys

import numpy as np

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
_spec = importlib.util.spec_from_file_location("jerarquico23", os.path.join(RAIZ, "23_bootstrap_jerarquico.py"))
B23 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(B23)
A11 = B23.A11
from argos_lib.ap import emparejar_conjunto                                  # noqa: E402
from argos_lib.gt import cargar_detecciones, cargar_gt                       # noqa: E402

UMBRAL = 2.0
B_IMG, B_JER = 1000, 2000
GT = {"silueta_severa": os.path.join("dataset", "test_sintetico", "silueta_severa", "gt_silueta_severa.json"),
      "generativa_severa": os.path.join("dataset", "test_sintetico", "generativa_severa", "gt_generativa_severa.json"),
      "nightowls": os.path.join("dataset", "externos", "gt_nightowls.json"),
      "citypersons_convencion": os.path.join("dataset", "externos", "gt_citypersons_convencion.json"),
      "test_proxy": os.path.join("dataset", "gt_test_proxy.json")}
REALES = [("nightowls", "ocluida"), ("citypersons_convencion", "heavy"), ("test_proxy", "severa")]


def corridas(v1, v3):
    """v1, v3: listas de (carpeta de resultados, nombre de corrida). Devuelve {clave: (variante, ruta_det_base)}."""
    out = {}
    for var, lista in (("V1", v1), ("V3", v3)):
        for d, n in lista:
            out["%s|%s|%s" % (var, d, n)] = (var, os.path.join(RAIZ, d, "det", n))
    return out


def bloques():
    m = "resultados_h12m"
    s = "resultados_h12s"
    v1_m = [(m, "yolo11m_V1_s%d" % k) for k in (0, 1, 2)]
    v1_5 = [("resultados_h9b", "V1_s%d" % k) for k in (0, 1, 2)] + [(s, "V1_s%d" % k) for k in (3, 4)]
    return [
        {"clave": "H12a", "nombre": "E10 YOLOv11m, siluetas (H12a)", "control": "silueta_severa", "decide": True,
         "corridas": corridas(v1_m, [(m, "yolo11m_V3sil_s%d" % k) for k in (0, 1, 2)])},
        {"clave": "H12b", "nombre": "E10 YOLOv11m, generativa (H12b)", "control": "generativa_severa", "decide": True,
         "corridas": corridas(v1_m, [(m, "yolo11m_V3gen_s%d" % k) for k in (0, 1, 2)])},
        {"clave": "E7b_5s", "nombre": "E7b con 5 semillas (YOLOv11s, generativa)", "control": "generativa_severa", "decide": False,
         "corridas": corridas(v1_5, [("resultados_h9b", "V3_s%d" % k) for k in (0, 1, 2)] + [(s, "V3gen_s%d" % k) for k in (3, 4)])},
        {"clave": "E8sil_5s", "nombre": "E8 siluetas con 5 semillas (YOLOv11s)", "control": "silueta_severa", "decide": False,
         "corridas": corridas(v1_5, [("resultados_h10", "V3S_s%d" % k) for k in (0, 1, 2)] + [(s, "V3sil_s%d" % k) for k in (3, 4)])},
        # enmienda v3.7b: las semillas 3-4 se entrenan en RunPod; se informan tambien solas
        {"clave": "E7b_s34", "nombre": "E7b solo semillas 3-4 (RunPod)", "control": "generativa_severa", "decide": False,
         "corridas": corridas(v1_5[3:], [(s, "V3gen_s%d" % k) for k in (3, 4)])},
        {"clave": "E8sil_s34", "nombre": "E8 siluetas solo semillas 3-4 (RunPod)", "control": "silueta_severa", "decide": False,
         "corridas": corridas(v1_5[3:], [(s, "V3sil_s%d" % k) for k in (3, 4)])},
    ]


def celda(bloque, conj, est, semilla):
    gt = cargar_gt(os.path.join(RAIZ, GT[conj]))
    estr, var = {}, {}
    for c, (v, base) in bloque["corridas"].items():
        ruta = "%s__%s.json" % (base, conj)
        if not os.path.exists(ruta):
            raise FileNotFoundError(ruta)
        emp, _ = emparejar_conjunto(gt["imagenes"], cargar_detecciones(ruta)["detecciones"], estrato=est)
        estr[c], var[c] = A11.APBootstrap(emp), v
    n_img = len(gt["imagenes"])
    full = {c: e.ap() for c, e in estr.items()}
    m = lambda v: float(np.mean([full[c] for c in estr if var[c] == v]))
    d = m("V3") - m("V1")
    img = B23.bootstrap_dos_niveles(estr, var, ["V3-V1"], n_img, B_IMG, np.random.RandomState(semilla))["V3-V1"][0]
    jer = B23.bootstrap_dos_niveles(estr, var, ["V3-V1"], n_img, B_JER, np.random.RandomState(semilla + 500))["V3-V1"][1]
    li, hi = A11.ic(img); lj, hj = A11.ic(jer)
    n_gt = int(estr[next(iter(estr))].n_gt_img.sum())
    return {"bloque": bloque["clave"], "conjunto": conj, "estrato": est, "tipo": "control" if conj == bloque["control"] else "real",
            "n_gt": n_gt, "n_V1": sum(v == "V1" for v in var.values()), "n_V3": sum(v == "V3" for v in var.values()),
            "AP50_V1": round(m("V1"), 4), "AP50_V3": round(m("V3"), 4), "delta_pp": round(100 * d, 2),
            "IC_img_lo": round(100 * li, 2), "IC_img_hi": round(100 * hi, 2),
            "IC_jer_lo": round(100 * lj, 2), "IC_jer_hi": round(100 * hj, 2), "semilla_celda": semilla}


def supera(f, jer=False):
    return f["delta_pp"] >= UMBRAL and f["IC_jer_lo" if jer else "IC_img_lo"] > 0


def veredicto(filas):
    """filas de un bloque que decide: 1 control + 3 reales."""
    ctrl = [f for f in filas if f["tipo"] == "control"][0]
    if not supera(ctrl):
        return "No concluyente", 0
    n = sum(supera(f) for f in filas if f["tipo"] == "real")
    return ("Refutada" if n >= 2 else "Sostenida"), n


def analizar():
    filas = []
    i = 0
    for b in bloques():
        for conj, est in [(b["control"], "severa")] + REALES:
            f = celda(b, conj, est, i)
            print("  %-9s %-24s %-8s V3-V1 %+6.2f [%+.2f; %+.2f] jer [%+.2f; %+.2f]"
                  % (b["clave"], conj, est, f["delta_pp"], f["IC_img_lo"], f["IC_img_hi"], f["IC_jer_lo"], f["IC_jer_hi"]), flush=True)
            filas.append(f)
            i += 1
    return filas


def informe(filas):
    L = ["# ARGOS-11 — Veredicto de H12 (E10, YOLOv11m) y extensión de semillas de E7b y E8", "",
         "Generado por `30_h12.py`. AP@0.5, media de semillas. IC 95 % por imágenes (1 000 réplicas, criterio) y jerárquico "
         "(semillas + imágenes, 2 000 réplicas). Regla literal de `PREREGISTRO_H12.md`, sección 2. *: supera +2 pp con IC por imágenes > 0.", ""]
    res = {}
    for b in bloques():
        fb = [f for f in filas if f["bloque"] == b["clave"]]
        L += ["## %s" % b["nombre"], "", "| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |", "|---|---|---|---|---|---|---|"]
        for f in fb:
            L.append("| %s %s%s | %d | %.3f | %.3f | %+.2f%s | [%+.2f; %+.2f] | [%+.2f; %+.2f] |"
                     % (f["conjunto"], f["estrato"], " (control)" if f["tipo"] == "control" else "", f["n_gt"], f["AP50_V1"], f["AP50_V3"],
                        f["delta_pp"], "*" if supera(f) else "", f["IC_img_lo"], f["IC_img_hi"], f["IC_jer_lo"], f["IC_jer_hi"]))
        if b["decide"]:
            v, n = veredicto(fb)
            res[b["clave"]] = v
            L += ["", "**%s: %s** (%d de 3 fuentes reales superan +2 pp con IC por imágenes > 0; la regla exige 2 para refutar)." % (b["clave"], v.upper(), n), ""]
        else:
            nj = sum(supera(f, jer=True) for f in fb if f["tipo"] == "real")
            ni = sum(supera(f) for f in fb if f["tipo"] == "real")
            L += ["", "Secundario (no decide): %d de 3 fuentes reales superan +2 pp con IC por imágenes > 0 y %d con IC jerárquico > 0. "
                  "Según el pre-registro, solo una celda que supere con el IC jerárquico se reportaría como contraria a la conclusión con 3 semillas." % (ni, nj), ""]
    return "\n".join(L) + "\n", res


def selftest():
    fallos = []

    def comp(desc, ok):
        print("  [%s] %s" % ("OK" if ok else "FALLO", desc))
        if not ok:
            fallos.append(desc)
    F = lambda c, r: [dict(tipo="control", delta_pp=c[0], IC_img_lo=c[1])] + [dict(tipo="real", delta_pp=a, IC_img_lo=b) for a, b in r]
    comp("control falla -> no concluyente", veredicto(F((1.5, 0.3), [(5, 1)] * 3))[0] == "No concluyente")
    comp("0 de 3 -> sostenida", veredicto(F((10, 8), [(1, -1), (-3, -5), (2.5, -0.1)]))[0] == "Sostenida")
    comp("1 de 3 -> sostenida", veredicto(F((10, 8), [(2.0, 0.1), (-3, -5), (1, 0.2)])) == ("Sostenida", 1))
    comp("2 de 3 -> refutada", veredicto(F((10, 8), [(2.0, 0.1), (3, 0.5), (1, 0.2)])) == ("Refutada", 2))
    comp("+2 exacto con IC en 0 no supera", not supera(dict(delta_pp=2.0, IC_img_lo=0.0)))
    comp("jerarquico se lee aparte", supera(dict(delta_pp=3, IC_img_lo=-1, IC_jer_lo=0.5), jer=True) and not supera(dict(delta_pp=3, IC_img_lo=-1, IC_jer_lo=0.5)))
    bl = bloques()
    comp("6 bloques; 2 deciden", len(bl) == 6 and sum(b["decide"] for b in bl) == 2)
    comp("E10: 3 V1 + 3 V3 por bloque", all(sum(v == "V1" for v, _ in b["corridas"].values()) == 3 and
                                             sum(v == "V3" for v, _ in b["corridas"].values()) == 3 for b in bl[:2]))
    comp("extension: 5 V1 + 5 V3 por bloque", all(sum(v == "V1" for v, _ in b["corridas"].values()) == 5 and
                                                   sum(v == "V3" for v, _ in b["corridas"].values()) == 5 for b in bl[2:4]))
    comp("solo s3-4: 2 V1 + 2 V3", all(sum(v == "V1" for v, _ in b["corridas"].values()) == 2 and
                                        sum(v == "V3" for v, _ in b["corridas"].values()) == 2 for b in bl[4:]))
    comp("E7b_5s reutiliza V3_s0-2 de H9b", any(p.endswith(os.path.join("resultados_h9b", "det", "V3_s2")) for _, p in bl[2]["corridas"].values()))
    print("\n%s" % ("AUTOTEST SUPERADO: %d/%d" % (11 - len(fallos), 11) if not fallos else "FALLOS: %s" % fallos))
    sys.exit(1 if fallos else 0)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - H12 (YOLOv11m) y extension de semillas")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    filas = analizar()
    md, res = informe(filas)
    out = os.path.join(RAIZ, "resultados_h12", "analisis")
    os.makedirs(out, exist_ok=True)
    json.dump(filas, open(os.path.join(out, "contrastes_h12.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    import pandas as pd
    pd.DataFrame(filas).to_csv(os.path.join(out, "contrastes_h12.csv"), index=False)
    open(os.path.join(RAIZ, "informes", "veredicto_h12.md"), "w", encoding="utf-8").write(md)
    print(md)
    for k, v in res.items():
        print("%s: %s" % (k, v))


if __name__ == "__main__":
    main()
