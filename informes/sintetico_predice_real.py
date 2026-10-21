#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Analisis posterior declarado (13/10/2026): ¿predice la ganancia en el control sintetico
la ganancia en oclusion real?

Una fila por bloque con control sintetico (E1-E4, E6-E9, con E7b y las dos variantes de E8; E5 no tiene control):
V3 - V1 (AP@0.5, pp) en el control y en las tres fuentes reales (NightOwls ocluida, CityPersons heavy,
ExDark proxy severa). Todo se lee de los ficheros de resultados; no se recalcula nada.

Salidas: informes/analisis_final/sintetico_vs_real.{csv,md} y fig6_sintetico_vs_real.{png,pdf}
Uso: python informes/sintetico_predice_real.py
"""
import json
import os

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AF = os.path.join(RAIZ, "informes", "analisis_final")
REALES = [("nightowls", "ocluida", "NightOwls ocluida"), ("citypersons_convencion", "heavy", "CityPersons heavy"),
          ("test_proxy", "severa", "ExDark proxy severa")]
UMBRAL = 2.0


def de_consolidada():
    t = pd.read_csv(os.path.join(AF, "tabla_consolidada.csv"))
    nombres = {"exp1": "E1 parches", "iter2": "E2 siluetas", "yolo26s": "E3 siluetas (YOLO26s)", "h6": "E4 siluetas (CityPersons)",
               "h8": "E6 siluetas (RT-DETR-l)", "h9": "E7 generativa (época 2)"}
    filas = []
    for b, nom in nombres.items():
        s = t[t.bloque == b]
        c = s[s.tipo.str.startswith("sint")].iloc[0]
        f = {"bloque": nom, "control": c.conjunto, "sint": c.delta_pp, "sint_lo": c.IC95_lo}
        for conj, est, _ in REALES:
            r = s[(s.conjunto == conj) & (s.estrato == est)].iloc[0]
            f[conj] = r.delta_pp; f[conj + "_lo"] = r.IC95_lo
        filas.append(f)
    return filas


def de_bootstrap(nom, ruta, control):
    b = pd.read_csv(os.path.join(RAIZ, ruta))
    b = b[b.contraste == "V3-V1"]
    g = lambda conj, est: b[(b.conjunto == conj) & (b.estrato == est)].iloc[0]
    c = g(control, "severa")
    f = {"bloque": nom, "control": control, "sint": c.delta_AP50_pp, "sint_lo": c.IC95_lo_pp}
    for conj, est, _ in REALES:
        r = g(conj, est)
        f[conj] = r.delta_AP50_pp; f[conj + "_lo"] = r.IC95_lo_pp
    return f


def de_h10(nom, contraste, control):
    b = pd.read_csv(os.path.join(RAIZ, "resultados_h10", "analisis", "contrastes_h10.csv"))
    b = b[b.contraste == contraste]
    g = lambda conj, est: b[(b.conjunto == conj) & (b.estrato == est)].iloc[0]
    c = g(control, "severa")
    f = {"bloque": nom, "control": control, "sint": c.delta_pp, "sint_lo": c.IC_imagenes_lo}
    for conj, est, _ in REALES:
        r = g(conj, est)
        f[conj] = r.delta_pp; f[conj + "_lo"] = r.IC_imagenes_lo
    return f


def de_json(nom, ruta, bloque):
    """Bloques de 30_h12.py / 34_h14.py (anadidos el 17/10/2026 al cerrar H12 y H14)."""
    fs = [f for f in json.load(open(os.path.join(RAIZ, ruta), encoding="utf-8")) if f["bloque"] == bloque]
    c = [f for f in fs if f["tipo"] == "control"][0]
    f = {"bloque": nom, "control": c["conjunto"], "sint": c["delta_pp"], "sint_lo": c["IC_img_lo"]}
    for conj, est, _ in REALES:
        r = [x for x in fs if x["conjunto"] == conj and x["estrato"] == est][0]
        f[conj] = r["delta_pp"]; f[conj + "_lo"] = r["IC_img_lo"]
    return f


def main():
    filas = de_consolidada()
    filas.append(de_bootstrap("E7b generativa (30 épocas)", "resultados_h9b/analisis/bootstrap.csv", "generativa_severa"))
    filas.append(de_h10("E8 geometría real (30 épocas)", "V3G-V1", "geometria_severa"))
    filas.append(de_h10("E8 siluetas (30 épocas)", "V3S-V1", "silueta_severa"))
    filas.append(de_bootstrap("E9 siluetas (CityPersons, 60 épocas)", "resultados_h11/analisis/bootstrap.csv", "cp_silueta_severa"))
    filas.append(de_json("E10 siluetas (YOLOv11m)", "resultados_h12/analisis/contrastes_h12.json", "H12a"))
    filas.append(de_json("E10 generativa (YOLOv11m)", "resultados_h12/analisis/contrastes_h12.json", "H12b"))
    filas.append(de_json("E11 orden de profundidad", "resultados_h14/analisis/contrastes_h14.json", "H14"))
    d = pd.DataFrame(filas)
    d["real_media"] = d[[c for c, _, _ in REALES]].mean(axis=1)
    d.to_csv(os.path.join(AF, "sintetico_vs_real.csv"), index=False)

    pasa = lambda v, lo: (v >= UMBRAL) & (lo > 0)
    n_sint = int(pasa(d.sint, d.sint_lo).sum())
    celdas = [(r.bloque, conj, r[conj], r[conj + "_lo"]) for _, r in d.iterrows() for conj, _, _ in REALES]
    n_real = sum(1 for _, _, v, lo in celdas if v >= UMBRAL and lo > 0)
    n_neg = sum(1 for _, _, v, _ in celdas if v < 0)
    res = {"bloques": len(d), "controles_que_pasan": n_sint, "celdas_reales": len(celdas), "celdas_reales_que_pasan": n_real,
           "celdas_reales_negativas": n_neg}
    rho = {}
    for conj, _, nom in REALES + [("real_media", None, "media de las 3 fuentes")]:
        r, p = spearmanr(d.sint, d[conj])
        rho[nom] = (round(float(r), 2), round(float(p), 3))
    # todas las celdas juntas (3 por bloque; no independientes)
    x = np.repeat(d.sint.values, 3); y = d[[c for c, _, _ in REALES]].values.ravel()
    r_all, p_all = spearmanr(x, y)
    res["spearman"] = rho
    res["spearman_30_celdas"] = (round(float(r_all), 2), round(float(p_all), 3))
    json.dump(res, open(os.path.join(AF, "sintetico_vs_real.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    figura(d)
    L = ["# ¿Predice la ganancia sintética la ganancia real?", "",
         "Análisis posterior declarado (13/10/2026), solo con resultados ya calculados (`informes/sintetico_predice_real.py`). "
         "V3 − V1 en AP@0.5 (pp), media de 3 semillas, IC 95 % por imágenes. No decide ninguna hipótesis.", "",
         "| Bloque | Control sintético | NightOwls ocluida | CityPersons heavy | ExDark proxy severa |", "|---|---|---|---|---|"]
    for r in d.itertuples():
        m = lambda v, lo: "%+.2f%s" % (v, "*" if v >= UMBRAL and lo > 0 else "")
        L.append("| %s | %s | %s | %s | %s |" % (r.bloque, m(r.sint, r.sint_lo), m(r.nightowls, r.nightowls_lo),
                                               m(r.citypersons_convencion, r.citypersons_convencion_lo), m(r.test_proxy, r.test_proxy_lo)))
    L += ["", "\\* supera +2 pp con IC > 0.", "",
          "- **Controles sintéticos que superan el umbral: %d de %d.** Celdas reales que lo superan: **%d de %d** (%d negativas)." % (n_sint, len(d), n_real, len(celdas), n_neg),
          "- Si se hubiera decidido solo con el banco sintético, se habría concluido que el aumento funciona en los %d bloques; "
          "con oclusión real, esa conclusión se sostiene en %d de %d celdas (valor predictivo %.0f %%)." % (n_sint, n_real, len(celdas), 100 * n_real / len(celdas)),
          "- Correlación de Spearman entre la ganancia sintética y la real, por bloque (n = %d):" % len(d)]
    for nom, (r, p) in rho.items():
        L.append("  - %s: ρ = %+.2f (p = %.3f)" % (nom, r, p))
    L += ["  - las %d celdas juntas (no independientes): ρ = %+.2f (p = %.3f)" % ((len(celdas),) + tuple(res["spearman_30_celdas"])), "",
          "**Lectura.** No hay una asociación fiable entre la ganancia en el control sintético y la ganancia en oclusión real: "
          "las correlaciones por fuente tienen signos distintos y ninguna se distingue de cero (la de la media, cercana a cero, "
          "promedia signos opuestos y no es informativa por sí sola). Con %d bloques no se descarta una asociación positiva "
          "moderada en NightOwls y CityPersons (con solo los 7 bloques de exposición igual, NightOwls da ρ = +0,64, p = 0,12). "
          "Lo que sí muestran los datos es que ganancias sintéticas de cualquier tamaño vinieron con ganancias reales bajo el "
          "umbral en casi todas las celdas: el banco sintético solo no basta para afirmar robustez a la oclusión real." % len(d)]
    open(os.path.join(AF, "SINTETICO_VS_REAL.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


def figura(d):
    for L in ("es", "en"):
        _figura(d, L)


def _figura(d, L):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    col = {"nightowls": "#2a78d4", "citypersons_convencion": "#e0782a", "test_proxy": "#1f9e76"}
    mk = {"nightowls": "o", "citypersons_convencion": "s", "test_proxy": "^"}
    plt.rcParams.update({"font.size": 9})
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.axhspan(-UMBRAL, UMBRAL, color="#bbb", alpha=0.18, lw=0)
    ax.axhline(0, color="#888", lw=1)
    for conj, _, nom in REALES:
        ax.scatter(d.sint, d[conj], s=34, marker=mk[conj], color=col[conj], label=nom if L == "es" else nom.replace("ocluida", "occluded").replace("severa", "severe"),
                   edgecolor="white", linewidth=0.8, zorder=3)
    for r in d.itertuples():
        if r.sint > 40:
            ax.annotate(r.bloque.split(" ")[0], (r.sint, max(r.nightowls, r.test_proxy, r.citypersons_convencion)),
                        xytext=(0, 6), textcoords="offset points", ha="center", fontsize=8, color="#444")
    ax.set_xlabel("V3 − V1 en el control sintético (AP@0.5, pp)" if L == "es" else "V3 − V1 on the synthetic control (AP@0.5, pp)")
    ax.set_ylabel("V3 − V1 en oclusión real (AP@0.5, pp)" if L == "es" else "V3 − V1 on real occlusion (AP@0.5, pp)")
    ax.grid(alpha=0.25); ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(AF, "fig6_sintetico_vs_real%s.%s" % ("" if L == "es" else "_en", ext)), dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    main()
