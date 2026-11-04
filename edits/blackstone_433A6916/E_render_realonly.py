# Video E "Not rendered. Real." - real footage and real site photos only (no AI, no renders). 16.8 s, 100 BPM (bar 2.4 s).
# bar 0      hook: full-bleed real site photo, NO RENDERS. / NO AI. / REAL. on the three timpani hits
# bars 1-3   site log: 12 real photos land as prints on the beat (shutter + flash): STEEL. / BRICK BY BRICK. / FLOOR BY FLOOR.
# bar 4      John, real footage: AND THE PEOPLE BEHIND IT / BLACKSTONE REAL ESTATE
# bars 5-6   John lands as the 13th print, the log blurs back, invitation card (approved words)
import sys, os, math, subprocess, time, random
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
from docs_common import *
import docs_common as DC
_c = DC._c

BAR, B = 2.4, 0.6
DUR = 7 * BAR
NFR = int(round(DUR * FPS))
HOOK = 'mmexport1792497989322.jpg'
LOG = [('STEEL.', ['mmexport1792497931884.jpg', 'mmexport1792497955791.jpg', 'mmexport1792497963081.jpg', 'mmexport1792673493181.jpg']),
       ('BRICK BY BRICK.', ['mmexport1792497950016.jpg', 'mmexport1792497980550.jpg', 'mmexport1792497978574.jpg', 'mmexport1792497976504.jpg']),
       ('FLOOR BY FLOOR.', ['mmexport1792497958870.jpg', 'mmexport1792497941583.jpg', 'mmexport1792673498404.jpg', 'mmexport1792497982990.jpg'])]
PRINTS = []   # (t_land, name, word)
for bi, (word, names) in enumerate(LOG):
    for k, nm in enumerate(names): PRINTS.append((BAR * (1 + bi) + k * B, nm, word))
T_JOHN, T_CARD = 4 * BAR, 5 * BAR
random.seed(4)
JIT = [(random.uniform(-26, 26), random.uniform(-22, 22), random.uniform(-3.2, 3.2)) for _ in range(14)]
PW, PH_, BORDER = 900, 675, 18
STACK_Y = 905

# ---------------------------------------------------------------- layers
_L = {}
def L(key):
    if key in _L: return _L[key]
    if key == 'nr': v = T('NO RENDERS.', 'mo7', 108, WHITE, track=2, shadow=0.6, sblur=16, sdy=6)
    elif key == 'nai': v = T('NO AI.', 'mo7', 108, WHITE, track=2, shadow=0.6, sblur=16, sdy=6)
    elif key == 'real': v = T('REAL.', 'mo7', 210, SAND, track=4, shadow=0.6, sblur=18, sdy=8)
    elif key == 'when': v = T('THE VANTA HOUSE SITE  ·  OCTOBER 2026', 'px5', 30, WHITE, track=2, shadow=0.8, sblur=8, sdy=2)
    elif key.startswith('w:'): v = T(key[2:], 'mo7', 84, CHAR, track=2, shadow=0)
    elif key.startswith('c:'): v = T(key[2:], 'px5', 28, GREY, track=1, shadow=0)
    elif key == 'people': v = T('AND THE PEOPLE BEHIND IT', 'px5', 30, WHITE, track=3, shadow=0.85, sblur=10, sdy=2)
    elif key == 'bre': v = T('BLACKSTONE REAL ESTATE', 'mo7', 62, WHITE, track=3, shadow=0.85, sblur=14, sdy=4)
    elif key == 'eyebrow': v = T('NO RENDERS. NO AI. JUST THE SITE.', 'px5', 28, SAND, track=2, shadow=0)
    elif key == 'h1': v = T('SEE IT WITH', 'mo7', 90, CHAR, track=2, shadow=0)
    elif key == 'h2': v = T('YOUR OWN EYES.', 'mo7', 90, CHAR, track=2, shadow=0)
    elif key == 'pill': v = pill('FREE SITE VISIT', 'mo6', 30, WHITE, CHAR, track=8, padx=44, pady=22)
    elif key == 'send': v = baseline_line([('Send', 'mo4', 44, CHAR, 0), ('VANTA', 'mo7', 44, SAND, 8), ('on WhatsApp to', 'mo4', 44, CHAR, 0)], gap=16)
    elif key == 'num': v = T('0741 131 420', 'mo6', 84, CHAR, track=3, shadow=0)
    elif key == 'sig': v = T('BLACKSTONE REAL ESTATE', 'mo5', 25, MIST, track=9, shadow=0)
    _L[key] = v
    return v

