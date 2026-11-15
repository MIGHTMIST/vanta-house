# Vanta site edits, round 4 (15 Nov): EVERYTHING ON THE BEAT. Song = owner's long train-song version.
# Beat grid measured on the drums: B(k) = 0.230 + 0.723 k  (hits within +-15 ms; claps on odd k).
#   VID=n2    : cut like the owner's Spider-Man reference (same song, same start): long intro shots with stuttering
#               "cover" graphics, 1-beat black gaps, flash on the drop (k16), one cut per beat in the verse, black + name tag.
#   VID=crew  : short loop (k16 -> k40, 17.35 s), the workers. Last shot runs straight into the first shot.
#   VID=build : short loop (k16 -> k40), the building with the AI camera moves.
# Every cut sits on the frame nearest its beat, no whip blur on the new shot (it lands sharp, with a zoom punch);
# slow-motion shots ramp up in their last frames into the cut ("slow ... slow ... boom"). No floor-reveal curtain, no John.
# usage: VID=crew [NOAUDIO=1] python3 render10.py out.mp4 [t_start t_end]
import sys, os, numpy as np, cv2, subprocess
H10 = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/hype'
sys.path.insert(0, H10)
VID = os.environ.get('VID', 'crew')
_v = os.environ.get('VID'); os.environ['VID'] = 'v1'
import render9 as R9                                   # text look + helpers (tword, fit, pop, halo, sky_clean, streak, swoosh)
if _v is None: del os.environ['VID']
else: os.environ['VID'] = _v
BASE = R9.BASE
from v2core import W, H, FPS, ease, eout, motion_blur_x, halftone_fast
from fx2 import *
import grade as GR
from look10 import film_look
BT = 0.723; PH0 = 0.230
def B(k): return PH0 + BT * k
M0 = 0.0 if VID == 'n2' else B(16)                     # song time at video frame 0
END = (B(48) if VID in ('n2', 'offplan') else B(40)) - M0
NF = int(round(END * FPS))
def fk(k): return int(round((B(k) - M0) * FPS))         # frame index of beat k
def tv(k): return fk(k) / FPS

SH = []
AISRC = R9.AISRC
def full(k0, k1, src, **o): SH.append(dict(kind='full', k0=k0, k1=k1, src=src, **o))
def ai(k0, k1, name, start, speed, **o):
    c, a = AISRC[name]; full(k0, k1, (c, a + start, a + start + 5.0), ai=(name, start, speed), **o)
def photo(k0, k1, name, **o): SH.append(dict(kind='photo', k0=k0, k1=k1, name=name, **o))
def black(k0, k1): SH.append(dict(kind='black', k0=k0, k1=k1))
def card(k0, k1, src, lines, cx=0.5): SH.append(dict(kind='halftone', k0=k0, k1=k1, src=src, cx=cx, lines=lines, flash=True))
HOOK = None; STACKS = []; COVERS = []; SWOOSH = []; TAG = None; TITLE = None; LYR = []; ENDTAG = None; STREAKS = []
STEPS = []; BLUESTUT = []; DATETAG = []; ENDCARD = None
def blue(k0, k1, name, start): SH.append(dict(kind='blue', k0=k0, k1=k1, ai_src=(name, start)))
L1b = [("IT'S", 14.3, 0), ('NOW', 14.6, 0), ('OR', 15.0, 1), ('NEVER.', 15.5, 1)]          # first line: only the urgent half
L2 = R9.L2

