---
name: presentacion-viva
description: Oficio para convertir CUALQUIER tema en una presentación viva cuya especialidad son los VIDEOS DE FLUJO (un objeto que viaja de etapa en etapa por un camino SVG animado, con la evidencia de cada paso y el resultado, renderizado a MP4) integrados en una página con scroll y escenas GSAP. Sirve con un repo, documentos, notas, fotos o ilustraciones (las adapta y anima), una idea dicha o un tema sin material, y con cualquier audiencia (junta, comité, estudiantes, clientes, clase, inducción). Úsala siempre que Leo pida presentar, explicar o contar algo de forma visual y animada, y sobre todo cuando haya un proceso, trámite, ciclo de vida, recorrido o historia que se cuente paso a paso, aunque no diga «presentación viva» ni «video». Frases típicas - «haz un video del flujo», «como los videos de SIGAF», «muéstrale el proyecto a los directivos», «explica este trámite con animaciones», «scrollytelling», «usa estas fotos en la presentación». NO es para un .pptx, un dashboard ni auditar el diseño de una app.
---

# Presentación viva

Un oficio, no una plantilla. Nació de la presentación de SIGAF, Talento Humano y Mantenimiento ante los
directivos de la Corporación Universitaria Americana ([bitácora](references/bitacora-de-presentaciones.md)), y lo
que más impresionó fueron **los videos de flujo**: un objeto que viaja por las etapas de un proceso, cada etapa
enseña su evidencia y al final se ve el resultado. Eso es la especialidad de esta skill y su diferencia con
cualquier otra: **convertir un proceso en un viaje que se ve**, con cualquier tema, cualquier composición y
cualquier identidad. La página con scroll es el escenario donde esos videos brillan.

Lo que funcionó y sirve para todo: **cada parte tiene una metáfora sacada de su mundo**, **todo se lee aunque falle
la animación** y **nada es inventado**.

Leo no es programador: habla con él de efectos y decisiones, no de código. Las preguntas, de una en una.

**Rutas de los scripts:** `<carpeta de la skill>` es la carpeta de esta skill, la que Claude muestra como «Base
directory» al cargarla (en la copia de trabajo, `~/.claude/skills/presentacion-viva`; instalada desde el plugin
`skill-de-autor`, otra). Los comandos de abajo la usan para funcionar en cualquier equipo.

## Reglas universales

- **Nada inventado.** Cada paso, estado, fecha y nombre sale de la fuente; lo que no está, se marca pendiente.
- **Cifras con fuente y fecha**, una por capítulo como mucho: una cifra sin fuente arrastra la credibilidad de todo.
- **Ningún dato personal sin permiso**, tampoco en capturas ni en maquetas (por eso las maquetas son abstractas).
- **Se lee sin animación.** El estado en reposo de cada escena es el final; con `prefers-reduced-motion` o con el CDN
  caído, la página se lee entera. Sin JS, el texto se lee; si una escena es imprescindible sin JS, dibuja su SVG en
  el HTML en vez de generarlo.
- Si hay perfil institucional, sus reglas se suman a estas (fase 3).

## Registro de trabajo (`notas.md`)

Todo encargo deja `notas.md` junto a los entregables y se escribe **mientras se trabaja**, no al final. Es lo que
deja a Leo revisar sin rehacer, y a la siguiente presentación no repetir. Sin él, una decisión no está tomada:
está supuesta. Siempre lleva estas secciones (sin ellas la iteración 3 de las evals bajó del 98 % al 91 %):

1. **Fuentes:** de dónde sale cada flujo (`fichero:línea`, documento o texto de Leo) y cada cifra (URL o documento,
   con fecha).
2. **Arco:** el elegido, por qué, y al menos un arco alternativo descartado con su porqué.
3. **Conceptos:** una tabla por escena **y por flujo de video**, sin excepción: tres conceptos, el elegido y el
   porqué de cada descarte. Una escena sin su fila no está decidida.
4. **Datos ficticios:** si se inventan datos de ejemplo (personas, montos, códigos, áreas), una línea que diga cuáles
   son ficticios. Si no se inventó ninguno, también se dice.
5. **Pregunta y supuestos:** **como mucho una pregunta** a Leo (la de la fase 2). Todo lo demás que no se sabe es un
   supuesto: se escribe «Supuesto: …» con lo que se tomó, nunca como pregunta. Contar dos preguntas es el fallo
   más repetido de las evals.
6. **Verificación:** cada comando corrido y su resultado, y la lista de lo que no se pudo verificar y por qué.
7. **Imágenes**, si hay: el inventario de [imagenes.md](references/imagenes.md) §2.

