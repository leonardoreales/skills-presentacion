# skills-presentacion

Dos skills para Claude Code que trabajan juntas:

| Skill | Para qué |
|---|---|
| `presentacion-viva` | Convierte cualquier tema en una página viva con scroll y escenas animadas (GSAP), y en **videos de flujo** deterministas en MP4: un objeto que viaja de etapa en etapa por un camino SVG. |
| `mochilero` | Biblioteca técnica verificada y con fuente (front, backend, automatizaciones y presentaciones). Se consulta con su buscador; presentacion-viva la usa como bolsillo. |

## Instalar

Dentro de Claude Code (terminal, app de escritorio o VS Code):

```
/plugin marketplace add leonardoreales/skills-presentacion
/plugin install skills-presentacion@skills-presentacion
```

Reinicia Claude Code. Para actualizar más adelante:

```
/plugin marketplace update skills-presentacion
```

## Requisitos

- **Python 3.10+**: lo usa el buscador del Mochilero.
- **Node.js 18+**: lo usan los scripts de presentacion-viva.
- Solo para renderizar videos MP4: Chromium de Playwright y ffmpeg. La skill te guía la primera vez
  (`node scripts/motor.mjs estado`).

## Probar

Pídele a Claude algo como: «hazme una presentación viva sobre el proceso de compras, con un video del flujo».

## Notas

- Las funciones del Mochilero que consultan 21st.dev necesitan una clave propia de 21st.dev. Son opcionales.
- `--perfil americana` aplica la identidad visual de la Corporación Universitaria Americana; sin esa opción,
  la skill deriva la identidad del tema.

Versión 0.6.0.
