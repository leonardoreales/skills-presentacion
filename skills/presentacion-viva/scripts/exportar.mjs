#!/usr/bin/env node
// Exporta una presentación viva a DOS ficheros sueltos, listos para mandar: un HTML AUTOCONTENIDO (imágenes, videos,
// librerías y fuentes embebidos: funciona sin internet) y un PDF horizontal, un capítulo por página. Y PRUEBA el HTML
// sin red (toda petición http bloqueada, a 375 px): si algo de fuera quedó sin embeber, lo dice.
//
//   node exportar.mjs <carpeta> --nombre "Mi-Presentacion" [--destino <dir>] [--css-impresa extra.css] [--captura]
//
// · Destino por defecto: Descargas del usuario.
// · En el PDF cada <video> de un flujo se sustituye por su hoja de contactos (video/hoja-flujo-N.png, o la que diga
//   data-hoja en el <video>), y la sala de pestañas por las hojas de todos sus flujos: el papel no reproduce video.
// · --css-impresa añade CSS propio de la variante impresa (p. ej. compactar un capítulo que no cabe en 900 px).
// · --captura deja _revision/impresa.png (la variante impresa entera) para MIRARLA: aquí no siempre hay con qué
//   rasterizar el PDF, y un capítulo cortado en el papel solo se ve mirando (medido 2026-10-30).
// Nació de la guía de traslado de activos (2026-10-30): el exportador se escribía a mano en cada encargo.
import { createRequire } from 'node:module';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { estado } from './motor.mjs';

const USO = 'uso: node exportar.mjs <carpeta> --nombre "Nombre" [--destino <dir>] [--css-impresa f.css] [--captura]';
const args = process.argv.slice(2);
const opt = n => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : null; };
const conValor = ['--nombre', '--destino', '--css-impresa'];
const dir = args.find((a, i) => !a.startsWith('--') && !conValor.includes(args[i - 1]));
const NOMBRE = opt('--nombre');
if (!dir || !NOMBRE || !fs.existsSync(path.join(dir, 'index.html'))) { console.error(USO); process.exit(2); }
const BASE = path.resolve(dir);
const DESTINO = path.resolve(opt('--destino') || path.join(os.homedir(), 'Downloads'));
const motor = estado();
if (!motor.listo) { console.error('Motor no listo. Falta: ' + motor.falta.join(' · ')); process.exit(2); }
const { chromium } = createRequire(path.join(motor.dir, 'render.js'))('playwright-core');

const TIPOS = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', webp: 'image/webp', avif: 'image/avif', svg: 'image/svg+xml',
  gif: 'image/gif', mp4: 'video/mp4', webm: 'video/webm', vtt: 'text/vtt', woff2: 'font/woff2' };
const dataUri = f => {
  const ext = path.extname(f).slice(1).toLowerCase();
  if (!TIPOS[ext]) throw new Error('Tipo sin MIME conocido: ' + f);
  return 'data:' + TIPOS[ext] + ';base64,' + fs.readFileSync(path.join(BASE, f)).toString('base64');
};
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36';
async function bajar(url, comoTexto) {
  const r = await fetch(url, { headers: { 'User-Agent': UA } });
  if (!r.ok) throw new Error(url + ' → ' + r.status);
  return comoTexto ? r.text() : Buffer.from(await r.arrayBuffer());
}

