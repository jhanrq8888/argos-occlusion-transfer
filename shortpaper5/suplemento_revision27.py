#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tablas del suplemento para la revision externa del 27/10 (H18, modelo mixto, analisis sin ExDark).
Lee resultados_h18/analisis/contrastes_h18.json, resultados_h18/resumen_ap.csv e
informes/analisis_final/modelo_mixto_m3.json; escribe tablas_suplemento_{es,en}_rev27.tex. Ninguna cifra a mano.
Uso: python suplemento_revision27.py"""
import json
import os

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
FUENTE = {"silueta_severa": "control", "nightowls": "NO", "citypersons_convencion": "CP", "test_proxy": "EX"}
BLOQUE_EN = {"H18a": "H18a", "H18e-baja": "H18e-low", "H18e-alta": "H18e-high"}
VERED = {"es": {"Sostenida": "No detectada", "Refutada": "Detectada"},
         "en": {"Sostenida": "Not detected", "Refutada": "Detected"}}
T = {
    "es": dict(
        cap_h18="H18 (PREREGISTRO\\_H18.md, v3.12): celdas con los dos IC. $\Delta$ = V3 $-$ V1 en AP@0.5 (pp), media de semillas; * pasa (+2 pp con IC $>0$).",
        cab_h18="Bloque & Fuente & $n$ & Semillas & V1 & V3 & $\Delta$ & IC imágenes & IC jerárquico & Veredicto",
        cap_esp="Especificidad de H18 (semillas 0--2): $\Delta$ por estrato. Con la dosis alta, la ganancia en las personas sin oclusión es igual o mayor que en las ocluidas.",
        cab_esp="Fuente & Estrato & $\Delta$ baja & $\Delta$ habitual & $\Delta$ alta",
        cap_mm="Modelo mixto global (REML): $\Delta$ por semilla $\\sim$ fuente + bloque + semilla(bloque). Estimación e IC del 95\\,\\%, en pp. Posterior a la revisión externa; no decide hipótesis.",
        cab_mm="Modelo & NightOwls & CityPersons & ExDark & Control (por DE) & Obs. / bloques",
        mod={"modelo0_igual_dosis_base": "Primario: dosis habitual, exposición igual",
             "modelo0c_igual_dosis_base_con_control": "Primario + ganancia en el control",
             "modelo0b_todos_dosis_base": "Dosis habitual, todos los bloques",
             "modelo1_igual": "Exposición igual, con H18e",
             "modelo1b_todos": "Todos los bloques, con H18e"},
        cap_rec="Recuentos descriptivos con el IC por imágenes y con el jerárquico (criterio uniforme de semillas).",
        cab_rec="Conjunto & Celdas & Pasan (img./jer.) & Descartan +2 (img./jer.) & No concluyentes (img./jer.)",
        rec={"igual_dosis_base": "Exposición igual, dosis habitual", "todos_dosis_base": "Con control, dosis habitual",
             "igual_33": "Exposición igual, con H18e", "todos_51": "Con control, con H18e"},
        sinex="\\noindent\\textbf{Sin el indicador de ExDark.} Exigiendo que pasen NightOwls y CityPersons, detectan transferencia: %s (IC por imágenes) y %s (IC jerárquico). De %d celdas sin ExDark, pasan %d con el IC por imágenes y %d con el jerárquico.\n",
        y=" y ", est={"global": "global", "sin": "sin oclusión", "ocluida": "ocluida", "bare": "sin oclusión (\\emph{bare})",
                      "partial": "\\emph{partial}", "heavy": "\\emph{heavy}", "severa": "severa", "ligera": "ligera",
                      "moderada": "moderada"}),
    "en": dict(
        cap_h18="H18 (PREREGISTRO\\_H18.md, v3.12): cells with both CIs. $\Delta$ = V3 $-$ V1 in AP@0.5 (pp), mean over seeds; * passes (+2 pp with CI $>0$).",
        cab_h18="Block & Source & $n$ & Seeds & V1 & V3 & $\Delta$ & Image CI & Hierarchical CI & Verdict",
        cap_esp="Specificity of H18 (seeds 0--2): $\Delta$ by stratum. At the high dose, the gain on unoccluded people is equal to or larger than on occluded ones.",
        cab_esp="Source & Stratum & $\Delta$ low & $\Delta$ usual & $\Delta$ high",
        cap_mm="Global mixed model (REML): per-seed $\Delta$ $\\sim$ source + block + seed(block). Estimate and 95\\,\\% CI, in pp. Post hoc, after the external review; decides no hypothesis.",
        cab_mm="Model & NightOwls & CityPersons & ExDark & Control (per SD) & Obs. / blocks",
        mod={"modelo0_igual_dosis_base": "Primary: usual dose, equal exposure",
             "modelo0c_igual_dosis_base_con_control": "Primary + gain on the control",
             "modelo0b_todos_dosis_base": "Usual dose, all blocks",
             "modelo1_igual": "Equal exposure, with H18e",
             "modelo1b_todos": "All blocks, with H18e"},
        cap_rec="Descriptive counts with the image CI and with the hierarchical CI (uniform seed criterion).",
        cab_rec="Set & Cells & Pass (img./hier.) & Rule out +2 (img./hier.) & Inconclusive (img./hier.)",
        rec={"igual_dosis_base": "Equal exposure, usual dose", "todos_dosis_base": "With control, usual dose",
             "igual_33": "Equal exposure, with H18e", "todos_51": "With control, with H18e"},
        sinex="\\noindent\\textbf{Without the ExDark proxy.} Requiring NightOwls and CityPersons to pass, transfer is detected by: %s (image CI) and %s (hierarchical CI). Of %d cells without ExDark, %d pass with the image CI and %d with the hierarchical one.\n",
        y=" and ", est={"global": "overall", "sin": "unoccluded", "ocluida": "occluded", "bare": "unoccluded (\\emph{bare})",
                        "partial": "\\emph{partial}", "heavy": "\\emph{heavy}", "severa": "severe", "ligera": "light",
                        "moderada": "moderate"}),
}


def num(x, lang, signo=True):
    s = ("%+.2f" if signo else "%.3f") % x
    s = s.replace("-", "$-$")
    return s.replace(".", "{,}") if lang == "es" else s


def ic(lo, hi, lang):
    return "[%s; %s]" % (num(lo, lang), num(hi, lang))


def tabla(cap, cab, filas, cols):
    return ("\\begin{table}[H]\\centering\\small\n\\caption{%s}\n\\begin{tabular}{@{}%s@{}}\\toprule\n%s \\\\\\midrule\n%s\n"
            "\\bottomrule\\end{tabular}\\end{table}\n\n" % (cap, cols, cab, "\n".join(f + " \\\\" for f in filas)))


def main():
    h18 = json.load(open(os.path.join(RAIZ, "resultados_h18", "analisis", "contrastes_h18.json"), encoding="utf-8"))
    mm = json.load(open(os.path.join(RAIZ, "informes", "analisis_final", "modelo_mixto_m3.json"), encoding="utf-8"))
    ap = pd.read_csv(os.path.join(RAIZ, "resultados_h18", "resumen_ap.csv"))
    ap = ap[(ap.luz == "todas") & (ap.semilla <= 2)].copy()
    ap["var"] = ap.corrida.str.replace(r"_s\d+$", "", regex=True)
    m = ap.groupby(["conjunto", "estrato", "var"]).AP50.mean().unstack()
    for lang, t in T.items():
        out = []
        filas = []
        for c in h18:
            pasa = c["delta_pp"] >= 2 and c["IC_img_lo"] > 0
            pasa_j = c["delta_pp"] >= 2 and c["IC_jer_lo"] > 0
            filas.append(" & ".join([BLOQUE_EN[c["bloque"]] if lang == "en" else c["bloque"], FUENTE[c["conjunto"]],
                                     str(c["n_gt"]), str(c["n_V3"]), num(c["AP50_V1"], lang, False),
                                     num(c["AP50_V3"], lang, False), num(c["delta_pp"], lang) + ("*" if pasa else ""),
                                     ic(c["IC_img_lo"], c["IC_img_hi"], lang),
                                     ic(c["IC_jer_lo"], c["IC_jer_hi"], lang) + ("*" if pasa_j else ""),
                                     VERED[lang][c["veredicto_bloque"]] if c["tipo"] == "real" and FUENTE[c["conjunto"]] == "NO" else ""]))
        out.append(tabla(t["cap_h18"], t["cab_h18"], filas, "llrrrrrlll"))
        filas = []
        for conj, ests in (("nightowls", ("sin", "ocluida")), ("citypersons_convencion", ("bare", "partial", "heavy")),
                           ("test_proxy", ("global", "sin", "severa"))):
            for e in ests:
                r = m.loc[(conj, e)]
                filas.append(" & ".join([FUENTE[conj], t["est"][e]] +
                                        [num(100 * (r[v] - r["V1"]), lang) for v in ("V3baja", "V3sil", "V3alta")]))
        out.append(tabla(t["cap_esp"], t["cab_esp"], filas, "llrrr"))
        filas = []
        for k, nom in t["mod"].items():
            x = mm[k]
            g = lambda f: "%s %s" % (num(x[f]["est"], lang), ic(*x[f]["ic"], lang)) if f in x else "---"
            filas.append(" & ".join([nom, g("C(fuente)[NO]"), g("C(fuente)[CP]"), g("C(fuente)[EX]"), g("z_control"),
                                     "%d / %d" % (x["n_obs"], x["n_bloques"])]))
        out.append(tabla(t["cap_mm"], t["cab_mm"], filas, "p{4.2cm}llllr"))
        rc = mm["recuentos"]
        filas = [" & ".join([nom, str(rc[k]["celdas"]), "%d / %d" % (rc[k]["pasan_img"], rc[k]["pasan_jer"]),
                             "%d / %d" % (rc[k]["descartan_img"], rc[k]["descartan_jer"]),
                             "%d / %d" % (rc[k]["no_concluyentes_img"], rc[k]["no_concluyentes_jer"])])
                 for k, nom in t["rec"].items()]
        out.append(tabla(t["cap_rec"], t["cab_rec"], filas, "lrrrr"))
        s = rc["sin_EX"]
        nb = lambda L: t["y"].join(L).replace("H18e-alta", "H18e-high" if lang == "en" else "H18e-alta")
        out.append(t["sinex"] % (nb(s["bloques_ambas_img"]), nb(s["bloques_ambas_jer"]), s["celdas"], s["pasan_img"],
                                 s["pasan_jer"]))
        open(os.path.join(AQUI, "tablas_suplemento_%s_rev27.tex" % lang), "w", encoding="utf-8").write("".join(out))
        print(lang, "ok")


if __name__ == "__main__":
    main()
