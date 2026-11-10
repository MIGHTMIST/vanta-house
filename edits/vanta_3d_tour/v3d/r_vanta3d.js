// r_vanta3d.js - Vanta House (Blackstone Real Estate, Naguru, Kampala) - REALISM build.
// Same API as vanta3d.js (buildVanta, makeRenderer, makeSky, lighting, makePeople, makeCars, parkedCars, textSprite, planTexture,
// explodeFloors, setFloorsVisible, viewportSize, offsetPoly, levelOf, GOLD...) plus extras: makeEnvironment, makeContext, makeTrees,
// glass shaders, procedural textures (TEX), focusShadow(), setSun(), APT (apartment corner coordinates shared with r_interior.js).
// Metres, y up, ground = 0. x = east, z = SOUTH (plan north is -z). Origin: centre between the two blocks.
export const GOLD = '#B08A4E', GOLD_HI = '#D6B26E', IVORY = '#FAF8F3', INK = '#101012';
let T; // THREE namespace

// ------------------------------------------------------------------ site-plan tracing (px of site.jpg -> m)
const SC = 1 / 18.3, OX = 400, OY = 600;
const pm = (p) => [(p[0] - OX) * SC, (p[1] - OY) * SC];
const PM = (arr) => arr.map(pm);
const PLOT_PX = [[190, 170], [640, 188], [1354, 1005], [47, 1002]];
const NORTH_PX = [[190,265],[262,265],[262,218],[430,218],[430,265],[597,265],[597,410],[487,410],[487,540],[523,540],[523,608],[190,608]];
// south block: east step moved to z=10.9 (px 799.5) so the typical 2-bed corner apartment of the approved plan fits; extra collinear
// vertex at x=8.1 (px 548.2) splits the north face at the apartment's party wall.
const XA = 8.1, ZS = 10.9;
const SOUTH_PX = [[150,635],[488,635],[488,700],[517,700],[517,635],[OX + XA / SC,635],[707,635],[707,OY + ZS / SC],[690,OY + ZS / SC],[690,940],[455,940],[455,975],[372,975],[372,865],[340,865],[340,945],[150,945]];
const DRIVE_PX = [[487,412],[597,412],[597,545],[947,545],[1039,640],[1060,665],[1060,975],[707,975],[707,640],[523,640],[523,545],[487,545]];
const POOL_DECK_PX = [[630,222],[630,490],[650,518],[925,518]];
const POOL_WATER_PX = [[650,250],[650,445],[668,468],[838,468]];
const RAMP_PX = [[1047,792],[1158,792],[1280,930],[1047,930]];
const GUARD_PX = { c: [887, 664], w: 205, d: 58 };
const GATE_PX = [985, 577];
const xDiag = (y) => 640 + 714 * (y - 188) / 817;

export const LEVELS = { ground: 0, basement: -3.3, f1: 4.0, step: 3.3, roof: 40.3, parapet: 1.0 };
export const levelOf = (n) => n === 0 ? 0 : 4.0 + (n - 1) * 3.3;
// Apartment corner of the south block (typical 2-bed unit, plan grid E-G / rows 2-3), shared with r_interior.js
export const APT = { level: 6, x0: XA, x1: 16.78, z0: 1.91, z1: ZS, // outer box
  liftX: -1.0, corrZ: [5.9, 7.5], lobby: { x0: 6.55, x1: 16.6, z0: 2.05, z1: 10.7 } };
// custom east/north elevation rhythm of the corner (all floors): openings in local metres
export const CORNER = {
  north: [ { a: 9.15, b: 10.75, y0: .9, y1: 2.45, kind: 'win' }, { a: 11.9, b: 12.5, y0: 1.7, y1: 2.3, kind: 'win', real: 1 }, { a: 13.85, b: 15.75, y0: .55, y1: 2.45, kind: 'win', real: 1 } ],
  east: [ { a: 2.55, b: 5.25, y0: 0, y1: 2.4, kind: 'door', real: 1, balc: [2.2, 5.6, 1.45] }, { a: 6.25, b: 7.05, y0: 1.0, y1: 2.45, kind: 'win', real: 1 },

          { a: 7.55, b: 10.55, y0: 0, y1: 2.45, kind: 'door', real: 1, balc: [7.3, 10.85, 1.8] } ],
};

// ------------------------------------------------------------------ geometry utils
const area2 = (p) => { let a = 0; for (let i = 0; i < p.length; i++) { const q = p[(i + 1) % p.length]; a += p[i][0] * q[1] - q[0] * p[i][1]; } return a / 2; };
function edgeNormal(a, b, A) { const dx = b[0] - a[0], dz = b[1] - a[1], L = Math.hypot(dx, dz); return A > 0 ? [dz / L, -dx / L] : [-dz / L, dx / L]; }
export function offsetPoly(p, d) {
  const A = area2(p), n = p.length, out = [];
  for (let i = 0; i < n; i++) {
    const a = p[(i + n - 1) % n], b = p[i], c = p[(i + 1) % n];
    const n1 = edgeNormal(a, b, A), n2 = edgeNormal(b, c, A), k = 1 + n1[0] * n2[0] + n1[1] * n2[1];
    out.push([b[0] + (n1[0] + n2[0]) * d / k, b[1] + (n1[1] + n2[1]) * d / k]);
  }
  return out;
}
export function inPoly(pt, p) { let c = false; for (let i = 0, j = p.length - 1; i < p.length; j = i++) { if (((p[i][1] > pt[1]) !== (p[j][1] > pt[1])) && (pt[0] < (p[j][0] - p[i][0]) * (pt[1] - p[i][1]) / (p[j][1] - p[i][1]) + p[i][0])) c = !c; } return c; }
const centroid = (p) => { let x = 0, z = 0; p.forEach(q => { x += q[0]; z += q[1]; }); return [x / p.length, z / p.length]; };
const bbox = (p) => { let a = [1e9, 1e9], b = [-1e9, -1e9]; p.forEach(q => { a = [Math.min(a[0], q[0]), Math.min(a[1], q[1])]; b = [Math.max(b[0], q[0]), Math.max(b[1], q[1])]; }); return { min: a, max: b }; };
function shapeOf(p, holes) {
  const s = new T.Shape(); p.forEach((q, i) => i ? s.lineTo(q[0], -q[1]) : s.moveTo(q[0], -q[1])); s.closePath();
  (holes || []).forEach(h => { const hp = new T.Path(); h.forEach((q, i) => i ? hp.lineTo(q[0], -q[1]) : hp.moveTo(q[0], -q[1])); hp.closePath(); s.holes.push(hp); });
  return s;
}
export function flatGeo(p, holes) { const g = new T.ShapeGeometry(shapeOf(p, holes)); g.rotateX(-Math.PI / 2); return g; }
export function prismGeo(p, y0, y1, holes) { const g = new T.ExtrudeGeometry(shapeOf(p, holes), { depth: y1 - y0, bevelEnabled: false, steps: 1 }); g.rotateX(-Math.PI / 2); g.translate(0, y0, 0); return g; }
function mesh(g, m, o = {}) { const x = new T.Mesh(g, m); x.castShadow = o.cast !== false; x.receiveShadow = o.recv !== false; if (o.name) x.name = o.name; return x; }
function box(w, h, d, m, x, y, z, o = {}) { const b = mesh(new T.BoxGeometry(w, h, d), m, o); b.position.set(x, y, z); return b; }
export const rnd = (seed) => () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296;
const smooth = (a, b, x) => { const t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

// ------------------------------------------------------------------ procedural noise + canvas textures
function hash2(x, y, s) { let h = (Math.imul(x | 0, 374761393) + Math.imul(y | 0, 668265263) + Math.imul(s | 0, 982451653)) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; }
function vnoise(x, y, s, per) {
  const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi, u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
  const P = (a) => per ? ((a % per) + per) % per : a;
  const a = hash2(P(xi), P(yi), s), b = hash2(P(xi + 1), P(yi), s), c = hash2(P(xi), P(yi + 1), s), d = hash2(P(xi + 1), P(yi + 1), s);
  return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
}
export function fbm(x, y, s = 0, oct = 4, per = 0) { let f = 0, a = .5, fr = 1, n = 0; for (let i = 0; i < oct; i++) { f += a * vnoise(x * fr, y * fr, s + i * 17, per ? per * fr : 0); n += a; a *= .5; fr *= 2; } return f / n; }
const hexRGB = (h) => { const c = parseInt(h.slice(1), 16); return [(c >> 16) & 255, (c >> 8) & 255, c & 255]; };
// canvas -> texture.  fn(g, w, h) draws.  o: {rep:[x,y], srgb, aniso}
export function canvasTex(w, h, fn, o = {}) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); fn(g, w, h, c);
  const t = new T.CanvasTexture(c); t.wrapS = t.wrapT = T.RepeatWrapping; t.anisotropy = o.aniso ?? 8; if (o.srgb !== false) t.colorSpace = T.SRGBColorSpace;
  if (o.rep) t.repeat.set(o.rep[0], o.rep[1]); t.generateMipmaps = true; t.minFilter = T.LinearMipmapLinearFilter; return t;
}
// fill with per-pixel function (x,y) -> [r,g,b,(a)] (0..255) ; tileable noise via per-period
function pixFill(g, w, h, f) { const id = g.createImageData(w, h), d = id.data; for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const c = f(x, y), i = (y * w + x) * 4; d[i] = c[0]; d[i + 1] = c[1]; d[i + 2] = c[2]; d[i + 3] = c.length > 3 ? c[3] : 255; } g.putImageData(id, 0, 0); }
const mixc = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
const mulc = (a, k) => [a[0] * k, a[1] * k, a[2] * k];

export const TEX = {};
function buildTextures() {
  if (TEX.ready) return TEX;
  // stone-look facade cladding (cream), 3 m x 3.3 m tile: 1.5 m x 0.825 m panels with 6 mm joints, gentle tone variation
  TEX.plaster = canvasTex(512, 512, (g, w, h) => {
    const base = hexRGB('#DCD6C9'); pixFill(g, w, h, (x, y) => { const n = fbm(x / 64, y / 64, 3, 4, 8), m = fbm(x / 9, y / 9, 9, 2, 57); const panel = hash2(Math.floor(x / 256), Math.floor((y) / 128), 5);
      const streak = Math.pow(fbm(x / 3, y / 140, 15, 3, 0), 3) * smooth(.0, .5, ((y % 170) / 170)) * .14;
      return mulc(base, .95 + n * .06 + m * .02 + panel * .025 - streak); });
    g.fillStyle = 'rgba(70,60,45,.32)'; for (let y = 0; y < h; y += 128) g.fillRect(0, y, w, 2); for (let x = 0; x < w; x += 256) g.fillRect(x, 0, 2, h);
  }, { rep: [1 / 3, 1 / 3.3] });
  TEX.plasterDark = canvasTex(256, 256, (g, w, h) => { const base = hexRGB('#4A4C51'); pixFill(g, w, h, (x, y) => mulc(base, .9 + fbm(x / 32, y / 32, 4, 4, 8) * .2));
    g.fillStyle = 'rgba(0,0,0,.35)'; for (let y = 0; y < h; y += 64) g.fillRect(0, y, w, 2); for (let x = 0; x < w; x += 128) g.fillRect(x, 0, 2, h); }, { rep: [1 / 2.4, 1 / 2.4] });
  // charcoal metal panel with vertical standing seams (sign band, accent strips)
  TEX.seam = canvasTex(256, 64, (g, w, h) => { pixFill(g, w, h, (x, y) => { const k = .9 + fbm(x / 40, y / 8, 2, 3, 6) * .14; return mulc([40, 41, 45], k); });
    for (let x = 0; x < w; x += 32) { g.fillStyle = 'rgba(255,255,255,.07)'; g.fillRect(x, 0, 2, h); g.fillStyle = 'rgba(0,0,0,.4)'; g.fillRect(x + 2, 0, 2, h); } }, { rep: [1 / 2.4, 1] });
  TEX.concrete = canvasTex(256, 256, (g, w, h) => { const base = hexRGB('#A3A19B'); pixFill(g, w, h, (x, y) => mulc(base, .85 + fbm(x / 24, y / 24, 7, 5, 11) * .3)); }, { rep: [1 / 4, 1 / 4] });
  // large-format pavers 0.6 x 0.3 (running bond), joints, tone variation per paver
  TEX.paver = canvasTex(512, 512, (g, w, h) => { const base = hexRGB('#C9C3B5'); pixFill(g, w, h, (x, y) => { const r = Math.floor(y / 64), c = Math.floor((x + (r % 2) * 64) / 128); const v = hash2(c, r, 11);
      return mulc(base, .88 + v * .12 + fbm(x / 20, y / 20, 13, 3, 26) * .08); });
    g.fillStyle = 'rgba(60,55,45,.55)'; for (let y = 0; y < h; y += 64) { g.fillRect(0, y, w, 2); const off = ((y / 64) % 2) * 64; for (let x = off; x < w + 128; x += 128) g.fillRect(x % w, y, 2, 64); } }, { rep: [1 / 2.4, 1 / 2.4] });
  TEX.paverPale = canvasTex(512, 512, (g, w, h) => { const base = hexRGB('#E4DED0'); pixFill(g, w, h, (x, y) => { const c = Math.floor(x / 128), r = Math.floor(y / 128), v = hash2(c, r, 21);
      return mulc(base, .92 + v * .08 + fbm(x / 30, y / 30, 23, 3, 17) * .06); });
    g.fillStyle = 'rgba(90,80,65,.45)'; for (let y = 0; y < h; y += 128) g.fillRect(0, y, w, 2); for (let x = 0; x < w; x += 128) g.fillRect(x, 0, 2, h); }, { rep: [1 / 2.4, 1 / 2.4] });
  TEX.asphalt = canvasTex(512, 512, (g, w, h) => { pixFill(g, w, h, (x, y) => { const n = fbm(x / 6, y / 6, 31, 2, 85), m = fbm(x / 70, y / 70, 37, 3, 7), s = hash2(x, y, 3) > .985 ? 1.25 : 1;
      return mulc([66, 67, 70], (.8 + n * .25 + m * .18) * s); }); }, { rep: [1 / 6, 1 / 6] });
  TEX.grass = canvasTex(512, 512, (g, w, h) => { pixFill(g, w, h, (x, y) => { const n = fbm(x / 40, y / 40, 41, 4, 13), f = fbm(x / 3, y / 3, 43, 2, 171), b = hash2(x, y, 7);
      return mixc([82, 112, 52], [128, 146, 70], n * .9 + (b > .8 ? .15 : 0)).map(v => v * (.84 + f * .3)); }); }, { rep: [1 / 7, 1 / 7] });
  TEX.soil = canvasTex(256, 256, (g, w, h) => { pixFill(g, w, h, (x, y) => mixc([92, 64, 44], [128, 92, 62], fbm(x / 16, y / 16, 47, 4, 16))); }, { rep: [1 / 3, 1 / 3] });
  TEX.roof = canvasTex(256, 256, (g, w, h) => { pixFill(g, w, h, (x, y) => mulc([70, 72, 74], .85 + fbm(x / 20, y / 20, 51, 4, 13) * .25)); g.fillStyle = 'rgba(0,0,0,.2)'; for (let y = 0; y < h; y += 64) g.fillRect(0, y, w, 1); }, { rep: [1 / 4, 1 / 4] });
  TEX.poolTile = canvasTex(256, 256, (g, w, h) => { pixFill(g, w, h, (x, y) => { const v = hash2(Math.floor(x / 32), Math.floor(y / 32), 61); return mixc([150, 214, 222], [196, 236, 238], v * .8); });
    g.fillStyle = 'rgba(255,255,255,.7)'; for (let y = 0; y < h; y += 32) g.fillRect(0, y, w, 2); for (let x = 0; x < w; x += 32) g.fillRect(x, 0, 2, h); }, { rep: [1 / 0.8, 1 / 0.8] });
  TEX.bark = canvasTex(64, 256, (g, w, h) => { pixFill(g, w, h, (x, y) => { const ring = Math.pow(Math.abs(Math.sin(y / 256 * Math.PI * 14)), 6); return mulc([118, 100, 80], .7 + fbm(x / 8, y / 8, 71, 3, 8) * .35 - ring * .25); }); }, { rep: [1, 1] });
  // palm frond card: midrib + leaflets, alpha
  TEX.frond = canvasTex(256, 512, (g, w, h) => {
    g.clearRect(0, 0, w, h); const R = rnd(91);
    for (let i = 0; i < 70; i++) { const t = i / 70, y = h * (.04 + t * .94), len = w * .5 * Math.sin(Math.PI * Math.min(1, t * 1.05 + .08)) * (.85 + R() * .2);
      for (const s of [-1, 1]) { const col = `hsl(${88 + R() * 16},${38 + R() * 12}%,${20 + R() * 12 + t * 6}%)`; g.strokeStyle = col; g.lineWidth = 3.2 + (1 - t) * 2; g.beginPath(); g.moveTo(w / 2, y); g.quadraticCurveTo(w / 2 + s * len * .5, y - 10, w / 2 + s * len, y + 26 + t * 18); g.stroke(); } }
    g.strokeStyle = '#6d6a3e'; g.lineWidth = 5; g.beginPath(); g.moveTo(w / 2, 0); g.lineTo(w / 2, h); g.stroke();
  }, { aniso: 4 });
  // red murram verge with patchy grass, tyre-worn edge
  TEX.verge = canvasTex(512, 512, (g, w, h) => pixFill(g, w, h, (x, y) => { const n = fbm(x / 50, y / 50, 81, 4, 10), m = fbm(x / 6, y / 6, 83, 2, 85), gr = smooth(.42, .62, n);
    return mixc(mulc([138, 96, 72], .85 + m * .25), mulc([98, 114, 66], .8 + m * .3), gr); }), { rep: [1 / 5, 1 / 5] });
  // rubble-stone / crazy-paving cladding (ochre + brown stones, dark joints)
  TEX.rubble = canvasTex(512, 256, (g, w, h) => { g.fillStyle = '#3d342b'; g.fillRect(0, 0, w, h); const R = rnd(7); for (let i = 0; i < 260; i++) { const x = R() * w, y = R() * h, r = 14 + R() * 22; g.fillStyle = `hsl(${24 + R() * 16},${30 + R() * 25}%,${42 + R() * 22}%)`; g.beginPath(); const k = 5 + (R() * 3 | 0); for (let j = 0; j < k; j++) { const a = j / k * 6.283 + R() * .5, rr = r * (.7 + R() * .4); g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr * .7); } g.closePath(); g.fill(); } }, { rep: [1 / 1.6, 1 / .8] });
  TEX.ochre = canvasTex(256, 256, (g, w, h) => pixFill(g, w, h, (x, y) => mulc([206, 150, 88], .88 + fbm(x / 30, y / 30, 91, 4, 8) * .2 - Math.pow(fbm(x / 3, y / 90, 93, 2, 0), 3) * .2)), { rep: [1 / 3, 1 / 3] });
  TEX.clay = canvasTex(256, 256, (g, w, h) => pixFill(g, w, h, (x, y) => { const r = Math.floor(y / 16), c = Math.floor((x + (r % 2) * 8) / 16); const v = hash2(c, r, 3); const shade = (y % 16) / 16; return mulc([178, 78, 44], .78 + v * .2 + shade * .14 - fbm(x / 40, y / 40, 95, 3, 6) * .12); }), { rep: [1 / 2, 1 / 2] });
  TEX.ready = true; return TEX;

}

