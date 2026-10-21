#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Veredicto de H15 (PREREGISTRO_H15.md, E12: detector de dos etapas, Faster R-CNN).
V3sil - V1 (Faster R-CNN ResNet-50 FPN v2, 30 epocas fijas, last.pth, semillas 0-2, RunPod), control silueta_severa y
las tres fuentes reales; regla de H4/H8/H9/H9b/H10/H12/H14 (refutada si 2 de 3 fuentes superan +2 pp con IC por
imagenes > 0; no concluyente si el control falla). Reutiliza celda() y veredicto() de 30_h12.py.
Secundario declarado: los controles de las otras familias (matriz cruzada).
Lee resultados_h15/det/{V1_sN, V3sil_sN}__{conjunto}.json; escribe resultados_h15/analisis/contrastes_h15.json
e informes/veredicto_h15.md.

Uso:  python 36_h15.py   |   python 36_h15.py --selftest
"""
import argparse
import importlib.util
import json
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("h12", os.path.join(RAIZ, "30_h12.py"))
H12 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(H12)
for _c in ("generativa_severa", "geometria_severa", "profundidad_severa"):
    H12.GT.setdefault(_c, os.path.join("dataset", "test_sintetico", _c, "gt_%s.json" % _c))
OTROS_CONTROLES = ["generativa_severa", "geometria_severa", "profundidad_severa"]


def bloque():
    d = "resultados_h15"
    return {"clave": "H15", "nombre": "E12 Faster R-CNN, siluetas (H15)", "control": "silueta_severa", "decide": True,
            "corridas": H12.corridas([(d, "V1_s%d" % k) for k in (0, 1, 2)], [(d, "V3sil_s%d" % k) for k in (0, 1, 2)])}


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - veredicto de H15")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        b = bloque()
        ok = [len(b["corridas"]) == 6, b["control"] in H12.GT, all(c in H12.GT for c in OTROS_CONTROLES),
              H12.veredicto([{"tipo": "control", "delta_pp": 9, "IC_img_lo": 5}] + [{"tipo": "real", "delta_pp": 3, "IC_img_lo": 1}] * 2
                            + [{"tipo": "real", "delta_pp": -1, "IC_img_lo": -3}])[0] == "Refutada",
              H12.veredicto([{"tipo": "control", "delta_pp": 1, "IC_img_lo": -1}] + [{"tipo": "real", "delta_pp": 0, "IC_img_lo": -1}] * 3)[0]
              == "No concluyente"]
        print("AUTOTEST %s: %d/5" % ("SUPERADO" if all(ok) else "FALLIDO", sum(ok)))
        sys.exit(0 if all(ok) else 1)
    b = bloque()
    filas = [H12.celda(b, c, e, i) for i, (c, e) in enumerate([(b["control"], "severa")] + H12.REALES)]
    v, n = H12.veredicto(filas)
    sec = []
    for c in OTROS_CONTROLES:
        try:
            f = H12.celda(b, c, "severa", 100 + len(sec)); f["tipo"] = "secundario"; sec.append(f)
        except (FileNotFoundError, KeyError):
            pass
    fila = lambda f: "| %s %s | %d | %.3f | %.3f | %+.2f%s | [%+.2f; %+.2f] | [%+.2f; %+.2f] |" % (
        f["conjunto"], f["estrato"], f["n_gt"], f["AP50_V1"], f["AP50_V3"], f["delta_pp"], "*" if H12.supera(f) else "",
        f["IC_img_lo"], f["IC_img_hi"], f["IC_jer_lo"], f["IC_jer_hi"])
    L = ["# ARGOS-11 — Veredicto de H15 (E12, Faster R-CNN, siluetas)", "",
         "Generado por `36_h15.py`. AP@0.5, media de 3 semillas; IC 95 % por imágenes (criterio) y jerárquico. Regla literal de `PREREGISTRO_H15.md`.", "",
         "| Celda | n | V1 | V3sil | V3 − V1 | IC imágenes | IC jerárquico |", "|---|---|---|---|---|---|---|"]
    L += [fila(f) for f in filas]
    L += ["", "## Veredicto H15: **%s** (%d de 3 fuentes reales superan +2 pp con IC por imágenes > 0; la regla exige 2 para refutar)" % (v.upper(), n)]
    if sec:
        L += ["", "## Secundario (no decide): controles de otras familias", "", "| Celda | n | V1 | V3sil | V3 − V1 | IC imágenes | IC jerárquico |",
              "|---|---|---|---|---|---|---|"] + [fila(f) for f in sec]
    os.makedirs(os.path.join(RAIZ, "resultados_h15", "analisis"), exist_ok=True)
    json.dump(filas + sec, open(os.path.join(RAIZ, "resultados_h15", "analisis", "contrastes_h15.json"), "w", encoding="utf-8"), indent=1)
    open(os.path.join(RAIZ, "informes", "veredicto_h15.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
