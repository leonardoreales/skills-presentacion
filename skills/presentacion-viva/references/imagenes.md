# Imágenes del usuario: adaptarlas a la presentación

Cuando quien pide la presentación trae fotos, ilustraciones, logos o capturas, no se pegan tal cual: se adaptan al
formato, al color del tema y al ritmo de las escenas, y se animan con el mismo oficio que el resto. Este fichero dice
cómo, **en cualquier equipo**: la skill no puede suponer que quien la usa tiene Python, OpenCV o ffmpeg.

**Índice:** 1. La escalera de capacidades · 2. Recibir las imágenes · 3. Tratamientos · 4. Animar imágenes ·
5. Inteligencia artificial · 6. Puerta · 7. Bolsillo

## 1. La escalera de capacidades

Cada operación declara qué necesita. **Se usa el escalón más bajo que resuelva el caso**, y la página final
**nunca** depende de un escalón superior al 0: lo que hacen los scripts es optimizar de antemano, no hacer posible.

| Nivel | Necesita | Qué da | Dónde |
|---|---|---|---|
| **0** | un navegador (PC, tableta, móvil, nube) | recorte por punto focal, duotono, grises, velo para texto, AVIF/WebP/JPEG según lo que codifique ESE navegador, fragmento `<picture>` y manifiesto | `assets/taller-imagen/index.html` (abrir con doble clic o publicarlo como Artifact) · CSS y GSAP en la página (§3, §4) |
| **1** | Python + Pillow | lo mismo por lotes y con AVIF garantizado; corrige el giro EXIF | `scripts/preparar-imagen.py formato · duotono` |
| **2** | + OpenCV · ffmpeg | trazo animable (contornos a SVG), quitar fondo sin IA (GrabCut), Ken Burns en MP4 | `preparar-imagen.py trazo · fondo · kenburns` |
| **3** | IA (local o en la nube) | quitar fondo fino, ampliar, generar ilustración | §5, y solo tras el freno de privacidad |

Primero: `python scripts/preparar-imagen.py diagnostico`. Dice qué escalón hay en esta máquina y el remedio de
cada hueco. Sin Python, el diagnóstico es otro: **abrir el taller (nivel 0) y seguir**. Un script que no encuentra
su herramienta sale con código 3 y lo dice; nunca finge el resultado (medido: con Python sin paquetes, `formato` sale
con 3 y remite al taller).

## 2. Recibir las imágenes

Antes de tocar una, haz el inventario en `notas.md`, una línea por imagen:

- **Qué es:** foto, ilustración, logo, captura de pantalla o diagrama. Cada tipo pide otro trato (§3).
- **Qué hace en la historia:** evidencia (prueba que algo existe), ambiente (sitúa) o decoración. Si no hace nada,
  sobra: una foto sin función compite con el mensaje.
- **Procedencia y licencia:** propia del área, banco con licencia (fila del bolsillo `librerias-ilustracion`),
  generada por IA (se declara). Sin procedencia no se usa.
- **Personas reconocibles:** necesitan autorización escrita (Ley 1581 de 2012). Sin ella: otra foto, recorte sin
  rostros, o la escena convertida en ilustración.
- **Capturas con datos:** nombres, cédulas o correos se recrean como maqueta con datos ficticios, igual que en los
  flujos de video. Desenfocar no basta: se lee.
- **Metadatos:** una foto del móvil lleva EXIF con GPS, que es dato de ubicación (PTI-019). Reexportar la limpia: el
  script y el taller nunca copian el original ni sus metadatos. Nunca publiques el fichero original.
- **Resolución:** para proyector, 1920 px de ancho. Una más pequeña se usa a su tamaño o en un hueco menor; no se
  amplía (los scripts y el taller se niegan a ampliar y lo avisan).

**Un solo tratamiento para todo el deck.** Fotos de orígenes distintos se ven como un collage si cada una conserva
su color. Elige uno en la fase 3 (duotono con el tema, grises con acento o color natural con velo) y aplícalo a
todas. Es parte de la identidad, como la tipografía.

## 3. Tratamientos