// ------------------------------------------------------------------ text helpers (unchanged API)
export function textSprite(THREE, text, o = {}) {
  T = THREE; const size = o.size || 64, font = o.font || `600 ${size}px "Helvetica Neue", Arial, sans-serif`, pad = o.padding ?? size * .35, sc = o.scale || 2;
  const c = document.createElement('canvas'), g = c.getContext('2d'); g.font = font;
  const lines = String(text).split('\n'), w = Math.max(...lines.map(l => g.measureText(l).width + (o.letterSpacing || 0) * l.length));
  const lh = size * 1.2, W = Math.ceil(w + pad * 2), H = Math.ceil(lh * lines.length + pad * 2);
  c.width = W * sc; c.height = H * sc; g.scale(sc, sc); g.font = font; g.textBaseline = 'middle'; g.textAlign = 'center';
  if (g.letterSpacing !== undefined && o.letterSpacing) g.letterSpacing = o.letterSpacing + 'px';
  if (o.bg) { g.fillStyle = o.bg; g.beginPath(); g.roundRect ? g.roundRect(0, 0, W, H, o.radius ?? size * .3) : g.rect(0, 0, W, H); g.fill(); }
  g.fillStyle = o.color || IVORY; if (o.shadow) { g.shadowColor = 'rgba(0,0,0,.55)'; g.shadowBlur = size * .15; }
  lines.forEach((l, i) => g.fillText(l, W / 2, pad + lh * (i + .5)));
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.generateMipmaps = true; tex.minFilter = THREE.LinearMipmapLinearFilter;
  const m = new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false, depthTest: o.depthTest ?? true, sizeAttenuation: o.sizeAttenuation ?? true, fog: false });
  const s = new THREE.Sprite(m); const hh = o.worldHeight || 4; s.scale.set(hh * W / H, hh, 1); s.userData.aspect = W / H; s.renderOrder = 10; return s;
}
// lettering on a plane: lit (MeshStandard, alpha-tested) so it sits in the scene like real ivory letters
export function letterPlane(text, wm, hm, o = {}) {
  const c = document.createElement('canvas'); const W = 2048, H = Math.round(2048 * hm / wm); c.width = W; c.height = H; const g = c.getContext('2d');
  const fs = H * (o.fs || .62); g.font = `${o.weight || 400} ${fs}px ${o.family || '"Caladea","Liberation Serif","DejaVu Serif",serif'}`; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.letterSpacing = (fs * (o.ls ?? .04)) + 'px'; g.fillStyle = '#ffffff'; g.fillText(text, W / 2, H / 2 + fs * .04);
  const tex = new T.CanvasTexture(c); tex.colorSpace = T.SRGBColorSpace; tex.anisotropy = 16;
  const m = new T.MeshStandardMaterial({ map: tex, color: o.color || '#F1E9D8', roughness: o.rough ?? .45, metalness: o.metal ?? 0, alphaTest: .45, transparent: false, emissive: new T.Color(o.color || '#F1E9D8'), emissiveMap: tex, emissiveIntensity: o.glow ?? .12, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
  const ms = new T.Mesh(new T.PlaneGeometry(wm, hm), m); ms.castShadow = false; ms.receiveShadow = true; return ms;
}
export function planTexture(THREE, url) {
  return new Promise((res, rej) => new THREE.TextureLoader().load(url, t => { t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 16; res(t); }, undefined, rej));
}
export function viewportSize() { return { w: window.RENDER_W || window.innerWidth, h: window.RENDER_H || window.innerHeight }; }

// ------------------------------------------------------------------ sun / sky / environment
// warm late-afternoon sun, 31 deg elevation from the east-south-east (lights the road/east elevation and the pool deck)
export const SUN = { elev: 38, az: 30 };
function sunVec(elev, az) { const e = elev * Math.PI / 180, a = az * Math.PI / 180; return new T.Vector3(Math.cos(e) * Math.cos(a), Math.sin(e), Math.cos(e) * Math.sin(a)); }
export const ENV = {};
// equirectangular sky painted once on a canvas (gradient, sun glow, fbm cumulus, ground below the horizon for reflections)
export function skyTexture() {
  if (ENV.skyTex) return ENV.skyTex; const sd = sunVec(SUN.elev, SUN.az); SUN.dir = sd;
  const W = 1024, H = 512;
  ENV.skyTex = canvasTex(W, H, (g) => pixFill(g, W, H, (x, y) => {
    const u = (x + .5) / W, v = 1 - (y + .5) / H, ph = (u - .5) * 2 * Math.PI, el = (v - .5) * Math.PI;
    const dx = Math.cos(ph) * Math.cos(el), dy = Math.sin(el), dz = Math.sin(ph) * Math.cos(el);
    const cs = Math.max(0, dx * sd.x + dy * sd.y + dz * sd.z);
    if (el < 0) { const k = Math.min(1, -el * 5); return mixc([176, 184, 170], [74, 86, 60], Math.pow(k, .6)); }
    const t = el / (Math.PI / 2);
    let c = mixc([188, 207, 238], [40, 89, 163], Math.pow(t, .55));
    c = mixc(c, [216, 221, 227], Math.exp(-el * 14) * .6);
    const gl = Math.pow(cs, 6) * .28 + Math.pow(cs, 60) * .6; c = [c[0] + 255 * gl, c[1] + 224 * gl, c[2] + 180 * gl];
    if (el > .015) { // clouds on a plane
      const k = 1 / (dy + .12), px = dx * k * .9, pz = dz * k * .9;
      const n = fbm(px * 2.2 + 7, pz * 2.2 + 3, 101, 5), d = smooth(.6, .76, n) * smooth(.015, .16, el) * (1 - .5 * smooth(.5, 1, t));
      if (d > 0) { const sh = fbm(px * 1.3 + 7 - sd.x * .08, pz * 1.3 + 3 - sd.z * .08, 101, 4); const lit = .78 + .22 * smooth(.45, .75, n - sh + .55) + .18 * Math.pow(cs, 3);
        const cc = mixc([196, 204, 216], [255, 252, 246], Math.min(1, lit - .1)); c = mixc(c, cc, d * .92); }
    }
    return c.map(q => Math.min(255, q));
  }), { aniso: 1 });
  ENV.skyTex.wrapS = T.RepeatWrapping; ENV.skyTex.wrapT = T.ClampToEdgeWrapping; ENV.skyTex.generateMipmaps = false; ENV.skyTex.minFilter = T.LinearFilter;
  return ENV.skyTex;
}
export function skyEnv() { if (ENV.skyEnv) return ENV.skyEnv; const t = skyTexture().clone(); t.mapping = T.EquirectangularReflectionMapping; t.needsUpdate = true; ENV.skyEnv = t; return t; }
// instance-aware bounds so InstancedMeshes can be frustum-culled (main + shadow camera)
export function cullable(root) { root.traverse(o => { if (o.isInstancedMesh && !o.userData.dynamic && o.count > 0) { o.computeBoundingSphere(); o.frustumCulled = true; } }); }
// split a big static InstancedMesh into spatial cells (so the camera / shadow frustum can cull most of it)
export function splitInstanced(im, cell = 250) {
  const grp = new T.Group(); grp.name = im.name; const buckets = new Map(), m4 = new T.Matrix4(), c = new T.Color();
  for (let i = 0; i < im.count; i++) { im.getMatrixAt(i, m4); const k = Math.floor(m4.elements[12] / cell) + ',' + Math.floor(m4.elements[14] / cell); if (!buckets.has(k)) buckets.set(k, []); buckets.get(k).push(i); }
  buckets.forEach(ids => { const n = new T.InstancedMesh(im.geometry, im.material, ids.length); ids.forEach((id, j) => { im.getMatrixAt(id, m4); n.setMatrixAt(j, m4); if (im.instanceColor) { im.getColorAt(id, c); n.setColorAt(j, c); } });
    n.castShadow = im.castShadow; n.receiveShadow = im.receiveShadow; n.computeBoundingSphere(); n.frustumCulled = true; grp.add(n); });
  return grp;
}
const EQ_GLSL = `vec2 eqUv(vec3 d){ return vec2(atan(d.z,d.x)*0.1591549+0.5, asin(clamp(d.y,-1.,1.))*0.3183099+0.5); }`;

// cheaper soft shadows: 2x2 bilinear PCF (4 depth fetches instead of three's 16) - crisp ~1-texel sun penumbra, ~half the receive cost
// "photographed" grade applied after ACES in every shader: saturation 0.9, slightly lifted blacks, warm highlights
function patchToneChunk(THREE) {
  const k = 'tonemapping_fragment'; if (THREE.ShaderChunk[k].includes('VANTA_GRADE')) return;
  THREE.ShaderChunk[k] = THREE.ShaderChunk[k].replace('gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );', `gl_FragColor.rgb = toneMapping( gl_FragColor.rgb ); // VANTA_GRADE
	{ float lum = dot( gl_FragColor.rgb, vec3( 0.2126, 0.7152, 0.0722 ) ); gl_FragColor.rgb = mix( vec3( lum ), gl_FragColor.rgb, 0.9 );
	  gl_FragColor.rgb = gl_FragColor.rgb * vec3( 1.0, 0.995, 0.975 ) * 0.992 + vec3( 0.0075, 0.0078, 0.0088 ) + vec3( 0.012, 0.006, -0.004 ) * smoothstep( 0.5, 1.0, lum ); }`);
}
function patchShadowChunk(THREE) {
  const k = 'shadowmap_pars_fragment', src = THREE.ShaderChunk[k]; if (src.includes('VANTA_PCF4')) return;
  const a = src.indexOf('#elif defined( SHADOWMAP_TYPE_PCF_SOFT )'), b = src.indexOf('#elif defined( SHADOWMAP_TYPE_VSM )', a); if (a < 0 || b < 0) return;
  THREE.ShaderChunk[k] = src.slice(0, a) + `#elif defined( SHADOWMAP_TYPE_PCF_SOFT ) // VANTA_PCF4
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize; vec2 uv = shadowCoord.xy * shadowMapSize - 0.5; vec2 f = fract( uv ); uv = ( floor( uv ) + 0.5 ) * texelSize;
			shadow = mix( mix( texture2DCompare( shadowMap, uv, shadowCoord.z ), texture2DCompare( shadowMap, uv + vec2( texelSize.x, 0.0 ), shadowCoord.z ), f.x ),
			              mix( texture2DCompare( shadowMap, uv + vec2( 0.0, texelSize.y ), shadowCoord.z ), texture2DCompare( shadowMap, uv + texelSize, shadowCoord.z ), f.x ), f.y );
		` + src.slice(b);
}
export function makeRenderer(THREE, canvas, o = {}) {
  T = THREE; patchShadowChunk(THREE); patchToneChunk(THREE); const { w, h } = viewportSize();

  const r = new THREE.WebGLRenderer({ canvas, antialias: o.antialias ?? (window.NOAA ? false : true), preserveDrawingBuffer: true, powerPreference: 'high-performance' });
  r.setPixelRatio(1); r.setSize(w, h, false); r.outputColorSpace = THREE.SRGBColorSpace; r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = o.exposure ?? 1.0;
  r.shadowMap.enabled = true; r.shadowMap.type = THREE.PCFSoftShadowMap; return r;
}
export function makeSky(THREE, scene, mood = 'day') {
  T = THREE; buildTextures(); scene.getObjectByName('sky')?.removeFromParent();
  const tex = skyTexture();
  const m = new THREE.Mesh(new THREE.SphereGeometry(2400, 48, 24), new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { uSky: { value: tex }, uSun: { value: SUN.dir }, uWarm: { value: 0 }, uDark: { value: mood === 'ink' ? 1 : 0 } },
    vertexShader: 'varying vec3 vD; void main(){ vD=normalize(position); vec4 p=projectionMatrix*modelViewMatrix*vec4(position,1.); gl_Position=p.xyww; }',
    fragmentShader: `uniform sampler2D uSky; uniform vec3 uSun; uniform float uWarm, uDark; varying vec3 vD; ${EQ_GLSL}
      void main(){ vec3 d=normalize(vD); vec3 c=texture2D(uSky,eqUv(d)).rgb; float s=dot(d,uSun);
        c += vec3(1.,.85,.6)*smoothstep(.99965,.9999,s)*14.;
        c *= mix(vec3(1.), vec3(1.12,.98,.82), uWarm); c = mix(c, vec3(.012,.012,.016), uDark);
        gl_FragColor=vec4(c,1.);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }` }));
  m.name = 'sky'; m.renderOrder = -10; m.frustumCulled = false; scene.add(m);
  scene.background = new THREE.Color(mood === 'ink' ? INK : '#cddbe4');
  scene.fog = mood === 'ink' ? new THREE.Fog(0x121215, 220, 900) : new THREE.FogExp2(0xcfd8dd, 0.0011);
  ENV.skyMesh = m; return m;
}
// key (sun, PCF-soft shadows) + hemisphere sky/ground.  fill/rim are kept for API compatibility but not added (each light costs per pixel).
export function lighting(THREE, scene, mood = 'day', o = {}) {
  T = THREE; (scene.userData.vantaLights || []).forEach(l => { l.removeFromParent(); }); const L = [];
  const add = (l) => { scene.add(l); L.push(l); return l; };
  const day = mood !== 'ink'; const shadowSize = o.shadowSize || 2048; skyTexture();
  const key = add(new THREE.DirectionalLight(day ? 0xffdcb4 : 0xfff2e4, day ? 3.3 : 2.2));
  key.position.copy(SUN.dir).multiplyScalar(200); key.castShadow = true; key.shadow.mapSize.set(shadowSize, shadowSize);
  add(key.target); const R = o.shadowRadius || 95; const sc = key.shadow.camera; sc.left = -R; sc.right = R; sc.top = R; sc.bottom = -R; sc.near = 1; sc.far = 500;
  key.shadow.bias = -0.0003; key.shadow.normalBias = 0.04;
  const hemi = add(new THREE.HemisphereLight(day ? 0x8fb0e0 : 0x4a5a78, day ? 0xb8a98f : 0x15151a, day ? 1.0 : .8));
  const fill = new THREE.DirectionalLight(0x9cbcf0, 0), rim = new THREE.DirectionalLight(0xD6B26E, 0);
  if (!day) { rim.intensity = .7; rim.position.set(-80, 30, -40); add(rim); }
  if (o.renderer && !ENV.pmrem) { const pg = new THREE.PMREMGenerator(o.renderer); ENV.pmrem = pg.fromEquirectangular(skyTexture()).texture; pg.dispose(); }
  const Mt = o.materials; if (Mt && ENV.pmrem) Object.keys(Mt).forEach(k => { const m = Mt[k]; if (m && m.userData && m.userData.env) { m.envMap = ENV.pmrem; m.envMapIntensity = m.userData.env; m.needsUpdate = true; } });
  scene.userData.vantaLights = L; const res = { key, fill, hemi, rim, all: L, R };
  scene.userData.vantaLightRig = res; return res;
}
// re-centre the sun shadow frustum on c (Vector3) with half-size R, snapped to shadow texels (no shimmer when the camera moves)
const _r = {}; export function focusShadow(Lt, c, R) {
  const key = Lt.key, d = SUN.dir, sc = key.shadow.camera;
  if (!_r.f) { _r.f = new T.Vector3(); _r.r = new T.Vector3(); _r.u = new T.Vector3(); _r.c = new T.Vector3(); }
  _r.f.copy(d).negate(); _r.r.crossVectors(_r.f, new T.Vector3(0, 1, 0)).normalize(); _r.u.crossVectors(_r.r, _r.f).normalize();
  const tex = 2 * R / key.shadow.mapSize.x; const a = c.dot(_r.r), b = c.dot(_r.u);
  _r.c.copy(c).addScaledVector(_r.r, Math.round(a / tex) * tex - a).addScaledVector(_r.u, Math.round(b / tex) * tex - b);
  const D = R + 160; key.target.position.copy(_r.c); key.position.copy(_r.c).addScaledVector(d, D); key.target.updateMatrixWorld();
  if (sc.right !== R || sc.far !== D + R + 60) { sc.left = -R; sc.right = R; sc.top = R; sc.bottom = -R; sc.near = Math.max(1, D - R - 80); sc.far = D + R + 60; sc.updateProjectionMatrix(); }
  key.shadow.normalBias = 0.012 + R * 0.0004;
}

// ------------------------------------------------------------------ glass shaders
// Facade glass: sky reflection (equirect lookup, Fresnel, coated-glass base reflectance) over a parallax "interior mapped" room
// (floor/ceiling/side/back walls), seeded curtains/sheers and a few warm lamp-lit rooms.  One shader for all instanced panes.
export function facadeGlassMaterial(o = {}) {
  const uniforms = Object.assign({ uSky: { value: skyTexture() }, uSun: { value: SUN.dir }, uSunCol: { value: new T.Color(1, .88, .7) },
    uTint: { value: new T.Color(o.tint || '#a9b8bb') }, uLit: { value: o.lit ?? .07 }, uRefl: { value: o.refl ?? .24 }, uLamp: { value: o.lamp ?? 1 } }, T.UniformsLib.fog);
  return new T.ShaderMaterial({ uniforms, fog: true, lights: false,
    vertexShader: `varying vec3 vW, vN, vL, vCL, vS, vLN; varying float vSeed;
      #include <fog_pars_vertex>
      void main(){ mat4 im = mat4(1.);
        #ifdef USE_INSTANCING
          im = instanceMatrix;
        #endif
        mat4 m = modelMatrix*im; vec4 w = m*vec4(position,1.); vW=w.xyz;
        vN = normalize(transpose(inverse(mat3(m)))*normal);
        vS = vec3(length(m[0].xyz),length(m[1].xyz),length(m[2].xyz)); vL = position*vS; vCL=(inverse(m)*vec4(cameraPosition,1.)).xyz*vS; vLN=normal;
        vec3 q = m[3].xyz; vSeed = fract(sin(dot(floor(q*4.)+.5, vec3(12.9898,78.233,37.719)))*43758.5453);
        vec4 mvPosition = viewMatrix*w; gl_Position = projectionMatrix*mvPosition;
        #include <fog_vertex>
      }`,
    fragmentShader: `uniform sampler2D uSky; uniform vec3 uSun, uSunCol, uTint; uniform float uLit, uRefl, uLamp;
      varying vec3 vW, vN, vL, vCL, vS, vLN; varying float vSeed;
      #include <fog_pars_fragment>
      ${EQ_GLSL}
      float h1(float n){ return fract(sin(n)*43758.5453); }
      void main(){
        vec3 N=normalize(vN), V=normalize(vW-cameraPosition), R=reflect(V,N);
        vec3 sky=texture2D(uSky,eqUv(R)).rgb;
        float ct=clamp(dot(-V,N),0.,1.), F=uRefl+(1.-uRefl)*pow(1.-ct,4.);
        vec3 col=vec3(.012);
        if (vLN.z>.5) {
          vec3 ro=vL, rd=normalize(vL-vCL); float w=vS.x, h=vS.y; bool door=h>2.05;
          float s1=h1(vSeed*13.1), s2=h1(vSeed*29.7), s3=h1(vSeed*51.3), s4=h1(vSeed*77.9);
          float flo=-h*.5-(door?.02:.9), cei=flo+2.75, xr=w*.5+.7+s4, dep=3.+s1*2.;
          float tx=((rd.x>0.?xr:-xr)-ro.x)/rd.x, ty=((rd.y>0.?cei:flo)-ro.y)/rd.y, tz=-dep/min(rd.z,-1e-3);
          float t=min(min(tx,ty),tz); vec3 hp=ro+rd*t; float dd=clamp((ro.z-hp.z)/dep,0.,1.);
          vec3 c = mix(vec3(.80,.76,.69),vec3(.70,.70,.68),s2);
          if (t==ty) c = rd.y<0. ? mix(vec3(.42,.30,.2),vec3(.55,.52,.48),s4) : vec3(.9);
          if (t==tz && hp.y<flo+.9 && abs(hp.x)<.9) c*=.45;  // furniture silhouette against back wall
          float L=(.05+.05*s2)*(1.35-dd*.9);
          bool lamp = s3<uLit;
          vec3 ins = c*L;
          if (lamp) { vec3 lc=vec3(1.,.66,.36); ins = c*lc*(.20+.35*exp(-2.5*length(hp-vec3(0.,cei-.4,ro.z-dep*.55))))*uLamp; }
          float u=vL.x/w+.5; float cl=s1<.55?s1*.75:0., cr=s2<.5?s2*.85:0.; if(door){cl*=.6;cr*=.6;}
          float msk=max(step(u,cl),step(1.-cr,u)), sheer=(s4>.68)?.55:0.;
          vec3 cc=mix(vec3(.86,.82,.74),vec3(.6,.58,.55),h1(vSeed*3.7)); float fold=.8+.2*sin(u*w*31.+s1*6.);
          vec3 curt=cc*fold*(lamp?vec3(.55,.40,.25):vec3(.22));
          ins=mix(ins,curt,max(msk*.94,sheer));
          float frame = step(abs(vL.x), w*.5-.02)*step(abs(vL.y),h*.5-.02); // thin edge
          col = ins*uTint*frame;
        }
        col = col*(1.-F) + sky*F*.92 + uSunCol*pow(max(dot(R,uSun),0.),900.)*9.;
        gl_FragColor=vec4(col,1.);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
        #include <fog_fragment>
      }` });
}
// balustrade / partition glass: transparent, Fresnel sky reflection, faint green edge tint
export function railGlassMaterial(o = {}) {
  const uniforms = Object.assign({ uSky: { value: skyTexture() }, uTint: { value: new T.Color(o.tint || '#5f7a78') }, uA: { value: o.alpha ?? .16 } }, T.UniformsLib.fog);
  return new T.ShaderMaterial({ uniforms, fog: true, transparent: true, depthWrite: false, side: T.DoubleSide,
    vertexShader: `varying vec3 vW, vN; #include <fog_pars_vertex>
      void main(){ mat4 im=mat4(1.);
        #ifdef USE_INSTANCING
          im=instanceMatrix;
        #endif
        mat4 m=modelMatrix*im; vec4 w=m*vec4(position,1.); vW=w.xyz; vN=normalize(transpose(inverse(mat3(m)))*normal);
        vec4 mvPosition=viewMatrix*w; gl_Position=projectionMatrix*mvPosition;
        #include <fog_vertex>
      }`.replace('#include <fog_pars_vertex>', '\n#include <fog_pars_vertex>\n'),
    fragmentShader: `uniform sampler2D uSky; uniform vec3 uTint; uniform float uA; varying vec3 vW, vN;
      #include <fog_pars_fragment>
      ${EQ_GLSL}
      void main(){ vec3 V=normalize(vW-cameraPosition), N=normalize(vN); if(dot(N,V)>0.) N=-N; vec3 R=reflect(V,N);
        float F=.06+.94*pow(1.-clamp(dot(-V,N),0.,1.),4.); vec3 sky=texture2D(uSky,eqUv(R)).rgb;
        vec3 c=mix(uTint*.35,sky,F); gl_FragColor=vec4(c, uA+ (1.-uA)*F*.8);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
        #include <fog_fragment>
      }` });
}

// ------------------------------------------------------------------ materials
function makeMaterials() {
  buildTextures();
  // matte surfaces use Lambert (per-pixel, cheaper than Standard in software GL); metals/glossy keep Standard
  const S = (c, r = .85, m = 0, extra = {}) => (m > 0 || r < .5) ? new T.MeshStandardMaterial({ color: c, roughness: r, metalness: m, ...extra }) : new T.MeshLambertMaterial({ color: c, ...extra });
  const env = (m, k) => m;
  const M = {
    plaster: S('#ffffff', .88, 0, { map: TEX.plaster }), plasterDark: S('#ffffff', .8, 0, { map: TEX.plasterDark }), band: S('#ffffff', .55, .25, { map: TEX.seam }),
    pier: S('#EEE6D4', .8), slab: S('#E7E0CF', .85), balcSlab: S('#E3DCCB', .85), soffit: S('#D9D2C2', .9),
    frame: S('#2A2C30', .45, .55), sill: S('#ECE7DA', .6),
    glass: facadeGlassMaterial(), railGlass: railGlassMaterial(),
    rail: env(S('#2A2B2E', .35, .8), .6), concrete: S('#ffffff', .9, 0, { map: TEX.concrete }), concreteDark: S('#6A6A6A', .9, 0, { map: TEX.concrete }), roofDark: S('#ffffff', .85, 0, { map: TEX.roof }),
    signDark: S('#ffffff', .5, .35, { map: TEX.seam }), gold: env(S('#B08A4E', .35, .8), 1), goldHi: env(S('#D6B26E', .3, .9), 1),
    asphalt: S('#ffffff', .92, 0, { map: TEX.asphalt }), paver: S('#ffffff', .85, 0, { map: TEX.paver }), paverPale: S('#ffffff', .8, 0, { map: TEX.paverPale }),
    grass: S('#ffffff', 1, 0, { map: TEX.grass }), terrain: new T.MeshLambertMaterial({ vertexColors: true }),
    wall: S('#E2DCCD', .9, 0, { map: TEX.plaster }), trunk: S('#ffffff', .95, 0, { map: TEX.bark }), leaf: S('#5C8A3C', .9), leaf2: S('#44773A', .9),
    road: S('#ffffff', .95, 0, { map: TEX.asphalt }), kerb: S('#C9C5BB', .85), white: S('#F2F0EA', .6), soil: S('#ffffff', 1, 0, { map: TEX.soil }),
    glassCurtain: env(S('#2c3e4d', .06, .6, { transparent: true, opacity: .55, depthWrite: false }), 1.2), stone: S('#8A6F58', .85),
    chrome: env(S('#d8d8d8', .25, 1), 1), poolTile: S('#ffffff', .4, 0, { map: TEX.poolTile }),
    verge: new T.MeshLambertMaterial({ map: TEX.verge }), rubble: new T.MeshLambertMaterial({ map: TEX.rubble }),
  };
  return M;
}

