"""Arnés de los ids estables (hallazgo 4). Trabaja en un directorio temporal: nunca toca datos/ids/.

  python herramientas/pruebas_ids.py

Control negativo: el mismo escenario se corre con un asignador POSICIONAL (el de antes del hallazgo 4) y debe
suspender; si pasara, el escenario no estaría midiendo nada.
"""
import json
import os
import shutil
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ids_estables import ErrorIds, MapaIds, ids_retirados  # noqa: E402

ok = total = 0


def caso(nombre, cond):
    global ok, total
    total += 1
    ok += bool(cond)
    print(("✅ " if cond else "❌ ") + nombre)


class Posicional:
    """El asignador de antes: el id es la posición en la pasada."""
    def __init__(self, *_a, **_k):
        self.i = 0

    def asignar(self, _clave):
        self.i += 1
        return f"UX-{self.i:03d}"

    def cerrar(self):
        return []


def escenario(clase, d):
    """Tres pasadas del origen: [a,b,c] → [a,x,c] → [a,b]. Devuelve los ids de cada pasada."""
    pasadas = []
    for origen in (["a", "b", "c"], ["a", "x", "c"], ["a", "b"]):
        m = clase("ux", "UX", 3, sembrar=True, directorio=d)
        pasadas.append({k: m.asignar(k) for k in origen})
        m.cerrar()
    return pasadas


def esperado(p):
    return (p[0] == {"a": "UX-001", "b": "UX-002", "c": "UX-003"}
            and p[1] == {"a": "UX-001", "x": "UX-004", "c": "UX-003"}
            and p[2] == {"a": "UX-001", "b": "UX-002"})


d = tempfile.mkdtemp(prefix="moc-ids-")
try:
    p = escenario(MapaIds, d)
    caso("siembra [a,b,c] → UX-001..003 (reproduce los ids posicionales de hoy)", p[0] == {"a": "UX-001", "b": "UX-002", "c": "UX-003"})
    caso("[a,x,c]: a y c conservan su id, x recibe UX-004 (nunca reutiliza UX-002)", p[1] == {"a": "UX-001", "x": "UX-004", "c": "UX-003"})
    caso("[a,b]: b recupera UX-002 al volver", p[2] == {"a": "UX-001", "b": "UX-002"})
    guardado = json.load(open(os.path.join(d, "ux.json"), encoding="utf-8"))
    caso("tras [a,b]: c y x quedan retirados con su id", guardado["retirados"] == {"c": "UX-003", "x": "UX-004"})
    caso("siguiente = 5: un id retirado jamás se vuelve a emitir", guardado["siguiente"] == 5)
    caso("ids_retirados() los expone para fusionar", ids_retirados("ux", d) == {"UX-003", "UX-004"})

    # Clave repetida en una pasada: error y el mapa no se toca.
    antes = open(os.path.join(d, "ux.json"), encoding="utf-8").read()
    m = MapaIds("ux", "UX", 3, directorio=d)
    try:
        m.asignar("a")
        m.asignar("a")
        caso("clave repetida ⇒ ErrorIds", False)
    except ErrorIds:
        caso("clave repetida ⇒ ErrorIds", True)
    caso("…y el mapa en disco no cambió", open(os.path.join(d, "ux.json"), encoding="utf-8").read() == antes)

    # Sin mapa y sin sembrar: error (re-sembrar en silencio desplazaría los ids).
    try:
        MapaIds("otra", "OT", 3, directorio=d)
        caso("mapa ausente sin --sembrar ⇒ ErrorIds", False)
    except ErrorIds:
        caso("mapa ausente sin --sembrar ⇒ ErrorIds", True)

    # Prefijo o ancho distintos al del mapa: error.
    try:
        MapaIds("ux", "UX", 4, directorio=d)
        caso("ancho distinto al del mapa ⇒ ErrorIds", False)
    except ErrorIds:
        caso("ancho distinto al del mapa ⇒ ErrorIds", True)
finally:
    shutil.rmtree(d, ignore_errors=True)

# Control negativo por mutación.
d = tempfile.mkdtemp(prefix="moc-ids-mut-")
try:
    caso("mutante posicional ⇒ el escenario lo suspende", not esperado(escenario(Posicional, d)))
finally:
    shutil.rmtree(d, ignore_errors=True)

print(f"\n{ok}/{total} {'en verde' if ok == total else 'EN ROJO'}")
sys.exit(0 if ok == total else 1)
