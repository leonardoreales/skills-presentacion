# Procedencia del Mochilero

## 1. ui-ux-pro-max → `datos/front/` (estilos, productos, razonamiento, paletas, tipografía, fuentes, iconos, gráficas, movimiento, landing, ux, app-nativa, rendimiento-react, stacks/)

- **Origen:** `nextlevelbuilder/ui-ux-pro-max-skill`, **MIT**, verificada el 2026-09-25 con la API de GitHub. Aviso
  en `LICENCIAS/ui-ux-pro-max-MIT.txt`.
- **Versión fijada:** copia local instalada el 2026-09-11, hash de carpeta
  `f0415e89eeadda8933a49a3f432acae52fa542aa`. Ruta: `~/.claude/skills/ui-ux-pro-max/data`.
- **Qué se cambió:**
  - las cabeceras y la prosa se tradujeron al español con 7 subagentes, según `trabajo/traduccion/BRIEF.md`;
  - las palabras clave quedaron en español e inglés;
  - las paletas pasaron a formato por rol y token, con el contraste WCAG calculado: 31 de 192 tienen alguna pareja
    que no cumple AA;
  - la licencia de cada fuente de Google se añadió a su fila;
  - se excluyeron 6 stacks de escritorio (WPF, WinUI, UWP, Uno, Avalonia, JavaFX);
  - las filas `deprecated` se marcaron como `obsoleta`.
- **Pulido:** el origen tiene 0 filas marcadas `[revisar]` por los traductores; se corrigió una errata, UX-098
  («Thumps» por «Thumbs»).
- **Puerta de fusión:** `fusionar` aplica solo los campos pedidos y guarda la huella del texto de origen en
  `trabajo/traduccion/huellas/`. Si al re-derivar cambia el texto de una fila, rechaza su traducción vieja.
- **Límite conocido (revisión, hallazgo 4):** los ids son la posición de la fila. En `styles.csv` la columna `No`
  del origen no coincide con la posición en 35 filas; por eso `fuente` cita el `No` del origen. Si una re-derivación
  cambia el orden, las huellas lo detectan, pero los ids citados en otros documentos podrían moverse. Arreglo
  pendiente: un mapa persistente de clave de origen → id.

## 2. 21st.dev → `componentes-21st`, `plantillas-21st`, `temas-21st`

- Solo herramientas gratuitas (`search`, `get_theme`), el 2026-09-25: **0 recuperaciones de código gastadas**.
- 757 componentes en 78 géneros, 49 plantillas y 45 temas en claro y oscuro. Solo 1 tema pasa AA en los dos modos.
  TEM-026 tiene el texto en `transparent` y cuenta como fallo.
- **La clave:** el Mochilero es su custodio oficial desde el 2026-09-25 (decisión de Leonardo, freno de la revisión,
  hallazgo 1, cerrado). Vive solo en `.mcp.json` de esta skill (1 de 194 ficheros, medido) y la lee
  `herramientas/clave_21st.js`. Detalle en la sección «Custodia» de `SKILL.md`.
- Cada componente tiene su propia licencia: se revisa al traerlo.

## 3. Investigación web → `datos/backend/`, `datos/automatizaciones/`, librerías y `rendimiento-web`

- **4 subagentes con WebFetch y WebSearch, el 2026-09-25.** Redactado con palabras propias y la URL en cada fila.
- **Lo que los investigadores declararon NO verificado:**
  - `api` y `seguridad-api`: no abrieron las guías de Microsoft, W3C trace-context, trpc.io, PortSwigger CORS ni
    varias cheat sheets de OWASP (URLs canónicas, sin descargar). Tampoco comprobaron las anclas `#section-x.y` de
    las RFC. OpenAPI 3.1 se cita con el índice de spec.openapis.org.
  - Los borradores que siguen siéndolo están marcados en su fila: Idempotency-Key (caducado), RateLimit y OAuth 2.1.
  - `resiliencia`, `datos`, `observabilidad` y `plataforma`: comprobaron que cada URL responde y que su título
    encaja, pero solo contrastaron el texto en unas pocas. Los ejemplos (k6, Kubernetes, pino, OTel) no se
    ejecutaron. La página RED de Grafana devuelve 403.
  - **Librerías y `rendimiento-web`:**
    - Las licencias se verificaron con npm, `gh api` y PyPI.
    - Temporal en Safari y `scheduler.yield()` quedaron **sin verificar** en la fecha de la investigación.
    - Las «fechas de madurez» son la fecha de la última publicación en npm, no una medida de estabilidad.
    - Avisos vigentes al investigar: el `latest` de `prisma` es una RC; Auth.js está en mantenimiento; `lucia` está
      deprecado; shadcn usa Base UI por defecto; `@base-ui-components/react` pasó a llamarse `@base-ui/react`.
  - **Automatizaciones** (webhooks, n8n, tareas y colas, integraciones, IA). Sus 77 URLs respondieron 200, pero
    declaró **sin verificar**:
    - los topes de Retry On Fail de n8n (5 intentos, 5000 ms), que salen de un foro y no de la documentación;
    - la condición de fin de la paginación del nodo HTTP Request, que no se sabe;
    - que `pinData` viaja en el JSON exportado, que se afirma sin cita;
    - que `$vars` no sirve para secretos, que es una deducción;
    - el ejemplo de horario de verano de TAR-003, que es razonamiento propio;
    - N8N-029, que se apoya en una analogía.