def make_print(img_rgb_pil, w=PW, h=PH_):
    key = ('pr', id(img_rgb_pil), w, h)
    if key in _c: return _c[key]
    ph = fit_crop(img_rgb_pil, w, h)
    card = Image.new('RGBA', (w + 2 * BORDER, h + 2 * BORDER), (252, 251, 248, 255)); card.paste(ph, (BORDER, BORDER))
    sh, pad = soft_shadow(card.width, card.height, 4, blur=22, a=0.30, dy=18)
    out = sh.copy(); out.alpha_composite(card, (pad, pad))
    _c[key] = out
    return out

def draw_print(im, P, cx, cy, rot, sc=1.0, a=1.0):
    if abs(rot) > 0.05 or abs(sc - 1) > 1e-3:
        P = P.resize((max(1, int(P.width * sc)), max(1, int(P.height * sc))), Image.BICUBIC).rotate(rot, resample=Image.BICUBIC, expand=True)
    place(im, P, cx, cy, a=a)

def stack(im, t, upto=None, john_print=None):
    """all prints landed by time t; newest on top; older ones stay underneath"""
    landed = [(k, p) for k, p in enumerate(PRINTS) if t >= p[0] - 0.12]
    if john_print is not None: landed.append(john_print)
    show = landed[-4:]
    for k, item in show:
        t_land, nm = item[0], item[1]
        P = john_print_img() if nm == 'JOHN' else make_print(photo(nm))
        jx, jy, rot = JIT[k]
        p = eo(clamp((t - (t_land - 0.12)) / 0.16))
        sc = 1.10 - 0.10 * p
        draw_print(im, P, 540 + jx, STACK_Y + jy, rot, sc=sc, a=clamp(p * 1.6))

def flash(im, t, t_hit, peak=0.32, dur=0.14):
    d = t - t_hit
    if 0 <= d < dur:
        a = peak * (1 - d / dur) ** 2
        im.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * a))))

# ---------------------------------------------------------------- John
def john_close(i):
    fr = wide_frames()[min(i, 121)]
    u = clamp(i / 72)
    z = 1.0 + 0.05 * u
    ch = 1080 / z; cw = ch * 9 / 16
    x0 = 460 - cw / 2; y0 = 420 - (420 - 0) / z if False else (1080 - ch) * 0.35
    M = np.array([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]], np.float32)
    return Image.fromarray(cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)).convert('RGBA')

def john_print_img():
    if 'jp' not in _c:
        fr = Image.fromarray(wide_frames()[100]).crop((60, 140, 860, 590))     # John only (the other man is not cleared yet)
        _c['jp'] = make_print(fr, 900, 506)
    return _c['jp']

_SH = None
def topshade(im):
    global _SH
    if _SH is None:
        y = np.arange(H, dtype=np.float32)
        al = (np.clip(1 - y / 900.0, 0, 1) ** 1.5 * 0.7)[:, None] * np.ones((1, W), np.float32)
        _SH = Image.new('RGBA', (W, H), (12, 12, 12, 0)); _SH.putalpha(Image.fromarray((al * 255).astype(np.uint8)))
    im.alpha_composite(_SH)

# ---------------------------------------------------------------- frame
def hook_frame(t):
    z = 1.0 + 0.06 * clamp(t / BAR)
    ph = fit_crop(photo(HOOK), W, H, cx=0.52, cy=0.5, zoom=z)
    a = np.asarray(ph).astype(np.float32) * 0.52
    im = Image.fromarray(a.astype(np.uint8)).convert('RGBA')
    hits = [(0.0, 'nr', 640), (B, 'nai', 790), (2 * B, 'real', 990)]
    for th, key, y in hits:
        if t >= th - 0.001:
            p = eo(clamp((t - th) / 0.14)) if th > 0 else eo(clamp(0.6 + t / 0.14))
            place(im, L(key), 540, y, a=clamp(p * 1.4), sc=1.22 - 0.22 * p)
            if th > 0: flash(im, t, th, peak=0.18, dur=0.12)
    if t >= 1.62:
        p = eo(clamp((t - 1.62) / 0.4)); v = ST.wipe(L('when'), p)
        if v is not None: place(im, v, 540, 1135)
    return im