// ------------------------------------------------------------------ polyline tracks
export function makeTrack(pts, closed) {
  const P = pts.slice(); if (closed) P.push(P[0]); const cum = [0];
  for (let i = 1; i < P.length; i++) cum.push(cum[i - 1] + Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]));
  const L = cum[cum.length - 1];
  const at = (s) => { s = Math.max(0, Math.min(L - 1e-6, s)); let i = 1; while (cum[i] < s) i++; const u = (s - cum[i - 1]) / (cum[i] - cum[i - 1] || 1);
    const a = P[i - 1], b = P[i]; return { x: a[0] + (b[0] - a[0]) * u, z: a[1] + (b[1] - a[1]) * u, ang: Math.atan2(b[0] - a[0], b[1] - a[1]) }; };
  // smoothed heading (looks ahead/behind 0.8 m) so walkers turn corners gently
  const atS = (s) => { const r = at(s), a = at(Math.max(0, s - .8)), b = at(Math.min(L - 1e-6, s + .8)); if (Math.hypot(b.x - a.x, b.z - a.z) > .01) r.ang = Math.atan2(b.x - a.x, b.z - a.z); return r; };
  return { L, at: atS, closed };
}
function walk(tr, v, t, off, dwell = 0.6) {
  if (tr.closed) { const s = ((t * v + off) % tr.L + tr.L) % tr.L; const r = tr.at(s); r.moving = 1; r.s = t * v + off; return r; }
  const leg = tr.L / v, cyc = 2 * (leg + dwell); let u = (((t + off / v) % cyc) + cyc) % cyc; const lap = Math.floor((t + off / v) / cyc) * 2 * tr.L;
  if (u < leg) { const r = tr.at(u * v); r.moving = 1; r.s = lap + u * v; return r; }
  u -= leg; if (u < dwell) { const r = tr.at(tr.L); r.moving = 0; r.s = lap + tr.L; r.ang = r.ang + Math.PI * smooth(0, dwell * .8, u); return r; }
  u -= dwell; if (u < leg) { const r = tr.at(tr.L - u * v); r.ang += Math.PI; r.moving = 1; r.s = lap + tr.L + u * v; return r; }
  u -= leg; const r = tr.at(0); r.ang += Math.PI * (1 - smooth(0, dwell * .8, u)); r.moving = 0; r.s = lap + 2 * tr.L; return r;
}

// ------------------------------------------------------------------ default paths (metres, [x,z])
function roadGeometry() {
  const A = pm([640, 188]), B = pm([1354, 1005]); const dx = B[0] - A[0], dz = B[1] - A[1], L = Math.hypot(dx, dz), u = [dx / L, dz / L];
  const nn = [Math.abs(u[1]), -Math.abs(u[0])]; // outward = east (+x), north (-z)
  return { A, B, u, n: nn, L, at: (s, off) => [A[0] + u[0] * s + nn[0] * off, A[1] + u[1] * s + nn[1] * off], lane: (s, off = 11.5) => [A[0] + u[0] * s + nn[0] * off, A[1] + u[1] * s + nn[1] * off] };
}
export function defaultPaths() {
  const D = (a) => PM(a), rd = roadGeometry();
  const along = (s0, s1, off) => [rd.at(s0, off), rd.at(s1, off)];
  return {
    gateToNorth: D([[1000, 556], [800, 546], [560, 546], [560, 430]]),
    gateToSouth: D([[975, 580], [800, 592], [640, 592], [612, 625]]),
    gateToCourt: D([[1022, 622], [930, 640], [885, 700], [885, 880]]),
    poolDeck: (() => { const w = PM(POOL_WATER_PX), A = w[3], B = w[0], d = [B[0] - A[0], B[1] - A[1]], L = Math.hypot(...d), n = [d[1] / L, -d[0] / L]; const s = (n[0] * (25 - A[0]) + n[1] * (-15 - A[1])) > 0 ? 1 : -1; return [[A[0] + n[0] * s * .75 - d[0] * .05, A[1] + n[1] * s * .75 - d[1] * .05], [B[0] + n[0] * s * .75 + d[0] * .02, B[1] + n[1] * s * .75 + d[1] * .02]]; })(),
    pavement: along(-30, 90, 2.2), pavement2: along(95, -25, 3.4), pavement3: along(-10, 75, 14.6), pavement4: along(70, -20, 15.4),
    lawn: D([[690, 500], [860, 505], [905, 520]]),
  };
}

