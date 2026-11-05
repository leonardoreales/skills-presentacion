"""Deriva el contenido de ui-ux-pro-max (MIT) hacia el formato del Mochilero.

Dos pasos, reproducibles:
  python derivar_uiuxpromax.py derivar  [--origen RUTA] [--sembrar]   # CSV en español + pendientes de traducir
  (--sembrar solo la primera vez: crea datos/ids/. Sin él, falta de mapa = error; ver ids_estables.py)
  python derivar_uiuxpromax.py fusionar                   # aplica las traducciones y valida

Qué hace «derivar»:
  - renombra columnas al español y fija un esquema por tabla (M-2 del diseño);
  - pasa las paletas a formato largo por ROL y TOKEN, y calcula el contraste WCAG de cada pareja (M-4);
  - excluye los stacks de escritorio (M-5) y marca las filas obsoletas (M-6);
  - une la licencia de cada fuente de Google Fonts;
  - deja en trabajo/traduccion/pendiente/ los campos de prosa, en inglés, para traducir.

Qué hace «fusionar»:
  - lee trabajo/traduccion/hecho/<tabla>*.jsonl;
  - comprueba que cada id y cada campo pendiente tiene traducción, y que no sobra nada;
  - escribe los CSV finales. Si algo falta, no escribe esa tabla y lo dice.

Origen fijado: nextlevelbuilder/ui-ux-pro-max-skill, hash de carpeta f0415e89eeadda8933a49a3f432acae52fa542aa
(instalada el 2026-09-11). Licencia MIT, aviso en LICENCIAS/ui-ux-pro-max-MIT.txt.
"""
import csv
import glob
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ids_estables import ErrorIds, MapaIds, ids_retirados  # noqa: E402

RAIZ =os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEN_POR_DEFECTO = os.path.join(os.path.expanduser("~"), ".claude", "skills", "ui-ux-pro-max", "data")
FRONT = os.path.join(RAIZ, "datos", "front")
PENDIENTE = os.path.join(RAIZ, "trabajo", "traduccion", "pendiente")
HECHO = os.path.join(RAIZ, "trabajo", "traduccion", "hecho")
BORRADOR = os.path.join(RAIZ, "trabajo", "traduccion", "borrador")

SEVERIDAD = {"critical": "Crítica", "high": "Alta", "medium": "Media", "low": "Baja"}
ESTADO = {"active": "vigente", "deprecated": "obsoleta", "": "vigente"}

# Esquema común de las tablas de reglas (M-2). Las filas investigadas en la web usan las 14 primeras.
GUIA = ["id", "categoria", "tema", "palabras_clave", "descripcion", "hacer", "no_hacer", "ejemplo_bien",
        "ejemplo_mal", "severidad", "puestos", "artefacto", "fuente", "verificado_el", "aplica_a", "estado"]
GUIA_TRADUCIR = ["categoria", "tema", "palabras_clave", "descripcion", "hacer", "no_hacer"]

STACKS = {  # código de id por stack; los de escritorio quedan fuera (M-5)
    "react": "RCT", "nextjs": "NXT", "vue": "VUE", "nuxtjs": "NUX", "nuxt-ui": "NUI", "svelte": "SVL",
    "astro": "AST", "angular": "ANG", "laravel": "LRV", "html-tailwind": "TWD", "shadcn": "SHD",
    "threejs": "THR", "react-native": "RNT", "flutter": "FLT", "swiftui": "SWF", "jetpack-compose": "JPC",
}
STACKS_EXCLUIDOS = ["wpf", "winui", "uwp", "uno", "avalonia", "javafx"]

