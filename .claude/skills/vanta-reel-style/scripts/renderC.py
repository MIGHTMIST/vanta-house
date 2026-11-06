# Video C: Claude's own edit of blackstone 433A6916 in the proposed Vanta style v2
# (Vanta Black / Stone / Champagne, Cormorant Garamond + Jost). Same approved facts as video A.
# Shot 1  0.00-1.87  John close, "Who is behind VANTA HOUSE?" behind his head
# Move    1.87-2.50  one continuous zoom-out from John's close-up to the full meeting, framed as an editorial window
# Shot 2  2.50-3.95  the meeting in the window, "Vanta House is by / BLACKSTONE REAL ESTATE" above it
# End     3.80-8.47  dark end card (approved words), dark-to-dark dissolve, no white flash
# Usage: python3 renderC.py masks | <out.mkv | frames_dir> [comma list of frames]
import sys, os, math, subprocess, time
import numpy as np, cv2
from PIL import Image, ImageFilter
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
import styleC as ST
from styleC import R, T, place, comp, clamp, eo, eio, W, H, ONYX, STONE, CHAMP, MIST, reveal, rule, line, outline_pill, onyx_bg

S = ST.S
FPS = 30
WIDE = S + '/C/wideC.mkv'
MASKDIR = S + '/C/masks'
NPL = 122
X_IN, X_OUT = 3.80, 4.12          # dissolve plate -> end card
TE = 3.95                         # end card time base
END_LEN = 4.52
NFR = int(round((TE + END_LEN) * FPS))
NM = 60                           # frames that need person masks (shot 1)

# ---------------------------------------------------------------- camera: source (1920x1080) -> screen (1080x1920)
SC_CLOSE = 1080 / 608.0           # close: source x 156..764 fills the screen
F = np.array([460.0, 420.0])      # focal point: John's face
WIN = (40, 600, 1000, 562.5)      # editorial window x, y, w, h
SC_WIDE = WIN[2] / 1920.0
MOVE0, MOVE1 = 1.87, 2.50

def cam(t):
    """returns scale s and offset (ox, oy): screen = s * src + o, plus clip rect or None"""
    push = 1 + 0.04 * clamp(t / MOVE0)                       # slow push-in on the close-up
    s_close = SC_CLOSE * push
    fx_close = np.array([540.0, (420 - 0) * SC_CLOSE])       # where the face sits on screen in the close-up
    # keep the head line: the push-in grows about the face
    pos_close = fx_close
    s_wide = SC_WIDE
    pos_wide = np.array([WIN[0], WIN[1]]) + F * SC_WIDE
    if t <= MOVE0:
        s, pos, clip = s_close, pos_close, None
    elif t < MOVE1:
        p = eio((t - MOVE0) / (MOVE1 - MOVE0))
        s = math.exp(math.log(SC_CLOSE * 1.04) * (1 - p) + math.log(s_wide) * p)
        pos = pos_close * (1 - p) + pos_wide * p
        clip = None
    else:
        q = clamp((t - MOVE1) / (TE + 0.4 - MOVE1))
        s = s_wide * (1 + 0.035 * q)                         # slow push inside the window
        c = np.array([WIN[0] + WIN[2] / 2, WIN[1] + WIN[3] / 2])
        pos = c + (F - np.array([960.0, 540.0])) * s * 0.0 + (F - np.array([960.0, 540.0])) * s  # keep frame centred on window centre
        pos = c + (F - np.array([960.0, 540.0])) * s
        clip = WIN
    o = pos - s * F
    return s, o, clip

