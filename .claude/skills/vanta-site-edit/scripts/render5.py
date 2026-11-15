# STACKED edit (owner's pick, 15 Nov): three whole 16:9 pictures stacked edge to edge, filling the 9:16 screen.
# Every beat of the train song one band changes (rotating top -> middle -> bottom), so each shot stays ~2.2 s in slow motion.
# usage: python3 render4.py out.mp4 [ta tb]
import sys, numpy as np, cv2, subprocess
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/hype')
from v2core import *
from fx2 import *
import grade as GR
_orig_init = Src.__init__
_graded = set()
SKYM = {}
TOWER = {'GV3A9990', 'GV3A9991', 'GV3A9989'}
def _graded_init(self, clip, t0, t1):
    _orig_init(self, clip, t0, t1)
    key = (clip, round(t0, 2), round(t1, 2))
    if key not in _graded:
        p = GR.params(clip, t0, t1)
        if clip in TOWER:
            SKYM[key] = np.stack([(cv2.resize(GR.sky_mask(f.astype(np.float32)), (256, 144), interpolation=cv2.INTER_AREA) * 255).astype(np.uint8) for f in self.f])
        g = np.stack([GR.sharpen(GR.grade(f.astype(np.float32), p), 0.3) for f in self.f]).astype(np.uint8)
        Src.cache[key] = (g, t0); self.f = g; _graded.add(key)
    else:
        self.f = Src.cache[key][0]
Src.__init__ = _graded_init
R = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/'

BT = 0.73; PH0 = 0.40
def B(k): return PH0 + BT * k
END = 38.2
BH = 608; BY = [16, 656, 1296]                 # band height and top y of each band (32 px dark gaps)
BG = 9.0
CREAM = np.array((255, 244, 216), np.float32)

# worker-heavy playlist from the Sonnet footage passes (no large faces, no documents); repeats are fine
PL = [('GV3A0016', 0.0, 5.8), ('GV3A9992', 3.2, 7.3), ('GV3A0008', 0.0, 3.5), ('GV3A0011', 0.4, 2.0), ('GV3A9989', 0.3, 5.2),
      ('GV3A0035', 0.5, 2.6), ('GV3A0014', 0.3, 4.2), ('GV3A0043', 0.5, 4.5), ('GV3A0017', 0.0, 2.1), ('GV3A9994', 0.2, 4.3),
      ('GV3A0012', 0.0, 4.0), ('GV3A0028', 0.0, 3.2), ('GV3A0013', 0.4, 3.4), ('GV3A9982', 7.0, 16.0), ('GV3A0029', 0.0, 3.4),
      ('GV3A0015', 1.4, 3.8), ('GV3A0033', 0.3, 3.1), ('GV3A0009', 0.0, 3.8), ('GV3A9999', 0.2, 4.4), ('GV3A0036', 15.0, 18.0),
      ('GV3A0005', 0.0, 4.5), ('GV3A9998', 0.2, 3.4), ('GV3A0018', 0.7, 5.5), ('GV3A0021', 0.7, 5.3), ('GV3A9981', 1.0, 6.5),
      ('GV3A0037', 0.0, 6.5), ('GV3A0028', 21.2, 23.0), ('GV3A0042', 0.0, 4.2), ('GV3A9992', 0.3, 3.2), ('GV3A0019', 0.7, 5.6),
      ('GV3A0011', 2.5, 4.5), ('GV3A0023', 4.8, 8.0), ('GV3A0004', 0.0, 3.8), ('GV3A9980', 4.5, 10.0), ('GV3A0028', 10.0, 13.5),
      ('GV3A0003', 0.3, 3.6), ('GV3A0020', 0.6, 4.7), ('GV3A0043', 4.5, 8.5), ('GV3A0036', 0.0, 4.3), ('GV3A0008', 3.5, 7.0),
      ('GV3A0028', 6.6, 9.6), ('GV3A0037', 48.0, 57.0), ('GV3A9995', 0.1, 2.2), ('GV3A0006', 0.2, 2.8), ('GV3A0002', 0.0, 3.1),
      ('GV3A0028', 15.0, 18.5), ('GV3A0041', 8.2, 9.9), ('GV3A9980', 11.0, 15.5), ('GV3A9981', 7.0, 13.5), ('GV3A0044', 0.2, 7.0)]

