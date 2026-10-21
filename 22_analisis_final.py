#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Analisis final consolidado (cronograma: "Analisis final consolidado y
figuras definitivas"). No recalcula nada: lee los bootstrap.csv, descriptivo.csv,
diagnostico_transferencia.csv y resumen_costo.csv ya generados por cada bloque.

Bloques (todos V1 = base, V3 = aumento de oclusion; mismo evaluador):
  exp1      parches v1, YOLOv11s, entrenado en ExDark        resultados/analisis/
  iter2     siluetas v2, YOLOv11s, entrenado en ExDark       resultados_v2/analisis_yolo11s/
  yolo26s   siluetas v2, YOLO26s, entrenado en ExDark        resultados_v2/analisis_yolo26s/
  h6        siluetas v2, YOLOv11s, entrenado en CityPersons  resultados_h6/analisis/
  h7        siluetas v2, YOLOv11s, entrenado en NightOwls    resultados_h7_20000/analisis/ (+ escalera)

Salidas en informes/analisis_final/:
  tabla_consolidada.csv / .md      V1, V3, V3-V1 [IC] por bloque y conjunto
  fig1_bloques_sintetico_vs_real   efecto del aumento en cada bloque y conjunto
  fig2_h7_escalera                 AP de V1 y V3 frente al tamano del entrenamiento
  fig3_mecanismo                   recall y falsos positivos, V1 -> V3
  fig4_costo                       FPS por variante frente a los criterios del PPI

Uso:
    python 22_analisis_final.py
    python 22_analisis_final.py --selftest