## El bolsillo: el Mochilero

El oficio vive aquí y aquí se decide. El catálogo (qué diagramas, componentes, recetas, librerías y reglas existen,
con su fuente, su licencia y su veredicto) vive en el **Mochilero**, en el dominio `presentacion`:

```
python "<carpeta de esta skill>/../mochilero/scripts/buscar.py" "<2 a 5 términos>" --dominio presentacion
```

Cada fase de abajo dice qué preguntarle. Son como mucho 3 consultas por escena, y se cita el id de la fila al
justificar una elección. Si el Mochilero no está, se sigue con [mecanismos.md](references/mecanismos.md) y
[referencias-web.md](references/referencias-web.md), y se dice. Las consultas
probadas, cómo leer la respuesta y cómo devolverle lo aprendido están en
[bolsillo-mochilero.md](references/bolsillo-mochilero.md).

## Fases

Cada fase termina en una **puerta**: no se pasa a la siguiente sin cumplirla. **Atajo:** si el pedido es «solo el
video», haz las fases 1 y 4 (y la 3 solo para la identidad), y entrega MP4 y hoja de contactos.

### 1. Entender el tema y encontrar sus flujos
- **Repo de código:** lanza un agente explorador (`feature-dev:code-explorer` o `Explore`) que escriba cada flujo
  real como *disparador → pasos → estados → resultado*, con rutas `fichero:línea`. Comprueba lo que devuelve.
- **Documentos, PDF, hojas de cálculo:** léelos (`markitdown` convierte PDF/DOCX/XLSX) y extrae lo mismo.
- **Notas o una idea dicha:** reescríbela ordenada y devuélvesela a Leo para que confirme. No lances exploradores.
- **Tema sin material:** investiga con fuentes verificables y guarda cada una con su URL.
- **Fotos, ilustraciones, logos o capturas:** inventario en `notas.md`, una línea por imagen: qué es, qué hace en la
  historia, procedencia y licencia, si salen personas y su resolución ([imagenes.md](references/imagenes.md) §2).
  Capturas con datos personales se recrean como maqueta ficticia. Mide qué herramientas hay con
  `python scripts/preparar-imagen.py diagnostico`; sin Python, el taller del nivel 0 (§1).

Mientras lees, marca **qué se puede contar como «primero…, luego…, al final…»**: esos son los flujos candidatos a
video ([gramatica-del-flujo.md](references/gramatica-del-flujo.md) §2).

**Puerta:** un resumen del tema con fuentes, y la lista de flujos candidatos, que Leo reconoce como ciertos.

### 2. Derivar el arco
Aplica [arcos-narrativos.md](references/arcos-narrativos.md): audiencia → decisión o reacción buscada → tensión →
secuencia que la resuelve. Si el pedido no dice audiencia ni reacción, pregunta **una sola cosa**: «¿Quién lo va a
ver y qué quieres que decidan o sientan al terminar?». Los arcos del fichero son ejemplos; si ninguno encaja,
inventa uno. Decide **en qué capítulo va la sala de flujos**: suele ser el clímax, donde el proceso se ve funcionar.
Bolsillo: `--tabla narrativa` (conclusión primero, regla pico-final para abrir y cerrar, revelación progresiva).

**Puerta:** la lista de capítulos leída en voz alta cuenta la historia por sí sola.

### 3. Identidad y escenas (protocolo creativo)
Sigue [protocolo-creativo.md](references/protocolo-creativo.md): inventario del mundo del tema; por escena **tres
conceptos distintos** con mecanismos de [mecanismos.md](references/mecanismos.md) y las opciones del bolsillo
(abajo); descarta los genéricos diciendo por qué; crítica final:
**«¿esto se confundiría con otra presentación?»**. Para cada flujo, el mismo protocolo decide su composición (la
forma del camino) y la maqueta de cada etapa. Bolsillo, para ampliar el abanico antes de elegir:
`diagramas`, `componentes-narrativos` y `recetas`. Si hay datos, también `graficas-narrativas`: la gráfica se elige
por la pregunta y se descartan las que engañan. Para la identidad, `legibilidad` (texto en sala, cifras tabulares).

Identidad: con perfil (p. ej. [perfil-institucional-americana.md](references/perfil-institucional-americana.md)),
se aplica en la página (`--perfil`) y en los videos (`SV.tema('americana')`); sin perfil, se deriva del tema y los
videos la reciben como tres colores `{ fondo, tinta, acento }`. Si hay imágenes, la identidad incluye **un solo
tratamiento para todas** (duotono con el tema, grises con acento o color con velo): fotos de orígenes distintos
sin tratar se ven como un collage ([imagenes.md](references/imagenes.md) §2-3). Para ideas frescas,
[referencias-web.md](references/referencias-web.md) y, antes de algo importante o cada mes, el agente `vigia-visual`.

