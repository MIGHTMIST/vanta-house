# Own motion graphics for the John / Vanta films (8 Nov). Every graphic is drawn in code, frame by frame, no stock.
# Cards: draw(fr, tl, p) for iv 'card' pics.  Overlays: fn(fr, tl, p) called from an extra() hook.
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import iv
from iv import text_layer, place, ANTON, INTERB, WHITE, GOLD, ease, eout, clamp

NAVY0, NAVY1 = (8, 14, 26), (18, 32, 54)          # cool past
WARM0, WARM1 = (20, 13, 8), (52, 33, 16)            # warm Africa / Vanta
STEEL = (150, 178, 210)
_c = {}

def lerp(a, b, u): return tuple(int(x + (y - x) * u) for x, y in zip(a, b))

def bg(fr, c0, c1, tl, vign=True):
    """vertical gradient + soft moving glow, never a still frame"""
    OW, OH = fr.size; k = ('bg', OW, OH, c0, c1)
    if k not in _c:
        y = np.linspace(0, 1, OH)[:, None, None]; x = np.linspace(-1, 1, OW)[None, :, None]
        g = np.array(c0, np.float32) * (1 - y) + np.array(c1, np.float32) * y
        if vign: g = g * (1 - 0.35 * (x ** 2))
        _c[k] = g
    g = _c[k]
    cx = 0.5 + 0.12 * math.sin(tl * 0.6); cy = 0.42 + 0.05 * math.cos(tl * 0.5)
    kk = ('glow', OW, OH)
    if kk not in _c:
        yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32); _c[kk] = (xx, yy)
    xx, yy = _c[kk]
    glow = np.exp(-(((xx - cx * OW) / (OW * 0.55)) ** 2 + ((yy - cy * OH) / (OH * 0.35)) ** 2))[..., None]
    img = np.clip(g + glow * np.array(c1, np.float32) * 0.9, 0, 255).astype(np.uint8)
    fr.paste(Image.fromarray(img).convert('RGBA'))

