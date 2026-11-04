# Video A: Vanta House short in Abdullahi's method (talking-head-reel-pipeline + video-ad-editor + vanta-film-workflow),
# built with the Motion Explainer Kit helpers. Source: blackstone 433A6916.MOV (0.5x slow motion, John's office).
# Usage: python3 renderA.py <out.mkv | frames_dir> [comma list of frames]
import sys, os, math, subprocess, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'
sys.path.insert(0, S + '/A/build')
import render as R
F = S + '/kit/fonts/'
R.FN.update({'anton': F + 'Anton.woff', 'ci': F + 'Caslon-Italic.woff', 'c': F + 'Caslon.woff', 'cb': F + 'Caslon-Bold.woff'})
from render import T, place, comp, fit, kin, eo, eio, eback, clamp, W, H, GOLD, GOLD_D, WHITE, INK, CREAM, rrect, chip
import kin2 as K
import motion_v3 as M

FPS = 30
PLATE = S + '/A/plateA.mkv'
MASKDIR = S + '/A/masks'
NPL = 122                 # plate frames (4.067 s)
END_IN = NPL              # end card starts right after the plate
END_LEN = 4.6
NFR = END_IN + int(END_LEN * FPS)

# ---------------------------------------------------------------- timing (s)
HOOK_HIT = 4 / FPS        # hook lands (whoosh peak, bass shake)
HOOK_OUT = 1.47           # hook eases out
BY_IN = 1.80              # "Vanta House is by" + BLACKSTONE pill rise from behind the head
BY_OUT = 3.47
TE = END_IN / FPS         # end card / flash

def f2t(f): return f / FPS

# ---------------------------------------------------------------- masks / person
def mask(i):
    p = os.path.join(MASKDIR, '%05d.png' % min(i, NPL - 1))
    return Image.open(p).convert('L')

def head_top(i):
    a = np.array(mask(i)); band = a[:, 200:340]
    rows = np.where(band.max(1) > 128)[0]
    return rows[0] * 2 if len(rows) else 460

def person(plate, i):
    m = mask(i).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))
    L = plate.copy(); L.putalpha(m); return L

# stronger top shade for this bright window/wall plate (kit topshade is tuned for darker plates)
_SH = None
def topshade(im):
    global _SH
    if _SH is None:
        y = np.arange(H, dtype=np.float32)
        a = (np.clip(1 - y / 980.0, 0, 1) ** 1.5 * 0.62)[:, None] * np.ones((1, W), np.float32)
        _SH = Image.new('RGBA', (W, H), (8, 6, 4, 0)); _SH.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    im.alpha_composite(_SH)

# ---------------------------------------------------------------- 1. hook: "Who is behind / VANTA HOUSE?" behind John's head
_hk = {}
def hook_layers():
    if _hk: return _hk
    s = fit('VANTA HOUSE?', 'anton', 930, 250)          # stays inside the 6 % side margins
    _hk['big'] = K.glow_text('VANTA HOUSE?', 'anton', s, GOLD, glow_col=M.GLOW, glow=16, gop=0.85)
    _hk['shadow'] = T('VANTA HOUSE?', 'anton', s, (0, 0, 0), shadow=0).filter(ImageFilter.GaussianBlur(14))
    _hk['h'] = M.gh('VANTA HOUSE?', 'anton', s)
    _hk['l1'] = T('Who is behind', 'ci', 70, WHITE, shadow=0.9, sblur=10, sdy=4)
    return _hk

def hook(im, t, i):
    if t > HOOK_OUT + 0.32: return
    Hk = hook_layers()
    p = clamp((t + 0.06) / (HOOK_HIT + 0.06))           # frame 0 already shows it arriving (thumbnail)
    e = eo(p)
    o = eo(clamp((t - HOOK_OUT) / 0.28))                  # ease out
    a = (0.55 + 0.45 * e) * (1 - o)
    sc = (1.0 + 0.22 * (1 - e)) * (1 + 0.03 * clamp(t / 1.6)) * (1 - 0.06 * o)
    cy = head_top(i) + 62 - Hk['h'] / 2 * sc              # glyph bottom tucks behind John's hair
    L = M.sheen(Hk['big'], (t - 0.75) / 0.6)
    place(im, Hk['shadow'], 540, cy + 10, a=0.55 * a, sc=sc)
    place(im, L, 540, cy - 20 * o, a=a, blur=(1 - e) * 6 + o * 10, sc=sc)
    gy = cy - Hk['h'] / 2 * sc
    if t < HOOK_OUT:
        kin(im, Hk['l1'], 540, gy - 62, t, -0.2, 9, din=0.3, dout=0, mode='rise')
    else:
        place(im, Hk['l1'], 540, gy - 62 - 24 * o, a=1 - o, blur=o * 10)

