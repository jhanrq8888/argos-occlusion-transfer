#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Analisis pedidos por el reporte de seguimiento del 11/11/2026 (posteriores y declarados; ninguno cambia una
regla ni un veredicto registrado).
  obs. 11  IC por celda con la varianza entre semillas (t de Welch con los AP por semilla de V1 y V3) en las 42 celdas
           reales de la evidencia primaria; recuento de celdas que pasan la regla y que descartan +2 pp con ese IC.
  obs. 17  especificidad en una segunda escala: cambio relativo (V3/V1 - 1) y diferencia en logit del AP, en personas
           ocluidas y sin oclusion, para los bloques de Faster R-CNN con siluetas (H15, H18a, H18e-b, H18e-a).
Salida: informes/analisis_final/revision_11nov.json, ic_welch_celdas.csv, especificidad_escalas.csv
Uso: python informes/revision_11nov.py
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AF = os.path.join(RAIZ, "informes", "analisis_final")
UMBRAL = 2.0
# bloque -> (carpeta de V1, prefijo V1, carpeta de V3, prefijo V3, semillas de V1 o None para todas)
BLOQUES = {
    "h9b": ("resultados_h9b", "V1_s", "resultados_h9b", "V3_s", None),
    "h10g": ("resultados_h10", "V1_s", "resultados_h10", "V3G_s", None),
    "h10s": ("resultados_h10", "V1_s", "resultados_h10", "V3S_s", None),
    "h11": ("resultados_h11", "V1_s", "resultados_h11", "V3_s", None),
    "h12a": ("resultados_h12m", "yolo11m_V1_s", "resultados_h12m", "yolo11m_V3sil_s", None),
    "h12b": ("resultados_h12m", "yolo11m_V1_s", "resultados_h12m", "yolo11m_V3gen_s", None),
    "h14": ("resultados_h14", "V1_s", "resultados_h14", "V3prof_s", None),
    "h15": ("resultados_h15", "V1_s", "resultados_h15", "V3sil_s", None),
    "h16a": ("resultados_h15", "V1_s", "resultados_h16", "V3gen_s", None),
    "h16b": ("resultados_h15", "V1_s", "resultados_h16", "V3prof_s", None),
    "h17": ("resultados_h17", "V1_s", "resultados_h17", "V3sil_s", None),
    "h18a": ("resultados_h18", "V1_s", "resultados_h18", "V3sil_s", None),
    "h18e_baja": ("resultados_h18", "V1_s", "resultados_h18", "V3baja_s", [0, 1, 2]),
    "h18e_alta": ("resultados_h18", "V1_s", "resultados_h18", "V3alta_s", [0, 1, 2]),
}
SIN = {"nightowls": "sin", "citypersons_convencion": "bare", "test_proxy": "sin"}


def ap(carpeta, prefijo, conj, est, semillas=None):
    d = pd.read_csv(os.path.join(RAIZ, carpeta, "resumen_ap.csv"))
    d = d[(d.conjunto == conj) & (d.estrato == est) & (d.luz == "todas") & d.corrida.str.match(prefijo)]
    if semillas is not None:
        d = d[d.corrida.str.extract(r"_s(\d+)$")[0].astype(int).isin(semillas)]
    return d.sort_values("corrida").AP50.values * 100


def welch(x1, x3):
    v1, v3 = x1.var(ddof=1) / len(x1), x3.var(ddof=1) / len(x3)
    se = np.sqrt(v1 + v3)
    gl = se ** 4 / (v1 ** 2 / (len(x1) - 1) + v3 ** 2 / (len(x3) - 1))
    t = stats.t.ppf(0.975, gl)
    dlt = x3.mean() - x1.mean()
    return dlt, dlt - t * se, dlt + t * se, gl


