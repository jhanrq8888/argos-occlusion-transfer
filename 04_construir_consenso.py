#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Paso 2c: consenso y ground truth real estratificado (Fuente 2b).

Combina los CSV de los dos anotadores con la columna `consenso` de
discrepancias.csv y produce:

    consenso.csv                  etiqueta final por instancia
    dataset/gt_test_real.json     GT estratificado del split de prueba
                                  (formato comun de argos_lib.gt): las
                                  instancias NO anotadas quedan como
                                  'sin_anotar' (validas en la evaluacion
                                  global, ignore en la estratificada: regla
                                  b de la Seccion 2.4) y las no evaluables
                                  como 'ignorar'.
    dataset/conteo_estratos_real.json   conteo publicable por estrato

Y verifica las cuotas (>=300 evaluables, >=50 por estrato ligera/moderada/
severa). Si severa < 50 recuerda la regla de fusion declarada a priori;
la fusion la aplica el script de evaluacion con --fusion, de modo que el
GT conserva siempre los cuatro estratos originales.

Uso:
    python 04_construir_consenso.py --a anotacion_anotador_A.csv --b anotacion_anotador_B.csv
    python 04_construir_consenso.py --a piloto_ana.csv lote_ana.csv \
                                    --b piloto_anotador_B.csv lote_anotador_B.csv \
                                    --discrepancias discrepancias.csv
    python 04_construir_consenso.py --selftest
