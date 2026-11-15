# Vanta site edit v2 (16 Nov): full 9:16, a different trick on every section, every cut on the train-song beat.
# usage: [NOAUDIO=1] python3 render6.py out.mp4 [t_start t_end]
import sys, os, numpy as np, cv2, subprocess
H6 = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/hype'
sys.path.insert(0, H6)
from v2core import W, H, FPS, ease, eout, motion_blur_x, halftone_fast
from fx2 import *
from fillcore import SrcF
import grade as GR
R = GR.R
BT = 0.73; PH0 = 0.40
def B(k): return PH0 + BT * k
END = 38.2
CREAM = np.array((255, 244, 216), np.float32)
BG = 8.0

# ---------------- sources ----------------
_pc = {}
def prm(c, a, b):
    k = (c, a, b)
    if k not in _pc: _pc[k] = GR.params(c, a, b)
    return _pc[k]

def clipframe(src, u, w, h, cx=(0.5, 0.5), sp=0.5, zoom=1.0, ramp=False, dur=1.0):
    """graded crop of a site clip filling w x h. u = seconds since the shot started"""
    c, a, b = src
    if ramp:                                          # speed ramp: real speed x2.2 for 5 frames, then slow
        k = u * FPS; tt = (min(k, 5) * 2.2 + max(k - 5, 0) * sp) / FPS
    else: tt = u * sp
    tt = a + min(tt, b - a - 0.06)
    p = cx[0] + (cx[1] - cx[0]) * ease(u / max(dur, 0.01))
    ch = 1080 / zoom; cw = ch * w / h
    if cw > 1920: cw = 1920; ch = cw * h / w
    s = SrcF(c, a, b)
    img = s.crop(tt, p * 1920 - cw / 2, (1080 - ch) / 2, int(round(cw)), int(round(ch)), w, h)
    RAW[0] = img
    return GR.sharpen(GR.grade(img, prm(c, a, b)), 0.25)
RAW = [None]

