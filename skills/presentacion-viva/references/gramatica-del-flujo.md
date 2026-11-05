# Gramática del flujo en video — la especialidad de la skill

Contenido: 1 Por qué funciona · 2 Cuándo hay flujo · 3 El guion · 4 Anatomía · 5 Composición · 6 Maquetas ·
7 Microacciones · 8 Ritmo · 9 Identidad · 10 Serie y sala · 11 Revisión

Los tres videos de SIGAF (ingesta, traslado, paz y salvo) fueron lo que más impresionó a los directivos: más que
la página y más que las cifras. Míralos antes de hacer uno: `assets/referencia/hoja-flujo-*.jpg` (un fotograma
cada 2 s). Este fichero explica por qué funcionaron y cómo hacer otro igual de bueno **con cualquier tema**.

## 1. Por qué funciona

- **Se ve el proceso moverse.** Un objeto (la ficha) viaja de etapa en etapa: la audiencia sigue *una cosa*, no
  lee un diagrama. Es la diferencia entre un mapa y un viaje.
- **Cada etapa enseña su objeto.** El panel muestra lo que de verdad aparece en ese paso (un botón, un acta, un
  sello, una lista que cambia de estado), dibujado en abstracto. Eso le da a la gente algo que reconocer.
- **Abstracción honesta.** Barras en vez de texto, siluetas en vez de fotos: no hay datos personales que tapar,
  el video vale para cualquier caso y nadie se distrae leyendo.
- **Corto y cerrado.** Unos 14 s. Termina diciendo qué se logró. Se entiende sin sonido y sin narrador, en bucle.
- **Nada inventado.** Las etapas y los estados son los del sistema o de la fuente. Un estado con su nombre real
  (`FIRMA_SOLICITADA`) da más confianza que cualquier adjetivo.

## 2. Cuándo hay flujo (y cuándo no)

Hay flujo cuando el tema se puede contar como **«primero…, luego…, al final…»** con un resultado. Eso pasa mucho
más allá del software:

| Tema | Qué viaja (la ficha) | Etapas | Resultado |
|---|---|---|---|
| Un trámite (caja menor, matrícula, compra) | la solicitud, el anticipo, el expediente | quién hace qué | trámite cerrado |
| Un sistema (ingesta, traslado, aprobación) | el registro, el bien, el documento | pasos del código | estado final |
| Un ciclo de vida (préstamo, equipo, contrato) | el objeto | estados que se repiten | vuelve a empezar |
| Una historia (institución, proyecto) | el tiempo, una idea | hitos con fecha y fuente | lo que es hoy |
| Una metodología o una receta | el producto que se transforma | operaciones | el producto terminado |
| Un recorrido (sedes, ruta, cadena) | una persona, un paquete | lugares | el destino |

**No hay flujo** si el tema es una comparación (antes/después, opción A/B), una composición (de qué está hecho),
una cifra o un argumento. Ahí la forma es una escena de la página (`mecanismos.md`; para ampliar opciones, el bolsillo `--tabla diagramas`), no un
video. Forzar un flujo donde no lo hay produce una fila de cajas con una bolita encima.

**Por defecto:** cuando el tema tiene flujos, propón un video por cada flujo principal (de 1 a 3) e intégralos en la
página con la sala de flujos (§10). Es el pico de la presentación. Si el pedido es «solo el video», haz solo eso.

## 3. El guion (antes de abrir el motor)

Escribe el flujo como tabla y enséñaselo a Leo en una línea por etapa. Es la puerta: si el guion no se entiende
leído, el video tampoco.

| # | Etapa (≤16 car.) | Frase de acción (≤52) | Estado real | Maqueta: qué objeto se ve | Microacción |
|---|---|---|---|---|---|
| 1 | Expediente | Activos Fijos pulsa «Generar acta» | ACTIVA | ficha de la persona con 3 bienes | el botón se hunde y brilla |
| 2 | Acta creada | Se crea el acta con foto fija de cada activo | FIRMA_SOLICITADA | documento con 3 miniaturas | flash en cada foto |

