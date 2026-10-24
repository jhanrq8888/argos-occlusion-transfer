"""Tablas y figura del material suplementario del short paper (revision del 20/10/2026). Todo se lee de los ficheros de
resultados del proyecto; nada se escribe a mano. Genera tablas_suplemento_es.tex, tablas_suplemento_en.tex,
fig_gap_ic.png y fig_gap_ic_es.png.
Uso: python suplemento_tablas.py"""
import csv
import glob
import json
import os
import re
from datetime import datetime, timedelta

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
AF = os.path.join(RAIZ, "informes", "analisis_final")


def num(x, es, d=2, signo=False):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "---"
    s = ("%+.*f" if signo else "%.*f") % (d, x)
    s = s.replace("-", "$-$") if signo or x < 0 else s
    return s.replace(".", "{,}") if es else s


def ic(lo, hi, es):
    if pd.isna(lo):
        return "---"
    return "[%s; %s]" % (num(lo, es, 2, True), num(hi, es, 2, True))


# ---------------------------------------------------------------------------------------------------------- hipotesis
VERSIONES = {  # hipotesis -> (archivo, version, hash del congelamiento, carpetas de runs del bloque)
    "H1--H3": ("PROTOCOLO.md", "v1.0", "c5002ea5", ["argos"]),
    "H4, H5": ("PROTOCOLO\\_v2.md", "v2.0", "9915d90f", ["argos_v2"]),
    "H6": ("PREREGISTRO\\_H6\\_H7.md", "v3.0", "e971ab8b", ["argos_cp"]),
    "H7": ("PREREGISTRO\\_H6\\_H7.md", "v3.1", "b0043c89", ["argos_no_20000", "argos_no_2000", "argos_no_5000", "argos_no_10000"]),
    "H8": ("PREREGISTRO\\_H8.md", "v3.2", "51c0a2d8", ["argos_rtdetr"]),
    "H9": ("PREREGISTRO\\_H9.md", "v3.3b", "243acffb", ["argos_gen"]),
    "H9b": ("PREREGISTRO\\_H9b.md", "v3.4", "51786d9d", ["argos_gen_fijo"]),
    "H10": ("PREREGISTRO\\_H10.md", "v3.5", "1489961a", ["argos_geo", "argos_sil_fijo"]),
    "H11": ("PREREGISTRO\\_H11.md", "v3.6b", "bd2666fd", ["argos_cp_fijo"]),
    "H12": ("PREREGISTRO\\_H12.md", "v3.7b", "ef6138c1", ["argos_m_gen", "argos_m_sil", "argos_gen_fijo_s34", "argos_sil_fijo_s34"]),
    "H13": ("PREREGISTRO\\_H13.md", "v3.8", "7ce00c9c", []),
    "H14": ("PREREGISTRO\\_H14.md", "v3.9", "264ac449", ["argos_prof"]),
    "H15": ("PREREGISTRO\\_H15.md", "v3.10", "b7843b3a", ["argos_frcnn"]),
    "H16a, H16b": ("PREREGISTRO\\_H16\\_H17.md", "v3.11", "e9b85aee", ["argos_frcnn_gen", "argos_frcnn_prof"]),
    "H17": ("PREREGISTRO\\_H16\\_H17.md", "v3.11", "e9b85aee", ["argos_retina"]),
}
# Los entrenamientos de torchvision (35_dos_etapas.py) no guardan la fecha en registro_argos.json: la primera corrida se
# lee del registro del pod (UTC). Hipotesis -> (registro, patron de la linea de inicio)
INICIO_POD = {"H15": ("runpod_h15/h15.log", r"inicio H15"), "H16a, H16b": ("runpod_h16/h16.log", r"lanzada (gen|prof)_"),
              "H17": ("runpod_h16/h16.log", r"lanzada retina_")}
PRED = {  # predicción con dirección y veredicto (es, en)
    "H1--H3": ("V4 y V3 mejoran $\\geq$2 pp a V1 en oclusión (H1, H2) y la mejora se transfiere a la real (H3)",
               "V4 and V3 improve occluded AP by $\\geq$2 pp over V1 (H1, H2) and the gain transfers to real occlusion (H3)",
               "No confirmada (0 de 3 fuentes en H3)", "Not confirmed (0 of 3 sources in H3)"),
    "H4, H5": ("Con siluetas la ganancia se transfiere (H4); menor ganancia sintética y menor brecha (H5)",
               "With silhouettes the gain transfers (H4); smaller synthetic gain and gap (H5)",
               "H4 no confirmada (0 de 3); H5 parcial", "H4 not confirmed (0 of 3); H5 partial"),
    "H6": ("Sin transferencia al re-entrenar en CityPersons", "No transfer when retraining on CityPersons", "No detectada (0 de 3)", "Not detected (0 of 3)"),
    "H7": ("Sin transferencia con 20\\,000 imágenes nocturnas", "No transfer with 20,000 night images", "No detectada (sin control)", "Not detected (no control)"),
    "H8": ("Sin transferencia con RT-DETR-l", "No transfer with RT-DETR-l", "No detectada (0 de 3)", "Not detected (0 of 3)"),
    "H9": ("Sin transferencia con oclusores por difusión", "No transfer with diffusion occluders", "No detectada (1 de 3)", "Not detected (1 of 3)"),
    "H9b": ("Ídem con 30 épocas fijas", "Same with 30 fixed epochs", "No detectada (0 de 3)", "Not detected (0 of 3)"),
    "H10": ("Sin transferencia con la geometría de la oclusión real", "No transfer with real-occlusion geometry", "No detectada (1 de 3)", "Not detected (1 of 3)"),
    "H11": ("Ganancia $\\geq$2 pp en visibilidad 0,20--0,50 de CityPersons con exposición igual",
            "Gain $\\geq$2 pp at CityPersons visibility 0.20--0.50 with equal exposure", "No se confirma", "Not confirmed"),
    "H12": ("Sin transferencia con YOLOv11m (siluetas, H12a; difusión, H12b)", "No transfer with YOLOv11m (silhouettes, H12a; diffusion, H12b)",
            "No detectada (0 de 3 y 0 de 3)", "Not detected (0 of 3 and 0 of 3)"),
    "H13": ("AUC(parches) $>$ AUC(siluetas) $>$ AUC(difusión) con DINOv2", "AUC(patches) $>$ AUC(silhouettes) $>$ AUC(diffusion) with DINOv2",
            "Se confirma en parte", "Partially confirmed"),
    "H14": ("Sin transferencia con orden de profundidad", "No transfer with depth order", "No detectada (1 de 3)", "Not detected (1 of 3)"),
    "H15": ("Sin transferencia con Faster R-CNN", "No transfer with Faster R-CNN", None, None),
    "H16a, H16b": ("Con Faster R-CNN se transfiere también con difusión (H16a) y con orden de profundidad (H16b)",
                   "With Faster R-CNN transfer also occurs with diffusion (H16a) and depth order (H16b)",
                   "Refutadas (0 de 3 y 0 de 3)", "Refuted (0 of 3 and 0 of 3)"),
    "H17": ("Sin transferencia con RetinaNet (una etapa, misma red base que H15, con su receta de referencia)",
            "No transfer with RetinaNet (one-stage, same backbone as H15, its own reference recipe)", "No detectada (0 de 3)", "Not detected (0 of 3)"),
}


