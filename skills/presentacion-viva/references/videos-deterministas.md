# Videos deterministas: el motor `seek(t)`

El oficio (qué contar, cómo componerlo, maquetas, ritmo) está en [gramatica-del-flujo.md](gramatica-del-flujo.md).
Aquí va la técnica.

Por qué un motor propio: cada fotograma es una **función pura del tiempo**, así que el render sale idéntico cada vez,
se puede pedir el fotograma 6,2 s para revisarlo y no depende de la velocidad de la máquina. Remotion haría lo mismo
pero no es de código abierto (gratis solo para organizaciones sin ánimo de lucro o de hasta 3 personas); Theatre.js
y Motion Canvas no se usan como base. Ver [referencias-web.md](referencias-web.md) §2.

## Ficheros (`assets/motor-video/`)

| Fichero | Qué hace |
|---|---|
| `motor.js` | `SV.run(cfg)` construye la escena 1920×1080 y expone `window.seek(t)`, `window.DURATION`, `window.__ready`; temas, composiciones y tiempos |
| `comun.css` | Estilos del escenario con variables del tema. Sin transiciones ni animaciones CSS: todo lo pinta `seek` |
| `render.js` | Playwright abre cada `flujo-*.html`, llama a `seek(f/30)`, fotografía `#stage` por CDP (PNG sin pérdida; nunca `optimizeForSpeed`, que cambia píxeles) y ffmpeg arma el MP4 y la hoja. **No se copia al proyecto:** lo instala `scripts/motor.mjs` |
| `package.json` | Única dependencia: `playwright-core` 1.63.0. Tampoco se copia |
| `flujo-1-ingesta.html` | Ejemplo lineal con datos ficticios: 6 etapas, rama a «sala de espera», ficha que cambia de forma, contador |
| `flujo-2-cierre.html` | Ejemplo lineal con puente a otro sistema: botón, destello de fotos, sello con onda, estados que cambian |
| `flujo-3-ciclo.html` | Ejemplo de **ciclo** con panel en columna y **tema derivado** de tres colores (no institucional) |
| `flujo-4-documento.html` | Ejemplo **sin estaciones** (gramática §5.bis): un documento protagonista que se escribe solo, se firma, entra en una bandeja y vuelve sellado. Tema claro derivado, `cfg.limpio` y los ayudantes `SV.poses/escribir/trazo/sello/golpe`. Su hoja: `assets/referencia/hoja-flujo-4-documento.jpg`; la versión real y larga, la guía de traslado: `hoja-guia-traslado-documento.jpg` |

Los dos primeros son copias exactas de los videos que se proyectaron (tema `americana`, idénticos píxel a píxel).
Bórralos de la copia del proyecto cuando ya no sirvan de modelo.

## API del motor

- **Tema.** `const C = SV.tema(T)` al principio del flujo (antes de construir las maquetas) y `tema: T` en `SV.run`.
  `T` = `'americana'` | `'neutral'` | `{ fondo, tinta, acento }` (deriva el resto) | objeto con claves de `C`.
  En JS: `C.gold`, `SV.rgba(C.mute, .3)`, `SV.mix(a, b, p)`. En CSS: `var(--gold)`, `rgba(var(--mute-rgb),.3)`.
- **Composición.** `SV.composicion(tipo, n, opciones)` → `{ d, puntos: [{ x, y, fr, labelPos }] }`. Tipos `lineal`
  (`y, x0, x1, desde, hasta`), `zigzag` (`ya, yb, x0, x1`), `ciclo` (`cx, cy, r`), `arco` (`cx, cy, r, ry`),
  `escalera` (`x0, x1, y0, y1`). Trazo propio: escribe `d` y usa `SV.fraccion(d, x, y)` para cada estación.
- **Tiempos.** `SV.tiempos(n, { inicio, paso, cierre })` → `{ T, resultado, duracion }`.
- **Ficha.** `ficha: { kinds, trazo: comp.d, segs: SV.rutaFr(T, fracciones) }`: con `trazo`, los tramos van en
  fracciones del camino y la ficha lo recorre exacto. Sin `trazo`, `segs` en píxeles (`{t0,t1,x0,y0,x1,y1,cx?,cy?}`)
  o `SV.route(inicio, paradas)`. Formas: `doc`, `row`, `rowHollow`, `plate`; `weights(t)` mezcla formas.
- **Vías.** `tracks: [{ d: comp.d }]` (se dibuja y se ilumina hasta donde va la ficha) o rectas
  `{ x0, x1, y, dashed, inAt }`.
- **Estaciones.** `nodes: [{ x, y, num, name, sub, labelPos, arr, next, dashed, ghost, noCheck, appear }]`.
- **Panel.** `panel: { x, y, w, h, forma: 'columna'? }`, `pointer: [{ t, x }]` (o `{ t, y }` en columna) y
  `panels: [{ t0, t1, eyebrow, phrase, chips: [{ t, k: 'state', at, swap }], html, tick(lt, el, api), init }]`;
  el último con `full: true` es el resultado. Todo es opcional: sin `panel`, sin `ficha` o sin `title`, no se pintan.