Reglas: **una idea por etapa**; la frase empieza por quien actúa o por lo que pasa, en presente; el estado sale de
la fuente (si no lo hay, una nota corta o nada); de 3 a 7 etapas (8 como mucho, en zigzag; más, parte el flujo en
dos videos). Añade el **puente** si el flujo entrega a otro sistema o área, y el **resultado** en una frase.

Ese guion, en JSON, genera el esqueleto con todo calculado:
```
node "<carpeta de la skill>/scripts/nuevo-flujo.mjs" guion.json <carpeta-de-flujos>
```
```json
{ "slug": "paz-y-salvo", "n": 3, "de": 3, "sistema": "SIGAF", "titulo": "Paz y salvo",
  "subtitulo": "El cierre del ciclo del funcionario con sus activos",
  "tema": "americana", "composicion": "lineal", "ficha": "doc",
  "etapas": [ { "nombre": "Expediente", "frase": "Activos Fijos pulsa «Generar acta»", "estado": "ACTIVA",
                "nota": "rechaza si ya hay un acta abierta", "maqueta": "ficha de la persona con 3 bienes" } ],
  "puente": { "nombre": "Talento Humano", "etiqueta": "Desvinculaciones" },
  "resultado": { "titulo": "Ciclo del funcionario cerrado", "sub": "La etapa final, que conecta con Talento Humano" } }
```
`tema`: `"americana"`, `"neutral"` o `{ "fondo", "tinta", "acento" }`. `composicion`: §5. `ficha`: `doc` (documento),
`row` (fila de hoja de cálculo), `rowHollow` (fila vacía, a la espera), `plate` (placa). El esqueleto deja cada
maqueta como marcador `MAQUETA ·` y `verificar.mjs` falla mientras quede uno: dibujarlas es tu trabajo (§6).

## 4. Anatomía (todas las piezas son opcionales menos el resultado)

1. **Cabecera**: «Sistema · Flujo N de M», título y subtítulo. Entra centrada y se retira a la esquina (0,1–1,3 s).
2. **Trazo**: el camino (vía) que se dibuja al entrar y se ilumina detrás de la ficha.
3. **Estaciones**: nodos numerados con nombre; se encienden al llegar la ficha, laten y dejan un visto al irse.
4. **Ficha**: el protagonista que viaja, con estela y halo. Cambia de forma si el objeto se transforma
   (`kinds` + `weights`: la fila de Excel se vuelve placa en la ingesta).
5. **Panel de evidencia**: «Etapa 0N de 0M», la frase, chips de estado (el de estado parpadea al aparecer) y la
   maqueta. Un puntero lo une a la estación activa.
6. **Rama** (opcional): un camino secundario para lo que espera o se desvía (la «sala de espera» de la ingesta,
   con `extra(api)`). Úsala solo si en la realidad existe.
7. **Puente** (opcional): una estación fantasma, con trazo punteado, hacia otro sistema o área.
8. **Resultado**: el panel completo dice qué se logró, con un dibujo final (un círculo que se cierra, un contador).
9. **Salida**: todo se funde al fondo en el último segundo, para que el bucle no salte.

## 5. Composición: la forma del camino es la forma del tema

`SV.composicion(tipo, n, opciones)` da las posiciones de las estaciones y el trazo; la ficha lo recorre exacto.

| Composición | Cuándo | Ejemplo |
|---|---|---|
| `lineal` | proceso con principio y fin, 3-6 etapas | trámite, aprobación (los tres de SIGAF) |
| `zigzag` | proceso largo, 7-8 etapas, en dos filas | compra pública completa |
| `ciclo` | lo que vuelve a empezar | préstamo, ciclo de vida de un equipo, mejora continua (`flujo-3-ciclo.html`) |
| `arco` | progresión con cima: crece y se consolida | de idea a rutina, adopción de un sistema |
| `escalera` | niveles o madurez que se suben | del papel a lo automático |
| trazo libre | cuando el tema tiene su propia forma | un mapa de sedes, una ruta, un árbol, un embudo |