# ---- band schedule: per band, list of (start, src, speed, slide_dir) ----
import json, os
JW0, JW1 = B(41), B(45)                      # John Yan on site: big panel over the top two bands
def load_playlist():
    """deep-pass moments (Sonnet pass 2) + real site photos; falls back to PL"""
    mom, ph = [], []
    for f in 'abc':
        p = R + 'hype/moments_%s.json' % f
        if os.path.exists(p):
            d = json.load(open(p))
            for m in d.get('moments', []):
                if m.get('score', 0) >= 3 and not m.get('face') and m.get('slowmo') != 'poor' and m['out'] - m['in'] >= 0.9:
                    mom.append((m['score'], m.get('type', ''), (m['clip'], float(m['in']), float(m['out']))))
            for q in d.get('photos', []):
                if q.get('score', 0) >= 3 and not q.get('face'): ph.append(('PHOTO', q['photo']))
    import glob
    user = [('PHOTO', 'user15/' + os.path.basename(f)) for f in sorted(glob.glob(R + 'site/user15/u*.jpg'))]
    ph = user + ph[:10]
    if not mom: return PL
    # interleave: workers / building / detail by score, so the screen never shows three of the same kind
    pools = {k: [m[2] for m in sorted([m for m in mom if m[1] == k], key=lambda m: -m[0])] for k in ('workers', 'building', 'detail')}
    out = []; order = ['workers', 'building', 'workers', 'detail', 'workers', 'building']
    i = 0
    while any(pools.values()):
        k = order[i % len(order)]; i += 1
        if pools.get(k): out.append(pools[k].pop(0))
        if ph and i % 3 == 0: out.append(ph.pop(0))
    return out + ph
PLAY = load_playlist()
used_clips = set()
BANDS = [[], [], []]
BANDS[0].append((0.0,  ('GV3A9991', 2.4, 5.2), 0.45, -1))     # hook: the tower (balcony view, name behind it),
BANDS[1].append((B(1), ('GV3A9982', 0.8, 6.5), 0.55, 1))      # the worker walking to it (song starts),
BANDS[2].append((B(2), ('GV3A9990', 0.2, 5.2), 0.50, -1))     # and the tower from below
PQ = list(PLAY) * 3; PP = [0]
def key(src): return src[1] if src[0] == 'PHOTO' else src[0]
def nxt(t):
    """next playlist item whose clip is not already on screen in another band (keeps playlist order otherwise)"""
    vis = set(key(L[-1][1]) for L in BANDS if L)
    p = PP[0]
    for j in range(p, min(p + 12, len(PQ))):
        if key(PQ[j]) not in vis:
            PQ[p], PQ[j] = PQ[j], PQ[p]; break
    PP[0] += 1
    return PQ[p]
def add(t, band, speed, d):
    if JW0 <= t < JW1 and band < 2: return False            # top two bands are John's panel then
    src = nxt(t)
    if src[0] != 'PHOTO': src = (src[0], src[1], min(src[2], src[1] + 2.6))   # decode/grade only what is shown
    BANDS[band].append((t, src, speed, d)); return True
rot = 0
def step(t, speed, d):
    """change the next band in rotation (skipping John's bands during his panel)"""
    global rot
    for _ in range(3):
        band = rot % 3; rot += 1
        if add(t, band, speed, d): return
k = 5.0
while k < 19: step(B(k), 0.5, 1 if int(k) % 2 else -1); k += 1          # one band per beat
k = 19.0
while k < 31: step(B(k), 0.55, 1 if int(k * 2) % 2 else -1); k += 0.5    # the busiest part: one band per half beat
for q in range(8): step(B(31 + q * 0.25), 1.0, 1 if q % 2 else -1)       # burst (R2 23.2): quarter-beat changes
k = 33.0
while k < 45: step(B(k), 0.5, 1 if int(k) % 2 else -1); k += 1
BANDS[0].append((B(45), ('GV3A9990', 0.2, 5.2), 0.35, -1))     # ending: the building, three ways
BANDS[1].append((B(45.5), ('GV3A9991', 3.0, 5.2), 0.40, 1))
BANDS[2].append((B(46), ('GV3A9989', 0.3, 5.2), 0.40, -1))

