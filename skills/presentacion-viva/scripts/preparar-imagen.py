#!/usr/bin/env python3
"""Prepara las imágenes del usuario para una presentación viva: formato, recorte, color del tema, trazo, fondo y
Ken Burns. Es el NIVEL 1-2 de la escalera de references/imagenes.md; el nivel 0 (cualquier navegador, sin instalar
nada) es assets/taller-imagen/index.html, y la página final nunca depende de este script.

Cada operación declara qué necesita. Si falta, lo dice, sale con código 3 y nombra el remedio: nunca finge.
  Pillow  -> formato, duotono            (pip install Pillow)
  OpenCV  -> trazo, fondo                (pip install opencv-python-headless numpy)
  ffmpeg  -> kenburns                    (https://ffmpeg.org/download.html)
  rembg   -> fondo --ia (opcional, local; usa birefnet-general, MIT, y lo descarga la primera vez)

Uso:
  python preparar-imagen.py diagnostico
  python preparar-imagen.py formato  <img...> --salida DIR [--anchos 640,1280,1920] [--aspecto 16:9] [--foco 0.5,0.4]
  python preparar-imagen.py duotono  <img...> --salida DIR (--tema-de index.html | --sombra HEX --luz HEX)
  python preparar-imagen.py trazo    <img>    --salida DIR [--detalle 0.5] [--max-trazos 120]
  python preparar-imagen.py fondo    <img>    --salida DIR [--ia]
  python preparar-imagen.py kenburns <img>    --salida DIR [--segundos 6] [--zoom 1.15] [--foco 0.5,0.4]

Toda salida se apunta en DIR/manifiesto.json con `alt`, `procedencia` y `personas` en PENDIENTE: la página no se
publica hasta que una persona los rellene (WCAG 1.1.1, licencia de la imagen y Ley 1581 si salen personas).
Sin dependencias obligatorias: la biblioteca estándar basta para `diagnostico`.
"""
import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PENDIENTE = "PENDIENTE"
MODELO_IA = "birefnet-general"  # nunca el por defecto de rembg (bria-rmbg, no comercial)
SIN_HERRAMIENTA = 3


def hay(modulo):
    return importlib.util.find_spec(modulo) is not None


def capacidades():
    c = {"pillow": hay("PIL"), "opencv": hay("cv2") and hay("numpy"), "ffmpeg": shutil.which("ffmpeg") is not None,
         "rembg": hay("rembg"), "avif": False, "webp": False}
    if c["pillow"]:
        from PIL import features
        c["avif"] = bool(features.check("avif"))
        c["webp"] = bool(features.check("webp"))
    return c


REMEDIO = {
    "pillow": "pip install Pillow",
    "opencv": "pip install opencv-python-headless numpy",
    "ffmpeg": "instala ffmpeg (https://ffmpeg.org/download.html) o haz el Ken Burns en la página con GSAP "
              "(references/imagenes.md §4)",
}
NIVEL0 = "assets/taller-imagen/index.html (abre en cualquier navegador, no instala nada)"


def exigir(cap, *nombres):
    faltan = [n for n in nombres if not cap[n]]
    if faltan:
        for n in faltan:
            print(f"FALTA  {n}: {REMEDIO[n]}", file=sys.stderr)
        print(f"ALTERNATIVA  sin instalar nada: {NIVEL0}", file=sys.stderr)
        sys.exit(SIN_HERRAMIENTA)


def slug(ruta):
    """Nombre seguro para una URL: sin tildes, ñ ni espacios («Bodega año 1.jpg» -> «bodega-ano-1»)."""
    import unicodedata
    s = unicodedata.normalize("NFD", Path(ruta).stem)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "imagen"


def hex_a_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise SystemExit(f"Color no válido: {h!r} (se espera #RRGGBB)")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def tema_de(pagina):
    """Lee los roles --bg, --ink y --accent del :root de la página: el color sale del tema, nunca de un literal."""
    css = Path(pagina).read_text(encoding="utf-8")
    roles = {}
    for rol in ("bg", "ink", "accent"):
        m = re.search(r"--" + rol + r"\s*:\s*(#[0-9a-fA-F]{3,6})\b", css)
        if m:
            roles[rol] = m.group(1)
    if "bg" not in roles or ("accent" not in roles and "ink" not in roles):
        raise SystemExit(f"{pagina}: no encuentro --bg y --accent/--ink en :root")
    return roles