- **Atributos declarativos** en el `html` de un panel: `data-in`, `data-pop`, `data-draw="a,dur"`,
  `data-fade="a,dur,de,a"`, `data-slide="a,dur,dx,dy"`, `data-out` (segundos desde el inicio del panel).
- **Piezas propias**: `extra(api)` recibe `{ C, S, D, L (capas SVG), html, ups, F (ficha), makeFicha, makeNode,
  pathAt, route, rutaFr, auto, … }`; añade funciones `t => …` a `api.ups` para animarlas.
- **Composición limpia (sin estaciones).** `limpio: true` en `SV.run`: paneles a pantalla completa, sin caja, desde
  t = 0 (no hace falta `panel` ni `panelIn`). Sin `nodes`, `ficha`, `tracks` ni `pointer`, no hay camino. El
  protagonista se construye en `extra(api)` y se cuelga de **`api.root`** (encima de los paneles; `api.html` queda
  debajo y una ventana opaca de un panel lo taparía).
- **Ayudantes del documento protagonista** (ejemplo completo en `flujo-4-documento.html`):
  - `SV.poses([[t, x, y, escala, opacidad], …])` → `f(t)`: el objeto que vive todo el video, por poses clave.
  - `SV.escribir([{ el, texto, pausa? }], t0)` → `{ fin, up(t) }`: campos que se teclean solos, uno tras otro, a
    0,011 s por carácter + 0,12 s por campo. `fin` encadena lo siguiente (la X de una casilla, las filas).
  - `SV.trazo(path)` → `up(t, a, dur)`: firma o subrayado que se dibuja, invisible hasta su instante.
  - `SV.sello({ arriba, abajo, id })` (SVG con texto en arco por `textPath`) y `SV.golpe(g, t, a)` (cae y se asienta).
- La cabecera entra centrada y se retira a la esquina; al final todo se funde a fondo (`duration − 1 s`).
- **Sin reloj**: nada de `requestAnimationFrame`, `setTimeout`, `Date.now()` ni transiciones CSS. Si algo depende
  del tiempo real, dos renders salen distintos y los fotogramas saltan.

## Hacer un flujo nuevo

**Prepara una vez, renderiza en sitio, revisa en una pasada, corrige en una tanda.** El tiempo se iba en instalar el
motor en cada proyecto, en decenas de comprobaciones sueltas y en renders repetidos por correcciones que llegaban de
una en una. La calidad no cambia: el MP4 sale idéntico byte a byte y las puertas son las mismas.

`M` = `<carpeta de la skill>/scripts`, donde `<carpeta de la skill>` es la «Base directory» que Claude muestra al cargarla.

1. **Prepara el motor, una vez por máquina:** `node M/motor.mjs estado` (3 s; JSON con `listo` y lo que `falta`). Si
   no está listo, `node M/motor.mjs preparar`: instala `render.js` y `playwright-core` en
   `~/.presentacion-viva/motor-video/<huella>/` (unos 15 s) y anota el entorno en `entorno.json`. No hay
   `npm install` por presentación; la huella cambia sola si cambia `render.js` o `package.json`.
2. La carpeta de los flujos solo lleva lo suyo: `motor.js`, `comun.css` y los `flujo-*.html`
   (`nueva-presentacion.mjs --video` la crea en `video/src/`). Sus copias de `motor.js` y `comun.css` fijan la
   versión con la que se hizo el video. Borra de ahí los tres flujos de ejemplo en cuanto no sirvan de modelo: un
   render sin id los renderiza también.
3. Escribe el guion en JSON y genera el esqueleto: `node M/nuevo-flujo.mjs guion.json presentacion/video/src`.
4. Dibuja cada `MAQUETA ·` y su microacción ([gramatica-del-flujo.md](gramatica-del-flujo.md) §6-7).
5. **Fotogramas sueltos de TODOS los flujos antes de cualquier render completo:**
   `node M/motor.mjs render presentacion/video/src flujo-2-x --stills 2.8,4.4,6,12` deja PNG en `video/_revision/`.
   Usan la misma captura que el video y recorren los `seek` en el mismo orden: son fieles a lo que saldrá.
6. **Revisa en una pasada:** `node M/revisar.mjs <carpeta>` ya corre `verificar.mjs` en modo flujo sobre cada
   `flujo-*.html`, también cuando NO hay página (un video solo: apúntalo a la carpeta de los flujos). No lo
   repitas a mano ni lo complementes con scripts propios (ver «Revisión en una pasada»). Junta TODO lo que
   encuentres (stills, `revisar.mjs`, mosaicos si hay página) en una lista.
