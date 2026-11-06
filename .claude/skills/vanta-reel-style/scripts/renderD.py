# Video D: Vanta House short in style 3 "Modern Clean" (Montserrat; off-white, charcoal, sand), 15 s, scored at 114 BPM.
# 0.00-1.87  John close-up, "WHO IS BEHIND / VANTA HOUSE?" behind his head
# 1.87-2.50  zoom-out to the meeting in a rounded window on off-white
# 2.50-4.21  "VANTA HOUSE IS BY / BLACKSTONE REAL ESTATE"
# 4.21 / 6.32 / 8.42  hard cuts on bar lines to three Vanta renders (artist's impression), fact chip on each
# 10.53-15.00  end card panel slides up (approved words)
# Usage: python3 renderD.py <out.mkv | frames_dir> [comma list of frames]
import sys, os, math, subprocess, time
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
SC = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts'
sys.path.insert(0, SC)
_argv = sys.argv; sys.argv = [sys.argv[0], 'masks']
import renderC as RC
sys.argv = _argv
import styleC as ST
from styleC import R, T, place, comp, clamp, eo, eio, W, H, reveal, baseline_line

S = ST.S
MO = S + '/fonts2/montserrat/package/files/montserrat-latin-'
R.FN.update({'mo4': MO + '400-normal.woff', 'mo5': MO + '500-normal.woff', 'mo6': MO + '600-normal.woff', 'mo7': MO + '700-normal.woff'})
OFF, OFF2 = (243, 241, 237), (232, 229, 223)
CHAR, SAND, GREY, MIST = (30, 30, 30), (176, 146, 104), (110, 106, 100), (140, 136, 130)
WHITE = (255, 255, 255)

FPS = 30
BAR = 4 * 60 / 114
CUTS = [2 * BAR, 3 * BAR, 4 * BAR]          # 4.21, 6.32, 8.42
TE = 5 * BAR                                # 10.53 end card
DUR = 15.0
NFR = int(DUR * FPS)
MOVE0, MOVE1 = RC.MOVE0, RC.MOVE1
WIN = RC.WIN
NO_WA = False                               # True: end card without the WhatsApp line (owner, 4 Nov)
RAD = 26

# ---------------------------------------------------------------- backgrounds
_c = {}
def light_bg():
    if 'bg' in _c: return _c['bg'].copy()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H * 0.42) / (H * 0.6)) ** 2)
    k = np.clip(1 - d, 0, 1) ** 1.4
    rgb = np.array(OFF2, np.float32) * (1 - k[..., None]) + np.array(OFF, np.float32) * k[..., None]
    _c['bg'] = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert('RGBA')
    return _c['bg'].copy()