- `integrar_investigacion.py` solo comprueba que la fuente sea una URL, no que exista.

## 4. El bolsillo de presentacion-viva → `datos/presentacion/` (12 tablas, 308 filas, 2026-10-26)

Tres orígenes, todos por `trabajo/investigacion/*.jsonl` → `herramientas/integrar_investigacion.py`:

- **Migración del catálogo de presentacion-viva** (152 filas). Salen de `references/catalogo-visual.md` y
  `references/referencias-web.md`, consultados el 2026-10-23, más las reglas de `patrones-gsap.md` §4-5. El inventario
  que separa oficio y catálogo está en `fase-1-inventario.md` de la mesa de experimentos. Lo que en el origen iba como
  [NV] entra con `[revisar: …]`, igual que las filas de las fuentes que se añadieron en la migración y no se
  consultaron. **El oficio no se migró y sigue en presentacion-viva:** arcos, protocolo creativo, gramática del flujo,
  mecanismos con código, motor de video, perfil institucional y bitácora.
- **Vigía visual** (agente `vigia-visual`, 2026-10-26). Su JSONL trae 74 altas, aunque su resumen decía 66. Además
  reportó 24 cambios, 3 bajas y 12 alertas de licencia. Se descartaron 15 altas por duplicadas, cada una con su
  motivo. Las bajas y alertas entraron como 4 filas con veredicto Evitar o Vigilar: Typed.js 3.x, p5.js, mp4-muxer y
  Remix Icon. Los cambios se aplicaron a las filas migradas. El informe íntegro está en la mesa, en
  `investigacion/vigia-visual-2026-10-26.md`.
- **Oficio de presentar** (agente general, 2026-10-26). Trajo 104 filas: narrativa, legibilidad, accesibilidad,
  tipografía, frameworks, componentes, ilustración y color. Tiene 96 marcadas V y 8 NV, y se descartaron 11 por
  duplicadas.

**Verificado por Claude contra el origen** (no solo de palabra del agente): la API de cdnjs para GSAP 3.12.5 (13
`.min.js` en raíz, sin DrawSVG, MorphSVG ni SplitText) y para 3.15.0 (26, con todos); `remotion` latest = 4.0.539;
`typed.js` latest = 3.0.0 GPL-3.0; y el `LICENSE.md` de ApexCharts 8.5.0, cuyo tramo gratuito exige menos de USD 2M de
presupuesto. Lo demás es palabra de los agentes, con su URL.

**Recuento:** 185 filas de guía y 123 de librería. Los veredictos de las librerías se reparten así: Adoptar 37 ·
Probar 48 · Vigilar 11 · Condicional 6 · Evitar 20 · Mantener 1. **60 filas (19 %) llevan `[revisar]`.**

**No verificado** (lo declararon los agentes):
- Codrops (tympanus.net) devuelve 403: sus tutoriales se vieron solo por el buscador.
- No cargaron Apple HIG Motion, m3.material.io, ni las páginas de DANE y Openverse.
- Los valores hex de Okabe-Ito salen de fuentes secundarias.
- Ningún peso con gzip: los pesos son minificados sin comprimir, de jsDelivr.
- No se sabe si el iframe del Artifact concede `screen-wake-lock` o carga iframes de Datawrapper o Flourish.
- Faltan las fechas de commit de Zdog, Frappe, d3-svg-annotation, lottie-web y Revideo.
- Del estudio Garner y Alley (2013), de Mayer y Moreno (2003) y de Hyman (1953) solo se confirmó la ficha
  bibliográfica.

## 5. Imágenes del usuario → `librerias-imagen` (PIM, 16) y `tratamiento-imagen` (PTI, 22), 2026-10-26

Un agente general investigó en fuentes primarias (PyPI, npm, GitHub del proyecto, MDN, W3C/WAI, web.dev, Función
Pública, c2pa.org) cómo adaptar fotos e ilustraciones a una presentación: formatos, recorte, duotono, vectorizado,
quitar fondo, IA local y en la nube, accesibilidad y derechos. 38 filas, 10 con `[revisar]`. Su JSONL íntegro está en
la mesa, en `investigacion/librerias-imagen.jsonl` y `investigacion/tratamiento-imagen.jsonl`.

**Verificado por Claude contra el origen:** el modelo por defecto de `rembg` es `bria-rmbg`
(`rembg/session_factory.py`, `new_session(model_name: str = "bria-rmbg")`) y la lista de modelos `birefnet-*` del
README de rembg. Por eso `preparar-imagen.py fondo --ia` de presentacion-viva fija `birefnet-general`.

**Alertas:** BRIA RMBG-2.0 es CC BY-NC 4.0 (PIM-011, Evitar); Potrace es GPL (PIM-005) y @imgly/background-removal es
AGPL (PIM-014), ambos Condicional; el FFmpeg de gyan.dev se compila con GPL-3.0 (PIM-003); Real-ESRGAN con
`--face_enhance` inventa rasgos (PIM-013); Adobe Firefly y toda nube, Condicional porque la imagen sale del equipo.

**No verificado:** la licencia de BRIA se leyó por el agente (Hugging Face no sirvió el README sin sesión); Canva no tiene
fila porque su ayuda dio 403; la página de GrabCut de OpenCV dio 403 y la fila cita PyPI; sic.gov.co falló por
certificado TLS y la Ley 1581 se leyó en funcionpublica.gov.co.
