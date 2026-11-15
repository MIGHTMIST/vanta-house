# Vanta site edit, 3-video set on the long song (15 Nov, owner's lyric-video audio). VID=v1|v2|v3
#   v1 THE CREW  /  v2 THE BUILDING (AI camera moves)  /  v3 THE PHOTOS (all 14 owner photos)
# Every word in the owner's favourite "ON SITE" look: Inter Black, teal, pop-in + glint sweep; song words appear
# word by word as they are sung (like the owner's lyric video). Beat grid of the song: B(k) = 0.244 + 0.723 k.
# usage: VID=v1 [NOAUDIO=1] python3 render9.py out.mp4 [t_start t_end]
import sys, os, numpy as np, cv2, subprocess
H9 = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/hype'
sys.path.insert(0, H9)
import render8 as BASE                          # clipframe / photo / aiframe / selective2 / title_behind / outline / sweep
from v2core import W, H, FPS, ease, eout, motion_blur_x, halftone_fast
from fx2 import *
import grade as GR
VID = os.environ.get('VID', 'v1')
BT = 0.723; PH0 = 0.244
def B(k): return PH0 + BT * k
END = 47.0
BG = 8.0

# ---------------- timeline helpers ----------------
SH = []
AISRC = {'A01': ('GV3A9982', 1.8), 'A02': ('GV3A0008', 0.0), 'A03': ('GV3A9991', 2.4), 'A06': ('GV3A0036', 0.0), 'A07': ('GV3A0021', 0.0),
         'A08': ('GV3A0044', 0.2), 'A10': ('GV3A9982', 0.0), 'A11': ('GV3A9990', 0.2), 'A12': ('GV3A9980', 23.4)}
def full(k0, k1, src, **o): SH.append(dict(kind='full', k0=k0, k1=k1, src=src, **o))
def ai(k0, k1, name, start, speed, **o):
    c, a = AISRC[name]; full(k0, k1, (c, a + start, a + start + 5.0), ai=(name, start, speed), **o)
def photo(k0, k1, name, **o): SH.append(dict(kind='photo', k0=k0, k1=k1, name=name, **o))
def black(k0, k1): SH.append(dict(kind='black', k0=k0, k1=k1))
def split(k0, k1, parts): SH.append(dict(kind='split', k0=k0, k1=k1, parts=parts))
def strips(k0, k1, parts, **o): SH.append(dict(kind='strips', k0=k0, k1=k1, parts=parts, **o))
def card(k0, k1, src, lines, cx=0.5, **o): SH.append(dict(kind='halftone', k0=k0, k1=k1, src=src, cx=cx, lines=lines, flash=True, **o))
def burst(k0, items):
    for i, (c, a, b, x) in enumerate(items): full(k0 + i * 0.25, k0 + (i + 1) * 0.25, (c, a, b), cx=(x, x), sp=1.0, quick=True)
def john(k0, k1): SH.append(dict(kind='john', k0=k0, k1=k1))

HOOK = None; GREY_UNTIL = None; STROBE = []; INSERTS = []; STACKS = []; STREAKS = []; SWOOSH = []; TAG = None
# song words as sung (times read off the owner's lyric video); line breaks like that video. The last line
# ("...I think I wrecked it") is never written on screen: wrong message for a property brand.
L1 = [('I', 12.0, 0), ('HAD', 12.2, 0), ('TO', 12.8, 0), ('TELL', 13.0, 1), ('YA,', 13.6, 1), ("IT'S", 14.3, 2), ('NOW', 14.6, 2),
      ('OR', 15.0, 3), ('NEVER.', 15.5, 3)]
L2 = [('SO', 23.8, 0), ('MUCH', 24.1, 0), ('FOR', 24.6, 1), ('CLOSURE,', 25.0, 1), ('I', 25.6, 2), ('LOST', 26.2, 2), ('COMPOSURE.', 26.6, 3)]
L3 = [('I', 35.2, 0), ('GET', 35.6, 0), ('THE', 35.8, 0), ('MESSAGE,', 36.3, 1), ('I', 37.0, 2), ('LEARNED', 37.2, 2), ('MY', 37.4, 3), ('LESSON.', 37.7, 3)]
LYRICS = [(L1, 17.2), (L2, 28.6), (L3, 39.1)]
STROBE_A = [B(5.5 + 0.25 * i) for i in range(10)]

