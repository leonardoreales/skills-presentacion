// headersHelper del MCP global de 21st: Claude Code lo ejecuta al conectar y lee de stdout un JSON con las
// cabeceras. La clave sale SOLO por stdout hacia Claude Code; los errores van a stderr y nunca la contienen.
const { leerClave, ErrorClave21st } = require("./clave_21st");

try {
  process.stdout.write(JSON.stringify({ "x-api-key": leerClave() }));
} catch (e) {
  console.error(e instanceof ErrorClave21st ? e.message : "No se pudo leer la clave de 21st.");
  process.exit(1);
}