// ------------------------------------------------------------------ people: articulated low-poly humans (instanced per body part)
function limbGeo(len, r0, r1, seg = 6) {   // pivot at top (y=0), hangs to -len; rounded ends
  const p = [], n = 2; p.push(new T.Vector2(0.0001, -len - r1 * .8));
  for (let i = 1; i <= n; i++) { const a = i / n * Math.PI / 2; p.push(new T.Vector2(Math.sin(a) * r1, -len - Math.cos(a) * r1 * .8)); }
  p.push(new T.Vector2(r0 * .98, -len * .55)); p.push(new T.Vector2(r0, -len * .12));
  for (let i = 1; i <= n; i++) { const a = i / n * Math.PI / 2; p.push(new T.Vector2(Math.cos(a) * r0, Math.sin(a) * r0 * .8)); }
  p[p.length - 1].x = 0.0001; return new T.LatheGeometry(p, seg);
}
function latheY(prof, seg = 10, sz = 1) { const g = new T.LatheGeometry(prof.map(([r, y]) => new T.Vector2(Math.max(r, .0001), y)), seg); g.scale(1, 1, sz); return g; }
const SKIN = ['#5A3A27', '#4A2F21', '#6B4532', '#3C271B', '#7A5038', '#55372A'];
const SHIRT = ['#F1EEE6', '#1F2A3C', '#C9B48E', '#7A2E2B', '#E9E3D3', '#3F5A4A', '#2B2D31', '#B86B3E', '#8BA3B8', '#D9C9A3', '#5B4A7A', '#E7D7B9', '#2F4F6F', '#A33B3B'];
const PANTS = ['#24262B', '#3A3F4A', '#8B7F68', '#1F2A3C', '#C8BCA2', '#4A4F57', '#2E3B55'];
const DRESS = ['#B0413E', '#E3A33B', '#2F6F8F', '#6A3D7A', '#F0E6D2', '#2D6B4F', '#C2557A'];
const SHOES = ['#151515', '#3A2A20', '#EDEDED', '#5A4636'];
// spec: {path|pos, v, off, pose:'walk'|'stand'|'sit'|'recline'|'swim', h, seed, ang, y}
export function makePeople(THREE, n = 14, paths = defaultPaths(), o = {}) {
  T = THREE; const group = new T.Group(); group.name = 'people';
  const R = rnd(o.seed || 7); const specs = [];
  if (Array.isArray(n)) n.forEach(s => specs.push(s));
  else { const keys = Object.keys(paths); for (let i = 0; i < n; i++) { const k = keys[i % keys.length]; specs.push({ path: paths[k], closed: k === 'poolDeck' || (o.closed || []).includes(k) }); } }
  const N = specs.length;
  const G = {
    head: new T.SphereGeometry(.105, 12, 9).scale(.92, 1.06, 1), hair: new T.SphereGeometry(.112, 12, 6, 0, Math.PI * 2, 0, Math.PI * .52).scale(.94, 1.0, 1.04).translate(0, .012, -.008),
    neck: limbGeo(.08, .05, .055, 6), torso: latheY([[.0, -.02], [.135, .0], [.128, .12], [.142, .26], [.158, .38], [.155, .46], [.12, .51], [.05, .535], [0, .54]], 10, .66),
    pelvis: latheY([[0, -.10], [.11, -.085], [.148, -.02], [.142, .06], [.13, .1], [0, .1]], 10, .72),
    skirt: latheY([[0, .02], [.135, .02], [.17, -.2], [.21, -.46], [0, -.46]], 12, .8),
    thigh: limbGeo(.43, .078, .056), shin: limbGeo(.42, .055, .04), foot: new T.BoxGeometry(.09, .065, .24).translate(0, -.03, .05),
    uarm: limbGeo(.28, .048, .04), farm: limbGeo(.25, .038, .03), hand: new T.SphereGeometry(.042, 8, 6).scale(.8, 1.25, .55).translate(0, -.04, 0),
  };
  const mat = new T.MeshLambertMaterial();
  const parts = {}; const mk = (k, geo, cnt) => { const im = new T.InstancedMesh(geo, mat, cnt); im.castShadow = true; im.receiveShadow = true; im.frustumCulled = false; im.userData.dynamic = true; im.name = 'people_' + k; group.add(im); parts[k] = im; return im; };
  ['head', 'hair', 'neck', 'torso', 'pelvis', 'skirt'].forEach(k => mk(k, G[k], N)); ['thigh', 'shin', 'foot', 'uarm', 'farm', 'hand'].forEach(k => mk(k, G[k], 2 * N));
  const blob = new T.InstancedMesh(new T.CircleGeometry(.36, 16).rotateX(-Math.PI / 2), new T.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: .2, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4, map: blobTex() }), N);
  blob.frustumCulled = false; blob.userData.dynamic = true; group.add(blob);
  const col = new T.Color(); const ppl = [];
  specs.forEach((sp, i) => {
    const r = rnd((sp.seed ?? i * 31 + (o.seed || 7)) + 1); r(); const pick = (a) => a[Math.floor(r() * a.length)];
    const female = sp.female ?? r() < .5, dress = sp.dress ?? (female && r() < .55), shorts = !dress && (sp.pose === 'recline' || sp.pose === 'swim' || r() < .15), shortSleeve = r() < .6;
    const skin = col.set(pick(SKIN)).clone(), shirt = new T.Color(sp.shirt || pick(SHIRT)), pants = new T.Color(dress ? pick(DRESS) : pick(PANTS)), shoe = new T.Color(pick(SHOES)), hair = new T.Color(r() < .85 ? '#120F0D' : '#2B211A');
    const h = sp.h ?? (female ? 1.58 + r() * .16 : 1.68 + r() * .18);
    const p = { ...sp, tr: sp.path ? makeTrack(sp.path, !!sp.closed) : null, v: sp.v ?? (1.25 + r() * .2), off: sp.off ?? r() * 200, k: h / 1.75, ph: r() * 6.28, dress, female, wide: female ? .95 : 1.05 };
    if (p.tr && sp.off === undefined) p.off = r() * p.tr.L * (p.tr.closed ? 1 : 2);
    ppl.push(p);
    const dressC = dress ? pants : null;
    parts.head.setColorAt(i, skin); parts.neck.setColorAt(i, skin); parts.hair.setColorAt(i, hair); parts.torso.setColorAt(i, dress ? dressC : shirt);
    parts.pelvis.setColorAt(i, dress ? dressC : pants); parts.skirt.setColorAt(i, dress ? dressC : pants);
    for (const s of [0, 1]) { const j = 2 * i + s; parts.thigh.setColorAt(j, dress || shorts ? skin : pants); parts.shin.setColorAt(j, dress || shorts ? skin : pants); parts.foot.setColorAt(j, sp.pose === 'swim' || sp.pose === 'recline' ? skin : shoe);
      parts.uarm.setColorAt(j, sp.pose === 'swim' ? skin : (dress ? dressC : shirt)); parts.farm.setColorAt(j, shortSleeve || sp.pose === 'swim' ? skin : (dress ? dressC : shirt)); parts.hand.setColorAt(j, skin); }
  });
  Object.values(parts).forEach(m => { if (m.instanceColor) m.instanceColor.needsUpdate = true; });
  const Rt = new T.Matrix4(), A = new T.Matrix4(), B = new T.Matrix4(), C = new T.Matrix4(), tm = new T.Matrix4(), rm = new T.Matrix4(), Z = new T.Matrix4().makeScale(0, 0, 0), sv = new T.Vector3();
  const tr = (x, y, z) => tm.makeTranslation(x, y, z), rx = (a) => rm.makeRotationX(a), ry = (a) => rm.makeRotationY(a), rz = (a) => rm.makeRotationZ(a);
  function pose(p, t) {
    let x, z, ang, s = 0, mode = p.pose || 'walk', y0 = p.y || 0;
    if (p.tr) { const w = walk(p.tr, p.v, t + (p.t0 || 0), p.off, p.dwell ?? .8); x = w.x; z = w.z; ang = w.ang; s = w.s; if (!w.moving) mode = 'stand'; }
    else { x = p.pos[0]; z = p.pos[1]; ang = p.ang || 0; }
    return { x, z, ang, s, mode, y0 };
  }
  function update(t) {
    ppl.forEach((p, i) => {
      const q = pose(p, t), k = p.k; let ph = q.s / (1.42 * k) * Math.PI * 2 + p.ph; const walking = q.mode === 'walk';
      const sw = walking ? 1 : 0, sP = Math.sin(ph), cP = Math.cos(ph);
      let hipL = -.40 * sP * sw, hipR = .40 * sP * sw, kneeL = sw * (.06 + .85 * Math.pow(Math.max(0, Math.cos(ph - .25)), 2)), kneeR = sw * (.06 + .85 * Math.pow(Math.max(0, Math.cos(ph + Math.PI - .25)), 2));
      let shL = .30 * sP * sw, shR = -.30 * sP * sw, elL = -(.18 + .3 * Math.max(0, -sP) * sw), elR = -(.18 + .3 * Math.max(0, sP) * sw);
      let bob = walking ? .022 * Math.cos(2 * ph) - .01 : 0, lean = walking ? .05 : 0, twist = walking ? .07 * sP : 0, rootPitch = 0, py = .935;
      const idle = Math.sin(t * 1.1 + p.ph);
      if (q.mode === 'stand') { hipL = .03 * idle; hipR = -.02; kneeL = .05; kneeR = .02; shL = .04 * idle + (p.armsCrossed ? -.6 : 0); shR = -.03 * idle; elL = -.15; elR = -.25; }
      if (q.mode === 'sit') { py = p.seat ?? .47; hipL = hipR = -1.5; kneeL = kneeR = 1.5 + (p.dangle ? .1 * Math.sin(t * 1.3 + p.ph) : 0); shL = shR = -.25; elL = elR = -.7; lean = -.05; }
      if (q.mode === 'recline') { py = p.seat ?? .42; rootPitch = -1.05; hipL = hipR = -.55; kneeL = .12; kneeR = .4; shL = shR = .25; elL = elR = -.25; }
      if (q.mode === 'swim') { py = -.55; hipL = -.25 * Math.sin(t * 2 + p.ph); hipR = .25 * Math.sin(t * 2 + p.ph); kneeL = kneeR = .2; shL = -1.0 + .5 * Math.sin(t * 1.4 + p.ph); shR = -1.0 - .5 * Math.sin(t * 1.4 + p.ph); elL = elR = -.6; }
      Rt.makeTranslation(q.x, q.y0 + .015, q.z).multiply(ry(q.ang)).multiply(sv.set(k, k, k) && tm.makeScale(k, k, k));
      // pelvis frame
      A.copy(Rt).multiply(tr(0, py + bob, 0)).multiply(rx(rootPitch)).multiply(ry(twist * .5)); parts.pelvis.setMatrixAt(i, A);
      if (p.dress && q.mode !== 'sit') parts.skirt.setMatrixAt(i, B.copy(A).multiply(tm.makeScale(1, q.mode === 'recline' ? .6 : 1, 1))); else parts.skirt.setMatrixAt(i, Z);
      // torso, neck, head
      B.copy(A).multiply(tr(0, .08, 0)).multiply(rx(lean)).multiply(ry(-twist)); parts.torso.setMatrixAt(i, C.copy(B).multiply(tm.makeScale(p.wide, 1, 1)));
      C.copy(B).multiply(tr(0, .6, 0)); parts.neck.setMatrixAt(i, C); C.multiply(tr(0, .15, .005)).multiply(rx(-lean * .6 + (q.mode === 'recline' ? .5 : 0))); parts.head.setMatrixAt(i, C); parts.hair.setMatrixAt(i, C);
      // arms
      [[-1, shL, elL], [1, shR, elR]].forEach(([sd, sh, el], j) => { const jj = 2 * i + j;
        C.copy(B).multiply(tr(sd * .175 * p.wide, .465, -.005)).multiply(rz(sd * .07)).multiply(rx(sh)); parts.uarm.setMatrixAt(jj, C);
        C.multiply(tr(0, -.28, 0)).multiply(rx(el)); parts.farm.setMatrixAt(jj, C); C.multiply(tr(0, -.25, 0)); parts.hand.setMatrixAt(jj, C); });
      // legs
      [[-1, hipL, kneeL], [1, hipR, kneeR]].forEach(([sd, hp, kn], j) => { const jj = 2 * i + j;
        C.copy(A).multiply(tr(sd * .088, -.01, 0)).multiply(rx(hp)); parts.thigh.setMatrixAt(jj, C);
        C.multiply(tr(0, -.43, 0)).multiply(rx(kn)); parts.shin.setMatrixAt(jj, C);
        C.multiply(tr(0, -.43, 0)).multiply(rx(-(hp + kn) * (q.mode === 'walk' ? .85 : .6) + (q.mode === 'recline' || q.mode === 'swim' ? .9 : 0))); parts.foot.setMatrixAt(jj, C); });
      const vis = q.mode === 'swim' || q.mode === 'recline' || (p.y || 0) > .3 ? 0 : 1;
      tm.makeTranslation(q.x, (q.y0 || 0) + .045, q.z); if (!vis) tm.makeScale(0, 0, 0); blob.setMatrixAt(i, tm);
    });
    Object.values(parts).forEach(m => m.instanceMatrix.needsUpdate = true); blob.instanceMatrix.needsUpdate = true;
  }
  update(0); return { group, update, paths, specs: ppl };
}
let _blobTex; function blobTex() { if (_blobTex) return _blobTex; _blobTex = canvasTex(128, 128, (g) => { const r = g.createRadialGradient(64, 64, 4, 64, 64, 64); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(.5, 'rgba(255,255,255,.55)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, 128, 128); }, { srgb: false }); _blobTex.wrapS = _blobTex.wrapT = T.ClampToEdgeWrapping; return _blobTex; }
export { blobTex };

// ------------------------------------------------------------------ cars: rounded extruded bodies, arches, glass greenhouse, wheels with rims
const CAR_COLS = ['#F4F3EF', '#2B2D31', '#A7ABB0', '#1F2C47', '#7A2E2B', '#D2CEC4', '#F4F3EF', '#5E6166', '#F4F3EF', '#C7C9CC'];
let CARG = null;
function carGeos() {
  if (CARG) return CARG; const sh = new T.Shape();
  const arch = (cx, s) => { for (let i = 0; i <= 6; i++) { const a = Math.PI - i / 6 * Math.PI; s.lineTo(cx + Math.cos(a) * .42, .30 + Math.sin(a) * .40); } };
  sh.moveTo(-2.22, .34); sh.lineTo(-1.72, .30); arch(-1.30, sh); sh.lineTo(1.08, .30); arch(1.50, sh); sh.lineTo(2.2, .32);
  sh.quadraticCurveTo(2.33, .36, 2.31, .56); sh.quadraticCurveTo(2.28, .78, 2.05, .84); sh.lineTo(.86, .97); sh.lineTo(-1.5, 1.0); sh.quadraticCurveTo(-2.18, .99, -2.26, .86); sh.quadraticCurveTo(-2.33, .5, -2.22, .34);
  const body = new T.ExtrudeGeometry(sh, { depth: 1.58, bevelEnabled: true, bevelThickness: .1, bevelSize: .08, bevelSegments: 2, curveSegments: 3 }); body.translate(0, 0, -.79);
  const gh = new T.Shape(); gh.moveTo(-1.62, .97); gh.lineTo(.88, .95); gh.quadraticCurveTo(.2, 1.38, -.05, 1.43); gh.lineTo(-1.08, 1.44); gh.quadraticCurveTo(-1.45, 1.36, -1.62, .97);
  const glass = new T.ExtrudeGeometry(gh, { depth: 1.36, bevelEnabled: true, bevelThickness: .06, bevelSize: .05, bevelSegments: 1, curveSegments: 3 }); glass.translate(0, 0, -.68);
  const rf = new T.Shape(); rf.moveTo(-1.12, 1.39); rf.lineTo(-.02, 1.38); rf.lineTo(-.06, 1.46); rf.lineTo(-1.08, 1.47); const roof = new T.ExtrudeGeometry(rf, { depth: 1.34, bevelEnabled: true, bevelThickness: .05, bevelSize: .04, bevelSegments: 2 }); roof.translate(0, 0, -.67);
  const tire = new T.CylinderGeometry(.33, .33, .23, 12).rotateX(Math.PI / 2), rim = new T.CylinderGeometry(.21, .21, .242, 8).rotateX(Math.PI / 2);
  const lights = new T.BoxGeometry(.05, .1, .34);
  CARG = { body, glass, roof, tire, rim, lights }; return CARG;
}
// a fleet: n cars as instanced parts; set(i, x, y, z, ang, roll) positions car i
export function carFleet(THREE, n, mats = {}) {
  T = THREE; const g = carGeos(), grp = new T.Group(); grp.name = 'cars';
  // Phong + direct equirect sky reflection: one texture lookup (PMREM env on Standard cost ~0.8 s/frame in software GL)
  const env = skyEnv();
  const paint = new T.MeshPhongMaterial({ shininess: 90, specular: '#666666', envMap: env, reflectivity: .22, combine: T.MixOperation });
  const gl = new T.MeshPhongMaterial({ color: '#0d1217', shininess: 120, specular: '#888888', envMap: env, reflectivity: .5, combine: T.MixOperation });
  const tireM = new T.MeshLambertMaterial({ color: '#161618' }), rimM = new T.MeshPhongMaterial({ color: '#b8bbbf', shininess: 60, specular: '#999999', envMap: env, reflectivity: .35, combine: T.MixOperation });
  const hl = new T.MeshLambertMaterial({ color: '#ffffff', emissive: '#fff6e6', emissiveIntensity: .6 }), tl = new T.MeshLambertMaterial({ color: '#8a1010', emissive: '#a01010', emissiveIntensity: .35 });
  const mk = (geo, m, c) => { const im = new T.InstancedMesh(geo, m, c); im.castShadow = true; im.receiveShadow = true; im.frustumCulled = false; im.userData.dynamic = true; grp.add(im); return im; };
  const body = mk(g.body, paint, n), glass = mk(g.glass, gl, n), roof = mk(g.roof, paint, n), tire = mk(g.tire, tireM, 4 * n), rim = mk(g.rim, rimM, 4 * n), fl = mk(g.lights, hl, 2 * n), rl = mk(g.lights, tl, 2 * n);
  [fl, rl, glass].forEach(m => m.castShadow = false);
  const c = new T.Color(); for (let i = 0; i < n; i++) { c.set(mats.colors?.[i] || CAR_COLS[i % CAR_COLS.length]); body.setColorAt(i, c); roof.setColorAt(i, c); }
  body.instanceColor.needsUpdate = true; roof.instanceColor.needsUpdate = true;
  const Mx = new T.Matrix4(), W = new T.Matrix4(), tm = new T.Matrix4(), rm = new T.Matrix4();
  // car local frame: length along +x in the geometry; heading ang (rad, atan2(dx,dz) convention) -> rotate so +x points along heading
  function set(i, x, y, z, ang, roll = 0) {
    Mx.makeTranslation(x, y, z).multiply(rm.makeRotationY(ang - Math.PI / 2));
    body.setMatrixAt(i, Mx); glass.setMatrixAt(i, Mx); roof.setMatrixAt(i, Mx);
    let k = 0; for (const a of [-1.30, 1.50]) for (const s of [-1, 1]) { W.copy(Mx).multiply(tm.makeTranslation(a, .33, s * .80)).multiply(rm.makeRotationZ(-roll)); tire.setMatrixAt(4 * i + k, W); rim.setMatrixAt(4 * i + k, W); k++; }
    for (const s of [0, 1]) { W.copy(Mx).multiply(tm.makeTranslation(2.27, .66, (s ? 1 : -1) * .58)); fl.setMatrixAt(2 * i + s, W); W.copy(Mx).multiply(tm.makeTranslation(-2.3, .74, (s ? 1 : -1) * .6)); rl.setMatrixAt(2 * i + s, W); }
  }
  function commit() { [body, glass, roof, tire, rim, fl, rl].forEach(m => m.instanceMatrix.needsUpdate = true); }
  return { group: grp, set, commit, n, materials: { paint, glass: gl, rim: rimM } };
}
export function parkedCars(THREE, spots) { T = THREE; const f = carFleet(THREE, spots.length, { colors: spots.map(s => s.c) }); spots.forEach((s, i) => f.set(i, s.x, s.y || 0, s.z, s.ang || 0)); f.commit(); f.group.name = 'cars_parked'; f.group.children.forEach(m => m.userData.dynamic = false); return f.group; }
export function makeCars(THREE, o = {}) {
  T = THREE; const P = defaultPaths(), rd = roadGeometry(); const spots = [];
  const used = [[0, 1, 3, 5], [1, 4]];
  [[760, 0], [935, 1]].forEach(([yy, row]) => used[row].forEach((i) => { const p = pm([805 + i * 46 + 23, yy]); spots.push({ x: p[0], z: p[1], ang: row ? 0 : Math.PI }); }));
  (o.extraSpots || []).forEach(s => spots.push(s));
  // moving: driveway shuttle + two-way public road traffic (looping long straight, starts/ends off camera)
  const moving = [
    { tr: makeTrack(P.gateToCourt, false), v: 3.0, off: 0, dwell: 5 },
    { tr: makeTrack(PM([[1000, 545], [800, 545], [612, 545], [612, 470]]), false), v: 3.0, off: 31, dwell: 8 },

  ];
  const lanes = [{ off: 10.7, dir: 1 }, { off: 7.8, dir: -1 }]; const roadCars = []; // Uganda drives on the left
  for (let i = 0; i < 7; i++) roadCars.push({ lane: lanes[i % 2], v: 8.5 + (i * 1.7) % 3, ph: i * 61 });
  const fleet = carFleet(T, spots.length + moving.length + roadCars.length, { colors: spots.map(s => s.c) });
  const group = fleet.group; spots.forEach((s, i) => fleet.set(i, s.x, s.y || 0, s.z, s.ang || 0)); fleet.commit();
  const S0 = -260, S1 = 330, LEN = S1 - S0;
  function update(t) {
    moving.forEach((mv, j) => { const r = walk(mv.tr, mv.v, t, mv.off * mv.v, mv.dwell); fleet.set(spots.length + j, r.x, .03, r.z, r.ang, r.s / .33); });
    roadCars.forEach((c, j) => { let s = ((t * c.v + c.ph * 7) % LEN + LEN) % LEN; if (c.lane.dir < 0) s = LEN - s; s += S0; const p = rd.at(s, c.lane.off);
      fleet.set(spots.length + moving.length + j, p[0], .03, p[1], Math.atan2(rd.u[0] * c.lane.dir, rd.u[1] * c.lane.dir), t * c.v / .33); });
    fleet.commit();
  }
  update(0); return { group, update, fleet };
}

// ------------------------------------------------------------------ shared sway uniform (trees, palms)
export const SWAY = { uTime: { value: 0 } };
function swayMat(m, amp, mode = 'crown') {
  m.onBeforeCompile = (sh) => { sh.uniforms.uTime = SWAY.uTime;
    sh.vertexShader = 'uniform float uTime;\n' + sh.vertexShader.replace('#include <begin_vertex>', `#include <begin_vertex>
      { vec3 ip = vec3(0.);
        #ifdef USE_INSTANCING
          ip = instanceMatrix[3].xyz;
        #endif
        float ph = ip.x*.37+ip.z*.29;
        ${mode === 'frond' ? `float k = max(0., position.z)/3.2; transformed.y += ${amp.toFixed(3)}*k*k*(sin(uTime*1.7+ph)+.5*sin(uTime*3.1+ph*1.7)); transformed.x += ${(amp * .4).toFixed(3)}*k*sin(uTime*1.3+ph);`
        : `float k = clamp(position.y*.5+.5,0.,1.); transformed.x += ${amp.toFixed(3)}*k*sin(uTime*1.1+ph); transformed.z += ${(amp * .7).toFixed(3)}*k*sin(uTime*.9+ph*1.3);`} }`); };
  m.customProgramCacheKey = () => 'sway_' + mode + amp; return m;
}
// world-metre UVs for a box geometry placed at (cx,cy,cz) (keeps plaster texture continuous)
function worldUV(g, cx, cy, cz) { const p = g.attributes.position, n = g.attributes.normal, uv = g.attributes.uv;
  for (let i = 0; i < p.count; i++) { const x = p.getX(i) + cx, y = p.getY(i) + cy, z = p.getZ(i) + cz, ax = Math.abs(n.getX(i)), ay = Math.abs(n.getY(i));
    if (ay > .5) uv.setXY(i, x, z); else if (ax > .5) uv.setXY(i, z, y); else uv.setXY(i, x, y); } uv.needsUpdate = true; return g; }
export function wallBox(m, x0, x1, y0, y1, z0, z1, o = {}) { const w = x1 - x0, h = y1 - y0, d = z1 - z0; if (w <= .001 || h <= .001 || d <= .001) return null;
  const g = worldUV(new T.BoxGeometry(w, h, d), (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); const b = mesh(g, m, o); b.position.set((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); return b; }

// ------------------------------------------------------------------ facade generator
const BAY = { B: 3.0, A: 1.4, W: 2.2 };
function buildFloorGroups(M, blocks, floors, o) {
  const mtx = new T.Matrix4(), X = new T.Vector3(), Y = new T.Vector3(0, 1, 0), Z = new T.Vector3(), Rm = new T.Matrix4(), qq = new T.Quaternion(), pp = new T.Vector3(), ss = new T.Vector3();
  const BG = new T.BoxGeometry(1, 1, 1);
  const types = { frame: M.frame, glass: M.glass, sill: M.sill, band: M.band, bslab: M.balcSlab, bglass: M.railGlass, brail: M.rail, pier: M.pier, soffitL: M.soffit };
  const allPolys = Object.values(blocks).map(b => b.polygon);
  const isCornerEdge = (bi, a, b) => bi === 1 && ((Math.abs(a[1] - 1.91) < .05 && Math.abs(b[1] - 1.91) < .05 && Math.min(a[0], b[0]) > XA - .05) || (Math.abs(a[0] - 16.78) < .05 && Math.abs(b[0] - 16.78) < .05));
  for (let k = 1; k <= 11; k++) {
    const fl = floors[k + 1], level = levelOf(k), g = fl.group, lists = {}; Object.keys(types).forEach(t => lists[t] = []);
    const notch = k === APT.level && o.interiorLevel !== false;
    Object.values(blocks).forEach((blk, bi) => {
      const poly = blk.polygon, A = area2(poly), n = poly.length;
      g.add(mesh(prismGeo(offsetPoly(poly, .14), level - .3, level), M.slab, { name: 'slab' }));
      const wpoly = (notch && bi === 1) ? blk.notchPolygon : poly;
      g.add(mesh(prismGeo(wpoly, level, level + 3.0), k === 1 ? M.plasterDark : M.plaster, { name: 'walls' }));
      for (let e = 0; e < n; e++) {
        const a = poly[e], b = poly[(e + 1) % n], nrm = edgeNormal(a, b, A), L = Math.hypot(b[0] - a[0], b[1] - a[1]);
        const t = [nrm[1], -nrm[0]];
        const s0 = a[0] * t[0] + a[1] * t[1], s1 = b[0] * t[0] + b[1] * t[1], sa = Math.min(s0, s1), sb = Math.max(s0, s1);
        const org = (s, o2) => [a[0] + t[0] * (s - s0) + nrm[0] * o2, a[1] + t[1] * (s - s0) + nrm[1] * o2];
        const em = (type, sc, y, o2, w, h, d) => { const p = org(sc, o2); lists[type].push([p[0], level + y, p[1], w, h, d, t, nrm]); };
        if (isCornerEdge(bi, a, b)) { // ---- custom corner elevation (typical 2-bed unit), coordinates along the face
          const north = Math.abs(nrm[1] + 1) < .1; const ops = north ? CORNER.north : CORNER.east;
          const toS = (c) => north ? (c * t[0]) : (c * t[1]);   // world x (north) or z (east) -> s
          let prev = north ? XA : 1.91; const end = north ? 16.78 : ZS;
          const pier = (c0, c1) => { if (c1 - c0 < .25) return; const sc = (toS(c0) + toS(c1)) / 2; em('pier', sc, 1.35, .09, Math.abs(c1 - c0) - .02, 3.3, .18); };
          ops.forEach(op => {
            pier(prev + .05, op.a - .08); prev = op.b + .08;
            const sc = (toS(op.a) + toS(op.b)) / 2, w = op.b - op.a, h = op.y1 - op.y0, yc = (op.y0 + op.y1) / 2;
            if (op.real && notch) { const s0 = toS(op.a), s1 = toS(op.b); em('frame', s0, yc, .02, .08, h + .12, .1); em('frame', s1, yc, .02, .08, h + .12, .1); em('frame', sc, op.y0 - .02, .02, w + .12, .06, .1); em('frame', sc, op.y1 + .02, .02, w + .12, .06, .1); }
            else em('frame', sc, yc, .02, w + .12, h + .12, .08);
            em('frame', sc, op.y1 + .1, .06, w + .3, .2, .16);

            if (!(op.real && notch)) em('glass', sc, yc, .045, w - .04, h - .04, .03);
            if ((op.kind === 'door' || w > 1.4) && !(op.real && notch)) em('frame', sc, yc, .07, .06, h, .06);

            if (op.kind === 'win') em('sill', sc, op.y0 - .03, .1, w + .3, .06, .22);
            if (op.balc) { const [c0, c1, dp] = op.balc, bw = c1 - c0, bc = (toS(c0) + toS(c1)) / 2;
              em('bslab', bc, -.12, dp / 2, bw, .24, dp); em('bglass', bc, .55, dp - .06, bw - .12, 1.0, .025); em('brail', bc, 1.07, dp - .06, bw - .04, .045, .07); em('brail', bc, .06, dp - .06, bw - .04, .12, .08);
              for (const sd of [-1, 1]) { em('bglass', bc + sd * (bw / 2 - .06) * Math.sign(t[0] + t[1] || 1), .55, dp / 2, .025, 1.0, dp - .1); em('brail', bc + sd * (bw / 2 - .06) * Math.sign(t[0] + t[1] || 1), 1.07, dp / 2, .045, .045, dp - .1); } }
          });
          pier(prev, end - .05);
          continue;
        }
        if (L < 2.6) continue;
        const mid = org((sa + sb) / 2, 0); let balcOK = L >= 6;
        for (const f of [1.8, 2.8]) { const pt = [mid[0] + nrm[0] * f, mid[1] + nrm[1] * f]; if (allPolys.some(pp2 => inPoly(pt, pp2))) balcOK = false; }
        const usable = L - 1.4; const seq = ['B', 'A', 'W', 'A']; let si = (e + bi) % 2 === 0 ? 0 : 2; const row = []; let tot = 0;
        for (let guard = 0; guard < 40; guard++) { let ty = seq[si % 4]; si++; let w = BAY[ty]; if (tot + w > usable) { if (tot + BAY.W <= usable && ty !== 'A') { ty = 'W'; w = BAY.W; } else break; } row.push([ty, w]); tot += w; }
        if (row.length && row[row.length - 1][0] === 'A') { tot -= row.pop()[1]; }
        let cur = sa + (L - tot) / 2;
        // end piers (stone corners)
        em('pier', sa + (cur - sa) / 2, 1.35, .09, Math.max(.2, cur - sa - .04), 3.3, .18);
        row.forEach(([ty, w], ri) => {
          const c = cur + w / 2; cur += w;
          const F = (type, y, o2, ww, h, d, lat = 0) => em(type, c + lat, y, o2, ww, h, d);
          if (ty !== 'A') { F('pier', 1.35, .09, .34, 3.3, .18, -w / 2 + .17); if (ri === row.length - 1 || row[ri + 1][0] !== 'A') F('pier', 1.35, .09, .34, 3.3, .18, w / 2 - .17); }
          if (ty === 'B') {
            if (balcOK) {
              const dw = w - .9; F('frame', 1.2, .03, dw + .12, 2.42, .08); F('glass', 1.2, .05, dw - .02, 2.32, .03); F('frame', 1.2, .07, .06, 2.3, .06); F('frame', 2.48, .08, dw + .3, .16, .16);
              F('bslab', -.13, .7, w - .1, .26, 1.4); F('bglass', .56, 1.36, w - .2, 1.0, .025); F('brail', 1.08, 1.36, w - .12, .045, .07); F('brail', .06, 1.36, w - .12, .12, .08);
              F('bglass', .56, .72, .025, 1.0, 1.26, -(w - .16) / 2); F('bglass', .56, .72, .025, 1.0, 1.26, (w - .16) / 2); F('brail', 1.08, .72, .045, .045, 1.3, -(w - .16) / 2); F('brail', 1.08, .72, .045, .045, 1.3, (w - .16) / 2);
            } else { const ww = w - 1.0; F('frame', 1.55, .03, ww + .12, 1.72, .08); F('glass', 1.55, .05, ww - .02, 1.62, .03); F('frame', 1.55, .07, .06, 1.6, .06); F('sill', .66, .1, ww + .3, .06, .22); F('frame', 2.48, .07, ww + .3, .16, .14); }
          } else if (ty === 'W') { const ww = w - 1.0; F('frame', 1.55, .03, ww + .12, 1.72, .08); F('glass', 1.55, .05, ww - .02, 1.62, .03); F('frame', 1.55, .07, .06, 1.6, .06); F('sill', .66, .1, ww + .3, .06, .22); F('frame', 2.48, .07, ww + .3, .16, .14); }
          else { F('band', 1.35, .05, w, 3.3, .1); F('frame', 1.55, .1, .62, 1.78, .06); F('glass', 1.55, .11, .5, 1.66, .03); }
        });
        em('pier', cur + (sb - cur) / 2, 1.35, .09, Math.max(.2, sb - cur - .04), 3.3, .18);
      }
    });
    const zones = (o.customZones || []).filter(zn => zn.level === k);
    for (const tname of Object.keys(types)) {
      const Ls = lists[tname].filter(r => !zones.some(zn => r[0] > zn.rect[0] && r[0] < zn.rect[1] && r[2] > zn.rect[2] && r[2] < zn.rect[3])); if (!Ls.length) continue;
      const im = new T.InstancedMesh(BG, types[tname], Ls.length); im.name = tname; im.castShadow = ['bslab', 'band', 'pier'].includes(tname); im.receiveShadow = !['glass', 'bglass'].includes(tname); im.frustumCulled = false;
      Ls.forEach((r, i) => { const tt = r[6], nn = r[7]; X.set(tt[0], 0, tt[1]); Z.set(nn[0], 0, nn[1]); Rm.makeBasis(X, Y, Z); qq.setFromRotationMatrix(Rm); ss.set(r[3], r[4], r[5]);
        pp.set(r[0], r[1], r[2]); mtx.compose(pp, qq, ss); im.setMatrixAt(i, mtx); });
      if (tname === 'bglass') im.renderOrder = 2;
      g.add(im);
    }
    // level-6 notch: exterior walls of the corner unit with real openings (inner faces are lined by r_interior.js)
    if (notch) { const sb = blocks.south; const y0 = level, y1 = level + 3.0, Wm = M.plaster, th = .2;
      const face = (ops, along0, along1, mk) => { let c = along0; ops.forEach(op => { mk(c, op.a, y0, y1); mk(op.a, op.b, y0, y0 + op.y0); mk(op.a, op.b, y0 + op.y1, y1); c = op.b; }); mk(c, along1, y0, y1); };
      face(CORNER.north, XA, 16.78, (a, b, ya, yb) => { const m = wallBox(Wm, a, b, ya, yb, 1.91, 1.91 + th, { name: 'aptWall' }); if (m) g.add(m); });
      face(CORNER.east, 1.91, ZS, (a, b, ya, yb) => { const m = wallBox(Wm, 16.78 - th, 16.78, ya, yb, a, b, { name: 'aptWall' }); if (m) g.add(m); });
      const m2 = wallBox(Wm, 15.85, 16.78, y0, y1, ZS - th, ZS, { name: 'aptWall' }); if (m2) g.add(m2);
    }
  }
}

// ------------------------------------------------------------------ ground / basement / roof
function gridPoints(poly, sx, sz, inset) { const bb = bbox(poly), ip = offsetPoly(poly, -inset), out = []; for (let x = bb.min[0] + 1.5; x < bb.max[0]; x += sx) for (let z = bb.min[1] + 1.5; z < bb.max[1]; z += sz) if (inPoly([x, z], ip)) out.push([x, z]); return out; }
function carSpotsIn(poly, rows, seed, y, prob) {
  const R = rnd(seed), bb = bbox(poly), ip = offsetPoly(poly, -1.6), spots = [];
  for (let z = bb.min[1] + rows[0]; z < bb.max[1]; z += rows[1]) for (let x = bb.min[0] + 2; x < bb.max[0]; x += 2.7) {
    if (!inPoly([x, z], ip) || !inPoly([x, z + 2.3], ip) || !inPoly([x, z - 2.3], ip)) continue;
    const col = ((x - bb.min[0] - 1.5) % 7.5); if (Math.abs(col) < .8 || Math.abs(col - 7.5) < .8) continue;
    if (R() < prob) spots.push({ x, z, y, ang: R() < .5 ? 0 : Math.PI });
  } return spots;
}
const inRects = (x, z, rs, m = 0) => rs.some(r => x > r[0] - m && x < r[1] + m && z > r[2] - m && z < r[3] + m);
function buildGround(M, blocks, g, o) {
  const clear = o.clearRects || [];
  Object.values(blocks).forEach((blk, bi) => {
    const poly = blk.polygon, n = poly.length;
    g.add(mesh(prismGeo(offsetPoly(poly, .02), 3.05, 3.7, [offsetPoly(poly, -.2)]), M.plasterDark, { name: 'fascia' }));
    const cols = []; for (let e = 0; e < n; e++) { const a = poly[e], b = poly[(e + 1) % n], L = Math.hypot(b[0] - a[0], b[1] - a[1]); if (L < 2) continue; const k = Math.max(1, Math.round(L / 5)); for (let i = 0; i < k; i++) { const u = i / k; cols.push([a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u]); } }
    gridPoints(poly, 7.5, 8, 3).forEach(p => cols.push(p));
    const keep = cols.filter(c => !inRects(c[0], c[1], clear, .45));
    const im = new T.InstancedMesh(new T.BoxGeometry(.6, 3.7, .6), M.concreteDark, keep.length); const m4 = new T.Matrix4();
    keep.forEach((c, i) => { m4.makeTranslation(c[0], 1.85, c[1]); im.setMatrixAt(i, m4); }); im.castShadow = true; im.receiveShadow = true; g.add(im);
    const c = centroid(poly); const bb = bbox(poly); blk.core = bi ? [-1.9, 6.65] : [Math.min(bb.max[0] - 4, c[0] - 2), c[1]];
    if (!bi) g.add(box(5.5, 3.7, 6.5, M.concrete, blk.core[0], 1.85, blk.core[1]));
  });
  const ex = 11.9, ez = 1.91;
  g.add(box(9.6, .24, 3.4, M.roofDark, ex, 3.12, ez - 1.5, { name: 'canopy' })); g.add(box(9.6, .06, .06, M.goldHi, ex, 3.0, ez - 3.18, { name: 'canopyGold' }));
  for (const s of [-1, 1]) g.add(box(.14, 3.0, .14, M.frame, ex + s * 4.5, 1.5, ez - 3.0));
  blocks.south.entrance = [ex, ez - 1.5]; const nn = pm([540, 430]); blocks.north.entrance = [nn[0], nn[1]];
  const spots = [...carSpotsIn(blocks.south.polygon, [3, 8], 11, 0, .55), ...carSpotsIn(blocks.north.polygon, [3, 8], 5, 0, .5)].filter(s => !Object.values(blocks).some(b => Math.abs(s.x - b.core[0]) < 3.6 && Math.abs(s.z - b.core[1]) < 4.4) && !inRects(s.x, s.z, clear, 2.6) && !(s.x > 4 && s.z > 0 && s.z < 12));
  g.add(parkedCars(T, spots));
}
function buildBasement(M, blocks, g) {
  const px = (y) => 190 - 143 * (y - 170) / 832 + 40;
  const bp = PM([[px(240), 240], [600, 240], [600, 540], [925, 540], [1015, 640], [1047, 700], [1047, 975], [px(975), 975]]);
  g.add(mesh(prismGeo(bp, -3.75, -3.3), M.concrete, { name: 'basementSlab' }));
  g.add(mesh(prismGeo(offsetPoly(bp, .35), -3.3, -.05, [bp]), M.concreteDark, { name: 'basementWall' }));
  const cols = gridPoints(bp, 7.5, 8, 1.5); const im = new T.InstancedMesh(new T.BoxGeometry(.6, 3.2, .6), M.concrete, cols.length), m4 = new T.Matrix4();
  cols.forEach((c, i) => { m4.makeTranslation(c[0], -1.7, c[1]); im.setMatrixAt(i, m4); }); g.add(im);
  g.add(parkedCars(T, carSpotsIn(bp, [3, 8], 21, -3.3, .7)));
  g.userData.polygon = bp; return bp;
}
// Tower A roof terrace (sheet 04: "roof terrace +37.000", 1.2 m dwarf wall, 3x3 water tanks over the core):
// timber deck, black steel pergola with dark timber slats, sand-coloured low sofas, outdoor kitchen, dining table, terracotta pots, dense planting.
function buildRoofTerrace(M, g, blk, y0) {
  const c = blk.core, R = rnd(404); const L = (col) => new T.MeshLambertMaterial({ color: col });
  const tankM = new T.MeshLambertMaterial({ color: '#1f2226' }); // 3x3 tanks on the core
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) { const x = c[0] - 1.9 + i * 1.9, z = c[1] - 2.2 + j * 2.2; const t = mesh(new T.CylinderGeometry(.78, .78, 1.6, 18), tankM); t.position.set(x, y0 + 3.6 + .8, z); g.add(t); const cp = mesh(new T.CylinderGeometry(.25, .25, .1, 10), L('#3a3d40')); cp.position.set(x, y0 + 4.45, z); g.add(cp); }
  if (!TEX.deck) TEX.deck = canvasTex(512, 512, (gg, w, h) => { pixFill(gg, w, h, (x, y) => { const b = Math.floor(x / 32), v = hash2(b, Math.floor((y + b * 97) / 512 * 3), 7), gr = fbm(x / 6, y / 60, 3 + b, 3, 0); return (x % 32) < 3 ? [40, 32, 26] : mulc(mixc([112, 84, 64], [143, 106, 76], v), .82 + gr * .3); }); }, { rep: [1 / 1.6, 1 / 1.6] });
  const deckM = new T.MeshLambertMaterial({ map: TEX.deck });
  const D = [2.2, 15.0, 6.2, 17.6]; const deck = mesh(flatGeo([[D[0], D[2]], [D[1], D[2]], [D[1], D[3]], [D[0], D[3]]]).translate(0, y0 + .08, 0), deckM, { cast: false }); g.add(deck);
  g.add(aoDecal([[D[0], D[2]], [D[1], D[2]], [D[1], D[3]], [D[0], D[3]]], .9, .5, .01, y0 + .095).children[0].parent);
  // pergola 8 x 5 m
  const steel = new T.MeshPhongMaterial({ color: '#1E1E20', shininess: 20, specular: '#222222' }), slat = L('#3C2E24');
  const P = [6.0, 14.0, 10.6, 15.6], H = 2.9, yb = y0 + .1;
  for (const x of [P[0], (P[0] + P[1]) / 2, P[1]]) for (const z of [P[2], P[3]]) g.add(box(.12, H, .12, steel, x, yb + H / 2, z));
  for (const z of [P[2], P[3]]) g.add(box(P[1] - P[0] + .2, .3, .1, steel, (P[0] + P[1]) / 2, yb + H - .15, z));
  for (const x of [P[0], P[1]]) g.add(box(.1, .3, P[3] - P[2], steel, x, yb + H - .15, (P[2] + P[3]) / 2));
  const ns = Math.floor((P[1] - P[0]) / .15); const sl = new T.InstancedMesh(new T.BoxGeometry(.045, .07, P[3] - P[2] + .3), slat, ns); const m4 = new T.Matrix4();
  for (let i = 0; i < ns; i++) { m4.makeTranslation(P[0] + .08 + i * .15, yb + H + .04, (P[2] + P[3]) / 2); sl.setMatrixAt(i, m4); } sl.castShadow = true; g.add(sl);
  // linen curtain on the west side
  const lin = new T.MeshLambertMaterial({ color: '#E8E0D0', side: T.DoubleSide }); const cg = new T.PlaneGeometry(P[3] - P[2] - .4, H - .15, 24, 1); { const p = cg.attributes.position; for (let i = 0; i < p.count; i++) p.setZ(i, .06 * Math.sin(p.getX(i) * 9)); cg.computeVertexNormals(); }
  const cur = mesh(cg, lin); cur.rotation.y = Math.PI / 2; cur.position.set(P[0] + .12, yb + (H - .15) / 2, (P[2] + P[3]) / 2 + .2); cur.scale.x = .45; cur.position.z = P[2] + 1.2; g.add(cur);
  // low L sofa (sand), drum tables, lounge chairs
  const sand = L('#C8B79A'), sand2 = L('#BDAA8C'), drum = L('#2B2B2B'), terr = L('#A9623F'), conc = L('#A9A59E'), wood = L('#8F6A4C');
  const sofa = (x0, x1, z0, z1, back) => { g.add(box(x1 - x0, .38, z1 - z0, sand, (x0 + x1) / 2, yb + .19, (z0 + z1) / 2)); const bw = back === 'z1' ? [x1 - x0, .7, .22, (x0 + x1) / 2, z1 - .11] : back === 'x0' ? [.22, .7, z1 - z0, x0 + .11, (z0 + z1) / 2] : [x1 - x0, .7, .22, (x0 + x1) / 2, z0 + .11];
    g.add(box(bw[0], bw[1], bw[2], sand2, bw[3], yb + .35, bw[4])); for (let k = 0; k < 3; k++) { const cu = box(.42, .38, .14, k % 2 ? L('#D9CDB8') : L('#8E6B4E'), x0 + .5 + k * ((x1 - x0) - 1) / 2, yb + .58, back === 'z1' ? z1 - .3 : z0 + .3); cu.rotation.x = back === 'z1' ? .25 : -.25; g.add(cu); } };
  sofa(8.6, 12.6, 14.5, 15.5, 'z1'); sofa(8.6, 9.6, 12.0, 14.5, 'x0');
  for (const [x, z, r] of [[10.9, 13.3, .45], [11.8, 12.6, .3]]) { const d = mesh(new T.CylinderGeometry(r, r, .42, 20), drum); d.position.set(x, yb + .21, z); g.add(d); }
  const lounge = (x, z, a) => { const q = new T.Group(); q.position.set(x, yb, z); q.rotation.y = a; q.add(box(.8, .36, .8, sand, 0, .18, 0), box(.8, .5, .2, sand2, 0, .5, -.32), box(.18, .32, .7, sand2, .33, .5, 0), box(.18, .32, .7, sand2, -.33, .5, 0)); g.add(q); };
  lounge(12.9, 11.6, -2.4); lounge(10.4, 11.3, -3.4);
  g.add(box(4.2, .03, 3.0, L('#B9AE96'), 10.6, yb + .012, 13.6));  // outdoor rug
  // outdoor kitchen along the north side: concrete base, stone top, grill, tall fridge
  g.add(box(3.4, .88, .7, conc, 4.6, yb + .44, 11.0)); g.add(box(3.5, .05, .76, L('#C7C1B6'), 4.6, yb + .905, 11.0)); g.add(box(.7, .1, .45, steel, 4.0, yb + .98, 11.0));
  g.add(box(.7, 1.9, .7, L('#BFC3C4'), 2.65, yb + .95, 11.0));
  // dining under the open sky: timber table + stools
  g.add(box(2.2, .06, .95, wood, 5.3, yb + .74, 8.2)); for (const sx of [-1, 1]) g.add(box(.08, .72, .8, steel, 5.3 + sx * .95, yb + .36, 8.2));
  for (let k = 0; k < 6; k++) { const st = box(.42, .45, .42, wood, 4.6 + (k % 3) * .7, yb + .225, 8.2 + (k < 3 ? -.85 : .85)); st.rotation.y = (R() - .5) * .3; g.add(st); }
  // planters along the parapet + big terracotta pots
  const pots = []; for (let x = 2.6; x < 14.6; x += 1.15) pots.push([x, 17.25]); for (let z = 6.6; z < 16.6; z += 1.3) pots.push([2.6, z]); pots.push([13.8, 9.6], [7.2, 12.2], [14.3, 16.0], [6.4, 15.0]);
  const potI = new T.InstancedMesh(new T.CylinderGeometry(.32, .24, .55, 14).translate(0, .275, 0), terr, pots.length); pots.forEach(([x, z], i) => { const s = .8 + R() * .5; m4.compose(new T.Vector3(x, yb, z), new T.Quaternion(), new T.Vector3(s, s, s)); potI.setMatrixAt(i, m4); }); potI.castShadow = true; g.add(potI);
  const plantLines = pots.map(([x, z]) => [[x, z], [x + .01, z], 1, .7 + R() * .9, [.24 + R() * .05, .45, .26]]); const pl = makeShrubs(T, plantLines, { seed: 41 }); pl.position.y = yb + .45; g.add(pl);
  // agave/sansevieria spikes in a few pots
  const spike = new T.InstancedMesh(new T.ConeGeometry(.05, .8, 4).translate(0, .4, 0), L('#5F7A48'), 60); let si = 0;
  [[13.8, 9.6], [7.2, 12.2], [6.4, 15.0]].forEach(([x, z]) => { for (let k = 0; k < 20; k++) { const a = k * 2.4, tl = .25 + R() * .35; m4.compose(new T.Vector3(x + Math.cos(a) * .1, yb + .5, z + Math.sin(a) * .1), new T.Quaternion().setFromEuler(new T.Euler(Math.cos(a) * tl, 0, Math.sin(a) * tl)), new T.Vector3(1, .8 + R() * .6, 1)); spike.setMatrixAt(si++, m4); } }); g.add(spike);
  // string of festoon bulbs across the open dining area
  const bulbM = new T.MeshLambertMaterial({ color: '#fff4dc', emissive: '#ffd9a0', emissiveIntensity: .5 }); const bulbs = new T.InstancedMesh(new T.SphereGeometry(.05, 6, 4), bulbM, 22);
  for (let i = 0; i < 22; i++) { const u = i / 21, x = 3.2 + u * 4.2, z = 6.8 + u * 3.6, y = yb + 2.75 - Math.sin(u * Math.PI) * .45; m4.makeTranslation(x, y, z); bulbs.setMatrixAt(i, m4); } g.add(bulbs);
}
function buildRoof(M, blocks, g, signText) {

  const y0 = LEVELS.roof, R = rnd(77);
  Object.values(blocks).forEach((blk, bi) => {
    const p = blk.polygon;
    g.add(mesh(prismGeo(offsetPoly(p, .14), y0 - .3, y0), M.slab, { name: 'roofSlab' }));
    g.add(mesh(prismGeo(offsetPoly(p, .02), y0, y0 + 1.1, [offsetPoly(p, -.25)]), M.plaster, { name: 'parapet' }));
    g.add(mesh(prismGeo(offsetPoly(p, .1), y0 + 1.1, y0 + 1.2, [offsetPoly(p, -.33)]), M.sill, { name: 'coping' }));
    g.add(mesh(flatGeo(offsetPoly(p, -.3)).translate(0, y0 + .02, 0), M.roofDark, { cast: false, name: 'roofDeck' }));
    const c = blk.core; g.add(box(6, 3.4, 7, M.plaster, c[0], y0 + 1.7, c[1], { name: 'overrun' })); g.add(box(6.4, .22, 7.4, M.sill, c[0], y0 + 3.5, c[1]));
    if (bi === 1) { buildRoofTerrace(M, g, blk, y0); return; }
    // water tanks on a steel stand, condensers, PV array, roof hatch
    const tankM = new T.MeshStandardMaterial({ color: bi ? '#1d2024' : '#2a4e7a', roughness: .6 });
    for (let i = 0; i < 3; i++) { const t = mesh(new T.CylinderGeometry(1.0, 1.0, 1.9, 20), tankM); t.position.set(c[0] + 4.6, y0 + 1.75, c[1] - 2.6 + i * 2.6); g.add(t); const cap = mesh(new T.SphereGeometry(1.0, 16, 6, 0, 6.3, 0, .5), tankM); cap.position.set(c[0] + 4.6, y0 + 2.62, c[1] - 2.6 + i * 2.6); g.add(cap); }
    g.add(box(2.4, .12, 8.0, M.rail, c[0] + 4.6, y0 + .76, c[1])); for (const dz of [-3.6, 3.6]) for (const dx of [-1, 1]) g.add(box(.1, .76, .1, M.rail, c[0] + 4.6 + dx, y0 + .38, c[1] + dz));
    const bb = bbox(p); const pv = new T.MeshStandardMaterial({ color: '#1a2333', roughness: .25, metalness: .4 }); pv.userData.env = 1;
    const pvm = new T.InstancedMesh(new T.BoxGeometry(1.0, .04, 1.7), pv, 40); let k = 0; const m4 = new T.Matrix4(), q = new T.Quaternion().setFromEuler(new T.Euler(-.17, 0, 0));
    for (let i = 0; i < 8 && k < 40; i++) for (let j = 0; j < 5 && k < 40; j++) { const x = bb.min[0] + 3 + i * 1.1, z = bb.min[1] + 3 + j * 2.2; if (!inPoly([x, z], offsetPoly(p, -1.5)) || Math.hypot(x - c[0], z - c[1]) < 6) continue; m4.compose(new T.Vector3(x, y0 + .55, z), q, new T.Vector3(1, 1, 1)); pvm.setMatrixAt(k++, m4); }
    pvm.count = k; pvm.castShadow = true; g.add(pvm);
    for (let i = 0; i < 4; i++) g.add(box(.9, .7, .45, M.white, c[0] - 4.2, y0 + .35, c[1] - 3 + i * 1.4));
  });
  // sign: dark standing-seam band on the south block roof edge, ivory serif lettering (both faces)
  const sx = 15.25, z0 = pm([0, 645])[1], z1 = pm([0, 935])[1], len = z1 - z0, zc = (z0 + z1) / 2, sh = 3.6, th = .45, yc = y0 + 1.1 + sh / 2 - .5;
  const sg = new T.Group(); sg.name = 'sign'; g.add(sg);
  const band = box(th, sh, len, M.signDark, sx, yc, zc, { name: 'signBand' }); band.geometry = worldUV(new T.BoxGeometry(th, sh, len), sx, yc, zc); sg.add(band);
  sg.add(box(th + .06, .08, len + .06, M.sill, sx, yc + sh / 2 + .04, zc));
  for (const z of [z0 + 1.2, z1 - 1.2, zc]) sg.add(box(.15, 1.2, .15, M.rail, sx - .5, y0 + .6, z));
  const tw = len * .84, th2 = 2.4;
  const te = letterPlane(signText, tw, th2); te.rotation.y = Math.PI / 2; te.position.set(sx + th / 2 + .03, yc + .05, zc); sg.add(te);
  const tw2 = letterPlane(signText, tw, th2); tw2.rotation.y = -Math.PI / 2; tw2.position.set(sx - th / 2 - .03, yc + .05, zc); sg.add(tw2);
  g.userData.sign = sg;
}

// ------------------------------------------------------------------ site helpers
function seg(a, b, h, th, mat, y0 = 0) { const L = Math.hypot(b[0] - a[0], b[1] - a[1]); const g = worldUV(new T.BoxGeometry(L, h, th), L / 2, y0 + h / 2, 0); const m = mesh(g, mat); m.position.set((a[0] + b[0]) / 2, y0 + h / 2, (a[1] + b[1]) / 2); m.rotation.y = -Math.atan2(b[1] - a[1], b[0] - a[0]); return m; }
function strip(a, b, w, inward, mat, y) {
  const g = new T.BufferGeometry(); const v = [a, b, [b[0] + inward[0] * w, b[1] + inward[1] * w], [a[0] + inward[0] * w, a[1] + inward[1] * w]];
  g.setAttribute('position', new T.Float32BufferAttribute(v.flatMap(p => [p[0], y, p[1]]), 3));
  const cr = (v[1][0] - v[0][0]) * (v[2][1] - v[0][1]) - (v[1][1] - v[0][1]) * (v[2][0] - v[0][0]); g.setIndex(cr < 0 ? [0, 1, 2, 0, 2, 3] : [0, 2, 1, 0, 3, 2]); g.setAttribute('normal', new T.Float32BufferAttribute([0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], 3));
  g.setAttribute('uv', new T.Float32BufferAttribute(v.flatMap(p => [p[0], -p[1]]), 2));
  const m = new T.Mesh(g, mat); m.receiveShadow = true; return m;
}
// soft ambient-occlusion decal around/under a footprint (multiply blend): inside darkness k, fades over fin inside / fout outside
export function aoDecal(poly, k = .55, fin = 2.5, fout = 1.6, y = .035) {
  const rings = [[offsetPoly(poly, -fin), k], [poly, Math.min(1, k + .12)], [offsetPoly(poly, fout), 1]]; const pos = [], col = [], idx = [];
  rings.forEach(([r, c]) => r.forEach(p => { pos.push(p[0], y, p[1]); col.push(c, c, c); }));
  const n = poly.length; for (let ri = 0; ri < 2; ri++) for (let i = 0; i < n; i++) { const a = ri * n + i, b = ri * n + (i + 1) % n, c = (ri + 1) * n + (i + 1) % n, d = (ri + 1) * n + i; idx.push(a, d, c, a, c, b); }
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3)); g.setAttribute('color', new T.Float32BufferAttribute(col, 3)); g.setIndex(idx);
  const inner = new T.ShapeGeometry(shapeOf(rings[0][0])); inner.rotateX(-Math.PI / 2); inner.translate(0, y, 0); const ic = []; for (let i = 0; i < inner.attributes.position.count; i++) ic.push(k, k, k); inner.setAttribute('color', new T.Float32BufferAttribute(ic, 3));
  const mat = new T.MeshBasicMaterial({ vertexColors: true, blending: T.MultiplyBlending, transparent: true, depthWrite: false, toneMapped: false, side: T.DoubleSide, polygonOffset: true, polygonOffsetFactor: -3, polygonOffsetUnits: -3, fog: false });
  const grp = new T.Group(); grp.add(new T.Mesh(g, mat), new T.Mesh(inner, mat)); grp.children.forEach(m => m.renderOrder = 1); grp.name = 'ao'; return grp;
}
const MOODS = {
  day: { terrain: null, grass: '#ffffff', paver: '#ffffff', paverPale: '#ffffff', asphalt: '#ffffff', road: '#ffffff', wall: '#E2DCCD' },
  ink: { terrain: null, grass: '#1C2620', paver: '#2A2A2E', paverPale: '#3A3A3F', asphalt: '#1A1A1D', road: '#17171A', wall: '#3A3A3E' },
};
let BRICK; function brickMat() { if (BRICK) return BRICK;
  const t = canvasTex(512, 256, (g, w, h) => { pixFill(g, w, h, (x, y) => { const r = Math.floor(y / 32), c = Math.floor((x + (r % 2) * 64) / 128); const v = hash2(c, r, 5), n = fbm(x / 10, y / 10, 3, 3, 51);
      const mort = (y % 32) < 4 || ((x + (r % 2) * 64) % 128) < 4; return mort ? mulc([178, 166, 150], .9 + n * .15) : mulc(mixc([150, 72, 48], [178, 98, 64], v), .8 + n * .35); }); }, { rep: [1 / 1.15, 1 / .6] });
  BRICK = new T.MeshStandardMaterial({ map: t, roughness: .92 }); return BRICK; }

function buildSite(M, blocks, o) {
  const site = new T.Group(); site.name = 'site'; const ground = new T.Group(); ground.name = 'ground'; site.add(ground);
  const plot = PM(PLOT_PX), rd = roadGeometry();
  const ramp = PM(RAMP_PX);
  const poolHole = offsetPoly(PM(POOL_WATER_PX), .34);
  const base = mesh(flatGeo(plot, [ramp, poolHole]), M.paver, { cast: false }); base.name = 'plotBase'; ground.add(base);
  // road reserve (footpath), road, kerbs, centre dashes, edge lines, side drains
  const R = (s0, s1, o0, o1, mat, y, name) => { const a = rd.at(s0, o0), b = rd.at(s1, o0); const m = strip(a, b, o1 - o0, rd.n, mat, y); if (name) m.name = name; return m; };
  // Naguru Vale Road as filmed: narrow two-lane tarmac (6.7 m), white edge lines, red murram + grass verges, low rubble-stone edge
  ground.add(R(-300, rd.L + 300, 0, 5.9, M.verge, .02, 'roadReserve')); ground.add(R(-300, rd.L + 300, 5.9, 12.6, M.road, .01, 'road')); ground.add(R(-300, rd.L + 300, 12.6, 17.6, M.verge, .02));
  const lineM = new T.MeshLambertMaterial({ color: '#DDD9CE' }); const m4 = new T.Matrix4(), q = new T.Quaternion();
  for (const off of [6.1, 12.3]) { const a = rd.at(-300, off), b = rd.at(rd.L + 300, off); const l = strip(a, b, .13, rd.n, lineM, .016); ground.add(l); }
  { const a = rd.at(-300, .25), b = rd.at(rd.L + 300, .25); const k = seg(a, b, .32, .45, M.rubble, 0); k.castShadow = false; ground.add(k); }

  // planting strips inside the plot (setbacks) + lawn by the pool
  const inw = (a, b) => { const A = area2(plot); const n = edgeNormal(a, b, A); return [-n[0], -n[1]]; };
  const P = plot; const gs = (a, b, w, y = .03) => { const m = strip(a, b, w, inw(a, b), M.grass, y); m.name = 'planting'; ground.add(m); };
  gs(P[0], P[1], 2.6); gs(P[3], P[0], 2.6); gs(pm([100, 1002]), pm([1047, 1002]), 2.4);
  const dp = (y) => pm([xDiag(y), y]); gs(dp(188), dp(500), 2.6); gs(dp(660), dp(792), 2.4);
  ground.add((() => { const g = flatGeo(PM([[600, 215], [645, 195], [925, 516], [600, 530]]), [poolHole]).translate(0, .035, 0); const m = mesh(g, M.grass, { cast: false }); m.name = 'poolLawn'; return m; })());
  // driveway asphalt + bay markings + kerb edges
  const drive = mesh(flatGeo(PM(DRIVE_PX)).translate(0, .045, 0), M.asphalt, { cast: false }); drive.name = 'driveway'; ground.add(drive);
  const bays = new T.InstancedMesh(new T.BoxGeometry(.1, .012, 5), lineM, 40); let bi = 0;
  [[725, 815], [890, 975]].forEach(([y0, y1]) => { for (let i = 0; i <= 6; i++) { const c = pm([805 + i * 46, (y0 + y1) / 2]); m4.makeTranslation(c[0], .055, c[1]); bays.setMatrixAt(bi++, m4); } }); bays.count = bi; ground.add(bays);
  // AO under / around the blocks, guardhouse
  Object.values(blocks).forEach(b => ground.add(aoDecal(b.polygon, .5, 3.0, 1.4)));
  // boundary wall: red brick, piers every ~3 m, concrete coping, dark sliding gate
  const wall = new T.Group(); wall.name = 'boundaryWall'; site.add(wall); const WH = 2.3, WT = .23, brk = brickMat();
  const gateC = pm(GATE_PX); const gp = (s) => rd.at(s, 0); const sGate = ((gateC[0] - rd.A[0]) * rd.u[0] + (gateC[1] - rd.A[1]) * rd.u[1]);
  const wp = (a, b) => { wall.add(seg(a, b, WH, WT, brk)); wall.add(seg(a, b, .08, WT + .1, M.sill, WH));
    const L = Math.hypot(b[0] - a[0], b[1] - a[1]), k = Math.max(1, Math.round(L / 3.2)); for (let i = 0; i <= k; i++) { const u = i / k, x = a[0] + (b[0] - a[0]) * u, z = a[1] + (b[1] - a[1]) * u; const pr = box(.42, WH + .18, .42, brk, x, (WH + .18) / 2, z); pr.rotation.y = -Math.atan2(b[1] - a[1], b[0] - a[0]); wall.add(pr); wall.add(box(.5, .07, .5, M.sill, x, WH + .2, z)); } };
  const sEnd = ((pm([xDiag(792), 792])[0] - rd.A[0]) * rd.u[0] + (pm([xDiag(792), 792])[1] - rd.A[1]) * rd.u[1]);
  wp(P[3], P[0]); wp(P[0], P[1]); wp(P[3], pm([1047, 1002])); wp(gp(0), gp(sGate - 4.8)); wp(gp(sGate + 4.8), gp(sEnd));
  const gate = new T.Group(); gate.name = 'gate'; site.add(gate); const ang = -Math.atan2(rd.u[1], rd.u[0]);
  for (const s of [-4.8, 4.8]) { const c = gp(sGate + s); const pil = new T.Group(); pil.position.set(c[0], 0, c[1]); pil.rotation.y = ang; pil.add(box(.9, 2.9, .9, M.plaster, 0, 1.45, 0), box(1.05, .16, 1.05, M.sill, 0, 2.98, 0), box(.3, .25, .12, new T.MeshStandardMaterial({ color: '#fff3dd', emissive: '#ffd9a0', emissiveIntensity: .4 }), 0, 2.4, .5)); gate.add(pil); }
  const gateM = new T.MeshPhongMaterial({ color: '#1E1F22', shininess: 40, specular: '#333333' });
  const leaf = new T.Group(); leaf.name = 'gateLeaf'; leaf.rotation.y = ang; leaf.add(box(9.2, .12, .1, gateM, 0, .18, 0), box(9.2, .12, .1, gateM, 0, 2.2, 0)); for (let i = -22; i <= 22; i++) leaf.add(box(.06, 2.05, .06, gateM, i * .205, 1.2, 0));
  leaf.add(box(9.2, .5, .04, gateM, 0, 1.95, 0)); gate.add(leaf);
  const inwG = [-rd.n[0], -rd.n[1]];
  const setGate = (f) => { const s = sGate + f * 9.4; const c = gp(s); leaf.position.set(c[0] + inwG[0] * .55, 0, c[1] + inwG[1] * .55); }; setGate(0);
  gate.userData.setOpen = setGate;
  { const c = gp(sGate - 9.5); const plaque = new T.Group(); plaque.position.set(c[0] + rd.n[0] * 1.5, 0, c[1] + rd.n[1] * 1.5); plaque.rotation.y = ang; plaque.add(box(6.2, 1.7, .5, brk, 0, .85, 0)); plaque.add(box(6.35, .09, .6, M.sill, 0, 1.74, 0));
    for (const s of [1, -1]) { const t = letterPlane('Vanta House', 5.0, .9, { fs: .7 }); t.position.set(0, .92, s * .26); t.rotation.y = s > 0 ? 0 : Math.PI; plaque.add(t); } gate.add(plaque); }
  // guardhouse
  const gc = pm(GUARD_PX.c), gw = GUARD_PX.w * SC, gd = GUARD_PX.d * SC; const gh = new T.Group(); gh.name = 'guardhouse'; gh.position.set(gc[0], 0, gc[1]); site.add(gh);
  gh.add(box(gw, 3.0, gd, M.plaster, 0, 1.5, 0), box(gw + .9, .32, gd + .9, M.frame, 0, 3.16, 0), box(gw + .6, .1, gd + .6, M.grass, 0, 3.36, 0));
  gh.add(makeShrubs(T, [[[-gw / 2, -gd / 2 + .1], [gw / 2, -gd / 2 + .1], .7, .35, [.25, .35, .3]], [[-gw / 2, gd / 2 - .1], [gw / 2, gd / 2 - .1], .8, .3, [.22, .4, .28]]], { seed: 5 }).translateY(3.4));

  const ghg = new T.InstancedMesh(new T.BoxGeometry(1, 1, 1), M.glass, 6); let gi = 0; for (const s of [-1, 1]) for (const xx of [-3.2, 0, 3.2]) { m4.compose(new T.Vector3(xx, 1.75, s * (gd / 2 + .02)), new T.Quaternion().setFromAxisAngle(new T.Vector3(0, 1, 0), s > 0 ? 0 : Math.PI), new T.Vector3(2.4, 1.3, .04)); ghg.setMatrixAt(gi++, m4); } gh.add(ghg);
  gh.add(box(gw + .02, .5, gd + .02, M.plasterDark, 0, .25, 0)); gh.add(aoDecal([[-gw / 2, -gd / 2], [gw / 2, -gd / 2], [gw / 2, gd / 2], [-gw / 2, gd / 2]], .6, .4, 1.2));
  // ramp (14 deg) down to the basement
  const rampG = new T.Group(); rampG.name = 'ramp'; site.add(rampG); const xE = ramp[2][0]; const yr = (x) => -Math.max(0, Math.min(3.3, Math.tan(14 * Math.PI / 180) * (xE - x)));
  { const v = ramp.map(p => [p[0], yr(p[0]) + .02, p[1]]); const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(v.flat(), 3)); g.setIndex([0, 2, 1, 0, 3, 2]); g.computeVertexNormals(); const mm = new T.Mesh(g, M.concreteDark); mm.receiveShadow = true; mm.name = 'rampSurface'; rampG.add(mm);
    for (const [i, j] of [[0, 1], [1, 2], [2, 3]]) { const a = ramp[i], b = ramp[j]; const vv = [[a[0], yr(a[0]), a[1]], [b[0], yr(b[0]), b[1]], [b[0], .12, b[1]], [a[0], .12, a[1]]]; const wg = new T.BufferGeometry(); wg.setAttribute('position', new T.Float32BufferAttribute(vv.flat(), 3)); wg.setIndex([0, 1, 2, 0, 2, 3, 0, 2, 1, 0, 3, 2]); wg.computeVertexNormals(); const wm = new T.Mesh(wg, M.concrete); wm.receiveShadow = true; rampG.add(wm); } }
  const pool = buildPool(M); site.add(pool.group);
  const trees = buildTrees(M, rd, blocks); site.add(trees.group);
  const boundaryPoints = plot.map(p => new T.Vector3(p[0], 0, p[1]));
  const setMood = (mood) => { const pal = MOODS[mood] || MOODS.day; Object.keys(pal).forEach(k => { if (pal[k] && M[k]) M[k].color.set(pal[k]); }); };
  return { group: site, ground, boundaryPoints, road: { group: ground.getObjectByName('road'), geometry: rd, lane: rd.lane }, gate, guardhouse: gh, ramp: rampG, trees, pool, setMood, polygon: plot, sGate };
}

// ------------------------------------------------------------------ vegetation
let VEG; function vegGeos() {
  if (VEG) return VEG;
  const blobG = (seed, det = 2) => { const g = new T.IcosahedronGeometry(1, det); const p = g.attributes.position, c = [];
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i); const n = fbm(x * 1.7 + seed, z * 1.7 + y * 1.3, seed, 3), k = .78 + n * .5; p.setXYZ(i, x * k, y * k * .85, z * k); const ao = .5 + .5 * Math.min(1, Math.max(0, (y + .9) / 1.6)); c.push(ao, ao, ao); }
    g.setAttribute('color', new T.Float32BufferAttribute(c, 3)); g.computeVertexNormals();
    { const nn = g.attributes.normal; for (let i = 0; i < p.count; i++) { const v = new T.Vector3(p.getX(i), p.getY(i) * 1.15, p.getZ(i)).normalize(); const f = new T.Vector3(nn.getX(i), nn.getY(i), nn.getZ(i)); v.lerp(f, .25).normalize(); nn.setXYZ(i, v.x, v.y, v.z); } }
    return g; };
  const trunk = new T.CylinderGeometry(.12, .2, 1, 7).translate(0, .5, 0);
  const prof = []; for (let i = 0; i <= 12; i++) { const y = i / 12; prof.push(new T.Vector2(.2 - .05 * y + (i === 0 ? .07 : 0) + .015 * Math.sin(y * 40), y)); }
  const palmTrunk = new T.LatheGeometry(prof, 8); { const p = palmTrunk.attributes.position; for (let i = 0; i < p.count; i++) { const y = p.getY(i); p.setX(i, p.getX(i) + .35 * y * y); } palmTrunk.computeVertexNormals(); }
  const fr = new T.PlaneGeometry(1.0, 3.3, 2, 10); fr.rotateX(-Math.PI / 2); fr.translate(0, 0, 1.65);
  { const p = fr.attributes.position; for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i), u = z / 3.3; p.setY(i, .9 * Math.sin(u * Math.PI * .55) - 1.5 * u * u - Math.abs(x) * .28 * (1 - u * .5)); p.setX(i, x * (.35 + .65 * Math.sin(Math.PI * Math.min(1, u * 1.15 + .05)))); } fr.computeVertexNormals(); }
  const cardCrown = (n, seed, sz = 1.25, shell = true) => { const R = rnd(seed), pos = [], nor = [], uv = [], col = [], idx = []; const q = new T.Quaternion(), e = new T.Euler(), v = new T.Vector3();
    for (let i = 0; i < n; i++) { let x, y, z; do { x = R() * 2 - 1; y = R() * 2 - 1; z = R() * 2 - 1; } while (x * x + y * y + z * z > 1); const rr = Math.pow(x * x + y * y + z * z, .5), k = (shell ? .78 + .22 * R() : .55 + .45 * Math.pow(rr, .35)) / Math.max(rr, 1e-3); x *= k; y *= k * .85; z *= k;
      if (shell) { q.setFromUnitVectors(new T.Vector3(0, 0, 1), new T.Vector3(x, y, z).normalize()); q.multiply(new T.Quaternion().setFromEuler(e.set((R() - .5) * 1.4, (R() - .5) * 1.4, R() * 6.3))); } else q.setFromEuler(e.set(R() * 6.3, R() * 6.3, R() * 6.3)); const s = sz * (.75 + R() * .5), b = pos.length / 3, u0 = (R() < .5 ? 0 : .5);
      [[-1, -1], [1, -1], [1, 1], [-1, 1]].forEach(([a, c]) => { v.set(a * s / 2, c * s / 2, 0).applyQuaternion(q); const px = x + v.x, py = y + v.y, pz = z + v.z; pos.push(px, py, pz); const L = Math.hypot(px, py * 1.2, pz) || 1; nor.push(px / L, py * 1.2 / L, pz / L);
        uv.push(u0 + (a + 1) / 4, (c + 1) / 2); const ao = .45 + .55 * Math.min(1, Math.max(0, (py + 1) / 1.7)) * (.6 + .4 * Math.min(1, L)); col.push(ao, ao, ao); });
      idx.push(b, b + 1, b + 2, b, b + 2, b + 3); }
    const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3)); g.setAttribute('normal', new T.Float32BufferAttribute(nor, 3)); g.setAttribute('uv', new T.Float32BufferAttribute(uv, 2)); g.setAttribute('color', new T.Float32BufferAttribute(col, 3)); g.setIndex(idx); return g; };
  VEG = { blob: blobG(3), blobLo: blobG(9, 1), trunk, palmTrunk, frond: fr, crown: cardCrown(30, 5, .95), crown2: cardCrown(22, 8, 1.0), crownLo: cardCrown(26, 11, 1.9) }; return VEG;
}
let CARDT; export function leafCardTex() { if (CARDT) return CARDT;
  CARDT = canvasTex(512, 256, (g, w, h) => { g.clearRect(0, 0, w, h); for (let half = 0; half < 2; half++) { const R = rnd(31 + half), cx = half * 256 + 128;
      g.strokeStyle = 'rgba(80,60,40,1)'; g.lineWidth = 2; for (let i = 0; i < 6; i++) { g.beginPath(); g.moveTo(cx, 200); g.lineTo(cx + (R() - .5) * 200, 40 + R() * 120); g.stroke(); }
      for (let i = 0; i < 260; i++) { const a = R() * 6.283, r = Math.sqrt(R()) * 108, x = cx + Math.cos(a) * r, y = 128 + Math.sin(a) * r * .95; const L = 14 + R() * 10, l = 30 + R() * 22;
        g.fillStyle = `hsl(${85 + R() * 30},${45 + R() * 20}%,${l}%)`; g.save(); g.translate(x, y); g.rotate(R() * 6.283); g.beginPath(); g.ellipse(0, 0, L / 2, L / 5, 0, 0, 6.283); g.fill(); g.restore(); } } }, { aniso: 4 });
  CARDT.wrapS = CARDT.wrapT = T.ClampToEdgeWrapping; return CARDT; }
