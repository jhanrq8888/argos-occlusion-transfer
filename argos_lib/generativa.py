# -*- coding: utf-8 -*-
"""
H9 (PREREGISTRO_H9.md): tercera familia de oclusor, OCLUSION GENERATIVA.

Un modelo de difusion (Stable Diffusion inpainting) pinta un objeto dentro de
una mascara anclada a un borde de la caja de la persona, con la luz, la
textura y la perspectiva de la escena y sin bordes de pegado. Diferencias con
las familias 1 (parches) y 2 (siluetas): el oclusor no se compone a partir de
un recorte, sino que lo sintetiza el modelo en contexto.

Piezas:
  mascara_oclusor     mascara (en coordenadas de la imagen) anclada a un lado
                      de la caja y escalada por busqueda binaria hasta cubrir
                      la fraccion f de la caja.
  GeneradorOclusion   carga el modelo de inpainting y el segmentador de
                      control; ocluye personas en lotes (varias imagenes a la
                      vez), con control de calidad y reintentos.
  OclusionGenerativa  configuracion del aumento para el entrenamiento: la
                      difusion es demasiado lenta para usarse en linea, asi
                      que el dataset sustituye la imagen leida por una version
                      ocluida generada de antemano (argos_lib.entrenamiento).
"""

import json
import math
import os

import numpy as np

from .oclusion import escribir_imagen, leer_imagen  # noqa: F401

# (prompt, clase COCO equivalente). Diez clases de COCO que no son personas.
OCLUSORES = [("a parked car", "car"), ("a bicycle", "bicycle"), ("a motorcycle", "motorcycle"),
             ("a wooden bench", "bench"), ("a potted plant", "potted plant"),
             ("a fire hydrant", "fire hydrant"), ("a suitcase", "suitcase"),
             ("an open umbrella", "umbrella"), ("a chair", "chair"), ("a truck", "truck")]
SUFIJO = ", at night, low light, realistic photo"
NEGATIVO = "person, people, human, man, woman, child, body, face, legs, clothes, text, watermark"
PROB_LADO = (0.5, 0.2, 0.2, 0.1)      # 0 abajo, 1 izquierda, 2 derecha, 3 arriba
LADO_RECORTE = (2.2, 128)             # lado = max(2.2 x lado mayor de la caja, 128 px)
TAM_SD = 512
PASOS, GUIA = 20, 7.5
UMBRAL_PERSONA = 0.3                  # >30 % de la mascara sigue siendo persona -> fallo (0,5 en el pre-registro; endurecido tras la demo)
REINTENTOS = 2
MIN_LADO_CAJA = 8


# --- Mascara ------------------------------------------------------------------
def _forma(caja, lado, d, r, H, W):
    """Mascara uint8 (H, W) de un oclusor que entra desde `lado` con profundidad d
    (fraccion de la caja a lo largo del eje). r: tres uniformes fijas para que la
    busqueda en d sea monotona. Borde interior en cupula achatada."""
    x1, y1, x2, y2 = caja
    bw, bh = x2 - x1, y2 - y1
    m = np.zeros((H, W), np.uint8)
    anch = 1.1 + 0.4 * r[0]                 # el oclusor es mas ancho que la persona
    desl = (r[1] - 0.5) * 0.3
    if lado in (0, 3):                      # abajo / arriba: barre en x
        cx = (x1 + x2) / 2 + desl * bw
        hw = anch * bw / 2
        xa, xb = int(max(0, math.floor(cx - hw))), int(min(W, math.ceil(cx + hw)))
        if xb <= xa:
            return m
        xs = np.arange(xa, xb)
        u = np.clip((xs + 0.5 - cx) / hw, -1, 1)
        prof = d * bh * (0.75 + 0.25 * np.sqrt(1 - u ** 2))
        for x, p in zip(xs, prof):
            if lado == 0:
                ya, yb = int(round(y2 - p)), int(min(H, math.ceil(y2 + 0.2 * bh)))
            else:
                ya, yb = int(max(0, math.floor(y1 - 0.2 * bh))), int(round(y1 + p))
            ya, yb = max(0, ya), min(H, yb)
            if yb > ya:
                m[ya:yb, x] = 1
    else:                                   # izquierda / derecha: barre en y
        cy = (y1 + y2) / 2 + desl * bh
        hh = anch * bh / 2
        ya, yb = int(max(0, math.floor(cy - hh))), int(min(H, math.ceil(cy + hh)))
        if yb <= ya:
            return m
        ys = np.arange(ya, yb)
        u = np.clip((ys + 0.5 - cy) / hh, -1, 1)
        prof = d * bw * (0.75 + 0.25 * np.sqrt(1 - u ** 2))
        for y, p in zip(ys, prof):
            if lado == 1:
                xa, xb = int(max(0, math.floor(x1 - 0.2 * bw))), int(round(x1 + p))
            else:
                xa, xb = int(round(x2 - p)), int(min(W, math.ceil(x2 + 0.2 * bw)))
            xa, xb = max(0, xa), min(W, xb)
            if xb > xa:
                m[y, xa:xb] = 1
    return m


