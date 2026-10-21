#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - H13 (PREREGISTRO_H13.md): realismo MEDIDO de cada familia de oclusor.

Todo dentro de CityPersons val (mismo dominio, mismas camaras), para que el clasificador no aprenda a
distinguir conjuntos de datos:
  real      400 personas con oclusion REAL heavy (visibilidad anotada 0,20-0,65, altura >= 50 px), semilla 0
  base      400 personas VISIBLES (bare, visibilidad >= 0,90, altura >= 50 px), semilla 0, sin tocar (referencia)
  familias  las mismas 400 personas visibles ocluidas por cada familia, con una cobertura objetivo tomada de
            la distribucion de oclusion real (1 - visibilidad de las heavy, semilla 1):
              parches     E1  (parche interior; textura de la imagen 0,4 / recorte de objeto 0,5 / opaco 0,1)
              siluetas    E2, E4, E8-S (banco siluetas_cp_val, anclado a un lado de la caja)
              geometria   E8-G (mismo banco, colocado sobre la region oculta de un patron real de CityPersons train)
              generativa  E7, E7b (SD1.5 inpainting, mismo generador y control de calidad que H9)
Recorte: caja ampliada 20 % por lado, cuadrado con relleno gris (114), 224 x 224.
Caracteristicas: DINOv2-base (CLS, primaria) y CLIP ViT-B/16 (imagen, secundaria).
Realismo = indistinguibilidad de la oclusion real: AUC de una regresion logistica (estandarizada, C = 1) que separa
'real' de cada familia, con validacion cruzada estratificada 5x5 (puntuacion fuera de muestra promediada);
IC por bootstrap de personas (1 000 replicas, semilla 0), pareado entre familias (mismas 400 personas base).
AUC 0,5 = indistinguible de la oclusion real; cuanto mayor, menos realista. Secundario: KID (nucleo polinomico).

Uso:
    python 31_realismo.py generar [--familias parches siluetas geometria generativa]
    python 31_realismo.py caracteristicas
    python 31_realismo.py analisis
    python 31_realismo.py --selftest
