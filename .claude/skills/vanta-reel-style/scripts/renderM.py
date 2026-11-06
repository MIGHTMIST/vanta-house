# Video M: a longer cousin of MyEdit_B_own (the 4 s slow glide the client liked).
# Same look: slow-motion glide, cinematic grade, vignette, grain, bottom gradient, teal bar, Inter two-line titles, ambient pad.
# Three shots: John at his desk (new cutaway, slowed) -> real site slab -> rebar + skyline, ends on VANTA HOUSE / NAGURU, KAMPALA.
import sys, subprocess, math
import numpy as np, cv2
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter

S = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'
D = S + '/M/'
W, H, FPS = 1080, 1920, 30
L, X = 4.3, 0.5                       # shot length, crossfade
STARTS = [0, L - X, 2 * (L - X)]
DUR = 3 * L - 2 * X                   # 11.9 s
FB = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
FM = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'
TEAL = (0x2E, 0xC4, 0xB6)

def ss(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)

def enc_pipe(path, w=W, h=H, pix='rgb24'):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', pix, '-s', '%dx%d' % (w, h), '-r', str(FPS), '-i', '-',
                             '-c:v', 'ffv1', '-level', '3', path], stdin=subprocess.PIPE)

def warp(img, cx, cy, ch):
    """crop a 9:16 window of height ch (source px) centred at (cx, cy), scaled to W x H, sub-pixel smooth"""
    cw = ch * W / H; s = H / ch
    x0 = cx - cw / 2; y0 = cy - ch / 2
    M = np.array([[s, 0, -x0 * s], [0, s, -y0 * s]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

def shot_john():
    # cutaway 10.90-12.73 in the B2 clip (wide, John at desk); slowed 2.4x with motion interpolation + gentle push-in
    vf = 'minterpolate=fps=72:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,setpts=2.4*PTS,fps=30'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', '10.92', '-t', '1.79', '-i', S + '/H/src2.mp4', '-an', '-vf', vf,
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    out = enc_pipe(D + 'm1.mkv'); n = int(round(L * FPS)); last = None
    for i in range(n):
        b = p.stdout.read(W * H * 3)
        if len(b) == W * H * 3: last = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        u = ss(i / (n - 1)); z = 1.0 + 0.07 * u
        ch = H / z
        out.stdin.write(warp(last, W / 2 + 18 * u, H * 0.47, ch).tobytes())
    p.stdout.close(); p.wait(); out.stdin.close(); out.wait()

def still(name, zmax):
    im = np.asarray(ImageOps.exif_transpose(Image.open(S + '/site/mmexport1792497' + name + '.jpg')).convert('RGB'))
    f = H / im.shape[0] * zmax                         # pre-shrink with area filter so the move never downsamples hard (no shimmer on rebar)
    return cv2.resize(im, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)

def shot_still(name, path, z0, z1, cx0, cx1, cy):
    im = still(name, z1); ih, iw = im.shape[:2]
    out = enc_pipe(path); n = int(round(L * FPS))
    for i in range(n):
        u = ss(0.08 + 0.92 * i / (n - 1)) if False else ss(i / (n - 1))
        z = z0 + (z1 - z0) * u; ch = ih / z; cw = ch * W / H
        cx = (cx0 + (cx1 - cx0) * u) * iw; cx = min(max(cx, cw / 2), iw - cw / 2)
        out.stdin.write(warp(im, cx, cy * ih, ch).tobytes())
    out.stdin.close(); out.wait()

# ---------- titles overlay (RGBA) ----------
TITLES = [  # (t_in, t_out or None, line1, size1, line2)
    (0.60, 3.45, '10 YEARS IN BANKING', 80, 'NOW BUILDING IN KAMPALA'),
    (STARTS[1] + 0.55, STARTS[1] + 3.45, '100 BOUTIQUE HOMES', 80, 'RISING IN NAGURU'),
    (STARTS[2] + 0.70, None, 'VANTA HOUSE', 104, 'NAGURU, KAMPALA'),
]

def text_layer(txt, font, size, col):
    F = ImageFont.truetype(font, size); bb = F.getbbox(txt)
    w, h = bb[2] - bb[0] + 40, bb[3] + 40
    t = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(t).text((20 - bb[0], 20), txt, font=F, fill=col)
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((20 - bb[0], 23), txt, font=F, fill=(0, 0, 0, 95))
    sh = sh.filter(ImageFilter.GaussianBlur(3)); sh.alpha_composite(t)
    return sh, bb[1]

def overlay():
    yy = np.arange(H, dtype=np.float32)
    g = np.where(yy < 980, 0, 215 * np.clip((yy - 980) / 940, 0, 1) ** 0.9).astype(np.float32)
    grad = np.zeros((H, W, 4), np.float32); grad[..., 3] = g[:, None]
    layers = []
    for (tin, tout, l1, s1, l2) in TITLES:
        a, top1 = text_layer(l1, FB, s1, (255, 255, 255, 255))
        b, top2 = text_layer(l2, FM, 46, (255, 255, 255, 236))
        layers.append((tin, tout, a, top1, b, top2, s1))
    out = enc_pipe(D + 'ov.mkv', pix='rgba'); n = int(round(DUR * FPS))
    for i in range(n):
        t = i / FPS
        fr = Image.fromarray(grad.astype(np.uint8), 'RGBA')
        for (tin, tout, a, top1, b, top2, s1) in layers:
            fo = 1.0 if tout is None else 1 - ss((t - tout) / 0.35)
            if t < tin - 0.05 or fo <= 0: continue
            p1 = ss((t - tin) / 0.5); p2 = ss((t - tin - 0.25) / 0.5)
            y1 = 1300 - top1 - 20                     # cap top of line 1 at y=1300
            y2 = 1300 + int(s1 * 0.73) + 46 - top2 - 20
            bar = Image.new('RGBA', (96, 6), TEAL + (int(255 * p1 * fo),)); fr.alpha_composite(bar, ((W - 96) // 2, 1268))
            for L_, p, y in ((a, p1, y1), (b, p2, y2)):
                if p <= 0: continue
                l = L_.copy(); l.putalpha(l.getchannel('A').point(lambda v, k=p * fo: int(v * k)))
                fr.alpha_composite(l, ((W - l.width) // 2, int(y + 26 * (1 - p) ** 2)))
        out.stdin.write(fr.tobytes())
    out.stdin.close(); out.wait()

# ---------- ambient score (numpy) ----------
def score():
    sr = 48000; n = int(DUR * sr); t = np.arange(n) / sr
    chords = [[110.0, 164.81, 220.0, 261.63, 493.88],          # Am(add9)
              [87.31, 130.81, 220.0, 329.63, 392.0],            # Fmaj7
              [65.41, 130.81, 196.0, 329.63, 587.33]]           # C(add9) - lands on the title
    L_ = np.zeros((2, n))
    for k, ch in enumerate(chords):
        a = STARTS[k] - (0.0 if k == 0 else 0.3); b = (STARTS[k] + L + 0.3) if k < 2 else DUR
        env = np.clip((t - a) / 1.1, 0, 1) * (np.clip((b - t) / 0.9, 0, 1) if k < 2 else np.clip((DUR - t) / 1.4, 0, 1))
        env = env ** 1.5
        for j, f in enumerate(ch):
            amp = [1, .8, .6, .45, .22][j]
            for c, det in enumerate((-0.18, 0.21)):
                L_[c] += amp * env * (np.sin(2 * np.pi * (f + det) * t) + 0.5 * np.sin(2 * np.pi * (f * 1.003 - det) * t + c))
    L_ *= 0.045 * (0.82 + 0.18 * np.sin(2 * np.pi * 0.4 * t))[None]
    # whoosh swells into each cut
    rng = np.random.default_rng(7); nz = rng.standard_normal((2, n))
    nz = np.cumsum(nz, axis=1); nz -= cv2.blur(nz.astype(np.float32), (401, 1)).astype(np.float64)   # crude pink-ish, DC removed
    nz /= np.abs(nz).max()
    for c in STARTS[1:]:
        e = np.exp(-((t - c - 0.2) / 0.38) ** 2); L_ += 0.18 * e * nz
    # soft low hit under the final title
    tt = t - (STARTS[2] + 0.7); hit = np.where(tt > 0, np.sin(2 * np.pi * 46 * tt) * np.exp(-tt / 0.9) * np.clip(tt / 0.02, 0, 1), 0)
    L_ += 0.35 * hit
    x = (np.clip(L_.T, -1, 1) * 32767).astype(np.int16)
    import wave
    w = wave.open(D + 'score_raw.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(x.tobytes()); w.close()

if __name__ == '__main__':
    import os; os.makedirs(D, exist_ok=True)
    what = sys.argv[1:] or ['plates', 'ov', 'score']
    if 'plates' in what:
        if 'nojohn' not in what: shot_john()
        shot_still('982990', D + 'm2.mkv', 1.00, 1.05, 0.34, 0.62, 0.55)    # slab + workers, slow pan right
        shot_still('989322', D + 'm3.mkv', 1.00, 1.12, 0.40, 0.44, 0.50)    # rebar + skyline, slow push-in
    if 'ov' in what: overlay()
    if 'score' in what: score()
