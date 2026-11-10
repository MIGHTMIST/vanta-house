# Vanta House - three.js model + frame-render harness

Files: `vanta3d.js` (model + helpers, ES module) - `render.js` (node frame harness) - `encode.sh` (mp4) - `demo.html` (usage example) - `dbg.html`/`dsnap.js` (camera debug snapshots).
three r160 lives in `./node_modules/three`; pages load it through an importmap (`"three": "./node_modules/three/build/three.module.js"`). Scenes must sit in this folder (or adjust the importmap).

## Coordinates
Metres, **y up**, ground = 0. **x = east, z = SOUTH** (plan north is -z). Origin sits between the two blocks (site.jpg px (400,600)); scale 18.3 px/m (verified: plot area 2153 m2 vs 2143.9 m2 on the drawing, road edge 59.3 m).
* Plot quad (m): top-left (-11.5,-23.5) - top-right (13.1,-22.5) - bottom-right (52.1,22.1) - bottom-left (-19.3, 21.9)... see `site.boundaryPoints`. Road (NAGURU VALE ROAD) is the diagonal on the **east/north-east** side; building faces the road with its east elevation = "Elevation 01".
* **north block**: footprint x -11.5..10.8, z -19.3..0.4 (L/stepped, 12 vertices). **south block**: x -13.7..16.8, z 1.9..18.9 (16 vertices). 1.5 m gap between them (light-well). Polygons: `blocks.north.polygon` / `blocks.south.polygon` as `[x,z]` arrays (also `.center .bbox .area .core .entrance`).
* Roof sign band ("VANTA HOUSE", both faces, east+west) on the south block roof, x = 15.3, 16 m long, rises to y = 44.2 (group `sign` inside the roof floor).
* Swimming pool (rounded triangle) NE of the driveway: x 12.6..28.7, z -20.6..-4.5. Gate (8 m opening) on the road boundary at (31.9,-1.3). Guardhouse 11.2 x 3.2 x 3.3 m at (26.6, 3.5). 14-degree basement ramp at lower right (x 35..48, z 10..18). Basement parking at -3.3.

## API (vanta3d.js)
```js
import * as THREE from 'three';
import { buildVanta, makeRenderer, makeSky, lighting, makePeople, makeCars, textSprite, planTexture,
         explodeFloors, setFloorsVisible, viewportSize, GOLD, GOLD_HI, IVORY, INK } from './vanta3d.js';
const v = buildVanta(THREE, { people: 14, cars: true, sign: 'VANTA HOUSE', mood: 'day' });  scene.add(v.group);
```
`buildVanta` returns `{ group, floors, blocks, site, dims, materials, update(t), setMood(m) }`
* `floors[]` - 14 entries ordered **basement, ground, level 1..11, roof**: `{ name, key, level, yBase, height, index, group }`. Group names `floor_B1, floor_G, floor_1 ... floor_11, floor_roof`. Slab top of floor k is at `level`: ground 0, L1 4.0, then +3.3 (L2 7.3 ... L11 37.0), roof 40.3 (parapet to 41.3, sign to 44.2), basement -3.3. Each group holds both blocks' slab, walls, window/door/frame/sill instanced meshes, accent bands, balcony slabs + glass railings (levels), columns/fascia/lobby/core/cars (ground), columns/walls/cars (basement), parapet/sign/roof plant (roof). Geometry is in absolute world y, so `group.position.y = d` lifts a floor; `group.visible=false` hides it.
* `blocks.north|south` as above. `site`: `{ group, ground (terrain, paving, road, planting, driveway - hide it to see the basement), boundaryPoints[Vector3], road{group,geometry,lane(s,off)}, gate, guardhouse, ramp, trees{group,positions}, pool{group,water,setTime(t),update(t)}, people, cars, setMood(m) }`.
* `dims` - `roofLevel, totalHeight, buildingBBox, buildingCenter [x,z], plotArea, gate, mapPx(x,y)` (convert site.jpg pixel to metres), `levels[]`.
* `update(t)` - deterministic animation at time t (seconds): pool ripple, people, cars. Call it from `renderAt`. Nothing uses Math.random at render time (seeded LCG), any frame can be rendered independently/out of order.
* `makeRenderer(THREE, canvas, {antialias, exposure})` ACES tone mapping, sRGB, PCF shadows, sized from `viewportSize()` (= `window.RENDER_W/H` set by the harness, else innerWidth/Height).
* `makeSky(THREE, scene, 'day'|'ink')` sky dome/gradient + fog; `lighting(THREE, scene, 'day'|'ink', {renderer, materials: v.materials, shadowSize, shadowRadius})` -> `{key, fill, hemi, rim}` (warm key + cool fill, soft shadows; ink = low warm key + gold rim, dark ink ground). Call all three (`makeSky`, `lighting`, `v.setMood`) when switching mood; they are idempotent (old sky/lights are replaced).
* `makePeople(THREE, n, paths?)` -> `{group, update(t)}` stylised capsule figures walking 1.3 m/s with leg/arm swing, soft blob shadow. `paths` = `{name: [[x,z],...]}`; `poolDeck` is a closed loop, other paths ping-pong with a short turn-around pause. Defaults (`defaultPaths()`): gate->north entrance, gate->south lobby, gate->parking court, pool deck loop, two road-side pavement paths. `buildVanta` already adds 14 people (`opts.people`); make extra sets for custom paths and `scene.add(group)`.
* `makeCars(THREE)` -> `{group, update(t)}` parked cars in the court bays + 3 moving cars (driveway x2, one on the public road). `parkedCars(THREE, [{x,z,ang,y,c}])` = cheap instanced parked cars.
* `textSprite(THREE, text, {size, font, color, bg, padding, worldHeight, letterSpacing, shadow, sizeAttenuation, depthTest})` crisp canvas-texture Sprite (2x supersampled, mipmapped) for 3D labels. `planTexture(THREE, url)` -> Promise<Texture> (sRGB, anisotropic) for drawing images on a plane: `new THREE.Mesh(new THREE.PlaneGeometry(w,h), new THREE.MeshBasicMaterial({map:tex}))`, rotate -PI/2 and put at y=0.05.
* `explodeFloors(floors, gap, {fromGround})`, `setFloorsVisible(floors, (f,i)=>bool)`, `offsetPoly`, `levelOf(n)`.
* Colours: `GOLD #B08A4E, GOLD_HI #D6B26E, IVORY #FAF8F3, INK #101012`.
* Content rules honoured: sign text is only "VANTA HOUSE" (also on the gate plaque); no prices / unit counts / names. The pool is modelled (owner change).