ROLES = [  # (columna de origen, rol, token de la agencia, token shadcn)
    ("Primary", "primario", "--color-primario", "--primary"),
    ("On Primary", "sobre-primario", "--color-sobre-primario", "--primary-foreground"),
    ("Secondary", "secundario", "--color-secundario", "--secondary"),
    ("On Secondary", "sobre-secundario", "--color-sobre-secundario", "--secondary-foreground"),
    ("Accent", "acento", "--color-acento", "--accent"),
    ("On Accent", "sobre-acento", "--color-sobre-acento", "--accent-foreground"),
    ("Background", "fondo", "--color-fondo", "--background"),
    ("Foreground", "tinta", "--color-tinta", "--foreground"),
    ("Card", "superficie", "--color-superficie", "--card"),
    ("Card Foreground", "tinta-superficie", "--color-tinta-superficie", "--card-foreground"),
    ("Muted", "apagado", "--color-apagado", "--muted"),
    ("Muted Foreground", "tinta-apagada", "--color-tinta-apagada", "--muted-foreground"),
    ("Border", "borde", "--color-borde", "--border"),
    ("Destructive", "destructivo", "--color-destructivo", "--destructive"),
    ("On Destructive", "sobre-destructivo", "--color-sobre-destructivo", "--destructive-foreground"),
    ("Ring", "anillo-foco", "--color-anillo-foco", "--ring"),
]
# Pareja contra la que se mide cada rol, y umbral WCAG 2.2: 4,5 texto normal (1.4.3), 3 componentes (1.4.11).
PAREJAS = {
    "sobre-primario": ("primario", 4.5), "sobre-secundario": ("secundario", 4.5),
    "sobre-acento": ("acento", 4.5), "tinta": ("fondo", 4.5), "tinta-superficie": ("superficie", 4.5),
    "tinta-apagada": ("fondo", 4.5), "sobre-destructivo": ("destructivo", 4.5), "anillo-foco": ("fondo", 3.0),
    "primario": ("fondo", 3.0), "destructivo": ("fondo", 3.0), "borde": ("fondo", 3.0),
}
# 1.4.11 exige 3:1 al borde solo cuando es lo ÚNICO que delimita un control (un campo sin fondo propio, una casilla).
# Un borde decorativo, o el de un control que ya se distingue por su fondo, no lo necesita: su fallo es condicional.
CONDICIONALES = {"borde"}
AVISO_CONDICIONAL = "⚠1.4.11 si el borde es el único límite del control"


def veredicto(rol, ratio, umbral):
    if ratio >= umbral:
        return "sí"
    return "condicional" if rol in CONDICIONALES else "no"


def etiqueta_fallo(rol, pareja, ratio, cumple):
    return f"{rol}/{pareja} {ratio}" + (f" {AVISO_CONDICIONAL}" if cumple == "condicional" else "")


def leer_csv(ruta):
    with open(ruta, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def escribir_csv(ruta, columnas, filas):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas, extrasaction="raise")
        w.writeheader()
        for fila in filas:
            w.writerow({c: fila.get(c, "") for c in columnas})


def escribir_pendiente(tabla, filas, campos):
    os.makedirs(PENDIENTE, exist_ok=True)
    with open(os.path.join(PENDIENTE, tabla + ".jsonl"), "w", encoding="utf-8") as f:
        for fila in filas:
            f.write(json.dumps({"id": fila["id"], "campos": {c: fila.get(c, "") for c in campos}},
                               ensure_ascii=False) + "\n")


def sev(v):
    return SEVERIDAD.get((v or "").strip().lower(), v)


def luminancia(hexa):
    h = hexa.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    canales = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def opaco(color, base):
    """Un color translúcido (rgba) se ve MEZCLADO con lo que tiene debajo: se compone sobre `base` (hex) y se devuelve
    en hex, que es lo que mide el contraste. Los bordes de las paletas oscuras vienen como rgba(255,255,255,0.08)."""
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)", color.strip())
    if not m:
        return color
    alfa = float(m.group(4)) if m.group(4) is not None else 1.0
    h = base.strip().lstrip("#")
    h = "".join(c * 2 for c in h) if len(h) == 3 else h
    debajo = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(float(c) * alfa + d * (1 - alfa)):02X}" for c, d in zip(m.groups()[:3], debajo))


