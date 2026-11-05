# Protocolo creativo: escenas e identidad que salen del tema

Por qué existe: lo genérico se nota a los diez segundos (el mismo diagrama de cajas y flechas en cada capítulo,
tarjetas que suben con fundido, un degradado morado). La audiencia lo reconoce como relleno y deja de mirar. Lo que
impresionó en la presentación de SIGAF fue que cada sistema tenía su propia metáfora, sacada de su mundo: un bien
que viaja, un expediente que se arma, un calendario que se cumple.

## 1. Inventario del mundo del tema (antes de dibujar nada)

Escribe tres listas cortas a partir de lo que se entendió en la fase 1:
- **Objetos:** las cosas que existen en ese mundo (una placa, un acta, una gota, un diploma, una llave, un plano).
- **Materiales y texturas:** papel, metal, agua, tiza, pantalla, tela, madera; colores que el tema ya trae.
- **Vocabulario:** los verbos y sustantivos que usa la gente del tema («se radica», «se firma», «se evapora»,
  «se gradúa»). Los títulos y rótulos salen de aquí.

## 2. Tres conceptos por escena

Por cada escena, propone **tres conceptos visuales distintos** usando objetos del inventario y uno o más
mecanismos ([mecanismos.md](mecanismos.md); amplitud de opciones en el bolsillo, [bolsillo-mochilero.md](bolsillo-mochilero.md)).
Distintos de verdad: cambia el objeto protagonista, no solo el color.

Ejemplo, escena «el estudiante a lo largo de la carrera»:
- A. Un camino con estaciones (semestres) por el que viaja una ficha con su foto genérica. → viaje (2) + sello (8)
- B. Un diploma que se arma pieza a pieza: cada asignatura aprobada es un fragmento que encaja. → acumulación (6) + transformación (3)
- C. Una línea de tiempo vertical con hitos que se encienden. → línea de tiempo (9)

## 3. Descartar lo genérico, con el porqué

Descarta los conceptos que caigan en un delator y escribe por qué en una línea:
- **El mismo diagrama para todo:** si esta escena se parece a la anterior, la audiencia no nota el cambio de tema.
- **Cajas y flechas:** comunican «hay pasos», nada más; cualquier tema podría ponerlas.
- **Tarjetas con fade-up en cada bloque:** animación de entrada sin significado; cansa en la tercera.
- **Texto donde cabía un diagrama:** si el párrafo describe un movimiento, ese movimiento es la escena.
- **Clichés de IA:** degradados morado-azul, orbes brillantes, robots, cerebros, circuitos, «glassmorphism» sin motivo.

(En el ejemplo: C se descarta, es una línea de tiempo que serviría para cualquier institución; A y B sobreviven.)

## 4. Elegir uno y pasar la crítica final

Elige el concepto que mejor resuelva la tensión del capítulo y pregúntale: **«¿esto se confundiría con otra
presentación?»** Si sí, vuelve al inventario. Si no, se construye. Anota en una línea el concepto elegido y los
descartados: es lo que Leo revisa antes de que se escriba código, y lo que alimenta la bitácora.

## 5. Identidad visual

- **Con perfil** (p. ej. [perfil-institucional-americana.md](perfil-institucional-americana.md)): se aplican sus
  colores, marca y reglas de lenguaje, y la creatividad vive en las escenas.
- **Sin perfil:** la identidad se deriva del tema con el mismo protocolo. Paleta: 1 fondo, 1 superficie, 1 tinta,
  1 tinta suave y **un** acento, tomados de los materiales del inventario (el ocre del papel de archivo, el azul de
  un plano, el verde de una pizarra). Tipografía: una de display y una de texto cuyo carácter encaje (serif clásica
  para historia, grotesca técnica para ingeniería, redonda y amable para niños). Se escriben en los tokens de
  `:root` del andamiaje. Contraste mínimo 4,5:1 para el texto.
- Si `ui-ux-pro-max` está instalada, su buscador da pares tipográficos y paletas por tipo de producto; se toma el
  ROL de cada color, no el hex a ciegas.

## 6. Referencias frescas

Cuando el tema pide algo que el catálogo no tiene, busca antes de inventar: [referencias-web.md](referencias-web.md)
como banco de ideas, y fuentes vivas como Codrops (tutoriales con código), Awwwards (sitios premiados de
scrollytelling) y la documentación y demos de GSAP. Se toma la idea y se reconstruye con los mecanismos propios;
no se copia código ajeno sin revisar su licencia. Antes de una presentación importante, o cada mes, se puede lanzar
el agente `vigia-visual` para refrescar el catálogo.