// 1 · Recursos locales: todo src/href/poster RELATIVO que apunte a un fichero existente se embebe. Los enlaces de
// navegación (http, mailto, #) se quedan: no se cargan, se siguen.
function embeberLocales(html) {
  return html.replace(/\b(src|href|poster|data-src|data-hoja)="([^"#:]+?)"/g, (m, attr, ruta) => {
    const f = ruta.replace(/^\.\//, '');
    if (!fs.existsSync(path.join(BASE, f)) || fs.statSync(path.join(BASE, f)).isDirectory() || /\.html?$/i.test(f)) return m;
    return attr + '="' + dataUri(f) + '"';
  });
}
// 2 · Externos: <script src="https…"> y la hoja de Google Fonts (solo latin y latin-ext: el español completo).
async function embeberExternos(html) {
  for (const m of [...html.matchAll(/<script src="(https:[^"]+)"><\/script>/g)]) {
    const js = (await bajar(m[1], true)).replace(/<\/script/gi, '<\\/script');
    html = html.replace(m[0], () => '<script>/* ' + m[1] + ' */\n' + js + '\n</script>');
  }
  for (const link of [...html.matchAll(/<link rel="stylesheet" href="(https:\/\/fonts\.googleapis\.com[^"]+)">/g)]) {
    const css = await bajar(link[1].replace(/&amp;/g, '&'), true);
    const bloques = [...css.matchAll(/\/\* ([\w-]+) \*\/\s*(@font-face\s*\{[^}]+\})/g)].filter(b => b[1] === 'latin' || b[1] === 'latin-ext');
    let fuentes = '';
    for (const b of bloques) {
      const url = b[2].match(/url\((https:[^)]+)\)/)[1];
      fuentes += b[2].replace(url, 'data:font/woff2;base64,' + (await bajar(url)).toString('base64')) + '\n';
    }
    html = html.replace(link[0], () => '<style>' + fuentes + '</style>');
  }
  return html.replace(/<link rel="preconnect"[^>]*>\s*/g, '');
}
// La hoja de contactos de un video: data-hoja explícito, o video/hoja-flujo-N.png por el número del MP4.
function hojaDe(mp4, explicita) {
  if (explicita) return explicita;
  const n = (mp4.match(/flujo-(\d+)/) || [])[1];
  const f = n && 'video/hoja-flujo-' + n + '.png';
  return f && fs.existsSync(path.join(BASE, f)) ? f : null;
}
const figura = (hoja, alt) => '<figure class="hojac"><img src="' + hoja + '" alt="' + alt + '"><figcaption>Fotogramas del video. ' +
  'La versión web lo reproduce animado.</figcaption></figure>';

