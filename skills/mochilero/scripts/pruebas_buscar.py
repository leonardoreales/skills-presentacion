"""Arnés del Mochilero. Solo biblioteca estándar.

  python pruebas_buscar.py

Comprueba cinco cosas y trae control negativo en cada una:
  1. relevancia: consultas reales de cada puesto devuelven la tabla correcta en los 3 primeros;
  2. honestidad: una consulta sin sentido responde «sin coincidencias», y una MUTACIÓN que quita el umbral de
     cobertura tiene que romper esa prueba (si no la rompe, la prueba no mira nada);
  3. tildes: «Paginación» y «paginacion» son el mismo término, y una MUTACIÓN sin plegado de tildes tiene que romperlo;
  4. obsoletas: una regla obsoleta no sale por defecto y sí con --incluir-obsoletas;
  5. integridad y contrato: ids únicos, reglas con tema y palabras clave, colores con token --color-*, contraste
     WCAG correcto contra valores conocidos, y respuesta por defecto dentro del presupuesto de contexto.
Sale con código 1 si algo falla. Una tabla que aún no existe cuenta como FALLO, no como omitida.
"""
import contextlib
import io
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), "herramientas"))
sys.stdout.reconfigure(encoding="utf-8")

import buscar  # noqa: E402
from derivar_uiuxpromax import contraste  # noqa: E402

RESULTADOS = []


def comprobar(nombre, condicion, detalle=""):
    RESULTADOS.append((bool(condicion), nombre, detalle))


TABLAS = buscar.cargar()
IDX = buscar.Indice(TABLAS)


def top(consulta, n=3, **filtro):
    dominio, tabla = filtro.get("dominio"), filtro.get("tabla")

    def f(t, fila):
        if dominio and buscar.dominio_de(t) != dominio:
            return False
        if tabla and t.split("/", 1)[1] != tabla:
            return False
        return fila.get("estado") != "obsoleta"
    res, _ = IDX.buscar(consulta, f, n)
    return [(t, fila.get("id", "")) for _, t, fila in res]


# 1. Relevancia: (consulta, tabla que debe aparecer en los 3 primeros)
CASOS = [
    ("paginacion cursor offset", "backend/api"),
    ("errores problem details 422", "backend/api"),
    ("idempotency key reintento POST", "backend/api"),
    ("autorizacion a nivel de objeto BOLA", "backend/seguridad-api"),
    ("cookies sesion samesite", "backend/seguridad-api"),
    ("reintentos backoff jitter", "backend/resiliencia"),
    ("circuit breaker dependencia", "backend/resiliencia"),
    ("indice compuesto orden columnas", "backend/datos"),
    ("trazas correlation id opentelemetry", "backend/observabilidad"),
    ("blue green canary despliegue", "backend/plataforma"),
    # La verificación de firmas vive legítimamente en dos tablas (SAPI-031 y WHK-001): se aceptan ambas.
    ("firma hmac webhook", ("automatizaciones/webhooks", "backend/seguridad-api")),
    ("webhook replay timestamp tolerancia", "automatizaciones/webhooks"),
    ("n8n error workflow", "automatizaciones/n8n"),
    ("cron solapamiento bloqueo", "automatizaciones/tareas-y-colas"),
    ("rate limit api tercero retry-after", "automatizaciones/integraciones"),
    ("inyeccion de prompt llm", "automatizaciones/ia-automatizacion"),
    ("contraste texto accesibilidad", "front/ux"),
    ("lcp imagen fetchpriority", "front/rendimiento-web"),
    ("glassmorphism", "front/estilos"),
    ("fintech banca", "front/paletas"),
    ("grafica serie temporal tendencia", "front/graficas"),
    ("formularios validacion react", "front/librerias-front"),
    ("orm postgres typescript", "backend/librerias-backend"),
    ("pricing table", "front/componentes-21st"),
    ("tema oscuro azul", "front/temas-21st"),
    # El bolsillo de presentacion-viva (2026-10-26): una pregunta real por tabla, sin filtro de dominio.
    ("diagrama quien hace que areas", "presentacion/diagramas"),
    ("sello aprobado", "presentacion/componentes-narrativos"),
    ("drawsvg motionpath combinacion", "presentacion/recetas"),
    ("scrolljacking", "presentacion/disciplina"),
    ("torta porciones", "presentacion/graficas-narrativas"),
    ("conclusion primero directivos", "presentacion/narrativa"),
    ("tamano de texto proyector sala", "presentacion/legibilidad"),
    ("trazo que se dibuja ruta", "presentacion/librerias-efectos"),
    ("video determinista frames", "presentacion/librerias-video"),
    ("sankey d3", "presentacion/librerias-graficas"),
    ("ilustraciones personas cc0", "presentacion/librerias-ilustracion"),
    ("diapositivas vista del presentador", "presentacion/librerias-presentacion"),
    ("quitar fondo foto modelo", "presentacion/librerias-imagen"),
    ("vectorizar imagen svg", "presentacion/librerias-imagen"),
    ("texto alternativo foto decorativa", "presentacion/tratamiento-imagen"),
    ("personas en fotos autorizacion", "presentacion/tratamiento-imagen"),
    ("metadatos gps exif", "presentacion/tratamiento-imagen"),
]
for consulta, esperada in CASOS:
    validas = esperada if isinstance(esperada, tuple) else (esperada,)
    if not all(v in TABLAS for v in validas):
        comprobar(f"relevancia «{consulta}»", False, f"la tabla {esperada} aún no existe")
        continue
    obtenido = top(consulta)
    comprobar(f"relevancia «{consulta}»", any(t in validas for t, _ in obtenido),
              f"esperaba {esperada}, obtuvo {[t for t, _ in obtenido]}")

