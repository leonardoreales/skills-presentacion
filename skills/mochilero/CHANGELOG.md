# CHANGELOG — Mochilero (MOC)

## 0.3.1 · 2026-10-30 · lo aprendido en la guía de traslado de activos (presentacion-viva)

**Huella (PRO-008):** `sha256 5c3932387a0b04318f0b653eecb054abc6866e4fe25f2e8aa685499bdb12cb6f` · 272 ficheros.

- **+6 filas propias** devueltas por presentacion-viva («Devolver lo aprendido»), todas `[revisar: receta propia]`
  con su origen en la bitácora 2026-10-30 y su base técnica como fuente: `recetas` PRC-017 documento protagonista
  (video sin estaciones), PRC-018 campos que se teclean solos, PRC-019 sello con texto en arco, PRC-020 exportar
  HTML autocontenido + PDF con prueba sin red; `componentes-narrativos` PCN-025 documento que se diligencia campo por
  campo y PCN-026 lista que el lector marca. Llenan dos huecos medidos: «lista verificacion interactiva» y
  «checklist» no tenían respuesta.
- La fuente de una fila propia no puede ser la ruta de la bitácora (el integrador exige URL): va en la descripción.

**Arneses:** `pruebas_buscar.py` **82/82** · `pruebas_ids.py` **11/11**.

## 0.3.0 · 2026-10-26 · imágenes del usuario: tratamiento, animación, IA y derechos

**Huella (PRO-008):** `sha256 5054628918229fe548eb85015b0573ae177b93bec6a5d94b3b0293f4a7c9ecae` · 272 ficheros
(estable en dos corridas). Hecho en la mesa de experimentos, sin tocar la copia instalada ni `skill-de-autor`.

- **Dos tablas nuevas en `presentacion`, ya son 14 con 346 filas:** `librerias-imagen` (PIM, 16) y
  `tratamiento-imagen` (PTI, 22). Procedencia en `FUENTES.md` §5; 10 filas con `[revisar]`.
- **Alerta que cambió código de presentacion-viva:** el modelo por defecto de `rembg` es `bria-rmbg`, no comercial
  (verificado en su código). `preparar-imagen.py fondo --ia` fija `birefnet-general` (MIT).
- **`buscar.py`** (`INFO`) e **`integrar_investigacion.py`** (`DOMINIO`): las dos tablas. Las 12 anteriores, idénticas
  byte a byte tras reintegrar (medido con md5).
- **`pruebas_buscar.py`:** +5 casos de relevancia, contrato de prefijos con PIM y PTI, «14 tablas». La prueba de
  orientación por término suelto usaba «ley 1581 habeas data», que desde PTI-018 SÍ tiene respuesta: pasa a
  «habeas plomeria» (misma premisa) y se añade una prueba de que la consulta vieja responde con PTI-018.

**Arneses:** `pruebas_buscar.py` **82/82** · `pruebas_ids.py` **11/11**.

## 0.2.0 · 2026-10-26 · dominio `presentacion`: el bolsillo de presentacion-viva

**Huella (PRO-008):** `sha256 845d3a112f59b09ad73e65b2db1b90da4ea0081f6080bf4d21df65567f0996ea` · 268 ficheros
(estable en dos corridas). Hecho en la mesa de experimentos (`~/mesa-de-experimentos`), sin tocar la copia
instalada en `~/.claude/skills/mochilero` ni el repo `skill-de-autor`.

- **Dominio nuevo `presentacion`, con 12 tablas y 308 filas.** 152 filas migran el catálogo de presentacion-viva; las
  otras 156 salen de dos investigaciones web (vigía visual y oficio de presentar), con 26 descartes por duplicado, cada
  uno con su motivo. Procedencia en `FUENTES.md` §4. Ids con prefijo por tabla: `PDG PCN PRC PDS PGN PNR PLG PTC PVD
  PLB PIC PFW`. Comprobado que ninguno existía antes.
- **Corrección que afecta al andamiaje de presentacion-viva:** cdnjs no publica DrawSVG, MorphSVG ni SplitText para
  GSAP 3.12.5, y sí para 3.15.0 (API de cdnjs, verificado). Va en PTC-004, PTC-005, PTC-007 y PTC-035.
