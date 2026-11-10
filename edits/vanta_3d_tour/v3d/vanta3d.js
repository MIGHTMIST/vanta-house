// vanta3d.js - Vanta House (Blackstone Real Estate, Naguru, Kampala) three.js model + helpers.
// Metres, y up, ground = 0. x = east, z = SOUTH (plan north is -z). Origin: centre between the two blocks.
export const GOLD = '#B08A4E', GOLD_HI = '#D6B26E', IVORY = '#FAF8F3', INK = '#101012';

let T; // THREE namespace (set on entry of every exported fn)

// ------------------------------------------------------------------ site-plan tracing (px of site.jpg -> m)
const SC = 1 / 18.3, OX = 400, OY = 600;               // 71.4 m bottom edge == 1307 px
const pm = (p) => [(p[0] - OX) * SC, (p[1] - OY) * SC];
const PM = (arr) => arr.map(pm);
const PLOT_PX = [[190, 170], [640, 188], [1354, 1005], [47, 1002]];
const NORTH_PX = [[190,265],[262,265],[262,218],[430,218],[430,265],[597,265],[597,410],[487,410],[487,540],[523,540],[523,608],[190,608]];
const SOUTH_PX = [[150,635],[488,635],[488,700],[517,700],[517,635],[707,635],[707,790],[690,790],[690,940],[455,940],[455,975],[372,975],[372,865],[340,865],[340,945],[150,945]];
const DRIVE_PX = [[487,412],[597,412],[597,545],[947,545],[1039,640],[1060,665],[1060,975],[707,975],[707,640],[523,640],[523,545],[487,545]];
const POOL_DECK_PX = [[630,222],[630,490],[650,518],[925,518]];
const POOL_WATER_PX = [[650,250],[650,445],[668,468],[838,468]];
const RAMP_PX = [[1047,792],[1158,792],[1280,930],[1047,930]];
const GUARD_PX = { c: [887, 664], w: 205, d: 58 };
const GATE_PX = [985, 577];
const xDiag = (y) => 640 + 714 * (y - 188) / 817;

export const LEVELS = { ground: 0, basement: -3.3, f1: 4.0, step: 3.3, roof: 40.3, parapet: 1.0 };
export const levelOf = (n) => n === 0 ? 0 : 4.0 + (n - 1) * 3.3;     // n = 0..11 ; 12 -> roof 40.3

// ------------------------------------------------------------------ geometry utils
const area2 = (p) => { let a = 0; for (let i = 0; i < p.length; i++) { const q = p[(i + 1) % p.length]; a += p[i][0] * q[1] - q[0] * p[i][1]; } return a / 2; };
function edgeNormal(a, b, A) { const dx = b[0] - a[0], dz = b[1] - a[1], L = Math.hypot(dx, dz); return A > 0 ? [dz / L, -dx / L] : [-dz / L, dx / L]; }
export function offsetPoly(p, d) {  // d>0 outwards
  const A = area2(p), n = p.length, out = [];
  for (let i = 0; i < n; i++) {
    const a = p[(i + n - 1) % n], b = p[i], c = p[(i + 1) % n];
    const n1 = edgeNormal(a, b, A), n2 = edgeNormal(b, c, A), k = 1 + n1[0] * n2[0] + n1[1] * n2[1];
    out.push([b[0] + (n1[0] + n2[0]) * d / k, b[1] + (n1[1] + n2[1]) * d / k]);
  }
  return out;
}
function inPoly(pt, p) { let c = false; for (let i = 0, j = p.length - 1; i < p.length; j = i++) { if (((p[i][1] > pt[1]) !== (p[j][1] > pt[1])) && (pt[0] < (p[j][0] - p[i][0]) * (pt[1] - p[i][1]) / (p[j][1] - p[i][1]) + p[i][0])) c = !c; } return c; }
const centroid = (p) => { let x = 0, z = 0; p.forEach(q => { x += q[0]; z += q[1]; }); return [x / p.length, z / p.length]; };
const bbox = (p) => { let a = [1e9, 1e9], b = [-1e9, -1e9]; p.forEach(q => { a = [Math.min(a[0], q[0]), Math.min(a[1], q[1])]; b = [Math.max(b[0], q[0]), Math.max(b[1], q[1])]; }); return { min: a, max: b }; };
function shapeOf(p, holes) {
  const s = new T.Shape(); p.forEach((q, i) => i ? s.lineTo(q[0], -q[1]) : s.moveTo(q[0], -q[1])); s.closePath();
  (holes || []).forEach(h => { const hp = new T.Path(); h.forEach((q, i) => i ? hp.lineTo(q[0], -q[1]) : hp.moveTo(q[0], -q[1])); hp.closePath(); s.holes.push(hp); });
  return s;
}
// flat polygon at y=0 (xz), optionally with holes
function flatGeo(p, holes) { const g = new T.ShapeGeometry(shapeOf(p, holes)); g.rotateX(-Math.PI / 2); return g; }
// prism from y0 to y1 (xz polygon)
function prismGeo(p, y0, y1, holes) { const g = new T.ExtrudeGeometry(shapeOf(p, holes), { depth: y1 - y0, bevelEnabled: false, steps: 1 }); g.rotateX(-Math.PI / 2); g.translate(0, y0, 0); return g; }
function mesh(g, m, o = {}) { const x = new T.Mesh(g, m); x.castShadow = o.cast !== false; x.receiveShadow = o.recv !== false; if (o.name) x.name = o.name; return x; }
function box(w, h, d, m, x, y, z, o = {}) { const b = mesh(new T.BoxGeometry(w, h, d), m, o); b.position.set(x, y, z); return b; }

// ------------------------------------------------------------------ materials
function makeMaterials() {
  const S = (c, r = .85, m = 0, extra = {}) => new T.MeshStandardMaterial({ color: c, roughness: r, metalness: m, ...extra });
  return {
    plaster: S('#E8DFC9', .9), plasterDark: S('#55565B', .8), band: new T.MeshLambertMaterial({ color: '#585A5F' }), slab: S('#D9D1BE', .85),
    balcSlab: S('#D9D1BE', .85), frame: new T.MeshLambertMaterial({ color: '#26272A' }), sill: new T.MeshLambertMaterial({ color: '#E9E4D6' }),
    glass: new T.MeshPhongMaterial({ color: '#27394d', specular: '#a9c4dc', shininess: 120 }),
    railGlass: new T.MeshLambertMaterial({ color: '#8fb6bd', transparent: true, opacity: .4, depthWrite: false }),
    rail: new T.MeshLambertMaterial({ color: '#2A2B2E' }), concrete: S('#9B9A96', .9), concreteDark: S('#5E5E5F', .9), roofDark: S('#2B2C30', .8),
    signDark: S('#17181B', .55, .2), gold: S('#B08A4E', .35, .8), goldHi: S('#D6B26E', .3, .9),
    asphalt: S('#3A3B3F', .95), paver: S('#BDB8AC', .9), paverPale: S('#DAD5C8', .85), grass: S('#6F8F4A', 1), terrain: S('#8C9B6C', 1),
    wall: S('#D7D2C6', .9), trunk: S('#5B4633', 1), leaf: S('#5C8A3C', .9), leaf2: S('#3F6F3A', .9), road: S('#2F3033', .95),
    kerb: S('#B9B6AE', .9), white: S('#F2F0EA', .6), glassCurtain: S('#34506B', .08, .5, { transparent: true, opacity: .8 }),
  };
}

// ------------------------------------------------------------------ text helpers
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
function textPlane(text, wm, hm, o = {}) {   // unlit crisp text on a plane (sign faces)
  const c = document.createElement('canvas'); const W = 2048, H = Math.round(2048 * hm / wm); c.width = W; c.height = H; const g = c.getContext('2d');
  const fs = H * (o.fs || .52); g.font = `${o.weight || 600} ${fs}px "Liberation Serif","DejaVu Serif",Georgia,serif`; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.letterSpacing = (fs * .12) + 'px'; g.fillStyle = o.color || '#F3EBD9'; g.fillText(text, W / 2, H / 2 + fs * .03);
  const tex = new T.CanvasTexture(c); tex.colorSpace = T.SRGBColorSpace; tex.anisotropy = 16;
  return new T.Mesh(new T.PlaneGeometry(wm, hm), new T.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, toneMapped: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 }));
}
export function planTexture(THREE, url) {  // Promise<Texture> of a drawing image (sRGB, anisotropic)
  return new Promise((res, rej) => new THREE.TextureLoader().load(url, t => { t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 16; res(t); }, undefined, rej));
}
export function viewportSize() { return { w: window.RENDER_W || window.innerWidth, h: window.RENDER_H || window.innerHeight }; }

