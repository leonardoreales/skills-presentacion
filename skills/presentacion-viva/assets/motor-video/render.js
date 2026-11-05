// Render determinista: abre cada HTML, llama a window.seek(t) fotograma a fotograma, captura PNG y codifica con ffmpeg.
// Se usa a través de scripts/motor.mjs, que lo instala una vez por máquina y le pasa la carpeta de los flujos en
// MOTOR_SRC (sin MOTOR_SRC, los flujos son los de la carpeta de este fichero). Argumentos:
//   (ninguno)                              -> todos los flujo-*.html de la carpeta a MP4 + hoja de contactos
//   flujo-1-ingesta                        -> solo ese flujo
//   flujo-1-ingesta --stills 2.5,6,12      -> solo capturas sueltas en ../_revision/ (no MP4)
// Salida: la carpeta PADRE de la de los flujos (MP4, hojas, _revision/). Navegador: CHROME_EXE, o el chromium
// headless shell más reciente de ms-playwright (npx playwright install chromium-headless-shell).
'use strict';
const path = require('path');
const fs = require('fs');
const { execFileSync } = require('child_process');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright-core');

const SRC = process.env.MOTOR_SRC ? path.resolve(process.env.MOTOR_SRC) : __dirname;
const OUT = path.resolve(SRC, '..');
const FPS = 30;
function findExe() {
  if (process.env.CHROME_EXE) return process.env.CHROME_EXE;
  const roots = [
    process.env.PLAYWRIGHT_BROWSERS_PATH,
    process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, 'ms-playwright'),
    process.env.HOME && path.join(process.env.HOME, '.cache', 'ms-playwright'),
    process.env.HOME && path.join(process.env.HOME, 'Library', 'Caches', 'ms-playwright')
  ].filter(Boolean);
  const names = ['chrome-headless-shell.exe', 'chrome-headless-shell'];
  for (const root of roots) {
    if (!fs.existsSync(root)) continue;
    const dirs = fs.readdirSync(root).filter(d => d.startsWith('chromium_headless_shell-'))
      .sort((a, b) => Number(b.split('-')[1]) - Number(a.split('-')[1]));
    for (const d of dirs) for (const sub of fs.readdirSync(path.join(root, d))) for (const n of names) {
      const p = path.join(root, d, sub, n);
      if (fs.existsSync(p)) return p;
    }
  }
  return '';
}
const EXE = findExe();
const FLOWS = fs.readdirSync(SRC).filter(f => /^flujo-.*\.html$/.test(f)).map(f => f.replace(/\.html$/, '')).sort();
// Piezas con hoja de contactos propia: { 'id': { every: s, cols, name, pad: '0xRRGGBB' } }.
// Las que no estén aquí usan la hoja por defecto (un fotograma cada 2 s, 4 columnas).
const SHEETS = {};

const args = process.argv.slice(2);
const stillsIdx = args.indexOf('--stills');
const stills = stillsIdx >= 0 ? args[stillsIdx + 1].split(',').map(Number) : null;
const wanted = args.filter((a, i) => !a.startsWith('--') && (stillsIdx < 0 || i !== stillsIdx + 1));
const flows = wanted.length ? wanted : FLOWS;

function ff(argv) { execFileSync('ffmpeg', argv, { stdio: ['ignore', 'ignore', 'inherit'] }); }

