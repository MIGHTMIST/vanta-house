# Third-party assets used by r_scene_tour.html

| File | Source | Licence |
|---|---|---|
| r_assets/adventurer.glb.js (guide character: rigged body, Walk/Idle/Interact/Wave clips; recoloured, backpack hidden, normals smoothed) | Quaternius, "Adventurer" (Ultimate Animated Character pack) via npm package `@netforge/asset-library-files@0.2.0` (library/lowpoly/adventurer.glb) | CC0 1.0 (public domain); see r_assets/NOTICE_netforge.txt and r_assets/CC0-1.0.txt |
| r_assets/worker.glb.js (passers-by: rigged base human, Man_Walk/Man_Idle clips; recoloured per person) | Quaternius, "BaseHuman"/worker via the same npm package (library/lowpoly/worker.glb) | CC0 1.0 |

The npm package's own code/index is MIT (NetNet Capital Management); only the CC0 model files were copied.
GLBs are stored as base64 ES modules (r_assets/*.glb.js) because the headless renderer loads pages from file://, where fetch() is blocked.
Other candidates in r_assets_src/ (sedan, suv, mini characters, etc.) were looked at and NOT used (toy-like style).
Cars, buildings, furniture, vegetation and all textures are procedural (r_vanta3d.js, r_interior.js, r_units.js).
Vanta House's own 360 renders (ref3d/F_vanta_own) were used as design reference only; nothing from them is shown on screen.
