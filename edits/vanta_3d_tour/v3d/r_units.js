// r_units.js - furnished 1-bed (Tower B, level 4) and 3-bed (Tower A, level 9) units, real 3D, styled after Vanta House's own
// interior renders (light oak plank floor, warm-white walls, white kitchens, cream boucle, oak/white floating joinery, black metal).
// Also their lift corridors. Uses the shared helpers and light model of r_interior.js.
import { H_, interiorize, setLights, useLights, IL } from './r_interior.js';
import { levelOf, unitOpening, rnd, makeShrubs } from './r_vanta3d.js';
let T, M, B, wallX, wallZ, plane, contact, cyl, plant, printTex, frameArt, EM, liftDoors;
const R = rnd(4242);
export const U1 = { level: 4, y: levelOf(4), rect: [4.6, 12.7, -16.4, -10.5], zone: [4.4, 12.9, -16.6, -10.4] };
export const U3 = { level: 9, y: levelOf(9), rect: [-1.6, 15.9, 10.9, 20.6], zone: [-3.6, 17.95, 10.95, 22.6] };
// ------------------------------------------------------------------ small kits (local coords, then placed)
function grp(parent, x, y, z, ry = 0) { const g = new T.Group(); g.position.set(x, y, z); g.rotation.y = ry; parent.add(g); return g; }
function sofaCorner(g) { // L sofa, back along -z, chaise to +x ; origin = back-left corner on the floor
  const m = M.boucle; B(g, m, 0, 2.6, 0, .42, 0, .95, { r: .14, seg: 4 }); B(g, m, 1.75, 2.6, 0, .42, .95, 1.75, { r: .14, seg: 4 });
  for (let i = 0; i < 3; i++) { const bc = B(g, m, .06 + i * .86, .9 + i * .86, .36, .86, 0, .3, { r: .15, seg: 4 }); bc.rotation.x = .06; }
  B(g, m, -.12, .16, 0, .62, 0, .95, { r: .12, seg: 4 }); B(g, m, 2.48, 2.72, 0, .62, 0, 1.75, { r: .12, seg: 4 });
  const c1 = B(g, M.beige, .25, .72, .4, .84, .22, .4, { r: .09, seg: 3 }); c1.rotation.z = .12; const c2 = B(g, M.beige, 1.6, 2.05, .4, .84, .22, .4, { r: .09, seg: 3 }); c2.rotation.z = -.1;
  const th = B(g, M.greyThrow, .3, .8, .42, .47, .3, .9, { r: .02 }); th.rotation.y = .3; contact(g, 1.3, .7, 2.6, 1.6, 0); }
function coffeeOval(g) { const ct = cyl(g, M.marble, .5, .5, .04, 0, .36, 0, 40); ct.scale.z = .6; cyl(g, M.black, .05, .05, .36, 0, 0, 0, 10); cyl(g, M.black, .22, .22, .015, 0, 0, 0, 20); contact(g, 0, 0, 1.0, .65, .012);
  cyl(g, M.black, .08, .08, .012, .2, .4, .05, 18); const bk = B(g, M.white, -.3, -.05, .4, .43, -.12, .1, { wuv: false }); bk.rotation.y = .3; }
function rugDots(g, w, d) { B(g, M.dotRug, -w / 2, w / 2, 0, .012, -d / 2, d / 2, { cast: false, wuv: false }); }
function arcLamp(g) { cyl(g, M.black, .16, .18, .03, 0, 0, 0, 18); const crv = new T.QuadraticBezierCurve3(new T.Vector3(0, 0, 0), new T.Vector3(0, 2.55, 0), new T.Vector3(-.9, 2.0, .6)); g.add(new T.Mesh(new T.TubeGeometry(crv, 20, .011, 6), M.chrome));
  const sh = new T.Mesh(new T.SphereGeometry(.2, 18, 8, 0, 6.3, 0, 1.45), interiorize(new T.MeshLambertMaterial({ color: '#F4F1EA', emissive: '#ffe3bc', emissiveIntensity: .35, side: T.DoubleSide }))); sh.position.set(-.9, 1.85, .6); g.add(sh); }
function tvWall(g, w = 2.4) { // against a wall at z=0 facing +z
  B(g, M.white, -w / 2, w / 2, .3, .48, 0, .4, { r: .05, seg: 3 }); B(g, M.oakLight, -w / 2, w / 2, .48, .52, 0, .42, { r: .01 }); B(g, M.black, -.85, .85, 1.0, 1.95, 0, .04, { wuv: false }); B(g, M.blackGlass, -.83, .83, 1.02, 1.93, .04, .042, { wuv: false }); contact(g, 0, .2, w, .4, 0);
  cyl(g, M.white, .05, .04, .16, -w / 2 + .2, .52, .2, 12); }
function diningLong(g, len = 2.0, n = 3) { // table along x centred at origin
  B(g, M.worktop, -len / 2, len / 2, .72, .76, -.45, .45, { r: .03 }); for (const sx of [-1, 1]) B(g, M.white, sx * (len / 2 - .25) - .04, sx * (len / 2 - .25) + .04, 0, .72, -.38, .38, { r: .02 }); contact(g, 0, 0, len, .9, 0);
  const chair = (x, z, a) => { const c = grp(g, x, 0, z, a + (R() - .5) * .1); B(c, M.cream, -.23, .23, .43, .48, -.22, .2, { r: .03, wuv: false }); for (const [lx, lz] of [[-.2, -.18], [.2, -.18], [-.2, .16], [.2, .16]]) B(c, M.oakLight, lx - .016, lx + .016, 0, .44, lz - .016, lz + .016, { wuv: false });
    const back = new T.Mesh(new T.TorusGeometry(.24, .022, 6, 18, Math.PI), M.oakLight); back.rotation.x = Math.PI / 2; back.position.set(0, .72, -.02); c.add(back); B(c, M.oakLight, -.02, .02, .45, .72, .19, .23, { wuv: false }); };
  for (let i = 0; i < n; i++) { const x = -len / 2 + (i + .5) * len / n; chair(x, -.62, 0); chair(x, .62, Math.PI); }
  cyl(g, M.white, .09, .07, .1, -.3, .76, 0, 14); cyl(g, M.oakLight, .12, .12, .02, .35, .76, .05, 16); }