def view(src, t):
    s, o, clip = cam(t)
    M = np.array([[s, 0, o[0]], [0, s, o[1]]], np.float32)
    interp = cv2.INTER_LANCZOS4 if s > 1 else cv2.INTER_AREA
    out = cv2.warpAffine(src, M, (W, H), flags=interp, borderMode=cv2.BORDER_CONSTANT, borderValue=ONYX)
    # where the frame does not cover the screen we want the onyx background
    cover = cv2.warpAffine(np.full(src.shape[:2], 255, np.uint8), M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    if clip is not None:
        x, y, w, h = clip
        m = np.zeros((H, W), np.uint8); m[int(round(y)):int(round(y + h)), int(round(x)):int(round(x + w))] = 255
        cover = np.minimum(cover, m)
    return out, cover

# ---------------------------------------------------------------- masks (shot 1 only)
def make_masks():
    from rembg import new_session, remove
    os.makedirs(MASKDIR, exist_ok=True)
    ses = new_session('u2net_human_seg')
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', WIDE, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    for i in range(NM):
        raw = dec.stdout.read(1920 * 1080 * 3)
        src = np.frombuffer(raw, np.uint8).reshape(1080, 1920, 3)
        v, _ = view(src, i / FPS)
        small = Image.fromarray(v).resize((540, 960), Image.BILINEAR)
        remove(small, session=ses, only_mask=True).save(os.path.join(MASKDIR, '%05d.png' % i))
    dec.kill(); print('masks', NM)

def mask(i):
    return Image.open(os.path.join(MASKDIR, '%05d.png' % min(i, NM - 1))).convert('L')

def head_top(i):
    a = np.array(mask(i)); band = a[:, 200:340]
    rows = np.where(band.max(1) > 128)[0]
    return rows[0] * 2 if len(rows) else 460

# ---------------------------------------------------------------- layers
_SH = None
def topshade(im, a=1.0):
    global _SH
    if _SH is None:
        y = np.arange(H, dtype=np.float32)
        al = (np.clip(1 - y / 1000.0, 0, 1) ** 1.4 * 0.72)[:, None] * np.ones((1, W), np.float32)
        _SH = Image.new('RGBA', (W, H), ONYX + (0,)); _SH.putalpha(Image.fromarray((al * 255).astype(np.uint8)))
    im.alpha_composite(_SH if a >= 1 else R.fade(_SH, a))

_L = {}
def L(key):
    if key in _L: return _L[key]
    if key == 'who':   v = T('Who is behind', 'serif_i6', 84, CHAMP, shadow=0.9, sblur=14, sdy=4)
    elif key == 'vh':
        s = R.fit('VANTA HOUSE?', 'serif_b', 880, 220, track=2)
        v = T('VANTA HOUSE?', 'serif_b', s, STONE, track=2, shadow=0.9, sblur=18, sdy=6)
    elif key == 'by':  v = T('Vanta House is by', 'serif_i', 66, CHAMP, shadow=0)
    elif key == 'bre': v = T('BLACKSTONE REAL ESTATE', 'sans', 46, STONE, track=9, shadow=0)
    elif key == 'come': v = T('COME AND SEE', 'sans', 33, CHAMP, track=12, shadow=0)
    elif key == 'VH':
        s = R.fit('VANTA HOUSE', 'serif', 930, 168, track=10)
        v = T('VANTA HOUSE', 'serif', s, STONE, track=10, shadow=0)
    elif key == 'nag': v = T('Naguru, Kampala', 'serif_i', 60, CHAMP, shadow=0)
    elif key == 'fsv': v = outline_pill('FREE SITE VISIT', 31, 10, CHAMP)
    elif key == 'send':
        v = ST.baseline_line([('Send', 'serif_i', 58, STONE, 0), ('VANTA', 'sans_sb', 46, CHAMP, 8), ('on WhatsApp to', 'serif_i', 58, STONE, 0)], gap=18)
    elif key == 'num': v = T('0741 131 420', 'sans', 84, STONE, track=6, shadow=0)
    elif key == 'sig': v = T('BLACKSTONE REAL ESTATE', 'sans', 27, MIST, track=9, shadow=0)
    _L[key] = v
    return v

def hook(im, t, i):
    """behind John's head: visible at frame 0, out before the zoom-out"""
    t_out = 1.50
    if t > t_out + 0.35: return
    vh = L('vh'); who = L('who')
    gh = vh.height - 2 * (18 * 2 + 6 + 4)                      # approx glyph block height inside the padded layer
    bottom = head_top(i) + 58
    cy = bottom - vh.height / 2 + 30
    p = 0.78 + 0.22 * eo(clamp(t / 0.22))                       # nearly complete at frame 0 (thumbnail), settles fast
    sc = 1.0 + 0.03 * clamp(t / 1.5)
    o = eo(clamp((t - t_out) / 0.3))
    v2 = ST.wipe(vh, p)
    if v2 is not None:
        place(im, v2, 540, cy - 24 * o, a=1 - o, blur=o * 10, sc=sc)
    w2 = ST.wipe(who, clamp(0.9 + t / 0.2))
    if w2 is not None:
        place(im, w2, 540, cy - vh.height / 2 - 16 - 24 * o, a=1 - o, blur=o * 10)

def window_frame(im, t):
    """hairline champagne frame + soft shadow around the editorial window once it lands"""
    a = eo(clamp((t - MOVE1 + 0.05) / 0.35)) * (1 - eo(clamp((t - X_IN) / (X_OUT - X_IN))))
    if a <= 0: return
    x, y, w, h = WIN
    fr = R.rrect((int(w) + 2, int(h) + 2), 2, (0, 0, 0, 0), outline=CHAMP + (int(150 * a),), width=1)
    comp(im, fr, x - 1, y - 1)

def label(im, t):
    t_out = X_IN - 0.05
    reveal(im, L('by'), 540, 410, t, 2.30, dur=0.6, t_out=t_out)
    if t >= 2.48:
        a = 1 - eo(clamp((t - t_out) / 0.3))
        rule(im, 540, 470, 90, clamp((t - 2.48) / 0.45), a=a)
    reveal(im, L('bre'), 540, 528, t, 2.58, dur=0.65, t_out=t_out)

def end_card(t):
    im = onyx_bg()
    reveal(im, L('come'), 540, 470, t, TE + 0.10, dur=0.5)
    # hero: wipe in, tracking-like breathe via slow scale
    if t >= TE + 0.30:
        p = eo((t - TE - 0.30) / 0.75)
        v = ST.wipe(L('VH'), p)
        if v is not None: place(im, v, 540, 590 + 14 * (1 - p), a=1.0, sc=1 + 0.02 * clamp((t - TE - 0.3) / 3.5))
    reveal(im, L('nag'), 540, 692, t, TE + 0.70, dur=0.55)
    if t >= TE + 0.95: rule(im, 540, 770, 120, clamp((t - TE - 0.95) / 0.5))
    if t >= TE + 1.15:
        p = eo((t - TE - 1.15) / 0.45)
        place(im, L('fsv'), 540, 860 + 12 * (1 - p), a=p)
    reveal(im, L('send'), 540, 1000, t, TE + 1.60, dur=0.6)
    reveal(im, L('num'), 540, 1098, t, TE + 1.95, dur=0.6)
    if t >= TE + 2.4:
        place(im, L('sig'), 540, 1215, a=eo((t - TE - 2.4) / 0.6))
    s = 1 + 0.02 * clamp((t - TE) / END_LEN)                  # slow push-in of the whole card
    big = im.resize((round(W * s), round(H * s)), Image.BICUBIC)
    ox, oy = (big.width - W) / 2, (big.height - H) * 0.45
    return big.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))