"""
import argparse
import json
import os
import sys
import time

import numpy as np

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
GT_CP = os.path.join(RAIZ, "dataset", "externos", "gt_citypersons_convencion.json")
SAL = os.path.join(RAIZ, "dataset", "realismo")
RES = os.path.join(RAIZ, "resultados_h13")
N = 400
FAMILIAS = ["parches", "siluetas", "geometria", "generativa"]
CONJUNTOS = ["real", "base"] + FAMILIAS
TAM = 224
AMPLIA = 0.20
COB = (0.35, 0.80)
B = 1000
UMBRAL_DIF = 0.0          # H13: diferencias de AUC con IC 95 % que excluya el cero


# ----------------------------------------------------------------------------- muestras
def muestras(gt):
    """Lista ordenada de (rel, idx, caja, vis) para real (heavy) y base (bare), con altura >= 50."""
    real, base = [], []
    for rel in sorted(gt["imagenes"]):
        for i, o in enumerate(gt["imagenes"][rel]["instancias"]):
            h = o["y2"] - o["y1"]
            if h < 50:
                continue
            t = (rel, i, (o["x1"], o["y1"], o["x2"], o["y2"]), o.get("vis", -1))
            if o["estrato"] == "heavy":
                real.append(t)
            elif o["estrato"] == "bare":
                base.append(t)
    r0 = np.random.RandomState(0)
    real = [real[k] for k in sorted(r0.choice(len(real), N, replace=False))]
    base = [base[k] for k in sorted(r0.choice(len(base), N, replace=False))]
    r1 = np.random.RandomState(1)
    ocl = np.clip(1 - np.array([v for *_, v in real]), *COB)
    objetivo = [float(ocl[k]) for k in r1.randint(0, N, N)]
    return real, base, objetivo


def recorte(im, caja):
    import cv2
    H, W = im.shape[:2]
    x1, y1, x2, y2 = caja
    w, h = x2 - x1, y2 - y1
    a, b = int(max(0, x1 - AMPLIA * w)), int(max(0, y1 - AMPLIA * h))
    c, d = int(min(W, x2 + AMPLIA * w)), int(min(H, y2 + AMPLIA * h))
    r = im[b:d, a:c]
    s = max(r.shape[:2])
    lienzo = np.full((s, s, 3), 114, np.uint8)
    oy, ox = (s - r.shape[0]) // 2, (s - r.shape[1]) // 2
    lienzo[oy:oy + r.shape[0], ox:ox + r.shape[1]] = r
    return cv2.resize(lienzo, (TAM, TAM), interpolation=cv2.INTER_AREA)


def cajas_de(meta):
    return [(o["x1"], o["y1"], o["x2"], o["y2"]) for o in meta["instancias"]]


# ----------------------------------------------------------------------------- generacion
def generar(familias):
    import cv2
    from argos_lib.gt import cargar_gt
    from argos_lib.oclusion import (BancoRecortes, PROB_TIPO_ENTRENAMIENTO, cobertura_por_caja,
                                    contenido_parche, leer_imagen, parche_interior, pegar)
    from argos_lib.siluetas import BancoSiluetas, ocluir_siluetas
    from argos_lib.geometria import BancoPatrones, ocluir_geometria
    gt = cargar_gt(GT_CP)
    dimg = gt["dir_imagenes"] if os.path.isdir(gt["dir_imagenes"]) else os.path.join(RAIZ, "externos", "citypersons", "Citypersons", "images", "val")
    real, base, objetivo = muestras(gt)
    os.makedirs(SAL, exist_ok=True)
    meta = {"real": [], "base": []}
    for nombre, lista in (("real", real), ("base", base)):
        os.makedirs(os.path.join(SAL, nombre), exist_ok=True)
        for k, (rel, i, caja, vis) in enumerate(lista):
            ruta = os.path.join(SAL, nombre, "%03d.png" % k)
            if not os.path.exists(ruta):
                cv2.imwrite(ruta, recorte(leer_imagen(os.path.join(dimg, rel)), caja))
            meta[nombre].append({"k": k, "rel": rel, "idx": i, "vis": vis, "alto": caja[3] - caja[1]})
    banco_r = BancoRecortes(os.path.join(RAIZ, "dataset", "banco_train.json"))
    banco_s = BancoSiluetas(os.path.join(RAIZ, "dataset", "siluetas_cp_val"))
    patrones = BancoPatrones(os.path.join(RAIZ, "dataset", "geometria", "patrones_train.json"))
    gen = None
    for fam in familias:
        os.makedirs(os.path.join(SAL, fam), exist_ok=True)
        filas, t0 = [], time.time()
        for k, (rel, i, caja, _) in enumerate(base):
            ruta = os.path.join(SAL, fam, "%03d.png" % k)
            f = objetivo[k]
            rnd = np.random.RandomState(13000 + k)
            im = leer_imagen(os.path.join(dimg, rel))
            todas = cajas_de(gt["imagenes"][rel])
            cov = 0.0
            if fam == "parches":
                tipos, probs = zip(*PROB_TIPO_ENTRENAMIENTO.items())
                tipo = str(rnd.choice(tipos, p=probs))
                rect = parche_interior(rnd, caja, f)
                cont = contenido_parche(rnd, tipo, im, todas, rect[2] - rect[0], rect[3] - rect[1], banco_r, textura_propia=True)
                m = np.zeros(im.shape[:2], np.uint8)
                pegar(im, m, rect, cont)
                cov = float(cobertura_por_caja(m, [caja])[0])
                extra = {"tipo": tipo}
            elif fam == "siluetas":
                ap, _, _ = ocluir_siluetas(im, [caja], rnd, banco_s, todas=True, f_fijo=lambda r, f=f: f)
                cov = float(ap[0][3]) if ap else 0.0
                extra = {"clase": ap[0][1] if ap else None}
            elif fam == "geometria":
                ap, _, _ = ocluir_geometria(im, [caja], rnd, banco_s, patrones, todas=True,
                                            rango_c=(max(0.35, f - 0.05), min(0.95, f + 0.05)))
                cov = float(ap[0][3]) if ap else 0.0
                extra = {"clase": ap[0][1] if ap else None}
            else:
                if gen is None:
                    from argos_lib.generativa import GeneradorOclusion
                    gen = GeneradorOclusion(os.path.join(RAIZ, "modelos", "sd15_inpaint"), lote=1)
                (res, efectiva), = gen.ocluir([{"im": im, "cajas": [caja], "objetivo": [(0, f)], "semilla": 13000 + k}])
                cov = float(cobertura_por_caja(efectiva, [caja])[0])
                extra = {"ok": bool(res[0]["ok"]) if res else False, "prompt": res[0]["prompt"] if res else None}
            cv2.imwrite(ruta, recorte(im, caja))
            filas.append({"k": k, "rel": rel, "idx": i, "f_objetivo": round(f, 4), "cobertura": round(cov, 4), **extra})
            if (k + 1) % 50 == 0:
                print("  %s: %d/%d (%.1f s/persona)" % (fam, k + 1, N, (time.time() - t0) / (k + 1)), flush=True)
        meta[fam] = filas
        json.dump(meta, open(os.path.join(SAL, "indice.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump(meta, open(os.path.join(SAL, "indice.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("Generacion: %s" % {k: len(v) for k, v in meta.items()})


# ----------------------------------------------------------------------------- caracteristicas
def caracteristicas():
    import torch
    from PIL import Image
    from transformers import AutoImageProcessor, AutoModel, CLIPModel, CLIPProcessor
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    modelos = {"dinov2": ("facebook/dinov2-base", "dino"), "clip": ("openai/clip-vit-base-patch16", "clip")}
    os.makedirs(RES, exist_ok=True)
    out = {}
    for clave, (hf, tipo) in modelos.items():
        if tipo == "dino":
            proc, mod = AutoImageProcessor.from_pretrained(hf), AutoModel.from_pretrained(hf).to(dev).eval()
        else:
            proc, mod = CLIPProcessor.from_pretrained(hf), CLIPModel.from_pretrained(hf).to(dev).eval()
        for c in CONJUNTOS:
            rutas = [os.path.join(SAL, c, "%03d.png" % k) for k in range(N)]
            vec = []
            for a in range(0, N, 32):
                ims = [Image.open(r).convert("RGB") for r in rutas[a:a + 32]]
                with torch.no_grad():
                    if tipo == "dino":
                        x = proc(images=ims, return_tensors="pt").to(dev)
                        v = mod(**x).pooler_output
                    else:
                        x = proc(images=ims, return_tensors="pt").to(dev)
                        v = mod.get_image_features(**x)
                        v = v if hasattr(v, "float") else v.pooler_output     # transformers 5: objeto con pooler_output
                vec.append(v.float().cpu().numpy())
            out["%s__%s" % (clave, c)] = np.concatenate(vec)
            print("  %s %s %s" % (clave, c, out["%s__%s" % (clave, c)].shape), flush=True)
    np.savez_compressed(os.path.join(RES, "caracteristicas.npz"), **out)


# ----------------------------------------------------------------------------- analisis
def puntuaciones_oof(X_real, X_otro, rep=5, k=5):
    """Puntuacion fuera de muestra (promedio de rep repeticiones de CV estratificada k) para 'otro' (clase 1)."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    X = np.vstack([X_real, X_otro]); y = np.r_[np.zeros(len(X_real)), np.ones(len(X_otro))]
    s = np.zeros(len(y))
    for r in range(rep):
        for tr, te in StratifiedKFold(k, shuffle=True, random_state=r).split(X, y):
            clf = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000))
            clf.fit(X[tr], y[tr])
            s[te] += clf.decision_function(X[te]) / rep
    return s[:len(X_real)], s[len(X_real):]