def rounded_mask(x, y, w, h, r):
    """antialiased rounded-rect mask (2x supersampled)"""
    m = Image.new('L', (W * 2, H * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle((x * 2, y * 2, (x + w) * 2, (y + h) * 2), r * 2, fill=255)
    return np.array(m.resize((W, H), Image.LANCZOS))

def shadow_layer(x, y, w, h, r, a=0.17):
    q = 4
    m = Image.new('L', (W // q, H // q), 0)
    ImageDraw.Draw(m).rounded_rectangle((x / q, (y + 26) / q, (x + w) / q, (y + h + 26) / q), r / q, fill=int(255 * a))
    m = m.filter(ImageFilter.GaussianBlur(30 / q)).resize((W, H), Image.BILINEAR)
    L = Image.new('RGBA', (W, H), CHAR + (0,)); L.putalpha(m); return L

# ---------------------------------------------------------------- stage 1+2: John, zoom-out, window
_L = {}
def L(key):
    if key in _L: return _L[key]
    if key == 'who': v = T('WHO IS BEHIND', 'mo5', 40, WHITE, track=10, shadow=0.9, sblur=12, sdy=3)
    elif key == 'vh':
        s = R.fit('VANTA HOUSE?', 'mo7', 880, 210, track=1)
        v = T('VANTA HOUSE?', 'mo7', s, WHITE, track=1, shadow=0.85, sblur=18, sdy=6)
    elif key == 'by': v = T('VANTA HOUSE IS BY', 'mo6', 30, SAND, track=10, shadow=0)
    elif key == 'bre': v = T('BLACKSTONE REAL ESTATE', 'mo7', 54, CHAR, track=3, shadow=0)
    elif key == 'tag':
        Lt = T("ARTIST'S IMPRESSION  ·  FURNITURE SHOWN FOR STYLE", 'mo5', 21, WHITE, track=3, shadow=0)
        g = Lt.getbbox(); w, h = g[2] - g[0] + 44, g[3] - g[1] + 26
        v = R.rrect((w, h), h // 2, CHAR + (120,)); comp(v, Lt, (w - Lt.width) / 2, (h - Lt.height) / 2)
    _L[key] = v
    return v

def hook(im, t, i):
    t_out = 1.50
    if t > t_out + 0.35: return
    vh, who = L('vh'), L('who')
    cy = RC.head_top(i) + 58 - vh.height / 2 + 30
    p = 0.78 + 0.22 * eo(clamp(t / 0.22))
    o = eo(clamp((t - t_out) / 0.3))
    v2 = ST.wipe(vh, p)
    if v2 is not None: place(im, v2, 540, cy - 24 * o, a=1 - o, blur=o * 10, sc=1 + 0.03 * clamp(t / 1.5))
    w2 = ST.wipe(who, clamp(0.9 + t / 0.2))
    if w2 is not None: place(im, w2, 540, cy - vh.height / 2 - 4 - 24 * o, a=1 - o, blur=o * 10)

def stage_john(src, t, i):
    v, cover = RC.view(src, t)
    s, o, clip = RC.cam(t)
    plate = Image.fromarray(v).convert('RGBA')
    im = light_bg()
    if t > MOVE0:
        pr = clamp((t - MOVE0) / (MOVE1 - MOVE0))
        x, y, w, h = (WIN if clip is not None else (o[0], o[1], 1920 * s, 1080 * s))
        if w < 2600:
            r = RAD * eo(pr)
            if clip is not None:
                if 'winmask' not in _c: _c['winmask'] = rounded_mask(*WIN, RAD); _c['winshadow'] = shadow_layer(*WIN, RAD)
                rm, sh = _c['winmask'], _c['winshadow']
            else:
                rm, sh = rounded_mask(x, y, w, h, r), shadow_layer(x, y, w, h, r, a=0.17 * pr)
            cover = np.minimum(cover, rm)
            im.alpha_composite(sh)
    pl = plate.copy(); pl.putalpha(Image.fromarray(cover)); im.alpha_composite(pl)
    if t <= MOVE0 + 0.1:
        RC.topshade(im, a=1 - eo(clamp((t - MOVE0 + 0.2) / 0.3)))
        hook(im, t, i)
        if i < RC.NM:
            m = RC.mask(i).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))
            person = plate.copy(); person.putalpha(Image.fromarray(np.minimum(np.array(m), cover)))
            im.alpha_composite(person)
    reveal(im, L('by'), 540, 430, t, 2.30, dur=0.5)
    reveal(im, L('bre'), 540, 500, t, 2.45, dur=0.6)
    return im

# ---------------------------------------------------------------- stage 3: renders (artist's impression)
RD = S + '/renders/'
SHOTS = [('vanta_vr_3bhk_1_living.jpg', 2, 1330, 40, '1, 2 & 3 BEDROOM HOMES'),
         ('vanta_vr_2bhk_2_bedroom1.jpg', 2, 1250, -40, 'IN NAGURU, KAMPALA'),
         ('vanta_vr_2bhk_1_living.jpg', 0, 1300, 50, 'HANDOVER EXPECTED OCTOBER 2027')]
def face(k):
    key = 'face%d' % k
    if key not in _c:
        f, idx, *_ = SHOTS[k]
        im = cv2.cvtColor(cv2.imread(RD + f), cv2.COLOR_BGR2RGB)
        _c[key] = np.ascontiguousarray(im[idx * 2560:(idx + 1) * 2560])
    return _c[key]

def chip(txt):
    key = 'chip:' + txt
    if key not in _c:
        Lt = T(txt, 'mo6', 32, WHITE, track=6, shadow=0)
        g = Lt.getbbox(); w, h = g[2] - g[0] + 84, g[3] - g[1] + 46
        P = R.rrect((w, h), h // 2, CHAR + (236,)); comp(P, Lt, (w - Lt.width) / 2, (h - Lt.height) / 2)
        _c[key] = P
    return _c[key]

def render_shot(k, tl, dur):
    F = face(k); _, _, cx, pan, txt = SHOTS[k]
    u = clamp(tl / dur)
    z = 1.06 + 0.08 * u
    if tl < 0.2: z *= 1 + 0.05 * (1 - eo(tl / 0.2))            # punch settle on the cut
    ch = 2560 / z; cw = ch * 9 / 16
    x0 = cx + pan * u - cw / 2; y0 = 1370 - ch / 2
    x0 = max(0, min(2560 - cw, x0)); y0 = max(0, min(2560 - ch, y0))
    M = np.array([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]], np.float32)
    v = cv2.warpAffine(F, M, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REFLECT)
    if 'vig' not in _c:                                          # light photographic finish for the renders
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W * 0.7)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)
        _c['vig'] = (1 - 0.13 * np.clip(d - 0.35, 0, 1) ** 1.3)[..., None].astype(np.float32)
    f = v.astype(np.float32)
    f = (f - 128) * 1.06 + 124                                    # a touch more contrast, highlights eased
    f[..., 2] *= 0.985                                            # warm a hair
    v = np.clip(f * _c['vig'], 0, 255).astype(np.uint8)
    im = Image.fromarray(v).convert('RGBA')
    p = eo(clamp((tl - 0.10) / 0.32))
    if p > 0:
        sc = 0.9 + 0.1 * R.eback(clamp((tl - 0.10) / 0.32), 1.8)
        place(im, chip(txt), 540, 360 + 16 * (1 - p), a=p, sc=sc)
        place(im, L('tag'), 540, 1212, a=0.92 * p)
    return im

# ---------------------------------------------------------------- stage 4: end card (style 3)
def end_layers():
    if 'end' in _c: return _c['end']
    s = R.fit('VANTA HOUSE', 'mo7', 900, 150, track=4)
    Lt = T('FREE SITE VISIT', 'mo6', 30, WHITE, track=8, shadow=0); g = Lt.getbbox(); w, h = g[2] - g[0] + 88, g[3] - g[1] + 44
    pill = R.rrect((w, h), h // 2, CHAR + (255,)); comp(pill, Lt, (w - Lt.width) / 2, (h - Lt.height) / 2)
    E = dict(come=T('COME AND SEE', 'mo6', 30, SAND, track=10, shadow=0),
             vh=T('VANTA HOUSE', 'mo7', s, CHAR, track=4, shadow=0),
             nag=T('Naguru, Kampala', 'mo5', 46, GREY, shadow=0),
             pill=pill,
             send=baseline_line([('Send', 'mo4', 44, CHAR, 0), ('VANTA', 'mo7', 44, SAND, 8), ('on WhatsApp to', 'mo4', 44, CHAR, 0)], gap=16),
             num=T('0741 131 420', 'mo6', 82, CHAR, track=3, shadow=0),
             sig=T('BLACKSTONE REAL ESTATE', 'mo5', 25, MIST, track=9, shadow=0))
    _c['end'] = E
    return E

def end_panel(t):
    E = end_layers(); tl = t - TE
    im = light_bg()
    reveal(im, E['come'], 540, 470, t, TE + 0.25, dur=0.45)
    if t >= TE + 0.38:
        p = eo((t - TE - 0.38) / 0.6); v = ST.wipe(E['vh'], p)
        if v is not None: place(im, v, 540, 572 + 14 * (1 - p))
    reveal(im, E['nag'], 540, 668, t, TE + 0.70, dur=0.45)
    if t >= TE + 0.90: ST.rule(im, 540, 740, 110, clamp((t - TE - 0.90) / 0.45), col=SAND)
    if t >= TE + 1.05:
        q = clamp((t - TE - 1.05) / 0.35)
        place(im, E['pill'], 540, 832, a=eo(q), sc=0.8 + 0.2 * R.eback(q, 1.8))
    if not NO_WA:
        reveal(im, E['send'], 540, 985, t, TE + 1.45, dur=0.5)
        reveal(im, E['num'], 540, 1080, t, TE + 1.75, dur=0.5)
    if t >= TE + (1.5 if NO_WA else 2.15): place(im, E['sig'], 540, 980 if NO_WA else 1200, a=eo((t - TE - (1.5 if NO_WA else 2.15)) / 0.5))
    s = 1 + 0.015 * clamp(tl / (DUR - TE))
    big = im.resize((round(W * s), round(H * s)), Image.BICUBIC)
    ox, oy = (big.width - W) / 2, (big.height - H) * 0.45
    return big.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))

