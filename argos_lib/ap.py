# -*- coding: utf-8 -*-
"""
AP estilo COCO con regiones *ignore* (protocolo de la Seccion 2.4 del PPI).

Reglas del protocolo, identicas para todos los estratos:
  (a) al evaluar un estrato solo cuentan como GT las instancias de ese estrato;
  (b) las instancias de otros estratos en la misma imagen se marcan como
      regiones ignore (convencion de CityPersons / iscrowd de COCO): las
      detecciones que caen sobre ellas no cuentan ni como FP ni como TP;
  (c) todas las imagenes participan en todos los estratos;
  (d) se reporta el numero de instancias efectivas de cada estrato.

Implementacion: el emparejamiento se hace por imagen y se guarda (score, tp)
por umbral de IoU. Eso permite el bootstrap sobre imagenes (Seccion 2.6) sin
volver a emparejar: se remuestrean las imagenes y se concatenan sus listas.

La logica de emparejamiento reproduce la de pycocotools (evaluateImg):
  - detecciones ordenadas por score descendente, maximo MAX_DET por imagen;
  - GT no-ignore primero, ignore despues;
  - para GT ignore el "IoU" es interseccion / area de la deteccion;
  - una deteccion emparejada con un GT ignore se descarta de la curva;
  - AP con interpolacion en 101 puntos de recall.
El autotest contrasta contra pycocotools cuando esta instalado.
"""

import numpy as np

IOU_THRS = np.round(np.arange(0.50, 0.96, 0.05), 2)   # 0.50:0.05:0.95
REC_THRS = np.linspace(0.0, 1.0, 101)
MAX_DET = 100


def _iou_matriz(dets, gts, ign):
    """IoU entre detecciones (N,4) y GT (M,4) xyxy. Para GT ignore usa
    interseccion / area de la deteccion (semantica iscrowd de COCO)."""
    if len(dets) == 0 or len(gts) == 0:
        return np.zeros((len(dets), len(gts)))
    d = np.asarray(dets, dtype=float)[:, :4]
    g = np.asarray(gts, dtype=float)[:, :4]
    ix1 = np.maximum(d[:, None, 0], g[None, :, 0])
    iy1 = np.maximum(d[:, None, 1], g[None, :, 1])
    ix2 = np.minimum(d[:, None, 2], g[None, :, 2])
    iy2 = np.minimum(d[:, None, 3], g[None, :, 3])
    inter = np.clip(ix2 - ix1, 0, None) * np.clip(iy2 - iy1, 0, None)
    ad = (d[:, 2] - d[:, 0]) * (d[:, 3] - d[:, 1])
    ag = (g[:, 2] - g[:, 0]) * (g[:, 3] - g[:, 1])
    union = ad[:, None] + ag[None, :] - inter
    ign = np.asarray(ign, dtype=bool)
    denom = np.where(ign[None, :], np.repeat(ad[:, None], len(g), axis=1), union)
    with np.errstate(divide="ignore", invalid="ignore"):
        iou = np.where(denom > 0, inter / denom, 0.0)
    return iou


def emparejar_imagen(dets, gts, ign, iou_thrs=IOU_THRS, max_det=MAX_DET):
    """Empareja una imagen.

    dets: lista [x1,y1,x2,y2,score]; gts: lista [x1,y1,x2,y2];
    ign: lista bool (True = region ignore).

    Devuelve dict con:
        n_gt      numero de GT no-ignore
        scores    (T, K) scores de las detecciones no descartadas por umbral
        tp        (T, K) bool
    Las columnas K varian por umbral, asi que se guardan como listas.
    """
    dets = sorted(dets, key=lambda r: -r[4])[:max_det]
    ign = list(ign)
    orden = sorted(range(len(gts)), key=lambda i: ign[i])   # no-ignore primero
    gts_o = [gts[i] for i in orden]
    ign_o = [ign[i] for i in orden]
    n_gt = sum(1 for v in ign_o if not v)
    iou = _iou_matriz(dets, gts_o, ign_o)

    scores_t, tp_t = [], []
    for thr in iou_thrs:
        gt_usado = [False] * len(gts_o)
        sc, tp = [], []
        for di, d in enumerate(dets):
            mejor, mejor_iou = -1, min(thr, 1 - 1e-10)
            for gi in range(len(gts_o)):
                if gt_usado[gi] and not ign_o[gi]:
                    continue
                if mejor > -1 and not ign_o[mejor] and ign_o[gi]:
                    break            # ya emparejada con GT real: no pasar a ignore
                if iou[di, gi] < mejor_iou:
                    continue
                mejor_iou, mejor = iou[di, gi], gi
            if mejor == -1:
                sc.append(d[4]); tp.append(False)      # falso positivo
            elif ign_o[mejor]:
                continue                                # cae sobre ignore: se descarta
            else:
                gt_usado[mejor] = True
                sc.append(d[4]); tp.append(True)
        scores_t.append(np.asarray(sc, dtype=float))
        tp_t.append(np.asarray(tp, dtype=bool))
    return {"n_gt": n_gt, "scores": scores_t, "tp": tp_t}