// ------------------------------------------------------------------ renderer / sky / lighting
export function makeRenderer(THREE, canvas, o = {}) {
  const { w, h } = viewportSize();
  const r = new THREE.WebGLRenderer({ canvas, antialias: o.antialias ?? (window.NOAA ? false : true), preserveDrawingBuffer: true, powerPreference: 'high-performance' });
  r.setPixelRatio(1); r.setSize(w, h, false); r.outputColorSpace = THREE.SRGBColorSpace; r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = o.exposure ?? 1.0;
  r.shadowMap.enabled = true; r.shadowMap.type = THREE.PCFShadowMap; return r;
}
export function makeSky(THREE, scene, mood = 'day') {
  T = THREE; scene.getObjectByName('sky')?.removeFromParent();
  if (mood === 'ink') {
    const c = document.createElement('canvas'); c.width = 4; c.height = 512; const g = c.getContext('2d'); const gr = g.createLinearGradient(0, 0, 0, 512);
    gr.addColorStop(0, '#0a0a0c'); gr.addColorStop(.55, '#15151a'); gr.addColorStop(1, '#1d1b19'); g.fillStyle = gr; g.fillRect(0, 0, 4, 512);
    const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
    const m = new THREE.Mesh(new THREE.SphereGeometry(1200, 24, 16), new THREE.MeshBasicMaterial({ map: tex, side: THREE.BackSide, fog: false, depthWrite: false })); m.name = 'sky'; m.renderOrder = -10; scene.add(m);
    scene.background = new THREE.Color(INK); scene.fog = new THREE.Fog(0x121215, 220, 700); return m;
  }
  const m = new THREE.Mesh(new THREE.SphereGeometry(1200, 32, 16), new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false, toneMapped: false,
    uniforms: { top: { value: new THREE.Color('#5d95d6') }, mid: { value: new THREE.Color('#a9cdee') }, hor: { value: new THREE.Color('#eaf2f7') } },
    vertexShader: 'varying vec3 vD; void main(){vD=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
    fragmentShader: 'uniform vec3 top,mid,hor; varying vec3 vD; void main(){float h=clamp(vD.y,0.,1.); vec3 c=mix(hor,mid,smoothstep(0.,.18,h)); c=mix(c,top,smoothstep(.15,.8,h)); gl_FragColor=vec4(c,1.);}'
  }));
  m.name = 'sky'; m.renderOrder = -10; scene.add(m); scene.background = new THREE.Color('#a9cdee'); scene.fog = new THREE.Fog(0xdfe9ef, 300, 1300); return m;
}
export function lighting(THREE, scene, mood = 'day', o = {}) {
  T = THREE; (scene.userData.vantaLights || []).forEach(l => { l.removeFromParent(); }); const L = [];
  const add = (l) => { scene.add(l); L.push(l); return l; };
  const day = mood !== 'ink'; const shadowSize = o.shadowSize || 2048;
  const key = add(new THREE.DirectionalLight(day ? 0xfff5e8 : 0xfff2e4, day ? 2.5 : 2.4));
  key.position.set(day ? 70 : 65, day ? 95 : 70, day ? 55 : 45); key.castShadow = true; key.shadow.mapSize.set(shadowSize, shadowSize);
  const sc = key.shadow.camera; const R = o.shadowRadius || 85; sc.left = -R; sc.right = R; sc.top = R; sc.bottom = -R; sc.near = 10; sc.far = 330; key.shadow.bias = -0.0004; key.shadow.normalBias = 0.35; key.shadow.radius = 3;
  const fill = add(new THREE.DirectionalLight(day ? 0x9cbcf0 : 0x6f8fd0, day ? .5 : 1.5)); fill.position.set(-60, 40, -70);
  const hemi = add(new THREE.HemisphereLight(day ? 0xbfd8ff : 0x4a5a78, day ? 0x8b8068 : 0x15151a, day ? .55 : .8));
  const rim = add(new THREE.DirectionalLight(0xD6B26E, day ? 0 : .7)); rim.position.set(-80, 30, -40);
  if (o.renderer) {   // reflective env for glass: tiny gradient room via PMREM
    const pm = new THREE.PMREMGenerator(o.renderer); const es = new THREE.Scene();
    const m = new THREE.Mesh(new THREE.SphereGeometry(50, 16, 8), new THREE.ShaderMaterial({ side: THREE.BackSide,
      uniforms: { a: { value: new THREE.Color(day ? '#78a8e0' : '#1c1f2a') }, b: { value: new THREE.Color(day ? '#f4f1e8' : '#5a5f6b') } },
      vertexShader: 'varying vec3 vD; void main(){vD=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
      fragmentShader: 'uniform vec3 a,b; varying vec3 vD; void main(){gl_FragColor=vec4(mix(b,a,smoothstep(-.1,.7,vD.y)),1.);}' })); es.add(m);
    scene.userData.vantaEnv?.dispose?.(); const tex = pm.fromScene(es, 0.02).texture; pm.dispose(); scene.userData.vantaEnv = tex;
    // NOTE: scene.environment is expensive in software GL (3x frame time), so the env map is applied only to the glass/metal materials.
    const Mt = o.materials; if (Mt) ['glassCurtain', 'gold', 'goldHi'].forEach(k => { if (Mt[k]) { Mt[k].envMap = tex; Mt[k].needsUpdate = true; } });
  }
  scene.userData.vantaLights = L; return { key, fill, hemi, rim, all: L };
}

// ------------------------------------------------------------------ polyline tracks (people / cars)
function makeTrack(pts, closed) {
  const P = pts.slice(); if (closed) P.push(P[0]); const cum = [0];
  for (let i = 1; i < P.length; i++) cum.push(cum[i - 1] + Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]));
  const L = cum[cum.length - 1];
  const at = (s) => { s = Math.max(0, Math.min(L - 1e-6, s)); let i = 1; while (cum[i] < s) i++; const u = (s - cum[i - 1]) / (cum[i] - cum[i - 1] || 1);
    const a = P[i - 1], b = P[i]; return { x: a[0] + (b[0] - a[0]) * u, z: a[1] + (b[1] - a[1]) * u, ang: Math.atan2(b[0] - a[0], b[1] - a[1]) }; };
  return { L, at, closed };
}
// state of a walker on a track at time t. Closed: loops. Open: ping-pong with dwell (turns in place).
function walk(tr, v, t, off, dwell = 0.6) {
  if (tr.closed) { const s = ((t * v + off) % tr.L + tr.L) % tr.L; const r = tr.at(s); r.moving = 1; r.s = s; return r; }
  const leg = tr.L / v, cyc = 2 * (leg + dwell); let u = (((t + off / v) % cyc) + cyc) % cyc;
  if (u < leg) { const r = tr.at(u * v); r.moving = 1; r.s = u * v; return r; }
  u -= leg; if (u < dwell) { const r = tr.at(tr.L); r.moving = 0; r.s = tr.L; r.ang = r.ang + Math.PI * Math.min(1, u / (dwell * .7)); return r; }
  u -= dwell; if (u < leg) { const r = tr.at(tr.L - u * v); r.ang += Math.PI; r.moving = 1; r.s = tr.L - u * v; return r; }
  u -= leg; const r = tr.at(0); r.ang += Math.PI * (1 - Math.min(1, u / (dwell * .7))); r.moving = 0; r.s = 0; return r;
}
const rnd = (seed) => () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296;