# John Yan on site (owner's phone clip, vertical 960x1280): 14.0-19.5 s has workers passing behind him
class JohnClip:
    f = None
    @classmethod
    def at(cls, u):
        if cls.f is None:
            pth = '/root/.claude/uploads/253db02e-90a6-5547-b8b3-69bd9a44cdc8/3edf9be4-beauty_20261017161429.mp4'
            pr = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '14.0', '-i', pth, '-t', '2.2', '-vf', 'fps=30,scale=1080:1440',
                                 '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'], capture_output=True)
            a = np.frombuffer(pr.stdout, np.uint8); n = a.size // (1080 * 1440 * 3); fr = a[:n * 1080 * 1440 * 3].reshape(n, 1440, 1080, 3)
            pj = GR.measure([cv2.resize(fr[k], (360, 480)) for k in range(0, n, max(1, n // 6))])
            out = np.empty_like(fr)
            for k in range(n):                                    # frame by frame: keeps memory low
                out[k] = np.clip(GR.grade(fr[k].astype(np.float32), pj, sky=False) * 0.6 + fr[k] * 0.4, 0, 255).astype(np.uint8)
            cls.f = out
        q = u * 0.6 * FPS; i0 = int(q); w = q - i0; i0 = min(i0, len(cls.f) - 1); i1 = min(i0 + 1, len(cls.f) - 1)
        fr = cls.f[i0].astype(np.float32) * (1 - w) + cls.f[i1].astype(np.float32) * w
        return fr[96:96 + 1248]                                  # 1080x1248 panel = top two bands
T_JN = text_rgba('JOHN YAN', 'Inter-ExtraBold.otf', 66)
T_JT = text_rgba('FOUNDER  ·  BLACKSTONE REAL ESTATE', 'Inter-SemiBold.otf', 30, fill=(236, 236, 236), tracking=2)

def cur(b, t):
    L = BANDS[b]; i = -1
    for j, e in enumerate(L):
        if e[0] <= t: i = j
    return i

_ph = {}
def photo(path, u):
    """real site photo shown whole-width: 16:9 window that drifts slowly (tilt for tall photos) + gentle push-in"""
    if path not in _ph:
        im = cv2.cvtColor(cv2.imread(R + 'site/' + path), cv2.COLOR_BGR2RGB).astype(np.float32)
        h, w = im.shape[:2]; s = 1600 / w
        im = cv2.resize(im, (1600, int(h * s)), interpolation=cv2.INTER_AREA)
        pp = GR.photo_params(path, im); g = GR.grade(im, pp, sky=False)
        _ph[path] = im * 0.45 + g * 0.55
    im = _ph[path]; h, w = im.shape[:2]; ch = 900
    e = ease(min(u / 2.6, 1.0))
    if h > 1300: y0 = (h - ch) * (0.12 + 0.6 * e)            # tall photo: tilt down the wall
    else: y0 = (h - ch) * (0.25 + 0.35 * e)                    # landscape: gentle drift down
    z = 1.0 + 0.04 * e
    cw2, ch2 = w / z, ch / z; x0 = (w - cw2) / 2; y0 = y0 + (ch - ch2) / 2
    M = np.float32([[PW / cw2, 0, -x0 * PW / cw2], [0, PH / ch2, -y0 * PH / ch2]])
    return cv2.warpAffine(im, M, (PW, PH), flags=cv2.INTER_AREA if z < 1.01 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def band_pic(b, i, t):
    st, src, sp, d = BANDS[b][i]
    if src[0] == 'PHOTO': return photo(src[1], t - st)
    c, a, z = src
    return Src(c, a, z).at(a + min((t - st) * sp, z - a - 0.05))

def band_mask(b, t):
    """sky mask (1080x608 float 0..1) of the tower picture now in band b, or None"""
    i = cur(b, t)
    if i < 0: return None
    st, src, sp, d = BANDS[b][i]
    if src[0] == 'PHOTO' or src[0] not in TOWER: return None
    c, a, z = src; key = (c, round(a, 2), round(z, 2))
    if key not in SKYM: Src(c, a, z)
    m = SKYM.get(key)
    if m is None: return None
    q = int(round(min((t - st) * sp, z - a - 0.05) * FPS)); q = min(max(q, 0), len(m) - 1)
    return cv2.resize(m[q].astype(np.float32) / 255, (W, BH), interpolation=cv2.INTER_LINEAR)

def sweep(img, u, dur=0.9):
    """passing light: a soft warm diagonal band moves across the picture once (R12/R13 'light sweep')"""
    if not (0 <= u < dur): return img
    p = u / dur; h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h:4, 0:w:4].astype(np.float32)
    d = (xx + yy * 0.6) / (w + h * 0.6) - (p * 1.5 - 0.25)
    g = np.exp(-(d / 0.07) ** 2) * np.sin(np.pi * p) * 0.33
    g = cv2.resize(g, (w, h), interpolation=cv2.INTER_LINEAR)[..., None]
    return img + (np.array([255, 246, 228], np.float32) - img) * g

def band_img(b, t):
    i = cur(b, t)
    if i < 0: return None, None
    img = cv2.resize(band_pic(b, i, t), (W, BH), interpolation=cv2.INTER_CUBIC)
    st, src, sp, d = BANDS[b][i]
    if t < B(5) + 0.1:                                           # R15 intro: grey with only hi-vis in colour, snaps to colour at B5
        amt = 1.0 if t < B(5) else 1 - (t - B(5)) * FPS / 3
        img = GR.selective(img, max(amt, 0))
    if src[0] in TOWER and t >= B(5):
        img = sweep(img, t - max(st, B(5)) - 0.1)                          # light passes over the building each time it appears
    k = (t - BANDS[b][i][0]) * FPS
    if k < 7:                                                    # new shot slides in over the old one (R4), blurred
        d = BANDS[b][i][3]; e = eout(k / 7); dx = int(d * W * (1 - e))
        new = motion_blur_x(img, 50 * (1 - e)) if e < 0.95 else img
        old = cv2.resize(band_pic(b, i - 1, t), (W, BH), interpolation=cv2.INTER_CUBIC) if i > 0 else np.full_like(img, BG)
        out = old.copy()
        if dx >= 0: out[:, dx:] = new[:, :W - dx]
        else: out[:, :W + dx] = new[:, -dx:]
        if k < 2: out = out * (1 - 0.35) + CREAM * 0.35                   # small warm flash on that band
        return out, k
    return img, k

LYR = [('TO TELL YOU', 14.0, 15.36, 'floor', 0.22), ("IT'S NOW", 15.36, 16.24, 'floor', 0.16),
       ('OR NEVER.', 16.24, 17.9, 'wall', 0.10), ('SO MUCH', 24.96, 25.6, 'floor', 0.2), ('FOR CLOSURE,', 25.6, 27.2, 'wall', -0.06),
       ('I LOST', 27.2, 28.08, 'wall', 0.05), ('COMPOSURE.', 28.08, 29.9, 'wall', -0.05)]
WORDS = [(B(25), 'REAL'), (B(26), 'WORKERS.'), (B(27), 'REAL'), (B(28), 'STEEL.'), (B(29), 'REAL'), (B(30), 'CONCRETE.')]
_wimg = {w: text_rgba(w, 'Inter-Black.otf', 96) for _, w in WORDS}
T_V = text_rgba('VANTA HOUSE', 'Inter-ExtraBold.otf', 104)
T_N = text_rgba('NAGURU, KAMPALA', 'Inter-Medium.otf', 46, fill=(236, 236, 236), tracking=3)
T_HV = text_rgba('ON SITE', 'Inter-Black.otf', 210, fill=TEAL)
T_END = text_rgba('NAGURU  ·  KAMPALA', 'Inter-SemiBold.otf', 34, fill=(240, 240, 240), tracking=16)
def _behind(size, y):
    tx = text_rgba('VANTA HOUSE', 'Inter-Black.otf', size); h, w = tx.shape[:2]
    if w > 1040: tx = cv2.resize(tx, (1040, int(h * 1040 / w)), interpolation=cv2.INTER_AREA); h, w = tx.shape[:2]
    lay = np.zeros((BH, W, 4), np.float32); x0 = (W - w) // 2; lay[y:y + h, x0:x0 + w] = tx; return lay
BEHIND = _behind(140, 10)         # hook: balcony view of the tower (GV3A9991)
BEHIND_END = _behind(140, 10)     # end: tilt up the balconies (GV3A9991)
_lc = {}
def lyr(j):
    if j not in _lc:
        tx, a, b, mode, amt = LYR[j]; nw = neon(tx, 116); h, w = nw.shape[:2]; cx, cy = 540, 960
        src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        if mode == 'floor':
            ins = w * amt / 2; dst = np.float32([[cx - w / 2 + ins, cy - h * 0.38], [cx + w / 2 - ins, cy - h * 0.38], [cx + w / 2, cy + h / 2], [cx - w / 2, cy + h / 2]])
        else:
            d = h * amt * 2; dst = np.float32([[cx - w / 2, cy - h / 2 + d], [cx + w / 2, cy - h / 2 - d], [cx + w / 2, cy + h / 2 + d * 0.4], [cx - w / 2, cy + h / 2 - d * 0.4]])
        _lc[j] = warp_word(nw, cv2.getPerspectiveTransform(src, dst))
    return _lc[j]

def frame(fi, rng):
    t = fi / FPS
    c = np.full((H, W, 3), BG, np.float32)
    for b in range(3):
        img, k = band_img(b, t)
        if img is not None: c[BY[b]:BY[b] + BH] = img
    if JW0 <= t < JW1:                                           # John's panel slides down over the top two bands
        u = t - JW0; e = eout(u * FPS / 8); pan = JohnClip.at(u)
        dy = int(-1264 * (1 - e)); y0 = 16 + dy
        ya, yb = max(y0, 0), min(y0 + 1248, H)
        if yb > ya: c[ya:yb] = pan[ya - y0:yb - y0]
        if u * FPS < 2: c = c * 0.7 + CREAM * 0.3
        ul = u - 0.5
        if ul > 0:
            al = ease(ul / 0.4) * (1 - ease((t - (JW1 - 0.25)) / 0.25))
            c = bar(c, 92, 1080, al, w=72, grow=ease(ul / 0.5))
            c = paste(c, T_JN, 56 + T_JN.shape[1] / 2, 1132, alpha=al, dy=18 * (1 - eout(ul / 0.4)))
            c = paste(c, T_JT, 56 + T_JT.shape[1] / 2, 1196, alpha=ease((ul - 0.2) / 0.4) * (1 - ease((t - (JW1 - 0.25)) / 0.25)))
    # R2: halftone sepia switch on the beat with the big title, bands keep changing underneath (9.9-12.8 s)
    if B(13) <= t < B(17):
        c = halftone_fast(c, pitch=9.0)
        u = t - B(13.25)
        if u > 0:
            al = ease(u / 0.4) * (1 - ease((t - B(16.6)) / 0.2))
            c = paste(c, shine(T_HV, (u - 0.5) / 0.9) if 0.5 < u < 1.4 else T_HV, 540, 948, alpha=al, scale=1.0 + 0.12 * (1 - eout(u / 0.4)), shadow=0.25)
    ks = int(round((t - B(13)) * FPS))
    if 0 <= ks < 5: c = c * (1 - [1, .9, .6, .35, .15][ks]) + CREAM * [1, .9, .6, .35, .15][ks]   # cream flash into it (R2 7.83)
    ks = int(round((t - B(17)) * FPS)); c = flash(c, ks, warm=True) if 0 <= ks < 5 else c
    ks = int(round((t - B(33)) * FPS))                            # end of the burst: cream flash + impact shake
    if 0 <= ks < 6:
        if ks == 0: c = c * 0.2 + CREAM * 0.8
        dx, dy = shake(ks - 1); c = np.roll(np.roll(c, dx, 1), dy, 0)
    ks = int(round((t - B(19)) * FPS)); dx, dy = shake(ks); c = np.roll(np.roll(c, dx, 1), dy, 0) if (dx or dy) else c
    ks = int(round((t - B(45)) * FPS)); c = light_leak(c, ks) if 0 <= ks < 10 else c
    # hook: VANTA HOUSE standing BEHIND the tower in the top picture (R18 text-behind-subject), from the song's first beat
    if B(1) <= t < B(5):
        u = t - B(1); m = band_mask(0, t)
        if m is not None:
            al = ease(u / 0.6) * (1 - ease((t - (B(5) - 0.25)) / 0.25))
            sl = BEHIND[..., 3] * m * al
            top = c[BY[0]:BY[0] + BH]
            c[BY[0]:BY[0] + BH] = top * (1 - sl[..., None]) + BEHIND[..., :3] * 255 * sl[..., None]
        c = paste(c, T_END, 540, BY[0] + BH - 34, alpha=ease((u - 0.4) / 0.6) * (1 - ease((t - (B(5) - 0.25)) / 0.25)), shadow=0.6)
    # the song's own words glowing in the scene (R9), over the middle band
    for j, (tx, a, b, mode, amt) in enumerate(LYR):
        if a <= t < b:
            c = comp_rgba(c, np.roll(lyr(j), int((t - a) * -14), 1), neon_flicker(int((t - a) * FPS)) * (1 - ease((t - (b - 0.12)) / 0.12)))
    # our words, low on the screen (bottom band), one per beat
    for j, (tw, w) in enumerate(WORDS):
        te = WORDS[j + 1][0] if j + 1 < len(WORDS) else tw + BT
        if tw <= t < te:
            k = (t - tw) * FPS
            c = paste(c, _wimg[w], 540, 1600, alpha=min(1, k / 2 + 0.35), scale=1.0 + 0.2 * (1 - eout(k / 5)))
    # end: the tower's outline draws itself in brand teal, glowing (R17/R18 'outline the subject')
    if t >= B(45.2):
        m = band_mask(0, t)
        if m is not None:
            p = ease((t - B(45.2)) / 1.3)
            sky = (m > 0.5).astype(np.uint8)
            cs, _ = cv2.findContours(sky, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if cs:
                cnt = max(cs, key=cv2.contourArea)[:, 0, :]
                keep = (cnt[:, 0] > 3) & (cnt[:, 0] < W - 4) & (cnt[:, 1] > 3) & (cnt[:, 1] < BH - 4)
                pts = cnt[keep]
                if len(pts) > 20:
                    pts = pts[np.argsort(pts[:, 0], kind='stable')] if False else pts
                    n = int(len(pts) * p)
                    lay = np.zeros((BH, W), np.float32)
                    if n > 2:
                        seg = pts[:n].reshape(-1, 1, 2).astype(np.int32)
                        cv2.polylines(lay, [seg], False, 1.0, 3, lineType=cv2.LINE_AA)
                    glow = np.clip(cv2.GaussianBlur(lay, (0, 0), 7) * 3.0, 0, 1)
                    a = np.maximum(lay, glow * 0.65)[..., None]
                    top = c[BY[0]:BY[0] + BH]
                    col = np.array(TEAL, np.float32) * (1 - lay[..., None]) + np.array([235, 255, 252], np.float32) * lay[..., None]
                    c[BY[0]:BY[0] + BH] = top * (1 - a) + col * a
    # end title over the middle band
    ue = t - B(46.5)
    if ue > 0:
        m = band_mask(1, t)
        if m is not None:
            sl = BEHIND_END[..., 3] * m * ease(ue / 0.7)
            mid = c[BY[1]:BY[1] + BH]
            c[BY[1]:BY[1] + BH] = mid * (1 - sl[..., None]) + BEHIND_END[..., :3] * 255 * sl[..., None]
        c = paste(c, T_END, 540, BY[1] + BH - 34, alpha=ease((ue - 0.5) / 0.6), shadow=0.6)
    if t < 0.4: c = c * ease(t / 0.4)
    if t > END - 0.6: c = c * ease((END - t) / 0.6)
    return grain(c, rng, 3.0)

def main(out, ta=0.0, tb=END):
    AUD = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/hype/train_mix.wav'
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', '30', '-i', '-',
        *([] if os.environ.get('NOAUDIO') else ['-ss', '%.3f' % ta, '-t', '%.3f' % (tb - ta), '-i', AUD, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k']), '-movflags', '+faststart',
        '-vf', "colorbalance=rs=-0.03:gs=0.0:bs=0.04:rm=0.02:bm=-0.015:rh=0.03:gh=0.005:bh=-0.03",
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-maxrate', '9M', '-bufsize', '18M', '-pix_fmt', 'yuv420p',
        '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', out], stdin=subprocess.PIPE)
    rng = np.random.default_rng(5)
    for fi in range(int(round(ta * FPS)), int(round(tb * FPS))):
        enc.stdin.write(np.clip(frame(fi, rng), 0, 255).astype(np.uint8).tobytes())
        if fi % 60 == 0:
            print('%.1f' % (fi / FPS), flush=True)
            if len(Src.cache) > 12:
                for kk in list(Src.cache)[:-9]: del Src.cache[kk]
    enc.stdin.close(); enc.wait()

if __name__ == '__main__':
    a = sys.argv[2:]; main(sys.argv[1], *(float(x) for x in a))
