# Motion graphics built on Marketing's MOTION + SOUND KIT and MOTION GRAPHICS REFERENCES (8 Nov):
# T1 word-pop captions, T3 bar titles, T4 counter, T5 map route (real land-mask dot map), T8 light leak,
# MOTION_01 word pops (out-back overshoot), MOTION_02 name strip, MOTION_08 tracked luxury titles.
# Safe area 9:16: text inside x 60..960, y 285..1440 (kit). Theme T = dict(acc, font, cap, ...).
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import iv

INTER_XB = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
INTER_B = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
INTER_MD = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'
OFFW = (236, 236, 236); DARK = (14, 14, 16)
_c = {}

def cl(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def smooth(x): x = cl(x); return x * x * (3 - 2 * x)
def ocubic(x): x = cl(x); return 1 - (1 - x) ** 3
def icubic(x): x = cl(x); return x ** 3
def oexpo(x): x = cl(x); return 1 - 2 ** (-10 * x) if x < 1 else 1.0
def oback(x, c=1.70158): x = cl(x); return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def font(p, s): return iv.font(p, s)

def text(txt, size, path, col=(255, 255, 255), shadow=0.55, blur=6, off=4, track=0):
    """crisp text layer; soft drop shadow (kit: black 55 %, 4 px down, blur 6); optional letter tracking"""
    k = (txt, size, path, col, shadow, blur, off, track)
    if k in _c: return _c[k]
    F = font(path, size); pad = 30
    if track:
        ws = [F.getlength(ch) for ch in txt]; w = int(sum(ws) + track * (len(txt) - 1)) + 2 * pad
    else: w = int(F.getlength(txt)) + 2 * pad
    asc, desc = F.getmetrics(); h = asc + desc + 2 * pad
    L = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(L)
    if track:
        x = pad
        for ch, cw in zip(txt, ws): d.text((x, pad), ch, font=F, fill=col + (255,)); x += cw + track
    else: d.text((pad, pad), txt, font=F, fill=col + (255,))
    if shadow > 0:
        a = np.asarray(L.getchannel('A')); S = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        sa = Image.fromarray((a * shadow).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
        S.putalpha(sa); out = Image.new('RGBA', (w, h)); out.alpha_composite(S, (0, off)); out.alpha_composite(L); L = out
    _c[k] = L; return L

def put(fr, L, cx, cy, a=1.0, sc=1.0, left=False):
    if a <= 0.003: return
    if abs(sc - 1) > 1e-3: L = L.resize((max(1, int(L.width * sc)), max(1, int(L.height * sc))), Image.BICUBIC)
    if a < 0.999: L = L.copy(); L.putalpha(L.getchannel('A').point(lambda v: int(v * a)))
    x = int(cx - (30 if left else L.width / 2)); fr.alpha_composite(L, (x, int(cy - L.height / 2)))

def bar(fr, cx, cy, w, h, col, a=1.0):
    if w < 1 or a <= 0: return
    ImageDraw.Draw(fr).rectangle((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2)), fill=col + (int(255 * a),))

# ---------------------------------------------------------------- T1 word-pop captions (active word in the accent, pop 1.00 -> 1.16 -> 1.00)
def caption(fr, t, ch, T, y):
    """ch = dict(t0, t1, words=[(w, ts)]) ; one line, Inter Bold 52, centred at y"""
    if not (ch['t0'] <= t <= ch['t1']): return
    a = min(ocubic((t - ch['t0']) / 0.27), 1 - smooth((t - (ch['t1'] - 0.22)) / 0.22)); dy = (1 - ocubic((t - ch['t0']) / 0.27)) * 14
    F = font(INTER_B, 52); sp = 24
    ws = [F.getlength(w) for w, _ in ch['words']]; tot = sum(ws) + sp * (len(ws) - 1); x = 540 - tot / 2
    if a > 0:                                     # soft dark pill behind the line (MOTION_01), keeps the accent word readable on bright walls
        L = Image.new('RGBA', fr.size, (0, 0, 0, 0)); ImageDraw.Draw(L).rounded_rectangle((x - 26, y + dy - 44, x + tot + 26, y + dy + 42), 22, fill=(12, 12, 14, int(150 * a)))
        fr.alpha_composite(L)
    active = max([i for i, (w, ts) in enumerate(ch['words']) if ts <= t] or [-1])
    for i, ((w, ts), wl) in enumerate(zip(ch['words'], ws)):
        on = i == active; k = (t - ts) / (8 / 30)
        sc = 1 + 0.10 * math.sin(math.pi * cl(k)) if on and 0 <= k <= 1 else 1.0
        u = cl((t - ts) / 0.1) if on else 0
        col = tuple(int(255 + (c - 255) * u) for c in T['acc']) if on else (255, 255, 255)
        put(fr, text(w, 52, INTER_B, col, 0.55, 6, 4), x + wl / 2, y + dy, a=a, sc=sc); x += wl + sp

def chunk_words(words, maxw=4, gap=0.32):
    """words [(w, t_start, t_end)] -> caption chunks, break at sentence ends / pauses / 4 words"""
    out = []; cur = []
    for k, (w, ts, te) in enumerate(words):
        cur.append((w, ts, te))
        nxt = words[k + 1][1] if k + 1 < len(words) else None
        if len(cur) >= maxw or w[-1] in '.?!,' or nxt is None or nxt - te > gap:
            out.append(dict(t0=cur[0][1] - 0.06, t1=(min(nxt - 0.02, cur[-1][2] + 0.35) if nxt else cur[-1][2] + 0.4), words=[(x, s) for x, s, _ in cur])); cur = []
    return out

# ---------------------------------------------------------------- T3 title (bar wipes from centre, lines rise in) - used for the hook
def title2(fr, t, H, T, y=330):
    tl = t - H['t0']; uo = 1 - smooth((t - (H['t1'] - 0.3)) / 0.3)
    bw = 96 * oexpo((tl - 0.2) / 0.4); bar(fr, 540, y - 62, bw, 6, T['acc'], uo)
    for i, (txt, col) in enumerate(H['lines']):
        u = ocubic((tl - 0.27 - 0.27 * i) / 0.47)
        L = text(txt, H.get('size', 84), T['font'], col, 0.6, 10, 5)
        if L.width > 960: L = L.resize((960, int(L.height * 960 / L.width)), Image.LANCZOS)
        put(fr, L, 540, y + 10 + i * H.get('gap', 98) + (1 - u) * 26, a=min(u, uo))

# ---------------------------------------------------------------- MOTION_01 word pop (out-back overshoot ~110 %, 4-5 frame exit)
def word_pop(fr, t, W, T):
    tl = t - W['t0']; a_in = cl(tl / (6 / 30)); s = 0.6 + 0.4 * oback(tl / (8 / 30), 2.2); out = cl((t - (W['t1'] - 5 / 30)) / (5 / 30))
    a = min(a_in, 1 - out); s *= (1 - 0.15 * out)
    if a <= 0: return
    if W.get('small'):          # mixed weights: small light connector over a huge bold word ("real" / "WORKERS")
        put(fr, text(W['small'], 46, INTER_MD, OFFW, 0.6, 6, 3), 540, W['y'] - W.get('size', 150) * 0.62, a=a)
    L = text(W['text'], W.get('size', 150), T['font'], W.get('col', (255, 255, 255)), 0.6, 12, 6)
    if L.width > 980: L = L.resize((980, int(L.height * 980 / L.width)), Image.LANCZOS)
    put(fr, L, 540, W['y'], a=a, sc=s)

# ---------------------------------------------------------------- MOTION_02 name strip (accent line draws down, text slides from the left)
def name_strip(fr, t, L, T):
    tl = t - L['t0']; out = smooth((t - (L['t1'] - 8 / 30)) / (8 / 30)); a_line = 1 - out
    x = 64; y0 = L.get('y0', 1236); h = 120 * ocubic(tl / (10 / 30))
    if h > 1: ImageDraw.Draw(fr).rectangle((x, y0, x + 4, y0 + h), fill=T['acc'] + (int(255 * a_line),))
    u1 = smooth((tl - 4 / 30) / (8 / 30)); u2 = smooth((tl - 8 / 30) / (8 / 30))
    put(fr, text(L['l1'], 58, T['font'], (255, 255, 255), 0.75, 8, 4), x + 22 - 14 * (1 - u1) - 20 * out, y0 + 34, a=min(u1, 1 - out), left=True)
    put(fr, text(L['l2'], 32, INTER_MD, OFFW, 0.8, 7, 3), x + 22 - 14 * (1 - u2) - 20 * out, y0 + 92, a=min(u2, 1 - out), left=True)

# ---------------------------------------------------------------- T4 counter "10 YEARS" (fixed digit slots, ease 1-(1-x)^2.2, 7 % land pop, 3 % push)
def counter(fr, t, C, T):
    tl = t - C['t0']; uo = 1 - smooth((t - (C['t1'] - 0.3)) / 0.3); ui = ocubic((tl - 4 / 30) / (12 / 30))
    a = min(ui, uo); dy = (1 - ui) * 26
    x = cl((tl - 20 / 30) / (50 / 30)); n = int(round(10 * (1 - (1 - x) ** 2.2)))
    land = (tl - 70 / 30) / (10 / 30); pop = 1 + 0.07 * math.sin(math.pi * cl(land)) if 0 <= land <= 1 else 1.0
    push = 1 + 0.03 * cl((tl - 80 / 30) / 2.0); sc = pop * push
    big = 380 if T['font'] == INTER_XB else 430
    s = '%2d' % n; F = font(T['font'], big); slot = F.getlength('0') * 1.02
    for i, ch in enumerate(s):
        if ch == ' ': continue
        put(fr, text(ch, big, T['font'], (255, 255, 255), 0.5, 14, 8), 540 + (i - 0.5) * slot * sc, 860 + dy, a=a, sc=sc)
    bar(fr, 540, 860 - big * 0.62 * sc + dy, 96 * ocubic(tl / 0.5), 6, T['acc'], a)
    put(fr, text('YEARS', 96, T['font'], (255, 255, 255), 0.5, 10, 6), 540, 1190 + dy, a=a, sc=push)
    if C.get('sub'): put(fr, text(C['sub'], 34, INTER_MD, OFFW, 0.6, 6, 3, track=6), 540, 1290 + dy, a=a * ocubic((tl - 0.9) / 0.4))

def counter_sfx(t0):
    clicks = sorted({round(t0 + (20 + 50 * (1 - (1 - (k / 10)) ** (1 / 2.2) if False else 0)) / 30, 3) for k in range(1)})
    out = [('sfx_riser_1', t0, -20)]
    last = 0
    for f in range(20, 71):
        x = (f - 20) / 50; n = int(round(10 * (1 - (1 - x) ** 2.2)))
        if n != last: out.append(('sfx_click_1', t0 + f / 30, -24)); last = n
    out += [('sfx_impact_soft_1', t0 + 71 / 30, -15), ('sfx_impact_sub_2', t0 + 71 / 30, -23)]
    return out

# ---------------------------------------------------------------- T5 map route China -> Kampala on a real land-mask dot map
LON0, LON1, LAT0, LAT1 = 14.0, 136.0, -22.0, 52.0
def _map_base(W=1080, H=1920):
    if 'map' in _c: return _c['map']
    from global_land_mask import globe
    ppd = (W - 120) / (LON1 - LON0); y0 = 900 - (LAT1 - LAT0) * ppd / 2
    def xy(lon, lat): return 60 + (lon - LON0) * ppd, y0 + (LAT1 - lat) * ppd
    step = 13
    xs = np.arange(60, W - 60, step); ys = np.arange(y0, y0 + (LAT1 - LAT0) * ppd, step)
    X, Y = np.meshgrid(xs, ys); lon = LON0 + (X - 60) / ppd; lat = LAT1 - (Y - y0) / ppd
    land = globe.is_land(lat, lon)
    uga = land & (lat > -1.45) & (lat < 4.2) & (lon > 29.6) & (lon < 35.0) & ~((lat < 0.2) & (lon > 31.7) & (lon < 34.0))   # minus most of Lake Victoria
    base = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(base)
    for x, y in zip(X[land], Y[land]): d.ellipse((x - 2.6, y - 2.6, x + 2.6, y + 2.6), fill=(150, 150, 155, 105))
    ug = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(ug)
    for x, y in zip(X[uga], Y[uga]): d2.ellipse((x - 3.4, y - 3.4, x + 3.4, y + 3.4), fill=(255, 255, 255, 255))
    _c['map'] = (base, ug, xy); return _c['map']

def map_card(fr, tl, p):
    """full-frame card (iv 'card' draw): dark C look, dot map, route draws over ~2.5 s with a slow push-in"""
    T = p['T']; W, H = fr.size; base, ug, xy = _map_base(W, H)
    bg = Image.new('RGBA', fr.size, DARK + (255,)); fr.paste(bg)
    k = ('vig', W, H)
    if k not in _c:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - 900) / H) ** 2)
        _c[k] = Image.fromarray(np.dstack([np.full((H, W), 40, np.uint8)] * 3 + [(np.clip(1 - r * 1.6, 0, 1) * 255).astype(np.uint8)]), 'RGBA')
    fr.alpha_composite(_c[k])
    z = 1 + 0.09 * smooth(tl / max(p['dur'], 0.1))                       # camera push 9 % (ref: 8-10 % while the line draws)
    A = xy(121.5, 31.2); B = xy(32.58, 0.35); cxp, cyp = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2
    def zz(pt): return (cxp + (pt[0] - cxp) * z, cyp + (pt[1] - cyp) * z)
    lay = Image.new('RGBA', fr.size, (0, 0, 0, 0)); lay.alpha_composite(base)
    arr = cl((tl - 0.6 - 2.45) / 0.5)
    if arr > 0:
        g = ug.copy(); g.putalpha(g.getchannel('A').point(lambda v: int(v * 0.32 * arr)))
        tint = Image.new('RGBA', fr.size, T['acc'] + (0,)); tint.putalpha(g.getchannel('A')); lay.alpha_composite(tint)
    if abs(z - 1) > 1e-3:
        lay = lay.resize((int(W * z), int(H * z)), Image.BILINEAR); ox = int(cxp * z - cxp); oy = int(cyp * z - cyp); lay = lay.crop((ox, oy, ox + W, oy + H))
    fr.alpha_composite(lay)
    a0, b0 = zz(A), zz(B); ctrl = ((a0[0] + b0[0]) / 2 - 40, (a0[1] + b0[1]) / 2 - 230 * z)
    # China: label + small red dot (only red in the kit)
    ua = ocubic((tl - 0.2) / 0.5)
    ImageDraw.Draw(fr).ellipse((a0[0] - 7, a0[1] - 7, a0[0] + 7, a0[1] + 7), fill=(205, 45, 45, int(255 * ua)))
    put(fr, text('CHINA', 38, INTER_B, (255, 255, 255), 0.7, 6, 3), a0[0], a0[1] - 44, a=ua, sc=0.8 + 0.2 * oback((tl - 0.2) / 0.27))
    u = smooth((tl - 0.6) / 2.45); N = 90; pts = []
    for i in range(int(N * u) + 1):
        s = i / N; pts.append(((1 - s) ** 2 * a0[0] + 2 * (1 - s) * s * ctrl[0] + s * s * b0[0], (1 - s) ** 2 * a0[1] + 2 * (1 - s) * s * ctrl[1] + s * s * b0[1]))
    if len(pts) > 1:
        Lg = Image.new('RGBA', fr.size, (0, 0, 0, 0)); ImageDraw.Draw(Lg).line(pts, fill=T['acc'] + (150,), width=14, joint='curve')
        fr.alpha_composite(Lg.filter(ImageFilter.GaussianBlur(7)))
        ImageDraw.Draw(fr).line(pts, fill=T['acc'] + (255,), width=5, joint='curve')
        hx, hy = pts[-1]; ImageDraw.Draw(fr).ellipse((hx - 7, hy - 7, hx + 7, hy + 7), fill=(255, 250, 235, 255))
    if arr > 0:
        ring = cl((tl - 3.05) / (14 / 30)); R = 9 + 60 * ring
        d = ImageDraw.Draw(fr); d.ellipse((b0[0] - R, b0[1] - R, b0[0] + R, b0[1] + R), outline=T['acc'] + (int(255 * (1 - ring)),), width=3)
        d.ellipse((b0[0] - 9, b0[1] - 9, b0[0] + 9, b0[1] + 9), fill=(255, 255, 255, 255))
        sc = 0.8 + 0.2 * oback((tl - 3.05) / (8 / 30))
        put(fr, text('KAMPALA', 44, INTER_XB if T['font'] == INTER_XB else T['font'], (255, 255, 255), 0.7, 8, 4), b0[0] + 10, b0[1] + 62, a=arr, sc=sc)
        put(fr, text('UGANDA', 30, INTER_MD, T['acc'], 0.7, 6, 3, track=5), b0[0] + 10, b0[1] + 112, a=arr * ocubic((tl - 3.2) / 0.3))