**Puerta:** Leo ve, por escena y por flujo, el concepto elegido y los descartados en una línea cada uno, y aprueba.

### 4. Los flujos en video (la especialidad)
Todo el oficio está en [gramatica-del-flujo.md](references/gramatica-del-flujo.md): por qué funcionan, el guion, la
anatomía, las composiciones (lineal, zigzag, ciclo, arco, escalera o un trazo con la forma del tema), las maquetas,
las microacciones, el ritmo de ~14 s y la revisión. Míralo junto a `assets/referencia/hoja-*.jpg`, el listón.
**No todo es un camino con estaciones** (§5.bis): si la última entrada de la bitácora usó estaciones, o el proceso
gira alrededor de un papel, usa otra gramática. La más celebrada hasta hoy es el **documento protagonista** (guía de
traslado, 2026-10-30: «quedó muy áspero»): plantilla `assets/motor-video/flujo-4-documento.html`, con `limpio: true`
y `SV.poses`, `SV.escribir`, `SV.trazo`, `SV.sello`. Para una **guía** (se mira para aprender) el video puede durar
~45 s si cada panel es un solo paso.
1. Escribe el **guion** de cada flujo (tabla: etapa, frase, estado real, maqueta, microacción) y enséñalo.
2. **Prepara el motor una vez por máquina:** `node "<carpeta de la skill>/scripts/motor.mjs" estado`
   (3 s) y, si no está `listo`, `motor.mjs preparar`. Nada de copiar el motor ni `npm install` por presentación:
   la carpeta de flujos (`nueva-presentacion.mjs --video`) solo lleva `motor.js`, `comun.css` y los `flujo-*.html`.
   Genera el esqueleto: `node "<carpeta de la skill>/scripts/nuevo-flujo.mjs" guion.json <carpeta-de-flujos>`.
3. Dibuja cada maqueta y su microacción. **Renderiza en sitio** (`motor.mjs render <carpeta-de-flujos> <id> --stills …`),
   **revisa en una pasada** (stills de todos los flujos y `revisar.mjs`), **corrige todo en una tanda** y solo
   entonces el render final, una vez (`motor.mjs render <carpeta-de-flujos>`). Un render completo por cada
   corrección suelta era el mayor gasto de tiempo, y no mejora nada.
   **`revisar.mjs` SUSTITUYE a la revisión manual, no se suma a ella** (§6), y **vale también para un video solo:**
   apúntalo a la carpeta de los flujos (sin `index.html` se salta lo de la página y corre `verificar.mjs` en modo
   flujo sobre cada `flujo-*.html`, los vetados y ffprobe de cada MP4). Para un video solo la revisión completa es:
   stills mirados + `revisar.mjs` + la hoja de contactos del render final, mirada entera.
Técnica del motor, requisitos (Node, Chromium headless shell de Playwright, ffmpeg) y errores conocidos:
[videos-deterministas.md](references/videos-deterministas.md). Si falta una herramienta, dilo; no finjas el render.
Bolsillo: `librerias-video` (motores y licencias; Playwright Clock y `getAnimations()` para lo que no expone `seek`).

**Puerta:** `verificar.mjs` sobre cada flujo da PASA (modo flujo); la hoja de contactos, mirada entera, no tiene
texto cortado ni datos personales; y **cada MP4 lleva al lado su alternativa en texto**, la lista de etapas
(WCAG 1.2.1, PDS-043): un video mudo no puede ser la única fuente.

