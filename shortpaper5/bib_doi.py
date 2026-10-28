#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera references_es.bib y references_en.bib a partir de references.bib (observacion m3 de la revision del 27/10).
- IEEEtran.bst no imprime el campo doi: se anade al campo note como «DOI: ...» para que cada referencia sea rastreable.
- Las notas de consulta y de numero de articulo quedan en el idioma de cada version.
Uso: python bib_doi.py"""
import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))
NOTAS = {"es": {"Accessed: Jun. 2026": "Consultado: jun. 2026", "Consultado el 20 oct. 2026": "Consultado: 20 oct. 2026",
                "Art. no. 12476": "Art. n.\\textsuperscript{o}~12476"},
         "en": {"Accessed: Jun. 2026": "Accessed: Jun. 2026", "Consultado el 20 oct. 2026": "Accessed: Oct. 20, 2026",
                "Art. no. 12476": "Art. no. 12476",
                "Registro Nacional de Municipalidades 2015": "National Register of Municipalities 2015 (in Spanish)",
                "Registro Nacional de Municipalidades 2023": "National Register of Municipalities 2023 (in Spanish)"}}


def entradas(texto):
    """Divide el .bib en bloques que empiezan con @ (conserva comentarios entre entradas)."""
    return re.split(r"(?m)^(?=@)", texto)


def campo(bloque, nombre):
    m = re.search(r"(?im)^\s*%s\s*=\s*\{(.*)\},?\s*$" % nombre, bloque)
    return m.group(1).strip() if m else None


def convertir(bloque, lang):
    if not bloque.startswith("@"):
        return bloque
    doi = campo(bloque, "doi")
    nota = campo(bloque, "note")
    if nota:
        nota = NOTAS[lang].get(nota, nota)
    partes = [p for p in (nota, "DOI: %s" % doi.replace("_", "\\_").replace("%", "\\%") if doi else None) if p]
    bloque = re.sub(r"(?im)^\s*note\s*=\s*\{.*\},?\s*\n", "", bloque)
    if partes:
        k = bloque.rfind("\n}")                     # cierre de la entrada; lo que sigue son comentarios
        assert k > 0, bloque[:60]
        cuerpo, resto = bloque[:k].rstrip().rstrip(","), bloque[k + 2:]
        bloque = cuerpo + ",\n  note = {{%s}}\n}" % ". ".join(partes) + resto
    return bloque


def main():
    texto = open(os.path.join(AQUI, "references.bib"), encoding="utf-8").read()
    for lang in ("es", "en"):
        salida = "".join(convertir(b, lang) for b in entradas(texto))
        open(os.path.join(AQUI, "references_%s.bib" % lang), "w", encoding="utf-8", newline="\n").write(salida)
        print(lang, salida.count("DOI:"), "DOI")


if __name__ == "__main__":
    main()
