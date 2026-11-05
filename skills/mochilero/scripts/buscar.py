"""Buscador del Mochilero: devuelve filas puntuales con su fuente, nunca la biblioteca entera.

  python buscar.py "consulta" [--dominio front|backend|automatizaciones] [--tabla ux,api] [--stack react]
                   [-n 3] [--completo] [--incluir-obsoletas]
  python buscar.py --id API-014          # una fila entera por su id
  python buscar.py --tablas              # qué hay en la mochila, con recuentos

Solo biblioteca estándar. BM25 sobre todas las tablas de datos/, con normalización de tildes y palabras clave en
español e inglés. Si nada coincide de verdad, lo dice: no rellena con resultados flojos.
"""
import argparse
import csv
import math
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")
csv.field_size_limit(10_000_000)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, "datos")

# Tablas que no se indexan solas: se muestran como detalle de su índice (paletas y temas).
DETALLE = {"front/paletas-roles": ("front/paletas", "paleta_id"), "front/temas-21st-roles": ("front/temas-21st", "tema_id")}
# Columnas que no aportan al buscador (enlaces, código largo, fechas).
RUIDO = {"fuente", "url", "vista_previa", "instalar", "verificado_el", "import_css", "config_tailwind", "snippet_gsap",
         "variables", "reglas_decision", "url_google", "importar", "ejemplo_bien", "ejemplo_mal", "aduana", "id_demo",
         "css_clave", "palabras_prompt", "rango_popularidad", "rango_tendencia", "anadida", "modificada"}
# Nunca se entregan: CSS crudo con colores literales (F-08) y la marca interna de cobertura.
NO_MOSTRAR = {"variables", "css_clave", "palabras_prompt", "_cobertura"}
PESO = {"palabras_clave": 3.0, "tema": 2.5, "nombre": 2.5, "estilo": 2.5, "producto": 2.5, "categoria_ui": 2.5,
        "par": 2.0, "patron": 2.0, "tipo_de_dato": 2.0, "icono": 2.0, "familia": 2.5, "generos": 2.5, "categoria": 1.5}

VACIAS = set("""a al algo con como cual cuando de del desde donde el en entre es esa ese esta este esto hay la las lo los
mas me mi muy no o para pero por que se si sin sobre su sus te un una uno unos y ya the a an and are as at be by for from
how in is it of on or that this to use using what when with vs de""".split())