def par_float(texto, nombre):
    try:
        a, b = (float(v) for v in texto.split(","))
    except ValueError:
        raise SystemExit(f"--{nombre} espera dos números separados por coma (p. ej. 0.5,0.4)")
    if not (0 <= a <= 1 and 0 <= b <= 1):
        raise SystemExit(f"--{nombre}: los valores van de 0 a 1")
    return a, b


def aspecto(texto):
    if not texto:
        return None
    m = re.fullmatch(r"(\d+(?:\.\d+)?)[:/x](\d+(?:\.\d+)?)", texto)
    if not m:
        raise SystemExit("--aspecto espera ancho:alto (p. ej. 16:9)")
    return float(m.group(1)) / float(m.group(2))


class Manifiesto:
    def __init__(self, salida):
        self.ruta = Path(salida) / "manifiesto.json"
        self.datos = json.loads(self.ruta.read_text(encoding="utf-8")) if self.ruta.exists() else {"imagenes": []}

    def anotar(self, origen, operacion, ficheros, **extra):
        entrada = {"origen": Path(origen).name, "operacion": operacion,
                   "ficheros": [Path(f).name for f in ficheros], "alt": PENDIENTE, "procedencia": PENDIENTE,
                   "personas": PENDIENTE}
        entrada.update(extra)
        previas = {(e["origen"], e["operacion"]): e for e in self.datos["imagenes"]}
        vieja = previas.get((entrada["origen"], operacion))
        if vieja:  # repetir una operación no borra lo que una persona ya rellenó
            for k in ("alt", "procedencia", "personas"):
                if vieja.get(k) not in (None, PENDIENTE):
                    entrada[k] = vieja[k]
            self.datos["imagenes"].remove(vieja)
        self.datos["imagenes"].append(entrada)

    def guardar(self):
        self.ruta.write_text(json.dumps(self.datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def abrir(ruta):
    from PIL import Image, ImageOps
    img = Image.open(ruta)
    img = ImageOps.exif_transpose(img)  # la foto del móvil llega girada si no se aplica su EXIF
    return img


def recortar(img, proporcion, foco):
    from PIL import ImageOps
    if not proporcion:
        return img
    w, h = img.size
    if abs(w / h - proporcion) < 0.01:
        return img
    nuevo = (w, round(w / proporcion)) if w / h < proporcion else (round(h * proporcion), h)
    return ImageOps.fit(img, nuevo, centering=foco)


def guardar_variantes(img, base, anchos, cap):
    """Guarda cada ancho en AVIF, WebP y JPEG (el último como respaldo universal). Nunca amplía."""
    formatos = [f for f, ok in (("avif", cap["avif"]), ("webp", cap["webp"])) if ok] + ["jpg"]
    escritos, por_formato = [], {f: [] for f in formatos}
    w0 = img.size[0]
    anchos = sorted({min(a, w0) for a in anchos})
    tiene_alfa = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    for a in anchos:
        r = img if a == w0 else img.resize((a, round(img.size[1] * a / w0)), resample=3)  # 3 = LANCZOS
        for f in formatos:
            if f == "jpg" and tiene_alfa:
                f_real, im = "png", r
            else:
                f_real, im = f, (r.convert("RGB") if f == "jpg" else r)
            p = base.with_name(f"{base.name}-{a}.{f_real}")
            opciones = {"avif": {"quality": 60}, "webp": {"quality": 80}, "jpg": {"quality": 82, "optimize": True,
                                                                                  "progressive": True}}.get(f_real, {})
            im.save(p, **opciones)
            escritos.append(p)
            por_formato[f].append((p, a))
    return escritos, por_formato, anchos


def html_picture(por_formato, alto_sobre_ancho, ancho_max):
    tipos = {"avif": "image/avif", "webp": "image/webp"}
    lineas = ["<picture>"]
    for f, lista in por_formato.items():
        if f in tipos:
            srcset = ", ".join(f"media/{p.name} {a}w" for p, a in lista)
            lineas.append(f'  <source type="{tipos[f]}" srcset="{srcset}" sizes="(min-width: 900px) 60vw, 100vw">')
    respaldo = por_formato["jpg"]
    srcset = ", ".join(f"media/{p.name} {a}w" for p, a in respaldo)
    lineas.append(f'  <img src="media/{respaldo[-1][0].name}" srcset="{srcset}" '
                  f'sizes="(min-width: 900px) 60vw, 100vw" width="{ancho_max}" '
                  f'height="{round(ancho_max * alto_sobre_ancho)}" loading="lazy" decoding="async" alt="{PENDIENTE}">')
    lineas.append("</picture>")
    return "\n".join(lineas)


def cmd_diagnostico(a, cap):
    print("Escalera de capacidades (references/imagenes.md):")
    print(f"  nivel 0  navegador .......... siempre: {NIVEL0} + CSS en la página")
    print(f"  nivel 1  Pillow ............. {'sí' if cap['pillow'] else 'NO -> ' + REMEDIO['pillow']}"
          + (f"  (AVIF {'sí' if cap['avif'] else 'no'} · WebP {'sí' if cap['webp'] else 'no'})" if cap["pillow"] else ""))
    print(f"  nivel 2  OpenCV ............. {'sí' if cap['opencv'] else 'NO -> ' + REMEDIO['opencv']}")
    print(f"  nivel 2  ffmpeg ............. {'sí' if cap['ffmpeg'] else 'NO -> ' + REMEDIO['ffmpeg']}")
    print(f"  nivel 3  rembg (IA local) ... {'sí' if cap['rembg'] else 'no (opcional; sin él, fondo usa GrabCut)'}")
    return 0


def cmd_formato(a, cap):
    exigir(cap, "pillow")
    anchos = [int(v) for v in a.anchos.split(",")]
    foco, prop = par_float(a.foco, "foco"), aspecto(a.aspecto)
    man = Manifiesto(a.salida)
    for ruta in a.entradas:
        img = recortar(abrir(ruta), prop, foco)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.mode or "transparency" in img.info else "RGB")
        base = Path(a.salida) / slug(ruta)
        escritos, por_formato, usados = guardar_variantes(img, base, anchos, cap)
        if img.size[0] < max(anchos):
            print(f"AVISO  {Path(ruta).name}: mide {img.size[0]} px de ancho; no se amplía (proyector 1920 px)")
        fragmento = html_picture(por_formato, img.size[1] / img.size[0], usados[-1])
        man.anotar(ruta, "formato", escritos, anchos=usados, tamano=list(img.size), html=fragmento)
        print(f"OK     {Path(ruta).name}: {len(escritos)} ficheros ({', '.join(por_formato)}) · {img.size[0]}×{img.size[1]}")
    man.guardar()
    return 0


def cmd_duotono(a, cap):
    exigir(cap, "pillow")
    from PIL import ImageOps
    if a.tema_de:
        t = tema_de(a.tema_de)
        sombra, luz = t["bg"], t.get("accent", t.get("ink"))
    elif a.sombra and a.luz:
        sombra, luz = a.sombra, a.luz
    else:
        raise SystemExit("duotono necesita --tema-de <index.html> o --sombra y --luz")
    man = Manifiesto(a.salida)
    for ruta in a.entradas:
        img = abrir(ruta)
        alfa = img.getchannel("A") if "A" in img.getbands() else None
        gris = ImageOps.autocontrast(img.convert("L"), cutoff=1)
        duo = ImageOps.colorize(gris, black=hex_a_rgb(sombra), white=hex_a_rgb(luz))
        if alfa is not None:
            duo.putalpha(alfa)
        p = Path(a.salida) / f"{slug(ruta)}-duotono.{'webp' if cap['webp'] else 'png'}"
        duo.save(p, **({"quality": 82} if p.suffix == ".webp" else {}))
        man.anotar(ruta, "duotono", [p], sombra=sombra, luz=luz)
        print(f"OK     {Path(ruta).name} -> {p.name} (sombra {sombra} · luz {luz})")
    man.guardar()
    return 0


def cmd_trazo(a, cap):
    """Contornos de la imagen como <path> con pathLength=1: se animan con strokeDashoffset 1 -> 0 (sin DrawSVG,
    que GSAP 3.12.5 no trae en cdnjs). El color es currentColor: lo pone la página con su token."""
    exigir(cap, "opencv")
    import cv2
    import numpy as np
    ruta = a.entradas[0]
    datos = np.fromfile(ruta, dtype=np.uint8)  # imread no abre rutas con tildes en Windows
    img = cv2.imdecode(datos, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise SystemExit(f"No pude leer {ruta}")
    h, w = img.shape
    escala = min(1.0, 1600 / max(w, h))
    if escala < 1:
        img = cv2.resize(img, (round(w * escala), round(h * escala)), interpolation=cv2.INTER_AREA)
        h, w = img.shape
    d = min(max(a.detalle, 0.0), 1.0)
    k = 7 if d < 0.34 else 5 if d < 0.67 else 3  # menos detalle = más suavizado = menos bordes menudos
    suave = cv2.GaussianBlur(img, (k, k), 0)
    mediana = float(np.median(suave))  # regla de la mediana para Canny: umbrales a ±33 % de la mediana
    bajo, alto = int(max(0, 0.67 * mediana)), int(min(255, 1.33 * mediana))
    bordes = cv2.Canny(suave, bajo, max(alto, bajo + 1))
    contornos, _ = cv2.findContours(bordes, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    minimo = (0.02 + 0.08 * (1 - d)) * max(w, h)
    elegidos = sorted((c for c in contornos if cv2.arcLength(c, False) >= minimo),
                      key=lambda c: cv2.arcLength(c, False), reverse=True)[:a.max_trazos]
    paths = []
    for c in elegidos:
        aprox = cv2.approxPolyDP(c, 0.002 * max(w, h) + 1.0, False)
        pts = aprox.reshape(-1, 2)
        if len(pts) < 2:
            continue
        dd = "M" + " L".join(f"{x},{y}" for x, y in pts)
        paths.append(f'  <path d="{dd}" pathLength="1"/>')
    if not paths:
        print("AVISO  no salió ningún trazo: sube --detalle o usa una imagen con más contraste", file=sys.stderr)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" class="trazo" fill="none" '
           f'stroke="currentColor" stroke-width="{max(1.5, round(max(w, h) / 600, 1))}" stroke-linecap="round" '
           f'stroke-linejoin="round" role="img" aria-label="{PENDIENTE}">\n' + "\n".join(paths) + "\n</svg>\n")
    p = Path(a.salida) / f"{slug(ruta)}-trazo.svg"
    p.write_text(svg, encoding="utf-8")
    man = Manifiesto(a.salida)
    man.anotar(ruta, "trazo", [p], trazos=len(paths), bytes=p.stat().st_size)
    man.guardar()
    print(f"OK     {Path(ruta).name} -> {p.name}: {len(paths)} trazos · {p.stat().st_size // 1024} KB")
    if p.stat().st_size > 400_000:
        print("AVISO  más de 400 KB de SVG: baja --detalle o --max-trazos", file=sys.stderr)
    return 0


def cmd_fondo(a, cap):
    ruta = a.entradas[0]
    p = Path(a.salida) / f"{slug(ruta)}-sin-fondo.png"
    if a.ia:
        if not cap["rembg"]:
            print(f"FALTA  rembg (IA local): pip install rembg — la primera vez descarga el modelo {MODELO_IA} "
                  "(cientos de MB); references/imagenes.md §5", file=sys.stderr)
            print("ALTERNATIVA  sin --ia, este mismo comando usa GrabCut (OpenCV, sin IA ni red)", file=sys.stderr)
            sys.exit(SIN_HERRAMIENTA)
        from rembg import new_session, remove
        # Modelo EXPLÍCITO: el de rembg por defecto es bria-rmbg (RMBG-2.0, CC BY-NC 4.0, no comercial; medido en
        # rembg/session_factory.py el 2026-10-26). birefnet-general es MIT. Mochilero: librerias-imagen.
        p.write_bytes(remove(Path(ruta).read_bytes(), session=new_session(MODELO_IA)))
        metodo = f"rembg {MODELO_IA} (IA local, MIT)"
    else:
        exigir(cap, "opencv")
        import cv2
        import numpy as np
        img = cv2.imdecode(np.fromfile(ruta, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise SystemExit(f"No pude leer {ruta}")
        h, w = img.shape[:2]
        mascara = np.zeros((h, w), np.uint8)
        margen = (round(w * 0.05), round(h * 0.05))
        rect = (margen[0], margen[1], w - 2 * margen[0], h - 2 * margen[1])
        bg, fg = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
        cv2.grabCut(img, mascara, rect, bg, fg, 5, cv2.GC_INIT_WITH_RECT)
        alfa = np.where((mascara == cv2.GC_FGD) | (mascara == cv2.GC_PR_FGD), 255, 0).astype("uint8")
        alfa = cv2.GaussianBlur(alfa, (3, 3), 0)
        rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        rgba[:, :, 3] = alfa
        ok, buf = cv2.imencode(".png", rgba)
        p.write_bytes(buf.tobytes())
        metodo = "GrabCut (OpenCV, sin IA)"
        cobertura = float((alfa > 127).mean())
        if cobertura < 0.05 or cobertura > 0.95:
            print(f"AVISO  la figura ocupa {cobertura:.0%} de la imagen: el recorte probablemente falló; "
                  "revisa a ojo o prueba --ia", file=sys.stderr)
    man = Manifiesto(a.salida)
    man.anotar(ruta, "fondo", [p], metodo=metodo)
    man.guardar()
    print(f"OK     {Path(ruta).name} -> {p.name} con {metodo}. Revísalo a ojo antes de usarlo.")
    return 0


def cmd_kenburns(a, cap):
    exigir(cap, "ffmpeg")
    ruta = a.entradas[0]
    fx, fy = par_float(a.foco, "foco")
    fps, seg = 30, a.segundos
    cuadros = round(fps * seg)
    z = max(1.01, min(a.zoom, 1.6))
    paso = (z - 1) / cuadros
    p = Path(a.salida) / f"{slug(ruta)}-kenburns.mp4"
    # Escalar a 4K primero evita el temblor de zoompan; el encuadre lo fija el foco. Determinista: misma entrada,
    # mismo MP4 en cada máquina con la misma versión de ffmpeg.
    vf = (f"scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,"
          f"zoompan=z='min(1+{paso:.6f}*on,{z})':x='(iw-iw/zoom)*{fx}':y='(ih-ih/zoom)*{fy}':"
          f"d={cuadros}:s=1920x1080:fps={fps},format=yuv420p")
    orden = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(ruta), "-vf", vf, "-frames:v", str(cuadros),
             "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-movflags", "+faststart", str(p)]
    r = subprocess.run(orden, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("ffmpeg falló: " + r.stderr.strip()[-400:])
    man = Manifiesto(a.salida)
    man.anotar(ruta, "kenburns", [p], segundos=seg, zoom=z, foco=[fx, fy],
               alternativa_texto=PENDIENTE)  # un MP4 mudo necesita su alternativa en texto (WCAG 1.2.1)
    man.guardar()
    print(f"OK     {Path(ruta).name} -> {p.name}: {seg} s · 1920×1080 · zoom {z}")
    return 0


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("operacion", choices=["diagnostico", "formato", "duotono", "trazo", "fondo", "kenburns"])
    ap.add_argument("entradas", nargs="*")
    ap.add_argument("--salida", default="media")
    ap.add_argument("--anchos", default="640,1280,1920")
    ap.add_argument("--aspecto")
    ap.add_argument("--foco", default="0.5,0.5")
    ap.add_argument("--tema-de")
    ap.add_argument("--sombra")
    ap.add_argument("--luz")
    ap.add_argument("--detalle", type=float, default=0.5)
    ap.add_argument("--max-trazos", type=int, default=120)
    ap.add_argument("--ia", action="store_true")
    ap.add_argument("--segundos", type=float, default=6)
    ap.add_argument("--zoom", type=float, default=1.15)
    a = ap.parse_args(argv)
    cap = capacidades()
    if a.operacion != "diagnostico":
        if not a.entradas:
            ap.error(f"{a.operacion} necesita al menos una imagen")
        for e in a.entradas:
            if not Path(e).is_file():
                ap.error(f"no existe {e}")
        Path(a.salida).mkdir(parents=True, exist_ok=True)
    return globals()["cmd_" + a.operacion](a, cap)


if __name__ == "__main__":
    sys.exit(main())
