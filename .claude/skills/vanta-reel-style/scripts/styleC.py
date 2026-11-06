# Vanta House style v2 (proposal): Vanta Black + Stone + Champagne, Cormorant Garamond + Jost.
# Uses the Motion Explainer Kit text engine (render.T, place, comp) with the new fonts registered.
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'
sys.path.insert(0, S + '/A/build')
import render as R
from render import T, place, comp, clamp, eo, eio, W, H

CG = S + '/fonts2/cormorant-garamond/package/files/cormorant-garamond-latin-'
JO = S + '/fonts2/jost/package/files/jost-latin-'
R.FN.update({
    'serif':    CG + '600-normal.woff',   # display: VANTA HOUSE
    'serif_b':  CG + '700-normal.woff',
    'serif_i':  CG + '500-italic.woff',   # accent phrases
    'serif_i6': CG + '600-italic.woff',
    'sans':     JO + '500-normal.woff',   # labels, numbers (tracked caps)
    'sans_r':   JO + '400-normal.woff',
    'sans_sb':  JO + '600-normal.woff',
})

# palette
ONYX = (15, 14, 12)          # Vanta Black  #0F0E0C
ONYX_2 = (27, 24, 20)        # warm black for gradients  #1B1814
STONE = (239, 233, 223)      # Stone ivory  #EFE9DF
CHAMP = (201, 172, 125)      # Champagne    #C9AC7D
CHAMP_D = (150, 122, 84)     # Bronze (on light)  #967A54
MIST = (150, 141, 128)       # Warm grey    #968D80

def hexs(c): return '#%02X%02X%02X' % c

def wipe(L, p, soft=0.35):
    """soft left-to-right reveal of a text layer"""
    if p >= 1: return L
    if p <= 0: return None
    w = L.width
    x = np.linspace(0, 1, w, dtype=np.float32)
    a = np.clip((p * (1 + soft) - x) / soft, 0, 1)
    al = np.array(L.getchannel('A'), np.float32) * a[None, :]
    L = L.copy(); L.putalpha(Image.fromarray(al.astype(np.uint8))); return L

def reveal(im, L, cx, cy, t, t0, dur=0.55, rise=18, t_out=None, dout=0.3):
    """wipe + rise in; optional fade/blur/rise out"""
    if t < t0: return
    p = eo((t - t0) / dur)
    L2 = wipe(L, p * 1.0)
    if L2 is None: return
    a, blur, dy = 1.0, 0.0, rise * (1 - p)
    if t_out is not None and t > t_out:
        o = eo((t - t_out) / dout)
        a, blur, dy = 1 - o, o * 10, dy - 22 * o
    place(im, L2, cx, cy + dy, a=a, blur=blur)

def rule(im, cx, cy, w, p, col=CHAMP, a=1.0, thick=2):
    """hairline that grows from the centre"""
    if p <= 0: return
    ww = max(1, int(w * eo(p)))
    L = Image.new('RGBA', (ww, thick), col + (int(255 * a),))
    place(im, L, cx, cy)

def line(parts, gap=14):
    """compose several text layers on one baseline-centred line: parts = [(L, dy)]"""
    ws = [L.width for L, _ in parts]; hs = [L.height for L, _ in parts]
    Wt = sum(ws) - gap * 0 + gap * (len(parts) - 1); Ht = max(hs) + 20
    out = Image.new('RGBA', (Wt, Ht), (0, 0, 0, 0)); x = 0
    for (L, dy), w in zip(parts, ws):
        out.alpha_composite(L, (x, int((Ht - L.height) / 2 + dy))); x += w + gap
    return out

def outline_pill(txt, size=32, track=10, col=CHAMP, padx=44, pady=22, width=2):
    L = T(txt, 'sans', size, col, track=track, shadow=0)
    g = L.getbbox(); tw, th = g[2] - g[0], g[3] - g[1]
    w, h = int(tw + 2 * padx), int(th + 2 * pady)
    P = R.rrect((w, h), h // 2, (0, 0, 0, 0), outline=col + (255,), width=width)
    comp(P, L, (w - L.width) / 2, (h - L.height) / 2)
    return P

_bg = {}
def onyx_bg():
    """Vanta Black with a soft warm centre, not flat"""
    if 'bg' in _bg: return _bg['bg'].copy()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.42) / (H * 0.55)) ** 2)
    k = np.clip(1 - d, 0, 1) ** 1.6
    rgb = np.array(ONYX, np.float32)[None, None, :] * (1 - k[..., None]) + np.array(ONYX_2, np.float32)[None, None, :] * k[..., None]
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert('RGBA')
    _bg['bg'] = im
    return im.copy()

def baseline_line(parts, gap=16):
    """one line of mixed fonts on a shared baseline. parts = [(text, fontkey, size, colour, track_px)]"""
    from PIL import ImageDraw
    fonts = [R.font(fk, sz) for _, fk, sz, _, _ in parts]
    widths = [sum(f.getlength(c) for c in txt) + tr * max(len(txt) - 1, 0) for (txt, _, _, _, tr), f in zip(parts, fonts)]
    asc = max(f.getmetrics()[0] for f in fonts); desc = max(f.getmetrics()[1] for f in fonts)
    pad = 20
    Wt = int(sum(widths) + gap * (len(parts) - 1) + 2 * pad); Ht = asc + desc + 2 * pad
    im = Image.new('RGBA', (Wt, Ht), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = pad; base = pad + asc
    for (txt, fk, sz, col, tr), f, w in zip(parts, fonts, widths):
        cx = x
        for c in txt:
            d.text((cx, base), c, font=f, fill=col + (255,), anchor='ls'); cx += f.getlength(c) + tr
        x += w + gap
    bb = im.getbbox()
    return im.crop((bb[0] - 4, bb[1] - 4, bb[2] + 4, bb[3] + 4))