let LEAFT; function leafTex() { if (LEAFT) return LEAFT; LEAFT = canvasTex(256, 256, (g, w, h) => { pixFill(g, w, h, (x, y) => { const n = fbm(x / 6, y / 6, 3, 3, 43), s = hash2(x >> 1, y >> 1, 9); return mulc([255, 255, 255], .6 + n * .5 + (s > .8 ? .2 : 0) - (s < .2 ? .38 : 0)).map(v => Math.max(0, Math.min(255, v))); }); }, { rep: [4, 4], srgb: false }); return LEAFT; }
export function makeTrees(THREE, list, palms, o = {}) {   // list: [[x,z,(h),(r)]], palms: [[x,z,(h)]]
  T = THREE; buildTextures(); const V = vegGeos(), g = new T.Group(); g.name = 'trees'; const R = rnd(o.seed || 3);
  const trunkM = new T.MeshLambertMaterial({ color: '#6b5a48', map: TEX.bark });
  const crownM = swayMat(new T.MeshLambertMaterial({ vertexColors: true, map: leafCardTex(), alphaTest: .5, side: T.DoubleSide }), .05);
  const coreM = swayMat(new T.MeshLambertMaterial({ vertexColors: true, map: leafTex(), color: '#7d8a62' }), .05);
  const frondM = swayMat(new T.MeshLambertMaterial({ map: TEX.frond, alphaTest: .5, side: T.DoubleSide, color: '#b7c79a' }), .12, 'frond');
  const nb = list.length; const trunk = new T.InstancedMesh(V.trunk, trunkM, nb * 3), crown = new T.InstancedMesh(V.crown, crownM, nb * 5), core = new T.InstancedMesh(V.blobLo, coreM, nb * 5);
  const ptr = new T.InstancedMesh(V.palmTrunk, new T.MeshLambertMaterial({ color: '#9a8a74', map: TEX.bark }), palms.length), frond = new T.InstancedMesh(V.frond, frondM, palms.length * 16);
  const nut = new T.InstancedMesh(new T.SphereGeometry(.13, 6, 5), new T.MeshStandardMaterial({ color: '#4d5a2a', roughness: .8 }), palms.length * 5);
  const m4 = new T.Matrix4(), q = new T.Quaternion(), e = new T.Euler(), v = new T.Vector3(), s = new T.Vector3(), c = new T.Color(); let ti = 0, ci = 0, fi = 0, ni = 0;
  list.forEach(([x, z, hh, rr]) => {
    const h = hh || 3.0 + R() * 2.2, r = rr || 2.0 + R() * 1.4, ya = R() * 6.28, lean = (R() - .5) * .12;
    q.setFromEuler(e.set(lean, ya, -lean)); m4.compose(v.set(x, 0, z), q, s.set(1.2, h + r * .5, 1.2)); trunk.setMatrixAt(ti++, m4);
    for (const bk of [-1, 1]) { q.setFromEuler(e.set(.7 * bk, ya + bk, 0)); m4.compose(v.set(x, h * .62, z), q, s.set(.6, r * .9, .6)); trunk.setMatrixAt(ti++, m4); }
    const hue = .22 + R() * .07, sat = .38 + R() * .18, lit = .24 + R() * .1;
    for (let k = 0; k < 5; k++) { const a = k / 4 * 6.28 + R(), d = k ? r * (.45 + R() * .3) : 0, rk = r * (k ? .6 + R() * .25 : .85);
      q.setFromEuler(e.set(R() * 3, R() * 3, R() * 3)); m4.compose(v.set(x + Math.cos(a) * d, h + r * .55 + (k ? (R() - .3) * r * .5 : r * .2), z + Math.sin(a) * d), q, s.set(rk, rk * .82, rk)); crown.setMatrixAt(ci, m4);
      m4.compose(v, q, s.multiplyScalar(.8)); core.setMatrixAt(ci, m4); core.setColorAt(ci, c.setHSL(.24, .3, .32));
      crown.setColorAt(ci++, c.setHSL(.1, .08, .62 + lit + (R() - .5) * .1)); }
  });
  palms.forEach(([x, z, hh]) => {
    const h = hh || 6 + R() * 4, ya = R() * 6.28; q.setFromEuler(e.set(0, ya, (R() - .5) * .06)); m4.compose(v.set(x, 0, z), q, s.set(1, h, 1)); ptr.setMatrixAt(ti % 1 + (fi / 16 | 0), m4);
    const top = new T.Vector3(.35, 1, 0).applyMatrix4(m4);
    for (let k = 0; k < 16; k++) { const ring = k < 6 ? 0 : 1; const a = k * 2.399 + R() * .3, pitch = ring ? .35 + R() * .45 : -.35 + R() * .4, sc = .8 + R() * .3;
      q.setFromEuler(e.set(pitch, a, (R() - .5) * .3, 'YXZ')); m4.compose(v.set(top.x, top.y - .1, top.z), q, s.set(sc, sc, sc)); frond.setMatrixAt(fi++, m4); }
    for (let k = 0; k < 5; k++) { m4.makeTranslation(top.x + Math.cos(k * 1.3) * .22, top.y - .35 - (k % 2) * .12, top.z + Math.sin(k * 1.3) * .22); nut.setMatrixAt(ni++, m4); }
  });
  crown.instanceColor.needsUpdate = true; core.instanceColor.needsUpdate = true;
  [trunk, crown, core, ptr, frond, nut].forEach(m => { m.castShadow = true; m.receiveShadow = true; m.frustumCulled = false; g.add(m); });
  return { group: g, positions: list.concat(palms) };
}
// hedges / shrubs / flowering bushes along lines: [[a,b], spacing, height, colourHSL]
export function makeShrubs(THREE, lines, o = {}) {
  T = THREE; const V = vegGeos(), R = rnd(o.seed || 17); const pts = [];
  lines.forEach(([a, b, sp, h, hsl]) => { const L = Math.hypot(b[0] - a[0], b[1] - a[1]), n = Math.max(1, Math.floor(L / sp)); for (let i = 0; i <= n; i++) { const u = i / n; pts.push([a[0] + (b[0] - a[0]) * u + (R() - .5) * .3, a[1] + (b[1] - a[1]) * u + (R() - .5) * .3, h * (.8 + R() * .4), hsl]); } });
  const cardM = swayMat(new T.MeshLambertMaterial({ vertexColors: true, map: leafCardTex(), alphaTest: .5, side: T.DoubleSide }), .02), coreM = swayMat(new T.MeshLambertMaterial({ vertexColors: true, map: leafTex() }), .02);
  const m = new T.InstancedMesh(V.crown2, cardM, pts.length), core = new T.InstancedMesh(V.blobLo, coreM, pts.length);
  const m4 = new T.Matrix4(), q = new T.Quaternion(), e = new T.Euler(), c = new T.Color();
  pts.forEach(([x, z, h, hsl], i) => { q.setFromEuler(e.set(0, R() * 6, 0)); const r = h * (.75 + R() * .3); const sc = new T.Vector3(r * .62, h * .55, r * .62); m4.compose(new T.Vector3(x, h * .45, z), q, sc); m.setMatrixAt(i, m4);
    m4.compose(new T.Vector3(x, h * .42, z), q, sc.multiplyScalar(.82)); core.setMatrixAt(i, m4);
    c.setHSL(hsl[0] + (R() - .5) * .02, hsl[1], hsl[2] + (R() - .5) * .06); core.setColorAt(i, c); const l = c.getHSL({}); c.setHSL(l.h, Math.min(1, l.s * .5), Math.min(.95, .45 + l.l)); m.setColorAt(i, c); });
  m.instanceColor.needsUpdate = true; core.instanceColor.needsUpdate = true; const grp = new T.Group(); grp.name = 'shrubs';
  [m, core].forEach(x => { x.castShadow = true; x.receiveShadow = true; x.frustumCulled = false; grp.add(x); }); return grp;
}
function buildTrees(M, rd, blocks) {
  const diagPt = (y, off) => { const P0 = pm([xDiag(y), y]); return [P0[0] - rd.n[0] * off, P0[1] - rd.n[1] * off]; };
  const outPt = (s, off) => rd.at(s, off);
  const list = [[478, 1.6], [700, 1.6], [760, 1.6]].map(([y, o]) => diagPt(y, o)).concat(PM([[225, 235], [480, 238], [215, 215], [112, 540], [100, 880], [1100, 975], [330, 990], [520, 985], [130, 300], [80, 700], [240, 990]]));
  // (street trees across the road now live in the villa gardens, see makeStreet)
  const palms = PM([[930, 548], [1010, 700], [700, 560], [640, 520], [905, 505], [612, 230]]).concat([diagPt(560, 1.5), diagPt(840, 1.5)]);
  const t = makeTrees(T, list, palms);
  const sh = makeShrubs(T, [
    [diagPt(200, 1.2), diagPt(530, 1.2), 1.1, .9, [.27, .45, .27]], [diagPt(640, 1.2), diagPt(780, 1.2), 1.1, .9, [.27, .45, .27]],
    [pm([200, 182]), pm([630, 196]), 1.3, 1.1, [.26, .4, .25]], [pm([180, 190]), pm([60, 990]), 1.3, 1.1, [.26, .4, .25]], [pm([70, 990]), pm([1040, 990]), 1.4, 1.0, [.27, .42, .26]],
    [pm([900, 640]), pm([990, 735]), 1.0, .7, [.9, .62, .52]], [pm([620, 240]), pm([620, 480]), 1.2, .8, [.26, .45, .27]],
    [diagPt(205, .8), diagPt(300, .8), 2.2, .7, [.93, .65, .55]], [diagPt(650, .9), diagPt(700, .9), 1.6, .6, [.08, .7, .55]],
  ]);
  t.group.add(sh); return t;
}