**Trazo libre:** escribe el `d` de SVG con la forma del tema (la silueta de una ciudad, el río que une las sedes),
coloca las estaciones donde toque y calcula su fracción con `SV.fraccion(d, x, y)`. Ficha y vía siguen el trazo
solas. Esto es lo que hace que un flujo no se confunda con otro: si el tema es un recorrido geográfico, el camino
debería parecerse al mapa, no a una línea recta.

Con `ciclo` el panel va en columna a la derecha (`forma: 'columna'`, el puntero entra por el lado); en el resto,
abajo. Las etiquetas se colocan hacia fuera solas (`labelPos`: above, below, left, right).

### 5.bis Más allá de las estaciones

Todas las composiciones de arriba son **un camino con estaciones y una ficha que lo recorre**. Funciona, pero repetido
cansa: Leo lo vetó en la guía de traslado (2026-10-30: «no uses la línea horizontal de estaciones»). **Regla: antes de
elegir composición, lee la bitácora; si la última presentación usó estaciones, esta no las usa**, salvo que el tema
sea literalmente un recorrido. Cuatro gramáticas sin estaciones, todas con el mismo motor:

| Gramática | La idea | Cuándo | Cómo con el motor |
|---|---|---|---|
| **Documento protagonista** | Un solo objeto (acta, formulario, expediente) vive todo el video y **se transforma**: se escribe, se firma, se adjunta, vuelve sellado | trámites donde el papel ES el proceso | `limpio: true` + paneles `full: true` con el texto de cada paso a la derecha; el objeto en `cfg.extra(api)` colgado de `api.root`, movido con `SV.poses` y animado con `SV.escribir`, `SV.trazo`, `SV.sello`/`SV.golpe`. **Plantilla: `assets/motor-video/flujo-4-documento.html`** |
| **Mapa ilustrado** | Un plano del lugar (campus, sede, ciudad) y el recorrido dibujado encima | el tema es *dónde* va algo | Un SVG a pantalla completa en `extra`; el trazo con `data-draw` y lo que se mueve con `api.route` |
| **Carriles por actor** | Una franja por persona o área; el objeto cruza de una a otra | importa *quién* hace cada cosa y cuándo pasa de mano | Franjas en `extra`; el objeto baja de carril con poses clave; un panel por traspaso |
| **Objeto que se transforma** | La cosa cambia de estado (borrador → firmado → aprobado; dañado → reparado) sin moverse | el valor está en el cambio, no en el viaje | El objeto quieto al centro; cada panel cambia una capa (`data-fade`, `data-pop`); el sello al final (PRC-003) |

**Por qué gustó tanto (Leo, 2026-10-30: «quedó muy áspero»)** — lo que hay que repetir, no el acta en sí:
- **Un solo protagonista que no se va nunca.** La audiencia sigue al objeto, no a una lista de pasos; cada paso es
  algo que *le pasa* (se escribe, se encoge, se firma, se adjunta, vuelve sellado).
- **Dos columnas fijas:** el objeto a la izquierda, a pantalla completa de alto; a la derecha, número de paso, una
  frase de 6 palabras, una línea de apoyo y **una nota con etiqueta** (HORARIO, OBLIGATORIO, COMPROMISO, CUIDADO): la
  regla que el funcionario no se puede saltar.
- **Datos reales del proceso, datos de persona ficticios:** captura real del portal, correos reales, horario real;
  nombres y cédulas inventados y rotulados en el propio objeto.
- **Apertura y cierre centrados con la marca**, y el cierre dice el valor («cumplir el proceso protege los bienes de
  la institución»), no el resumen.