### 5. Construir la página
```
node "<carpeta de la skill>/scripts/nueva-presentacion.mjs" <carpeta> --titulo "…" [--perfil americana] [--video]
```
Copia el andamiaje (`assets/andamiaje/index.html`): tokens, franja con capítulo y progreso, modo presentador
(Av Pág / Re Pág), movimiento reducido, librerías con versión fija, la API de escenas `PV.escena(id, construir)` y la
**sala de flujos** (pestañas de video, comentada en el `<main>`). Escribe los capítulos del arco, borra la escena de
humo, construye cada escena con su mecanismo y pon los MP4 en `media/` dentro de la sala. Antes de la primera
escena, lee las **trampas ya pagadas** de [patrones-gsap.md](references/patrones-gsap.md). Antes de usar un plugin
o una librería, su fila en `librerias-efectos` o `librerias-graficas` da la versión, el CDN exacto y el veredicto.
**En cdnjs, GSAP 3.12.5 no trae DrawSVG, MorphSVG ni SplitText** (PTC-035): con el andamiaje en 3.12.5, usar
`pathLength`, o subir todas las URL a 3.15.0.
**Imágenes:** prepáralas con el escalón más bajo que resuelva ([imagenes.md](references/imagenes.md) §1): el taller
`assets/taller-imagen/index.html` (cualquier navegador) o `scripts/preparar-imagen.py` (`formato`, `duotono`,
`trazo`, `fondo`, `kenburns`). Se animan con `PV.escena(id, construir, false)`, que no crea lienzo y hereda el
movimiento reducido (§4). La página nunca depende de esas herramientas: solo de sus ficheros en `media/`.

**Puerta:** todas las escenas quedan en su estado final con movimiento reducido, y la sala reproduce cada flujo.

### 6. Verificar con criterios medibles
Una pasada, una tanda: se junta todo lo que falla y se corrige de una vez, no hallazgo a hallazgo.
**`revisar.mjs` ES esta revisión; no se complementa con la tuya.** No escribas scripts propios de capturas, mosaicos,
consola, desborde ni vetados: ya los hace, y repetirlos costó ~9 min en la medición (28-oct). Se corre **a lo sumo
dos veces**: la primera para reunir TODOS los hallazgos y la segunda, tras corregirlos en una tanda, para confirmar
PASA. Una tercera corrida o un diagnóstico propio solo se justifican si la máquina no puede medir lo que falla (ver
el punto 3), y acotados a eso.
1. `node "<carpeta de la skill>/scripts/revisar.mjs" <carpeta> --vetar "<términos>"` → **PASA**. Corre
   `verificar.mjs` sobre la página y cada flujo, abre la página a 1440 px, 375 px y con movimiento reducido, busca
   los vetados en todos los ficheros de texto, mira cada MP4 con ffprobe y deja `_revision/revision.json` y dos
   mosaicos. Un vetado cuenta aunque esté en un `<meta>` o un comentario: la regla es el grep.
2. Cada cifra que lista `verificar.mjs` tiene su fuente al lado (o en una nota) y es la de la fase 1.
3. **Mira enteros `_revision/mosaico-1440.png` y `mosaico-375.png`** (texto de las escenas legible, ≥12 px reales;
   nada encimado ni cortado). El script mide 0 errores de consola, sin scroll horizontal, imágenes cargadas y el
   estado final con movimiento reducido; lo que no mide (íconos que se ven, la sala con controles en reducido) se
   comprueba en el navegador.
4. El perfil, si hay: sus términos vetados en cero.
5. Repaso con el bolsillo (`--tabla disciplina`): destellos (2.3.1), bucles con pausa (2.2.2), contraste 3:1 de líneas
   e íconos (1.4.11) y licencia y atribución de cada recurso de terceros (PDS-030).
6. Imágenes, si hay: `media/manifiesto.json` sin un `PENDIENTE` (texto alternativo, procedencia, personas con
   autorización) y ningún original con metadatos publicado ([imagenes.md](references/imagenes.md) §6).
   `verificar.mjs` ya da FALLA ante un `alt="PENDIENTE"`.
7. **Lenguaje de la audiencia:** si no es técnica (o el pedido dice «sin entrar en lo técnico»), lee los rótulos de
   las escenas y de los videos con sus alternativas en texto y confirma que **no hay jerga técnica visible**
   (API, endpoint, nombres de lenguajes, librerías o nubes). `revisar.mjs` no la mide: se lee. El perfil
   ([perfil-institucional-americana.md](references/perfil-institucional-americana.md)) trae la regla y cómo traducir
   las capas de construcción.
8. **Entrega limpia:** `notas.md` va terminado **antes** de la última corrida de `revisar.mjs` y sin copiar la cadena
   `--vetar` ni los términos vetados. Con esa corrida en PASA y los mosaicos ya mirados, **borra `_revision/`** (y
   `_tmp/`, `_fotogramas/`): es carpeta de trabajo, `revision.json` repite rutas absolutas y los términos hallados.
   Entrega lo que no se borra: `index.html`, `media/`, `video/`, `capturas/`, `notas.md`.

**Puerta:** los ocho puntos con su evidencia, o la lista de lo que no se pudo verificar y por qué.

### 7. Entregar y registrar
- Publica como Artifact (misma `file_path` o `url` para conservar el enlace; imágenes y MP4 en `files`, dentro del
  directorio de trabajo) o entrega la carpeta.