"""
import argparse
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(RAIZ, "informes", "analisis_final")

# Paleta validada (dataviz, modo claro): slot 1 azul = V1 / sintetico, slot 2 naranja = V3 / real
AZUL, NARANJA = "#2a78d6", "#eb6834"
TINTA, TINTA2, TENUE, REJILLA, SUPERFICIE = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"

BLOQUES = [  # clave, etiqueta, carpeta de analisis, control sintetico (conjunto, estrato), semillas
    ("exp1", "Exp. 1 · parches\nYOLOv11s · ExDark", "resultados/analisis", ("opaco_severa", "severa"), 3),
    ("iter2", "Iter. 2 · siluetas\nYOLOv11s · ExDark", "resultados_v2/analisis_yolo11s", ("silueta_severa", "severa"), 3),
    ("yolo26s", "Generalidad · siluetas\nYOLO26s · ExDark", "resultados_v2/analisis_yolo26s", ("silueta_severa", "severa"), 3),
    ("h6", "H6 · siluetas\nYOLOv11s · CityPersons", "resultados_h6/analisis", ("cp_silueta_severa", "severa"), 3),
    ("h7", "H7 · siluetas\nYOLOv11s · NightOwls 20k", "resultados_h7_20000/analisis", None, 3),
    ("h8", "H8 · siluetas\nRT-DETR-l · ExDark", "resultados_h8/analisis", ("silueta_severa", "severa"), 3),
    ("h9", "H9 · generativa\nYOLOv11s · ExDark", "resultados_h9/analisis", ("generativa_severa", "severa"), 3),
]
BLOQUES = [b for b in BLOQUES if os.path.exists(os.path.join(RAIZ, b[2], "bootstrap.csv"))]
REALES = [("nightowls", "ocluida", "NightOwls\npeatones ocluidos"),
          ("citypersons_convencion", "heavy", "CityPersons\nheavy (vis. 20–65 %)"),
          ("test_proxy", "severa", "ExDark\noclusión severa (proxy)")]
UMBRAL = 2.0
NUM = {3: "tres", 4: "cuatro", 5: "cinco", 6: "seis", 7: "siete"}
_RJ = os.path.join(RAIZ, "informes", "analisis_final", "bootstrap_jerarquico.csv")
JER = pd.read_csv(_RJ) if os.path.exists(_RJ) else None   # de 23_bootstrap_jerarquico.py


def _estilo():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": TENUE, "axes.linewidth": 0.8,
        "axes.labelcolor": TINTA2, "xtick.color": TINTA2, "ytick.color": TINTA2, "axes.titlecolor": TINTA,
        "axes.titlesize": 10, "axes.titleweight": "bold", "figure.facecolor": SUPERFICIE,
        "axes.facecolor": SUPERFICIE, "savefig.facecolor": SUPERFICIE, "legend.frameon": False,
    })


def _guardar(fig, nombre):
    os.makedirs(SALIDA, exist_ok=True)
    fig.savefig(os.path.join(SALIDA, nombre + ".png"), dpi=220, bbox_inches="tight")
    fig.savefig(os.path.join(SALIDA, nombre + ".pdf"), bbox_inches="tight")
    plt.close(fig)


def contraste(dir_an, conj, est, k="V3-V1"):
    ruta = os.path.join(RAIZ, dir_an, "bootstrap.csv")
    if not os.path.exists(ruta):
        return None
    b = pd.read_csv(ruta)
    r = b[(b.conjunto == conj) & (b.estrato == est) & (b.contraste == k)]
    if r.empty:
        return None
    r = r.iloc[0]
    return {"delta": float(r.delta_AP50_pp), "lo": float(r.IC95_lo_pp), "hi": float(r.IC95_hi_pp),
            "excluye0": bool(r.excluye_cero), "n": int(r.n_gt)}


def media(dir_an, conj, est, var):
    d = pd.read_csv(os.path.join(RAIZ, dir_an, "descriptivo.csv"))
    r = d[(d.conjunto == conj) & (d.estrato == est) & (d.variante == var)]
    return (float(r.AP50_media.iloc[0]), float(r.AP50_sd.iloc[0])) if not r.empty else (np.nan, np.nan)


# ----------------------------------------------------------------------------- tabla
def tabla_consolidada():
    filas = []
    for clave, etiq, dir_an, sint, nsem in BLOQUES:
        sets = ([(sint[0], sint[1], "sintético (control)")] if sint else []) + [(c, e, "real") for c, e, _ in REALES]
        for conj, est, tipo in sets:
            c = contraste(dir_an, conj, est)
            if c is None:
                continue
            v1, v1sd = media(dir_an, conj, est, "V1"); v3, v3sd = media(dir_an, conj, est, "V3")
            filas.append({"bloque": clave, "descripcion": etiq.replace("\n", " · "), "semillas": nsem, "tipo": tipo,
                          "conjunto": conj, "estrato": est, "n": c["n"], "AP50_V1": round(v1, 4), "AP50_V3": round(v3, 4),
                          "delta_pp": round(c["delta"], 2), "IC95_lo": round(c["lo"], 2), "IC95_hi": round(c["hi"], 2),
                          "excluye_cero": c["excluye0"], "supera_umbral_2pp": bool(c["delta"] >= UMBRAL and c["lo"] > 0),
                          "fuente": dir_an + "/bootstrap.csv"})
    return pd.DataFrame(filas)


def tabla_md(df):
    f = lambda x: ("%+.2f" % x).replace("-", "−")
    L = ["| Bloque | Conjunto | Tipo | n | V1 | V3 | V3 − V1 (pp) | IC 95 % | ≥ +2 pp con IC > 0 |", "|---|---|---|---|---|---|---|---|---|"]
    for r in df.itertuples():
        L.append("| %s | %s / %s | %s | %d | %.3f | %.3f | **%s** | [%s; %s] | %s |" % (
            r.descripcion, r.conjunto, r.estrato, r.tipo, r.n, r.AP50_V1, r.AP50_V3, f(r.delta_pp), f(r.IC95_lo), f(r.IC95_hi),
            "sí" if r.supera_umbral_2pp else "no"))
    return "\n".join(L)


# ----------------------------------------------------------------------------- figura 1
def fig_bloques(df):
    paneles = [("sintetico", "Control sintético\n(oclusión severa)")] + [(c, t) for c, _, t in REALES]
    fig, axes = plt.subplots(1, 4, figsize=(12.5, 0.75 * len(BLOQUES) + 0.6), sharey=True, gridspec_kw={"width_ratios": [1.15, 1, 1, 1]})
    etiquetas = [b[1] for b in BLOQUES]
    ys = np.arange(len(BLOQUES))[::-1]
    for ax, (clave_p, titulo) in zip(axes, paneles):
        color = AZUL if clave_p == "sintetico" else NARANJA
        for y, (clave, _, _, sint, _) in zip(ys, BLOQUES):
            if clave_p == "sintetico":
                sub = df[(df.bloque == clave) & (df.tipo != "real")]
            else:
                sub = df[(df.bloque == clave) & (df.conjunto == clave_p)]
            if sub.empty:
                ax.text(0.5, y, "sin control sintético", transform=ax.get_yaxis_transform(), ha="center", va="center",
                        fontsize=7.5, color=TENUE, style="italic")
                continue
            r = sub.iloc[0]
            if JER is not None:
                j = JER[(JER.bloque == clave) & (JER.conjunto == r.conjunto) & (JER.estrato == r.estrato) & (JER.contraste == "V3-V1")]
                if not j.empty:
                    ax.hlines(y, j.iloc[0].IC_jerarquico_lo, j.iloc[0].IC_jerarquico_hi, color=color, lw=0.9, alpha=0.75, zorder=2)
                    for xx in (j.iloc[0].IC_jerarquico_lo, j.iloc[0].IC_jerarquico_hi):
                        ax.vlines(xx, y - 0.09, y + 0.09, color=color, lw=0.9, alpha=0.75, zorder=2)
            ax.hlines(y, r.IC95_lo, r.IC95_hi, color=color, lw=3, zorder=3)
            ax.plot(r.delta_pp, y, "o", ms=8, color=color, mec=SUPERFICIE, mew=2, zorder=4)
            ax.annotate(("%+.1f" % r.delta_pp).replace("-", "−"), (r.delta_pp, y), xytext=(0, 8),
                        textcoords="offset points", ha="center", fontsize=7.5, color=TINTA2)
        ax.axvline(0, color=TINTA2, lw=0.9, zorder=1)
        ax.axvline(UMBRAL, color=TENUE, lw=0.9, ls=(0, (4, 3)), zorder=1)
        ax.set_title(titulo, fontsize=9.5, loc="left")
        ax.grid(axis="x", color=REJILLA, lw=0.6); ax.set_axisbelow(True)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.tick_params(axis="y", length=0)
        if clave_p == "sintetico":
            ax.set_xlim(-8, 68)
        else:
            ax.set_xlim(-24, 12)
    axes[0].set_yticks(ys); axes[0].set_yticklabels(etiquetas, fontsize=8.5, color=TINTA)
    axes[0].set_ylim(-0.6, len(BLOQUES) - 0.4)
    axes[1].text(UMBRAL, len(BLOQUES) - 0.45, " umbral +2 pp", color=TENUE, fontsize=7, va="top")
    fig.supxlabel("Δ AP@0.5 del aumento de oclusión (V3 − V1), puntos porcentuales · trazo grueso: IC 95 % por imágenes (pre-registrado, 1 000 réplicas); "
                  "trazo fino: IC 95 % jerárquico, semillas + imágenes (2 000 réplicas)", fontsize=8, color=TINTA2, y=-0.03)
    fig.suptitle("El aumento sintético de oclusión mejora sobre oclusión sintética y casi nunca sobre oclusión real (%s bloques)" % NUM.get(len(BLOQUES), len(BLOQUES)),
                 x=0.01, ha="left", fontsize=11, fontweight="bold", color=TINTA, y=1.02)
    fig.tight_layout(w_pad=1.2)
    _guardar(fig, "fig1_bloques_sintetico_vs_real")


# ----------------------------------------------------------------------------- figura 2
def fig_escalera():
    pel = [2000, 5000, 10000, 20000]
    coco = pd.read_csv(os.path.join(RAIZ, "resultados", "resumen_ap.csv"))
    coco = coco[(coco.corrida == "preliminar_coco_person") & (coco.luz == "todas") & (coco.conjunto == "nightowls")]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.9), sharex=True)
    for ax, (est, titulo) in zip(axes, [("ocluida", "Peatones ocluidos (n = 530)"), ("sin", "Peatones sin oclusión (n = 2 763)")]):
        for var, color in (("V1", AZUL), ("V3", NARANJA)):
            m, sd = zip(*[media("resultados_h7_%d/analisis" % k, "nightowls", est, var) for k in pel])
            ax.plot(pel, m, "-", color=color, lw=2, zorder=3)
            ax.plot(pel[:-1], m[:-1], "o", color=color, ms=8, mec=SUPERFICIE, mew=2, zorder=4)
            ax.errorbar(pel[-1], m[-1], yerr=sd[-1], fmt="o", color=color, ms=8, mec=SUPERFICIE, mew=2, capsize=3, lw=1.5, zorder=4)
            ax.annotate("%s  %.3f" % ("V1 base" if var == "V1" else "V3 aumento", m[-1]), (pel[-1], m[-1]), xytext=(8, 0 if var == "V1" else -2),
                        textcoords="offset points", va="center", fontsize=8, color=TINTA)
        cval = float(coco[coco.estrato == est].AP50.iloc[0])
        ax.axhline(cval, color=TENUE, lw=1.2, ls=(0, (4, 3)), zorder=2)
        ax.annotate("COCO sin ajustar %.3f" % cval, (5600 if est == "ocluida" else pel[0], cval), xytext=(0, -11 if est == "ocluida" else 5), textcoords="offset points",
                    fontsize=7.5, color=TINTA2)
        ax.set_xscale("log"); ax.set_xticks(pel); ax.set_xticklabels(["2 000", "5 000", "10 000", "20 000\n(3 semillas)"])
        ax.minorticks_off(); ax.set_xlim(1700, 38000)
        ax.set_title(titulo, loc="left"); ax.set_ylabel("AP@0.5 en NightOwls val")
        ax.grid(axis="y", color=REJILLA, lw=0.6); ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.supxlabel("Imágenes de NightOwls train (escalera anidada, presupuesto fijo de 200 000 presentaciones). "
                  "Solo el peldaño de 20 000 tiene 3 semillas (barras: ± d.e.); los demás, una.", fontsize=8, color=TINTA2, y=-0.04)
    from matplotlib.lines import Line2D
    fig.legend([Line2D([], [], color=AZUL, lw=2, marker="o"), Line2D([], [], color=NARANJA, lw=2, marker="o"),
                Line2D([], [], color=TENUE, lw=1.2, ls=(0, (4, 3)))], ["V1 base", "V3 aumento de oclusión", "COCO sin ajustar"],
               loc="upper right", ncol=3, fontsize=8, bbox_to_anchor=(1.0, 1.06))
    fig.suptitle("H7: más datos del dominio mejoran a los visibles y apenas a los ocluidos; el efecto del aumento oscila sin tendencia",
                 x=0.01, ha="left", fontsize=11, fontweight="bold", color=TINTA, y=1.08)
    fig.tight_layout()
    _guardar(fig, "fig2_h7_escalera")


# ----------------------------------------------------------------------------- figura 3
def fig_mecanismo():
    fuentes = [("Exp. 1 · parches\nentrenado en ExDark", "resultados/analisis"),
               ("Iter. 2 · siluetas\nentrenado en ExDark", "resultados_v2/analisis_yolo11s"),
               ("H6 · siluetas\nentrenado en CityPersons", "resultados_h6/analisis"),
               ("H7 · siluetas\nentrenado en NightOwls 20k", "resultados_h7_20000/analisis"),
               ("H8 · RT-DETR-l, siluetas\nentrenado en ExDark", "resultados_h8/analisis"),
               ("H9 · generativa\nentrenado en ExDark", "resultados_h9/analisis")]
    fuentes = [f for f in fuentes if os.path.exists(os.path.join(RAIZ, f[1], "diagnostico_transferencia.csv"))]
    datos = []
    for nom, d in fuentes:
        dg = pd.read_csv(os.path.join(RAIZ, d, "diagnostico_transferencia.csv"))
        a = dg[(dg.conjunto == "nightowls") & (dg.estrato == "ocluida") & (dg.variante == "V1")].iloc[0]
        b = dg[(dg.conjunto == "nightowls") & (dg.estrato == "ocluida") & (dg.variante == "V3")].iloc[0]
        datos.append((nom, a, b))
    fig, axes = plt.subplots(1, 2, figsize=(10, 0.8 * len(datos) + 0.7), sharey=True)
    ys = np.arange(len(datos))[::-1]
    for ax, (col, titulo, fmt) in zip(axes, [("recall", "Recall de peatones ocluidos", "%.2f"),
                                              ("fp_por_imagen", "Falsos positivos por imagen", "%.2f")]):
        for y, (nom, a, b) in zip(ys, datos):
            ax.annotate("", xy=(b[col], y), xytext=(a[col], y),
                        arrowprops=dict(arrowstyle="-|>", color=TENUE, lw=1.4, shrinkA=7, shrinkB=7), zorder=2)
            ax.plot(a[col], y, "o", color=AZUL, ms=9, mec=SUPERFICIE, mew=2, zorder=3)
            ax.plot(b[col], y, "o", color=NARANJA, ms=9, mec=SUPERFICIE, mew=2, zorder=3)
            for v, dy in ((a[col], 9), (b[col], -14)):
                ax.annotate(fmt % v, (v, y), xytext=(0, dy), textcoords="offset points", ha="center", fontsize=7.5, color=TINTA2)
        ax.set_title(titulo, loc="left", fontsize=9.5)
        ax.grid(axis="x", color=REJILLA, lw=0.6); ax.set_axisbelow(True)
        for sp in ("top", "right", "left"):
            ax.spines[sp].set_visible(False)
        ax.tick_params(axis="y", length=0)
    axes[0].set_yticks(ys); axes[0].set_yticklabels([d[0] for d in datos], fontsize=8.5, color=TINTA)
    axes[0].set_ylim(-0.6, len(datos) - 0.4)
    from matplotlib.lines import Line2D
    fig.legend([Line2D([], [], color=AZUL, marker="o", ls="", ms=8), Line2D([], [], color=NARANJA, marker="o", ls="", ms=8)],
               ["V1 base", "V3 aumento de oclusión"], loc="upper right", ncol=2, fontsize=8, bbox_to_anchor=(1.0, 1.07))
    fig.supxlabel("NightOwls val, 530 peatones ocluidos; detecciones con confianza ≥ 0,25; media de 3 semillas por variante", fontsize=8, color=TINTA2, y=-0.03)
    fig.suptitle("Mecanismo: con el aumento, el recall de ocluidos reales baja en los %s bloques" % NUM.get(len(datos), len(datos)),
                 x=0.01, ha="left", fontsize=11, fontweight="bold", color=TINTA, y=1.08)
    fig.tight_layout()
    _guardar(fig, "fig3_mecanismo")


# ----------------------------------------------------------------------------- figura 4
def fig_costo():
    co = pd.read_csv(os.path.join(RAIZ, "resultados", "resumen_costo.csv"))
    g = co[co.variante.isin(["V1", "V2", "V3", "V4"])].groupby("variante").ort_fps_forward.agg(["mean", "std"]).reindex(["V1", "V2", "V3", "V4"])
    nombres = {"V1": "V1 base", "V2": "V2 + CBAM", "V3": "V3 + aumento", "V4": "V4 ARGOS-11 (CBAM + aumento)"}
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ys = np.arange(4)[::-1]
    ax.barh(ys, g["mean"], height=0.55, color=AZUL, zorder=3)
    ax.errorbar(g["mean"], ys, xerr=g["std"], fmt="none", ecolor=TINTA2, lw=1, capsize=3, zorder=4)
    for y, (v, r) in zip(ys, g.iterrows()):
        ax.text(r["mean"] + r["std"] + 3, y, "%.0f FPS" % r["mean"], va="center", fontsize=8, color=TINTA)
    ax.axvline(30, color=TENUE, lw=1, ls=(0, (4, 3)))
    ax.text(31, 3.45, "criterio (c): 30 FPS", fontsize=7.5, color=TINTA2)
    lim = 0.9 * g.loc["V1", "mean"]
    ax.axvline(lim, color=TINTA2, lw=1, ls=(0, (1, 2)))
    ax.text(lim + 1, -0.62, "90 %% de V1 (H1): %.0f" % lim, fontsize=7.5, color=TINTA2)
    ax.set_yticks(ys); ax.set_yticklabels([nombres[v] for v in g.index], fontsize=8.5, color=TINTA)
    ax.set_xlim(0, 215); ax.set_ylim(-0.8, 3.7)
    ax.set_xlabel("FPS · ONNX Runtime FP16, batch 1, 640 px, RTX 5050 Laptop (media de 3 semillas ± d.e.)")
    ax.grid(axis="x", color=REJILLA, lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_title("Costo: todas cumplen 30 FPS; el CBAM quita un 15–18 % de velocidad", loc="left")
    fig.tight_layout()
    _guardar(fig, "fig4_costo")


def selftest():
    fallos = []
    def comp(d, ok):
        print("  [%s] %s" % ("ok" if ok else "FALLA", d)); ok or fallos.append(d)
    comp("al menos cinco bloques con analisis", len(BLOQUES) >= 5)
    comp("tres fuentes reales", len(REALES) == 3)
    comp("contraste inexistente devuelve None", contraste("no_existe", "a", "b") is None)
    print("\n%s" % ("AUTOTEST SUPERADO" if not fallos else "FALLOS: %s" % fallos)); sys.exit(1 if fallos else 0)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - analisis final consolidado")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    _estilo()
    df = tabla_consolidada()
    os.makedirs(SALIDA, exist_ok=True)
    df.to_csv(os.path.join(SALIDA, "tabla_consolidada.csv"), index=False)
    open(os.path.join(SALIDA, "tabla_consolidada.md"), "w", encoding="utf-8").write(tabla_md(df) + "\n")
    fig_bloques(df); fig_escalera(); fig_mecanismo(); fig_costo()
    reales = df[df.tipo == "real"]
    print("filas: %d | reales: %d | reales que superan +2 pp con IC>0: %d | sinteticos que lo superan: %d/%d" % (
        len(df), len(reales), int(reales.supera_umbral_2pp.sum()),
        int(df[df.tipo != "real"].supera_umbral_2pp.sum()), int((df.tipo != "real").sum())))
    print("-> %s" % SALIDA)


if __name__ == "__main__":
    main()