def fechas_congelamiento():
    out = {}
    for l in open(os.path.join(RAIZ, "CAMBIOS_PROTOCOLO.md"), encoding="utf-8"):
        m = re.match(r"- (\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}\s+hash_global=([0-9a-f]{8})", l)
        if m:
            out[m.group(2)] = m.group(1)
    return out


def primera_corrida(carpetas):
    ini = []
    for c in carpetas:
        for r in glob.glob(os.path.join(RAIZ, "runs", c, "*", "registro_argos.json")):
            j = json.load(open(r, encoding="utf-8"))
            if j.get("smoke"):
                continue
            try:
                f = datetime.fromisoformat(str(j["fecha"])[:19])
                ini.append(f - timedelta(seconds=float(j.get("segundos_totales") or 0)))
            except (KeyError, ValueError):
                pass
    return min(ini).strftime("%Y-%m-%d %H:%M") if ini else None


def inicio_pod(h):
    if h not in INICIO_POD:
        return None
    ruta = os.path.join(os.path.dirname(RAIZ), INICIO_POD[h][0])
    if not os.path.exists(ruta):
        return None
    for l in open(ruta, encoding="utf-8"):
        if re.search(INICIO_POD[h][1], l):
            return l[:16]
    return None


def tabla_hipotesis(es, veredicto_h15):
    fc = fechas_congelamiento()
    L = ["\\begin{table}[H]\\centering\\scriptsize",
         "\\caption{%s}\\label{tab:s-hip}" % ("Hipótesis, predicción, congelamiento y veredicto. La huella es la del protocolo congelado (SHA-256 global, primeros 8 caracteres); la fecha es la registrada por el propio proyecto, no por un tercero. Primera corrida: inicio de la primera corrida válida del bloque, según su registro (hora local, UTC$-$5, en la laptop; UTC en RunPod: H11, H12 y H14--H17)." if es else
                                          "Hypotheses, prediction, freeze and verdict. The fingerprint is that of the frozen protocol (global SHA-256, first 8 characters); the date is self-recorded by the project, not by a third party. First run: start of the first valid run of the block, from its log (local time, UTC$-$5, on the laptop; UTC on RunPod: H11, H12 and H14--H17)."),
         "\\resizebox{\\textwidth}{!}{\\begin{tabular}{@{}l p{6.3cm} l l l l p{3.2cm}@{}}\\toprule",
         ("Hip. & Predicción & Archivo & Versión y huella & Congelado & Primera corrida & Veredicto \\\\" if es else
          "Hyp. & Prediction & File & Version and fingerprint & Frozen & First run & Verdict \\\\"), "\\midrule"]
    for h, (arch, ver, hsh, carp) in VERSIONES.items():
        p = PRED[h]
        v = (p[2] if es else p[3]) or veredicto_h15 or ("pendiente" if es else "pending")
        pc = primera_corrida(carp) or inicio_pod(h) or ("sin entrenamiento" if es and h == "H13" else "no training" if h == "H13" else "---")
        L.append("%s & %s & \\texttt{%s} & %s \\texttt{%s} & %s & %s & %s \\\\" % (h, p[0] if es else p[1], arch, ver, hsh, fc.get(hsh, "---"), pc, v))
    L += ["\\bottomrule\\end{tabular}}\\end{table}"]
    return "\n".join(L)


# ------------------------------------------------------------------------------------------------- registro de corridas
def tabla_registro(es):
    d = pd.read_csv(os.path.join(AF, "registro_corridas.csv"))
    L = ["\\begin{table}[H]\\centering\\scriptsize",
         "\\caption{%s}\\label{tab:s-registro}" % ("Registro de corridas por bloque (el detalle por corrida está en \\texttt{informes/analisis\\_final/registro\\_corridas.csv}). Épocas: entrenadas y de los pesos evaluados, mín.--máx. Con selección por validación, la época evaluada es la de máxima mAP50-95 en validación (ExDark val y val ocluida)." if es else
                                               "Run log by block (per-run detail in \\texttt{informes/analisis\\_final/registro\\_corridas.csv}). Epochs: trained and of the evaluated weights, min--max. With validation selection, the evaluated epoch is the one with maximum validation mAP50-95 (ExDark val and occluded val)."),
         "\\resizebox{\\textwidth}{!}{\\begin{tabular}{@{}l l r l l l l r@{}}\\toprule",
         ("Bloque & Detector & Corridas & Ép. V1 (eval./entr.) & Ép. V3 (eval./entr.) & Regla de exposición & Máquina & Horas \\\\" if es else
          "Block & Detector & Runs & V1 ep. (eval./train.) & V3 ep. (eval./train.) & Exposure rule & Machine & Hours \\\\"), "\\midrule"]
    rango = lambda s: ("%d" % s.min()) if s.min() == s.max() else "%d--%d" % (s.min(), s.max())
    tr = {"parada temprana (paciencia 20, max. 100)": ("selección por validación", "validation selection"),
          "presupuesto fijo de presentaciones, paciencia 1/5": ("presentaciones fijas, paciencia 1/5", "fixed presentations, patience 1/5"),
          "30 epocas fijas": ("30 épocas fijas", "30 fixed epochs"), "60 epocas fijas": ("60 épocas fijas", "60 fixed epochs")}
    for b, g in d.groupby("bloque", sort=False):
        celdas = []
        for v in ("V1", "V3"):
            s = g[g.variante == v]
            celdas.append("%s / %s" % (rango(s.epoca_evaluada), rango(s.epocas_entrenadas)) if len(s) else "---")
        nom = b.replace("Iteracion", "Iteración").replace("peldano", "peldaño").replace("geometria", "geometría").replace("Replica", "Réplica").replace("Extension", "Extensión")
        L.append("%s & %s & %d & %s & %s & %s & %s & %s \\\\" % (nom.replace("_", "\\_"), ", ".join(sorted(g.detector.unique())), len(g), celdas[0], celdas[1],
                                                               tr[g.regla_de_exposicion.iloc[0]][0 if es else 1], "RTX 4090" if "4090" in g.maquina.iloc[0] else "RTX 5050 Laptop",
                                                               num(g.horas_gpu.sum(), es, 1)))
    L.append("\\midrule %s & & %d & & & & & %s \\\\" % ("Total", len(d), num(d.horas_gpu.sum(), es, 1)))
    L += ["\\bottomrule\\end{tabular}}\\end{table}"]
    return "\n".join(L)