if VID == 'v1':      # ---------------- THE CREW ----------------
    HOOK = ('BEFORE YOU BUY A FLAT', 'IN KAMPALA, WATCH THIS.'); GREY_UNTIL = 8; STROBE = STROBE_A
    ai(0, 3, 'A01', 0.35, 1.0)                                                     # hook: worker from behind walks to the tower
    full(3, 5, ('GV3A0019', 2.5, 5.6), cx=(0.70, 0.78), sp=0.6)                    # kneeling crew
    full(5, 8, ('GV3A9992', 0.0, 2.0), cx=(0.55, 0.62), sp=0.55)                   # rebar bench, strobe build
    full(8, 10, ('GV3A0018', 0.0, 3.0), cx=(0.55, 0.62), sp=0.6, flash=True)       # colour snaps on
    full(10, 12, ('GV3A0035', 0.0, 2.6), cx=(0.50, 0.56), sp=0.55)
    full(12, 13.5, ('GV3A9981', 3.5, 6.0), cx=(0.22, 0.28), sp=0.6)
    burst(13.5, [('GV3A0020', 0.6, 2.0, 0.42), ('GV3A0024', 0.5, 2.0, 0.57), ('GV3A0012', 0.0, 1.5, 0.5), ('GV3A0037', 33.0, 34.5, 0.42),
                 ('GV3A0009', 0.0, 1.5, 0.42), ('GV3A9995', 0.0, 1.5, 0.42), ('GV3A0028', 12.0, 13.5, 0.42), ('GV3A0028', 10.5, 12.0, 0.42)])
    black(15.5, 16)
    ai(16, 18, 'A06', 2.0, 1.25, flash=True)                                       # drop: push in on the crew
    full(18, 20, ('GV3A0028', 0.0, 3.0), cx=(0.55, 0.60), sp=0.55)
    ai(20, 22, 'A07', 1.3, 1.25)                                                   # forward through the rebar
    full(22, 24, ('GV3A9994', 0.2, 2.0), cx=(0.80, 0.86), sp=0.6)                  # machine (no face)
    full(24, 26, ('GV3A0017', 0.0, 2.2), cx=(0.40, 0.46), sp=0.6); STACKS.append((24, 26, ['BRICK', 'BY BRICK.']))
    split(26, 28, [(26, ('GV3A0028', 19.0, 21.0), (0.40, 0.46)), (26.18, ('GV3A0036', 15.0, 18.0), (0.55, 0.62))])
    full(28, 30, ('GV3A9992', 4.0, 6.0), cx=(0.36, 0.42), sp=0.55); STACKS.append((28, 30, ['BAR', 'BY BAR.'])); STREAKS.append(B(28.5))
    full(30, 32, ('GV3A9980', 5.5, 8.5), cx=(0.25, 0.25), sp=0.6, echo=True); STACKS.append((30, 32, ['DAY', 'BY DAY.']))
    full(32, 34, ('GV3A0018', 3.0, 5.5), cx=(0.55, 0.60), sp=0.55, flash=True); SWOOSH.append(B(32) - 0.05)
    strips(34, 36, [('GV3A0033', 0.3, 3.1), ('GV3A0023', 0.0, 3.0), ('GV3A9992', 6.0, 7.6)])
    full(36, 38, ('GV3A0028', 21.0, 21.75), cx=(0.55, 0.58), sp=0.5)
    full(38, 40, ('GV3A0029', 0.0, 3.4), cx=(0.30, 0.36), sp=0.55)
    card(40, 42, ('GV3A0016', 0.0, 3.0), ['ON SITE'], cx=0.72)
    full(42, 44, ('GV3A9982', 3.0, 6.0), cx=(0.40, 0.46), sp=0.55); INSERTS += [(B(42.5), 'u02.jpg'), (B(43), 'u07.jpg'), (B(43.5), 'u04.jpg')]
    full(44, 46, ('GV3A0004', 0.0, 2.0), cx=(0.42, 0.48), sp=0.6)
    full(46, 47.5, ('GV3A9981', 6.0, 9.0), cx=(0.25, 0.30), sp=0.6)
    black(47.5, 48)
    ai(48, 50, 'A08', 0.3, 2.0, flash=True)
    full(50, 52, ('GV3A0044', 3.5, 7.4), cx=(0.42, 0.48), sp=0.55)
    full(52, 54, ('GV3A0021', 2.5, 5.3), cx=(0.55, 0.60), sp=0.55)
    full(54, 56, ('GV3A9989', 0.0, 3.0), cx=(0.56, 0.62), sp=0.55)
    full(56, 99, ('GV3A9990', 3.0, 5.4), cx=(0.42, 0.46), sp=0.35, end=True, outline=True, flash=True)