def log_frame(t):
    im = radial(OFF, OFF2, 'off')
    stack(im, t)
    # current word + counter
    k = max(j for j, p in enumerate(PRINTS) if t >= p[0] - 0.12) if t >= PRINTS[0][0] - 0.12 else 0
    word = PRINTS[k][2]
    w0 = BAR * (1 + [w for w, _ in LOG].index(word))
    p = eo(clamp((t - w0 + 0.05) / 0.25))
    place(im, L('w:' + word), 540, 345 + 18 * (1 - p), a=p)
    place(im, L('c:REAL PHOTO %02d/12  ·  VANTA HOUSE SITE  ·  OCT 2026' % (k + 1)), 540, 432, a=clamp((t - PRINTS[0][0] + 0.1) / 0.2))
    for tl, _, _ in PRINTS: flash(im, t, tl, peak=0.30)
    return im

def john_frame(t):
    i = int(round((t - T_JOHN) * FPS))
    im = john_close(i); topshade(im)
    reveal(im, L('people'), 540, 300, t, T_JOHN + 0.15, dur=0.45)
    reveal(im, L('bre'), 540, 372, t, T_JOHN + 0.35, dur=0.55)
    return im

def card_frame(t):
    im = radial(OFF, OFF2, 'off')
    jp = (12, (T_CARD + 0.12, 'JOHN', ''))
    tmp = radial(OFF, OFF2, 'off'); stack(tmp, t, john_print=jp)
    flash(tmp, t, T_CARD + 0.12, peak=0.28)
    q = eio(clamp((t - T_CARD - 0.55) / 0.5))               # the log steps back: blur + fade
    if q > 0:
        tmp = tmp.filter(ImageFilter.GaussianBlur(14 * q))
        tmp = Image.blend(tmp, radial(OFF, OFF2, 'off'), 0.78 * q)
    im = tmp
    if t >= T_CARD + 0.75:
        tc = T_CARD + 0.75
        reveal(im, L('eyebrow'), 540, 520, t, tc, dur=0.45)
        reveal(im, L('h1'), 540, 625, t, tc + 0.15, dur=0.5)
        reveal(im, L('h2'), 540, 735, t, tc + 0.30, dur=0.5)
        if t >= tc + 0.6:
            qq = clamp((t - tc - 0.6) / 0.35); place(im, L('pill'), 540, 870, a=eo(qq), sc=0.8 + 0.2 * R.eback(qq, 1.8))
        reveal(im, L('send'), 540, 1000, t, tc + 0.95, dur=0.5)
        reveal(im, L('num'), 540, 1095, t, tc + 1.20, dur=0.5)
        if t >= tc + 1.6: place(im, L('sig'), 540, 1210, a=eo((t - tc - 1.6) / 0.5))
    return im

reveal = ST.reveal
def frame(i):
    t = i / FPS
    if t < BAR: im = hook_frame(t)
    elif t < T_JOHN: im = log_frame(t)
    elif t < T_CARD: im = john_frame(t)
    else: im = card_frame(t)
    if t >= T_CARD:                                         # slow push-in so the end card never sits still
        sc = 1 + 0.022 * clamp((t - T_CARD) / (DUR - T_CARD))
        big = im.resize((round(W * sc), round(H * sc)), Image.BICUBIC); ox, oy = (big.width - W) / 2, (big.height - H) * 0.45
        im = big.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    return im.convert('RGB')

def main(out, only=None):
    enc = None
    if out.endswith('.mkv'):
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                '-c:v', 'libx264rgb', '-qp', '0', '-preset', 'veryfast', out], stdin=subprocess.PIPE)
    else: os.makedirs(out, exist_ok=True)
    t0 = time.time()
    for i in (sorted(only) if only else range(NFR)):
        im = frame(i)
        if enc: enc.stdin.write(im.tobytes())
        else: im.save(os.path.join(out, '%05d.jpg' % i), quality=92)
        if i % 60 == 0: print(i, '%.1fs' % (time.time() - t0), flush=True)
    if enc: enc.stdin.close(); enc.wait()
    print('done', NFR, 'frames', '%.0fs' % (time.time() - t0), flush=True)

if __name__ == '__main__':
    only = set(int(x) for x in sys.argv[2].split(',')) if len(sys.argv) > 2 else None
    main(sys.argv[1], only)