| Problema | Tratamiento | Nivel 0 (en la página) | Nivel 1-2 (antes) |
|---|---|---|---|
| Pesa mucho, no se ve nítida | variantes 640/1280/1920 en AVIF o WebP + JPEG, `srcset`, `width`/`height` | taller | `formato` |
| Encuadre equivocado para 16:9 | recorte por punto focal | `object-fit:cover; object-position:50% 40%` · taller | `formato --aspecto 16:9 --foco 0.5,0.4` |
| Colores que no casan con el tema | duotono `--bg` → `--accent` | CSS de abajo · taller | `duotono --tema-de index.html` |
| Texto encima ilegible | velo degradado desde `--bg` (contraste 4.5:1 medido sobre la zona del texto) | `linear-gradient` sobre la foto · taller | — |
| Quiero dibujarla al hacer scroll | contornos a trazos SVG | dibujar a mano el SVG | `trazo --detalle 0.5` |
| La figura sobre el fondo del tema | quitar el fondo | — | `fondo` (GrabCut) · `fondo --ia` |
| Una foto fija en la sala de flujos | Ken Burns lento | GSAP (§4) | `kenburns --segundos 6` |

Los colores salen siempre de los roles del tema (`--bg`, `--ink`, `--accent`): el script los lee de la página con
`--tema-de`, el taller acepta pegar el `:root`, y el SVG de trazo usa `currentColor`. Nunca un `#hex` suelto en un
componente.

**Duotono solo con CSS** (nivel 0, sin procesar la foto; cambia solo si cambia el tema):

```css
.duo { position: relative; background: var(--accent); isolation: isolate; overflow: hidden; }
.duo img { display: block; width: 100%; height: auto; filter: grayscale(1) contrast(1.1); mix-blend-mode: multiply; }
.duo::after { content: ""; position: absolute; inset: 0; background: var(--bg); mix-blend-mode: lighten; }
```

El gris multiplicado sobre el acento lleva el blanco al acento; el `lighten` con el fondo sube el negro al fondo.

## 4. Animar imágenes

Las fotos se animan con la misma API que las escenas: `PV.escena(id, construir, false)`. Con `false` no se crea
lienzo SVG; `construir(null, host)` anima el `<picture>` que ya está en el host. Así hereda gratis lo que el
andamiaje garantiza: estado final sin JS ni con movimiento reducido, y pausa fuera de pantalla.

```html
<figure class="escena kb" id="foto-bodega"><picture>…</picture></figure>
```

**Revelado** (la foto entra al llegar; trampa 5.bis de [patrones-gsap.md](patrones-gsap.md): el `set` al inicio
evita que aparezca terminada al repetir):

```js
PV.escena('foto-bodega', function(_, host){
  var img = host.querySelector('img');
  return PV.G.timeline({paused:true})
    .set(img, {clipPath:'inset(0 100% 0 0)'}, 0)
    .to(img, {clipPath:'inset(0 0% 0 0)', duration:1.2, ease:'power2.out'});
}, false);
```

**Ken Burns** (contenedor con `overflow:hidden`; 12-16 s, escala ≤ 1.12: más rápido marea):

```js
PV.escena('foto-sala', function(_, host){
  return PV.G.timeline({paused:true, repeat:-1, yoyo:true})
    .fromTo(host.querySelector('img'), {scale:1, xPercent:0}, {scale:1.1, xPercent:-3, duration:14, ease:'none',
      immediateRender:false});
}, false);
```

**Trazo que se dibuja** (SVG de `preparar-imagen.py trazo`, o uno dibujado a mano con `pathLength="1"`). Funciona
con GSAP 3.12.5, que en cdnjs no trae DrawSVG:

```css
.trazo path { stroke-dasharray: 1; stroke-dashoffset: 0; }   /* reposo = dibujado */
```
```js
.fromTo(svg.querySelectorAll('.trazo path'), {strokeDashoffset:1}, {strokeDashoffset:0, duration:1.6,
  stagger:{amount:1.2}, ease:'none', immediateRender:false})
```

Si pasas el SVG por SVGO (PIM-007) para aligerarlo, desactiva `cleanupIds` o protege los `id` con `preservePrefixes`:
su preset por defecto los acorta y rompe los selectores de GSAP. Potrace (PIM-005) es GPL: usarlo como herramienta
sirve, incluirlo dentro de un producto no.

Detrás, la foto en duotono puede subir de `opacity:0` a 1 al final del trazo: primero el dibujo, luego la realidad.