# ---------------------------------------------------------------- 2. answer: "Vanta House is by" + BLACKSTONE REAL ESTATE glass pill rising from behind the head
_pl = {}
def pill_layers():
    if _pl: return _pl
    l1 = T('Vanta House is by', 'ci', 50, GOLD, shadow=0)
    l2 = T('BLACKSTONE REAL ESTATE', 'anton', 66, WHITE, track=2, shadow=0)
    w = max(l1.width, l2.width) + 90; h = 190
    _pl.update(l1=l1, l2=l2, w=w, h=h, shape=rrect((w, h), 30, (255, 255, 255, 255)),
               border=rrect((w, h), 30, (0, 0, 0, 0), outline=(255, 255, 255, 120), width=2))
    sh = Image.new('RGBA', (w + 120, h + 120), (0, 0, 0, 0)); sh.alpha_composite(rrect((w, h), 30, (0, 0, 0, 120)), (60, 78))
    _pl['shadow'] = sh.filter(ImageFilter.GaussianBlur(20))
    return _pl

def by_pill(im, t, i, front=False):
    """dark frosted glass card, drawn BEFORE John's layer: it rises out from behind his head"""
    if front or not (BY_IN - 0.02 <= t <= BY_OUT + 0.4): return
    P = pill_layers()
    ht = head_top(i)
    pin = clamp((t - BY_IN) / 0.45)
    po = clamp((t - BY_OUT) / 0.32)
    y_end, y_start = 362, ht + 110                       # starts hidden behind the head, rises above it
    y = y_start + (y_end - y_start) * eback(pin, 1.1) + (y_start - y_end) * eio(po)
    y += 3 * math.sin((t - BY_IN) * 2.1)
    a = clamp(pin * 2.5) * (1 - clamp(po * 1.4 - 0.4))
    if a <= 0: return
    w, h = P['w'], P['h']
    comp(im, R.fade(P['shadow'], a), 540 - w / 2 - 60, y - h / 2 - 60)
    K.frosted(im, P['shape'], 540, y, a=a, blur=18, tint=(14, 12, 10, 150))
    comp(im, R.fade(P['border'], a), 540 - w / 2, y - h / 2)
    place(im, P['l1'], 540, y - 42, a=a)
    place(im, P['l2'], 540, y + 30, a=a)

# ---------------------------------------------------------------- 3. end card (approved Vanta card, no logo file here)
_E = None
def end_layout():
    global _E
    if _E: return _E
    badge = chip('FREE SITE VISIT', 50, fill=GOLD_D + (255,), col=WHITE, padx=48, pady=22, track=5)
    def g(txt, fn, size):
        b = R.font(fn, size).getbbox(txt); return b[3] - b[1]
    items = [('come', g('Come and see', 'ci', 56), 0), ('vh', g('VANTA HOUSE', 'anton', 150), 30),
             ('nag', g('Naguru, Kampala', 'ci', 48), 26), ('fsv', badge.height, 64), ('send', g('Send', 'ci', 52), 64),
             ('vanta', g('VANTA', 'anton', 124), 22), ('wa', g('on WhatsApp to', 'ci', 46), 22), ('num', g('0741 131 420', 'anton', 92), 24)]
    top, bot = 330, 1215
    k = (bot - top - sum(h for _, h, _ in items)) / sum(gap for _, _, gap in items)
    y = top; out = {'badge': badge}
    for name, h, gap in items:
        y += gap * k; out[name] = y + h / 2; y += h
    _E = out
    return out