# ------------------------------------------------------------------------------------------------------- celdas
ETQ = {"control": "Control", "NO": "NO", "CP": "CP", "EX": "EX"}


def tabla_celdas(es):
    d = pd.read_csv(os.path.join(AF, "celdas_completas.csv"))
    expo = {"desigual (seleccion por validacion)": ("desigual", "unequal"), "igual (epocas fijas)": ("igual", "equal"),
            "seleccion temprana en ambas": ("temprana", "early")}
    L = ["\\begin{table}[H]\\centering\\scriptsize",
         "\\caption{%s}\\label{tab:s-celdas}" % ("Todas las celdas: V3$-$V1 en AP@0.5 (pp), IC 95\\,\\% por imágenes (1\\,000 réplicas) y jerárquico (semillas e imágenes, 2\\,000), 3 semillas por variante. * pasa: estimación $\\geq+2$ e IC por imágenes $>0$. $\\dagger$ descarta una ganancia de $+2$ pp (límite superior del IC por imágenes $<+2$). Exposición: igual (épocas fijas), desigual (V1 y V3 seleccionados en épocas distintas por validación) o temprana (ambas en las épocas 1--2)." if es else
                                            "All cells: V3$-$V1 in AP@0.5 (pp), 95\\,\\% CI over images (1,000 replicates) and hierarchical (seeds and images, 2,000), 3 seeds per variant. * passes: estimate $\\geq+2$ and image CI $>0$. $\\dagger$ rules out a $+2$ pp gain (upper image-CI limit $<+2$). Exposure: equal (fixed epochs), unequal (V1 and V3 selected at different epochs by validation) or early (both at epochs 1--2)."),
         "\\resizebox{\\textwidth}{!}{\\begin{tabular}{@{}l l l r l l | l r l l@{}}\\toprule",
         ("Bloque & Exp. & Celda & $\\Delta$ & IC imágenes & IC jerárquico & Celda & $\\Delta$ & IC imágenes & IC jerárquico \\\\" if es else
          "Block & Exp. & Cell & $\\Delta$ & Image CI & Hierarchical CI & Cell & $\\Delta$ & Image CI & Hierarchical CI \\\\"), "\\midrule"]
    for b, g in d.groupby("bloque", sort=False):
        filas = []
        for _, r in g.iterrows():
            marca = ("*" if r.pasa else "") + ("$^\\dagger$" if r.descarta_2pp else "")
            filas.append("%s & %s%s & %s & %s" % (ETQ.get(r.fuente, r.fuente), num(r.delta, es, 2, True), marca, ic(r.ic_lo, r.ic_hi, es), ic(r.jer_lo, r.jer_hi, es)))
        while len(filas) < 4:
            filas.append("& & &")
        L.append("%s & %s & %s & %s \\\\" % (g.etiqueta.iloc[0], expo[g.exposicion.iloc[0]][0 if es else 1], filas[0], filas[1]))
        L.append(" & & %s & %s \\\\" % (filas[2], filas[3]))
    L += ["\\bottomrule\\end{tabular}}\\end{table}"]
    return "\n".join(L)


# --------------------------------------------------------------------------------------------------- matriz cruzada
def tabla_cruzada(es):
    fam = [("parches", "opaco_severa"), ("sil", "silueta_severa"), ("gen", "generativa_severa"), ("geo", "geometria_severa"), ("prof", "profundidad_severa")]
    nom = {"parches": ("Parches", "Patches"), "sil": ("Siluetas", "Silhouettes"), "gen": ("Generativa", "Generative"),
           "geo": ("Geometría real", "Real geometry"), "prof": ("Profundidad", "Depth order")}
    ruta = os.path.join(AF, "matriz_cruzada.csv")
    if not os.path.exists(ruta):
        return "%% matriz cruzada pendiente"
    m = pd.read_csv(ruta)
    L = ["\\begin{table}[H]\\centering\\scriptsize",
         "\\caption{%s}\\label{tab:s-cruzada}" % ("Matriz cruzada de controles: V3$-$V1 (AP@0.5, pp, 3 semillas) de cada familia de entrenamiento (filas) en el control severo de cada familia (columnas), IC por imágenes entre corchetes. Todos los controles usan imágenes de ExDark test e instancias de oclusor no vistas en el entrenamiento. Parches: modelos del experimento 1 (épocas 1--2); el resto, 30 épocas fijas." if es else
                                              "Cross-family control matrix: V3$-$V1 (AP@0.5, pp, 3 seeds) of each training family (rows) on each family's severe control (columns), image CI in brackets. All controls use ExDark test images and occluder instances unseen in training. Patches: experiment-1 models (epochs 1--2); the rest, 30 fixed epochs."),
         "\\setlength{\\tabcolsep}{2pt}\\begin{tabular}{@{}l ccccc@{}}\\toprule",
         ("Entrenado con & " if es else "Trained with & ") + " & ".join(nom[f][0 if es else 1] for f, _ in fam) + " \\\\ \\midrule"]
    for f, _ in fam:
        val, ics = [], []
        for _, c in fam:
            r = m[(m.fila == f) & (m.control == c)]
            if len(r):
                r = r.iloc[0]
                v = num(r.delta, es, 1, True)
                val.append("\\textbf{%s}" % v if f == _fam_de(c) else v)
                ics.append("{\\tiny %s}" % ic(r.ic_lo, r.ic_hi, es))
            else:
                val.append("---"); ics.append("")
        L.append("%s & %s \\\\" % (nom[f][0 if es else 1], " & ".join(val)))
        L.append(" & %s \\\\[2pt]" % " & ".join(ics))
    L += ["\\bottomrule\\end{tabular}\\end{table}"]
    return "\n".join(L)


