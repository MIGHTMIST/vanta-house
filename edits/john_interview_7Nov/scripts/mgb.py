# Brand motion graphics for Vanta House by Blackstone Real Estate (9 Nov 2026).
# Cards: fn(fr, tl, p) draw onto a 1080x1920 RGBA frame.  Overlays: gold_sweep / gold_dust draw over live footage.
# Palette: bronze-gold gradients (top light -> bottom dark, like the logo), ivory, deep ink.  All drawn in code.
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import iv, mg, mgk
from mgk import cl, smooth, ocubic, oexpo, oback, INTER_XB, INTER_B, INTER_MD

S = iv.S
LOGO = S + '/brand/logo_blackstone_vanta_640.png'
ANTON = iv.ANTON
GOLD_HI = (214, 178, 110); GOLD = (176, 138, 78); GOLD_LO = (122, 92, 50)
IVORY = (250, 248, 243); INK = (16, 16, 18); GREY = (150, 150, 150)
W, H = 1080, 1920
_c = {}

# ------------------------------------------------------------------ small tools
def seg(t, a, b): return cl((t - a) / (b - a))
def oquart(x): x = cl(x); return 1 - (1 - x) ** 4
def obounce(x):
    x = cl(x); n, d = 7.5625, 2.75
    if x < 1 / d: return n * x * x
    if x < 2 / d: x -= 1.5 / d; return n * x * x + 0.75
    if x < 2.5 / d: x -= 2.25 / d; return n * x * x + 0.9375
    x -= 2.625 / d; return n * x * x + 0.984375
def fade_out(tl, p, d=0.3): return 1 - smooth((tl - (p.get('dur', 99) - d)) / d)

def grad(w, h, stops, axis='v'):
    """RGB image, stops=[(pos, (r,g,b))...] from 0 to 1 along y (axis v) or x (axis h)"""
    n = h if axis == 'v' else w; u = np.linspace(0, 1, n)
    ps = [s[0] for s in stops]; ch = [np.interp(u, ps, [s[1][i] for s in stops]) for i in range(3)]
    a = np.stack(ch, -1).astype(np.uint8)
    a = np.repeat(a[:, None, :], w, 1) if axis == 'v' else np.repeat(a[None, :, :], h, 0)
    return Image.fromarray(a, 'RGB')

GOLD3 = [(0, GOLD_HI), (0.5, GOLD), (1, GOLD_LO)]
GOLD2 = [(0, GOLD_HI), (1, GOLD)]

def tint(mask, stops=GOLD3, axis='v'):
    L = grad(mask.width, mask.height, stops, axis).convert('RGBA'); L.putalpha(mask); return L

def ss_mask(w, h, fn, S_=3):
    """anti-aliased mask: fn(draw, scale) draws white on a S_x larger canvas"""
    m = Image.new('L', (w * S_, h * S_), 0); fn(ImageDraw.Draw(m), S_)
    return m.reduce(S_) if S_ > 1 else m

def comp(fr, L, x, y):
    """alpha_composite with clipping"""
    x, y = int(x), int(y); x0, y0 = max(0, -x), max(0, -y); x1, y1 = min(L.width, fr.width - x), min(L.height, fr.height - y)
    if x1 <= x0 or y1 <= y0: return
    if (x0, y0, x1, y1) != (0, 0, L.width, L.height): L = L.crop((x0, y0, x1, y1))
    fr.alpha_composite(L, (x + x0, y + y0))

def with_alpha(L, a):
    if a >= 0.999: return L
    L = L.copy(); L.putalpha(L.getchannel('A').point(lambda v: int(v * a))); return L

def ss_draw(fr, bbox, fn, S_=3, col=GOLD):
    """vector drawing, anti-aliased by supersampling. fn(draw, P, S_) with P(x,y)->canvas coords"""
    x0, y0, x1, y1 = [int(v) for v in bbox]; x0 = max(x0, 0); y0 = max(y0, 0); x1 = min(x1, fr.width); y1 = min(y1, fr.height)
    if x1 <= x0 or y1 <= y0: return
    L = Image.new('RGBA', ((x1 - x0) * S_, (y1 - y0) * S_), col + (0,)); d = ImageDraw.Draw(L)
    fn(d, lambda x, y: ((x - x0) * S_, (y - y0) * S_), S_)
    fr.alpha_composite(L.reduce(S_), (x0, y0))

def TX(txt, size, path=INTER_MD, track=0, fill=IVORY, stops=None):
    """tracked text layer (cached); fill = rgb, or stops -> vertical gradient"""
    k = ('tx', txt, size, path, track, fill, str(stops))
    if k in _c: return _c[k]
    F = mgk.font(path, size); pad = 14
    adv = [F.getlength(txt[:i + 1]) - F.getlength(txt[:i]) for i in range(len(txt))]
    w = int(sum(adv) + track * (len(txt) - 1)) + 2 * pad; asc, desc = F.getmetrics(); h = asc + desc + 2 * pad
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m); x = pad
    for ch, a in zip(txt, adv): d.text((x, pad), ch, font=F, fill=255); x += a + track
    L = tint(m, stops) if stops else Image.merge('RGBA', [Image.new('L', (w, h), c) for c in fill] + [m])
    _c[k] = L; return L