def contraste(a, b):
    la, lb = sorted([luminancia(a), luminancia(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


# ---------------------------------------------------------------------------------------------- tablas de reglas
def guia_desde(filas, ids, mapa, puestos, artefacto, tabla_origen, extra_clave=""):
    salida = []
    for i, r in enumerate(filas, 1):
        g = {c: "" for c in GUIA}
        g["id"] = ids.asignar(r.get("No"))
        for dst, src in mapa.items():
            g[dst] = (r.get(src) or "").strip()
        g["palabras_clave"] = " ".join(x for x in [extra_clave, (r.get("Keywords") or "").strip()] if x)
        g["severidad"] = sev(g["severidad"])
        g["estado"] = ESTADO.get((r.get("Status") or "").strip().lower(), r.get("Status", ""))
        g["puestos"], g["artefacto"] = puestos, artefacto
        if not g["fuente"]:
            g["fuente"] = f"ui-ux-pro-max · {tabla_origen} #{r.get('No', i)}"
        if not g["verificado_el"]:
            g["verificado_el"] = "origen 2026-09-11"
        salida.append(g)
    return salida


MAPA_REGLA = {"categoria": "Category", "tema": "Issue", "descripcion": "Description", "hacer": "Do",
              "no_hacer": "Don't", "ejemplo_bien": "Code Example Good", "ejemplo_mal": "Code Example Bad",
              "severidad": "Severity", "aplica_a": "Platform"}
MAPA_STACK = {"categoria": "Category", "tema": "Guideline", "descripcion": "Description", "hacer": "Do",
              "no_hacer": "Don't", "ejemplo_bien": "Code Good", "ejemplo_mal": "Code Bad", "severidad": "Severity",
              "fuente": "Docs URL", "aplica_a": "Applies To", "verificado_el": "Verified At"}

# ---------------------------------------------------------------------------------------------- tablas de catálogo
CATALOGOS = {
    # tabla: (fichero de origen, prefijo, [(columna destino, columna origen, ¿traducir?)])
    "estilos": ("styles.csv", "EST", [
        ("estilo", "Style Category", False), ("tipo", "Type", True), ("palabras_clave", "Keywords", True),
        ("colores_primarios", "Primary Colors", True), ("colores_secundarios", "Secondary Colors", True),
        ("efectos", "Effects & Animation", True), ("ideal_para", "Best For", True),
        ("evitar_en", "Do Not Use For", True), ("modo_claro", "Light Mode ✓", False),
        ("modo_oscuro", "Dark Mode ✓", False), ("rendimiento", "Performance", False),
        ("accesibilidad", "Accessibility", False), ("movil", "Mobile-Friendly", False),
        ("conversion", "Conversion-Focused", False), ("compatibilidad", "Framework Compatibility", False),
        ("origen", "Era/Origin", True), ("complejidad", "Complexity", False),
        ("palabras_prompt", "AI Prompt Keywords", False), ("css_clave", "CSS/Technical Keywords", False),
        ("checklist", "Implementation Checklist", True), ("variables", "Design System Variables", False),
        ("estilo_id", "Style ID", False), ("alias", "Aliases", False), ("estado", "Status", False),
        ("padre_id", "Parent Style ID", False), ("reemplazo_dominio", "Replacement Domain", False),
        ("reemplazo_id", "Replacement ID", False), ("modo_preferido", "Preferred Mode", False)]),
    "productos": ("products.csv", "PRD", [
        ("producto", "Product Type", True), ("palabras_clave", "Keywords", True),
        ("estilo_principal", "Primary Style Recommendation", False),
        ("estilos_secundarios", "Secondary Styles", False), ("patron_landing", "Landing Page Pattern", False),
        ("estilo_dashboard", "Dashboard Style (if applicable)", True),
        ("foco_color", "Color Palette Focus", True), ("consideraciones", "Key Considerations", True)]),
    "razonamiento": ("ui-reasoning.csv", "RZN", [
        ("categoria_ui", "UI_Category", True), ("patron", "Recommended_Pattern", False),
        ("prioridad_estilo", "Style_Priority", False), ("animo_color", "Color_Mood", True),
        ("animo_tipografia", "Typography_Mood", True), ("efectos_clave", "Key_Effects", True),
        ("reglas_decision", "Decision_Rules", False), ("antipatrones", "Anti_Patterns", True),
        ("severidad", "Severity", False), ("razonamiento", "Reasoning", True), ("confianza", "Confidence", False)]),
    "tipografia": ("typography.csv", "TIP", [
        ("par", "Font Pairing Name", True), ("categoria", "Category", True),
        ("fuente_titulos", "Heading Font", False), ("fuente_cuerpo", "Body Font", False),
        ("palabras_clave", "Mood/Style Keywords", True), ("ideal_para", "Best For", True),
        ("url_google", "Google Fonts URL", False), ("import_css", "CSS Import", False),
        ("config_tailwind", "Tailwind Config", False), ("notas", "Notes", True)]),
    "iconos": ("icons.csv", "ICO", [
        ("categoria", "Category", True), ("icono", "Icon Name", False), ("palabras_clave", "Keywords", True),
        ("libreria", "Library", False), ("importar", "Import Code", False), ("uso", "Usage", True),
        ("ideal_para", "Best For", True), ("estilo", "Style", False), ("rol_semantico", "Semantic Role", False),
        ("contextos", "Allowed Contexts", False)]),
    "graficas": ("charts.csv", "GRF", [
        ("tipo_de_dato", "Data Type", True), ("palabras_clave", "Keywords", True),
        ("grafica", "Best Chart Type", True), ("alternativas", "Secondary Options", True),
        ("cuando_usar", "When to Use", True), ("cuando_no", "When NOT to Use", True),
        ("umbral_volumen", "Data Volume Threshold", True), ("color", "Color Guidance", True),
        ("riesgo_accesibilidad", "Accessibility Risk", False), ("notas_accesibilidad", "Accessibility Notes", True),
        ("alternativa_accesible", "A11y Fallback", True), ("librerias", "Library Recommendation", False),
        ("interactividad", "Interactive Level", True)]),
    "movimiento": ("motion.csv", "MOV", [
        ("categoria", "Category", True), ("intensidad", "Intensity Tier", False),
        ("palabras_clave", "Keywords", True), ("disparador", "Trigger", False), ("duracion", "Duration", False),
        ("easing", "Easing", False), ("snippet_gsap", "GSAP Snippet", False),
        ("notas_framework", "Framework Notes", True), ("hacer", "Do", True), ("no_hacer", "Don't", True),
        ("notas_rendimiento", "Performance Notes", True)]),
    "landing": ("landing.csv", "LND", [
        ("patron", "Pattern Name", True), ("palabras_clave", "Keywords", True),
        ("orden_secciones", "Section Order", True), ("ubicacion_cta", "Primary CTA Placement", True),
        ("estrategia_color", "Color Strategy", True), ("efectos", "Recommended Effects", True),
        ("conversion", "Conversion Optimization", True), ("patron_id", "Pattern ID", False),
        ("alias", "Aliases", False)]),
}
INTENSIDAD = {"subtle": "Sutil", "standard": "Estándar", "complex": "Compleja"}
# Clave de origen que da identidad a cada fila (hallazgo 4). Por defecto la columna `No`; donde el origen trae un
# id con nombre propio, se usa ese, porque `No` podría renumerarse (en styles.csv ya falta el 54).
CLAVE_ORIGEN = {"estilos": "Style ID", "landing": "Pattern ID"}


def derivar(origen, sembrar=False):
    resumen = []
    mapa_ids = lambda tabla, prefijo, ancho=3: MapaIds(tabla, prefijo, ancho, sembrar=sembrar)  # noqa: E731

    # 1. Reglas: UX, app nativa y rendimiento de React.
    for tabla, fichero, prefijo, puestos, artefacto in [
        ("ux", "ux-guidelines.csv", "UX", "DFC DVF QA", "PAN"),
        ("app-nativa", "app-interface.csv", "APP", "DFC DVF QA", "PAN"),
        ("rendimiento-react", "react-performance.csv", "RRP", "DVF REN", "PRF"),
    ]:
        filas = leer_csv(os.path.join(origen, fichero))
        ids = mapa_ids(tabla, prefijo)
        g = guia_desde(filas, ids, MAPA_REGLA, puestos, artefacto, fichero)
        ids.cerrar()
        escribir_csv(os.path.join(BORRADOR, tabla + ".csv"), GUIA, g)
        escribir_pendiente(tabla, g, GUIA_TRADUCIR)
        resumen.append((tabla, len(filas), len(g)))

    # 2. Stacks web y móvil.
    for nombre, codigo in STACKS.items():
        filas = leer_csv(os.path.join(origen, "stacks", nombre + ".csv"))
        tabla = "stack-" + nombre
        ids = mapa_ids(tabla, codigo)
        g = guia_desde(filas, ids, MAPA_STACK, "DVF DFC", "PAN", f"stacks/{nombre}.csv", extra_clave=nombre)
        ids.cerrar()
        escribir_csv(os.path.join(BORRADOR, tabla + ".csv"), GUIA, g)
        escribir_pendiente(tabla, g, GUIA_TRADUCIR)
        resumen.append((tabla, len(filas), len(g)))

    # 3. Catálogos con esquema propio.
    for tabla, (fichero, prefijo, cols) in CATALOGOS.items():
        filas = leer_csv(os.path.join(origen, fichero))
        ids = mapa_ids(tabla, prefijo)
        salida = []
        for i, r in enumerate(filas, 1):
            s = {"id": ids.asignar(r.get(CLAVE_ORIGEN.get(tabla, "No")))}
            for dst, src, _ in cols:
                s[dst] = (r.get(src) or "").strip()
            if "severidad" in s:
                s["severidad"] = sev(s["severidad"])
            if "estado" in s:
                s["estado"] = ESTADO.get(s["estado"].lower(), s["estado"])
            if "intensidad" in s:
                s["intensidad"] = INTENSIDAD.get(s["intensidad"].lower(), s["intensidad"])
            s["fuente"] = f"ui-ux-pro-max · {fichero} #{r.get('No', i)}"
            salida.append(s)
        ids.cerrar()
        columnas = ["id"] + [c[0] for c in cols] + ["fuente"]
        escribir_csv(os.path.join(BORRADOR, tabla + ".csv"), columnas, salida)
        escribir_pendiente(tabla, salida, [c[0] for c in cols if c[2]])
        resumen.append((tabla, len(filas), len(salida)))

    # 4. Paletas: índice + formato largo por rol, con contraste calculado.
    colores = leer_csv(os.path.join(origen, "colors.csv"))
    productos = {r["Product Type"]: r for r in leer_csv(os.path.join(origen, "products.csv"))}
    indice, roles = [], []
    ids = mapa_ids("paletas", "PAL")
    for i, r in enumerate(colores, 1):
        pid = ids.asignar(r.get("No"))
        valores = {rol: r[src].strip() for src, rol, _, _ in ROLES}
        fallos = []
        for src, rol, token, token_shadcn in ROLES:
            pareja, umbral, ratio, cumple = "", "", "", "n.a."
            if rol in PAREJAS:
                pareja, u = PAREJAS[rol]
                ratio_v = contraste(opaco(valores[rol], valores[pareja]), valores[pareja])
                ratio, umbral = f"{ratio_v:.2f}", f"{u:g}"
                cumple = veredicto(rol, ratio_v, u)
                if cumple != "sí":
                    fallos.append(etiqueta_fallo(rol, pareja, ratio, cumple))
            roles.append({"paleta_id": pid, "rol": rol, "token": token, "token_shadcn": token_shadcn,
                          "valor": valores[rol], "pareja": pareja, "contraste": ratio, "umbral": umbral,
                          "cumple_aa": cumple})
        prod = productos.get(r["Product Type"], {})
        indice.append({"id": pid, "producto": r["Product Type"], "palabras_clave": prod.get("Keywords", ""),
                       "foco_color": prod.get("Color Palette Focus", ""), "notas": r.get("Notes", ""),
                       "fallos_aa": "; ".join(fallos) if fallos else "ninguno",
                       "fuente": f"ui-ux-pro-max · colors.csv #{r.get('No', i)}"})
    ids.cerrar()
    escribir_csv(os.path.join(BORRADOR, "paletas.csv"),
                 ["id", "producto", "palabras_clave", "foco_color", "notas", "fallos_aa", "fuente"], indice)
    escribir_csv(os.path.join(FRONT, "paletas-roles.csv"),
                 ["paleta_id", "rol", "token", "token_shadcn", "valor", "pareja", "contraste", "umbral", "cumple_aa"],
                 roles)
    escribir_pendiente("paletas", indice, ["producto", "palabras_clave", "foco_color", "notas"])
    resumen.append(("paletas", len(colores), len(indice)))
    resumen.append(("paletas-roles", len(colores) * len(ROLES), len(roles)))

    # 5. Fuentes de Google: catálogo sin traducir, con su licencia unida.
    fuentes = leer_csv(os.path.join(origen, "google-fonts.csv"))
    lic = json.load(open(os.path.join(origen, "google-font-licenses.json"), encoding="utf-8"))
    licencia = {f["name"]: f.get("license", "") for f in lic["families"]}
    mapa = [("familia", "Family"), ("categoria", "Category"), ("trazo", "Stroke"),
            ("clasificaciones", "Classifications"), ("palabras_clave", "Keywords"), ("estilos", "Styles"),
            ("ejes_variables", "Variable Axes"), ("subconjuntos", "Subsets"), ("disenadores", "Designers"),
            ("rango_popularidad", "Popularity Rank"), ("rango_tendencia", "Trending Rank"), ("es_noto", "Is Noto"),
            ("anadida", "Date Added"), ("modificada", "Last Modified"), ("url", "Google Fonts URL")]
    salida = []
    ids = mapa_ids("fuentes", "FNT", 4)
    for i, r in enumerate(fuentes, 1):
        s = {"id": ids.asignar(r.get("Family"))}
        for dst, src in mapa:
            s[dst] = (r.get(src) or "").strip()
        s["licencia"] = {"OFL": "OFL-1.1", "APACHE2": "Apache-2.0", "UFL": "UFL-1.0"}.get(licencia.get(r["Family"], ""),
                                                                                        "sin dato")
        s["fuente"] = "ui-ux-pro-max · google-fonts.csv (google/fonts rev 038b637)"
        salida.append(s)
    ids.cerrar()
    escribir_csv(os.path.join(FRONT, "fuentes.csv"), ["id"] + [m[0] for m in mapa] + ["licencia", "fuente"], salida)
    resumen.append(("fuentes", len(fuentes), len(salida)))

    print(f"{'tabla':<26}{'origen':>8}{'derivada':>10}")
    for t, a, b in resumen:
        marca = "" if a == b or t == "paletas-roles" else "  ← DISTINTO"
        print(f"{t:<26}{a:>8}{b:>10}{marca}")
    print("excluidos (M-5):", ", ".join(STACKS_EXCLUIDOS))


def fusionar(solo=None, validar_solo=False):
    """solo: lista de tablas (None = todas). validar_solo: comprueba sin escribir nada."""
    ok, fallos = [], []
    for ruta_p in sorted(glob.glob(os.path.join(PENDIENTE, "*.jsonl"))):
        tabla = os.path.basename(ruta_p)[:-6]
        if solo and tabla not in solo:
            continue
        pendientes = [json.loads(l) for l in open(ruta_p, encoding="utf-8") if l.strip()]
        hechas = {}
        for ruta_h in sorted(glob.glob(os.path.join(HECHO, tabla + ".jsonl")) +
                             glob.glob(os.path.join(HECHO, tabla + ".parte*.jsonl"))):
            for n, l in enumerate(open(ruta_h, encoding="utf-8"), 1):
                if l.strip():
                    try:
                        o = json.loads(l)
                    except json.JSONDecodeError as e:
                        fallos.append(f"{tabla}: JSON roto en {os.path.basename(ruta_h)}:{n} ({e})")
                        continue
                    hechas[o["id"]] = o["campos"]
        if not hechas:
            fallos.append(f"{tabla}: sin traducción")
            continue
        errores = []
        ruta_huellas = os.path.join(RAIZ, "trabajo", "traduccion", "huellas", tabla + ".json")
        previas = json.load(open(ruta_huellas, encoding="utf-8")) if os.path.exists(ruta_huellas) else {}
        huellas = {}
        for p in pendientes:
            h = hechas.get(p["id"])
            if h is None:
                errores.append(f"falta {p['id']}")
                continue
            huellas[p["id"]] = hashlib.sha256(json.dumps(p["campos"], sort_keys=True,
                                                         ensure_ascii=False).encode()).hexdigest()[:16]
            if p["id"] in previas and previas[p["id"]] != huellas[p["id"]]:
                errores.append(f"{p['id']}: el texto de origen cambió desde la traducción; hay que retraducirla")
            sobra = set(h) - set(p["campos"])
            if sobra:
                errores.append(f"{p['id']}: campos que no se pidieron traducir {sorted(sobra)}")
            for campo, original in p["campos"].items():
                if campo not in h:
                    errores.append(f"{p['id']}.{campo} ausente")
                elif original.strip() and not str(h[campo]).strip():
                    errores.append(f"{p['id']}.{campo} vacío")
        # Un id retirado del origen conserva su traducción en hecho/ (y su huella) por si vuelve: no es un sobrante.
        sobran = set(hechas) - {p["id"] for p in pendientes} - ids_retirados(tabla)
        if sobran:
            errores.append(f"ids que no existen: {sorted(sobran)[:5]}")
        cambiadas = sum(1 for e in errores if "el texto de origen cambió" in e)
        if cambiadas >= 5:
            fallos.append(f"{tabla}: AVISO — {cambiadas} textos de origen cambiaron a la vez. Si el origen renumeró su "
                          f"clave, los ids se desplazaron: revisa CLAVE_ORIGEN antes de retraducir nada.")
        if errores:
            fallos.append(f"{tabla}: {len(errores)} errores, p. ej. {errores[:4]}")
            continue
        if validar_solo:
            ok.append(f"{tabla} ({len(pendientes)}) válida")
            continue
        borrador = os.path.join(BORRADOR, tabla + ".csv")
        with open(borrador, encoding="utf-8", newline="") as f:
            lector = csv.DictReader(f)
            columnas, filas = lector.fieldnames, list(lector)
        pedidos = {p["id"]: set(p["campos"]) for p in pendientes}
        for fila in filas:
            for campo, texto in hechas[fila["id"]].items():
                if campo in pedidos[fila["id"]]:  # nunca toca código ni campos no pedidos
                    fila[campo] = str(texto).strip()
        os.makedirs(os.path.dirname(ruta_huellas), exist_ok=True)
        # Se MEZCLAN con las previas: la huella de un id retirado debe seguir ahí si ese id vuelve.
        json.dump({**previas, **huellas}, open(ruta_huellas, "w", encoding="utf-8"), indent=0)
        destino = os.path.join(FRONT, "stacks", tabla[6:] + ".csv") if tabla.startswith("stack-") \
            else os.path.join(FRONT, tabla + ".csv")
        escribir_csv(destino, columnas, filas)
        ok.append(f"{tabla} ({len(filas)})")
    print("FUSIONADAS:", ", ".join(ok) if ok else "ninguna")
    for f in fallos:
        print("PENDIENTE:", f)
    return 0 if not fallos else 1


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    if modo == "derivar":
        origen = sys.argv[sys.argv.index("--origen") + 1] if "--origen" in sys.argv else ORIGEN_POR_DEFECTO
        derivar(origen, sembrar="--sembrar" in sys.argv)
    elif modo == "fusionar":
        sys.exit(fusionar(sys.argv[2:] or None))
    elif modo == "validar":
        sys.exit(fusionar(sys.argv[2:] or None, validar_solo=True))
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        main()
    except ErrorIds as e:
        print("ERROR de ids:", e, file=sys.stderr)
        sys.exit(3)