// ------------------------------------------------------------------ pool: refracted tiled floor with animated caustics, sky reflection, coping, loungers, umbrellas
function buildPool(M) {
  const g = new T.Group(); g.name = 'pool'; const deck = PM(POOL_DECK_PX), water = PM(POOL_WATER_PX);
  g.add(mesh(flatGeo(deck, [offsetPoly(water, .34)]).translate(0, .06, 0), M.paverPale, { cast: false, name: 'poolDeck' }));
  g.add(mesh(prismGeo(offsetPoly(water, .34), .04, .14, [water]), M.sill, { name: 'poolCoping' }));
  g.add(mesh(prismGeo(offsetPoly(water, .01), -.5, .05, [offsetPoly(water, -.02)]), M.poolTile, { name: 'poolWall', cast: false }));
  const wmat = new T.ShaderMaterial({ uniforms: Object.assign({ t: { value: 0 }, uSky: { value: skyTexture() }, uSun: { value: SUN.dir } }, T.UniformsLib.fog), fog: true,
    vertexShader: `varying vec3 vW; \n#include <fog_pars_vertex>\n void main(){ vec4 w=modelMatrix*vec4(position,1.); vW=w.xyz; vec4 mvPosition=viewMatrix*w; gl_Position=projectionMatrix*mvPosition; \n#include <fog_vertex>\n }`,
    fragmentShader: `uniform float t; uniform sampler2D uSky; uniform vec3 uSun; varying vec3 vW;
      #include <fog_pars_fragment>
      ${EQ_GLSL}
      float hgt(vec2 p){ return .5*sin(p.x*2.1+t*1.3)+.45*sin(p.y*2.6-t*1.05)+.3*sin((p.x-p.y)*3.7+t*1.7)+.18*sin((p.x+p.y)*6.3-t*2.3)+.1*sin(p.x*9.1-p.y*7.7+t*2.9); }
      float caus(vec2 uv, float time){ vec2 p=mod(uv*6.28318,6.28318)-250.; vec2 i=p; float c=1.; float inten=.005;
        for(int n=0;n<4;n++){ float tt=time*(1.-(3.5/float(n+1))); i=p+vec2(cos(tt-i.x)+sin(tt+i.y), sin(tt-i.y)+cos(tt+i.x)); c+=1./length(vec2(p.x/(sin(i.x+tt)/inten), p.y/(cos(i.y+tt)/inten))); }
        c/=4.; c=1.17-pow(c,1.4); return pow(abs(c),8.); }
      void main(){ vec2 p=vW.xz; float e=.04, a=.035;
        vec3 N=normalize(vec3(-(hgt(p+vec2(e,0.))-hgt(p-vec2(e,0.)))*a/e*.5, 1., -(hgt(p+vec2(0.,e))-hgt(p-vec2(0.,e)))*a/e*.5));
        vec3 V=normalize(vW-cameraPosition); vec3 R=reflect(V,N); R.y=abs(R.y);
        vec3 sky=texture2D(uSky,eqUv(R)).rgb; float F=.02+.98*pow(1.-clamp(dot(-V,N),0.,1.),5.);
        vec3 rd=refract(V,N,.752); float tb=(-1.35-vW.y)/min(rd.y,-.05); vec3 fp=vW+rd*tb;
        vec2 tg=abs(fract(fp.xz/.25)-.5); float grid=smoothstep(.44,.49,max(tg.x,tg.y));
        vec3 fc=mix(vec3(.42,.70,.78),vec3(.80,.90,.92),grid*.5);
        float cs=caus(fp.xz*.33, t*.6); fc+=vec3(1.,1.,.95)*cs*.45;
        float L=tb; vec3 col=fc*exp(-L*vec3(.7,.2,.14)); col=mix(col,vec3(.02,.26,.36)*.85,1.-exp(-L*.3));
        col=col*.95+vec3(.0,.03,.04);
        col=mix(col,sky*.75,F*.7)+vec3(1.,.9,.75)*pow(max(dot(R,uSun),0.),300.)*4.;
        gl_FragColor=vec4(col,1.);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
        #include <fog_fragment>
      }` });
  const wm = new T.Mesh(flatGeo(offsetPoly(water, -.01)), wmat); wm.position.y = -.07; wm.name = 'poolWater'; wm.receiveShadow = false; g.add(wm);
  g.add(seg(deck[0], deck[1], .9, .3, M.concrete)); g.add(seg(deck[1], pm([600, 505]), .9, .3, M.concrete));
  // loungers (aluminium frame, ivory cushions), side tables, canvas umbrellas
  const lg = new T.Group(); lg.name = 'loungers'; g.add(lg);
  const cush = new T.MeshStandardMaterial({ color: '#EFEAE0', roughness: .85 }), frameM = new T.MeshStandardMaterial({ color: '#3a3b3e', roughness: .4, metalness: .6 }), wood = new T.MeshStandardMaterial({ color: '#8a6446', roughness: .7 }), canvas = new T.MeshStandardMaterial({ color: '#F1EADB', roughness: .9, side: T.DoubleSide });
  const lounger = (x, z, ang) => { const l = new T.Group(); l.position.set(x, .06, z); l.rotation.y = ang;
    l.add(box(.66, .05, 1.35, frameM, 0, .3, .28), box(.62, .09, 1.3, cush, 0, .37, .28));
    const back = new T.Group(); back.position.set(0, .34, -.4); back.rotation.x = -.62; back.add(box(.66, .05, .8, frameM, 0, 0, -.4), box(.62, .09, .78, cush, 0, .07, -.4)); l.add(back);
    for (const sx of [-.3, .3]) for (const sz of [-.35, .9]) l.add(box(.04, .3, .04, frameM, sx, .15, sz)); lg.add(l); return l; };
  const umb = (x, z) => { const u = new T.Group(); u.position.set(x, .06, z); const pole = mesh(new T.CylinderGeometry(.03, .03, 2.5, 8), wood); pole.position.y = 1.25;
    const top = mesh(new T.ConeGeometry(1.45, .5, 8, 1, true), canvas); top.position.y = 2.45; const fin = mesh(new T.CylinderGeometry(.06, .06, .2, 6), wood); fin.position.y = 2.75;
    const bs = mesh(new T.CylinderGeometry(.28, .3, .1, 16), frameM); bs.position.y = .05; u.add(pole, top, fin, bs); lg.add(u); return u; };
  const lp = [[702, 497], [729, 497], [776, 497], [803, 497], [850, 497]]; lp.forEach(([x, y]) => { const p = pm([x, y]); lounger(p[0], p[1], Math.PI); });
  const tb = (x, y) => { const p = pm([x, y]); const t = new T.Group(); t.position.set(p[0], .06, p[1]); t.add(box(.42, .04, .42, wood, 0, .42, 0), box(.04, .42, .04, frameM, 0, .21, 0)); lg.add(t); };
  tb(715, 495); tb(790, 495); umb(...pm([715, 503])); umb(...pm([790, 503])); umb(...pm([865, 503]));
  // a couple of loungers on the north-east deck strip facing the water
  { const A = water[3], B = water[0], d = [B[0] - A[0], B[1] - A[1]], L = Math.hypot(...d), u = [d[0] / L, d[1] / L], n = [-u[1], u[0]];
    const nn = (n[0] * (25 - A[0]) + n[1] * (-15 - A[1])) > 0 ? n : [-n[0], -n[1]];
    [.3, .45, .6].forEach(f => { const x = A[0] + d[0] * f + nn[0] * 1.75, z = A[1] + d[1] * f + nn[1] * 1.75; lounger(x, z, Math.atan2(-nn[0], -nn[1])); }); }
  return { group: g, water: wm, setTime: (t) => { wmat.uniforms.t.value = t; }, update: (t) => { wmat.uniforms.t.value = t; }, loungers: lp.map(q => pm(q)) };
}