if VID == 'n2':
    HOOK = ('BEFORE YOU BUY A FLAT', 'IN KAMPALA, WATCH THIS.')
    ai(0, 3, 'A01', 0.0, 0.85)                                  ; COVERS.append((2, 3, 'onsite'))
    black(3, 4)
    ai(4, 8, 'A03', 0.0, 1.5)                                   ; COVERS += [(5, 6, 'vanta'), (6, 7, 'realwork')]
    full(8, 11, ('GV3A0032', 0.0, 3.3), cx=(0.60, 0.74), sp=0.6); TAG = (9, 11, 'NAGURU, KAMPALA')
    black(11, 12)
    ai(12, 16, 'A10', 0.2, 0.75, boom=True)
    ai(16, 17, 'A06', 2.0, 1.25, flash=True)
    for k, src, cx in [(17, ('GV3A0019', 2.5, 5.6), (0.70, 0.76)), (18, ('GV3A9992', 0.0, 2.0), (0.55, 0.60)), (19, ('GV3A0017', 0.0, 2.2), (0.40, 0.45))]:
        full(k, k + 1, src, cx=cx, sp=0.55)
    ai(20, 21, 'A07', 1.3, 1.25)
    for k, src, cx in [(21, ('GV3A9994', 0.2, 2.0), (0.80, 0.85)), (22, ('GV3A0028', 0.0, 3.0), (0.55, 0.59)), (23, ('GV3A9981', 3.5, 6.0), (0.22, 0.27))]:
        full(k, k + 1, src, cx=cx, sp=0.55, boom=(k == 23))
    LYR.append((L1b, 17.2))
    full(24, 25, ('GV3A0018', 3.0, 5.5), cx=(0.55, 0.58), sp=0.5)
    full(25, 27, ('GV3A9980', 5.5, 8.5), cx=(0.25, 0.25), sp=0.5, echo=True)
    photo(27, 28, 'u02.jpg', slam=True)
    full(28, 29, ('GV3A0036', 15.0, 18.0), cx=(0.55, 0.60), sp=0.5, boom=True)
    ai(29, 30, 'A12', 0.4, 2.2, flash=True)
    full(30, 32, ('GV3A0044', 3.5, 7.4), cx=(0.42, 0.48), sp=0.5, flash=True, boom=True)
    full(32, 33, ('GV3A9991', 3.0, 5.6), cx=(0.40, 0.44), sp=0.5, flash=True); SWOOSH.append(32)     # (9982 6-12: worker faces the lens)
    ai(33, 34, 'A02', 0.3, 2.2)
    full(34, 36, ('GV3A9989', 0.0, 3.0), cx=(0.56, 0.62), sp=0.45)
    ai(36, 38, 'A11', 0.0, 1.2)
    full(38, 40, ('GV3A0021', 2.5, 5.3), cx=(0.55, 0.60), sp=0.45, boom=True)
    LYR.append((L2, 28.6))
    ai(40, 43, 'A08', 0.0, 1.0)
    full(43, 44, ('GV3A9991', 0.0, 3.0), cx=(0.40, 0.44), sp=0.5, boom=True)
    black(44, 99); ENDTAG = 44.35
elif VID == 'crew':
    HOOK = ('BEFORE YOU BUY A FLAT', 'IN KAMPALA, WATCH THIS.')
    AW = 2 * BT                                                  # loop: A01 continues across the end -> start
    ai(16, 18, 'A01', AW, 1.0)
    full(18, 19, ('GV3A0019', 2.5, 5.6), cx=(0.70, 0.75), sp=0.5)
    full(19, 20, ('GV3A9992', 0.0, 2.0), cx=(0.55, 0.60), sp=0.5)
    full(20, 21, ('GV3A0017', 0.0, 2.2), cx=(0.40, 0.45), sp=0.55)
    ai(21, 22, 'A07', 1.3, 1.25)
    full(22, 23, ('GV3A9994', 0.2, 2.0), cx=(0.80, 0.85), sp=0.55)
    full(23, 24, ('GV3A0028', 0.0, 3.0), cx=(0.55, 0.59), sp=0.5, boom=True)
    LYR.append((L1b, 17.2))
    ai(24, 25, 'A06', 2.0, 1.25, flash=True)
    full(25, 27, ('GV3A0036', 15.0, 18.0), cx=(0.55, 0.60), sp=0.45); STACKS.append((25, 27, ['BRICK', 'BY BRICK.']))
    full(27, 29, ('GV3A9992', 4.0, 6.0), cx=(0.36, 0.41), sp=0.45); STACKS.append((27, 29, ['BAR', 'BY BAR.'])); STREAKS.append(27.4)
    full(29, 31, ('GV3A9980', 5.5, 8.5), cx=(0.25, 0.25), sp=0.5, echo=True, boom=True); STACKS.append((29, 31, ['DAY', 'BY DAY.']))
    card(31, 32, ('GV3A0016', 0.0, 3.0), ['ON SITE'], cx=0.72)
    full(32, 34, ('GV3A0018', 3.0, 5.5), cx=(0.55, 0.59), sp=0.45, flash=True); SWOOSH.append(32)
    full(34, 36, ('GV3A0029', 0.0, 3.4), cx=(0.30, 0.35), sp=0.45, boom=True)
    full(36, 37, ('GV3A9981', 6.0, 9.0), cx=(0.25, 0.29), sp=0.55)
    full(37, 38, ('GV3A0016', 3.0, 5.8), cx=(0.74, 0.78), sp=0.55)
    ai(38, 40, 'A01', 0.0, 1.0)
    LYR.append((L2, 28.6))
