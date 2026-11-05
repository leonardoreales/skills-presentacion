/* Motor «sistema vivo»: cada fotograma es una funcion pura del tiempo.
   window.seek(t) pinta el segundo t; no se usa requestAnimationFrame, ni relojes, ni transiciones CSS. */
(function () {
  'use strict';
  const W = 1920, H = 1080, NS = 'http://www.w3.org/2000/svg';
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, p) => a + (b - a) * p;
  function hexRgb(h) {
    if (h.startsWith('rgb')) return h.replace(/[^\d,.]/g, '').split(',').slice(0, 3).map(Number);
    h = h.replace('#', ''); if (h.length === 3) h = h.replace(/./g, c => c + c);
    return [0, 2, 4].map(i => parseInt(h.substr(i, 2), 16));
  }
  const hex2 = v => Math.round(clamp(v, 0, 255)).toString(16).padStart(2, '0');
  const mixHex = (a, b, p) => { const A = hexRgb(a), B = hexRgb(b); return '#' + A.map((v, i) => hex2(lerp(v, B[i], p))).join(''); };

  // Tema: los colores salen de ROLES, nunca de literales sueltos. «gold» es el acento del tema, sea del color que sea
  // (el nombre viene del primer perfil). Un tema se elige con cfg.tema: 'americana' | 'neutral' |
  // { fondo, tinta, acento } (se deriva el resto) | un objeto con claves de C para afinar.
  function derivar(o) {
    const f = o.fondo, t = o.tinta, a = o.acento, hi = o.acentoHi || mixHex(a, '#ffffff', 0.38);
    // Fondo claro: la sombra de la viñeta va hacia la tinta y suave; hacia negro al 70 % ensuciaba el blanco de gris
    // (medido 2026-10-30). En un tema claro, el acento como texto se oscurece hacia la tinta para leerse (contraste).
    const [r, g, b] = hexRgb(f), claro = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255 > 0.6;
    if (claro) return Object.assign(derivarOscuro(f, t, a, hi), {
      shade: mixHex(f, t, 0.16), goldL: mixHex(a, t, 0.18), goldTxt: mixHex(a, t, 0.32), pass: mixHex(a, t, 0.18),
      plate: mixHex(a, f, 0.55), cream: mixHex(a, t, 0.5), goldHi: mixHex(a, f, 0.2)
    });
    return derivarOscuro(f, t, a, hi);
  }
  function derivarOscuro(f, t, a, hi) {
    return {
      bg: f, bg2: mixHex(f, t, 0.035), bg3: mixHex(f, t, 0.065), node: mixHex(f, t, 0.018), panel: mixHex(f, t, 0.07),
      panel2: mixHex(f, t, 0.04), ink: t, mute: mixHex(t, f, 0.3), info: mixHex(t, f, 0.22), dim: mixHex(t, f, 0.55),
      pend: mixHex(t, f, 0.55), faint: mixHex(f, t, 0.13), track: mixHex(f, t, 0.12), line: mixHex(f, t, 0.18),
      gold: a, goldL: hi, goldHi: mixHex(a, '#ffffff', 0.45), goldTxt: mixHex(a, hi, 0.4), pass: mixHex(a, hi, 0.55),
      plate: mixHex(a, '#ffffff', 0.5), cream: mixHex(hi, '#ffffff', 0.3), shade: mixHex(f, '#000000', 0.7)
    };
  }
  const TEMAS = {
    americana: {
      bg: '#0E1F35', bg2: '#142943', bg3: '#18314F', node: '#12253D', panel: '#192F4C', panel2: '#112239',
      ink: '#F4F7FB', mute: '#A8B8CD', info: '#BAC8DA', dim: '#6F86A6', pend: '#6F86A6', faint: '#2E4869',
      track: '#2B4566', line: '#3A5578', gold: '#B68D40', goldL: '#DDBD78', goldHi: '#E6C784', goldTxt: '#D2B06C',
      pass: '#CDAD6C', plate: '#E3C27E', cream: '#EBCF90', shade: '#040A14'
    },
    neutral: derivar({ fondo: '#16181C', tinta: '#F2F3F5', acento: '#D9A441', acentoHi: '#EBC77E' })
  };
  const C = Object.assign({}, TEMAS.neutral);
  const rgb = h => hexRgb(h).join(',');
  const rgba = (h, a) => 'rgba(' + rgb(h) + ',' + a + ')';
  function aplicarTema(t) {
    const base = typeof t === 'string' ? TEMAS[t] : (t && t.fondo ? derivar(t) : Object.assign({}, TEMAS.neutral, t || {}));
    if (!base) throw new Error('Tema desconocido: ' + t + ' (hay: ' + Object.keys(TEMAS).join(', ') + ')');
    Object.assign(C, base);
    const css = document.documentElement.style;
    for (const k in C) { css.setProperty('--' + k, C[k]); css.setProperty('--' + k + '-rgb', rgb(C[k])); }
  }
  const prog = (t, a, b) => (b <= a ? (t >= a ? 1 : 0) : clamp((t - a) / (b - a)));
  const ease = {
    lin: p => p,
    inCubic: p => p * p * p,
    outCubic: p => 1 - Math.pow(1 - p, 3),
    outQuint: p => 1 - Math.pow(1 - p, 5),
    inOutCubic: p => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2),
    inOutSine: p => -(Math.cos(Math.PI * p) - 1) / 2,
    outBack: p => { const c1 = 1.25, c3 = c1 + 1; return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2); }
  };
  function mix(a, b, p) { const A = hexRgb(a), B = hexRgb(b); p = clamp(p); return 'rgb(' + A.map((v, i) => Math.round(lerp(v, B[i], p))).join(',') + ')'; }
  function S(tag, attrs, parent) { const e = document.createElementNS(NS, tag); if (attrs) for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
  function D(cls, parent, html) { const e = document.createElement('div'); if (cls) e.className = cls; if (html != null) e.innerHTML = html; if (parent) parent.appendChild(e); return e; }
  function set(e, attrs) { for (const k in attrs) e.setAttribute(k, attrs[k]); }
  const f2 = v => (Math.round(v * 100) / 100).toString();

  // Trayectoria por tramos: {t0,t1,x0,y0,x1,y1,[cx,cy]} con easing suave (nunca lineal).
  function pathAt(segs, t) {
    if (t <= segs[0].t0) return { x: segs[0].x0, y: segs[0].y0 };
    let last = segs[0];
    for (const s of segs) {
      if (t < s.t0) return { x: last.x1, y: last.y1 };
      if (t <= s.t1) {
        const p = (s.ease || ease.inOutCubic)(prog(t, s.t0, s.t1));
        if (s.cx != null) { const u = 1 - p; return { x: u * u * s.x0 + 2 * u * p * s.cx + p * p * s.x1, y: u * u * s.y0 + 2 * u * p * s.cy + p * p * s.y1 }; }
        return { x: lerp(s.x0, s.x1, p), y: lerp(s.y0, s.y1, p) };
      }
      last = s;
    }
    return { x: last.x1, y: last.y1 };
  }
  // Construye tramos a partir de paradas: [{t:llegada, x, y, travel}]
  function route(start, stops) {
    const segs = []; let px = start.x, py = start.y;
    for (const s of stops) {
      const tr = s.travel || 0.55;
      segs.push({ t0: s.t - tr, t1: s.t, x0: px, y0: py, x1: s.x, y1: s.y == null ? py : s.y, cx: s.cx, cy: s.cy, ease: s.ease });
      px = s.x; py = s.y == null ? py : s.y;
    }
    return segs;
  }

  // Animador declarativo para los artefactos: data-in, data-pop, data-draw="a,dur", data-fade="a,dur,de,a", data-out, data-slide="a,dur,dx,dy"
  function auto(rootEl) {
    const items = [];
    rootEl.querySelectorAll('[data-in],[data-pop],[data-draw],[data-fade],[data-out],[data-slide]').forEach(e => {
      const it = { e };
      const d = e.dataset;
      if (d.in) it.in = +d.in;
      if (d.pop) it.pop = +d.pop;
      if (d.out) it.out = +d.out;
      if (d.draw) { const [a, du] = d.draw.split(',').map(Number); it.draw = [a, du || 0.5]; e.setAttribute('pathLength', '1'); e.style.strokeDasharray = '1'; e.style.strokeDashoffset = '1'; }
      if (d.fade) it.fade = d.fade.split(',').map(Number);
      if (d.slide) it.slide = d.slide.split(',').map(Number);
      if (e instanceof SVGElement && (it.pop != null || it.slide || it.in != null)) { e.style.transformBox = 'fill-box'; e.style.transformOrigin = 'center'; }
      items.push(it);
    });
    return lt => {
      for (const it of items) {
        let op = 1, tf = '';
        if (it.in != null) { const p = ease.outCubic(prog(lt, it.in, it.in + 0.45)); op *= p; tf += 'translateY(' + f2((1 - p) * 18) + 'px) '; }
        if (it.pop != null) { const p = prog(lt, it.pop, it.pop + 0.5); op *= clamp(p * 2.5); tf += 'scale(' + (0.84 + 0.16 * ease.outBack(p)).toFixed(4) + ') '; }
        if (it.slide) { const [a, du, dx, dy] = it.slide; const p = ease.inOutCubic(prog(lt, a, a + du)); tf += 'translate(' + f2(dx * p) + 'px,' + f2(dy * p) + 'px) '; }
        if (it.fade) { const [a, du, fr, to] = it.fade; op *= lerp(fr, to, ease.inOutSine(prog(lt, a, a + du))); }
        if (it.out != null) op *= 1 - ease.inOutSine(prog(lt, it.out, it.out + 0.3));
        if (it.draw) { const p = ease.inOutCubic(prog(lt, it.draw[0], it.draw[0] + it.draw[1])); it.e.style.strokeDashoffset = (1 - p).toFixed(4); }
        it.e.style.opacity = op.toFixed(4);
        it.e.style.transform = tf;
      }
    };
  }

  // Icono de visto (para las listas de comprobacion)
  function checkSvg(at, opts) {
    opts = opts || {};
    const col = opts.color || C.goldL;
    return '<svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="17" fill="' + rgba(C.gold, .16) + '" stroke="' + col + '" stroke-width="2" data-pop="' + at + '"/>' +
      '<path d="M12 20.5 L18 26.5 L29 14" fill="none" stroke="' + col + '" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" data-draw="' + (at + 0.12) + ',0.35"/></svg>';
  }

  // ---- Composiciones: dónde van las etapas y por dónde viaja la ficha ----
  // SV.composicion(tipo, n, opciones) -> { d, puntos:[{x,y,fr,labelPos}] }. fr = fracción del trazo (0..1) en la
  // que está cada etapa. Tipos: lineal · zigzag · ciclo · arco · escalera. Para otra forma, escribe tu propio d y
  // pasa los puntos con su fr (SV.fraccion(d, x, y) la calcula).
  function composicion(tipo, n, o) {
    o = o || {};
    const pts = [];
    if (tipo === 'lineal') {
      const x0 = o.x0 != null ? o.x0 : 240, x1 = o.x1 != null ? o.x1 : 1680, y = o.y != null ? o.y : 450;
      const a = o.desde != null ? o.desde : 110, b = o.hasta != null ? o.hasta : 1810;
      for (let i = 0; i < n; i++) { const x = n === 1 ? (x0 + x1) / 2 : lerp(x0, x1, i / (n - 1)); pts.push({ x, y, fr: (x - a) / (b - a), labelPos: 'above' }); }
      return { d: 'M' + a + ' ' + y + ' H' + b, puntos: pts };
    }
    if (tipo === 'ciclo') {
      const cx = o.cx != null ? o.cx : 560, cy = o.cy != null ? o.cy : 600, r = o.r != null ? o.r : 300;
      for (let i = 0; i < n; i++) {
        const an = -Math.PI / 2 + 2 * Math.PI * i / n, x = cx + r * Math.cos(an), y = cy + r * Math.sin(an);
        const c = Math.cos(an), sn = Math.sin(an);
        pts.push({ x, y, fr: i / n, labelPos: Math.abs(sn) > 0.7 ? (sn < 0 ? 'above' : 'below') : (c > 0 ? 'right' : 'left') });
      }
      const d = 'M' + cx + ' ' + (cy - r) + ' A' + r + ' ' + r + ' 0 1 1 ' + cx + ' ' + (cy + r) + ' A' + r + ' ' + r + ' 0 1 1 ' + cx + ' ' + (cy - r);
      return { d, puntos: pts, cerrado: true };
    }
    if (tipo === 'arco') {
      const cx = o.cx != null ? o.cx : 960, cy = o.cy != null ? o.cy : 640, r = o.r != null ? o.r : 640, ry = o.ry != null ? o.ry : 330;
      for (let i = 0; i < n; i++) {
        const an = Math.PI + Math.PI * (n === 1 ? 0.5 : i / (n - 1));
        pts.push({ x: cx + r * Math.cos(an), y: cy + ry * Math.sin(an), fr: n === 1 ? 0.5 : i / (n - 1), labelPos: 'above' });
      }
      return { d: 'M' + (cx - r) + ' ' + cy + ' A' + r + ' ' + ry + ' 0 0 1 ' + (cx + r) + ' ' + cy, puntos: pts, frAprox: true };
    }
    if (tipo === 'escalera') {
      const x0 = o.x0 != null ? o.x0 : 260, x1 = o.x1 != null ? o.x1 : 1660, y0 = o.y0 != null ? o.y0 : 600, y1 = o.y1 != null ? o.y1 : 230;
      let d = '', segs = [];
      for (let i = 0; i < n; i++) {
        const x = n === 1 ? x0 : lerp(x0, x1, i / (n - 1)), y = n === 1 ? y0 : lerp(y0, y1, i / (n - 1));
        pts.push({ x, y, labelPos: 'above' });
        if (i === 0) d = 'M' + (x - 150) + ' ' + y + ' H' + x; else { d += ' H' + (x - 70) + ' V' + y + ' H' + x; }
      }
      return { d, puntos: pts, frMedir: true };
    }
    if (tipo === 'zigzag') {
      const fila = Math.ceil(n / 2), x0 = o.x0 != null ? o.x0 : 300, x1 = o.x1 != null ? o.x1 : 1620;
      const ya = o.ya != null ? o.ya : 370, yb = o.yb != null ? o.yb : 600, rr = (yb - ya) / 2;
      for (let i = 0; i < n; i++) {
        const k = i < fila ? i : i - fila, xs = fila === 1 ? (x0 + x1) / 2 : lerp(x0, x1, k / (fila - 1));
        pts.push({ x: i < fila ? xs : x1 - (xs - x0), y: i < fila ? ya : yb, labelPos: i < fila ? 'above' : 'below' });
      }
      const d = 'M' + (x0 - 140) + ' ' + ya + ' H' + x1 + ' A' + rr + ' ' + rr + ' 0 0 1 ' + x1 + ' ' + yb + ' H' + (x0 - 140);
      return { d, puntos: pts, frMedir: true };
    }
    throw new Error('Composición desconocida: ' + tipo + ' (hay: lineal, zigzag, ciclo, arco, escalera)');
  }
  // Fracción del trazo d más cercana al punto (x,y). Necesita el DOM; se usa al construir.
  function fraccion(d, x, y) {
    const pe = S('path', { d }, S('svg', null, document.body)), L = pe.getTotalLength();
    let best = 0, bd = Infinity;
    for (let i = 0; i <= 600; i++) { const q = pe.getPointAtLength(L * i / 600), dd = (q.x - x) ** 2 + (q.y - y) ** 2; if (dd < bd) { bd = dd; best = i / 600; } }
    pe.parentNode.remove();
    return best;
  }
  function medir(c) { if (c.frMedir || c.frAprox) c.puntos.forEach(p => { p.fr = fraccion(c.d, p.x, p.y); }); return c; }
  // Tiempos de llegada: la primera etapa a los `inicio` s y una cada `paso` s. El resultado entra ~0,1 s después
  // de la última llegada + `paso`. Con 5 etapas y los valores por defecto: 2,0 · 3,6 · 5,2 · 6,8 · 8,4 → resultado
  // a 10,0 y duración 13,5 s, el ritmo de los videos que se proyectaron.
  function tiempos(n, o) {
    o = o || {};
    const ini = o.inicio != null ? o.inicio : 2.0, paso = o.paso != null ? o.paso : 1.6;
    const T = []; for (let i = 0; i < n; i++) T.push(+(ini + i * paso).toFixed(2));
    const res = +(ini + n * paso).toFixed(2);
    return { T, resultado: res, duracion: +(res + (o.cierre != null ? o.cierre : 3.5)).toFixed(2) };
  }
  // Tramos de la ficha sobre un trazo: paradas en fracciones fr con llegada t.
  function rutaFr(T, frs, o) {
    o = o || {};
    const segs = []; let pf = o.desde != null ? o.desde : 0;
    T.forEach((t, i) => { const tr = (i === 0 ? o.primerViaje : o.viaje) || (i === 0 ? 0.5 : 0.55); segs.push({ t0: t - tr, t1: t, x0: pf, y0: 0, x1: frs[i], y1: 0 }); pf = frs[i]; });
    return segs;
  }

  function fichaShape(g, kind) {
    const s = S('g', null, g);
    const dark = C.bg;
    if (kind === 'row') {
      S('rect', { x: -34, y: -16, width: 68, height: 32, rx: 7, fill: 'url(#gGold)' }, s);
      S('rect', { x: -32, y: -14, width: 64, height: 9, rx: 5, fill: '#fff', opacity: 0.2 }, s);
      for (const x of [-12, 9]) S('rect', { x, y: -10, width: 2, height: 20, fill: dark, opacity: 0.32 }, s);
      for (const [x, w] of [[-27, 11], [-6, 11], [15, 13]]) S('rect', { x, y: -1, width: w, height: 5, rx: 2, fill: dark, opacity: 0.45 }, s);
    } else if (kind === 'rowHollow') {
      S('rect', { x: -34, y: -16, width: 68, height: 32, rx: 7, fill: rgba(C.bg, .9), stroke: C.goldTxt, 'stroke-width': 2, 'stroke-dasharray': '5 4' }, s);
      S('rect', { x: -2, y: -9, width: 4, height: 11, rx: 2, fill: C.goldTxt }, s);
      S('circle', { cx: 0, cy: 7, r: 2.4, fill: C.goldTxt }, s);
    } else if (kind === 'doc') {
      S('path', { d: 'M-21 -27 H11 L22 -16 V27 H-21 Z', fill: 'url(#gGold)' }, s);
      S('path', { d: 'M11 -27 V-16 H22 Z', fill: dark, opacity: 0.28 }, s);
      for (const [y, w] of [[-12, 26], [-3, 32], [6, 32], [15, 20]]) S('rect', { x: -14, y, width: w, height: 4, rx: 2, fill: dark, opacity: 0.42 }, s);
    } else if (kind === 'plate') {
      S('rect', { x: -36, y: -17, width: 72, height: 34, rx: 6, fill: 'url(#gGold)' }, s);
      S('rect', { x: -29, y: -9, width: 58, height: 18, rx: 3, fill: dark, opacity: 0.55 }, s);
      for (let i = 0; i < 6; i++) S('rect', { x: -25 + i * 9, y: -3, width: 5, height: 6, rx: 1, fill: C.plate, opacity: 0.95 }, s);
    }
    return s;
  }

  function build(cfg) {
    const stage = document.getElementById('stage');
    D('bg', stage); D('grid', stage); D('vignette', stage);
    const root = D('root', stage);
    const spot = D('spot', root);
    const svg = S('svg', { width: W, height: H, viewBox: '0 0 ' + W + ' ' + H, class: 'main' }, root);
    S('defs', null, svg).innerHTML =
      '<linearGradient id="gGold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="' + C.goldHi + '"/><stop offset="1" stop-color="' + C.gold + '"/></linearGradient>' +
      '<filter id="blur3" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>' +
      '<filter id="blur14" x="-150%" y="-150%" width="400%" height="400%"><feGaussianBlur stdDeviation="14"/></filter>' +
      '<filter id="blur20" x="-150%" y="-150%" width="400%" height="400%"><feGaussianBlur stdDeviation="20"/></filter>';
    const L = {};
    for (const k of ['track', 'links', 'nodes', 'sat', 'trail', 'ficha', 'top']) L[k] = S('g', null, svg);
    const html = D('', root);
    const ups = [];
    const api = { C, W, H, clamp, lerp, prog, ease, mix, rgba, S, D, set, pathAt, route, rutaFr, auto, checkSvg, ups, L, html, svg, root, cfg };

    // ---- Cabecera: entra como titulo centrado y se retira a la esquina ----
    if (cfg.title) {
    const hd = D('header', root, (cfg.eyebrow ? '<div class="eyebrow">' + cfg.eyebrow + '</div>' : '') + '<div class="title">' + cfg.title + '</div>' + (cfg.subtitle ? '<div class="subtitle">' + cfg.subtitle + '</div>' : ''));
    const hw = hd.offsetWidth, hh = hd.offsetHeight, s0 = 1.42, HX = 120, HY = 58;
    const dx0 = (W - hw * s0) / 2 - HX, dy0 = (H - hh * s0) / 2 - HY - 20;
    ups.push(t => {
      const a = ease.outCubic(prog(t, 0.1, 0.6));
      const m = ease.inOutCubic(prog(t, 0.78, 1.32));
      const s = lerp(s0, 1, m);
      hd.style.opacity = a.toFixed(4);
      hd.style.transform = 'translate(' + f2(lerp(dx0, 0, m)) + 'px,' + f2(lerp(dy0, 0, m) + (1 - a) * 30) + 'px) scale(' + s.toFixed(4) + ')';
    });
    }

    // ---- Ficha principal (va primero: el resto lee su posicion) ----
    function makeFicha(o) {
      const trail = [];
      for (let k = 0; k < 12; k++) trail.push(S('line', { stroke: o.trailColor || C.gold, 'stroke-linecap': 'round', filter: 'url(#blur3)', opacity: 0 }, o.trailLayer || L.trail));
      const g = S('g', null, o.layer || L.ficha);
      const glow = S('ellipse', { rx: 48, ry: 32, fill: o.glowColor || C.gold, filter: 'url(#blur14)', opacity: 0 }, g);
      const shapes = {};
      for (const k of o.kinds) shapes[k] = fichaShape(g, k);
      // Con o.trazo (un d de SVG), los x de los tramos son FRACCIONES del trazo y la ficha lo recorre exacto.
      let pe = null, PL = 0;
      if (o.trazo) { pe = S('path', { d: o.trazo, fill: 'none', stroke: 'none' }, svg); PL = pe.getTotalLength(); }
      const at = t => { const r = pathAt(o.segs, t); if (!pe) return r; const q = pe.getPointAtLength(clamp(r.x) * PL); return { x: q.x, y: q.y, fr: clamp(r.x) }; };
      const st = { x: 0, y: 0, a: 0, fr: 0 };
      ups.push(t => {
        const p = at(t), a = o.alpha ? o.alpha(t) : ease.outCubic(prog(t, 1.45, 1.8));
        const q = at(t - 0.03), sp = Math.hypot(p.x - q.x, p.y - q.y);
        const w = o.weights ? o.weights(t) : { [o.kinds[0]]: 1 };
        const sc = (o.scale ? o.scale(t) : 1) * (1 + 0.06 * clamp(sp / 25));
        set(g, { transform: 'translate(' + f2(p.x) + ',' + f2(p.y) + ') scale(' + sc.toFixed(4) + ')', opacity: a.toFixed(4) });
        for (const k in shapes) shapes[k].setAttribute('opacity', (w[k] || 0).toFixed(4));
        glow.setAttribute('opacity', ((o.glow == null ? 0.5 : o.glow) * (0.8 + 0.4 * clamp(sp / 20)) * a).toFixed(4));
        let prev = p;
        for (let k = 0; k < trail.length; k++) {
          const pk = at(t - (k + 1) * 0.022);
          const d = Math.hypot(pk.x - prev.x, pk.y - prev.y);
          const op = a * 0.6 * (1 - k / trail.length) * clamp(d / 5);
          set(trail[k], { x1: f2(prev.x), y1: f2(prev.y), x2: f2(pk.x), y2: f2(pk.y), 'stroke-width': (16 * (1 - k / trail.length) + 2).toFixed(1), opacity: op.toFixed(4) });
          prev = pk;
        }
        st.x = p.x; st.y = p.y; st.a = a; st.fr = p.fr != null ? p.fr : 0;
      });
      return st;
    }
    api.makeFicha = makeFicha;
    const F = cfg.ficha ? makeFicha(cfg.ficha) : { x: 0, y: 0, a: 0, fr: 0 };
    api.F = F;
    ups.push(() => { spot.style.transform = 'translate(' + f2(F.x) + 'px,' + f2(F.y) + 'px)'; spot.style.opacity = F.a.toFixed(4); });

    // ---- Vias ----
    (cfg.tracks || []).forEach((tr, i) => {
      if (tr.d) {
        // Vía sobre un trazo libre: se dibuja al entrar y se ilumina hasta donde va la ficha (F.fr).
        const base = S('path', { d: tr.d, fill: 'none', stroke: C.track, 'stroke-width': tr.dashed ? 4 : 3, 'stroke-linecap': 'round', pathLength: 1 }, L.track);
        const prg = S('path', { d: tr.d, fill: 'none', stroke: C.gold, 'stroke-width': tr.dashed ? 4 : 3, 'stroke-linecap': 'round', pathLength: 1, opacity: 0 }, L.track);
        const a0 = tr.inAt != null ? tr.inAt : 1.0 + i * 0.15, a1 = a0 + (tr.dibujo || 0.9);
        ups.push(t => {
          const p = ease.inOutCubic(prog(t, a0, a1));
          base.setAttribute('stroke-dasharray', tr.dashed ? '0.002 0.012' : p + ' 1');
          base.setAttribute('opacity', tr.dashed ? p.toFixed(4) : (p > 0 ? 1 : 0));
          const f = clamp(tr.hasta != null ? Math.min(F.fr, tr.hasta) : F.fr);
          prg.setAttribute('stroke-dasharray', f.toFixed(4) + ' 1');
          prg.setAttribute('opacity', (f > 0.001 && F.a > 0 ? 0.62 : 0).toFixed(3));
        });
        return;
      }
      const base = S('line', { x1: tr.x0, y1: tr.y, x2: tr.x0, y2: tr.y, stroke: C.track, 'stroke-width': 3, 'stroke-linecap': 'round' }, L.track);
      const prg = S('line', { x1: tr.x0, y1: tr.y, x2: tr.x0, y2: tr.y, stroke: C.gold, 'stroke-width': 3, 'stroke-linecap': 'round', opacity: 0 }, L.track);
      if (tr.dashed) { base.setAttribute('stroke-dasharray', '1 13'); prg.setAttribute('stroke-dasharray', '1 13'); base.setAttribute('stroke-width', 4); prg.setAttribute('stroke-width', 4); }
      const a0 = tr.inAt != null ? tr.inAt : 1.0 + i * 0.15, a1 = a0 + 0.75;
      ups.push(t => {
        const p = ease.inOutCubic(prog(t, a0, a1));
        base.setAttribute('x2', f2(lerp(tr.x0, tr.x1, p)));
        base.setAttribute('opacity', p > 0 ? 1 : 0);
        const fx = clamp(F.x, tr.x0, tr.x1);
        prg.setAttribute('x2', f2(fx));
        prg.setAttribute('opacity', (fx > tr.x0 + 1 && F.a > 0 ? 0.62 : 0).toFixed(3));
      });
    });

    // ---- Nodos (etapas) ----
    function makeNode(o, idx) {
      const g = S('g', null, L.nodes);
      const pulse = S('circle', { r: 34, fill: 'none', stroke: C.goldL, 'stroke-width': 2, opacity: 0 }, g);
      const halo = S('circle', { r: 46, fill: C.gold, filter: 'url(#blur20)', opacity: 0 }, g);
      const core = S('circle', { r: 34, fill: C.node, stroke: C.faint, 'stroke-width': 2.5 }, g);
      if (o.dashed) core.setAttribute('stroke-dasharray', '6 6');
      const tint = S('circle', { r: 32.5, fill: C.gold, opacity: 0 }, g);
      const dot = S('circle', { r: 4.5, fill: C.dim, opacity: 0.9 }, g);
      const check = S('path', { d: 'M-10 1 L-3 8 L11 -7', fill: 'none', stroke: C.goldL, 'stroke-width': 3.5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', opacity: 0 }, g);
      const lab = D('nlabel' + (o.labelPos === 'right' || o.labelPos === 'left' ? ' right' : ''), html,
        (o.num ? '<div class="num">' + o.num + '</div>' : '') + '<div class="name">' + o.name + '</div>' + (o.sub ? '<div class="sub">' + o.sub + '</div>' : ''));
      if (o.labelPos === 'right') { lab.style.left = (o.x + 54) + 'px'; lab.style.top = (o.y - 30) + 'px'; }
      else if (o.labelPos === 'left') { lab.style.left = (o.x - 54 - 420) + 'px'; lab.style.top = (o.y - 30) + 'px'; lab.style.textAlign = 'right'; }
      else if (o.labelPos === 'below') { lab.style.left = (o.x - 135) + 'px'; lab.style.top = (o.y + 54) + 'px'; }
      else { lab.style.left = (o.x - 135) + 'px'; lab.style.bottom = (H - (o.y - 54)) + 'px'; }
      const numEl = lab.querySelector('.num'), nameEl = lab.querySelector('.name');
      const ap = o.appear != null ? o.appear : 1.1 + idx * 0.07;
      ups.push(t => {
        const a = prog(t, ap, ap + 0.5), ab = ease.outBack(a);
        set(g, { transform: 'translate(' + o.x + ',' + o.y + ') scale(' + (0.6 + 0.4 * ab).toFixed(4) + ')', opacity: clamp(a * 2).toFixed(4) });
        const la = ease.outCubic(prog(t, ap + 0.1, ap + 0.55));
        lab.style.opacity = la.toFixed(4);
        lab.style.transform = 'translateY(' + f2((1 - la) * 12) + 'px)';
        const lit = ease.outCubic(prog(t, o.arr, o.arr + 0.35));
        const left = o.next != null ? ease.inOutSine(prog(t, o.next, o.next + 0.45)) : 0;
        const cur = lit * (1 - left), passed = lit * left;
        const strokeC = o.ghost ? mix(C.faint, C.goldL, lit * 0.8) : mix(C.faint, C.gold, lit);
        set(core, { stroke: strokeC, 'stroke-width': (2.5 + 1.2 * cur).toFixed(2) });
        tint.setAttribute('opacity', (0.07 * cur + 0.16 * passed).toFixed(4));
        halo.setAttribute('opacity', ((o.ghost ? 0.25 : 0.42) * cur * (0.88 + 0.12 * Math.sin(t * 5))).toFixed(4));
        const pp = prog(t, o.arr, o.arr + 0.95);
        set(pulse, { r: f2(34 + 26 * ease.outCubic(pp)), opacity: (pp > 0 && pp < 1 ? 0.8 * (1 - pp) : 0).toFixed(4) });
        dot.setAttribute('opacity', (0.9 * (1 - lit)).toFixed(4));
        check.setAttribute('opacity', (o.noCheck ? 0 : passed).toFixed(4));
        const nameC = passed > 0 ? mix(mix(C.pend, C.ink, lit), C.pass, passed) : mix(C.pend, C.ink, lit);
        nameEl.style.color = nameC;
        if (numEl) numEl.style.color = mix(C.dim, C.goldL, lit);
      });
      return o;
    }
    (cfg.nodes || []).forEach(makeNode);
    api.makeNode = makeNode;

    // ---- Panel de la etapa ----
    // cfg.limpio: composición SIN estaciones (gramática §5.bis). Los paneles ocupan la pantalla entera, sin caja,
    // borde ni sombra, y entran desde t = 0; el protagonista se construye en cfg.extra.
    if (cfg.limpio) { cfg.panel = cfg.panel || { x: 0, y: 0, w: W, h: H }; if (cfg.panelIn == null) cfg.panelIn = 0; }
    const P = cfg.panel;
    if (P) {
    const COL = P.forma === 'columna';
    const box = D('pbox' + (COL ? ' columna' : '') + (cfg.limpio ? ' limpio' : ''), root);
    Object.assign(box.style, { left: P.x + 'px', top: P.y + 'px', width: P.w + 'px', height: P.h + 'px' });
    const edge = D('pedge', root); const ptr = D('pptr', root);
    if (COL) { edge.style.left = (P.x - 1) + 'px'; ptr.style.left = P.x + 'px'; edge.classList.add('v'); ptr.classList.add('v'); }
    else { edge.style.top = (P.y - 1) + 'px'; ptr.style.top = P.y + 'px'; }
    const pIn = cfg.panelIn != null ? cfg.panelIn : 1.45;
    const pk = cfg.pointer || []; // [{t, x}] o, con forma 'columna', [{t, y}]
    const KEY = COL ? 'y' : 'x', LO = COL ? P.y : P.x, HI = COL ? P.y + P.h : P.x + P.w;
    function ptrX(t) {
      if (!pk.length) return -9999;
      let x = clamp(pk[0][KEY], LO + 40, HI - 40);
      for (let i = 1; i < pk.length; i++) { const p = ease.inOutCubic(prog(t, pk[i].t, pk[i].t + 0.5)); x = lerp(x, clamp(pk[i][KEY], LO + 40, HI - 40), p); }
      return x;
    }
    ups.push(t => {
      const a = ease.outCubic(prog(t, pIn, pIn + 0.6));
      box.style.opacity = a.toFixed(4); box.style.transform = 'translateY(' + f2((1 - a) * 26) + 'px)';
      const pa = pk.length ? ease.outCubic(prog(t, pk[0].t - 0.05, pk[0].t + 0.35)) : 0;
      const x = ptrX(t);
      ptr.style[COL ? 'top' : 'left'] = f2(x) + 'px'; ptr.style.opacity = (pa * a).toFixed(4);
      const e0 = Math.max(x - 130, LO + 24), e1 = Math.min(x + 130, HI - 24);
      if (COL) { edge.style.top = f2(e0 + 130) + 'px'; edge.style.height = f2(Math.max(0, e1 - e0)) + 'px'; edge.style.backgroundPosition = '0 ' + f2(-(e0 - (x - 130))) + 'px'; }
      else { edge.style.left = f2(e0 + 130) + 'px'; edge.style.width = f2(Math.max(0, e1 - e0)) + 'px'; edge.style.backgroundPosition = f2(-(e0 - (x - 130))) + 'px 0'; }
      edge.style.opacity = (pa * a).toFixed(4);
    });

    function makeChip(parent, c, i) {
      const e = D('chip ' + (c.k || 'info'), parent);
      if (c.k === 'state') D('cdot', e);
      const tx = D('', e); tx.style.display = 'inline'; tx.textContent = c.t;
      const at = c.at != null ? c.at : 0.4 + i * 0.16;
      return lt => {
        const p = prog(lt, at, at + 0.45), b = ease.outBack(p);
        e.style.opacity = clamp(p * 2.2).toFixed(4);
        e.style.transform = 'translateY(' + f2((1 - clamp(b)) * 14) + 'px) scale(' + (0.9 + 0.1 * b).toFixed(4) + ')';
        let txt = c.t, flash = c.k === 'state' ? clamp(1 - (lt - at) / 0.7) * (lt >= at ? 1 : 0) : 0;
        if (c.swap) for (const s of c.swap) { if (lt >= s.at) { txt = s.t; const fz = 1 - (lt - s.at) / 0.7; if (fz > 0) flash = Math.max(flash, fz); } }
        if (tx.textContent !== txt) tx.textContent = txt;
        e.style.boxShadow = flash > 0 ? '0 0 ' + f2(28 * flash) + 'px ' + rgba(C.goldL, (0.55 * flash).toFixed(3)) : 'none';
        if (c.k === 'state') e.style.background = rgba(C.gold, (0.15 + 0.25 * flash).toFixed(3));
      };
    }

    cfg.panels.forEach(p => {
      const pc = D('pc', box);
      const parts = [];
      let artEl;
      if (p.full) { artEl = D('pc-full', pc); }
      else {
        const col = D('pc-col', pc);
        const eb = D('pc-eyebrow', col, p.eyebrow || '');
        const ph = D('pc-phrase', col, p.phrase);
        const chips = D('pc-chips', col);
        const cu = (p.chips || []).map((c, i) => makeChip(chips, c, i));
        artEl = D('pc-art', pc);
        parts.push(lt => {
          const e1 = ease.outCubic(prog(lt, 0.08, 0.5));
          eb.style.opacity = e1.toFixed(4);
          const e2 = ease.outCubic(prog(lt, 0.14, 0.62));
          ph.style.opacity = e2.toFixed(4); ph.style.transform = 'translateY(' + f2((1 - e2) * 30) + 'px)';
          for (const u of cu) u(lt);
        });
      }
      let artUp = null;
      if (p.html) { artEl.innerHTML = p.html; const au = auto(artEl); artUp = p.tick ? (lt => { au(lt); p.tick(lt, artEl, api); }) : au; if (p.init) p.init(artEl, api); }
      const tin = p.t0 + 0.06, tout = p.t1;
      ups.push(t => {
        if (t < tin - 0.001 || (tout != null && t > tout + 0.3)) { pc.style.display = 'none'; return; }
        pc.style.display = 'block';
        const a = ease.outCubic(prog(t, tin, tin + 0.45));
        const o = tout == null ? 0 : ease.inOutSine(prog(t, tout - 0.04, tout + 0.22));
        pc.style.opacity = (a * (1 - o)).toFixed(4);
        pc.style.transform = 'translateY(' + f2(-o * 14) + 'px)';
        const lt = t - p.t0;
        for (const u of parts) u(lt);
        if (artUp) artUp(lt);
      });
    });
    }

    // ---- Tramos (encabezados de grupo) ----
    (cfg.tramos || []).forEach((g, i) => {
      const ln = S('path', { d: 'M' + g.x0 + ' ' + (g.y + 14) + ' V' + g.y + ' H' + g.x1 + ' V' + (g.y + 14), fill: 'none', stroke: C.line, 'stroke-width': 2 }, L.track);
      const lb = D('tramo', html, '<b>' + g.tag + '</b>' + g.label);
      lb.style.left = g.x0 + 'px'; lb.style.top = (g.y - 44) + 'px';
      const ap = g.appear != null ? g.appear : 1.25 + i * 0.15;
      ups.push(t => {
        const a = ease.outCubic(prog(t, ap, ap + 0.5));
        ln.setAttribute('opacity', a.toFixed(4)); lb.style.opacity = a.toFixed(4);
        const lit = g.lit ? clamp(prog(t, g.lit[0], g.lit[0] + 0.4) - prog(t, g.lit[1], g.lit[1] + 0.4)) : 0;
        ln.setAttribute('stroke', mix(C.line, C.gold, lit));
        lb.style.color = mix(C.mute, C.ink, lit);
      });
    });

    if (cfg.extra) cfg.extra(api);

    // ---- Salida limpia: queda solo el fondo ----
    const D0 = cfg.duration;
    ups.push(t => { root.style.opacity = (1 - ease.inOutSine(prog(t, D0 - 1.0, D0 - 0.42))).toFixed(4); });

    window.DURATION = D0;
    // Momentos que la hoja de contactos debe enseñar: la cabecera, cada panel ya asentado y el resultado.
    // Así ninguna etapa se queda fuera, dure lo que dure (un muestreo fijo cada 2 s se saltaba etapas).
    window.MOMENTOS = [1.0].concat((cfg.panels || []).map(p => +(p.t0 + (p.full ? 1.6 : 0.9)).toFixed(2)))
      .filter(t => t < D0 - 0.1);
    window.FONDO = C.bg;
    window.seek = function (t) { for (const u of ups) u(t); return t; };
    window.seek(0);
  }

  function run(cfg) {
    aplicarTema(cfg.tema);
    const go = () => {
      build(cfg);
      // Fotos de una maqueta (<img>, o <image> de SVG): se esperan CARGADAS antes de __ready. Sin esto, los primeros
      // fotogramas pueden salir sin la foto y el MP4 deja de ser determinista (references/imagenes.md §4).
      // Se espera `load`, no `decode()`: decode() no resuelve en una pestaña en segundo plano (medido 2026-10-26).
      // Tope de 10 s: una foto rota se avisa en consola, nunca cuelga el render.
      const fotos = [...document.querySelectorAll('img, image')].map(el => {
        const esImg = el.tagName.toLowerCase() === 'img';
        const src = esImg ? el.currentSrc || el.src
          : el.getAttribute('href') || el.getAttributeNS('http://www.w3.org/1999/xlink', 'href');
        if (!src) return null;
        const i = esImg ? el : new Image();
        return new Promise(ok => {
          // Una sola vez: sin la bandera, el tope de 10 s se disparaba DESPUÉS del load y ensuciaba la consola
          // a mitad de un render largo (que entonces fallaba al terminar). Medido 2026-10-30, guía de traslado.
          let hecho = false;
          const fin = bien => { if (hecho) return; hecho = true; if (!bien) console.error('Imagen que no carga en el flujo: ' + src); ok(); };
          if (esImg && i.complete) return fin(i.naturalWidth > 0);
          i.addEventListener('load', () => fin(true), { once: true });
          i.addEventListener('error', () => fin(false), { once: true });
          setTimeout(() => fin(false), 10000);
          if (!esImg) i.src = src;
        });
      });
      Promise.all(fotos).then(() => { window.seek(0); window.__ready = true; });
    };
    const fonts = ['600 50px Bahnschrift', '400 34px Bahnschrift', '400 24px Consolas'];
    Promise.all(fonts.map(f => document.fonts.load(f))).then(() => document.fonts.ready).then(go, go);
  }

  // SV.tema(t): aplica el tema ya y devuelve C, para que el flujo construya sus maquetas con los colores del tema
  // antes de llamar a SV.run (que lo vuelve a aplicar con cfg.tema; da igual hacerlo dos veces).
  const tema = t => { aplicarTema(t); return C; };

  // ---- Ayudantes del DOCUMENTO PROTAGONISTA (gramática §5.bis; nacieron en la guía de traslado, 2026-10-30) ----

  // SV.poses(K): K = [[t, v1, v2, …], …] en orden de t. Devuelve f(t) → [v1, v2, …] interpolado con inOutCubic.
  // Para un objeto que vive todo el video: [t, x, y, escala, opacidad] y cada cambio de panel es una pose nueva.
  function poses(K, e) {
    e = e || ease.inOutCubic;
    return t => {
      if (t <= K[0][0]) return K[0].slice(1);
      for (let i = 1; i < K.length; i++) if (t <= K[i][0]) {
        const a = K[i - 1], b = K[i], p = e(prog(t, a[0], b[0]));
        return a.slice(1).map((v, j) => lerp(v, b[j + 1], p));
      }
      return K[K.length - 1].slice(1);
    };
  }
  // SV.escribir(campos, t0, o): campos = [{ el, texto, pausa? }]; los escribe uno tras otro desde t0, como si alguien
  // tecleara. Ritmo medido: 0,011 s por carácter + 0,12 s por campo + 0,06 s entre campos (a 0,018 s no cabía).
  // Devuelve { fin, up(t) }: fin es cuando termina el último (para encadenar lo siguiente); up va en api.ups.
  function escribir(campos, t0, o) {
    o = o || {};
    const pc = o.porCaracter || 0.011, base = o.base || 0.12, hueco = o.hueco || 0.06;
    let cur = t0;
    const v = campos.map(c => { const d = base + c.texto.length * pc, w = [cur, cur + d]; cur += d + hueco + (c.pausa || 0); return w; });
    return {
      fin: cur, ventanas: v,
      up: t => campos.forEach((c, i) => {
        const s = c.texto.slice(0, Math.round(c.texto.length * prog(t, v[i][0], v[i][1])));
        if (c.el.textContent !== s) c.el.textContent = s;
      })
    };
  }
  // SV.trazo(path): prepara un trazo para dibujarse (firma, subrayado, ruta). Devuelve up(t, a, dur).
  // Oculto hasta su instante: con linecap redondo, un dasharray en 1 deja un PUNTO visible antes de empezar.
  function trazo(pe) {
    pe.setAttribute('pathLength', '1'); pe.style.strokeDasharray = '1';
    return (t, a, du) => { pe.style.opacity = t < a ? '0' : '1'; pe.style.strokeDashoffset = (1 - ease.inOutSine(prog(t, a, a + (du || 0.9)))).toFixed(4); };
  }
  // SV.sello(o): SVG de un sello circular con texto en arco (arriba y abajo) y un visto al centro. El texto va por
  // textPath: recto se monta sobre el anillo. El de abajo va en sentido antihorario para leerse derecho.
  // o = { arriba, abajo, color, tinta, id }. Se anima con SV.golpe(g, t, a). Regla PRC-003: el sello, al final.
  function sello(o) {
    const id = o.id || 'sello', col = o.color || C.gold, tx = o.tinta || C.goldTxt;
    return '<svg viewBox="-105 -105 210 210" style="overflow:visible"><g class="' + id + '"><circle r="96" fill="none" stroke="' + col + '" stroke-width="6"/>' +
      '<circle r="82" fill="none" stroke="' + col + '" stroke-width="2" stroke-dasharray="4 6"/>' +
      '<path id="' + id + 'A" d="M-62 0 A62 62 0 0 1 62 0" fill="none"/><path id="' + id + 'B" d="M-70 0 A70 70 0 0 0 70 0" fill="none"/>' +
      '<text font-size="19" font-family="Consolas" fill="' + tx + '" letter-spacing="2"><textPath href="#' + id + 'A" startOffset="50%" text-anchor="middle">' + (o.arriba || '') + '</textPath></text>' +
      '<path d="M-26 4 L-8 22 L28 -14" fill="none" stroke="' + tx + '" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>' +
      '<text font-size="19" font-family="Consolas" fill="' + tx + '" letter-spacing="2"><textPath href="#' + id + 'B" startOffset="50%" text-anchor="middle">' + (o.abajo || '') + '</textPath></text></g></svg>';
  }
  // SV.golpe(g, t, a): el sello cae desde grande y girado, y se asienta en 0,3 s.
  function golpe(g, t, a) {
    const p = prog(t, a, a + 0.3);
    g.setAttribute('opacity', (t < a ? 0 : clamp(p * 2.5)).toFixed(3));
    g.setAttribute('transform', 'scale(' + (1.6 - 0.6 * ease.outCubic(p)).toFixed(3) + ') rotate(' + (-18 + 10 * ease.outCubic(p)).toFixed(2) + ')');
  }

  window.SV = { run, tema, C, TEMAS, derivar, clamp, lerp, prog, ease, mix, rgba, checkSvg, composicion: (t, n, o) => medir(composicion(t, n, o)), fraccion, tiempos, rutaFr, route,
    poses, escribir, trazo, sello, golpe };
})();
