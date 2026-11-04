# Video F "Imagined vs Real" - Film 1 AI shots (artist's impression) against real site photos, then John (real), 17.5 s, 96 BPM (bar 2.5 s).
# bars 0-3  split screen: THE DREAM (AI, labelled) over THE WORK (real photo, dated); a new pair wipes in on every bar line
# bar 4     BUILT BY REAL PEOPLE: John (real footage, John-only crop), BLACKSTONE REAL ESTATE
# bars 5-6  FROM PICTURE / TO PLACE. + invitation (approved words)
import sys, os, math, subprocess, time
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
from docs_common import *
import docs_common as DC
_c = DC._c
reveal = ST.reveal

BAR = 2.5
DUR = 7 * BAR
NFR = int(round(DUR * FPS))
PW, PHH = 1000, 562
TOP = (40, 430); BOT = (40, 1016)
PAIRS = [(23.6, 'mmexport1792497989322.jpg', (0.50, 0.45)), (0.3, 'mmexport1792497982990.jpg', (0.5, 0.5)),
         (9.4, 'mmexport1792497986840.jpg', (0.5, 0.5)), (27.0, 'mmexport1792497978574.jpg', (0.5, 0.55))]
T_JOHN, T_END = 4 * BAR, 5 * BAR

def ai_frames(k):
    key = 'ai%d' % k
    if key not in _c: _c[key] = video_frames(FILM1, PAIRS[k][0], BAR + 0.6, 1080, 608)
    return _c[key]

def panel_ai(k, tl):
    fr = ai_frames(k); f = fr[min(max(int(tl * FPS), 0), len(fr) - 1)]
    z = 1.0 + 0.05 * clamp(tl / (BAR + 0.5))
    return fit_crop(Image.fromarray(f), PW, PHH, zoom=1.08 * z / 1.08 + 0.0)

def panel_real(k, tl):
    _, nm, (cx, cy) = PAIRS[k]
    z = 1.0 + 0.07 * clamp(tl / (BAR + 0.5))
    return fit_crop(photo(nm), PW, PHH, cx=cx + 0.02 * clamp(tl / BAR), cy=cy, zoom=z)

