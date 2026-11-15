# v2 effects + text (brand: Inter, white, teal #2EC4B6)
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from v2core import W, H, ease, eout
FONT = '/usr/share/fonts/opentype/inter/'
TEAL = (46, 196, 182)
_fc = {}
def font(name, size):
    k = (name, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(FONT + name, size)
    return _fc[k]

def text_rgba(text, name, size, fill=(255, 255, 255), tracking=0, stroke=0):
    f = font(name, size)
    d0 = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    if tracking:
        ws = [d0.textlength(c, font=f) for c in text]; tw = int(sum(ws) + tracking * (len(text) - 1)) + 8
    else:
        tw = int(d0.textlength(text, font=f)) + 8
    asc, desc = f.getmetrics(); th = asc + desc + 8
    im = Image.new('RGBA', (tw + 2 * stroke, th + 2 * stroke), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if tracking:
        x = 4 + stroke
        for c, w in zip(text, ws): d.text((x, 4 + stroke), c, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 160)); x += w + tracking
    else:
        d.text((4 + stroke, 4 + stroke), text, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 160))
    return np.asarray(im).astype(np.float32) / 255

def paste(canvas, rgba, cx, cy, alpha=1.0, scale=1.0, blur=0.0, shadow=0.55, dy=0.0):
    """alpha-composite an RGBA text image centred at (cx, cy) with soft shadow; scale pop and blur-resolve"""
    if alpha <= 0.01: return canvas
    a = rgba
    if scale != 1.0: a = cv2.resize(a, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    if blur > 0.3: a = cv2.GaussianBlur(a, (0, 0), blur)
    h, w = a.shape[:2]; x0 = int(round(cx - w / 2)); y0 = int(round(cy - h / 2 + dy))
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if xb <= xa or yb <= ya: return canvas
    sub = a[ya - y0:yb - y0, xa - x0:xb - x0]
    if shadow:
        sh = cv2.GaussianBlur(a[..., 3], (0, 0), 7) * shadow * alpha
        sh = np.roll(np.roll(sh, 5, 0), 3, 1)[ya - y0:yb - y0, xa - x0:xb - x0]
        canvas[ya:yb, xa:xb] *= (1 - sh[..., None])
    k = sub[..., 3:4] * alpha
    canvas[ya:yb, xa:xb] = canvas[ya:yb, xa:xb] * (1 - k) + sub[..., :3] * 255 * k
    return canvas

def bar(canvas, cx, y, alpha=1.0, w=96, h=6, grow=1.0):
    ww = int(w * grow)
    if ww < 2 or alpha <= 0: return canvas
    x0 = int(cx - ww / 2); canvas[y:y + h, x0:x0 + ww] = canvas[y:y + h, x0:x0 + ww] * (1 - alpha) + np.array(TEAL, np.float32) * alpha
    return canvas

def shine(rgba, p, width=0.18):
    """R3 'Shine': a bright diagonal glint sweeping across the letters, p = 0..1 progress"""
    h, w = rgba.shape[:2]; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    pos = (xx + yy * 0.5) / (w + h * 0.5); g = np.exp(-((pos - (p * 1.4 - 0.2)) / width) ** 2)
    out = rgba.copy(); out[..., :3] = np.clip(out[..., :3] + g[..., None] * 0.9 * out[..., 3:4], 0, 1)
    out[..., :3] = out[..., :3] * (1 - 0.35 * g[..., None]) + np.array([0.75, 1.0, 0.97]) * 0.35 * g[..., None]
    return out

# ---------- frame effects ----------
def flash(img, k, warm=False):
    """white-out on a cut (R4): k = frame index relative to cut (-1..5)"""
    al = {-1: 0.6, 0: 1.0, 1: 0.7, 2: 0.45, 3: 0.25, 4: 0.1}.get(k, 0)
    if al <= 0: return img
    col = np.array((255, 232, 196) if warm else (255, 255, 255), np.float32)
    return img * (1 - al) + col * al

def light_leak(img, k, n=10, corner=(1.0, 0.15)):
    """warm orange->yellow leak from a corner (R6), screen blend; k = 0..n-1"""
    al = [0.0, 0.25, 0.5, 0.9, 1.0, 0.6, 0.35, 0.2, 0.1, 0.0][min(max(k, 0), 9)]
    if al <= 0: return img
    yy, xx = np.mgrid[0:H:8, 0:W:8].astype(np.float32)
    d = np.sqrt(((xx / W - corner[0]) * 1.0) ** 2 + ((yy / H - corner[1]) * 0.6) ** 2)
    g = np.clip(1 - d / 0.9, 0, 1) ** 1.6
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    col = np.dstack([np.full_like(g[..., 0], 255), 150 + 90 * g[..., 0], 30 + 120 * g[..., 0] ** 2])
    lay = col * g * al
    return 255 - (255 - img) * (255 - lay) / 255

def shake(k):
    """4-frame camera shake offsets on an impact (dx, dy)"""
    return [(8, -6), (-6, 5), (4, -3), (-2, 1)][k] if 0 <= k < 4 else (0, 0)

def blur_in(img, k):
    s = [14, 9, 5, 3, 1.5][k] if 0 <= k < 5 else 0
    return cv2.GaussianBlur(img, (0, 0), s) * (1 + 0.02 * s / 14 * 5) if s else img

def grain(img, rng, amt=5.0):
    n = rng.standard_normal((H // 2, W // 2)).astype(np.float32)
    n = cv2.resize(n, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    return img + n * amt

def paper(seed=3):
    """warm newsprint paper texture (R2 collage / halftone background)"""
    rng = np.random.default_rng(seed)
    base = np.ones((H, W, 3), np.float32) * np.array((226, 214, 192), np.float32)
    n = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 2.0) * 10
    n2 = cv2.resize(cv2.GaussianBlur(rng.standard_normal((H // 16, W // 16)).astype(np.float32), (0, 0), 2), (W, H)) * 14
    base = base + (n + n2)[..., None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = 1 - 0.28 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return base * v[..., None]

def neon(text, size=120, name='Inter-ExtraBold.otf', glow=(120, 235, 225)):
    """R9 glowing word: white core + teal-tinted glow (brand teal), returned as RGBA float"""
    core = text_rgba(text, name, size)
    pad = int(size * 0.6)
    a = cv2.copyMakeBorder(core, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    al = a[..., 3]
    g1 = cv2.GaussianBlur(al, (0, 0), size * 0.07); g2 = cv2.GaussianBlur(al, (0, 0), size * 0.22)
    glowa = np.clip(g1 * 1.1 + g2 * 0.9, 0, 1)
    col = np.array(glow, np.float32) / 255
    rgb = col * glowa[..., None] * (1 - al[..., None]) + np.array([1.0, 1.0, 1.0]) * al[..., None]
    out = np.dstack([rgb / np.maximum(np.maximum(glowa, al)[..., None], 1e-3), np.maximum(glowa * 0.85, al)])
    return np.clip(out, 0, 1)

def warp_word(rgba, M33, out_w=W, out_h=H):
    """place an RGBA word with a 3x3 perspective matrix onto canvas coords; returns full-size RGBA"""
    return cv2.warpPerspective(rgba, M33, (out_w, out_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

def comp_rgba(canvas, full, alpha=1.0, add_glow=True, backing=0.6):
    k = full[..., 3:4] * alpha
    if backing:    # soft dark halo behind the neon so it reads on bright sky / concrete
        bk = cv2.GaussianBlur(full[..., 3], (0, 0), 14)[..., None] * alpha * backing
        canvas = canvas * (1 - bk)
    if add_glow:   # screen-like: glow brightens, core covers
        return canvas * (1 - k * 0.55) + full[..., :3] * 255 * k
    return canvas * (1 - k) + full[..., :3] * 255 * k

def neon_flicker(k):
    """neon switch-on: frames 0..6 alpha pattern"""
    return [0.0, 0.8, 0.15, 1.0, 0.5, 1.0, 1.0][k] if 0 <= k < 7 else 1.0
