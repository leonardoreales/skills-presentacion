# Mecanismos: piezas de construcción

Piezas combinables, no escenas hechas. Una escena buena casi siempre junta dos o tres (un objeto que **viaja**, deja
un **trazo**, y al llegar cae un **sello**). Este fichero es el «cómo se construye»: código mínimo y trampas. Para
la amplitud de opciones (tipos de diagrama, técnicas, combinaciones probadas, novedades) ver
el bolsillo, el Mochilero ([bolsillo-mochilero.md](bolsillo-mochilero.md)); para elegir qué mecanismo lleva cada escena, el protocolo creativo de
[protocolo-creativo.md](protocolo-creativo.md).

Los fragmentos asumen el andamiaje (`PV.el`, `PV.txt`, `PV.ico`, `PV.G` = gsap) y las reglas de
[patrones-gsap.md](patrones-gsap.md): todo se dibuja en su estado final y los «desde» van con
`fromTo(…, {immediateRender:false})`. «Plugin 3.15» = requiere GSAP 3.15 de jsdelivr (gratis), ver ese fichero §6:
en cdnjs 3.12.5 no existe. Las opciones de cada pieza, con su fuente y su veredicto, se consultan en el Mochilero
([bolsillo-mochilero.md](bolsillo-mochilero.md)); aquí queda el cómo con nuestro andamiaje.

**Índice:** 1 Trazo que se dibuja · 2 Objeto que viaja por una ruta · 3 Un documento se transforma en otro ·
4 Reordenamiento · 5 Texto que se arma · 6 Acumulación o llenado · 7 Contador · 8 Sello o estampado ·
9 Línea de tiempo que avanza · 10 Mapa que se ilumina · 11 Antes y después con cortina · 12 Red que se conecta ·
13 Medidor o aguja · 14 Capas que se separan · 15 Cámara que hace zoom · 16 Pantalla real con foco guiado ·
17 Video determinista · 18 Documento que se diligencia campo por campo · 19 Lista que el lector marca

---

## 1. Trazo que se dibuja
**Comunica:** un recorrido, una firma, una conexión que nace. **Cuándo:** rutas, firmas, contornos, gráficas de línea.
**Librería:** GSAP core con `pathLength` (sin plugin); DrawSVG (plugin 3.15) si hace falta dibujar tramos parciales.
```js
var p=PV.el('path',{d:'M40 300 C200 80 440 80 600 300',fill:'none',stroke:PV.token('accent'),'stroke-width':3,
  pathLength:1,'stroke-dasharray':1,'stroke-dashoffset':0},svg);
tl.fromTo(p,{attr:{'stroke-dashoffset':1}},{attr:{'stroke-dashoffset':0},duration:1.4,ease:'power2.inOut',immediateRender:false});
```
**Trampas:** `pathLength:1` normaliza; sin él hay que medir `getTotalLength()`. Con `stroke-linecap:round` queda un
punto visible en offset 1: ocúltalo con opacidad al inicio.

## 2. Objeto que viaja por una ruta
**Comunica:** algo pasa por estaciones y cambia en cada una. **Cuándo:** un trámite, un producto, una carta, un
estudiante a lo largo de su carrera, una gota en el ciclo del agua. **Librería:** MotionPathPlugin (3.12.5 ya lo trae).
```js
var mp=function(a,b){return{path:route,align:route,alignOrigin:[.5,.5],start:a,end:b}};
tl.to(tk,{motionPath:mp(0,.36),duration:1.6,ease:'power1.inOut'})
  .to(estacion[0],{fill:'rgba('+PV.token('accent-rgb')+',.35)',duration:.3})
  .to(historial[1],{opacity:1,duration:.3},'<');
```
**Trampas:** dibuja la ficha ya en `route.getPointAtLength(route.getTotalLength())` (estado final). Tramos con
`start/end` en vez de un único viaje: permiten pausas en cada estación. Ver trampa 2 de patrones-gsap si la ficha
tiene `transform` propio.

## 3. Un documento se transforma en otro
**Comunica:** conversión (solicitud → acta, borrador → ley, semilla → árbol). **Librería:** MorphSVG (plugin 3.15).
```js
tl.to('#forma-a',{morphSVG:'#forma-b',duration:1.2,ease:'power2.inOut'});
```
**Trampas:** formas con número de puntos muy distinto se retuercen; simplifica ambas o usa `shapeIndex`. Sin el
plugin: fundido cruzado + escala, que se lee igual de bien a distancia.

## 4. Reordenamiento
**Comunica:** lo que estaba desordenado se organiza; un ranking cambia. **Librería:** Flip (plugin 3.15), sobre HTML.
```js
var st=Flip.getState('.ficha'); contenedor.classList.add('ordenado'); Flip.from(st,{duration:.8,ease:'power2.inOut',stagger:.04});
```
**Trampas:** Flip mide el DOM: funciona sobre elementos HTML, no dentro de un SVG. En bucle, guarda el estado
inicial y alterna la clase.

