"""Ids estables del Mochilero (hallazgo 4 de la revisión; decisión de Leonardo, opción A, 2026-09-25).

Un id depende de QUÉ es la fila (su clave en el origen), no de DÓNDE está. El mapa de cada tabla vive en
datos/ids/<tabla>.json:

  {"prefijo": "UX", "ancho": 3, "siguiente": 120,
   "ids": {"<clave de origen>": "UX-001", ...},          # vivos
   "retirados": {"<clave de origen>": "UX-057", ...}}    # ya no están en el origen; su id NUNCA se reutiliza

Reglas:
  - clave conocida          → el mismo id de siempre;
  - clave retirada que vuelve → recupera SU id (fusionar decide, por la huella, si su traducción sigue valiendo);
  - clave nueva             → prefijo-siguiente, y siguiente sube;
  - clave repetida en una misma pasada → error y no se escribe nada.

Sembrar (asignar por primera vez, en el orden del origen) SOLO ocurre con sembrar=True. Si falta el mapa y no se
pidió sembrar, es un error: sembrar sobre un origen que ya cambió volvería a dar ids por posición sin avisar.
"""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_IDS = os.path.join(RAIZ, "datos", "ids")


class ErrorIds(Exception):
    pass


class MapaIds:
    def __init__(self, tabla, prefijo, ancho, sembrar=False, directorio=None):
        self.tabla, self.prefijo, self.ancho = tabla, prefijo, ancho
        self.ruta = os.path.join(directorio or DIR_IDS, tabla + ".json")
        self.vistas = set()
        if os.path.exists(self.ruta):
            with open(self.ruta, encoding="utf-8") as f:
                d = json.load(f)
            if d["prefijo"] != prefijo or d["ancho"] != ancho:
                raise ErrorIds(f"{tabla}: el mapa es {d['prefijo']}/{d['ancho']} y se pidió {prefijo}/{ancho}")
            self.siguiente, self.ids, self.retirados = d["siguiente"], d["ids"], d["retirados"]
            self.sembrando = False
        elif sembrar:
            self.siguiente, self.ids, self.retirados = 1, {}, {}
            self.sembrando = True
        else:
            raise ErrorIds(f"{tabla}: falta {os.path.relpath(self.ruta, RAIZ)}. Si es la primera vez, siembra con "
                           f"--sembrar; si se borró, restáuralo de la copia: re-sembrar desplazaría los ids.")

    def asignar(self, clave):
        clave = str(clave).strip()
        if not clave:
            raise ErrorIds(f"{self.tabla}: fila sin clave de origen")
        if clave in self.vistas:
            raise ErrorIds(f"{self.tabla}: la clave de origen {clave!r} aparece dos veces")
        self.vistas.add(clave)
        if clave in self.ids:
            return self.ids[clave]
        if clave in self.retirados:
            self.ids[clave] = self.retirados.pop(clave)
            return self.ids[clave]
        nuevo = f"{self.prefijo}-{self.siguiente:0{self.ancho}d}"
        self.siguiente += 1
        self.ids[clave] = nuevo
        return nuevo

    def cerrar(self):
        """Retira lo que no apareció en esta pasada y guarda el mapa. Devuelve (nuevas, retiradas)."""
        faltan = [c for c in self.ids if c not in self.vistas]
        for c in faltan:
            self.retirados[c] = self.ids.pop(c)
        os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
        with open(self.ruta, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"prefijo": self.prefijo, "ancho": self.ancho, "siguiente": self.siguiente,
                       "ids": self.ids, "retirados": self.retirados}, f, ensure_ascii=False, indent=1)
            f.write("\n")
        return faltan


def ids_retirados(tabla, directorio=None):
    """Ids retirados de una tabla (vacío si no hay mapa). Lo usa fusionar para no rechazarlos."""
    ruta = os.path.join(directorio or DIR_IDS, tabla + ".json")
    if not os.path.exists(ruta):
        return set()
    with open(ruta, encoding="utf-8") as f:
        return set(json.load(f)["retirados"].values())