elif VID == 'offplan':
    # OFF-PLAN EXPLAINED (loop k16 -> k48, 23.1 s). Facts only: no prices, no returns, no payment numbers.
    HOOK = ('BUYING A FLAT OFF-PLAN?', "HERE'S HOW IT WORKS.")
    blue(16, 18, 'A08', 0.0)                                      # the building as a plan (drawn from the real shot)
    ai(18, 20, 'A08', 0.0, 1.4); BLUESTUT.append((18, 19))       # plan -> real, flickering on the 16th notes
    ai(20, 22, 'A03', 0.4, 1.6)
    full(22, 24, ('GV3A9991', 3.0, 5.6), cx=(0.40, 0.45), sp=0.5, boom=True)
    STEPS.append((20, 24, 1)); STACKS.append((20, 24, ['YOU BUY IT', "BEFORE IT'S BUILT."]))
    full(24, 26, ('GV3A0019', 2.5, 5.6), cx=(0.70, 0.75), sp=0.5)
    full(26, 28, ('GV3A0017', 0.0, 2.2), cx=(0.40, 0.45), sp=0.55, boom=True)
    STEPS.append((24, 28, 2)); STACKS.append((24, 28, ['YOU PAY', 'IN PARTS.']))
    ai(28, 30, 'A10', 0.2, 2.4)
    full(30, 32, ('GV3A9989', 0.0, 3.0), cx=(0.56, 0.60), sp=0.5, boom=True)
    STEPS.append((28, 32, 3)); STACKS.append((28, 32, ['YOU CHOOSE', 'YOUR FLOOR.']))
    photo(32, 34, 'u08.jpg', slam=True)
    full(34, 36, ('GV3A0032', 0.0, 3.3), cx=(0.60, 0.72), sp=0.55)
    STEPS.append((32, 36, 4)); STACKS.append((32, 36, ['LIVE IN IT', 'OR RENT IT OUT.']))
    card(36, 37, ('GV3A0016', 0.0, 3.0), ['THE RULE:'], cx=0.72)
    full(37, 38, ('GV3A0021', 2.5, 5.3), cx=(0.55, 0.60), sp=0.55)
    full(38, 40, ('GV3A9980', 5.5, 8.5), cx=(0.25, 0.25), sp=0.5, echo=True, boom=True)
    STACKS.append((37, 40, ['SEE THE SITE', 'BEFORE YOU PAY.']))
    full(40, 41, ('GV3A9992', 0.0, 2.0), cx=(0.55, 0.60), sp=0.55)
    full(41, 42, ('GV3A0028', 0.0, 3.0), cx=(0.55, 0.59), sp=0.55)
    full(42, 43, ('GV3A0018', 3.0, 5.5), cx=(0.55, 0.59), sp=0.5)
    full(43, 44, ('GV3A0036', 15.0, 18.0), cx=(0.55, 0.60), sp=0.55)
    DATETAG.append((38, 44))
    full(44, 48, ('GV3A9990', 3.0, 5.4), cx=(0.42, 0.46), sp=0.35, flash=True); ENDCARD = (44, 0.45)
