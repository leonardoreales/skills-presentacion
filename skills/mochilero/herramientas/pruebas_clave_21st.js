// Arnés de la custodia de la clave de 21st. Usa SOLO una clave FALSA en un directorio temporal:
// nunca lee el custodio real. Control negativo: un mutante que reenvía e.message debe filtrar la clave falsa.
//
//   node herramientas/pruebas_clave_21st.js
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const FALSA = "falsa-CLAVEDEPRUEBA-7f3a9c";
const AQUI = __dirname;
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "moc-21st-"));

const valido = JSON.stringify({ mcpServers: { "21st": { type: "http", url: "https://21st.dev/api/mcp", headers: { "x-api-key": FALSA } } } });
const ROTOS = {
  "sin comillas": `{"mcpServers":{"21st":{"headers":{"x-api-key": ${FALSA}}}}}`,
  "cortado": `{"mcpServers":{"21st":{"headers":{"x-api-key":"${FALSA}`,
  "basura al final": `${valido} ${FALSA}`,
  "comillas simples": `{'x-api-key': '${FALSA}'}`,
};

function fichero(nombre, contenido) {
  const r = path.join(tmp, nombre);
  fs.writeFileSync(r, contenido);
  return r;
}

function correr(script, env) {
  const e = { ...process.env, ...env };
  delete e.API_KEY_21ST;
  Object.assign(e, env);
  const r = spawnSync(process.execPath, [script], { env: e, encoding: "utf8", timeout: 10000 });
  return { codigo: r.status, out: r.stdout || "", err: r.stderr || "" };
}

let ok = 0, total = 0;
function caso(nombre, cond) {
  total++;
  if (cond) ok++;
  console.log(`${cond ? "✅" : "❌"} ${nombre}`);
}
// Medido en Node 24.16: V8 no imprime la clave entera, pero sí una ventana de ~14 caracteres alrededor del
// fallo («"falsa-CLAVEDEP"... is not valid JSON»). Por eso se busca CUALQUIER trozo de 6 caracteres de la clave.
const TROZOS = Array.from({ length: FALSA.length - 5 }, (_, i) => FALSA.slice(i, i + 6));
const limpio = (r) => !TROZOS.some((t) => r.out.includes(t) || r.err.includes(t));

const cabeceras = path.join(AQUI, "cabeceras_21st.js");
const recolectar = path.join(AQUI, "recolectar_21st.js");

// 1. Camino feliz: el helper entrega exactamente la cabecera.
let r = correr(cabeceras, { MOCHILERO_21ST_JSON: fichero("valido.json", valido) });
caso("custodio válido ⇒ stdout es {\"x-api-key\": <clave>} y exit 0",
  r.codigo === 0 && JSON.stringify(JSON.parse(r.out)) === JSON.stringify({ "x-api-key": FALSA }) && r.err === "");

// 2. Ningún fallo filtra la clave.
for (const [nombre, texto] of Object.entries(ROTOS)) {
  r = correr(cabeceras, { MOCHILERO_21ST_JSON: fichero(`roto-${nombre.replace(/ /g, "-")}.json`, texto) });
  caso(`JSON roto (${nombre}) ⇒ exit 1 y la clave no aparece`, r.codigo === 1 && limpio(r) && r.out === "");
}
r = correr(cabeceras, { MOCHILERO_21ST_JSON: path.join(tmp, "no-existe.json") });
caso("custodio ausente ⇒ exit 1 con mensaje genérico", r.codigo === 1 && r.err.includes("No se encuentra") && r.out === "");
r = correr(cabeceras, { MOCHILERO_21ST_JSON: fichero("sin-campo.json", JSON.stringify({ mcpServers: { "21st": { headers: {} } } })) });
caso("custodio sin x-api-key ⇒ exit 1", r.codigo === 1 && r.err.includes("x-api-key") && r.out === "");

// 3. La variable de entorno manda sobre el fichero.
r = correr(cabeceras, { MOCHILERO_21ST_JSON: path.join(tmp, "no-existe.json"), API_KEY_21ST: "de-entorno-123" });
caso("API_KEY_21ST manda sobre el custodio", r.codigo === 0 && JSON.parse(r.out)["x-api-key"] === "de-entorno-123");

// 4. El recolector no llega a la red con un custodio roto y no filtra la clave.
r = correr(recolectar, { MOCHILERO_21ST_JSON: fichero("roto-recolectar.json", ROTOS["sin comillas"]) });
caso("recolectar_21st.js con custodio roto ⇒ exit 2 sin la clave", r.codigo === 2 && limpio(r));

// 5. ocultar() tapa la clave.
const { ocultar } = require("./clave_21st");
caso("ocultar() tapa la clave en un mensaje", ocultar(`fallo con ${FALSA} dentro`, FALSA) === "fallo con [clave oculta] dentro");

// 6. Control negativo por mutación: si el módulo reenviara e.message, algún JSON roto filtraría la clave.
const mut = fs.mkdtempSync(path.join(os.tmpdir(), "moc-21st-mut-"));
const original = fs.readFileSync(path.join(AQUI, "clave_21st.js"), "utf8");
const ancla = 'catch { throw new ErrorClave21st("El custodio de la clave de 21st no es';
const mutante = original.replace(ancla, 'catch (e) { throw new ErrorClave21st(e.message || "El custodio de la clave de 21st no es');
caso("mutación aplicable (el ancla existe)", mutante !== original);
fs.writeFileSync(path.join(mut, "clave_21st.js"), mutante);
fs.copyFileSync(cabeceras, path.join(mut, "cabeceras_21st.js"));
let fugas = 0;
for (const [nombre, texto] of Object.entries(ROTOS)) {
  r = correr(path.join(mut, "cabeceras_21st.js"), { MOCHILERO_21ST_JSON: fichero(`mut-${nombre.replace(/ /g, "-")}.json`, texto) });
  if (!limpio(r)) fugas++;
}
caso(`mutante que reenvía e.message ⇒ el arnés detecta la fuga (${fugas} de ${Object.keys(ROTOS).length})`, fugas > 0);

fs.rmSync(tmp, { recursive: true, force: true });
fs.rmSync(mut, { recursive: true, force: true });
console.log(`\n${ok}/${total} ${ok === total ? "en verde" : "EN ROJO"}`);
process.exit(ok === total ? 0 : 1);