def put(fr, L, cx, cy, a=1.0, dy=0, sc=1.0):
    mgk.put(fr, L, cx, cy + dy, a=a, sc=sc)

def hline(fr, cx, y, w, h, stops, a=1.0):
    w = int(w)
    if w < 2 or a <= 0: return
    L = tint(Image.new('L', (w, h), 255), stops, 'h'); comp(fr, with_alpha(L, a), cx - w / 2, y - h / 2)

# ------------------------------------------------------------------ background
def base_bg():
    if 'bg' not in _c:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.46) / (H * 0.62)) ** 2)
        k = np.clip(1 - r, 0, 1) ** 1.6
        c = np.array(INK, np.float32)[None, None, :] + k[..., None] * np.array([13, 11, 8], np.float32)
        _c['bg'] = Image.fromarray(np.clip(c, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    return _c['bg']

def new_frame(fr):
    fr.paste(base_bg()); return base_bg()

def grain(fr, f, amt=2.6):
    """fine film grain from a cached bank of noise frames (fast)"""
    if 'gb' not in _c:
        rng = np.random.default_rng(3); bank = []
        for i in range(6):
            n = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32); n = np.repeat(np.repeat(n, 2, 0), 2, 1)
            bank.append(Image.fromarray(np.clip(128 + n * amt, 0, 255).astype(np.uint8)).convert('RGB'))
        _c['gb'] = bank
    fr.paste(ImageChops.add(fr.convert('RGB'), _c['gb'][f % 6], 1.0, -128))

def finish(fr, tl, p, bgimg, out=None):
    """end fade (towards the background) + subtle grain"""
    o = fade_out(tl, p) if out is None else out
    if o < 0.999:
        fr.paste(Image.blend(bgimg, fr, o))
    grain(fr, int(tl * 30))

# ------------------------------------------------------------------ emblem (keyed out of the logo)
def emblem():
    """gold-gradient emblem on transparent, upscaled; returns RGBA (master ~ 4x)"""
    if 'emb' in _c: return _c['emb']
    im = Image.open(LOGO).convert('RGB').crop((235, 150, 405, 335))
    b = np.asarray(im).astype(np.float32)[..., 2]
    a = np.clip((242 - b) / (242 - 115), 0, 1)
    A = Image.fromarray((a * 255).astype(np.uint8)).resize((im.width * 5, im.height * 5), Image.LANCZOS)
    a2 = np.asarray(A).astype(np.float32) / 255
    a2 = np.clip((a2 - 0.30) / 0.40, 0, 1); a2 = a2 * a2 * (3 - 2 * a2)          # re-sharpen edges lost in the upscale
    A = Image.fromarray((a2 * 255).astype(np.uint8)); bb = A.point(lambda v: 255 if v > 40 else 0).getbbox()
    A = A.crop(bb)
    _c['emb'] = tint(A, GOLD3); return _c['emb']

def emblem_at(width):
    E = emblem(); k = ('embs', width)
    if k not in _c: _c[k] = E.resize((width, int(E.height * width / E.width)), Image.LANCZOS)
    return _c[k]

# ------------------------------------------------------------------ 1. INTRO
INTRO_TEXT = ['Who is building', 'Vanta House?']
_INTRO_GOLD_FROM = len(INTRO_TEXT[0])           # chars of line 2 are gold

def intro_key_times():
    """timeline seconds (relative to card start) of each keystroke, 28 keys incl. spaces, 2.10 s -> 3.80 s, uneven"""
    n = sum(len(s) for s in INTRO_TEXT); rng = np.random.default_rng(11)
    w = rng.uniform(0.55, 1.5, n - 1)
    chars = ''.join(INTRO_TEXT)
    for i, ch in enumerate(chars[:-1]):
        if ch == ' ': w[i] *= 1.35                      # tiny hesitation on spaces
    w[len(INTRO_TEXT[0]) - 1] *= 1.8                    # slight beat at the line break
    t = 2.10 + np.concatenate([[0], np.cumsum(w)]) / w.sum() * 1.70
    return [round(float(x), 3) for x in t]

PH_W, PH_H, PH_R = 454, 940, 66
PH_CX, PH_CY = 540, 860

def _phone():
    if 'ph' in _c: return _c['ph']
    pad = 40; w, h = PH_W + 2 * pad, PH_H + 2 * pad
    def outline(d, s):
        d.rounded_rectangle((pad * s, pad * s, (pad + PH_W) * s, (pad + PH_H) * s), PH_R * s, outline=255, width=int(3.2 * s))
    frame = tint(ss_mask(w, h, outline, 3))
    def inner(d, s):
        i = 3
        d.rounded_rectangle(((pad + i) * s, (pad + i) * s, (pad + PH_W - i) * s, (pad + PH_H - i) * s), (PH_R - i) * s, fill=255)
    sm = ss_mask(w, h, inner, 2)
    back = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    scr = grad(w, h, [(0, (24, 23, 22)), (1, (14, 14, 15))]).convert('RGBA'); scr.putalpha(sm); back.alpha_composite(scr); back.alpha_composite(frame)
    # dynamic island
    isl = ss_mask(w, h, lambda d, s: d.rounded_rectangle(((pad + PH_W / 2 - 52) * s, (pad + 24) * s, (pad + PH_W / 2 + 52) * s, (pad + 24 + 30) * s), 15 * s, fill=255), 2)
    back.alpha_composite(Image.merge('RGBA', [Image.new('L', (w, h), 0)] * 3 + [isl.point(lambda v: int(v * 0.9))]))
    # contents
    con = Image.new('RGBA', (w, h), (0, 0, 0, 0)); cx = w // 2; top = pad
    def P(L, y, a=1.0): con.alpha_composite(with_alpha(L, a), (int(cx - L.width / 2), int(top + y - L.height / 2)))
    P(TX('INCOMING CALL', 20, INTER_MD, 5, GREY), 168)
    E = emblem_at(150); P(E, 345)
    P(TX('BLACKSTONE REAL ESTATE', 19, INTER_XB, 3.2, stops=GOLD2), 490)
    P(TX('YOUR TURNKEY HOUSING SOLUTION', 11, INTER_MD, 2.6, (130, 130, 130)), 524)
    # slide-to-answer track
    ty = 810
    def track(d, s):
        d.rounded_rectangle((pad * s + (PH_W / 2 - 130) * s, (pad + ty - 28) * s, pad * s + (PH_W / 2 + 130) * s, (pad + ty + 28) * s), 28 * s, outline=255, width=int(1.6 * s))
    con.alpha_composite(with_alpha(tint(ss_mask(w, h, track, 3), [(0, (110, 110, 110)), (1, (80, 80, 80))]), 0.9))
    kn = ss_mask(w, h, lambda d, s: d.ellipse((pad * s + (PH_W / 2 - 124) * s, (pad + ty - 22) * s, pad * s + (PH_W / 2 - 80) * s, (pad + ty + 22) * s), fill=255), 3)
    con.alpha_composite(tint(kn, GOLD3))
    _c['ph'] = (back, con, pad); return _c['ph']

def _glow_sprite():
    if 'gl' not in _c:
        gw, gh = 360, 760; yy, xx = np.mgrid[0:gh, 0:gw].astype(np.float32)
        r = np.sqrt(((xx - gw / 2) / (gw / 2)) ** 2 + ((yy - gh * 0.42) / (gh * 0.5)) ** 2)
        a = np.clip(1 - r, 0, 1) ** 2
        L = Image.new('RGBA', (gw, gh), GOLD_HI + (0,)); L.putalpha(Image.fromarray((a * 255).astype(np.uint8))); _c['gl'] = L
    return _c['gl']

def _ring(fr, off, a, cx, cy):
    if a <= 0.01: return
    x0, y0 = cx - PH_W / 2 - off, cy - PH_H / 2 - off; x1, y1 = cx + PH_W / 2 + off, cy + PH_H / 2 + off
    bb = (x0 - 8, y0 - 8, x1 + 8, y1 + 8)
    bx, by = int(bb[0]), int(bb[1]); bw, bh = int(bb[2] - bb[0]), int(bb[3] - bb[1])
    m = ss_mask(bw, bh, lambda d, s: d.rounded_rectangle(((x0 - bx) * s, (y0 - by) * s, (x1 - bx) * s, (y1 - by) * s), (PH_R + off) * s, outline=int(255 * a), width=int(2 * s)), 2)
    L = Image.new('RGBA', (bw, bh), GOLD_HI + (0,)); L.putalpha(m); comp(fr, L, bx, by)

def intro_card(fr, tl, p):
    bgi = new_frame(fr); dur = p.get('dur', 5.6)
    # ---- phone 0 - 2.1
    if tl < 2.2:
        pin = oquart(seg(tl, 0.0, 0.5)); pout = smooth(seg(tl, 1.62, 2.1)); a = pin * (1 - pout)
        jit = 0.0
        for a0, a1 in ((0.15, 0.65), (0.9, 1.35)):
            if a0 <= tl <= a1:
                e = math.sin(math.pi * (tl - a0) / (a1 - a0)) ** 0.5
                jit = e * (5.0 * math.sin(tl * 2 * math.pi * 24) + 2.5 * math.sin(tl * 2 * math.pi * 37 + 1))
        cx = PH_CX + jit; cy = PH_CY - 150 * oquart(seg(tl, 1.62, 2.1)) ** 1.0 + 14 * (1 - pin)
        for st in (0.15, 0.6, 1.05):                                    # ring pulses
            e = seg(tl, st, st + 0.85)
            if 0 < e < 1: _ring(fr, 18 + 170 * oquart(e), 0.8 * (1 - smooth(e)) * (1 - pout) * pin, cx, cy)
        back, con, pad = _phone(); ox, oy = int(cx - back.width / 2), int(cy - back.height / 2)
        comp(fr, with_alpha(back, a), ox, oy)
        pulse = 0.55 + 0.45 * math.sin(tl * 2 * math.pi * 1.6) ** 2 if tl < 1.7 else 0.4
        G = _glow_sprite(); gx, gy = int(cx - G.width / 2), int(cy - G.height * 0.42 - 40)
        comp(fr, with_alpha(G, 0.20 * pulse * a), gx, gy)
        comp(fr, with_alpha(con, a), ox, oy)
    # ---- typing 2.1 - 4.3
    if 2.0 <= tl < 4.35:
        keys = _keys(); F = mgk.font(INTER_XB, 84); track = 1.2
        n = sum(1 for k in keys if tl >= k); a_all = oquart(seg(tl, 2.0, 2.3)) * (1 - smooth(seg(tl, 4.05, 4.3)))
        ly = [880, 1000]; layer = Image.new('RGBA', (W, 330), IVORY + (0,)); d = ImageDraw.Draw(layer); idx = 0; cur = None
        for li, line in enumerate(INTRO_TEXT):
            tw = F.getlength(line) + track * (len(line) - 1); x0 = (W - tw) / 2; yy = ly[li] - 760
            for i, ch in enumerate(line):
                x = x0 + F.getlength(line[:i]) + track * i
                if idx < n:
                    ka = oquart((tl - keys[idx]) / 0.07); col = GOLD_HI if li == 1 else IVORY
                    if ch != ' ': d.text((x, yy - 42 + 5 * (1 - ka)), ch, font=F, fill=col + (int(255 * ka),))
                    cur = (x + F.getlength(ch) + track, yy)
                elif cur is None and idx == 0: cur = (x0, yy)
                idx += 1
        if cur is None: cur = ((W - (F.getlength(INTRO_TEXT[0]) + track * 14)) / 2, ly[0] - 760)
        # cursor sits at the end of the last typed char, solid while typing, blinking after
        since = tl - (keys[max(n - 1, 0)] if n else 2.0)
        on = True if (n and since < 0.35 and tl < keys[-1] + 0.01) else (int((tl - 2.0) * 2.4) % 2 == 0)
        if n == 0: on = int((tl - 2.0) * 2.4) % 2 == 0
        if on:
            kx, ky = cur; d.rectangle((kx + 4, ky - 46, kx + 9, ky + 42), fill=GOLD_HI + (255,))
        comp(fr, with_alpha(layer, a_all), 0, 760 - 6 * (1 - a_all) * 0 - 12 * smooth(seg(tl, 4.05, 4.3)))
        # fine hairline above the line, draws in
        hline(fr, 540, 800, 90 * oquart(seg(tl, 2.0, 2.5)) * (1 - smooth(seg(tl, 4.05, 4.3))), 2, GOLD2, a_all)
    # ---- logo reveal 4.3 - 5.6
    if tl >= 4.3:
        u = tl - 4.3; E = emblem_at(380); ex, ey = 540 - E.width / 2, 690 - E.height / 2
        wipe = oexpo(seg(u, 0.0, 0.62))                      # bottom -> top
        mk = Image.new('L', E.size, 0); ImageDraw.Draw(mk).rectangle((0, int(E.height * (1 - wipe)), E.width, E.height), fill=255)
        edge = int(E.height * (1 - wipe))
        mk = Image.new('L', E.size, 0); arr = np.zeros((E.height, E.width), np.float32)
        yy = np.arange(E.height)[:, None]; arr = np.clip((yy - (E.height * (1 - wipe) - 30 * wipe)) / 30, 0, 1) * np.ones((1, E.width), np.float32)
        mk = Image.fromarray((arr * 255).astype(np.uint8))
        EL = E.copy(); EL.putalpha(ImageChops.multiply(E.getchannel('A'), mk))
        # thin light sweep across the emblem
        sw = seg(u, 0.38, 0.95)
        if 0 < sw < 1:
            xs = np.arange(E.width)[None, :].astype(np.float32); ys = np.arange(E.height)[:, None].astype(np.float32)
            pos = -0.3 * E.width + (1.6 * E.width) * oquart(sw); dd = (xs + ys * 0.45) - pos
            band = np.exp(-(dd / (E.width * 0.045)) ** 2) * 0.85 * math.sin(math.pi * sw) ** 0.6
            hi = Image.new('RGBA', E.size, (255, 244, 214, 0)); hi.putalpha(Image.fromarray((band * 255).astype(np.uint8)))
            hi.putalpha(ImageChops.multiply(hi.getchannel('A'), EL.getchannel('A'))); EL.alpha_composite(hi)
        comp(fr, EL, ex, ey)
        # hit flash line: hairline at the base that opens and settles
        ln = seg(u, 0.0, 0.5)
        hline(fr, 540, ey + E.height + 34, 520 * oexpo(ln), 2, [(0, GOLD_LO), (0.5, GOLD_HI), (1, GOLD_LO)], 1 - 0.0)
        ta = oquart(seg(u, 0.32, 0.72)); put(fr, TX('BLACKSTONE REAL ESTATE', 40, INTER_XB, 9, stops=GOLD2), 540, ey + E.height + 96, ta, 18 * (1 - ta))
        tb = oquart(seg(u, 0.52, 0.92)); put(fr, TX('VANTA HOUSE  ·  NAGURU, KAMPALA', 25, INTER_MD, 7.5, IVORY), 540, ey + E.height + 156, tb * 0.92, 18 * (1 - tb))
    finish(fr, tl, p, bgi, out=1 - smooth(seg(tl, dur - 0.25, dur)))

def _keys():
    if 'keys' not in _c: _c['keys'] = intro_key_times()
    return _c['keys']

# ------------------------------------------------------------------ 2. BANKING
_CHART = (90, 380, 990, 960)
def _chart():
    if 'chart' in _c: return _c['chart']
    x0, y0, x1, y1 = _CHART; w, h = x1 - x0, y1 - y0
    cp = [(0, .06), (.07, .12), (.15, .10), (.25, .22), (.34, .29), (.43, .25), (.53, .41), (.62, .47), (.71, .44), (.80, .63), (.90, .76), (1, .95)]
    P = np.array(cp, np.float64); P = np.vstack([P[0] - (P[1] - P[0]), P, P[-1] + (P[-1] - P[-2])])
    xs, ys = [], []
    for i in range(1, len(P) - 2):
        for s in np.linspace(0, 1, 40, endpoint=False):
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            q = 0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3)
            xs.append(q[0]); ys.append(q[1])
    xs.append(1.0); ys.append(cp[-1][1])
    px = np.array(xs) * w; py = h - np.array(ys) * h * 0.97
    S_ = 3; pad = 20
    line = ss_mask(w + 2 * pad, h + 2 * pad, lambda d, s: d.line([((a + pad) * s, (b + pad) * s) for a, b in zip(px, py)], fill=255, width=int(6 * s), joint='curve'), S_)
    fill_m = ss_mask(w + 2 * pad, h + 2 * pad, lambda d, s: d.polygon([((a + pad) * s, (b + pad) * s) for a, b in zip(px, py)] + [((w + pad) * s, (h + pad) * s), (pad * s, (h + pad) * s)], fill=255), 2)
    fa = np.asarray(fill_m).astype(np.float32) / 255
    vy = np.linspace(1, 0, h + 2 * pad)[:, None]; fa = fa * (vy ** 1.4) * 0.16                   # soft area under the curve, fades downward
    F = tint(Image.fromarray((fa * 255).astype(np.uint8)), GOLD3)
    Ln = tint(line, GOLD3); F.alpha_composite(Ln)
    _c['chart'] = (F, px, py, pad); return _c['chart']

