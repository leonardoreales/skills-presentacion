"""Huella SHA-256 del Mochilero (PRO-008): fija la versión que se examina.

  python herramientas/huella.py

Método (reproducible): SHA-256 de las líneas «<sha256 del fichero>  <ruta relativa con />», ordenadas por ruta, una
por fichero. Excluye:
  - CHANGELOG.md, que es donde se anota la huella;
  - .mcp.json, el custodio de la clave de 21st: rotar la clave no es una versión nueva, y así la huella no depende
    de un secreto;
  - __pycache__/, que es caché de Python.
"""
import hashlib
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUIDOS = {"CHANGELOG.md", ".mcp.json"}


def huella(raiz=RAIZ):
    lineas = []
    for base, dirs, ficheros in os.walk(raiz):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in ficheros:
            rel = os.path.relpath(os.path.join(base, f), raiz).replace(os.sep, "/")
            if rel in EXCLUIDOS:
                continue
            with open(os.path.join(base, f), "rb") as h:
                lineas.append(f"{hashlib.sha256(h.read()).hexdigest()}  {rel}")
    lineas.sort(key=lambda l: l.split("  ", 1)[1])
    return hashlib.sha256("\n".join(lineas).encode("utf-8")).hexdigest(), len(lineas)


if __name__ == "__main__":
    h, n = huella()
    print(f"sha256 {h} · {n} ficheros")