## 5. Texto que se arma
**Comunica:** una frase clave que se pronuncia. **Cuándo:** solo para UNA frase por presentación (la tesis); en todo
lo demás es ruido. **Librería:** SplitText (plugin 3.15).
```js
var sp=SplitText.create('.tesis',{type:'words'});
tl.fromTo(sp.words,{opacity:0,y:12},{opacity:1,y:0,stagger:.06,duration:.4,immediateRender:false});
```
**Trampas:** lectores de pantalla: SplitText ya pone `aria-label`; compruébalo. Con reduced-motion, la frase entera.

## 6. Acumulación o llenado
**Comunica:** cantidad que crece, capacidad que se ocupa (casillas que se encienden, un vaso que se llena, ladrillos).
```js
tl.to(casillas,{attr:{fill:PV.token('accent')},duration:.2,stagger:.03});
// llenado: un rect con transform-origin abajo
tl.fromTo(nivel,{scaleY:0,transformOrigin:'50% 100%'},{scaleY:1,duration:1.4,immediateRender:false});
```
**Trampas:** en SVG, `transformOrigin` necesita `transform-box:fill-box` o GSAP lo calcula sobre el bbox; verifica.

## 7. Contador
**Comunica:** una cifra que importa. **Cuándo:** una o dos por presentación, cada una con fuente visible.
```js
var o={n:0}; tl.to(o,{n:856,duration:1.4,ease:'power2.out',onUpdate:function(){c.textContent=Math.round(o.n).toLocaleString('es')}});
```
**Trampas:** el texto del HTML ya lleva la cifra final (estado de reposo). Ancho fijo (`font-variant-numeric:tabular-nums`) para que no baile.

## 8. Sello o estampado
**Comunica:** aprobado, cerrado, certificado, vencido. **Pieza:** rect + texto girado en un `<g>`.
```js
tl.fromTo(sello,{opacity:0,scale:2.2,transformOrigin:'50% 50%'},{opacity:1,scale:1,duration:.45,ease:'back.out(1.6)',immediateRender:false});
```
**Trampas:** el giro va en un `<g>` exterior y la escala en otro interior (trampa 2).

## 9. Línea de tiempo que avanza
**Comunica:** historia, calendario, cronograma, plan. **Pieza:** eje + marcas + línea «hoy» que se desplaza; las marcas
pasadas se encienden.
```js
tl.fromTo(hoy,{x:-dist},{x:0,duration:3.4,ease:'none',immediateRender:false});
marcas.forEach(function(m,i){tl.to(m,{attr:{class:'hito hecho'},duration:.01},.1+i*.33)});
```
**Trampas:** en móvil una línea horizontal larga no cabe: rota a vertical o mete el SVG en `overflow-x:auto` con
`min-width`. Fechas siempre verificadas.

## 10. Mapa que se ilumina
**Comunica:** cobertura, sedes, procedencia, expansión. **Pieza:** `<path>` por región (SVG de mapa con licencia libre)
o puntos sobre un contorno; se encienden con stagger.
```js
tl.to(regiones,{attr:{fill:PV.token('accent')},duration:.3,stagger:.12});
```
**Trampas:** mapas pesados (>200 KB) frenan el móvil; simplifica. Revisa la licencia del mapa y que las fronteras sean
las oficiales.

## 11. Antes y después con cortina
**Comunica:** un cambio de estado claro. **Pieza:** sección alta (180vh) con hijo `position:sticky`; la capa «después»
con `clip-path:inset(0 calc(100% - var(--g)*100%) 0 0)` y una línea de acento en el borde; `--g` se calcula al scroll.
```js
var r=sec.getBoundingClientRect(), span=r.height-innerHeight;
sec.style.setProperty('--g',Math.min(1,Math.max(0,(-r.top)/span*1.15-.08)).toFixed(4));
```
**Trampas:** con reduced-motion, apilar las dos capas (sin sticky ni clip). Es scroll del usuario, no scrolljacking.

## 12. Red que se conecta
**Comunica:** integración, comunidad, alianzas, ecosistema. **Pieza:** nodos + líneas que se dibujan (mecanismo 1) +
pulsos que viajan por ellas (`<animateMotion>` o MotionPath).
```html
<circle r="5" class="pulso"><animateMotion dur="3s" repeatCount="indefinite" path="M230 70 L80 320"/></circle>
```
**Trampas:** más de ~8 nodos se vuelve espagueti; agrupa. Oculta los pulsos con reduced-motion.

## 13. Medidor o aguja
**Comunica:** cumplimiento, riesgo, nivel frente a una meta.
```js
var nd=PV.el('g',{transform:'rotate(76)'},pivote), ang={a:76};
function setA(){nd.setAttribute('transform','rotate('+ang.a.toFixed(2)+')')}
tl.fromTo(ang,{a:-90},{a:-90,duration:.01,onUpdate:setA,immediateRender:false})
  .to(ang,{a:76,duration:1.2,ease:'elastic.out(1,.6)',onUpdate:setA});
```
Arco: `pathLength:100` y `stroke-dashoffset` de 100 a (100 − %). **Trampas:** nada de `svgOrigin` (trampa 3); marca
la meta con una raya y la palabra «meta».