def banking_card(fr, tl, p):
    bgi = new_frame(fr); x0, y0, x1, y1 = _CHART
    # grid at ~6 % ivory
    ga = 15
    for i in range(6):
        y = y0 + i * (y1 - y0) / 5; u = oquart(seg(tl, 0.05 + 0.06 * i, 0.7 + 0.06 * i))
        if u > 0: ImageDraw.Draw(fr).line((x0, y, x0 + (x1 - x0) * u, y), fill=IVORY + (255,), width=1) if False else _gline(fr, x0, y, x0 + (x1 - x0) * u, y, ga)
    for i in range(7):
        x = x0 + i * (x1 - x0) / 6; u = oquart(seg(tl, 0.15 + 0.05 * i, 0.8 + 0.05 * i))
        if u > 0: _gline(fr, x, y1, x, y1 - (y1 - y0) * u, ga)
    # curve draws left -> right
    F, px, py, pad = _chart(); u = smooth(seg(tl, 0.35, 2.15)); cw = int((x1 - x0 + pad) * u)
    if cw > 2:
        comp(fr, F.crop((0, 0, min(F.width, cw + pad), F.height)) if False else _clip_cols(F, cw + pad // 2), x0 - pad, y0 - pad)
        xc = u * (x1 - x0); yc = float(np.interp(xc, px, py))
        a = 1 - smooth(seg(tl, 2.3, 2.6)) * 0.0
        tx, ty = x0 + xc, y0 + yc
        ss_draw(fr, (tx - 30, ty - 30, tx + 30, ty + 30), lambda d, P, s: (d.ellipse((*P(tx - 7, ty - 7), *P(tx + 7, ty + 7)), fill=IVORY + (255,)),
                d.ellipse((*P(tx - 15, ty - 15), *P(tx + 15, ty + 15)), outline=GOLD_HI + (int(200 * (1 - u * 0.6)),), width=int(2 * s))), 3, GOLD_HI)
    # headline
    A = TX('10 YEARS', 230, ANTON, 7, IVORY); ha = oquart(seg(tl, 0.9, 1.5))
    if ha > 0:
        hh = int(A.height * ha); layer = A.crop((0, A.height - hh, A.width, A.height)) if False else A
        put(fr, A, 540, 1130, ha, 40 * (1 - ha))
    hline(fr, 540, 1262, 260 * oexpo(seg(tl, 1.5, 2.1)), 8, [(0, GOLD_HI), (1, GOLD_LO)], 1)
    put(fr, TX('INVESTMENT BANKING  ·  CHINA', 31, INTER_XB, 9, stops=GOLD2), 540, 1334, oquart(seg(tl, 1.75, 2.3)), 16 * (1 - oquart(seg(tl, 1.75, 2.3))))
    finish(fr, tl, p, bgi)

def _gline(fr, x0, y0, x1, y1, a):
    L = Image.new('RGBA', (int(abs(x1 - x0)) + 2, int(abs(y1 - y0)) + 2), IVORY + (a,))
    comp(fr, L, min(x0, x1), min(y0, y1))

def _clip_cols(F, cw):
    L = F.crop((0, 0, min(F.width, cw), F.height)); return L

# ------------------------------------------------------------------ 3. ROUTE
def _map_layers():
    if 'maplay' in _c: return _c['maplay']
    base, ug, xy = mgk._map_base(W, H); y0 = 520; y1 = 1300
    ba = np.asarray(base)[y0:y1, :, 3].astype(np.float32) / 255; ua = np.asarray(ug)[y0:y1, :, 3].astype(np.float32) / 255
    dots = Image.new('RGBA', (W, y1 - y0), IVORY + (0,)); dots.putalpha(Image.fromarray((ba * 0.62 * 255).astype(np.uint8)))
    uga = Image.new('RGBA', (W, y1 - y0), GOLD_HI + (0,)); uga.putalpha(Image.fromarray((ua * 0.55 * 255).astype(np.uint8)))
    hh = y1 - y0; yy = np.arange(hh) + y0; fy = np.clip(np.minimum(yy - 596, 1204 - yy) / 90.0, 0, 1)[:, None]; fx = np.clip(np.minimum(np.arange(W) - 52, 1028 - np.arange(W)) / 90.0, 0, 1)[None, :]
    fm = (fy * fx) ** 1.5
    for im in (dots, uga): im.putalpha(Image.fromarray((np.asarray(im.getchannel('A')).astype(np.float32) * fm).astype(np.uint8)))
    z = 1.12; rs = lambda im: im.resize((int(im.width * z), int(im.height * z)), Image.BILINEAR)
    _c['maplay'] = (rs(dots), rs(uga), xy, y0); return _c['maplay']

def route_card(fr, tl, p):
    bgi = new_frame(fr); dur = p.get('dur', 4.2)
    dots, uga, xy, my0 = _map_layers(); A = xy(121.47, 31.23); B = xy(32.58, 0.35)
    z = 1.12; cxp, cyp = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2 + 20; pan = 16 * (0.5 - smooth(tl / dur))      # fixed zoom, slow drift
    zz = lambda pt: (cxp + (pt[0] - cxp) * z + pan, cyp + (pt[1] - cyp) * z)
    t_route0, t_route1 = 0.55, 2.55; u = smooth(seg(tl, t_route0, t_route1)); arr = oquart(seg(tl, t_route1 - 0.1, t_route1 + 0.5))
    lay = Image.new('RGBA', dots.size, (0, 0, 0, 0)); lay.alpha_composite(with_alpha(dots, oquart(seg(tl, 0.0, 0.7))));
    if arr > 0: lay.alpha_composite(with_alpha(uga, arr))
    ox = cxp + (0 - cxp) * z + pan; oy = cyp + (my0 - cyp) * z; comp(fr, lay, ox, oy)
    a0, b0 = zz(A), zz(B); ctrl = ((a0[0] + b0[0]) / 2 + 20, (a0[1] + b0[1]) / 2 - 250 * z)
    N = 120; bez = lambda s: ((1 - s) ** 2 * a0[0] + 2 * (1 - s) * s * ctrl[0] + s * s * b0[0], (1 - s) ** 2 * a0[1] + 2 * (1 - s) * s * ctrl[1] + s * s * b0[1])
    ua_ = oquart(seg(tl, 0.25, 0.8))
    # title
    put(fr, TX('CHINA  TO  UGANDA', 46, INTER_XB, 12, IVORY), 540, 470, oquart(seg(tl, 0.1, 0.7)), 18 * (1 - oquart(seg(tl, 0.1, 0.7))))
    hline(fr, 540, 530, 120 * oexpo(seg(tl, 0.4, 1.0)), 3, GOLD2)
    # endpoints
    ss_draw(fr, (a0[0] - 40, a0[1] - 40, a0[0] + 40, a0[1] + 40), lambda d, P, s: d.ellipse((*P(a0[0] - 7, a0[1] - 7), *P(a0[0] + 7, a0[1] + 7)), fill=IVORY + (int(255 * ua_),)), 3, IVORY)
    put(fr, TX('SHANGHAI', 28, INTER_MD, 7, IVORY), a0[0] - 50, a0[1] + 46, ua_, 0)
    n = int(N * u)
    if n > 1:
        pts = [bez(i / N) for i in range(n + 1)]
        xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
        def dr(d, P, s):
            for i in range(len(pts) - 1):
                t = i / N; col = tuple(int(GOLD_LO[k] + (GOLD_HI[k] - GOLD_LO[k]) * (t ** 0.8)) for k in range(3))
                d.line((*P(*pts[i]), *P(*pts[i + 1])), fill=col + (255,), width=int(4.5 * s))
        ss_draw(fr, (min(xs) - 20, min(ys) - 20, max(xs) + 20, max(ys) + 20), dr, 2, GOLD)
        hx, hy = pts[-1]
        if u < 1:
            ss_draw(fr, (hx - 40, hy - 40, hx + 40, hy + 40), lambda d, P, s: (d.ellipse((*P(hx - 16, hy - 16), *P(hx + 16, hy + 16)), outline=GOLD_HI + (110,), width=int(1.6 * s)),
                    d.ellipse((*P(hx - 7, hy - 7), *P(hx + 7, hy + 7)), fill=(255, 240, 205, 255))), 3, GOLD_HI)
    if arr > 0:
        for st in (t_route1 - 0.05, t_route1 + 0.65):
            e = seg(tl, st, st + 1.1)
            if 0 < e < 1:
                R = 12 + 70 * oquart(e); al = int(210 * (1 - smooth(e)) * arr)
                ss_draw(fr, (b0[0] - R - 6, b0[1] - R - 6, b0[0] + R + 6, b0[1] + R + 6), lambda d, P, s: d.ellipse((*P(b0[0] - R, b0[1] - R), *P(b0[0] + R, b0[1] + R)), outline=GOLD_HI + (al,), width=int(2.2 * s)), 3, GOLD_HI)
        ss_draw(fr, (b0[0] - 30, b0[1] - 30, b0[0] + 30, b0[1] + 30), lambda d, P, s: (d.ellipse((*P(b0[0] - 12, b0[1] - 12), *P(b0[0] + 12, b0[1] + 12)), fill=GOLD_HI + (int(255 * arr),)),
                d.ellipse((*P(b0[0] - 5, b0[1] - 5), *P(b0[0] + 5, b0[1] + 5)), fill=IVORY + (int(255 * arr),))), 3, GOLD_HI)
        put(fr, TX('KAMPALA', 34, INTER_XB, 9, IVORY), b0[0] + 30, b0[1] + 64, arr, 10 * (1 - arr))
        put(fr, TX('UGANDA', 22, INTER_MD, 7, stops=GOLD2), b0[0] + 30, b0[1] + 104, arr * oquart(seg(tl, t_route1 + 0.2, t_route1 + 0.6)))
    finish(fr, tl, p, bgi)

# ------------------------------------------------------------------ 4. UGANDA
def _pin():
    if 'pin' in _c: return _c['pin']
    R = 56; dd = 2.2 * R; pad = 12; w = 2 * R + 2 * pad; h = int(R + dd + 2 * pad)
    phi = math.acos(R / dd)
    def dr(d, s):
        cx, cy = w / 2 * s, (pad + R) * s
        a0 = math.pi / 2 + phi; a1 = math.pi / 2 - phi + 2 * math.pi
        pts = [(cx + R * s * math.cos(a0 + (a1 - a0) * i / 80), cy + R * s * math.sin(a0 + (a1 - a0) * i / 80)) for i in range(81)] + [(cx, cy + dd * s)]
        d.polygon(pts, fill=255); d.ellipse((cx - 0.38 * R * s, cy - 0.38 * R * s, cx + 0.38 * R * s, cy + 0.38 * R * s), fill=0)
    m = ss_mask(w, h, dr, 4); _c['pin'] = (tint(m, GOLD3), w, h, pad, R, dd); return _c['pin']

def uganda_card(fr, tl, p):
    bgi = new_frame(fr); G = 810; L, pw, ph, pad, R, dd = _pin()
    pa = oquart(seg(tl, 0.0, 0.25)); drop = 1 - obounce(seg(tl, 0.0, 0.7)); y_tip = G - 420 * drop
    # soft ground shadow
    sa = oquart(seg(tl, 0.15, 0.7)) * 0.5
    ss_draw(fr, (540 - 60, G - 14, 540 + 60, G + 14), lambda d, P, s: d.ellipse((*P(540 - 26 * (1 - 0.4 * drop), G - 6), *P(540 + 26 * (1 - 0.4 * drop), G + 6)), fill=(0, 0, 0, int(200 * sa))), 3, (0, 0, 0))
    for st in (0.30, 0.78):
        e = seg(tl, st, st + 1.2)
        if 0 < e < 1:
            rx = 22 + 300 * oquart(e); ry = rx * 0.30; al = int(200 * (1 - smooth(e)))
            ss_draw(fr, (540 - rx - 6, G - ry - 6, 540 + rx + 6, G + ry + 6), lambda d, P, s: d.ellipse((*P(540 - rx, G - ry), *P(540 + rx, G + ry)), outline=GOLD_HI + (al,), width=int(2 * s)), 3, GOLD_HI)
    comp(fr, with_alpha(L, pa), 540 - pw / 2, y_tip - (ph - pad))
    ka = oquart(seg(tl, 0.55, 1.15))
    put(fr, TX('KAMPALA', 118, INTER_XB, 20, IVORY), 540 + 10, 1025, ka, 24 * (1 - ka))
    hline(fr, 540, 1108, 440 * oexpo(seg(tl, 0.85, 1.5)), 3, [(0, GOLD_LO), (0.5, GOLD_HI), (1, GOLD_LO)])
    ua = oquart(seg(tl, 1.05, 1.6))
    put(fr, TX('UGANDA  ·  EAST AFRICA', 30, INTER_MD, 9, stops=GOLD2), 540 + 4, 1168, ua, 14 * (1 - ua))
    finish(fr, tl, p, bgi)

# ------------------------------------------------------------------ 5. OVERLAYS (over live footage)
def gold_sweep(fr, t, t_cut, strength=0.6):
    """diagonal soft gold light sweep, screen blend, peaks at t_cut (about 0.8 s long)"""
    pr = (t - (t_cut - 0.4)) / 0.8
    if pr <= 0 or pr >= 1: return
    env = math.sin(math.pi * pr) ** 2 * strength
    w, h = 270, 480; k = ('sw',)
    if k not in _c:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); _c[k] = ((xx / w) * 0.62 + (yy / h) * 0.38)   # diagonal coordinate 0..1
    c = _c[k]; pos = -0.35 + 1.7 * smooth(pr)
    d = c - pos
    m = 0.75 * np.exp(-(d / 0.20) ** 2) + 0.40 * np.exp(-(d / 0.04) ** 2)        # broad glow + brighter core
    m = np.clip(m * env, 0, 1)
    M = Image.fromarray((m * 255).astype(np.uint8)).resize(fr.size, Image.BICUBIC)
    chans = [M.point(lambda v, c_=c_: int(v * c_ / 255)) for c_ in (255, 205, 135)]
    rgb = fr.convert('RGB'); out = ImageChops.screen(rgb, Image.merge('RGB', chans))
    fr.paste(out.convert('RGBA'))

def gold_dust(fr, t, t0, t1, n=80):
    """fine drifting gold particles (deterministic) between t0 and t1"""
    if t < t0 or t > t1: return
    a_env = oquart(seg(t, t0, t0 + 0.7)) * (1 - smooth(seg(t, t1 - 0.5, t1)))
    if 'dust' not in _c:
        rng = np.random.default_rng(5)
        _c['dust'] = dict(x=rng.uniform(0, W, n), y=rng.uniform(0, H, n), vx=rng.uniform(-6, 6, n), vy=-rng.uniform(10, 34, n),
                         r=rng.choice([1.8, 2.5, 3.3, 4.5], n, p=[.4, .3, .2, .1]), ph=rng.uniform(0, 6.28, n), fq=rng.uniform(0.4, 1.3, n), al=rng.uniform(0.35, 0.9, n))
        for r in (1.8, 2.5, 3.3, 4.5):
            sz = int(r * 6) | 1; yy, xx = np.mgrid[0:sz, 0:sz].astype(np.float32); rr = np.hypot(xx - sz // 2, yy - sz // 2) / (r * 1.5)
            a = np.clip(1 - rr, 0, 1) ** 1.3; L = Image.new('RGBA', (sz, sz), GOLD_HI + (0,)); L.putalpha(Image.fromarray((a * 255).astype(np.uint8))); _c[('ds', r)] = L
    D = _c['dust']; tt = t - t0; layer = Image.new('RGBA', fr.size, GOLD_HI + (0,))
    for i in range(min(n, len(D['x']))):
        x = (D['x'][i] + D['vx'][i] * tt + 14 * math.sin(tt * 0.5 + D['ph'][i])) % W; y = (D['y'][i] + D['vy'][i] * tt) % H
        a = D['al'][i] * (0.55 + 0.45 * math.sin(tt * D['fq'][i] * 2 + D['ph'][i])) * a_env
        S_ = _c[('ds', D['r'][i])]; comp(layer, with_alpha(S_, a), x - S_.width / 2, y - S_.height / 2)
    fr.alpha_composite(layer)

def warm():
    """pre-build the heavy caches (dot map, emblem, phone, grain bank) so the first frame is not slow"""
    fr = Image.new('RGBA', (W, H))
    for f, t in ((intro_card, 1.0), (intro_card, 4.8), (banking_card, 1.0), (route_card, 1.0), (uganda_card, 1.0)): f(fr, t, {'dur': 5})
    gold_dust(fr, 1.0, 0.0, 3.0)