def end_card(t):
    tl = t - TE
    im = Image.new('RGBA', (W, H), CREAM + (255,))
    # soft warm vignette so the cream is not flat
    E = end_layout()
    C2 = (80, 68, 52)
    kin(im, T('Come and see', 'ci', 56, C2, shadow=0), 540, E['come'], t, TE + 0.12, 99, din=0.3, dout=0, mode='rise')
    kin(im, T('VANTA HOUSE', 'anton', 150, INK, shadow=0), 540, E['vh'], t, TE + 0.42, 99, din=0.3, dout=0, mode='slam')
    kin(im, T('Naguru, Kampala', 'ci', 48, GOLD_D, shadow=0), 540, E['nag'], t, TE + 0.78, 99, din=0.3, dout=0, mode='rise')
    badge = E['badge']
    kin(im, badge, 540, E['fsv'], t, TE + 1.20, 99, din=0.32, dout=0, mode='pop')
    sp = (t - (TE + 1.75)) / 0.6
    if 0 < sp < 1:
        sh = Image.new('RGBA', badge.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        x = -120 + sp * (badge.width + 240)
        sd.polygon([(x, 0), (x + 60, 0), (x - 20, badge.height), (x - 80, badge.height)], fill=(255, 255, 255, 90))
        m = np.array(badge.getchannel('A')); sa = np.array(sh.getchannel('A')); sh.putalpha(Image.fromarray(np.minimum(m, sa)))
        place(im, sh, 540, E['fsv'])
    kin(im, T('Send', 'ci', 52, C2, shadow=0), 540, E['send'], t, TE + 1.75, 99, din=0.25, dout=0, mode='rise')
    kin(im, T('VANTA', 'anton', 124, GOLD_D, shadow=0), 540, E['vanta'], t, TE + 1.98, 99, din=0.25, dout=0, mode='slam')
    kin(im, T('on WhatsApp to', 'ci', 46, C2, shadow=0), 540, E['wa'], t, TE + 2.30, 99, din=0.3, dout=0, mode='rise')
    kin(im, T('0741 131 420', 'anton', 92, INK, track=3, shadow=0), 540, E['num'], t, TE + 2.62, 99, din=0.3, dout=0, mode='rise')
    s = 1 + 0.025 * clamp(tl / END_LEN)                  # slow push-in of the whole card
    if s > 1.0005:
        big = im.resize((round(W * s), round(H * s)), Image.BICUBIC)
        ox, oy = (big.width - W) / 2, (big.height - H) * 0.45
        im = big.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    return im

# ---------------------------------------------------------------- shake on the hook hit
def shake(im, i, hit=4):
    k = i - hit
    if 0 <= k < 6:
        amp = 10 * (1 - k / 6); dx = amp * math.sin(k * 2.7); dy = amp * math.cos(k * 3.3); s = 1.02
        big = im.resize((round(W * s), round(H * s)), Image.BICUBIC)
        ox = (big.width - W) / 2 + dx; oy = (big.height - H) / 2 + dy
        return big.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    return im

# ---------------------------------------------------------------- frame
def frame(i, fr):
    t = i / FPS
    if i >= END_IN:
        im = end_card(t)
        im = M.flash(im, t, TE, half=0.12, peak=0.9)
        return im.convert('RGB')
    plate = Image.fromarray(fr).convert('RGBA')
    im = plate.copy(); topshade(im)
    hook(im, t, i)                       # behind John
    by_pill(im, t, i, front=False)       # behind John (rises out from behind his head)
    im.alpha_composite(person(plate, i))
    by_pill(im, t, i, front=True)        # the small line above, in front
    im = shake(im, i)
    im = M.flash(im, t, TE, half=0.12, peak=0.9)
    return im.convert('RGB')

def main(out, only=None):
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', PLATE, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = None
    if out.endswith('.mkv'):
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                '-c:v', 'libx264rgb', '-qp', '0', '-preset', 'veryfast', out], stdin=subprocess.PIPE)
    else:
        os.makedirs(out, exist_ok=True)
    t0 = time.time(); last = None
    top = max(only) if only else NFR - 1
    for i in range(NFR):
        if i > top: break
        if i < NPL:
            raw = dec.stdout.read(W * H * 3)
            if len(raw) == W * H * 3: last = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
        if only is not None and i not in only: continue
        im = frame(i, last)
        if enc: enc.stdin.write(im.tobytes())
        else: im.save(os.path.join(out, '%05d.jpg' % i), quality=92)
        if i % 30 == 0: print(i, '%.1fs' % (time.time() - t0), flush=True)
    dec.stdout.close(); dec.kill()
    if enc: enc.stdin.close(); enc.wait()
    print('done', NFR, 'frames', '%.0fs' % (time.time() - t0), flush=True)

if __name__ == '__main__':
    only = set(int(x) for x in sys.argv[2].split(',')) if len(sys.argv) > 2 else None
    main(sys.argv[1], only)
