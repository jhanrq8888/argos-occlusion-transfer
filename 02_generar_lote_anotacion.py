#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGOS-11 - Paso 2a: generar el lote de anotacion de oclusion real.

Muestrea instancias de persona del split de prueba y produce una herramienta
HTML autocontenida que ambos anotadores abren en el navegador. No requiere
instalar nada: se abre con doble clic y exporta un CSV al terminar.

Uso:
    python 02_generar_lote_anotacion.py --dataset ./dataset --n 330
    python 02_generar_lote_anotacion.py --dataset ./dataset --piloto 50
    python 02_generar_lote_anotacion.py --selftest

Salida (en <dataset>/anotacion/):
    lote.json        manifiesto de instancias, con orden fijado por semilla
    anotador.html    herramienta de anotacion
    LEEME.txt        instrucciones para el anotador
"""

import argparse
import json
import os
import random
import sys

PLANTILLA_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>ARGOS-11 - Anotacion de oclusion</title>
<style>
 :root { --sin:#4a9; --lig:#7a5; --mod:#c94; --sev:#c55; --nev:#888; }
 * { box-sizing: border-box; }
 body { font-family: system-ui, -apple-system, sans-serif; margin:0;
        background:#1a1a1a; color:#eee; }
 header { padding:10px 16px; background:#111; display:flex;
          align-items:center; gap:16px; flex-wrap:wrap; }
 header h1 { font-size:15px; margin:0; font-weight:600; }
 #progreso { flex:1; height:6px; background:#333; border-radius:3px;
             min-width:120px; }
 #barra { height:100%; background:#4a9; border-radius:3px; width:0; }
 #contador { font-variant-numeric: tabular-nums; font-size:13px; }
 main { display:flex; gap:12px; padding:12px; flex-wrap:wrap; }
 .panel { background:#222; border-radius:6px; padding:8px; }
 .panel h2 { font-size:11px; text-transform:uppercase; letter-spacing:.08em;
             color:#999; margin:0 0 6px; font-weight:600; }
 #ctxWrap { flex:2; min-width:320px; }
 #cropWrap { flex:1; min-width:220px; }
 canvas { max-width:100%; display:block; background:#000; border-radius:4px; }
 footer { padding:12px 16px; background:#111; position:sticky; bottom:0; }
 .fila { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:8px; }
 button { border:none; border-radius:5px; padding:11px 14px; font-size:14px;
          cursor:pointer; color:#fff; font-weight:600; }
 button:disabled { opacity:.35; cursor:not-allowed; }
 .b-sin{background:var(--sin)} .b-lig{background:var(--lig)}
 .b-mod{background:var(--mod)} .b-sev{background:var(--sev)}
 .b-nev{background:var(--nev)} .b-ocl{background:#47a}
 .b-sec{background:#444; font-weight:400; font-size:13px; padding:9px 12px;}
 .marca { background:#333; border:1px solid #555; }
 .marca.on { background:#4a9; border-color:#4a9; }
 kbd { background:#000; border:1px solid #555; border-radius:3px;
       padding:0 4px; font-size:11px; }
 #aviso { padding:10px 16px; background:#5a3; color:#fff; display:none; }
 #fin { padding:40px; text-align:center; display:none; }
</style>
</head>
<body>
<header>
  <h1>Anotacion de oclusion &mdash; <span id="quien"></span></h1>
  <div id="progreso"><div id="barra"></div></div>
  <span id="contador">0 / 0</span>
  <button class="b-sec" onclick="document.getElementById('fimp').click()">Cargar CSV previo</button>
  <input type="file" id="fimp" accept=".csv" style="display:none" onchange="importar(this.files[0])">
  <button class="b-sec" onclick="exportar()">Exportar CSV</button>
</header>
<div id="aviso"></div>

<main id="trabajo">
  <div class="panel" id="ctxWrap">
    <h2>Contexto &mdash; que la tapa?</h2>
    <canvas id="ctx"></canvas>
  </div>
  <div class="panel" id="cropWrap">
    <h2>Detalle</h2>
    <canvas id="crop"></canvas>
  </div>
</main>

<footer>
  <div id="paso1">
    <div class="fila" style="margin-bottom:4px">
      <span style="font-size:13px;color:#ccc;align-self:center;margin-right:6px">
        <b>Paso 1 &mdash; &iquest;Qu&eacute; objeto la tapa?</b> (si no puedes nombrarlo: Nada)
      </span>
    </div>
    <div class="fila">
      <button class="b-sin" onclick="oclusor('nada')">Nada: se ve entera <kbd>1</kbd></button>
      <button class="b-ocl" onclick="oclusor('persona')">Otra persona <kbd>2</kbd></button>
      <button class="b-ocl" onclick="oclusor('vehiculo')">Veh&iacute;culo <kbd>3</kbd></button>
      <button class="b-ocl" onclick="oclusor('objeto')">Mobiliario / objeto <kbd>4</kbd></button>
      <button class="b-ocl" onclick="oclusor('estructura')">Pared / poste / valla <kbd>5</kbd></button>
      <button class="b-ocl" onclick="oclusor('otro')">Otro objeto <kbd>6</kbd></button>
      <button class="b-nev" onclick="marcar('no_evaluable','ninguno')">No evaluable <kbd>0</kbd></button>
    </div>
  </div>
  <div id="paso2" style="display:none">
    <div class="fila" style="margin-bottom:4px">
      <span style="font-size:13px;color:#ccc;align-self:center;margin-right:6px">
        <b>Paso 2 &mdash; &iquest;Cu&aacute;nto tapa</b> <span id="queTapa"></span><b>?</b>
        (piensa en tres bandas: cabeza-hombros / torso / piernas)
      </span>
    </div>
    <div class="fila">
      <button class="b-lig" onclick="grado('ligera')">Ligera: menos de una banda <kbd>1</kbd></button>
      <button class="b-mod" onclick="grado('moderada')">Moderada: una banda o media persona <kbd>2</kbd></button>
      <button class="b-sev" onclick="grado('severa')">Severa: dos bandas o m&aacute;s <kbd>3</kbd></button>
      <button class="b-sec" onclick="volverPaso1()">&larr; Cambiar oclusor <kbd>Esc</kbd></button>
    </div>
  </div>
  <div class="fila">
    <button class="b-sec marca" id="btrunc" onclick="alternarTrunc()">Cortada por el borde de la foto <kbd>T</kbd></button>
    <button class="b-sec" onclick="atras()">&larr; Atras <kbd>&#8592;</kbd></button>
    <span style="font-size:12px;color:#888;align-self:center">
      Oscuridad, ropa oscura o desenfoque NO son oclusion. El borde de la foto tampoco (usa T).
    </span>
  </div>
</footer>

<div id="fin">
  <h2>Lote completado</h2>
  <p>Pulsa <b>Exportar CSV</b> y envia el fichero al responsable.</p>
</div>

<script>
const LOTE = __LOTE__;
const RAIZ = "__RAIZ__";
let i = 0, trunc = false;
const res = {};
const quien = (new URLSearchParams(location.search)).get("anotador")
              || prompt("Nombre o iniciales del anotador:") || "anon";
document.getElementById("quien").textContent = quien;
let t0 = Date.now();

function pintar() {
  if (i >= LOTE.length) {
    document.getElementById("trabajo").style.display = "none";
    document.querySelector("footer").style.display = "none";
    document.getElementById("fin").style.display = "block";
    return;
  }
  const i0 = LOTE[i];
  document.getElementById("contador").textContent = (i + 1) + " / " + LOTE.length;
  document.getElementById("barra").style.width =
      (100 * i / LOTE.length).toFixed(1) + "%";
  trunc = res[i0.id] ? !!res[i0.id].truncado : false;
  document.getElementById("btrunc").classList.toggle("on", trunc);

  const img = new Image();
  img.onload = () => {
    // Contexto: imagen completa con la caja objetivo resaltada.
    const c = document.getElementById("ctx"), g = c.getContext("2d");
    const esc = Math.min(760 / img.width, 520 / img.height, 1);
    c.width = img.width * esc; c.height = img.height * esc;
    g.drawImage(img, 0, 0, c.width, c.height);
    g.strokeStyle = "#0f0"; g.lineWidth = 3;
    g.strokeRect(i0.x * esc, i0.y * esc, i0.w * esc, i0.h * esc);

    // Detalle: recorte con margen del 60% alrededor de la caja.
    const m = 0.6;
    const rx = Math.max(0, i0.x - i0.w * m), ry = Math.max(0, i0.y - i0.h * m);
    const rw = Math.min(img.width - rx, i0.w * (1 + 2 * m));
    const rh = Math.min(img.height - ry, i0.h * (1 + 2 * m));
    const c2 = document.getElementById("crop"), g2 = c2.getContext("2d");
    const e2 = Math.min(380 / rw, 520 / rh, 4);
    c2.width = rw * e2; c2.height = rh * e2;
    g2.imageSmoothingEnabled = false;
    g2.drawImage(img, rx, ry, rw, rh, 0, 0, c2.width, c2.height);
    g2.strokeStyle = "#0f0"; g2.lineWidth = 2;
    g2.strokeRect((i0.x - rx) * e2, (i0.y - ry) * e2, i0.w * e2, i0.h * e2);
  };
  img.onerror = () => {
    const c = document.getElementById("ctx"), g = c.getContext("2d");
    c.width = 600; c.height = 120; g.fillStyle = "#a33";
    g.fillRect(0, 0, 600, 120); g.fillStyle = "#fff"; g.font = "14px sans-serif";
    g.fillText("No se pudo cargar: " + i0.imagen, 12, 60);
  };
  img.src = RAIZ + i0.imagen;
  t0 = Date.now();
}

let oclActual = null;
function oclusor(o) {
  if (o === "nada") { marcar("sin", "nada"); return; }
  oclActual = o;
  document.getElementById("queTapa").textContent = ({persona:"la otra persona", vehiculo:"el vehiculo",
      objeto:"el objeto", estructura:"la estructura", otro:"el objeto"})[o] || o;
  document.getElementById("paso1").style.display = "none";
  document.getElementById("paso2").style.display = "block";
}
function grado(e) { marcar(e, oclActual); }
function volverPaso1() {
  oclActual = null;
  document.getElementById("paso2").style.display = "none";
  document.getElementById("paso1").style.display = "block";
}
function marcar(e, o) {
  const i0 = LOTE[i];
  res[i0.id] = { ...i0, estrato: e, oclusor: o || "", truncado: trunc ? 1 : 0,
                 no_evaluable: e === "no_evaluable" ? 1 : 0,
                 segundos: ((Date.now() - t0) / 1000).toFixed(1) };
  volverPaso1();
  i++; pintar();
}
function alternarTrunc() {
  trunc = !trunc;
  document.getElementById("btrunc").classList.toggle("on", trunc);
}
function atras() { if (i > 0) { i--; pintar(); } }

document.addEventListener("keydown", ev => {
  const enPaso2 = document.getElementById("paso2").style.display === "block";
  if (ev.key.toLowerCase() === "t") { alternarTrunc(); return; }
  if (ev.key === "ArrowLeft") { volverPaso1(); atras(); return; }
  if (enPaso2) {
    const g = {"1":"ligera","2":"moderada","3":"severa"};
    if (g[ev.key]) grado(g[ev.key]);
    else if (ev.key === "Escape") volverPaso1();
    return;
  }
  const o = {"1":"nada","2":"persona","3":"vehiculo","4":"objeto","5":"estructura","6":"otro"};
  if (o[ev.key]) oclusor(o[ev.key]);
  else if (ev.key === "0") marcar("no_evaluable", "ninguno");
});

function exportar() {
  const filas = ["id_instancia,imagen,x,y,w,h,estrato,oclusor,truncado,no_evaluable,segundos"];
  LOTE.forEach(o => {
    const r = res[o.id];
    if (r) filas.push([r.id, r.imagen, r.x, r.y, r.w, r.h, r.estrato, r.oclusor || "",
                       r.truncado, r.no_evaluable, r.segundos].join(","));
  });
  if (filas.length === 1) { alert("Aun no hay nada anotado."); return; }
  const b = new Blob([filas.join("\n")], {type: "text/csv"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(b);
  a.download = "anotacion_" + quien.replace(/[^a-zA-Z0-9]/g, "_") + ".csv";
  a.click();
  const av = document.getElementById("aviso");
  av.textContent = "CSV exportado (" + (filas.length - 1) + " instancias).";
  av.style.display = "block";
  setTimeout(() => { av.style.display = "none"; }, 4000);
}

// Reanudar: carga un CSV exportado antes (p. ej. el del piloto, cuyas 50
// instancias son las primeras del lote completo) y salta a la primera
// instancia sin anotar.
function importar(fichero) {
  if (!fichero) return;
  const lector = new FileReader();
  lector.onload = () => {
    const lineas = lector.result.split(/\r?\n/).filter(l => l.trim());
    const cab = lineas.shift().split(",");
    const col = n => cab.indexOf(n);
    let n = 0;
    const ids = new Set(LOTE.map(o => o.id));
    lineas.forEach(l => {
      const c = l.split(",");
      const id = c[col("id_instancia")];
      if (!ids.has(id)) return;
      res[id] = { id: id, imagen: c[col("imagen")], x: c[col("x")], y: c[col("y")],
                  w: c[col("w")], h: c[col("h")], estrato: c[col("estrato")], oclusor: col("oclusor") >= 0 ? c[col("oclusor")] : "",
                  truncado: c[col("truncado")], no_evaluable: c[col("no_evaluable")],
                  segundos: c[col("segundos")] };
      n++;
    });
    i = 0;
    while (i < LOTE.length && res[LOTE[i].id]) i++;
    const av = document.getElementById("aviso");
    av.textContent = "Cargadas " + n + " instancias; continuando en la " + (i + 1) + ".";
    av.style.display = "block";
    setTimeout(() => { av.style.display = "none"; }, 5000);
    pintar();
  };
  lector.readAsText(fichero);
}

pintar();
</script>
</body>
</html>
"""

