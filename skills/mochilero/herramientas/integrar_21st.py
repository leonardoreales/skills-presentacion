"""Convierte lo recolectado de 21st.dev (trabajo/21st/*.json) en tablas del Mochilero.

  python integrar_21st.py

Salida en datos/front/:
  componentes-21st.csv   catálogo de componentes por género (metadatos; el código NO se trae: M-9)
  plantillas-21st.csv    plantillas completas (solo enlace)
  temas-21st.csv         índice de temas con sus fallos de contraste en claro y oscuro
  temas-21st-roles.csv   cada tema en formato largo por MODO, ROL y TOKEN, con el contraste WCAG calculado (M-4)
"""
import colorsys
import json
import math
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from derivar_uiuxpromax import CONDICIONALES, PAREJAS, escribir_csv, etiqueta_fallo, veredicto  # noqa: E402
from ids_estables import MapaIds  # noqa: E402

SEMBRAR = "--sembrar" in sys.argv  # solo la primera vez; ver ids_estables.py

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA = os.path.join(RAIZ, "trabajo", "21st")
FRONT = os.path.join(RAIZ, "datos", "front")
HOY = __import__("datetime").date.today().isoformat()
ADUANA = ("Trae colores crudos de Tailwind: cambiarlos por tokens de rol antes de integrar. Revisar su licencia. "
          "Traer el código gasta 1 de las 2 recuperaciones diarias (get_component con id_demo).")

# Variable shadcn → (rol de la agencia, token de la agencia)
ROL_SHADCN = {
    "background": "fondo", "foreground": "tinta", "card": "superficie", "card-foreground": "tinta-superficie",
    "popover": "emergente", "popover-foreground": "tinta-emergente", "primary": "primario",
    "primary-foreground": "sobre-primario", "secondary": "secundario", "secondary-foreground": "sobre-secundario",
    "muted": "apagado", "muted-foreground": "tinta-apagada", "accent": "acento", "accent-foreground": "sobre-acento",
    "destructive": "destructivo", "destructive-foreground": "sobre-destructivo", "border": "borde",
    "input": "borde-campo", "ring": "anillo-foco", "chart-1": "grafica-1", "chart-2": "grafica-2",
    "chart-3": "grafica-3", "chart-4": "grafica-4", "chart-5": "grafica-5",
}
COLOR_ES = {"blue": "azul", "violet": "violeta morado", "green": "verde", "orange": "naranja", "red": "rojo",
            "neutral": "neutro gris", "rose": "rosa", "yellow": "amarillo", "teal": "turquesa verde azulado",
            "pink": "rosa fucsia"}
PAREJAS_TEMA =dict(PAREJAS, **{"tinta-emergente": ("emergente", 4.5)})


def a_rgb(valor):
    """Devuelve (r, g, b) en 0..1 o None. Acepta hex, rgb(), hsl() o su forma desnuda, y oklch()."""
    v = valor.strip().lower()
    if v.startswith("#"):
        h = v[1:]
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h[:3])
        if len(h) in (6, 8):
            return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        return None
    nums = [float(x) for x in re.findall(r"-?\d*\.?\d+", v.split("/")[0])]
    if v.startswith("rgb") and len(nums) >= 3:
        return tuple(n / 255 for n in nums[:3])
    if v.startswith("oklch") and len(nums) >= 3:
        l, c, hgrados = nums[:3]
        if "%" in v.split(" ")[0]:
            l = l / 100
        a, b = c * math.cos(math.radians(hgrados)), c * math.sin(math.radians(hgrados))
        l_ = (l + 0.3963377774 * a + 0.2158037573 * b) ** 3
        m_ = (l - 0.1055613458 * a - 0.0638541728 * b) ** 3
        s_ = (l - 0.0894841775 * a - 1.2914855480 * b) ** 3
        lin = [4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
               -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
               -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_]
        return tuple(min(1, max(0, 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055)) for c in lin)
    if (v.startswith("hsl") or "%" in v) and len(nums) >= 3:
        r, g, b = colorsys.hls_to_rgb(nums[0] / 360, nums[2] / 100, nums[1] / 100)
        return (r, g, b)
    return None