def main():
    c = pd.read_csv(os.path.join(AF, "celdas_con_h18.csv"))
    c = c[(c.tipo == "real") & (c.exposicion == "igual (epocas fijas)")]
    filas = []
    for _, r in c.iterrows():
        f1, p1, f3, p3, sem = BLOQUES[r.bloque]
        x1, x3 = ap(f1, p1, r.conjunto, r.estrato, sem), ap(f3, p3, r.conjunto, r.estrato)
        d, lo, hi, gl = welch(x1, x3)
        filas.append({"bloque": r.bloque, "etiqueta": r.etiqueta, "fuente": r.fuente, "delta_tabla": r.delta,
                      "delta_semillas": round(d, 2), "n_V1": len(x1), "n_V3": len(x3),
                      "img_lo": r.ic_lo, "img_hi": r.ic_hi, "jer_lo": r.jer_lo, "jer_hi": r.jer_hi,
                      "welch_lo": round(lo, 2), "welch_hi": round(hi, 2), "gl": round(gl, 1),
                      "pasa_regla": bool(r.pasa), "pasa_jer": bool(r.pasa_jer),
                      "pasa_welch": bool(d >= UMBRAL and lo > 0),
                      "descarta_jer": bool(r.descarta_2pp_jer), "descarta_welch": bool(hi < UMBRAL),
                      "dosis": "habitual" if not r.bloque.startswith("h18e") else r.bloque.split("_")[1]})
    t = pd.DataFrame(filas)
    t.to_csv(os.path.join(AF, "ic_welch_celdas.csv"), index=False)
    hab = t[t.dosis == "habitual"]
    out = {"celdas_primarias_habitual": len(hab),
           "max_dif_delta_tabla_vs_semillas": round(float((t.delta_tabla - t.delta_semillas).abs().max()), 2),
           "pasan": {"imagenes": int(hab.pasa_regla.sum()), "jerarquico": int(hab.pasa_jer.sum()), "welch": int(hab.pasa_welch.sum())},
           "descartan_2pp": {"jerarquico": int(hab.descarta_jer.sum()), "welch": int(hab.descarta_welch.sum())},
           "ancho_medio": {"imagenes": round(float((hab.img_hi - hab.img_lo).mean()), 2),
                           "jerarquico": round(float((hab.jer_hi - hab.jer_lo).mean()), 2),
                           "welch": round(float((hab.welch_hi - hab.welch_lo).mean()), 2)},
           "celdas_que_pasan_la_regla": t[t.pasa_regla][["etiqueta", "fuente", "delta_tabla", "img_lo", "img_hi", "jer_lo", "jer_hi",
                                                          "welch_lo", "welch_hi", "n_V1", "n_V3"]].to_dict("records"),
           "descartan_welch_lista": hab[hab.descarta_welch][["etiqueta", "fuente", "delta_tabla", "welch_hi"]].to_dict("records")}
    # obs. 17: especificidad en escala relativa y logit (Faster R-CNN con siluetas)
    esp = []
    for b in ("h15", "h18a", "h18e_baja", "h18e_alta"):
        f1, p1, f3, p3, sem = BLOQUES[b]
        for conj, oc in (("nightowls", "ocluida"), ("citypersons_convencion", "heavy")):
            for estrato in (oc, SIN[conj]):
                a1, a3 = ap(f1, p1, conj, estrato, sem).mean() / 100, ap(f3, p3, conj, estrato).mean() / 100
                lg = lambda p: np.log(p / (1 - p))
                esp.append({"bloque": b, "conjunto": conj, "estrato": "ocluida" if estrato == oc else "sin oclusion",
                            "AP_V1": round(a1, 3), "AP_V3": round(a3, 3), "dif_pp": round((a3 - a1) * 100, 2),
                            "cambio_relativo_pct": round((a3 / a1 - 1) * 100, 1), "dif_logit": round(lg(a3) - lg(a1), 3),
                            "dif_tasa_fallo_relativa_pct": round(((1 - a3) / (1 - a1) - 1) * 100, 1)})
    e = pd.DataFrame(esp)
    e.to_csv(os.path.join(AF, "especificidad_escalas.csv"), index=False)
    out["especificidad"] = esp
    json.dump(out, open(os.path.join(AF, "revision_11nov.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items() if k != "especificidad"}, indent=1, ensure_ascii=False))
    print(e.to_string())


if __name__ == "__main__":
    main()
