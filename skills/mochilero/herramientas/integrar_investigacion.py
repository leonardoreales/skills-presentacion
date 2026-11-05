"""Integra la investigación web (trabajo/investigacion/*.jsonl) en las tablas del Mochilero.

  python integrar_investigacion.py

Valida cada línea (JSON válido, claves exactas, id único, fuente con URL) y escribe datos/<dominio>/<tabla>.csv.
Una tabla con errores no se escribe: se informa y se sigue con las demás.
"""
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from derivar_uiuxpromax import GUIA, escribir_csv  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA = os.path.join(RAIZ, "trabajo", "investigacion")
DOMINIO = {
    "api": "backend", "seguridad-api": "backend", "resiliencia": "backend", "datos": "backend",
    "observabilidad": "backend", "plataforma": "backend", "librerias-backend": "backend",
    "webhooks": "automatizaciones", "n8n": "automatizaciones", "tareas-y-colas": "automatizaciones",
    "integraciones": "automatizaciones", "ia-automatizacion": "automatizaciones",
    "librerias-automatizacion": "automatizaciones", "librerias-front": "front", "rendimiento-web": "front",
    # El bolsillo de presentacion-viva (2026-10-26): catálogo migrado de sus referencias más la investigación web.
    "diagramas": "presentacion", "componentes-narrativos": "presentacion", "recetas": "presentacion",
    "disciplina": "presentacion", "graficas-narrativas": "presentacion", "narrativa": "presentacion",
    "legibilidad": "presentacion", "librerias-efectos": "presentacion", "librerias-video": "presentacion",
    "librerias-graficas": "presentacion", "librerias-ilustracion": "presentacion",
    "librerias-presentacion": "presentacion",
    # Imágenes del usuario (2026-10-26): tratamiento, animación, IA y derechos.
    "librerias-imagen": "presentacion", "tratamiento-imagen": "presentacion",
}
GUIA_IN = GUIA[:14]
LIBRERIA = ["id", "dominio", "categoria", "nombre", "para_que", "cuando_usar", "cuando_no", "alternativas", "licencia",
            "ecosistema", "madurez", "url", "puestos", "palabras_clave", "verificado_el"]


def main():
    todos_ids, informe, errores_totales = set(), [], 0
    for ruta in sorted(glob.glob(os.path.join(ENTRADA, "*.jsonl"))):
        tabla = os.path.basename(ruta)[:-6]
        if tabla not in DOMINIO:
            informe.append(f"IGNORADA {tabla}: no tiene dominio asignado")
            continue
        esquema = LIBRERIA if tabla.startswith("librerias") else GUIA_IN
        filas, errores = [], []
        for n, linea in enumerate(open(ruta, encoding="utf-8"), 1):
            if not linea.strip():
                continue
            try:
                o = json.loads(linea)
            except json.JSONDecodeError as e:
                errores.append(f"línea {n}: JSON roto ({e})")
                continue
            if list(o.keys()) != esquema and set(o.keys()) != set(esquema):
                errores.append(f"línea {n}: claves distintas {sorted(set(o) ^ set(esquema))}")
                continue
            if o["id"] in todos_ids:
                errores.append(f"línea {n}: id repetido {o['id']}")
            todos_ids.add(o["id"])
            url = o.get("fuente") or o.get("url") or ""
            if not re.match(r"https?://", url):
                errores.append(f"{o['id']}: fuente sin URL")
            fila = {k: str(v).strip() for k, v in o.items()}
            if esquema is GUIA_IN:
                fila.update({"aplica_a": "", "estado": "vigente"})
            filas.append(fila)
        if errores:
            errores_totales += len(errores)
            informe.append(f"CON ERRORES {tabla}: {len(errores)} → {errores[:3]}")
            continue
        escribir_csv(os.path.join(RAIZ, "datos", DOMINIO[tabla], tabla + ".csv"),
                     LIBRERIA if esquema is LIBRERIA else GUIA, filas)
        informe.append(f"ok {DOMINIO[tabla]}/{tabla}: {len(filas)} filas")
    print("\n".join(informe) or "No hay investigación que integrar.")
    faltan = sorted(set(DOMINIO) - {os.path.basename(r)[:-6] for r in glob.glob(os.path.join(ENTRADA, "*.jsonl"))})
    if faltan:
        print("Aún sin investigar:", ", ".join(faltan))
    return 1 if errores_totales else 0


if __name__ == "__main__":
    sys.exit(main())
