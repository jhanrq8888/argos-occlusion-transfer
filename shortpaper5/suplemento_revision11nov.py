"""Tablas del suplemento pedidas por el reporte de seguimiento del 11/11/2026 (obs. 11 y 17), y nota sobre H1, H2, H5, H11
y H19 (obs. 12 y 14). Lee informes/analisis_final/ic_welch_celdas.csv, especificidad_escalas.csv y revision_11nov.json
y escribe tablas_suplemento_{es,en}_rev11.tex.
Uso: python suplemento_revision11nov.py"""
import json
import os

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
AF = os.path.join(os.path.dirname(AQUI), "informes", "analisis_final")
W = pd.read_csv(os.path.join(AF, "ic_welch_celdas.csv"))
E = pd.read_csv(os.path.join(AF, "especificidad_escalas.csv"))
R = json.load(open(os.path.join(AF, "revision_11nov.json"), encoding="utf-8"))
ETQ = {"H18e-baja": ("H18e-b", "H18e-l"), "H18e-alta": ("H18e-a", "H18e-h")}
BLQ = {"h15": "H15", "h18a": "H18a", "h18e_baja": ("H18e-b", "H18e-l"), "h18e_alta": ("H18e-a", "H18e-h")}


def n(v, es, d=2):
    s = ("%+." + str(d) + "f") % v
    s = ("$-$" + s[1:]) if s.startswith("-") else s
    return s.replace(".", "{,}") if es else s


def ic(a, b, es):
    return "[%s; %s]" % (n(a, es), n(b, es))


