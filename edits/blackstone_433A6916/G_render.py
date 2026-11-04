# Video G: John's cold open re-edited. Hook first, captions of his exact words, key-word chips, Modern Clean end card.
import sys, os, json, subprocess, time
import numpy as np
from PIL import Image
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
from docs_common import *
import docs_common as DC
_argv = sys.argv; sys.argv = [sys.argv[0], 'masks']
import renderD as D
sys.argv = _argv
G = S + '/G/'
SEGS = json.load(open(G + 'segs.json')); PLATE_DUR = SEGS['dur']; SEGS = SEGS['segs']
WORDS = json.load(open(G + 'words.json'))['words']
def out_t(i):
    w = WORDS[i]['t']
    for a, b, t0 in SEGS:
        if a - 0.05 <= w < b: return t0 + max(0, w - a)
    raise ValueError(i)
CHUNKS = [(24, 'After 10 years'), (27, "in China's investment"), (30, 'banking industry,'), (32, 'I saw significant'), (35, 'opportunities'),
          (36, "in Africa's"), (38, 'real estate market.'), (41, 'I founded Blackstone'), (44, 'to bring professional'), (47, 'investment analysis'),
          (49, 'to build'), (51, 'trusted development,'), (53, 'deliver lasting value'), (56, 'and grow'), (58, 'alongside Uganda.'),
          (0, 'Our immediate priority'), (3, 'is to successfully'), (6, 'deliver'), (7, 'Vanta House'), (9, 'in our flagship'),
          (12, 'residential development'), (14, 'in Naguru.')]
CAPS = []
for k, (i, txt) in enumerate(CHUNKS):
    t0 = out_t(i) - 0.05
    nxt = out_t(CHUNKS[k + 1][0]) - 0.09 if k + 1 < len(CHUNKS) else PLATE_DUR - 0.05
    CAPS.append((t0, min(nxt, t0 + 2.4), txt))
T_FOUNDED = out_t(42); T_VANTA = out_t(7)
TE = PLATE_DUR; DUR = TE + 4.2; NFR = int(round(DUR * FPS))
D.TE, D.DUR = TE, DUR

_L = {}
def L(k):
    if k in _L: return _L[k]
    if k == 'h1': v = T('FROM INVESTMENT BANKING', 'mo7', 56, WHITE, track=2, shadow=0.85, sblur=14, sdy=4)
    elif k == 'h2': v = T('TO BUILDING IN KAMPALA.', 'mo7', 56, SAND, track=2, shadow=0.85, sblur=14, sdy=4)
    elif k == 'bs': v = pill('BLACKSTONE REAL ESTATE', 'mo7', 30, WHITE, CHAR, track=6, padx=36, pady=20, alpha=235)
    elif k == 'vh': v = pill('VANTA HOUSE  ·  NAGURU, KAMPALA', 'mo7', 30, CHAR, SAND, track=5, padx=36, pady=20)
    elif k.startswith('c:'): v = pill(k[2:], 'mo6', 50, WHITE, (18, 18, 18), track=0, padx=30, pady=18, alpha=165)
    _L[k] = v; return v

_SH = None
def topshade(im):
    global _SH
    if _SH is None:
        y = np.arange(H, dtype=np.float32)
        al = (np.clip(1 - y / 820.0, 0, 1) ** 1.5 * 0.55)[:, None] * np.ones((1, W), np.float32)
        _SH = Image.new('RGBA', (W, H), (10, 10, 10, 0)); _SH.putalpha(Image.fromarray((al * 255).astype(np.uint8)))
    im.alpha_composite(_SH)

def chip(im, t, L_, t0, hold, y=360):
    if not (t0 - 0.02 <= t <= t0 + hold + 0.3): return
    p = clamp((t - t0) / 0.32); o = clamp((t - t0 - hold) / 0.28)
    a = eo(p) * (1 - eo(o))
    place(im, L_, 540, y + 14 * (1 - eo(p)) - 14 * eo(o), a=a, sc=0.86 + 0.14 * R.eback(p, 1.8))

def overlay(im, t):
    topshade(im)
    if t < 3.75:
        p = 0.8 + 0.2 * eo(clamp(t / 0.25)); o = eo(clamp((t - 3.45) / 0.3))
        place(im, L('h1'), 540, 325 - 20 * o, a=p * (1 - o), blur=o * 8); place(im, L('h2'), 540, 405 - 20 * o, a=p * (1 - o), blur=o * 8)
    chip(im, t, L('bs'), T_FOUNDED, 2.6)
    chip(im, t, L('vh'), T_VANTA, PLATE_DUR - T_VANTA - 0.45)
    for a, b, txt in CAPS:
        if a <= t < b: place(im, L('c:' + txt), 540, 1195)

def main(out):
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', G + 'plateG.mkv', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264rgb', '-qp', '0', '-preset', 'veryfast', out], stdin=subprocess.PIPE) if out.endswith('.mkv') else None
    only = None
    if not enc: os.makedirs(out, exist_ok=True); only = set(int(x) for x in sys.argv[2].split(','))
    last = None; t0 = time.time()
    for i in range(NFR):
        t = i / FPS
        raw = dec.stdout.read(W * H * 3) if t < PLATE_DUR else b''
        if len(raw) == W * H * 3: last = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
        if only is not None and i not in only: continue
        if t < TE:
            im = Image.fromarray(last).convert('RGBA'); overlay(im, t)
        else:
            im = Image.fromarray(last).convert('RGBA')
            p = eio(clamp((t - TE) / 0.45))
            im = Image.blend(im, Image.new('RGBA', (W, H), (0, 0, 0, 255)), 0.3 * p)
            panel = D.end_panel(t); y = int(H * (1 - p))
            if y < H: comp(im, panel.crop((0, 0, W, H - y)), 0, y)
        rgb = im.convert('RGB')
        if enc: enc.stdin.write(rgb.tobytes())
        else: rgb.save(os.path.join(out, '%05d.jpg' % i), quality=90)
    dec.kill()
    if enc: enc.stdin.close(); enc.wait()
    print('done', NFR, '%.0fs' % (time.time() - t0), 'founded at %.2f vanta at %.2f' % (T_FOUNDED, T_VANTA))

if __name__ == '__main__':
    main(sys.argv[1])