def ap_desde_listas(scores, tp, n_gt, rec_thrs=REC_THRS):
    """AP (101 puntos) a partir de scores y tp concatenados de todas las
    imagenes, para UN umbral de IoU."""
    if n_gt == 0:
        return float("nan")
    if len(scores) == 0:
        return 0.0
    orden = np.argsort(-scores, kind="mergesort")
    tp = tp[orden].astype(float)
    fp = 1.0 - tp
    tpc, fpc = np.cumsum(tp), np.cumsum(fp)
    rec = tpc / n_gt
    prec = tpc / np.maximum(tpc + fpc, np.finfo(float).eps)
    # envolvente monotona de precision (como COCO)
    for i in range(len(prec) - 1, 0, -1):
        if prec[i] > prec[i - 1]:
            prec[i - 1] = prec[i]
    idx = np.searchsorted(rec, rec_thrs, side="left")
    q = np.zeros(len(rec_thrs))
    validos = idx < len(prec)
    q[validos] = prec[idx[validos]]
    return float(np.mean(q))


def ap_conjunto(emparejados, indices=None, iou_thrs=IOU_THRS):
    """AP por umbral sobre un conjunto de imagenes ya emparejadas.

    emparejados: lista de dicts de emparejar_imagen (una por imagen).
    indices: si se da, remuestreo (bootstrap) de imagenes por indice.
    Devuelve dict {"AP50", "AP", "AP_por_umbral", "n_gt"}.
    """
    if indices is None:
        indices = range(len(emparejados))
    n_gt = sum(emparejados[i]["n_gt"] for i in indices)
    aps = []
    for t in range(len(iou_thrs)):
        sc = np.concatenate([emparejados[i]["scores"][t] for i in indices]) \
            if len(emparejados) else np.zeros(0)
        tp = np.concatenate([emparejados[i]["tp"][t] for i in indices]) \
            if len(emparejados) else np.zeros(0, dtype=bool)
        aps.append(ap_desde_listas(sc, tp, n_gt))
    aps = np.asarray(aps)
    return {"AP50": float(aps[0]), "AP": float(np.nanmean(aps)) if n_gt else float("nan"),
            "AP_por_umbral": aps.tolist(), "n_gt": int(n_gt)}


def emparejar_conjunto(gt_imagenes, detecciones, estrato=None, filtro_imagen=None,
                       ignorar=("ignorar",)):
    """Empareja todas las imagenes de un GT para un estrato dado.

    - estrato=None: evaluacion global; todas las instancias son GT salvo las
      de las etiquetas en `ignorar` (no evaluables), que son ignore.
    - estrato='severa': solo las de ese estrato son GT; el resto (otros
      estratos, 'sin_anotar', 'ignorar') son ignore -> regla (b).
    - filtro_imagen(nombre, meta) -> bool permite restringir por condicion
      de luz (las imagenes descartadas no participan).
    Devuelve (lista_emparejados, nombres_imagen).
    """
    emparejados, nombres = [], []
    for nombre, meta in gt_imagenes.items():
        if filtro_imagen and not filtro_imagen(nombre, meta):
            continue
        gts, ign = [], []
        for o in meta["instancias"]:
            gts.append([o["x1"], o["y1"], o["x2"], o["y2"]])
            if estrato is None:
                ign.append(o["estrato"] in ignorar)
            else:
                ign.append(o["estrato"] != estrato)
        dets = detecciones.get(nombre, [])
        emparejados.append(emparejar_imagen(dets, gts, ign))
        nombres.append(nombre)
    return emparejados, nombres