# 2. Honestidad y su mutación.
comprobar("sin sentido → sin coincidencias", top("plomeria submarina api") == [], str(top("plomeria submarina api")))
original = buscar.Indice.buscar


def buscar_sin_umbral(self, consulta, filtro=lambda t, f: True, n=3, k1=1.4, b=0.75):
    q = buscar.tokens(consulta, self.norm)
    puntos = []
    for tabla, fila, tf, largo in self.docs:
        if not filtro(tabla, fila):
            continue
        s = sum(self.idf[t] * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * largo / self.media))
                for t in set(q) if tf.get(t))
        if s > 0:
            puntos.append((s, tabla, fila))
    puntos.sort(key=lambda x: -x[0])
    return puntos[:n], q


buscar.Indice.buscar = buscar_sin_umbral
comprobar("MUTACIÓN sin umbral rompe la prueba de honestidad", top("plomeria submarina api") != [],
          "la mutación no cambió nada: la prueba de honestidad no mira nada")
buscar.Indice.buscar = original

# 2b. Con 2 términos deben coincidir los dos (hallazgo de la revisión): «plomeria api» no es una consulta de API.
comprobar("2 términos, 1 ajeno → sin coincidencias", top("plomeria api") == [], str(top("plomeria api")))
comprobar("coincidencia parcial se marca", "coincidencia parcial" in buscar.presentar(
    "backend/api", dict(TABLAS["backend/api"][0], _cobertura="2/3"), TABLAS))
comprobar("CSS crudo (variables, css_clave) nunca se entrega (F-08)",
          all(k not in buscar.presentar("front/estilos", TABLAS["front/estilos"][0], TABLAS, completo=True)
              for k in ("Variables:", "Css clave:")))

# 3. Tildes y plurales, y su mutación.
comprobar("plurales simétricos (clave/claves, retry/retries, error/errores)",
          all(buscar.tokens(a) == buscar.tokens(b) for a, b in
              [("clave", "claves"), ("retry", "retries"), ("error", "errores"), ("indice", "indices")]))