## Writing a scene (see demo.html)
```html
<div id="stage"><canvas id="gl"></canvas><canvas id="ui"></canvas></div>   <!-- both canvases absolutely stacked -->
<script type="module"> ...
const {w:W,h:H} = viewportSize();  ui.width=W; ui.height=H;
window.DURATION = 6;                         // seconds
window.renderAt = (t) => { v.update(t); /* move camera, draw 3D */ renderer.render(scene,cam); /* draw 2D overlay on #ui */ return true; };
window.ready = true;                         // after everything loaded (await planTexture etc. first)
</script>
```
Rules: `renderAt(t)` must be a pure function of t. Draw 2D text on `#ui` with `clearRect` each call; scale fonts by `W/1080`. Camera tips: portrait 1080x1920, fov 32-40; the tower is 44 m tall x ~31 m wide, so ~165 m camera distance at fov 32 frames the whole site; ~70 m frames the tower.

## Rendering
```
node render.js demo.html frames/ --w 1080 --h 1920 --fps 30 [--from 0 --to 180 --fmt png|jpg --shard 0/2]
./encode.sh frames out.mp4 30        # H.264 crf14 yuv420p faststart
```
The harness opens the page headless (swiftshader), waits `window.ready`, reads `window.DURATION`, per frame awaits `renderAt(t)`, then composites **all canvases inside #stage (DOM order) onto one in-page canvas** and saves it (so the WebGL canvas and 2D overlay are both captured; verified in demo frames). Resumable (existing `f%05d.png` skipped, written atomically), prints ms/frame + ETA. `--shard i/n` lets you run n processes in parallel on different frames of the same dir.

## Performance (software GL, 4 cores)
1080x1920: ~0.9-1.0 s/frame (MSAA on), ~0.75 s/frame with `makeRenderer(..., {antialias:false})`; 540x960 ~0.35 s. Cost drivers: MSAA, `scene.environment` (do NOT set it: 3x slower; the lib applies the env map only to gold/curtain glass), shadows (~0.3 s; lower with `lighting(..,{shadowSize:1024})`), the ~1,500 instanced window/balcony parts (hide floors you do not show). Tips: use `setFloorsVisible` to cull, keep `people`<=20, avoid transparent full-screen layers, render long videos with 2-3 `--shard` processes.

## Known limitations
* Facade is a generated rhythm (balcony / dark band / window bays, 3 m module) following the elevations, not a drawing-exact bay map; interior is hollow (windows are glass boxes). Stone-clad rear column and the dark roof band from the photo render are not modelled.
* Block outlines are traced by eye from site.jpg (about +-0.5 m); both blocks are modelled 11 storeys + roof, same height. Terrain is flat; surroundings (neighbouring buildings, hills) are not modelled.
* Palms are low-poly flat fronds; people have no faces and simple limbs; trees are blobs.
