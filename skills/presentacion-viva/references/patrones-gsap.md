# Fundamentos GSAP y trampas ya pagadas

La base técnica sobre la que se montan los mecanismos ([mecanismos.md](mecanismos.md)). Todo asume el andamiaje
`assets/andamiaje/index.html` y su API `PV` (`el`, `txt`, `ico`, `stage`, `token`, `escena`, `listo`).

**Índice:** 1. Pila y versiones · 2. Anatomía de una escena · 3. Trampas ya pagadas · 4. Movimiento reducido ·
5. Reglas de ScrollTrigger · 6. Mejora opcional (GSAP 3.15)

## 1. Pila y versiones

```html
<meta charset="utf-8">  <!-- primero: sin esto las tildes salen rotas en un servidor local -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/MotionPathPlugin.min.js"></script>
<script src="https://unpkg.com/lucide@0.460.0/dist/umd/lucide.min.js"></script>
```

Versión exacta siempre: una URL sin versión puede cambiar la API el día de la presentación, y los Artifacts de
claude.ai exigen versiones exactas de dominios permitidos (cdnjs, jsdelivr/npm, unpkg). Íconos Lucide dentro de SVG:
`lucide.createElement(lucide.icons.NombreEnPascalCase)`; `PV.ico` avisa en consola si el nombre no existe.

## 2. Anatomía de una escena

```js
PV.escena('escena-x', function(svg, host){
  // 1) Dibujar TODO en su estado FINAL: es lo que se ve sin JS, con reduced-motion o si el CDN falla.
  // 2) Sin GSAP, devolver null y la escena queda quieta y completa.
  if(!PV.G) return null;
  // 3) Timeline en pausa y en bucle; los «desde» con fromTo(..., {immediateRender:false}).
  return PV.G.timeline({paused:true, repeat:-1, repeatDelay:.6}) /* … */;
}, '0 0 640 480');
// … más escenas, EN ORDEN DE PÁGINA …
PV.listo();
```

`PV.escena` crea un ScrollTrigger con `onToggle` que reproduce la escena mientras se ve y la pausa fuera. Así una
página con seis escenas en bucle no consume CPU: solo corre la visible.

## 3. Trampas ya pagadas

1. **Estado en reposo = estado final.** Se dibuja todo terminado y los timelines usan
   `fromTo(..., {immediateRender:false})`. Con `from()` o `immediateRender:true`, GSAP aplica el «desde» al crear el
   timeline y la escena queda vacía si nunca se activa, si el CDN falla o con reduced-motion.
2. **GSAP `x/y` pisa un `transform` propio del SVG.** Un `<g transform="translate(..) rotate(..)">` animado con
   `x/y` pierde su rotación y posición. Se envuelve en `<g class="mv">` y se anima el envoltorio.
3. **Agujas con proxy, no con `svgOrigin`.** `svgOrigin` en un grupo ya trasladado dio pivotes erróneos. Proxy `{a}`
   + `onUpdate` que escribe `rotate(a)` dentro de un grupo colocado en el pivote ([mecanismos.md](mecanismos.md) §13).
4. **`<meta charset="utf-8">` primero.** Sin él, `python -m http.server` sirve con otra codificación y las tildes salen
   como «GestiÃ³n».
5. **Nada encima del contenido.** Un marco con esquinas fijo sobre la página pisaba el contenido; se usa una franja
   superior opaca con marca y capítulo, y el progreso como línea de 2 px bajo ella.
6. **Pie de figura debajo, no superpuesto.** Un `figcaption` absoluto tapaba la escena en móvil: es un bloque debajo.
7. **Etiquetas lejos del borde.** Un `<text>` a menos de ~20 px del borde del `viewBox` se corta, sobre todo con
   `text-anchor="end"` o a 375 px. Deja margen.
8. **ScrollTrigger `onToggle`** para reproducir/pausar escenas en bucle; `scrub` solo para lo que debe seguir al dedo
   (cortina, explosionado).
9. **Versiones fijas** en todos los CDN.
10. **Rejillas con `minmax(0,1fr)`**: con `1fr` a secas, un SVG ancho desborda en móvil.
11. **Texto siempre visible.** Los revelados por scroll animan trazos y formas; si el texto depende de una animación
    para aparecer, un fallo de JS deja la página muda.

## 4. Movimiento reducido

El andamiaje usa el patrón oficial de GSAP, `gsap.matchMedia()` con una condición de `prefers-reduced-motion`: con
`reduce`, cada timeline salta a su final (`tl.progress(1).pause()`) y se queda quieto; el CSS apaga animaciones y
transiciones. matchMedia además revierte y reconstruye si la preferencia cambia en vivo. Lo que use `scrub` o `pin`
también debe ir dentro de un `mm.add(...)` para que con `reduce` se muestre estático.

## 5. Reglas de ScrollTrigger

- **Scrollytelling, no scrolljacking:** el scroll siempre es del usuario. Nada de bloquear la rueda ni convertirla en
  saltos. El modo presentador (Av Pág / Re Pág) es opcional y usa `scrollTo` normal.
- No se anima el elemento que lleva `pin`: se anima un hijo.
- Un solo ScrollTrigger por timeline.
- Se crean en el orden en que aparecen en la página; `PV.listo()` llama a `ScrollTrigger.sort()` y `refresh()` por si
  acaso.

## 5.bis Trampas pagadas en la iteración 1 de la skill

- **Al repetir un timeline, lo que entra tarde aparece ya terminado.** `immediateRender:false` deja el estado final
  en reposo, pero cuando `onToggle` vuelve a reproducir la escena, los `fromTo` que empiezan más tarde muestran su
  final hasta que les toca. Remedio: al principio del timeline, `tl.set(<esos elementos>, {<estado inicial>}, 0)`.
- **Texto dentro del SVG ilegible en móvil.** Un `viewBox` de 640 a 375 px escala el texto un 59 %: un `font-size`
  de 14 queda en 8 px reales. Rótulos de escena a 20 o más en el `viewBox`, o menos texto dentro del dibujo y más en
  el pie. Mide en la captura de 375 px.

## 6. Mejora opcional: GSAP 3.15

El andamiaje se queda en 3.12.5 porque es la probada. **Pero en cdnjs, 3.12.5 no trae DrawSVG, MorphSVG ni
SplitText** (sí trae ScrollTrigger, MotionPath, Flip, Observer, Text y CustomEase): medido en la API de cdnjs el
2026-10-26, Mochilero PTC-035. Un mecanismo que los necesite obliga a subir. Mejora opcional: la 3.15.0 en jsdelivr
(`https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js`, `.../dist/ScrollTrigger.min.js`, etc.). Desde que GSAP
es gratuito, todos los plugins lo son, incluidos **DrawSVG, MorphSVG, SplitText y Flip** — varios mecanismos los
usan. Si se cambia, se cambian TODAS las URLs de GSAP a la vez y se repite la verificación completa. Fuentes en
[referencias-web.md](referencias-web.md) §1.