else:   # build
    HOOK = ('BUYING OFF-PLAN IN KAMPALA?', 'SEE THE REAL SITE FIRST.')
    AW = 2 * BT * 1.4
    ai(16, 18, 'A08', AW, 1.4)
    ai(18, 19, 'A02', 0.3, 2.4)
    full(19, 20, ('GV3A9989', 0.0, 3.0), cx=(0.56, 0.60), sp=0.5)
    ai(20, 22, 'A03', 0.4, 1.6); TITLE = (20, 22)
    ai(22, 23, 'A10', 0.2, 2.4)
    full(23, 24, ('GV3A9991', 3.0, 5.6), cx=(0.40, 0.45), sp=0.5, boom=True)
    LYR.append((L1b, 17.2))
    ai(24, 25, 'A12', 0.4, 2.2, flash=True)
    full(25, 27, ('GV3A0032', 0.0, 3.3), cx=(0.60, 0.72), sp=0.55); TAG = (25, 27, 'NAGURU, KAMPALA')
    photo(27, 29, 'u06.jpg', slam=True); STACKS.append((27, 29, ['ROOM', 'BY ROOM.']))
    full(29, 31, ('GV3A0044', 3.5, 7.4), cx=(0.42, 0.47), sp=0.45, boom=True); COVERS += [(29.0, 29.9, 'vanta'), (30.0, 30.9, 'naguru')]
    card(31, 32, ('photo', 'u14.jpg'), ['ON SITE'])
    full(32, 34, ('GV3A9989', 3.0, 5.5), cx=(0.56, 0.61), sp=0.45, flash=True); SWOOSH.append(32)     # (9982 6-12: worker faces the lens)
    ai(34, 35, 'A02', 2.4, 1.2)
    photo(35, 36, 'u08.jpg', cx=(0.30, 0.45))
    ai(36, 38, 'A11', 0.0, 1.4)
    ai(38, 40, 'A08', 0.0, 1.4)
    LYR.append((L2, 28.6))
for s in SH: s['f0'] = max(fk(s['k0']), 0); s['f1'] = min(fk(s['k1']), NF); s['t0'] = s['f0'] / FPS; s['t1'] = s['f1'] / FPS
SH[0]['f0'] = 0; SH[0]['t0'] = 0.0                     # the first shot owns frame 0
CUTS = sorted(set(s['k0'] for s in SH))

def shot_at(fi):
    for i, s in enumerate(SH):
        if s['f0'] <= fi < s['f1']: return i
    return len(SH) - 1

# ---------------- covers (our motion graphics in place of the reference's comic covers) ----------------
_cov = {}
def cover(name):
    if name in _cov: return _cov[name]
    cw, ch = 860, 1240
    def ph(n, cx=0.5):
        im = BASE.photo(n, 0.0, cw, ch, (cx, cx), dur=1.0); return im
    if name == 'onsite':
        im = halftone_fast(ph('u14.jpg'), pitch=9.0); lines = ['ON SITE']
    elif name == 'realwork':
        im = halftone_fast(ph('u02.jpg', 0.45), pitch=9.0); lines = ['REAL', 'WORK.']
    elif name == 'naguru':
        im = halftone_fast(ph('u09.jpg', 0.55), pitch=9.0); lines = ['NAGURU']
    else:  # 'vanta': magazine-style cover on the sunny slab photo
        im = film_look(ph('u08.jpg', 0.45)); lines = None
    im = im.copy()
    if lines:
        n = len(lines)
        for j, ln in enumerate(lines):
            r = R9.tword(ln, R9.fit(ln, 200, 760)); im = paste(im, r, cw / 2, ch / 2 + (j - (n - 1) / 2) * 200, shadow=0.35)
    else:
        im[:330] *= np.linspace(0.45, 1.0, 330, dtype=np.float32)[:, None, None]
        r = R9.tword('VANTA HOUSE', R9.fit('VANTA HOUSE', 140, 780)); im = paste(im, r, cw / 2, 120, shadow=0.35)
        im = paste(im, R9.T_NKE, cw / 2, 222, shadow=0.4)
        im[262:268, int(cw / 2 - 48):int(cw / 2 + 48)] = np.array(TEAL, np.float32)
    _cov[name] = im
    return im

