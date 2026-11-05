#!/usr/bin/env node
// Revisión de una presentación en UNA pasada, con un informe y dos mosaicos para mirar.
//
//   node revisar.mjs <carpeta-de-la-presentación> [--vetar "a,b"]
//
// Sustituye a las decenas de comprobaciones sueltas (y al verificador propio que cada presentación se escribía):
//  1. verificar.mjs de la skill sobre index.html y cada flujo-*.html (estático);
//  2. la página a 1440 px, a 375 px y con movimiento reducido: errores de consola, desborde horizontal, imágenes
//     rotas, letra mínima visible, y elementos que con movimiento reducido quedan invisibles (no en su estado final);
//  3. términos vetados en los ficheros de texto, node_modules, _tmp o _fotogramas olvidados, y cada MP4 con ffprobe;
//  4. _revision/mosaico-1440.png y mosaico-375.png: la página entera recorrida por pantallas, en dos imágenes.
// Escribe _revision/revision.json y termina con 1 si algo FALLA. Mirar los dos mosaicos sigue siendo
// obligatorio: la máquina mide, el juicio visual es de quien revisa.
import { createRequire } from 'node:module';
import { execFileSync, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { estado } from './motor.mjs';

const USO = 'uso: node revisar.mjs <carpeta-de-la-presentación> [--vetar "a,b"]';
const args = process.argv.slice(2);
const opt = n => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : null; };
const dest = args.find((a, i) => !a.startsWith('--') && args[i - 1] !== '--vetar');
if (!dest || !fs.existsSync(dest) || !fs.statSync(dest).isDirectory()) { console.error(USO); process.exit(2); }
const OUT = path.resolve(dest);
// Sin --vetar no se veta nada: los términos son de cada perfil (p. ej. perfil-institucional-americana.md).
const VETADOS = (opt('--vetar') || '').split(',').map(s => s.trim()).filter(Boolean);
const VERIFICAR = path.join(path.dirname(fileURLToPath(import.meta.url)), 'verificar.mjs');

// playwright-core y Chromium salen del motor instalado una vez (motor.mjs): sin npm install por presentación.
const motor = estado();
if (!motor.listo) { console.error('Motor no listo. Falta: ' + motor.falta.join(' · ')); process.exit(2); }
const { chromium } = createRequire(path.join(motor.dir, 'render.js'))('playwright-core');

// Todo lo que produce la revisión va a _revision/ (junto a los --stills): una sola carpeta de trabajo que no se
// publica y que no se revisa a sí misma (revision.json repite los términos vetados que encontró).
const REV = path.join(OUT, '_revision');
const inf = { carpeta: OUT, fallos: [], avisos: [], hechos: {} };
const falla = m => inf.fallos.push(m), avisa = m => inf.avisos.push(m);
const recorrer = (d, f = []) => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name);
  if (e.isDirectory()) { if (e.name === 'node_modules') f.push(p); else if (!['.git', '_revision'].includes(e.name)) recorrer(p, f); }
  else f.push(p); } return f; };
const todos = recorrer(OUT);

// 1. estático
const htmls = todos.filter(f => /(^|[\\/])(index|flujo-[^\\/]*)\.html$/.test(f));
inf.hechos.verificar = {};
for (const h of htmls) {
  const r = spawnSync(process.execPath, [VERIFICAR, h, ...(VETADOS.length ? ['--vetar', VETADOS.join(',')] : [])], { encoding: 'utf8' });
  const lineas = (r.stdout || '').split(/\r?\n/).filter(l => /^(FALLA|AVISO)|PASA ·|FALLA ·/.test(l));
  inf.hechos.verificar[path.relative(OUT, h)] = { exit: r.status, lineas };
  if (r.status !== 0) falla(`verificar.mjs ${path.relative(OUT, h)}: ${lineas.filter(l => l.startsWith('FALLA')).join(' | ')}`);
}

// 3. ficheros: vetados, restos, videos
const texto = todos.filter(f => /\.(html|md|txt|vtt|json|svg|js|css|mjs)$/i.test(f) && !f.includes('node_modules'));
const sinTildes = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
inf.hechos.vetados = [];
for (const f of texto) {
  // las URL de CDN no cuentan: «claude» o «codex» pueden aparecer en una ruta ajena
  const t = sinTildes(fs.readFileSync(f, 'utf8')).replace(/https?:\/\/\S+/g, '');
  for (const v of VETADOS) if (t.includes(sinTildes(v))) inf.hechos.vetados.push(`${path.relative(OUT, f)}: «${v}»`);
}
if (inf.hechos.vetados.length) falla('términos vetados: ' + inf.hechos.vetados.join(', '));
const restos = todos.filter(f => /[\\/](node_modules|_tmp|_fotogramas)([\\/]|$)/.test(f));
if (restos.length) falla(`quedan temporales: ${[...new Set(restos.map(f => path.relative(OUT, f).split(/[\\/]/).slice(0, 2).join('/')))].join(', ')}`);
inf.hechos.mp4 = {};
for (const v of todos.filter(f => f.endsWith('.mp4'))) {
  try {
    const [w, h, d] = execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height:format=duration',
      '-of', 'csv=p=0:nk=1', v], { encoding: 'utf8' }).split(/[\r\n,]+/).filter(Boolean).map(Number);
    inf.hechos.mp4[path.relative(OUT, v)] = { w, h, s: Math.round(d * 10) / 10, mb: Math.round(fs.statSync(v).size / 1e5) / 10 };
    if (w !== 1920 || h !== 1080) avisa(`${path.relative(OUT, v)} es ${w}×${h}, no 1920×1080`);
  } catch { falla(`ffprobe no pudo leer ${path.relative(OUT, v)}`); }
}

