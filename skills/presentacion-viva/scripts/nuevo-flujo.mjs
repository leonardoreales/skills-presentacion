#!/usr/bin/env node
// Genera el esqueleto de un video de flujo (flujo-N-<slug>.html) a partir de un guion JSON. Sin dependencias.
// Uso: node nuevo-flujo.mjs <guion.json> <carpeta-de-flujos> [--forzar]   (la que lleva motor.js y comun.css)
// El esqueleto ya trae tiempos, composición, etapas, frases, estados, puente y resultado; las MAQUETAS de cada
// etapa salen como marcadores «MAQUETA:» que hay que dibujar a mano (es lo que hace único cada flujo).
// Formato del guion: references/gramatica-del-flujo.md §3.
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const args = process.argv.slice(2);
const [gPath, dir] = args.filter(a => !a.startsWith('--'));
if (!gPath || !dir) { console.error('Uso: node nuevo-flujo.mjs <guion.json> <carpeta-de-flujos> [--forzar]'); process.exit(2); }
const g = JSON.parse(readFileSync(gPath, 'utf8'));
const fallos = [], avisos = [];
const E = g.etapas || [];
if (!g.slug || !/^[a-z0-9-]+$/.test(g.slug)) fallos.push('slug obligatorio, en minúsculas y con guiones');
if (!g.titulo) fallos.push('titulo obligatorio');
if (E.length < 2 || E.length > 8) fallos.push('entre 2 y 8 etapas (hay ' + E.length + '); con más, parte el flujo en dos videos');
const comp = g.composicion || (E.length > 6 ? 'zigzag' : 'lineal');
if (!['lineal', 'zigzag', 'ciclo', 'arco', 'escalera'].includes(comp)) fallos.push('composición desconocida: ' + comp);
if (comp === 'lineal' && E.length > 6) avisos.push('7-8 etapas en lineal quedan apretadas: prueba "zigzag"');
E.forEach((e, i) => {
  if (!e.nombre || !e.frase) fallos.push(`etapa ${i + 1}: nombre y frase obligatorios`);
  if (e.nombre && e.nombre.replace('<br>', ' ').length > 16) avisos.push(`etapa ${i + 1}: nombre de ${e.nombre.length} caracteres (>16 se parte en dos líneas; usa <br>)`);
  if (e.frase && e.frase.length > 52) avisos.push(`etapa ${i + 1}: frase de ${e.frase.length} caracteres (>52 no cabe en dos líneas del panel)`);
});
if (!g.resultado || !g.resultado.titulo) fallos.push('resultado.titulo obligatorio: el video termina diciendo qué se logró');
if (fallos.length) { fallos.forEach(f => console.error('FALLA  ' + f)); process.exit(1); }

const n = g.n || 1, de = g.de || 1;
const out = join(resolve(dir), `flujo-${n}-${g.slug}.html`);
if (existsSync(out) && !args.includes('--forzar')) { console.error('Ya existe ' + out + ' (usa --forzar)'); process.exit(1); }
const paso = g.paso || (E.length >= 7 ? 1.35 : 1.6);
const ini = 2.0, TRES = +(ini + E.length * paso).toFixed(2), dur = +(TRES + 3.5).toFixed(2);
if (dur < 10 || dur > 20) avisos.push(`duración ${dur} s fuera de 10-20 s: ajusta "paso"`);
const columna = comp === 'ciclo';
const panel = columna ? { x: 1080, y: 330, w: 720, h: 560, forma: 'columna' }
  : { x: 140, y: comp === 'lineal' ? 680 : comp === 'zigzag' ? 760 : 710, w: 1640, h: comp === 'lineal' ? 320 : comp === 'zigzag' ? 270 : 300 };
const opts = { lineal: { y: 450, x0: 240, x1: g.puente ? 1400 : 1680, hasta: g.puente ? 1500 : 1810 }, zigzag: {}, ciclo: { cx: 540, cy: 650, r: 270 },
  arco: { cy: 640, ry: 300 }, escalera: { y0: 560, y1: 250 } }[comp];
const q = s => JSON.stringify(s);
const tema = typeof g.tema === 'object' ? JSON.stringify(g.tema) : q(g.tema || 'neutral');
const ficha = g.ficha || 'doc';

const panels = E.map((e, i) => {
  const chips = [];
  if (e.estado) chips.push(`{ t: ${q(e.estado)}, k: 'state', at: 0.7 }`);
  if (e.nota) chips.push(`{ t: ${q(e.nota)}, at: 0.9 }`);
  return `      { t0: T[${i}], t1: ${i < E.length - 1 ? `T[${i + 1}]` : 'TRES'}, eyebrow: ${q(`${g.etiquetaPaso || 'Etapa'} ${String(i + 1).padStart(2, '0')} de ${String(E.length).padStart(2, '0')}`)}, phrase: ${q(e.frase)},
        chips: [${chips.join(', ')}],
        // MAQUETA: ${e.maqueta || 'el objeto que se ve en esta etapa (pantalla, documento, sello, lista…), abstracto: barras en vez de datos'}
        html: maqueta(${q(e.maqueta || e.nombre)}) },`;
}).join('\n');

