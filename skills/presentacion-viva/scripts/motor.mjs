#!/usr/bin/env node
// El motor de video se instala UNA vez por máquina y renderiza los flujos en su sitio. Sin dependencias.
//
//   node motor.mjs estado                         → JSON con lo que hay (rápido; no instala nada)
//   node motor.mjs preparar                       → instala o actualiza el motor y comprueba el entorno (idempotente)
//   node motor.mjs render <carpeta-flujos> [id…] [--stills 2.8,6]   → render en sitio; salida en la carpeta padre
//
// La carpeta del proyecto solo lleva lo que es suyo: los flujo-*.html y sus copias de motor.js y comun.css (fijan
// la versión con la que se hizo el video). render.js, package.json y node_modules viven en
// ~/.presentacion-viva/motor-video/<huella>/, y la huella cambia si cambia el motor: nada de `npm install` por
// presentación ni de comprobar node, ffmpeg y Chromium a mano cada vez.
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
// Origen del motor: assets/motor-video de esta skill (o MOTOR_ORIGEN para probar otra copia).
const ORIGEN = path.resolve(process.env.MOTOR_ORIGEN || path.join(AQUI, '..', 'assets', 'motor-video'));
const BASE = path.join(os.homedir(), '.presentacion-viva', 'motor-video');
const PIEZAS = ['render.js', 'package.json']; // lo que se instala una vez; motor.js y comun.css van con cada proyecto

// Sin distinguir CRLF de LF: la misma versión del motor da la misma huella en una copia de git con autocrlf y en
// otra sin él (si no, cada copia reinstalaría el mismo motor).
function huella() {
  const h = createHash('sha256');
  for (const f of PIEZAS) h.update(f).update(fs.readFileSync(path.join(ORIGEN, f), 'utf8').replace(/\r\n/g, '\n'));
  return h.digest('hex').slice(0, 12);
}

function chromium() {
  if (process.env.CHROME_EXE) return fs.existsSync(process.env.CHROME_EXE) ? process.env.CHROME_EXE : '';
  const raices = [process.env.PLAYWRIGHT_BROWSERS_PATH,
    process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, 'ms-playwright'),
    path.join(os.homedir(), '.cache', 'ms-playwright'), path.join(os.homedir(), 'Library', 'Caches', 'ms-playwright')]
    .filter(Boolean);
  for (const r of raices) {
    if (!fs.existsSync(r)) continue;
    const dirs = fs.readdirSync(r).filter(d => d.startsWith('chromium_headless_shell-'))
      .sort((a, b) => Number(b.split('-')[1]) - Number(a.split('-')[1]));
    for (const d of dirs) for (const sub of fs.readdirSync(path.join(r, d)))
      for (const n of ['chrome-headless-shell.exe', 'chrome-headless-shell']) {
        const p = path.join(r, d, sub, n);
        if (fs.existsSync(p)) return p;
      }
  }
  return '';
}

function ejecutable(cmd, args) {
  const r = spawnSync(cmd, args, { encoding: 'utf8' }); // sin shell: los argumentos no se concatenan
  return r.status === 0 ? (r.stdout || r.stderr).split(/\r?\n/)[0].trim() : '';
}

const instalado = dir => fs.existsSync(path.join(dir, 'node_modules', 'playwright-core', 'package.json'));

export function estado() {
  const dir = path.join(BASE, huella());
  const e = {
    huella: path.basename(dir), dir, instalado: instalado(dir),
    node: process.version, node_ok: Number(process.versions.node.split('.')[0]) >= 18,
    ffmpeg: ejecutable('ffmpeg', ['-version']), chromium: chromium(),
  };
  e.listo = e.instalado && e.node_ok && !!e.ffmpeg && !!e.chromium;
  e.falta = [!e.node_ok && 'Node 18+', !e.ffmpeg && 'ffmpeg en el PATH', !e.chromium &&
    'Chromium headless: npx playwright@1.63.0 install chromium-headless-shell', !e.instalado && 'node motor.mjs preparar']
    .filter(Boolean);
  return e;
}

function preparar() {
  const dir = path.join(BASE, huella());
  if (!instalado(dir)) {
    // Cerrojo: dos `preparar` a la vez (p. ej. dos subagentes) harían dos `npm install` en la misma carpeta.
    // mkdir es atómico: el segundo falla en vez de pisar al primero.
    const cerrojo = dir + '.instalando';
    fs.mkdirSync(BASE, { recursive: true });
    try { fs.mkdirSync(cerrojo); } catch {
      throw new Error('Otra instalación del motor está en curso (' + cerrojo + '): espera y repite. Si no hay ninguna, borra esa carpeta.');
    }
    try {
      fs.mkdirSync(dir, { recursive: true });
      for (const f of PIEZAS) fs.copyFileSync(path.join(ORIGEN, f), path.join(dir, f));
      // npm es npm.cmd en Windows y necesita shell; la orden es fija, sin argumentos de fuera.
      const r = process.platform === 'win32'
        ? spawnSync('npm install --no-audit --no-fund --loglevel=error', { cwd: dir, stdio: 'inherit', shell: true })
        : spawnSync('npm', ['install', '--no-audit', '--no-fund', '--loglevel=error'], { cwd: dir, stdio: 'inherit' });
      if (r.status !== 0) throw new Error('npm install falló en ' + dir);
    } finally { fs.rmSync(cerrojo, { recursive: true, force: true }); }
  }
  const e = estado();
  fs.writeFileSync(path.join(BASE, 'entorno.json'), JSON.stringify({ ...e, comprobado: new Date().toISOString() }, null, 1));
  return e;
}

function render(src, resto) {
  const e = estado();
  if (!e.listo) { console.error('Motor no listo. Falta: ' + e.falta.join(' · ')); process.exit(2); }
  const carpeta = path.resolve(src);
  if (!fs.existsSync(carpeta) || !fs.readdirSync(carpeta).some(f => /^flujo-.*\.html$/.test(f))) {
    console.error('No hay flujo-*.html en ' + carpeta); process.exit(2);
  }
  // MOTOR_SRC: render.js lee los flujos de aquí y escribe en la carpeta padre, igual que si viviera dentro.
  const r = spawnSync(process.execPath, [path.join(e.dir, 'render.js'), ...resto],
    { stdio: 'inherit', env: { ...process.env, MOTOR_SRC: carpeta, CHROME_EXE: e.chromium } });
  if (r.error) console.error('No se pudo lanzar render.js: ' + r.error.message);
  process.exit(r.status ?? 1);
}

// Solo como orden: revisar.mjs importa estado() sin disparar nada. Se compara la ruta real (enlaces resueltos y,
// en Windows, sin distinguir mayúsculas: «c:\» y «C:\» son la misma unidad).
const real = p => { const r = fs.realpathSync(p); return process.platform === 'win32' ? r.toLowerCase() : r; };
if (process.argv[1] && fs.existsSync(process.argv[1]) && real(process.argv[1]) === real(fileURLToPath(import.meta.url))) {
  const [orden, ...args] = process.argv.slice(2);
  if (orden === 'estado') console.log(JSON.stringify(estado(), null, 1));
  else if (orden === 'preparar') { const e = preparar(); console.log(e.listo ? 'LISTO ' + e.huella : 'FALTA: ' + e.falta.join(' · ')); }
  else if (orden === 'render' && args[0]) render(args[0], args.slice(1));
  else { console.error('uso: node motor.mjs estado | preparar | render <carpeta-flujos> [id…] [--stills t1,t2]'); process.exit(2); }
}