// ------------------------------------------------------------------ default paths (metres, [x,z])
export function defaultPaths() {
  const gate = pm(GATE_PX), D = (a) => PM(a);
  const diag = (y0, y1, off) => { const u = [714, 817], l = Math.hypot(...u); const n = [817 / l, -714 / l]; const a = [640 + u[0] * (y0 - 188) / 817, y0], b = [640 + u[0] * (y1 - 188) / 817, y1]; const o = off / SC; return [pm([a[0] + n[0] * o, a[1] + n[1] * o]), pm([b[0] + n[0] * o, b[1] + n[1] * o])]; };
  return {
    gateToNorth: D([[975, 577], [800, 590], [560, 590], [560, 430]]),
    gateToSouth: D([[975, 580], [800, 592], [612, 592], [612, 640]]),
    gateToCourt: D([[975, 583], [900, 600], [880, 700], [880, 880]]),
    poolDeck: offsetPoly(PM(POOL_WATER_PX), 0.55),     // closed loop
    pavement: diag(300, 880, 3.5),                      // road-side pavement outside the boundary (open, ping-pong)
    pavement2: diag(880, 400, 4.2),
  };
}
// ------------------------------------------------------------------ people
export function makePeople(THREE, n = 14, paths = defaultPaths(), o = {}) {
  T = THREE; const group = new T.Group(); group.name = 'people';
  const keys = Object.keys(paths); const tracks = keys.map(k => makeTrack(paths[k], k === 'poolDeck' || (o.closed || []).includes(k)));
  const R = rnd(o.seed || 7), parts = { torso: new T.CapsuleGeometry(.16, .46, 3, 8), head: new T.SphereGeometry(.105, 10, 8),
    leg: new T.CapsuleGeometry(.065, .6, 3, 6), arm: new T.CapsuleGeometry(.048, .46, 3, 6) };
  const mk = (g, name) => { const im = new T.InstancedMesh(g, new T.MeshStandardMaterial({ roughness: .85, metalness: 0 }), n * (name === 'leg' || name === 'arm' ? 2 : 1)); im.castShadow = true; im.receiveShadow = false; im.frustumCulled = false; im.name = 'people_' + name; group.add(im); return im; };
  const torso = mk(parts.torso, 'torso'), head = mk(parts.head, 'head'), leg = mk(parts.leg, 'leg'), arm = mk(parts.arm, 'arm');
  const blob = new T.InstancedMesh(new T.CircleGeometry(.42, 14).rotateX(-Math.PI / 2), new T.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: .22, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4 }), n); blob.frustumCulled = false; group.add(blob);
  const shirts = ['#D9D2C3', '#3F4D5C', '#7D7667', '#A9553F', '#E8E5DE', '#556B55', '#2F3136', '#B79B6A'], pants = ['#24262B', '#3A3F4A', '#8B7F68', '#1F2A3C'], skins = ['#8A5A3C', '#6B4429', '#A06C48', '#4E3222', '#7A4E33'];
  const col = new T.Color(); const ppl = [];
  for (let i = 0; i < n; i++) {
    const ti = i % tracks.length, tr = tracks[ti], sh = col.set(shirts[Math.floor(R() * shirts.length)]).clone(), pa = new T.Color(pants[Math.floor(R() * pants.length)]), sk = new T.Color(skins[Math.floor(R() * skins.length)]);
    const h = .93 + R() * .14; ppl.push({ tr, off: R() * tr.L * (tr.closed ? 1 : 2), v: 1.3 * (.94 + R() * .12), h, ph: R() * 6.28 });
    torso.setColorAt(i, sh); head.setColorAt(i, sk); leg.setColorAt(2 * i, pa); leg.setColorAt(2 * i + 1, pa); arm.setColorAt(2 * i, sh); arm.setColorAt(2 * i + 1, sh);
  }
  [torso, head, leg, arm].forEach(m => { if (m.instanceColor) m.instanceColor.needsUpdate = true; });
  const P = new T.Matrix4(), Q = new T.Matrix4(), W = new T.Matrix4(), eul = new T.Euler(), qq = new T.Quaternion(), one = new T.Vector3(1, 1, 1), sc = new T.Vector3();
  const place = (im, idx, base, px, py, pz, rx, h) => { // pivot at (px,py,pz) in person space, swing rx, part centre hangs below pivot by cy
    Q.makeRotationX(rx); W.copy(base).multiply(Q); im.setMatrixAt(idx, W); };
  function update(t) {
    ppl.forEach((p, i) => {
      const w = walk(p.tr, p.v, t, p.off, .6), sw = w.moving ? Math.sin(w.s * Math.PI * 2 / 1.5 + p.ph * 0) * .55 : 0;
      P.makeRotationY(w.ang); P.setPosition(w.x, .03, w.z); sc.set(p.h, p.h, p.h); P.scale(sc);
      const bob = w.moving ? Math.abs(Math.sin(w.s * Math.PI * 2 / 1.5)) * .02 : 0;
      const loc = (x, y, z, rx = 0, cy = 0) => { Q.makeTranslation(x, y + bob, z); const M = new T.Matrix4().copy(P).multiply(Q); if (rx || cy) { M.multiply(new T.Matrix4().makeRotationX(rx)); M.multiply(new T.Matrix4().makeTranslation(0, cy, 0)); } return M; };
      torso.setMatrixAt(i, loc(0, 1.12, 0)); head.setMatrixAt(i, loc(0, 1.6, 0.01));
      leg.setMatrixAt(2 * i, loc(-.09, .86, 0, sw, -.37)); leg.setMatrixAt(2 * i + 1, loc(.09, .86, 0, -sw, -.37));
      arm.setMatrixAt(2 * i, loc(-.23, 1.38, 0, -sw * .8, -.26)); arm.setMatrixAt(2 * i + 1, loc(.23, 1.38, 0, sw * .8, -.26));
      Q.makeTranslation(w.x, .06, w.z); blob.setMatrixAt(i, Q);
    });
    [torso, head, leg, arm, blob].forEach(m => m.instanceMatrix.needsUpdate = true);
  }
  update(0); return { group, update, paths };
}