def put_cover(c, name, j, dy=60):
    """card tilted, soft shadow; j = which flash in the stutter (alternating tilt, tiny jump)"""
    im = cover(name); ch, cw = im.shape[:2]
    ang = (-5.0, 4.0, -3.0, 6.0)[j % 4]; sc = (1.0, 0.96, 1.03, 0.98)[j % 4]
    big = np.zeros((H, W, 4), np.float32); y0 = (H - ch) // 2 + dy; x0 = (W - cw) // 2
    big[y0:y0 + ch, x0:x0 + cw, :3] = im; big[y0:y0 + ch, x0:x0 + cw, 3] = 1.0
    M = cv2.getRotationMatrix2D((W / 2, H / 2 + dy), ang, sc); big = cv2.warpAffine(big, M, (W, H))
    a = big[..., 3:4]
    sh = cv2.GaussianBlur(a[..., 0], (0, 0), 22)[..., None] * 0.55
    c = c * (1 - np.roll(np.roll(sh, 18, 0), 10, 1))
    return c * (1 - a) + big[..., :3] * a

# ---------------- picture ----------------
def u_eff(s, u, dur):
    """slow motion; with boom=True the last 7 frames run 3.2x faster into the cut"""
    sp = s.get('sp', 0.5) if not s.get('ai') else s['ai'][2]
    r = 7 / FPS
    if s.get('boom') and u > dur - r: return sp * (dur - r) + (u - (dur - r)) * sp * 3.2
    return sp * u

def aiimg(s, u, dur):
    name, a, sp = s['ai']; ue = u_eff(s, u, dur)
    f, i0 = BASE.AiF.get(name, a, a + sp * dur * 1.6 + 0.1)
    q = (a + ue) * 24 - i0; j = int(np.floor(q)); j = min(max(j, 0), len(f) - 1); j1 = min(j + 1, len(f) - 1)
    img = BASE.interp(f[j], f[j1], float(q - np.floor(q))) if j1 != j else f[j].astype(np.float32)
    BASE.RAW[0] = None; BASE.AIRAW[0] = img
    return img

def clipimg(s, u, dur, du=0.0):
    sp = s.get('sp', 0.5); ue = u_eff(s, max(u - du, 0), dur)
    img = BASE.clipframe(s['src'], ue, W, H, s.get('cx', (0.5, 0.5)), 1.0, dur=sp * dur)
    return R9.sky_clean(img, BASE.RAW[0])

def picture(s, fi):
    t = fi / FPS; u = t - s['t0']; dur = s['t1'] - s['t0']; kind = s['kind']
    BASE.AIRAW[0] = None; BASE.RAW[0] = None
    if kind == 'full':
        if s.get('ai'): return aiimg(s, u, dur)
        img = clipimg(s, u, dur)
        if s.get('echo'):
            raw = BASE.RAW[0]; p1 = clipimg(s, u, dur, 4 / FPS); p2 = clipimg(s, u, dur, 8 / FPS); BASE.RAW[0] = raw
            m = cv2.GaussianBlur((np.abs(img - p1).mean(-1) > 16).astype(np.float32), (0, 0), 6)
            m2 = cv2.GaussianBlur((np.abs(img - p2).mean(-1) > 16).astype(np.float32), (0, 0), 6)
            gh = np.maximum(m * 0.42, m2 * 0.28)[..., None]; img = img * (1 - gh) + (p1 * 0.6 + p2 * 0.4) * gh
        return img
    if kind == 'photo':
        img = BASE.photo(s['name'], u, W, H, s.get('cx', (0.35, 0.65)), dur=dur)
        if s.get('slam') and u < 0.3:
            e = eout(u / 0.3); M = cv2.getRotationMatrix2D((W / 2, H / 2), 5.0 * (1 - e), 1.0 + 0.24 * (1 - e))
            img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
            if e < 0.8: img = motion_blur_x(img, int(40 * (1 - e)))
        return img
    if kind == 'black': return np.full((H, W, 3), 2.0, np.float32)
    if kind == 'blue':
        im = blueprint(*s['ai_src']); z = 1.0 + 0.04 * ease(u / max(dur, 0.01))
        return punch(im, z - 1.0)
    if kind == 'halftone':
        src = s['src']
        img = BASE.photo(src[1], 0.3, W, H, (0.5, 0.5), dur=1.0) if src[0] == 'photo' else BASE.clipframe(src, 0.6, W, H, (s['cx'], s['cx']), 0.5)
        return halftone_fast(img, pitch=10.0)
    raise ValueError(kind)