(async () => {
  const fuente = fs.readFileSync(path.join(BASE, 'index.html'), 'utf8');
  // Variante impresa: se decide sobre el HTML con rutas (antes de embeber), para poder leer el nombre de cada MP4.
  let impresa = fuente
    .replace(/<div class="sala">[\s\S]*?<p class="frase"><\/p>\s*<\/div>/g, sala => {
      const hojas = [...sala.matchAll(/data-src="([^"]+)"[^>]*>([^<]+)</g)].map(m => [hojaDe(m[1]), m[2].trim()]).filter(h => h[0]);
      return hojas.map(h => figura(h[0], 'Fotogramas del video «' + h[1] + '»')).join('');
    })
    .replace(/<video\b[^>]*>[\s\S]*?<\/video>/g, v => {
      const src = (v.match(/src="([^"]+\.mp4)"/) || [])[1] || '', hoja = hojaDe(src, (v.match(/data-hoja="([^"]+)"/) || [])[1]);
      const alt = (v.match(/aria-label="([^"]+)"/) || [])[1] || 'Fotogramas del video';
      return hoja ? figura(hoja, alt) : '';
    })
    .replace(/<p class="pista">[\s\S]*?<\/p>/g, '')
    .replace('</style>', () => `
@page{size:1440px 900px;margin:0}
html,body{-webkit-print-color-adjust:exact;print-color-adjust:exact}
.franja{display:none}
.cap{min-height:900px;padding-block:48px;break-after:page;break-inside:avoid}
.cap:last-child{break-after:auto}
.hojac{margin:0}
.hojac img{display:block;width:100%;max-height:420px;object-fit:contain;border:1px solid var(--line)}
.hojac figcaption{color:var(--mute);font-size:14px;padding-top:8px}
` + (opt('--css-impresa') ? fs.readFileSync(path.resolve(opt('--css-impresa')), 'utf8') : '') + '\n</style>');

  const web = await embeberExternos(embeberLocales(fuente));
  impresa = await embeberExternos(embeberLocales(impresa));
  // Ningún recurso que se CARGA puede seguir fuera (los <a href> de navegación sí).
  for (const [n, h] of [['web', web], ['impresa', impresa]]) if (/\s(src|poster)="https?:|<link[^>]+href="https?:/.test(h)) throw new Error('Queda un recurso externo en la variante ' + n);
  fs.mkdirSync(DESTINO, { recursive: true });
  const rutaHtml = path.join(DESTINO, NOMBRE + '.html');
  fs.writeFileSync(rutaHtml, web, 'utf8');

  const tmp = path.join(BASE, '_impresa.html');
  fs.writeFileSync(tmp, impresa, 'utf8');
  const browser = await chromium.launch({ executablePath: motor.chromium });
  const errores = [];
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
    page.on('console', m => { if (m.type() === 'error') errores.push('impresa: ' + m.text()); });
    page.on('pageerror', e => errores.push('impresa: ' + e.message));
    await page.goto(pathToFileURL(tmp).href, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const rutaPdf = path.join(DESTINO, NOMBRE + '.pdf');
    await page.pdf({ path: rutaPdf, width: '1440px', height: '900px', printBackground: true, preferCSSPageSize: true });
    if (args.includes('--captura')) {
      await page.emulateMedia({ media: 'print' });
      fs.mkdirSync(path.join(BASE, '_revision'), { recursive: true });
      await page.screenshot({ path: path.join(BASE, '_revision', 'impresa.png'), fullPage: true });
    }
    const paginas = (fs.readFileSync(rutaPdf, 'latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;

    // Prueba SIN RED del HTML entregado, a 375 px: lo que no se embebió aparece aquí.
    const ctx = await browser.newContext({ viewport: { width: 375, height: 812 } });
    let bloqueadas = 0;
    await ctx.route(/^https?:/, r => { bloqueadas++; r.abort(); });
    const p2 = await ctx.newPage();
    p2.on('console', m => { if (m.type() === 'error') errores.push('sin red: ' + m.text()); });
    p2.on('pageerror', e => errores.push('sin red: ' + e.message));
    await p2.goto(pathToFileURL(rutaHtml).href, { waitUntil: 'load' });
    await p2.evaluate(() => document.fonts.ready);
    const sinRed = await p2.evaluate(async () => {
      const vids = [...document.querySelectorAll('video')];
      await Promise.all(vids.map(v => v.readyState >= 1 ? 0 : new Promise(ok => { v.addEventListener('loadedmetadata', ok, { once: true }); v.addEventListener('error', ok, { once: true }); setTimeout(ok, 8000); })));
      return {
        fuentes: [...new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family))],
        imagenesRotas: [...document.images].filter(i => !i.complete || i.naturalWidth === 0).map(i => i.alt || i.src.slice(0, 40)),
        videos: vids.map(v => Math.round(v.duration || 0)), desborde: document.documentElement.scrollWidth > innerWidth
      };
    });
    const mb = f => (fs.statSync(f).size / 1048576).toFixed(1) + ' MB';
    console.log('HTML  ' + rutaHtml + ' · ' + mb(rutaHtml));
    console.log('PDF   ' + rutaPdf + ' · ' + mb(rutaPdf) + ' · ' + paginas + ' páginas');
    console.log('SIN RED · peticiones bloqueadas ' + bloqueadas + ' · fuentes ' + (sinRed.fuentes.join(', ') || 'ninguna web') +
      ' · imágenes rotas ' + sinRed.imagenesRotas.length + ' · videos (s) ' + (sinRed.videos.join(', ') || '—') + ' · desborde 375 px ' + (sinRed.desborde ? 'SÍ' : 'no'));
    const malo = bloqueadas || sinRed.imagenesRotas.length || sinRed.desborde || sinRed.videos.some(d => !d) || errores.length;
    if (errores.length) console.log(errores.join('\n'));
    console.log(malo ? 'FALLA · revisa lo de arriba' : 'PASA · HTML y PDF listos para mandar');
    process.exitCode = malo ? 1 : 0;
  } finally {
    await browser.close();
    fs.rmSync(tmp, { force: true });
  }
})().catch(e => { console.error(e); process.exit(1); });