comprobar("tildes plegadas", buscar.tokens("Paginación Autenticación") == buscar.tokens("paginacion autenticacion"))
sin_plegar = lambda t: t.lower()  # noqa: E731
comprobar("MUTACIÓN sin plegar tildes rompe la prueba",
          buscar.tokens("Paginación", sin_plegar) != buscar.tokens("paginacion", sin_plegar))

# 4. Obsoletas.
obsoletas = [(t, f) for t, filas in TABLAS.items() for f in filas if f.get("estado") == "obsoleta" and f.get("tema")]
if obsoletas:
    t, f = obsoletas[0]
    consulta = f["tema"]
    por_defecto = [i for _, i in top(consulta, n=10)]
    res, _ = IDX.buscar(consulta, lambda tt, ff: True, 10)
    con_flag = [ff.get("id") for _, tt, ff in res]
    comprobar("obsoleta oculta por defecto", f["id"] not in por_defecto, f"{f['id']} salió sin pedirla")
    comprobar("obsoleta visible si se pide", f["id"] in con_flag, f"{f['id']} no sale ni pidiéndola")
else:
    comprobar("hay reglas obsoletas marcadas", False, "ninguna fila con estado=obsoleta: ¿se perdió el marcado M-6?")

# 5. Integridad y contrato.
vistos, repetidos = set(), []
for t, filas in TABLAS.items():
    if t in buscar.DETALLE:
        continue
    for f in filas:
        i = f.get("id", "")
        if not i or i in vistos:
            repetidos.append(f"{t}:{i}")
        vistos.add(i)
comprobar("ids únicos y no vacíos", not repetidos, str(repetidos[:5]))
reglas_malas = [f"{t}:{f['id']}" for t, filas in TABLAS.items() for f in filas
                if "hacer" in f and "tema" in f and not (f["tema"].strip() and f["palabras_clave"].strip())]
comprobar("reglas con tema y palabras clave", not reglas_malas, str(reglas_malas[:5]))
tokens_malos = [f"{t}:{f['rol']}" for t in buscar.DETALLE for f in TABLAS.get(t, [])
                if not f["token"].startswith("--color-")]
comprobar("colores por token --color-* (F-08)", not tokens_malos and all(t in TABLAS for t in buscar.DETALLE),
          str(tokens_malos[:5]))
comprobar("contraste negro/blanco = 21", abs(contraste("#000000", "#FFFFFF") - 21) < 0.01)
comprobar("contraste #767676/blanco ≥ 4.5 (límite AA)", 4.5 <= contraste("#767676", "#FFFFFF") < 4.6)
comprobar("contraste #777777/blanco < 4.5", contraste("#777777", "#FFFFFF") < 4.5)

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    buscar.main(["reintentos backoff jitter"])
salida = buf.getvalue()
comprobar("respuesta por defecto ≤ 2.500 caracteres (~700 tokens)", 0 < len(salida) <= 2500, f"{len(salida)} caracteres")
comprobar("cada resultado lleva su fuente", salida.count("Fuente:") == len(re.findall(r"^\[", salida, re.M)))

# 5b. Dominio presentacion (el bolsillo de presentacion-viva, 2026-10-26): contrato de sus filas y su filtro.
PREFIJOS = {"diagramas": "PDG", "componentes-narrativos": "PCN", "recetas": "PRC", "disciplina": "PDS",
            "graficas-narrativas": "PGN", "narrativa": "PNR", "legibilidad": "PLG", "librerias-efectos": "PTC",
            "librerias-video": "PVD", "librerias-graficas": "PLB", "librerias-ilustracion": "PIC",
            "librerias-presentacion": "PFW", "librerias-imagen": "PIM", "tratamiento-imagen": "PTI"}
faltan = [t for t in PREFIJOS if f"presentacion/{t}" not in TABLAS]
comprobar("las 14 tablas de presentacion existen", not faltan, str(faltan))
malas = [f"{t}:{f.get('id')}" for t, pre in PREFIJOS.items() for f in TABLAS.get(f"presentacion/{t}", [])
         if not f.get("id", "").startswith(pre + "-")
         or not re.match(r"https?://", f.get("fuente") or f.get("url") or "")
         or "PRV" not in f.get("puestos", "")
         or "[revisar" in f.get("verificado_el", "")]