_bp = {}
def blueprint(name, start):
    """the building as an architect's plan: edges of the REAL frame drawn in light lines on a teal-dark grid"""
    key = (name, start)
    if key in _bp: return _bp[key]
    f, i0 = BASE.AiF.get(name, start, start + 0.3)
    img = f[max(int(start * 24) - i0, 0)].astype(np.uint8)
    g = cv2.bilateralFilter(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY), 7, 40, 7)
    e = cv2.Canny(g, 45, 120); e = cv2.dilate(e, np.ones((2, 2), np.uint8)).astype(np.float32) / 255
    soft = cv2.GaussianBlur(e, (0, 0), 0.8); glow = np.clip(cv2.GaussianBlur(e, (0, 0), 6) * 1.6, 0, 1)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    bg = np.array([12, 46, 58], np.float32) * (1 - yy) + np.array([6, 26, 36], np.float32) * yy
    bg = np.repeat(np.repeat(bg, 1, 0), W, 1)
    grid = np.zeros((H, W), np.float32); grid[::54, :] = 0.10; grid[:, ::54] = 0.10; grid[::270, :] = 0.22; grid[:, ::270] = 0.22
    lum = g.astype(np.float32)[..., None] / 255
    out = bg + lum * np.array([20, 60, 64], np.float32) * 0.5 + grid[..., None] * np.array([90, 190, 190], np.float32)
    out = out + glow[..., None] * np.array(TEAL, np.float32) * 0.55
    out = out * (1 - soft[..., None]) + np.array([228, 250, 246], np.float32) * soft[..., None]
    # title block like a real drawing sheet (bottom right)
    x0, y0, x1, y1 = 600, 1640, 1040, 1830
    out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * 0.25 + np.array([8, 32, 42], np.float32) * 0.75
    cv2.rectangle(out, (x0, y0), (x1, y1), (200, 240, 236), 2); cv2.line(out, (x0, y0 + 70), (x1, y0 + 70), (200, 240, 236), 2)
    out = paste(out, text_rgba('VANTA HOUSE', 'Inter-ExtraBold.otf', 44, fill=(228, 250, 246), tracking=4), (x0 + x1) / 2, y0 + 36, shadow=0)
    out = paste(out, text_rgba('NAGURU, KAMPALA', 'Inter-SemiBold.otf', 30, fill=(160, 220, 214), tracking=4), (x0 + x1) / 2, y0 + 110, shadow=0)
    out = paste(out, text_rgba('ON PLAN', 'Inter-SemiBold.otf', 30, fill=TEAL, tracking=6), (x0 + x1) / 2, y0 + 155, shadow=0)
    _bp[key] = np.clip(out, 0, 255)
    return _bp[key]

T_DATE = text_rgba('REAL SITE  \u00b7  FILMED 7 NOV 2026', 'Inter-SemiBold.otf', 34, fill=(240, 240, 240), tracking=3)
T_CTA = None
_stepl = {}
def steplabel(n):
    if n not in _stepl: _stepl[n] = text_rgba('STEP %d OF 4' % n, 'Inter-SemiBold.otf', 40, fill=(242, 242, 242), tracking=6)
    return _stepl[n]

def punch(c, amt):
    if amt < 0.003: return c
    s = 1 + amt; h2, w2 = int(H / s), int(W / s); y0, x0 = (H - h2) // 2, (W - w2) // 2
    return cv2.resize(c[y0:y0 + h2, x0:x0 + w2], (W, H), interpolation=cv2.INTER_LINEAR)

