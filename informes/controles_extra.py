#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Controles sinteticos adicionales (analisis posteriores pedidos por el panel de revision del 22/10/2026;
O4-VL y S10 de shortpaper5/revision_panel_22oct/DECISION_EDITORIAL.md). No decide ninguna hipotesis.

  cp_silueta_severa  el control de siluetas construido sobre imagenes de CityPersons val (el de H6/H11). Evaluado con
                     los modelos entrenados en ExDark separa el cambio de dominio de la oclusion: si el aumento gana
                     aqui pero no en CityPersons heavy, el deficit no es solo de dominio.
  silueta_moderada   el control de siluetas de ExDark test con cobertura 0,35-0,70, parecida a la de CityPersons heavy
                     (visibilidad 0,20-0,65), en lugar de 0,70-1,00.

Usa los mismos pesos que cada bloque evaluo (campo 'pesos' de resultados_*/eval/*.json), infiere cada modelo una sola
vez y escribe en resultados_controles_extra/ (no toca las carpetas originales). Reanudable: salta lo ya evaluado.
Uso: python informes/controles_extra.py inferir     (GPU, ~1-2 h)
     python informes/controles_extra.py analizar    (CPU; escribe informes/analisis_final/controles_extra.csv)
"""
import argparse
import glob
import importlib.util
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
SAL = os.path.join(RAIZ, "resultados_controles_extra")
PY = sys.executable
GT = {"cp_silueta_severa": os.path.join("dataset", "test_sintetico", "cp_silueta_severa", "gt_cp_silueta_severa.json"),
      "silueta_moderada": os.path.join("dataset", "test_sintetico", "silueta_moderada", "gt_silueta_moderada.json")}
ESTRATO = {"cp_silueta_severa": "severa", "silueta_moderada": "moderada"}
# bloques entrenados en ExDark (H6 y H11 se entrenaron en CityPersons y H7 en NightOwls)
BLOQUES = [("exp1", "H3", "resultados", dict(excluir_prefijo="yolo26s_")),
           ("iter2", "H4", "resultados_v2", dict(excluir_prefijo="yolo26s_")),
           ("yolo26s", "H4-Y26", "resultados_v2", dict(solo_prefijo="yolo26s_")),
           ("h8", "H8", "resultados_h8", {}), ("h9", "H9", "resultados_h9", {}), ("h9b", "H9b", "resultados_h9b", {}),
           ("h10g", "H10", "resultados_h10", dict(excluir_prefijo="V3S")),
           ("h10s", "H10-s", "resultados_h10", dict(excluir_prefijo="V3G")),
           ("h12a", "H12a", "resultados_h12m", dict(excluir_prefijo="yolo11m_V3gen")),
           ("h12b", "H12b", "resultados_h12m", dict(excluir_prefijo="yolo11m_V3sil")),
           ("h14", "H14", "resultados_h14", {}), ("h15", "H15", "resultados_h15", {}),
           ("h16a", "H16a", "resultados_h16", dict(excluir_prefijo=("V3prof", "V1rep"))),
           ("h16b", "H16b", "resultados_h16", dict(excluir_prefijo=("V3gen", "V1rep"))),
           ("h17", "H17", "resultados_h17", {})]


def manifiesto():
    """Una fila por (bloque, corrida V1/V3) con sus pesos y el nombre unico del modelo en resultados_controles_extra."""
    filas = []
    for clave, etq, carpeta, filtro in BLOQUES:
        for f in sorted(glob.glob(os.path.join(RAIZ, carpeta, "eval", "*.json"))):
            e = json.load(open(f, encoding="utf-8"))
            c, v = e.get("corrida", ""), {"V3G": "V3", "V3S": "V3"}.get(e.get("variante"), e.get("variante"))
            if v not in ("V1", "V3"):
                continue
            ex, so = filtro.get("excluir_prefijo"), filtro.get("solo_prefijo")
            if (ex and c.startswith(ex)) or (so and not c.startswith(so)):
                continue
            pesos = os.path.normpath(e["pesos"]).replace("\\", "/")
            partes = pesos.split("/")
            nombre = "%s__%s" % (partes[-4], partes[-3]) if partes[-2] == "weights" else os.path.basename(pesos)
            filas.append({"bloque": clave, "etiqueta": etq, "corrida": c, "variante": v, "semilla": e.get("semilla"),
                          "pesos": pesos, "nombre": nombre})
    return pd.DataFrame(filas)


def inferir():
    m = manifiesto()
    os.makedirs(SAL, exist_ok=True)
    m.to_csv(os.path.join(SAL, "manifiesto.csv"), index=False)
    unicos = m.drop_duplicates("nombre")
    print("modelos unicos: %d (filas %d)" % (len(unicos), len(m)), flush=True)
    gts = list(GT.values())
    for i, r in enumerate(unicos.itertuples(), 1):
        if os.path.exists(os.path.join(SAL, "eval", "%s.json" % r.nombre)):
            continue
        if not os.path.exists(os.path.join(RAIZ, r.pesos)):
            print("FALTAN_PESOS %s" % r.pesos, flush=True)
            continue
        if r.pesos.endswith(".pth"):
            det = "retina" if "argos_retina" in r.pesos else "frcnn"
            subprocess.run([PY, "35_dos_etapas.py", "inferir", "--detector", det, "--pesos", r.pesos, "--nombre", r.nombre,
                            "--resultados", SAL, "--gt"] + gts, cwd=RAIZ, check=True)
        subprocess.run([PY, "09_evaluar_estratificado.py", "--pesos", r.pesos, "--nombre", r.nombre, "--variante", r.variante,
                        "--semilla", str(r.semilla), "--resultados", SAL, "--gt"] + gts, cwd=RAIZ, check=True)
        print("[%d/%d] %s" % (i, len(unicos), r.nombre), flush=True)
    print("INFERENCIA_TERMINADA", flush=True)


def analizar(B=1000):
    sp = importlib.util.spec_from_file_location("a11", os.path.join(RAIZ, "11_analisis_estadistico.py"))
    A11 = importlib.util.module_from_spec(sp); sp.loader.exec_module(A11)
    from argos_lib.ap import emparejar_conjunto
    from argos_lib.gt import cargar_detecciones, cargar_gt
    m = pd.read_csv(os.path.join(SAL, "manifiesto.csv"))
    cc = pd.read_csv(os.path.join(RAIZ, "informes", "analisis_final", "celdas_completas.csv"))
    out = []
    for conj, ruta in GT.items():
        gimg = cargar_gt(os.path.join(RAIZ, ruta))["imagenes"]
        est = {}
        for n in m.nombre.unique():
            emp, _ = emparejar_conjunto(gimg, cargar_detecciones(os.path.join(SAL, "det", "%s__%s.json" % (n, conj)))["detecciones"],
                                        estrato=ESTRATO[conj])
            est[n] = A11.APBootstrap(emp)
        n_img = len(gimg)
        rnd = np.random.RandomState(7)
        W = [np.bincount(rnd.randint(0, n_img, n_img), minlength=n_img).astype(float) for _ in range(B)]
        apw = {n: np.array([e.ap(w) for w in W]) for n, e in est.items()}
        for (b, etq), g in m.groupby(["bloque", "etiqueta"], sort=False):
            v1, v3 = g[g.variante == "V1"].nombre.tolist(), g[g.variante == "V3"].nombre.tolist()
            d = np.mean([est[n].ap() for n in v3]) - np.mean([est[n].ap() for n in v1])
            boot = np.mean([apw[n] for n in v3], axis=0) - np.mean([apw[n] for n in v1], axis=0)
            fila = {"bloque": b, "etiqueta": etq, "control": conj, "delta": round(100 * d, 2),
                    "ic_lo": round(100 * np.percentile(boot, 2.5), 2), "ic_hi": round(100 * np.percentile(boot, 97.5), 2),
                    "AP_V1": round(np.mean([est[n].ap() for n in v1]), 4), "n_V1": len(v1), "n_V3": len(v3)}
            for s in ("CP", "NO", "EX", "control"):
                r = cc[(cc.bloque == b) & (cc.fuente == s)]
                fila["delta_%s" % s] = float(r.delta.iloc[0]) if len(r) else np.nan
            out.append(fila)
    d = pd.DataFrame(out)
    d.to_csv(os.path.join(RAIZ, "informes", "analisis_final", "controles_extra.csv"), index=False)
    print(d.to_string())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=("inferir", "analizar", "manifiesto"))
    a = ap.parse_args()
    if a.accion == "inferir":
        inferir()
    elif a.accion == "analizar":
        analizar()
    else:
        m = manifiesto()
        print(m.groupby("etiqueta").variante.value_counts().unstack().to_string())
        print("modelos unicos:", m.nombre.nunique())


if __name__ == "__main__":
    main()