// ------------------------------------------------------------------ cars
const CAR_COLS = ['#F1EFEA', '#2B2D31', '#9EA2A8', '#1F2C47', '#7A2E2B', '#C9C5BA'];
function carParts() { return { body: new T.BoxGeometry(1.8, .62, 4.4), cabin: new T.BoxGeometry(1.55, .5, 2.2), wheel: new T.CylinderGeometry(.34, .34, .24, 12).rotateZ(Math.PI / 2) }; }
export function parkedCars(THREE, spots, mats) {      // spots: [{x,z,ang,y?,c?}] -> instanced group
  T = THREE; const g = carParts(), n = spots.length, grp = new T.Group(); grp.name = 'cars_parked';
  const body = new T.InstancedMesh(g.body, new T.MeshStandardMaterial({ roughness: .35, metalness: .5 }), n), cab = new T.InstancedMesh(g.cabin, mats?.glass || new T.MeshStandardMaterial({ color: '#1d2a38', roughness: .1, metalness: .6 }), n), wh = new T.InstancedMesh(g.wheel, new T.MeshStandardMaterial({ color: '#141416', roughness: .9 }), n * 4);
  const m = new T.Matrix4(), q = new T.Quaternion(), p = new T.Vector3(), s = new T.Vector3(1, 1, 1), up = new T.Vector3(0, 1, 0), c = new T.Color();
  spots.forEach((sp, i) => {
    const y = sp.y || 0; q.setFromAxisAngle(up, sp.ang || 0); const fw = new T.Vector3(Math.sin(sp.ang || 0), 0, Math.cos(sp.ang || 0)), rt = new T.Vector3(fw.z, 0, -fw.x);
    m.compose(p.set(sp.x, y + .66, sp.z), q, s); body.setMatrixAt(i, m); body.setColorAt(i, c.set(sp.c || CAR_COLS[i % CAR_COLS.length]));
    m.compose(p.set(sp.x - fw.x * .15, y + 1.22, sp.z - fw.z * .15), q, s); cab.setMatrixAt(i, m);
    let k = 0; for (const a of [-1, 1]) for (const b of [-1, 1]) { m.compose(p.set(sp.x + rt.x * a * .85 + fw.x * b * 1.45, y + .34, sp.z + rt.z * a * .85 + fw.z * b * 1.45), q, s); wh.setMatrixAt(i * 4 + k++, m); }
  });
  [body, cab, wh].forEach(x => { x.castShadow = true; x.receiveShadow = true; x.frustumCulled = false; grp.add(x); }); if (body.instanceColor) body.instanceColor.needsUpdate = true; return grp;
}
function carMesh(color) {
  const g = carParts(), G = new T.Group();
  const b = mesh(g.body, new T.MeshStandardMaterial({ color, roughness: .3, metalness: .55 })); b.position.y = .66;
  const c = mesh(g.cabin, new T.MeshStandardMaterial({ color: '#1d2a38', roughness: .1, metalness: .6 })); c.position.set(0, 1.22, -.15); G.add(b, c);
  const wm = new T.MeshStandardMaterial({ color: '#141416', roughness: .9 });
  for (const a of [-1, 1]) for (const k of [-1, 1]) { const w = mesh(g.wheel, wm); w.position.set(a * .85, .34, k * 1.45); G.add(w); } return G;
}
export function makeCars(THREE, o = {}) {
  T = THREE; const group = new T.Group(); group.name = 'cars'; const P = defaultPaths();
  const spots = []; // parked in the south-east court bays (2.5 m bays, 5 m deep) - px -> m
  const used = [[0, 1, 3, 5], [1, 4]];
  [[760, 2, 0], [935, 3, 1]].forEach(([yy, , row]) => used[row].forEach((i) => { const p = pm([805 + i * 46 + 23, yy]); spots.push({ x: p[0], z: p[1], ang: row ? 0 : Math.PI }); }));
  (o.extraSpots || []).forEach(s => spots.push(s));
  group.add(parkedCars(T, spots));
  const moving = [
    { path: P.gateToCourt, v: 3.2, off: 0, c: '#F1EFEA', dwell: 2.4 }, { path: P.gateToSouth.slice(0, 3).concat([pm([700, 592])]), v: 3.6, off: 6, c: '#1F2C47', dwell: 3 },
    { path: PM([[1160, 1000], [1060, 840], [900, 640], [700, 470], [600, 330]]), v: 6, off: 0, c: '#7A2E2B', dwell: 0, road: true },
  ];
  // car on the public road: long straight, loops (start/end are off-camera)
  const rd = roadGeometry(); const roadPath = [rd.lane(-90), rd.lane(160)];
  moving[2].path = roadPath; moving[2].loop = true;
  const meshes = moving.map(mv => { const m = carMesh(mv.c); group.add(m); mv.tr = makeTrack(mv.path, false); return m; });
  function update(t) {
    moving.forEach((mv, i) => {
      let r; if (mv.loop) { const s = (((t * mv.v + 40) % mv.tr.L) + mv.tr.L) % mv.tr.L; r = mv.tr.at(s); } else r = walk(mv.tr, mv.v, t, mv.off, mv.dwell);
      meshes[i].position.set(r.x, .03, r.z); meshes[i].rotation.y = r.ang; });
  }
  update(0); return { group, update };
}
function roadGeometry() {
  const A = pm([640, 188]), B = pm([1354, 1005]); const dx = B[0] - A[0], dz = B[1] - A[1], L = Math.hypot(dx, dz), u = [dx / L, dz / L], n = [-u[1] * -1, u[0] * -1]; // n points east/outwards (+x, -z)
  const nn = [Math.abs(u[1]), -Math.abs(u[0])]; // outward = east (+x), north (-z)
  return { A, B, u, n: nn, L, at: (s, off) => [A[0] + u[0] * s + nn[0] * off, A[1] + u[1] * s + nn[1] * off], lane: (s, off = 11.5) => [A[0] + u[0] * s + nn[0] * off, A[1] + u[1] * s + nn[1] * off] };
}

// ------------------------------------------------------------------ facade generator
const BAY = { B: 3.0, A: 1.4, W: 2.2 };
function buildFloorGroups(M, blocks, floors) {
  const dummy = new T.Object3D(); const mtx = new T.Matrix4(), X = new T.Vector3(), Y = new T.Vector3(0, 1, 0), Z = new T.Vector3(), Rm = new T.Matrix4(), qq = new T.Quaternion(), pp = new T.Vector3(), ss = new T.Vector3();
  const BG = new T.BoxGeometry(1, 1, 1);
  const types = { frame: M.frame, glass: M.glass, sill: M.sill, band: M.band, bslab: M.balcSlab, bglass: M.railGlass, brail: M.rail };
  const allPolys = Object.values(blocks).map(b => b.polygon);
  for (let k = 1; k <= 11; k++) {
    const fl = floors[k + 1], level = levelOf(k), g = fl.group, lists = {}; Object.keys(types).forEach(t => lists[t] = []);
    const add = (type, ex, ey, ez, w, h, d) => lists[type].push([ex, ey, ez, w, h, d]);
    Object.values(blocks).forEach((blk, bi) => {
      const poly = blk.polygon, A = area2(poly), n = poly.length;
      g.add(mesh(prismGeo(offsetPoly(poly, .12), level - .3, level), M.slab, { name: 'slab' }));
      g.add(mesh(prismGeo(poly, level, level + 3.0), k === 1 ? M.plasterDark : M.plaster, { name: 'walls' }));
      for (let e = 0; e < n; e++) {
        const a = poly[e], b = poly[(e + 1) % n], nrm = edgeNormal(a, b, A), L = Math.hypot(b[0] - a[0], b[1] - a[1]);
        if (L < 2.6) continue;
        const tg = [nrm[1] * -1 * -1, 0]; const t = [nrm[1], -nrm[0]];           // tangent so that X x Y = n
        const s0 = a[0] * t[0] + a[1] * t[1], s1 = b[0] * t[0] + b[1] * t[1], sa = Math.min(s0, s1), sb = Math.max(s0, s1);
        const org = (s, o) => [a[0] + t[0] * (s - s0) + nrm[0] * o, a[1] + t[1] * (s - s0) + nrm[1] * o];
        // balcony allowed? free space 2 m out must not be inside any block
        const mid = org((sa + sb) / 2, 0); let balcOK = L >= 6;
        for (const f of [1.8, 2.8]) { const pt = [mid[0] + nrm[0] * f, mid[1] + nrm[1] * f]; if (allPolys.some(pp2 => inPoly(pt, pp2))) balcOK = false; }
        const usable = L - 1.4; const seq = ['B', 'A', 'W', 'A']; let si = (e + bi) % 2 === 0 ? 0 : 2; const row = []; let tot = 0;
        for (let guard = 0; guard < 40; guard++) { let ty = seq[si % 4]; si++; let w = BAY[ty]; if (tot + w > usable) { if (tot + BAY.W <= usable && ty !== 'A') { ty = 'W'; w = BAY.W; } else break; } row.push([ty, w]); tot += w; }
        if (row.length && row[row.length - 1][0] === 'A') { tot -= row.pop()[1]; }
        let cur = sa + (L - tot) / 2;
        const win = (sc, y0, w, h, mull) => {
          add('frame', sc, y0 + h / 2, .05, w + .14, h + .14, .10); add('glass', sc, y0 + h / 2, .092, w, h, .04);
          if (mull) add('frame', sc, y0 + h / 2, .105, .05, h, .12); add('sill', sc, y0 - .02, .11, w + .34, .07, .24);
        };
        const em = (type, sc, y, o, w, h, d) => { const p = org(sc, o); lists[type].push([p[0], level + y, p[1], w, h, d, t, nrm]); };
        row.forEach(([ty, w]) => {
          const c = cur + w / 2; cur += w;
          const F = (type, y, o, ww, h, d, lat = 0) => em(type, c + lat, y, o, ww, h, d);
          if (ty === 'B') {
            if (balcOK) {
              const dw = w - .8; F('frame', 1.2, .05, dw + .14, 2.44, .10); F('glass', 1.22, .092, dw, 2.3, .04); F('frame', 1.22, .105, .05, 2.3, .12);
              F('bslab', -.15, .10 + .7, w - .1, .28, 1.4); F('bglass', .55, 1.46, w - .18, 1.0, .03); F('brail', 1.07, 1.46, w - .1, .05, .07);
              F('brail', .55, 1.46, .05, 1.0, .05, -(w - .1) / 2 + .02); F('brail', .55, 1.46, .05, 1.0, .05, (w - .1) / 2 - .02);
              F('bglass', .55, .8, .03, 1.0, 1.3, -(w - .12) / 2); F('bglass', .55, .8, .03, 1.0, 1.3, (w - .12) / 2); F('brail', 1.07, .8, .05, .05, 1.38, -(w - .12) / 2); F('brail', 1.07, .8, .05, .05, 1.38, (w - .12) / 2);
              // balcony slab edge + underside rendered by slab; light
            } else { const ww = w - .9; F('frame', 1.5, .05, ww + .14, 1.6 + .14, .10); F('glass', 1.5, .092, ww, 1.6, .04); F('frame', 1.5, .105, .05, 1.6, .12); F('sill', .66, .11, ww + .34, .07, .24); F('frame', 1.5, .105, ww * .5, .04, .12, -.0); }
          } else if (ty === 'W') { const ww = w - 1.0; F('frame', 1.5, .05, ww + .14, 1.6 + .14, .10); F('glass', 1.5, .092, ww, 1.6, .04); F('frame', 1.5, .105, .05, 1.6, .12); F('sill', .66, .11, ww + .34, .07, .24); }
          else { // accent band with narrow slit window
            F('band', 1.5, .035, w, 3.0, .07); F('frame', 1.5, .08, .66, 1.75, .06); F('glass', 1.5, .105, .5, 1.6, .03);
          }
        });
      }
    });
    // instanced meshes
    for (const tname of Object.keys(types)) {
      const L = lists[tname]; if (!L.length) continue;
      const im = new T.InstancedMesh(BG, types[tname], L.length); im.name = tname; im.castShadow = tname === 'bslab' || tname === 'band'; im.receiveShadow = tname === 'bslab'; im.frustumCulled = false;
      L.forEach((r, i) => { const t = r[6], nrm = r[7]; X.set(t[0], 0, t[1]); Z.set(nrm[0], 0, nrm[1]); Rm.makeBasis(X, Y, Z); qq.setFromRotationMatrix(Rm); ss.set(r[3], r[4], r[5]);
        const p0 = r[0], p1 = r[1], p2 = r[2]; pp.set(p0, p1, p2); mtx.compose(pp, qq, ss); im.setMatrixAt(i, mtx); });
      g.add(im);
    }
  }
}