# --- Autotest ---------------------------------------------------------------
def _pycoco_ap(imgs, iou_thr_idx=None):
    """Calcula AP con pycocotools sobre la misma estructura (para contraste)."""
    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval
    import io, contextlib
    images, anns, dts, aid = [], [], [], 1
    for iid, (dets, gts, ign) in enumerate(imgs, 1):
        images.append({"id": iid, "width": 1000, "height": 1000})
        for g, ig in zip(gts, ign):
            w, h = g[2] - g[0], g[3] - g[1]
            anns.append({"id": aid, "image_id": iid, "category_id": 1,
                         "bbox": [g[0], g[1], w, h], "area": w * h,
                         "iscrowd": int(ig)})
            aid += 1
        for d in dets:
            dts.append({"image_id": iid, "category_id": 1, "score": d[4],
                        "bbox": [d[0], d[1], d[2] - d[0], d[3] - d[1]]})
    coco = COCO()
    coco.dataset = {"images": images, "annotations": anns,
                    "categories": [{"id": 1, "name": "person"}]}
    with contextlib.redirect_stdout(io.StringIO()):
        coco.createIndex()
        cdt = coco.loadRes(dts) if dts else COCO()
        if not dts:
            cdt.dataset = {"images": images, "annotations": [],
                           "categories": coco.dataset["categories"]}
            cdt.createIndex()
        ev = COCOeval(coco, cdt, "bbox")
        ev.params.maxDets = [1, 10, MAX_DET]
        ev.evaluate(); ev.accumulate(); ev.summarize()
    return float(ev.stats[0]), float(ev.stats[1])


def selftest():
    rnd = np.random.RandomState(3)
    fallos = []

    def comp(desc, obt, esp, tol=1e-9):
        ok = abs(obt - esp) <= tol if isinstance(esp, float) else obt == esp
        print("  [%s] %-50s %s" % ("ok" if ok else "FALLA", desc,
                                   round(obt, 5) if isinstance(obt, float) else obt))
        if not ok:
            fallos.append(desc)

    # 1. Deteccion perfecta -> AP 1.
    e = emparejar_imagen([[0, 0, 10, 10, 0.9]], [[0, 0, 10, 10]], [False])
    comp("deteccion perfecta: AP50 = 1", ap_conjunto([e])["AP50"], 1.0)
    comp("deteccion perfecta: AP = 1", ap_conjunto([e])["AP"], 1.0)

    # 2. Sin detecciones -> AP 0; sin GT -> nan.
    e0 = emparejar_imagen([], [[0, 0, 10, 10]], [False])
    comp("sin detecciones: AP 0", ap_conjunto([e0])["AP50"], 0.0)
    en = emparejar_imagen([[0, 0, 10, 10, 0.9]], [], [])
    comp("sin GT: n_gt 0", ap_conjunto([en])["n_gt"], 0)

    # 3. Regla (b): deteccion sobre region ignore no es FP.
    dets = [[0, 0, 10, 10, 0.9], [50, 50, 60, 60, 0.95]]
    gts = [[0, 0, 10, 10], [50, 50, 60, 60]]
    con_ignore = emparejar_imagen(dets, gts, [False, True])
    sin_ignore = emparejar_imagen(dets, [gts[0]], [False])   # GT2 borrado: FP
    comp("deteccion sobre ignore no penaliza (AP50=1)",
         ap_conjunto([con_ignore])["AP50"], 1.0)
    comp("misma deteccion sin ignore si penaliza (AP50<1)",
         ap_conjunto([sin_ignore])["AP50"] < 1.0, True)
    comp("GT ignore no cuenta como instancia", con_ignore["n_gt"], 1)

    # 4. Bootstrap por indices: remuestrear la misma imagen da el mismo AP.
    comp("remuestreo identico conserva AP",
         ap_conjunto([e, e0], indices=[0, 1])["AP50"],
         ap_conjunto([e, e0])["AP50"])

    # 5. Contraste con pycocotools sobre datos aleatorios con ignore.
    try:
        import pycocotools  # noqa: F401
        imgs = []
        for _ in range(40):
            gts, ign = [], []
            for _ in range(rnd.randint(0, 6)):
                x, y = rnd.uniform(0, 900, 2)
                w, h = rnd.uniform(10, 100, 2)
                gts.append([x, y, x + w, y + h]); ign.append(bool(rnd.rand() < 0.25))
            dets = []
            for g in gts:
                if rnd.rand() < 0.8:
                    j = rnd.uniform(-8, 8, 4)
                    dets.append([g[0] + j[0], g[1] + j[1], g[2] + j[2], g[3] + j[3],
                                 float(rnd.rand())])
            for _ in range(rnd.randint(0, 4)):
                x, y = rnd.uniform(0, 900, 2)
                w, h = rnd.uniform(10, 100, 2)
                dets.append([x, y, x + w, y + h, float(rnd.rand())])
            imgs.append((dets, gts, ign))
        emp = [emparejar_imagen(d, g, i) for d, g, i in imgs]
        propio = ap_conjunto(emp)
        ap_c, ap50_c = _pycoco_ap(imgs)
        comp("AP50 coincide con pycocotools", propio["AP50"], ap50_c, 1e-6)
        comp("AP@.5:.95 coincide con pycocotools", propio["AP"], ap_c, 1e-6)
    except ImportError:
        print("  [--] pycocotools no instalado: se omite el contraste")

    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(selftest())
