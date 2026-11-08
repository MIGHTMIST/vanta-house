# Engine for the John interview edits (7 Nov 2026): Ways 1-4.
# Picture: crops that follow John (face track), warm clean grade, Anton graphics + Inter Bold captions (gold keyword).
# Sound: John's voice pieces (pauses > 0.6 s cut), room tone, music under the voice (sidechain), SFX on every graphic in/out, -14 LUFS.
import json, math, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'
SRC = S + '/J/john_full.mp4'
SND = S + '/snd/'
OUT = S + '/IV/'
os.makedirs(OUT, exist_ok=True)
FPS = 30
ANTON = S + '/fonts3/package/files/anton-latin-400-normal.woff'
INTERB = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
GOLD = (217, 179, 108)
WHITE = (255, 255, 255)
GRADE = "eq=contrast=1.04:saturation=1.06:gamma=1.01,colorbalance=rs=0.025:gs=0.008:bs=-0.03:rm=0.02:gm=0.0:bm=-0.025:rh=0.01:bh=-0.015"
WORDS = json.load(open(S + '/J/words.json'))['words']
TOK = [w['w'].lower().strip('.,?!:;"') for w in WORDS]
# what the ASR heard -> what he said
FIX = {'reestate': 'Real Estate', 'van': 'Vanta', 'venthouse': 'Vanta House', 'navuru': 'Naguru', 'interior': 'entire',
       'industries,': 'industry,', 'markets.': 'market.', 'lancet': 'alongside', 'klolu,': 'Kololo,'}

def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def ease(u): u = clamp(u); return u * u * (3 - 2 * u)
def eout(u): u = clamp(u); return 1 - (1 - u) ** 3

# ---------------------------------------------------------------- words / spans
def find(phrase, after=0.0):
    p = phrase.lower().split()
    for i in range(len(TOK)):
        if WORDS[i]['t'] >= after and TOK[i:i + len(p)] == p: return i
    raise ValueError('not found: ' + phrase)

def span(start_phrase, end_phrase, after=0.0, pre=0.10, post=0.14):
    """source (a, b) from the first word of start_phrase to the last word of end_phrase"""
    i = find(start_phrase, after); j = find(end_phrase, WORDS[i]['t']) + len(end_phrase.split()) - 1
    a = WORDS[i]['t'] - pre; b = WORDS[j]['end'] + post
    if i > 0: a = max(a, WORDS[i - 1]['end'] - 0.02)                 # never catch the tail of the word before
    if j + 1 < len(WORDS): b = min(b, WORDS[j + 1]['t'] + 0.02)      # ... or the start of the next one
    # trim silence after the last word (ASR stretches it to the next word): end where the sound goes quiet
    db = _db(); d = _est(WORDS[j]['w']); lo = int((WORDS[j]['t'] + 0.6 * d) * 100); seg = db[lo:int(b * 100)]
    q = np.where(seg < -62)[0]
    if len(q) and (lo + q[0]) / 100 + 0.12 < b: b = (lo + q[0]) / 100 + 0.12
    return (a, b)

_DB = None
def _db():
    global _DB
    if _DB is None:
        import soundfile as sf
        x, sr = sf.read(S + '/J/john16k.wav', dtype='float32'); hop = sr // 100
        e = np.sqrt(np.convolve(x ** 2, np.ones(hop * 2) / (hop * 2), 'same')[::hop] + 1e-9); _DB = 20 * np.log10(e)
    return _DB

def _est(w):
    import re
    return 0.12 + 0.072 * len(re.sub('[^a-z0-9]', '', w.lower()))

def pieces(a, b, maxgap=0.35, keep=0.07):
    """split a source span to remove 'um's, 'uh's and pauses: wherever a word's slot (its start to the next word's start)
    is longer than the word should take + maxgap, cut the excess (silent pause or voiced filler) and keep a short breath"""
    db = _db(); ws = [w for w in WORDS if a - 0.05 <= w['t'] < b]
    out = []; s = a
    for w0, w1 in zip(ws, ws[1:]):
        d = _est(w0['w']); slot = w1['t'] - w0['t']
        if slot > d + maxgap:
            lo, hi = int((w0['t'] + 0.6 * d) * 100), int((w0['t'] + d + 0.35) * 100)
            seg = db[lo:hi]; quiet = np.where(seg < -62)[0]
            cut0 = (lo + quiet[0]) / 100 + 0.04 if len(quiet) else w0['t'] + d + 0.06     # true end of the word if it goes quiet
            cut0 = min(cut0, w1['t'] - 0.1)
            out.append((s, cut0 + keep)); s = w1['t'] - 0.05
    out.append((s, b))
    return [(x, y) for x, y in out if y - x > 0.12]