def map_sfx(t0):
    return [('sfx_text_pop_2', t0 + 0.25, -17), ('sfx_line_draw_tone_1', t0 + 0.55, -15), ('sfx_impact_soft_1', t0 + 3.05, -14), ('sfx_text_pop_1', t0 + 3.05, -17)]

# ---------------------------------------------------------------- T8 light leak (3 warm blobs sweep L->R, screen blend, peak on the cut)
def light_leak(fr, t, t_cut, strength=0.75):
    f = (t - t_cut) * 30 + 37
    if f < 17 or f > 60: return
    env = math.exp(-((f - 37) / 8.5) ** 2) * strength; xs = -0.2 + 1.4 * smooth((f - 19) / 36)
    W, H = fr.size; k = ('lk', W, H)
    if k not in _c:
        yy, xx = np.mgrid[0:H:4, 0:W:4].astype(np.float32); _c[k] = (xx, yy)
    xx, yy = _c[k]; g = np.zeros(xx.shape + (3,), np.float32)
    for dx, dy, r, col in ((0.0, 0.25, 0.42, (255, 170, 80)), (-0.18, 0.55, 0.35, (255, 120, 60)), (0.12, 0.8, 0.3, (255, 205, 130))):
        m = np.exp(-(((xx / W) - (xs + dx)) ** 2 + ((yy / H) - dy) ** 2 * 0.35) / (r * r) * 2.2)
        g += m[..., None] * np.array(col, np.float32)
    g = np.clip(g * env, 0, 255); g = np.asarray(Image.fromarray(g.astype(np.uint8)).resize((W, H), Image.BILINEAR)).astype(np.float32)
    a = np.asarray(fr).astype(np.float32); a[..., :3] = 255 - (255 - a[..., :3]) * (255 - g) / 255
    fr.paste(Image.fromarray(a.astype(np.uint8)))