function trackPendant(g, len, Hc, lamps, room) { B(g, M.black, -len / 2, len / 2, Hc - .035, Hc, -.015, .015, { wuv: false, cast: false });
  for (let k = 0; k < 4; k++) { const x = -len / 2 + (k + .5) * len / 4; cyl(g, M.black, .003, .003, .45, x, Hc - .45, 0, 4); cyl(g, M.black, .045, .045, .14, x, Hc - .58, 0, 14); const lb = new T.Mesh(new T.CircleGeometry(.035, 12), EM('#ffe6c4', 2.2)); lb.rotation.x = Math.PI / 2; lb.position.set(x, Hc - .581, 0); g.add(lb);
    const wp = lb.getWorldPosition(new T.Vector3()); lamps.push({ p: [wp.x, wp.y - .05, wp.z], d: [0, -1, 0], k: .35, room }); } }
function kitchenRun(g, len, o = {}) { // run along x from 0..len, back at z=0, front at z=.6 ; uppers ; hob at o.hob ; sink at o.sink
  B(g, M.white, 0, len, .1, .88, 0, .6); B(g, M.oak, 0, len, 0, .1, .04, .6); B(g, M.worktop, 0, len, .88, .92, 0, .64);
  for (let x = .6; x < len - .1; x += .6) B(g, M.shadowLine, x - .003, x + .003, .12, .86, .6, .603, { wuv: false, cast: false });
  B(g, M.cream, 0, len, .92, 1.55, 0, .01); B(g, M.white, 0, len, 1.55, 2.3, 0, .36); for (let x = .6; x < len - .1; x += .6) B(g, M.shadowLine, x - .003, x + .003, 1.57, 2.28, .36, .363, { wuv: false, cast: false });
  B(g, M.oakLight, 0, len, 1.53, 1.55, 0, .37, { wuv: false });
  if (o.hob != null) { B(g, M.blackGlass, o.hob - .3, o.hob + .3, .92, .925, .04, .58, { wuv: false }); B(g, M.black, o.hob - .3, o.hob + .3, 1.48, 1.55, .0, .45, { wuv: false }); cyl(g, M.steel, .11, .1, .14, o.hob - .12, .925, .25, 16); cyl(g, M.terracotta, .1, .1, .12, o.hob + .14, .925, .35, 16); }
  if (o.sink != null) { B(g, M.black, o.sink - .28, o.sink + .28, .905, .925, .12, .52, { wuv: false }); cyl(g, M.black, .015, .015, .3, o.sink, .92, .06, 8); B(g, M.black, o.sink - .015, o.sink + .015, 1.2, 1.22, .06, .28, { wuv: false }); }
  contact(g, len / 2, .3, len, .6, 0); }
function fridge(g) { B(g, M.white, 0, .9, 0, 1.95, 0, .7, { r: .02 }); B(g, M.shadowLine, .448, .452, .05, 1.9, .7, .703, { wuv: false, cast: false }); B(g, M.black, .32, .58, 1.05, 1.35, .70, .705, { wuv: false }); }
function island(g, len) { B(g, M.white, -len / 2, len / 2, .08, .9, -.32, .32, { r: .02 }); B(g, M.shadowLine, -len / 2, len / 2, 0, .08, -.3, .3, { wuv: false }); B(g, M.worktop, -len / 2 - .02, len / 2 + .02, .9, .94, -.34, .34, { r: .01 });
  B(g, M.black, -.3, .25, .925, .945, -.2, .2, { wuv: false }); cyl(g, M.black, .015, .015, .32, .38, .94, -.15, 8); contact(g, 0, 0, len, .65, 0); }
function bedKit(g, wB = 1.6) { // headboard against z=0 wall, bed toward +z
  const hw = wB / 2 + .15; B(g, M.oakLight, -hw - .55, hw + .55, .3, 1.05, 0, .04); B(g, M.headboard, -hw, hw, .25, 1.12, .04, .2, { r: .07, seg: 3 });
  B(g, M.headboard, -wB / 2, wB / 2, .06, .32, .2, 2.25, { r: .06, seg: 3 }); B(g, M.linen, -wB / 2 + .02, wB / 2 - .02, .32, .54, .22, 2.22, { r: .06, seg: 3 });
  B(g, M.linen, -wB / 2 - .03, wB / 2 + .03, .5, .6, .65, 2.27, { r: .05, seg: 3 }); B(g, M.linen, -wB / 2 - .03, wB / 2 + .03, .2, .57, 2.2, 2.29, { r: .03 });
  for (const x of [-.38, .38]) { const p = B(g, M.linen, x - .34, x + .34, .54, .76, .24, .62, { r: .08, seg: 3 }); p.rotation.x = .22; }
  const ball = new T.Mesh(new T.SphereGeometry(.13, 18, 12), M.brownCushion); ball.position.set(0, .7, .7); ball.castShadow = true; g.add(ball);
  B(g, M.greyThrow, -wB / 2 - .05, wB / 2 + .05, .6, .63, 1.55, 2.0, { wuv: false }); B(g, M.greyThrow, -wB / 2 - .05, wB / 2 + .05, .2, .62, 2.27, 2.3, { wuv: false }); contact(g, 0, 1.2, wB + .2, 2.2, 0);
  for (const sx of [-1, 1]) { const x = sx * (hw + .3); B(g, M.white, x - .24, x + .24, .38, .5, .04, .48, { r: .02 }); B(g, M.oakLight, x - .24, x + .24, .5, .53, .04, .48, { r: .01 }); }
  cyl(g, M.white, .05, .06, .16, -(hw + .3), .53, .25, 12); }