## 14. Capas que se separan (explosionado)
**Comunica:** de qué está hecho algo (arquitectura de un sistema, partes de una célula, estructura de un plan).
**Pieza:** capas apiladas en perspectiva isométrica que se separan en Y con `scrub` y se rotulan al abrirse.
```js
PV.G.to(capas,{y:function(i){return -i*70},stagger:0,scrollTrigger:{trigger:host,start:'top 70%',end:'bottom 40%',scrub:true}});
```
**Trampas:** este usa su propio ScrollTrigger con `scrub` (no `PV.escena`); mételo en `gsap.matchMedia` con la
condición de movimiento normal. Rótulos fuera de las capas, a un lado.

## 15. Cámara que hace zoom a un detalle
**Comunica:** «miren esto». **Pieza:** animar el `viewBox` del SVG de vista general a la zona del detalle.
```js
tl.to(svg,{attr:{viewBox:'320 180 200 150'},duration:1.2,ease:'power2.inOut'}).to({}, {duration:1.5})
  .to(svg,{attr:{viewBox:'0 0 640 480'},duration:1});
```
**Trampas:** el estado en reposo es la vista general. El texto escala con el zoom: tamaños pensados para ambos.

## 16. Pantalla real del sistema con foco guiado
**Comunica:** «esto existe y se usa así». **Pieza:** captura real (sin datos personales) dentro de un marco; un
rectángulo de foco con el resto oscurecido (máscara SVG) que salta de zona en zona, con un rótulo por paso.
```html
<mask id="foco"><rect width="100%" height="100%" fill="#fff"/><rect id="hueco" x="40" y="60" width="200" height="80" rx="8" fill="#000"/></mask>
<rect width="100%" height="100%" fill="rgba(0,0,0,.6)" mask="url(#foco)"/>
```
```js
tl.to('#hueco',{attr:{x:300,y:220,width:180,height:60},duration:.8,ease:'power2.inOut'});
```
**Trampas:** revisa la captura píxel a píxel: nombres, cédulas, correos y proyectos reservados se borran o se
reemplazan por datos ficticios ANTES de publicar. Usa la captura en `.jpg` comprimida.

## 17. Video de flujo (la especialidad)
**Comunica:** un proceso contado como un viaje: un objeto recorre las etapas, cada una enseña su evidencia y al final
se ve el resultado. Es el pico de la presentación.
**Herramienta:** el motor `seek(t)` de `assets/motor-video/` y `scripts/nuevo-flujo.mjs`. El oficio está en
[gramatica-del-flujo.md](gramatica-del-flujo.md) y la técnica en [videos-deterministas.md](videos-deterministas.md).
En la página va en la **sala de flujos** del andamiaje (pestañas con flechas, bucle en silencio que suena solo en
pantalla, controles con movimiento reducido).

## 18. Documento que se diligencia campo por campo (página)
**Comunica:** «así se llena este formato», a quien lo va a llenar. **Pieza:** el formato dibujado en HTML (no una
imagen), cada campo es un `<button aria-pressed>` con su ejemplo ficticio, y un panel al lado (`aria-live="polite"`)
con qué escribir, una línea de «ojo» y botones Anterior/Siguiente. Nació en la guía de traslado (2026-10-30).
```html
<button class="campo" type="button" data-titulo="Destino" data-texto="A dónde va el activo." data-ojo="">
  <span class="n">5</span><span class="l">Destino</span><span class="v">Centro de convenciones</span>
  <span class="ayuda">A dónde va el activo.</span></button>
```
```css
.ayuda{display:none} html:not(.js) .ayuda{display:block} html:not(.js) .guia{display:none}
@media (max-width:980px){.guia{display:none}.campo[aria-pressed="true"] .ayuda{display:block}}
```
**Trampas:** en móvil el panel queda DEBAJO de todo el formato, lejos del campo tocado: ahí la ayuda se abre bajo el
campo elegido. Sin JS cada campo muestra su ayuda (se lee entero). Rotula el formato «EJEMPLO · DATOS FICTICIOS» en
el propio papel. En el PDF (`exportar.mjs --css-impresa`) oculta el panel y muestra todas las ayudas.

## 19. Lista que el lector marca
**Comunica:** «revisa antes de enviar»; convierte una lista de requisitos en un gesto. **Pieza:** `<label>` con
`<input type="checkbox">` real (oculto a la vista, no al lector de pantalla) y una casilla dibujada; un estado
`aria-live` que cuenta («3 de 5») y al completarse dice el resultado («Lista para enviar»).
**Trampas:** el foco visible va en la casilla dibujada (`input:focus-visible + span`). Sin JS la lista se lee y se
marca igual; solo falta el contador. No guardes el estado: es un repaso, no un formulario.