elif VID == 'v2':    # ---------------- THE BUILDING (AI camera moves) ----------------
    HOOK = ('BUYING OFF-PLAN IN KAMPALA?', 'SEE THE REAL SITE FIRST.'); STROBE = STROBE_A
    ai(0, 3, 'A08', 0.0, 1.4)                                                      # push in on the tower
    ai(3, 5, 'A02', 0.3, 2.2)                                                      # rise through the props
    photo(5, 8, 'u10.jpg', cx=(0.30, 0.62))                                        # the top slab in the sun, strobe build
    ai(8, 12, 'A03', 0.0, 1.6, flash=True, title=True, reveal=True)                # crane-up, floor by floor, name behind the tower
    full(12, 13.5, ('GV3A0032', 0.0, 3.3), cx=(0.62, 0.74), sp=0.6); TAG = (12, 13.5, 'NAGURU, KAMPALA')
    burst(13.5, [('GV3A0020', 0.6, 2.0, 0.42), ('GV3A0009', 0.0, 1.5, 0.42), ('GV3A9995', 0.0, 1.5, 0.42), ('GV3A0023', 0.0, 1.5, 0.42),
                 ('GV3A0029', 0.0, 1.5, 0.36), ('GV3A0018', 0.0, 1.5, 0.58), ('GV3A9992', 0.3, 1.8, 0.57), ('GV3A0028', 12.0, 13.5, 0.42)])
    black(15.5, 16)
    ai(16, 18, 'A10', 0.2, 2.4, flash=True); STREAKS.append(B(16) + 0.1)          # orbit at the base
    full(18, 20, ('GV3A0044', 3.5, 7.4), cx=(0.42, 0.48), sp=0.55)
    ai(20, 22, 'A12', 0.4, 2.2)                                                    # pull back from the facade
    full(22, 24, ('GV3A9989', 0.0, 3.0), cx=(0.56, 0.62), sp=0.55)
    card(24, 26, ('GV3A0016', 0.0, 3.0), ['ON SITE'], cx=0.72)
    full(26, 28, ('GV3A0012', 0.0, 4.0), cx=(0.46, 0.54), sp=0.6); STACKS.append((26, 28, ['FLOOR', 'BY FLOOR.']))
    photo(28, 30, 'u06.jpg', slam=True); STREAKS.append(B(28) + 0.25)
    split(30, 32, [(30, ('GV3A0021', 2.5, 5.3), (0.55, 0.60)), (30.18, ('GV3A0007', 0.0, 3.4), (0.55, 0.62))])
    full(32, 34, ('GV3A9982', 6.0, 12.0), cx=(0.40, 0.46), sp=0.5, flash=True); SWOOSH.append(B(32) - 0.05)
    full(34, 36, ('GV3A0008', 3.5, 7.0), cx=(0.42, 0.48), sp=0.55)
    full(36, 38, ('GV3A9989', 3.0, 5.5), cx=(0.56, 0.62), sp=0.55)
    photo(38, 40, 'u11.jpg', cx=(0.35, 0.6))
    strips(40, 42, [('photo', 'u08.jpg'), ('photo', 'u09.jpg'), ('photo', 'u13.jpg')])
    card(42, 44, ('photo', 'u14.jpg'), ['NAGURU'], cx=0.5)
    full(44, 46, ('GV3A0024', 0.5, 2.8), cx=(0.55, 0.60), sp=0.6)
    full(46, 47.5, ('GV3A9981', 6.0, 9.0), cx=(0.25, 0.30), sp=0.6)
    black(47.5, 48)
    ai(48, 50, 'A07', 1.3, 1.25, flash=True)
    full(50, 52, ('GV3A0018', 3.0, 5.5), cx=(0.55, 0.60), sp=0.55)
    full(52, 54, ('GV3A9991', 0.0, 3.0), cx=(0.40, 0.46), sp=0.55)
    ai(54, 99, 'A11', 0.0, 3.5 / (END - B(54)), end=True, outline=True, flash=True, card_delay=2.2)