const puenteNode = g.puente ? `,
    { x: XG, y: Y, num: ${q(g.puente.etiqueta || '')}, name: ${q(g.puente.nombre)}, arr: TRES - 0.1, dashed: true, ghost: true, noCheck: true, appear: 1.75 }` : '';

const html = `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Flujo ${n} · ${g.titulo}</title>
<link rel="stylesheet" href="comun.css">
<style>
  /* Estilos de las maquetas de ESTE flujo. Colores solo con variables del tema: var(--gold), rgba(var(--mute-rgb),.3)… */
  .ph { position: absolute; inset: 8px 20px; border-radius: 16px; border: 1.5px dashed var(--faint); display: flex; align-items: center; justify-content: center; text-align: center; padding: 20px; font-family: 'Consolas', monospace; font-size: 22px; color: var(--dim); }
</style>
</head>
<body>
<div id="stage"></div>
<script src="motor.js"></script>
<script>
(function () {
  // Generado por nuevo-flujo.mjs desde ${gPath.replace(/\\/g, '/').split('/').pop()}. Composición: ${comp}. Tema: ${typeof g.tema === 'object' ? 'derivado' : (g.tema || 'neutral')}.
  const TEMA = ${tema};
  const C = SV.tema(TEMA);
  const { prog, ease, mix, clamp } = SV;
  const comp = SV.composicion(${q(comp)}, ${E.length}, ${JSON.stringify(opts)});
  const P = comp.puntos, Y = P[0].y;
  const tm = SV.tiempos(${E.length}, { inicio: ${ini}, paso: ${paso} });
  const T = tm.T, TRES = tm.resultado;${g.puente ? '\n  const XG = 1700;' : ''}

  // Marcador de maqueta: SUSTITÚYELO por el artefacto de cada etapa (ver gramatica-del-flujo.md §5).
  const maqueta = qué => '<div class="ph" data-pop="0.1">MAQUETA · ' + qué + '</div>';

  const artRes = '<div class="res-eyebrow" data-in="0.05">Resultado</div>' +
    '<div class="res-title" data-in="0.15">' + ${q(g.resultado.titulo)} + '</div>' +
    '<div class="res-sub" data-in="0.4"${columna ? ' style="top:220px"' : ''}>' + ${q(g.resultado.sub || '')} + '</div>';

  SV.run({
    tema: TEMA,
    duration: tm.duracion,
    eyebrow: ${q(`${g.sistema ? g.sistema + ' · ' : ''}Flujo ${n} de ${de}`)},
    title: ${q(g.titulo)},
    subtitle: ${q(g.subtitulo || '')},
    ficha: { kinds: [${q(ficha)}], trazo: comp.d, segs: SV.rutaFr(T${comp === 'ciclo' ? '.concat([TRES])' : ''}, P.map(p => p.fr)${comp === 'ciclo' ? '.concat([1])' : ''}) },
    tracks: [{ d: comp.d }${g.puente ? ", { x0: P[P.length - 1].x + 100, x1: XG - 40, y: Y, dashed: true, inAt: 1.6 }" : ''}],
    nodes: P.map((p, i) => ({ x: p.x, y: p.y, labelPos: p.labelPos, num: String(i + 1).padStart(2, '0'),
      name: ${JSON.stringify(E.map(e => e.nombre))}[i], arr: T[i], next: i < P.length - 1 ? T[i + 1] : TRES }))${puenteNode ? `.concat([${puenteNode.slice(2).trim()}])` : ''},
    panel: ${JSON.stringify(panel)},
    pointer: P.map((p, i) => ({ t: T[i], ${columna ? 'y: p.y' : 'x: p.x'} })).concat([{ t: TRES, ${columna ? 'y: P[0].y' : (g.puente ? 'x: XG' : 'x: P[P.length - 1].x')} }]),
    panels: [
${panels}
      { t0: TRES, t1: null, full: true, html: artRes }
    ]
  });
})();
</script>
</body>
</html>
`;
writeFileSync(out, html, 'utf8');
avisos.forEach(a => console.log('AVISO  ' + a));
console.log(`Creado ${out} · ${E.length} etapas · ${comp} · ${dur} s`);
const motorMjs = join(dirname(fileURLToPath(import.meta.url)), 'motor.mjs');
console.log(`Siguiente: dibuja cada MAQUETA y revisa con  node "${motorMjs}" render "${resolve(dir)}" flujo-${n}-${g.slug}` +
  ' --stills 2.5,6,' + (TRES + 0.8).toFixed(1));