# ---------------------------------------------------------------- MOTION_08 tracked luxury title (letters fade in L->R over 20 f, key line solid accent)
def lux_title(fr, t, L, T):
    tl = t - L['t0']; out = smooth((t - (L['t1'] - 0.3)) / 0.3)
    s = L['small']; F = font(INTER_MD, 40); tr = 14; ws = [F.getlength(c) for c in s]; tot = sum(ws) + tr * (len(s) - 1); x = 540 - tot / 2
    for i, (c, w) in enumerate(zip(s, ws)):
        u = smooth((tl - i * (20 / 30) / len(s)) / 0.25)
        put(fr, text(c, 40, INTER_MD, OFFW, 0.7, 6, 3), x + w / 2, L['y'], a=u * (1 - out)); x += w + tr
    u2 = ocubic((tl - 0.6) / 0.4)
    put(fr, text(L['big'], 108, T['font'], T['acc'], 0.6, 12, 6), 540, L['y'] + 92 + (1 - u2) * 20, a=u2 * (1 - out))

# ---------------------------------------------------------------- T3 end card (dark C look, bar wipes from centre, VANTA HOUSE / NAGURU, KAMPALA)
def end_card(T):
    def draw(fr, tl, p):
        W, H = fr.size; fr.paste(Image.new('RGBA', fr.size, DARK + (255,)))
        k = ('vig', W, H)
        if k in _c: fr.alpha_composite(_c[k])
        push = 1 + 0.03 * cl(tl / 4.5)
        tealish = T['font'] == INTER_XB
        bw = 96 * oexpo((tl - 0.2) / 0.4); y = 880
        L1 = text('VANTA HOUSE', 104 if tealish else 150, T['font'], (255, 255, 255), 0.5, 10, 5)
        bar(fr, 540, y - L1.height / 2 + 18, bw * push, 6, T['acc'])
        u1 = ocubic((tl - 0.27) / 0.47); u2 = ocubic((tl - 0.53) / 0.6); u3 = ocubic((tl - 0.9) / 0.5)
        put(fr, L1, 540 + (1 - u1) * -70, y + 30, a=u1, sc=push)
        put(fr, text('NAGURU, KAMPALA', 46, INTER_MD, OFFW if tealish else T['acc'], 0.5, 6, 3, track=4), 540, y + 30 + L1.height * 0.5 + 34, a=u2, sc=push)
        put(fr, text('HANDOVER EXPECTED OCTOBER 2027', 28, INTER_MD, (170, 170, 170), 0.0, 1, 0, track=5), 540, y + 30 + L1.height * 0.5 + 118, a=u3 * 0.9)
        put(fr, text(iv.CREDIT, 20, INTER_MD, (130, 130, 130), 0.0, 1, 0), 540, 1400, a=u3 * 0.85)
    return draw

def end_sfx(t0): return [('sfx_whoosh_soft_2', t0 + 0.13, -17), ('sfx_impact_soft_1', t0 + 0.47, -17)]
