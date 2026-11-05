# Referencias web verificadas — presentacion-viva

> **Respaldo (2026-10-26).** El contenido vive ahora en el Mochilero, dominio `presentacion`, con datos más nuevos
> (por ejemplo, Remotion 5.0 aún no ha salido y cdnjs ya publica todos los plugins de GSAP 3.15.0). Este fichero
> solo se usa si el Mochilero no está; ante cualquier diferencia, manda el Mochilero. Su hermano
> `catalogo-visual.md` se retiró tras la puerta de no-regresión (iteración 3: misma nota con él y sin él).

Consulta: **2026-10-23** (todas las URL). Lo que no se pudo confirmar va marcado **«no verificado»**.

## 1. GSAP hoy

**Licencia.** GSAP es «100% free» para todos, gracias a Webflow, incluido el uso comercial
([gsap.com/pricing](https://gsap.com/pricing/)). La 3.13 metió los plugins que antes eran del Club
(SplitText, MorphSVG…) en el npm público ([gsap.com/blog/3-13](https://gsap.com/blog/3-13/)). El campo
`license` de npm apunta a la «Standard 'no charge' license»
([registry.npmjs.org/gsap/latest](https://registry.npmjs.org/gsap/latest)).
⚠️ **No es MIT.** La licencia prohíbe usar GSAP en herramientas visuales sin código que compitan con el
constructor de animaciones de Webflow. También permite a Webflow revocarla si se incumple
([texto en scancode-licensedb](https://scancode-licensedb.aboutcode.org/gsap-standard-no-charge-2025.html)).
Una presentación institucional no entra en ese supuesto.

**Versión estable: 3.15.0** ([npm](https://registry.npmjs.org/gsap/latest), [cdnjs](https://cdnjs.com/libraries/gsap)).
- `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.15.0/gsap.min.js` (cdnjs; mismo patrón para `ScrollTrigger.min.js`,
  `DrawSVGPlugin.min.js`…: en cdnjs **solo DrawSVG se vio listado**; el resto, no verificado allí).
- `https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/<Plugin>.min.js`: **verificados presentes** ScrollTrigger,
  DrawSVGPlugin, MorphSVGPlugin, SplitText, ScrollSmoother, Flip y MotionPathPlugin
  ([listado jsdelivr](https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/)).
- La presentación actual usa 3.12.5: la subida es opcional y no hace falta para lo que ya existe.

**Buenas prácticas oficiales.**
- `gsap.matchMedia()` con la condición `reduceMotion: "(prefers-reduced-motion: reduce)"`. Si la condición
  cambia, GSAP revierte las animaciones y ScrollTriggers y vuelve a ejecutar el handler. `mm.revert()` lo
  limpia todo. La función de limpieza que devuelves es solo para lo propio; **no** llames a
  `context.revert()` dentro ([docs matchMedia](https://gsap.com/docs/v3/GSAP/gsap.matchMedia()/)).
- ScrollTrigger ([docs](https://gsap.com/docs/v3/Plugins/ScrollTrigger/)):
  - **No animes el elemento fijado (`pin`)**, sino sus hijos.
  - `scrub: 1` suaviza: el cabezal tarda 1 s en alcanzar el scroll.
  - Pon **un ScrollTrigger en el timeline padre**, nunca en sus tweens hijos.
  - Crea los ScrollTriggers **en orden de página**, o usa `refreshPriority` / `ScrollTrigger.sort()`.
  - `markers: true` solo en desarrollo.
- MotionPathPlugin: mueve un marcador por un trazado. El tutorial de Codrops lo combina con DrawSVG
  (§4) ([búsqueda que lo localiza](https://tympanus.net/codrops/2026/05/21/creating-scroll-driven-svg-map-animations-with-gsap);
  página devolvió 403 a la consulta directa: **contenido no verificado de primera mano**).

**Plugins para contar procesos.**
| Plugin | Qué cuenta | Ejemplo |
|---|---|---|
| DrawSVG | un flujo que se traza: solicitud → aprobación → archivo | conector entre etapas que se dibuja con `scrub` |
| MorphSVG | un documento que cambia de forma: formulario en papel → registro digital | icono «hoja» que se vuelve «base de datos» |
| Flip | reordenar: del caos de planillas a una tabla ordenada | tarjetas sueltas que caen en una cuadrícula |
| MotionPath | algo que viaja: un activo o un oficio que recorre dependencias | punto que sigue la ruta DrawSVG |
| SplitText | titulares que entran por línea o palabra | cifra clave de cierre |

## 2. Video determinista: alternativas

| Herramienta | Licencia (verificada) | Estado | Cuándo conviene |
|---|---|---|---|
| **Motor propio** `seek(t)` + Playwright + ffmpeg | propio | — | Reutiliza el mismo SVG/GSAP de la página: **una fuente para web y video**. Por defecto. |
| **Remotion** | Licencia propia, **no OSS**. Gratis: individuos, empresas con fines de lucro **de hasta 3 empleados**, **organizaciones sin ánimo de lucro** y evaluación. El resto necesita licencia de empresa ([LICENSE.md](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)). En la 5.0 **los contratistas cuentan para el tamaño del equipo** ([migración 5.0](https://remotion.dev/docs/5-0-migration)). | activo | Videos React con `useCurrentFrame`, plantillas parametrizadas en serie. |
| **Motion Canvas** | MIT ([repo](https://github.com/motion-canvas/motion-canvas)) | última versión `@motion-canvas/core` 3.17.2, **2024-12-14** ([npm](https://registry.npmjs.org/@motion-canvas/core)): actividad baja | Animación explicativa programada con editor de vista previa. |
| **Revideo** | MIT ([repo](https://github.com/redotvideo/revideo)) | `@revideo/core` 0.11.0; fecha y mantenimiento **no verificados** | Render de video desde código vía API. Que derive de Motion Canvas: **no verificado** en la página consultada. |
| **Theatre.js** | core Apache-2.0; **studio AGPL-3.0** (solo en diseño; el bundle final lleva core) ([repo](https://github.com/theatre-js/theatre)) | `@theatre/core` 0.7.2; el desarrollo se pasó «temporalmente» a un repo privado | Ajuste fino de curvas con editor visual. Riesgo de continuidad. |
| **Lottie / dotLottie** | lottie-web MIT ([repo](https://github.com/airbnb/lottie-web)); `@lottiefiles/dotlottie-web` MIT, 0.81.0 ([npm](https://registry.npmjs.org/@lottiefiles/dotlottie-web)) | activo | Animaciones hechas en After Effects. `goToAndStop(frame, true)` permite saltar a un frame exacto, así que encaja con `seek(t)`. Usa `useSubFrames:false` para clavar el frame. |

⚠️ **Alerta Remotion:** la Corporación es una institución de educación superior. Si está constituida
**sin ánimo de lucro** (lo habitual en Colombia por la Ley 30 de 1992; **no verificado en esta consulta**),
le corresponde el tramo gratuito. Si un proveedor con fines de lucro de más de 3 personas, contando
contratistas, produce el video, ese proveedor necesita la licencia. Hay que confirmarlo antes de adoptarlo.

## 3. Scrollytelling: patrones y reglas

- **Pasos y gráfico fijo (sticky).** Cada bloque de texto dispara un estado del gráfico, que queda fijo
  mientras el texto sube ([The Pudding](https://pudding.cool/process/how-to-implement-scrollytelling/)).
  Scrollama 3.2.0 (MIT) usa IntersectionObserver en vez de eventos de scroll, y `position: sticky`
  para fijar. Tiene dos variantes: **lado a lado** y **superpuesto** a pantalla completa
  ([repo](https://github.com/russellsamora/scrollama)).
- **Scrollytelling ≠ scrolljacking.** El primero lee la posición del scroll sin alterarlo (The Pudding, ídem).
  NN/g recomienda **evitar el scrolljacking por defecto**. Si se usa: tramos cortos, nunca cambiar la
  dirección (horizontal con un gesto vertical), poco texto, nada crítico dentro, evitarlo en móvil y la
  navegación siempre visible ([NN/g](https://www.nngroup.com/articles/scrolljacking-101/)).
  ⇒ `pin` con `scrub` es scrolljacking suave: úsalo con moderación y nunca para pasar lateralmente.
- **Capítulos.** La franja superior con el capítulo actual y Av Pág / Re Pág es la versión del patrón
  «navegación visible» de NN/g.
- **Revelado progresivo** con `fromTo(...,{immediateRender:false})`: el estado en reposo es el final.
  Cumple la regla de que sin movimiento el contenido siga completo.
- **Movimiento reducido.** El criterio WCAG 2.2 **2.3.3 (AAA)** pide que la animación disparada por la
  interacción se pueda desactivar salvo que sea esencial. El parallax es el ejemplo de movimiento no
  esencial. Técnicas suficientes: C39 (CSS `prefers-reduced-motion`) y SCR40 (lo mismo en JS)
  ([W3C](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html)). La animación
  que arranca sola cae en el criterio 2.2.2 (Pausar, detener, ocultar).
- **Contraste.** Mínimo 4.5:1 para texto normal (WCAG 1.4.3, nivel AA). No se reconsultó hoy: **no verificado en esta sesión**.

## 4. Ideas de escenas (con referencia)

1. **Ruta que se dibuja + marcador que viaja.** Ejemplo: el recorrido de un traslado de activo entre sedes.
   Codrops, *Creating Scroll-Driven SVG Map Animations with GSAP* (2026-05-21): pin + timeline con
   scrub + DrawSVG + MotionPath ([enlace](https://tympanus.net/codrops/2026/05/21/creating-scroll-driven-svg-map-animations-with-gsap);
   descrito por el buscador, página con 403: **no verificado de primera mano**).
2. **Cambio de disposición con Flip.** Ejemplo: de planillas sueltas a un tablero ordenado. Codrops,
   *Scroll-Based Layout Animations* (2023-07-20, Manoela Ilic): primero se diseña el estado final en CSS
   con una clase y luego Flip anima la transición ([enlace](https://tympanus.net/codrops/2023/07/20/scroll-based-layout-animations)).
3. **Morph y trazos con los plugins ya gratis.** Ejemplo: el formulario que se vuelve registro. Codrops,
   *From SplitText to MorphSVG: 5 Creative Demos Using Free GSAP Plugins* (2025-05-14): subrayados con
   DrawSVG y un conmutador con MorphSVG ([enlace](https://tympanus.net/codrops/?p=93244)).
4. **Informe con storyboard.** Awwwards, caso *Behind The Checkout 2022*: un informe en scrollytelling
   planificado por fotogramas, como un guion gráfico
   ([enlace](https://www.awwwards.com/case-study-behind-the-checkout-2022.html)). Para inspirarse en una
   sección de proceso: [Awwwards, inspiración «Process timeline»](https://www.awwwards.com/inspiration/process-timeline-core-concepts).
5. **Contador y «antes / después».** Un contador animado con un proxy `{n}` y `onUpdate`. El antes y
   después, como una máscara que se desliza con `scrub`. Es un patrón general: **no hay una referencia
   Codrops concreta verificada**.

## 5. Íconos e ilustración (uso institucional)

| Recurso | Licencia | Nota |
|---|---|---|
| Lucide | ISC; los íconos que vienen de Feather, MIT ([lucide.dev/license](https://lucide.dev/license)) | conservar el aviso de copyright |
| Tabler Icons | MIT, 6.238 íconos (5.184 de contorno y 1.054 rellenos), cuadrícula de 24 y trazo de 2 px ([repo](https://github.com/tabler/tabler-icons)) | combina bien con Lucide |
| Phosphor | MIT, 1.248 íconos y 6 pesos, incluido duotono ([repo](https://github.com/phosphor-icons/homepage)) | el duotono sirve para escenas |
| unDraw | uso comercial gratis y sin atribución, se puede modificar. **Prohíbe** las colecciones que compitan, la descarga automatizada y **el uso para entrenar IA o la automatización sin permiso** ([licencia](https://undraw.co/license)) | ⚠️ que el agente no las descargue por script: descarga manual |
| Open Peeps | CC0, de Pablo Stanley ([openpeeps.com](https://www.openpeeps.com/)) | personas dibujadas a mano, sin restricción |

## 6. Diagramas animados

- **Mermaid** (flowchart): las aristas se animan con un ID (`e1@-->`), velocidad `fast` o `slow`, o con
  `classDef` ([docs](https://mermaid.js.org/syntax/flowchart.html); versión mínima **no verificada**).
  Aporta cuando hay que generar un diagrama de flujo desde texto en segundos. Controla poco la coreografía.
- **D3**: aporta cuando la escena es **dato real**, como barras, mapas o escalas. Su licencia no se
  reconsultó (ISC según lo conocido: **no verificado hoy**).
- **Rough.js**: MIT, pesa menos de 9 kB y da un trazo de boceto sobre SVG o canvas
  ([repo](https://github.com/rough-stuff/rough)). Aporta para el «antes» (el proceso manual, a mano
  alzada) frente al «después» limpio.

## Qué adoptar ya / qué probar / qué evitar

| Decisión | Qué | Por qué |
|---|---|---|
| **Adoptar ya** | GSAP 3.15.0 + DrawSVG/Flip/MorphSVG desde jsdelivr | gratis también en uso comercial y los siete plugins están verificados en el CDN |
| **Adoptar ya** | `gsap.matchMedia` con `reduceMotion` | práctica oficial que cumple las técnicas de WCAG 2.3.3 |
| **Adoptar ya** | Pasos con gráfico fijo (`position: sticky`) y un ScrollTrigger por timeline | es el patrón de The Pudding y Scrollama, sin secuestrar el scroll |
| **Adoptar ya** | Lucide + Tabler/Phosphor + Open Peeps | MIT, ISC y CC0: sin fricción institucional |
| **Mantener** | Motor propio `seek(t)` + Playwright + ffmpeg | la misma fuente da la web y el video, sin licencias de terceros |
| **Probar** | Lottie con `goToAndStop(frame,true)` | encaja con `seek(t)` si llega una animación de After Effects |
| **Probar** | Rough.js para el «antes» y Mermaid para borradores de flujo | contraste narrativo barato |
| **Evitar** | Remotion sin confirmar la naturaleza jurídica de quien produce | licencia no OSS: los contratistas cuentan desde la 5.0 |
| **Evitar** | Theatre.js y Motion Canvas como base | studio AGPL y desarrollo privado en uno, sin publicaciones desde dic-2024 en el otro |
| **Evitar** | Scroll horizontal secuestrado y parallax obligatorio | NN/g y WCAG 2.3.3 |
| **Evitar** | Descargar unDraw por script | su licencia lo prohíbe |
