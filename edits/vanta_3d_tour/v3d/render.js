#!/usr/bin/env node
// Frame-render harness. usage: node render.js scene.html outdir [--w 1080 --h 1920 --fps 30 --from 0 --to N --fmt png|jpg --shard i/n --dur S]
// Scene contract: sets window.ready=true when loaded; window.DURATION (s); window.renderAt(t) (may be async) draws frame at time t.
// Canvases: all <canvas> elements inside #stage (or the whole page) are composited in DOM order onto one canvas in-page
// (WebGL canvas first, 2D overlay canvas(es) after) -> frame file f%05d.png|jpg. Resumable: existing frames are skipped.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const a = process.argv.slice(2); const pos = a.filter((x, i) => !x.startsWith('--') && !(i > 0 && a[i - 1].startsWith('--')));
const opt = (k, d) => { const i = a.indexOf('--' + k); return i >= 0 ? a[i + 1] : d; };
const [scene, outdir] = pos; if (!scene || !outdir) { console.error('usage: node render.js scene.html outdir [--w --h --fps --from --to --fmt png|jpg --shard i/n]'); process.exit(1); }
const W = +opt('w', 1080), H = +opt('h', 1920), FPS = +opt('fps', 30), FROM = +opt('from', 0), FMT = opt('fmt', 'png'), SHARD = (opt('shard', '0/1')).split('/').map(Number);
fs.mkdirSync(outdir, { recursive: true });
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--disable-gpu-vsync'] });
  const p = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  p.on('console', m => { const t = m.text(); if (!/GPU stall|swiftshader/i.test(t)) console.log('[page]', t); }); p.on('pageerror', e => console.log('[pageerror]', e.message));
  await p.addInitScript(`window.RENDER_W=${W};window.RENDER_H=${H};window.FPS=${FPS};`);
  await p.goto('file://' + path.resolve(scene)); await p.waitForFunction('window.ready===true', { timeout: 180000 });
  const dur = +opt('dur', await p.evaluate('window.DURATION')); const N = Math.round(dur * FPS), TO = Math.min(+opt('to', N), N);
  await p.evaluate(({ fmt }) => {
    window.__cap = () => {
      const root = document.getElementById('stage') || document, cs = [...root.querySelectorAll('canvas')];
      if (!window.__off) { window.__off = document.createElement('canvas'); }
      const o = window.__off; if (o.width !== innerWidth || o.height !== innerHeight) { o.width = innerWidth; o.height = innerHeight; }
      const g = o.getContext('2d'); g.globalCompositeOperation = 'source-over'; g.clearRect(0, 0, o.width, o.height);
      for (const c of cs) { if (getComputedStyle(c).display === 'none') continue; g.drawImage(c, 0, 0, o.width, o.height); }
      return o.toDataURL(fmt === 'jpg' ? 'image/jpeg' : 'image/png', 0.95).split(',')[1];
    };
  }, { fmt: FMT });
  console.log(`scene ${scene}: ${dur}s @${FPS}fps = ${N} frames, ${W}x${H}, rendering ${FROM}..${TO - 1} shard ${SHARD.join('/')}`);
  const t0 = Date.now(); let done = 0, skipped = 0, total = 0;
  for (let i = FROM; i < TO; i++) if (i % SHARD[1] === SHARD[0]) total++;
  for (let i = FROM; i < TO; i++) {
    if (i % SHARD[1] !== SHARD[0]) continue;
    const f = path.join(outdir, 'f' + String(i).padStart(5, '0') + '.' + FMT);
    if (fs.existsSync(f) && fs.statSync(f).size > 1000) { skipped++; continue; }
    const b64 = await p.evaluate(async (t) => { await window.renderAt(t); return window.__cap(); }, i / FPS);
    fs.writeFileSync(f + '.tmp', Buffer.from(b64, 'base64')); fs.renameSync(f + '.tmp', f); done++;
    if (done % 10 === 0 || i === TO - 1) { const el = (Date.now() - t0) / 1000; console.log(`frame ${i}  ${done + skipped}/${total}  ${(el / done * 1000).toFixed(0)} ms/frame  eta ${((total - done - skipped) * el / done).toFixed(0)}s`); }
  }
  console.log(`done: ${done} rendered, ${skipped} skipped, ${((Date.now() - t0) / Math.max(1, done)).toFixed(0)} ms/frame`);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