7. **Corrige la lista entera en una tanda** y vuelve a mirar solo los stills de lo que tocaste. Un render completo
   por cada corrección suelta es lo que más tiempo tiraba.
8. **Render final, una vez:** `node M/motor.mjs render presentacion/video/src` (todos) o con el id de uno. Sale
   `video/flujo-2-x.mp4` y `video/hoja-flujo-2.png`. Mira la hoja entera.
9. Para la página: copia el MP4 a `presentacion/media/` y ponlo en la sala de flujos; `revisar.mjs` otra vez como
   puerta (comprueba también cada MP4 con ffprobe).

Proyectos antiguos con su propio `render.js` copiado siguen funcionando con `npm install` y `node render.js`; para
pasarlos al motor instalado basta borrar de su carpeta `render.js`, `package.json` y `node_modules`.

## Revisión en una pasada (`scripts/revisar.mjs`)

`node M/revisar.mjs <carpeta-de-la-presentación> [--vetar "a,b"]` hace en una corrida lo que antes eran 13-14
comprobaciones sueltas (y el verificador propio que cada presentación acababa escribiéndose):
- `verificar.mjs` sobre `index.html` y cada `flujo-*.html`;
- la página a 1440 px, a 375 px y con movimiento reducido: errores de consola, desborde horizontal, imágenes rotas,
  letra mínima visible y elementos de escena que con movimiento reducido no quedan en su estado final;
- términos vetados (fuera de URL), `node_modules`, `_tmp` o `_fotogramas` olvidados, y cada MP4 con ffprobe;
- dos mosaicos, `_revision/mosaico-1440.png` y `_revision/mosaico-375.png`: la página entera por pantallas.

Escribe `_revision/revision.json` y sale con 1 si algo FALLA. Usa el Chromium y el `playwright-core` del motor
instalado. **Mirar los dos mosaicos enteros sigue siendo obligatorio:** la máquina mide; el juicio visual es de
quien revisa. `_revision/` es carpeta de trabajo: no se publica, y **se borra al entregar** (tras la última corrida y
tras mirar los mosaicos): `revision.json` guarda rutas absolutas y los términos hallados.

**Sustituye, no se suma:** en la medición del 28-oct (eval-1 integrada) el ejecutor corrió `revisar.mjs` tres veces
y además hizo su propia revisión (capturas de escenas, mosaicos con ffmpeg), así que la revisión no bajó de los
~9 min. Con una carpeta de **solo video** (sin `index.html`) hace la parte estática: `verificar.mjs` por flujo,
vetados, restos y ffprobe de cada MP4; la parte visual la dan los stills y la hoja de contactos.

## Requisitos

- **Node 18+** (`npm` solo para `motor.mjs preparar`, una vez).
- **Chromium headless shell de Playwright:** `npx playwright@1.63.0 install chromium-headless-shell`. `motor.mjs`
  busca el más reciente en `%LOCALAPPDATA%\ms-playwright` (o `~/.cache/ms-playwright`); se puede forzar con
  `CHROME_EXE`. Si `estado` lo da en `falta`, falta este paso.
- **ffmpeg** (y ffprobe) en el PATH (en Windows: winget `Gyan.FFmpeg`). `motor.mjs estado` lo comprueba.
- Tiempo: unos 0,3 s por fotograma; 14 s de video = 405-420 fotogramas ≈ 2 min. Lánzalo en segundo plano.

## Errores conocidos

- Un error de consola en la página aborta el render a propósito: mejor parar que grabar 400 fotogramas rotos.
- `waitForFunction(__ready)` con timeout: si el HTML no llama a `SV.run`, o falla antes, salta a los 20 s.
- Texto que se sale del panel: el motor no recorta; revisa los `--stills` con frases largas (≤52 caracteres).
- Las maquetas se construyen ANTES de `SV.run`: sin `SV.tema(...)` al principio salen con los colores neutros.
- Tildes rotas: el HTML del flujo necesita `<meta charset="utf-8">` como cualquier página.
- En Windows, un script de Python que lea estos ficheros necesita `encoding='utf-8'` (o `PYTHONUTF8=1`).
- **Resuelto 2026-10-30 · «Imagen que no carga» a mitad de un render largo:** el tope de 10 s de la espera de imágenes
  se disparaba aunque ya hubieran cargado, escribía un error en consola y el render fallaba AL TERMINAR (tras grabar
  todos los fotogramas). Con `--stills` no se veía porque dura menos de 10 s. Si un proyecto trae un `motor.js`
  anterior a esa fecha, cópiale el de la skill.
- **Resuelto 2026-10-30 · Tema derivado claro con viñeta gris:** `{ fondo, tinta, acento }` con fondo blanco
  oscurecía los bordes hacia negro. Ahora un fondo claro deriva sombra suave hacia la tinta y oscurece el acento
  cuando va como texto. Con un `motor.js` viejo y fondo claro, fija `shade` a mano.