def cobertura(mascara, caja):
    x1, y1, x2, y2 = (int(round(v)) for v in caja)
    H, W = mascara.shape
    x1, y1, x2, y2 = max(0, x1), max(0, y1), min(W, x2), min(H, y2)
    area = max(1, (x2 - x1) * (y2 - y1))
    return float(mascara[y1:y2, x1:x2].sum()) / area


def mascara_oclusor(caja, f, rnd, H, W, iteraciones=10):
    """Mascara que cubre ~f de la caja, anclada a un lado elegido con PROB_LADO."""
    lado = int(rnd.choice(4, p=PROB_LADO))
    r = rnd.uniform(0, 1, 3)
    lo, hi, mejor = 0.02, 1.4, None
    for _ in range(iteraciones):
        d = (lo + hi) / 2
        m = _forma(caja, lado, d, r, H, W)
        c = cobertura(m, caja)
        if mejor is None or abs(c - f) < abs(mejor[0] - f):
            mejor = (c, m)
        if abs(c - f) < 0.02:
            break
        lo, hi = (d, hi) if c < f else (lo, d)
    return mejor[1], lado


def ventana(caja, H, W):
    """Recorte cuadrado alrededor de la caja (x, y, lado), dentro de la imagen."""
    x1, y1, x2, y2 = caja
    lado = int(round(max(LADO_RECORTE[0] * max(x2 - x1, y2 - y1), LADO_RECORTE[1])))
    lado = int(min(lado, H, W))
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    x = int(round(min(max(cx - lado / 2, 0), W - lado)))
    y = int(round(min(max(cy - lado / 2, 0), H - lado)))
    return x, y, lado