// ------------------------------------------------------------------ distant context: green Naguru hills, red-roofed villas, tree canopy, a neighbouring mid-rise
export function makeContext(THREE, o = {}) {
  T = THREE; buildTextures(); const grp = new T.Group(); grp.name = 'context'; const rd = roadGeometry(), R = rnd(o.seed || 101);
  const plot = PM(PLOT_PX); const C0 = [8, 0];
  const roadOff = (x, z) => (x - rd.A[0]) * rd.n[0] + (z - rd.A[1]) * rd.n[1];
  const hAt = (x, z) => { const r = Math.hypot(x - C0[0], z - C0[1]), ro = Math.abs(roadOff(x, z) - 12); const k = smooth(95, 420, r) * smooth(26, 90, ro);
    return k * (22 * fbm(x / 260 + 3, z / 260, 5, 3) - 8 + 150 * smooth(500, 2000, r) * (fbm(x / 900 + 9, z / 900, 9, 4) - .25)) - .09; };
  const N = 128, S = 5200,
 tg = new T.PlaneGeometry(S, S, N, N); tg.rotateX(-Math.PI / 2); const p = tg.attributes.position, col = [];
  for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i), h = hAt(x, z); p.setY(i, h); const n = fbm(x / 120, z / 120, 21, 3), m = fbm(x / 30, z / 30, 23, 2), r = Math.hypot(x, z);
    let c = mixc([44, 66, 34], [78, 96, 50], n); c = mixc(c, [34, 52, 30], smooth(.5, .8, m) * .6);
 if (r > 260) c = mixc(c, [128, 86, 64], smooth(.62, .8, fbm(x / 22, z / 22, 29, 2)) * .45 * smooth(260, 700, r));
    col.push(...c.map(v => Math.pow(v / 255, 2.2))); }
  tg.setAttribute('color', new T.Float32BufferAttribute(col, 3)); tg.computeVertexNormals();
  // canopy detail: mottled dark-green tree cover with lighter crowns and dark gaps (reads as dense Naguru canopy at distance)
  const canT = canvasTex(512, 512, (cg, w, h) => pixFill(cg, w, h, (x, y) => { const n = fbm(x / 14, y / 14, 31, 4, 37), m = fbm(x / 4, y / 4, 33, 2, 128), k = .55 + n * .7 + m * .25 - (n < .38 ? .3 : 0); return [255 * Math.min(1, k * .95), 255 * Math.min(1, k), 255 * Math.min(1, k * .9)]; }), { rep: [1 / 45, 1 / 45], srgb: false });
  const terr = new T.Mesh(tg, new T.MeshLambertMaterial({ vertexColors: true, map: canT })); terr.receiveShadow = true; terr.name = 'terrain'; grp.add(terr);
  // villas: plastered walls, hipped terracotta/red-iron roofs, scattered over the hills, plus compound walls nearby
  const ok = (x, z, m) => !inPoly([x, z], offsetPoly(plot, m)) && (roadOff(x, z) < -6 || roadOff(x, z) > 58) && Math.hypot(x + 150, z + 175) > 22;
  const vill = []; for (let i = 0; i < 6000 && vill.length < 2200; i++) { const r = 42 + Math.pow(R(), 2.0) * 1800, a = R() * 6.283, x = C0[0] + Math.cos(a) * r, z = C0[1] + Math.sin(a) * r; if (!ok(x, z, 14)) continue; if (Math.hypot(x + 46, z - 48) < 26) continue; vill.push([x, z, r]); }
  const body = new T.InstancedMesh(new T.BoxGeometry(1, 1, 1).translate(0, .5, 0), new T.MeshLambertMaterial(), vill.length * 2);
  const roofG = hipRoofGeo(1.4, 1, 1); const roof = new T.InstancedMesh(roofG, new T.MeshLambertMaterial({ map: TEX.clay }), vill.length * 2);
  const m4 = new T.Matrix4(), q = new T.Quaternion(), e = new T.Euler(), v = new T.Vector3(), s = new T.Vector3(), c = new T.Color(); let bi = 0;
  const WALLS = ['#EDE6D6', '#F2EFE8', '#E8D9BF', '#F0E2CC', '#DCD5C8', '#F5F1E8', '#E6C9A8'], ROOFS = ['#8E3B26', '#A5482C', '#7A3020', '#6E2E22', '#9B5A3A', '#5A4A44', '#B0563A'];
  vill.forEach(([x, z, r]) => { const w = 7 + R() * 14, d = 6 + R() * 9, hgt = R() < .35 ? 6.2 + (R() < .3 ? 3.2 : 0) : 3.4, ya = R() * 1.57 + Math.atan2(rd.u[0], rd.u[1]), y = hAt(x, z);
    const parts = R() < .4 ? 2 : 1, modern = R() < .3;
    for (let k = 0; k < parts; k++) { const ox = k ? (R() - .5) * w * .8 : 0, oz = k ? d * .55 : 0, ww = k ? w * .55 : w, dd = k ? d * .7 : d, hh = k ? 3.4 : hgt; const cs = Math.cos(ya), sn = Math.sin(ya);
      const px = x + ox * cs + oz * sn, pz = z - ox * sn + oz * cs; q.setFromEuler(e.set(0, ya, 0));
      m4.compose(v.set(px, y - .5, pz), q, s.set(ww, hh + .5, dd)); body.setMatrixAt(bi, m4); body.setColorAt(bi, c.set(WALLS[(R() * WALLS.length) | 0]));
      if (modern) { m4.makeScale(0, 0, 0); body.setColorAt(bi, c.set('#F2F0EC')); } else m4.compose(v.set(px, y + hh, pz), q, s.set(ww * 1.12 / 1.4, 1.8 + R() * 1.4, dd * 1.12)); roof.setMatrixAt(bi, m4); roof.setColorAt(bi, c.setHSL(.03 + R() * .03, .25 + R() * .3, .72 + R() * .22)); bi++; } });
  body.count = roof.count = bi; [body, roof].forEach(m => { m.instanceColor.needsUpdate = true; m.castShadow = true; m.receiveShadow = true; m.frustumCulled = false; grp.add(m); });
  // tree canopy (lumpy blobs, no trunks far away) - denser in valleys, around villas
  const V = vegGeos(); const trees = []; for (let i = 0; i < 12000 && trees.length < 3000; i++) { const r = 40 + Math.pow(R(), 1.6) * 1600
, a = R() * 6.283, x = C0[0] + Math.cos(a) * r, z = C0[1] + Math.sin(a) * r; if (!ok(x, z, 6)) continue; if (fbm(x / 90, z / 90, 61, 2) < .42) continue; trees.push([x, z, r]); }
  const near = trees.filter(t => t[2] < 230), far = trees.filter(t => t[2] >= 230), close = [];
  

  const farG = new T.IcosahedronGeometry(1, 0); { const p = farG.attributes.position, cc = [], nn = []; for (let i = 0; i < p.count; i++) { const y = p.getY(i), k = .85 + .3 * fbm(p.getX(i) * 2 + 1, p.getZ(i) * 2 + y, 3, 2); p.setXYZ(i, p.getX(i) * k, y * k, p.getZ(i) * k); const a = .55 + .45 * (y + 1) / 2; cc.push(a, a, a); const v = new T.Vector3(p.getX(i), p.getY(i) * 1.2, p.getZ(i)).normalize(); nn.push(v.x, v.y, v.z); } farG.setAttribute('color', new T.Float32BufferAttribute(cc, 3)); farG.setAttribute('normal', new T.Float32BufferAttribute(nn, 3)); }
  const crown = new T.InstancedMesh(V.blob, new T.MeshLambertMaterial({ vertexColors: true, map: leafTex() }), near.length);
  const crownF = new T.InstancedMesh(farG, new T.MeshLambertMaterial({ vertexColors: true, map: leafTex() }), far.length);
  const trunk = new T.InstancedMesh(V.trunk, new T.MeshStandardMaterial({ color: '#5a4a3a', roughness: 1 }), near.length);
  near.forEach(([x, z, r], i) => { const rr = 2.2 + R() * 3.0, y = hAt(x, z), h = 2.5 + R() * 3; q.setFromEuler(e.set(R(), R() * 6, R()));
    m4.compose(v.set(x, y + h + rr * .55, z), q, s.set(rr, rr * .8, rr)); crown.setMatrixAt(i, m4); crown.setColorAt(i, c.setHSL(.21 + R() * .09, .18 + R() * .18, .11 + R() * .1));
    m4.compose(v.set(x, y, z), q.identity(), s.set(1.4, h + rr * .4, 1.4)); trunk.setMatrixAt(i, m4); });
  far.forEach(([x, z, r], i) => { const rr = 2.4 + R() * 3.2, y = hAt(x, z); q.setFromEuler(e.set(R(), R() * 6, R()));
    m4.compose(v.set(x, y + 2.5 + rr * .7, z), q, s.set(rr, rr * .75, rr)); crownF.setMatrixAt(i, m4); crownF.setColorAt(i, c.setHSL(.21 + R() * .09, .16 + R() * .16, .09 + R() * .08)); });
  crown.instanceColor.needsUpdate = true; crownF.instanceColor.needsUpdate = true;
  [crown, trunk].forEach(m => { m.castShadow = false; m.receiveShadow = true; }); crownF.receiveShadow = false; crownF.castShadow = false;
  body.castShadow = roof.castShadow = false;
  [body, roof, crown, trunk, crownF].forEach(m => { grp.remove(m); grp.add(splitInstanced(m, 220)); });

  // neighbouring mid-rise tower to the south-west (9 floors), plain plaster + window grid
  const twT = canvasTex(256, 512, (g, w, h) => { g.fillStyle = '#D9D3C6'; g.fillRect(0, 0, w, h); for (let fy = 0; fy < 9; fy++) for (let wx = 0; wx < 6; wx++) { g.fillStyle = hash2(fy, wx, 3) > .2 ? '#2b3540' : '#56606a'; g.fillRect(8 + wx * 41, 14 + fy * 56, 26, 30); } g.fillStyle = 'rgba(0,0,0,.12)'; for (let fy = 0; fy < 9; fy++) g.fillRect(0, 50 + fy * 56, w, 4); });
  twT.wrapS = twT.wrapT = T.ClampToEdgeWrapping; const tw = new T.Mesh(new T.BoxGeometry(22, 31, 17), [0, 1, 2, 3, 4, 5].map(i => i === 2 || i === 3 ? new T.MeshStandardMaterial({ color: '#CFC9BC' }) : new T.MeshStandardMaterial({ map: twT, roughness: .85 })));
  tw.position.set(-48, 15.5 + hAt(-48, 52), 52); tw.rotation.y = .12; tw.castShadow = true; tw.receiveShadow = true; tw.name = 'neighbourTower'; grp.add(tw);
  // tower under construction wrapped in green netting (as filmed), with a red tower crane
  { const netT = canvasTex(128, 128, (g, w, h) => { pixFill(g, w, h, (x, y) => mulc([46, 128, 92], .85 + fbm(x / 20, y / 20, 5, 3, 6) * .25 + ((x % 8) < 1 || (y % 8) < 1 ? .1 : 0))); g.fillStyle = 'rgba(40,40,40,.35)'; for (let y = 0; y < h; y += 32) g.fillRect(0, y, w, 3); }, { rep: [1 / 6, 1 / 6.6] });
    const tx = -150, tz = -175, ty = hAt(tx, tz); const net = new T.Mesh(worldUV(new T.BoxGeometry(24, 46, 20), tx, ty + 23, tz), new T.MeshLambertMaterial({ map: netT })); net.position.set(tx, ty + 23, tz); net.castShadow = true; grp.add(net);
    const frame = new T.Mesh(new T.BoxGeometry(23.5, 8, 19.5), new T.MeshLambertMaterial({ color: '#9b9a95' })); frame.position.set(tx, ty + 50, tz); grp.add(frame);
  }
  // distant Kampala skyline on the ridges (west / south-west), hazed by the fog
  { const sk = new T.InstancedMesh(new T.BoxGeometry(1, 1, 1).translate(0, .5, 0), new T.MeshLambertMaterial(), 70); let k = 0;
    for (let i = 0; i < 70; i++) { const a = 2.35 + R() * 1.25, r = 2100 + R() * 1300, x = Math.cos(a) * r, z = Math.sin(a) * r * .9, y = hAt(x, z); const h = 25 + Math.pow(R(), 2) * 60;
      m4.compose(v.set(x, y - 2, z), q.setFromEuler(e.set(0, R() * 3, 0)), s.set(18 + R() * 25, h, 14 + R() * 18)); sk.setMatrixAt(k, m4); sk.setColorAt(k++, c.set(R() < .7 ? '#e9e6df' : '#9fb0b8')); }
    sk.instanceColor.needsUpdate = true; sk.frustumCulled = false; grp.add(sk); }

  return { group: grp, hAt };
}

