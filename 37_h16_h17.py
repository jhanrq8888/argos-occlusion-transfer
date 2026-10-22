#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Veredictos de H16a, H16b y H17 (PREREGISTRO_H16_H17.md, E13).
  H16a  Faster R-CNN, V3gen - V1 (V1 de H15), control generativa_severa; prediccion: transferencia
  H16b  Faster R-CNN, V3prof - V1 (V1 de H15), control profundidad_severa; prediccion: transferencia
  H17   RetinaNet, V3sil - V1 (V1 propia), control silueta_severa; prediccion: no transferencia
Regla de H4-H15 sobre 1 control + 3 fuentes reales, con celda() y veredicto() de 30_h12.py (que devuelven el veredicto
respecto de la prediccion de NO transferencia). En H16a/H16b la prediccion es la contraria: 'Refutada' de 30_h12
(2 o 3 fuentes superan) es 'Sostenida' aqui y viceversa; 'No concluyente' (el control falla) no cambia.
Secundarios declarados (no deciden): controles de las otras familias, V3 - V1 por estrato (resumen_ap.csv de 09_) y la
replica de V1 semilla 0 de Faster R-CNN entre pods.
Escribe resultados_h16/analisis/contrastes_h16_h17.json e informes/veredicto_h16_h17.md.

Uso:  python 37_h16_h17.py   |   python 37_h16_h17.py --selftest
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
CONTROLES = ["silueta_severa", "generativa_severa", "geometria_severa", "profundidad_severa"]
for _c in CONTROLES:
    H12.GT.setdefault(_c, os.path.join("dataset", "test_sintetico", _c, "gt_%s.json" % _c))
ESTRATOS = {"nightowls": ["sin", "ocluida"], "citypersons_convencion": ["bare", "partial", "heavy"],
            "test_proxy": ["sin", "ligera", "moderada", "severa"]}
INVERTIR = {"Refutada": "Sostenida", "Sostenida": "Refutada", "No concluyente": "No concluyente"}


def bloques():
    h15, h16, h17 = "resultados_h15", "resultados_h16", "resultados_h17"
    v1_frcnn = [(h15, "V1_s%d" % k) for k in (0, 1, 2)]
    return [
        {"clave": "H16a", "nombre": "E13 Faster R-CNN, generativa (H16a)", "control": "generativa_severa", "decide": True,
         "prediccion": "transferencia", "v1": v1_frcnn, "v3": [(h16, "V3gen_s%d" % k) for k in (0, 1, 2)],
         "corridas": H12.corridas(v1_frcnn, [(h16, "V3gen_s%d" % k) for k in (0, 1, 2)])},
        {"clave": "H16b", "nombre": "E13 Faster R-CNN, profundidad (H16b)", "control": "profundidad_severa", "decide": True,
         "prediccion": "transferencia", "v1": v1_frcnn, "v3": [(h16, "V3prof_s%d" % k) for k in (0, 1, 2)],
         "corridas": H12.corridas(v1_frcnn, [(h16, "V3prof_s%d" % k) for k in (0, 1, 2)])},
        {"clave": "H17", "nombre": "E13 RetinaNet, siluetas (H17)", "control": "silueta_severa", "decide": True,
         "prediccion": "no transferencia", "v1": [(h17, "V1_s%d" % k) for k in (0, 1, 2)],
         "v3": [(h17, "V3sil_s%d" % k) for k in (0, 1, 2)],
         "corridas": H12.corridas([(h17, "V1_s%d" % k) for k in (0, 1, 2)], [(h17, "V3sil_s%d" % k) for k in (0, 1, 2)])},
    ]


def veredicto(b, filas):
    v, n = H12.veredicto(filas)
    return (INVERTIR[v] if b["prediccion"] == "transferencia" else v), n