- **Ritmo de guía:** ~4–6 s por paso, 9 paneles, ~47 s. Más largo que un flujo de presentación, porque se mira
  para aprender, no para impresionar.

**Lo aprendido con el documento protagonista (guía de traslado, 2026-10-30):**
- Sin `cfg.nodes`, `cfg.ficha` ni `cfg.pointer` no se dibuja ninguna estación; `limpio: true` deja los paneles como
  pantallas limpias (antes había que fijar `panel`, `panelIn` y quitar el fondo del `.pbox` a mano).
- El objeto va en `api.root`, no en `api.html`: `html` queda **debajo** de los paneles y una ventana de correo opaca lo
  tapa justo cuando el acta tiene que entrar en ella.
- La escritura sola se hace con `textContent = texto.slice(0, n)`, con `n` función de `t` (sigue siendo
  determinista). Ritmo que se lee: **~0,011 s por carácter + 0,12 s por campo**; a 0,018 s el acta no terminaba en
  su panel.
- Un trazo de firma con `stroke-dasharray` y `linecap: round` **deja un punto antes de empezar**: opacidad 0 hasta su
  instante.
- Texto sobre un sello circular: con `textPath` sobre dos arcos (el de abajo en sentido antihorario para que se lea
  derecho); el texto recto se monta sobre el anillo.
- Los datos ficticios se rotulan **en el objeto** («EJEMPLO · DATOS FICTICIOS»), no solo en el texto de al lado.
- Un video de guía completa puede pasar de los ~14 s (el de traslado mide ~47 s) si cada panel es un paso que se lee
  solo; lo que no puede es tener dos pasos en un panel.

## 6. Maquetas: el objeto de cada etapa

La maqueta es el corazón de cada etapa. Ocupa 600×272 px a la derecha del panel (o el ancho de la columna).

- **Del mundo del tema.** Software: la pantalla, el botón, la lista con estados. Trámite: el correo, el formato, la
  firma, el sello, la hoja de cálculo. Historia: el documento de archivo, el mapa, la foto enmarcada, el sello de una
  resolución. Logística: la caja, la etiqueta, el camión. Salud: la ficha, el turno. Pregunta «¿qué tiene en la
  mano o en la pantalla la persona en este paso?».
- **Abstracta.** `.bar` para el texto, círculos y rectángulos para las imágenes, el texto real solo en lo que
  importa (el nombre de un botón, un estado, un título de documento). Así no hay datos personales y nadie lee.
- **Cualquier diagrama cabe en una maqueta**: barras que suben, un medidor, una línea de tiempo, un mapa con puntos,
  una mini red de nodos, un calendario que se llena. Para elegir, el bolsillo (`--tabla diagramas`); para construirlo, SVG en la
  cadena `html` del panel con los atributos declarativos del motor.
- **Distinta en cada etapa.** Si dos etapas seguidas muestran la misma tarjeta con barras, una sobra o le falta
  su objeto.
- Atributos que animan solos (tiempo relativo al inicio del panel): `data-in="0.5"` (sube y aparece),
  `data-pop="0.3"` (salta con rebote), `data-draw="0.2,0.8"` (un trazo se dibuja), `data-fade`, `data-slide`,
  `data-out`. Lo que no cubren va en `tick(lt, el)`.

## 7. Microacciones (una por etapa, la que cuenta lo que pasa)

| Lo que pasa | Microacción | Cómo |
|---|---|---|
| alguien decide o pulsa | el botón se hunde y brilla | `tick`: `scale(1-0.06k)`, `boxShadow` y `mix(C.gold, C.goldHi, k)` |
| se registra o fotografía | destello sobre cada miniatura | rect blanco con opacidad 0,85→0 escalonada |
| se aprueba o firma | sello que cae y deja onda | escala 1,7→1 con giro −14°→0 y un círculo que crece y se apaga |
| cambia un estado | la etiqueta cambia con un pulso | chip `swap: [{ at, t }]` o el texto de `.mini` en `tick` |
| se envía o archiva | el documento viaja a la carpeta | trazo punteado `data-draw` + flecha + carpeta `data-pop` |
| se valida | lista que se marca | `SV.checkSvg(at)` por fila |
| pasa el tiempo | casillas que se llenan | opacidad del fondo por índice |
| se cuenta | contador que sube | `textContent` redondeado desde `prog(lt, a, b)` |
| se bloquea o protege | candado que se cierra | arco del candado con `data-draw` |

