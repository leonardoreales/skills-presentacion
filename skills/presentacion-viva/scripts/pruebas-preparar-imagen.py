#!/usr/bin/env python3
"""Arnés de preparar-imagen.py con imágenes sintéticas. Uso: python pruebas-preparar-imagen.py [--mutar]
--mutar invierte lo que se espera del duotono: el arnés DEBE salir en rojo (control de que mira algo).
Las pruebas de una herramienta ausente se marcan OMITIDA, nunca VERDE."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("pi", AQUI / "preparar-imagen.py")
pi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pi)
MUTAR = "--mutar" in sys.argv
CAP = pi.capacidades()
resultados = []


def caso(nombre, requiere=()):
    def deco(f):
        faltan = [r for r in requiere if not CAP[r]]
        if faltan:
            resultados.append(("OMITIDA", nombre, "falta " + ", ".join(faltan)))
            return f
        try:
            f()
            resultados.append(("VERDE", nombre, ""))
        except AssertionError as e:
            resultados.append(("ROJO", nombre, str(e)))
        except SystemExit as e:
            resultados.append(("ROJO", nombre, f"SystemExit {e.code}"))
        return f
    return deco


TMP = Path(tempfile.mkdtemp(prefix="pv-img-"))
BG, AC = "#16181C", "#D9A441"


def sintetica(nombre, w=2400, h=1600):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (w, h), (235, 235, 235))
    d = ImageDraw.Draw(img)
    d.ellipse((w * 0.3, h * 0.2, w * 0.7, h * 0.8), fill=(40, 60, 120))
    d.rectangle((w * 0.42, h * 0.35, w * 0.58, h * 0.65), fill=(250, 200, 60))
    p = TMP / nombre
    img.save(p, quality=92)
    return p


def correr(*args):
    return pi.main([*args])


@caso("diagnóstico corre solo con la biblioteca estándar")
def _():
    assert correr("diagnostico") == 0


@caso("falta una herramienta → sale con 3 y nombra la alternativa del nivel 0")
def _():
    sin = dict(CAP, pillow=False)
    try:
        pi.exigir(sin, "pillow")
    except SystemExit as e:
        assert e.code == pi.SIN_HERRAMIENTA, e.code
        return
    raise AssertionError("no salió")


@caso("slug: nombres de salida seguros para una URL")
def _():
    assert pi.slug("C:/x/Bodega Año 1.JPG") == "bodega-ano-1", pi.slug("C:/x/Bodega Año 1.JPG")
    assert pi.slug("¿¿.png") == "imagen"


@caso("tema_de lee --bg y --accent del andamiaje real")
def _():
    t = pi.tema_de(AQUI.parent / "assets" / "andamiaje" / "index.html")
    assert t["bg"].upper() == BG and t["accent"].upper() == AC, t


@caso("formato: AVIF/WebP/JPEG por ancho, recorte 16:9 y <picture> con alt PENDIENTE", requiere=("pillow",))
def _():
    src, out = sintetica("foto.jpg"), TMP / "f"
    assert correr("formato", str(src), "--salida", str(out), "--aspecto", "16:9") == 0
    m = json.loads((out / "manifiesto.json").read_text(encoding="utf-8"))["imagenes"][0]
    assert m["alt"] == m["procedencia"] == m["personas"] == "PENDIENTE"
    w, h = m["tamano"]
    assert abs(w / h - 16 / 9) < 0.01, m["tamano"]
    esperados = 3 * (1 + CAP["avif"] + CAP["webp"])
    assert len(m["ficheros"]) == esperados, (len(m["ficheros"]), esperados)
    assert 'alt="PENDIENTE"' in m["html"] and "<picture>" in m["html"] and 'width="1920"' in m["html"]


@caso("formato: nunca amplía una imagen pequeña", requiere=("pillow",))
def _():
    src, out = sintetica("chica.jpg", 800, 600), TMP / "c"
    correr("formato", str(src), "--salida", str(out))
    m = json.loads((out / "manifiesto.json").read_text(encoding="utf-8"))["imagenes"][0]
    assert max(m["anchos"]) == 800, m["anchos"]


@caso("manifiesto: repetir no borra el alt que ya escribió una persona", requiere=("pillow",))
def _():
    src, out = sintetica("repite.jpg"), TMP / "r"
    correr("formato", str(src), "--salida", str(out))
    ruta = out / "manifiesto.json"
    d = json.loads(ruta.read_text(encoding="utf-8"))
    d["imagenes"][0]["alt"] = "Bodega de activos"
    ruta.write_text(json.dumps(d), encoding="utf-8")
    correr("formato", str(src), "--salida", str(out))
    d = json.loads(ruta.read_text(encoding="utf-8"))
    assert len(d["imagenes"]) == 1 and d["imagenes"][0]["alt"] == "Bodega de activos", d


@caso("duotono con el tema: lo oscuro sale del --bg y lo claro del --accent", requiere=("pillow",))
def _():
    from PIL import Image
    src, out = sintetica("duo.jpg"), TMP / "d"
    tema = AQUI.parent / "assets" / "andamiaje" / "index.html"
    assert correr("duotono", str(src), "--salida", str(out), "--tema-de", str(tema)) == 0
    p = next(out.glob("duo-duotono.*"))
    im = Image.open(p).convert("RGB")
    claro = im.getpixel((10, 10))           # fondo gris claro de la sintética
    oscuro = im.getpixel((im.width * 0.35, im.height * 0.5))  # elipse azul oscuro
    esperado_claro, esperado_oscuro = pi.hex_a_rgb(AC), pi.hex_a_rgb(BG)
    if MUTAR:
        esperado_claro, esperado_oscuro = esperado_oscuro, esperado_claro
    dist = lambda a, b: max(abs(x - y) for x, y in zip(a, b))
    assert dist(claro, esperado_claro) < 30, (claro, esperado_claro)
    assert dist(oscuro, esperado_oscuro) < 60, (oscuro, esperado_oscuro)


@caso("trazo: SVG con paths animables (pathLength=1) y color currentColor", requiere=("opencv", "pillow"))
def _():
    src, out = sintetica("trazo.png"), TMP / "t"
    assert correr("trazo", str(src), "--salida", str(out)) == 0
    svg = (out / "trazo-trazo.svg").read_text(encoding="utf-8")
    n = svg.count("<path ")
    assert n >= 2 and svg.count('pathLength="1"') == n, n
    assert 'stroke="currentColor"' in svg and "#" not in svg, "el SVG no debe llevar colores literales"


@caso("trazo: abre una ruta con tildes (imread falla en Windows)", requiere=("opencv", "pillow"))
def _():
    src = sintetica("gestión-año.png")
    assert correr("trazo", str(src), "--salida", str(TMP / "tt")) == 0


@caso("fondo sin IA (GrabCut): deja transparente el borde y opaco el centro", requiere=("opencv", "pillow"))
def _():
    from PIL import Image
    src, out = sintetica("fondo.png", 900, 600), TMP / "b"
    assert correr("fondo", str(src), "--salida", str(out)) == 0
    im = Image.open(out / "fondo-sin-fondo.png")
    assert im.mode == "RGBA"
    assert im.getpixel((5, 5))[3] < 30 and im.getpixel((450, 300))[3] > 220


@caso("fondo --ia sin rembg → sale con 3, no finge")
def _():
    if CAP["rembg"]:
        return
    src = TMP / "x.png"
    src.write_bytes(b"\x89PNG")
    try:
        correr("fondo", str(src), "--salida", str(TMP / "ia"), "--ia")
    except SystemExit as e:
        assert e.code == pi.SIN_HERRAMIENTA, e.code
        return
    raise AssertionError("no salió")


@caso("fondo --ia nunca usa el modelo por defecto de rembg (bria-rmbg, no comercial)")
def _():
    fuente = (AQUI / "preparar-imagen.py").read_text(encoding="utf-8")
    assert pi.MODELO_IA.startswith("birefnet"), pi.MODELO_IA
    import re  # remove( sin punto delante = la función de rembg, no list.remove
    llamadas = [l for l in fuente.splitlines() if re.search(r"(?<![.\w])remove\(", l) and not l.strip().startswith("#")]
    assert llamadas and all("session=new_session(MODELO_IA)" in l for l in llamadas), llamadas


@caso("kenburns: MP4 1920×1080 de la duración pedida", requiere=("ffmpeg", "pillow"))
def _():
    src, out = sintetica("kb.jpg"), TMP / "k"
    assert correr("kenburns", str(src), "--salida", str(out), "--segundos", "2") == 0
    mp4 = out / "kb-kenburns.mp4"
    if shutil.which("ffprobe"):
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=width,height,nb_frames", "-of", "csv=p=0", str(mp4)],
                           capture_output=True, text=True)
        w, h, n = r.stdout.strip().split(",")
        assert (w, h) == ("1920", "1080") and int(n) == 60, r.stdout
    m = json.loads((out / "manifiesto.json").read_text(encoding="utf-8"))["imagenes"][0]
    assert m["alternativa_texto"] == "PENDIENTE"


shutil.rmtree(TMP, ignore_errors=True)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
for estado, nombre, det in resultados:
    print(f"{estado:8} {nombre}" + (f"  — {det}" if det else ""))
verdes = sum(r[0] == "VERDE" for r in resultados)
rojos = sum(r[0] == "ROJO" for r in resultados)
print(f"\n{verdes} verdes · {rojos} rojos · {len(resultados) - verdes - rojos} omitidas")
sys.exit(1 if rojos else 0)