_ph = {}
def photo(name, u, w, h, cx=(0.4, 0.6), dur=1.0):
    if name not in _ph:
        im = cv2.cvtColor(cv2.imread(R + 'site/user15/' + name), cv2.COLOR_BGR2RGB).astype(np.float32)
        pp = GR.photo_params(name, im); _ph[name] = im * 0.45 + GR.grade(im, pp, sky=False) * 0.55
    im = _ph[name]; ih, iw = im.shape[:2]
    p = cx[0] + (cx[1] - cx[0]) * ease(u / max(dur, 0.01)); z = 1.0 + 0.05 * ease(u / max(dur, 0.01))
    ch = ih / z; cw = ch * w / h
    if cw > iw: cw = iw / z; ch = cw * h / w
    x0 = min(max(p * iw - cw / 2, 0), iw - cw); y0 = (ih - ch) / 2
    M = np.float32([[w / cw, 0, -x0 * w / cw], [0, h / ch, -y0 * h / ch]])
    return cv2.warpAffine(im, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

class John:
    f = None
    @classmethod
    def at(cls, u):
        if cls.f is None:
            pth = '/root/.claude/uploads/253db02e-90a6-5547-b8b3-69bd9a44cdc8/3edf9be4-beauty_20261017161429.mp4'
            pr = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '14.0', '-i', pth, '-t', '2.2', '-vf', 'fps=30,crop=720:1280:120:0,scale=1080:1920',
                                 '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'], capture_output=True)
            a = np.frombuffer(pr.stdout, np.uint8); n = a.size // (W * H * 3); fr = a[:n * W * H * 3].reshape(n, H, W, 3)
            pj = GR.measure([cv2.resize(fr[k], (270, 480)) for k in range(0, n, max(1, n // 6))])
            out = np.empty_like(fr)
            for k in range(n): out[k] = np.clip(GR.grade(fr[k].astype(np.float32), pj, sky=False) * 0.6 + fr[k] * 0.4, 0, 255).astype(np.uint8)
            cls.f = out
        q = u * 0.6 * FPS; i0 = min(int(q), len(cls.f) - 1); i1 = min(i0 + 1, len(cls.f) - 1); w = q - int(q)
        return cls.f[i0].astype(np.float32) * (1 - w) + cls.f[i1].astype(np.float32) * w

# ---------------- timeline v7 (16 Nov): picky shots only, every cut on a beat of the train song ----------------
# SCRIPT: hook (who + promise) -> the work in grey, hi-vis in colour -> the building appears floor by floor + name ->
# where it is (Kampala views) -> the crews (split) -> ON SITE freeze -> real photos -> one shot per beat with the
# song's words -> REAL WORKERS / STEEL / CONCRETE -> fast burst -> three strips -> the building -> John -> end card.
SH = []
def full(k0, k1, src, **o): SH.append(dict(kind='full', k0=k0, k1=k1, src=src, **o))
full(-0.548, 1, ('GV3A9982', 1.8, 6.5), cx=(0.27, 0.34), sp=0.55)                    # HOOK: worker walks to the tower (back only)
full(1, 2, ('GV3A0029', 0.0, 3.4), cx=(0.30, 0.36), sp=0.6)                           # two workers at the rebar
full(2, 3, ('GV3A0017', 0.0, 2.1), cx=(0.44, 0.50), sp=0.6)                           # two men laying blocks
full(3, 4, ('GV3A9994', 0.2, 2.0), cx=(0.36, 0.42), sp=0.6)                           # rebar machine
full(4, 5, ('GV3A0008', 0.0, 3.5), cx=(0.42, 0.42), sp=0.6, push=0.06)                # forest of props, looking up
full(5, 8, ('GV3A9991', 2.4, 5.2), cx=(0.38, 0.44), sp=0.45, flash=True, title=True, reveal=True)  # building, floor by floor + name
full(8, 9, ('GV3A0032', 0.0, 3.3), cx=(0.62, 0.74), sp=0.6, tag=True)                 # Kampala skyline: where it is
SH.append(dict(kind='split', k0=9, k1=13, parts=[(9, ('GV3A0035', 0.5, 2.6), (0.45, 0.55)), (9.18, ('GV3A9992', 2.0, 4.0), (0.25, 0.35)),
                                                (11, ('GV3A0033', 0.3, 3.1), (0.34, 0.42)), (11.18, ('GV3A0028', 0.0, 3.2), (0.56, 0.62))]))
SH.append(dict(kind='halftone', k0=13, k1=15, src=('GV3A0016', 0.0, 3.0), cx=0.72, flash=True))
for i, pn in enumerate(['u12.jpg', 'u02.jpg', 'u08.jpg', 'u13.jpg']): SH.append(dict(kind='photo', k0=15 + i * 0.5, k1=15.5 + i * 0.5, name=pn))
for k, src, cx, o in [(17, ('GV3A0036', 0.0, 3.0), (0.26, 0.34), dict(flash=True)), (18, ('GV3A9992', 4.0, 6.0), (0.28, 0.40), {}),
                      (19, ('GV3A9980', 3.6, 5.5), (0.18, 0.24), dict(shake=True)), (20, ('GV3A0021', 0.0, 2.5), (0.50, 0.58), {}),
                      (21, ('GV3A0028', 22.0, 23.0), (0.48, 0.54), {}), (22, ('GV3A9989', 3.0, 5.5), (0.58, 0.64), dict(push=0.05)),
                      (23, ('GV3A0019', 0.0, 2.5), (0.62, 0.70), {}), (24, ('GV3A9981', 3.5, 6.0), (0.30, 0.36), {})]:
    full(k, k + 1, src, cx=cx, sp=0.55, **o)
for k, src, cx, o in [(25, ('GV3A0044', 0.2, 3.5), (0.42, 0.50), dict(push=0.05)),     # REAL
                      (26, ('GV3A0018', 0.7, 3.0), (0.30, 0.40), {}),                   # WORKERS.
                      (27, ('GV3A9994', 2.0, 4.5), (0.40, 0.46), {}),                   # REAL
                      (28, ('GV3A0021', 2.5, 5.3), (0.46, 0.56), {}),                   # STEEL.
                      (29, ('GV3A0008', 3.5, 7.0), (0.42, 0.48), {}),                   # REAL
                      (30, ('GV3A9991', 0.2, 2.4), (0.42, 0.48), dict(push=0.05))]:     # CONCRETE.
    full(k, k + 1, src, cx=cx, sp=0.6, **o)
BURST = [('GV3A0020', 0.6, 2.0, 0.42), ('GV3A0024', 0.5, 2.0, 0.57), ('GV3A0038', 3.0, 4.5, 0.42), ('GV3A0012', 0.0, 1.5, 0.5),
         ('GV3A9992', 0.3, 1.8, 0.57), ('GV3A0009', 0.0, 1.5, 0.42), ('GV3A0016', 0.0, 1.5, 0.75), ('GV3A9987', 3.0, 4.5, 0.5)]
for i, (c, a, b, x) in enumerate(BURST): full(31 + i * 0.25, 31.25 + i * 0.25, (c, a, b), cx=(x, x), sp=1.0, quick=True)
SH.append(dict(kind='strips', k0=33, k1=37, parts=[('GV3A0019', 2.5, 5.6), ('GV3A0023', 0.0, 3.0), ('GV3A9992', 6.0, 7.6)], flash=True))
for k, src, cx, o in [(37, ('GV3A9980', 23.0, 25.0), (0.52, 0.58), {}), (38, ('GV3A9982', 0.0, 1.5), (0.46, 0.52), dict(push=0.05)),
                      (39, ('GV3A0044', 3.8, 6.5), (0.40, 0.46), {}), (40, ('GV3A0005', 0.0, 3.0), (0.70, 0.76), {})]:
    full(k, k + 1, src, cx=cx, sp=0.55, **o)
SH.append(dict(kind='john', k0=41, k1=44))
full(44, 53, ('GV3A9990', 0.2, 5.2), cx=(0.42, 0.50), sp=0.38, end=True, flash=True)
for s in SH: s['t0'] = max(B(s['k0']), 0.0); s['t1'] = min(B(s['k1']), END)

def shot_at(t):
    for i, s in enumerate(SH):
        if s['t0'] <= t < s['t1']: return i
    return len(SH) - 1

# ---------------- text ----------------
T_H1 = text_rgba('BEFORE YOU BUY A FLAT', 'Inter-ExtraBold.otf', 78)
T_H2 = text_rgba('IN KAMPALA, WATCH THIS.', 'Inter-ExtraBold.otf', 78)
T_NK = text_rgba('NAGURU  ·  KAMPALA', 'Inter-SemiBold.otf', 36, fill=(240, 240, 240), tracking=14)
T_VE = text_rgba('VANTA HOUSE', 'Inter-ExtraBold.otf', 104)
T_NKE = text_rgba('NAGURU, KAMPALA', 'Inter-Medium.otf', 46, fill=(236, 236, 236), tracking=3)
T_LOC = text_rgba('NAGURU, KAMPALA', 'Inter-ExtraBold.otf', 84)
T_OS = text_rgba('ON SITE', 'Inter-Black.otf', 230, fill=TEAL)
T_JN = text_rgba('JOHN YAN', 'Inter-ExtraBold.otf', 72)
T_JT = text_rgba('FOUNDER  ·  BLACKSTONE REAL ESTATE', 'Inter-SemiBold.otf', 32, fill=(236, 236, 236), tracking=2)
WORDS = [(B(25), 'REAL'), (B(26), 'WORKERS.'), (B(27), 'REAL'), (B(28), 'STEEL.'), (B(29), 'REAL'), (B(30), 'CONCRETE.')]
_wimg = {w: text_rgba(w, 'Inter-Black.otf', 124) for _, w in WORDS}
LYR = [('TO TELL YOU', 14.0, 15.36, 'floor', 0.22), ("IT'S NOW", 15.36, 16.24, 'floor', 0.16), ('OR NEVER.', 16.24, 17.9, 'wall', 0.10),
       ('SO MUCH', 24.96, 25.6, 'floor', 0.2), ('FOR CLOSURE,', 25.6, 27.2, 'wall', -0.06),
       ('I LOST', 27.2, 28.08, 'wall', 0.05), ('COMPOSURE.', 28.08, 29.9, 'wall', -0.05)]
_lc = {}
def lyr(j, cy):
    k = (j, cy)
    if k not in _lc:
        tx, a, b, mode, amt = LYR[j]; nw = neon(tx, 112); h, w = nw.shape[:2]; cx = 540
        if w > 1060: nw = cv2.resize(nw, (1060, int(h * 1060 / w))); h, w = nw.shape[:2]
        src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        if mode == 'floor':
            ins = w * amt / 2; dst = np.float32([[cx - w / 2 + ins, cy - h * 0.38], [cx + w / 2 - ins, cy - h * 0.38], [cx + w / 2, cy + h / 2], [cx - w / 2, cy + h / 2]])
        else:
            d = h * amt * 2; dst = np.float32([[cx - w / 2, cy - h / 2 + d], [cx + w / 2, cy - h / 2 - d], [cx + w / 2, cy + h / 2 + d * 0.4], [cx - w / 2, cy + h / 2 - d * 0.4]])
        _lc[k] = warp_word(nw, cv2.getPerspectiveTransform(src, dst))
    return _lc[k]

def title_behind(c, size, y, alpha):
    """VANTA HOUSE behind the building: letters only where the sky is"""
    if alpha <= 0: return c
    m = GR.sky_mask(RAW[0] if RAW[0] is not None and RAW[0].shape == c.shape else c)
    tx = text_rgba('VANTA HOUSE', 'Inter-Black.otf', size); h, w = tx.shape[:2]
    if w > 1030: tx = cv2.resize(tx, (1030, int(h * 1030 / w)), interpolation=cv2.INTER_AREA); h, w = tx.shape[:2]
    x0 = (W - w) // 2
    a = tx[..., 3] * m[y:y + h, x0:x0 + w] * alpha
    c[y:y + h, x0:x0 + w] = c[y:y + h, x0:x0 + w] * (1 - a[..., None]) + 255 * a[..., None]
    return c

def outline(c, p):
    """teal line traces the tower's edge against the sky, glowing"""
    m = (GR.sky_mask(RAW[0] if RAW[0] is not None and RAW[0].shape == c.shape else c) > 0.5).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not cs: return c
    pts = max(cs, key=cv2.contourArea)[:, 0, :]
    pts = pts[(pts[:, 0] > 3) & (pts[:, 0] < W - 4) & (pts[:, 1] > 3) & (pts[:, 1] < H - 4)]
    n = int(len(pts) * p)
    if n < 3: return c
    lay = np.zeros((H, W), np.float32)
    cv2.polylines(lay, [pts[:n].reshape(-1, 1, 2).astype(np.int32)], False, 1.0, 4, lineType=cv2.LINE_AA)
    glow = np.clip(cv2.GaussianBlur(lay, (0, 0), 9) * 3.0, 0, 1)
    a = np.maximum(lay, glow * 0.6)[..., None]
    col = np.array(TEAL, np.float32) * (1 - lay[..., None]) + np.array([235, 255, 252], np.float32) * lay[..., None]
    return c * (1 - a) + col * a

def sweep(img, u, dur=0.9):
    if not (0 <= u < dur): return img
    p = u / dur; h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h:4, 0:w:4].astype(np.float32)
    d = (xx + yy * 0.6) / (w + h * 0.6) - (p * 1.5 - 0.25)
    g = cv2.resize(np.exp(-(d / 0.07) ** 2) * np.sin(np.pi * p) * 0.33, (w, h), interpolation=cv2.INTER_LINEAR)[..., None]
    return img + (np.array([255, 246, 228], np.float32) - img) * g

# ---------------- picture per shot ----------------
def picture(s, t):
    u = t - s['t0']; dur = s['t1'] - s['t0']; kind = s['kind']
    if kind == 'full':
        return clipframe(s['src'], u, W, H, s.get('cx', (0.5, 0.5)), s.get('sp', 0.5), zoom=1.0 + s.get('push', 0.0) * ease(u / max(dur, 0.01)),
                         ramp=s.get('ramp', False), dur=dur)
    if kind == 'split':                                   # top / bottom halves, each lands on its own beat, whip-in
        c = np.full((H, W, 3), BG, np.float32); hh = 956
        slots = [None, None]
        for j, (kin, src, cx) in enumerate(s['parts']):
            if t >= B(kin): slots[j % 2] = (kin, src, cx)
        for half, sl in enumerate(slots):
            if sl is None: continue
            kin, src, cx = sl; uu = t - B(kin)
            img = clipframe(src, uu, W, hh, cx, 0.55, dur=2 * BT)
            k = uu * FPS
            if k < 6:
                e = eout(k / 6); dx = int((1 - e) * W * (1 if half else -1))
                img = motion_blur_x(img, 60 * (1 - e)); img = np.roll(img, dx, 1)
                if dx > 0: img[:, :dx] = BG
                elif dx < 0: img[:, dx:] = BG
            c[half * 964: half * 964 + hh] = img
        return c
    if kind == 'halftone':                                # R2: freeze + newspaper dots
        img = clipframe(s['src'], 0.6, W, H, (s['cx'], s['cx']), 0.5)
        return halftone_fast(img, pitch=10.0)
    if kind == 'photo':
        return photo(s['name'], u, W, H, (0.35, 0.65), dur=dur)
    if kind == 'strips':                                  # R4: three full-width bands landing on half beats
        c = np.full((H, W, 3), BG, np.float32)
        for j, src in enumerate(s['parts']):
            ta = s['t0'] + j * 4 / FPS
            if t < ta: continue
            k = (t - ta) * FPS
            band = clipframe(src, t - s['t0'], W, 636, (0.5, 0.5), 0.5, dur=dur)
            e = eout(k / 6); dx = int(W * (1 - e) * (1 if j % 2 else -1))
            band = np.roll(motion_blur_x(band, 50 * (1 - e)), dx, 1)
            if dx > 0: band[:, :dx] = BG
            elif dx < 0: band[:, dx:] = BG
            c[j * 642: j * 642 + 636] = band
        return c
    if kind == 'john':
        return John.at(u)
    raise ValueError(kind)

def frame(fi, rng):
    t = fi / FPS; i = shot_at(t); s = SH[i]
    c = picture(s, t)
    kin = int(round((t - s['t0']) * FPS)); kout = int(round((s['t1'] - t) * FPS))
    # ---- cut treatment: whip in (alternating), flash where marked ----
    if i > 0 and s['kind'] in ('full', 'photo', 'john') and not s.get('flash') and not s.get('quick') and kin < 3:
        d = 1 if i % 2 else -1
        c = np.roll(motion_blur_x(c, [70, 34, 12][kin]), d * [90, 36, 10][kin], 1)
    if s.get('flash') and kin < 5: c = flash(c, kin, warm=True)
    if s.get('quick') and kin < 2: c = flash(c, kin + 2, warm=True)
    if s['kind'] == 'photo' and kin < 3: c = c * (1 - [0.6, 0.3, 0.1][kin]) + 255 * [0.6, 0.3, 0.1][kin]
    if s.get('shake'):
        dx, dy = shake(kin); c = np.roll(np.roll(c, dx, 1), dy, 0) if (dx or dy) else c
    # ---- R15 intro: grey with only hi-vis in colour ----
    if t < B(5): c = GR.selective(c, 1.0)
    # ---- the building appears floor by floor: colour rises from the ground in 4 quarter-beat steps ----
    if s.get('reveal') and t < B(7.1):
        q = (t - B(5)) / (BT / 2); step = min(int(q), 4); frac = ease(min((q - int(q)) * 2.5, 1.0)) if step < 4 else 1.0
        line = H * (1 - (step + frac) / 4.0)
        yy = np.arange(H, dtype=np.float32)[:, None, None]
        m = np.clip((yy - line) / 40.0, 0, 1)
        grey = GR.selective(c, 1.0) * 0.55
        c = grey * (1 - m) + c * m
        if step < 4:
            lay = np.zeros((H, 1), np.float32); lp = int(min(max(line, 0), H - 1))
            lay[max(lp - 2, 0):lp + 3] = 1.0
            glow = np.clip(cv2.GaussianBlur(np.repeat(lay, 8, 1), (0, 0), 14)[:, :1] * 2.2, 0, 1)
            a = np.maximum(lay, glow * 0.7)[..., None]
            c = c * (1 - a) + np.array(TEAL, np.float32) * a
    if s.get('tag'):
        u = t - s['t0']
        c = bar(c, 540, 1438, ease(u / 0.3), w=96, grow=ease(u / 0.4))
        c = paste(c, T_LOC, 540, 1500, alpha=ease(u / 0.3), dy=16 * (1 - eout(u / 0.35)))
    # ---- hook text: readable from the first frame ----
    if t < B(2.6):
        al = 1 - ease((t - (B(2.6) - 0.2)) / 0.2)
        c[:620] *= (1 - 0.5 * al * (1 - np.linspace(0, 1, 620, dtype=np.float32)) ** 1.2)[:, None, None]
        c = bar(c, 540, 262, al, w=96)
        c = paste(c, T_H1, 540, 330, alpha=al, scale=1.0 + 0.06 * (1 - eout(t * FPS / 4)))
        c = paste(c, T_H2, 540, 424, alpha=al * ease((t - 0.25) / 0.2) if t > 0.25 else 0.0, dy=14 * (1 - eout((t - 0.25) * FPS / 5)))
    # ---- titles behind the tower ----
    if s.get('title'):
        u = t - s['t0']; c = sweep(c, u - 0.3)
        c = title_behind(c, 140, 40, ease((u - 1.1) / 0.5))
    if s['kind'] == 'halftone':
        u = t - s['t0']
        c = paste(c, shine(T_OS, (u - 0.5) / 0.8) if 0.5 < u < 1.3 else T_OS, 540, 960, alpha=ease(u / 0.25), scale=1.0 + 0.15 * (1 - eout(u / 0.35)), shadow=0.3)
    if s.get('end'):
        u = t - s['t0']
        c = light_leak(c, kin)
        if u > 0.2: c = outline(c, ease((u - 0.2) / 1.4))
        ue = u - 1.2
        if ue > 0:                                         # house-style end card over the tower
            c = c * (1 - 0.3 * ease(ue / 0.6))
            c = bar(c, 540, 832, ease(ue / 0.4), grow=ease(ue / 0.5))
            c = paste(c, shine(T_VE, (ue - 0.6) / 1.0) if 0.6 < ue < 1.6 else T_VE, 540, 900, alpha=ease(ue / 0.5), blur=6 * (1 - ease(ue / 0.4)), dy=24 * (1 - eout(ue / 0.5)))
            c = paste(c, T_NKE, 540, 1040, alpha=ease((ue - 0.3) / 0.5))
    if s['kind'] == 'john':
        u = t - s['t0']; al = ease((u - 0.4) / 0.4)
        c = bar(c, 92, 1420, al, w=72, grow=ease((u - 0.4) / 0.5))
        c = paste(c, T_JN, 56 + T_JN.shape[1] / 2, 1476, alpha=al, dy=16 * (1 - eout((u - 0.4) / 0.4)))
        c = paste(c, T_JT, 56 + T_JT.shape[1] / 2, 1546, alpha=ease((u - 0.6) / 0.4))
    # ---- the song's own words, glowing in the scene ----
    for j, (tx, a, b, mode, amt) in enumerate(LYR):
        if a <= t < b:
            cy = 1290 if s['kind'] == 'strips' else 980
            c = comp_rgba(c, np.roll(lyr(j, cy), int((t - a) * -14), 1), neon_flicker(int((t - a) * FPS)) * (1 - ease((t - (b - 0.12)) / 0.12)))
    # ---- REAL / WORKERS. / ... one word per beat ----
    for j, (tw, w) in enumerate(WORDS):
        te = WORDS[j + 1][0] if j + 1 < len(WORDS) else tw + BT
        if tw <= t < te:
            k = (t - tw) * FPS
            c = paste(c, _wimg[w], 540, 1420, alpha=min(1, k / 2 + 0.35), scale=1.0 + 0.2 * (1 - eout(k / 5)))
    if t > END - 0.6: c = c * ease((END - t) / 0.6)
    return grain(c, rng, 3.0)

def main(out, ta=0.0, tb=END):
    AUD = H6 + '/final_mix7.wav'
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', '30', '-i', '-',
        *([] if os.environ.get('NOAUDIO') else ['-ss', '%.3f' % ta, '-t', '%.3f' % (tb - ta), '-i', AUD, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '256k']),
        '-movflags', '+faststart', '-vf', "colorbalance=rs=-0.03:gs=0.0:bs=0.04:rm=0.02:bm=-0.015:rh=0.03:gh=0.005:bh=-0.03",
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
        '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', out], stdin=subprocess.PIPE)
    rng = np.random.default_rng(int(ta * 10) + 3)
    for fi in range(int(round(ta * FPS)), int(round(tb * FPS))):
        enc.stdin.write(np.clip(frame(fi, rng), 0, 255).astype(np.uint8).tobytes())
        if fi % 30 == 0: print('%.1f' % (fi / FPS), flush=True)
    enc.stdin.close(); enc.wait()

if __name__ == '__main__':
    a = sys.argv[2:]; main(sys.argv[1], *(float(x) for x in a))