def _fam_de(control):
    return {"opaco_severa": "parches", "silueta_severa": "sil", "generativa_severa": "gen", "geometria_severa": "geo", "profundidad_severa": "prof"}[control]


# ------------------------------------------------------------------------------------- semillas, escalera, visibilidad, MR
def tabla_extra(es):
    j = json.load(open(os.path.join(RAIZ, "resultados_h12", "analisis", "contrastes_h12.json"), encoding="utf-8"))
    L = ["\\begin{table}[H]\\centering\\scriptsize",
         "\\caption{%s}\\label{tab:s-extra}" % ("Análisis secundarios declarados: cinco semillas (YOLOv11s, 30 épocas), escalera de NightOwls de H7 (semilla 0, NightOwls ocluida) y tasa de fallos MR$^{-2}$ (pp; negativo = el aumento pierde menos personas)." if es else
                                            "Declared secondary analyses: five seeds (YOLOv11s, 30 epochs), the H7 NightOwls ladder (seed 0, NightOwls occluded) and miss rate MR$^{-2}$ (pp; negative = augmentation misses fewer people)."),
         "\\setlength{\\tabcolsep}{2.5pt}\\begin{tabular}{@{}l l r l@{}}\\toprule",
         ("Análisis & Celda & $\\Delta$ & IC (imágenes / jerárquico) \\\\" if es else "Analysis & Cell & $\\Delta$ & CI (images / hierarchical) \\\\"), "\\midrule"]
    for b, et in (("E7b_5s", ("H9b, 5 semillas", "H9b, 5 seeds")), ("E8sil_5s", ("H10-s, 5 semillas", "H10-s, 5 seeds"))):
        for f in [x for x in j if x["bloque"] == b and x["tipo"] == "real"]:
            L.append("%s & %s & %s & %s / %s \\\\" % (et[0 if es else 1], ETQ[{"nightowls": "NO", "citypersons_convencion": "CP", "test_proxy": "EX"}[f["conjunto"]]],
                                                    num(f["delta_pp"], es, 2, True), ic(f["IC_img_lo"], f["IC_img_hi"], es), ic(f["IC_jer_lo"], f["IC_jer_hi"], es)))
    L.append("\\midrule")
    for k in ("2000", "5000", "10000", "20000"):
        b = pd.read_csv(os.path.join(RAIZ, "resultados_h7_%s" % k, "analisis", "bootstrap.csv"))
        r = b[(b.conjunto == "nightowls") & (b.estrato == "ocluida") & (b.contraste == "V3-V1")].iloc[0]
        L.append("%s & NO & %s & %s \\\\" % (("H7, %s img." if es else "H7, %s img.") % k, num(r.delta_AP50_pp, es, 2, True), ic(r.IC95_lo_pp, r.IC95_hi_pp, es)))
    L.append("\\midrule")
    mr = pd.concat([pd.read_csv(os.path.join(AF, f)) for f in ("miss_rate.csv", "miss_rate_secundarios.csv", "miss_rate_recientes.csv")
                    if os.path.exists(os.path.join(AF, f))] + [pd.read_csv(os.path.join(RAIZ, "resultados_h11", "analisis", "descriptivos_h11_miss_rate.csv"))])
    etq = {"exp1": "H3", "iter2": "H4", "yolo26s": "H4-Y26", "h6": "H6", "h7": "H7", "h8": "H8", "h9": "H9", "h9b": "H9b", "h10_geometria": "H10",
           "h10_siluetas": "H10-s", "h11": "H11", "h12a": "H12a", "h12b": "H12b", "h14": "H14", "h15": "H15", "h16a": "H16a", "h16b": "H16b", "h17": "H17"}
    mr = mr[(mr.tipo == "real")]
    for b in etq:
        g = mr[mr.bloque == b]
        if not len(g):
            continue
        txt = "; ".join("%s %s" % ({"nightowls": "NO", "citypersons_convencion": "CP", "test_proxy": "EX"}.get(r.conjunto, r.conjunto), num(r.delta_pp, es, 1, True))
                        for _, r in g.iterrows() if r.conjunto in ("nightowls", "citypersons_convencion", "test_proxy"))
        mej = int(g.mejora_relevante.sum())
        L.append("MR$^{-2}$ %s & \\multicolumn{3}{l}{%s%s} \\\\" % (etq[b], txt, (" (%d %s)" % (mej, "mejora $\\geq$2 con IC" if es else "improve $\\geq$2 with CI")) if mej else ""))
    L += ["\\bottomrule\\end{tabular}\\end{table}"]
    return "\n".join(L)