LEEME = """ARGOS-11 - Anotacion de oclusion real
=====================================

1. Lee primero GUIA_DE_ANOTACION.md entera. En especial la regla de la
   Seccion 2: OSCURIDAD NO ES OCLUSION.

2. Abre anotador.html con doble clic (Chrome o Firefox). Te pedira tu
   nombre o iniciales.

3. Atajos de teclado:
       1  sin oclusion        3  moderada       0  no evaluable
       2  ligera              4  severa         T  truncado por borde
       flecha izquierda: volver a la instancia anterior

4. Al terminar pulsa "Exportar CSV". Puedes exportar antes de acabar
   para guardar avance parcial y reanudar despues con "Cargar CSV previo".
   Las 50 instancias del piloto son las primeras del lote completo: carga
   tu CSV del piloto y la herramienta salta a la instancia 51.

5. NO consultes con el otro anotador durante el trabajo. Las
   discrepancias se resuelven despues, por consenso.

IMPORTANTE: si el navegador no muestra las imagenes, es que bloquea el
acceso a ficheros locales. Solucion: abre una consola en la carpeta
<dataset>/ y ejecuta

    python -m http.server 8000

y luego entra en http://localhost:8000/anotacion/anotador.html
"""


def cargar_instancias(dataset, split="test"):
    """Lee las etiquetas YOLO del split y devuelve la lista de instancias."""
    dir_lab = os.path.join(dataset, "labels", split)
    dir_img = os.path.join(dataset, "images", split)
    if not os.path.isdir(dir_lab):
        sys.exit("ERROR: no existe %s. Ejecutar antes el paso 1." % dir_lab)

    try:
        from PIL import Image
    except ImportError:
        sys.exit("ERROR: falta Pillow. Instalar con: pip install Pillow")

    imgs = {os.path.splitext(f)[0]: f for f in os.listdir(dir_img)}
    instancias = []
    for fl in sorted(os.listdir(dir_lab)):
        base = os.path.splitext(fl)[0]
        nombre = imgs.get(base)
        if nombre is None:
            continue
        ruta = os.path.join(dir_img, nombre)
        try:
            with Image.open(ruta) as im:
                W, H = im.size
        except Exception:
            continue
        with open(os.path.join(dir_lab, fl), encoding="utf-8") as fh:
            for k, linea in enumerate(fh):
                p = linea.split()
                if len(p) != 5:
                    continue
                xc, yc, w, h = (float(v) for v in p[1:])
                instancias.append({
                    "id": "%s#%d" % (base, k),
                    "imagen": "%s/%s" % (split, nombre),
                    "x": round((xc - w / 2) * W, 1),
                    "y": round((yc - h / 2) * H, 1),
                    "w": round(w * W, 1),
                    "h": round(h * H, 1),
                    "alto_px": round(h * H, 1),
                })
    return instancias