def auc(s0, s1):
    """AUC de Mann-Whitney (clase 1 por encima de clase 0)."""
    from scipy.stats import rankdata
    r = rankdata(np.r_[s0, s1])
    n0, n1 = len(s0), len(s1)
    return (r[n0:].sum() - n1 * (n1 + 1) / 2) / (n0 * n1)


def kid(A, Bm, n_sub=50, tam=100, semilla=0):
    rnd = np.random.RandomState(semilla)
    d = A.shape[1]
    k = lambda x, y: (x @ y.T / d + 1) ** 3
    v = []
    for _ in range(n_sub):
        a = A[rnd.choice(len(A), tam, replace=False)]; b = Bm[rnd.choice(len(Bm), tam, replace=False)]
        kaa, kbb, kab = k(a, a), k(b, b), k(a, b)
        m = tam
        v.append((kaa.sum() - np.trace(kaa)) / (m * (m - 1)) + (kbb.sum() - np.trace(kbb)) / (m * (m - 1)) - 2 * kab.mean())
    v = np.array(v)
    return float(v.mean()), float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def analizar_extractor(F, clave):
    Xr = F["%s__real" % clave]
    sc = {}
    for c in ["base"] + FAMILIAS:
        sc[c] = puntuaciones_oof(Xr, F["%s__%s" % (clave, c)])
    rnd = np.random.RandomState(0)
    boot = {c: np.zeros(B) for c in sc}
    for b in range(B):
        ir = rnd.randint(0, N, N); io = rnd.randint(0, N, N)      # personas reales y personas base (pareadas entre familias)
        for c, (s0, s1) in sc.items():
            boot[c][b] = auc(s0[ir], s1[io])
    filas = []
    for c, (s0, s1) in sc.items():
        filas.append({"extractor": clave, "conjunto": c, "AUC": round(float(auc(s0, s1)), 4),
                      "IC_lo": round(float(np.percentile(boot[c], 2.5)), 4), "IC_hi": round(float(np.percentile(boot[c], 97.5)), 4)})
    difs = []
    for a, b_ in [("parches", "siluetas"), ("siluetas", "generativa"), ("parches", "generativa"), ("siluetas", "geometria"),
                  ("geometria", "generativa")] + [("base", f) for f in FAMILIAS]:
        d = boot[a] - boot[b_]
        difs.append({"extractor": clave, "contraste": "%s - %s" % (a, b_),
                     "dif_AUC": round(float(auc(*sc[a]) - auc(*sc[b_])), 4),
                     "IC_lo": round(float(np.percentile(d, 2.5)), 4), "IC_hi": round(float(np.percentile(d, 97.5)), 4)})
    kids = []
    for c in ["base"] + FAMILIAS:
        m, lo, hi = kid(Xr, F["%s__%s" % (clave, c)])
        kids.append({"extractor": clave, "conjunto": c, "KID": round(m, 5), "IC_lo": round(lo, 5), "IC_hi": round(hi, 5)})
    return filas, difs, kids


