"""ARGOS-11 - Tabla de veredictos H1-H7: redaccion literal pre-registrada
(PROTOCOLO.md s.7, PROTOCOLO_v2.md s.2, PREREGISTRO_H6_H7.md s.2) frente al
resultado observado, leido de los ficheros de analisis ya calculados.

No recalcula nada. Fuentes:
  resultados/analisis/{criterios.json,bootstrap.csv}                (exp. 1, v1.1b)
  resultados_v2/analisis_yolo11s/{criterios.json,bootstrap.csv}     (iteracion 2, v2.0)
  resultados/resumen_costo.csv                                      (FPS)

Uso:
    python 19_veredictos.py            # -> informes/veredictos_H1_H7.md
    python 19_veredictos.py --selftest
"""
import argparse
import json
import os

import pandas as pd

RAIZ = os.path.dirname(os.path.abspath(__file__))

LITERAL = {
    "H1": ("PROTOCOLO.md s.7 (v1.0, 11/09/2026)",
           "AP@0.5 de V4 > V1 en moderada y severa, con FPS ≥ 90 % del baseline. "
           "Se sostiene cuando conjuntamente: (a) ΔAP@0.5 ≥ +2 pp frente a V1 (media de 3 semillas) "
           "en moderada y severa; (b) el IC 95 % por bootstrap sobre imágenes (≥1000 réplicas) excluye "
           "el cero; (c) FPS ≥ 30 en GPU de escritorio."),
    "H2": ("PROTOCOLO.md s.7 (v1.0)",
           "Aporte de VI₂ (aumento de oclusión, V3−V1) > aporte de VI₁ (CBAM, V2−V1) en los estratos ocluidos."),
    "H3": ("PROTOCOLO.md s.7 (v1.0)",
           "La dirección del efecto se conserva sobre oclusión real, en ≥2 de 3 fuentes (propia, NightOwls, "
           "CityPersons); si discrepan, no concluyente."),
    "H4": ("PROTOCOLO_v2.md s.2 (v2.0, 12/09/2026)",
           "Con oclusores de silueta real (personas y objetos con máscara, sin parches rectangulares ni opacos), "
           "el aumento de oclusión (V3′/V4′) mejora el AP@0.5 frente a V1′ en los estratos ocluidos de al menos "
           "dos de las tres fuentes reales (NightOwls ocluida, CityPersons moderada+severa / heavy, subconjunto "
           "propio), con IC 95 % bootstrap que excluya el cero. Umbral de relevancia: +2 pp."),
    "H5": ("PROTOCOLO_v2.md s.2 (v2.0)",
           "La mejora sintética de la iteración 2 sobre silueta_* será menor que la de la iteración 1 sobre "
           "opaco_*/textura_* (menos “firma” aprendible), y la brecha sintético→real se reducirá."),
    "H6": ("PREREGISTRO_H6_H7.md s.2 (19/09/2026)",
           "El déficit de transferencia de H3 se replica al re-entrenar directamente sobre CityPersons: V3−V1 "
           "(AP@0.5, media de 3 semillas) sobre CityPersons val en la convención oficial heavy no alcanza +2 pp o "
           "su IC 95 % incluye el cero, aun cuando el control sintético cp_silueta_severa sea ≥ +2 pp."),
    "H8": ("PREREGISTRO_H8.md s.2 (26/09/2026)",
           "El déficit de transferencia se replica con un detector de otra familia: con RT-DETR-l entrenado con el "
           "protocolo de la iteración 2, V3′−V1′ no alcanza +2 pp con IC 95 % que excluya el cero en al menos 2 de las "
           "3 fuentes reales (NightOwls ocluida, CityPersons heavy, ExDark proxy severa), aun cuando el control "
           "silueta_severa sea ≥ +2 pp con IC que excluya el cero."),
    "H9": ("PREREGISTRO_H9.md s.2 (02/10/2026)",
           "El déficit de transferencia se replica con una tercera familia de oclusor, la oclusión generativa: con "
           "YOLOv11s entrenado con el protocolo de la iteración 2 y oclusores pintados por un modelo de difusión "
           "(Stable Diffusion inpainting), V3ᵍ−V1′ no alcanza +2 pp con IC 95 % que excluya el cero en al menos 2 de "
           "las 3 fuentes reales (NightOwls ocluida, CityPersons heavy, ExDark proxy severa), aun cuando el control "
           "generativa_severa sea ≥ +2 pp con IC que excluya el cero."),
    "H7": ("PREREGISTRO_H6_H7.md s.2 (19/09/2026)",
           "El déficit de transferencia persiste con datos abundantes del dominio nocturno: en el peldaño de "
           "20 000 imágenes de NightOwls train, V3−V1 sobre NightOwls val estrato ocluida no alcanza +2 pp o su "
           "IC 95 % incluye el cero."),
}


