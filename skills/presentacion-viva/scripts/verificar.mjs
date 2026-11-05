#!/usr/bin/env node
// Verificación estática de una presentación viva. Sin dependencias.
// Uso: node verificar.mjs <ruta/index.html | ruta/flujo-N-x.html> [--vetar "termino1,termino2"]
// Un flujo de video (usa motor.js y SV.run) se reconoce solo y se mide con sus propias reglas.
// Sale con código 1 si algo FALLA; los AVISOS no bloquean, pero se revisan a mano.
import { readFileSync } from 'node:fs';

const args = process.argv.slice(2);
const file = args.find(a => !a.startsWith('--') && args[args.indexOf(a) - 1] !== '--vetar');
if (!file) { console.error('Uso: node verificar.mjs <index.html> [--vetar "a,b,c"]'); process.exit(2); }
const vi = args.indexOf('--vetar');
const vetados = vi >= 0 ? args[vi + 1].split(',').map(s => s.trim()).filter(Boolean) : [];

const html = readFileSync(file, 'utf8');
const lines = html.split(/\r?\n/);
const fallos = [], avisos = [], ok = [];
const sinTildes = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
const esFlujo = /motor\.js/.test(html) && /SV\.run\(/.test(html);
if (esFlujo) ok.push('modo FLUJO (video): no aplican viewport ni reduced-motion; se miden duración, colores por rol y guion');

// 1. charset en los primeros 1024 bytes (si no, las tildes se rompen en un servidor local)
if (/<meta\s+charset=["']?utf-8/i.test(html.slice(0, 1024))) ok.push('meta charset utf-8 al principio');
else fallos.push('Falta <meta charset="utf-8"> en los primeros 1024 bytes');

// 2. viewport (sin él, el móvil muestra la versión de escritorio encogida)
if (esFlujo) {}
else if (/<meta\s+name=["']viewport/i.test(html)) ok.push('meta viewport');
else avisos.push('Falta <meta name="viewport" …>: revisa el móvil');

// 3. scripts y hojas externas con versión exacta
const ext = [...html.matchAll(/<(?:script|link)[^>]+(?:src|href)=["'](https?:\/\/[^"']+)["']/gi)].map(m => m[1]);
for (const u of ext) {
  if (/fonts\.(googleapis|gstatic)\.com/.test(u)) continue;
  if (/latest|@\d+(\.\d+)?\/|@\d+(\.\d+)?$/i.test(u) || !/\d+\.\d+\.\d+/.test(u)) fallos.push('Librería sin versión exacta: ' + u);
  else ok.push('versión fija: ' + u.replace(/^https?:\/\//, ''));
}

// 4. movimiento reducido
const rm = /prefers-reduced-motion/.test(html), mm = /matchMedia/.test(html);
if (esFlujo) {}
else if (rm) ok.push('prefers-reduced-motion presente' + (mm ? ' (CSS/JS)' : ''));
else fallos.push('No se respeta prefers-reduced-motion');

// 5. «desde» de GSAP sin immediateRender:false (la escena puede quedar vacía en reposo)
const fromTo = (html.match(/\.fromTo\(/g) || []).length, ir = (html.match(/immediateRender\s*:\s*false/g) || []).length;
const fromSolo = (html.match(/\.from\(/g) || []).length;
if (fromSolo) avisos.push(fromSolo + ' llamada(s) a .from(): el estado en reposo debe ser el final; usa fromTo(…,{immediateRender:false})');
if (fromTo > ir) avisos.push(fromTo + ' fromTo y solo ' + ir + ' immediateRender:false: revisa que cada «desde» lo lleve');

// 6. términos vetados (sin distinguir tildes ni mayúsculas); en URLs se informan pero no cuentan
for (const t of vetados) {
  const tt = sinTildes(t);
  lines.forEach((ln, i) => {
    const l = sinTildes(ln);
    let k = l.indexOf(tt);
    while (k >= 0) {
      const ctx = ln.slice(Math.max(0, k - 40), k + tt.length + 40);
      const antes = ln.slice(0, k);
      const enUrl = /https?:\/\/\S*$/.test(antes);
      // Solo una URL de CDN se tolera: un <meta> o un comentario también salen en un grep, y la regla es el grep.
      const tecnico = enUrl ? ' (dentro de una URL)' : '';
      (tecnico ? avisos : fallos).push('Término vetado «' + t + '»' + tecnico + ' en línea ' + (i + 1) + ': …' + ctx.trim() + '…');
      k = l.indexOf(tt, k + 1);
    }
  });
}
if (vetados.length && !fallos.some(f => f.startsWith('Término vetado'))) ok.push('0 términos vetados (' + vetados.join(', ') + ')');

// 7. cifras visibles: listarlas para comprobar que cada una tiene fuente
const visible = html.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>|<!--[\s\S]*?-->/g, ' ').replace(/<[^>]+>/g, ' ');
const cifras = [...new Set((visible.match(/\b\d{1,3}(?:[.,]\d{3})+\b|\b\d{2,}(?:[.,]\d+)?\s?%|\b\d{3,}\b/g) || []))];
if (cifras.length) avisos.push('Cifras en el texto (cada una necesita fuente y fecha): ' + cifras.join(', '));

// 8. imágenes sin alt
const sinAlt = [...html.matchAll(/<img(?![^>]*\balt=)[^>]*>/gi)].length;
if (sinAlt) avisos.push(sinAlt + ' <img> sin atributo alt');
// 8.bis Datos de imagen sin rellenar: preparar-imagen y el taller dejan PENDIENTE hasta que una persona escribe el
// texto alternativo (WCAG 1.1.1). Con un PENDIENTE no se publica (references/imagenes.md §6).
const pendientes = [...html.matchAll(/\b(?:alt|aria-label)\s*=\s*["']PENDIENTE["']/gi)].length;
if (pendientes) fallos.push(pendientes + ' imagen(es) con alt o aria-label «PENDIENTE»: escribe qué muestran');
const sinMedidas = [...html.matchAll(/<img(?![^>]*\bwidth=)[^>]*>/gi)].length;
if (sinMedidas) avisos.push(sinMedidas + ' <img> sin width/height: la página salta al cargar (CLS)');

// 9. Reglas propias de un flujo de video (references/gramatica-del-flujo.md)
if (esFlujo) {
  const script = (html.match(/<script>([\s\S]*?)<\/script>/g) || []).join('\n');
  const dm = script.match(/duration:\s*([\d.]+)/), usaTiempos = /SV\.tiempos\(/.test(script);
  if (dm) { const d = +dm[1]; (d >= 10 && d <= 20 ? ok : avisos).push('duración ' + d + ' s' + (d >= 10 && d <= 20 ? '' : ': fuera de 10-20 s (los que se proyectaron duran 13,5-14 s); parte el flujo o acorta el paso')); }
  else if (usaTiempos) ok.push('duración calculada con SV.tiempos');
  else avisos.push('No encuentro la duración (duration: N o SV.tiempos)');
  if (/SV\.tema\(|tema:\s*['{]/.test(script)) ok.push('tema declarado'); else avisos.push('Sin tema declarado: sale el neutral. Usa SV.tema(...) y tema: en SV.run');
  const hexes = [...new Set((html.replace(/const TEMA = \{[^}]*\}/g, '').match(/#[0-9A-Fa-f]{6}\b/g) || []))];
  if (hexes.length) avisos.push(hexes.length + ' colores literales (' + hexes.slice(0, 6).join(' ') + (hexes.length > 6 ? '…' : '') + '): usa roles del tema (C.gold, var(--mute)…) para que el flujo cambie de identidad');
  else ok.push('colores por rol del tema');
  const etapas = (script.match(/eyebrow:\s*'[^']*\d+ de \d+'/g) || []).length;
  if (etapas && (etapas < 2 || etapas > 8)) avisos.push(etapas + ' paneles de etapa: entre 3 y 7 se leen; más, parte el flujo');
  const marcadores = (script.match(/MAQUETA ·|maqueta\(/g) || []).length;
  if (marcadores) fallos.push('Quedan ' + marcadores + ' marcadores de MAQUETA sin dibujar');
  const frases = [...script.matchAll(/phrase:\s*'([^']*)'/g)].map(m => m[1]).filter(f => f.length > 52);
  if (frases.length) avisos.push('Frases largas (>52, no caben en dos líneas): ' + frases.map(f => '«' + f.slice(0, 30) + '…»').join(' '));
}

for (const s of ok) console.log('OK     ' + s);
for (const s of avisos) console.log('AVISO  ' + s);
for (const s of fallos) console.log('FALLA  ' + s);
console.log('\n' + (fallos.length ? 'NO PASA' : 'PASA') + ' · ' + fallos.length + ' fallo(s) · ' + avisos.length + ' aviso(s)');
console.log(esFlujo ? 'Parte estática del flujo. Falta: --stills revisados, render y hoja de contactos mirada entera.'
  : 'Esto es la parte estática. Falta la del navegador: consola sin errores, íconos, 375 px, escritorio y reduced-motion.');
process.exit(fallos.length ? 1 : 0);
