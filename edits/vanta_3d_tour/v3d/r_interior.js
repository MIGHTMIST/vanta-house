// r_interior.js - Vanta House interiors laid out from the approved typical floor plan (Tower A, east 2-bed unit, grid E-G / rows 2-3):
// ground-floor entrance lobby + lift hall, lift car, level-6 lift lobby/corridor, one furnished apartment (living/dining/kitchen, hall,
// master bedroom, bathroom glimpse, east balcony).  Lighting: real sun (shadowed) through the openings + an analytic interior
// light model injected into Lambert materials (window "portals", warm lamps, box-room ambient occlusion, room-scoped).
import { RoundedBoxGeometry } from './node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';
import { APT, CORNER, levelOf, canvasTex, rnd, fbm, blobTex, railGlassMaterial, skyEnv, makeShrubs, letterPlane, makePeople, pottedPlant } from './r_vanta3d.js';
let T;
const Y6 = levelOf(APT.level);
export const ROOMS = {   // [x0,x1,y0,y1,z0,z1]
  living: [8.48, 16.58, Y6, Y6 + 2.85, 5.96, 10.7], master: [13.03, 16.58, Y6, Y6 + 2.85, 2.11, 5.81], bath: [11.53, 12.88, Y6, Y6 + 2.6, 2.11, 5.81],
  balcony: [16.78, 18.55, Y6, Y6 + 3.0, 7.3, 10.85], corridor: [-1.0, 8.1, Y6, Y6 + 2.7, 5.9, 7.5],
  lobby: [6.55, 16.6, 0, 3.35, 2.05, 10.7], lifthall: [-.98, 6.55, 0, 3.0, 5.6, 8.0], cab: [-2.8, -1.02, 0, 2.45, 5.62, 7.68],
};
export const LIFT = { x: -1.0, z0: 6.1, z1: 7.2, cabX: [-2.75, -1.15], cabZ: [5.65, 7.65] };

// ------------------------------------------------------------------ textures
const H = (x, y, s) => { let h = (Math.imul(x | 0, 374761393) + Math.imul(y | 0, 668265263) + Math.imul(s | 0, 982451653)) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; };
function pix(g, w, h, f) { const id = g.createImageData(w, h), d = id.data; for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const c = f(x, y), i = (y * w + x) * 4; d[i] = c[0]; d[i + 1] = c[1]; d[i + 2] = c[2]; d[i + 3] = 255; } g.putImageData(id, 0, 0); }
const X = {};
function textures() {
  if (X.ok) return X;
  // 600x600 matt grey porcelain, 3 mm pale joints, faint mottling (texture = 2.4 m)
  X.tile = canvasTex(512, 512, (g, w, h) => pix(g, w, h, (x, y) => { const tx = Math.floor(x / 128), ty = Math.floor(y / 128), v = H(tx, ty, 3) * .05, n = fbm(x / 18, y / 18, 5, 3, 28) * .08, s = fbm(x / 3, y / 3, 9, 2, 170) * .04;
    const j = (x % 128) < 2 || (y % 128) < 2; const b = j ? 208 : 184 * (.95 + v + n + s); return [b, b, b * .995]; }), { rep: [1 / 2.4, 1 / 2.4] });
  // pale travertine 1200x600 for the lobby
  X.trav = canvasTex(512, 512, (g, w, h) => pix(g, w, h, (x, y) => { const r = Math.floor(y / 128), c = Math.floor((x + (r % 2) * 128) / 256); const v = H(c, r, 5), n = fbm(x / 40, y / 6, 7, 4, 13), p = H(x, y, 1) > .993 ? .8 : 1;
    const j = (y % 128) < 2 || ((x + (r % 2) * 128) % 256) < 2; return j ? [176, 164, 150] : [212, 198, 178].map(q => q * (.92 + v * .06 + n * .09) * p); }), { rep: [1 / 2.4, 1 / 2.4] });
  // oak veneer (cathedral grain), used with world UVs (1 m tile)
  X.oak = canvasTex(256, 512, (g, w, h) => pix(g, w, h, (x, y) => { const k = Math.floor(x / 64), gx = x + 18 * Math.sin(y / 70 + k * 2) + 6 * fbm(x / 9, y / 30, k, 2, 0), ring = Math.pow(Math.abs(Math.sin(gx / (6 + k * 2))), 6), n = fbm(x / 3, y / 60, 11 + k, 3, 0);
    return [193, 148, 115].map((q, i) => q * (.9 - ring * .12 + n * .16 + H(k, 0, 2) * .06)); }), { rep: [1, 1] });
  X.oakFloor = canvasTex(512, 512, (g, w, h) => pix(g, w, h, (x, y) => { const b = Math.floor(x / 42.6), o = H(b, 0, 4) * 512, by = Math.floor((y + o) / 340), v = H(b, by, 9), n = fbm(x / 4, (y + o) / 50, b, 3, 0);
    const j = (x % 43) < 1.2 || ((y + o) % 340) < 1.2; return j ? [168, 138, 108] : [214, 184, 146].map(q => q * (.9 + v * .08 + n * .09)); }), { rep: [1 / 1.6, 1 / 1.6] });
  X.whiteTile = canvasTex(256, 256, (g, w, h) => pix(g, w, h, (x, y) => { const j = (x % 32) < 2 || (y % 32) < 2; const v = H(x >> 5, y >> 5, 3) * .03; return j ? [214, 214, 210] : [240, 240, 236].map(q => q * (.98 + v)); }), { rep: [1 / .8, 1 / .8] });
  X.metro = canvasTex(256, 256, (g, w, h) => pix(g, w, h, (x, y) => { const r = Math.floor(y / 32), j = (y % 32) < 2 || ((x + (r % 2) * 32) % 64) < 2; return j ? [205, 205, 200] : [238, 238, 234]; }), { rep: [1 / 1.2, 1 / 1.2] });
  X.linen = canvasTex(256, 256, (g, w, h) => pix(g, w, h, (x, y) => { const n = fbm(x / 30, y / 30, 3, 3, 9) * .06 + ((x + y) % 4 < 2 ? .015 : 0); return [240, 235, 227].map(q => q * (.95 + n)); }), { rep: [1, 1] });
  X.fabric = canvasTex(256, 256, (g, w, h) => pix(g, w, h, (x, y) => { const n = fbm(x / 6, y / 6, 13, 2, 43) * .1 + ((x % 3) === 0 ? .03 : 0); return [255, 255, 255].map(q => q * (.86 + n)); }), { rep: [2, 2], srgb: false });
  X.rug = canvasTex(512, 512, (g, w, h) => { pix(g, w, h, (x, y) => { const n = fbm(x / 5, y / 5, 21, 2, 102) * .08; const bx = Math.min(x, w - x), by = Math.min(y, h - y), border = Math.min(bx, by) < 26 && Math.min(bx, by) > 14;
      const dia = (Math.abs(((x + y) % 128) - 64) < 3 || Math.abs(((x - y + 1024) % 128) - 64) < 3) && Math.min(bx, by) > 40; const c = border || dia ? [169, 98, 63] : [214, 202, 182]; return c.map(q => q * (.93 + n)); }); }, { rep: [1, 1] });
  X.marble = canvasTex(512, 512, (g, w, h) => pix(g, w, h, (x, y) => { const n = fbm(x / 90, y / 90, 3, 5, 6), v = Math.pow(1 - Math.abs(Math.sin((x * .6 + y + n * 260) / 40)), 18); return [232, 230, 236].map((q, i) => q * (1 - v * (.45 - i * .02)) - n * 12); }), { rep: [1 / 1.6, 1 / 1.6] });
  X.slats = canvasTex(256, 64, (g, w, h) => pix(g, w, h, (x, y) => { const gap = (x % 32) > 24; return gap ? [24, 18, 14] : [72, 54, 42].map(q => q * (.85 + fbm(x / 4, y / 20, 5, 2, 0) * .3)); }), { rep: [1 / .6, 1] });
  X.steel = canvasTex(256, 256, (g, w, h) => pix(g, w, h, (x, y) => { const n = fbm(x / 80, y / 1.5, 3, 3, 0) * .12; return [190, 192, 194].map(q => q * (.9 + n)); }), { rep: [1, 1] });
  X.dots = canvasTex(512, 512, (g, w, h) => { pix(g, w, h, (x, y) => { const n = fbm(x / 5, y / 5, 31, 2, 102) * .06; return [244, 241, 236].map(q => q * (.95 + n)); }); g.fillStyle = '#222'; for (let y = 24; y < h; y += 52) for (let x = 24 + ((y / 52) % 2) * 26; x < w; x += 52) g.fillRect(x - 7, y - 7, 14, 14); }, { rep: [1, 1] });
  X.sandTile = canvasTex(256, 256, (g, w, h) => pix(g, w, h, (x, y) => { const j = (x % 128) < 2 || (y % 128) < 2; const v = H(x >> 7, y >> 7, 9) * .04; return j ? [206, 190, 166] : [229, 214, 186].map(q => q * (.97 + v + fbm(x / 30, y / 30, 3, 3, 8) * .04)); }), { rep: [1 / 1.2, 1 / 1.2] });
  X.ok = true; return X;
}