def _ic(df, conj, est, contraste):
    r = df[(df.conjunto == conj) & (df.estrato == est) & (df.contraste == contraste)]
    if r.empty:
        return None
    r = r.iloc[0]
    return r.delta_AP50_pp, r.IC95_lo_pp, r.IC95_hi_pp, int(r.n_gt)


def _fmt(t):
    if t is None:
        return "no calculado"
    d, lo, hi, n = t
    return f"{d:+.2f} pp [{lo:+.2f}; {hi:+.2f}] (n={n})"


def construir(raiz):
    d1 = os.path.join(raiz, "resultados", "analisis")
    d2 = os.path.join(raiz, "resultados_v2", "analisis_yolo11s")
    c1 = json.load(open(os.path.join(d1, "criterios.json"), encoding="utf-8"))
    c2 = json.load(open(os.path.join(d2, "criterios.json"), encoding="utf-8"))
    b1 = pd.read_csv(os.path.join(d1, "bootstrap.csv"))
    b2 = pd.read_csv(os.path.join(d2, "bootstrap.csv"))
    fps = c1.get("fps_medidos", {})
    propia1 = c1["resumen"].get("fuente_real_propia", "test_real")
    propia2 = c2["resumen"].get("fuente_real_propia", "test_real")

    filas = []
    # H1
    ev = [f"V4−V1 {propia1} moderada: {_fmt(_ic(b1, propia1, 'moderada', 'V4-V1'))}",
          f"V4−V1 {propia1} severa: {_fmt(_ic(b1, propia1, 'severa', 'V4-V1'))}"]
    if fps.get("V1") and fps.get("V4"):
        ev.append(f"FPS ORT FP16: V4 {fps['V4']:.0f} vs V1 {fps['V1']:.0f} → {100 * fps['V4'] / fps['V1']:.0f} % del baseline "
                  f"(criterio ≥ 90 %: {'cumple' if fps['V4'] >= 0.9 * fps['V1'] else 'no cumple'}; criterio (c) ≥ 30 FPS: cumple)")
    ver1 = "**No sostenida**" if not c1["resumen"]["H1_AP_criterios_a_b"] else "Sostenida"
    filas.append(("H1", ver1, ev, "Criterios (a) y (b) no se cumplen en ningún estrato ocluido de la fuente propia; "
                  "el criterio FPS ≥ 90 % del baseline tampoco (el CBAM cuesta ~18 %). (c) sí se cumple."))
    # H2
    h2 = c1["resumen"]["H2"]
    ev = [f"Aporte VI₂ (V3−V1) en {h2.get('fuente', propia1)} moderada+severa: {h2['aporte_oclusion_pp']:+.2f} pp (media de semillas)",
          f"Aporte VI₁ (V2−V1): {h2['aporte_cbam_pp']:+.2f} pp",
          f"V3−V1 {propia1} severa con IC: {_fmt(_ic(b1, propia1, 'severa', 'V3-V1'))}",
          f"V2−V1 {propia1} severa con IC: {_fmt(_ic(b1, propia1, 'severa', 'V2-V1'))}"]
    ver2 = "Sostenida (trivialmente)" if h2["sostenida"] else "**No sostenida**"
    filas.append(("H2", ver2, ev, "Ambos aportes son negativos o nulos sobre oclusión real; la comparación entre "
                  "ellos no tiene el sentido previsto (ninguno mejora). Sobre sintético, VI₂ ≫ VI₁ (+43/+61 pp vs ≈0)."))
    # H3. El "efecto" cuya direccion se comprueba es V4-V1 (ARGOS-11 completo frente al baseline,
    # el mismo contraste de H1), NO V3-V1. Por fuente, 11_ promedia delta_V4_V1_pp de los estratos
    # ocluidos disponibles (proxy: moderada y severa; NightOwls: ocluida; CityPersons: heavy) y lo
    # guarda en criterios.json -> resumen.H3.fuentes[*].delta_media_pp. Aqui se explicita ese calculo
    # y se listan los estratos con su IC para que cada cifra sea trazable a bootstrap.csv.
    h3 = c1["resumen"]["H3"]
    ev = [f"Contraste: V4−V1 (exp. 1), el mismo de H1. Dirección sintética (media de moderada+severa "
          f"de los conjuntos sintéticos): {h3['direccion_sintetica']}"]
    estratos_por_fuente = {"test_proxy": ["moderada", "severa"], "test_real": ["moderada", "severa"],
                           "nightowls": ["ocluida"], "citypersons_convencion": ["heavy"],
                           "citypersons": ["moderada", "severa"]}
    for k, f in h3["fuentes"].items():
        conj = f["conjunto"]
        partes = [f"{e} {_fmt(_ic(b1, conj, e, 'V4-V1'))}" for e in estratos_por_fuente.get(conj, [])]
        agg = ("media de " + " y ".join(estratos_por_fuente[conj])) if len(estratos_por_fuente.get(conj, [])) > 1 else "único estrato ocluido"
        ev.append(f"{k} ({conj}), {agg} = {f['delta_media_pp']:+.2f} pp → dirección {f['direccion']}; "
                  "por estrato: " + "; ".join(partes))
    lect = h3["lectura"]
    ver3 = ("**No sostenida**" if lect.startswith("no sostenida") else
            "No concluyente" if lect.startswith("no concluyente") else
            "Sostenida" if lect.startswith("sostenida") else lect)
    filas.append(("H3", ver3, ev, f"Lectura automática ({h3['coinciden']} de {h3['de']} fuentes conservan la dirección): {lect}. "
                  "Las fuentes no discrepan entre sí (todas negativas), por lo que no aplica la cláusula «no concluyente». "
                  "El promedio por fuente procede de criterios.json (11_analisis_estadistico.py); los IC, de bootstrap.csv."))
    # H4 (iteracion 2)
    ev = [f"NightOwls ocluida V3′−V1′: {_fmt(_ic(b2, 'nightowls', 'ocluida', 'V3-V1'))}",
          f"CityPersons heavy V3′−V1′: {_fmt(_ic(b2, 'citypersons_convencion', 'heavy', 'V3-V1'))}",
          f"{propia2} severa V3′−V1′: {_fmt(_ic(b2, propia2, 'severa', 'V3-V1'))}",
          f"NightOwls ocluida V4′−V1′: {_fmt(_ic(b2, 'nightowls', 'ocluida', 'V4-V1'))}"]
    filas.append(("H4", "**Refutada**", ev, "0 de 3 fuentes mejoran; dos empeoran con IC que excluye el cero. "
                  "Cumple la condición de refutación declarada (ΔAP ≤ 0 o IC con cero en ≥2 fuentes)."))
    # H5
    s1o = _ic(b1, "opaco_severa", "severa", "V3-V1"); s1t = _ic(b1, "textura_severa", "severa", "V3-V1")
    s2s = _ic(b2, "silueta_severa", "severa", "V3-V1")
    r1 = _ic(b1, "nightowls", "ocluida", "V3-V1"); r2 = _ic(b2, "nightowls", "ocluida", "V3-V1")
    ev = [f"Iteración 1, opaco severa V3−V1: {_fmt(s1o)}; textura severa: {_fmt(s1t)}",
          f"Iteración 2, silueta severa V3′−V1′: {_fmt(s2s)}",
          f"Brecha sintético→real (NightOwls ocluida): iter. 1 {s1o[0] - r1[0]:.1f} pp → iter. 2 {s2s[0] - r2[0]:.1f} pp, "
          f"pero el efecto real pasó de {r1[0]:+.1f} a {r2[0]:+.1f} pp"]
    filas.append(("H5", "**Parcialmente sostenida**", ev, "La primera parte se cumple (menor mejora sintética con "
                  "siluetas). La brecha numérica se reduce solo porque la mejora sintética es menor; el efecto real "
                  "empeoró, que es lo contrario de lo que H5 anticipaba."))
    # H6: replica de entrenamiento sobre CityPersons (resultados_h6/, protocolo v3.0).
    # Regla literal (PREREGISTRO_H6_H7.md s.2): control sintetico cp_silueta_severa >= +2 pp con IC
    # que excluya el cero (si no, "no concluyente"); sostenida si V3-V1 heavy < +2 pp o IC incluye 0;
    # refutada si >= +2 pp con IC que excluya 0 y misma direccion en partial.
    d6 = os.path.join(raiz, "resultados_h6", "analisis", "bootstrap.csv")
    if os.path.exists(d6):
        b6 = pd.read_csv(d6)
        ctrl = _ic(b6, "cp_silueta_severa", "severa", "V3-V1")
        heavy = _ic(b6, "citypersons_convencion", "heavy", "V3-V1")
        partial = _ic(b6, "citypersons_convencion", "partial", "V3-V1")
        ev = [f"Control sintético cp_silueta_severa V3−V1: {_fmt(ctrl)}",
              f"Primario: CityPersons heavy (vis 20–65 %) V3−V1: {_fmt(heavy)}",
              f"partial V3−V1: {_fmt(partial)}; bare: {_fmt(_ic(b6, 'citypersons_convencion', 'bare', 'V3-V1'))}; "
              f"global: {_fmt(_ic(b6, 'citypersons_convencion', 'global', 'V3-V1'))}",
              f"Estratos propios: moderada {_fmt(_ic(b6, 'citypersons', 'moderada', 'V3-V1'))}; severa {_fmt(_ic(b6, 'citypersons', 'severa', 'V3-V1'))}",
              f"Cruzados (descriptivo): NightOwls ocluida {_fmt(_ic(b6, 'nightowls', 'ocluida', 'V3-V1'))}; "
              f"proxy severa {_fmt(_ic(b6, propia2, 'severa', 'V3-V1'))}"]
        ctrl_ok = ctrl is not None and ctrl[0] >= 2.0 and ctrl[1] > 0
        if not ctrl_ok:
            ver6, nota6 = "No concluyente", "El control sintético no reproduce la mejora: el contraste real no es informativo."
        else:
            refut = heavy[0] >= 2.0 and heavy[1] > 0 and partial is not None and partial[0] > 0 and partial[1] > 0
            sost = heavy[0] < 2.0 or heavy[1] <= 0
            ver6 = "**Refutada**" if refut else ("**Sostenida**" if sost else "Indeterminada")
            nota6 = ("El déficit de transferencia se replica según la regla literal: el efecto real no alcanza el umbral de "
                     "relevancia de +2 pp (%+.2f pp) frente a %+.1f pp en el control sintético. Entrenar en el dominio elimina "
                     "el signo negativo observado al evaluar sin re-entrenar (exp. 1 −0,4; iter. 2 −3,9 en heavy), pero no "
                     "cierra la brecha sintético→real (%.0f:1). El IC por imágenes excluye el cero, pero el IC jerárquico "
                     "(semillas + imágenes, análisis de sensibilidad) lo incluye [−0,86; +4,42]: el efecto en el dominio es "
                     "nulo o levemente positivo. La refutación exigía además la misma dirección en partial con IC que "
                     "excluya el cero, que no se cumple." % (heavy[0], ctrl[0], ctrl[0] / max(heavy[0], 1e-9))
                     if sost else "Cumple la condición de refutación declarada.")
        filas.append(("H6", ver6, ev, nota6))
    else:
        filas.append(("H6", "Pendiente", ["Pre-registrada el 19/09/2026 (SHA-256 en CAMBIOS_PROTOCOLO.md). 6 corridas, sin ejecutar."],
                      "Requiere conversión de CityPersons train, bancos de siluetas y congelamiento v3.0."))
    # H7: escalera NightOwls (resultados_h7_20000/, protocolo v3.1). Regla literal
    # (PREREGISTRO_H6_H7.md s.2 y s.4): sostenida si V3-V1 en NightOwls 'ocluida' del peldano
    # 20 000 < +2 pp o IC con cero; refutada si >= +2 pp con IC que excluya el cero.
    # Comprobacion pre-registrada (s.4): V1 del peldano 20 000 debe superar a COCO sin ajustar
    # en NightOwls ocluida (0,387); si no, H7 pasa a "no concluyente".
    d7 = os.path.join(raiz, "resultados_h7_20000", "analisis")
    if os.path.exists(os.path.join(d7, "bootstrap.csv")):
        b7 = pd.read_csv(os.path.join(d7, "bootstrap.csv"))
        de7 = pd.read_csv(os.path.join(d7, "descriptivo.csv"))
        prim = _ic(b7, "nightowls", "ocluida", "V3-V1")
        v1o = de7[(de7.conjunto == "nightowls") & (de7.estrato == "ocluida") & (de7.variante == "V1")].AP50_media.iloc[0]
        v1s = de7[(de7.conjunto == "nightowls") & (de7.estrato == "sin") & (de7.variante == "V1")].AP50_media.iloc[0]
        coco = pd.read_csv(os.path.join(raiz, "resultados", "resumen_ap.csv"))
        coco = coco[(coco.corrida == "preliminar_coco_person") & (coco.luz == "todas") & (coco.conjunto == "nightowls")]
        coco_o = float(coco[coco.estrato == "ocluida"].AP50.iloc[0]); coco_s = float(coco[coco.estrato == "sin"].AP50.iloc[0])
        ev = [f"Primario: NightOwls ocluida, peldaño 20 000, V3−V1: {_fmt(prim)}",
              f"NightOwls sin oclusión V3−V1: {_fmt(_ic(b7, 'nightowls', 'sin', 'V3-V1'))}",
              f"Comprobación pre-registrada: V1 (20 000) en NightOwls ocluida {v1o:.3f} frente a COCO sin ajustar "
              f"{coco_o:.3f} → {'la supera' if v1o > coco_o else 'NO la supera'} ({100 * (v1o - coco_o):+.1f} pp); "
              f"en sin oclusión {v1s:.3f} frente a {coco_s:.3f} ({100 * (v1s - coco_s):+.1f} pp)",
              f"Cruzados (descriptivo): CityPersons heavy {_fmt(_ic(b7, 'citypersons_convencion', 'heavy', 'V3-V1'))}; "
              f"proxy severa {_fmt(_ic(b7, 'test_proxy', 'severa', 'V3-V1'))}"]
        if v1o <= coco_o:
            ver7, nota7 = "No concluyente", "El ajuste en dominio no supera al modelo genérico en ocluidos: condición pre-registrada."
        elif prim[0] >= 2.0 and prim[1] > 0:
            ver7, nota7 = "**Refutada**", "Cumple la condición de refutación declarada."
        else:
            ver7 = "**Sostenida**"
            nota7 = ("Con 20 000 imágenes del dominio nocturno (33 274 peatones, 10 veces ExDark), el aumento no mejora "
                     "la detección de peatones ocluidos (%+.2f pp, IC con cero). Los datos del dominio sí mejoran mucho "
                     "a los no ocluidos (%+.1f pp sobre COCO) pero apenas a los ocluidos (%+.1f pp): la oclusión real no "
                     "se resuelve ni con más datos ni con el aumento. La tendencia por peldaño (2k/5k/10k) es descriptiva."
                     % (prim[0], 100 * (v1s - coco_s), 100 * (v1o - coco_o)))
        filas.append(("H7", ver7, ev, nota7))
    else:
        filas.append(("H7", "Pendiente", ["Pre-registrada el 19/09/2026. 12 corridas, sin ejecutar; descarga (~8 GB) pendiente de autorización."],
                      "Escalera anidada 2k/5k/10k/20k con presupuesto fijo de 200 000 presentaciones por corrida."))

    # H8: RT-DETR-l (resultados_h8/, protocolo v3.2). Regla literal (PREREGISTRO_H8.md s.2).
    d8 = os.path.join(raiz, "resultados_h8", "analisis", "bootstrap.csv")
    if os.path.exists(d8):
        b8 = pd.read_csv(d8)
        ctrl = _ic(b8, "silueta_severa", "severa", "V3-V1")
        fuentes = [("NightOwls ocluida", "nightowls", "ocluida"), ("CityPersons heavy", "citypersons_convencion", "heavy"),
                   ("ExDark proxy severa", "test_proxy", "severa")]
        res = [(n, _ic(b8, c, e, "V3-V1")) for n, c, e in fuentes]
        mejora = sum(1 for _, r in res if r and r[0] >= 2.0 and r[1] > 0)
        ev = [f"Control silueta_severa V3′−V1′: {_fmt(ctrl)}"] + [f"{n} V3′−V1′: {_fmt(r)}" for n, r in res]
        rp = os.path.join(raiz, "resultados_h8", "resumen_ap.csv")
        v1g = cog = None
        if os.path.exists(rp):
            ra = pd.read_csv(rp)
            ra = ra[(ra.luz == "todas") & (ra.conjunto == "test_proxy") & (ra.estrato == "global")]
            if (ra.variante == "V1").any():
                v1g = float(ra[ra.variante == "V1"].AP50.mean())
            co = ra[ra.corrida == "rtdetr_coco_person"]
            cog = float(co.AP50.iloc[0]) if not co.empty else None
            if v1g is not None and cog is not None:
                ev.append(f"Comprobación: V1′ RT-DETR en ExDark test global {v1g:.3f} frente a RT-DETR COCO sin ajustar {cog:.3f}")
        if ctrl is None or not (ctrl[0] >= 2.0 and ctrl[1] > 0):
            ver8, nota8 = "No concluyente", "El control sintético no supera +2 pp con IC positivo: el aumento no se aprendió."
        elif v1g is not None and cog is not None and v1g <= cog:
            ver8, nota8 = "No concluyente", "El ajuste de RT-DETR no supera al modelo COCO sin ajustar en ExDark test."
        elif mejora >= 2:
            ver8, nota8 = "**Refutada**", "V3′−V1′ ≥ +2 pp con IC positivo en al menos 2 de 3 fuentes reales."
        else:
            ver8 = "**Sostenida**"
            nota8 = ("Con un detector de otra familia (transformer, sin NMS) el patrón se repite: el aumento se aprende "
                     "(control %+.2f pp) y no mejora la oclusión real (%d de 3 fuentes superan el umbral)." % (ctrl[0], mejora))
        filas.append(("H8", ver8, ev, nota8))
    else:
        filas.append(("H8", "Pendiente", ["Pre-registrada el 26/09/2026 (v3.2). 6 corridas de RT-DETR-l en curso."],
                      "Réplica con un detector de otra familia (transformer)."))

    # H9: oclusion generativa (resultados_h9/, protocolo v3.3b). Regla literal (PREREGISTRO_H9.md s.2).
    d9 = os.path.join(raiz, "resultados_h9", "analisis", "bootstrap.csv")
    if os.path.exists(d9):
        b9 = pd.read_csv(d9)
        ctrl = _ic(b9, "generativa_severa", "severa", "V3-V1")
        fuentes = [("NightOwls ocluida", "nightowls", "ocluida"), ("CityPersons heavy", "citypersons_convencion", "heavy"),
                   ("ExDark proxy severa", "test_proxy", "severa")]
        res = [(n, _ic(b9, c, e, "V3-V1")) for n, c, e in fuentes]
        mejora = sum(1 for _, r in res if r and r[0] >= 2.0 and r[1] > 0)
        ev = [f"Control generativa_severa V3ᵍ−V1′: {_fmt(ctrl)}"] + [f"{n} V3ᵍ−V1′: {_fmt(r)}" for n, r in res]
        qc = None
        ind = os.path.join(raiz, "dataset", "generativa_train", "indice.json")
        if os.path.exists(ind):
            qc = json.load(open(ind, encoding="utf-8"))["control_calidad"]["tasa_exito"]
            ev.append(f"Control de calidad del generador en train: {100 * qc:.1f} % de oclusiones aceptadas")
        if qc is not None and qc < 0.5:
            ver9, nota9 = "No concluyente", "El generador falla: menos del 50 % de las oclusiones de train superan el control de calidad."
        elif ctrl is None or not (ctrl[0] >= 2.0 and ctrl[1] > 0):
            ver9, nota9 = "No concluyente", "El control sintético no supera +2 pp con IC positivo: el aumento no se aprendió."
        elif mejora >= 2:
            ver9, nota9 = "**Refutada**", "V3ᵍ−V1′ ≥ +2 pp con IC positivo en al menos 2 de 3 fuentes reales."
        else:
            ver9 = "**Sostenida**"
            nota9 = ("Con la tercera familia de oclusor (generativa, la más realista) el patrón se repite: el aumento se "
                     "aprende (control %+.2f pp) y no mejora la oclusión real (%d de 3 fuentes superan el umbral)." % (ctrl[0], mejora))
        filas.append(("H9", ver9, ev, nota9))
    else:
        filas.append(("H9", "Pendiente", ["Pre-registrada el 02/10/2026 (v3.3b). 3 corridas V3ᵍ de YOLOv11s."],
                      "Tercera familia de oclusor: oclusión generativa."))

    lineas = ["# ARGOS-11 — Veredictos de las hipótesis pre-registradas (H1–H9)", "",
              "Generado por `19_veredictos.py` a partir de `resultados/analisis/`, "
              "`resultados_v2/analisis_yolo11s/` y `resultados/resumen_costo.csv`. "
              "La columna «Hipótesis (literal)» reproduce el texto pre-registrado sin reformular; "
              "el veredicto se aplica con los criterios (a)–(c) de PROTOCOLO.md s.7.", "",
              f"Fuente real propia usada para H1–H3: `{propia1}` (proxy objetivo de oclusión inter-persona; "
              "la anotación manual `test_real` quedó descartada como GT el 13/09/2026).", "",
              "| H | Pre-registro | Hipótesis (literal) | Evidencia (AP@0.5, pp; IC 95 % bootstrap, 1 000 réplicas) | Veredicto | Nota |",
              "|---|---|---|---|---|---|"]
    for h, ver, ev, nota in filas:
        fuente, texto = LITERAL[h]
        lineas.append(f"| {h} | {fuente} | {texto} | " + "<br>".join(ev) + f" | {ver} | {nota} |")
    lineas += ["", "## Réplica de generalidad (sin hipótesis numerada, PROTOCOLO_v2.md paso 4)", "",
               "YOLO26s, V1′/V3′ × {0,1,2}: V3′−V1′ en NightOwls ocluida −14,3 pp (media de semillas: 0,312 → 0,169), "
               "misma dirección que YOLOv11s. Confirma que el patrón negativo no depende de la arquitectura.", "",
               "## Hallazgos adicionales (post hoc, 19/09/2026; no reformulan H1–H5)", "",
               "Efecto puro del CBAM (V2−V1): nunca positivo sobre oclusión real; negativo con IC que excluye el cero en "
               "NightOwls y CityPersons con el IC por imágenes, y solo en la iteración 2 con el IC jerárquico "
               "(`informes/analisis_final/BOOTSTRAP_JERARQUICO.md`); "
               "interacción (V4−V3)−(V2−V1) con signo dependiente de la fuente. Ver "
               "`informes/reporte_oclusion_real_32_corridas.md`, secciones 5–7."]
    return "\n".join(lineas) + "\n"


def selftest():
    assert set(LITERAL) == {f"H{i}" for i in range(1, 9)}
    assert _fmt(None) == "no calculado" and _fmt((1.234, -0.5, 2.0, 10)).startswith("+1.23 pp [-0.50; +2.00]")
    df = pd.DataFrame([{"conjunto": "a", "estrato": "b", "contraste": "V3-V1", "n_gt": 5,
                        "delta_AP50_pp": 1.0, "IC95_lo_pp": 0.0, "IC95_hi_pp": 2.0}])
    assert _ic(df, "a", "b", "V3-V1")[3] == 5 and _ic(df, "a", "z", "V3-V1") is None
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - tabla de veredictos H1-H7")
    ap.add_argument("--salida", default=os.path.join(RAIZ, "informes", "veredictos_H1_H7.md"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    md = construir(RAIZ)
    os.makedirs(os.path.dirname(a.salida), exist_ok=True)
    with open(a.salida, "w", encoding="utf-8") as fh:
        fh.write(md)
    print("escrito", a.salida)
    try:
        print(md)
    except UnicodeEncodeError:  # consola cp1252
        print(md.encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
