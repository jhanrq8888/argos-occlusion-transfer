#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Veredictos de H18 (PREREGISTRO_H18.md, E14: replica de H15 con 5 semillas y dosis del aumento).
  H18a       Faster R-CNN, V3sil - V1, semillas 0-4 (replica de H15), control silueta_severa
  H18e-baja  Faster R-CNN, V3 siluetas con dosis baja - V1 (semillas 0-2, V1 de H18a)
  H18e-alta  Faster R-CNN, V3 siluetas con dosis alta - V1 (semillas 0-2, V1 de H18a)
Prediccion comun: no se detecta transferencia. Regla de H4-H17 con celda() y veredicto() de 30_h12.py ('Refutada' =
2 o 3 fuentes pasan). Cada celda lleva tambien el IC jerarquico (criterio uniforme de semillas). Secundarios: dosis-
respuesta y variacion entre maquinas frente a H15.
Escribe resultados_h18/analisis/contrastes_h18.json e informes/veredicto_h18.md.
Uso:  python 38_h18.py   |   python 38_h18.py --selftest
"""
import argparse
import csv
import importlib.util
import json
import os
import sys

import numpy as np

RAIZ = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("h12", os.path.join(RAIZ, "30_h12.py"))
H12 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(H12)
H12.GT.setdefault("silueta_severa", os.path.join("dataset", "test_sintetico", "silueta_severa", "gt_silueta_severa.json"))
F = "resultados_h18"


def bloques():
    v1_5 = [(F, "V1_s%d" % k) for k in range(5)]
    v1_3 = v1_5[:3]
    return [
        {"clave": "H18a", "nombre": "E14 Faster R-CNN, siluetas, dosis base, 5 semillas (replica de H15)", "control": "silueta_severa",
         "corridas": H12.corridas(v1_5, [(F, "V3sil_s%d" % k) for k in range(5)]), "v3": "V3sil_s"},
        {"clave": "H18e-baja", "nombre": "E14 Faster R-CNN, siluetas, dosis baja", "control": "silueta_severa",
         "corridas": H12.corridas(v1_3, [(F, "V3baja_s%d" % k) for k in range(3)]), "v3": "V3baja_s"},
        {"clave": "H18e-alta", "nombre": "E14 Faster R-CNN, siluetas, dosis alta", "control": "silueta_severa",
         "corridas": H12.corridas(v1_3, [(F, "V3alta_s%d" % k) for k in range(3)]), "v3": "V3alta_s"},
    ]


def ap_semillas(carpeta, prefijo, conj, est):
    ruta = os.path.join(RAIZ, carpeta, "resumen_ap.csv")
    if not os.path.exists(ruta):
        return np.array([])
    with open(ruta, encoding="utf-8") as fh:
        return np.array([100 * float(r["AP50"]) for r in csv.DictReader(fh) if r["corrida"].startswith(prefijo)
                         and r["conjunto"] == conj and r["estrato"] == est and r["luz"] == "todas"])


def selftest():
    bs = bloques()
    ctrl = lambda d, lo: {"tipo": "control", "delta_pp": d, "IC_img_lo": lo}
    real = lambda d, lo: {"tipo": "real", "delta_pp": d, "IC_img_lo": lo}
    v1 = lambda b: [k for k in b["corridas"] if k.startswith("V1")]
    ok = [len(bs) == 3, len(bs[0]["corridas"]) == 10 and all(len(b["corridas"]) == 6 for b in bs[1:]),
          all(b["control"] in H12.GT for b in bs),
          H12.veredicto([ctrl(9, 5), real(3, 1), real(3, 1), real(0, -1)])[0] == "Refutada",
          H12.veredicto([ctrl(9, 5), real(3, -1), real(1, 0.5), real(0, -1)])[0] == "Sostenida",
          H12.veredicto([ctrl(1, -1), real(3, 1), real(3, 1), real(3, 1)])[0] == "No concluyente",
          # las dosis comparten las V1 (semillas 0-2) de H18a, de la misma maquina
          v1(bs[1]) == v1(bs[2]) == v1(bs[0])[:3]]
    print("AUTOTEST %s: %d/%d" % ("SUPERADO" if all(ok) else "FALLIDO", sum(ok), len(ok)))
    return all(ok)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - veredictos de H18")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    fila = lambda f: "| %s %s | %d | %.3f | %.3f | %+.2f%s | [%+.2f; %+.2f] | [%+.2f; %+.2f]%s |" % (
        f["conjunto"], f["estrato"], f["n_gt"], f["AP50_V1"], f["AP50_V3"], f["delta_pp"], "*" if H12.supera(f) else "",
        f["IC_img_lo"], f["IC_img_hi"], f["IC_jer_lo"], f["IC_jer_hi"], "*" if H12.supera(f, jer=True) else "")
    L = ["# ARGOS-11 — Veredictos de H18 (E14, réplica de H15 con 5 semillas y dosis del aumento)", "",
         "Generado por `38_h18.py`. AP@0.5, media de semillas; IC 95 % por imágenes (regla) y jerárquico (criterio uniforme "
         "de semillas); * = pasa (+2 pp con IC > 0). Regla literal de `PREREGISTRO_H18.md`; predicción común: no se detecta "
         "transferencia («Refutada» = 2 o 3 fuentes pasan).", ""]
    todo, i = [], 0
    for b in bloques():
        filas = []
        for c, e in [(b["control"], "severa")] + H12.REALES:
            filas.append(H12.celda(b, c, e, 400 + i)); i += 1
        v, n = H12.veredicto(filas)
        L += ["## %s" % b["nombre"], "", "| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |", "|---|---|---|---|---|---|---|"]
        L += [fila(f) for f in filas]
        L += ["", "**Veredicto %s: %s** (%d de 3 fuentes reales pasan; control %s)" % (b["clave"], v.upper(), n,
                                                                                   "pasa" if H12.supera(filas[0]) else "NO pasa"), ""]
        for f in filas:
            f["bloque"], f["veredicto_bloque"] = b["clave"], v
        todo += filas
    # secundario: dosis-respuesta (semillas 0-2, mismas V1)
    L += ["## Secundario: dosis-respuesta (semillas 0-2, V3 − V1 en pp)", "", "| Celda | baja | base | alta |", "|---|---|---|---|"]
    for conj, est in [("silueta_severa", "severa")] + H12.REALES:
        v1 = ap_semillas(F, "V1_s", conj, est)[:3]
        d = [ap_semillas(F, p, conj, est)[:3].mean() - v1.mean() if len(v1) else float("nan")
             for p in ("V3baja_s", "V3sil_s", "V3alta_s")]
        L.append("| %s %s | %+.2f | %+.2f | %+.2f |" % (conj, est, *d))
    # secundario: variacion entre maquinas (semillas 0-2) frente a H15
    L += ["", "## Secundario: H18a frente a H15 (semillas 0-2, AP@0.5 medio en pp)", "",
          "| Fuente | V1 H15 | V1 H18a | V3 H15 | V3 H18a |", "|---|---|---|---|---|"]
    for conj, est in H12.REALES:
        m = lambda x: "%.2f" % x.mean() if len(x) else "—"
        L.append("| %s %s | %s | %s | %s | %s |" % (conj, est, m(ap_semillas("resultados_h15", "V1_s", conj, est)[:3]),
                                                    m(ap_semillas(F, "V1_s", conj, est)[:3]),
                                                    m(ap_semillas("resultados_h15", "V3sil_s", conj, est)[:3]),
                                                    m(ap_semillas(F, "V3sil_s", conj, est)[:3])))
    os.makedirs(os.path.join(RAIZ, F, "analisis"), exist_ok=True)
    json.dump(todo, open(os.path.join(RAIZ, F, "analisis", "contrastes_h18.json"), "w", encoding="utf-8"), indent=1)
    open(os.path.join(RAIZ, "informes", "veredicto_h18.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