"""

import argparse
import csv
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argos_lib import ESTRATOS                        # noqa: E402
from argos_lib.gt import (cargar_split_yolo, guardar_gt,   # noqa: E402
                          leer_luz_por_imagen)

CUOTA_POR_ESTRATO = 50
CUOTA_TOTAL = 300


def leer_varios(rutas):
    datos = {}
    for ruta in rutas:
        if not os.path.exists(ruta):
            sys.exit("ERROR: no se encuentra %s" % ruta)
        with open(ruta, newline="", encoding="utf-8-sig") as fh:
            for fila in csv.DictReader(fh):
                if fila.get("id_instancia"):
                    datos[fila["id_instancia"]] = fila   # la ultima gana
    return datos


def leer_discrepancias(ruta):
    cons = {}
    if not ruta or not os.path.exists(ruta):
        return cons
    with open(ruta, newline="", encoding="utf-8-sig") as fh:
        for fila in csv.DictReader(fh):
            v = (fila.get("consenso") or "").strip().lower()
            if fila.get("id_instancia"):
                cons[fila["id_instancia"]] = v
    return cons


def construir(rutas_a, rutas_b, ruta_disc, dataset, raiz_exdark, salida_csv,
              verbose=True):
    A = leer_varios(rutas_a)
    B = leer_varios(rutas_b) if rutas_b else {}
    cons = leer_discrepancias(ruta_disc)
    # Instancias con un solo anotador (fuera del subconjunto doble): se
    # toman tal cual y se contabilizan aparte (anotador unico, limitacion).
    solo_a = sorted(set(A) - set(B))
    comunes = sorted(set(A) & set(B)) if B else []
    validas = set(ESTRATOS) | {"no_evaluable"}

    finales, pendientes, invalidas = {}, [], []
    for i in solo_a:
        ea = A[i].get("estrato", "")
        if ea in validas:
            finales[i] = {"id_instancia": i, "imagen": A[i].get("imagen", ""),
                          "x": A[i].get("x"), "y": A[i].get("y"), "w": A[i].get("w"), "h": A[i].get("h"),
                          "estrato": ea, "truncado": int(A[i].get("truncado") in ("1", 1)),
                          "no_evaluable": int(ea == "no_evaluable"), "origen": "anotador_unico",
                          "oclusor": A[i].get("oclusor", "")}
    for i in comunes:
        ea, eb = A[i].get("estrato", ""), B[i].get("estrato", "")
        if ea == eb and ea in validas:
            est = ea
        elif i in cons and cons[i] in validas:
            est = cons[i]
        elif i in cons and cons[i] == "":
            pendientes.append(i); continue
        elif i in cons:
            invalidas.append((i, cons[i])); continue
        else:
            pendientes.append(i); continue
        trunc = int(A[i].get("truncado") in ("1", 1)) or int(B[i].get("truncado") in ("1", 1))
        finales[i] = {"id_instancia": i, "imagen": A[i].get("imagen", ""),
                      "x": A[i].get("x"), "y": A[i].get("y"),
                      "w": A[i].get("w"), "h": A[i].get("h"),
                      "estrato": est, "truncado": trunc,
                      "no_evaluable": int(est == "no_evaluable"),
                      "origen": "acuerdo" if ea == eb else "consenso",
                      "oclusor": A[i].get("oclusor", "") or B[i].get("oclusor", "")}

    with open(salida_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id_instancia", "imagen", "x", "y",
                                           "w", "h", "estrato", "truncado",
                                           "no_evaluable", "origen", "oclusor"])
        w.writeheader()
        for i in sorted(finales):
            w.writerow(finales[i])

    # --- GT del split de prueba -------------------------------------------
    luz = leer_luz_por_imagen(os.path.join(raiz_exdark, "imageclasslist.txt"))
    imagenes = cargar_split_yolo(dataset, "test", luz)
    por_id = {}
    for nombre, meta in imagenes.items():
        for o in meta["instancias"]:
            por_id[o["id"]] = o
    no_hallados = 0
    for i, f in finales.items():
        o = por_id.get(i)
        if o is None:
            no_hallados += 1
            continue
        o["estrato"] = "ignorar" if f["estrato"] == "no_evaluable" else f["estrato"]
        o["truncado"] = f["truncado"]
        o["anotada"] = 1
        o["oclusor"] = f.get("oclusor", "")
    ruta_gt = os.path.join(dataset, "gt_test_real.json")
    guardar_gt(ruta_gt, "test_real", os.path.join(dataset, "images"), imagenes,
               extra={"fuente": "anotacion manual, 2 anotadores + consenso",
                      "n_anotadas": len(finales), "n_pendientes": len(pendientes)})

    cnt = Counter(f["estrato"] for f in finales.values())
    total_eval = sum(cnt[c] for c in ESTRATOS)
    conteo = {"por_estrato": {c: cnt[c] for c in ESTRATOS},
              "n_doble_anotacion": len(comunes), "n_anotador_unico": len(solo_a),
              "no_evaluable": cnt["no_evaluable"],
              "evaluables": total_eval,
              "pendientes_de_consenso": len(pendientes),
              "cuota_por_estrato": CUOTA_POR_ESTRATO, "cuota_total": CUOTA_TOTAL,
              "cumple_total": total_eval >= CUOTA_TOTAL,
              "cumple_estratos": {c: cnt[c] >= CUOTA_POR_ESTRATO
                                  for c in ("ligera", "moderada", "severa")},
              "aplicar_fusion_moderada_severa": cnt["severa"] < CUOTA_POR_ESTRATO}
    with open(os.path.join(dataset, "conteo_estratos_real.json"), "w",
              encoding="utf-8") as fh:
        json.dump(conteo, fh, indent=2, ensure_ascii=False)

    if verbose:
        print("=" * 62)
        print("CONSENSO Y GT REAL ESTRATIFICADO")
        print("=" * 62)
        print("  doble anotacion (A y B) : %d" % len(comunes))
        print("  anotador unico (solo A) : %d" % len(solo_a))
        print("  con etiqueta final      : %d (%d por acuerdo, %d por consenso, %d anotador unico)"
              % (len(finales),
                 sum(1 for f in finales.values() if f["origen"] == "acuerdo"),
                 sum(1 for f in finales.values() if f["origen"] == "consenso"),
                 sum(1 for f in finales.values() if f["origen"] == "anotador_unico")))
        print("  pendientes de consenso  : %d" % len(pendientes))
        for i in pendientes[:10]:
            print("      %-22s %-12s vs %-12s" % (i, A[i].get("estrato"), B[i].get("estrato")))
        if len(pendientes) > 10:
            print("      ... y %d mas" % (len(pendientes) - 10))
        if invalidas:
            print("  consensos invalidos     : %d  (valores: %s)"
                  % (len(invalidas), ", ".join(sorted({v for _, v in invalidas}))))
        if no_hallados:
            print("  AVISO: %d ids anotados no estan en el split de prueba" % no_hallados)
        print("\nConteo por estrato (publicable):")
        for c in ESTRATOS:
            marca = ""
            if c != "sin" and cnt[c] < CUOTA_POR_ESTRATO:
                marca = "  <-- por debajo de %d" % CUOTA_POR_ESTRATO
            print("  %-12s %4d%s" % (c, cnt[c], marca))
        print("  %-12s %4d" % ("no_evaluable", cnt["no_evaluable"]))
        print("  %-12s %4d  (cuota %d)" % ("evaluables", total_eval, CUOTA_TOTAL))
        if conteo["aplicar_fusion_moderada_severa"]:
            print("\n  Severa < %d: si el lote esta COMPLETO, aplicar la regla de"
                  % CUOTA_POR_ESTRATO)
            print("  fusion (evaluar con --fusion: moderada+severa -> 'ocluida',")
            print("  n=%d) y declararlo como limitacion." % (cnt["moderada"] + cnt["severa"]))
        else:
            print("\n  Cuotas por estrato satisfechas; no procede fusionar.")
        print("\n  -> %s" % salida_csv)
        print("  -> %s" % ruta_gt)
        print("  -> %s" % os.path.join(dataset, "conteo_estratos_real.json"))
    return finales, conteo, imagenes


def selftest():
    import shutil
    import tempfile
    from PIL import Image
    tmp = tempfile.mkdtemp(prefix="consenso_test_")
    ds = os.path.join(tmp, "dataset")
    os.makedirs(os.path.join(ds, "images", "test"))
    os.makedirs(os.path.join(ds, "labels", "test"))
    Image.new("RGB", (200, 100)).save(os.path.join(ds, "images", "test", "x.jpg"))
    with open(os.path.join(ds, "labels", "test", "x.txt"), "w") as f:
        f.write("0 0.25 0.35 0.2 0.5\n0 0.8 0.8 0.1 0.2\n0 0.5 0.5 0.1 0.1\n0 0.1 0.1 0.1 0.1\n")
    with open(os.path.join(tmp, "imageclasslist.txt"), "w") as f:
        f.write("x.jpg 11 5 1 3\n")
    cab = "id_instancia,imagen,x,y,w,h,estrato,truncado,no_evaluable,segundos\n"
    with open(os.path.join(tmp, "a.csv"), "w") as f:
        f.write(cab + "x#0,test/x.jpg,30,10,40,50,severa,1,0,3\n"
                "x#1,test/x.jpg,0,0,1,1,ligera,0,0,3\n"
                "x#2,test/x.jpg,0,0,1,1,sin,0,0,3\n")
    with open(os.path.join(tmp, "b.csv"), "w") as f:
        f.write(cab + "x#0,test/x.jpg,30,10,40,50,severa,0,0,3\n"
                "x#1,test/x.jpg,0,0,1,1,moderada,0,0,3\n"
                "x#2,test/x.jpg,0,0,1,1,no_evaluable,0,1,3\n")
    with open(os.path.join(tmp, "disc.csv"), "w") as f:
        f.write("id_instancia,imagen,estrato_A,estrato_B,consenso\n"
                "x#1,test/x.jpg,ligera,moderada,moderada\n"
                "x#2,test/x.jpg,sin,no_evaluable,\n")
    print("--- construyendo consenso sobre datos sinteticos ---\n")
    fin, conteo, imgs = construir([os.path.join(tmp, "a.csv")],
                                  [os.path.join(tmp, "b.csv")],
                                  os.path.join(tmp, "disc.csv"), ds, tmp,
                                  os.path.join(tmp, "consenso.csv"))
    print("\n" + "=" * 58 + "\nVERIFICACION\n" + "=" * 58)
    fallos = []

    def comp(desc, obt, esp):
        ok = obt == esp
        print("  [%s] %-46s %s" % ("ok" if ok else "FALLA", desc, obt))
        if not ok:
            fallos.append(desc)

    comp("acuerdo directo conservado", fin["x#0"]["estrato"], "severa")
    comp("truncado = OR de ambos", fin["x#0"]["truncado"], 1)
    comp("discrepancia resuelta por consenso", fin["x#1"]["estrato"], "moderada")
    comp("discrepancia pendiente excluida", "x#2" in fin, False)
    comp("pendientes contadas", conteo["pendientes_de_consenso"], 1)
    inst = {o["id"]: o for o in imgs["test/x.jpg"]["instancias"]}
    comp("GT: estrato asignado", inst["x#0"]["estrato"], "severa")
    comp("GT: instancia no anotada -> sin_anotar", inst["x#3"]["estrato"], "sin_anotar")
    comp("GT: pendiente -> sin_anotar", inst["x#2"]["estrato"], "sin_anotar")
    comp("GT: luz desde imageclasslist", imgs["test/x.jpg"]["luz"], "Weak")
    comp("fusion recomendada (severa<50)", conteo["aplicar_fusion_moderada_severa"], True)
    with open(os.path.join(tmp, "a2.csv"), "w") as f:
        f.write(cab + "x#0,test/x.jpg,30,10,40,50,severa,1,0,3\nx#3,test/x.jpg,0,0,1,1,ligera,0,0,3\n")
    fin2, c2, _ = construir([os.path.join(tmp, "a2.csv")], [], None, ds, tmp, os.path.join(tmp, "c2.csv"), verbose=False)
    comp("anotador unico: todas las instancias de A", (len(fin2), fin2["x#3"]["origen"]), (2, "anotador_unico"))
    comp("anotador unico: conteo", (c2["n_doble_anotacion"], c2["n_anotador_unico"]), (0, 2))
    shutil.rmtree(tmp)
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO: 12/12 comprobaciones.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - consenso y GT real")
    ap.add_argument("--a", nargs="+", help="CSV(s) del anotador A")
    ap.add_argument("--b", nargs="*", default=[], help="CSV(s) del anotador B (opcional: sin B, anotador unico)")
    ap.add_argument("--discrepancias", default="discrepancias.csv")
    ap.add_argument("--dataset", default="./dataset")
    ap.add_argument("--raiz", default=".", help="raiz con imageclasslist.txt")
    ap.add_argument("--salida", default="consenso.csv")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if not args.a:
        ap.error("se requiere --a (o --selftest)")
    construir(args.a, args.b, args.discrepancias, args.dataset, args.raiz,
              args.salida)


if __name__ == "__main__":
    main()