// ------------------------------------------------------------------ interior light model (injected into Lambert/Phong)
const NR = 12, NP = 10, NL = 48;
export const IL = {
  uRMin: { value: [] }, uRMax: { value: [] }, uRCnt: { value: [] }, uNR: { value: 0 },
  uPC: { value: [] }, uPN: { value: [] }, uPS: { value: [] }, uPCol: { value: [] }, uNP: { value: 0 },
  uLP: { value: [] }, uLD: { value: [] }, uLC: { value: [] }, uNL: { value: 0 }, uDay: { value: 1 },
};
function THREE_V4() { return { x: 0, y: 0, z: 0, w: 0, isVector4: true, toArray(a, o) { a[o] = this.x; a[o + 1] = this.y; a[o + 2] = this.z; a[o + 3] = this.w; return a; } }; }
const GLSL_PARS = `
#define NR ${NR}
#define NP ${NP}
#define NL ${NL}
uniform vec4 uRMin[NR]; uniform vec4 uRMax[NR]; uniform float uRCnt[NR]; uniform int uNR;
uniform vec4 uPC[NP]; uniform vec3 uPN[NP]; uniform vec2 uPS[NP]; uniform vec3 uPCol[NP]; uniform int uNP;
uniform vec4 uLP[NL]; uniform vec3 uLD[NL]; uniform vec3 uLC[NL]; uniform int uNL; uniform float uDay;
varying vec3 vIW;`;
const GLSL_LIGHT = `
{ vec3 wN = inverseTransformDirection( normal, viewMatrix ); vec3 P = vIW; float ao = 1.; int room = -1; float amb = .35;
  for (int i = 0; i < NR; i++) { if (i >= uNR) break; vec3 a = uRMin[i].xyz, b = uRMax[i].xyz;
    if (room < 0 && all(greaterThan(P, a - .07)) && all(lessThan(P, b + .07))) { room = i; amb = uRMin[i].w;
      vec3 d0 = max(P - a, 0.), d1 = max(b - P, 0.); vec3 wa = 1. - abs(wN);
      ao *= 1. - .42 * wa.x * (1. - smoothstep(0., .5, d0.x)); ao *= 1. - .42 * wa.x * (1. - smoothstep(0., .5, d1.x));
      ao *= 1. - .42 * wa.z * (1. - smoothstep(0., .5, d0.z)); ao *= 1. - .42 * wa.z * (1. - smoothstep(0., .5, d1.z));
      ao *= 1. - .30 * wa.y * (1. - smoothstep(0., .35, d0.y)); ao *= 1. - .36 * wa.y * (1. - smoothstep(0., .5, d1.y)); } }
  vec3 E = vec3(0.);
  int pr = room >= 0 ? int(uRMax[room].w + .5) : 0; int p0 = pr / 4096, pn = (pr / 64) % 64;
  int lr = room >= 0 ? int(uRCnt[room] + .5) : 0; int lstart = lr / 64, lcount = lr % 64;
  for (int k = 0; k < NP; k++) { if (room < 0 || k >= pn) break; int i = p0 + k;
    vec3 d = uPC[i].xyz - P; float d2 = dot(d, d); vec3 l = d * inversesqrt(d2); float A = 4. * uPS[i].x * uPS[i].y;
    float cr = max(dot(-l, uPN[i]) * .8 + .2, 0.), cs = max(dot(wN, l) * .7 + .3, 0.);
    E += uPCol[i] * uDay * A * cr * cs / (d2 + A * .5 + .5); }
  for (int k = 0; k < NL; k++) { if (room < 0 || k >= lcount) break; int i = lstart + k;
    vec3 d = uLP[i].xyz - P; float d2 = dot(d, d); vec3 l = d * inversesqrt(d2);
    float sp = dot(uLD[i], uLD[i]) > .5 ? pow(max(dot(-l, uLD[i]), 0.), 2.5) : 1.;
    E += uLC[i] * sp * max(dot(wN, l) * .8 + .2, 0.) / (d2 + .2); }
  if (room >= 0) irradiance = (irradiance * amb + E) * ao; }
`;
let SHARED = null;
export function interiorize(m) {
  if (m.userData.interior) return m; m.userData.interior = true;
  m.onBeforeCompile = (sh) => {
    if (!SHARED) SHARED = IL; Object.assign(sh.uniforms, SHARED);
    sh.vertexShader = 'varying vec3 vIW;\n' + sh.vertexShader.replace('#include <project_vertex>', `#include <project_vertex>
      { vec4 iw = vec4( transformed, 1.0 );
      #ifdef USE_INSTANCING
        iw = instanceMatrix * iw;
      #endif
      vIW = ( modelMatrix * iw ).xyz; }`);
    sh.fragmentShader = GLSL_PARS + '\n' + sh.fragmentShader.replace('#include <lights_fragment_end>', GLSL_LIGHT + '\n#include <lights_fragment_end>');
  };
  m.customProgramCacheKey = () => 'vanta_interior_' + m.type + (m.map ? 'm' : '') + (m.vertexColors ? 'v' : '') + (m.alphaTest ? 'a' : '');
  return m;
}
// light set-up helpers
export function setLights(rooms, portals, lamps) {
  const V3 = (a) => new T.Vector3(...a), V4 = (a, w) => new T.Vector4(a[0], a[1], a[2], w);
  portals.sort((a, b) => a.room - b.room); lamps.sort((a, b) => a.room - b.room);
  const range = (arr, r) => { let s0 = arr.findIndex(x => x.room === r); const n = arr.filter(x => x.room === r).length; return [s0 < 0 ? 0 : s0, n]; };
  IL.uRMin.value = []; IL.uRMax.value = []; IL.uRCnt.value = []; rooms.forEach(([b, amb], ri) => { const [p0, pn] = range(portals, ri), [l0, ln] = range(lamps, ri); IL.uRMin.value.push(new T.Vector4(b[0], b[2], b[4], amb)); IL.uRMax.value.push(new T.Vector4(b[1], b[3], b[5], p0 * 4096 + pn * 64)); IL.uRCnt.value.push(l0 * 64 + ln); });
  while (IL.uRMin.value.length < NR) { IL.uRMin.value.push(new T.Vector4(0, -999, 0, 0)); IL.uRMax.value.push(new T.Vector4(0, -998, 0, 0)); IL.uRCnt.value.push(0); } IL.uNR.value = rooms.length;
  ['uPC', 'uPN', 'uPS', 'uPCol'].forEach(k => IL[k].value = []);
  portals.forEach(p => { IL.uPC.value.push(V4(p.c, p.room)); IL.uPN.value.push(V3(p.n)); IL.uPS.value.push(new T.Vector2(p.s[0], p.s[1])); IL.uPCol.value.push(new T.Color(p.col || '#fbf7f0').multiplyScalar(p.k)); });
  while (IL.uPC.value.length < NP) { IL.uPC.value.push(new T.Vector4(0, 0, 0, -9)); IL.uPN.value.push(new T.Vector3()); IL.uPS.value.push(new T.Vector2()); IL.uPCol.value.push(new T.Color(0)); } IL.uNP.value = portals.length;
  ['uLP', 'uLD', 'uLC'].forEach(k => IL[k].value = []);
  lamps.forEach(l => { IL.uLP.value.push(V4(l.p, l.room)); IL.uLD.value.push(V3(l.d || [0, 0, 0])); IL.uLC.value.push(new T.Color(l.col || '#ffd9a8').multiplyScalar(l.k)); l.uni = IL.uLC.value[IL.uLC.value.length - 1]; l.base = l.uni.clone(); });
  while (IL.uLP.value.length < NL) { IL.uLP.value.push(new T.Vector4(0, 0, 0, -9)); IL.uLD.value.push(new T.Vector3()); IL.uLC.value.push(new T.Color(0)); } IL.uNL.value = lamps.length;
  if (lamps.length > NL || portals.length > NP || rooms.length > NR) console.warn('interior lights over limit', rooms.length, portals.length, lamps.length);
  const snap = {}; ['uRMin', 'uRMax', 'uRCnt', 'uNR', 'uPC', 'uPN', 'uPS', 'uPCol', 'uNP', 'uLP', 'uLD', 'uLC', 'uNL'].forEach(k => snap[k] = IL[k].value); return snap;
}
export function useLights(snap) { for (const k in snap) IL[k].value = snap[k]; }

// ------------------------------------------------------------------ geometry helpers
const L = (col, o = {}) => interiorize(new T.MeshLambertMaterial({ color: col, ...o }));
const PH = (col, o = {}) => interiorize(new T.MeshPhongMaterial({ color: col, shininess: 40, specular: '#2a2a2a', ...o }));
function wuv(g, cx, cy, cz) { const p = g.attributes.position, n = g.attributes.normal, uv = g.attributes.uv; if (!uv) return g;
  for (let i = 0; i < p.count; i++) { const x = p.getX(i) + cx, y = p.getY(i) + cy, z = p.getZ(i) + cz, ax = Math.abs(n.getX(i)), ay = Math.abs(n.getY(i));
    if (ay > .5) uv.setXY(i, x, z); else if (ax > .5) uv.setXY(i, z, y); else uv.setXY(i, x, y); } uv.needsUpdate = true; return g; }
