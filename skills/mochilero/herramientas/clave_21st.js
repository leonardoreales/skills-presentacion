// Custodia de la clave de 21st.dev. El Mochilero es su custodio oficial (decisión de Leo, 2026-09-25).
//
// Fuente, por orden:
//   1. la variable de entorno API_KEY_21ST, si existe;
//   2. el custodio: ../.mcp.json (mcpServers["21st"].headers["x-api-key"]).
// MOCHILERO_21ST_JSON cambia la ruta del custodio; solo la usa el arnés, con una clave falsa.
//
// Regla: ningún mensaje de este módulo contiene la clave ni el texto del fichero. Un JSON roto en Node 24
// muestra un trozo de lo que no pudo leer, por eso aquí nunca se reenvía e.message.
const fs = require("fs");
const path = require("path");

const CUSTODIO = path.join(__dirname, "..", ".mcp.json");

class ErrorClave21st extends Error {}

function leerClave() {
  const entorno = process.env.API_KEY_21ST;
  if (entorno && entorno.trim()) return entorno.trim();

  const ruta = process.env.MOCHILERO_21ST_JSON || CUSTODIO;
  let texto;
  try { texto = fs.readFileSync(ruta, "utf8"); }
  catch { throw new ErrorClave21st("No se encuentra el custodio de la clave de 21st (.mcp.json del Mochilero)."); }

  let clave;
  try { clave = JSON.parse(texto).mcpServers["21st"].headers["x-api-key"]; }
  catch { throw new ErrorClave21st("El custodio de la clave de 21st no es un .mcp.json válido con mcpServers.21st.headers.x-api-key."); }

  if (typeof clave !== "string" || !clave.trim()) {
    throw new ErrorClave21st("El custodio de 21st no trae la cabecera x-api-key.");
  }
  return clave.trim();
}

// Tapa la clave en cualquier texto antes de imprimirlo (mensajes de error de red, del servidor, etc.).
function ocultar(texto, clave) {
  const s = String(texto);
  return clave ? s.split(clave).join("[clave oculta]") : s;
}

module.exports = { leerClave, ocultar, ErrorClave21st, CUSTODIO };
