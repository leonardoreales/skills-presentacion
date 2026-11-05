#!/usr/bin/env node
// Crea la carpeta de una presentación viva a partir del andamiaje. Sin dependencias.
// Uso: node nueva-presentacion.mjs <carpeta-destino> [--titulo "…"] [--perfil americana] [--video] [--forzar]
//   --perfil americana  aplica colores, tipografía y escudo del perfil de la Corporación Universitaria Americana
//   --video             copia también la parte de proyecto del motor de video a <destino>/video/src
//   --forzar            sobrescribe un index.html existente (por defecto se niega, para no pisar trabajo)
import { readFileSync, writeFileSync, mkdirSync, existsSync, copyFileSync, readdirSync } from 'node:fs';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const SKILL = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const opt = n => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : null; };
const flag = n => args.includes(n);
const conValor = new Set(['--titulo', '--perfil']);
const dest = args.find((a, i) => !a.startsWith('--') && !conValor.has(args[i - 1]));
if (!dest) { console.error('Uso: node nueva-presentacion.mjs <carpeta> [--titulo "…"] [--perfil americana] [--video] [--forzar]'); process.exit(2); }

const out = resolve(dest);
const idx = join(out, 'index.html');
if (existsSync(idx) && !flag('--forzar')) { console.error('Ya existe ' + idx + ' (usa --forzar para sobrescribir).'); process.exit(1); }
mkdirSync(join(out, 'media'), { recursive: true });

let html = readFileSync(join(SKILL, 'assets', 'andamiaje', 'index.html'), 'utf8');
const titulo = opt('--titulo');
if (titulo) html = html.replace('<title>Título de la presentación</title>', '<title>' + titulo.replace(/</g, '&lt;') + '</title>');

const perfil = opt('--perfil');
if (perfil) {
  if (perfil !== 'americana') { console.error('Perfil desconocido: ' + perfil + ' (disponible: americana)'); process.exit(2); }
  const tokens = {
    '--bg:#16181C; --bg-2:#1E2127; --line:#353A44;': '--bg:#0E1F35; --bg-2:#142943; --line:#2A4570;',
    '--ink:#F2F3F5; --mute:#A9AFBB;': '--ink:#F4F7FB; --mute:#AFC0D8;',
    '--accent:#D9A441; --accent-hi:#EBC77E; --accent-rgb:217,164,65;': '--accent:#B68D40; --accent-hi:#DDBD78; --accent-rgb:182,141,64;',
    '--display:Georgia, "Times New Roman", serif;': '--display:"Libre Baskerville", Georgia, "Times New Roman", serif;',
    '--body:"Segoe UI", system-ui, -apple-system, sans-serif;': '--body:"Source Sans 3", "Segoe UI", system-ui, sans-serif;'
  };
  for (const [a, b] of Object.entries(tokens)) {
    if (!html.includes(a)) { console.error('El andamiaje cambió y no encuentro: ' + a); process.exit(1); }
    html = html.replace(a, b);
  }
  html = html.replace('<title>',
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Source+Sans+3:wght@400;600;700&display=swap">\n<title>');
  // Primero el escudo del repo de origen; si no está (otra máquina, la nube), la copia que viaja con la skill.
  const escudo = ['C:\\Users\\Leonardo Reales\\cua-mantenimiento\\apps\\web\\public\\logo-americana.png',
    join(SKILL, 'assets', 'marca', 'escudo.png')].find(p => existsSync(p)) || join(SKILL, 'assets', 'marca', 'escudo.png');
  if (existsSync(escudo)) {
    copyFileSync(escudo, join(out, 'media', 'escudo.png'));
    html = html.replace('<!-- <img src="media/marca.png" alt=""> -->Marca', '<img src="media/escudo.png" alt="">Corporación Universitaria Americana');
  } else console.warn('AVISO: no encontré el escudo en ' + escudo + '; la franja queda con «Marca».');
}
writeFileSync(idx, html, 'utf8');
console.log('Creado ' + idx);

if (flag('--video')) {
  const src = join(SKILL, 'assets', 'motor-video'), vd = join(out, 'video', 'src');
  mkdirSync(vd, { recursive: true });
  // Solo lo que es del proyecto (motor.js, comun.css y los flujos de ejemplo): render.js y sus dependencias viven
  // instalados una vez por máquina (scripts/motor.mjs preparar).
  for (const f of readdirSync(src)) if (!['node_modules', 'render.js', 'package.json'].includes(f)) copyFileSync(join(src, f), join(vd, f));
  console.log('Flujos en ' + vd + '. Motor: node "' + join(SKILL, 'scripts', 'motor.mjs') + '" preparar (una vez por máquina).');
  console.log('Escribe el guion de cada flujo y genera su esqueleto con scripts/nuevo-flujo.mjs; ver references/gramatica-del-flujo.md');
}
console.log('Siguiente: borra la escena de humo, escribe los capítulos del arco y verifica con scripts/verificar.mjs.');