(async () => {
  if (!fs.existsSync(EXE)) throw new Error('No encuentro el navegador: ' + EXE);
  const browser = await chromium.launch({ executablePath: EXE, args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text'] });
  try {
    for (const id of flows) {
      const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
      const errs = [];
      page.on('pageerror', e => errs.push(String(e)));
      page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
      await page.goto(pathToFileURL(path.join(SRC, id + '.html')).href);
      await page.waitForFunction(() => window.__ready === true, null, { timeout: 20000 });
      if (errs.length) throw new Error(id + ': errores en la página:\n' + errs.join('\n'));
      const dur = await page.evaluate(() => window.DURATION);
      const momentos = await page.evaluate(() => window.MOMENTOS || null);
      const fondo = '0x' + String(await page.evaluate(() => window.FONDO || '#0A1626')).replace('#', '');
      const stage = await page.$('#stage');
      // Captura por CDP directa: la misma llamada que hace stage.screenshot() de Playwright, sin su trabajo previo
      // por fotograma (desplazar a la vista, esperar estabilidad). Mismos píxeles y el doble de rápida (121 s frente
      // a 244-277 s para 405 fotogramas). NO usar optimizeForSpeed: es 3× más rápido, pero cambia píxeles
      // (medido 2026-10-27: 264 de 405 fotogramas distintos, PSNR ≥ 56 dB, el MP4 deja de ser el mismo).
      // Se sigue en serie: el fotograma depende de la historia de seeks (subpíxel), y repartirlo en páginas
      // paralelas ni ahorra tiempo ni sale idéntico. Los --stills usan la misma captura: lo que se revisa es lo que
      // sale en el video.
      const cdp = await page.context().newCDPSession(page);
      const caja = await stage.boundingBox();
      const clip = { x: caja.x, y: caja.y, width: caja.width, height: caja.height, scale: 1 };
      async function captura(t, fichero) {
        await page.evaluate(tt => window.seek(tt), t);
        const { data } = await cdp.send('Page.captureScreenshot',
          { format: 'png', captureBeyondViewport: false, clip });
        fs.writeFileSync(fichero, Buffer.from(data, 'base64'));
      }

      if (stills) {
        const dir = path.join(OUT, '_revision'); fs.mkdirSync(dir, { recursive: true });
        for (const t of stills) await captura(t, path.join(dir, id + '_t' + t.toFixed(2) + '.png'));
        console.log(id + ': ' + stills.length + ' capturas en ' + dir);
        await cdp.detach();
        await page.close();
        continue;
      }

      const frames = Math.round(dur * FPS);
      const dir = path.join(OUT, '_fotogramas', id);
      fs.rmSync(dir, { recursive: true, force: true });
      fs.mkdirSync(dir, { recursive: true });
      const t0 = Date.now();
      for (let f = 0; f < frames; f++) {
        await captura(f / FPS, path.join(dir, String(f).padStart(5, '0') + '.png'));
        if (f % 60 === 0) process.stdout.write(id + ' ' + f + '/' + frames + '\n');
      }
      await cdp.detach();
      if (errs.length) throw new Error(id + ': errores durante el render:\n' + errs.join('\n'));
      console.log(id + ': ' + frames + ' fotogramas en ' + ((Date.now() - t0) / 1000).toFixed(1) + ' s');
      await page.close();

      const mp4 = path.join(OUT, id + '.mp4');
      ff(['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(dir, '%05d.png'),
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(FPS),
        '-movflags', '+faststart', '-an', mp4]);
      const sh = SHEETS[id];
      if (sh) {
        // Hoja propia de la pieza: un fotograma cada sh.every s desde t = 0, rejilla de sh.cols columnas
        const step = Math.round(sh.every * FPS);
        const n = Math.ceil(frames / step);
        const rows = Math.ceil(n / sh.cols);
        const hoja = path.join(OUT, sh.name + '.png');
        ff(['-y', '-loglevel', 'error', '-i', mp4, '-vf',
          "select='not(mod(n\\," + step + "))',scale=640:360,pad=656:376:8:8:color=" + sh.pad + ',tile=' + sh.cols + 'x' + rows + ':color=' + sh.pad,
          '-frames:v', '1', '-fps_mode', 'passthrough', hoja]);
        fs.rmSync(dir, { recursive: true, force: true });
        console.log('OK ' + mp4 + '\n   ' + hoja);
        continue;
      }
      // Hoja de contactos: un fotograma por momento del flujo (cabecera, cada etapa asentada, resultado), 4 columnas.
      // Sin MOMENTOS (motor antiguo), uno cada 2 s desde t = 1.
      const ts = momentos && momentos.length ? momentos : Array.from({ length: Math.floor((dur - 1) / 2) + 1 }, (_, i) => 1 + 2 * i);
      const sel = ts.map(t => 'eq(n\\,' + Math.min(frames - 1, Math.round(t * FPS)) + ')').join('+');
      const rows = Math.ceil(ts.length / 4);
      const hoja = path.join(OUT, 'hoja-' + id.replace(/^flujo-(\d).*/, 'flujo-$1') + '.png');
      ff(['-y', '-loglevel', 'error', '-i', mp4, '-vf',
        "select='" + sel + "',scale=640:360,pad=656:376:8:8:color=" + fondo + ',tile=4x' + rows + ':color=' + fondo,
        '-frames:v', '1', '-fps_mode', 'passthrough', hoja]);
      fs.rmSync(dir, { recursive: true, force: true });
      console.log('OK ' + mp4 + '\n   ' + hoja);
    }
  } finally {
    await browser.close();
    const fr = path.join(OUT, '_fotogramas');
    if (fs.existsSync(fr) && fs.readdirSync(fr).length === 0) fs.rmdirSync(fr);
  }
})().catch(e => { console.error(e); process.exit(1); });