for es in (True, False):
    k = 0 if es else 1
    filas = []
    previo = None
    for _, r in W.iterrows():
        etq = ETQ.get(r.etiqueta, (r.etiqueta, r.etiqueta))[k]
        if previo is not None and r.dosis != "habitual" and previo == "habitual":
            filas.append("\\midrule")
        previo = r.dosis
        marca = lambda pasa, desc: ("*" if pasa else "") + ("$^\\ddagger$" if desc else "")
        filas.append("%s & %s & %s & %s%s & %s%s & %s \\\\" % (
            etq, r.fuente, n(r.delta_tabla, es), ic(r.jer_lo, r.jer_hi, es), marca(r.pasa_jer, r.descarta_jer),
            ic(r.welch_lo, r.welch_hi, es), marca(r.pasa_welch, r.descarta_welch), ("%.1f" % r.gl).replace(".", "{,}" if es else ".")))
    p, dsc, an = R["pasan"], R["descartan_2pp"], R["ancho_medio"]
    f = lambda v: (("%.2f" % v).replace(".", ",") if es else "%.2f" % v)
    if es:
        cap = ("IC por celda con la varianza entre semillas (reporte de seguimiento del 11/11/2026, obs. 11; análisis posterior). "
               "Celdas reales de la evidencia primaria: V3$-$V1 (pp), IC del 95\\,\\%% jerárquico (semillas e imágenes, el de la tabla I) "
               "y de la $t$ de Welch con los AP por semilla de V1 y V3 (gl: grados de libertad de Welch). Con 3 semillas, el "
               "\\emph{bootstrap} jerárquico solo tiene 10 remuestreos distintos de semillas y subestima la varianza entre ellas; "
               "Welch con 2--4 gl es, a su vez, inestable, así que ninguno de los dos es exacto y ambos son sensibilidad: la regla "
               "registrada usa el IC por imágenes y su veredicto no cambia. * pasa (+2 pp e IC $>0$); $^\\ddagger$ descarta +2 pp. "
               "En las 36 celdas de dosis habitual pasan %d (imágenes), %d (jerárquico) y %d (Welch), y descartan +2 pp %d (jerárquico) "
               "y %d (Welch). Ancho medio del IC: %s, %s y %s pp. H18e usa las V1 de las semillas 0--2. Script: "
               "\\texttt{informes/revision\\_11nov.py}; datos: \\texttt{ic\\_welch\\_celdas.csv}."
               % (p["imagenes"], p["jerarquico"], p["welch"], dsc["jerarquico"], dsc["welch"], f(an["imagenes"]), f(an["jerarquico"]), f(an["welch"])))
        cab = "Bloque & Fuente & $\\Delta$ & IC jerárquico & IC de Welch & gl \\\\"
    else:
        cap = ("Per-cell CI with the between-seed variance (follow-up review of 11 November 2026, obs. 11; post hoc analysis). "
               "Real cells of the primary evidence: V3$-$V1 (pp), hierarchical 95\\,\\%% CI (seeds and images, as in Table I) and "
               "Welch $t$ CI from the per-seed AP of V1 and V3 (df: Welch degrees of freedom). With 3 seeds the hierarchical "
               "bootstrap has only 10 distinct seed resamples and underestimates the between-seed variance; Welch with 2--4 df is "
               "itself unstable, so neither is exact and both are sensitivities: the registered rule uses the image CI and its "
               "verdict does not change. * passes (+2 pp and CI $>0$); $^\\ddagger$ rules out +2 pp. Of the 36 usual-dose cells, "
               "%d pass (images), %d (hierarchical) and %d (Welch), and %d (hierarchical) and %d (Welch) rule out +2 pp. Mean CI "
               "width: %s, %s and %s pp. H18e uses the V1 of seeds 0--2. Script: \\texttt{informes/revision\\_11nov.py}; data: "
               "\\texttt{ic\\_welch\\_celdas.csv}."
               % (p["imagenes"], p["jerarquico"], p["welch"], dsc["jerarquico"], dsc["welch"], f(an["imagenes"]), f(an["jerarquico"]), f(an["welch"])))
        cab = "Block & Source & $\\Delta$ & Hierarchical CI & Welch CI & df \\\\"
    t1 = ("\\begin{table}[H]\\centering\\footnotesize\n\\caption{%s}\\label{tab:s-welch}\n\\begin{tabular}{@{}llrllr@{}}\\toprule\n%s\\midrule\n%s\n"
          "\\bottomrule\\end{tabular}\\end{table}\n" % (cap, cab, "\n".join(filas)))
    # especificidad en tres escalas
    filas = []
    for _, r in E.iterrows():
        b = BLQ[r.bloque]
        b = b[k] if isinstance(b, tuple) else b
        conj = {"nightowls": "NO", "citypersons_convencion": "CP"}[r.conjunto]
        est = {"ocluida": ("ocluidas", "occluded"), "sin oclusion": ("sin oclusión", "unoccluded")}[r.estrato][k]
        filas.append("%s & %s & %s & %s & %s & %s & %s & %s \\\\" % (
            b, conj, est, f(r.AP_V1), f(r.AP_V3), n(r.dif_pp, es), n(r.cambio_relativo_pct, es, 1), n(r.dif_tasa_fallo_relativa_pct, es, 1)))
    if es:
        cap = ("Especificidad en tres escalas (obs. 17; análisis posterior): Faster R-CNN con siluetas, AP@0.5 de V1 y V3 (media de "
               "semillas) en personas ocluidas y sin oclusión, diferencia en pp (la del texto), cambio relativo del AP y cambio "
               "relativo de la tasa de fallos (1$-$AP). En pp, la dosis alta mejora igual a ocluidos y no ocluidos; en escala "
               "relativa, más a los ocluidos (su AP base es mucho menor); en tasa de fallos, menos. La lectura de «no específica» "
               "depende, por tanto, de la escala; el texto usa la diferencia en pp. Datos: \\texttt{especificidad\\_escalas.csv} "
               "(incluye la diferencia en logit).")
        cab = "Bloque & Fuente & Personas & AP V1 & AP V3 & pp & Relativo (\\%) & Tasa de fallos (\\%) \\\\"
    else:
        cap = ("Specificity on three scales (obs. 17; post hoc analysis): Faster R-CNN with silhouettes, AP@0.5 of V1 and V3 (mean "
               "over seeds) for occluded and unoccluded people, difference in pp (the one in the text), relative change in AP and "
               "relative change in miss rate (1$-$AP). In pp, the high dose improves occluded and unoccluded people equally; on the "
               "relative scale, occluded people more (their base AP is much lower); in miss rate, less. Whether the gain is "
               "``not specific'' therefore depends on the scale; the text uses the pp difference. Data: "
               "\\texttt{especificidad\\_escalas.csv} (includes the logit difference).")
        cab = "Block & Source & People & AP V1 & AP V3 & pp & Relative (\\%) & Miss rate (\\%) \\\\"
    t2 = ("\\begin{table}[H]\\centering\\footnotesize\n\\caption{%s}\\label{tab:s-escalas}\n\\begin{tabular}{@{}lllrrrrr@{}}\\toprule\n%s\\midrule\n%s\n"
          "\\bottomrule\\end{tabular}\\end{table}\n" % (cap, cab, "\n".join(filas)))
    if es:
        nota = ("\\noindent\\textbf{Lo registrado y lo reportado (obs. 14).} El programa empezó con H1, H2 y H5 (\\texttt{PROTOCOLO.md}, "
                "11/09/2026, y \\texttt{PROTOCOLO\\_v2.md}): H1 predecía que YOLOv11s con un módulo de atención CBAM y aumento (V4) "
                "superaría a V1 en ExDark ocluido sin perder más del 10\\,\\%% de FPS, y no se sostuvo (V4$-$V1 $-$3,29 pp en la oclusión "
                "severa); H2, que el aumento aportaría más que CBAM (V3$-$V1 frente a V2$-$V1), y no se sostuvo ($-$2,43 frente a "
                "+0,18 pp); H5, que la ganancia sintética de las siluetas sería menor que la de los parches, y se sostuvo. Sus 14 "
                "corridas (variantes V2 y V4 y dos controles) están entre las 133 (tabla de corridas) y su veredicto, en "
                "\\texttt{informes/veredictos\\_H1\\_H7.md}. La celda registrada de H11 era la visibilidad 0,20--0,50 de CityPersons "
                "($n=432$): +1,44 [$-$0,64; +3,34] (no confirmada); la tabla I da \\emph{heavy} para comparar con los demás bloques. "
                "H13 predecía AUC(parches) $>$ AUC(siluetas) $>$ AUC(difusión) con DINOv2: se cumplió la primera diferencia (+0,043 "
                "[+0,031; +0,057]) y no la segunda (+0,015 [$-$0,003; +0,034]), de ahí «parcialmente confirmada».\n\n"
                "\\noindent\\textbf{H19 (obs. 12).} Para cerrar la alternativa del detector \\emph{transformer}, el 11/11/2026 se "
                "registró un bloque RT-DETR-l con 30 épocas fijas y V1 y V3 en la misma máquina (\\texttt{PREREGISTRO\\_H19.md}, "
                "congelamiento v3.13, sellado con OpenTimestamps antes de entrenar). No se ejecutó por falta de presupuesto para la "
                "GPU alquilada, y así queda declarado en \\texttt{CAMBIOS\\_PROTOCOLO.md}; RT-DETR-l solo tiene el bloque H8, con "
                "exposición desigual (V1 en 28--31 épocas, V3 en 51--77).\n\n")
    else:
        nota = ("\\noindent\\textbf{Registered versus reported (obs. 14).} The programme began with H1, H2 and H5 (\\texttt{PROTOCOLO.md}, "
                "11 September 2026, and \\texttt{PROTOCOLO\\_v2.md}): H1 predicted that YOLOv11s with a CBAM attention module and "
                "augmentation (V4) would beat V1 on occluded ExDark without losing more than 10\\,\\%% FPS, and did not hold (V4$-$V1 "
                "$-$3.29 pp on severe occlusion); H2, that augmentation would contribute more than CBAM (V3$-$V1 against V2$-$V1), and "
                "did not hold ($-$2.43 against +0.18 pp); H5, that the synthetic gain of silhouettes would be smaller than that of "
                "patches, and held. Their 14 runs (variants V2 and V4 and two controls) are among the 133 (run table) and their "
                "verdict is in \\texttt{informes/veredictos\\_H1\\_H7.md}. The registered H11 cell was CityPersons visibility "
                "0.20--0.50 ($n=432$): +1.44 [$-$0.64; +3.34] (not confirmed); Table I gives \\emph{heavy} for comparison with the "
                "other blocks. H13 predicted AUC(patches) $>$ AUC(silhouettes) $>$ AUC(diffusion) with DINOv2: the first difference "
                "held (+0.043 [+0.031; +0.057]) and the second did not (+0.015 [$-$0.003; +0.034]), hence ``partially confirmed''.\n\n"
                "\\noindent\\textbf{H19 (obs. 12).} To close the \\emph{transformer} alternative, on 11 November 2026 an RT-DETR-l "
                "block with 30 fixed epochs and V1 and V3 on the same machine was registered (\\texttt{PREREGISTRO\\_H19.md}, freeze "
                "v3.13, sealed with OpenTimestamps before training). It was not run for lack of budget for the rented GPU, as "
                "declared in \\texttt{CAMBIOS\\_PROTOCOLO.md}; RT-DETR-l only has block H8, with unequal exposure (V1 at 28--31 "
                "epochs, V3 at 51--77).\n\n")
    open(os.path.join(AQUI, "tablas_suplemento_%s_rev11.tex" % ("es" if es else "en")), "w", encoding="utf-8").write(nota + t1 + t2)
print("ok")