# ---------------------------------------------------------------- frame
def frame(i, src):
    t = i / FPS
    if t < CUTS[0]:
        im = stage_john(src, t, i)
    elif t < TE + 0.5:
        k = 0 if t < CUTS[1] else (1 if t < CUTS[2] else 2)
        t0 = CUTS[k]; t1 = CUTS[k + 1] if k < 2 else TE + 0.5
        im = render_shot(k, t - t0, t1 - t0)
        if t >= TE:                                             # end card panel slides up over the last render
            p = eio((t - TE) / 0.45)
            im = Image.blend(im, Image.new('RGBA', (W, H), (0, 0, 0, 255)), 0.25 * p)
            panel = end_panel(t); y = int(H * (1 - p))
            sh = Image.new('RGBA', (W, 60), (0, 0, 0, 0)); a = np.linspace(0, 70 * p, 60).astype(np.uint8)[:, None] * np.ones((1, W), np.uint8)
            sh.putalpha(Image.fromarray(a)); comp(im, sh, 0, y - 60)
            comp(im, panel.crop((0, 0, W, H - y)), 0, y)
    else:
        im = end_panel(t)
    return im.convert('RGB')

def main(out, only=None):
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', RC.WIDE, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
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
        if i < RC.NPL:
            raw = dec.stdout.read(1920 * 1080 * 3)
            if len(raw) == 1920 * 1080 * 3: last = np.frombuffer(raw, np.uint8).reshape(1080, 1920, 3)
        if only is not None and i not in only: continue
        im = frame(i, last)
        if enc: enc.stdin.write(im.tobytes())
        else: im.save(os.path.join(out, '%05d.jpg' % i), quality=92)
        if i % 60 == 0: print(i, '%.1fs' % (time.time() - t0), flush=True)
    dec.stdout.close(); dec.kill()
    if enc: enc.stdin.close(); enc.wait()
    print('done', NFR, 'frames', '%.0fs' % (time.time() - t0), flush=True)

if __name__ == '__main__':
    only = set(int(x) for x in sys.argv[2].split(',')) if len(sys.argv) > 2 else None
    main(sys.argv[1], only)