# ---------------------------------------------------------------- framing
def face(who, t):
    """(cx, cy, face_w) in source pixels; from the face track medians per section"""
    if isinstance(who, tuple): return who
    if who == 'host': return (1700, 470, 270) if t < 470 else (888, 360, 264)
    if t < 470: return (440, 462, 245)          # wide two-shot, John left
    if t < 570: return (850, 446, 286)          # medium close of John
    if t < 622: return (888, 360, 264)          # host alone (outro)
    return (980, 400, 260)                      # John closing line

def crop(who, t, z, OW, OH, top=0.36):
    cx, cy, fw = face(who, t)
    ar = OW / OH
    ch = (1080 if 1920 / ar >= 1080 else 1920 / ar) / z; cw = ch * ar
    if who == 'full': return ((1920 - cw) / 2, (1080 - ch) / 2, cw, ch)
    x0 = clamp(cx - cw / 2, 0, 1920 - cw); y0 = clamp(cy - top * ch, 0, 1080 - ch)
    return (x0, y0, cw, ch)

class Reader:
    def __init__(self, a, dur, rate=1.0, path=None, grade=None):
        g = grade or GRADE
        vf = g + ',scale=1920:1080,fps=30'
        if rate != 1.0: vf = g + ',scale=1920:1080,setpts=%.4f*PTS,fps=30' % (1 / rate)
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', '%.3f' % a, '-t', '%.3f' % (dur / rate + 0.5), '-stream_loop', '-1', '-i', path or SRC, '-an', '-vf', vf,
                                   '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        self.last = None
    def get(self):
        b = self.p.stdout.read(1920 * 1080 * 3)
        if len(b) == 1920 * 1080 * 3: self.last = np.frombuffer(b, np.uint8).reshape(1080, 1920, 3)
        return self.last
    def close(self):
        try: self.p.stdout.close(); self.p.kill()
        except Exception: pass

def warp(img, rect, OW, OH):
    x0, y0, cw, ch = rect; s = OW / cw
    M = np.array([[s, 0, -x0 * s], [0, s, -y0 * s]], np.float32)
    out = cv2.warpAffine(img, M, (OW, OH), flags=cv2.INTER_LANCZOS4 if s > 1 else cv2.INTER_AREA, borderMode=cv2.BORDER_REFLECT)
    if s > 1.25:                                   # gentle sharpen after enlarging
        bl = cv2.GaussianBlur(out, (0, 0), 1.1); out = cv2.addWeighted(out, 1.35, bl, -0.35, 0)
    return out

# ---------------------------------------------------------------- text
_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]

def text_layer(parts, size, path, shadow=0.55, blur=10, track=0):
    """parts: [(text, colour)] on one line -> RGBA layer with soft shadow"""
    F = font(path, size); pad = 40
    ws = [F.getbbox(t)[2] - F.getbbox(t)[0] for t, c in parts]; sp = F.getbbox(' ')[2] if len(parts) > 1 else 0
    asc, desc = F.getmetrics(); w = sum(ws) + sp * (len(parts) - 1) + 2 * pad; h = asc + desc + 2 * pad
    L = Image.new('RGBA', (w, h), (0, 0, 0, 0)); sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(L); ds = ImageDraw.Draw(sh); x = pad
    for (t, c), wi in zip(parts, ws):
        ds.text((x - F.getbbox(t)[0], pad + 3), t, font=F, fill=(0, 0, 0, int(255 * shadow)))
        d.text((x - F.getbbox(t)[0], pad), t, font=F, fill=c + (255,)); x += wi + sp
    sh = sh.filter(ImageFilter.GaussianBlur(blur)); sh.alpha_composite(L); return sh

def place(fr, L, cx, cy, a=1.0, sc=1.0):
    if a <= 0.003: return
    if sc != 1.0: L = L.resize((max(1, int(L.width * sc)), max(1, int(L.height * sc))), Image.BICUBIC)
    if a < 0.999: L = L.copy(); L.putalpha(L.getchannel('A').point(lambda v: int(v * a)))
    fr.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))

# ---------------------------------------------------------------- captions
PROPER = {'i', 'blackstone', 'uganda', "uganda's", 'ugandan', 'ugandans', 'vanta', 'house', 'naguru', 'kampala', 'africa', "africa's", 'african', "china's", 'china', 'east', 'real', 'estate', 'ceo', 'john', 'kololo'}