def tabla_vis(es):
    v = pd.read_csv(os.path.join(AF, "visibilidad_citypersons.csv"))
    tramos = list(dict.fromkeys(v.tramo_vis))
    etq = {"E1": "H3", "E2": "H4", "E3": "H4-Y26", "E4": "H6", "E5": "H7", "E6": "H8", "E7": "H9", "E7b": "H9b"}
    L = ["\\begin{table}[H]\\centering\\scriptsize",
         "\\caption{%s}\\label{tab:s-vis}" % ("CityPersons por visibilidad anotada (análisis posterior declarado): V3$-$V1 en AP@0.5 (pp) por tramo; las demás personas son regiones \\emph{ignore}." if es else
                                          "CityPersons by annotated visibility (declared post hoc analysis): V3$-$V1 in AP@0.5 (pp) per bin; other people are \\emph{ignore} regions."),
         "\\setlength{\\tabcolsep}{2.5pt}\\begin{tabular}{@{}l %s@{}}\\toprule" % ("r" * len(tramos)),
         ("Bloque & " if es else "Block & ") + " & ".join(t.replace("-", "--").replace(".", "{,}" if es else ".") for t in tramos) + " \\\\ \\midrule"]
    for e, g in v.groupby("exp", sort=False):
        L.append("%s & %s \\\\" % (etq.get(e, e), " & ".join(num(g[g.tramo_vis == t].delta_pp.iloc[0], es, 1, True) if len(g[g.tramo_vis == t]) else "---" for t in tramos)))
    L += ["\\bottomrule\\end{tabular}\\end{table}"]
    return "\n".join(L)


def tabla_estadistica(es):
    r = json.load(open(os.path.join(AF, "revision_sp.json"), encoding="utf-8"))
    pe = r["por_exposicion"]
    g = lambda k: pe[k]
    eq, des, tem = g("igual (epocas fijas)"), g("desigual (seleccion por validacion)"), g("seleccion temprana en ambas")
    mm, mm2, sd, rho = r["modelo_mixto"], r["modelo_mixto_sin_H3"], r["sd_semillas_V1"], r["rho_ic_bloques"]
    n = lambda x, d=2, s=False: num(x, es, d, s)
    filas = ([("Celdas reales que pasan (estimación $\\geq+2$ e IC $>0$)", "Real cells that pass (estimate $\\geq+2$ and CI $>0$)", "%d de %d (con IC jerárquico: %d)" % (r["pasan"], r["celdas_reales"], r["pasan_jer"]) if es else "%d of %d (hierarchical CI: %d)" % (r["pasan"], r["celdas_reales"], r["pasan_jer"])),
              ("Descartan una ganancia de +2 pp (no superioridad, unilateral 2,5 \\%)", "Rule out a +2 pp gain (non-superiority, one-sided 2.5 \\%)", "%d de %d (jerárquico: %d)" % (r["descartan_2pp"], r["celdas_reales"], r["descartan_2pp_jer"]) if es else "%d of %d (hierarchical: %d)" % (r["descartan_2pp"], r["celdas_reales"], r["descartan_2pp_jer"])),
              ("Exposición igual (%d celdas): pasan / negativas con IC / media" % eq["celdas"], "Equal exposure (%d cells): pass / negative with CI / mean" % eq["celdas"], "%d / %d / %s pp" % (eq["pasan"], eq["negativas_ic"], n(eq["media_delta"], 2, True))),
              ("Exposición desigual (%d celdas): pasan / negativas con IC / media" % des["celdas"], "Unequal exposure (%d cells): pass / negative with CI / mean" % des["celdas"], "%d / %d / %s pp" % (des["pasan"], des["negativas_ic"], n(des["media_delta"], 2, True))),
              ("Selección temprana en ambas (%d celdas): pasan / negativas con IC / media" % tem["celdas"], "Early selection in both (%d cells): pass / negative with CI / mean" % tem["celdas"], "%d / %d / %s pp" % (tem["pasan"], tem["negativas_ic"], n(tem["media_delta"], 2, True))),
              ("Sin el indicador de ExDark: celdas que pasan; bloques con 2 de 2", "Without the ExDark proxy: passing cells; blocks with 2 of 2", "%d de %d; %d" % (r["sin_indicador_exdark"]["pasan"], r["sin_indicador_exdark"]["celdas"], len(r["sin_indicador_exdark"]["bloques_con_2_de_2"])) if es else "%d of %d; %d" % (r["sin_indicador_exdark"]["pasan"], r["sin_indicador_exdark"]["celdas"], len(r["sin_indicador_exdark"]["bloques_con_2_de_2"]))),
              ("DE entre semillas del AP@0.5 de V1 en fuentes reales (mediana; máx.)", "Between-seed SD of V1 AP@0.5 on real sources (median; max.)", "%s; %s pp (%d grupos)" % (n(sd["mediana_pp"]), n(sd["max_pp"]), sd["n"]) if es else "%s; %s pp (%d groups)" % (n(sd["mediana_pp"]), n(sd["max_pp"]), sd["n"]))]
             + [("$\\rho$ de Spearman, %s (IC bootstrap de bloques)" % s, "Spearman $\\rho$, %s (block-bootstrap CI)" % s, "%s %s" % (n(rho[s]["rho"], 2, True), ic(*rho[s]["IC95"], es))) for s in ("NO", "CP", "EX")]
             + [("Modelo mixto: pendiente por DE de ganancia sintética (%s pp)" % n(mm["DE_sintetico_pp"], 1), "Mixed model: slope per SD of synthetic gain (%s pp)" % n(mm["DE_sintetico_pp"], 1), "%s pp %s, $p=%s$" % (n(mm["pendiente_pp_por_DE"], 2, True), ic(*mm["IC95"], es), n(mm["p"], 2))),
                ("Ídem sin H3", "Same without H3", "%s pp %s, $p=%s$" % (n(mm2["pendiente_pp_por_DE"], 2, True), ic(*mm2["IC95"], es), n(mm2["p"], 2)))])
    L = ["\\begin{table}[H]\\centering\\scriptsize",
         "\\caption{%s}\\label{tab:s-estad}" % ("Recuentos y análisis estadísticos declarados (posteriores): 13 bloques con control, 39 celdas reales. Modelo mixto: ganancia real $\\sim$ ganancia sintética (estandarizada) + fuente, con intercepto aleatorio por bloque." if es else
                                            "Counts and declared (post hoc) statistical analyses: 13 blocks with a control, 39 real cells. Mixed model: real gain $\\sim$ synthetic gain (standardized) + source, with a random intercept per block."),
         "\\begin{tabular}{@{}p{5.0cm} p{2.9cm}@{}}\\toprule"]
    L += ["%s & %s \\\\" % (f[0] if es else f[1], f[2]) for f in filas]
    L += ["\\bottomrule\\end{tabular}\\end{table}"]
    return "\n".join(L)