INFO = {  # descripción de cada tabla para --tablas. Las que no estén aquí se listan igual.
    "front/ux": "Reglas de UX y accesibilidad (WCAG) para web",
    "front/app-nativa": "Reglas de interfaz para apps nativas (iOS, Android, React Native)",
    "front/rendimiento-react": "Rendimiento en React y Next.js",
    "front/rendimiento-web": "Core Web Vitals, imágenes, fuentes, JS y caché del navegador (REN)",
    "front/estilos": "Estilos visuales: cuándo usarlos y cuándo no",
    "front/productos": "Tipos de producto y el estilo, landing y color que les encajan",
    "front/razonamiento": "Reglas de decisión de diseño por tipo de producto",
    "front/paletas": "Paletas por producto, por ROL y TOKEN, con el contraste AA calculado",
    "front/tipografia": "Pares tipográficos",
    "front/fuentes": "Catálogo de Google Fonts con su licencia",
    "front/iconos": "Iconos por uso y rol semántico",
    "front/graficas": "Qué gráfica usar según el dato, con su alternativa accesible",
    "front/movimiento": "Animación: duraciones, easing y presets",
    "front/landing": "Estructuras de landing page y conversión",
    "front/componentes-21st": "Catálogo de componentes de 21st.dev por género (solo metadatos)",
    "front/plantillas-21st": "Plantillas completas de 21st.dev (enlace)",
    "front/temas-21st": "Temas shadcn de 21st.dev en claro y oscuro, por ROL y TOKEN, con contraste AA",
    "front/librerias-front": "Librerías de front: para qué, cuándo sí, cuándo no, licencia",
    "backend/api": "Diseño de APIs HTTP: recursos, errores, paginación, versionado, idempotencia",
    "backend/seguridad-api": "Seguridad de APIs: OWASP API Top 10, auth, sesiones, validación",
    "backend/resiliencia": "Timeouts, reintentos, circuit breaker, caché de servidor, SLO (RES)",
    "backend/datos": "Referencia rápida de datos y PostgreSQL (lo profundo es del puesto BD)",
    "backend/observabilidad": "Logs, trazas, métricas y alertas",
    "backend/plataforma": "Entornos, CI/CD, despliegue y reversión (OPS, DSP)",
    "backend/librerias-backend": "Librerías de backend: para qué, cuándo sí, cuándo no, licencia",
    "automatizaciones/webhooks": "Recibir y enviar webhooks",
    "automatizaciones/n8n": "Buenas prácticas de n8n",
    "automatizaciones/tareas-y-colas": "Cron, colas, reintentos y outbox",
    "automatizaciones/integraciones": "Consumir APIs de terceros",
    "automatizaciones/ia-automatizacion": "Automatizaciones con modelos de lenguaje",
    "automatizaciones/librerias-automatizacion": "Plataformas y librerías de automatización",
    "presentacion/diagramas": "Tipos de diagrama por la pregunta que responden (FT Visual Vocabulary)",
    "presentacion/componentes-narrativos": "Piezas de escena que cuentan algo: contador, sello, cortina, medidor…",
    "presentacion/recetas": "Combinaciones probadas de técnicas e ideas de escena con referencia",
    "presentacion/disciplina": "Reglas del oficio: duración, foco, accesibilidad del movimiento, rendimiento, datos",
    "presentacion/graficas-narrativas": "Gráfica por pregunta, gráficas que engañan y cómo animar datos",
    "presentacion/narrativa": "Estructura y relato para audiencia ejecutiva",
    "presentacion/legibilidad": "Legibilidad proyectada y a distancia: texto, contraste, sala",
    "presentacion/librerias-efectos": "Técnicas y librerías de animación y efecto (GSAP, CSS, SVG, WebGL)",
    "presentacion/librerias-video": "Video determinista desde código: motores y licencias",
    "presentacion/librerias-graficas": "Librerías de gráficas y mapas para presentar",
    "presentacion/librerias-ilustracion": "Íconos, ilustración y fotografía con licencia institucional",
    "presentacion/librerias-presentacion": "Frameworks de presentación y scrollytelling",
    "presentacion/librerias-imagen": "Herramientas para tratar imágenes: formatos, recorte, vectorizado, fondo, IA",
    "presentacion/tratamiento-imagen": "Oficio para adaptar y animar fotos e ilustraciones: alt, contraste, derechos",
}
DOMINIOS = ("front", "backend", "automatizaciones", "presentacion")


def normalizar(texto):
    t = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def raiz(palabra):
    """Plural simétrico en español e inglés: clave/claves, error/errores, retry/retries dan la misma raíz."""
    p = palabra
    if len(p) > 4 and p.endswith("ies"):
        p = p[:-3] + "i"
    elif len(p) > 4 and p.endswith("es"):
        p = p[:-2]
    elif len(p) > 3 and p.endswith("s") and not p.endswith("ss"):
        p = p[:-1]
    if len(p) > 3 and p.endswith("y"):
        p = p[:-1] + "i"
    if len(p) > 4 and p.endswith("e"):
        p = p[:-1]
    return p


def tokens(texto, norm=normalizar):
    return [raiz(p) for p in re.findall(r"[a-z0-9$@]+", norm(texto)) if p not in VACIAS and len(p) > 1]


def cargar():
    tablas = {}
    for base, _, ficheros in os.walk(DATOS):
        for f in ficheros:
            if f.endswith(".csv"):
                ruta = os.path.join(base, f)
                nombre = os.path.relpath(ruta, DATOS)[:-4].replace(os.sep, "/")
                with open(ruta, encoding="utf-8", newline="") as fh:
                    tablas[nombre] = list(csv.DictReader(fh))
    return tablas


def dominio_de(tabla):
    return tabla.split("/")[0]