def cap_chunks(voice, keywords, maxw=4, maxc=22):
    """voice: [(src_a, src_b, t_out)] -> [(t0, t1, [(word, is_kw)])], 2-4 words, break at punctuation/pauses"""
    out = []; prev_end = True
    kws = [k.lower() for k in keywords]
    for a, b, t0 in voice:
        ws = [w for w in WORDS if a - 0.03 <= w['t'] < b - 0.05]
        nxt_w = {id(w0): w1['w'] for w0, w1 in zip(ws, ws[1:])}; prev_core = {id(w1): w0['w'].lower() == 'core' for w0, w1 in zip(ws, ws[1:])}
        cur = []
        def flush():
            if cur:
                s = t0 + cur[0]['t'] - a; e = t0 + cur[-1]['end'] - a
                out.append([s, e, [(x['txt'], x['kw']) for x in cur], [t0 + x['t'] - a for x in cur]])   # 4th: word start times (kit word-pop captions)
        for w in ws:
            raw = w['w']; core = raw.rstrip('.,?!'); tail = raw[len(core):]
            txt = FIX.get(raw.lower(), None) or (FIX[core.lower()] + tail if core.lower() in FIX else raw)
            if raw.lower() == 'van' or raw.lower().startswith('venthouse'): txt = 'Vanta'
            if raw.lower() == 'core' and nxt_w.get(id(w), '').lower().startswith('investment'): txt = 'co-'
            if raw.lower().startswith('investment') and prev_core.get(id(w)): txt = 'investment' + raw[len('investment'):]; cur[-1]['txt'] = 'co-' + txt; continue
            kw = any(k in txt.lower().strip('.,?!') for k in kws if k)
            if cur and (len(cur) >= maxw or sum(len(x['txt']) + 1 for x in cur) + len(txt) > maxc or w['t'] - cur[-1]['end'] > 0.35):
                flush(); cur = []
            if txt == 'i': txt = 'I'
            if prev_end:
                txt = txt[:1].upper() + txt[1:]
            elif txt[:1].isupper() and txt.strip('.,?!').lower() not in PROPER:
                txt = txt[:1].lower() + txt[1:]
            prev_end = raw[-1] in '.?!'
            cur.append(dict(txt=txt, kw=kw, t=w['t'], end=w['end']))
            if raw[-1] in '.,?!': flush(); cur = []
        flush()
    for i in range(len(out) - 1):                       # hold each chunk until the next one (no flicker)
        if out[i + 1][0] - out[i][1] < 0.6: out[i][1] = out[i + 1][0]
    return out

def cap_layer(words, size, box=False):
    parts = []
    for i, (w, kw) in enumerate(words):
        parts.append((w, GOLD if kw else WHITE))
    L = text_layer(parts, size, INTERB, shadow=0.0 if box else 0.75, blur=9)
    if box:
        bb = L.getbbox(); pad = 22
        B = Image.new('RGBA', L.size, (0, 0, 0, 0)); d = ImageDraw.Draw(B)
        d.rounded_rectangle((bb[0] - pad, bb[1] - pad * 0.6, bb[2] + pad, bb[3] + pad * 0.6), 14, fill=(12, 12, 14, 175))
        B.alpha_composite(L); return B
    return L

# ---------------------------------------------------------------- graphics (Anton), each eases in and out
def graphic_draw(fr, g, t):
    t_in, t_out = g['t'], g['t'] + g['dur']; D = 0.35
    if t < t_in or t > t_out: return
    u_in = eout((t - t_in) / D); u_out = 1 - ease((t - (t_out - D)) / D)
    a = min(u_in, u_out); sc = 0.9 + 0.1 * min(u_in, 1.0); dy = (1 - min(u_in, u_out)) * 26
    if 'L' not in g:
        if g.get('kind') == 'sub':     # small Anton line (lower third second line / labels)
            g['L'] = text_layer([(g['text'], g.get('col', WHITE))], g.get('size', 44), ANTON, shadow=0.6, blur=8)
        else:
            g['L'] = text_layer([(g['text'], g.get('col', WHITE))], g.get('size', 150), ANTON, shadow=0.55, blur=14)
    place(fr, g['L'], g['x'], g['y'] + dy, a=a, sc=sc)
    if g.get('bar'):                    # thin gold bar under the word
        bw = int(min(g['L'].width - 80, 260) * a);
        if bw > 4:
            d = ImageDraw.Draw(fr); y = int(g['y'] + g['L'].height / 2 - 30 + dy)
            d.rounded_rectangle((g['x'] - bw / 2, y, g['x'] + bw / 2, y + 6), 3, fill=GOLD + (int(255 * a),))

