// r_people2.js - rigged humans (CC0 Quaternius models via @netforge/asset-library-files, see r_CREDITS.md) driven deterministically from t.
import * as THREE from 'three';
import { GLTFLoader } from './node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import { MeshoptDecoder } from './node_modules/three/examples/jsm/libs/meshopt_decoder.module.js';
import { clone as skClone } from './node_modules/three/examples/jsm/utils/SkeletonUtils.js';
import { mergeVertices } from './node_modules/three/examples/jsm/utils/BufferGeometryUtils.js';
const L = new GLTFLoader(); L.setMeshoptDecoder(MeshoptDecoder);
const CACHE = {};
export async function loadGLB(name) { if (CACHE[name]) return CACHE[name]; const b64 = (await import('./r_assets/' + name + '.glb.js')).default; const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0)).buffer; const g = await L.parseAsync(bin, ''); CACHE[name] = g;
  // smooth the faceted low-poly shading once (merge by position+skin data, recompute normals)
  g.scene.traverse(o => { if (o.isSkinnedMesh) { const geo = o.geometry; geo.deleteAttribute('normal'); const uv = geo.attributes.uv; if (uv) geo.deleteAttribute('uv'); const m = mergeVertices(geo, 1e-4); m.computeVertexNormals(); o.geometry = m; } });
  return g; }
// palette: material name -> colour hex (or null = hide)
export const GUIDE_PALETTE = { Green: '#E9E4D9', LightGreen: '#DDD6C8', Brown: '#2B3446', Brown2: '#4A3424', Black: '#1E1A17', Grey: '#5A3E2A', Skin: '#8A5A3F', Hair: '#18120E', Eyebrows: '#18120E', Eye: '#1a1410', Gold: '#8a7040' };
export function makeHuman(gltf, o = {}) {
  const root = skClone(gltf.scene); const pal = o.palette || {}; const hide = o.hide || [];
  root.traverse(m => { if (!m.isMesh) return; if (hide.some(h => m.name.startsWith(h))) { m.visible = false; return; }
    const src = m.material, col = pal[src.name] ?? ('#' + src.color.getHexString()); m.material = new THREE.MeshLambertMaterial({ color: col }); m.material.name = src.name; m.castShadow = true; m.receiveShadow = true; m.frustumCulled = false; });
  const mixer = new THREE.AnimationMixer(root); const acts = {};
  gltf.animations.forEach(a => { const k = a.name.split('|').pop(); const act = mixer.clipAction(a); act.play(); act.weight = 0; act.enabled = true; acts[k] = act; });
  // scale to height
  const s = (o.height || 1.78) / (o.nativeHeight || 1.83); root.scale.setScalar(s * (o.k || 1));
  const wrap = new THREE.Group(); wrap.add(root); wrap.name = o.name || 'human';
  // pose: {x,y,z,heading, clips:[[name, time, weight],...]}
  function set(p) { wrap.position.set(p.x, p.y || 0, p.z); wrap.rotation.y = p.heading || 0;
    for (const k in acts) acts[k].weight = 0; let tot = 0; (p.clips || []).forEach(c => { tot += c[2]; });
    (p.clips || []).forEach(([k, time, w]) => { const a = acts[k]; if (!a) return; a.weight = w / (tot || 1); a.time = ((time % a.getClip().duration) + a.getClip().duration) % a.getClip().duration; });
    mixer.update(0); wrap.updateMatrixWorld(true); }
  return { group: wrap, root, mixer, acts, set, clipLen: (k) => acts[k] ? acts[k].getClip().duration : 1 };
}
// path walking helper: polyline [[x,z],...] + speed -> state at time u (seconds into the walk)
export function pathAt(pts, s) { let acc = 0; for (let i = 1; i < pts.length; i++) { const a = pts[i - 1], b = pts[i], L = Math.hypot(b[0] - a[0], b[1] - a[1]); if (s <= acc + L || i === pts.length - 1) { const u = Math.max(0, Math.min(1, (s - acc) / (L || 1))); return { x: a[0] + (b[0] - a[0]) * u, z: a[1] + (b[1] - a[1]) * u, heading: Math.atan2(b[0] - a[0], b[1] - a[1]) }; } acc += L; } }
export function pathLen(pts) { let L = 0; for (let i = 1; i < pts.length; i++) L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); return L; }