comprobar("presentacion: prefijo de id, fuente con URL, puesto PRV y [revisar] fuera de la fecha", not malas, str(malas[:5]))


def contrato_roto(fila, pre):
    return (not fila.get("id", "").startswith(pre + "-") or not re.match(r"https?://", fila.get("fuente") or fila.get("url") or "")
            or "PRV" not in fila.get("puestos", "") or "[revisar" in fila.get("verificado_el", ""))


base = TABLAS["presentacion/diagramas"][0]
comprobar("MUTACIÓN: una fila sin fuente, sin PRV, con otro prefijo o con [revisar] en la fecha rompe el contrato",
          not contrato_roto(base, "PDG") and all(contrato_roto(dict(base, **m), "PDG") for m in
          ({"fuente": "sin url"}, {"puestos": "DFC"}, {"id": "PTC-001"}, {"verificado_el": "2026-10-26 [revisar: x]"})))
solo_dominio = lambda t, f: buscar.dominio_de(t) == "presentacion"  # noqa: E731
res, _ = IDX.buscar("duracion animacion escena", solo_dominio, 3)
comprobar("--dominio presentacion solo devuelve filas del dominio", res and all(t.startswith("presentacion/") for _, t, _ in res),
          str([t for _, t, _ in res]))
res_sin, _ = IDX.buscar("duracion animacion escena", lambda t, f: True, 3)
comprobar("MUTACIÓN sin filtro de dominio cuela otras tablas (la prueba anterior mira algo)",
          any(not t.startswith("presentacion/") for _, t, _ in res_sin), str([t for _, t, _ in res_sin]))
comprobar("presentacion: sin sentido → sin coincidencias", IDX.buscar("plomeria submarina", solo_dominio, 3)[0] == [])
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    buscar.main(["sankey d3", "--dominio", "presentacion"])
comprobar("CLI --dominio presentacion responde con fuente", "PLB-015" in buf.getvalue() and "Fuente:" in buf.getvalue(),
          buf.getvalue()[:200])


# 6. Falsa ausencia (MOC-1) y su mutación. En el examen, «education booking» respondió «sin coincidencias» y el puesto
#    concluyó que no había paleta, cuando PAL-009 y PAL-104 existen: ninguna fila tiene los DOS términos.
def ejecutar(argv):
    b = io.StringIO()
    with contextlib.redirect_stdout(b):
        buscar.main(argv)
    return b.getvalue()


mezcla = ejecutar(["education booking", "--tabla", "paletas"])
comprobar("mezcla de dos productos sigue sin respuesta completa (no se relaja la regla)",
          top("education booking", tabla="paletas") == [] and "Sin coincidencias verificadas" in mezcla)
comprobar("…pero orienta por término suelto: PAL-009 y PAL-104 a la vista", "PAL-009" in mezcla and "PAL-104" in mezcla,
          mezcla)
# Hasta el 2026-10-26 la consulta era «ley 1581 habeas data», sin respuesta completa; desde PTI-018 la tiene, así que
# la premisa (consulta sin respuesta que orienta por término suelto) se conserva con un término ajeno.
comprobar("se enseña la palabra escrita, no la raíz («habeas», no «habea»)",
          "«habeas»" in ejecutar(["habeas plomeria"]) and "«habea»" not in ejecutar(["habeas plomeria"]))
comprobar("«ley 1581 habeas data» ya responde: PTI-018 (personas en fotos)",
          ejecutar(["ley 1581 habeas data"]).startswith("[PTI-018"))
nada = ejecutar(["plomeria submarina", "--tabla", "paletas"])
comprobar("control negativo: términos ajenos no listan ningún id", not re.search(r"\b[A-Z0-9]{2,4}-\d{3,4}\b", nada), nada)
original_pt = buscar.Indice.por_termino
buscar.Indice.por_termino = lambda self, q, filtro=None, **k: []
comprobar("MUTACIÓN sin orientación rompe la prueba de falsa ausencia",
          "PAL-104" not in ejecutar(["education booking", "--tabla", "paletas"]),
          "la mutación no cambió nada: la prueba de falsa ausencia no mira nada")