def graphic_sfx(g, sin='pop_soft', sout='whoosh_cinematic_5', gin=-6, gout=-12):
    return [(g.get('sfx_in', sin), g['t'] - 0.02, g.get('g_in', gin)), (g.get('sfx_out', sout), g['t'] + g['dur'] - 0.35, g.get('g_out', gout))]

_cache = {}
# ---------------------------------------------------------------- render picture
def render_video(name, OW, OH, pics, graphics, caps, dur, extra=None, cap_y=None, cap_size=54, fxs=None, cap_box=False):
    """pics: [dict(t, dur, src, who, z0, z1, kind='src'|'card'|'photo', ...)] later entries win"""
    path = OUT + name + '_v.mkv'
    if os.environ.get('REUSE') and os.path.exists(path) and os.path.getsize(path) > 1e6: return path
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (OW, OH), '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-crf', '9', '-preset', 'veryfast', '-pix_fmt', 'yuv444p', path], stdin=subprocess.PIPE)
    readers = {}; NF = int(round(dur * FPS)); cap_y = cap_y or int(OH * 0.77)
    capL = {}
    for i in range(NF):
        t = i / FPS
        act = [p for p in pics if p['t'] - 1e-6 <= t < p['t'] + p['dur'] - 1e-6]
        for k, p in enumerate(pics):                      # advance every live source reader so frames stay in sync
            if p.get('kind', 'src') in ('src', 'clip') and p['t'] - 1e-6 <= t < p['t'] + p['dur'] - 1e-6:
                if id(p) not in readers: readers[id(p)] = Reader(p['src'], p['dur'], p.get('rate', 1.0), p.get('path'), p.get('grade'))
                p['_f'] = readers[id(p)].get()
            elif id(p) in readers and t >= p['t'] + p['dur'] - 1e-6:
                readers.pop(id(p)).close()
        p = act[-1] if act else pics[-1]; tl = clamp((t - p['t']) / max(p['dur'], 0.01))
        kind = p.get('kind', 'src')
        if kind == 'src':
            z = p.get('z0', 1.0) + (p.get('z1', p.get('z0', 1.0)) - p.get('z0', 1.0)) * ease(tl)
            img = warp(p['_f'], crop(p.get('who', 'john'), p['src'] + t - p['t'], z, OW, OH, p.get('top', 0.36)), OW, OH)
        elif kind == 'clip':
            z = p.get('z0', 1.0) + (p.get('z1', 1.06) - p.get('z0', 1.0)) * ease(tl)
            ch = 1080 / z; cw = ch * OW / OH
            if cw > 1920: cw = 1920 / z; ch = cw * OH / OW
            img = warp(p['_f'], ((1920 - cw) * p.get('cx', 0.5), (1080 - ch) * p.get('cy', 0.5), cw, ch), OW, OH)
        elif kind == 'photo':
            if '_im' not in p:
                im = Image.open(p['path']).convert('RGB'); im = np.asarray(im); f = max(OW / im.shape[1], OH / im.shape[0]) * 1.12
                p['_im'] = cv2.resize(im, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
            im = p['_im']; z = p.get('z0', 1.0) + (p.get('z1', 1.06) - p.get('z0', 1.0)) * ease(tl)
            ch = OH / z; cw = OW / z                       # image is pre-sized 1.12x the frame: 1:1 at z=1, room to drift
            img = warp(im, ((im.shape[1] - cw) * p.get('cx', 0.5), (im.shape[0] - ch) * p.get('cy', 0.5), cw, ch), OW, OH)
        else:                                               # full-screen card
            img = np.full((OH, OW, 3), p.get('bg', (16, 16, 17)), np.uint8)
        if p.get('tint') is not None and kind in ('photo', 'clip'):
            img = np.clip(img.astype(np.float32) * np.array(p['tint'], np.float32)[None, None, :] + p.get('lift', 0), 0, 255).astype(np.uint8)
        if OH > OW * 1.2 and kind != 'card':           # soft dark shade low in the frame so captions read on the bright desk
            if ('_band', OH) not in _cache:
                yy = np.arange(OH, dtype=np.float32)[:, None, None]
                _cache[('_band', OH)] = 1 - 0.58 * np.clip((yy - OH * 0.66) / (OH * 0.16), 0, 1) ** 1.2 * np.clip((OH * 0.97 - yy) / (OH * 0.08), 0.35, 1)
            img = (img.astype(np.float32) * _cache[('_band', OH)]).astype(np.uint8)
        for fx in (fxs or []):
            if fx['t'] <= t < fx['t'] + fx['dur']:
                if id(fx) not in readers: readers[id(fx)] = Reader(fx.get('start', 0), fx['dur'], 1.0, fx['path'], 'null')
                ov = readers[id(fx)].get()
                if ov is not None:
                    tl2 = (t - fx['t']) / fx['dur']; a = fx.get('alpha', 0.8) * min(1, tl2 / 0.25, (1 - tl2) / 0.25)
                    ov = cv2.resize(ov, (OW, OH), interpolation=cv2.INTER_AREA) if OW / OH < 1 else cv2.resize(ov, (OW, OH))
                    base = img.astype(np.float32); o = ov.astype(np.float32) * a
                    img = (255 - (255 - base) * (255 - o) / 255).astype(np.uint8)
            elif id(fx) in readers and t >= fx['t'] + fx['dur']:
                readers.pop(id(fx)).close()
        fr = None
        gs = [g for g in graphics if g['t'] - 0.01 <= t <= g['t'] + g['dur'] + 0.01]
        cs = [c for c in caps if c[0] <= t < c[1]] if not p.get('nocap') else []
        if gs or cs or kind == 'card' or extra:
            fr = Image.fromarray(img).convert('RGBA')
            if kind == 'card' and p.get('draw'): p['draw'](fr, t - p['t'], p)
            for g in gs: graphic_draw(fr, g, t)
            for c in cs:
                k = id(c)
                if k not in capL: capL[k] = cap_layer(c[2], cap_size, box=cap_box)
                fa = min(1.0, (t - c[0]) / 0.08)
                place(fr, capL[k], OW / 2, cap_y, a=fa)
            if extra: extra(fr, t)
            img = np.asarray(fr.convert('RGB'))
        enc.stdin.write(np.ascontiguousarray(img).tobytes())
    for r in readers.values(): r.close()
    enc.stdin.close(); enc.wait(); return path

# ---------------------------------------------------------------- sound
def lufs(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    v = [l for l in r.split('\n') if l.strip().startswith('I:')]
    return float(v[-1].split()[1]) if v else -70.0

VOICE = 'highpass=f=75,lowpass=f=13000,afftdn=nf=-30:nr=8,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.0:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3'

def render_audio(name, voice, sfx, music, dur, music_db_under=19.0, swells=(), room=True, smooth=False, lift=(), lift_db=6.0):
    W = OUT + name + '_'
    segs = []
    for k, (a, b, t0) in enumerate(voice):
        f = W + 'vo%02d.wav' % k
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '%.3f' % a, '-t', '%.3f' % (b - a), '-i', SRC, '-vn', '-af',
                        'aresample=48000,aformat=channel_layouts=stereo,%s,afade=t=in:d=0.025,afade=t=out:st=%.3f:d=0.05,adelay=%d|%d'
                        % (VOICE, max(0, b - a - 0.05), int(t0 * 1000), int(t0 * 1000)), f], check=True)
        segs.append(f)
    vo = W + 'voice.wav'
    inp = sum((['-i', f] for f in segs), [])
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ''.join('[%d:a]' % i for i in range(len(segs))) +
                    'amix=inputs=%d:normalize=0:duration=longest,apad=whole_dur=%.3f,atrim=0:%.3f[o]' % (len(segs), dur, dur), '-map', '[o]', vo], check=True)
    vl = lufs(vo)
    # music: loop to length, level it ~music_db_under below the voice, sidechain duck so it breathes up only in the gaps
    mus = W + 'music.wav'
    sw = '+'.join("%.2f*exp(-((t-%.2f)/%.2f)*((t-%.2f)/%.2f))" % (g, c, w, c, w) for c, w, g in swells) or '0'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-stream_loop', '-1', '-i', SND + music, '-t', '%.3f' % dur, '-af',
                    'aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=1.2,afade=t=out:st=%.3f:d=2.0,volume=eval=frame:volume=1+%s' % (max(0, dur - 2.0), sw),
                    mus], check=True)
    ml = lufs(mus); g_m = (vl - music_db_under) - ml
    if smooth:   # steady bed under the voice, rising gently (0.3 s ramps) where he is not talking (cards) - no pumping
        k = 10 ** (lift_db / 20) - 1
        env = '+'.join("%.3f*min(1,max(0,min((t-%.2f)/0.3,(%.2f-t)/0.3)))" % (k, a0, b0) for a0, b0 in lift) or '0'
        env = env.replace(',', '\\,')
        parts = [vo, mus]; fl = ['[0:a]anull[v1]', '[1:a]volume=%.2fdB,volume=eval=frame:volume=1+%s[md]' % (g_m, env)]
    else:
        parts = [vo, mus]; fl = ['[0:a]asplit=2[v1][vk]', '[1:a]volume=%.2fdB[m0]' % g_m, '[m0][vk]sidechaincompress=threshold=0.03:ratio=4:attack=60:release=500:makeup=1[md]']
    mixin = ['[v1]', '[md]']; n = 2
    if room:
        parts.append(SND + 'room_tone_office_v2.mp3'); fl.append('[%d:a]aresample=48000,aformat=channel_layouts=stereo,aloop=loop=-1:size=2000000,atrim=0:%.3f,volume=%.2fdB[rt]' % (n, dur, vl - 24 - lufs(SND + 'room_tone_office_v2.mp3')))
        mixin.append('[rt]'); n += 1
    for nm, t, gdb in sfx:
        parts.append(SND + nm + '.mp3')
        fl.append('[%d:a]aresample=48000,aformat=channel_layouts=stereo,volume=%.1fdB,adelay=%d|%d[s%d]' % (n, gdb, int(max(0, t) * 1000), int(max(0, t) * 1000), n))
        mixin.append('[s%d]' % n); n += 1
    fl.append(''.join(mixin) + 'amix=inputs=%d:normalize=0:duration=first,atrim=0:%.3f[mx]' % (len(mixin), dur))
    pre = W + 'pre.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + sum((['-i', p] for p in parts), []) + ['-filter_complex', ';'.join(fl), '-map', '[mx]', '-c:a', 'pcm_s24le', pre], check=True)
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', pre, '-af', 'loudnorm=I=-14:TP=-2.0:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    j = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
    af = 'loudnorm=I=-14:TP=-2.0:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true,aresample=48000' % (
        j['input_i'], j['input_tp'], j['input_lra'], j['input_thresh'], j['target_offset'])
    fin = W + 'mix.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', pre, '-af', af, '-c:a', 'pcm_s24le', fin], check=True)
    print(name, 'voice %.1f LUFS, music %.1f dB under, final %.1f' % (vl, music_db_under, lufs(fin)))
    return fin