# ---------------------------------------------------------------- frame
def frame(i, src):
    t = i / FPS
    endc = end_card(t) if t >= X_IN else None
    if t >= X_OUT: return endc.convert('RGB')
    v, cover = view(src, t)
    plate = Image.fromarray(v).convert('RGBA')
    bg = onyx_bg()
    # ambient: very dark blurred copy of the picture behind the window (depth, not flat black)
    if t > MOVE0:
        amb = Image.fromarray(cv2.resize(cv2.GaussianBlur(src, (0, 0), 25), (W, H))).convert('RGBA')
        amb = Image.blend(bg, amb, 0.10)
        k = eo(clamp((t - MOVE0) / 0.6)); bg = Image.blend(bg, amb, k)
    pl = plate.copy(); pl.putalpha(Image.fromarray(cover))
    im = bg; im.alpha_composite(pl)
    if t <= MOVE0 + 0.1:
        topshade(im, a=1 - eo(clamp((t - MOVE0 + 0.2) / 0.3)))
        hook(im, t, i)
        if i < NM:
            m = mask(i).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))
            person = plate.copy(); person.putalpha(Image.fromarray(np.minimum(np.array(m), cover)))
            im.alpha_composite(person)
    window_frame(im, t)
    label(im, t)
    if endc is not None:                                       # dark-to-dark dissolve
        k = eio((t - X_IN) / (X_OUT - X_IN))
        im = Image.blend(im.convert('RGBA'), endc.convert('RGBA'), k)
    return im.convert('RGB')

def main(out, only=None):
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', WIDE, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
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
            raw = dec.stdout.read(1920 * 1080 * 3)
            if len(raw) == 1920 * 1080 * 3: last = np.frombuffer(raw, np.uint8).reshape(1080, 1920, 3)
        if only is not None and i not in only: continue
        im = frame(i, last)
        if enc: enc.stdin.write(im.tobytes())
        else: im.save(os.path.join(out, '%05d.jpg' % i), quality=92)
        if i % 30 == 0: print(i, '%.1fs' % (time.time() - t0), flush=True)
    dec.stdout.close(); dec.kill()
    if enc: enc.stdin.close(); enc.wait()
    print('done', NFR, 'frames', '%.0fs' % (time.time() - t0), flush=True)

if __name__ == '__main__':
    if sys.argv[1] == 'masks': make_masks()
    else:
        only = set(int(x) for x in sys.argv[2].split(',')) if len(sys.argv) > 2 else None
        main(sys.argv[1], only)