def frame(fi, rng):
    t = fi / FPS; i = shot_at(fi); s = SH[i]; kind = s['kind']
    c = picture(s, fi)
    kin = fi - s['f0']; u = t - s['t0']
    if kind not in ('black', 'halftone', 'blue'): c = film_look(c)
    for k0b, k1b in BLUESTUT:                            # plan <-> real flicker on the 16th notes
        if fk(k0b) <= fi < fk(k1b) and ((t + M0 - B(k0b)) / (BT / 4)) % 1 < 0.5:
            bs = [x for x in SH if x['kind'] == 'blue'][0]; c = blueprint(*bs['ai_src']).copy()
    # boom ramp: the last frames before the cut get motion blur from the speed-up
    if s.get('boom') and s['f1'] - fi <= 7 and kind == 'full': c = motion_blur_x(c, 10 * (8 - (s['f1'] - fi)))
    # on the beat: the new shot lands sharp with a zoom punch (bigger on the claps = odd beats)
    if kind != 'black':
        k0 = s['k0']; strong = (int(round(k0)) % 2 == 1)
        amt = (0.07 if strong else 0.045) * (1 - eout(kin / 6)) if kin < 6 else 0.0
        # inside a long shot: a small pulse on every clap
        for kb in range(int(np.ceil(s['k0'] + 0.01)), int(s['k1'])):
            if kb % 2 == 1:
                kk = fi - fk(kb)
                if 0 <= kk < 5: amt = max(amt, 0.025 * (1 - eout(kk / 5)))
        c = punch(c, amt)
    if (s.get('flash') or (i > 0 and SH[i - 1]['kind'] == 'black')) and kin < 5: c = flash(c, kin, warm=True)
    if kind == 'photo' and not s.get('slam') and kin < 3: c = c * (1 - [0.45, 0.2, 0.06][kin]) + 255 * [0.45, 0.2, 0.06][kin]
    for ks in STREAKS: c = R9.streak(c, (t - tv(ks)) / 0.55)
    for k0c, k1c, nm in COVERS:                           # stutter: on 4 frames, off 3, alternating tilt
        f0c, f1c = fk(k0c), fk(k1c)
        qb = (t + M0 - B(k0c)) / (BT / 4)                 # flicker on the quarter beats (16th notes): on, off, on, off
        if f0c <= fi < f1c and (qb % 1) < 0.62: c = put_cover(c, nm, int(qb), dy=(190 if (HOOK and M0 == 0 and t < tv(3)) else 60))
    if TITLE and tv(TITLE[0]) <= t < tv(TITLE[1]):
        uu = t - tv(TITLE[0]); c = BASE.title_behind(c, 140, 40, ease((uu - 0.35) / 0.4))
    if TAG and tv(TAG[0]) <= t < tv(TAG[1]):
        uu = t - tv(TAG[0]); r = R9.tword(TAG[2], R9.fit(TAG[2], 100, 960))
        c = bar(c, 540, 1420, ease(uu / 0.3), w=96, grow=ease(uu / 0.4)); c = R9.pop(c, r, 540, 1500, uu, halo_k=0.5)
    if kind == 'halftone':
        n = len(s['lines'])
        for j, ln in enumerate(s['lines']):
            r = R9.tword(ln, R9.fit(ln, 230, 980)); c = R9.pop(c, r, 540, 960 + (j - (n - 1) / 2) * 230, u - j * 0.2, big=True)
    if HOOK and t < tv((19 if M0 > 0 else 3)) - 0.0:
        tend = tv(19 if M0 > 0 else 3); al = 1 - ease((t - (tend - 0.2)) / 0.2)
        c[:640] *= (1 - 0.55 * al * (1 - np.linspace(0, 1, 640, dtype=np.float32)) ** 1.2)[:, None, None]
        c = bar(c, 540, 250, al, w=96)
        r1 = R9.tword(HOOK[0], R9.fit(HOOK[0], 96, 1000)); r2 = R9.tword(HOOK[1], R9.fit(HOOK[1], 96, 1000))
        c = R9.pop(c, r1, 540, 330, t, hold_alpha=al, start_visible=True)
        c = R9.pop(c, r2, 540, 330 + r1.shape[0] * 0.95, t - BT / 2, hold_alpha=al)
    for k0s, k1s, lines in STACKS:
        if tv(k0s) <= t < tv(k1s):
            out = 1 - ease((t - (tv(k1s) - 0.12)) / 0.12)
            for j, ln in enumerate(lines):
                if t >= tv(k0s + j):
                    y0s = 420 if STEPS else 330
                    r = R9.tword(ln, R9.fit(ln, 150, 960)); c = R9.pop(c, r, 64 + r.shape[1] / 2, y0s + j * 160, t - tv(k0s + j), hold_alpha=out, halo_k=0.6)
    for k0s, k1s, n in STEPS:                            # small "STEP n OF 4" label above the stacked words
        if tv(k0s) <= t < tv(k1s):
            out = 1 - ease((t - (tv(k1s) - 0.12)) / 0.12); r = steplabel(n); uu = t - tv(k0s)
            c = bar(c, 64 + 36, 214, out * ease(uu / 0.25), w=72, grow=ease(uu / 0.3))
            c = R9.pop(c, r, 64 + r.shape[1] / 2, 254, uu, hold_alpha=out, halo_k=0.55)
    for k0d, k1d in DATETAG:                             # proof: the real date of the footage
        if tv(k0d) <= t < tv(k1d):
            uu = t - tv(k0d); al = ease(uu / 0.3) * (1 - ease((t - (tv(k1d) - 0.15)) / 0.15))
            c = R9.halo(c, T_DATE, 540, 1800, al, 1.0, 0.55); c = paste(c, T_DATE, 540, 1800, alpha=al, shadow=0.4)
    if ENDCARD is not None and t >= tv(ENDCARD[0]) + ENDCARD[1]:
        global T_CTA
        if T_CTA is None: T_CTA = R9.tword('MESSAGE US FOR A FREE SITE VISIT.', R9.fit('MESSAGE US FOR A FREE SITE VISIT.', 62, 960))
        ue = t - (tv(ENDCARD[0]) + ENDCARD[1]); r = R9.tword('VANTA HOUSE', R9.fit('VANTA HOUSE', 150, 980))
        c = c * (1 - 0.32 * ease(ue / 0.5)); c = bar(c, 540, int(860 - r.shape[0] / 2 - 18), ease(ue / 0.4), grow=ease(ue / 0.5))
        c = R9.pop(c, r, 540, 860, ue, big=True)
        c = paste(c, R9.T_NKE, 540, 990, alpha=ease((ue - 0.3) / 0.4))
        c = R9.pop(c, T_CTA, 540, 1110, ue - BT, halo_k=0.6)
    for words, tend in LYR:                               # the song's words, as sung, in the ON SITE look
        ts = t + M0
        if not (words[0][1] - 0.05 <= ts < tend): continue
        out = 1 - ease((ts - (tend - 0.15)) / 0.15); xs = {}
        for wd, tw_, ln in words:
            r = R9.tword(wd, 118); x = xs.get(ln, 66)
            if ts >= tw_: c = R9.pop(c, r, x + r.shape[1] / 2, 800 + ln * 132, ts - tw_, hold_alpha=out, halo_k=0.62)
            xs[ln] = x + r.shape[1] + 31
    for ks in SWOOSH: c = R9.swoosh(c, t - (tv(ks) - 0.05))
    if ENDTAG is not None and t >= tv(ENDTAG):            # name tag flickers on over black (the reference's end tag)
        ue = t - tv(ENDTAG); fl = [1, 0, 1, 1, 0, 1][int(ue * FPS)] if ue * FPS < 6 else 1
        if fl:
            r = R9.tword('VANTA HOUSE', R9.fit('VANTA HOUSE', 150, 980))
            c = bar(c, 540, int(910 - r.shape[0] / 2 - 18), 1.0, grow=ease(ue / 0.4)); c = R9.pop(c, r, 540, 910, ue, big=True)
            c = paste(c, R9.T_NKE, 540, 1040, alpha=ease((ue - 0.3) / 0.4))
    return grain(c, rng, 3.0)

def main(out, ta=0.0, tb=None):
    fa = int(round(ta * FPS)); fb = NF if tb is None else min(int(round(tb * FPS)), NF)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', '30', '-i', '-',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p',
        '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', out], stdin=subprocess.PIPE)
    rng = np.random.default_rng(fa + 11)
    for fi in range(fa, fb):
        enc.stdin.write(np.clip(frame(fi, rng), 0, 255).astype(np.uint8).tobytes())
        if fi % 30 == 0: print('%.1f' % (fi / FPS), flush=True)
    enc.stdin.close(); enc.wait()

if __name__ == '__main__':
    a = sys.argv[2:]; main(sys.argv[1], *(float(x) for x in a))
