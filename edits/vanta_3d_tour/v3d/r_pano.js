// r_pano.js - Vanta House's own 360 interior renders (cubemap strips 2560 x 6*2560: faces 0-3 walls left->right, 4 ceiling, 5 floor)
// loaded as THREE.CubeTexture for use as scene.background while the camera "stands" in that room (rotation + FOV only).
// MAP: three.js face slot order [px, nx, py, ny, pz, nz] -> strip face index, with per-face transforms (flipX, rot quarter turns)
export const PANO_MAP = { order: [1, 3, 4, 5, 0, 2], flipX: [0, 0, 0, 0, 0, 0], rot: [0, 0, 0, 0, 0, 0] };  // verified: walls seamless, not mirrored (with the -x lookup in panoDome)
export function loadPano(THREE, url, size = 1024, map = PANO_MAP) {
  return new Promise((res, rej) => { const img = new Image(); img.onload = () => {
    const W = img.width, faces = [];
    for (let k = 0; k < 6; k++) { const i = map.order[k]; const c = document.createElement('canvas'); c.width = c.height = size; const g = c.getContext('2d'); g.imageSmoothingQuality = 'high';
      g.translate(size / 2, size / 2); g.rotate((map.rot[k] || 0) * Math.PI / 2); if (map.flipX[k]) g.scale(-1, 1); if (map.flipY && map.flipY[k]) g.scale(1, -1); g.translate(-size / 2, -size / 2);
      g.drawImage(img, 0, i * W, W, W, 0, 0, size, size); faces.push(c); }
    const t = new THREE.CubeTexture(faces); t.colorSpace = THREE.SRGBColorSpace; t.generateMipmaps = false; t.minFilter = THREE.LinearFilter; t.needsUpdate = true; res(t); };
    img.onerror = rej; img.src = url; });
}
// inside-out sphere that always surrounds the camera and samples the cube by view direction (independent of three's background path)
export function panoDome(THREE) {
  const mat = new THREE.ShaderMaterial({ uniforms: { uCube: { value: null }, uCube2: { value: null }, uMix: { value: 0 }, uYaw: { value: 0 }, uYaw2: { value: 0 }, uExp: { value: 1 }, uAlpha: { value: 1 } },
    vertexShader: 'varying vec3 vD; void main(){ vD = position; vec4 p = projectionMatrix * modelViewMatrix * vec4(position, 1.); gl_Position = p.xyww; }',
    fragmentShader: `uniform samplerCube uCube, uCube2; uniform float uMix, uYaw, uYaw2, uExp, uAlpha; varying vec3 vD;
      vec3 rotY(vec3 d, float a){ float c = cos(a), s = sin(a); return vec3(-(c*d.x + s*d.z), d.y, -s*d.x + c*d.z); }
      void main(){ vec3 d = normalize(vD); vec3 a = textureCube(uCube, rotY(d, uYaw)).rgb; vec3 b = uMix > 0. ? textureCube(uCube2, rotY(d, uYaw2)).rgb : a;
        gl_FragColor = vec4(mix(a, b, uMix) * uExp, uAlpha);
        #include <colorspace_fragment>
      }`, side: THREE.BackSide, depthWrite: false, depthTest: false, transparent: true, toneMapped: false });
  const m = new THREE.Mesh(new THREE.SphereGeometry(10, 64, 32), mat); m.frustumCulled = false; m.renderOrder = 1000; m.name = 'panoDome';
  m.onBeforeRender = (r, s, cam) => { m.position.copy(cam.position); m.updateMatrixWorld(); };
  return m;
}