function wardrobe(g, len, h = 2.6) { B(g, M.white, 0, len, 0, h, 0, .6); for (let x = .5; x < len - .05; x += .5) B(g, M.shadowLine, x - .002, x + .002, .02, h - .02, .6, .603, { wuv: false, cast: false }); }
function bathKit(g, Hc, lamps, room) { // vanity on the wall z=0 facing +z at x 0 ; shower to +x
  B(g, M.oak, -.55, .55, .45, .82, 0, .5, { r: .02 }); B(g, M.stone, -.58, .58, .82, .9, 0, .52, { r: .02 }); B(g, M.cream, -.25, .25, .86, .9, .1, .42, { wuv: false });
  cyl(g, M.black, .025, .025, .02, 0, 1.1, .02, 10).rotation.x = Math.PI / 2; B(g, M.black, -.012, .012, 1.08, 1.1, .02, .2, { wuv: false });
  B(g, M.black, -.56, .56, 1.2, 2.0, 0, .14); B(g, M.mirror, -.53, .53, 1.23, 1.97, .14, .145, { wuv: false });
  B(g, M.black, .9, 1.6, 1.55, 1.58, .02, .12, { wuv: false }); B(g, M.black, .9, 1.6, 1.3, 1.33, .02, .12, { wuv: false });
  const sg = new T.Mesh(new T.PlaneGeometry(1.0, 2.0), M.glass); sg.rotation.y = Math.PI / 2; sg.position.set(1.75, 1.0, .6); g.add(sg); B(g, M.black, 1.74, 1.76, 0, 2.0, 1.08, 1.1, { wuv: false }); B(g, M.black, 1.74, 1.76, 1.98, 2.0, .1, 1.1, { wuv: false });
  B(g, M.black, 2.3, 2.5, 2.05, 2.08, .05, .3, { wuv: false }); B(g, M.black, 2.35, 2.45, 2.08, 2.2, .05, .07, { wuv: false }); B(g, M.black, 2.0, 2.03, .9, 1.6, .02, .05, { wuv: false });
  B(g, M.white, -1.2, -.8, .38, .8, 0, .55, { r: .08, seg: 3 }); B(g, M.black, -1.07, -.93, 1.0, 1.12, 0, .01, { wuv: false });
  const wp = g.localToWorld(new T.Vector3(0, 1.8, .4)); lamps.push({ p: [wp.x, wp.y, wp.z], k: 1.1, room }); const wc = g.localToWorld(new T.Vector3(.6, 2.4, 1.0)); lamps.push({ p: [wc.x, wc.y, wc.z], d: [0, -1, 0], k: 1.0, room }); }
function cloakKit(g, len, wd, Hc, lamps, room, o_door) { // walk-through dressing corridor along x (0..len), width wd (z 0..wd)
  for (const side of [0, 1]) { const z0 = side ? wd - .55 : 0, z1 = side ? wd : .55;
    for (let x = 0; x < len - .05; x += 1.1) { if (side && o_door && x + 1.08 > o_door[0] && x < o_door[1]) continue; const open = (Math.floor(x / 1.1) % 3 === 1); if (open) { B(g, M.oakLight, x, x + 1.08, 0, 2.6, side ? wd - .02 : 0, side ? wd : .02); for (const y of [.5, 1.0, 1.5, 2.0]) { B(g, M.oakLight, x, x + 1.08, y, y + .03, z0, z1); B(g, EM('#fff1d8', 1.4), x + .02, x + 1.06, y - .012, y - .004, side ? z0 + .02 : z1 - .04, side ? z0 + .04 : z1 - .02, { wuv: false, cast: false }); }
        for (let k = 0; k < 4; k++) B(g, k % 2 ? M.white : M.greyThrow, x + .1 + k * .22, x + .28 + k * .22, 1.03, 1.12 + R() * .05, z0 + .1, z1 - .1, { wuv: false }); }
      else { B(g, M.white, x, x + 1.08, 0, 2.6, z0, z1); B(g, M.shadowLine, x + .538, x + .542, .02, 2.58, side ? z0 - .003 : z1, side ? z0 : z1 + .003, { wuv: false, cast: false }); } } }
  B(g, M.oakLight, len - .5, len, .42, .46, .7, wd - .7, { r: .01 }); const wp = g.localToWorld(new T.Vector3(len / 2, Hc - .1, wd / 2)); lamps.push({ p: [wp.x, wp.y, wp.z], d: [0, -1, 0], k: 2.2, room }, { p: [wp.x, wp.y - 1.4, wp.z], k: .9, room }, { p: [wp.x - len / 3, wp.y - .3, wp.z], d: [0, -1, 0], k: 1.2, room }); }
function sheers(g, len, h, n = 2) { const sheer = interiorize(new T.MeshLambertMaterial({ color: '#F6F3EE', transparent: true, opacity: .62, side: T.DoubleSide, depthWrite: false })); const cg = new T.PlaneGeometry(.75, h, 22, 1); { const p = cg.attributes.position; for (let i = 0; i < p.count; i++) p.setZ(i, .05 * Math.sin(p.getX(i) * 30)); cg.computeVertexNormals(); }
  for (let i = 0; i < n; i++) { const c = new T.Mesh(cg, sheer); c.position.set(i ? len - .4 : .4, h / 2 + .02, 0); c.renderOrder = 4; g.add(c); } }