def veredicto(difs):
    """H13: AUC(parches) > AUC(siluetas) > AUC(generativa), ambas diferencias con IC > 0 (DINOv2)."""
    d = {x["contraste"]: x for x in difs if x["extractor"] == "dinov2"}
    a, b = d["parches - siluetas"]["IC_lo"] > UMBRAL_DIF, d["siluetas - generativa"]["IC_lo"] > UMBRAL_DIF
    return "Confirmada" if a and b else ("Parcialmente confirmada" if a or b else "No confirmada")


def analisis():
    F = dict(np.load(os.path.join(RES, "caracteristicas.npz")))
    idx = json.load(open(os.path.join(SAL, "indice.json"), encoding="utf-8"))
    filas, difs, kids = [], [], []
    for clave in ("dinov2", "clip"):
        a, b, c = analizar_extractor(F, clave)
        filas += a; difs += b; kids += c
    # confusor de tamano: AUC usando solo la altura de la caja (real frente a base)
    ar = np.array([m["alto"] for m in idx["real"]], float); ab = np.array([m["alto"] for m in idx["base"]], float)
    auc_alto = float(auc(np.log(ar), np.log(ab)))
    cob = {f: {"cobertura_media": round(float(np.mean([m["cobertura"] for m in idx[f]])), 3),
               "sin_oclusion": int(sum(m["cobertura"] <= 0 for m in idx[f]))} for f in FAMILIAS if f in idx}
    v = veredicto(difs)
    res = {"veredicto_H13": v, "auc": filas, "diferencias": difs, "kid": kids, "AUC_solo_altura_real_vs_base": round(auc_alto, 4),
           "cobertura": cob, "oclusion_real_media": round(float(np.mean([1 - m["vis"] for m in idx["real"]])), 3)}
    os.makedirs(os.path.join(RES, "analisis"), exist_ok=True)
    json.dump(res, open(os.path.join(RES, "analisis", "realismo_h13.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    L = ["# ARGOS-11 — Veredicto de H13 (realismo medido de cada familia de oclusor)", "",
         "Generado por `31_realismo.py analisis`. Regla literal de `PREREGISTRO_H13.md`. AUC de un clasificador lineal que separa "
         "la oclusión real (CityPersons heavy) de cada conjunto; 0,5 = indistinguible. IC 95 %: bootstrap de personas (1 000).", "",
         "| Extractor | Conjunto | AUC frente a oclusión real | IC 95 % |", "|---|---|---|---|"]
    L += ["| %s | %s | %.3f | [%.3f; %.3f] |" % (x["extractor"], x["conjunto"], x["AUC"], x["IC_lo"], x["IC_hi"]) for x in filas]
    L += ["", "| Extractor | Contraste | Diferencia de AUC | IC 95 % |", "|---|---|---|---|"]
    L += ["| %s | %s | %+.3f | [%+.3f; %+.3f] |" % (x["extractor"], x["contraste"], x["dif_AUC"], x["IC_lo"], x["IC_hi"]) for x in difs]
    L += ["", "| Extractor | Conjunto | KID frente a oclusión real | IC 95 % |", "|---|---|---|---|"]
    L += ["| %s | %s | %.4f | [%.4f; %.4f] |" % (x["extractor"], x["conjunto"], x["KID"], x["IC_lo"], x["IC_hi"]) for x in kids]
    L += ["", "- AUC usando solo la altura de la caja (real frente a base): %.3f." % auc_alto,
          "- Cobertura conseguida por familia: %s; oclusión real media: %.3f." % (cob, res["oclusion_real_media"]), "",
          "## Veredicto H13: **%s**" % v, "",
          "Regla: confirmada si, con DINOv2, AUC(parches) − AUC(siluetas) y AUC(siluetas) − AUC(generativa) tienen IC 95 % > 0; "
          "parcialmente si solo una; no confirmada si ninguna."]
    open(os.path.join(RAIZ, "informes", "veredicto_h13.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


# ----------------------------------------------------------------------------- autotest
def selftest():
    fallos = []

    def comp(desc, ok):
        print("  [%s] %s" % ("OK" if ok else "FALLO", desc))
        if not ok:
            fallos.append(desc)
    comp("AUC perfecta = 1", auc(np.array([0., 1, 2]), np.array([5., 6, 7])) == 1.0)
    comp("AUC empate total = 0,5", auc(np.zeros(5), np.zeros(5)) == 0.5)
    rnd = np.random.RandomState(0)
    a, b = rnd.normal(0, 1, (200, 8)), rnd.normal(0, 1, (200, 8))
    s0, s1 = puntuaciones_oof(a, b, rep=2)
    comp("misma distribucion -> AUC fuera de muestra ~0,5", abs(auc(s0, s1) - 0.5) < 0.1)
    c = rnd.normal(1.5, 1, (200, 8))
    s0, s1 = puntuaciones_oof(a, c, rep=2)
    comp("distribuciones separadas -> AUC > 0,9", auc(s0, s1) > 0.9)
    comp("KID ~0 con la misma distribucion", abs(kid(a, b, n_sub=10, tam=50)[0]) < 0.05)
    comp("KID > 0 con distribuciones distintas", kid(a, c, n_sub=10, tam=50)[0] > kid(a, b, n_sub=10, tam=50)[0])
    D = lambda ps, sg: [{"extractor": "dinov2", "contraste": "parches - siluetas", "IC_lo": ps},
                        {"extractor": "dinov2", "contraste": "siluetas - generativa", "IC_lo": sg}]
    comp("ambas > 0 -> confirmada", veredicto(D(0.01, 0.02)) == "Confirmada")
    comp("una > 0 -> parcial", veredicto(D(0.05, -0.01)) == "Parcialmente confirmada")
    comp("ninguna -> no confirmada", veredicto(D(-0.01, 0.0)) == "No confirmada")
    im = np.zeros((100, 200, 3), np.uint8)
    comp("recorte 224x224 en el borde", recorte(im, (0, 0, 30, 90)).shape == (TAM, TAM, 3))
    print("\n%s" % ("AUTOTEST SUPERADO: %d/%d" % (10 - len(fallos), 10) if not fallos else "FALLOS: %s" % fallos))
    sys.exit(1 if fallos else 0)


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - H13: realismo medido")
    ap.add_argument("paso", nargs="?", choices=["generar", "caracteristicas", "analisis"])
    ap.add_argument("--familias", nargs="+", default=FAMILIAS)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    if a.paso == "generar":
        generar(a.familias)
    elif a.paso == "caracteristicas":
        caracteristicas()
    elif a.paso == "analisis":
        analisis()
    else:
        ap.error("indicar paso")


if __name__ == "__main__":
    main()