def luminancia(rgb):
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contraste(a, b):
    la, lb = sorted([luminancia(a), luminancia(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def bloques(css):
    """{'claro': {var: valor}, 'oscuro': {...}} a partir de :root y .dark."""
    salida = {}
    for selector, cuerpo in re.findall(r"([:.\w-]+)\s*\{([^}]*)\}", css):
        modo = "oscuro" if "dark" in selector else "claro" if "root" in selector else None
        if modo:
            salida[modo] = dict(re.findall(r"--([\w-]+)\s*:\s*([^;]+);", cuerpo))
    return salida


def clave(texto):
    t = texto.lower()
    for a, b in zip("áéíóúüñ", "aeiouun"):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", t)).strip()


def main():
    # Ids estables (hallazgo 4): la clave es el id de 21st. El orden solo decide qué número recibe una fila NUEVA.
    ids_c = MapaIds("componentes-21st", "C21", 4, sembrar=SEMBRAR)
    ids_p = MapaIds("plantillas-21st", "P21", 3, sembrar=SEMBRAR)
    ids_t = MapaIds("temas-21st", "TEM", 3, sembrar=SEMBRAR)

    comps = json.load(open(os.path.join(ENTRADA, "componentes.json"), encoding="utf-8"))
    filas = []
    for c in sorted(comps, key=lambda x: (x["generos"][0], x["name"])):
        filas.append({
            "id": ids_c.asignar(c["id"]), "generos": " · ".join(c["generos"]),
            "palabras_clave": " ".join(dict.fromkeys(clave(" ".join(c["generos"]) + " " + c["consulta"] + " "
                                                            + c["name"]).split())),
            "nombre": c["name"].strip(), "autor": c.get("author", ""), "id_demo": c["id"], "url": c.get("url", ""),
            "vista_previa": c.get("previewUrl") or "", "instalar": c.get("installCommand", ""),
            "descripcion_original": re.sub(r"\s+", " ", (c.get("description") or "")).strip()[:300],
            "aduana": ADUANA, "verificado_el": HOY})
    escribir_csv(os.path.join(FRONT, "componentes-21st.csv"), list(filas[0].keys()), filas)

    plant = json.load(open(os.path.join(ENTRADA, "plantillas.json"), encoding="utf-8"))
    pf = [{"id": ids_p.asignar(p["id"]), "nombre": p["name"].strip(), "palabras_clave": clave(p["consulta"] + " " + p["name"]),
           "autor": p.get("author", ""), "precio": p.get("price", ""), "url": p.get("url", ""),
           "descripcion_original": re.sub(r"\s+", " ", (p.get("description") or "")).strip()[:300],
           "verificado_el": HOY} for p in plant]
    escribir_csv(os.path.join(FRONT, "plantillas-21st.csv"), list(pf[0].keys()), pf)

    temas = json.load(open(os.path.join(ENTRADA, "temas.json"), encoding="utf-8"))
    indice, roles, sin_parsear = [], [], 0
    for t in sorted((t for t in temas if t.get("css")), key=lambda x: x["name"]):
        tid = ids_t.asignar(t["id"])
        th = t["css"]["theme"]
        modos = bloques(th["css"])
        fallos = {"claro": [], "oscuro": []}
        for modo, vars_ in modos.items():
            por_rol = {ROL_SHADCN[k]: v.strip() for k, v in vars_.items() if k in ROL_SHADCN}
            for rol, valor in por_rol.items():
                pareja, umbral, ratio, cumple = "", "", "", "n.a."
                if rol in PAREJAS_TEMA and PAREJAS_TEMA[rol][0] in por_rol:
                    pareja, u = PAREJAS_TEMA[rol]
                    a, b = a_rgb(valor), a_rgb(por_rol[pareja])
                    if a and b:
                        r = contraste(a, b)
                        ratio, umbral, cumple = f"{r:.2f}", f"{u:g}", veredicto(rol, r, u)
                        if cumple != "sí":
                            fallos[modo].append(etiqueta_fallo(rol, pareja, ratio, cumple))
                    elif "transparent" in (valor + por_rol[pareja]).lower():
                        # Un texto o fondo transparente no tiene contraste garantizado: es fallo, no «sin dato».
                        cumple = "condicional" if rol in CONDICIONALES else "no"
                        fallos[modo].append(etiqueta_fallo(rol, pareja, "transparente", cumple))
                    else:
                        cumple, sin_parsear = "sin calcular", sin_parsear + 1
                        fallos[modo].append(f"{rol}/{pareja} ⚠sin calcular")
                token_shadcn = "--" + next(k for k, v in ROL_SHADCN.items() if v == rol)
                roles.append({"tema_id": tid, "modo": modo, "rol": rol, "token": "--color-" + rol,
                              "token_shadcn": token_shadcn, "valor": valor, "pareja": pareja, "contraste": ratio,
                              "umbral": umbral, "cumple_aa": cumple})
        vc = modos.get("claro", {})
        indice.append({"id": tid, "nombre": th["name"], "autor": th.get("author", ""), "color": t.get("color", ""),
                       "palabras_clave": clave(f"{t.get('color', '')} {COLOR_ES.get(t.get('color', ''), '')} {th['name']}"
                                               f" tema theme paleta palette"
                                               + (" oscuro dark claro light" if "oscuro" in modos else " claro light")),
                       "modos": " + ".join(modos), "fuente_sans": vc.get("font-sans", "").strip(),
                       "fuente_serif": vc.get("font-serif", "").strip(), "fuente_mono": vc.get("font-mono", "").strip(),
                       "radio": vc.get("radius", "").strip(),
                       "fallos_aa_claro": "; ".join(fallos["claro"]) or "ninguno",
                       "fallos_aa_oscuro": "; ".join(fallos["oscuro"]) or ("ninguno" if "oscuro" in modos else "sin modo oscuro"),
                       "url": th.get("url", ""), "verificado_el": HOY})
    for m in (ids_c, ids_p, ids_t):
        m.cerrar()
    escribir_csv(os.path.join(FRONT, "temas-21st.csv"), list(indice[0].keys()), indice)
    escribir_csv(os.path.join(FRONT, "temas-21st-roles.csv"), list(roles[0].keys()), roles)
    limpios = sum(1 for x in indice if x["fallos_aa_claro"] == "ninguno" and x["fallos_aa_oscuro"] == "ninguno")
    print(f"componentes {len(filas)} · plantillas {len(pf)} · temas {len(indice)} ({limpios} sin fallos AA en ningún modo)"
          f" · filas por rol {len(roles)} · valores sin parsear {sin_parsear}")


if __name__ == "__main__":
    main()