function B(grp, m, x0, x1, y0, y1, z0, z1, o = {}) { const w = x1 - x0, h = y1 - y0, d = z1 - z0; if (w <= 1e-3 || h <= 1e-3 || d <= 1e-3) return null;
  const g = o.r ? new RoundedBoxGeometry(w, h, d, o.seg || 2, Math.min(o.r, w / 2 - 1e-3, h / 2 - 1e-3, d / 2 - 1e-3)) : new T.BoxGeometry(w, h, d);
  if (o.wuv !== false) wuv(g, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
  const ms = new T.Mesh(g, m); ms.position.set((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); ms.castShadow = o.cast !== false; ms.receiveShadow = true; if (o.name) ms.name = o.name; grp.add(ms); return ms; }
// wall along x (normal z) from x0..x1 at z0..z1 with openings [{a,b,y0,y1}] (absolute x, absolute y)
function wallX(grp, m, x0, x1, y0, y1, z0, z1, ops = []) { let c = x0; ops.slice().sort((p, q) => p.a - q.a).forEach(o => { B(grp, m, c, o.a, y0, y1, z0, z1); B(grp, m, o.a, o.b, y0, o.y0, z0, z1); B(grp, m, o.a, o.b, o.y1, y1, z0, z1); c = o.b; }); B(grp, m, c, x1, y0, y1, z0, z1); }
function wallZ(grp, m, x0, x1, y0, y1, z0, z1, ops = []) { let c = z0; ops.slice().sort((p, q) => p.a - q.a).forEach(o => { B(grp, m, x0, x1, y0, y1, c, o.a); B(grp, m, x0, x1, y0, o.y0, o.a, o.b); B(grp, m, x0, x1, o.y1, y1, o.a, o.b); c = o.b; }); B(grp, m, x0, x1, y0, y1, c, z1); }
// horizontal plane (floor faces up / ceiling faces down)
function plane(grp, m, x0, x1, z0, z1, y, down = false) { const g = new T.PlaneGeometry(x1 - x0, z1 - z0); g.rotateX(down ? Math.PI / 2 : -Math.PI / 2); g.translate((x0 + x1) / 2, y, (z0 + z1) / 2);
  const uv = g.attributes.uv, p = g.attributes.position; for (let i = 0; i < p.count; i++) uv.setXY(i, p.getX(i), p.getZ(i)); const ms = new T.Mesh(g, m); ms.receiveShadow = true; grp.add(ms); return ms; }
let CT; function contactTex() { if (CT) return CT; CT = canvasTex(128, 128, (g) => { const r = g.createRadialGradient(64, 64, 10, 64, 64, 64); r.addColorStop(0, 'rgb(150,150,150)'); r.addColorStop(.55, 'rgb(205,205,205)'); r.addColorStop(1, 'rgb(255,255,255)'); g.fillStyle = r; g.fillRect(0, 0, 128, 128); }, { srgb: false }); CT.wrapS = CT.wrapT = T.ClampToEdgeWrapping; return CT; }
// soft contact shadow under furniture (multiply)
function contact(grp, x, z, w, d, y, k = 1) { const m = new T.MeshBasicMaterial({ map: contactTex(), blending: T.MultiplyBlending, transparent: true, depthWrite: false, toneMapped: false, polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4, opacity: 1 });
  if (k !== 1) m.color.setScalar(1).lerp(new T.Color(1, 1, 1), 0); const g = new T.PlaneGeometry(w * 1.35 + .25, d * 1.35 + .25); g.rotateX(-Math.PI / 2); const ms = new T.Mesh(g, m); ms.position.set(x, y + .004, z); ms.renderOrder = 1; grp.add(ms); return ms; }
function cyl(grp, m, r0, r1, h, x, y, z, seg = 16) { const ms = new T.Mesh(new T.CylinderGeometry(r0, r1, h, seg), m); ms.position.set(x, y + h / 2, z); ms.castShadow = true; ms.receiveShadow = true; grp.add(ms); return ms; }
// a potted plant: grey/terracotta pot + leaf-card crown
function plant(grp, x, y, z, h, pot = '#6E6E70', seed = 1) { const pr = Math.max(.14, h * .16); cyl(grp, L(pot), pr, pr * .78, pr * 2.1, x, y, z, 14);
  const sh = pottedPlant(T, x, y + pr * 2.0, z, h, { seed: 50 + seed, n: h < .6 ? 9 : 13, color: ['#a9be8c', '#9fb784', '#b4c493'][seed % 3] }); interiorize(sh.material); grp.add(sh); return sh; }
// emissive (unlit-ish) material for lamp shades / LED strips
const EM = (col, k = 1) => new T.MeshBasicMaterial({ color: new T.Color(col).multiplyScalar(k), toneMapped: true });

// ------------------------------------------------------------------ lift (landing doors per floor + moving car)
function liftDoors(grp, y, steelM, frameM) {
  const g = new T.Group(); grp.add(g); const x = LIFT.x, zc = (LIFT.z0 + LIFT.z1) / 2, hw = (LIFT.z1 - LIFT.z0) / 2;
  const pL = B(g, steelM, x - .1, x - .05, y + .005, y + 2.1, zc - hw, zc, { wuv: false }), pR = B(g, steelM, x - .1, x - .05, y + .005, y + 2.1, zc, zc + hw, { wuv: false });
  // portal trim + indicator
  B(g, frameM, x - .02, x + .03, y, y + 2.2, LIFT.z0 - .12, LIFT.z0); B(g, frameM, x - .02, x + .03, y, y + 2.2, LIFT.z1, LIFT.z1 + .12); B(g, frameM, x - .02, x + .03, y + 2.1, y + 2.22, LIFT.z0 - .12, LIFT.z1 + .12);
  const cv = document.createElement('canvas'); cv.width = 128; cv.height = 64; const tex = new T.CanvasTexture(cv); tex.colorSpace = T.SRGBColorSpace;
  const disp = new T.Mesh(new T.PlaneGeometry(.36, .18), new T.MeshBasicMaterial({ map: tex })); disp.rotation.y = Math.PI / 2; disp.position.set(x + .035, y + 2.42, zc); g.add(disp);
  B(g, frameM, x + .005, x + .03, y + 2.31, y + 2.53, zc - .22, zc + .22);
  const btn = B(g, frameM, x + .005, x + .035, y + 1.0, y + 1.32, LIFT.z1 + .3, LIFT.z1 + .42); const bl = new T.Mesh(new T.CircleGeometry(.025, 12), new T.MeshBasicMaterial({ color: '#ffe3b0' })); bl.rotation.y = Math.PI / 2; bl.position.set(x + .037, y + 1.18, LIFT.z1 + .36); g.add(bl);
  let last = '';
  return { set(f, floor, dir) { f = Math.max(0, Math.min(1, f)); pL.position.z = zc - hw / 2 - f * hw * .98; pR.position.z = zc + hw / 2 + f * hw * .98; const key = floor + '|' + dir; if (key === last) return; last = key;
    const c = cv.getContext('2d'); c.fillStyle = '#0b0b0c'; c.fillRect(0, 0, 128, 64); c.fillStyle = '#F2D7A6'; c.font = '600 40px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(String(floor), 76, 34);
    if (dir) { c.beginPath(); const yy = dir > 0 ? 18 : 46, s = dir > 0 ? 1 : -1; c.moveTo(28, yy); c.lineTo(18, yy + 14 * s); c.lineTo(38, yy + 14 * s); c.fill(); } tex.needsUpdate = true; } };
}
function liftCar(grp, M) {
  const g = new T.Group(); grp.add(g); const [x0, x1] = LIFT.cabX, [z0, z1] = LIFT.cabZ, zc = (LIFT.z0 + LIFT.z1) / 2, hw = (LIFT.z1 - LIFT.z0) / 2;
  B(g, M.granite, x0, x1, -.04, 0, z0, z1); B(g, M.cabWall, x0 - .04, x0, 0, 2.45, z0, z1); // back wall
  B(g, M.mirror, x0 + .005, x0 + .02, .9, 2.2, z0 + .25, z1 - .25); for (const z of [z0 + .005, z1 - .02]) B(g, M.mirror, x0 + .3, x1 - .3, 1.0, 2.15, z, z + .015, { wuv: false });
  B(g, M.cabWall, x0, x1, 0, 2.45, z0 - .04, z0); B(g, M.cabWall, x0, x1, 0, 2.45, z1, z1 + .04);
  B(g, M.cabCeil, x0, x1, 2.45, 2.5, z0, z1); B(g, EM('#fff4e2', 1.5), x0 + .25, x1 - .25, 2.44, 2.445, z0 + .3, z1 - .3, { cast: false, wuv: false });
  wallZ(g, M.cabWall, x1, x1 + .04, 0, 2.45, z0, z1, [{ a: LIFT.z0, b: LIFT.z1, y0: 0, y1: 2.1 }]);
  for (const z of [z0 + .06, z1 - .06]) B(g, M.chrome, x0 + .25, x1 - .2, .92, .96, z - .02, z + .02, { wuv: false });
  B(g, M.chrome, x0 + .06, x0 + .1, .92, .96, z0 + .2, z1 - .2, { wuv: false });
  const pL = B(g, M.steel, x1 + .045, x1 + .075, .005, 2.1, zc - hw, zc, { wuv: false }), pR = B(g, M.steel, x1 + .045, x1 + .075, .005, 2.1, zc, zc + hw, { wuv: false });
  // inner display above the door
  const cv = document.createElement('canvas'); cv.width = 128; cv.height = 64; const tex = new T.CanvasTexture(cv); tex.colorSpace = T.SRGBColorSpace;
  const disp = new T.Mesh(new T.PlaneGeometry(.3, .15), new T.MeshBasicMaterial({ map: tex })); disp.rotation.y = -Math.PI / 2; disp.position.set(x1 - .005, 2.27, zc); g.add(disp);
  // button panel
  B(g, M.chrome, x1 - .02, x1, .9, 1.45, z1 - .3, z1 - .12, { wuv: false });
  let last = '';
  return { group: g, set(y, f, floor, dir) { g.position.y = y; f = Math.max(0, Math.min(1, f)); pL.position.z = zc - hw / 2 - f * hw * .98; pR.position.z = zc + hw / 2 + f * hw * .98;
    const key = floor + '|' + dir; if (key === last) return; last = key; const c = cv.getContext('2d'); c.fillStyle = '#0b0b0c'; c.fillRect(0, 0, 128, 64); c.fillStyle = '#F2D7A6'; c.font = '600 40px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(String(floor), 76, 34);
    if (dir) { c.beginPath(); const yy = dir > 0 ? 18 : 46, s = dir > 0 ? 1 : -1; c.moveTo(28, yy); c.lineTo(18, yy + 14 * s); c.lineTo(38, yy + 14 * s); c.fill(); } tex.needsUpdate = true; } };
}
// abstract earthy print for frames (no text)
function printTex(seed, pal) { return canvasTex(256, 320, (g, w, h) => { const R = rnd(seed); g.fillStyle = pal[0]; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 5; i++) { g.fillStyle = pal[1 + (i % (pal.length - 1))]; g.globalAlpha = .85; g.beginPath(); g.ellipse(w * (.2 + R() * .6), h * (.2 + R() * .6), w * (.12 + R() * .25), h * (.08 + R() * .2), R() * 3, 0, 6.283); g.fill(); }
  g.globalAlpha = 1; g.strokeStyle = 'rgba(30,25,20,.6)'; g.lineWidth = 3; g.beginPath(); g.moveTo(w * .1, h * .8); g.bezierCurveTo(w * .4, h * .5, w * .6, h * .9, w * .9, h * .3); g.stroke(); }, { rep: [1, 1] }); }
function frameArt(grp, axis, x, y, z, w, h, tex, frameM) { const g = new T.Group(); grp.add(g); g.position.set(x, y, z); if (axis === 'x+') g.rotation.y = Math.PI / 2; if (axis === 'x-') g.rotation.y = -Math.PI / 2; if (axis === 'z-') g.rotation.y = Math.PI;
  B(g, frameM, -w / 2, w / 2, -h / 2, h / 2, 0, .035, { wuv: false }); const p = new T.Mesh(new T.PlaneGeometry(w - .12, h - .12), interiorize(new T.MeshLambertMaterial({ map: tex }))); p.position.z = .036; g.add(p); return g; }

// ------------------------------------------------------------------ main build
export function buildInteriors(THREE, vanta, o = {}) {
  T = THREE; textures(); const root = new T.Group(); root.name = 'interiors';
  const M = {
    wall: L('#EDE8DF'), wallWarm: L('#EDE8DF'), lobbyWall: L('#E6E0D5'), ceil: L('#F4F0EA'), tile: L('#ffffff', { map: X.tile }), trav: L('#ffffff', { map: X.trav }),
    oak: L('#ffffff', { map: X.oak }), oakDark: L('#7a5237', { map: X.oak }), walnut: L('#6a4a33', { map: X.oak }), oakFloor: L('#ffffff', { map: X.oakFloor }), oakLight: L('#efdcc0', { map: X.oak }), cream: L('#EFE9DF'), beige: L('#CDB38E', { map: X.fabric }), greyThrow: L('#9E9C98', { map: X.fabric }), brownCushion: L('#7A5A45', { map: X.fabric }), headboard: L('#D8D0C4', { map: X.fabric }), shadowLine: L('#9c958a'),
    white: L('#F1EEE8'), sandTile: L('#ffffff', { map: X.sandTile }), tileOut: new T.MeshLambertMaterial({ map: X.tile, color: '#d8d6d2' }), cream2: L('#E8DCC8'), whiteTile: L('#ffffff', { map: X.whiteTile }), metro: L('#ffffff', { map: X.metro }), worktop: PH('#F0EFEC', { shininess: 30 }),
    black: PH('#1E1E20', { shininess: 30 }), blackGlass: PH('#0e0f10', { shininess: 90, specular: '#666666', envMap: skyEnv(), reflectivity: .25, combine: T.MixOperation }),
    steel: PH('#c9cbcd', { map: X.steel, shininess: 60, specular: '#888888' }), chrome: PH('#d9dbdd', { shininess: 90, specular: '#cccccc' }),
    granite: PH('#2a2a2c', { shininess: 50 }), mirror: PH('#3a3632', { shininess: 120, specular: '#777777' }),
    doorGrey: L('#4a4a4c'), cabWall: PH('#d6cbbb', { map: X.steel, shininess: 50, specular: '#555555' }), cabCeil: L('#e8e6e2'),
    sofa: L('#9A9897', { map: X.fabric }), linen: L('#ffffff', { map: X.linen }), boucle: L('#EEE7DC', { map: X.fabric }), rust: L('#C57A22', { map: X.fabric }), olive: L('#8E9A4A', { map: X.fabric }), terra: L('#B5694A', { map: X.fabric }),
    sage: L('#8FA889'), stone: L('#CDCAD1'), marble: PH('#ffffff', { map: X.marble, shininess: 40 }), slats: L('#ffffff', { map: X.slats }), rug: L('#ffffff', { map: X.rug }), dotRug: L('#ffffff', { map: X.dots }), sand: L('#C8B79A', { map: X.fabric }),
    pot: L('#6E6E70'), terracotta: L('#A9623F'), book: L('#ffffff', { vertexColors: true }), shade: L('#E8DFCF', { side: T.DoubleSide }), brass: PH('#B98F4E', { shininess: 70, specular: '#7a6030' }),
    glass: railGlassMaterial({ alpha: .05, tint: '#9fb4b0' }), frame: PH('#1E1E20', { shininess: 30 }),
  };
  const W = { lobby: new T.Group(), corridor: new T.Group(), apt: new T.Group(), cab: new T.Group(), balcony: new T.Group() };
  Object.entries(W).forEach(([k, g]) => { g.name = 'int_' + k; root.add(g); });
  const lamps = [], portals = [];
  const R = rnd(99);
  // ============================================================== GROUND: lobby + lift hall
  { const g = W.lobby, [x0, x1, , , z0, z1] = ROOMS.lobby, Hc = 3.35, yf = .05;
    plane(g, M.trav, x0, x1, z0, z1, yf); plane(g, M.trav, -1.0, x0, 5.6, 8.0, yf); plane(g, M.ceil, x0, x1, z0, z1, Hc, true); plane(g, M.ceil, -1.0, x0, 5.6, 8.0, 3.0, true);
    // north + east glazing: thin black mullions, transoms, low-iron panes; sliding entrance x 10.9..12.9
    const mull = (x, z, alongX) => alongX ? B(g, M.frame, x - .03, x + .03, yf, Hc, z - .05, z + .05) : B(g, M.frame, x - .05, x + .05, yf, Hc, z - .03, z + .03);
    for (let x = x0; x <= x1 + .01; x += (x1 - x0) / 8) if (x < 10.85 || x > 12.95) mull(x, z0, true);
    mull(10.88, z0, true); mull(12.92, z0, true); for (let z = z0; z <= z1 + .01; z += (z1 - z0) / 7) mull(x1, z, false);
    B(g, M.frame, x0, x1, 3.0, Hc, z0 - .05, z0 + .05); B(g, M.frame, x1 - .05, x1 + .05, 3.0, Hc, z0, z1); B(g, M.frame, x0, x1, yf, yf + .06, z0 - .05, z0 + .05); B(g, M.frame, x1 - .05, x1 + .05, yf, yf + .06, z0, z1);
    const pane = (a, b, z) => { const p = new T.Mesh(new T.PlaneGeometry(b - a, 2.95), M.glass); p.position.set((a + b) / 2, yf + 1.5, z); p.renderOrder = 3; g.add(p); };
    pane(x0, 10.88, z0); pane(12.92, x1, z0); { const p = new T.Mesh(new T.PlaneGeometry(z1 - z0, 2.95), M.glass); p.rotation.y = Math.PI / 2; p.position.set(x1, yf + 1.5, (z0 + z1) / 2); p.renderOrder = 3; g.add(p); }
    const leaf = (s) => { const lg = new T.Group(); g.add(lg); B(lg, M.frame, -.5, .5, yf, yf + 3.0, -.03, .03, { wuv: false }).visible = false; const fr = (a, b, c, d) => B(lg, M.frame, a, b, c, d, -.025, .025, { wuv: false });
      fr(-.5, -.45, yf, yf + 2.95); fr(.45, .5, yf, yf + 2.95); fr(-.5, .5, yf, yf + .08); fr(-.5, .5, yf + 2.87, yf + 2.95); fr(-.47, -.4, yf + 1.0, yf + 1.15); const p = new T.Mesh(new T.PlaneGeometry(.9, 2.8), M.glass); p.position.y = yf + 1.5; p.renderOrder = 3; lg.add(p); lg.userData.s = s; return lg; };
    const dL = leaf(-1), dR = leaf(1);
    // walls: south (feature), west (with lift-hall opening), lift hall walls
    wallX(g, M.lobbyWall, x0 - .2, x1, yf, Hc, z1, z1 + .2); wallZ(g, M.lobbyWall, x0 - .2, x0, yf, Hc, z0, z1, [{ a: 5.6, b: 8.0, y0: yf, y1: 3.0 }]);
    wallX(g, M.lobbyWall, -1.0, x0 - .2, yf, 3.0, 5.4, 5.6); wallX(g, M.oak, -1.0, x0 - .2, yf, 3.0, 8.0, 8.2); B(g, M.lobbyWall, -1.0, x0 - .2, 3.0, 3.35, 5.4, 8.2);
    wallZ(g, M.lobbyWall, -1.15, -1.0, yf, 3.0, 5.6, 8.0, [{ a: LIFT.z0, b: LIFT.z1, y0: yf, y1: yf + 2.1 }]);
    // feature wall: dark timber slats + bronze lettering, grazed by warm light
    B(g, M.slats, 9.4, 15.6, yf, Hc, z1 - .06, z1, { cast: false }); B(g, M.brass, 9.4, 15.6, 2.45, 2.47, z1 - .1, z1 - .06);
    const lt = letterPlane('Vanta House', 3.2, .5, { color: '#C9A46A', glow: .25, metal: .6, rough: .35 }); lt.rotation.y = Math.PI; lt.position.set(12.5, 2.05, z1 - .065); interiorize(lt.material); g.add(lt);
    // reception desk: oak body (rounded), travertine top, inner counter, monitor
    B(g, M.oak, 11.2, 14.4, yf, yf + 1.02, 8.95, 9.65, { r: .06 }); B(g, M.marble, 11.15, 14.45, yf + 1.02, yf + 1.07, 8.9, 9.7, { r: .015 }); B(g, M.black, 11.2, 14.4, yf, yf + .08, 8.95, 9.62);
    B(g, M.white, 11.3, 14.3, yf, yf + .74, 9.65, 10.1); B(g, M.black, 12.4, 12.95, yf + .78, yf + 1.12, 9.85, 9.88); contact(g, 12.8, 9.4, 3.3, 1.0, yf);
    const vase = cyl(g, M.terracotta, .07, .1, .28, 11.6, yf + 1.07, 9.3); plant(g, 11.6, yf + 1.2, 9.3, .45, '#A9623F', 3);
    // lounge group by the east glazing
    B(g, M.rug, 13.3, 16.1, yf, yf + .012, 3.0, 6.3, { cast: false });
    const chair = (x, z, a, m) => { const c = new T.Group(); c.position.set(x, yf, z); c.rotation.y = a; g.add(c); B(c, m, -.42, .42, .0, .42, -.4, .4, { r: .14, seg: 3, wuv: false }); B(c, m, -.42, .42, .3, .82, -.42, -.18, { r: .12, seg: 3, wuv: false }); B(c, m, -.44, -.26, .3, .64, -.4, .35, { r: .08, wuv: false }); B(c, m, .26, .44, .3, .64, -.4, .35, { r: .08, wuv: false }); contact(g, x, z, .9, .9, yf); };
    chair(14.0, 4.0, 2.3, M.boucle); chair(15.6, 5.6, -2.6, M.boucle); chair(14.0, 5.7, .9, M.boucle);
    cyl(g, M.marble, .42, .42, .04, 14.9, yf + .38, 4.75, 28); cyl(g, M.black, .08, .12, .38, 14.9, yf, 4.75, 12); contact(g, 14.9, 4.75, .9, .9, yf);
    cyl(g, M.rust, .25, .25, .4, 15.7, yf, 3.6, 18);
    plant(g, 16.15, yf, 2.55, 1.9, '#5f5f61', 1); plant(g, 7.1, yf, 2.6, 1.6, '#A9623F', 2); plant(g, 7.1, yf, 10.1, 2.0, '#5f5f61', 4); plant(g, 16.1, yf, 9.9, 1.4, '#A9623F', 5);
    // west-wall art + bench
    frameArt(g, 'x+', x0 + .01, 1.65, 3.7, 1.5, 1.05, printTex(7, ['#E9E1D3', '#B5694A', '#6E8A7A', '#2B2D31', '#C9A46A']), M.black);
    B(g, M.oak, x0, x0 + .45, yf, yf + .44, 8.4, 10.2, { r: .03 }); contact(g, x0 + .22, 9.3, .45, 1.8, yf);
    // chandelier (capiz-like disc) + downlight discs + light slot
    const ch = cyl(g, EM('#fff1d8', 1.25), .55, .55, .06, 14.9, 2.55, 4.75, 32); cyl(g, M.brass, .01, .01, .74, 14.9, 2.61, 4.75, 6);
    for (const [x, z] of [[8.6, 4.0], [11.9, 4.0], [8.6, 7.6], [11.9, 6.5], [10.5, 9.9], [14.5, 9.9], [1.0, 6.8], [3.2, 6.8], [5.4, 6.8]]) { const d = new T.Mesh(new T.CircleGeometry(.07, 14), EM('#fff4e0', 2.2)); d.rotation.x = Math.PI / 2; d.position.set(x, x < 6.5 ? 2.995 : Hc - .005, z); g.add(d); }
    lamps.push({ p: [8.6, 3.3, 4.0], d: [0, -1, 0], k: 1.1, room: 1 }, { p: [11.9, 3.3, 4.0], d: [0, -1, 0], k: 1.1, room: 1 }, { p: [8.6, 3.3, 7.6], d: [0, -1, 0], k: 1.1, room: 1 }, { p: [11.9, 3.3, 6.5], d: [0, -1, 0], k: 1.1, room: 1 },
      { p: [10.5, 3.3, 10.2], d: [0, -1, 0], k: 1.6, room: 1 }, { p: [14.5, 3.3, 10.2], d: [0, -1, 0], k: 1.6, room: 1 }, { p: [14.9, 2.45, 4.75], k: 1.0, room: 1 }, { p: [12.8, .35, 8.7], k: .35, room: 1 },
      { p: [1.0, 2.95, 6.8], d: [0, -1, 0], k: 2.2, room: 2 }, { p: [3.2, 2.95, 6.8], d: [0, -1, 0], k: 2.2, room: 2 }, { p: [5.4, 2.95, 6.8], d: [0, -1, 0], k: 2.2, room: 2 }, { p: [3.2, 1.6, 6.8], k: .9, room: 2 }, { p: [-.3, 1.8, 6.8], k: .6, room: 2 });
    portals.push({ c: [11.6, 1.6, z0], n: [0, 0, 1], s: [5.0, 1.5], k: 2.6, room: 1 }, { c: [x1, 1.6, 6.4], n: [-1, 0, 0], s: [4.3, 1.5], k: 2.8, room: 1 }, { c: [x0, 1.5, 6.8], n: [-1, 0, 0], s: [1.2, 1.5], k: .5, room: 2 });
    W.lobbyDoors = { set(f) { f = Math.max(0, Math.min(1, f)); dL.position.set(11.4 - f * .98, 0, z0 + .07); dR.position.set(12.4 + f * .98, 0, z0 + .07); } }; W.lobbyDoors.set(0);
  }
  // lift landing doors (G and L6) + car
  const steelL = M.steel, trimM = M.chrome;
  const doorsG = liftDoors(W.lobby, .05, steelL, trimM), doors6 = liftDoors(W.corridor, Y6 + .02, steelL, trimM);
  const car = liftCar(W.cab, M);
  // ============================================================== LEVEL 6: corridor
  { const g = W.corridor, [x0, x1, y0, y1, z0, z1] = ROOMS.corridor, yf = y0 + .02;
    plane(g, M.tile, x0, x1, z0, z1, yf); plane(g, M.ceil, x0, x1, z0, z1, y1, true);
    wallX(g, M.wall, x0, x1, y0, y1, z0 - .15, z0, [{ a: 1.4, b: 2.3, y0: yf, y1: yf + 2.1 }]); wallX(g, M.oak, x0, x1, y0, y1, z1, z1 + .15, [{ a: 3.3, b: 4.2, y0: yf, y1: yf + 2.1 }]);
    wallZ(g, M.wall, x0 - .15, x0, y0, y1, z0, z1, [{ a: LIFT.z0, b: LIFT.z1, y0: yf, y1: yf + 2.1 }]);
    B(g, M.oak, 1.4, 2.3, yf, yf + 2.1, z0 - .1, z0 - .06); B(g, M.oak, 3.3, 4.2, yf, yf + 2.1, z1 + .06, z1 + .1);
    for (const [x, z, s] of [[2.2, z0 - .05, 1], [3.4, z1 + .05, -1]]) B(g, M.black, x - .03, x + .03, yf + 1.0, yf + 1.03, z - .04 * s, z, { wuv: false });
    B(g, M.black, x0, x1, yf, yf + .07, z0, z0 + .012); for (let x = .4; x < 7.8; x += 1.9) { const d = new T.Mesh(new T.CircleGeometry(.06, 14), EM('#fff4e0', 2.2)); d.rotation.x = Math.PI / 2; d.position.set(x, y1 - .005, 6.7); g.add(d); lamps.push({ p: [x, y1 - .05, 6.7], d: [0, -1, 0], k: 1.9, room: 3 }, { p: [x, y0 + 1.5, 6.7], k: .45, room: 3 }); }
    frameArt(g, 'z+', 5.6, yf + 1.55, z0 + .01, .8, 1.0, printTex(17, ['#E2DACB', '#6E8A7A', '#B5694A', '#2B2D31']), M.black);
    plant(g, 7.55, yf, 6.0, 1.2, '#5f5f61', 6);
  }
  // ============================================================== LEVEL 6: apartment
  const aptDoor = new T.Group(), slider = new T.Group();
  { const g = W.apt, y0 = Y6, yf = Y6 + .02, Hc = Y6 + 2.85, Lv = ROOMS.living, Mb = ROOMS.master, Ba = ROOMS.bath;
    plane(g, M.oakFloor, Lv[0], Lv[1], Lv[4], Lv[5], yf); plane(g, M.oakFloor, Mb[0], Mb[1], Mb[4], Mb[5], yf); plane(g, M.tile, Ba[0], Ba[1], Ba[4], Ba[5], yf);
    plane(g, M.ceil, Lv[0], Lv[1], Lv[4], Lv[5], Hc, true); plane(g, M.ceil, Mb[0], Mb[1], Mb[4], Mb[5], Hc, true); plane(g, M.ceil, Ba[0], Ba[1], Ba[4], Ba[5], Y6 + 2.6, true);
    const ry = (op) => ({ a: op.a, b: op.b, y0: y0 + op.y0, y1: y0 + op.y1 });
    // exterior wall linings (inner faces) with the facade's openings
    wallZ(g, M.wall, 16.56, 16.58, y0, Hc, Lv[4], Lv[5], CORNER.east.filter(o => o.a > 5.9).map(ry)); wallZ(g, M.wallWarm, 16.56, 16.58, y0, Hc, Mb[4], Mb[5], CORNER.east.filter(o => o.a < 5.9).map(ry));
    wallX(g, M.wallWarm, Mb[0], Mb[1], y0, Hc, 2.11, 2.13, CORNER.north.filter(o => o.a > 13).map(ry)); wallX(g, M.metro, Ba[0], Ba[1], y0, Y6 + 2.6, 2.11, 2.13, CORNER.north.filter(o => o.a > 11.5 && o.a < 13).map(ry));
    // party / corridor walls
    wallZ(g, M.wall, 8.1, 8.48, y0, Hc, 5.81, 10.9, [{ a: 6.25, b: 7.15, y0: yf, y1: yf + 2.1 }]); wallX(g, M.wall, 8.48, 16.56, y0, Hc, 10.7, 10.9);
    // partitions: hall/bedrooms wall with doors (B2 closed, bath + master open)
    const dB2 = { a: 10.2, b: 11.05, y0: yf, y1: yf + 2.1 }, dBa = { a: 11.7, b: 12.5, y0: yf, y1: yf + 2.1 }, dMb = { a: 13.1, b: 13.95, y0: yf, y1: yf + 2.1 };
    wallX(g, M.wall, 8.48, 16.56, y0, Hc, 5.81, 5.96, [dB2, dBa, dMb]);
    wallZ(g, M.metro, 11.38, 11.53, y0, Hc, 2.11, 5.81); wallZ(g, M.metro, 12.88, 13.03, y0, Hc, 2.11, 5.81); B(g, M.wallWarm, 13.03, 13.05, y0, Hc, 2.11, 5.81);
    B(g, M.oak, dB2.a, dB2.b, yf, yf + 2.1, 5.84, 5.88, { name: 'doorB2' }); B(g, M.black, dB2.b - .14, dB2.b - .05, yf + 1.0, yf + 1.02, 5.96, 5.99, { wuv: false });
    const openLeaf = (d, ang) => { const p = new T.Group(); p.position.set(d.a + .02, 0, 5.96); p.rotation.y = ang; g.add(p); B(p, M.oak, 0, d.b - d.a - .03, yf, yf + 2.08, -.045, 0, { wuv: false }); return p; };
    openLeaf(dBa, 1.9); openLeaf(dMb, 1.75);
    // skirting shadow gap
    B(g, M.black, 8.48, 16.56, yf, yf + .06, 10.69, 10.7, { cast: false, wuv: false }); B(g, M.black, 8.48, 16.56, yf, yf + .06, 5.96, 5.97, { cast: false, wuv: false });
    // ---- entry door (oak, hinged on the south jamb, swings into the hall)
    aptDoor.position.set(8.47, 0, 7.14); g.add(aptDoor); B(aptDoor, M.doorGrey, -.045, 0, yf, yf + 2.09, -.88, 0, { wuv: false }); B(aptDoor, M.black, -.1, -.045, yf + 1.0, yf + 1.03, -.8, -.66, { wuv: false }); B(aptDoor, M.black, .0, .05, yf + 1.0, yf + 1.03, -.8, -.66, { wuv: false });
    B(W.corridor, M.oakDark, 8.06, 8.1, yf, yf + 2.2, 6.15, 6.25); B(W.corridor, M.oakDark, 8.06, 8.1, yf, yf + 2.2, 7.15, 7.25); B(W.corridor, M.oakDark, 8.06, 8.1, yf + 2.1, yf + 2.2, 6.15, 7.25);
    const books = (x, y, z, n, rot = 0) => { let yy = y; for (let i = 0; i < n; i++) { const h = .025 + R() * .02, bk = B(g, i % 3 ? M.white : M.terra, x - .12 - R() * .03, x + .12, yy, yy + h, z - .09, z + .09, { wuv: false }); bk.rotation.y = rot + (R() - .5) * .3; yy += h; } };
    // ==== styled after Vanta House's own 2-bed renders: light oak plank floor, warm off-white walls, white kitchen, cream boucle sofa,
    // dotted rug, oval white table, arc lamp, floating TV shelf, long white dining table + cream curved chairs, black track spots, square LED panel
    // ---- kitchen: white flat upper + lower units, white top and splash, black tap, range hood, tall white fridge unit
    B(g, M.white, 8.48, 9.12, yf, yf + 2.5, 7.38, 8.9, { r: .01 }); B(g, M.black, 9.12, 9.125, yf + .1, yf + 2.4, 8.14, 8.142, { wuv: false, cast: false }); B(g, M.black, 9.124, 9.13, yf + 1.0, yf + 1.3, 7.95, 7.97, { wuv: false });
    B(g, M.white, 8.48, 9.08, yf + .1, yf + .88, 8.9, 10.7); B(g, M.white, 9.08, 11.15, yf + .1, yf + .88, 10.1, 10.7); B(g, M.oak, 8.48, 9.04, yf, yf + .1, 8.9, 10.7); B(g, M.oak, 9.04, 11.15, yf, yf + .1, 10.14, 10.7);
    for (const z of [9.5, 10.1]) B(g, M.shadowLine, 9.081, 9.084, yf + .12, yf + .86, z - .003, z + .003, { wuv: false, cast: false }); for (const x of [9.7, 10.3, 10.75]) B(g, M.shadowLine, x - .003, x + .003, yf + .12, yf + .86, 10.098, 10.1, { wuv: false, cast: false });
    for (const y of [.42, .64]) B(g, M.shadowLine, 9.081, 9.084, yf + y, yf + y + .004, 8.92, 10.08, { wuv: false, cast: false });
    B(g, M.worktop, 8.48, 9.12, yf + .88, yf + .92, 8.9, 10.7); B(g, M.worktop, 9.12, 11.17, yf + .88, yf + .92, 10.06, 10.7);
    B(g, M.cream, 8.48, 8.49, yf + .92, yf + 1.55, 8.9, 10.7); B(g, M.cream, 8.48, 11.17, yf + .92, yf + 1.55, 10.69, 10.7);
    B(g, M.white, 8.48, 8.84, yf + 1.55, yf + 2.3, 8.9, 10.7); B(g, M.white, 8.84, 11.17, yf + 1.55, yf + 2.3, 10.34, 10.7);   // upper units
    for (const z of [9.5, 10.1]) B(g, M.shadowLine, 8.841, 8.844, yf + 1.57, yf + 2.28, z - .003, z + .003, { wuv: false, cast: false }); for (const x of [9.7, 10.3]) B(g, M.shadowLine, x - .003, x + .003, yf + 1.57, yf + 2.28, 10.338, 10.34, { wuv: false, cast: false });
    B(g, M.black, 8.5, 9.0, yf + 1.5, yf + 1.56, 9.35, 9.95, { wuv: false }); B(g, M.blackGlass, 8.52, 9.06, yf + .92, yf + .925, 9.35, 9.95, { wuv: false });
    B(g, M.steel, 9.7, 10.25, yf + .905, yf + .925, 10.2, 10.6, { wuv: false }); cyl(g, M.black, .015, .015, .3, 9.97, yf + .92, 10.62, 8); B(g, M.black, 9.955, 9.985, yf + 1.2, yf + 1.22, 10.42, 10.64, { wuv: false });
    cyl(g, M.steel, .11, .1, .14, 8.8, yf + .92, 9.55, 16); cyl(g, M.terracotta, .1, .1, .12, 8.8, yf + .92, 9.8, 16); B(g, M.oak, 8.56, 8.96, yf + .92, yf + .94, 9.0, 9.3, { r: .008, wuv: false }); cyl(g, M.white, .14, .09, .09, 10.75, yf + .92, 10.4, 16);
    // ---- dining: long white table, cream curved-back chairs (light oak frames), black track with cylinder spots
    const dx = 12.05, dz = 8.95; B(g, M.worktop, dx - .85, dx + .85, yf + .72, yf + .76, dz - .42, dz + .42, { r: .012 }); for (const sx of [-1, 1]) B(g, M.white, dx + sx * .72 - .03, dx + sx * .72 + .03, yf, yf + .72, dz - .36, dz + .36, { wuv: false }); contact(g, dx, dz, 1.8, .9, yf);
    const chairD = (x, z, a) => { const c = new T.Group(); c.position.set(x, yf, z); c.rotation.y = a + (R() - .5) * .12; g.add(c);
      B(c, M.cream, -.23, .23, .43, .48, -.22, .2, { r: .02, wuv: false }); for (const [lx, lz] of [[-.2, -.18], [.2, -.18], [-.2, .16], [.2, .16]]) B(c, M.oakLight, lx - .016, lx + .016, 0, .44, lz - .016, lz + .016, { wuv: false });
      const back = new T.Mesh(new T.TorusGeometry(.24, .02, 6, 18, Math.PI), M.oakLight); back.rotation.x = Math.PI / 2; back.position.set(0, .72, -.02); back.scale.set(1, 1.05, 1); c.add(back); B(c, M.oakLight, -.02, .02, .45, .72, .19, .23, { wuv: false }); };
    chairD(dx - .45, dz - .62, 0); chairD(dx + .45, dz - .62, 0); chairD(dx - .45, dz + .62, Math.PI); chairD(dx + .45, dz + .62, Math.PI);
    B(g, M.black, dx - 1.3, dx + 1.3, Hc - .035, Hc, dz - .015, dz + .015, { wuv: false, cast: false });
    for (const k of [-1.0, -.35, .3, .95]) { cyl(g, M.black, .003, .003, .45, dx + k, Hc - .45, dz, 4); const sp = cyl(g, M.black, .045, .045, .14, dx + k, Hc - .58, dz, 14); const lb = new T.Mesh(new T.CircleGeometry(.035, 12), EM('#ffe6c4', 2.2)); lb.rotation.x = Math.PI / 2; lb.position.set(dx + k, Hc - .581, dz); g.add(lb); lamps.push({ p: [dx + k, Hc - .62, dz], d: [0, -1, 0], k: .35, room: 4 }); }
    cyl(g, M.white, .09, .07, .1, dx - .2, yf + .76, dz, 14); cyl(g, M.oakLight, .12, .12, .02, dx + .4, yf + .76, dz + .05, 16);
    // ---- lounge: cream boucle modular sofa, beige cushions, grey throw, dotted rug, oval white table, white arc lamp, floating TV shelf
    B(g, M.dotRug, 13.1, 16.0, yf, yf + .012, 7.85, 10.35, { cast: false, wuv: false }).geometry.attributes.uv && 0;
    { const sx0 = 13.25, sx1 = 15.8, sz0 = 9.68, sz1 = 10.64; const n = 3, w = (sx1 - sx0) / n;
      for (let i = 0; i < n; i++) { const a = sx0 + i * w; B(g, M.boucle, a + .01, a + w - .01, yf + .02, yf + .44, sz0, sz1 - .05, { r: .14, seg: 4 }); const bc = B(g, M.boucle, a + .02, a + w - .02, yf + .38, yf + .86, sz1 - .34, sz1, { r: .16, seg: 4 }); bc.rotation.x = -.08; }
      B(g, M.boucle, sx0 - .12, sx0 + .14, yf + .02, yf + .62, sz0, sz1, { r: .12, seg: 4 }); B(g, M.boucle, sx1 - .14, sx1 + .12, yf + .02, yf + .62, sz0, sz1, { r: .12, seg: 4 });
      const c1 = B(g, M.beige, 13.55, 14.05, yf + .44, yf + .9, 10.18, 10.36, { r: .09, seg: 3 }); c1.rotation.z = .12; const c2 = B(g, M.beige, 14.55, 15.05, yf + .44, yf + .9, 10.2, 10.38, { r: .09, seg: 3 }); c2.rotation.z = -.1; const c3 = B(g, M.boucle, 15.05, 15.45, yf + .44, yf + .82, 10.18, 10.32, { r: .08, seg: 3 }); c3.rotation.z = .2;
      const th = B(g, M.greyThrow, 13.2, 13.65, yf + .35, yf + .66, sz0 + .05, sz1 - .1, { r: .03 }); th.rotation.z = .1; contact(g, (sx0 + sx1) / 2, (sz0 + sz1) / 2, sx1 - sx0, sz1 - sz0, yf); }
    { const ct = cyl(g, M.marble, .5, .5, .04, 14.45, yf + .36, 8.85, 40); ct.scale.z = .62; const st = cyl(g, M.black, .05, .05, .36, 14.45, yf, 8.85, 10); const bs = cyl(g, M.black, .22, .22, .015, 14.45, yf, 8.85, 20); contact(g, 14.45, 8.85, 1.0, .65, yf + .012);
      books(14.3, yf + .4, 8.8, 2, .4); cyl(g, M.black, .07, .07, .015, 14.7, yf + .4, 8.95, 16); cyl(g, M.terracotta, .025, .02, .06, 14.66, yf + .415, 8.92, 8); }
    { cyl(g, M.black, .16, .18, .03, 16.25, yf, 10.35, 18); const crv = new T.QuadraticBezierCurve3(new T.Vector3(16.25, yf, 10.35), new T.Vector3(16.25, yf + 2.55, 10.35), new T.Vector3(15.32, yf + 2.02, 9.4)); const arc = new T.Mesh(new T.TubeGeometry(crv, 24, .011, 6), M.chrome); g.add(arc); const sh2 = new T.Mesh(new T.SphereGeometry(.2, 18, 8, 0, 6.3, 0, 1.45), interiorize(new T.MeshLambertMaterial({ color: '#F4F1EA', emissive: '#ffe3bc', emissiveIntensity: .35, side: T.DoubleSide }))); sh2.position.set(15.32, yf + 1.85, 9.4); g.add(sh2); lamps.push({ p: [15.32, yf + 1.7, 9.4], d: [0, -1, 0], k: .3, room: 4 }); }
    // TV wall (bedroom wall of the hall): wall-hung TV over a floating white + oak shelf with a curved end
    B(g, M.white, 14.2, 16.45, yf + .3, yf + .48, 5.96, 6.36, { r: .03 }); B(g, M.oakLight, 14.2, 16.45, yf + .48, yf + .52, 5.96, 6.38, { r: .01 });
    B(g, M.black, 14.6, 16.1, yf + 1.0, yf + 1.86, 5.96, 6.0, { wuv: false }); B(g, M.blackGlass, 14.62, 16.08, yf + 1.02, yf + 1.84, 6.0, 6.002, { wuv: false }); contact(g, 15.3, 6.16, 2.2, .4, yf);
    cyl(g, M.white, .05, .04, .16, 14.45, yf + .52, 6.15, 12); books(16.1, yf + .52, 6.17, 2, 1.4);
    frameArt(g, 'z-', 14.5, yf + 1.6, 10.69, .75, 1.0, printTex(23, ['#EFE7DC', '#E3A88A', '#C98B6E', '#F5EFE6']), M.black);
    plant(g, 16.15, yf, 10.25, 1.35, '#E8E4DC', 11); plant(g, 16.3, yf, 6.78, 1.1, '#E8E4DC', 12);
    // sheer floor-to-ceiling curtains either side of the balcony door, on a ceiling track
    { const sheer = interiorize(new T.MeshLambertMaterial({ color: '#F6F3EE', transparent: true, opacity: .62, side: T.DoubleSide, depthWrite: false })); const cg = new T.PlaneGeometry(.7, 2.8, 22, 1); { const p = cg.attributes.position; for (let i = 0; i < p.count; i++) p.setZ(i, .05 * Math.sin(p.getX(i) * 30)); cg.computeVertexNormals(); }
      for (const z of [7.3, 10.55]) { const c = new T.Mesh(cg, sheer); c.rotation.y = -Math.PI / 2; c.position.set(16.42, yf + 1.42, z); c.renderOrder = 4; g.add(c); } B(g, M.white, 16.38, 16.48, Hc - .05, Hc, 6.0, 10.68, { wuv: false, cast: false }); }
    // ceiling: square flush LED panel (living) + round downlights (hall/kitchen)
    { const pnl = new T.Mesh(new T.PlaneGeometry(.6, .6), EM('#fff7ea', 1.6)); pnl.rotation.x = Math.PI / 2; pnl.position.set(14.6, Hc - .004, 8.5); g.add(pnl); B(g, M.white, 14.28, 14.92, Hc - .012, Hc, 8.18, 8.82, { wuv: false, cast: false }).visible = false;
      lamps.push({ p: [14.6, Hc - .15, 8.5], d: [0, -1, 0], k: .9, room: 4 });
      for (const [x, z] of [[9.0, 6.65], [10.4, 6.65], [12.6, 6.65], [9.8, 9.6], [10.3, 8.2]]) { const d = new T.Mesh(new T.CircleGeometry(.05, 14), EM('#fff4e0', 2.2)); d.rotation.x = Math.PI / 2; d.position.set(x, Hc - .004, z); g.add(d); lamps.push({ p: [x, Hc - .1, z], d: [0, -1, 0], k: .45, room: 4 }); } }
    // hall: white full-height wardrobe + oak skirting everywhere
    B(g, M.white, 8.5, 10.12, yf, Hc - .05, 5.96, 6.5); for (const x of [9.04, 9.58]) B(g, M.shadowLine, x - .002, x + .002, yf + .02, Hc - .07, 6.5, 6.503, { wuv: false, cast: false });
    B(g, M.oakLight, 8.48, 16.56, yf, yf + .08, 10.685, 10.7, { cast: false, wuv: false }); B(g, M.oakLight, 10.12, 16.56, yf, yf + .08, 5.96, 5.975, { cast: false, wuv: false }); B(g, M.oakLight, 8.48, 8.495, yf, yf + .08, 7.15, 7.38, { cast: false, wuv: false });
    // ---- master bedroom: upholstered headboard on an oak panel, floating bedside shelves, white wardrobe wall, grey throw, sheer curtains
    { const bx = 13.05; B(g, M.oakLight, bx, bx + .05, yf, yf + 1.05, 2.4, 5.15); const bed = { x0: bx + .2, x1: 15.25, z0: 3.17, z1: 4.79 };
      B(g, M.headboard, bx + .05, bx + .2, yf + .25, yf + 1.15, bed.z0 - .05, bed.z1 + .05, { r: .07, seg: 3 }); B(g, M.headboard, bed.x0, bed.x1, yf + .08, yf + .32, bed.z0 - .04, bed.z1 + .04, { r: .06, seg: 3 });
      B(g, M.linen, bed.x0 + .02, bed.x1 - .02, yf + .32, yf + .54, bed.z0 + .02, bed.z1 - .02, { r: .06, seg: 3 });
      B(g, M.linen, bed.x0 + .45, bed.x1 + .03, yf + .5, yf + .6, bed.z0 - .03, bed.z1 + .03, { r: .05, seg: 3 }); B(g, M.linen, bed.x1 - .06, bed.x1 + .04, yf + .22, yf + .57, bed.z0 - .03, bed.z1 + .03, { r: .03 });
      for (const z of [3.58, 4.38]) { const p = B(g, M.linen, bed.x0 + .04, bed.x0 + .42, yf + .54, yf + .76, z - .34, z + .34, { r: .08, seg: 3 }); p.rotation.z = -.22; }
      { const ball = new T.Mesh(new T.SphereGeometry(.13, 18, 12), M.brownCushion); ball.position.set(bed.x0 + .55, yf + .7, 3.98); ball.castShadow = true; g.add(ball); }
      B(g, M.greyThrow, bed.x1 - .62, bed.x1 - .18, yf + .6, yf + .63, bed.z0 - .05, bed.z1 + .05, { wuv: false }); const tf = B(g, M.greyThrow, bed.x1 - .55, bed.x1 - .2, yf + .2, yf + .62, bed.z1 + .03, bed.z1 + .06, { wuv: false }); contact(g, (bed.x0 + bed.x1) / 2, 3.98, 2.1, 1.7, yf);
      for (const z of [2.7, 5.25]) { B(g, M.white, bx + .05, bx + .5, yf + .38, yf + .5, z - .24, z + .24, { r: .02 }); B(g, M.oakLight, bx + .05, bx + .5, yf + .5, yf + .53, z - .24, z + .24, { r: .01 }); }
      cyl(g, M.white, .05, .06, .16, bx + .25, yf + .53, 2.7, 12); books(bx + .3, yf + .53, 5.25, 2, .2);
      for (const z of [2.7, 5.25]) { const sc = cyl(g, EM('#ffe6c0', 1.5), .05, .05, .08, bx + .1, yf + 1.3, z, 12); lamps.push({ p: [bx + .2, yf + 1.3, z], k: .3, room: 5 }); }
      B(g, M.white, 14.35, 16.56, yf, Hc - .02, 5.2, 5.81); for (let x = 14.35 + .55; x < 16.5; x += .55) B(g, M.shadowLine, x - .002, x + .002, yf + .02, Hc - .05, 5.198, 5.2, { wuv: false, cast: false });
      const sheer = interiorize(new T.MeshLambertMaterial({ color: '#F6F3EE', transparent: true, opacity: .6, side: T.DoubleSide, depthWrite: false })); const cg = new T.PlaneGeometry(1.1, 2.75, 30, 1); { const p = cg.attributes.position; for (let i = 0; i < p.count; i++) p.setZ(i, .04 * Math.sin(p.getX(i) * 28)); cg.computeVertexNormals(); }
      const c1 = new T.Mesh(cg, sheer); c1.position.set(16.0, yf + 1.38, 2.22); g.add(c1); const c2 = new T.Mesh(cg, sheer); c2.rotation.y = -Math.PI / 2; c2.position.set(16.45, yf + 1.38, 5.3); c2.scale.x = .5; g.add(c2);
      B(g, M.white, 13.7, 16.5, Hc - .06, Hc - .02, 2.17, 2.22, { wuv: false }); B(g, M.white, 16.45, 16.5, Hc - .06, Hc - .02, 2.2, 5.6, { wuv: false });
      plant(g, 16.2, yf, 2.55, 1.2, '#E8E4DC', 14);
      const d = new T.Mesh(new T.CircleGeometry(.05, 14), EM('#fff4e0', 2.2)); d.rotation.x = Math.PI / 2; d.position.set(14.8, Hc - .004, 4.0); g.add(d); lamps.push({ p: [14.8, Hc - .05, 4.0], d: [0, -1, 0], k: .45, room: 5 }); }
    // ---- bathroom glimpse: oak vanity + stone trough sink, black wall tap, mirror with light strip, glass shower screen
    { B(g, M.oak, 12.38, 12.88, yf + .2, yf + .72, 2.6, 3.9, { r: .02 }); B(g, M.stone, 12.33, 12.88, yf + .72, yf + .86, 2.55, 3.95, { r: .02 }); B(g, M.black, 12.84, 12.88, yf + 1.05, yf + 1.08, 3.2, 3.3, { wuv: false });
      B(g, M.mirror, 12.86, 12.88, yf + 1.15, yf + 2.0, 2.75, 3.75, { wuv: false }); B(g, EM('#fff1dc', 1.6), 12.855, 12.86, yf + 1.15, yf + 2.0, 3.76, 3.79, { wuv: false, cast: false });
      const sg = new T.Mesh(new T.PlaneGeometry(1.0, 2.0), M.glass); sg.rotation.y = Math.PI / 2; sg.position.set(12.2, yf + 1.0, 4.6); g.add(sg); B(g, M.black, 12.19, 12.21, yf, yf + 2.0, 4.08, 4.1, { wuv: false });
      cyl(g, M.white, .1, .1, .03, 12.4, yf + .86, 3.6, 12); lamps.push({ p: [12.6, yf + 1.6, 3.25], k: .45, room: 6 }); }
    // living lamps + portals
    lamps.push({ p: [dx, yf + 1.7, dz], k: .55, room: 4 }, { p: [9.8, Hc - .1, 8.27], d: [-.4, -.9, .2], k: .55, room: 4 }, { p: [11.2, Hc - .1, 8.27], d: [-.3, -.9, .3], k: .4, room: 4 }, { p: [15.3, Hc - .1, 6.6], d: [0, -1, 0], k: .45, room: 4 }, { p: [13.05, yf + 1.4, 9.85], k: .3, room: 4 }, { p: [9.7, yf + 1.6, 9.8], k: .3, room: 4 });
    portals.push({ c: [16.58, Y6 + 1.22, 9.05], n: [-1, 0, 0], s: [1.5, 1.22], k: 5.4, room: 4 }, { c: [16.58, Y6 + 1.72, 6.65], n: [-1, 0, 0], s: [.4, .72], k: 4.6, room: 4 },
      { c: [16.58, Y6 + 1.2, 3.9], n: [-1, 0, 0], s: [1.35, 1.2], k: 4.6, room: 5 }, { c: [14.8, Y6 + 1.5, 2.11], n: [0, 0, 1], s: [.95, .95], k: 4.2, room: 5 }, { c: [12.2, Y6 + 2.0, 2.11], n: [0, 0, 1], s: [.3, .3], k: 4.6, room: 6 });
    // real glazing in the corner openings (facade supplies frames)
    [...CORNER.north.map(o => ['n', o]), ...CORNER.east.map(o => ['e', o])].filter(([, o]) => o.real).forEach(([f, o]) => {
      const w = o.b - o.a, h = o.y1 - o.y0, yc = Y6 + (o.y0 + o.y1) / 2; if (o.kind === 'door') return;
      const p = new T.Mesh(new T.PlaneGeometry(w - .04, h - .04), M.glass); p.renderOrder = 3; if (f === 'n') p.position.set((o.a + o.b) / 2, yc, 1.91 - .045); else { p.rotation.y = Math.PI / 2; p.position.set(16.78 + .045, yc, (o.a + o.b) / 2); } g.add(p); });
    // sliding doors (living + master): fixed pane + sliding pane in thin black frames
    const sd = (o, grpS) => { const w = (o.b - o.a) / 2, h = o.y1 - o.y0, y0b = Y6 + o.y0; const mk = (zc, off) => { const s = new T.Group(); s.position.set(16.78 + off, 0, zc); const fr = (a, b, c, d) => B(s, M.frame, -.02, .02, y0b + c, y0b + d, a, b, { wuv: false });
        fr(-w / 2, -w / 2 + .05, 0, h); fr(w / 2 - .05, w / 2, 0, h); fr(-w / 2, w / 2, 0, .06); fr(-w / 2, w / 2, h - .05, h); const p = new T.Mesh(new T.PlaneGeometry(w - .1, h - .11), M.glass); p.rotation.y = Math.PI / 2; p.position.y = y0b + h / 2; p.renderOrder = 3; s.add(p); return s; };
      const fixed = mk(o.b - w / 2, .02), mov = mk(o.a + w / 2, -.04); grpS.add(fixed); grpS.add(mov); return { mov, a: o.a + w / 2, b: o.b - w / 2 + .02 }; };
    g.add(slider); const sl = sd(CORNER.east[2], slider); const sm = sd(CORNER.east[0], g); sm.mov.position.z = sm.b - .05;
    W.slider = { set(f) { f = Math.max(0, Math.min(1, f)); sl.mov.position.z = sl.a + (sl.b - sl.a) * f; } }; W.slider.set(0);
  }
  // ============================================================== balconies (outdoor): tiles, folding timber chairs, table, planters
  { const g = W.balcony, yf = Y6 + .005; const tileM = new T.MeshLambertMaterial({ map: X.tile, color: '#d8d6d2' }); const wood = new T.MeshLambertMaterial({ color: '#8a6446' }), potM = new T.MeshLambertMaterial({ color: '#6E6E70' });
    const pl = plane(g, tileM, 16.8, 18.5, 7.32, 10.83, yf); plane(g, tileM, 16.8, 18.15, 2.22, 5.58, yf);
    const fchair = (x, z, a) => { const c = new T.Group(); c.position.set(x, yf, z); c.rotation.y = a; g.add(c); for (let i = 0; i < 5; i++) { const sl = new T.Mesh(new T.BoxGeometry(.42, .02, .06), wood); sl.position.set(0, .45, -.16 + i * .08); sl.castShadow = true; c.add(sl); }
      for (let i = 0; i < 4; i++) { const b = new T.Mesh(new T.BoxGeometry(.42, .06, .02), wood); b.position.set(0, .62 + i * .09, -.21); b.rotation.x = -.15; b.castShadow = true; c.add(b); }
      for (const sx of [-.2, .2]) { const l1 = new T.Mesh(new T.BoxGeometry(.025, .95, .03), wood); l1.position.set(sx, .47, -.05); l1.rotation.x = .3; l1.castShadow = true; c.add(l1); const l2 = new T.Mesh(new T.BoxGeometry(.025, .5, .03), wood); l2.position.set(sx, .24, .12); l2.rotation.x = -.35; c.add(l2); } };
    fchair(17.55, 9.35, -2.2); fchair(17.75, 10.35, -1.0); { const t = new T.Mesh(new T.CylinderGeometry(.3, .3, .03, 20), wood); t.position.set(18.05, yf + .66, 9.85); t.castShadow = true; g.add(t); const l = new T.Mesh(new T.CylinderGeometry(.02, .02, .66, 6), M.frame); l.position.set(18.05, yf + .33, 9.85); g.add(l); }
    const pots = [[18.25, 10.55, .9]]; pots.forEach(([x, z, h], i) => { const p = new T.Mesh(new T.CylinderGeometry(.2, .16, .38, 14), potM); p.position.set(x, yf + .19, z); p.castShadow = true; g.add(p); const sh = makeShrubs(T, [[[x, z], [x + .01, z], 1, h, [.27, .45, .28]]], { seed: 80 + i }); sh.position.y = yf + .3; g.add(sh); });
  }
  // ============================================================== people inside (receptionist, resident)
  const ppl = makePeople(T, [{ pos: [12.8, 10.25], ang: Math.PI, pose: 'stand', seed: 811, shirt: '#2B2D31', female: true, dress: false, h: 1.68, y: .05 }, { pos: [14.0, 5.7], ang: .9 + Math.PI, pose: 'sit', seat: .45, seed: 812, y: .05, shirt: '#E9E3D3' }]);
  ppl.group.children.forEach(m => { if (m.material && !m.material.map) interiorize(m.material); }); W.lobby.add(ppl.group);
  // lights: room list (index = room id used by lamps/portals)
  const roomList = [[ROOMS.cab, .6], [ROOMS.lobby, .7], [ROOMS.lifthall, .5], [ROOMS.corridor, .45], [ROOMS.living, .62], [ROOMS.master, .6], [ROOMS.bath, .55]];
  const cabLamp = { p: [-1.95, 2.35, 6.65], k: 4.5, room: 0 }; lamps.push(cabLamp);
  if (lamps.length > NL || portals.length > NP) console.warn('interior lights over limit', lamps.length, portals.length);
  const baseLights = setLights(roomList, portals, lamps);
  const cabMin = IL.uRMin.value[0], cabMax = IL.uRMax.value[0], cabLP = IL.uLP.value[lamps.indexOf(cabLamp)];
  // ------------------------------------------------------------------ state API (pure: call every frame)
  function set(s = {}) {
    W.lobbyDoors.set(s.entry || 0); W.slider.set(s.slider || 0); aptDoor.rotation.y = -(s.aptDoor || 0) * 1.75;
    const cy = s.cabY ?? 0, fl = s.floor ?? 'G', dir = s.dir || 0;
    car.set(cy, s.carDoor ?? 0, fl, dir); doorsG.set(s.liftG || 0, fl, dir); doors6.set(s.lift6 || 0, fl, dir);
    cabMin.y = cy - .05; cabMax.y = cy + 2.5; cabLP.y = cy + 2.35;
    ppl.update(s.t || 0);
  }
  set({});
  return { group: root, groups: W, set, rooms: ROOMS, lift: LIFT, materials: M, people: ppl, Y6, baseLights, car, doorsG, doors6, aptDoor };
}

// ------------------------------------------------------------------ helpers shared with r_units.js
export const H_ = { B: (...a) => B(...a), wallX: (...a) => wallX(...a), wallZ: (...a) => wallZ(...a), plane: (...a) => plane(...a), contact: (...a) => contact(...a), cyl: (...a) => cyl(...a),
  plant: (...a) => plant(...a), printTex: (...a) => printTex(...a), frameArt: (...a) => frameArt(...a), liftDoors: (...a) => liftDoors(...a), EM: (...a) => EM(...a), L: (...a) => L(...a), PH: (...a) => PH(...a), X: () => textures() };