# ------------------------------------------------------------- analisis posteriores pedidos por la revision del 22/10
def tabla_panel(es):
    """Lee informes/analisis_final/{revision_panel.json, especificidad.csv, cruzada_torchvision.csv}, que genera
    informes/revision_panel_analisis.py."""
    ruta = os.path.join(AF, "revision_panel.json")
    if not os.path.exists(ruta):
        return "% revision_panel.json pendiente"
    r = json.load(open(ruta, encoding="utf-8"))
    e = pd.read_csv(os.path.join(AF, "especificidad.csv"))
    n = lambda x, d=2, s=True: num(x, es, d, s)
    orden = ["H3", "H4", "H4-Y26", "H6", "H7", "H8", "H9", "H9b", "H10", "H10-s", "H11", "H12a", "H12b", "H14", "H15", "H16a", "H16b", "H17"]
    marca = lambda f: "*" if f.esp_lo > 0 else ("$^-$" if f.esp_hi < 0 else "")
    L = ["\\begin{table}[H]\\centering\\scriptsize",
         "\\caption{%s}\\label{tab:s-especificidad}" % (
             "Especificidad y convención de cajas (análisis posteriores, revisión del 22/10). Especificidad: [V3$-$V1] en las personas ocluidas menos [V3$-$V1] en las personas sin oclusión de la misma fuente (NO: ocluida $-$ sin; CP: \\emph{heavy} $-$ \\emph{bare}; EX: severa $-$ sin), con las mismas imágenes remuestreadas para ambos estratos (1\\,000 réplicas). * IC $>0$ (la ganancia es mayor en las ocluidas); $^-$ IC $<0$. CP \\emph{heavy}: V3$-$V1 puntuando con la caja completa (protocolo de CityPersons) y con la caja visible (\\texttt{bboxVis} de \\texttt{anno\\_val.mat}), IoU $\\geq$ 0,5." if es else
             "Specificity and box convention (post hoc analyses, review of 22 October). Specificity: [V3$-$V1] on occluded people minus [V3$-$V1] on unoccluded people of the same source (NO: occluded $-$ none; CP: \\emph{heavy} $-$ \\emph{bare}; EX: severe $-$ none), with the same images resampled for both strata (1,000 replicates). * CI $>0$ (the gain is larger for occluded people); $^-$ CI $<0$. CP \\emph{heavy}: V3$-$V1 scored with the full box (CityPersons protocol) and with the visible box (\\texttt{bboxVis} from \\texttt{anno\\_val.mat}), IoU $\\geq$ 0.5."),
         "\\setlength{\\tabcolsep}{3pt}\\begin{tabular}{@{}l lll rr@{}}\\toprule",
         ("Bloque & Especificidad NO & Especificidad CP & Especificidad EX & CP caja completa & CP caja visible \\\\" if es else
          "Block & Specificity NO & Specificity CP & Specificity EX & CP full box & CP visible box \\\\"), "\\midrule"]
    for b in orden:
        g = e[e.etiqueta == b].set_index("fuente")
        if not len(g):
            continue
        cel = []
        for s in ("NO", "CP", "EX"):
            f = g.loc[s] if s in g.index else None
            cel.append("---" if f is None else "%s%s %s" % (n(f.especificidad), marca(f), ic(f.esp_lo, f.esp_hi, es)))
        cpf = n(g.loc["CP"].d_heavy) if "CP" in g.index else "---"
        cpv = ("%s %s" % (n(g.loc["CPvis"].d_heavy), ic(g.loc["CPvis"].d_heavy_lo, g.loc["CPvis"].d_heavy_hi, es))) if "CPvis" in g.index else "---"
        L.append("%s & %s & %s & %s & %s & %s \\\\" % (b, cel[0], cel[1], cel[2], cpf, cpv))
    L += ["\\bottomrule\\end{tabular}\\end{table}", ""]
    # resumen estadistico
    rp, mp, eq, po, mu, sp = r["recuento_primario"], r["media_por_fuente_igual"], r["equivalencia_por_fuente"], r["potencia_regla"], r["multiplicidad"], r["spearman"]
    filas = [(("Recuento primario (exposición igual: %d bloques, %d celdas): pasan / descartan +2 / no concluyentes" if es else
               "Primary count (equal exposure: %d blocks, %d cells): pass / rule out +2 / inconclusive") % (rp["bloques"], rp["celdas"]),
              "%d (%d) / %d (%d) / %d" % (rp["pasan"], rp["pasan_jer"], rp["descartan_2pp"], rp["descartan_2pp_jer"], rp["no_concluyentes"]))]
    for s in ("NO", "CP", "EX"):
        filas.append((("Media %s con exposición igual, IC bootstrap de bloques; bloques positivos" if es else "Mean %s with equal exposure, block-bootstrap CI; positive blocks") % s,
                      "%s %s; %d de %d" % (n(mp[s]["media"]), ic(*mp[s]["IC_bloques"], es), mp[s]["positivas"], mp[s]["k"]) if es else
                      "%s %s; %d of %d" % (n(mp[s]["media"]), ic(*mp[s]["IC_bloques"], es), mp[s]["positivas"], mp[s]["k"])))
    for s in ("NO", "CP", "EX"):
        q = eq[s]
        filas.append((("Efectos aleatorios %s: media, IC 90\\,\\%% (TOST $\\pm$2 pp), $\\tau$" if es else "Random effects %s: mean, 90\\,\\%% CI (TOST $\\pm$2 pp), $\\tau$") % s,
                      "%s %s, $\\tau$=%s; %s" % (n(q["media"]), ic(*q["IC90"], es), n(q["tau"], 2, False),
                                                ("equivalente" if q["equivalente_2pp"] else "no equivalente") if es else ("equivalent" if q["equivalente_2pp"] else "not equivalent"))))
    filas.append((("Potencia de la regla «2 de 3»: P(detectar) con +2 pp verdaderos en las tres fuentes (mediana [rango]); con +3 pp" if es else
                   "Power of the ``2 of 3'' rule: P(detect) with a true +2 pp on all three sources (median [range]); with +3 pp"),
                  "%s [%s; %s]; %s" % (n(po["mediana_p_detectar_+2"], 2, False), n(po["rango_+2"][0], 2, False), n(po["rango_+2"][1], 2, False), n(po["mediana_p_detectar_+3"], 2, False))))
    filas.append((("Multiplicidad (%d celdas, independencia supuesta): pases esperados bajo el nulo, error por imágenes / jerárquico; observados" if es else
                   "Multiplicity (%d cells, independence assumed): expected passes under the null, image / hierarchical error; observed") % mu["celdas"],
                  "%s / %s; %d" % (n(mu["pases_esperados_nulo"], 2, False), n(mu["pases_esperados_nulo_jer"], 2, False), mu["pases_observados"])))
    filas.append((("P(algún bloque llega a «2 de 3» por azar), error por imágenes / jerárquico" if es else "P(some block reaches ``2 of 3'' by chance), image / hierarchical error"),
                  "%s / %s" % (n(mu["p_algun_bloque_2de3_nulo"], 3, False), n(mu["p_algun_bloque_2de3_nulo_jer"], 3, False))))
    for f in [x for x in r["ic_semillas"] if x["bloque"] == "H15" or (x["fuente"] in ("CP",) and x["bloque"].startswith("H10")) or (x["bloque"] in ("H9", "H14") and x["fuente"] == "EX")]:
        if f["bloque"] == "H15" or abs(f["delta"]) >= 2:
            filas.append((("IC con la varianza entre semillas (t de Welch, gl %s): %s %s" if es else "CI with between-seed variance (Welch's t, df %s): %s %s") % (n(f["gl"], 1, False), f["bloque"], f["fuente"]),
                          "%s %s" % (n(f["delta"]), ic(*f["IC_t"], es))))
    for f in r["h16_frente_replica"]:
        filas.append((("%s %s: con las V1 de H15 / con la réplica de V1 (otra máquina, una semilla)" if es else "%s %s: with the H15 V1 / with the V1 replicate (other machine, one seed)") % (f["bloque"], f["fuente"]),
                      "%s / %s" % (n(f["delta_V1_H15"]), n(f["delta_V1_replica"]))))
    for nombre, et in (("17_bloques", ("17 bloques", "17 blocks")), ("exposicion_igual", ("exposición igual", "equal exposure"))):
        filas.append((("$\\rho$ de Spearman control--real, %s (NO; CP; EX)" if es else "Spearman $\\rho$ control--real, %s (NO; CP; EX)") % et[0 if es else 1],
                      "; ".join("%s %s" % (n(sp[nombre][s]["rho"]), ic(*sp[nombre][s]["IC95"], es)) for s in ("NO", "CP", "EX"))))
    L += ["\\begin{table}[H]\\centering\\scriptsize",
          "\\caption{%s}\\label{tab:s-panel}" % ("Recuento primario y análisis estadísticos pedidos por la revisión (posteriores; \\texttt{informes/revision\\_panel\\_analisis.py}). Entre paréntesis, con el IC jerárquico." if es else
                                                "Primary count and statistical analyses requested by the review (post hoc; \\texttt{informes/revision\\_panel\\_analisis.py}). In brackets, with the hierarchical CI."),
          "\\begin{tabular}{@{}p{8.6cm} p{6.6cm}@{}}\\toprule"]
    L += ["%s & %s \\\\" % f for f in filas]
    L += ["\\bottomrule\\end{tabular}\\end{table}", ""]
    # matriz cruzada de torchvision
    cz = pd.read_csv(os.path.join(AF, "cruzada_torchvision.csv"))
    ctr = [("silueta_severa", ("Siluetas", "Silhouettes")), ("generativa_severa", ("Difusión", "Diffusion")), ("geometria_severa", ("Geometría", "Geometry")), ("profundidad_severa", ("Profundidad", "Depth"))]
    nomb = {"H15": "H15 Faster R-CNN, siluetas", "H16a": "H16a Faster R-CNN, difusión", "H16b": "H16b Faster R-CNN, profundidad", "H17": "H17 RetinaNet, siluetas"}
    nomb_en = {"H15": "H15 Faster R-CNN, silhouettes", "H16a": "H16a Faster R-CNN, diffusion", "H16b": "H16b Faster R-CNN, depth", "H17": "H17 RetinaNet, silhouettes"}
    L += ["\\begin{table}[H]\\centering\\scriptsize",
          "\\caption{%s}\\label{tab:s-cruzada-tv}" % ("Matriz cruzada de controles de los detectores de torchvision: V3$-$V1 (pp) de cada bloque en el control de cada familia; en negrita, su propio control." if es else
                                                     "Cross-family control matrix of the torchvision detectors: V3$-$V1 (pp) of each block on each family's control; in bold, its own control."),
          "\\begin{tabular}{@{}l rrrr@{}}\\toprule", ("Bloque & " if es else "Block & ") + " & ".join(c[1][0 if es else 1] for c in ctr) + " \\\\ \\midrule"]
    for b in ("H15", "H16a", "H16b", "H17"):
        g = cz[cz.bloque == b].set_index("control")
        cel = []
        for c, _ in ctr:
            if c in g.index:
                v = n(g.loc[c].delta, 1)
                cel.append("\\textbf{%s}" % v if bool(g.loc[c].propio) else v)
            else:
                cel.append("---")
        L.append("%s & %s \\\\" % ((nomb if es else nomb_en)[b], " & ".join(cel)))
    L += ["\\bottomrule\\end{tabular}\\end{table}", ""]
    # controles adicionales (informes/controles_extra.py)
    rce = os.path.join(AF, "controles_extra.csv")
    if os.path.exists(rce):
        ce = pd.read_csv(rce)
        L += ["\\begin{table}[H]\\centering\\scriptsize",
              "\\caption{%s}\\label{tab:s-controles-extra}" % (
                  "Controles adicionales con los mismos pesos de cada bloque (análisis posteriores; \\texttt{informes/controles\\_extra.py}). CP sintético: siluetas pegadas sobre imágenes de CityPersons val (\\texttt{cp\\_silueta\\_severa}, cobertura 0,70--1,00), evaluado con modelos entrenados en ExDark: separa el cambio de dominio de la oclusión. Moderado: siluetas sobre ExDark test con cobertura 0,35--0,70, parecida a la de CityPersons \\emph{heavy}. V3$-$V1 (pp) con IC por imágenes; * pasa. A la derecha, CityPersons \\emph{heavy} real (tabla~I del artículo)." if es else
                  "Additional controls with the same weights of each block (post hoc analyses; \\texttt{informes/controles\\_extra.py}). Synthetic CP: silhouettes pasted on CityPersons val images (\\texttt{cp\\_silueta\\_severa}, coverage 0.70--1.00), evaluated with models trained on ExDark: it separates the domain shift from occlusion. Moderate: silhouettes on ExDark test with coverage 0.35--0.70, similar to CityPersons \\emph{heavy}. V3$-$V1 (pp) with image CI; * passes. On the right, real CityPersons \\emph{heavy} (Table~I of the paper)."),
              "\\begin{tabular}{@{}l ll r@{}}\\toprule",
              ("Bloque & CP sintético & Moderado (ExDark) & CP \\emph{heavy} real \\\\" if es else "Block & Synthetic CP & Moderate (ExDark) & Real CP \\emph{heavy} \\\\"), "\\midrule"]
        for b in ["H3", "H4", "H4-Y26", "H8", "H9", "H9b", "H10", "H10-s", "H12a", "H12b", "H14", "H15", "H16a", "H16b", "H17"]:
            g = ce[ce.etiqueta == b].set_index("control")
            if not len(g):
                continue
            cel = []
            for c in ("cp_silueta_severa", "silueta_moderada"):
                r = g.loc[c]
                cel.append("%s%s %s" % (n(r.delta), "*" if (r.delta >= 2 and r.ic_lo > 0) else "", ic(r.ic_lo, r.ic_hi, es)))
            L.append("%s & %s & %s & %s \\\\" % (b, cel[0], cel[1], n(g.iloc[0].delta_CP)))
        L += ["\\bottomrule\\end{tabular}\\end{table}"]
    return "\n".join(L)