// 2 y 4. navegador: una sola instancia, tres contextos
const indice = path.join(OUT, 'index.html');
if (fs.existsSync(indice)) {
  fs.mkdirSync(REV, { recursive: true });
  const nav = await chromium.launch({ executablePath: motor.chromium });
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'revision-'));
  inf.hechos.pagina = {};
  try { for (const [clave, w, h, reducido] of [['w1440', 1440, 900, false], ['w375', 375, 812, false], ['reduce', 1440, 900, true]]) {
    const ctx = await nav.newContext({ viewport: { width: w, height: h }, reducedMotion: reducido ? 'reduce' : 'no-preference' });
    const p = await ctx.newPage(); const errores = [];
    p.on('console', m => { if (m.type() === 'error') errores.push(m.text().slice(0, 160)); });
    p.on('pageerror', e => errores.push('pageerror: ' + String(e).slice(0, 160)));
    await p.goto(pathToFileURL(indice).href, { waitUntil: 'load', timeout: 30000 });
    await p.evaluate(() => document.fonts.ready.then(() => true));
    const alto = await p.evaluate(() => document.documentElement.scrollHeight);
    const capturas = [];
    for (let y = 0, i = 0; y < alto; y += h, i++) {
      await p.evaluate(yy => window.scrollTo(0, yy), y);
      await p.waitForTimeout(reducido ? 50 : 900); // deja correr la escena que se dispara al entrar (no en reduce)
      if (!reducido) { const f = path.join(tmp, `${clave}-${String(i).padStart(2, '0')}.png`); await p.screenshot({ path: f }); capturas.push(f); }
    }
    const m = await p.evaluate(() => {
      // texto que de verdad se ve: ni oculto, ni transparente, ni recortado a 1 px (sr-only)
      const visibles = [...document.querySelectorAll('body *')].filter(e => {
        const r = e.getBoundingClientRect(), s = getComputedStyle(e);
        return r.width > 1 && r.height > 1 && s.visibility !== 'hidden' && s.opacity !== '0' &&
          [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
      });
      const minLetra = Math.min(...visibles.map(e => parseFloat(getComputedStyle(e).fontSize)).filter(Boolean));
      const rotas = [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src'));
      // en estado final no debe quedar nada de una escena (figure.escena del andamiaje) escondido por la animación
      const ocultos = [...document.querySelectorAll('.escena *')].filter(e => {
        const s = getComputedStyle(e); return (s.opacity === '0' || s.visibility === 'hidden') && !e.closest('[aria-hidden="true"],defs,clipPath,mask');
      }).length;
      return { desborde: document.documentElement.scrollWidth - window.innerWidth, minLetra, rotas, ocultos };
    });
    inf.hechos.pagina[clave] = { errores, ...m, pantallas: Math.ceil(alto / h) };
    if (errores.length) falla(`${clave}: ${errores.length} errores de consola (${errores[0]})`);
    if (m.desborde > 0) falla(`${clave}: desborde horizontal de ${m.desborde} px`);
    if (m.rotas.length) falla(`${clave}: imágenes rotas ${m.rotas.join(', ')}`);
    if (clave === 'w375' && m.minLetra < 12) avisa(`375 px: letra mínima visible ${m.minLetra}px (< 12)`);
    if (clave === 'reduce' && m.ocultos > 0) avisa(`movimiento reducido: ${m.ocultos} elementos de escena siguen ocultos (¿no quedan en su estado final?)`);
    if (capturas.length) {
      const cols = clave === 'w375' ? 6 : 3, ancho = clave === 'w375' ? 250 : 640;
      const mosaico = path.join(REV, `mosaico-${clave.slice(1)}.png`);
      execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', path.join(tmp, `${clave}-%02d.png`), '-vf',
        `scale=${ancho}:-1,pad=iw+8:ih+8:4:4:color=white,tile=${cols}x${Math.ceil(capturas.length / cols)}`, '-frames:v', '1', mosaico]);
      inf.hechos.pagina[clave].mosaico = path.relative(OUT, mosaico);
    }
    await ctx.close();
  } } finally {
    await nav.close();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
}

inf.veredicto = inf.fallos.length ? 'FALLA' : 'PASA';
fs.mkdirSync(REV, { recursive: true });
fs.writeFileSync(path.join(REV, 'revision.json'), JSON.stringify(inf, null, 1));
for (const f of inf.fallos) console.log('FALLA  ' + f);
for (const a of inf.avisos) console.log('AVISO  ' + a);
console.log(`${inf.veredicto} · ${inf.fallos.length} fallo(s) · ${inf.avisos.length} aviso(s) · _revision/revision.json` +
  (inf.hechos.pagina ? ' · mira _revision/mosaico-1440.png y mosaico-375.png enteros' : ''));
process.exit(inf.fallos.length ? 1 : 0);