def encode(name, vpath, apath, label, crf=16, small=True):
    hq = S + '/out/%s_HQ.mp4' % label
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vpath, '-i', apath, '-map', '0:v', '-map', '1:a', '-vf',
                    'scale=out_color_matrix=bt709:out_range=tv:flags=lanczos+accurate_rnd+full_chroma_int,format=yuv420p',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-tune', 'film', '-profile:v', 'high', '-g', '30', '-r', '30',
                    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
                    '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', '-movflags', '+faststart', hq], check=True)
    return hq

# ---------------------------------------------------------------- end card (CTA on hold): VANTA HOUSE / Naguru, Kampala
CREDIT = 'Sounds: Oculus Audio Pack 01 by Oculus VR, LLC, CC BY 4.0'
def end_card_draw(fr, tl, p):
    OW, OH = fr.size
    if 'L' not in p:
        p['L'] = text_layer([('VANTA HOUSE', WHITE)], int(OW * 0.15), ANTON, shadow=0.4, blur=12)
        p['L2'] = text_layer([('Naguru, Kampala', GOLD)], int(OW * 0.052), INTERB, shadow=0.4, blur=8)
        p['L3'] = text_layer([(CREDIT, (150, 150, 150))], int(OW * 0.018), INTERB, shadow=0.0, blur=1)
    u = eout(tl / 0.45); u2 = eout((tl - 0.25) / 0.45)
    place(fr, p['L'], OW / 2, OH * 0.46 + (1 - u) * 24, a=u, sc=0.94 + 0.06 * u + 0.012 * tl)   # slow push, never still
    place(fr, p['L2'], OW / 2, OH * 0.46 + p['L'].height * 0.5 + 10 + (1 - u2) * 18 + 2.5 * tl, a=u2, sc=1 + 0.01 * tl)
    place(fr, p['L3'], OW / 2, OH * 0.95, a=min(u2, 0.9))