function downlight(g, x, y, z, lamps, room, k = .45) { const d = new T.Mesh(new T.CircleGeometry(.05, 14), EM('#fff4e0', 2.2)); d.rotation.x = Math.PI / 2; d.position.set(x, y - .004, z); g.add(d); lamps.push({ p: [x, y - .1, z], d: [0, -1, 0], k, room }); }
function ledPanel(g, x, y, z, lamps, room, s = .55) { const p = new T.Mesh(new T.PlaneGeometry(s, s), EM('#fff7ea', 1.6)); p.rotation.x = Math.PI / 2; p.position.set(x, y - .004, z); g.add(p); lamps.push({ p: [x, y - .15, z], d: [0, -1, 0], k: .8, room }); }
function balconySet(g) { const wood = new T.MeshLambertMaterial({ color: '#8a6446' }); const chair = (x, z, a) => { const c = grp(g, x, 0, z, a); for (let i = 0; i < 5; i++) { const s = new T.Mesh(new T.BoxGeometry(.42, .02, .06), wood); s.position.set(0, .45, -.16 + i * .08); s.castShadow = true; c.add(s); }
    for (let i = 0; i < 4; i++) { const b = new T.Mesh(new T.BoxGeometry(.42, .06, .02), wood); b.position.set(0, .62 + i * .09, -.21); b.rotation.x = -.15; b.castShadow = true; c.add(b); } for (const sx of [-.2, .2]) { const l = new T.Mesh(new T.BoxGeometry(.025, .95, .03), wood); l.position.set(sx, .47, -.05); l.rotation.x = .3; c.add(l); } };
  chair(-.5, 0, .3); chair(.5, 0, -.3); const t = new T.Mesh(new T.CylinderGeometry(.28, .28, .03, 20), wood); t.position.set(0, .62, .45); g.add(t); const l = new T.Mesh(new T.CylinderGeometry(.02, .02, .62, 6), M.frame); l.position.set(0, .31, .45); g.add(l); }