else:                # ---------------- THE PHOTOS (all 14) ----------------
    HOOK = ('YOUR FLAT,', "BEFORE IT'S A FLAT.")
    full(0, 3, ('GV3A0018', 0.0, 3.0), cx=(0.55, 0.62), sp=0.6)
    photo(3, 5, 'u07.jpg', cx=(0.35, 0.6))
    strips(5, 8, [('photo', 'u01.jpg'), ('photo', 'u03.jpg'), ('photo', 'u04.jpg')], slow=True); STROBE = [B(7 + 0.25 * i) for i in range(4)]
    full(8, 10, ('GV3A0019', 2.5, 5.6), cx=(0.70, 0.78), sp=0.6, flash=True)
    photo(10, 12, 'u02.jpg', cx=(0.3, 0.55))
    full(12, 13.5, ('GV3A0029', 0.0, 3.4), cx=(0.30, 0.36), sp=0.6)
    burst(13.5, [('GV3A0016', 0.0, 1.5, 0.75), ('GV3A0023', 0.0, 1.5, 0.42), ('GV3A0033', 0.3, 1.8, 0.42), ('GV3A9995', 0.0, 1.5, 0.42),
                 ('GV3A0028', 12.0, 13.5, 0.42), ('GV3A0004', 0.0, 1.5, 0.45), ('GV3A0012', 0.0, 1.5, 0.5), ('GV3A0009', 0.0, 1.5, 0.42)])
    black(15.5, 16)
    ai(16, 18, 'A06', 2.0, 1.25, flash=True)
    photo(18, 20, 'u12.jpg', cx=(0.45, 0.62))
    full(20, 22, ('GV3A0017', 0.0, 2.2), cx=(0.40, 0.46), sp=0.6)
    photo(22, 24, 'u13.jpg', cx=(0.4, 0.6))
    full(24, 26, ('GV3A9992', 4.0, 6.0), cx=(0.36, 0.42), sp=0.55); INSERTS += [(B(24.5), 'u10.jpg'), (B(25), 'u11.jpg'), (B(25.5), 'u14.jpg')]
    card(26, 28, ('photo', 'u14.jpg'), ['ON SITE'], cx=0.5)
    photo(28, 30, 'u11.jpg', slam=True)
    full(30, 32, ('GV3A0028', 0.0, 3.0), cx=(0.55, 0.60), sp=0.55)
    photo(32, 34, 'u08.jpg', cx=(0.3, 0.55), flash=True); SWOOSH.append(B(32) - 0.05)
    full(34, 36, ('GV3A0019', 0.0, 2.5), cx=(0.72, 0.78), sp=0.6)
    photo(36, 38, 'u05.jpg', cx=(0.4, 0.6))
    ai(38, 40, 'A02', 0.3, 1.8)
    photo(40, 42, 'u06.jpg', slam=True); STACKS.append((40, 42, ['ROOM', 'BY ROOM.']))
    full(42, 44, ('GV3A9994', 0.2, 2.0), cx=(0.80, 0.86), sp=0.6); STREAKS.append(B(42) + 0.2)
    photo(44, 46, 'u09.jpg', cx=(0.3, 0.7))
    full(46, 47.5, ('GV3A9981', 3.5, 6.0), cx=(0.22, 0.28), sp=0.6)
    black(47.5, 48)
    photo(48, 50, 'u10.jpg', cx=(0.4, 0.6), flash=True)
    full(50, 52, ('GV3A9991', 0.0, 3.0), cx=(0.40, 0.46), sp=0.55)
    ai(52, 54, 'A12', 0.4, 2.2)
    john(54, 57)
    full(57, 99, ('GV3A9989', 0.0, 3.0), cx=(0.56, 0.62), sp=0.45, end=True, flash=True)
for s in SH: s['t0'] = max(B(s['k0']), 0.0); s['t1'] = min(B(s['k1']), END)
SH[0]['t0'] = 0.0                                   # the hook owns frame 0 (first beat is at 0.244 s)

def shot_at(t):
    for i, s in enumerate(SH):
        if s['t0'] <= t < s['t1']: return i
    return len(SH) - 1

# ---------------- the owner's favourite text look ----------------
_tw = {}
def tword(text, size, fill=TEAL, name='Inter-Black.otf'):
    k = (text, size, fill, name)
    if k not in _tw: _tw[k] = text_rgba(text, name, size, fill=fill)
    return _tw[k]

def fit(text, size, maxw=1000):
    w = tword(text, size).shape[1]
    return size if w <= maxw else int(size * maxw / w)