# -------------------------------------------------------------------------------------------- figura con barras de error
def figura_ic(es):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    d = pd.read_csv(os.path.join(AF, "celdas_completas.csv"))
    d = d[d.bloque != "h7"]
    orden = [e for e in ["H3", "H4", "H4-Y26", "H6", "H8", "H9", "H9b", "H10", "H10-s", "H11", "H12a", "H12b", "H14", "H15", "H16a", "H16b", "H17"] if e in set(d.etiqueta)]
    fig, ax = plt.subplots(figsize=(7.0, 2.6), dpi=300)
    col = {"NO": "#1f4e9c", "CP": "#e08a00", "EX": "#2e7d32"}
    mk = {"NO": "s", "CP": "^", "EX": "D"}
    for i, b in enumerate(orden):
        g = d[d.etiqueta == b]
        c = g[g.fuente == "control"].iloc[0]
        ax.bar(i, min(c.delta, 30), width=0.6, color="#c8c8c8")
        ax.errorbar(i, min(c.delta, 30), yerr=[[min(c.delta, 30) - min(c.ic_lo, 30)], [min(c.ic_hi, 30) - min(c.delta, 30)]], color="0.4", lw=0.6, capsize=1.5)
        for k, s in enumerate(("NO", "CP", "EX")):
            r = g[g.fuente == s].iloc[0]
            x = i - 0.2 + 0.2 * k
            ax.errorbar(x, r.delta, yerr=[[r.delta - r.ic_lo], [r.ic_hi - r.delta]], fmt=mk[s], color=col[s], ms=3, lw=0.7, capsize=1.2)
    ax.axhline(2, color="#d32f2f", ls="--", lw=0.8)
    ax.axhline(0, color="black", lw=0.5)
    ax.set_xticks(range(len(orden)))
    ax.set_xticklabels(orden, fontsize=6.5, rotation=45, ha="right", rotation_mode="anchor")
    ax.set_ylim(-20, 30)
    ax.set_ylabel(r"$\Delta$AP@0.5 (pp)", fontsize=7)
    ax.tick_params(axis="y", labelsize=6.5)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color="#c8c8c8", label="Control")] + [Line2D([], [], marker=mk[s], ls="", color=col[s], ms=3.5, label=s) for s in col]
              + [Line2D([], [], color="#d32f2f", ls="--", lw=0.8, label="+2 pp")], fontsize=6, ncol=5, loc="upper center", bbox_to_anchor=(0.5, 1.16), frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(pad=0.4)
    fig.savefig(os.path.join(AQUI, "fig_gap_ic%s.png" % ("_es" if es else "")))
    plt.close(fig)


