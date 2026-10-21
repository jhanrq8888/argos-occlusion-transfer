#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Paso 2b: acuerdo inter-anotador y consenso.

Calcula el kappa ponderado (pesos cuadraticos) entre los dos anotadores,
lista las discrepancias para resolverlas por consenso y verifica las cuotas
por estrato exigidas en la Seccion 1.9 del PPI.

Se usa kappa PONDERADO y no simple porque el nivel de oclusion es ordinal:
confundir "ligera" con "severa" es un error mayor que confundir "ligera"
con "moderada", y el kappa simple los trata igual.

Uso:
    python 03_calcular_kappa.py --a anotacion_anotador_A.csv --b anotacion_anotador_B.csv
    python 03_calcular_kappa.py --a a.csv --b b.csv --consenso consenso.csv
    python 03_calcular_kappa.py --selftest
"""

import argparse
import csv
import os
import sys
from collections import Counter

# Orden ordinal de los estratos. La distancia entre ellos es lo que pondera
# el kappa cuadratico, de modo que el orden importa.
ORDEN = ["sin", "ligera", "moderada", "severa"]
CUOTA_POR_ESTRATO = 50
CUOTA_TOTAL = 300


def leer_csv(ruta):
    """Devuelve {id_instancia: fila} desde un CSV de la herramienta."""
    if not os.path.exists(ruta):
        sys.exit("ERROR: no se encuentra %s" % ruta)
    datos = {}
    with open(ruta, newline="", encoding="utf-8-sig") as fh:
        for fila in csv.DictReader(fh):
            if fila.get("id_instancia"):
                datos[fila["id_instancia"]] = fila
    return datos


def kappa_ponderado(pares, categorias=ORDEN):
    """Kappa de Cohen con pesos cuadraticos.

    `pares` es una lista de tuplas (etiqueta_a, etiqueta_b).
    Devuelve (kappa, matriz_confusion, n).

    Pesos: w_ij = 1 - ((i-j)^2 / (k-1)^2), de modo que el acuerdo pleno pesa
    1 y el desacuerdo maximo pesa 0.
    """
    k = len(categorias)
    idx = {c: i for i, c in enumerate(categorias)}
    n = len(pares)
    if n == 0:
        return None, None, 0

    obs = [[0] * k for _ in range(k)]
    for a, b in pares:
        obs[idx[a]][idx[b]] += 1

    fila = [sum(obs[i]) for i in range(k)]
    col = [sum(obs[i][j] for i in range(k)) for j in range(k)]

    def peso(i, j):
        if k == 1:
            return 1.0
        return 1.0 - ((i - j) ** 2) / float((k - 1) ** 2)

    po = sum(peso(i, j) * obs[i][j] for i in range(k) for j in range(k)) / n
    pe = sum(peso(i, j) * fila[i] * col[j] for i in range(k)
             for j in range(k)) / float(n * n)

    if abs(1.0 - pe) < 1e-12:
        # Acuerdo esperado igual a 1: kappa indefinido (todo en una categoria).
        return None, obs, n
    return (po - pe) / (1.0 - pe), obs, n


def interpretar(kp):
    if kp is None:
        return "indefinido (sin variabilidad suficiente)"
    if kp < 0.40:
        return "INSUFICIENTE - revisar la guia y repetir el piloto"
    if kp < 0.60:
        return "DEBIL - repetir el piloto antes de continuar"
    if kp < 0.80:
        return "aceptable - declarar el valor en el informe"
    return "bueno"


def analizar(ruta_a, ruta_b, ruta_consenso=None, nombre_a="A", nombre_b="B"):
    A, B = leer_csv(ruta_a), leer_csv(ruta_b)
    comunes = sorted(set(A) & set(B))

    print("=" * 62)
    print("ACUERDO INTER-ANOTADOR")
    print("=" * 62)
    print("  %-12s %d instancias" % (nombre_a, len(A)))
    print("  %-12s %d instancias" % (nombre_b, len(B)))
    print("  %-12s %d instancias" % ("en comun", len(comunes)))
    solo_a, solo_b = set(A) - set(B), set(B) - set(A)
    if solo_a or solo_b:
        print("  AVISO: %d solo en %s, %d solo en %s (se ignoran)"
              % (len(solo_a), nombre_a, len(solo_b), nombre_b))
    if not comunes:
        sys.exit("ERROR: no hay instancias en comun.")

    # El kappa se calcula solo sobre instancias evaluables por AMBOS: incluir
    # "no_evaluable" como una categoria mas mezclaria dos decisiones distintas
    # (que estrato es / si se puede juzgar).
    pares, no_eval, invalidas = [], [], 0
    for i in comunes:
        ea, eb = A[i].get("estrato", ""), B[i].get("estrato", "")
        if ea == "no_evaluable" or eb == "no_evaluable":
            no_eval.append(i)
        elif ea in ORDEN and eb in ORDEN:
            pares.append((ea, eb))
        else:
            invalidas += 1

    print("\n  evaluables por ambos : %d" % len(pares))
    print("  no evaluables        : %d (excluidas del kappa)" % len(no_eval))
    if invalidas:
        print("  etiquetas invalidas  : %d" % invalidas)

    kp, mat, n = kappa_ponderado(pares)
    print("\n" + "-" * 62)
    if kp is None:
        print("  Kappa ponderado: indefinido")
    else:
        print("  KAPPA PONDERADO (cuadratico): %.3f" % kp)
    print("  Lectura: %s" % interpretar(kp))
    print("-" * 62)

    if mat:
        print("\nMatriz de confusion (filas=%s, columnas=%s):" % (nombre_a, nombre_b))
        print("            " + "".join("%10s" % c for c in ORDEN))
        for i, c in enumerate(ORDEN):
            print("  %-10s" % c + "".join("%10d" % v for v in mat[i]))

        adyacentes = sum(mat[i][j] for i in range(len(ORDEN))
                         for j in range(len(ORDEN)) if abs(i - j) == 1)
        lejanos = sum(mat[i][j] for i in range(len(ORDEN))
                      for j in range(len(ORDEN)) if abs(i - j) >= 2)
        acuerdo = sum(mat[i][i] for i in range(len(ORDEN)))
        print("\n  acuerdo exacto      : %d (%.1f%%)" % (acuerdo, 100.0 * acuerdo / n))
        print("  desacuerdo vecino   : %d (%.1f%%)" % (adyacentes, 100.0 * adyacentes / n))
        print("  desacuerdo lejano   : %d (%.1f%%)" % (lejanos, 100.0 * lejanos / n))
        if lejanos:
            print("  -> Los desacuerdos lejanos suelen indicar que un anotador")
            print("     esta contando la oscuridad como oclusion. Revisar la")
            print("     Seccion 2 de la guia con esos casos concretos.")

    # --- Discrepancias a resolver -------------------------------------------
    disc = [i for i in comunes
            if A[i].get("estrato") != B[i].get("estrato")]
    print("\nDiscrepancias a resolver por consenso: %d" % len(disc))
    for i in disc[:15]:
        print("  %-24s %-14s vs %-14s"
              % (i, A[i].get("estrato"), B[i].get("estrato")))
    if len(disc) > 15:
        print("  ... y %d mas (listado completo en discrepancias.csv)" % (len(disc) - 15))

    base = os.path.dirname(os.path.abspath(ruta_a))
    with open(os.path.join(base, "discrepancias.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id_instancia", "imagen", "estrato_" + nombre_a,
                    "estrato_" + nombre_b, "consenso"])
        for i in disc:
            w.writerow([i, A[i].get("imagen", ""), A[i].get("estrato"),
                        B[i].get("estrato"), ""])
    print("\n  -> discrepancias.csv generado. Rellenar la columna 'consenso'")
    print("     entre los dos anotadores y volver a ejecutar con --consenso.")

    # --- Cuotas -------------------------------------------------------------
    if ruta_consenso:
        verificar_cuotas(ruta_consenso)
    else:
        prov = Counter()
        for i in comunes:
            if A[i].get("estrato") == B[i].get("estrato") \
               and A[i].get("estrato") in ORDEN:
                prov[A[i]["estrato"]] += 1
        print("\nDistribucion provisional (solo acuerdos, sin consenso aun):")
        for c in ORDEN:
            print("    %-10s %4d" % (c, prov[c]))
        print("  Cifra orientativa: las cuotas se verifican sobre el fichero")
        print("  de consenso, no sobre esta.")
    return kp


def verificar_cuotas(ruta):
    """Comprueba las cuotas de la Seccion 1.9 sobre el fichero de consenso."""
    D = leer_csv(ruta)
    cnt = Counter(f.get("estrato") for f in D.values())
    total = sum(cnt[c] for c in ORDEN)

    print("\n" + "=" * 62)
    print("VERIFICACION DE CUOTAS (Seccion 1.9 del PPI)")
    print("=" * 62)
    for c in ORDEN:
        marca = "" if c == "sin" or cnt[c] >= CUOTA_POR_ESTRATO else "  <-- POR DEBAJO"
        print("  %-10s %4d%s" % (c, cnt[c], marca))
    print("  %-10s %4d" % ("TOTAL", total))

    problemas = [c for c in ("ligera", "moderada", "severa")
                 if cnt[c] < CUOTA_POR_ESTRATO]
    if total < CUOTA_TOTAL:
        print("\n  AVISO: total por debajo de %d instancias." % CUOTA_TOTAL)
    if problemas:
        print("\n  Estratos por debajo de %d: %s"
              % (CUOTA_POR_ESTRATO, ", ".join(problemas)))
        if "severa" in problemas:
            print("\n  APLICAR LA REGLA DE FUSION ya declarada en la Seccion 1.9:")
            print("    moderada + severa -> estrato unico 'ocluida >=30%%' (n=%d)"
                  % (cnt["moderada"] + cnt["severa"]))
            print("    Reportar el conteo alcanzado y declararlo como limitacion.")
            print("    La regla se fijo ANTES de ver los datos: no se renegocia.")
    else:
        print("\n  Cuotas satisfechas. No procede fusionar estratos.")


def selftest():
    import tempfile
    print("--- verificando el calculo de kappa ---\n")
    fallos = []

    def comp(desc, obt, esp, tol=1e-6):
        ok = (abs(obt - esp) < tol) if isinstance(esp, float) else (obt == esp)
        print("  [%s] %-46s %s" % ("ok" if ok else "FALLA", desc,
                                   round(obt, 4) if isinstance(obt, float) else obt))
        if not ok:
            fallos.append("%s: esperado %s, obtenido %s" % (desc, esp, obt))

    # 1. Acuerdo perfecto -> kappa = 1
    k, _, _ = kappa_ponderado([("sin", "sin"), ("severa", "severa"),
                               ("ligera", "ligera"), ("moderada", "moderada")])
    comp("acuerdo perfecto da kappa 1", k, 1.0)

    # 2. El desacuerdo vecino penaliza menos que el lejano.
    k_vec, _, _ = kappa_ponderado(
        [("sin", "ligera")] * 5 + [("severa", "severa")] * 5 +
        [("ligera", "ligera")] * 5 + [("moderada", "moderada")] * 5)
    k_lej, _, _ = kappa_ponderado(
        [("sin", "severa")] * 5 + [("severa", "severa")] * 5 +
        [("ligera", "ligera")] * 5 + [("moderada", "moderada")] * 5)
    comp("desacuerdo vecino penaliza menos que lejano", k_vec > k_lej, True)

    # 3. Contraste con un valor calculado a mano.
    #    Pares: 2x(sin,sin), 1x(sin,ligera), 1x(ligera,sin)
    #    k=4 categorias -> w_ij = 1 - (i-j)^2/9 ; w vecino = 8/9
    pares = [("sin", "sin"), ("sin", "sin"), ("sin", "ligera"), ("ligera", "sin")]
    k3, mat3, n3 = kappa_ponderado(pares)
    # po = (1+1+8/9+8/9)/4 = 0.944444
    po = (1 + 1 + 8 / 9 + 8 / 9) / 4.0
    # marginales A: sin=3, ligera=1 ; B: sin=3, ligera=1
    # pe = [w(0,0)*3*3 + w(0,1)*3*1 + w(1,0)*1*3 + w(1,1)*1*1] / 16
    pe = (1 * 9 + (8 / 9) * 3 + (8 / 9) * 3 + 1 * 1) / 16.0
    comp("kappa coincide con el calculo manual", k3, (po - pe) / (1 - pe))
    comp("matriz de confusion correcta", mat3[0][0], 2)
    comp("n de pares correcto", n3, 4)

    # 4. Kappa cerca de 0 cuando el acuerdo es el esperado por azar.
    import random
    rnd = random.Random(7)
    az = [(rnd.choice(ORDEN), rnd.choice(ORDEN)) for _ in range(4000)]
    k4, _, _ = kappa_ponderado(az)
    comp("etiquetado al azar da kappa proximo a 0", abs(k4) < 0.08, True)

    # 5. Flujo completo sobre CSV, incluyendo exclusion de no_evaluable.
    tmp = tempfile.mkdtemp(prefix="kappa_test_")
    cab = "id_instancia,imagen,x,y,w,h,estrato,truncado,no_evaluable,segundos\n"
    with open(os.path.join(tmp, "a.csv"), "w") as f:
        f.write(cab)
        f.write("i1,test/x.jpg,0,0,10,20,sin,0,0,3\n")
        f.write("i2,test/x.jpg,0,0,10,20,severa,0,0,4\n")
        f.write("i3,test/x.jpg,0,0,10,20,no_evaluable,0,1,2\n")
    with open(os.path.join(tmp, "b.csv"), "w") as f:
        f.write(cab)
        f.write("i1,test/x.jpg,0,0,10,20,sin,0,0,3\n")
        f.write("i2,test/x.jpg,0,0,10,20,moderada,0,0,5\n")
        f.write("i3,test/x.jpg,0,0,10,20,severa,0,0,2\n")
    print()
    analizar(os.path.join(tmp, "a.csv"), os.path.join(tmp, "b.csv"))
    disc = leer_csv(os.path.join(tmp, "discrepancias.csv"))
    comp("discrepancias.csv recoge i2 e i3", sorted(disc), ["i2", "i3"])

    import shutil
    shutil.rmtree(tmp)
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d):" % len(fallos))
        for f_ in fallos:
            print("   - %s" % f_)
        return 1
    print("AUTOTEST SUPERADO: 7/7 comprobaciones.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - kappa ponderado")
    ap.add_argument("--a", help="CSV del anotador A")
    ap.add_argument("--b", help="CSV del anotador B")
    ap.add_argument("--consenso", help="CSV de consenso (verifica cuotas)")
    ap.add_argument("--nombre-a", default="A")
    ap.add_argument("--nombre-b", default="B")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())
    if not (args.a and args.b):
        ap.error("se requieren --a y --b (o --selftest)")
    analizar(args.a, args.b, args.consenso, args.nombre_a, args.nombre_b)


if __name__ == "__main__":
    main()