def generar(dataset, n, semilla, piloto, min_alto):
    inst = cargar_instancias(dataset)
    print("Instancias de persona en test: %d" % len(inst))

    descartadas = [o for o in inst if o["alto_px"] < min_alto]
    inst = [o for o in inst if o["alto_px"] >= min_alto]
    print("Descartadas por altura < %d px: %d" % (min_alto, len(descartadas)))
    print("Candidatas a anotar: %d" % len(inst))

    if not inst:
        sys.exit("ERROR: no quedan instancias anotables.")

    rnd = random.Random(semilla)
    rnd.shuffle(inst)
    objetivo = piloto if piloto else n
    lote = inst[:min(objetivo, len(inst))]

    if len(lote) < objetivo:
        print("AVISO: solo hay %d instancias, se pidieron %d."
              % (len(lote), objetivo))

    salida = os.path.join(dataset, "anotacion")
    os.makedirs(salida, exist_ok=True)

    with open(os.path.join(salida, "lote.json"), "w", encoding="utf-8") as fh:
        json.dump({"semilla": semilla, "piloto": bool(piloto),
                   "n": len(lote), "instancias": lote}, fh, indent=1)

    html = (PLANTILLA_HTML
            .replace("__LOTE__", json.dumps(lote))
            .replace("__RAIZ__", "../images/"))
    with open(os.path.join(salida, "anotador.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    with open(os.path.join(salida, "LEEME.txt"), "w", encoding="utf-8") as fh:
        fh.write(LEEME)

    print("\nGenerado en %s" % os.path.abspath(salida))
    print("  lote.json      %d instancias (semilla %d)" % (len(lote), semilla))
    print("  anotador.html  abrir con doble clic")
    print("  LEEME.txt      instrucciones")
    if piloto:
        print("\nLOTE PILOTO: los dos anotadores etiquetan ESTAS MISMAS %d"
              % len(lote))
        print("instancias, y luego se calcula el kappa con 03_calcular_kappa.py.")
        print("Si kappa < 0,60 hay que revisar la guia y repetir.")
    else:
        print("\nCuotas a vigilar: >=300 evaluables y >=50 por estrato.")
        print("Con %d instancias en el lote hay margen si la distribucion" % len(lote))
        print("de oclusion acompana; el estrato severo es el que suele faltar.")
    return lote


def selftest():
    """Verifica la carga de instancias y la generacion sobre datos sinteticos."""
    import shutil
    import tempfile
    try:
        from PIL import Image
    except ImportError:
        sys.exit("ERROR: falta Pillow.")

    tmp = tempfile.mkdtemp(prefix="lote_test_")
    ds = os.path.join(tmp, "dataset")
    os.makedirs(os.path.join(ds, "images", "test"))
    os.makedirs(os.path.join(ds, "labels", "test"))

    # Imagen 200x100 con dos personas: una alta (50 px) y una diminuta (5 px).
    Image.new("RGB", (200, 100)).save(os.path.join(ds, "images", "test", "x.jpg"))
    with open(os.path.join(ds, "labels", "test", "x.txt"), "w") as f:
        f.write("0 0.250000 0.350000 0.200000 0.500000\n")   # h = 50 px
        f.write("0 0.800000 0.800000 0.050000 0.050000\n")   # h =  5 px

    print("--- generando lote sobre dataset sintetico ---\n")
    lote = generar(ds, n=10, semilla=0, piloto=0, min_alto=15)

    print("\n" + "=" * 58)
    print("VERIFICACION")
    print("=" * 58)
    fallos = []

    def comp(desc, obt, esp):
        ok = obt == esp
        print("  [%s] %-42s %s" % ("ok" if ok else "FALLA", desc, obt))
        if not ok:
            fallos.append(desc)

    comp("instancia diminuta descartada", len(lote), 1)
    o = lote[0]
    # xc=0.25,w=0.2 sobre 200 px -> x = (0.25-0.1)*200 = 30 ; w = 40
    # yc=0.35,h=0.5 sobre 100 px -> y = (0.35-0.25)*100 = 10 ; h = 50
    comp("conversion a pixeles: x", o["x"], 30.0)
    comp("conversion a pixeles: y", o["y"], 10.0)
    comp("conversion a pixeles: w", o["w"], 40.0)
    comp("conversion a pixeles: h", o["h"], 50.0)
    comp("id de instancia", o["id"], "x#0")
    comp("ruta relativa de imagen", o["imagen"], "test/x.jpg")

    html = open(os.path.join(ds, "anotacion", "anotador.html"),
                encoding="utf-8").read()
    comp("HTML sin marcadores sin sustituir",
         ("__LOTE__" in html or "__RAIZ__" in html), False)
    comp("HTML incluye la instancia", '"x#0"' in html, True)

    # Determinismo: misma semilla -> mismo lote.
    l2 = generar(ds, n=10, semilla=0, piloto=0, min_alto=15)
    comp("lote reproducible con la misma semilla",
         [q["id"] for q in l2], [q["id"] for q in lote])

    shutil.rmtree(tmp)
    print()
    if fallos:
        print("AUTOTEST FALLIDO (%d): %s" % (len(fallos), ", ".join(fallos)))
        return 1
    print("AUTOTEST SUPERADO: 10/10 comprobaciones.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="ARGOS-11 - lote de anotacion")
    ap.add_argument("--dataset", default="./dataset")
    ap.add_argument("--n", type=int, default=330,
                    help="instancias del lote completo (def. 330, Seccion 2.4)")
    ap.add_argument("--piloto", type=int, default=0,
                    help="genera un lote piloto de N instancias (def. 50)")
    ap.add_argument("--semilla", type=int, default=11)
    ap.add_argument("--min-alto", type=int, default=15,
                    help="descarta cajas mas bajas que N px (def. 15)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())
    generar(args.dataset, args.n, args.semilla, args.piloto, args.min_alto)


if __name__ == "__main__":
    main()