Movimiento con significado: si una microacción no cuenta qué pasa, sobra.

## 8. Ritmo

`SV.tiempos(n, { inicio: 2.0, paso: 1.6 })`: la primera llegada a los 2,0 s y una cada 1,6 s; el resultado
entra una etapa después de la última y el video dura 3,5 s más. Con 5 etapas, 13,5 s, como los que se proyectaron.
Con 7-8 etapas, `paso: 1.35`. Duración sana: **10-20 s**. Si pasa de 20, el flujo tiene dos historias: pártelo.
Las frases cortas se leen en 1,6 s; las de más de 52 caracteres, no.

## 9. Identidad

- Con perfil: `SV.tema('americana')` (azul profundo y dorado, idéntico píxel a píxel a los videos de SIGAF).
- Sin perfil: deriva el tema con el protocolo creativo y pásalo como tres colores:
  `{ fondo, tinta, acento }`. El motor calcula fondos, tintas apagadas, vías y acentos claros.
- **Ningún color literal** en las maquetas: `C.gold`, `C.mute`, `SV.rgba(C.ink, .3)` en el JS y `var(--gold)`,
  `rgba(var(--mute-rgb),.3)` en el CSS. Así el mismo flujo cambia de identidad con una línea, y `verificar.mjs` lo
  comprueba. Roles: `bg bg2 bg3 node panel ink mute info dim faint track line gold goldL goldHi goldTxt pass plate
  cream` (`gold` es el acento del tema, sea del color que sea).
- Tipografía: Bahnschrift y Consolas por defecto (vienen con Windows). Otra familia del perfil: `#stage{font-family}`
  en el `<style>` del flujo.

## 10. Serie y sala

- Varios flujos de un mismo tema forman una **serie**: «Flujo 1 de 3», misma composición base, mismo tema, misma
  ficha cuando el objeto es el mismo. La variedad la ponen las maquetas, no el andamiaje.
- En la página van en la **sala de flujos** del andamiaje (pestañas, una frase por flujo dicha por su resultado,
  bucle en silencio, se reproduce solo cuando está en pantalla, con controles si hay movimiento reducido). Copia los
  MP4 a `media/`. El patrón está comentado en `assets/andamiaje/index.html`.
- Solo video: entrega los MP4 y la hoja de contactos de cada uno.

## 11. Revisión (la puerta del flujo)

Una pasada de revisión y una tanda de correcciones **antes** del render final: los stills son fieles al video, así
que todo lo que se puede ver en el MP4 se ve antes en ellos.
1. `node motor.mjs render <carpeta-de-flujos> flujo-N-x --stills <llegada+0,8 de cada etapa>,<resultado+0,8>`, para
   TODOS los flujos de la serie: mira cada PNG con Read.
2. `node verificar.mjs flujo-N-x.html` (modo flujo): sin marcadores de maqueta, duración 10-20 s, colores por rol.
3. Crítica sobre los stills, en este orden: ¿se entiende sin sonido y sin narrador? ¿cada etapa muestra un objeto
   distinto? ¿la composición se parece a la forma del tema? ¿se confundiría con otro flujo de otra presentación? Si
   algo falla, vuelve al guion, no al código.
4. Junta lo de los pasos 1-3 en una lista y corrígela entera; repite solo los stills de lo que cambió.
5. Render final y **hoja de contactos mirada entera**: sin texto cortado ni encimado, sin datos personales.