- **`scripts/buscar.py`:** constante `DOMINIOS` (el `--dominio` y `--tablas` la leen) y descripciones del dominio en
  `INFO`. Sin cambios en el índice ni en la presentación.
- **`herramientas/integrar_investigacion.py`:** las 12 tablas en `DOMINIO`. Volver a correrlo sobre la 0.1.2 no cambia
  ni un byte de las tablas previas (medido con `git status` antes y después).
- **`scripts/pruebas_buscar.py`:** +12 casos de relevancia (uno por tabla) y +7 comprobaciones del dominio: las 12
  tablas existen; contrato de las filas (prefijo de id, fuente con URL, puesto PRV, `[revisar]` fuera de la fecha) con
  su mutación; el filtro `--dominio` con su mutación; honestidad sin sentido; y la CLI. Un sondeo de 22 preguntas reales
  de presentación dio 22/22 con la tabla correcta en los 3 primeros.
- **`SKILL.md`:** descripción (906 caracteres, bajo el tope de 1.024), comando y tabla «Qué hay en la mochila».

**Arneses:** `pruebas_buscar.py` **76/76** · `pruebas_ids.py` **11/11** · `pruebas_clave_21st.js` **12/12**.

## 0.1.2 · 2026-09-25 · hallazgos del repaso de la 0.1.1 (MOC-4, MOC-5); P1 entera pendiente

**Huella (PRO-008):** `sha256 a03428b291ab8919c328b6133b2bb0abf9f4289919603f2bba510f39e668d150` · 244 ficheros
(estable en dos corridas). 0.1.1 cerró MOC-1..3 con APR-F0-005. Leonardo pidió la P1 ENTERA para esta versión.

- **MOC-4 · `--id` no traía la fila entera.** `presentar()` recortaba «Hacer» (200) y «Evitar» (160) también con
  `--id`/`--completo`, contra lo que promete este `SKILL.md`. Ahora con `completo` no se recorta nada; sin él, sí.
- **MOC-5 · DAT-027 sin exclusión parcial.** Lo halló la candidata al cruzar DAT-027 con RF-04/CA-04: una reserva
  liberada o cancelada que se queda en la tabla seguía ocupando la franja. **Curado por BD** con medición en
  PostgreSQL 17.10: `EXCLUDE … WHERE (estado NOT IN ('liberada','cancelada'))`, enumerando los estados que LIBERAN
  (un estado nuevo bloquea: fallo cerrado), `estado NOT NULL` + CHECK del vocabulario, y `now()` prohibido en el
  predicado (la liberación es un UPDATE). Misma fila, mismo id: es la misma regla bien escrita. Fuente añadida:
  `sql-createtable.html#SQL-CREATETABLE-EXCLUDE`.

**Arneses:** `pruebas_buscar.py` **57/57** · `pruebas_ids.py` **11/11** · `pruebas_clave_21st.js` **12/12**.

## 0.1.1 · 2026-09-25 · arreglos del examen (MOC-1, MOC-2, MOC-3); repaso de la P1 pendiente

**Huella (PRO-008):** `sha256 939666dfc06b9cd6a1a657907183b93d0d4e457eda3c743d87fd29590ac2e719` · 244 ficheros
(estable en dos corridas). Mismo método que la 0.1.0. Dependencias sin cambios.

- **MOC-1 · falsa ausencia.** Causa medida: con 2 términos tienen que coincidir los dos en UNA fila, y «education
  booking» mezcla dos productos. **El diagnóstico del examen era la mitad falso:** las palabras clave de PAL-009
  («educacion education») y PAL-104 («reserva booking») YA eran bilingües, así que no se tocaron. Arreglo: la regla
  estricta se conserva (es la que impide inventar) y la respuesta de ausencia añade «Por término suelto», con las filas
  de cada término y la advertencia de que no responden la consulta entera (`scripts/buscar.py`, `Indice.por_termino`).
  `SKILL.md`: reformular con 1 o 2 términos antes de declarar ausencia, y un punto nuevo en la lista de verificación.
