# El bolsillo: cómo consultar al Mochilero

El oficio de esta skill (el arco, el protocolo creativo, la gramática del flujo y los mecanismos con su código) se
queda aquí y aquí se decide. El **Mochilero** guarda el catálogo: qué opciones existen, con su fuente, su licencia
y su veredicto. Desde el 2026-10-26 tiene un dominio entero para esta skill, `presentacion`, con 12 tablas.

**Cómo se reparten el trabajo:** el Mochilero ofrece las opciones con su fuente y esta skill elige, aplicando su
protocolo. Una fila del bolsillo nunca sustituye a la crítica final («¿esto se confundiría con otra presentación?»).

## Cómo se llama

```bash
python "<carpeta de esta skill>/../mochilero/scripts/buscar.py" "<2 a 5 términos>" --dominio presentacion
python "<carpeta de esta skill>/../mochilero/scripts/buscar.py" --id PCN-008        # una fila entera
python "<carpeta de esta skill>/../mochilero/scripts/buscar.py" --tablas            # recuentos al día
```

- La ruta `../mochilero` vale igual instalada en `~/.claude/skills/` que dentro del plugin `skill-de-autor`: las
  dos skills son hermanas.
- **Una intención por consulta**, con 2 a 5 términos. Se puede mezclar español e inglés.
- Salen 3 filas, unos 250 tokens. Hay que filtrar en cuanto se sepa dónde vive la respuesta: `--tabla recetas`, o
  `--tabla librerias-efectos,librerias-video`.
- **Presupuesto: como mucho 3 consultas por escena.** Si hace falta más, la escena aún no tiene concepto, y eso se
  resuelve con el protocolo creativo, no con más búsquedas.
- **Nunca se leen los CSV de `datos/`.** Cargarlos en el contexto es justo lo que el bolsillo evita.

**Si el Mochilero no está** (otra máquina, la nube, una instalación a medias), la skill sigue con su oficio
(`mecanismos.md`, con el código de cada mecanismo) y `referencias-web.md`, y lo dice en una línea.
El catálogo amplio que vivía en `catalogo-visual.md` se retiró el 2026-10-26: en la iteración 3 de las evals, con
él y sin él la skill sacó lo mismo (37/41). La skill no se debilita por faltar el bolsillo.

## Qué preguntarle en cada fase

| Fase | Para qué | Tabla | Consultas probadas |
|---|---|---|---|
| 2. Arco | Que la estructura sirva a una audiencia ejecutiva | `narrativa` | `conclusion primero directivos` · `pico final apertura cierre` · `revelacion progresiva` |
| 3. Escenas | Tener opciones donde elegir los tres conceptos de cada escena | `diagramas` · `componentes-narrativos` · `recetas` | `diagrama quien hace que areas` · `presupuesto reparto rubros` · `antes y despues cortina` · `sello aprobado` · `drawsvg motionpath combinacion` |
| 3. Identidad | Legibilidad en sala y color con sentido | `legibilidad` · `disciplina` | `tamano de texto proyector sala` · `cifras tabulares` · `daltonismo paleta datos` |
| 3. Datos | Elegir la gráfica por la pregunta y descartar las que engañan | `graficas-narrativas` | `torta porciones` · `doble eje` · `ranking quien va primero` |
| 4. Video | Elegir motor y licencia, y cumplir la alternativa en texto | `librerias-video` · `disciplina` | `video determinista frames` · `remotion licencia` · `alternativa texto video mudo` |
| 5. Construir | Versión exacta y CDN antes de usar un plugin o una librería | `librerias-efectos` · `librerias-graficas` · `disciplina` | `trazo que se dibuja ruta` · `objeto que viaja por una ruta` · `sankey d3` · `scrolljacking` |
| 6. Verificar | La lista de lo que la puerta no puede pasar por alto | `disciplina` | `destellos sello confeti` · `pausar bucle autoplay` · `contraste graficos lineas` · `licencia atribucion institucional` |
| 1, 3, 5 y 6. Imágenes | Herramienta con su licencia, tratamiento con el tema, derechos y accesibilidad de fotos e ilustraciones ([imagenes.md](imagenes.md)) | `librerias-imagen` · `tratamiento-imagen` · `librerias-ilustracion` | `quitar fondo foto modelo` · `vectorizar imagen svg` · `duotono foto tema` · `texto alternativo foto decorativa` · `personas en fotos autorizacion` · `metadatos gps exif` · `foto banco licencia` |

