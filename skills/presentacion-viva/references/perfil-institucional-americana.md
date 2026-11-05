# Perfil institucional: Corporación Universitaria Americana

Opcional. Se aplica solo cuando la presentación es de la Americana (Dirección Administrativa u otra dependencia).
Para otra organización, se escribe un perfil hermano con la misma estructura y se deja este intacto.

## Colores y tipografía (sustituyen los VALORES de `:root` del andamiaje, no los nombres)

| Token del andamiaje | Americana | Uso |
|---|---|---|
| `--bg` | `#0E1F35` | azul institucional, fondo |
| `--bg-2` | `#142943` | azul de bandas alternas y escenas (realce: `#1C3557`) |
| `--line` | `#2A4570` | líneas y bordes |
| `--ink` / `--mute` | `#F4F7FB` / `#AFC0D8` | texto y texto suave |
| `--accent` / `--accent-rgb` | `#B68D40` / `182,141,64` | dorado |
| `--accent-hi` | `#DDBD78` (la página de 2026 usó `#D6B06A`) | dorado claro, rótulos de escena |
| `--display` | `"Libre Baskerville", Georgia, serif` | títulos (Google Fonts) |
| `--body` | `"Source Sans 3", "Segoe UI", sans-serif` | texto (Google Fonts) |

Para documentos dentro de escenas se usó `#1F3A60` con borde `#3C5D8C`; para el «antes» en papel, fondo `#E6E1D8`
con tinta `#2E3544`. Este perfil fija la identidad, no las escenas: el protocolo creativo sigue aplicando.

## Escudo y logo

- Escudo dorado: `C:\Users\Leonardo Reales\cua-mantenimiento\apps\web\public\logo-americana.png`. Se copia a
  `media/escudo.png` de la presentación: `<img src="media/escudo.png" alt="">` en la `.marca` de la franja, y
  `<image href="media/escudo.png" …>` dentro de los SVG.
- Logo completo en dorado (ya usado): `C:\Users\Leonardo Reales\informe-direccion-administrativa\presentacion\media\logo-completo.png`,
  con alt «Americana, Corporación Universitaria. Vigilada MinEducación».
- Si esas rutas no existen (otra máquina o claude.ai), las dos piezas viajan con la skill:
  `assets/marca/escudo.png` y `assets/marca/logo-completo.png`.
- Al publicar como Artifact, las imágenes van en `files` y tienen que estar dentro del directorio de trabajo.

## Reglas de lenguaje (de Leo)

- Nunca «en casa» ni «hecho en casa»: se dice **«desarrollado desde la institución»**.
- No se nombra a personas ni a herramientas de IA (Claude, Claude Code, Codex…) como autores. El relato de
  construcción es: la institución creó **agentes de IA especializados por capa** (requerimientos, arquitectura,
  módulos, contratos/API, datos, experiencia, calidad y seguridad, coordinación) y **agentes que traducen el lenguaje
  natural del área a requerimientos oficiales (ERS ISO 29148)**. **El área decide y aprueba.**
  Esa lista de capas es **vocabulario interno**: en una página para un público no técnico las capas se escriben en
  palabras llanas («contratos/API» → «acuerdos entre sistemas», «arquitectura» → «cómo encajan las piezas»), nunca
  con la sigla.
- **Sin jerga técnica visible** cuando la audiencia no es técnica o el pedido dice «sin entrar en lo técnico»: ni en
  texto, rótulos, alternativas en texto ni leyendas de las escenas y los videos. Fuera: API, endpoint, framework, base
  de datos, backend, front, y los nombres de lenguajes, librerías o nubes (TypeScript, Hono, Drizzle, Cloudflare…).
  Se dice qué hace la pieza para la persona («guarda el historial de cada equipo»), no con qué está hecha. Los
  nombres de librerías en una `<script src>` no cuentan: no se ven.
- No se mencionan proyectos reservados. Hoy: el asistente conversacional de SIGAF y cualquier «IA dentro de SIGAF».
  Antes de cada presentación, pregunta a Leo si la lista cambió.
- Pocas cifras, todas con fuente y fecha; ningún dato personal (nombres, cédulas, correos) ni en capturas.
- Estados honestos: «En producción y en uso diario» solo si lo está; si no, «Demo funcional con datos ficticios».

## Grep de términos vetados para este perfil

```bash
node scripts/revisar.mjs presentacion --vetar "jarvis,en casa,hecho en casa,leonardo,claude,codex"
```
Debe dar cero coincidencias (salvo `claude` en una URL de CDN, que el andamiaje no tiene). `revisar.mjs` pasa la
lista a `verificar.mjs` en cada HTML y la busca además en todos los ficheros de texto de la carpeta (guiones,
alternativas en texto de los videos, notas).

**`notas.md` también es entregable:** no copies la cadena `--vetar "…"` ni los términos vetados en ella (ni al
contar la verificación: escribe «grep de vetados del perfil: 0 coincidencias»). El grep no distingue una cita de un
uso, y el cliente que abra `notas.md` lee la lista que se prohibió. Escribe `notas.md` **antes** de la última corrida
de `revisar.mjs`, para que esa corrida lo cubra.