- **MOC-2 · el borde no se medía.** `PAREJAS` mide ahora `borde` contra `fondo` a 3:1 (WCAG 1.4.11). Su fallo es
  **condicional** (`cumple_aa = condicional`, `⚠1.4.11`), no ✗AA: la norma solo obliga cuando el borde es el único
  límite del control. Los bordes translúcidos (`rgba`) se componen sobre el fondo antes de medir (`opaco()`). Aplica
  también a los temas de 21st (`integrar_21st.py`). Medido: **las 192 paletas quedan condicionales** (PAL-104 1,10:1 y
  PAL-009 1,33:1, iguales al examen); temas: 83 condicionales y 7 que cumplen. Comparado con la 0.1.0: solo cambian
  las filas de borde y las columnas `fallos_aa*`.
- **MOC-3 · hueco de RF-03.** Fila nueva **DAT-027** «Reservas sin solapes: restricción de exclusión por rangos»,
  **curada por BD** (F-08): aprobada con cambios tras ejecutar el SQL en PostgreSQL 17.10 desechable (NOT NULL y
  `CHECK (NOT isempty(franja))` cierran dos reservas dobles que el borrador dejaba pasar; concurrencia probada con dos
  sesiones; severidad Crítica, artefacto MIG CHK). Fuente: documentación de PostgreSQL, `#RANGETYPES-CONSTRAINT`.

**Arneses:** `pruebas_buscar.py` **54/54** (11 pruebas nuevas, con mutación que quita la orientación y controles
negativos) · `pruebas_ids.py` **11/11** · `pruebas_clave_21st.js` **12/12**.

## 0.1.0 · 2026-09-25 · construido; examen pendiente

**Huella (PRO-008):** `sha256 d1d313c2be1e48932043a86e4a2972f91a3f723ba3f1b5ca5294ca87c571ca1c` · 244 ficheros.
Se recalcula con `python herramientas/huella.py`; el método y las exclusiones (este fichero, el custodio `.mcp.json`
y `__pycache__/`) están en su cabecera. Control medido al fijarla: estable entre corridas, igual en una copia, y
**un byte cambiado en `datos/` cambia la huella**. Cualquier cambio en la carpeta es una versión nueva.

**Dependencias fijadas:**
- `ui-ux-pro-max` (MIT): hash de carpeta `f0415e89eeadda8933a49a3f432acae52fa542aa`, instalada el 2026-09-11. Es el
  hash anotado al derivar; no se recalculó con el método de arriba.
- 21st.dev: catálogo recolectado el 2026-09-25 con herramientas gratuitas (0 recuperaciones de código).
- Google Fonts: rev `038b637` (vía ui-ux-pro-max).

**Contenido:** front traducido desde ui-ux-pro-max (28 tablas fusionadas), 21st (componentes, plantillas y temas), y la
investigación web de backend, automatizaciones, librerías y rendimiento web. Procedencia y lo no verificado:
`FUENTES.md`.

**Arneses al fijar la versión:** `pruebas_buscar.py` **43/43** · `pruebas_ids.py` **11/11** ·
`pruebas_clave_21st.js` **12/12**. Los tres llevan control negativo por mutación.

**Decisiones de Leonardo incorporadas** (registradas en `leo-ingeniero/datos/decisiones.md`):
- **Custodia de la clave de 21st:** el Mochilero es su custodio oficial (`.mcp.json` propio, lectura única en
  `clave_21st.js`, MCP global por `headersHelper`). SIGAF conserva su copia hasta que consuma al Mochilero.
- **Ids estables (hallazgo 4, opción A):** `datos/ids/` con 32 mapas sembrados. La siembra reprodujo byte a byte
  los ids anteriores: `datos/`, `pendiente/`, `borrador/` y `huellas/` salieron idénticos a la copia previa.

**Revisión de Leo Ingeniero:** hallazgos 1, 2, 3, 4 y 5 resueltos; el 6, en parte (`fusionar` solo aplica los
campos pedidos y la fecha dejó de ir fija).