- **Para mandarlo por correo o dejarlo en Descargas:** `node scripts/exportar.mjs <carpeta> --nombre "Nombre"
  [--css-impresa impresa.css] [--captura]` → un HTML autocontenido (todo embebido, funciona sin internet) y un PDF
  de un capítulo por página, con los videos cambiados por su hoja de contactos. Prueba el HTML **sin red a 375 px** y
  da PASA/FALLA. Con `--captura`, **mira `_revision/impresa.png`**: un capítulo que no cabe en 900 px se corta en el
  papel y solo se ve mirando; se arregla en `impresa.css`, no en la página.
- Escribe la entrada en [bitacora-de-presentaciones.md](references/bitacora-de-presentaciones.md): audiencia, arco,
  escenas y flujos con descartes, identidad, verificación. Después de la reunión, «qué funcionó con la audiencia».
- Lo que funcionó y sirve para cualquier presentación vuelve al bolsillo como fila nueva, siguiendo el procedimiento
  y la puerta de [bolsillo-mochilero.md](references/bolsillo-mochilero.md) («Devolver lo aprendido»).

## Antipatrones (y por qué)

- **Un flujo sin flujo:** forzar el video sobre una comparación o una cifra da una fila de cajas con una bolita.
- **Todas las etapas con la misma tarjeta:** si la maqueta no cambia, la audiencia deja de mirar el panel.
- **Videos de 30 s o más:** se pierde el hilo; un flujo largo son dos historias. Excepción: una guía con un
  protagonista que no se va y un paso por panel (§5.bis).
- **Repetir la composición de la presentación anterior:** Leo vetó la línea de estaciones cuando ya la había visto;
  la bitácora dice cuál se usó la última vez.
- **El mismo diagrama para todo** o **texto donde cabía un diagrama.**
- **Animación de entrada en cada tarjeta** y **secuestrar el scroll:** movimiento sin significado.
- **Copiar una metáfora de la bitácora tal cual:** inspira, no es molde.
- **Clichés de IA** (degradados morados, cerebros, robots, circuitos) y **colores literales** en los flujos.

## Mapa de ficheros

| Cuándo | Fichero |
|---|---|
| Fase 1 y 4, el corazón: guion, composición, maquetas, ritmo | [references/gramatica-del-flujo.md](references/gramatica-del-flujo.md) |
| Fase 4, técnica del motor y render | [references/videos-deterministas.md](references/videos-deterministas.md) |
| Fase 2, derivar el orden | [references/arcos-narrativos.md](references/arcos-narrativos.md) |
| Fase 3, conceptos e identidad | [references/protocolo-creativo.md](references/protocolo-creativo.md) |
| Fase 3-5, construir cada pieza | [references/mecanismos.md](references/mecanismos.md) · bolsillo: `diagramas`, `componentes-narrativos`, `recetas` |
| Fase 3, ideas y fuentes externas | [references/referencias-web.md](references/referencias-web.md) |
| Todas las fases, el catálogo consultable con fuente (Mochilero) | [references/bolsillo-mochilero.md](references/bolsillo-mochilero.md) |
| Fase 5, antes de la primera escena | [references/patrones-gsap.md](references/patrones-gsap.md) |
| Fases 1, 3, 5 y 6, si el usuario trae fotos o ilustraciones | [references/imagenes.md](references/imagenes.md) · `assets/taller-imagen/index.html` · `scripts/preparar-imagen.py` |
| Presentaciones de la Americana | [references/perfil-institucional-americana.md](references/perfil-institucional-americana.md) |
| Fase 7, y al empezar para no repetir | [references/bitacora-de-presentaciones.md](references/bitacora-de-presentaciones.md) |
| El listón visual de los flujos | `assets/referencia/hoja-*.jpg` (con estaciones: `hoja-flujo-1..3`; documento protagonista: `hoja-flujo-4-documento`, `hoja-guia-traslado-documento`) |
| Andamiaje · motor y ejemplos de flujo | `assets/andamiaje/index.html` · `assets/motor-video/` (lineal, cierre con puente, ciclo, documento protagonista) |
| Scripts | `scripts/nueva-presentacion.mjs` · `scripts/nuevo-flujo.mjs` · `scripts/motor.mjs` (preparar una vez, render en sitio) · `scripts/verificar.mjs` · `scripts/revisar.mjs` (revisión en una pasada) · `scripts/exportar.mjs` (HTML autocontenido + PDF + prueba sin red) · `scripts/preparar-imagen.py` (+ `pruebas-preparar-imagen.py`) |