class Indice:
    def __init__(self, tablas, norm=normalizar):
        self.norm = norm
        self.docs = []  # (tabla, fila, Counter de términos, longitud)
        df = Counter()
        for tabla, filas in tablas.items():
            if tabla in DETALLE:
                continue
            for fila in filas:
                tf = Counter()
                for col, val in fila.items():
                    if col in RUIDO or col == "id" or not val:
                        continue
                    peso = PESO.get(col, 1.0)
                    for t in tokens(val, norm):
                        tf[t] += peso
                if tabla.startswith("front/stacks/"):
                    tf[raiz(tabla.split("/")[-1])] += 3.0
                self.docs.append((tabla, fila, tf, sum(tf.values())))
                df.update(tf.keys())
        n = len(self.docs) or 1
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}
        self.media = sum(d[3] for d in self.docs) / n

    def buscar(self, consulta, filtro=lambda tabla, fila: True, n=3, k1=1.4, b=0.75):
        q = tokens(consulta, self.norm)
        if not q:
            return [], q
        puntos = []
        for tabla, fila, tf, largo in self.docs:
            if not filtro(tabla, fila):
                continue
            s, cubiertos = 0.0, 0
            for t in set(q):
                f = tf.get(t, 0)
                if f:
                    cubiertos += 1
                    s += self.idf[t] * f * (k1 + 1) / (f + k1 * (1 - b + b * largo / self.media))
            # Con 1 o 2 términos deben coincidir todos; con más, al menos la mitad. Una palabra común no basta.
            total = len(set(q))
            if s > 0 and (cubiertos == total if total <= 2 else cubiertos * 2 >= total):
                # Premia cubrir más términos de la consulta: evita que una sola palabra rara gane.
                fila_cob = dict(fila, _cobertura=f"{cubiertos}/{total}")
                puntos.append((s * (cubiertos / total) ** 1.5, tabla, fila_cob))
        puntos.sort(key=lambda x: -x[0])
        return puntos[:n], q

    def por_termino(self, q, filtro=lambda tabla, fila: True, n=2, comun=15):
        """Para la respuesta de ausencia (MOC-1): qué filas casan con CADA término suelto. Una consulta que mezcla dos
        cosas («reservas educacion») no tiene una fila que cubra las dos, pero cada una puede tener la suya; sin esto,
        «sin coincidencias» se lee como «la mochila no tiene nada» y es falso. No responde la consulta: la orienta."""
        salida = []
        for t in dict.fromkeys(q):
            casan = sorted(((tf[t], tabla, fila) for tabla, fila, tf, _ in self.docs
                            if tf.get(t) and filtro(tabla, fila)), key=lambda x: -x[0])
            salida.append((t, len(casan), [(tabla, fila) for _, tabla, fila in casan[:n]] if len(casan) <= comun else []))
        return salida


# ------------------------------------------------------------------------------------------------ presentación
CODIGOS = {"risk": "riesgo", "requires": "requiere", "cost": "coste", "drivers": "motivos", "low": "bajo",
           "medium": "medio", "high": "alto", "conditional": "condicional", "none": "ninguno",
           "contrast-text-4.5": "contraste de texto 4,5:1", "keyboard": "teclado", "visible-focus": "foco visible",
           "reduced-motion": "movimiento reducido", "contrast-ui-3": "contraste de componentes 3:1"}


def legible(texto):
    """«risk:low|requires:keyboard,visible-focus» → «riesgo: bajo · requiere: teclado, foco visible»."""
    if not re.fullmatch(r"[\w.-]+:[\w.,|:-]+", texto or ""):
        return texto
    partes = []
    for bloque in texto.split("|"):
        k, _, v = bloque.partition(":")
        partes.append(f"{CODIGOS.get(k, k)}: " + ", ".join(CODIGOS.get(x, x.replace('-', ' ')) for x in v.split(",")))
    return " · ".join(partes)


def recorta(texto, n=220):
    texto = re.sub(r"\s+", " ", texto or "").strip()
    return texto if len(texto) <= n else texto[: n - 1].rstrip() + "…"


def titulo(fila):
    """Nombre corto de una fila de cualquier tabla, para listarla en una línea."""
    for k in ("tema", "producto", "nombre", "par", "icono", "tipo_de_dato", "categoria"):
        if fila.get(k):
            return recorta(fila[k], 60)
    otras = [v for k, v in fila.items() if k not in ("id", "fuente") and not k.startswith("_") and v]
    return recorta(otras[0], 60) if otras else ""


def detalle_roles(tablas, tabla_indice, id_, completo):
    for det, (idx, col) in DETALLE.items():
        if idx != tabla_indice:
            continue
        filas = [r for r in tablas.get(det, []) if r[col] == id_]
        lineas = []
        for modo in sorted({r.get("modo", "") for r in filas}):
            del_modo = [r for r in filas if r.get("modo", "") == modo]
            if not completo:
                del_modo = [r for r in del_modo if r["rol"] in ("fondo", "tinta", "primario", "sobre-primario",
                                                                 "acento", "borde", "destructivo")]
            pares = " · ".join(f"{r['token']}={r['valor']}" + {"no": " ✗AA", "sin calcular": " ⚠sin calcular",
                                                                "condicional": " ⚠1.4.11"}
                               .get(r["cumple_aa"], "") for r in del_modo)
            lineas.append(f"  {('Modo ' + modo + ': ') if modo else 'Roles: '}{pares}")
        return lineas
    return []