// ------------------------------------------------------------------ ground / basement / roof
function gridPoints(poly, sx, sz, inset) { const bb = bbox(poly), ip = offsetPoly(poly, -inset), out = []; for (let x = bb.min[0] + 1.5; x < bb.max[0]; x += sx) for (let z = bb.min[1] + 1.5; z < bb.max[1]; z += sz) if (inPoly([x, z], ip)) out.push([x, z]); return out; }
function carSpotsIn(poly, rows, seed, y, prob) {
  const R = rnd(seed), bb = bbox(poly), ip = offsetPoly(poly, -1.6), spots = [];
  for (let z = bb.min[1] + rows[0]; z < bb.max[1]; z += rows[1]) for (let x = bb.min[0] + 2; x < bb.max[0]; x += 2.7) {
    if (!inPoly([x, z], ip) || !inPoly([x, z + 2.3], ip) || !inPoly([x, z - 2.3], ip)) continue;
    const col = ((x - bb.min[0] - 1.5) % 7.5), cz = ((z - bb.min[1] - 1.5) % 8); if (Math.abs(col) < .8 || Math.abs(col - 7.5) < .8) continue;
    if (R() < prob) spots.push({ x, z, y, ang: R() < .5 ? 0 : Math.PI });
  } return spots;
}
function buildGround(M, blocks, g) {
  Object.values(blocks).forEach((blk, bi) => {
    const poly = blk.polygon, n = poly.length, A = area2(poly);
    g.add(mesh(prismGeo(offsetPoly(poly, .02), 3.05, 3.7, [offsetPoly(poly, -.2)]), M.plasterDark, { name: 'fascia' }));
    // perimeter + interior columns
    const cols = []; for (let e = 0; e < n; e++) { const a = poly[e], b = poly[(e + 1) % n], L = Math.hypot(b[0] - a[0], b[1] - a[1]); if (L < 2) continue; const k = Math.max(1, Math.round(L / 5)); for (let i = 0; i < k; i++) { const u = i / k; cols.push([a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u]); } }
    gridPoints(poly, 7.5, 8, 3).forEach(p => cols.push(p));
    const im = new T.InstancedMesh(new T.BoxGeometry(.62, 3.7, .62), M.concreteDark, cols.length); const m4 = new T.Matrix4();
    cols.forEach((c, i) => { m4.makeTranslation(c[0], 1.85, c[1]); im.setMatrixAt(i, m4); }); im.castShadow = true; im.receiveShadow = true; g.add(im);
    // lift / stair core
    const c = centroid(poly); const bb = bbox(poly); blk.core = [Math.min(bb.max[0] - 4, c[0] + (bi ? 4 : -2)), c[1]];
    g.add(box(5.5, 3.7, 6.5, M.concrete, blk.core[0], 1.85, blk.core[1]));
    const gl = box(4.2, 1.8, .06, M.glassCurtain, blk.core[0], 1.4, blk.core[1] + 3.28, { cast: false }); g.add(gl);
  });
  // entrance lobby on the south block's north face (towards the driveway) + canopy
  const ent = PM([[517, 635], [707, 635]]); const ex = (ent[0][0] + ent[1][0]) / 2, ez = ent[0][1];
  g.add(box(8.2, 3.0, .12, M.glassCurtain, ex, 1.5, ez + 1.2, { cast: false, name: 'lobbyGlass' }));
  g.add(box(9.0, .22, 3.2, M.roofDark, ex, 3.05, ez - .3, { name: 'canopy' })); g.add(box(9.0, .05, .06, M.goldHi, ex, 2.93, ez - 1.9, { name: 'canopyGold' }));
  g.add(box(2.2, 2.7, .1, M.goldHi, ex + 4.3, 1.35, ez + 1.15, { cast: false, name: 'lobbyDoor' }));
  blocks.south.entrance = [ex, ez - 1.5]; const nn = pm([540, 430]); blocks.north.entrance = [nn[0], nn[1]];
  // parked cars
  const spots = [...carSpotsIn(blocks.south.polygon, [3, 8], 11, 0, .55), ...carSpotsIn(blocks.north.polygon, [3, 8], 5, 0, .5)].filter(s => !Object.values(blocks).some(b => Math.abs(s.x - b.core[0]) < 3.6 && Math.abs(s.z - b.core[1]) < 4.4) && !(Math.abs(s.x - ex) < 5 && s.z > ez - .2 && s.z < ez + 3));
  g.add(parkedCars(T, spots, M));
}
function buildBasement(M, blocks, g) {
  const f = (x, y) => [x, y];
  const px = (y) => 190 - 143 * (y - 170) / 832 + 40;
  const bp = PM([[px(240), 240], [600, 240], [600, 540], [925, 540], [1015, 640], [1047, 700], [1047, 975], [px(975), 975]]);
  g.add(mesh(prismGeo(bp, -3.75, -3.3), M.concrete, { name: 'basementSlab' }));
  g.add(mesh(prismGeo(offsetPoly(bp, .35), -3.3, -.05, [bp]), M.concreteDark, { name: 'basementWall' }));
  g.add(mesh(prismGeo(offsetPoly(bp, .35), -.4, -.05), M.slab, { name: 'basementCeiling' }));
  const cols = gridPoints(bp, 7.5, 8, 1.5); const im = new T.InstancedMesh(new T.BoxGeometry(.6, 3.2, .6), M.concrete, cols.length), m4 = new T.Matrix4();
  cols.forEach((c, i) => { m4.makeTranslation(c[0], -1.7, c[1]); im.setMatrixAt(i, m4); }); g.add(im);
  g.add(parkedCars(T, carSpotsIn(bp, [3, 8], 21, -3.3, .7), M));
  g.userData.polygon = bp; return bp;
}
function buildRoof(M, blocks, g, signText) {
  const y0 = LEVELS.roof;
  Object.values(blocks).forEach((blk, bi) => {
    const p = blk.polygon;
    g.add(mesh(prismGeo(offsetPoly(p, .12), y0 - .3, y0), M.slab, { name: 'roofSlab' }));
    g.add(mesh(prismGeo(offsetPoly(p, .02), y0, y0 + 1.0, [offsetPoly(p, -.25)]), M.plaster, { name: 'parapet' }));
    g.add(mesh(prismGeo(offsetPoly(p, .08), y0 + 1.0, y0 + 1.08, [offsetPoly(p, -.31)]), M.sill, { name: 'coping' }));
    g.add(mesh(flatGeo(offsetPoly(p, -.3)).translate(0, y0 + .01, 0), M.roofDark, { cast: false, name: 'roofDeck' }));
    const c = blk.core; g.add(box(6, 3.2, 7, M.plaster, c[0], y0 + 1.6, c[1], { name: 'overrun' })); g.add(box(6.3, .2, 7.3, M.concrete, c[0], y0 + 3.3, c[1]));
    const bb = bbox(p); for (let i = 0; i < 2; i++) { const t = mesh(new T.CylinderGeometry(1.1, 1.1, 1.8, 16), M.white); t.position.set(c[0] + (i ? -6 : -6), y0 + .9, c[1] + (i ? 5 : -5)); g.add(t); }
  });
  // sign band over the east part of the south block roof
  const sx = 15.3, z0 = pm([0, 645])[1], z1 = pm([0, 940])[1], len = z1 - z0, zc = (z0 + z1) / 2, sh = 3.9, th = .5, yc = y0 + sh / 2;
  const sg = new T.Group(); sg.name = 'sign'; g.add(sg);
  sg.add(box(th, sh, len, M.signDark, sx, yc, zc, { name: 'signBand' }));
  sg.add(box(th + .08, .1, len + .1, M.goldHi, sx, y0 + sh + .05, zc)); sg.add(box(th + .08, .08, len + .1, M.goldHi, sx, y0 + .5, zc));
  const ribs = new T.InstancedMesh(new T.BoxGeometry(.05, sh - .4, .12), new T.MeshStandardMaterial({ color: '#2b2c31', roughness: .5, metalness: .4 }), 2 * Math.floor(len / .42)); const m4 = new T.Matrix4(); let ri = 0;
  for (let z = z0 + .3; z < z1 - .3 && ri < ribs.count - 1; z += .42) for (const s of [-1, 1]) { m4.makeTranslation(sx + s * (th / 2 + .02), yc, z); ribs.setMatrixAt(ri++, m4); } ribs.count = ri; sg.add(ribs);
  const tw = len * .78, th2 = 2.2;
  const te = textPlane(signText, tw, th2); te.rotation.y = Math.PI / 2; te.position.set(sx + th / 2 + .12, yc + .15, zc); sg.add(te);
  const tw2 = textPlane(signText, tw, th2); tw2.rotation.y = -Math.PI / 2; tw2.position.set(sx - th / 2 - .12, yc + .15, zc); sg.add(tw2);
  g.userData.sign = sg;
}

