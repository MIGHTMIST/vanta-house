# Vanta video 1 re-edit: patched plate + kinetic type + 3D props + Vanta animations + new end card.
# Audio is copied from the export untouched.
import numpy as np, cv2, subprocess, json, math, sys, os, random, time
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, '/home/claude/v2/build'); import patch

SRC = '/home/claude/v2/in/v1_720.mp4'
W, H, FPS = 1080, 1920, 30
NFR = 1175
GOLD = (214, 175, 98); GOLD_D = (158, 122, 70); INK = (22, 19, 15); CREAM = (245, 239, 227); WHITE = (255, 255, 255)
GLASS = (34, 40, 46); LIT = (243, 199, 122)
FN = {'anton': '/home/claude/kin/Anton.woff', 'ci': '/home/claude/kin/Caslon-Italic.woff', 'c': '/home/claude/kin/Caslon.woff',
      'cb': '/home/claude/kin/Caslon-Bold.woff', 'pop': '/home/claude/fonts/poppins_pkg/files/poppins-latin-700-normal.woff'}
_fc = {}
def font(n, s):
    k = (n, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(FN[n], int(s))
    return _fc[k]

def clamp(x): return max(0.0, min(1.0, x))
def eo(p): p = clamp(p); return 1 - (1 - p) ** 3
def eio(p): p = clamp(p); return 4 * p ** 3 if p < .5 else 1 - (-2 * p + 2) ** 3 / 2
def eback(p, s=1.6): p = clamp(p); p -= 1; return 1 + (s + 1) * p ** 3 + s * p ** 2

# ---------------- text ----------------
_tc = {}
def T(txt, fn, size, fill, track=0, shadow=0.55, sblur=12, sdy=6, stroke=0, sfill=(0, 0, 0)):
    k = (txt, fn, size, fill, track, shadow, sblur, sdy, stroke)
    if k in _tc: return _tc[k]
    f = font(fn, size)
    pad = int(size * 0.4) + sblur * 3 + stroke
    ws = [f.getlength(c) for c in txt]
    tw = int(sum(ws) + track * max(len(txt) - 1, 0)) + 2 * stroke + 4
    asc, desc = f.getmetrics()
    im = Image.new('RGBA', (tw + 2 * pad, asc + desc + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if track == 0:
        d.text((pad, pad), txt, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=sfill)
    else:
        x = pad
        for c, w in zip(txt, ws):
            d.text((x, pad), c, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=sfill); x += w + track
    gb = im.getbbox()
    if shadow > 0:
        a = np.array(im.getchannel('A'), np.float32) * shadow
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sh.putalpha(Image.fromarray(a.astype(np.uint8)))
        sh = sh.filter(ImageFilter.GaussianBlur(sblur))
        out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.alpha_composite(sh, (0, sdy)); out.alpha_composite(im); im = out
    # crop symmetric around glyph box so centre = glyph centre
    cx, cy = (gb[0] + gb[2]) / 2, (gb[1] + gb[3]) / 2
    hw = max(cx, im.width - cx); hh = max(cy, im.height - cy)
    m = sblur * 2 + abs(sdy)
    hw = min(hw, (gb[2] - gb[0]) / 2 + m + 4); hh = min(hh, (gb[3] - gb[1]) / 2 + m + 4)
    im = im.crop((int(cx - hw), int(cy - hh), int(cx + hw), int(cy + hh)))
    _tc[k] = im
    return im

def fit(txt, fn, maxw, maxs, track=0):
    s = maxs
    while s > 10:
        f = font(fn, s)
        if f.getlength(txt) + track * (len(txt) - 1) <= maxw: return s
        s -= 2
    return s

def comp(canvas, L, x, y):
    """alpha-composite L onto canvas with top-left (x,y), clipping safely"""
    x, y = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x), max(0, -y)
    dx0, dy0 = max(0, x), max(0, y)
    w = min(L.width - sx0, canvas.width - dx0); h = min(L.height - sy0, canvas.height - dy0)
    if w <= 0 or h <= 0: return
    if sx0 or sy0 or w != L.width or h != L.height: L = L.crop((sx0, sy0, sx0 + w, sy0 + h))
    canvas.alpha_composite(L, (dx0, dy0))

def fade(L, a):
    if a >= 0.999: return L
    L = L.copy(); al = (np.array(L.getchannel('A'), np.float32) * a).astype(np.uint8); L.putalpha(Image.fromarray(al)); return L

def place(canvas, L, cx, cy, a=1.0, blur=0.0, sc=1.0):
    if a <= 0.004: return
    if abs(sc - 1) > 1e-3: L = L.resize((max(1, round(L.width * sc)), max(1, round(L.height * sc))), Image.BICUBIC)
    if blur > 0.6:
        p = int(blur * 2.5) + 2; B = Image.new('RGBA', (L.width + 2 * p, L.height + 2 * p), (0, 0, 0, 0)); B.alpha_composite(L, (p, p))
        L = B.filter(ImageFilter.GaussianBlur(blur))
    comp(canvas, fade(L, a), cx - L.width / 2, cy - L.height / 2)

def kin(canvas, L, cx, cy, t, t0, t1, din=0.28, dout=0.2, mode='blur', grow=0.0, amax=1.0, blur_amt=16):
    if t < t0 - 1e-6 or t > t1 + 1e-6: return
    ein = 1.0 if din <= 0 else eo((t - t0) / din)
    eout = 1.0 if dout <= 0 else eo((t1 - t) / dout)
    a = min(ein, eout) * amax
    blur = (1 - ein) * blur_amt + (1 - eout) * 12
    sc, dy = 1.0, 0.0
    if mode == 'blur': sc = 1 + (1 - ein) * 0.08
    elif mode == 'rise': dy = (1 - ein) * 40
    elif mode == 'slam': sc = 1 + (1 - ein) * 0.32
    elif mode == 'pop': sc = (0.72 + 0.28 * eback((t - t0) / din)) if din > 0 else 1
    sc *= 1 + grow * clamp((t - t0) / max(t1 - t0, 1e-3))
    place(canvas, L, cx, cy + dy, a, blur, sc)

# ---------------- 3D props ----------------
def warp(card, rx, ry, rz=0.0, f=1500.0):
    w, h = card.size
    pts = np.array([[-w / 2, -h / 2, 0], [w / 2, -h / 2, 0], [w / 2, h / 2, 0], [-w / 2, h / 2, 0]], float)
    ax, ay, az = map(math.radians, (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(ax), -math.sin(ax)], [0, math.sin(ax), math.cos(ax)]])
    Ry = np.array([[math.cos(ay), 0, math.sin(ay)], [0, 1, 0], [-math.sin(ay), 0, math.cos(ay)]])
    Rz = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
    p = pts @ (Rz @ Ry @ Rx).T
    proj = np.stack([p[:, 0] * f / (f + p[:, 2]), p[:, 1] * f / (f + p[:, 2])], 1)
    mn = proj.min(0); mx = proj.max(0)
    ow, oh = int(mx[0] - mn[0]) + 6, int(mx[1] - mn[1]) + 6
    dst = (proj - mn + 3).astype(np.float32)
    src = np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32)
    M = cv2.getPerspectiveTransform(src, dst)
    a = np.array(card, np.float32)
    al = a[..., 3:4] / 255.0
    pm = np.concatenate([a[..., :3] * al, a[..., 3:4]], 2)
    out = cv2.warpPerspective(pm, M, (ow, oh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    al2 = out[..., 3:4] / 255.0
    rgb = np.where(al2 > 1e-4, out[..., :3] / np.maximum(al2, 1e-4), 0)
    res = np.concatenate([np.clip(rgb, 0, 255), out[..., 3:4]], 2).astype(np.uint8)
    # centre offset: where the card centre lands
    c = (np.array([0.0, 0.0]) - mn + 3)
    return Image.fromarray(res, 'RGBA'), c

def drop_shadow(card, blur=26, op=0.45, dy=22, pad=60):
    out = Image.new('RGBA', (card.width + 2 * pad, card.height + 2 * pad), (0, 0, 0, 0))
    a = np.array(card.getchannel('A'), np.float32) * op
    sh = Image.new('RGBA', card.size, (0, 0, 0, 0)); sh.putalpha(Image.fromarray(a.astype(np.uint8)))
    big = Image.new('RGBA', out.size, (0, 0, 0, 0)); big.alpha_composite(sh, (pad, pad + dy))
    big = big.filter(ImageFilter.GaussianBlur(blur))
    big.alpha_composite(card, (pad, pad))
    return big

def rrect(size, r, fill, outline=None, width=0, ss=3):
    w, h = size
    im = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss, fill=fill, outline=outline, width=width * ss)
    return im.resize((w, h), Image.LANCZOS)

def paste_c(card, L, cx, cy):
    comp(card, L, cx - L.width / 2, cy - L.height / 2)

def make_nova():
    w, h = 700, 310
    c = rrect((w, h), 30, CREAM + (255,))
    inner = rrect((w - 28, h - 28), 22, (0, 0, 0, 0), outline=GOLD_D + (200,), width=2)
    comp(c, inner, 14, 14)
    paste_c(c, T('PROOF  ·  DELIVERED', 'anton', 30, GOLD_D, track=5, shadow=0), w / 2, 62)
    paste_c(c, T('NOVA RESIDENCE', 'anton', 100, INK, shadow=0), w / 2, 150)
    paste_c(c, T('60 apartments  ·  Kinshasa  ·  2024', 'ci', 40, (70, 60, 48), shadow=0), w / 2, 238)
    return c

def make_stamp():
    s = 196; ss = 3
    im = Image.new('RGBA', (s * ss, s * ss), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    col = (176, 40, 34, 235)
    d.ellipse((6 * ss, 6 * ss, (s - 6) * ss, (s - 6) * ss), outline=col, width=9 * ss)
    d.ellipse((22 * ss, 22 * ss, (s - 22) * ss, (s - 22) * ss), outline=col, width=3 * ss)
    im = im.resize((s, s), Image.LANCZOS)
    paste_c(im, T('DELIVERED', 'anton', 38, (176, 40, 34), shadow=0), s / 2, s / 2 - 8)
    paste_c(im, T('2024', 'anton', 26, (176, 40, 34), track=4, shadow=0), s / 2, s / 2 + 32)
    return im.rotate(-14, resample=Image.BICUBIC, expand=True)

def make_price():
    w, h = 660, 330
    ss = 3
    im = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # tag body with angled left end
    poly = [(70, 0), (w, 0), (w, h), (70, h), (0, h / 2)]
    d.polygon([(x * ss, y * ss) for x, y in poly], fill=CREAM + (255,))
    d.ellipse(((40 - 14) * ss, (h / 2 - 14) * ss, (40 + 14) * ss, (h / 2 + 14) * ss), fill=(0, 0, 0, 0))
    d.line([(96 * ss, 22 * ss), (96 * ss, (h - 22) * ss)], fill=GOLD_D + (160,), width=2 * ss)
    im = im.resize((w, h), Image.LANCZOS)
    a = np.array(im); hole = np.zeros(a.shape[:2], np.uint8); cv2.circle(hole, (40, h // 2), 14, 255, -1)
    a[hole > 0] = 0; im = Image.fromarray(a)
    cx = 96 + (w - 96) / 2
    paste_c(im, T('1 BEDROOM  ·  FROM', 'anton', 32, GOLD_D, track=5, shadow=0), cx, 68)
    paste_c(im, T('USD 53,800', 'anton', 124, INK, shadow=0), cx, 168)
    paste_c(im, T('1st-floor price · +1% per floor up', 'ci', 34, (70, 60, 48), shadow=0), cx, 266)
    return im

def make_calendar():
    w, h = 420, 360
    body = rrect((w, h), 34, (255, 255, 255, 64), outline=(255, 255, 255, 170), width=3)
    band = rrect((w, 92), 34, GOLD + (235,))
    band = band.crop((0, 0, w, 92))
    mask = Image.new('L', (w, 92), 0); ImageDraw.Draw(mask).rectangle((0, 0, w, 92), fill=255)
    comp(body, band, 0, 0)
    d = ImageDraw.Draw(body)
    d.rectangle((0, 60, w, 92), fill=GOLD + (235,))
    for x in (120, w - 120):
        d.ellipse((x - 13, 30, x + 13, 56), fill=(40, 34, 26, 255))
        d.rounded_rectangle((x - 6, 6, x + 6, 50), 6, fill=(240, 236, 228, 255))
    paste_c(body, T('OCT', 'ci', 76, WHITE, shadow=0.35, sblur=6, sdy=3), w / 2, 150)
    paste_c(body, T('2027', 'anton', 150, WHITE, shadow=0.35, sblur=8, sdy=4), w / 2, 252)
    paste_c(body, T('EXPECTED COMPLETION', 'anton', 22, WHITE, track=4, shadow=0.3, sblur=4, sdy=2), w / 2, 330)
    shape = rrect((w, h), 34, (255, 255, 255, 255))
    return body, shape

def chip(txt, size=26, fill=(18, 16, 13, 215), col=WHITE, padx=26, pady=14, track=4, r=None):
    L = T(txt, 'anton', size, col, track=track, shadow=0)
    g = L.getbbox(); tw, th = g[2] - g[0], g[3] - g[1]
    w, h = tw + 2 * padx, th + 2 * pady
    c = rrect((w, h), r if r is not None else h // 2, fill)
    paste_c(c, L, w / 2, h / 2)
    return c

# ---------------- captions (match the burned-in CapCut style) ----------------
SRT = []
def load_srt(p):
    import re
    txt = open(p).read().strip().split('\n\n')
    for b in txt:
        ls = b.strip().split('\n')
        m = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', ls[1])
        g = list(map(int, m.groups()))
        t0 = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000; t1 = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        SRT.append((t0, t1, ' '.join(ls[2:])))
pass  # video-1 captions not used: load_srt('/home/claude/v1/v1b/video1_captions_human.srt')
def caption(canvas, t):
    for t0, t1, s in SRT:
        if t0 <= t < t1:
            L = T(s, 'pop', 62, WHITE, shadow=0.6, sblur=9, sdy=5, stroke=4)
            place(canvas, L, 540, 1195)

# ---------------- animation scenes ----------------
def dark_bg(t, seed=0):
    y = np.linspace(0, 1, H)[:, None]
    top = np.array([30, 25, 19]); bot = np.array([12, 10, 8])
    g = top * (1 - y[..., None]) + bot * y[..., None]
    img = np.repeat(g, W, 1)
    # warm glow behind the tower
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - 540) / 620.0) ** 2 + ((yy - 1050) / 760.0) ** 2)
    glow = np.clip(1 - r, 0, 1) ** 2 * 0.22
    img = img + glow[..., None] * np.array([214, 175, 98])
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(im)
    for x in range(0, W, 90): d.line([(x, 0), (x, H)], fill=(214, 175, 98, 14))
    for yv in range(0, H, 90): d.line([(0, yv), (W, yv)], fill=(214, 175, 98, 14))
    return im
_DARK = None
def DARK():
    global _DARK
    if _DARK is None:
        base = Image.new('RGBA', (W, H), (0, 0, 0, 255)); g = dark_bg(0)
        # gridlines need alpha compositing over the gradient
        _DARK = g
    return _DARK.copy()

rng = random.Random(7)
FLOORS = 12; FH = 60; TBASE = 1585; TW = 560; TX0 = 540 - TW // 2
def tower(canvas, tl, built_t0=0.12, per=0.12, light_t0=1.55):
    d = ImageDraw.Draw(canvas)
    # ground line
    d.rectangle((60, TBASE, W - 60, TBASE + 3), fill=GOLD + (200,))
    for k in range(FLOORS):
        st = built_t0 + k * per
        p = clamp((tl - st) / 0.22)
        if p <= 0: continue
        e = eback(p, 1.3)
        y1 = TBASE - k * FH; y0 = y1 - FH
        off = (1 - e) * -46
        a = int(255 * clamp(p * 1.6))
        lay = Image.new('RGBA', (TW + 40, FH + 14), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        if k < 2:
            ld.rectangle((20, 4, TW + 20, FH + 4), fill=(122, 112, 98, 255))
            for b in range(6):
                bx = 20 + 30 + b * 80
                ld.rounded_rectangle((bx, 18, bx + 52, FH - 6), 6, fill=(52, 47, 40, 255))
        else:
            ld.rectangle((20, 4, TW + 20, 14), fill=(238, 229, 212, 255))      # slab
            ld.rectangle((20, 14, TW + 20, FH + 4), fill=(46, 52, 58, 255))     # glass band
            for b in range(8):
                bx = 20 + 14 + b * 62
                lit_at = light_t0 + rng.random() * 0.0 + ((k * 8 + b) * 7919 % 97) / 97 * 0.7
                lp = clamp((tl - lit_at) / 0.15)
                col = tuple(int(46 + (c - 46) * lp) for c in LIT) if lp > 0 else (58, 64, 70)
                ld.rectangle((bx, 20, bx + 46, FH - 2), fill=col + (255,))
                ld.line([(bx + 23, 20), (bx + 23, FH - 2)], fill=(238, 229, 212, 140), width=2)
            ld.line([(20, FH - 8), (TW + 20, FH - 8)], fill=(214, 228, 232, 150), width=3)  # balcony glass rail
            ld.rectangle((10, 4, 30, FH + 4), fill=(238, 229, 212, 255)); ld.rectangle((TW + 10, 4, TW + 30, FH + 4), fill=(238, 229, 212, 255))
        comp(canvas, fade(lay, a / 255), TX0 - 20, y0 - 4 + off)
    # roof crown + sign when complete
    pr = clamp((tl - (built_t0 + FLOORS * per)) / 0.3)
    if pr > 0:
        ytop = TBASE - FLOORS * FH
        cr = Image.new('RGBA', (TW + 60, 70), (0, 0, 0, 0)); cd = ImageDraw.Draw(cr)
        cd.rectangle((30, 46, TW + 30, 60), fill=(238, 229, 212, 255))
        for ux in (110, 230, 350, 470):
            cd.polygon([(ux - 34, 38), (ux + 34, 38), (ux, 14)], fill=GOLD + (255,)); cd.line([(ux, 38), (ux, 52)], fill=GOLD + (255,), width=3)
        comp(canvas, fade(cr, eo(pr)), TX0 - 30, ytop - 58 + (1 - eo(pr)) * -20)

def crane(canvas, tl, hook_y):
    d = ImageDraw.Draw(canvas)
    mx = 935; top = 760
    a = int(255 * clamp(tl / 0.25))
    col = GOLD + (a,)
    d.line([(mx - 16, TBASE), (mx - 16, top)], fill=col, width=4); d.line([(mx + 16, TBASE), (mx + 16, top)], fill=col, width=4)
    for yy in range(TBASE, top, -46): d.line([(mx - 16, yy), (mx + 16, yy - 46)], fill=col, width=2)
    sway = math.sin(tl * 2.2) * 6
    d.line([(430, top - 10), (1060, top - 10)], fill=col, width=5)
    d.line([(430, top + 14), (mx, top + 14)], fill=col, width=3)
    for xx in range(430, mx, 40): d.line([(xx, top + 14), (xx + 40, top - 10)], fill=col, width=2)
    d.polygon([(mx - 22, top - 10), (mx + 22, top - 10), (mx, top - 80)], outline=col, width=3)
    d.rectangle((1020, top - 6, 1060, top + 34), fill=col)
    tx = 640 + sway
    d.line([(tx, top + 14), (tx, hook_y)], fill=(230, 220, 200, a), width=2)
    d.rectangle((tx - 9, hook_y, tx + 9, hook_y + 14), fill=col)

def scene_A(t):  # 11.567 - 14.300 "each of my condominium projects"
    tl = t - 11.567
    im = DARK()
    built = clamp((tl - 0.12) / (FLOORS * 0.12))
    hook_y = int(TBASE - min(FLOORS, (tl - 0.12) / 0.12 + 1) * FH - 40) if tl > 0.12 else TBASE - FH - 40
    crane(im, tl, max(800, hook_y))
    tower(im, tl)
    kin(im, chip('VANTA HOUSE  ·  NAGURU', 32, fill=(214, 175, 98, 46), col=GOLD, track=6), 540, 270, t, 11.567, 14.30, din=0.0, dout=0.15)
    kin(im, T('each of my', 'ci', 66, WHITE), 540, 362, t, 11.567, 14.30, din=0.0, dout=0.15)
    s = fit('CONDOMINIUM', 'anton', 940, 170)
    kin(im, T('CONDOMINIUM', 'anton', s, WHITE), 540, 470, t, 12.20, 14.30, din=0.3, dout=0.15, mode='blur')
    kin(im, T('projects', 'ci', 76, GOLD), 540, 590, t, 12.75, 14.30, din=0.3, dout=0.15, mode='rise')
    return im

def scene_B(t):  # 16.400 - 18.033 "small but refined project"
    tl = t - 16.4
    im = Image.new('RGBA', (W, H), CREAM + (255,))
    yy, xx = np.mgrid[0:H:8, 0:W:8]
    kin(im, T('small but', 'ci', 72, (90, 76, 58), shadow=0), 540, 330, t, 16.40, 18.033, din=0.0, dout=0.12)
    s = fit('REFINED', 'anton', 900, 280)
    kin(im, T('REFINED', 'anton', s, GOLD_D, shadow=0.18, sblur=10), 540, 500, t, 16.98, 18.033, din=0.22, dout=0.12, mode='slam')
    rows = ['Porcelain floor tiles', 'Fitted kitchen', 'Wardrobes in the bedrooms', 'Large scenic balcony']
    for k, r in enumerate(rows):
        t0 = 16.50 + k * 0.16
        y = 740 + k * 92
        if t < t0: continue
        p = eo((t - t0) / 0.25)
        row = Image.new('RGBA', (820, 84), (0, 0, 0, 0)); rd = ImageDraw.Draw(row)
        ss = 3; ck = Image.new('RGBA', (60 * ss, 60 * ss), (0, 0, 0, 0)); cdd = ImageDraw.Draw(ck)
        cdd.ellipse((0, 0, 60 * ss - 1, 60 * ss - 1), fill=GOLD_D + (255,))
        cdd.line([(16 * ss, 31 * ss), (26 * ss, 41 * ss), (45 * ss, 20 * ss)], fill=CREAM + (255,), width=6 * ss, joint='curve')
        ck = ck.resize((60, 60), Image.LANCZOS)
        comp(row, ck, 40, 12)
        L = T(r, 'ci', 52, INK, shadow=0)
        comp(row, L, 128, 42 - L.height / 2)
        place(im, row, 540 + (1 - p) * -40, y, a=p, blur=(1 - p) * 8)
    return im

def scene_C(t):  # 18.033 - 21.300 "with a small total volume scale"
    tl = t - 18.033
    im = DARK()
    d = ImageDraw.Draw(im)
    x0, x1, y0, y1 = 210, 870, 640, 1110
    a = int(255 * clamp(tl / 0.2))
    d.rectangle((x0 - 26, y0 - 30, x1 + 26, y1 + 18), fill=(238, 229, 212, a))
    cw = (x1 - x0) / 10; ch = (y1 - y0) / 10
    order = list(range(100)); random.Random(3).shuffle(order)
    for idx in range(100):
        r, c = divmod(idx, 10)
        k = order.index(idx)
        lt = 0.35 + k * 0.016
        lp = clamp((tl - lt) / 0.12)
        col = tuple(int(58 + (cc - 58) * lp) for cc in LIT) if lp > 0 else (58, 64, 70)
        bx = x0 + c * cw + 7; by = y0 + r * ch + 8
        d.rectangle((bx, by, bx + cw - 14, by + ch - 18), fill=col + (a,))
        d.line([(x0 - 26, by + ch - 6), (x1 + 26, by + ch - 6)], fill=(214, 228, 232, int(a * 0.5)), width=2)
    d.rectangle((x0 - 60, y1 + 18, x1 + 60, y1 + 24), fill=GOLD + (a,))
    s = fit('100', 'anton', 600, 300)
    kin(im, T('100', 'anton', s, GOLD), 540, 300, t, 18.10, 21.30, din=0.3, dout=0.15, mode='slam')
    kin(im, T('RESIDENCES ONLY', 'anton', 64, WHITE, track=6), 540, 480, t, 18.70, 21.30, din=0.3, dout=0.15, mode='rise')
    kin(im, T('on 10 residential floors', 'ci', 48, GOLD), 540, 560, t, 19.20, 21.30, din=0.3, dout=0.15, mode='rise')
    return im


_EL = None
def end_layout():
    global _EL
    if _EL: return _EL
    logo = Image.open('/home/claude/v1/assets/blackstone_logo_gold.png').convert('RGBA')
    lw = 400; logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    badge = chip('FREE SITE VISIT', 50, fill=GOLD_D + (255,), col=WHITE, padx=48, pady=22, track=5)
    def g(txt, fn, size):
        b = font(fn, size).getbbox(txt); return b[3] - b[1]
    items = [('logo', logo.height, 0), ('come', g('Come and see', 'ci', 52), 34), ('vh', g('VANTA HOUSE', 'anton', 118), 22),
             ('nag', g('Naguru, Kampala', 'ci', 42), 20), ('fsv', badge.height, 36), ('send', g('Send', 'ci', 50), 40),
             ('vanta', g('VANTA', 'anton', 112), 20), ('wa', g('on WhatsApp to', 'ci', 44), 20), ('num', g('0741 131 420', 'anton', 86), 20)]
    total = sum(h + gap for _, h, gap in items)
    top, bot = 300, 1225
    k = (bot - top - sum(h for _, h, _ in items)) / sum(gap for _, _, gap in items)
    y = top; out = {'logo_img': logo, 'badge': badge}
    for name, h, gap in items:
        y += gap * k
        out[name] = y + h / 2; y += h
    _EL = out
    return out

def scene_E(t):  # 28.300 - end: end card on Sarah's words
    tl = t - 28.3
    im = Image.new('RGBA', (W, H), CREAM + (255,))
    # very soft warm vignette
    E = end_layout()
    kin(im, E['logo_img'], 540, E['logo'], t, 28.30, 99, din=0.45, dout=0, mode='rise', blur_amt=10)
    kin(im, T('Come and see', 'ci', 52, (80, 68, 52), shadow=0), 540, E['come'], t, 29.15, 99, din=0.3, dout=0, mode='rise')
    kin(im, T('VANTA HOUSE', 'anton', 118, INK, shadow=0), 540, E['vh'], t, 29.62, 99, din=0.3, dout=0, mode='slam')
    kin(im, T('Naguru, Kampala', 'ci', 42, GOLD_D, shadow=0), 540, E['nag'], t, 30.10, 99, din=0.3, dout=0, mode='rise')
    badge = E['badge']
    kin(im, badge, 540, E['fsv'], t, 31.24, 99, din=0.3, dout=0, mode='pop')
    sp = (t - 32.0) / 0.6
    if 0 < sp < 1:
        sh = Image.new('RGBA', badge.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        x = -120 + sp * (badge.width + 240)
        sd.polygon([(x, 0), (x + 60, 0), (x - 20, badge.height), (x - 80, badge.height)], fill=(255, 255, 255, 90))
        m = np.array(badge.getchannel('A')); sa = np.array(sh.getchannel('A')); sh.putalpha(Image.fromarray(np.minimum(m, sa)))
        place(im, sh, 540, E['fsv'])
    kin(im, T('Send', 'ci', 50, (80, 68, 52), shadow=0), 540, E['send'], t, 32.50, 99, din=0.25, dout=0, mode='rise')
    kin(im, T('VANTA', 'anton', 112, GOLD_D, shadow=0), 540, E['vanta'], t, 32.82, 99, din=0.25, dout=0, mode='slam')
    kin(im, T('on WhatsApp to', 'ci', 44, (80, 68, 52), shadow=0), 540, E['wa'], t, 33.40, 99, din=0.3, dout=0, mode='rise')
    kin(im, T('0741 131 420', 'anton', 86, INK, track=3, shadow=0), 540, E['num'], t, 34.30, 99, din=0.3, dout=0, mode='rise')
    # slow push-in of the whole card
    s = 1 + 0.025 * clamp(tl / 10.8)
    if s > 1.0005:
        big = im.resize((round(W * s), round(H * s)), Image.BICUBIC)
        ox, oy = (big.width - W) / 2, (big.height - H) * 0.45
        im = big.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    return im

# ---------------- John segments ----------------
def hero(txt, maxs=250, maxw=960, col=GOLD):
    s = fit(txt, 'anton', maxw, maxs)
    return T(txt, 'anton', s, col, shadow=0.6, sblur=16, sdy=8)

def bottom_at(L, glyph_bottom, shadow_pad=None):
    # T() centres on the glyph box; its glyph height ~= L.height minus symmetric margins
    return glyph_bottom - GH[id(L)] / 2 if id(L) in GH else glyph_bottom - L.height / 2

GH = {}
def gh(txt, size):
    f = font('anton', size); b = f.getbbox(txt); return b[3] - b[1]

def place_hero(im, txt, t, t0, t1, head_top, overlap=50, **kw):
    s = fit(txt, 'anton', kw.pop('maxw', 960), kw.pop('maxs', 250))
    L = T(txt, 'anton', s, GOLD, shadow=0.6, sblur=16, sdy=8)
    h = gh(txt, s)
    cy = head_top + overlap - h / 2
    kin(im, L, 540, cy, t, t0, t1, **kw)
    return cy - h / 2   # glyph top

HT = {'W': 527, 'P': 446}
def topshade(im):
    global _SHADE
    try: _SHADE
    except NameError:
        a = np.zeros((H, W), np.float32)
        y = np.arange(H)
        a[:, :] = (np.clip(1 - y / 820.0, 0, 1) ** 1.6 * 0.46)[:, None]
        _SHADE = Image.new('RGBA', (W, H), (8, 6, 4, 0)); _SHADE.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    im.alpha_composite(_SHADE)

HERO_TOP = {}
def overlays_behind(im, t, i):
    if i < 110:   # S1 hook
        HERO_TOP['S1'] = place_hero(im, 'DIFFERENT?', t, 0.0, 3.62, HT['W'], overlap=48, din=0, dout=0.15, grow=0.03)
    elif 196 <= i < 275:
        HERO_TOP['S3'] = place_hero(im, 'FINANCE', t, 7.28, 8.45, HT['W'], overlap=48, maxs=300, maxw=900, din=0.22, dout=0.25, mode='slam')
    elif 429 <= i < 492:
        HERO_TOP['S6'] = place_hero(im, 'BOUTIQUE', t, 15.12, 16.40, HT['P'], overlap=46, maxs=280, maxw=960, din=0.25, dout=0.0, mode='slam', grow=0.03)

def overlays_front(im, t, i, plate_np):
    if i < 110:
        kin(im, T('Why is Blackstone', 'ci', 76, WHITE, shadow=0.9, sblur=10, sdy=4), 540, HERO_TOP.get('S1', 380) - 58, t, 0.0, 3.62, din=0, dout=0.15)
    elif i < 196:   # Nova proof card + stamp
        tl = t - 3.70
        if tl >= 0:
            card = drop_shadow(make_nova_c())
            rx = 7 + 2.5 * math.sin(tl * 2.1); ry = -12 + 3 * math.cos(tl * 1.7)
            wc, c = warp(card, rx, ry, -1.5)
            fl = 7 * math.sin(tl * 2.4)
            ein = eo(tl / 0.32); eout = eo((6.52 - t) / 0.18)
            place(im, wc, 560, 282 + fl + (1 - ein) * 40, a=min(ein, eout), blur=(1 - ein) * 14 + (1 - eout) * 10, sc=1 + (1 - ein) * 0.06)
            st0 = 4.60
            if t >= st0:
                p = clamp((t - st0) / 0.16)
                place(im, STAMP, 905, 168 + fl, a=min(clamp(p * 2), eout), sc=1.0 + (1 - eo(p)) * 0.9)
    elif 196 <= i < 234:
        kin(im, T('I majored in', 'ci', 76, WHITE, shadow=0.9, sblur=10, sdy=4), 540, HERO_TOP.get('S3', 380) - 58, t, 6.62, 7.80, din=0.25, dout=0.0, mode='rise')
    elif 234 <= i < 347:
        kin(im, T("that's why", 'ci', 80, WHITE, shadow=0.9, sblur=10, sdy=4), 540, 330, t, 9.08, 10.60, din=0.28, dout=0.25, mode='rise')
    elif 429 <= i < 492:
        kin(im, T('a small', 'ci', 80, WHITE, shadow=0.9, sblur=10, sdy=4), 540, HERO_TOP.get('S6', 320) - 60, t, 14.52, 16.40, din=0.28, dout=0.0, mode='rise')
    elif 639 <= i < 698:   # price tag
        tl = t - 21.33
        if tl >= 0:
            card = drop_shadow(PRICE)
            rx = 6 + 2 * math.sin(tl * 2.0); ry = 13 + 3 * math.cos(tl * 1.6)
            wc, c = warp(card, rx, ry, 2.0)
            fl = 7 * math.sin(tl * 2.3)
            ein = eo(tl / 0.32); eout = eo((23.25 - t) / 0.18)
            place(im, wc, 540, 300 + fl + (1 - ein) * 40, a=min(ein, eout), blur=(1 - ein) * 14 + (1 - eout) * 10, sc=1 + (1 - ein) * 0.06)
    elif 698 <= i < 768:   # site photo
        place(im, SITECHIP, 268, 628)
        kin(im, T('about', 'ci', 56, WHITE, shadow=0.75, sblur=14), 540, 250, t, 23.74, 25.58, din=0.25, dout=0.15, mode='rise')
        kin(im, T('15 MONTHS', 'anton', fit('15 MONTHS', 'anton', 900, 190), WHITE, shadow=0.75, sblur=18, sdy=8), 540, 380, t, 24.00, 25.58, din=0.25, dout=0.15, mode='slam')
        kin(im, T('to build', 'ci', 56, WHITE, shadow=0.75, sblur=14), 540, 510, t, 24.40, 25.58, din=0.25, dout=0.15, mode='rise')
    elif 768 <= i < 849:   # glass calendar
        tl = t - 25.66
        if tl >= 0:
            rx = 9 + 2.5 * math.sin(tl * 2.0); ry = -16 + 3 * math.cos(tl * 1.5)
            wb, c = warp(CAL_BODY, rx, ry, -3)
            ws, _ = warp(CAL_SHAPE, rx, ry, -3)
            fl = 7 * math.sin(tl * 2.2)
            ein = eo(tl / 0.35); eout = eo((28.29 - t) / 0.15)
            a = min(ein, eout)
            cx, cy = 560, 312 + fl + (1 - ein) * 40
            # frosted glass: blur what is behind the card
            x0 = int(cx - ws.width / 2); y0 = int(cy - ws.height / 2)
            reg = im.crop((x0, y0, x0 + ws.width, y0 + ws.height)).filter(ImageFilter.GaussianBlur(18))
            m = np.array(ws.getchannel('A'), np.float32) / 255 * a
            regn = np.array(reg, np.float32); basen = np.array(im.crop((x0, y0, x0 + ws.width, y0 + ws.height)), np.float32)
            mix = basen * (1 - m[..., None]) + regn * m[..., None]
            # soft shadow under glass
            shm = Image.fromarray((m * 255 * 0.35).astype(np.uint8)).filter(ImageFilter.GaussianBlur(20))
            sh = Image.new('RGBA', ws.size, (0, 0, 0, 0)); sh.putalpha(shm)
            im.paste(Image.fromarray(mix.astype(np.uint8), 'RGBA'), (x0, y0))
            comp(im, sh, x0, y0 + 26)
            comp(im, fade(wb, a), x0, y0)

def make_nova_c():
    global NOVA
    return NOVA

NOVA = None; STAMP = None; PRICE = None; CAL_BODY = None; CAL_SHAPE = None; SITECHIP = None
def build_assets():
    global NOVA, STAMP, PRICE, CAL_BODY, CAL_SHAPE, SITECHIP
    NOVA = make_nova(); STAMP = make_stamp(); PRICE = make_price()
    CAL_BODY, CAL_SHAPE = make_calendar()
    SITECHIP = chip('SITE PHOTO  ·  OCTOBER 2026', 30, fill=(18, 16, 13, 240), col=WHITE, padx=30, pady=20, track=4, r=14)
    if SITECHIP.width < 500 or SITECHIP.height < 76:
        big = rrect((max(500, SITECHIP.width), max(76, SITECHIP.height)), 14, (18, 16, 13, 240)); paste_c(big, T('SITE PHOTO  ·  OCTOBER 2026', 'anton', 30, WHITE, track=4, shadow=0), big.width / 2, big.height / 2); SITECHIP = big
    print('sitechip', SITECHIP.size)

# punch-in zoom after cuts into John / site segments
CUTS = [110, 196, 234, 429, 639, 698, 768]
def punch(im, i):
    for c in CUTS:
        if c <= i < c + 7:
            p = (i - c) / 6.0
            s = 1.07 - 0.07 * eo(p)
            big = im.resize((round(W * s), round(H * s)), Image.BICUBIC)
            ox = (big.width - W) / 2; oy = (big.height - H) * 0.4
            return big.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    if 234 <= i < 347:  # slow push-in while he explains
        s = 1 + 0.035 * (i - 234) / 113
        big = im.resize((round(W * s), round(H * s)), Image.BICUBIC)
        ox = (big.width - W) * 0.35; oy = (big.height - H) * 0.3
        return big.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    return im

MASKDIR = '/home/claude/v2/masks'
def person_layer(plate1080, i):
    p = os.path.join(MASKDIR, '%05d.png' % i)
    if not os.path.exists(p): return None
    m = Image.open(p).convert('L').resize((W, 1050), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))
    full = Image.new('L', (W, H), 0); full.paste(m, (0, 0))
    # below y 1000 keep everything person-side (text never goes there)
    L = plate1080.copy(); L.putalpha(full)
    return L

def frame(i, raw720, top):
    t = i / FPS
    if 347 <= i < 429: im = scene_A(t); caption(im, t)
    elif 492 <= i < 541: im = scene_B(t); caption(im, t)
    elif 541 <= i < 639: im = scene_C(t); caption(im, t)
    elif i >= 849: im = scene_E(t)
    else:
        fr = patch.patch(raw720, i, top) if i < 849 else raw720
        up = cv2.resize(fr, (W, H), interpolation=cv2.INTER_CUBIC)
        plate = Image.fromarray(up).convert('RGBA')
        if not (698 <= i < 768): topshade(plate)
        im = plate.copy()
        overlays_behind(im, t, i)
        pl = person_layer(plate, i) if (i < 110 or 196 <= i < 275 or 429 <= i < 492) else None
        if pl is not None: im.alpha_composite(pl)
        overlays_front(im, t, i, up)
    im = punch(im, i)
    return im.convert('RGB')

def main(out, f0=0, f1=NFR, only=None):
    build_assets()
    top = np.load('/home/claude/v2/plate_top.npy', mmap_mode='r')
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    frames_out = only
    if out.endswith('.mp4'):
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                '-i', SRC, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                                '-c:a', 'copy', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    else:
        enc = None; os.makedirs(out, exist_ok=True)
    t0 = time.time(); last = None
    for i in range(NFR):
        raw = dec.stdout.read(1280 * 720 * 3)
        if len(raw) == 1280 * 720 * 3: last = np.frombuffer(raw, np.uint8).reshape(1280, 720, 3)
        if i < f0: continue
        if i >= f1: break
        if only is not None and i not in only: continue
        im = frame(i, last, top)
        if enc: enc.stdin.write(im.tobytes())
        else: im.save(os.path.join(out, '%05d.jpg' % i), quality=90)
        if i % 60 == 0: print(i, '%.1fs' % (time.time() - t0), flush=True)
    dec.stdout.close(); dec.kill()
    if enc: enc.stdin.close(); enc.wait()
    print('done', time.time() - t0)

if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        only = set(int(x) for x in sys.argv[3].split(','))
        main(sys.argv[2], only=only)
    else:
        main(sys.argv[1])
