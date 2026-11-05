# Brief de traducción y pulido · Mochilero

El Mochilero es una biblioteca técnica en **español** que consultan agentes de IA de una agencia de desarrollo, con un
buscador que devuelve filas sueltas. Su contenido de front viene de `ui-ux-pro-max` (licencia MIT) y hay que
**traducirlo y pulirlo**, no copiarlo tal cual.

## Entrada y salida

- **Entrada:** `trabajo/traduccion/pendiente/<tabla>.jsonl`. Una línea por fila:
  `{"id": "UX-001", "campos": {"categoria": "...", "tema": "...", ...}}`. Solo vienen los campos que hay que traducir.
- **Salida:** `trabajo/traduccion/hecho/<tabla>.parte1.jsonl`, `.parte2.jsonl`… con **el mismo formato, los mismos
  ids y exactamente los mismos nombres de campo**. Como máximo 60 filas por parte.
- Rutas absolutas: la raíz es `C:\Users\Leonardo Reales\.claude\skills\mochilero\`.
- Lee con la herramienta Read y escribe con Write. **Nunca heredoc de bash.** Una línea = un objeto JSON válido, UTF-8,
  sin comas finales.

## Reglas de traducción

1. **Español correcto con todas sus tildes y eñes.** Frases claras y directas, registro técnico profesional.
2. **No se traduce:** código, fragmentos CSS o JSX, nombres de clases y props, nombres de componentes, APIs,
   librerías, fuentes tipográficas, nombres propios de estilos (Glassmorphism, Neumorphism, Bento Grid…), unidades y
   números. Un término técnico asentado en inglés puede quedarse (hover, layout, CTA, viewport, easing), sin alternar
   entre inglés y español en la misma tabla.
3. **`palabras_clave` SIEMPRE se rellena, aunque venga vacío:** de 6 a 12 términos en minúscula, **sin tildes**,
   separados por espacios, **mezclando español e inglés**. Se conservan los términos ingleses originales (sin comas) y
   se añaden sus equivalentes en español. Ejemplo: `formulario form validacion validation error inline campo field`.
4. **Colores en prosa (regla F-08 de la agencia): el valor no se borra, pero se nombra su rol.** Se escribe
   `primario: azul (#0080FF)` en vez de `Primary: #0080FF`. Roles válidos: primario, secundario, acento, fondo, tinta,
   superficie, apagado, borde, destructivo, éxito, aviso.
5. **Pulir sin inventar:** corrige erratas y ambigüedades obvias y deja la frase más precisa, **sin cambiar el
   significado**. Si una fila te parece incorrecta u obsoleta, tradúcela igual y añade al final del campo más largo
   ` [revisar: <motivo en ≤ 12 palabras>]`.
6. **`severidad`, `intensidad`, `estado` y demás campos cortos ya traducidos no vienen en la entrada:** no los añadas.
7. **Una traducción por cada campo de cada id.** Si un campo de origen viene vacío y no es `palabras_clave`, devuélvelo
   vacío.

## Validación antes de terminar

Ejecuta, por cada tabla tuya:

```
python "<carpeta de la skill>/herramientas/derivar_uiuxpromax.py" validar <tabla> [<tabla>…]
```

Debe decir `válida` para cada una. Si dice `PENDIENTE`, corrige y repite. **No uses el modo `fusionar`:** lo ejecuta
la sesión principal.

## Respuesta final (≤ 10 líneas)

Las tablas validadas, el número de filas marcadas con `[revisar: …]` (con 3 ejemplos) y cualquier problema.