def ap_resumen(d, corrida, conj, est):
    """AP@0.5 de una corrida en un conjunto y estrato (luz 'todas') leido de <d>/resumen_ap.csv de 09_."""
    with open(os.path.join(RAIZ, d, "resumen_ap.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["corrida"] == corrida and r["conjunto"] == conj and r["estrato"] == est and r["luz"] == "todas":
                return float(r["AP50"]), int(r["n_gt"])
    raise KeyError((d, corrida, conj, est))


def por_estrato(b):
    out = []
    for conj, ests in ESTRATOS.items():
        for est in ests:
            try:
                a1 = [ap_resumen(d, n, conj, est) for d, n in b["v1"]]
                a3 = [ap_resumen(d, n, conj, est) for d, n in b["v3"]]
            except (FileNotFoundError, KeyError):
                continue
            out.append({"bloque": b["clave"], "conjunto": conj, "estrato": est, "n_gt": a1[0][1],
                        "AP50_V1": round(float(np.mean([x for x, _ in a1])), 4), "AP50_V3": round(float(np.mean([x for x, _ in a3])), 4),
                        "delta_pp": round(100 * (np.mean([x for x, _ in a3]) - np.mean([x for x, _ in a1])), 2)})
    return out


def replica():
    out = []
    for conj, est in H12.REALES + [(c, "severa") for c in CONTROLES]:
        try:
            a, n = ap_resumen("resultados_h15", "V1_s0", conj, est)
            r, _ = ap_resumen("resultados_h16", "V1rep_s0", conj, est)
        except (FileNotFoundError, KeyError):
            continue
        out.append({"conjunto": conj, "estrato": est, "n_gt": n, "AP50_H15": round(a, 4), "AP50_rep": round(r, 4),
                    "dif_pp": round(100 * (r - a), 2), "real": (conj, est) in H12.REALES})
    return out


def selftest():
    bs = bloques()
    ctrl = lambda d, lo: {"tipo": "control", "delta_pp": d, "IC_img_lo": lo}
    real = lambda d, lo: {"tipo": "real", "delta_pp": d, "IC_img_lo": lo}
    pasa2 = [ctrl(9, 5), real(3, 1), real(3, 1), real(-1, -3)]
    pasa0 = [ctrl(9, 5), real(0, -1), real(1, -1), real(3, -1)]
    falla = [ctrl(1, -1), real(3, 1), real(3, 1), real(3, 1)]
    ok = [len(bs) == 3 and all(len(b["corridas"]) == 6 for b in bs),
          all(b["control"] in H12.GT for b in bs) and all(c in H12.GT for c in CONTROLES),
          veredicto(bs[0], pasa2)[0] == "Sostenida" and veredicto(bs[0], pasa0)[0] == "Refutada",
          veredicto(bs[2], pasa2)[0] == "Refutada" and veredicto(bs[2], pasa0)[0] == "Sostenida",
          veredicto(bs[1], falla)[0] == "No concluyente" and veredicto(bs[2], falla)[0] == "No concluyente",
          # H16 reutiliza las V1 de H15 (mismas rutas de deteccion que 36_h15.py); H17 tiene V1 propia
          bs[0]["v1"] == bs[1]["v1"] == [("resultados_h15", "V1_s%d" % k) for k in (0, 1, 2)] and bs[2]["v1"][0][0] == "resultados_h17"]
    print("AUTOTEST %s: %d/%d" % ("SUPERADO" if all(ok) else "FALLIDO", sum(ok), len(ok)))
    return all(ok)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - veredictos de H16a, H16b y H17")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    fila = lambda f: "| %s %s | %d | %.3f | %.3f | %+.2f%s | [%+.2f; %+.2f] | [%+.2f; %+.2f] |" % (
        f["conjunto"], f["estrato"], f["n_gt"], f["AP50_V1"], f["AP50_V3"], f["delta_pp"], "*" if H12.supera(f) else "",
        f["IC_img_lo"], f["IC_img_hi"], f["IC_jer_lo"], f["IC_jer_hi"])
    cab = ["| Celda | n | V1 | V3 | V3 − V1 | IC imágenes | IC jerárquico |", "|---|---|---|---|---|---|---|"]
    L = ["# ARGOS-11 — Veredictos de H16a, H16b y H17 (E13)", "",
         "Generado por `37_h16_h17.py`. AP@0.5, media de 3 semillas; IC 95 % por imágenes (criterio) y jerárquico; "
         "* = supera +2 pp con IC por imágenes > 0. Regla literal de `PREREGISTRO_H16_H17.md`.", ""]
    todo, i = [], 0
    for b in bloques():
        filas = []
        for c, e in [(b["control"], "severa")] + H12.REALES:
            filas.append(H12.celda(b, c, e, i)); i += 1
        v, n = veredicto(b, filas)
        sec = []
        for c in CONTROLES:
            if c == b["control"]:
                continue
            try:
                f = H12.celda(b, c, "severa", 100 + i); f["tipo"] = "secundario"; sec.append(f); i += 1
            except (FileNotFoundError, KeyError):
                pass
        est = por_estrato(b)
        L += ["## %s — predicción: %s" % (b["nombre"], b["prediccion"]), ""] + cab + [fila(f) for f in filas]
        L += ["", "**Veredicto %s: %s** (%d de 3 fuentes reales superan +2 pp con IC por imágenes > 0; control %s)" % (
            b["clave"], v.upper(), n, "supera" if H12.supera(filas[0]) else "NO supera"), ""]
        if sec:
            L += ["Secundario (no decide): controles de otras familias", ""] + cab + [fila(f) for f in sec] + [""]
        if est:
            L += ["Secundario (no decide): V3 − V1 por estrato (AP@0.5 de `resumen_ap.csv`)", "",
                  "| Fuente | Estrato | n | V1 | V3 | V3 − V1 |", "|---|---|---|---|---|---|"]
            L += ["| %s | %s | %d | %.3f | %.3f | %+.2f |" % (f["conjunto"], f["estrato"], f["n_gt"], f["AP50_V1"], f["AP50_V3"],
                                                            f["delta_pp"]) for f in est] + [""]
        for f in filas + sec:
            f["veredicto_bloque"] = v
        todo += filas + sec + [dict(f, tipo="estrato") for f in est]
    rep = replica()
    if rep:
        L += ["## Secundario (no decide): réplica de V1 semilla 0 de Faster R-CNN entre pods", "",
              "| Celda | n | V1_s0 de H15 | V1rep_s0 | Diferencia (pp) |", "|---|---|---|---|---|"]
        L += ["| %s %s | %d | %.3f | %.3f | %+.2f |" % (f["conjunto"], f["estrato"], f["n_gt"], f["AP50_H15"], f["AP50_rep"],
                                                     f["dif_pp"]) for f in rep]
        g = max(abs(f["dif_pp"]) for f in rep if f["real"]) if any(f["real"] for f in rep) else float("nan")
        L += ["", "Mayor diferencia en una fuente real: %.2f pp (umbral declarado 2 pp: %s)" % (
            g, "SUPERADO, H16 se interpreta con cautela" if g > 2 else "no superado"), ""]
        todo += [dict(f, tipo="replica") for f in rep]
    os.makedirs(os.path.join(RAIZ, "resultados_h16", "analisis"), exist_ok=True)
    json.dump(todo, open(os.path.join(RAIZ, "resultados_h16", "analisis", "contrastes_h16_h17.json"), "w", encoding="utf-8"), indent=1)
    open(os.path.join(RAIZ, "informes", "veredicto_h16_h17.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