buscar.Indice.por_termino = original_pt

# 7. Borde (MOC-2): WCAG 1.4.11 pide 3:1 al borde que es el único límite de un control. Se mide y su fallo es
#    CONDICIONAL (⚠1.4.11), no ✗AA, porque no todo borde delimita un control.
from derivar_uiuxpromax import PAREJAS, veredicto  # noqa: E402
comprobar("el borde se mide contra el fondo a 3:1", PAREJAS.get("borde") == ("fondo", 3.0), str(PAREJAS.get("borde")))
comprobar("veredicto: borde bajo = condicional; texto bajo = no; suficiente = sí",
          (veredicto("borde", 1.1, 3.0), veredicto("tinta", 1.1, 4.5), veredicto("borde", 3.2, 3.0))
          == ("condicional", "no", "sí"))
bordes = {f["paleta_id"]: f for f in TABLAS.get("front/paletas-roles", []) if f["rol"] == "borde"}
comprobar("PAL-104: su borde (1,10:1) queda medido y marcado condicional",
          bordes.get("PAL-104", {}).get("cumple_aa") == "condicional", str(bordes.get("PAL-104")))
p104 = ejecutar(["--id", "PAL-104"])
comprobar("PAL-104 ya no dice «Fallos AA: ninguno» y marca el borde ⚠1.4.11",
          "Fallos AA: ninguno" not in p104 and "⚠1.4.11" in p104, p104)
comprobar("control negativo: ningún borde lleva ✗AA (sería mentir hacia el otro lado)",
          all(f["cumple_aa"] != "no" for f in bordes.values()) and len(bordes) > 100, f"{len(bordes)} bordes")

# 8. Hueco de contenido (MOC-3): RF-03 («no hay dos reservas solapadas del mismo recurso») tiene su regla, curada
#    por BD. En el examen la mochila respondía «no tiene una fila sobre exclusión por rangos».
comprobar("RF-03: «reservas solape» y «double booking» traen DAT-027",
          all(("backend/datos", "DAT-027") in top(q, dominio="backend") for q in ("reservas solape", "double booking")),
          str([top(q, dominio="backend") for q in ("reservas solape", "double booking")]))

# 9. `--id` trae la fila ENTERA (MOC-4, hallado en el repaso de la P1 de la 0.1.1): recortaba «Hacer» a 200 y
#    «Evitar» a 160 y escondía el NOT NULL y el isempty de DAT-027. Dos signos: entera con --id, recortada por defecto.
d27 = next(f for f in TABLAS["backend/datos"] if f["id"] == "DAT-027")
entera = ejecutar(["--id", "DAT-027"])
comprobar("--id DAT-027 trae «Hacer» y «Evitar» enteros", d27["hacer"] in entera and d27["no_hacer"] in entera,
          entera[:300])
comprobar("MOC-5: DAT-027 limita la exclusión a las reservas vigentes (WHERE que libera canceladas y liberadas)",
          "WHERE (estado NOT IN" in d27["ejemplo_bien"] and "liberada" in d27["hacer"]
          and ("backend/datos", "DAT-027") in top("reserva cancelada liberada franja", dominio="backend"))
comprobar("control: sin --completo la búsqueda sigue recortando (ahorro de contexto)",
          d27["hacer"] not in ejecutar(["reservas solape", "--dominio", "backend", "-n", "1"]))

# Informe.
fallos = [r for r in RESULTADOS if not r[0]]
for ok, nombre, detalle in RESULTADOS:
    print(("✅ " if ok else "❌ ") + nombre + ("" if ok else f"  → {detalle}"))
print(f"\n{len(RESULTADOS) - len(fallos)}/{len(RESULTADOS)} en verde")
sys.exit(1 if fallos else 0)