def grain(fr, amount=7, seed=0):
    OW, OH = fr.size; rng = np.random.default_rng(seed)
    n = rng.normal(0, amount, (OH // 2, OW // 2)).astype(np.float32)
    n = np.repeat(np.repeat(n, 2, 0), 2, 1)
    a = np.asarray(fr).astype(np.float32); a[..., :3] = np.clip(a[..., :3] + n[..., None], 0, 255)
    fr.paste(Image.fromarray(a.astype(np.uint8)))

def glow_line(fr, pts, col, w, a=1.0, blur=10):
    """polyline with a soft glow under it"""
    L = Image.new('RGBA', fr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    if len(pts) > 1:
        d.line(pts, fill=col + (int(170 * a),), width=w * 3, joint='curve')
        L = L.filter(ImageFilter.GaussianBlur(blur)); d = ImageDraw.Draw(L)
        d.line(pts, fill=col + (int(255 * a),), width=w, joint='curve')
    fr.alpha_composite(L)

def dot(fr, x, y, r, col, a=1.0, ring=0.0):
    x, y, r, a, ring = float(x), float(y), float(r), float(a), float(ring)
    R = r + ring * r * 6 if ring > 0 else 0; m = int(max(r * 4.5, R + 6)) + 4
    L = Image.new('RGBA', (2 * m, 2 * m), (0, 0, 0, 0)); d = ImageDraw.Draw(L); c = m
    d.ellipse((c - r * 2.2, c - r * 2.2, c + r * 2.2, c + r * 2.2), fill=col + (int(110 * a),))
    L = L.filter(ImageFilter.GaussianBlur(r)); d = ImageDraw.Draw(L)
    d.ellipse((c - r, c - r, c + r, c + r), fill=col + (int(255 * a),))
    if ring > 0: d.ellipse((c - R, c - R, c + R, c + R), outline=col + (int(255 * a * (1 - ring)),), width=3)
    fr.alpha_composite(L, (int(x) - m, int(y) - m)) if 0 <= int(x) - m and 0 <= int(y) - m and int(x) + m <= fr.width and int(y) + m <= fr.height else _paste_clip(fr, L, int(x) - m, int(y) - m)

def _paste_clip(fr, L, x, y):
    big = Image.new('RGBA', fr.size, (0, 0, 0, 0)); big.paste(L, (x, y)); fr.alpha_composite(big)

def T(key, text, size, path=ANTON, col=WHITE, shadow=0.6, blur=12):
    k = (key, text, size, path, col)
    if k not in _c: _c[k] = text_layer([(text, col)], size, path, shadow=shadow, blur=blur)
    return _c[k]

def spaced(text, n=1): return (' ' * n).join(text)

# ------------------------------------------------------------------ 1. TEN YEARS (cool, banking)
def years_card(fr, tl, p):
    OW, OH = fr.size; bg(fr, NAVY0, NAVY1, tl)
    d = ImageDraw.Draw(fr)
    # moving grid
    gap = OW // 9; off = (tl * 24) % gap
    for x in range(-gap, OW + gap, gap): d.line((x - off, 0, x - off, OH), fill=(70, 100, 140, 26), width=1)
    for y in range(0, OH, gap): d.line((0, y + off * 0.4, OW, y + off * 0.4), fill=(70, 100, 140, 22), width=1)
    # market line drawing left to right (abstract, no values)
    if 'walk' not in p:
        rng = random.Random(7); v = 0.0; w = []
        for i in range(120): v += rng.uniform(-1, 1.18); w.append(v)
        lo, hi = min(w), max(w); p['walk'] = [(x - lo) / (hi - lo) for x in w]
    u = eout(tl / 2.2); n = max(2, int(len(p['walk']) * u))
    y0, y1 = OH * 0.70, OH * 0.52
    pts = [(OW * 0.06 + OW * 0.88 * i / (len(p['walk']) - 1), y0 + (y1 - y0) * v) for i, v in enumerate(p['walk'][:n])]
    glow_line(fr, pts, STEEL, 4, a=0.85)
    dot(fr, pts[-1][0], pts[-1][1], 7, (220, 235, 255))
    # counter 1 -> 10
    k = int(clamp(1 + 9 * eout((tl - 0.15) / 1.3), 1, 10))
    sc = 1.0 + 0.02 * tl
    num = T('yn', str(k), int(OW * 0.36)); place(fr, num, OW / 2, OH * 0.30, a=eout(tl / 0.3), sc=sc)
    lab = T('yl', 'YEARS', int(OW * 0.11)); place(fr, lab, OW / 2, OH * 0.30 + num.height * 0.42, a=eout((tl - 0.2) / 0.4), sc=sc)
    sub = T('ys', spaced('INVESTMENT BANKING') + '   ·   ' + spaced('CHINA'), int(OW * 0.030), INTERB, STEEL, 0.5, 8)
    place(fr, sub, OW / 2, OH * 0.30 + num.height * 0.42 + lab.height * 0.62, a=eout((tl - 0.6) / 0.5))
    grain(fr, 6, int(tl * 30))

# ------------------------------------------------------------------ 2. JOURNEY China -> Kampala (cool -> warm)
def journey_card(fr, tl, p):
    OW, OH = fr.size; w = ease((tl - 0.3) / 1.6)
    bg(fr, lerp(NAVY0, WARM0, w), lerp(NAVY1, WARM1, w), tl)
    d = ImageDraw.Draw(fr)
    # curved globe grid (latitude arcs + longitude lines), drifting
    cx, cy, R = OW * 0.5, OH * 0.48, OW * 0.95
    for i in range(-6, 7):
        yy = cy + i * OH * 0.06
        d.arc((cx - R, yy - R * 0.18, cx + R, yy + R * 0.18), 200, 340, fill=lerp((80, 110, 150), (150, 110, 60), w) + (34,), width=1)
    for i in range(-7, 8):
        xx = cx + (i + (tl * 0.15) % 1) * OW * 0.085
        d.arc((xx - OW * 0.10, OH * 0.12, xx + OW * 0.10, OH * 0.84), 250, 290, fill=lerp((80, 110, 150), (150, 110, 60), w) + (26,), width=1)
    A = (OW * 0.78, OH * 0.24); B = (OW * 0.26, OH * 0.60)        # Shanghai (NE) -> Kampala (SW)
    ctrl = (OW * 0.70, OH * 0.62)
    u = ease((tl - 0.35) / 1.5); N = 80; pts = []
    for i in range(int(N * u) + 1):
        s = i / N; pts.append(((1 - s) ** 2 * A[0] + 2 * (1 - s) * s * ctrl[0] + s * s * B[0], (1 - s) ** 2 * A[1] + 2 * (1 - s) * s * ctrl[1] + s * s * B[1]))
    dot(fr, A[0], A[1], 9, (200, 220, 255), a=eout(tl / 0.3))
    if len(pts) > 1:
        glow_line(fr, pts, lerp((200, 220, 255), GOLD, u), 5)
        dot(fr, pts[-1][0], pts[-1][1], 8, lerp((220, 235, 255), (255, 225, 160), u))
    if u >= 0.999:
        rr = ((tl - 1.85) % 1.2) / 1.2
        dot(fr, B[0], B[1], 11, GOLD, ring=rr)
    la = T('jA', 'SHANGHAI', int(OW * 0.05), INTERB, (210, 225, 245), 0.6, 8); place(fr, la, A[0] - la.width * 0.1, A[1] - 62, a=eout((tl - 0.1) / 0.4))
    lb = T('jB', 'KAMPALA', int(OW * 0.075), ANTON, WHITE); place(fr, lb, B[0] + lb.width / 2 - 30, B[1] + 70, a=eout((tl - 1.7) / 0.4), sc=0.92 + 0.08 * eout((tl - 1.7) / 0.4))
    lc = T('jC', 'UGANDA  ·  EAST AFRICA', int(OW * 0.032), INTERB, GOLD, 0.6, 8); place(fr, lc, B[0] + lc.width / 2 - 30, B[1] + 70 + lb.height * 0.42, a=eout((tl - 1.95) / 0.4))
    grain(fr, 6, int(tl * 30) + 50)

# ------------------------------------------------------------------ 3. LOGO reveal (Blackstone, from John's gold logo)
def _logo_parts():
    if 'logo' in _c: return _c['logo']
    im = np.asarray(Image.open(iv.S + '/brand/logo_blackstone_vanta_640.png').convert('RGB')).astype(np.float32)
    lum = im.mean(2); bgl = np.median(lum[:20, :20])
    a = np.clip((bgl - lum) / 120.0, 0, 1)                        # dark/gold ink on off-white -> alpha
    def cut(y0, y1, col=None):
        sub = im[y0:y1]; al = a[y0:y1]; cols = np.where(al.max(0) > 0.05)[0]; x0, x1 = cols.min() - 4, cols.max() + 5
        rgb = sub[:, x0:x1] if col is None else np.broadcast_to(np.array(col, np.float32), sub[:, x0:x1].shape)
        if col is None:   # brighten the gold so it sits on dark
            rgb = np.clip(rgb * 1.35 + 18, 0, 255)
        out = np.dstack([rgb, al[:, x0:x1] * 255]).astype(np.uint8); return Image.fromarray(out, 'RGBA')
    _c['logo'] = (cut(160, 325), cut(338, 372), cut(376, 396))     # emblem, BLACKSTONE REAL ESTATE, tagline
    return _c['logo']

def logo_card(fr, tl, p):
    OW, OH = fr.size; bg(fr, (12, 11, 12), (34, 27, 18), tl)
    em, name, tag = _logo_parts()
    s = OW * 0.42 / em.width; E = em.resize((int(em.width * s), int(em.height * s)), Image.LANCZOS)
    u = ease((tl - 0.05) / 0.9)                                     # wipe the emblem up from its base
    h = int(E.height * u)
    if h > 0:
        part = E.crop((0, E.height - h, E.width, E.height)); y = int(OH * 0.40 + E.height / 2 - h)
        L = Image.new('RGBA', fr.size, (0, 0, 0, 0)); L.alpha_composite(part, (int(OW / 2 - E.width / 2), y))
        # light sweep across the emblem
        sw = (tl - 0.9) / 0.7
        if 0 < sw < 1:
            band = Image.new('L', fr.size, 0); db = ImageDraw.Draw(band); bx = OW * (0.2 + 0.6 * sw)
            db.polygon([(bx - 40, 0), (bx + 10, 0), (bx - 160, OH), (bx - 210, OH)], fill=150)
            band = band.filter(ImageFilter.GaussianBlur(18))
            hl = Image.new('RGBA', fr.size, (255, 240, 200, 0)); hl.putalpha(Image.fromarray(np.minimum(np.asarray(band), np.asarray(L.getchannel('A')))))
            L.alpha_composite(hl)
        sh = L.copy(); sh = sh.filter(ImageFilter.GaussianBlur(22)); fr.alpha_composite(sh); fr.alpha_composite(L)
    s2 = OW * 0.78 / name.width; N = name.resize((int(name.width * s2), int(name.height * s2)), Image.LANCZOS)
    place(fr, N, OW / 2, OH * 0.40 + E.height / 2 + 70, a=eout((tl - 0.75) / 0.45), sc=0.96 + 0.04 * eout((tl - 0.75) / 0.45))
    s3 = OW * 0.62 / tag.width; G = tag.resize((int(tag.width * s3), int(tag.height * s3)), Image.LANCZOS)
    place(fr, G, OW / 2, OH * 0.40 + E.height / 2 + 70 + N.height + 18, a=0.85 * eout((tl - 1.05) / 0.45))
    grain(fr, 5, int(tl * 30) + 90)

# ------------------------------------------------------------------ 4. LAND -> BUILD -> MARKET -> DELIVER tracker (overlay on site photos)
STEPS = ['LAND', 'BUILD', 'MARKET', 'DELIVER']
def steps_overlay(fr, t, p):
    """p: t0, t1 (on/off), hits=[time each step lights]"""
    OW, OH = fr.size; tl = t - p['t0']; a = min(eout(tl / 0.35), 1 - ease((t - (p['t1'] - 0.35)) / 0.35))
    if a <= 0: return
    y = int(OH * p.get('y', 0.11 if OH > 1500 else 0.13)); x0, x1 = OW * 0.15, OW * 0.85
    L = Image.new('RGBA', fr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((OW * 0.04, y - 110, OW * 0.96, y + 115), 28, fill=(10, 10, 12, int(150 * a)))
    xs = [x0 + (x1 - x0) * i / 3 for i in range(4)]
    d.line((x0, y - 18, x1, y - 18), fill=(255, 255, 255, int(70 * a)), width=4)
    lit = [h for h in p['hits'] if t >= h]; n = len(lit)
    if n:
        last = lit[-1]; grow = eout((t - last) / 0.45)
        xe = xs[n - 1] if n == 1 else xs[n - 2] + (xs[n - 1] - xs[n - 2]) * grow
        if n == 1: xe = xs[0]
        d.line((x0, y - 18, xe, y - 18), fill=GOLD + (int(255 * a),), width=6)
    fr.alpha_composite(L)
    for i, (x, s) in enumerate(zip(xs, STEPS)):
        on = t >= p['hits'][i]; u = eout((t - p['hits'][i]) / 0.3) if on else 0
        dot(fr, x, y - 18, 9 + 4 * u, GOLD if on else (120, 120, 120), a=a, ring=clamp((t - p['hits'][i]) / 0.8) if on and t - p['hits'][i] < 0.8 else 0)
        lab = T('st' + s + str(on), s, int(OW * 0.05), ANTON, GOLD if on else (200, 200, 200), 0.6, 8)
        place(fr, lab, x, y + 52, a=a * (0.55 + 0.45 * u), sc=1 + 0.08 * u * (1 - clamp((t - p['hits'][i]) / 0.5)) if on else 1)

# ------------------------------------------------------------------ 5. THE GAP bars (overlay above John's head in the hook)
def gap_overlay(fr, t, p):
    OW, OH = fr.size; tl = t - p['t0']; a = min(eout(tl / 0.35), 1 - ease((t - (p['t1'] - 0.35)) / 0.35))
    if a <= 0: return
    top = int(OH * 0.035); bx0 = OW * 0.08; bw = OW * 0.84; bh = int(OH * 0.022)
    L = Image.new('RGBA', fr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((OW * 0.04, top, OW * 0.96, top + int(OH * 0.125)), 24, fill=(10, 10, 12, int(140 * a)))
    ud = eout((t - p['hit_demand']) / 0.9); us = eout((t - p['hit_supply']) / 0.9)
    y1 = top + int(OH * 0.042); y2 = top + int(OH * 0.092)
    d.rounded_rectangle((bx0, y1, bx0 + bw * ud, y1 + bh), bh // 2, fill=(255, 255, 255, int(235 * a)))
    d.rounded_rectangle((bx0, y2, bx0 + bw * 0.38 * us, y2 + bh), bh // 2, fill=GOLD + (int(255 * a),))
    fr.alpha_composite(L)
    l1 = T('gd', 'HOUSING DEMAND', int(OW * 0.028), INTERB, WHITE, 0.6, 6); place(fr, l1, bx0 + l1.width / 2 - 40, y1 - 22, a=a * eout((t - p['hit_demand']) / 0.3))
    l2 = T('gs', 'QUALITY SUPPLY', int(OW * 0.028), INTERB, GOLD, 0.6, 6); place(fr, l2, bx0 + l2.width / 2 - 40, y2 - 22, a=a * eout((t - p['hit_supply']) / 0.3))
    ug = eout((t - p['hit_gap']) / 0.4)
    if ug > 0:   # dashed bracket over the missing part + THE GAP
        gx0 = bx0 + bw * 0.38 + 14; gx1 = bx0 + bw; yy = y2 + bh // 2
        L = Image.new('RGBA', fr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L); x = gx0
        while x < gx0 + (gx1 - gx0) * ug:
            d.line((x, yy, min(x + 16, gx1), yy), fill=(255, 255, 255, int(200 * a)), width=4); x += 28
        fr.alpha_composite(L)
        g = T('gg', 'THE GAP', int(OW * 0.042), ANTON, WHITE); place(fr, g, (gx0 + gx1) / 2, y2 + bh + 30, a=a * ug, sc=0.9 + 0.1 * ug)

# ------------------------------------------------------------------ 6. location tag (Vanta House, Naguru) on the real site photo
def location_overlay(fr, t, p):
    OW, OH = fr.size; tl = t - p['t0']; a = min(eout(tl / 0.35), 1 - ease((t - (p['t1'] - 0.35)) / 0.35))
    if a <= 0: return
    x, y = OW * 0.09, OH * p.get('y', 0.085)
    import mgk; mgk.scrim(fr, int(y - 40), int(y + 95), 0.55 * a, fade=70)          # QA 8 Nov: readable on bright concrete
    dot(fr, x, y + 4, 10, GOLD, a=a, ring=(tl % 1.4) / 1.4)
    l1 = T('lo1', 'VANTA HOUSE', int(OW * 0.06), ANTON, WHITE); place(fr, l1, x + 34 + l1.width / 2 - 40 + (1 - eout(tl / 0.4)) * -30, y - 6, a=a)
    l2 = T('lo2' + p.get('l2', ''), p.get('l2', 'Naguru, Kampala  ·  Site photo 2026'), int(OW * 0.028), INTERB, GOLD, 0.7, 8); place(fr, l2, x + 34 + l2.width / 2 - 40, y + l1.height * 0.55, a=a * eout((tl - 0.2) / 0.4))

def label(fr, t, p, text):
    """small corner label: Artist's impression / Site photo"""
    OW, OH = fr.size; a = min(1.0, (t - p['t0']) / 0.3, (p['t1'] - t) / 0.3)
    if a <= 0: return
    L = T('lab' + text, text, 30, INTERB, WHITE, 0.85, 8); place(fr, L, OW - 50 - L.width / 2 + 40, int(OH * 0.06), a=a)

# ------------------------------------------------------------------ 7. PAPERS (integrity): safe header crops only, stamp last
PAP = iv.S + '/papers/'
def _paper(name, w):
    k = ('pap', name, w)
    if k not in _c:
        im = Image.open(PAP + name).convert('RGB'); s = w / im.width
        im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        card = Image.new('RGBA', (im.width + 60, im.height + 60), (0, 0, 0, 0))
        sh = Image.new('RGBA', card.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((30, 36, 30 + im.width, 36 + im.height), fill=(0, 0, 0, 170))
        card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14))); card.paste(im, (30, 30)); _c[k] = card
    return _c[k]

def _stamp(w, name='crop_stamp_clean.png'):
    """the APPROVED stamp with the white paper keyed out (no grey square over the cards); 8 Nov QA: the permit date/time line is cropped off"""
    k = ('stamp', w, name)
    if k not in _c:
        im = np.asarray(Image.open(PAP + name).convert('RGB')).astype(np.float32); s = w / im.shape[1]
        a = np.clip((235 - im.min(2)) / 90, 0, 1)
        L = Image.fromarray(np.dstack([im, a * 255]).astype(np.uint8), 'RGBA').resize((w, int(im.shape[0] * s)), Image.LANCZOS)
        _c[k] = L                                      # ink only, like a real stamp on the paper
    return _c[k]

def papers_card(fr, tl, p):
    OW, OH = fr.size; bg(fr, (16, 13, 10), (40, 30, 18), tl)
    tall = OH > 1500; w = int(OW * (0.82 if tall else 0.66))
    names = ['crop_building_permit.png', 'crop_nema.png', 'crop_kcca_dev.png']
    ys = [0.27, 0.43, 0.58] if tall else [0.26, 0.45, 0.63]
    if not p.get('title', True): ys = [y + 0.03 for y in ys]
    for i, (n, yy) in enumerate(zip(names, ys)):
        u = eout((tl - 0.15 - 0.28 * i) / 0.5)
        if u <= 0: continue
        C = _paper(n, w); rot = (1 - u) * (6 if i % 2 else -6) + (-1.2, 1.0, -0.6)[i]
        R = C.rotate(rot, resample=Image.BICUBIC, expand=True)
        place(fr, R, OW / 2 + (1 - u) * OW * 0.6 * (1 if i % 2 == 0 else -1), OH * yy, a=u, sc=1 + 0.01 * tl)
    us = (tl - 1.25) / 0.22
    if us > 0:   # stamp drops in from big to size
        st = _stamp(int(OW * 0.36)); sc = 1.0 + 0.6 * (1 - eout(us))
        place(fr, st, OW * 0.72, OH * (ys[-1] + p.get('stamp_dy', 0.0) - (0.008 if tall else 0.0)), a=eout(us), sc=sc)   # clear of the caption line
    if p.get('title', True):
        t1 = T('pt', 'INTEGRITY', int(OW * 0.11), ANTON, GOLD); place(fr, t1, OW / 2, OH * (0.12 if tall else 0.09), a=eout(tl / 0.35), sc=0.94 + 0.06 * eout(tl / 0.35))
    grain(fr, 5, int(tl * 30) + 33)

# ------------------------------------------------------------------ 8. BLUEPRINT -> RENDER (the real approved elevation drawing draws in, then the render)
def blueprint_card(fr, tl, p):
    OW, OH = fr.size; dur = p['dur']
    if 'bp' not in p:
        el = np.asarray(Image.open(PAP + 'crop_elevation.png').convert('L')).astype(np.float32)
        s = OW * 0.92 / el.shape[1]; el = np.asarray(Image.fromarray(el.astype(np.uint8)).resize((int(el.shape[1] * s), int(el.shape[0] * s)), Image.LANCZOS)).astype(np.float32)
        ink = np.clip((242 - el) / 90, 0, 1) ** 0.6                  # lines -> alpha (bold)
        ink = np.asarray(Image.fromarray((ink * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))).astype(np.float32) / 255
        rgb = np.zeros(el.shape + (3,), np.float32); rgb[:] = (200, 225, 255)
        p['bp'] = np.dstack([rgb, ink * 255]).astype(np.uint8)
        r = Image.open(iv.S + '/people/render_vanta_house.jpg').convert('RGB'); f = max(OW / r.width, OH / r.height) * 1.08
        p['rd'] = r.resize((int(r.width * f), int(r.height * f)), Image.LANCZOS)
    bg(fr, NAVY0, (20, 40, 70), tl)
    d = ImageDraw.Draw(fr); gap = OW // 12
    for x in range(0, OW, gap): d.line((x, 0, x, OH), fill=(90, 130, 190, 30))
    for y in range(0, OH, gap): d.line((0, y, OW, y), fill=(90, 130, 190, 30))
    bp = p['bp']; h, w = bp.shape[:2]; u = ease(tl / 1.5)            # floors rise from the ground up
    reveal = int(h * u); y0 = int(OH * 0.45 - h / 2); x0 = int(OW / 2 - w / 2)
    if reveal > 0:
        part = Image.fromarray(bp[h - reveal:], 'RGBA'); gl = Image.new('RGBA', fr.size, (0, 0, 0, 0)); gl.alpha_composite(part, (x0, y0 + h - reveal))
        fr.alpha_composite(gl.filter(ImageFilter.GaussianBlur(6))); fr.alpha_composite(gl)
        if u < 1:
            yl = y0 + h - reveal; L = Image.new('RGBA', (OW, 40), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
            dl.line((0, 20, OW, 20), fill=(255, 220, 150, 230), width=4); L = L.filter(ImageFilter.GaussianBlur(5))
            fr.alpha_composite(L, (0, max(0, yl - 20)))
    lab = T('bpl', 'Architectural drawing', 30, INTERB, (200, 220, 245), 0.8, 8)
    xr = clamp((tl - (dur * 0.55)) / 0.6)
    place(fr, lab, OW - 50 - lab.width / 2 + 40, int(OH * 0.06), a=min(eout(tl / 0.4), 1 - xr))
    if xr > 0:                                                        # cross-dissolve into the render (artist's impression)
        r = p['rd']; z = 1 + 0.05 * xr; cw, ch = int(OW / z), int(OH / z)
        crop = r.crop((int((r.width - cw) * 0.28), int((r.height - ch) * 0.45), int((r.width - cw) * 0.28) + cw, int((r.height - ch) * 0.45) + ch)).resize((OW, OH), Image.BILINEAR).convert('RGBA')
        crop.putalpha(int(255 * ease(xr))); fr.alpha_composite(crop)
        l2 = T('lab' + "Artist's impression", "Artist's impression", 30, INTERB, WHITE, 0.85, 8)
        place(fr, l2, OW - 50 - l2.width / 2 + 40, int(OH * 0.06), a=ease(xr))
    grain(fr, 5, int(tl * 30) + 71)

# ------------------------------------------------------------------ 9. FOUNDER: logo reveal, then a real photo of John (owner's choice 8 Nov: real photos only), name under it (never on the face)
def founder_card(fr, tl, p):
    OW, OH = fr.size; split = p.get('split', 0.0)          # 8 Nov: owner wants it simple - his picture and his name
    if split > 0 and tl < split + 0.4: logo_card(fr, tl, p)
    elif split == 0: bg(fr, (10, 10, 11), (18, 18, 20), tl, vign=False)
    if tl >= split:
        if 'hs' not in p:
            im = Image.open(iv.S + '/people/' + p.get('photo', 'john_headshot_black_shirt.jpg')).convert('RGB'); s = min(OW * 0.86 / im.width, OH * (0.47 if OH > 1500 else 0.50) / im.height)
            p['hs'] = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
            m = np.ones((p['hs'].height, p['hs'].width), np.float32)    # fade the bottom edge into the dark card
            fh = int(p['hs'].height * 0.18); m[-fh:] = np.linspace(1, 0, fh)[:, None]
            p['hm'] = Image.fromarray((m * 255).astype(np.uint8))
        u = ease((tl - split) / 0.45) if split > 0 else 1.0; z = 1.0 + 0.03 * (tl - split)
        base = Image.new('RGBA', fr.size, (10, 10, 11, int(255 * u))); fr.alpha_composite(base)
        hs = p['hs'].resize((int(p['hs'].width * z), int(p['hs'].height * z)), Image.BILINEAR).convert('RGBA')
        hm = p['hm'].resize(hs.size); hm = Image.fromarray((np.asarray(hm).astype(np.float32) * u).astype(np.uint8)); hs.putalpha(hm)
        top = int(OH * (0.07 if OH > 1500 else 0.02)); fr.alpha_composite(hs, (int(OW / 2 - hs.width / 2), top))
        ny = top + int(p['hs'].height * z) + int(OH * 0.035)
        if 'nA' not in p:
            p['nA'] = text_layer([('JOHN YAN', WHITE)], int(OW * 0.085), ANTON, shadow=0.6, blur=10)
            p['nB'] = text_layer([('Founder & CEO, Blackstone Real Estate', GOLD)], int(OW * 0.036), INTERB, shadow=0.6, blur=8)
        v = eout((tl - split - 0.3) / 0.45)
        place(fr, p['nA'], OW / 2, ny + (1 - v) * 20, a=v)
        place(fr, p['nB'], OW / 2, ny + p['nA'].height * 0.5 + (1 - v) * 20, a=v)