def halo(c, rgba, cx, cy, alpha, scale=1.0, k=0.42):
    """soft dark backing behind teal words so they read on bright sky / concrete"""
    a = rgba[..., 3]
    if scale != 1.0: a = cv2.resize(a, None, fx=scale, fy=scale)
    pad = 40; a = cv2.copyMakeBorder(a, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    g = np.clip(cv2.GaussianBlur(a, (0, 0), 20) * 1.5, 0, 1) * k * alpha
    h, w = g.shape; x0 = int(cx - w / 2); y0 = int(cy - h / 2)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if xb > xa and yb > ya: c[ya:yb, xa:xb] *= (1 - g[ya - y0:yb - y0, xa - x0:xb - x0, None])
    return c

def pop(c, rgba, cx, cy, u, big=False, hold_alpha=1.0, start_visible=False, halo_k=None):
    """'ON SITE' entrance: fade + scale pop, then the glint sweeps across the letters"""
    if u < 0: return c
    al = (1.0 if start_visible else ease(u / (0.25 if big else 0.12))) * hold_alpha
    sc = 1.0 + (0.15 if big else 0.2) * (1 - eout(u / (0.35 if big else 0.22)))
    if start_visible: sc = 1.0 + 0.04 * (1 - eout(u / 0.3))
    g0, g1 = (0.5, 1.3) if big else (0.12, 0.72)
    img = shine(rgba, (u - g0) / (g1 - g0)) if g0 < u < g1 else rgba
    c = halo(c, rgba, cx, cy, al, sc, halo_k if halo_k is not None else (0.30 if big else 0.42))
    return paste(c, img, cx, cy, alpha=al, scale=sc, shadow=0.3)

def lyrics(c, t):
    for words, tend in LYRICS:
        if not (words[0][1] - 0.05 <= t < tend): continue
        out = 1 - ease((t - (tend - 0.15)) / 0.15)
        size = 118; lh = 132; x0 = 66; y0 = 800; sp = int(size * 0.26)
        xs = {}
        for wd, tw_, ln in words:
            r = tword(wd, size); x = xs.get(ln, x0)
            if t >= tw_: c = pop(c, r, x + r.shape[1] / 2, y0 + ln * lh, t - tw_, hold_alpha=out, halo_k=0.62)
            xs[ln] = x + r.shape[1] + sp
    return c

def stack(c, t):
    for k0, k1, lines in STACKS:
        if not (B(k0) <= t < B(k1)): continue
        out = 1 - ease((t - (B(k1) - 0.12)) / 0.12)
        for j, ln in enumerate(lines):
            tl = B(k0 + j)
            if t < tl: continue
            r = tword(ln, fit(ln, 150, 960)); c = pop(c, r, 64 + r.shape[1] / 2, 330 + j * 160, t - tl, hold_alpha=out, halo_k=0.6)
    return c

def streak(c, p):
    """light streak: a narrow bright diagonal sweeping across steel (bluish-white core + wide glow)"""
    if not (0 <= p < 1): return c
    yy, xx = np.mgrid[0:H:4, 0:W:4].astype(np.float32)
    d = (xx * 0.8 + yy * 0.45) / (W * 0.8 + H * 0.45) - (p * 1.5 - 0.25)
    core = np.exp(-(d / 0.016) ** 2) * 0.5; glow = np.exp(-(d / 0.09) ** 2) * 0.3
    env = np.sin(np.pi * p)
    m = cv2.resize((core + glow) * env, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    return c + (np.array([255, 248, 232], np.float32) - c) * m

_S = None
def swoosh(c, u):
    """giant teal 'S' flies across into 'SO MUCH...' (owner's lyric video)"""
    global _S
    if not (0 <= u < 0.34): return c
    if _S is None: _S = tword('S', 1100)
    p = eout(u / 0.34); x = W + 500 - p * (W + 1100)
    img = _S.copy(); img = cv2.GaussianBlur(img, (0, 0), 0.1) if u > 0.3 else img
    lay = np.zeros((H, W, 4), np.float32); h, w = img.shape[:2]
    x0 = int(x - w / 2); y0 = int(H / 2 - h / 2)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if xb <= xa or yb <= ya: return c
    lay[ya:yb, xa:xb] = img[ya - y0:yb - y0, xa - x0:xb - x0]
    lay = motion_blur_x(lay, int(90 * (1 - p)) + 1) if p < 0.9 else lay
    a = lay[..., 3:4] * (0.9 * (1 - ease((u - 0.24) / 0.1)))
    return c * (1 - a) + lay[..., :3] * 255 * a

# ---------------- picture per shot ----------------
def sky_clean(img, raw):
    """the grade's local contrast mottles flat skies: smooth inside open sky only. Averages use sky pixels only
    (no halo), anything thin in the sky (masts, wires, scaffold tips) is kept sharp, big cloud shapes stay."""
    if raw is None or raw.shape != img.shape: return img
    m = GR.sky_mask(raw, 0.78)
    if m.mean() < 0.01: return img
    h, w = img.shape[:2]
    L = raw.mean(-1).astype(np.float32)
    edge = (np.abs(L - cv2.GaussianBlur(L, (0, 0), 2.0)) > 3.0).astype(np.uint8)
    edge = cv2.dilate(edge, np.ones((7, 7), np.uint8)).astype(np.float32)
    m = cv2.erode(m, np.ones((5, 5), np.uint8)) * (1 - edge)
    m = cv2.GaussianBlur(m, (0, 0), 2.0)
    q = 4; ms = cv2.resize(m, (w // q, h // q), interpolation=cv2.INTER_AREA)
    sm = cv2.resize(img, (w // q, h // q), interpolation=cv2.INTER_AREA) * ms[..., None]
    def nblur(sig):
        num = cv2.GaussianBlur(sm, (0, 0), sig); den = cv2.GaussianBlur(ms, (0, 0), sig)[..., None]
        return cv2.resize(num / np.maximum(den, 1e-3), (w, h), interpolation=cv2.INTER_LINEAR)
    b40 = nblur(8); b6 = nblur(1.2)
    return img * (1 - m[..., None]) + (b40 + 0.7 * (b6 - b40)) * m[..., None]

def clip(src, u, w, h, cx, sp, **o):
    img = BASE.clipframe(src, u, w, h, cx, sp, **o)
    return sky_clean(img, BASE.RAW[0])

def src_frame(src, u, w, h, cx, sp=0.55, dur=1.0, slow=False):
    if src[0] == 'photo': return BASE.photo(src[1], u, w, h, (0.35, 0.65) if not slow else (0.45, 0.55), dur=dur)
    return clip(src, u, w, h, cx, sp, dur=dur)

def picture(s, t):
    u = t - s['t0']; dur = s['t1'] - s['t0']; kind = s['kind']
    BASE.AIRAW[0] = None; BASE.RAW[0] = None
    if kind == 'full':
        if s.get('ai'): return BASE.aiframe(s, u, dur)
        img = clip(s['src'], u, W, H, s.get('cx', (0.5, 0.5)), s.get('sp', 0.5), zoom=1.0 + s.get('push', 0.0) * ease(u / max(dur, 0.01)),
                             ramp=s.get('ramp', False), dur=dur)
        if s.get('echo'):                              # ghost trail on the moving worker (N3)
            raw = BASE.RAW[0]
            p1 = BASE.clipframe(s['src'], max(u - 4 / FPS, 0), W, H, s['cx'], s['sp'], dur=dur)
            p2 = BASE.clipframe(s['src'], max(u - 8 / FPS, 0), W, H, s['cx'], s['sp'], dur=dur)
            BASE.RAW[0] = raw
            m = cv2.GaussianBlur((np.abs(img - p1).mean(-1) > 16).astype(np.float32), (0, 0), 6)
            m2 = cv2.GaussianBlur((np.abs(img - p2).mean(-1) > 16).astype(np.float32), (0, 0), 6)
            gh = np.maximum(m * 0.42, m2 * 0.28)[..., None]
            img = img * (1 - gh) + (p1 * 0.6 + p2 * 0.4) * gh
        return img
    if kind == 'photo':
        img = BASE.photo(s['name'], u, W, H, s.get('cx', (0.35, 0.65)), dur=dur)
        if s.get('slam') and u < 0.3:                  # slam in: tilted + bigger, settles on the beat
            e = eout(u / 0.3); ang = 5.0 * (1 - e); sc = 1.0 + 0.24 * (1 - e)
            M = cv2.getRotationMatrix2D((W / 2, H / 2), ang, sc); img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
            if e < 0.8: img = motion_blur_x(img, int(40 * (1 - e)))
        return img
    if kind == 'black': return np.full((H, W, 3), 2.0, np.float32)
    if kind == 'split':
        c = np.full((H, W, 3), BG, np.float32); hh = 956; slots = [None, None]
        for j, (kin, src, cx) in enumerate(s['parts']):
            if t >= B(kin): slots[j % 2] = (kin, src, cx)
        for half, sl in enumerate(slots):
            if sl is None: continue
            kin, src, cx = sl; uu = t - B(kin)
            img = src_frame(src, uu, W, hh, cx, 0.55, dur=2 * BT)
            k = uu * FPS
            if k < 6:
                e = eout(k / 6); dx = int((1 - e) * W * (1 if half else -1))
                img = np.roll(motion_blur_x(img, 60 * (1 - e)), dx, 1)
                if dx > 0: img[:, :dx] = BG
                elif dx < 0: img[:, dx:] = BG
            c[half * 964: half * 964 + hh] = img
        return c
    if kind == 'strips':                                # bands land one by one (N3); photo bands pan slowly
        c = np.full((H, W, 3), BG, np.float32); step = 4 / FPS
        for j, src in enumerate(s['parts']):
            ta = s['t0'] + j * step
            if t < ta: continue
            k = (t - ta) * FPS
            band = src_frame(src, t - s['t0'], W, 636, (0.5, 0.5), 0.5, dur=dur, slow=True)
            e = eout(k / 6); dx = int(W * (1 - e) * (1 if j % 2 else -1))
            band = np.roll(motion_blur_x(band, 50 * (1 - e)), dx, 1)
            if dx > 0: band[:, :dx] = BG
            elif dx < 0: band[:, dx:] = BG
            c[j * 642: j * 642 + 636] = band
        return c
    if kind == 'halftone':                              # R2 sepia dots freeze + the teal word (owner's favourite)
        src = s['src']
        img = BASE.photo(src[1], 0.3, W, H, (0.5, 0.5), dur=1.0) if src[0] == 'photo' else BASE.clipframe(src, 0.6, W, H, (s['cx'], s['cx']), 0.5)
        return halftone_fast(img, pitch=10.0)
    if kind == 'john': return BASE.John.at(u)
    raise ValueError(kind)

_ins = {}
def insert_img(name):
    if name not in _ins:
        im = BASE.photo(name, 0.0, W, H, (0.5, 0.5), dur=1.0)
        M = cv2.getRotationMatrix2D((W / 2, H / 2), 3.0, 1.12); _ins[name] = cv2.warpAffine(im, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return _ins[name]

T_NKE = text_rgba('NAGURU, KAMPALA', 'Inter-SemiBold.otf', 46, fill=(240, 240, 240), tracking=3)
T_JT = text_rgba('FOUNDER  ·  BLACKSTONE REAL ESTATE', 'Inter-SemiBold.otf', 32, fill=(236, 236, 236), tracking=2)

def frame(fi, rng):
    t = fi / FPS; i = shot_at(t); s = SH[i]
    c = picture(s, t)
    kin = int(round((t - s['t0']) * FPS))
    if i > 0 and s['kind'] in ('full', 'photo', 'john') and not s.get('flash') and not s.get('quick') and not s.get('slam') and kin < 3 \
            and SH[i - 1]['kind'] != 'black':
        d = 1 if i % 2 else -1
        c = np.roll(motion_blur_x(c, [70, 34, 12][kin]), d * [90, 36, 10][kin], 1)
    if (s.get('flash') or (i > 0 and SH[i - 1]['kind'] == 'black')) and kin < 5: c = flash(c, kin, warm=True)
    if s.get('quick') and kin < 2: c = flash(c, kin + 2, warm=True)
    if s['kind'] == 'photo' and not s.get('slam') and kin < 3: c = c * (1 - [0.5, 0.25, 0.08][kin]) + 255 * [0.5, 0.25, 0.08][kin]
    for ti, name in INSERTS:                            # N2: a photo flashes in for two frames on the beat
        k = (t - ti) * FPS
        if 0 <= k < 2: c = insert_img(name) * (0.75 if k < 1 else 1.0) + 255 * (0.25 if k < 1 else 0.0)
    if GREY_UNTIL is not None and t < B(GREY_UNTIL):
        c = BASE.selective2(c, 1.0) if s.get('ai') else GR.selective(c, 1.0)
    if s.get('reveal') and t < s['t0'] + 2.1 * BT:      # building appears floor by floor
        q = (t - s['t0']) / (BT / 2); step = min(int(q), 4); frac = ease(min((q - int(q)) * 2.5, 1.0)) if step < 4 else 1.0
        line = H * (1 - (step + frac) / 4.0); yy = np.arange(H, dtype=np.float32)[:, None, None]
        m = np.clip((yy - line) / 40.0, 0, 1); c = GR.selective(c, 1.0) * 0.55 * (1 - m) + c * m
        if step < 4:
            lay = np.zeros((H, 1), np.float32); lp = int(min(max(line, 0), H - 1)); lay[max(lp - 2, 0):lp + 3] = 1.0
            glow = np.clip(cv2.GaussianBlur(np.repeat(lay, 8, 1), (0, 0), 14)[:, :1] * 2.2, 0, 1)
            a = np.maximum(lay, glow * 0.7)[..., None]; c = c * (1 - a) + np.array(TEAL, np.float32) * a
    for ts in STROBE:                                   # strobe on the song's build
        k = (t - ts) * FPS
        if 0 <= k < 1: c = c * 0.45 + 255 * 0.55
        elif 1 <= k < 2: c = c * 0.75 + 255 * 0.25
    for ts in STREAKS: c = streak(c, (t - ts) / 0.55)
    if s.get('title'):
        u = t - s['t0']; c = BASE.sweep(c, u - 0.3); c = BASE.title_behind(c, 140, 40, ease((u - 1.1) / 0.5))
    if TAG and B(TAG[0]) <= t < B(TAG[1]):
        u = t - B(TAG[0]); r = tword(TAG[2], fit(TAG[2], 100, 960))
        c = bar(c, 540, 1420, ease(u / 0.3), w=96, grow=ease(u / 0.4)); c = pop(c, r, 540, 1500, u)
    if s['kind'] == 'halftone':
        u = t - s['t0']; n = len(s['lines'])
        for j, ln in enumerate(s['lines']):
            r = tword(ln, fit(ln, 230, 980)); cy = 960 + (j - (n - 1) / 2) * 230
            c = pop(c, r, 540, cy, u - j * 0.25, big=True)
    if t < B(3) and HOOK:                               # hook: readable on frame 0, same teal look
        al = 1 - ease((t - (B(3) - 0.2)) / 0.2)
        c[:640] *= (1 - 0.55 * al * (1 - np.linspace(0, 1, 640, dtype=np.float32)) ** 1.2)[:, None, None]
        c = bar(c, 540, 250, al, w=96)
        r1 = tword(HOOK[0], fit(HOOK[0], 96, 1000)); r2 = tword(HOOK[1], fit(HOOK[1], 96, 1000))
        c = pop(c, r1, 540, 330, t, hold_alpha=al, start_visible=True)
        c = pop(c, r2, 540, 330 + r1.shape[0] * 0.95, t - 0.3, hold_alpha=al)
    c = stack(c, t)
    c = lyrics(c, t)
    for ts in SWOOSH: c = swoosh(c, t - ts)
    if s['kind'] == 'john':
        u = t - s['t0']; al = ease((u - 0.4) / 0.4); r = tword('JOHN YAN', 84)
        c = bar(c, 92, 1420, al, w=72, grow=ease((u - 0.4) / 0.5))
        c = pop(c, r, 56 + r.shape[1] / 2, 1480, u - 0.4)
        c = paste(c, T_JT, 56 + T_JT.shape[1] / 2, 1556, alpha=ease((u - 0.7) / 0.4))
    if s.get('end'):
        u = t - s['t0']; c = light_leak(c, kin)
        if s.get('outline') and u > 0.2: c = BASE.outline(c, ease((u - 0.2) / 1.4))
        ue = u - s.get('card_delay', 1.2)
        if ue > 0:
            r = tword('VANTA HOUSE', fit('VANTA HOUSE', 150, 980))
            c = c * (1 - 0.3 * ease(ue / 0.6)); c = bar(c, 540, int(910 - r.shape[0] / 2 - 18), ease(ue / 0.4), grow=ease(ue / 0.5))
            c = pop(c, r, 540, 910, ue, big=True)
            c = paste(c, T_NKE, 540, 1040, alpha=ease((ue - 0.4) / 0.5))
    if t > END - 0.6: c = c * ease((END - t) / 0.6)
    return grain(c, rng, 3.0)

def main(out, ta=0.0, tb=END):
    AUD = H9 + '/final_mix9_%s.wav' % VID
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', '30', '-i', '-',
        *([] if os.environ.get('NOAUDIO') else ['-ss', '%.3f' % ta, '-t', '%.3f' % (tb - ta), '-i', AUD, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '256k']),
        '-movflags', '+faststart', '-vf', "colorbalance=rs=-0.03:gs=0.0:bs=0.04:rm=0.02:bm=-0.015:rh=0.03:gh=0.005:bh=-0.03",
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
        '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', out], stdin=subprocess.PIPE)
    rng = np.random.default_rng(int(ta * 10) + 7)
    for fi in range(int(round(ta * FPS)), int(round(tb * FPS))):
        enc.stdin.write(np.clip(frame(fi, rng), 0, 255).astype(np.uint8).tobytes())
        if fi % 30 == 0: print('%.1f' % (fi / FPS), flush=True)
    enc.stdin.close(); enc.wait()

if __name__ == '__main__':
    a = sys.argv[2:]; main(sys.argv[1], *(float(x) for x in a))
