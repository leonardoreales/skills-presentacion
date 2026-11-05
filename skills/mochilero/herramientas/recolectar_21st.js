// Recolecta el CATÁLOGO de 21st.dev para el Mochilero (decisión M-9: metadatos, no código).
// Usa solo herramientas gratuitas: search y get_theme. NUNCA llama a get_component (2 recuperaciones al día).
//
//   node recolectar_21st.js [dir salida]
//
// La clave la entrega el custodio del Mochilero (clave_21st.js): no depende de SIGAF.
// Jamás se imprime ni se escribe en la salida; todo mensaje de error pasa por ocultar().
const fs = require("fs");
const path = require("path");
const { leerClave, ocultar } = require("./clave_21st");

const [salidaArg] = process.argv.slice(2);
let key;
try { key = leerClave(); }
catch (e) { console.error(ocultar(e.message, key)); process.exit(2); }
const SALIDA = salidaArg || path.join(__dirname, "..", "trabajo", "21st");
fs.mkdirSync(SALIDA, { recursive: true });

async function llamar(tool, args, intento = 1) {
  try { return await llamarUnaVez(tool, args); }
  catch (e) {
    if (intento >= 3) throw e;
    await pausa(1500 * intento);
    return llamar(tool, args, intento + 1);
  }
}

async function llamarUnaVez(tool, args) {
  const r = await fetch("https://21st.dev/api/mcp", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json, text/event-stream",
      "MCP-Protocol-Version": "2025-06-18", "x-api-key": key },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/call", params: { name: tool, arguments: args } }),
  });
  let t = await r.text();
  const m = t.match(/^data: (.*)$/m); if (m) t = m[1];
  const j = JSON.parse(t);
  if (j.error) throw new Error(`${tool}: ${JSON.stringify(j.error).slice(0, 200)}`);
  return j.result.structuredContent || j.result;
}
const pausa = ms => new Promise(r => setTimeout(r, ms));

// Género en español → consulta en inglés. El género es la clave con la que busca el Mochilero.
const GENEROS = {
  "hero": "hero section", "barra de navegación": "navbar header", "barra lateral": "sidebar navigation",
  "pie de página": "footer", "precios": "pricing table", "testimonios": "testimonials",
  "sección de características": "features section", "bento": "bento grid", "llamada a la acción": "call to action cta",
  "preguntas frecuentes": "faq accordion", "dashboard": "dashboard layout", "tabla de datos": "data table",
  "formulario": "form", "inicio de sesión": "login sign in", "registro": "sign up", "modal": "modal dialog",
  "panel deslizante": "drawer sheet", "pestañas": "tabs", "paleta de comandos": "command palette",
  "menú desplegable": "dropdown menu", "notificación toast": "toast notification", "tooltip": "tooltip",
  "selector de fecha": "date picker", "subida de archivos": "file upload", "formulario por pasos": "multi step form stepper",
  "paginación": "pagination", "migas de pan": "breadcrumb", "avatar": "avatar", "insignia": "badge",
  "tarjeta": "card", "estado vacío": "empty state", "esqueleto de carga": "skeleton loader", "indicador de carga": "spinner loader",
  "barra de progreso": "progress bar", "gráfica": "chart", "kanban": "kanban board", "calendario": "calendar",
  "chat": "chat interface", "carrusel": "carousel", "galería": "image gallery", "línea de tiempo": "timeline",
  "árbol de archivos": "file tree", "dock": "dock", "buscador": "search bar", "ajustes": "settings page",
  "perfil": "profile page", "onboarding": "onboarding", "página 404": "404 page", "contacto": "contact form",
  "equipo": "team section", "nube de logos": "logo cloud", "métricas": "stats metrics", "comparativa": "comparison table",
  "mega menú": "mega menu", "navegación inferior móvil": "bottom navigation mobile", "cambio de tema": "theme toggle dark mode",
  "bloque de código": "code block", "editor de texto enriquecido": "rich text editor", "selector de color": "color picker",
  "deslizador": "slider range", "interruptor": "switch toggle", "valoración": "rating stars", "mapa": "map",
  "reproductor de vídeo": "video player", "checkout": "checkout", "tarjeta de producto": "product card",
  "carrito": "shopping cart", "fondo animado": "animated background", "animación de texto": "text animation",
  "animación al hacer scroll": "scroll animation", "botón": "button", "input": "input field", "select": "select combobox",
  "tabla de precios con conmutador": "pricing toggle monthly yearly", "aviso de cookies": "cookie consent banner",
  "banner de anuncio": "announcement banner", "lista de tareas": "todo list", "notificaciones": "notification center",
};
const PLANTILLAS = ["saas landing", "dashboard admin", "portfolio", "ecommerce store", "blog", "documentation docs",
  "agency", "startup", "ai app", "mobile app landing"];
const COLORES_TEMA = ["blue", "violet", "green", "orange", "red", "neutral", "rose", "yellow", "teal", "pink"];

(async () => {
  const componentes = {}, plantillas = {}, temas = {};
  let n = 0;
  for (const [genero, q] of Object.entries(GENEROS)) {
    try {
      const r = await llamar("search", { query: q, type: "component", limit: 10 });
      for (const it of r.results || []) {
        const k = String(it.id);
        if (!componentes[k]) componentes[k] = { ...it, generos: [genero], consulta: q };
        else if (!componentes[k].generos.includes(genero)) componentes[k].generos.push(genero);
      }
      n++;
    } catch (e) { console.error("fallo", genero, ocultar(e.message, key)); }
    await pausa(250);
  }
  for (const q of PLANTILLAS) {
    try {
      const r = await llamar("search", { query: q, type: "template", limit: 10 });
      for (const it of r.results || []) plantillas[String(it.id)] = { ...it, consulta: q };
    } catch (e) { console.error("fallo plantilla", q, ocultar(e.message, key)); }
    await pausa(250);
  }
  for (const color of COLORES_TEMA) {
    try {
      // Medido: el filtro `color` junto a la consulta devuelve casi nada; la consulta por el nombre del color, sí.
      const r = await llamar("search", { query: color, type: "theme", limit: 6 });
      for (const it of r.results || []) if (!temas[it.id]) temas[it.id] = { ...it, color };
    } catch (e) { console.error("fallo tema", color, ocultar(e.message, key)); }
    await pausa(250);
  }
  for (const id of Object.keys(temas)) {
    try { temas[id].css = await llamar("get_theme", { id }); } catch (e) { console.error("fallo get_theme", id, ocultar(e.message, key)); }
    await pausa(250);
  }
  fs.writeFileSync(path.join(SALIDA, "componentes.json"), JSON.stringify(Object.values(componentes), null, 1));
  fs.writeFileSync(path.join(SALIDA, "plantillas.json"), JSON.stringify(Object.values(plantillas), null, 1));
  fs.writeFileSync(path.join(SALIDA, "temas.json"), JSON.stringify(Object.values(temas), null, 1));
  const uso = await llamar("get_usage", {});
  console.log(`consultas de género: ${n}/${Object.keys(GENEROS).length} · componentes únicos: ${Object.keys(componentes).length}`
    + ` · plantillas: ${Object.keys(plantillas).length} · temas: ${Object.keys(temas).length}`
    + ` · recuperaciones de código que quedan: ${uso.freeRetrievalsRemaining}/${uso.freeRetrievalsPerDay}`);
})().catch(e => { console.error("ERROR", ocultar(e.message, key)); process.exit(1); });