// ------------------------------------------------------------------ build
export function buildUnits(THREE, INT, vanta) {
  T = THREE; M = INT.materials; ({ B, wallX, wallZ, plane, contact, cyl, plant, printTex, frameArt, EM, liftDoors } = H_);
  const VM = vanta.materials; const out = {};
  // =============================================================== 3-BED, Tower A level 9 (south-east unit of the typical plan)
  { const y0 = U3.y, yf = y0 + .02, Hc = y0 + 2.85, g = new T.Group(); g.name = 'unit3'; INT.group.add(g); const lamps = [], portals = [];
    const RM = { liv: [-1.38, 3.0, 11.05, 18.43], cor: [3.0, 11.2, 13.4, 14.9], bath: [3.15, 5.0, 11.05, 13.25], cloak: [6.6, 11.2, 11.05, 13.25], b1: [3.15, 6.45, 15.05, 18.43], b2: [6.6, 11.05, 15.05, 18.43], mas: [11.35, 15.7, 13.4, 18.43], ens: [11.35, 15.7, 11.05, 13.25],
      lc1: [-1.0, 2.6, 5.9, 7.5], lc2: [1.0, 2.6, 7.5, 10.9] };
    const ri = { cab: 0, lc1: 1, lc2: 2, liv: 3, cor: 4, bath: 5, cloak: 6, b1: 7, b2: 8, mas: 9, ens: 10 };
    // floors + ceilings
    for (const k of ['liv', 'cor', 'cloak', 'b1', 'b2', 'mas']) { const r = RM[k]; plane(g, M.oakFloor, r[0], r[1], r[2], r[3], yf); plane(g, M.ceil, r[0], r[1], r[2], r[3], Hc, true); }
    for (const k of ['bath', 'ens']) { const r = RM[k]; plane(g, M.sandTile, r[0], r[1], r[2], r[3], yf); plane(g, M.ceil, r[0], r[1], r[2], r[3], y0 + 2.6, true); }
    for (const k of ['lc1', 'lc2']) { const r = RM[k]; plane(g, M.tile, r[0], r[1], r[2], r[3], yf); plane(g, M.ceil, r[0], r[1], r[2], r[3], y0 + 2.7, true); }
    const D = (a, b) => ({ a, b, y0: yf, y1: yf + 2.1 });
    // walls
    wallX(g, M.wall, -1.53, 15.85, y0, Hc, 10.9, 11.05, [D(1.5, 2.4)]);                          // north party wall with the entrance door
    wallZ(g, M.wall, -1.53, -1.38, y0, Hc, 10.9, 18.43);                                          // west party wall
    wallZ(g, M.wall, 2.92, 3.0, y0, Hc, 11.05, 13.4); wallZ(g, M.wall, 3.0, 3.15, y0, Hc, 14.9, 18.43); // living east walls (TV wall)
    wallX(g, M.wall, 3.0, 11.35, y0, Hc, 13.25, 13.4, [D(3.45, 4.25), D(9.95, 10.75)]); wallX(g, M.wall, 3.0, 11.35, y0, Hc, 14.9, 15.05, [D(3.6, 4.4), D(7.0, 7.8)]);
    wallZ(g, M.wall, 5.0, 5.15, y0, Hc, 11.05, 13.25); wallZ(g, M.wall, 6.45, 6.6, y0, Hc, 11.05, 13.25); wallZ(g, M.wall, 6.45, 6.6, y0, Hc, 15.05, 18.43);
    wallZ(g, M.wall, 11.05, 11.35, y0, Hc, 14.9, 18.43); wallZ(g, M.wall, 11.2, 11.35, y0, Hc, 11.05, 14.9, [D(13.55, 14.55)]); wallX(g, M.wall, 11.35, 15.7, y0, Hc, 13.25, 13.4, [D(12.1, 12.9)]);
    // exterior walls (inner lining) with openings + the facade elements of the openings
    const OS = [{ a: 3.95, b: 5.55, y0: .9, y1: 2.45, kind: 'win' }, { a: 7.75, b: 9.55, y0: .9, y1: 2.45, kind: 'win' }, { a: 12.2, b: 14.7, y0: 0, y1: 2.45, kind: 'door', balc: [11.8, 15.1, 1.45] }];
    const OE = [{ a: 11.6, b: 12.4, y0: 1.6, y1: 2.3, kind: 'win' }, { a: 14.3, b: 17.6, y0: .5, y1: 2.45, kind: 'win' }];
    const ry = (o) => ({ a: o.a, b: o.b, y0: y0 + o.y0, y1: y0 + o.y1 });
    wallX(g, M.wall, 3.0, 15.85, y0, Hc, 18.43, 18.58, OS.map(ry)); wallZ(g, M.wall, 15.7, 15.85, y0, Hc, 10.9, 18.58, OE.map(ry));
    OS.forEach(o => unitOpening(T, g, VM, y0, { axis: 'z', at: 18.58, out: 1 }, o)); OE.forEach(o => unitOpening(T, g, VM, y0, { axis: 'x', at: 15.85, out: 1 }, o));
    // living balcony (the projecting bay of the plan): slider at z 18.43, balustrade on the projection's outer edges
    { const slA = -1.2, slB = 2.85, sy = y0 + 2.45; for (const [a, b] of [[slA - .05, slA], [slB, slB + .05], [-.05 + (slA + slB) / 2, .05 + (slA + slB) / 2]]) B(g, M.frame, a, b, y0, sy, 18.47, 18.53);
      B(g, M.frame, slA, slB, sy, sy + .06, 18.47, 18.53); B(g, M.frame, slA, slB, y0, y0 + .05, 18.47, 18.53); wallX(g, M.wall, -1.38, 3.0, y0, Hc, 18.43, 18.47, [{ a: slA, b: slB, y0: y0, y1: sy }]);
      const p1 = new T.Mesh(new T.PlaneGeometry((slB - slA) / 2 - .1, 2.4), M.glass); p1.position.set(slA + (slB - slA) * .75, y0 + 1.22, 18.5); p1.renderOrder = 3; g.add(p1);
      plane(g, M.tileOut, -1.48, 2.95, 18.58, 20.42, y0 + .005); const rail = (x0, x1, z0, z1) => { B(g, VM.railGlass, x0, x1, y0 + .06, y0 + 1.05, z0, z1, { cast: false, wuv: false }).renderOrder = 2; };
      rail(-1.48, 2.95, 20.4, 20.43); rail(-1.5, -1.47, 18.6, 20.42); rail(2.94, 2.97, 18.6, 20.42); B(g, VM.rail, -1.5, 2.97, y0 + 1.05, y0 + 1.1, 20.38, 20.46); B(g, VM.rail, -1.5, 2.97, y0, y0 + .12, 20.38, 20.46); for (const x of [-1.5, 2.94]) B(g, VM.rail, x, x + .04, y0 + 1.05, y0 + 1.1, 18.6, 20.42);
      const bs = grp(g, 1.9, y0, 19.6, Math.PI); balconySet(bs); const pt = new T.Mesh(new T.CylinderGeometry(.22, .17, .4, 14), new T.MeshLambertMaterial({ color: '#6E6E70' })); pt.position.set(-1.1, y0 + .2, 20.1); g.add(pt); const sh = makeShrubs(T, [[[-1.1, 20.1], [-1.09, 20.1], 1, 1.0, [.27, .45, .28]]], { seed: 93 }); sh.position.y = y0 + .3; g.add(sh);
      const sgr = grp(g, slA, y0, 18.38); sheers(sgr, slB - slA, 2.8); portals.push({ c: [(slA + slB) / 2, y0 + 1.22, 18.43], n: [0, 0, -1], s: [(slB - slA) / 2, 1.22], k: 5.2, room: ri.liv }); }
    // ---- kitchen at the entrance: run on the north wall, tall fridge, island with black sink, dark grey entrance door
    { const k = grp(g, -1.38, yf, 11.05); kitchenRun(k, 2.75, { hob: 1.6 }); const f = grp(g, -1.38, yf, 11.75, Math.PI / 2); fridge(f); const isl = grp(g, .45, yf, 12.55); island(isl, 1.7);
      { const pv = grp(g, 2.38, 0, 10.97); B(pv, M.doorGrey, -.86, 0, yf, yf + 2.09, -.02, .025, { wuv: false }); B(pv, M.black, -.8, -.66, yf + 1.0, yf + 1.03, .025, .07, { wuv: false }); B(pv, M.black, -.8, -.66, yf + 1.0, yf + 1.03, -.07, -.02, { wuv: false }); out.door3 = (f) => { pv.rotation.y = Math.max(0, Math.min(1, f)) * 1.7; }; }
      for (const [x, z] of [[-.4, 11.7], [1.2, 11.7], [-.4, 12.6], [2.2, 12.3]]) downlight(g, x, Hc, z, lamps, ri.liv, .45); }
    // ---- dining (long white table along z, oak round-back chairs, black track pendant)
    { const d = grp(g, .75, yf, 14.6, Math.PI / 2); diningLong(d, 2.0, 3); const tp = grp(g, .75, 0, 14.6, Math.PI / 2); trackPendant(tp, 1.6, Hc, lamps, ri.liv); }
    frameArt(g, 'x+', -1.37, yf + 1.55, 14.6, .75, 1.0, printTex(23, ['#EFE7DC', '#E3A88A', '#C98B6E', '#F5EFE6']), M.black);
    // ---- lounge: corner sofa against the west wall, oval table, dotted rug, arc lamp, TV wall on the east wall
    { const s = grp(g, -1.36, yf, 18.05, Math.PI / 2); sofaCorner(s); const r = grp(g, .75, yf, 16.9); rugDots(r, 2.4, 2.6); const c = grp(g, .85, yf, 16.9); coffeeOval(c); const al = grp(g, -1.1, yf, 18.2); arcLamp(al); al.rotation.y = -.8;
      const tv = grp(g, 2.92, yf, 16.8, -Math.PI / 2); tvWall(tv, 2.6); ledPanel(g, .8, Hc, 16.6, lamps, ri.liv); plant(g, 2.6, yf, 18.15, 1.3, '#E8E4DC', 31); }
    // ---- corridor: downlights, art, vanity niche glimpse handled by bath
    for (const x of [4.6, 7.0, 9.4]) downlight(g, x, Hc, 14.15, lamps, ri.cor, .55); frameArt(g, 'z-', 8.5, yf + 1.55, 14.89, .6, .8, printTex(41, ['#F0E8DD', '#D9A47E', '#B98B6A', '#E8D8C4']), M.black);
    // ---- bath 1 (cream large-format tile, oak vanity, glass shower, black fittings)
    { wallX(g, M.sandTile, 3.15, 5.0, y0, y0 + 2.6, 11.05, 11.07); const b = grp(g, 3.9, yf, 11.07); bathKit(b, y0 + 2.6, lamps, ri.bath); downlight(g, 4.1, y0 + 2.6, 12.4, lamps, ri.bath, .4); }
    // ---- cloakroom: white full-height doors, oak open shelves with LED strips, oak bench at the end
    { const c = grp(g, 6.6, yf, 11.05); cloakKit(c, 4.6, 2.2, Hc, lamps, ri.cloak, [3.25, 4.25]); }
    // ---- bedroom 1 + 2 (glimpses): beds, wardrobes, LED panels
    { const b = grp(g, 4.8, yf, 15.05); bedKit(b, 1.4); wardrobe(grp(g, 6.45, yf, 18.4, Math.PI), 1.6); ledPanel(g, 4.8, Hc, 16.8, lamps, ri.b1); portals.push({ c: [4.75, y0 + 1.7, 18.43], n: [0, 0, -1], s: [.8, .78], k: 4.2, room: ri.b1 });
      const b2 = grp(g, 9.0, yf, 15.05); bedKit(b2, 1.5); ledPanel(g, 8.8, Hc, 16.8, lamps, ri.b2); portals.push({ c: [8.65, y0 + 1.7, 18.43], n: [0, 0, -1], s: [.9, .78], k: 4.2, room: ri.b2 }); }
    // ---- master: bed against the west wall, wardrobe wall, TV, balcony door south, sheers
    { const b = grp(g, 11.35, yf, 15.9, Math.PI / 2); bedKit(b, 1.6); wardrobe(grp(g, 15.7, yf, 13.4, Math.PI / 2 * 0), 0); wardrobe(grp(g, 12.95, yf, 13.4), 2.6); const tv = grp(g, 15.7, yf, 16.1, -Math.PI / 2); B(tv, M.black, -.8, .8, 1.0, 1.9, 0, .04, { wuv: false });
      ledPanel(g, 13.5, Hc, 15.9, lamps, ri.mas); for (const z of [15.1, 16.7]) lamps.push({ p: [11.5, yf + 1.3, z], k: .28, room: ri.mas });
      const sgr = grp(g, 12.1, yf, 18.36); sheers(sgr, 2.7, 2.8); const sg2 = grp(g, 15.62, yf, 14.2, -Math.PI / 2); sheers(sg2, 3.4, 2.8);
      portals.push({ c: [13.45, y0 + 1.22, 18.43], n: [0, 0, -1], s: [1.25, 1.22], k: 4.6, room: ri.mas }, { c: [15.7, y0 + 1.47, 15.95], n: [-1, 0, 0], s: [1.65, .98], k: 4.6, room: ri.mas });
      plant(g, 15.3, yf, 18.1, 1.2, '#E8E4DC', 33); }
    // ---- ensuite glimpse
    { const e = grp(g, 13.8, yf, 11.07); bathKit(e, y0 + 2.6, lamps, ri.ens); wallX(g, M.sandTile, 11.35, 15.7, y0, y0 + 2.6, 11.05, 11.07); portals.push({ c: [15.7, y0 + 1.95, 12.0], n: [-1, 0, 0], s: [.4, .35], k: 3.5, room: ri.ens }); }
    // oak skirting
    for (const [x0, x1, z] of [[-1.38, 3.0, 18.42], [-1.38, 1.45, 11.06], [3.0, 11.2, 13.39], [3.0, 11.2, 14.91]]) B(g, M.oakLight, x0, x1, yf, yf + .08, z - .008, z + .008, { cast: false, wuv: false });
    // ---- level-9 lift lobby + corridor (lift at x=-1, then south to the unit door)
    { const c = new T.Group(); c.name = 'unit3corr'; g.add(c); const yc = y0 + 2.7;
      wallX(c, M.wall, -1.0, 2.6, y0, yc, 5.75, 5.9); wallX(c, M.oak, -1.0, 1.0, y0, yc, 7.5, 7.65); wallZ(c, M.wall, 2.6, 2.75, y0, yc, 5.75, 10.9); wallZ(c, M.oak, .85, 1.0, y0, yc, 7.5, 10.9);
      wallZ(c, M.wall, -1.15, -1.0, y0, yc, 5.9, 7.5, [{ a: 6.1, b: 7.2, y0: yf, y1: yf + 2.1 }]);
      for (const [x, z] of [[.3, 6.7], [1.8, 6.7], [1.8, 8.6], [1.8, 10.1]]) downlight(c, x, yc, z, lamps, ri[z < 7.5 ? 'lc1' : 'lc2'], 1.6);
      frameArt(c, 'x+', 1.01, yf + 1.55, 9.0, .6, .8, printTex(51, ['#E9E1D3', '#B5694A', '#6E8A7A', '#2B2D31']), M.black); out.doors9 = liftDoors(c, yf, M.steel, M.chrome); }
    const rooms = Object.keys(ri).map(k => [k === 'cab' ? [-2.8, -1.02, y0 - .05, y0 + 2.5, 5.62, 7.68] : [RM[k][0], RM[k][1], y0, y0 + (k === 'bath' || k === 'ens' ? 2.6 : 2.85), RM[k][2], RM[k][3]], k === 'liv' || k === 'mas' ? .6 : k === 'cab' ? .6 : k === 'bath' || k === 'ens' || k === 'cloak' ? .65 : .5]);
    lamps.push({ p: [-1.95, y0 + 2.35, 6.65], k: 4.5, room: ri.cab });
    out.lights3 = setLights(rooms, portals, lamps); out.unit3 = g; out.rooms3 = RM; }
  // =============================================================== 1-BED, Tower B level 4 (east side unit: lounge + breakfast-counter kitchen, bedroom, washroom, balcony)
  { const y0 = U1.y, yf = y0 + .02, Hc = y0 + 2.85, g = new T.Group(); g.name = 'unit1'; INT.group.add(g); const lamps = [], portals = [];
    const RM = { lou: [4.75, 10.62, -16.25, -13.3], bed: [6.6, 10.62, -13.15, -10.55], wsh: [4.75, 6.45, -13.15, -10.55], cor: [3.2, 4.6, -18.0, -10.8] };
    const ri = { cab: 0, cor: 1, lou: 2, bed: 3, wsh: 4 };
    plane(g, M.oakFloor, 4.75, 10.62, -16.25, -13.3, yf); plane(g, M.oakFloor, 6.6, 10.62, -13.15, -10.55, yf); plane(g, M.sandTile, 4.75, 6.45, -13.15, -10.55, yf); plane(g, M.tile, 3.2, 4.6, -18.0, -10.8, yf);
    plane(g, M.ceil, 4.75, 10.62, -16.25, -13.3, Hc, true); plane(g, M.ceil, 6.6, 10.62, -13.15, -10.55, Hc, true); plane(g, M.ceil, 4.75, 6.45, -13.15, -10.55, y0 + 2.6, true); plane(g, M.ceil, 3.2, 4.6, -18.0, -10.8, y0 + 2.7, true);
    const D = (a, b) => ({ a, b, y0: yf, y1: yf + 2.1 });
    wallX(g, M.wall, 4.6, 10.77, y0, Hc, -16.4, -16.25); wallX(g, M.wall, 4.6, 10.77, y0, Hc, -10.55, -10.4); wallZ(g, M.wall, 4.6, 4.75, y0, Hc, -16.25, -10.55, [D(-15.6, -14.7)]);
    wallX(g, M.wall, 4.75, 10.62, y0, Hc, -13.3, -13.15, [D(5.15, 5.85), D(6.95, 7.75)]); wallZ(g, M.wall, 6.45, 6.6, y0, Hc, -13.15, -10.55);
    const OE = [{ a: -16.0, b: -13.5, y0: 0, y1: 2.45, kind: 'door', balc: [-16.15, -13.35, 1.8] }, { a: -12.6, b: -11.0, y0: .9, y1: 2.45, kind: 'win' }];
    const ry = (o) => ({ a: o.a, b: o.b, y0: y0 + o.y0, y1: y0 + o.y1 }); wallZ(g, M.wall, 10.62, 10.77, y0, Hc, -16.4, -10.4, OE.map(ry)); OE.forEach(o => unitOpening(T, g, VM, y0, { axis: 'x', at: 10.77, out: 1 }, o));
    { const sl = new T.Mesh(new T.PlaneGeometry(1.2, 2.4), M.glass); sl.rotation.y = Math.PI / 2; sl.position.set(10.72, y0 + 1.22, -15.35); sl.renderOrder = 3; g.add(sl); B(g, M.frame, 10.68, 10.76, y0, y0 + 2.45, -14.77, -14.73);
      plane(g, M.tileOut, 10.8, 12.5, -16.1, -13.4, y0 + .005); const bs = grp(g, 11.9, y0, -14.6, -Math.PI / 2); balconySet(bs); const sgr = grp(g, 10.55, yf, -13.55, -Math.PI / 2); sheers(sgr, 2.5, 2.8);
      portals.push({ c: [10.62, y0 + 1.22, -14.75], n: [-1, 0, 0], s: [1.25, 1.22], k: 5.0, room: ri.lou }, { c: [10.62, y0 + 1.7, -11.8], n: [-1, 0, 0], s: [.8, .78], k: 4.4, room: ri.bed }); }
    // kitchen along the north wall + breakfast counter with stools
    { const k = grp(g, 4.75, yf, -16.25); kitchenRun(k, 2.8, { hob: 1.9, sink: .7 }); const f = grp(g, 7.55, yf, -16.25); fridge(f);
      B(g, M.white, 5.0, 7.0, yf + .08, yf + .95, -15.0, -14.6, { r: .02 }); B(g, M.oakLight, 4.95, 7.25, yf + .95, yf + .99, -15.05, -14.35, { r: .01 }); contact(g, 6.0, -14.8, 2.0, .4, yf);
      for (const x of [5.5, 6.4]) { cyl(g, M.oakLight, .17, .17, .05, x, yf + .7, -14.05, 18); for (const [lx, lz] of [[-.12, -.12], [.12, -.12], [-.12, .12], [.12, .12]]) B(g, M.black, x + lx - .012, x + lx + .012, yf, yf + .7, -14.05 + lz - .012, -14.05 + lz + .012, { wuv: false }); }
      for (const x of [5.4, 6.6]) { const tp = cyl(g, M.black, .045, .045, .14, x, yf + 2.15, -14.8, 14); cyl(g, M.black, .003, .003, .7, x, yf + 2.15, -14.8, 4); lamps.push({ p: [x, yf + 2.05, -14.8], d: [0, -1, 0], k: .35, room: ri.lou }); }
      downlight(g, 5.8, Hc, -15.8, lamps, ri.lou, .45); }
    // lounge: sofa against the bedroom partition facing north, TV wall on the north wall, oval table, dotted rug, arc lamp
    { const s = grp(g, 7.75, yf, -13.32, Math.PI); sofaCorner(s); s.scale.set(.85, 1, .85); const r = grp(g, 9.0, yf, -14.75); rugDots(r, 2.3, 1.8); const c = grp(g, 9.0, yf, -14.75); coffeeOval(c);
      const tv = grp(g, 9.1, yf, -16.25); tvWall(tv, 2.0); ledPanel(g, 9.0, Hc, -14.8, lamps, ri.lou); const al = grp(g, 10.3, yf, -13.6, 2.4); arcLamp(al); plant(g, 10.3, yf, -16.0, 1.2, '#E8E4DC', 21);
      frameArt(g, 'z+', 6.4, yf + 1.6, -16.24, .6, .8, printTex(23, ['#EFE7DC', '#E3A88A', '#C98B6E', '#F5EFE6']), M.black); }
    // bedroom: bed against the partition (head west), wardrobe, LED panel
    { const b = grp(g, 6.62, yf, -11.85, Math.PI / 2); bedKit(b, 1.4); wardrobe(grp(g, 10.6, yf, -13.1, -Math.PI / 2 * 0), 0); wardrobe(grp(g, 8.4, yf, -11.15), 1.8); ledPanel(g, 8.6, Hc, -11.9, lamps, ri.bed); const sgr = grp(g, 10.55, yf, -11.0, -Math.PI / 2); sheers(sgr, 1.6, 2.8, 1); }
    { const w = grp(g, 5.6, yf, -10.57, Math.PI); bathKit(w, y0 + 2.6, lamps, ri.wsh); }
    // corridor (Tower B, level 4): lift at the north end facing south, unit door on the east wall
    { const yc = y0 + 2.7; wallZ(g, M.wall, 3.05, 3.2, y0, yc, -18.0, -10.8); wallZ(g, M.oak, 4.6, 4.75, y0, yc, -18.0, -16.4); wallZ(g, M.oak, 4.6, 4.75, y0, yc, -10.55, -10.4); wallX(g, M.wall, 3.05, 4.75, y0, yc, -10.95, -10.8);
      wallX(g, M.wall, 3.05, 4.75, y0, yc, -18.15, -18.0, [{ a: 3.35, b: 4.45, y0: yf, y1: yf + 2.1 }]);
      for (const z of [-17.0, -15.0, -13.0, -11.6]) downlight(g, 3.9, yc, z, lamps, ri.cor, 1.6);
      { const pv = grp(g, 4.75, 0, -14.72); B(pv, M.doorGrey, -.045, 0, yf, yf + 2.09, -.86, 0, { wuv: false }); B(pv, M.black, 0, .05, yf + 1.0, yf + 1.03, -.8, -.66, { wuv: false }); B(pv, M.black, -.1, -.045, yf + 1.0, yf + 1.03, -.8, -.66, { wuv: false }); out.door1 = (f) => { pv.rotation.y = -Math.max(0, Math.min(1, f)) * 1.7; }; }
      const lg = new T.Group(); g.add(lg); out.doors4 = liftDoors(lg, yf, M.steel, M.chrome); lg.rotation.y = -Math.PI / 2; lg.position.set(10.55, 0, -17.0);
      lamps.push({ p: [3.9, yf + 1.5, -14.0], k: .4, room: ri.cor });
      // Tower B lift car (static at this landing): brushed panels, mirror, lit ceiling, handrail
      const cx0 = 3.05, cx1 = 4.75, cz0 = -19.75, cz1 = -18.05; B(g, M.granite, cx0, cx1, yf - .04, yf, cz0, cz1); B(g, M.cabWall, cx0, cx1, yf, yf + 2.45, cz0 - .04, cz0); B(g, M.cabWall, cx0 - .04, cx0, yf, yf + 2.45, cz0, cz1); B(g, M.cabWall, cx1, cx1 + .04, yf, yf + 2.45, cz0, cz1);
      B(g, M.mirror, cx0 + .3, cx1 - .3, yf + .95, yf + 2.15, cz0 + .005, cz0 + .02, { wuv: false }); B(g, M.chrome, cx0 + .2, cx1 - .2, yf + .92, yf + .96, cz0 + .05, cz0 + .09, { wuv: false }); B(g, M.cabCeil, cx0, cx1, yf + 2.45, yf + 2.5, cz0, cz1);
      B(g, EM('#fff4e2', 1.5), cx0 + .25, cx1 - .25, yf + 2.44, yf + 2.445, cz0 + .3, cz1 - .3, { wuv: false, cast: false }); lamps.push({ p: [3.9, yf + 2.3, -18.9], k: 2.5, room: ri.cab }); }
    const rooms = Object.keys(ri).map(k => [k === 'cab' ? [3.05, 4.75, y0, y0 + 2.5, -19.75, -18.05] : [RM[k][0], RM[k][1], y0, y0 + (k === 'wsh' ? 2.6 : k === 'cor' ? 2.7 : 2.85), RM[k][2], RM[k][3]], k === 'lou' ? .6 : k === 'cab' ? .6 : .45]);
    out.lights1 = setLights(rooms, portals, lamps); out.unit1 = g; out.rooms1 = RM; }
  useLights(INT.baseLights);
  return out;
}
