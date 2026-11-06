# Shared pieces for videos E (real only) and F (imagined vs real). Palette 3 (Modern Clean) + IBM Plex Mono for record stamps.
import sys, subprocess, math
import numpy as np, cv2
from PIL import Image, ImageOps, ImageDraw, ImageFilter
SC = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts'
sys.path.insert(0, SC)
import styleC as ST
from styleC import R, T, place, comp, clamp, eo, eio, W, H, baseline_line

S = ST.S
MO = S + '/fonts2/montserrat/package/files/montserrat-latin-'
PX = S + '/fonts2/ibm-plex-mono/package/files/ibm-plex-mono-latin-'
R.FN.update({'mo4': MO + '400-normal.woff', 'mo5': MO + '500-normal.woff', 'mo6': MO + '600-normal.woff', 'mo7': MO + '700-normal.woff',
             'px4': PX + '400-normal.woff', 'px5': PX + '500-normal.woff', 'px6': PX + '600-normal.woff'})
OFF, OFF2 = (243, 241, 237), (232, 229, 223)
CHAR, CHAR2 = (30, 30, 30), (44, 42, 39)
SAND, GREY, MIST, WHITE = (176, 146, 104), (110, 106, 100), (140, 136, 130), (255, 255, 255)
FPS = 30
SITE = S + '/site/'
WIDE = S + '/C/wideC.mkv'          # graded lossless John footage (1920x1080, 122 frames)
FILM1 = S + '/ref/film1/film1.mp4'

_c = {}
def radial(c_centre, c_edge, key):
    if key in _c: return _c[key].copy()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H * 0.42) / (H * 0.6)) ** 2)
    k = np.clip(1 - d, 0, 1) ** 1.4
    rgb = np.array(c_edge, np.float32) * (1 - k[..., None]) + np.array(c_centre, np.float32) * k[..., None]
    _c[key] = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert('RGBA')
    return _c[key].copy()

def photo(name):
    key = 'ph:' + name
    if key not in _c:
        _c[key] = ImageOps.exif_transpose(Image.open(SITE + name)).convert('RGB')
    return _c[key]

def fit_crop(img, w, h, cx=0.5, cy=0.5, zoom=1.0):
    """crop img (PIL RGB) to aspect w:h around (cx, cy) with zoom, resize to w x h (area for down, lanczos for up)"""
    iw, ih = img.size
    a = w / h
    if iw / ih > a: ch = ih / zoom; cw = ch * a
    else: cw = iw / zoom; ch = cw / a
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw); y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    arr = np.asarray(img)
    M = np.array([[w / cw, 0, -x0 * w / cw], [0, h / ch, -y0 * h / ch]], np.float32)
    interp = cv2.INTER_AREA if cw > w else cv2.INTER_LANCZOS4
    out = cv2.warpAffine(arr, M, (w, h), flags=interp, borderMode=cv2.BORDER_REFLECT)
    return Image.fromarray(out)

def video_frames(path, ss, dur, w, h, vf_extra=''):
    """decode a segment at 30 fps scaled to w x h (RGB numpy list)"""
    vf = 'fps=30,scale=%d:%d:flags=lanczos%s' % (w, h, vf_extra)
    p = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '%.3f' % ss, '-t', '%.3f' % dur, '-i', path, '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                       capture_output=True, check=True)
    a = np.frombuffer(p.stdout, np.uint8).reshape(-1, h, w, 3)
    return [a[i] for i in range(len(a))]

def wide_frames():
    if 'wide' not in _c:
        p = subprocess.run(['ffmpeg', '-v', 'error', '-i', WIDE, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True)
        a = np.frombuffer(p.stdout, np.uint8).reshape(-1, 1080, 1920, 3); _c['wide'] = a
    return _c['wide']

def rounded(img, r):
    m = Image.new('L', (img.width * 2, img.height * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width * 2 - 1, img.height * 2 - 1), r * 2, fill=255)
    out = img.convert('RGBA'); out.putalpha(m.resize(img.size, Image.LANCZOS)); return out

def soft_shadow(w, h, r, blur=26, a=0.28, dy=22, col=(0, 0, 0)):
    pad = blur * 3
    L = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), col + (0,))
    m = Image.new('L', L.size, 0); ImageDraw.Draw(m).rounded_rectangle((pad, pad + dy, pad + w, pad + h + dy), r, fill=int(255 * a))
    L.putalpha(m.filter(ImageFilter.GaussianBlur(blur))); return L, pad

def pill(txt, font, size, fg, bg, track=6, padx=40, pady=20, alpha=255):
    Lt = T(txt, font, size, fg, track=track, shadow=0)
    g = Lt.getbbox(); w, h = g[2] - g[0] + 2 * padx, g[3] - g[1] + 2 * pady
    P = R.rrect((w, h), h // 2, bg + (alpha,)); comp(P, Lt, (w - Lt.width) / 2, (h - Lt.height) / 2)
    return P

def wipe_mask(w, h, p, soft=0.18, direction=1):
    """horizontal soft wipe: 0..1 alpha across width"""
    x = np.linspace(0, 1, w, dtype=np.float32)
    if direction < 0: x = 1 - x
    a = np.clip((p * (1 + soft) - x) / soft, 0, 1)
    return (np.repeat(a[None, :], h, 0) * 255).astype(np.uint8)