def presentar(tabla, fila, tablas, completo=False):
    c = {k: v for k, v in fila.items() if k not in NO_MOSTRAR}
    # --id y --completo prometen la fila ENTERA (MOC-4): con completo no se recorta nada; sin él, se ahorra contexto.
    corta = (lambda texto, n=220: texto) if completo else recorta
    cob = fila.get("_cobertura", "")
    parcial = f" ⚠ coincidencia parcial ({cob} términos)" if cob and cob.split("/")[0] != cob.split("/")[1] else ""
    cab = lambda titulo, extra="": (f"[{c.get('id', '?')} · {tabla}{(' · ' + extra) if extra else ''}] {titulo}"
                                    + parcial)
    out = []
    if "hacer" in c and "tema" in c:  # esquema de guía (M-2)
        out.append(cab(c["tema"], c.get("severidad", "")))
        out.append("  " + corta(c.get("descripcion", ""), 400 if completo else 240))
        out.append(f"  Hacer: {corta(c.get('hacer', ''), 200)} | Evitar: {corta(c.get('no_hacer', ''), 160)}")
        if completo:
            if c.get("ejemplo_bien"):
                out.append(f"  Bien: {c['ejemplo_bien']}")
            if c.get("ejemplo_mal"):
                out.append(f"  Mal:  {c['ejemplo_mal']}")
            out.append(f"  Puestos: {c.get('puestos', '')} · Artefacto: {c.get('artefacto', '')}"
                       + (f" · Aplica a: {c['aplica_a']}" if c.get("aplica_a") else ""))
    elif "para_que" in c:  # librerías
        out.append(cab(f"{c['nombre']} ({c.get('categoria', '')})", c.get("licencia", "")))
        out.append(f"  {corta(c['para_que'])}")
        out.append(f"  Cuándo sí: {corta(c.get('cuando_usar', ''), 160)} | Cuándo no: {corta(c.get('cuando_no', ''), 160)}")
        out.append(f"  Alternativas: {c.get('alternativas', '')} · Madurez: {c.get('madurez', '')}")
        c = dict(c, fuente=c.get("url", ""))
    elif tabla.endswith("componentes-21st"):
        out.append(cab(f"{c['nombre']} — @{c.get('autor', '')}", c.get("generos", "")))
        if c.get("descripcion_original"):
            out.append("  " + corta(c["descripcion_original"], 180))
        out.append(f"  id_demo: {c['id_demo']} · Aduana: colores crudos → tokens; traer el código gasta 1 de 2 diarias")
        c = dict(c, fuente=c.get("url", ""))
    elif tabla.endswith("plantillas-21st"):
        out.append(cab(c["nombre"], f"precio {c.get('precio', '')}"))
        out.append("  " + corta(c.get("descripcion_original", ""), 200))
        c = dict(c, fuente=c.get("url", ""))
    elif tabla.endswith("temas-21st"):
        out.append(cab(c["nombre"], c.get("modos", "")))
        out.append(f"  Fallos AA claro: {c['fallos_aa_claro']} | oscuro: {c['fallos_aa_oscuro']}")
        if c.get("fuente_sans"):
            out.append(f"  Fuentes: {c['fuente_sans']} · radio {c.get('radio', '')}")
        out += detalle_roles(tablas, tabla, c["id"], completo)
        c = dict(c, fuente=c.get("url", ""))
    elif tabla.endswith("paletas"):
        out.append(cab(c["producto"], "paleta"))
        out.append(f"  Foco: {c.get('foco_color', '')} · Fallos AA: {c['fallos_aa']}")
        if completo and c.get("notas"):
            out.append(f"  Notas: {c['notas']}")
        out += detalle_roles(tablas, tabla, c["id"], completo)
    else:
        campos = {
            "estilos": ["tipo", "ideal_para", "evitar_en", "accesibilidad"],
            "productos": ["estilo_principal", "patron_landing", "foco_color", "consideraciones"],
            "razonamiento": ["patron", "prioridad_estilo", "animo_color", "antipatrones"],
            "tipografia": ["ideal_para", "notas"],
            "fuentes": ["categoria", "estilos", "ejes_variables", "licencia"],
            "iconos": ["libreria", "uso", "ideal_para"],
            "graficas": ["cuando_usar", "cuando_no", "alternativa_accesible"],
            "movimiento": ["duracion", "easing", "hacer", "no_hacer"],
            "landing": ["orden_secciones", "ubicacion_cta", "conversion"],
        }.get(tabla.split("/")[-1])
        cols = [k for k in c if k not in ("id", "fuente")]
        base = tabla.split("/")[-1]
        titulo = {"iconos": lambda: f"{c['icono']} ({c.get('categoria', '')})",
                  "graficas": lambda: f"{c['tipo_de_dato']} → {c.get('grafica', '')}",
                  "movimiento": lambda: f"{c['categoria']} ({c.get('intensidad', '')})",
                  "tipografia": lambda: f"{c['par']}: {c.get('fuente_titulos', '')} + {c.get('fuente_cuerpo', '')}",
                  }.get(base, lambda: c.get(cols[0], "") if cols else "")()
        out.append(cab(titulo))
        for k in (campos or cols[1:4]):
            if c.get(k):
                out.append(f"  {k.replace('_', ' ').capitalize()}: {corta(legible(c[k]), 200)}")
        if completo:
            for k in cols[1:]:
                if k not in (campos or []) and c.get(k):
                    out.append(f"  {k.replace('_', ' ').capitalize()}: {corta(legible(c[k]), 300)}")
    if c.get("fuente"):
        out.append(f"  Fuente: {c['fuente']}")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Buscador del Mochilero")
    ap.add_argument("consulta", nargs="?", default="")
    ap.add_argument("--dominio", choices=list(DOMINIOS))
    ap.add_argument("--tabla", help="una o varias, separadas por comas (p. ej. ux,api o stacks/react)")
    ap.add_argument("--stack", help="atajo de --tabla stacks/<stack>")
    ap.add_argument("-n", type=int, default=3)
    ap.add_argument("--completo", action="store_true")
    ap.add_argument("--incluir-obsoletas", action="store_true")
    ap.add_argument("--id")
    ap.add_argument("--tablas", action="store_true")
    a = ap.parse_args(argv)
    tablas = cargar()

    if a.tablas:
        for dom in DOMINIOS:
            print(f"## {dom}")
            for t in sorted(x for x in tablas if dominio_de(x) == dom and x not in DETALLE):
                print(f"  {t.split('/', 1)[1]:<34}{len(tablas[t]):>6}  {INFO.get(t, '')}")
        return 0

    if a.id:
        for t, filas in tablas.items():
            for f in filas:
                if f.get("id", "").lower() == a.id.lower():
                    print(presentar(t, f, tablas, completo=True))
                    return 0
        print(f"No existe ninguna fila con id {a.id}.")
        return 1

    if not a.consulta:
        ap.print_help()
        return 2

    pedidas = set()
    for x in ((a.tabla or "").split(",") + ([f"stacks/{a.stack}"] if a.stack else [])):
        if x.strip():
            pedidas.add(x.strip().strip("/"))

    def filtro(tabla, fila):
        if a.dominio and dominio_de(tabla) != a.dominio:
            return False
        if pedidas and not any(tabla.split("/", 1)[1] == p or tabla == p for p in pedidas):
            return False
        if not a.incluir_obsoletas and fila.get("estado") == "obsoleta":
            return False
        return True

    idx = Indice(tablas)
    res, q = idx.buscar(a.consulta, filtro, a.n)
    if not res:
        print(f"Sin coincidencias verificadas para «{a.consulta}». Prueba con otros términos, con --dominio o mira "
              f"--tablas. No hay respuesta del Mochilero para esto: no se debe inventar.")
        sueltos = idx.por_termino(q, filtro)
        # Se enseña la palabra que escribió el puesto, no su raíz interna («habeas», no «habea»).
        escrita = {}
        for p in re.findall(r"[a-z0-9$@]+", normalizar(a.consulta)):
            escrita.setdefault(raiz(p), p)
        if any(total for _, total, _ in sueltos):
            print("Por término suelto (NO responden la consulta entera; úsalos solo si uno de ellos ES tu pregunta):")
            for t, total, filas in sueltos:
                t = escrita.get(t, t)
                if not total:
                    print(f"  «{t}» → ninguna fila")
                elif not filas:
                    print(f"  «{t}» → {total} filas: término demasiado común para orientar, añade otro")
                else:
                    ids = " · ".join(f"{f.get('id', '?')} {titulo(f)}" for _, f in filas)
                    print(f"  «{t}» → {total} fila{'s' if total > 1 else ''}: {ids}")
        return 1
    for _, tabla, fila in res:
        print(presentar(tabla, fila, tablas, a.completo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