**Antes y después** (dos fotos apiladas; la de encima se recorta con `clip-path: inset(0 calc(100% - var(--x)) 0 0)`
y un `<input type="range">` mueve `--x`). Es el único control que se ofrece: un rango nativo ya funciona con teclado
y lector de pantalla. Con movimiento reducido sigue funcionando, porque es el usuario quien lo mueve.

**Fotos dentro de un video de flujo:** la maqueta de una etapa puede llevar una foto como `<image href="media/…">`
dentro del SVG (en duotono, para que case con el tema). El motor espera a que cada `<img>` e `<image>` cargue antes
de `__ready`, con un tope de 10 s y aviso en consola si una no carga (medido el 2026-10-26: `<img>`, `<image>` y
foto rota). El Ken Burns dentro del flujo se hace en el `seek(t)` (escala en función de `t`), no con el MP4 de
`kenburns`, que es para clips sueltos de la sala.

Disciplina: una foto en movimiento por pantalla; nada de parallax en varias capas (WCAG 2.3.3, mareo); todo bucle
se pausa fuera de pantalla (2.2.2), que el andamiaje ya hace.

## 5. Inteligencia artificial

La IA entra en el **nivel 3** y solo cuando los niveles 0-2 no resuelven: quitar el fondo de una foto difícil
(pelo, transparencias), ampliar una imagen pequeña o generar una ilustración que no existe.

**Freno de privacidad, antes de usarla** (aplica la doctrina del freno, `~/.claude/freno/`): ¿la imagen sale del equipo?
- **IA local** (p. ej. `rembg`, PIM-010): la imagen no sale. Mira la licencia **del modelo**, no solo la del
  código. **Trampa medida:** el modelo por defecto de `rembg` es `bria-rmbg` (RMBG-2.0, CC BY-NC 4.0, no comercial,
  PIM-011: Evitar). `preparar-imagen.py fondo --ia` fija `birefnet-general` (MIT, PIM-012) y su arnés se pone rojo
  si alguien lo quita. La primera vez descarga el modelo, cientos de MB: avísalo antes. Ampliar con Real-ESRGAN
  (PIM-013) sí, pero **nunca** con `--face_enhance` en fotos de personas: inventa rasgos. En el navegador,
  `@imgly/background-removal` (PIM-014) es AGPL-3.0: Condicional.
- **IA en la nube** (servicios de quitar fondo o generar imagen, incluidos los conectores de la cuenta): la imagen
  viaja a un tercero. **Nunca** con personas, datos personales, documentos internos ni nada reservado. Para una
  ilustración genérica sin datos, sí, diciéndolo.

Toda imagen generada por IA **se declara** en `notas.md` y en el manifiesto (`procedencia: generada con …`), y si
trae Content Credentials (C2PA) se conservan (PTI-021, `c2patool` PIM-016). No se
generan personas reales, logos de terceros ni nada que pueda pasar por una foto documental: una presentación
institucional no puede mostrar como evidencia algo que no ocurrió. Para que case con el deck, el prompt nombra el
tratamiento elegido en la fase 3 y los roles del tema por su color.

## 6. Puerta

Ninguna imagen entra en la página publicada si su manifiesto (`media/manifiesto.json`, lo escriben el script y el
taller) tiene un `PENDIENTE`:

1. **Texto alternativo** que dice qué muestra y por qué importa en esa escena; `alt=""` solo si es decorativa
   (WCAG 1.1.1). `verificar.mjs` da **FALLA** si encuentra `alt` o `aria-label` con `PENDIENTE`.
2. **Procedencia y licencia** escritas.
3. **Personas:** «no», o «sí, con autorización».
4. `width` y `height` en cada `<img>` (sin ellos la página salta al cargar; `verificar.mjs` lo avisa).
5. Peso: ninguna variante de 1920 px por encima de ~400 KB en AVIF/WebP; si pasa, bajar calidad o recortar.

## 7. Bolsillo

Consultas al Mochilero (`--dominio presentacion`):

| Pregunta | Consulta |
|---|---|
| ¿Qué librería o herramienta trata esta imagen, y con qué licencia? | `"quitar fondo foto" --tabla librerias-imagen` |
| ¿Cómo la adapto o la animo sin romper accesibilidad? | `"duotono foto tema" --tabla tratamiento-imagen` |
| ¿De dónde saco una foto o ilustración con licencia? | `"foto banco licencia" --tabla librerias-ilustracion` |