// ------------------------------------------------------------------ people preset for the film (outside); interiors add their own
export function filmPeople(pool) {
  const P = defaultPaths(), L = [];
  const add = (k, n, o = {}) => { for (let i = 0; i < n; i++) L.push({ path: P[k], closed: k === 'poolDeck', ...o, seed: L.length * 13 + 5 }); };
  add('pavement', 3); add('pavement2', 3); add('pavement3', 2); add('pavement4', 2); add('gateToNorth', 2); add('gateToCourt', 3);
  add('lawn', 1, { v: .9 });
  const lp = pool.loungers; // [x,z] lounger centres (south row, heads south)
  [0, 1, 3].forEach((j, i) => L.push({ pos: [lp[j][0], lp[j][1] + .2], ang: Math.PI, pose: 'recline', seat: .5, seed: 300 + i }));
  L.push({ pos: [16.8, -6.92], ang: Math.PI, pose: 'sit', seat: .24, dangle: 1, seed: 401 }, { pos: [17.7, -6.92], ang: Math.PI, pose: 'sit', seat: .24, dangle: 1, seed: 402, female: true, dress: false });
  L.push({ pos: [22.8, -5.6], ang: -2.4, pose: 'stand', seed: 601 }, { pos: [23.5, -6.1], ang: -.7, pose: 'stand', seed: 602, female: true });
  const g = pm(GUARD_PX.c); L.push({ pos: [g[0] + 2.5, g[1] - 2.2], ang: 2.3, pose: 'stand', seed: 701, shirt: '#2B3A55', armsCrossed: 1 });
  return L;
}

// ------------------------------------------------------------------ main
export function buildVanta(THREE, opts = {}) {
  T = THREE; const o = Object.assign({ people: 14, cars: true, sign: 'Vanta House', mood: 'day', context: true }, opts);
  buildTextures(); skyTexture();
  const M = makeMaterials(); const group = new T.Group(); group.name = 'VantaHouse';
  const north = { polygon: PM(NORTH_PX) }, south = { polygon: PM(SOUTH_PX) };
  south.notchPolygon = south.polygon.filter(p => !(Math.abs(p[0] - 16.78) < .05)).map(p => p); // drop the two corner vertices
  { const i = south.notchPolygon.findIndex(p => Math.abs(p[0] - XA) < .05 && Math.abs(p[1] - 1.91) < .05); south.notchPolygon.splice(i + 1, 0, [XA, ZS]); }
  [north, south].forEach(b => { b.center = centroid(b.polygon); b.bbox = bbox(b.polygon); b.area = Math.abs(area2(b.polygon)); });
  const blocks = { north, south };
  const floors = []; const mkFloor = (name, key, level, yBase, height) => { const g = new T.Group(); g.name = 'floor_' + key; group.add(g); const f = { name, key, level, yBase, height, group: g, index: floors.length }; floors.push(f); return f; };
  mkFloor('Basement', 'B1', -3.3, -3.3, 3.3); mkFloor('Ground', 'G', 0, 0, 4.0);
  for (let k = 1; k <= 11; k++) mkFloor('Level ' + k, String(k), levelOf(k), levelOf(k), 3.3);
  mkFloor('Roof', 'roof', LEVELS.roof, LEVELS.roof, 4.1);
  const bp = buildBasement(M, blocks, floors[0].group);
  const clearRects = o.clearRects || [[APT.lobby.x0 - .2, APT.lobby.x1, APT.lobby.z0, APT.lobby.z1], [-3.2, 6.6, 5.3, 8.1]];
  buildGround(M, blocks, floors[1].group, { clearRects });
  buildFloorGroups(M, blocks, floors, o);
  buildRoof(M, blocks, floors[13].group, o.sign);
  const site = buildSite(M, blocks, o); site.setMood(o.mood); group.add(site.group);
  const ctx = o.context ? makeContext(T) : null; if (ctx) { group.add(ctx.group); ctx.street = makeStreet(T, { sGate: site.sGate }); group.add(ctx.street.group); }
  const pspec = o.people === 'film' ? filmPeople(site.pool) : o.people;
  const people = makePeople(T, pspec, defaultPaths()); site.group.add(people.group);
  const rdg = roadGeometry(), suv = rdg.at(site.sGate + 34, 13.6);
  const cars = o.cars ? makeCars(T, { extraSpots: [{ x: suv[0], z: suv[1], ang: Math.atan2(-rdg.u[0], -rdg.u[1]), c: '#2B2D31' }] }) : null; if (cars) site.group.add(cars.group);

  const bb = bbox([...north.polygon, ...south.polygon]);
  const dims = { roofLevel: LEVELS.roof, parapetTop: LEVELS.roof + 1.2, signTop: LEVELS.roof + 4.2, totalHeight: LEVELS.roof + 4.2, basementLevel: -3.3, floorHeight: 3.3, groundHeight: 4.0, levels: floors.map(f => ({ name: f.name, level: f.level })),
    buildingBBox: { min: bb.min, max: bb.max }, buildingCenter: [(bb.min[0] + bb.max[0]) / 2, (bb.min[1] + bb.max[1]) / 2], plotArea: Math.abs(area2(site.polygon)), plotEdges: { bottom: 71.4, left: 45.9, top: 24.6, road: 59.3 }, px2m: SC, basementPolygon: bp,
    gate: pm(GATE_PX), mapPx: (x, y) => pm([x, y]), road: roadGeometry(), sGate: site.sGate };
  const update = (t) => { site.pool.update(t); people.update(t); cars?.update(t); SWAY.uTime.value = t; };
  cullable(group);
  return { group, floors, blocks, site: { ...site, people, cars }, context: ctx, dims, materials: M, update, setMood: (mood) => site.setMood(mood) };

}
export function explodeFloors(floors, amount, opts = {}) { floors.forEach((f, i) => { f.group.position.y = (opts.fromGround ? Math.max(0, i - 1) : i) * amount * (opts.k ?? 1); }); }
export function setFloorsVisible(floors, pred) { floors.forEach((f, i) => { f.group.visible = !!pred(f, i); }); }
export const lightingAlias = lighting;
export { lighting as makeLighting, roadGeometry, pm as mapPx };

// ------------------------------------------------------------------ hipped roof (w >= d), apex height h, centred, base at y=0
export function hipRoofGeo(w, d, h) { if (d > w) { const g = hipRoofGeo(d, w, h); g.rotateY(Math.PI / 2); return g; }
  const a = w / 2, b = d / 2, r = (w - d) / 2; const P = { A: [-a, 0, -b], B: [a, 0, -b], C: [a, 0, b], D: [-a, 0, b], E: [-r, h, 0], F: [r, h, 0] };
  const tri = []; const add = (...k) => k.forEach(n => tri.push(...P[n]));
  add('A', 'E', 'F', 'A', 'F', 'B', 'C', 'F', 'E', 'C', 'E', 'D', 'B', 'F', 'C', 'D', 'E', 'A');
  const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(tri, 3)); g.computeVertexNormals();
  const uv = []; for (let i = 0; i < tri.length; i += 3) uv.push(tri[i] + tri[i + 2] * .3, tri[i + 1] * 1.6 + tri[i + 2]); g.setAttribute('uv', new T.Float32BufferAttribute(uv, 2)); return g; }
let VILLA_T; function villaFacadeTex() { if (VILLA_T) return VILLA_T; VILLA_T = canvasTex(256, 256, (g, w, h) => { pixFill(g, w, h, (x, y) => mulc([236, 222, 188], .9 + fbm(x / 30, y / 30, 3, 3, 8) * .15));
    for (const [y0, y1] of [[40, 120], [170, 245]]) { g.fillStyle = '#F4F0E6'; g.fillRect(70, y0 - 8, 116, y1 - y0 + 16); g.fillStyle = '#2a3036'; g.fillRect(78, y0, 100, y1 - y0); g.fillStyle = '#F4F0E6'; g.fillRect(126, y0, 4, y1 - y0); g.fillRect(78, y0 + 30, 100, 3); } }, { rep: [1 / 4, 1 / 3.2] }); return VILLA_T; }
// the street as filmed: walled villa plots across the road (ochre/stone-clad walls, arched gates, cream houses, red clay hipped roofs,
// palms, mango/umbrella trees, cypress spires, flowering hedges), leaning timber utility poles with cables, triangular road sign.
export function makeStreet(THREE, o = {}) {
  T = THREE; buildTextures(); const g = new T.Group(); g.name = 'street'; const rd = roadGeometry(), R = rnd(o.seed || 222);
  const ochre = new T.MeshLambertMaterial({ map: TEX.ochre }), stone = new T.MeshLambertMaterial({ map: TEX.rubble }), cream = new T.MeshLambertMaterial({ map: villaFacadeTex() }), clay = new T.MeshLambertMaterial({ map: TEX.clay }), dark = new T.MeshLambertMaterial({ color: '#1d1e20' }), white = new T.MeshLambertMaterial({ color: '#EEEAE2' });
  const ang = Math.atan2(rd.u[0], rd.u[1]);
  const place = (m, s, off, y = 0) => { const p = rd.at(s, off); m.position.set(p[0], y, p[1]); m.rotation.y = ang; return m; };
  const wb = (grp, m, s0, s1, o0, o1, y0, y1) => { const w = o1 - o0, l = s1 - s0, hh = y1 - y0; const geo = worldUV(new T.BoxGeometry(w, hh, l), (o0 + o1) / 2, (y0 + y1) / 2, (s0 + s1) / 2); const b = mesh(geo, m); b.position.set((o0 + o1) / 2, (y0 + y1) / 2, (s0 + s1) / 2); grp.add(b); return b; };
  // villa plots: local frame x = offset from road edge (n), z = along road (u)
  const trees = [], palms = []; const shrubLines = [];
  const local = (s, off) => rd.at(s, off);
  for (let s0 = -150; s0 < 250; ) {
    const W = 26 + R() * 14, plot = new T.Group(); plot.position.set(rd.A[0], 0, rd.A[1]); plot.rotation.y = Math.atan2(rd.n[0], rd.n[1]) - Math.PI / 2 * 0; g.add(plot);
    // build in a road-aligned frame: X axis = n, Z axis = u
    plot.matrixAutoUpdate = false; plot.matrix.makeBasis(new T.Vector3(rd.n[0], 0, rd.n[1]), new T.Vector3(0, 1, 0), new T.Vector3(rd.u[0], 0, rd.u[1])).setPosition(rd.A[0], 0, rd.A[1]);
    const gs = s0 + W * .5 + (R() - .5) * 6, gw = 4.2;
    wb(plot, stone, s0, gs - gw / 2 - .5, 17.6, 17.9, 0, 1.1); wb(plot, ochre, s0, gs - gw / 2 - .5, 17.6, 17.9, 1.1, 2.3); wb(plot, stone, gs + gw / 2 + .5, s0 + W, 17.6, 17.9, 0, 1.1); wb(plot, ochre, gs + gw / 2 + .5, s0 + W, 17.6, 17.9, 1.1, 2.3);
    wb(plot, white, s0, gs - gw / 2 - .5, 17.55, 17.95, 2.3, 2.38); wb(plot, white, gs + gw / 2 + .5, s0 + W, 17.55, 17.95, 2.3, 2.38);
    for (let s = s0 + .8; s < s0 + W - .5; s += 1.6) { if (Math.abs(s - gs) < gw / 2 + .7) continue; wb(plot, white, s - .09, s + .09, 17.66, 17.84, 2.38, 2.75); wb(plot, dark, s - .095, s + .095, 17.655, 17.845, 2.62, 2.7); }
    for (const sd of [-1, 1]) { wb(plot, ochre, gs + sd * (gw / 2 + .25) - .3, gs + sd * (gw / 2 + .25) + .3, 17.45, 18.05, 0, 3.1); wb(plot, white, gs + sd * (gw / 2 + .25) - .35, gs + sd * (gw / 2 + .25) + .35, 17.4, 18.1, 3.1, 3.2); }
    { const ar = new T.Mesh(new T.TorusGeometry(gw / 2 + .25, .28, 6, 16, Math.PI), ochre); ar.rotation.y = Math.PI / 2; ar.position.set(17.75, 3.0, gs); ar.scale.set(1, .55, 1); ar.castShadow = true; plot.add(ar); }
    wb(plot, dark, gs - gw / 2, gs + gw / 2, 17.72, 17.78, .05, 2.4);
    wb(plot, ochre, s0, s0 + .25, 17.6, 50, 0, 2.3);
    // house
    const hw = 13 + R() * 8, hd = 10 + R() * 4, st = R() < .8 ? 2 : 1, hh = st * 3.3 + .4, hs = s0 + W * (.35 + R() * .3), ho = 27 + R() * 6;
    wb(plot, cream, hs - hw / 2, hs + hw / 2, ho, ho + hd, 0, hh);
    const roof = new T.Mesh(hipRoofGeo(hd + 1.4, hw + 1.4, 2.4 + R() * 1.2), clay); roof.position.set(ho + hd / 2, hh, hs); roof.castShadow = true; roof.receiveShadow = true; plot.add(roof);
    if (R() < .6) { const w2 = hw * .45; wb(plot, cream, hs + hw / 2 - w2, hs + hw / 2, ho - 3.2, ho, 0, 3.4); const r2 = new T.Mesh(hipRoofGeo(4.2, w2 + 1, 1.6), clay); r2.position.set(ho - 1.6, 3.4, hs + hw / 2 - w2 / 2); r2.castShadow = true; plot.add(r2); }
    // garden: palms, broad trees, cypress, flowering hedge behind the wall
    const P = (s, off) => local(s, off);
    for (let k = 0; k < 3; k++) palms.push([...P(s0 + 2 + R() * (W - 4), 19.5 + R() * 6), 9 + R() * 6]);
    for (let k = 0; k < 2; k++) trees.push([...P(s0 + 3 + R() * (W - 6), 23 + R() * 17), 4 + R() * 4, 3.0 + R() * 1.8]);
    if (R() < .6) for (let k = 0; k < 2; k++) trees.push([...P(s0 + 2 + R() * (W - 4), 19.2 + R() * 3), 1.5, -1]);
    shrubLines.push([P(s0 + .5, 18.5), P(s0 + W - .5, 18.5), 1.2, 1.6, R() < .5 ? [.03, .7, .5] : [.27, .45, .28]]);
    s0 += W;
  }
  // cypress spires: tall narrow crowns
  const spires = trees.filter(t => t[3] < 0); const broad = trees.filter(t => t[3] >= 0);
  const tg = makeTrees(T, broad, palms, { seed: 77 }); g.add(tg.group);
  if (spires.length) { const V = vegGeos(); const sp = new T.InstancedMesh(V.crown, swayMat(new T.MeshLambertMaterial({ vertexColors: true, map: leafCardTex(), alphaTest: .5, side: T.DoubleSide }), .04), spires.length); const m4 = new T.Matrix4(), c = new T.Color();
    spires.forEach(([x, z], i) => { const h = 7 + R() * 5; m4.compose(new T.Vector3(x, h / 2 + .5, z), new T.Quaternion(), new T.Vector3(1.1, h / 2, 1.1)); sp.setMatrixAt(i, m4); sp.setColorAt(i, c.setHSL(.25, .25, .42)); }); sp.castShadow = true; sp.receiveShadow = true; g.add(sp); }
  g.add(makeShrubs(T, shrubLines, { seed: 9 }));
  // utility poles (leaning timber) + cables
  const poleM = new T.MeshLambertMaterial({ color: '#8a7a64', map: TEX.bark }); const tops = [];
  for (let s = -190; s < 300; s += 30 + R() * 8) { const off = 4.4 + R() * .5, p = rd.at(s, off), lean = (R() - .5) * .08, lean2 = (R() - .5) * .06, h = 9 + R() * 1.5;
    const pole = new T.Group(); pole.position.set(p[0], 0, p[1]); pole.rotation.set(lean, ang, lean2); g.add(pole);
    const c = mesh(new T.CylinderGeometry(.11, .15, h, 7), poleM); c.position.y = h / 2; pole.add(c); const arm = mesh(new T.BoxGeometry(1.8, .1, .1), poleM); arm.position.set(0, h - .4, 0); arm.rotation.y = Math.PI / 2; pole.add(arm);
    pole.updateMatrixWorld(true); const t = []; for (const a of [-.8, -.25, .3, .8]) t.push(new T.Vector3(0, h - .32, a).applyMatrix4(pole.matrixWorld)); tops.push(t); }
  const cv = []; for (let i = 0; i + 1 < tops.length; i++) for (let k = 0; k < 4; k++) { const a = tops[i][k], b = tops[i + 1][k]; let prev = a; for (let j = 1; j <= 8; j++) { const u = j / 8, p = new T.Vector3().lerpVectors(a, b, u); p.y -= Math.sin(u * Math.PI) * (.55 + k * .1); cv.push(prev.x, prev.y, prev.z, p.x, p.y, p.z); prev = p; } }
  const cg = new T.BufferGeometry(); cg.setAttribute('position', new T.Float32BufferAttribute(cv, 3)); const cables = new T.LineSegments(cg, new T.LineBasicMaterial({ color: '#2a2a2a' })); cables.name = 'cables'; g.add(cables);
  // triangular warning sign near the gate
  { const p = rd.at((o.sGate || 28) + 14, 5.0), sg = new T.Group(); sg.position.set(p[0], 0, p[1]); sg.rotation.y = ang + Math.PI; g.add(sg); const post = mesh(new T.CylinderGeometry(.03, .03, 2.6, 6), new T.MeshLambertMaterial({ color: '#9a9ca0' })); post.position.y = 1.3; sg.add(post);
    const tc = canvasTex(128, 128, (c) => { c.fillStyle = '#c0222a'; c.beginPath(); c.moveTo(64, 6); c.lineTo(122, 116); c.lineTo(6, 116); c.closePath(); c.fill(); c.fillStyle = '#fafafa'; c.beginPath(); c.moveTo(64, 30); c.lineTo(102, 104); c.lineTo(26, 104); c.closePath(); c.fill(); c.fillStyle = '#111'; c.fillRect(60, 56, 8, 30); c.fillRect(60, 90, 8, 8); });
    const pl = new T.Mesh(new T.PlaneGeometry(.8, .8), new T.MeshLambertMaterial({ map: tc, transparent: true, alphaTest: .5, side: T.DoubleSide })); pl.position.y = 2.7; sg.add(pl); }
  return { group: g };
}

// indoor / potted plant: 9-14 arching leaves (palm-frond cards) from the pot top - reads as kentia/dracaena, never a ball
export function pottedPlant(THREE, x, y, z, h, o = {}) { T = THREE; buildTextures(); const V = vegGeos(), R = rnd(o.seed || 5), n = o.n || 12;
  const m = new T.InstancedMesh(V.frond, o.material || new T.MeshLambertMaterial({ map: TEX.frond, alphaTest: .5, side: T.DoubleSide, color: o.color || '#a9be8c' }), n); const m4 = new T.Matrix4(), q = new T.Quaternion(), e = new T.Euler(), s = h / 2.6;
  for (let i = 0; i < n; i++) { const a = i * 2.399 + R() * .4, pitch = -1.05 + R() * .75 + (i / n) * .4, sc = s * (.7 + R() * .45); q.setFromEuler(e.set(pitch, a, (R() - .5) * .4, 'YXZ')); m4.compose(new T.Vector3(x, y, z), q, new T.Vector3(sc * .8, sc, sc)); m.setMatrixAt(i, m4); }
  m.castShadow = true; m.receiveShadow = true; return m; }

// ------------------------------------------------------------------ unit facade openings (used by r_units.js for the furnished units)
// face: {axis:'x'|'z', at: plane coordinate of the exterior face, out: +1|-1 (outward direction along the axis)}; op: {a,b (along the face), y0,y1 (from level), kind, balc:[a,b,depth]}
export function unitOpening(THREE, grp, M, level, face, op) { T = THREE; const g = new T.Group(); grp.add(g);
  const w = op.b - op.a, h = op.y1 - op.y0, yc = level + (op.y0 + op.y1) / 2, mid = (op.a + op.b) / 2;
  const put = (m, along, off, y, sx, sy, sz) => { m.scale.set(sx, sy, sz); if (face.axis === 'x') { m.position.set(face.at + off * face.out, y, along); m.rotation.y = face.out > 0 ? Math.PI / 2 : -Math.PI / 2; } else { m.position.set(along, y, face.at + off * face.out); m.rotation.y = face.out > 0 ? 0 : Math.PI; } g.add(m); return m; };
  const BX = new T.BoxGeometry(1, 1, 1); const bx = (mat, along, off, y, sx, sy, sz, cast = true) => { const m = new T.Mesh(BX, mat); m.castShadow = cast; m.receiveShadow = true; return put(m, along, off, y, sx, sy, sz); };
  // frame bars
  bx(M.frame, op.a, .02, yc, .08, h + .1, .1); bx(M.frame, op.b, .02, yc, .08, h + .1, .1); bx(M.frame, mid, .02, level + op.y0 - .01, w + .1, .06, .1); bx(M.frame, mid, .02, level + op.y1 + .01, w + .1, .06, .1);
  bx(M.frame, mid, .06, level + op.y1 + .12, w + .3, .2, .16); if (op.kind === 'win') bx(M.sill, mid, .1, level + op.y0 - .04, w + .3, .06, .22);
  // outward fake-interior glass (front faces only: invisible from inside), inner clear glass
  // use a thin box face-on for the facade shader (it expects instanced boxes; a plain mesh works with instanceMatrix=identity)
  const fb = new T.Mesh(new T.PlaneGeometry(1, 1), M.glass); put(fb, mid, .06, yc, w - .04, h - .04, 1); fb.castShadow = false;   // front face only: outside sees the fake room, inside sees through
  const ig = new T.Mesh(new T.PlaneGeometry(w - .04, h - .04), M.railGlass); put(ig, mid, .0, yc, 1, 1, 1); ig.renderOrder = 3;
  if (op.balc) { const [c0, c1, dp] = op.balc, bw = c1 - c0, bc = (c0 + c1) / 2; bx(M.balcSlab, bc, dp / 2, level - .12, bw, .24, dp); bx(M.railGlass, bc, dp - .06, level + .55, bw - .12, 1.0, .025, false).renderOrder = 2;
    bx(M.rail, bc, dp - .06, level + 1.07, bw - .04, .045, .07); bx(M.rail, bc, dp - .06, level + .06, bw - .04, .12, .08);
    for (const sd of [-1, 1]) { bx(M.railGlass, bc + sd * (bw / 2 - .06), dp / 2, level + .55, .025, 1.0, dp - .1, false).renderOrder = 2; bx(M.rail, bc + sd * (bw / 2 - .06), dp / 2, level + 1.07, .045, .045, dp - .1); } }
  return g; }
