"""Verificación de citas de la RSL: huérfanas, campos y DOI contra Crossref."""
import json, re, sys, time, unicodedata, urllib.request, urllib.parse
from difflib import SequenceMatcher

# uso: citas.py salida.json archivo.bib main1.tex [main2.tex ...]
bib = open(sys.argv[2], encoding="utf-8").read()
tex = "\n".join(open(f, encoding="utf-8").read() for f in sys.argv[3:])
tex_sin_com = re.sub(r"(?<!\\)%.*", "", tex)

entradas = {}
for m in re.finditer(r"@(\w+)\s*\{\s*([^,]+),(.*?)\n\}", bib, re.S):
    tipo, clave, cuerpo = m.group(1).lower(), m.group(2).strip(), m.group(3)
    campos = {}
    for f in re.finditer(r"(\w+)\s*=\s*(\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}|\"[^\"]*\"|\d+)", cuerpo):
        v = f.group(2)
        campos[f.group(1).lower()] = v[1:-1] if v[0] in "{\"" else v
    entradas[clave] = (tipo, campos)

citas = set()
for m in re.finditer(r"\\(?:[a-zA-Z]*cite[a-zA-Z]*|nocite)\*?(?:\[[^\]]*\])*\{([^}]*)\}", tex_sin_com):
    citas |= {c.strip() for c in m.group(1).split(",") if c.strip()}

print("entradas bib:", len(entradas), "| claves citadas:", len(citas))
print("citadas sin entrada:", sorted(citas - set(entradas)))
print("entradas no citadas:", sorted(set(entradas) - citas))
dup = [k for k in re.findall(r"@\w+\s*\{\s*([^,]+),", bib)]
print("claves duplicadas:", sorted({k for k in dup if dup.count(k) > 1}))

req = {"article": ["author", "title", "journaltitle|journal", "year|date"],
       "inproceedings": ["author", "title", "booktitle", "year|date"],
       "misc": ["title", "year|date"], "online": ["title", "url", "year|date"],
       "book": ["author|editor", "title", "publisher", "year|date"],
       "incollection": ["author", "title", "booktitle", "year|date"]}
print("\n== Campos que faltan")
for k, (t, c) in sorted(entradas.items()):
    falta = [r for r in req.get(t, ["title"]) if not any(x in c for x in r.split("|"))]
    if falta:
        print(" ", k, t, "falta:", falta)
    if "doi" in c and not re.match(r"^10\.\d{4,9}/\S+$", c["doi"].strip()):
        print(" ", k, "DOI con formato raro:", c["doi"])
sin_doi = [k for k, (t, c) in entradas.items() if "doi" not in c]
print("sin DOI:", sorted(sin_doi))


def norm(s):
    s = re.sub(r"\\[a-zA-Z]+\s*|[{}\\'`^\"~]", "", s or "")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]", " ", re.sub(r"\s+", " ", s)).strip()


print("\n== Crossref")
res = {}
for k, (t, c) in sorted(entradas.items()):
    doi = c.get("doi", "").strip()
    if not doi:
        continue
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi) + "?mailto=revision.rsl@example.org"
    try:
        r = json.load(urllib.request.urlopen(url, timeout=30))["message"]
    except Exception as e:
        print(" ", k, doi, "NO RESUELVE:", e)
        res[k] = {"error": str(e)}
        continue
    tit = (r.get("title") or [""])[0]
    anio = (r.get("issued", {}).get("date-parts") or [[None]])[0][0]
    aut = (r.get("author") or [{}])[0].get("family", "")
    sim = SequenceMatcher(None, norm(tit), norm(c.get("title"))).ratio()
    anio_bib = (c.get("year") or c.get("date", ""))[:4]
    aut_bib = norm(c.get("author", "").split(" and ")[0])
    retr = [u for u in r.get("update-to", []) + r.get("updated-by", []) if "retract" in str(u.get("type", "")).lower()]
    rel = r.get("relation", {})
    obs = []
    if sim < 0.85: obs.append("título %.2f: '%s'" % (sim, tit[:90]))
    if anio and str(anio) != anio_bib: obs.append("año crossref %s vs bib %s" % (anio, anio_bib))
    if aut and norm(aut) not in aut_bib: obs.append("1.er autor crossref '%s' vs bib '%s'" % (aut, aut_bib[:40]))
    if retr or "is-retracted-by" in rel: obs.append("RETRACTACIÓN: %s" % (retr or rel.get("is-retracted-by")))
    res[k] = {"titulo_cr": tit, "anio_cr": anio, "autor_cr": aut, "sim": round(sim, 3), "obs": obs}
    print(" ", k, "OK" if not obs else "; ".join(obs))
    time.sleep(0.15)
json.dump(res, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