# --- Generador ----------------------------------------------------------------
class GeneradorOclusion:
    def __init__(self, dir_modelo, pesos_seg="yolo11s-seg.pt", device="cuda", lote=4):
        import torch
        from diffusers import DPMSolverMultistepScheduler, StableDiffusionInpaintPipeline
        from ultralytics import YOLO
        self.torch = torch
        pipe = StableDiffusionInpaintPipeline.from_pretrained(
            dir_modelo, torch_dtype=torch.float16, variant="fp16", safety_checker=None,
            requires_safety_checker=False)
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        pipe.set_progress_bar_config(disable=True)
        self.pipe = pipe.to(device)
        self.seg = YOLO(pesos_seg)
        self.device, self.lote = device, lote

    def _pintar(self, recortes, mascaras, prompts, semillas):
        from PIL import Image
        import cv2
        ims = [Image.fromarray(cv2.cvtColor(cv2.resize(c, (TAM_SD, TAM_SD), interpolation=cv2.INTER_AREA),
                                            cv2.COLOR_BGR2RGB)) for c in recortes]
        mks = [Image.fromarray((cv2.resize(m, (TAM_SD, TAM_SD), interpolation=cv2.INTER_NEAREST) * 255).astype(np.uint8))
               for m in mascaras]
        gens = [self.torch.Generator(self.device).manual_seed(int(s)) for s in semillas]
        out = self.pipe(prompt=[p + SUFIJO for p in prompts], negative_prompt=[NEGATIVO] * len(prompts),
                        image=ims, mask_image=mks, num_inference_steps=PASOS, guidance_scale=GUIA,
                        generator=gens, height=TAM_SD, width=TAM_SD).images
        return [cv2.cvtColor(np.asarray(o), cv2.COLOR_RGB2BGR) for o in out]

    def _personas(self, recortes):
        """Union de mascaras de persona (yolo11s-seg) por recorte."""
        import cv2
        res = self.seg.predict(recortes, conf=0.25, classes=[0], retina_masks=True, verbose=False,
                               device=self.device, imgsz=640)
        out = []
        for c, r in zip(recortes, res):
            u = np.zeros(c.shape[:2], np.uint8)
            if r.masks is not None:
                for m in r.masks.data.cpu().numpy():
                    if m.shape != u.shape:
                        m = cv2.resize(m.astype(np.float32), (u.shape[1], u.shape[0]))
                    u |= (m > 0.5).astype(np.uint8)
            out.append(u)
        return out

    def ocluir(self, trabajos, log=None):
        """trabajos: lista de dicts {im (BGR, se modifica), cajas, objetivo: [(idx, f)], semilla}.
        Procesa todas las personas objetivo en lotes de varias imagenes; devuelve por
        trabajo la lista de resultados por persona y la mascara efectiva acumulada."""
        import cv2
        estados = []
        for t in trabajos:
            H, W = t["im"].shape[:2]
            estados.append({"t": t, "cola": list(t["objetivo"]), "intento": 0,
                            "efectiva": np.zeros((H, W), np.uint8), "res": []})
        activos = [e for e in estados if e["cola"]]
        n_lote = 0
        while activos:
            grupo = activos[:self.lote]
            jobs = []
            for e in grupo:
                t = e["t"]; im = t["im"]; H, W = im.shape[:2]
                idx, f = e["cola"][0]
                caja = t["cajas"][idx]
                rnd = np.random.RandomState((t["semilla"] * 100003 + idx * 101 + e["intento"]) % (2 ** 31))
                m, lado = mascara_oclusor(caja, f, rnd, H, W)
                x, y, s = ventana(caja, H, W)
                k = int(rnd.randint(len(OCLUSORES)))
                jobs.append({"e": e, "idx": idx, "f": f, "caja": caja, "m": m, "lado": lado, "win": (x, y, s),
                             "prompt": OCLUSORES[k][0], "clase": OCLUSORES[k][1],
                             "semilla": int(rnd.randint(2 ** 31 - 1))})
            pintados = self._pintar([j["e"]["t"]["im"][j["win"][1]:j["win"][1] + j["win"][2], j["win"][0]:j["win"][0] + j["win"][2]]
                                     for j in jobs],
                                    [j["m"][j["win"][1]:j["win"][1] + j["win"][2], j["win"][0]:j["win"][0] + j["win"][2]] for j in jobs],
                                    [j["prompt"] for j in jobs], [j["semilla"] for j in jobs])
            compuestos = []
            for j, p in zip(jobs, pintados):
                x, y, s = j["win"]
                orig = j["e"]["t"]["im"][y:y + s, x:x + s]
                p = cv2.resize(p, (s, s), interpolation=cv2.INTER_LINEAR if s > TAM_SD else cv2.INTER_AREA)
                a = cv2.GaussianBlur(j["m"][y:y + s, x:x + s].astype(np.float32), (0, 0), max(1.0, s / 256))
                a = np.clip(a * 1.5, 0, 1)[..., None]
                compuestos.append((a * p + (1 - a) * orig).astype(np.uint8))
            personas = self._personas(compuestos)
            for j, comp, per in zip(jobs, compuestos, personas):
                e = j["e"]; t = e["t"]; x, y, s = j["win"]
                mw = j["m"][y:y + s, x:x + s]
                cx1, cy1, cx2, cy2 = (int(round(v)) for v in j["caja"])
                bx1, by1, bx2, by2 = max(cx1 - x, 0), max(cy1 - y, 0), min(cx2 - x, s), min(cy2 - y, s)
                caja_m = np.zeros_like(mw); caja_m[by1:by2, bx1:bx2] = 1
                zona = (mw & caja_m).astype(bool)
                frac_persona = float(per[zona].mean()) if zona.any() else 1.0
                ok = frac_persona <= UMBRAL_PERSONA
                if ok:
                    t["im"][y:y + s, x:x + s] = comp
                    ef = (mw.astype(bool) & ~per.astype(bool)).astype(np.uint8)
                    e["efectiva"][y:y + s, x:x + s] |= ef
                if ok or e["intento"] >= REINTENTOS:
                    e["res"].append({"idx": int(j["idx"]), "f": round(float(j["f"]), 4), "lado": j["lado"],
                                     "prompt": j["prompt"], "clase": j["clase"], "ok": bool(ok),
                                     "intentos": e["intento"] + 1, "frac_persona": round(frac_persona, 3)})
                    e["cola"].pop(0); e["intento"] = 0
                else:
                    e["intento"] += 1
            activos = [e for e in estados if e["cola"]]
            n_lote += 1
            if log and n_lote % 25 == 0:
                log("    lotes %d, imagenes pendientes %d" % (n_lote, len(activos)))
        return [(e["res"], e["efectiva"]) for e in estados]


# --- Aumento para el entrenamiento (sustitucion al leer la imagen) -------------
class OclusionGenerativa:
    """Configuracion del aumento generativo. nivel='imagen': DatasetOclusion no lo
    inserta como transform; en su lugar load_image sustituye la imagen leida por
    una de sus versiones ocluidas con probabilidad p_mosaico (con mosaico) o
    p_sin_mosaico (sin mosaico)."""
    nivel = "imagen"

    def __init__(self, dir_versiones, p_mosaico=0.15, p_sin_mosaico=0.5):
        self.dir_versiones = dir_versiones
        self.p_mosaico, self.p_sin_mosaico = p_mosaico, p_sin_mosaico
        self._indice = None

    @property
    def indice(self):
        if self._indice is None:
            with open(os.path.join(self.dir_versiones, "indice.json"), encoding="utf-8") as fh:
                d = json.load(fh)
            self._indice = {k: v for k, v in d["versiones"].items() if v}
        return self._indice

    def __getstate__(self):
        d = self.__dict__.copy(); d["_indice"] = None
        return d

    def sustituta(self, im_file, con_mosaico, rnd=np.random):
        p = self.p_mosaico if con_mosaico else self.p_sin_mosaico
        if rnd.rand() >= p:
            return None
        vs = self.indice.get(os.path.splitext(os.path.basename(str(im_file)))[0])
        if not vs:
            return None
        return os.path.join(self.dir_versiones, vs[int(rnd.randint(len(vs)))])