def main():
    v15 = None
    p = os.path.join(RAIZ, "informes", "veredicto_h15.md")
    if os.path.exists(p):
        m = re.search(r"Veredicto H15: \*\*(\w[\w ]*)\*\* \((\d) de 3", open(p, encoding="utf-8").read())
        if m:
            v15 = m.group(1).capitalize(), m.group(2)
    for es in (True, False):
        vh = None
        if v15:
            vh = ("No detectada (%s de 3)" % v15[1] if v15[0].startswith("Sostenida") else "Pasa la regla (%s de 3)" % v15[1]) if es else \
                 ("Not detected (%s of 3)" % v15[1] if v15[0].startswith("Sostenida") else "Passes the rule (%s of 3)" % v15[1])
        partes = {"hip": tabla_hipotesis(es, vh), "reg": tabla_registro(es), "celdas": tabla_celdas(es), "estad": tabla_estadistica(es),
                  "cruzada": tabla_cruzada(es), "extra": tabla_extra(es), "vis": tabla_vis(es), "panel": tabla_panel(es)}
        for k, v in partes.items():
            open(os.path.join(AQUI, "tablas_suplemento_%s_%s.tex" % ("es" if es else "en", k)), "w", encoding="utf-8").write(v + "\n")
        figura_ic(es)
    print("ok")


if __name__ == "__main__":
    main()