// ------------------------------------------------------------------ site
function seg(a, b, h, th, mat, y0 = 0) { const L = Math.hypot(b[0] - a[0], b[1] - a[1]); const m = box(L, h, th, mat, (a[0] + b[0]) / 2, y0 + h / 2, (a[1] + b[1]) / 2); m.rotation.y = -Math.atan2(b[1] - a[1], b[0] - a[0]); return m; }
function strip(a, b, w, inward, mat, y) { // quad a-b extruded inward by w (inward = unit [x,z])
  const g = new T.BufferGeometry(); const v = [a, b, [b[0] + inward[0] * w, b[1] + inward[1] * w], [a[0] + inward[0] * w, a[1] + inward[1] * w]];
  g.setAttribute('position', new T.Float32BufferAttribute(v.flatMap(p => [p[0], y, p[1]]), 3)); g.setIndex([0, 2, 1, 0, 3, 2]); g.setAttribute('normal', new T.Float32BufferAttribute([0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], 3));
  const m = new T.Mesh(g, mat); m.receiveShadow = true; m.material.side = T.DoubleSide; return m;
}
const MOODS = {
  day: { terrain: '#B9C1A4', grass: '#6E9148', paver: '#C2BDB1', paverPale: '#DDD8CB', asphalt: '#47484C', road: '#3B3C40', wall: '#DAD5C9', leaf: '#5C8A3C', leaf2: '#44773A' },
  ink: { terrain: '#101012', grass: '#1C2620', paver: '#2A2A2E', paverPale: '#3A3A3F', asphalt: '#1A1A1D', road: '#17171A', wall: '#3A3A3E', leaf: '#3a5e45', leaf2: '#2a4634' },
};
function buildSite(M, blocks, o) {
  const site = new T.Group(); site.name = 'site'; const ground = new T.Group(); ground.name = 'ground'; site.add(ground);
  const plot = PM(PLOT_PX), rd = roadGeometry();
  // terrain with hole for the plot
  const big = new T.Shape(); big.moveTo(-1800, -1800); big.lineTo(1800, -1800); big.lineTo(1800, 1800); big.lineTo(-1800, 1800); big.closePath();
  const hp = new T.Path(); plot.forEach((q, i) => i ? hp.lineTo(q[0], -q[1]) : hp.moveTo(q[0], -q[1])); hp.closePath(); big.holes.push(hp);
  const tg = new T.ShapeGeometry(big); tg.rotateX(-Math.PI / 2); const terrain = mesh(tg, M.terrain, { cast: false }); terrain.position.y = -.06; terrain.name = 'terrain'; ground.add(terrain);
  const ramp = PM(RAMP_PX);
  const base = mesh(flatGeo(plot, [ramp]), M.paver, { cast: false }); base.name = 'plotBase'; ground.add(base);
  // road reserve pavement, road, kerbs, dashes
  const R = (s0, s1, o0, o1, mat, y, name) => { const a = rd.at(s0, o0), b = rd.at(s1, o0); const m = strip(a, b, o1 - o0, rd.n, mat, y); if (name) m.name = name; return m; };
  ground.add(R(-200, rd.L + 200, 0, 5, M.paverPale, .005, 'roadReserve')); ground.add(R(-200, rd.L + 200, 5, 19.5, M.road, .01, 'road')); ground.add(R(-200, rd.L + 200, 4.8, 5.1, M.kerb, .04));
  const dash = new T.InstancedMesh(new T.BoxGeometry(.18, .02, 3), new T.MeshBasicMaterial({ color: '#CFC9B8' }), 70), m4 = new T.Matrix4(), q = new T.Quaternion(); let di = 0;
  for (let s = -150; s < rd.L + 150 && di < 70; s += 9) { const c = rd.at(s + 1.5, 12.25); q.setFromAxisAngle(new T.Vector3(0, 1, 0), Math.atan2(rd.u[0], rd.u[1])); m4.compose(new T.Vector3(c[0], .03, c[1]), q, new T.Vector3(1, 1, 1)); dash.setMatrixAt(di++, m4); } dash.count = di; ground.add(dash);
  // planting strips inside the plot (setbacks)
  const inw = (a, b) => { const A = area2(plot); const n = edgeNormal(a, b, A); return [-n[0], -n[1]]; };
  const P = plot, diagU = rd.u; const gs = (a, b, w, y = .02) => { const m = strip(a, b, w, inw(a, b), M.grass, y); m.name = 'planting'; ground.add(m); };
  gs(P[0], P[1], 2.6); gs(P[3], P[0], 2.6); gs(pm([100, 1002]), pm([1047, 1002]), 2.4);
  const dp = (y) => pm([xDiag(y), y]); gs(dp(188), dp(500), 2.6); gs(dp(660), dp(792), 2.4);
  ground.add((() => { const m = mesh(flatGeo(PM([[600, 215], [645, 195], [925, 516], [600, 530]])).translate(0, .025, 0), M.grass, { cast: false }); m.name = 'poolLawn'; return m; })());
  // driveway asphalt + parking bay markings
  const drive = mesh(flatGeo(PM(DRIVE_PX)).translate(0, .03, 0), M.asphalt, { cast: false }); drive.name = 'driveway'; ground.add(drive);
  const bays = new T.InstancedMesh(new T.BoxGeometry(.1, .02, 5), new T.MeshBasicMaterial({ color: '#E9E5D8' }), 40); let bi = 0;
  [[725, 815], [890, 975]].forEach(([y0, y1]) => { for (let i = 0; i <= 6; i++) { const c = pm([805 + i * 46, (y0 + y1) / 2]); m4.makeTranslation(c[0], .045, c[1]); bays.setMatrixAt(bi++, m4); } }); bays.count = bi; ground.add(bays);
  // boundary wall, gate
  const wall = new T.Group(); wall.name = 'boundaryWall'; site.add(wall); const WH = 1.8, WT = .28;
  const gateC = pm(GATE_PX); const gp = (s) => rd.at(s, 0); const sGate = ((gateC[0] - rd.A[0]) * rd.u[0] + (gateC[1] - rd.A[1]) * rd.u[1]);
  const wp = (a, b) => { wall.add(seg(a, b, WH, WT, M.wall)); wall.add(seg(a, b, .1, WT + .1, M.kerb, WH)); };
  wp(P[3], P[0]); wp(P[0], P[1]); wp(P[3], pm([1047, 1002]));
  wp(gp(0), gp(sGate - 4.6)); wp(gp(sGate + 4.6), gp(((pm(xDiag(792) ? [xDiag(792), 792] : [0, 0])[0] - rd.A[0]) * rd.u[0] + (pm([xDiag(792), 792])[1] - rd.A[1]) * rd.u[1])));
  const gate = new T.Group(); gate.name = 'gate'; site.add(gate); const ang = -Math.atan2(rd.u[1], rd.u[0]);
  for (const s of [-4.6, 4.6]) { const c = gp(sGate + s); const pil = new T.Group(); pil.position.set(c[0], 0, c[1]); pil.rotation.y = ang; pil.add(box(.8, 2.5, .8, M.plaster, 0, 1.25, 0), box(.95, .15, .95, M.concrete, 0, 2.58, 0), box(.2, .1, .2, M.goldHi, 0, 2.7, 0)); gate.add(pil); }
  { const c = gp(sGate + 6.4); const leaf = new T.Group(); leaf.position.set(c[0], 0, c[1]); leaf.rotation.y = ang; leaf.add(box(4.4, 1.7, .08, M.rail, 0, 1.0, 0)); for (let i = -10; i <= 10; i++) leaf.add(box(.04, 1.7, .12, M.frame, i * .2, 1.0, 0, { cast: false })); gate.add(leaf); }
  { const c = gp(sGate - 9); const plaque = new T.Group(); plaque.position.set(c[0] - rd.n[0] * 1.5, 0, c[1] - rd.n[1] * 1.5); plaque.rotation.y = ang; plaque.add(box(5.0, 1.5, .45, M.concreteDark, 0, .75, 0)); plaque.add(box(5.1, .08, .5, M.goldHi, 0, 1.54, 0));
    for (const s of [1, -1]) { const t = textPlane('VANTA HOUSE', 4.4, .8, { fs: .58 }); t.position.set(0, .8, s * .24); t.rotation.y = s > 0 ? 0 : Math.PI; plaque.add(t); } gate.add(plaque); }
  // guardhouse
  const gc = pm(GUARD_PX.c), gw = GUARD_PX.w * SC, gd = GUARD_PX.d * SC; const gh = new T.Group(); gh.name = 'guardhouse'; gh.position.set(gc[0], 0, gc[1]); site.add(gh);
  gh.add(box(gw, 3.0, gd, M.plaster, 0, 1.5, 0), box(gw + .7, .3, gd + .7, M.roofDark, 0, 3.15, 0), box(gw + .72, .06, gd + .72, M.goldHi, 0, 3.32, 0)); gh.add(box(gw - .6, 1.5, .1, M.glassCurtain, 0, 1.65, -gd / 2 - .03, { cast: false }), box(gw - .6, 1.5, .1, M.glassCurtain, 0, 1.65, gd / 2 + .03, { cast: false }), box(gw - .3, .6, gd + .06, M.plasterDark, 0, .3, 0));
  // ramp (14 deg) down to the basement
  const rampG = new T.Group(); rampG.name = 'ramp'; site.add(rampG); const xE = ramp[2][0]; const yr = (x) => -Math.max(0, Math.min(3.3, Math.tan(14 * Math.PI / 180) * (xE - x)));
  { const v = ramp.map(p => [p[0], yr(p[0]) + .02, p[1]]); const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(v.flat(), 3)); g.setIndex([0, 2, 1, 0, 3, 2]); g.computeVertexNormals(); const mm = new T.Mesh(g, M.concreteDark.clone()); mm.material.side = T.DoubleSide; mm.receiveShadow = true; mm.name = 'rampSurface'; rampG.add(mm);
    for (const [i, j] of [[0, 1], [1, 2], [2, 3]]) { const a = ramp[i], b = ramp[j]; const vv = [[a[0], yr(a[0]), a[1]], [b[0], yr(b[0]), b[1]], [b[0], .12, b[1]], [a[0], .12, a[1]]]; const wg = new T.BufferGeometry(); wg.setAttribute('position', new T.Float32BufferAttribute(vv.flat(), 3)); wg.setIndex([0, 1, 2, 0, 2, 3]); wg.computeVertexNormals(); const wm = new T.Mesh(wg, M.concrete.clone()); wm.material.side = T.DoubleSide; wm.receiveShadow = true; rampG.add(wm); }
    for (let i = 0; i < 12; i++) { const x = xE - 1.2 - i * 1.05, c = [x, (ramp[0][1] + ramp[3][1]) / 2]; const gr = new T.Mesh(new T.BoxGeometry(.12, .03, ramp[3][1] - ramp[0][1] - 1.2), new T.MeshBasicMaterial({ color: '#8c8a83' })); gr.position.set(x, yr(x) + .05, c[1]); gr.rotation.z = -Math.atan(Math.tan(14 * Math.PI / 180)) * 0; rampG.add(gr); } }
  // pool
  const pool = buildPool(M); site.add(pool.group);
  // trees
  const trees = buildTrees(M, rd); site.add(trees.group);
  const boundaryPoints = plot.map(p => new T.Vector3(p[0], 0, p[1]));
  const setMood = (mood) => { const pal = MOODS[mood] || MOODS.day; Object.keys(pal).forEach(k => M[k].color.set(pal[k])); };
  return { group: site, ground, boundaryPoints, road: { group: ground.getObjectByName('road'), geometry: rd, lane: rd.lane }, gate, guardhouse: gh, ramp: rampG, trees, pool, setMood, polygon: plot };
}
function buildTrees(M) {
  const g = new T.Group(); g.name = 'trees'; const R = rnd(3), rd = roadGeometry();
  const diagPt = (y, off) => { const u = rd.u, A = rd.A, P0 = pm([xDiag(y), y]); return [P0[0] + rd.n[0] * off, P0[1] + rd.n[1] * off]; };
  const list = [[300, 2.4], [372, 2.4], [478, 2.4], [700, 2.6], [760, 2.6], [960, 2.4]].map(([y, o]) => diagPt(y, o)).concat(PM([[225, 235], [480, 235], [215, 215], [112, 540], [100, 880], [1100, 960], [1040, 700], [330, 990], [520, 985]]));
  const palms = PM([[860, 545], [905, 660], [1000, 720], [700, 560]]).concat([diagPt(560, 2.4), diagPt(840, 2.4)]);
  const trunk = new T.InstancedMesh(new T.CylinderGeometry(.16, .26, 1, 8), M.trunk, list.length + palms.length), blob = new T.InstancedMesh(new T.IcosahedronGeometry(1, 1), M.leaf, list.length * 3);
  const frond = new T.InstancedMesh(new T.BoxGeometry(.7, .05, 3.6), M.leaf2, palms.length * 10); const m4 = new T.Matrix4(), q = new T.Quaternion(), e = new T.Euler(); let bi = 0, ti = 0, fi = 0; const c = new T.Color();
  list.forEach(([x, z]) => { const h = 3.2 + R() * 1.8, r = 1.8 + R() * .9; m4.compose(new T.Vector3(x, h / 2, z), q.identity(), new T.Vector3(1, h, 1)); trunk.setMatrixAt(ti++, m4);
    for (let k = 0; k < 3; k++) { const rr = r * (k ? .72 : 1); m4.compose(new T.Vector3(x + (k ? (R() - .5) * 1.6 : 0), h + 1 + k * .7, z + (k ? (R() - .5) * 1.6 : 0)), q.identity(), new T.Vector3(rr, rr * .85, rr)); blob.setMatrixAt(bi, m4); blob.setColorAt(bi++, c.setHSL(.27 + R() * .04, .4, .3 + R() * .08)); } });
  palms.forEach(([x, z]) => { const h = 5 + R() * 3; m4.compose(new T.Vector3(x, h / 2, z), q.identity(), new T.Vector3(1, h, 1)); trunk.setMatrixAt(ti++, m4);
    for (let k = 0; k < 10; k++) { const a = k / 10 * Math.PI * 2 + R() * .3; e.set(.6 + R() * .25, a, 0, 'YXZ'); q.setFromEuler(e); const dir = new T.Vector3(Math.sin(a), 0, Math.cos(a)); m4.compose(new T.Vector3(x + dir.x * 1.5, h - .1, z + dir.z * 1.5), q, new T.Vector3(1, 1, 1)); frond.setMatrixAt(fi++, m4); } });
  blob.instanceColor.needsUpdate = true; [trunk, blob, frond].forEach(m => { m.castShadow = true; m.receiveShadow = true; m.frustumCulled = false; g.add(m); }); return { group: g, positions: list.concat(palms) };
}
function buildPool(M) {
  const g = new T.Group(); g.name = 'pool'; const deck = PM(POOL_DECK_PX), water = PM(POOL_WATER_PX);
  g.add(mesh(flatGeo(deck, [offsetPoly(water, .02)]).translate(0, .04, 0), M.paverPale, { cast: false, name: 'poolDeck' }));
  // coping ring + basin
  const cop = mesh(prismGeo(offsetPoly(water, .3), .04, .16, [water]), M.sill, { name: 'poolCoping' }); g.add(cop);
  g.add(mesh(prismGeo(offsetPoly(water, .02), -1.4, .05, [offsetPoly(water, -.05)]), new T.MeshStandardMaterial({ color: '#7fc9c9', roughness: .5 }), { name: 'poolWall', cast: false }));
  const wmat = new T.ShaderMaterial({ uniforms: { t: { value: 0 } }, transparent: false,
    vertexShader: 'varying vec2 vP; void main(){ vP=position.xz; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: `uniform float t; varying vec2 vP;
      void main(){ float w=sin(vP.x*2.3+t*1.4)+sin(vP.y*2.9-t*1.15)+sin((vP.x-vP.y)*1.7+t*.8)+sin((vP.x+vP.y)*3.9-t*1.9)*.6;
        float c=pow(.5+.25*w,3.0); vec3 deep=vec3(.02,.48,.55), lite=vec3(.10,.85,.85); vec3 col=mix(deep,lite,.5+.18*w)+vec3(.6,.9,.95)*c*.16;
        gl_FragColor=vec4(col,1.);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }` });
  const wm = new T.Mesh(flatGeo(offsetPoly(water, -.05)), wmat); wm.position.y = -.1; wm.name = 'poolWater'; g.add(wm);
  // retaining wall (west) and steel railing (south + hypotenuse)
  g.add(seg(deck[0], deck[1], 1.0, .3, M.concrete)); g.add(seg(deck[1], pm([600, 505]), 1.0, .3, M.concrete));
  const rail = new T.Group(); rail.name = 'poolRailing'; g.add(rail);
  [[deck[2], deck[3]], [deck[3], deck[0]]].forEach(([a, b]) => { const L = Math.hypot(b[0] - a[0], b[1] - a[1]), k = Math.round(L / 1.5); rail.add(seg(a, b, .04, .05, M.rail, .98), seg(a, b, .04, .05, M.rail, .5)); for (let i = 0; i <= k; i++) { const u = i / k; rail.add(box(.05, 1.0, .05, M.rail, a[0] + (b[0] - a[0]) * u, .5, a[1] + (b[1] - a[1]) * u)); } });
  // loungers
  const lg = new T.Group(); lg.name = 'loungers'; g.add(lg); const lm = new T.MeshStandardMaterial({ color: '#F1EEE6', roughness: .7 }), lc = new T.MeshStandardMaterial({ color: '#1f3a4a', roughness: .9 });
  [[700, 495], [727, 495], [775, 495], [802, 495]].forEach(([x, y], i) => { const p = pm([x, y]); const l = new T.Group(); l.position.set(p[0], .04, p[1]);
    l.add(box(.7, .07, 1.1, lm, 0, .32, .3), box(.7, .07, .95, lm, 0, .55, -.62)); l.children[1].rotation.x = -.5; l.add(box(.66, .02, 1.05, lc, 0, .37, .3)); for (const sx of [-.3, .3]) for (const sz of [-.1, .9]) l.add(box(.05, .3, .05, M.rail, sx, .15, sz)); lg.add(l); });
  const umb = (px, py) => { const p = pm([px, py]); const u = new T.Group(); u.position.set(p[0], .04, p[1]); const pole = mesh(new T.CylinderGeometry(.03, .03, 2.4, 6), M.rail); pole.position.y = 1.2; const top = mesh(new T.ConeGeometry(1.4, .45, 8), lm); top.position.y = 2.5; u.add(pole, top); return u; };
  lg.add(umb(713, 497), umb(789, 497));
  return { group: g, water: wm, setTime: (t) => { wmat.uniforms.t.value = t; }, update: (t) => { wmat.uniforms.t.value = t; } };
}

// ------------------------------------------------------------------ main
export function buildVanta(THREE, opts = {}) {
  T = THREE; const o = Object.assign({ people: 14, cars: true, sign: 'VANTA HOUSE', mood: 'day' }, opts);
  const M = makeMaterials(); const group = new T.Group(); group.name = 'VantaHouse';
  const north = { polygon: PM(NORTH_PX) }, south = { polygon: PM(SOUTH_PX) };
  [north, south].forEach(b => { b.center = centroid(b.polygon); b.bbox = bbox(b.polygon); b.area = Math.abs(area2(b.polygon)); });
  const blocks = { north, south };
  const floors = []; const mkFloor = (name, key, level, yBase, height) => { const g = new T.Group(); g.name = 'floor_' + key; group.add(g); const f = { name, key, level, yBase, height, group: g, index: floors.length }; floors.push(f); return f; };
  mkFloor('Basement', 'B1', -3.3, -3.3, 3.3); mkFloor('Ground', 'G', 0, 0, 4.0);
  for (let k = 1; k <= 11; k++) mkFloor('Level ' + k, String(k), levelOf(k), levelOf(k), 3.3);
  mkFloor('Roof', 'roof', LEVELS.roof, LEVELS.roof, 4.1);
  const bp = buildBasement(M, blocks, floors[0].group);
  buildGround(M, blocks, floors[1].group);
  buildFloorGroups(M, blocks, floors);
  buildRoof(M, blocks, floors[13].group, o.sign);
  const site = buildSite(M, blocks, o); site.setMood(o.mood); group.add(site.group);
  const people = makePeople(T, o.people, defaultPaths()); site.group.add(people.group);
  const cars = o.cars ? makeCars(T) : null; if (cars) site.group.add(cars.group);
  const bb = bbox([...north.polygon, ...south.polygon]);
  const dims = { roofLevel: LEVELS.roof, parapetTop: LEVELS.roof + 1, signTop: LEVELS.roof + 3.9, totalHeight: LEVELS.roof + 3.9, basementLevel: -3.3, floorHeight: 3.3, groundHeight: 4.0, levels: floors.map(f => ({ name: f.name, level: f.level })),
    buildingBBox: { min: bb.min, max: bb.max }, buildingCenter: [(bb.min[0] + bb.max[0]) / 2, (bb.min[1] + bb.max[1]) / 2], plotArea: Math.abs(area2(site.polygon)), plotEdges: { bottom: 71.4, left: 45.9, top: 24.6, road: 59.3 }, px2m: SC, basementPolygon: bp,
    gate: pm(GATE_PX), mapPx: (x, y) => pm([x, y]) };
  const update = (t) => { site.pool.update(t); people.update(t); cars?.update(t); };
  return { group, floors, blocks, site: { ...site, people, cars }, dims, materials: M, update, setMood: (mood) => site.setMood(mood) };
}
// ------------------------------------------------------------------ floor helpers
export function explodeFloors(floors, amount, opts = {}) { floors.forEach((f, i) => { f.group.position.y = (opts.fromGround ? Math.max(0, i - 1) : i) * amount * (opts.k ?? 1); }); }
export function setFloorsVisible(floors, pred) { floors.forEach((f, i) => { f.group.visible = !!pred(f, i); }); }
export const lightingAlias = lighting;
export { lighting as makeLighting };
