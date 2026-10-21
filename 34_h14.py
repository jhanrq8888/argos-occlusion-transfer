#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Veredicto de H14 (PREREGISTRO_H14.md, E11: oclusores con orden de profundidad).
V3prof - V1 (YOLOv11s, 30 epocas fijas, last.pt, semillas 0-2, RunPod), control profundidad_severa y las tres
fuentes reales; regla de H4/H8/H9/H9b/H10/H12 (refutada si 2 de 3 fuentes superan +2 pp con IC por imagenes > 0;
no concluyente si el control falla). Reutiliza celda() y veredicto() de 30_h12.py.
Lee resultados_h14/det/{V1_sN, V3prof_sN}__{conjunto}.json; escribe resultados_h14/analisis/contrastes_h14.json
e informes/veredicto_h14.md.

Uso:  python 34_h14.py   |   python 34_h14.py --selftest
"""
import argparse
import importlib.util
import json
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("h12", os.path.join(RAIZ, "30_h12.py"))
H12 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(H12)
H12.GT["profundidad_severa"] = os.path.join("dataset", "test_sintetico", "profundidad_severa", "gt_profundidad_severa.json")


def bloque():
    d = "resultados_h14"
    return {"clave": "H14", "nombre": "E11 orden de profundidad (H14)", "control": "profundidad_severa", "decide": True,
            "corridas": H12.corridas([(d, "V1_s%d" % k) for k in (0, 1, 2)], [(d, "V3prof_s%d" % k) for k in (0, 1, 2)])}


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - veredicto de H14")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        b = bloque()
        ok = [len(b["corridas"]) == 6, b["control"] in H12.GT,
              H12.veredicto([{"tipo": "control", "delta_pp": 9, "IC_img_lo": 5}] + [{"tipo": "real", "delta_pp": 3, "IC_img_lo": 1}] * 2
                            + [{"tipo": "real", "delta_pp": -1, "IC_img_lo": -3}])[0] == "Refutada"]
        print("AUTOTEST %s: %d/3" % ("SUPERADO" if all(ok) else "FALLIDO", sum(ok)))
        sys.exit(0 if all(ok) else 1)
    b = bloque()
    filas = [H12.celda(b, c, e, i) for i, (c, e) in enumerate([(b["control"], "severa")] + H12.REALES)]
    v, n = H12.veredicto(filas)
    L = ["# ARGOS-11 — Veredicto de H14 (E11, oclusores con orden de profundidad)", "",
         "Generado por `34_h14.py`. AP@0.5, media de 3 semillas; IC 95 % por imágenes (criterio) y jerárquico. Regla literal de `PREREGISTRO_H14.md`.", "",
         "| Celda | n | V1 | V3prof | V3 − V1 | IC imágenes | IC jerárquico |", "|---|---|---|---|---|---|---|"]
    L += ["| %s %s | %d | %.3f | %.3f | %+.2f%s | [%+.2f; %+.2f] | [%+.2f; %+.2f] |" % (f["conjunto"], f["estrato"], f["n_gt"], f["AP50_V1"], f["AP50_V3"],
          f["delta_pp"], "*" if H12.supera(f) else "", f["IC_img_lo"], f["IC_img_hi"], f["IC_jer_lo"], f["IC_jer_hi"]) for f in filas]
    L += ["", "## Veredicto H14: **%s** (%d de 3 fuentes reales superan +2 pp con IC por imágenes > 0; la regla exige 2 para refutar)" % (v.upper(), n)]
    os.makedirs(os.path.join(RAIZ, "resultados_h14", "analisis"), exist_ok=True)
    json.dump(filas, open(os.path.join(RAIZ, "resultados_h14", "analisis", "contrastes_h14.json"), "w", encoding="utf-8"), indent=1)
    open(os.path.join(RAIZ, "informes", "veredicto_h14.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
