"""Tabla del suplemento con la sensibilidad de la estimación global (revisión del 10/11/2026, obs. 1 y 6).
Lee informes/analisis_final/revision_10nov.json y escribe tablas_suplemento_{es,en}_rev10.tex.
Uso: python suplemento_revision10nov.py"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(os.path.dirname(AQUI), "informes", "analisis_final", "revision_10nov.json"), encoding="utf-8"))


def n(v, es):
    s = ("%+.2f" % v)
    s = ("$-$" + s[1:]) if s.startswith("-") else s
    return s.replace(".", "{,}") if es else s


def ic(par, es):
    return "[%s; %s]" % (n(par[0], es), n(par[1], es))


for es in (True, False):
    filas = []
    nombres = {"mixto_original": ("Modelo mixto (texto)", "Mixed model (text)"),
               "mixto_V1_compartida": ("Con V1 compartidas", "With shared V1"),
               "bootstrap_bloques": ("\\emph{Bootstrap} de bloques", "Block bootstrap")}
    for conj, etq in (("dosis_habitual", ("Dosis habitual (12 bloques)", "Usual dose (12 blocks)")),
                      ("con_H18e", ("Con H18e (14 bloques)", "With H18e (14 blocks)"))):
        filas.append("\\multicolumn{4}{@{}l}{\\emph{%s}} \\\\" % etq[0 if es else 1])
        for m, nm in nombres.items():
            r = d[conj][m]
            celdas = []
            for f in ("NO", "CP", "EX"):
                est = r[f].get("est", r[f].get("media"))
                celdas.append("%s %s" % (n(est, es), ic(r[f]["IC90"], es)))
            filas.append("%s & %s \\\\" % (nm[0 if es else 1], " & ".join(celdas)))
    az = d["azar_dosis_habitual_con_control"]
    if es:
        cap = ("Sensibilidad de la estimación global por fuente (análisis posterior, revisión del 10/11/2026): estimación e IC del 90\\,\\%% "
               "(prueba unilateral de no superioridad: límite superior frente a +2 pp). «Con V1 compartidas» añade un componente aleatorio para las V1 que "
               "comparten H9b, H10 y H10-s; H12a y H12b; H15, H16a y H16b; y H18a con H18e. Celdas que pasarían la regla por azar "
               "(efecto 0) en los bloques con control y dosis habitual: %s con el IC por imágenes (observadas %d) y %s con el "
               "jerárquico (observadas %d), de %d. Script: \\texttt{informes/revision\\_10nov.py}."
               % (str(az["imagenes"]["esperadas_nulo"]).replace(".", "{,}"), az["imagenes"]["observadas"],
                  str(az["jerarquico"]["esperadas_nulo"]).replace(".", "{,}"), az["jerarquico"]["observadas"], az["celdas"]))
        cab = "Especificación & NO & CP & EX \\\\"
    else:
        cap = ("Sensitivity of the global estimate per source (post hoc analysis, review of 10 November 2026): estimate and 90\\,\\%% CI "
               "(one-sided non-superiority test: upper limit against +2 pp). ``With shared V1'' adds a random component for the V1 shared by H9b, H10 "
               "and H10-s; H12a and H12b; H15, H16a and H16b; and H18a with H18e. Cells that would pass the rule by chance (zero effect) "
               "in the usual-dose blocks with a control: %s with the image CI (%d observed) and %s with the hierarchical CI (%d observed), "
               "out of %d. Script: \\texttt{informes/revision\\_10nov.py}."
               % (az["imagenes"]["esperadas_nulo"], az["imagenes"]["observadas"], az["jerarquico"]["esperadas_nulo"],
                  az["jerarquico"]["observadas"], az["celdas"]))
        cab = "Specification & NO & CP & EX \\\\"
    tex = ("\\begin{table}[H]\\centering\\small\n\\caption{%s}\\label{tab:s-sens10}\n\\begin{tabular}{@{}llll@{}}\\toprule\n%s\\midrule\n%s\n"
           "\\bottomrule\\end{tabular}\\end{table}\n" % (cap, cab, "\n".join(filas)))
    open(os.path.join(AQUI, "tablas_suplemento_%s_rev10.tex" % ("es" if es else "en")), "w", encoding="utf-8").write(tex)
print("ok")