_L = {}
def L(key):
    if key in _L: return _L[key]
    if key == 'h1': v = T('ONE IS A PICTURE.', 'mo7', 62, WHITE, track=2, shadow=0)
    elif key == 'h2': v = T('ONE IS REAL.', 'mo7', 62, SAND, track=2, shadow=0)
    elif key == 'dream': v = pill('THE DREAM', 'mo7', 28, CHAR, SAND, track=6, padx=28, pady=16)
    elif key == 'work': v = pill('THE WORK', 'mo7', 28, CHAR, OFF, track=6, padx=28, pady=16)
    elif key == 'ai': v = pill("ARTIST'S IMPRESSION  ·  AI", 'px5', 22, WHITE, CHAR, track=2, padx=20, pady=12, alpha=170)
    elif key == 'real': v = pill('REAL PHOTO  ·  VANTA HOUSE SITE  ·  OCT 2026', 'px5', 22, WHITE, CHAR, track=2, padx=20, pady=12, alpha=170)
    elif key == 'vs':
        s = 96; im = Image.new('RGBA', (s * 3, s * 3), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.ellipse((6, 6, s * 3 - 6, s * 3 - 6), fill=CHAR + (255,), outline=SAND + (255,), width=6)
        im = im.resize((s, s), Image.LANCZOS); t = T('VS', 'mo7', 30, SAND, track=2, shadow=0); comp(im, t, (s - t.width) / 2, (s - t.height) / 2); v = im
    elif key == 'built': v = T('BUILT BY REAL PEOPLE.', 'mo7', 66, WHITE, track=2, shadow=0)
    elif key == 'bre': v = pill('BLACKSTONE REAL ESTATE', 'mo7', 32, CHAR, SAND, track=6, padx=36, pady=20)
    elif key == 'jreal': v = pill('REAL FOOTAGE', 'px5', 22, WHITE, CHAR, track=2, padx=20, pady=12, alpha=170)
    elif key == 'fp': v = T('FROM PICTURE', 'mo7', 108, SAND, track=2, shadow=0)
    elif key == 'tp': v = T('TO PLACE.', 'mo7', 108, WHITE, track=2, shadow=0)
    elif key == 'come': v = T('COME AND SEE THE SITE', 'px5', 32, (220, 216, 208), track=3, shadow=0)
    elif key == 'pill': v = pill('FREE SITE VISIT', 'mo7', 30, CHAR, SAND, track=8, padx=44, pady=22)
    elif key == 'send': v = baseline_line([('Send', 'mo4', 44, WHITE, 0), ('VANTA', 'mo7', 44, SAND, 8), ('on WhatsApp to', 'mo4', 44, WHITE, 0)], gap=16)
    elif key == 'num': v = T('0741 131 420', 'mo6', 84, WHITE, track=3, shadow=0)
    elif key == 'sig': v = T('BLACKSTONE REAL ESTATE', 'mo5', 25, MIST, track=9, shadow=0)
    _L[key] = v
    return v

def panel_layer(img, k_label, a=1.0):
    """rounded panel with its chips"""
    P = rounded(img, 22)
    if k_label == 'top':
        comp(P, L('dream'), 24, 24); comp(P, L('ai'), 24, PHH - L('ai').height - 22)
    else:
        comp(P, L('work'), 24, 24); comp(P, L('real'), 24, PHH - L('real').height - 22)
    return P

def shadow_for_panel():
    if 'psh' not in _c: _c['psh'] = soft_shadow(PW, PHH, 22, blur=28, a=0.45, dy=20)
    return _c['psh']

def pair_panels(t):
    """returns (top_img, bot_img) for time t in bars 0-3, wiping into the next pair on each bar line"""
    k = min(int(t // BAR), 3); tl = t - k * BAR
    top = panel_ai(k, tl + 0.4); bot = panel_real(k, tl + 0.4)
    if k > 0 and tl < 0.42:                         # wipe from the previous pair
        p = eio(tl / 0.42)
        pt = panel_ai(k - 1, BAR + tl + 0.4); pb = panel_real(k - 1, BAR + tl + 0.4)
        mt = Image.fromarray(wipe_mask(PW, PHH, p, direction=1)); mb = Image.fromarray(wipe_mask(PW, PHH, p, direction=-1))
        pt.paste(top, (0, 0), mt); pb.paste(bot, (0, 0), mb); top, bot = pt, pb
    return top, bot

def bg(): return radial(CHAR2, (18, 18, 17), 'char')

def john_panel(i):
    fr = Image.fromarray(wide_frames()[min(i, 121)]).crop((60, 140, 860, 590))    # John only
    z = 1.0 + 0.05 * clamp(i / 75)
    return fit_crop(fr, PW, PHH, zoom=z)

def frame(i):
    t = i / FPS
    im = bg()
    sh, pad = shadow_for_panel()
    if t < T_JOHN + 0.5:
        out = eio(clamp((t - T_JOHN) / 0.45))            # pair panels leave as John arrives
        if out < 1:
            top, bot = pair_panels(min(t, T_JOHN - 0.001))
            settle = 1 - eo(clamp(t / 0.3))
            for img, (x, y), lab, dy in ((top, TOP, 'top', -1), (bot, BOT, 'bot', 1)):
                P = panel_layer(img, lab)
                yy = y + dy * (260 * out) + dy * 18 * settle
                comp(im, R.fade(sh, 1 - out), x - pad, yy - pad); comp(im, R.fade(P, 1 - out), x, yy)
            place(im, L('vs'), 540, 1004, a=1 - out, sc=1 + 0.15 * settle)
            place(im, L('h1'), 540, 300, a=1 - out); place(im, L('h2'), 540, 368, a=1 - out)
    if T_JOHN <= t < T_END + 0.45:
        j = int(round((t - T_JOHN) * FPS))
        p = eo(clamp((t - T_JOHN - 0.1) / 0.45)); o = eio(clamp((t - T_END) / 0.4))
        J = rounded(john_panel(j), 22); comp(J, L('jreal'), 24, PHH - L('jreal').height - 22)
        sc = (0.9 + 0.1 * p) * (1 + 0.06 * o); a = p * (1 - o)
        place(im, R.fade(sh, a), 540, 860 + 20, sc=sc); place(im, J, 540, 860, a=a, sc=sc)
        if a > 0:
            reveal(im, L('built'), 540, 470, t, T_JOHN + 0.25, dur=0.5, t_out=T_END - 0.05, dout=0.3)
            if t >= T_JOHN + 0.6:
                q = clamp((t - T_JOHN - 0.6) / 0.35); place(im, L('bre'), 540, 1215, a=eo(q) * (1 - o), sc=0.85 + 0.15 * R.eback(q, 1.8))
    if t >= T_END + 0.2:
        te = T_END + 0.2
        reveal(im, L('fp'), 540, 545, t, te, dur=0.55)
        reveal(im, L('tp'), 540, 668, t, te + 0.2, dur=0.55)
        reveal(im, L('come'), 540, 790, t, te + 0.55, dur=0.5)
        if t >= te + 0.8:
            q = clamp((t - te - 0.8) / 0.35); place(im, L('pill'), 540, 885, a=eo(q), sc=0.8 + 0.2 * R.eback(q, 1.8))
        reveal(im, L('send'), 540, 1010, t, te + 1.1, dur=0.5)
        reveal(im, L('num'), 540, 1102, t, te + 1.35, dur=0.5)
        if t >= te + 1.8: place(im, L('sig'), 540, 1212, a=eo((t - te - 1.8) / 0.5))
    if t >= T_END:                                         # slow push-in so the end card never sits still
        sc = 1 + 0.022 * clamp((t - T_END) / (DUR - T_END))
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
