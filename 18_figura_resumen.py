"""ARGOS-11 - Figura resumen: efecto del aumento de oclusion (V3-V1) en
oclusion sintetica frente a oclusion real, con IC 95 % bootstrap.

Lee los bootstrap.csv ya calculados (no recalcula nada):
  - experimento 1 (parches v1, YOLOv11s):  resultados/analisis/bootstrap.csv
  - iteracion 2   (siluetas v2, YOLOv11s):  resultados_v2/analisis_yolo11s/bootstrap.csv

Uso:
    python 18_figura_resumen.py                 # -> informes/figuras/
    python 18_figura_resumen.py --contraste V4-V1
    python 18_figura_resumen.py --selftest
"""
import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAIZ = os.path.dirname(os.path.abspath(__file__))

# (conjunto, estrato, etiqueta, grupo)  -- estrato severo por familia sintetica,
# estrato ocluido oficial/propio por fuente real. Solo filas con n_gt >= 50.
FILAS = [
    ("textura_severa", "severa", "Sintético: textura severa", "sintetico"),
    ("recorte_severa", "severa", "Sintético: recorte severa", "sintetico"),
    ("opaco_severa", "severa", "Sintético: opaco severa", "sintetico"),
    ("silueta_severa", "severa", "Sintético: silueta severa", "sintetico"),
    ("test_proxy", "moderada", "Real: ExDark inter-persona, moderada", "real"),
    ("test_proxy", "severa", "Real: ExDark inter-persona, severa", "real"),
    ("nightowls", "ocluida", "Real: NightOwls ocluida", "real"),
    ("citypersons_convencion", "heavy", "Real: CityPersons heavy", "real"),
]

FUENTES = {
    "Exp. 1 — parches (v1.1b)": os.path.join("resultados", "analisis", "bootstrap.csv"),
    "Iteración 2 — siluetas (v2.0)": os.path.join("resultados_v2", "analisis_yolo11s", "bootstrap.csv"),
}


def cargar(raiz, contraste):
    out = {}
    for nombre, rel in FUENTES.items():
        ruta = os.path.join(raiz, rel)
        if not os.path.exists(ruta):
            print("  aviso: falta", rel)
            continue
        df = pd.read_csv(ruta)
        df = df[df.contraste == contraste]
        out[nombre] = {(r.conjunto, r.estrato): r for r in df.itertuples()}
    return out


def dibujar(datos, contraste, salida):
    filas = [f for f in FILAS]
    n = len(filas)
    fig, ax = plt.subplots(figsize=(9.5, 0.55 * n + 1.8))
    colores = {"Exp. 1 — parches (v1.1b)": "#1f77b4",
               "Iteración 2 — siluetas (v2.0)": "#d62728"}
    desplaz = {k: d for k, d in zip(datos, (-0.17, 0.17))}
    y_lab = []
    for i, (conj, est, etiqueta, grupo) in enumerate(filas):
        y = n - 1 - i
        y_lab.append((y, etiqueta))
        for nombre, tabla in datos.items():
            r = tabla.get((conj, est))
            if r is None or r.n_gt < 50:
                continue
            yy = y + desplaz[nombre]
            ax.errorbar(r.delta_AP50_pp, yy,
                        xerr=[[r.delta_AP50_pp - r.IC95_lo_pp], [r.IC95_hi_pp - r.delta_AP50_pp]],
                        fmt="o", color=colores[nombre], capsize=3, lw=1.4, ms=5,
                        label=nombre if i == 0 else None)
            ax.annotate(f"{r.delta_AP50_pp:+.1f}", (r.delta_AP50_pp, yy),
                        textcoords="offset points", xytext=(0, 5), ha="center",
                        fontsize=7.5, color=colores[nombre])
    # separador sintetico / real
    k = sum(1 for f in filas if f[3] == "sintetico")
    ax.axhline(n - k - 0.5, color="gray", lw=0.8, ls=":")
    ax.axvline(0, color="black", lw=0.8)
    ax.axvline(2, color="green", lw=0.8, ls="--", label="umbral de relevancia +2 pp")
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_yticks([y for y, _ in y_lab])
    ax.set_yticklabels([e for _, e in y_lab], fontsize=9)
    ax.set_xlabel(f"Δ AP@0.5 ({contraste}), puntos porcentuales — IC 95 % bootstrap por imágenes (1 000 réplicas)")
    ax.set_title("Aumento sintético de oclusión: mejora sintética frente a oclusión real\n"
                 "YOLOv11s, media de 3 semillas por variante, ExDark-People train", fontsize=10.5)
    ax.legend(loc="lower right", fontsize=8.5, frameon=True)
    ax.grid(axis="x", lw=0.4, alpha=0.5)
    fig.tight_layout()
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    fig.savefig(salida, dpi=200)
    fig.savefig(os.path.splitext(salida)[0] + ".pdf")
    plt.close(fig)


def tabla_csv(datos, contraste, salida):
    filas = []
    for conj, est, etiqueta, grupo in FILAS:
        for nombre, tabla in datos.items():
            r = tabla.get((conj, est))
            if r is None:
                continue
            filas.append({"bloque": nombre, "tipo": grupo, "conjunto": conj, "estrato": est,
                          "etiqueta": etiqueta, "contraste": contraste, "n_gt": r.n_gt,
                          "delta_pp": round(r.delta_AP50_pp, 2), "IC95_lo": round(r.IC95_lo_pp, 2),
                          "IC95_hi": round(r.IC95_hi_pp, 2), "excluye_cero": r.excluye_cero})
    pd.DataFrame(filas).to_csv(salida, index=False)


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        for rel in FUENTES.values():
            ruta = os.path.join(d, rel)
            os.makedirs(os.path.dirname(ruta), exist_ok=True)
            pd.DataFrame([{"conjunto": c, "estrato": e, "contraste": "V3-V1", "n_gt": 500,
                           "delta_AP50_pp": 1.0, "IC95_lo_pp": 0.0, "IC95_hi_pp": 2.0,
                           "excluye_cero": False, "replicas": 10}
                          for c, e, _, _ in FILAS]).to_csv(ruta, index=False)
        datos = cargar(d, "V3-V1")
        sal = os.path.join(d, "f", "resumen.png")
        dibujar(datos, "V3-V1", sal)
        tabla_csv(datos, "V3-V1", os.path.join(d, "f", "resumen.csv"))
        assert os.path.exists(sal) and os.path.exists(os.path.join(d, "f", "resumen.pdf"))
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - figura resumen sintetico vs real")
    ap.add_argument("--contraste", default="V3-V1")
    ap.add_argument("--salida", default=os.path.join(RAIZ, "informes", "figuras"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    datos = cargar(RAIZ, a.contraste)
    if not datos:
        sys.exit("sin datos")
    tag = a.contraste.replace("(", "").replace(")", "").replace("-", "m")
    png = os.path.join(a.salida, f"delta_sintetico_vs_real_{tag}.png")
    dibujar(datos, a.contraste, png)
    tabla_csv(datos, a.contraste, os.path.join(a.salida, f"delta_sintetico_vs_real_{tag}.csv"))
    print("escrito", png)
    for nombre, tabla in datos.items():
        print(" ", nombre)
        for conj, est, etiqueta, _ in FILAS:
            r = tabla.get((conj, est))
            if r is not None:
                print(f"    {etiqueta:40s} {r.delta_AP50_pp:+7.2f} [{r.IC95_lo_pp:+.2f}; {r.IC95_hi_pp:+.2f}] n={r.n_gt}")


if __name__ == "__main__":
    main()