## Cómo se lee la respuesta

- **Cada fila trae su id y su fuente.** Al enseñarle a Leo el concepto elegido y los descartados, se cita el id:
  «sello al final del recorrido (PCN-008)». Así cualquiera puede volver a la regla.
- **`madurez`** es el veredicto de las librerías: `Adoptar ya` · `Probar` · `Vigilar` · `Evitar` · `Condicional`.
  Una fila `Evitar` se respeta aunque la librería sea espectacular, y la razón va en «Cuándo no».
- **`[revisar: …]`** marca un dato que no se confirmó en su fuente. Se puede usar, pero se dice. Si la escena
  depende de ese dato, hay que comprobarlo antes.
- **Si una fila apunta a `mecanismos.md §n`**, el cómo con nuestro andamiaje está allí: el código no vive en el
  bolsillo.
- **«Sin coincidencias verificadas»**: primero se mira la lista «Por término suelto» y se reformula con 1 o 2
  términos. Si vuelve a fallar, el bolsillo no tiene la respuesta: se decide con el oficio y se anota el hueco
  (abajo).

## Lo que el bolsillo ya cambió en el oficio

Estas reglas llegaron con la investigación del 2026-10-26 y ya están en las puertas de esta skill:

- **GSAP 3.12.5 en cdnjs no trae DrawSVG, MorphSVG ni SplitText** (PTC-035, verificado en la API de cdnjs). Con el
  andamiaje en 3.12.5, el trazo se dibuja con `pathLength:1` (mecanismos.md §1), o se suben TODAS las URL a 3.15.0.
- **Cada MP4 de flujo lleva al lado su alternativa en texto** (PDS-043, WCAG 1.2.1, nivel A): la lista de etapas.
  Un video mudo no puede ser la única fuente de la información.
- **Un bucle que dura más de 5 s necesita control de pausa** (PDS-007, WCAG 2.2.2).

## Devolver lo aprendido (fase 7)

Una presentación entregada enseña cosas, y lo que sirve para cualquier otra vuelve al bolsillo:

1. **Qué sube:** una receta o una regla que se usó en una presentación real y funcionó con la audiencia (está en
   la bitácora), o un hueco que el bolsillo no supo responder. **Qué no sube:** el código del andamiaje (va a
   `mecanismos.md`), las metáforas de una presentación concreta (inspiran, no son molde) y nada con datos personales.
2. **Cómo:** se añade una línea a `../mochilero/trabajo/investigacion/<tabla>.jsonl` con el esquema de guía (`id`,
   `categoria`, `tema`, `palabras_clave`, `descripcion`, `hacer`, `no_hacer`, `ejemplo_bien`, `ejemplo_mal`,
   `severidad`, `puestos`, `artefacto`, `fuente`, `verificado_el`), con el siguiente id libre de la tabla. Si no hay
   una fuente externa, la fuente es la **referencia técnica en que se apoya** (MDN, W3C, la doc de la librería: el
   integrador exige una URL y rechaza la ruta de la bitácora, medido 2026-10-30) y la descripción lleva «Origen:
   bitácora AAAA-MM-DD» y `[revisar: receta propia]`.
3. **Puerta:** `python ../mochilero/herramientas/integrar_investigacion.py`, que no puede dar errores, y
   `python ../mochilero/scripts/pruebas_buscar.py`, que tiene que seguir en verde.
