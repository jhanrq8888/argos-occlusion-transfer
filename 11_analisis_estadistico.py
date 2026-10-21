#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Paso 9: analisis estadistico (Seccion 2.6) y contraste de
hipotesis y criterios de exito (Seccion 1.9).

Entradas: resultados/det/*.json (detecciones cacheadas por 09), los GT de
cada conjunto y resultados/eval/*.json (variante y semilla de cada
corrida); opcionalmente resultados/resumen_costo.csv (FPS, de 10).

Analisis:
  1. Descriptivo: media y desviacion entre semillas del AP50 y AP por
     variante x conjunto x estrato (variabilidad de replicacion).
  2. Estimacion de efectos con IC 95 % por BOOTSTRAP SOBRE IMAGENES
     (percentil, B >= 1000, remuestreo pareado: las mismas imagenes para
     todas las corridas): dAP50 = V - V1 para V2, V3, V4, promediando las
     semillas dentro de cada replica. Es el ancla de los criterios (b).
  3. Contraste de interaccion (V4 - V3) - (V2 - V1), mismo bootstrap.
  4. Tamano de efecto entre semillas: d de Cohen con correccion de Hedges.
  5. ANOVA 2x2 sobre las 12 corridas: SOLO EXPLORATORIO (n=3 por celda).
  6. Criterios de exito (a)(b)(c) y lectura de H1, H2 y H3.
  7. Figuras: AP50 vs nivel de oclusion por variante y tipo de parche.

Implementacion del bootstrap: las detecciones de cada corrida se ordenan
una sola vez por score; cada replica solo cambia el PESO de cada imagen
(cuantas veces fue muestreada), asi que el AP se obtiene con sumas
acumuladas ponderadas sin reordenar. El autotest comprueba que coincide
con el remuestreo por concatenacion.

Salida: resultados/analisis/ (CSV, JSON, figuras y INFORME.md).

Uso:
    python 11_analisis_estadistico.py
    python 11_analisis_estadistico.py --replicas 2000 --semilla 0
    python 11_analisis_estadistico.py --selftest
"""

import argparse
import csv
import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argos_lib import ESTRATOS                                        # noqa: E402
from argos_lib.ap import REC_THRS, ap_conjunto, emparejar_conjunto    # noqa: E402
from argos_lib.gt import cargar_detecciones, cargar_gt                # noqa: E402

RAIZ = os.path.dirname(os.path.abspath(__file__))
VARIANTES = ["V1", "V2", "V3", "V4"]
UMBRAL_PP = 2.0            # criterio (a): +2 puntos porcentuales
FPS_MIN = 30.0             # criterio (c)
FPS_REL_MIN = 0.90         # H1: >= 90 % del baseline
CUOTA = 50


# --- Bootstrap ponderado ----------------------------------------------------
class APBootstrap:
    """Estructura precalculada de una corrida sobre un conjunto/estrato para
    AP@0.5 (umbral 0 de emparejar_imagen) con remuestreo por pesos."""

    def __init__(self, emparejados, t=0):
        sc = np.concatenate([e["scores"][t] for e in emparejados]) if emparejados else np.zeros(0)
        tp = np.concatenate([e["tp"][t] for e in emparejados]) if emparejados else np.zeros(0, bool)
        idx = np.concatenate([np.full(len(e["scores"][t]), i) for i, e in enumerate(emparejados)]) \
            if emparejados else np.zeros(0, int)
        orden = np.argsort(-sc, kind="mergesort")
        self.tp = tp[orden].astype(float)
        self.idx = idx[orden].astype(int)
        self.n_gt_img = np.asarray([e["n_gt"] for e in emparejados], dtype=float)
        self.n_img = len(emparejados)

    def ap(self, pesos=None):
        if pesos is None:
            pesos = np.ones(self.n_img)
        n_gt = float(np.dot(pesos, self.n_gt_img))
        if n_gt == 0:
            return float("nan")
        if len(self.tp) == 0:
            return 0.0
        w = pesos[self.idx]
        tpc = np.cumsum(self.tp * w)
        fpc = np.cumsum((1.0 - self.tp) * w)
        rec = tpc / n_gt
        prec = tpc / np.maximum(tpc + fpc, np.finfo(float).eps)
        prec = np.maximum.accumulate(prec[::-1])[::-1]          # envolvente
        k = np.searchsorted(rec, REC_THRS, side="left")
        q = np.zeros(len(REC_THRS))
        v = k < len(prec)
        q[v] = prec[k[v]]
        return float(q.mean())


def bootstrap_efectos(estructuras, variantes_por_corrida, n_img, B, semilla):
    """estructuras: {corrida: APBootstrap}. Devuelve dict con AP por variante
    (media de semillas) y contrastes, cada uno como array de B replicas."""
    rnd = np.random.RandomState(semilla)
    por_var = defaultdict(list)
    for c, v in variantes_por_corrida.items():
        if c in estructuras:
            por_var[v].append(c)
    salida = {v: np.zeros(B) for v in por_var}
    for b in range(B):
        muestra = rnd.randint(0, n_img, n_img)
        pesos = np.bincount(muestra, minlength=n_img).astype(float)
        for v, cs in por_var.items():
            salida[v][b] = np.mean([estructuras[c].ap(pesos) for c in cs])
    return salida


def ic(x, alfa=0.05):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return (float("nan"), float("nan"))
    return (float(np.percentile(x, 100 * alfa / 2)), float(np.percentile(x, 100 * (1 - alfa / 2))))


def hedges_g(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        return float("nan")
    s = np.sqrt(((n1 - 1) * a.var(ddof=1) + (n2 - 1) * b.var(ddof=1)) / (n1 + n2 - 2))
    if s == 0:
        return float("nan")
    J = 1.0 - 3.0 / (4.0 * (n1 + n2) - 9.0)
    return float(J * (a.mean() - b.mean()) / s)


def anova_2x2(valores):
    """valores: {variante: [ap por semilla]}. Factores: A=CBAM (V2,V4),
    B=oclusion (V3,V4). Devuelve F y p de A, B y AxB (exploratorio)."""
    filas = []
    for v, xs in valores.items():
        a = 1 if v in ("V2", "V4") else 0
        bb = 1 if v in ("V3", "V4") else 0
        for x in xs:
            filas.append((a, bb, float(x)))
    if len(filas) < 8:
        return {}
    A = np.array([f[0] for f in filas]); Bf = np.array([f[1] for f in filas])
    y = np.array([f[2] for f in filas])
    gm = y.mean()
    celdas = {(a, b): y[(A == a) & (Bf == b)] for a in (0, 1) for b in (0, 1)}
    if any(len(c) < 2 for c in celdas.values()):
        return {}
    n = min(len(c) for c in celdas.values())
    mA = {a: y[A == a].mean() for a in (0, 1)}
    mB = {b: y[Bf == b].mean() for b in (0, 1)}
    ssA = sum(len(y[A == a]) * (mA[a] - gm) ** 2 for a in (0, 1))
    ssB = sum(len(y[Bf == b]) * (mB[b] - gm) ** 2 for b in (0, 1))
    ssCel = sum(len(c) * (c.mean() - gm) ** 2 for c in celdas.values())
    ssAB = ssCel - ssA - ssB
    ssE = sum(((c - c.mean()) ** 2).sum() for c in celdas.values())
    dfE = len(y) - 4
    if dfE <= 0 or ssE <= 0:
        return {}
    msE = ssE / dfE
    try:
        from scipy.stats import f as fdist
        p = lambda F: float(fdist.sf(F, 1, dfE))          # noqa: E731
    except ImportError:
        p = lambda F: float("nan")                        # noqa: E731
    out = {}
    for nombre, ss in (("CBAM", ssA), ("oclusion", ssB), ("interaccion", ssAB)):
        F = ss / msE
        out[nombre] = {"F": float(F), "p": p(F), "df": (1, dfE)}
    out["n_por_celda"] = int(n)
    return out


# --- Carga -------------------------------------------------------------------
def cargar_corridas(dir_res, excluir_prefijo=None, solo_prefijo=None):
    """excluir_prefijo: descarta corridas cuyo nombre empiece asi (p. ej.
    'yolo26s_' para analizar solo YOLOv11s sin mezclar arquitecturas)."""
    corr = {}
    for f in glob.glob(os.path.join(dir_res, "eval", "*.json")):
        with open(f, encoding="utf-8") as fh:
            ev = json.load(fh)
        if solo_prefijo and not ev.get("corrida", "").startswith(solo_prefijo):
            continue
        if excluir_prefijo and ev.get("corrida", "").startswith(excluir_prefijo):
            continue
        if ev.get("variante"):
            corr[ev["corrida"]] = {"variante": ev["variante"], "semilla": ev.get("semilla"),
                                   "conjuntos": {k: v["gt"] for k, v in ev["conjuntos"].items()}}
    return corr


def leer_costos(dir_res):
    ruta = os.path.join(dir_res, "resumen_costo.csv")
    fps = defaultdict(list)
    if os.path.exists(ruta):
        with open(ruta, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                v = r.get("variante") or r["corrida"]
                try:
                    fps[v].append(float(r["ort_fps_forward"] or r["pt_fps_forward"]))
                except ValueError:
                    pass
    return {v: float(np.mean(x)) for v, x in fps.items() if x}


def estratos_de(gt):
    pres = {o["estrato"] for m in gt["imagenes"].values() for o in m["instancias"]}
    return [e for e in ESTRATOS if e in pres] + sorted(pres - set(ESTRATOS) - {"sin_anotar", "ignorar"})


# --- Analisis principal -------------------------------------------------------
def analizar(dir_res, B, semilla, fusion, verbose=True, excluir_prefijo=None, subdir="analisis", solo_prefijo=None):
    corr = cargar_corridas(dir_res, excluir_prefijo, solo_prefijo)
    if not corr:
        sys.exit("No hay evaluaciones con variante/semilla en %s/eval. Ejecutar 09 --corridas." % dir_res)
    dir_out = os.path.join(dir_res, subdir)
    os.makedirs(os.path.join(dir_out, "figuras"), exist_ok=True)
    var_de = {c: d["variante"] for c, d in corr.items()}
    conjuntos = {}
    for d in corr.values():
        conjuntos.update(d["conjuntos"])

    descriptivo, boots, efectos, anovas = [], [], [], []
    ap_por = {}            # (conjunto, estrato, variante) -> [AP50 por semilla]
    ic_por = {}            # (conjunto, estrato, contraste) -> (delta, lo, hi)
    for conj, ruta_gt in sorted(conjuntos.items()):
        gt = cargar_gt(ruta_gt)
        n_img = len(gt["imagenes"])
        estr = ["global"] + estratos_de(gt)
        if fusion and "moderada" in estr and "severa" in estr:
            estr.append("ocluida")
        dets = {}
        for c in corr:
            ruta = os.path.join(dir_res, "det", "%s__%s.json" % (c, conj))
            if os.path.exists(ruta):
                dets[c] = cargar_detecciones(ruta)["detecciones"]
        if not dets:
            continue
        for e in estr:
            imgs = gt["imagenes"]
            if e == "ocluida":
                imgs = {k: {**m, "instancias": [{**o, "estrato": "ocluida" if o["estrato"] in ("moderada", "severa")
                                                  else o["estrato"]} for o in m["instancias"]]}
                        for k, m in imgs.items()}
            estructuras, ap_full = {}, {}
            for c, d in dets.items():
                emp, _ = emparejar_conjunto(imgs, d, estrato=None if e == "global" else e)
                estructuras[c] = APBootstrap(emp)
                ap_full[c] = ap_conjunto(emp)
            n_gt = next(iter(ap_full.values()))["n_gt"]
            # 1. descriptivo
            for v in sorted({var_de[c] for c in dets}):
                cs = [c for c in dets if var_de[c] == v]
                a50 = [ap_full[c]["AP50"] for c in cs]
                a = [ap_full[c]["AP"] for c in cs]
                ap_por[(conj, e, v)] = a50
                descriptivo.append({"conjunto": conj, "estrato": e, "variante": v, "n_semillas": len(cs),
                                    "n_gt": n_gt, "AP50_media": np.mean(a50), "AP50_sd": np.std(a50, ddof=1) if len(a50) > 1 else 0.0,
                                    "AP_media": np.mean(a), "AP_sd": np.std(a, ddof=1) if len(a) > 1 else 0.0})
            # 2-3. bootstrap pareado
            bs = bootstrap_efectos(estructuras, var_de, n_img, B, semilla)
            if "V1" in bs:
                for v in ("V2", "V3", "V4"):
                    if v in bs:
                        d = bs[v] - bs["V1"]
                        lo, hi = ic(d)
                        delta = float(np.mean(ap_por.get((conj, e, v), [np.nan])) - np.mean(ap_por[(conj, e, "V1")]))
                        ic_por[(conj, e, v)] = (delta, lo, hi)
                        boots.append({"conjunto": conj, "estrato": e, "contraste": "%s-V1" % v, "n_gt": n_gt,
                                      "delta_AP50_pp": 100 * delta, "IC95_lo_pp": 100 * lo, "IC95_hi_pp": 100 * hi,
                                      "excluye_cero": (lo > 0 or hi < 0), "replicas": B})
                if all(v in bs for v in VARIANTES):
                    inter = (bs["V4"] - bs["V3"]) - (bs["V2"] - bs["V1"])
                    lo, hi = ic(inter)
                    m = {v: np.mean(ap_por[(conj, e, v)]) for v in VARIANTES}
                    delta = (m["V4"] - m["V3"]) - (m["V2"] - m["V1"])
                    ic_por[(conj, e, "interaccion")] = (delta, lo, hi)
                    boots.append({"conjunto": conj, "estrato": e, "contraste": "(V4-V3)-(V2-V1)", "n_gt": n_gt,
                                  "delta_AP50_pp": 100 * delta, "IC95_lo_pp": 100 * lo, "IC95_hi_pp": 100 * hi,
                                  "excluye_cero": (lo > 0 or hi < 0), "replicas": B})
            # 4. Hedges g entre semillas
            for v in ("V2", "V3", "V4"):
                if (conj, e, v) in ap_por and (conj, e, "V1") in ap_por:
                    efectos.append({"conjunto": conj, "estrato": e, "contraste": "%s-V1" % v,
                                    "hedges_g": hedges_g(ap_por[(conj, e, v)], ap_por[(conj, e, "V1")])})
            # 5. ANOVA exploratorio
            vals = {v: ap_por[(conj, e, v)] for v in VARIANTES if (conj, e, v) in ap_por}
            an = anova_2x2(vals)
            if an:
                for k in ("CBAM", "oclusion", "interaccion"):
                    anovas.append({"conjunto": conj, "estrato": e, "factor": k, "F": an[k]["F"],
                                   "p": an[k]["p"], "n_por_celda": an["n_por_celda"],
                                   "nota": "EXPLORATORIO (n=3 por celda): sin valor confirmatorio"})
        if verbose:
            print("  %-18s %d imagenes, estratos %s" % (conj, n_img, ", ".join(estr)))

    escribir_csv(os.path.join(dir_out, "descriptivo.csv"), descriptivo)
    escribir_csv(os.path.join(dir_out, "bootstrap.csv"), boots)
    escribir_csv(os.path.join(dir_out, "efectos_hedges.csv"), efectos)
    escribir_csv(os.path.join(dir_out, "anova_exploratorio.csv"), anovas)

    # 6. Criterios de exito e hipotesis
    fps = leer_costos(dir_res)
    crit = criterios(ap_por, ic_por, fps, fusion)
    with open(os.path.join(dir_out, "criterios.json"), "w", encoding="utf-8") as fh:
        json.dump(crit, fh, indent=2, ensure_ascii=False)
    # 7. Figuras e informe
    figuras(descriptivo, dir_out)
    informe(dir_out, descriptivo, boots, efectos, anovas, crit, corr, B)
    if verbose:
        print("\nSalida en %s" % dir_out)
        print(json.dumps(crit["resumen"], indent=1, ensure_ascii=False))
    return descriptivo, boots, crit


def criterios(ap_por, ic_por, fps, fusion):
    """Aplica (a)(b)(c) sobre el subconjunto real (test_real) y, como
    apoyo, sobre los sinteticos; lee H1, H2 y H3."""
    out = {"umbral_pp": UMBRAL_PP, "fps_min": FPS_MIN, "fps_rel_min": FPS_REL_MIN,
           "fps_medidos": fps, "por_conjunto": {}, "resumen": {}}
    for (conj, e, v), (delta, lo, hi) in ic_por.items():
        if v != "V4":
            continue
        n_gt = None
        out["por_conjunto"].setdefault(conj, {})[e] = {
            "delta_V4_V1_pp": round(100 * delta, 2), "IC95_pp": [round(100 * lo, 2), round(100 * hi, 2)],
            "a_delta_ge_2pp": bool(100 * delta >= UMBRAL_PP), "b_ic_excluye_cero": bool(lo > 0)}
    # H1: V4 > V1 en moderada y severa (o en 'ocluida' si hubo fusion) de la fuente real
    # propia: el proxy objetivo inter-persona (test_proxy) si existe; si no, test_real
    # (anotacion manual, no fiable desde 2026-09-13; ver CAMBIOS_PROTOCOLO.md).
    propia = "test_proxy" if "test_proxy" in out["por_conjunto"] else "test_real"
    real = out["por_conjunto"].get(propia, {})
    estr_h1 = ["ocluida"] if (fusion and "ocluida" in real) else ["moderada", "severa"]
    h1_ap = all(real.get(e, {}).get("a_delta_ge_2pp") and real.get(e, {}).get("b_ic_excluye_cero")
                for e in estr_h1) if all(e in real for e in estr_h1) else None
    fps_v1, fps_v4 = fps.get("V1"), fps.get("V4")
    c_fps = (fps_v4 is not None and fps_v4 >= FPS_MIN)
    h1_fps = (fps_v1 and fps_v4 and fps_v4 >= FPS_REL_MIN * fps_v1) if (fps_v1 and fps_v4) else None
    # H2: aporte VI2 (V3-V1) > aporte VI1 (V2-V1) en los estratos ocluidos del real.
    h2 = None
    if all(((propia, e, v) in ap_por) for e in estr_h1 for v in ("V1", "V2", "V3")):
        d3 = np.mean([np.mean(ap_por[(propia, e, "V3")]) - np.mean(ap_por[(propia, e, "V1")]) for e in estr_h1])
        d2 = np.mean([np.mean(ap_por[(propia, e, "V2")]) - np.mean(ap_por[(propia, e, "V1")]) for e in estr_h1])
        h2 = {"fuente": propia, "aporte_oclusion_pp": round(100 * d3, 2), "aporte_cbam_pp": round(100 * d2, 2), "sostenida": bool(d3 > d2)}
    # H3: direccion del efecto (V4-V1 en estratos ocluidos) en las TRES fuentes reales
    # pre-registradas (PROTOCOLO.md s.7): propia, NightOwls, CityPersons. La fuente propia
    # es el proxy objetivo inter-persona (test_proxy) si existe; si no, test_real (anotacion
    # manual, no fiable desde 2026-09-13). Para CityPersons se usa la convencion oficial.
    # Los demas conjuntos reales se reportan como informativos, no cuentan para H3.
    def _dir(conj):
        d = out["por_conjunto"].get(conj)
        if not d:
            return None
        ocl = [d[e]["delta_V4_V1_pp"] for e in ("moderada", "severa", "ocluida", "heavy") if e in d]
        if not ocl:
            return None
        return {"delta_media_pp": round(float(np.mean(ocl)), 2), "direccion": "+" if np.mean(ocl) > 0 else "-"}
    fuentes, informativas = {}, {}
    for nombre, cands in (("propia", (propia,)), ("nightowls", ("nightowls",)),
                          ("citypersons", ("citypersons_convencion", "citypersons"))):
        for c in cands:
            r = _dir(c)
            if r:
                r["conjunto"] = c
                fuentes[nombre] = r
                break
    for conj in out["por_conjunto"]:
        if conj.startswith(("opaco_", "recorte_", "textura_", "silueta_")):
            continue
        if conj not in {f["conjunto"] for f in fuentes.values()}:
            r = _dir(conj)
            if r:
                informativas[conj] = r
    sint = [out["por_conjunto"][c][e]["delta_V4_V1_pp"] for c in out["por_conjunto"] if c.startswith(("opaco_", "recorte_", "textura_", "silueta_"))
            for e in ("moderada", "severa") if e in out["por_conjunto"][c]]
    dir_sint = ("+" if np.mean(sint) > 0 else "-") if sint else None
    h3 = None
    if fuentes and dir_sint:
        coinciden = sum(1 for f in fuentes.values() if f["direccion"] == dir_sint)
        n_f = len(fuentes)
        if n_f < 2:
            lectura = "insuficiente (solo %d fuente)" % n_f
        elif coinciden >= 2:
            lectura = "sostenida (direccion conservada en >=2 de %d fuentes)" % n_f
        elif coinciden == 0:
            lectura = "no sostenida (las %d fuentes coinciden en NO conservar la direccion sintetica)" % n_f
        else:
            lectura = "no concluyente (las fuentes discrepan entre si: %d de %d conservan la direccion)" % (coinciden, n_f)
        h3 = {"direccion_sintetica": dir_sint, "fuentes": fuentes, "informativas": informativas,
              "coinciden": coinciden, "de": n_f, "lectura": lectura}
    out["resumen"] = {"fuente_real_propia": propia, "estratos_H1": estr_h1, "H1_AP_criterios_a_b": h1_ap, "criterio_c_fps_ge_30": c_fps,
                      "H1_fps_ge_90pct_baseline": h1_fps, "H2": h2, "H3": h3,
                      "nota": "Inferencia basada en semillas: indicativa (n=3). El IC bootstrap sobre "
                              "imagenes es el ancla del criterio (b)."}
    return out


def escribir_csv(ruta, filas):
    if not filas:
        open(ruta, "w").close()
        return
    with open(ruta, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        for f in filas:
            w.writerow({k: (round(v, 5) if isinstance(v, float) else v) for k, v in f.items()})


def figuras(descriptivo, dir_out):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    niveles = ["sin", "ligera", "moderada", "severa"]
    tabla = defaultdict(dict)
    for f in descriptivo:
        tabla[(f["conjunto"], f["variante"])][f["estrato"]] = (f["AP50_media"], f["AP50_sd"])
    # Curvas AP50 vs nivel por tipo de parche: se usa el global del test_real
    # como nivel 'sin' y el estrato nominal de cada conjunto sintetico.
    for tipo in ("textura", "recorte", "opaco", "silueta"):
        fig, ax = plt.subplots(figsize=(6, 4))
        hay = False
        for v in VARIANTES:
            xs, ys, es = [], [], []
            if ("test_real", v) in tabla and "global" in tabla[("test_real", v)]:
                m, s = tabla[("test_real", v)]["global"]; xs.append(0); ys.append(m); es.append(s)
            for i, e in enumerate(niveles[1:], 1):
                k = ("%s_%s" % (tipo, e), v)
                if k in tabla and e in tabla[k]:
                    m, s = tabla[k][e]; xs.append(i); ys.append(m); es.append(s)
            if ys:
                hay = True
                ax.errorbar(xs, ys, yerr=es, marker="o", capsize=3, label=v)
        if hay:
            ax.set_xticks(range(4)); ax.set_xticklabels(niveles)
            ax.set_ylabel("AP@0.5 (person)"); ax.set_xlabel("nivel de oclusion sintetica (%s)" % tipo)
            ax.set_ylim(0, 1); ax.grid(alpha=.3); ax.legend()
            fig.tight_layout(); fig.savefig(os.path.join(dir_out, "figuras", "ap50_vs_oclusion_%s.png" % tipo), dpi=150)
        plt.close(fig)
    # Real anotado.
    fig, ax = plt.subplots(figsize=(6, 4))
    hay = False
    for v in VARIANTES:
        k = ("test_real", v)
        if k in tabla:
            xs = [i for i, e in enumerate(niveles) if e in tabla[k]]
            if xs:
                hay = True
                ax.errorbar(xs, [tabla[k][niveles[i]][0] for i in xs], yerr=[tabla[k][niveles[i]][1] for i in xs],
                            marker="s", capsize=3, label=v)
    if hay:
        ax.set_xticks(range(4)); ax.set_xticklabels(niveles); ax.set_ylim(0, 1)
        ax.set_ylabel("AP@0.5 (person)"); ax.set_xlabel("estrato de oclusion REAL anotada"); ax.grid(alpha=.3); ax.legend()
        fig.tight_layout(); fig.savefig(os.path.join(dir_out, "figuras", "ap50_vs_oclusion_real.png"), dpi=150)
    plt.close(fig)


def informe(dir_out, desc, boots, efectos, anovas, crit, corr, B):
    L = ["# ARGOS-11 - Informe de analisis estadistico", "",
         "Corridas analizadas: %d (%s)" % (len(corr), ", ".join(sorted(corr))),
         "Bootstrap sobre imagenes: B = %d, percentil, pareado entre corridas." % B, "",
         "## 1. Descriptivo (media +- sd entre semillas, AP@0.5)", "",
         "| conjunto | estrato | n_gt | " + " | ".join(VARIANTES) + " |", "|---|---|---|" + "---|" * len(VARIANTES)]
    t = defaultdict(dict)
    for f in desc:
        t[(f["conjunto"], f["estrato"], f["n_gt"])][f["variante"]] = "%.3f +- %.3f" % (f["AP50_media"], f["AP50_sd"])
    for (c, e, n), d in sorted(t.items()):
        L.append("| %s | %s | %d | %s |" % (c, e, n, " | ".join(d.get(v, "-") for v in VARIANTES)))
    L += ["", "## 2. Efectos con IC 95 % bootstrap (puntos porcentuales de AP@0.5)", "",
          "| conjunto | estrato | contraste | delta | IC95 | excluye 0 |", "|---|---|---|---|---|---|"]
    for b in boots:
        L.append("| %s | %s | %s | %+.2f | [%+.2f, %+.2f] | %s |" % (b["conjunto"], b["estrato"], b["contraste"],
                 b["delta_AP50_pp"], b["IC95_lo_pp"], b["IC95_hi_pp"], "si" if b["excluye_cero"] else "no"))
    L += ["", "## 3. Tamano de efecto entre semillas (Hedges g; indicativo, n=3)", "",
          "| conjunto | estrato | contraste | g |", "|---|---|---|---|"]
    for f in efectos:
        L.append("| %s | %s | %s | %s |" % (f["conjunto"], f["estrato"], f["contraste"],
                 "%.2f" % f["hedges_g"] if not np.isnan(f["hedges_g"]) else "nd"))
    L += ["", "## 4. ANOVA 2x2 (EXPLORATORIO, sin valor confirmatorio)", "",
          "| conjunto | estrato | factor | F | p |", "|---|---|---|---|---|"]
    for a in anovas:
        L.append("| %s | %s | %s | %.2f | %s |" % (a["conjunto"], a["estrato"], a["factor"], a["F"],
                 "%.3f" % a["p"] if not np.isnan(a["p"]) else "nd"))
    L += ["", "## 5. Criterios de exito e hipotesis", "", "```", json.dumps(crit["resumen"], indent=1, ensure_ascii=False), "```",
          "", "Confirmatorio: marginales por estrato agregando iluminacion. El cruce luz x estrato esta en",
          "resultados/resumen_ap.csv y es exploratorio. Figuras en figuras/."]
    with open(os.path.join(dir_out, "INFORME.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


# --- Autotest ---------------------------------------------------------------
def selftest():
    from argos_lib.ap import emparejar_imagen
    rnd = np.random.RandomState(5)
    fallos = []

    def comp(desc, obt, esp, tol=None):
        ok = (abs(obt - esp) <= tol) if tol is not None else (obt == esp)
        print("  [%s] %-52s %s" % ("ok" if ok else "FALLA", desc, round(obt, 5) if isinstance(obt, float) else obt))
        if not ok:
            fallos.append(desc)

    # Conjunto aleatorio con ignore; bootstrap ponderado == concatenacion.
    emp = []
    for _ in range(30):
        gts, ign, dets = [], [], []
        for _ in range(rnd.randint(0, 5)):
            x, y = rnd.uniform(0, 900, 2); w, h = rnd.uniform(10, 80, 2)
            gts.append([x, y, x + w, y + h]); ign.append(bool(rnd.rand() < 0.2))
            if rnd.rand() < 0.75:
                j = rnd.uniform(-6, 6, 4)
                dets.append([gts[-1][0] + j[0], gts[-1][1] + j[1], gts[-1][2] + j[2], gts[-1][3] + j[3], float(rnd.rand())])
        for _ in range(rnd.randint(0, 3)):
            x, y = rnd.uniform(0, 900, 2); w, h = rnd.uniform(10, 80, 2)
            dets.append([x, y, x + w, y + h, float(rnd.rand())])
        emp.append(emparejar_imagen(dets, gts, ign))
    est = APBootstrap(emp)
    comp("AP ponderado (pesos 1) == AP de referencia", est.ap(), ap_conjunto(emp)["AP50"], 1e-12)
    muestra = rnd.randint(0, 30, 30)
    pesos = np.bincount(muestra, minlength=30).astype(float)
    comp("AP ponderado == AP por concatenacion (replica)", est.ap(pesos),
         ap_conjunto(emp, indices=list(muestra))["AP50"], 1e-12)
    # Hedges g y ANOVA.
    comp("Hedges g de muestras identicas = 0", hedges_g([1, 2, 3], [1, 2, 3]), 0.0, 1e-12)
    comp("Hedges g positivo si a > b", hedges_g([5, 6, 7], [1, 2, 3]) > 2, True)
    an = anova_2x2({"V1": [1, 1.1, .9], "V2": [1, 1.1, .9], "V3": [3, 3.1, 2.9], "V4": [3, 3.1, 2.9]})
    comp("ANOVA: efecto principal oclusion grande", an["oclusion"]["F"] > 100, True)
    comp("ANOVA: sin efecto CBAM", an["CBAM"]["F"] < 1e-6, True)
    comp("ANOVA: p de oclusion < 0.001", an["oclusion"]["p"] < 1e-3, True)
    # Bootstrap de efectos: V2 identica a V1 -> IC contiene 0; V3 mejor -> IC > 0.
    estructuras = {"a_s0": est, "a_s1": est, "b_s0": est}
    bs = bootstrap_efectos(estructuras, {"a_s0": "V1", "a_s1": "V1", "b_s0": "V2"}, 30, 200, 0)
    lo, hi = ic(bs["V2"] - bs["V1"])
    comp("bootstrap: variantes identicas -> delta 0", (lo, hi), (0.0, 0.0))
    comp("ic: percentiles correctos", ic(np.arange(1, 1001)), (25.975, 975.025))
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO: 9/9 comprobaciones.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - analisis estadistico")
    ap.add_argument("--resultados", default=os.path.join(RAIZ, "resultados"))
    ap.add_argument("--replicas", type=int, default=1000)
    ap.add_argument("--semilla", type=int, default=0)
    ap.add_argument("--fusion", action="store_true", help="anadir estrato 'ocluida' (moderada+severa)")
    ap.add_argument("--excluir-prefijo", help="descartar corridas con este prefijo (p. ej. yolo26s_)")
    ap.add_argument("--subdir", default="analisis", help="subcarpeta de salida dentro de --resultados")
    ap.add_argument("--solo-prefijo", help="analizar solo corridas con este prefijo (p. ej. yolo26s_)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    analizar(args.resultados, args.replicas, args.semilla, args.fusion,
             excluir_prefijo=args.excluir_prefijo, subdir=args.subdir, solo_prefijo=args.solo_prefijo)


if __name__ == "__main__":
    main()
