# Openings A/B/C, version 3 = v2 with the MyEdit_B / video M type and colours (Inter, white, teal bar, bottom gradient).
# Version 2 (owner, 4 Nov): real cutaways from the B2 clip, Sarah's voice lines (no WhatsApp part),
# floor plans from the website pack, and every video ends on just "VANTA HOUSE / Naguru, Kampala".
import sys, os, json, subprocess, time
import numpy as np
from PIL import Image
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
_argv = sys.argv; sys.argv = [sys.argv[0], 'masks']
import renderABC as RA
sys.argv = _argv
from docs_common import *
IN = '/usr/share/fonts/opentype/inter/Inter-'
R.FN.update({'mo4': IN + 'Regular.otf', 'mo5': IN + 'Medium.otf', 'mo6': IN + 'Bold.otf', 'mo7': IN + 'ExtraBold.otf',
             'px4': IN + 'Medium.otf', 'px5': IN + 'Medium.otf', 'px6': IN + 'SemiBold.otf'})
TEAL = (0x2E, 0xC4, 0xB6)
def barred(Lt, gap=22):
    """video M title style: short teal bar centred above the text"""
    out = Image.new('RGBA', (max(Lt.width, 96), Lt.height + 6 + gap), (0, 0, 0, 0))
    out.paste(Image.new('RGBA', (96, 6), TEAL + (255,)), ((out.width - 96) // 2, 0))
    out.alpha_composite(Lt, ((out.width - Lt.width) // 2, 6 + gap)); return out
_yy = np.arange(H, dtype=np.float32)
_g = np.where(_yy < 980, 0, 215 * np.clip((_yy - 980) / 940, 0, 1) ** 0.9).astype(np.uint8)
GRAD = Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8), np.repeat(_g[:, None], W, 1)]), 'RGBA')
DARK = ((40, 42, 44), (10, 10, 11))
SRC, SRC2 = RA.SRC, RA.SRC2
SAR = S + '/sarah/vanta_reel_r%d_voice.mp3'
SW = {n: json.load(open(S + '/sarah/vanta_reel_r%d_voice.json' % n))['words'] for n in (1, 2, 8)}
john, cut = RA.john, RA.cut
HOOK = RA.HOOK

def sar(n, a, b, t):           # an audio entry from Sarah's clip n
    return (a, b, t, SAR % n, n)
def jv(a, b, t):               # an audio entry from John
    return (a, b, t, SRC, 0)
# caption chunks: John (word index in RA.WORDS) and Sarah (first word text, chunk text) per clip
SCH = {1: [("Don't", "Don't buy a home"), ('from', 'from a picture.'), ('Ask', 'Ask to see the site.'), ('This', 'This is Vanta House'),
           ('going', 'going up right now.'), ('Real', 'Real workers,'), ('real#2', 'real steel,'), ('real#3', 'real concrete.'),
           ('hundred', 'A hundred homes'), ('expected', 'expected to be ready'), ('in', 'in October 2027.')],
       2: [('Now', 'Now they are building'), ('100', '100 boutique homes here.')],
       8: [('Built', 'Built for those'), ('who', 'who want a refined address'), ('above', 'above the city.')]}

def build(name):
    if name == 'A':
        shots = [cut(10.90, 12.73, 0.0), cut(16.40, 17.33, 1.83), cut(4.13, 6.30, 2.76)]; audio = []
        t = 4.93
        for (a, b), z in zip(HOOK, (1.40, 1.58)):
            shots.append(john(a, b, t, z)); audio.append(jv(a, b, t)); t += b - a
        jc = t; audio.append(jv(25.80, 39.40, jc))
        shots += [dict(kind='photo', name='mmexport1792497989322.jpg', t=jc, dur=1.15, z0=1.0, z1=1.10),
                  dict(kind='photo', name='mmexport1792497982990.jpg', t=jc + 1.15, dur=1.15, z0=1.08, z1=1.0), john(25.80 + 2.30, 39.40, jc + 2.30, 1.0)]
        s0 = jc + 13.60 + 0.24; audio.append(sar(8, 5.10, 11.25, s0))
        v = s0 + (8.64 - 5.10) - 0.08                        # "Vanta House, in Naguru, Kampala." -> end card
        shots += [dict(kind='plan', img='p3d_1br', lab='1 BEDROOM', t=s0, dur=1.15), dict(kind='plan', img='p3d_2br', lab='2 BEDROOMS', t=s0 + 1.15, dur=1.15),
                  dict(kind='plan', img='p3d_3br', lab='3 BEDROOMS', t=s0 + 2.30, dur=v - s0 - 2.30), dict(kind='vend', dark=True, t=v, dur=3.6)]
        return dict(shots=shots, audio=audio, dur=v + 3.6, end=v, trend=4.93)
    if name == 'B':
        shots = []; audio = []; t = 0.0
        for (a, b), z in zip(HOOK, (1.55, 1.75)):
            shots.append(john(a, b, t, z)); audio.append(jv(a, b, t)); t += b - a
        sil = t; shots.append(dict(kind='black', t=sil, dur=1.0)); t2 = sil + 1.0
        shots.append(john(25.80, 39.40, t2, 1.0)); audio.append(jv(25.80, 39.40, t2))
        shots += [cut(10.90, 12.73, t2), cut(21.43, 22.37, t2 + 6.0), cut(26.40, 27.30, t2 + 10.2)]
        s0 = t2 + 13.60 + 0.27; audio.append(sar(2, 10.98, 16.80, s0))
        v = s0 + (14.16 - 10.98) - 0.08
        shots += [dict(kind='plan', img='p3d_3br', lab='3 BEDROOMS', t=s0, dur=1.6), dict(kind='plan', img='p3d_2br', lab='2 BEDROOMS', t=s0 + 1.6, dur=v - s0 - 1.6),
                  dict(kind='vend', dark=True, t=v, dur=3.6)]
        return dict(shots=shots, audio=audio, dur=v + 3.6, end=v, silence=sil, title=t2)
    if name == 'C':
        # v3: John speaks first, Sarah comes in after him and has the last word (owner, 4 Nov)
        shots = []; audio = []; t = 0.0
        for (a, b), z in zip(HOOK, (1.40, 1.58)):
            shots.append(john(a, b, t, z)); audio.append(jv(a, b, t)); t += b - a
        shots.append(cut(26.40, 27.30, t - (HOOK[1][1] - HOOK[1][0])))
        s = t + 0.30                                          # Sarah in
        audio += [sar(1, 0.0, 3.55, s), sar(1, 3.85, 10.35, s + 3.70)]
        o = s + 3.70 - 3.85                                   # Sarah clip time -> video time for the 2nd piece
        shots += [dict(kind='photo', name='mmexport1792497989322.jpg', t=s, dur=2.06, z0=1.0, z1=1.07, txt='NO RENDERS.'),
                  dict(kind='photo', name='mmexport1792497986840.jpg', t=s + 2.06, dur=1.64, z0=1.07, z1=1.0, txt='REAL SITE.'),
                  dict(kind='photo', name='mmexport1792497982990.jpg', t=s + 3.70, dur=6.96 + o - 0.1 - (s + 3.70), z0=1.0, z1=1.06, txt='stamp'),
                  dict(kind='photo', name='mmexport1792497978574.jpg', t=6.96 + o - 0.1, dur=1.12, z0=1.06, z1=1.0),
                  dict(kind='photo', name='mmexport1792497931884.jpg', t=8.08 + o - 0.1, dur=1.12, z0=1.0, z1=1.06),
                  dict(kind='photo', name='mmexport1792497958870.jpg', t=9.20 + o - 0.1, dur=10.35 + o - (9.20 + o - 0.1) + 0.25, z0=1.06, z1=1.0)]
        p0 = 10.35 + o + 0.25                                 # "A hundred homes expected to be ready in October 2027." over the plans
        audio.append(sar(1, 10.50, 14.62, p0)); pl = 14.62 - 10.50
        shots += [dict(kind='plan', img='p3d_1br', lab='1 BEDROOM', t=p0, dur=1.33), dict(kind='plan', img='p3d_2br', lab='2 BEDROOMS', t=p0 + 1.33, dur=1.33),
                  dict(kind='plan', img='p3d_3br', lab='3 BEDROOMS', t=p0 + 2.66, dur=pl + 0.12 - 2.66)]
        v = p0 + pl + 0.12; audio.append(sar(1, 14.80, 17.45, v + 0.15))   # "Vanta House in Naguru, Kampala." on the end card
        shots.append(dict(kind='vend', dark=True, t=v, dur=3.2))
        return dict(shots=shots, audio=audio, dur=v + 3.2, end=v, sarah=s)

def captions(plan):
    caps = []
    for a, b, t0, src, n in plan['audio']:
        if n == 0:
            idx = [i for i in range(len(RA.WORDS)) if a - 0.05 <= RA.WORDS[i]['t'] < b]
            ch = [(RA.WORDS[i]['t'], txt) for i, txt in RA.CH if i in idx]
        else:
            ws = [w for w in SW[n] if a - 0.05 <= w['t'] < b]; ch = []; seen = {}
            for key, txt in SCH[n]:
                k0 = key.split('#')[0]; nth = int(key.split('#')[1]) if '#' in key else 1
                hits = [w for w in ws if w['w'].strip('.,?').lower() == k0.lower()]
                if len(hits) >= nth: ch.append((hits[nth - 1]['t'], txt))
        for k, (wt, txt) in enumerate(ch):
            s = t0 + wt - a - 0.05
            e = (t0 + ch[k + 1][0] - a - 0.09) if k + 1 < len(ch) else t0 + (b - a) - 0.05
            caps.append((s, min(e, s + 2.6), txt))
    return caps

_L = {}
def L(k):
    if k in _L: return _L[k]
    if k == 'rs': v = barred(T('REAL SITE.', 'mo7', 104, WHITE, shadow=0.7, sblur=16, sdy=6))
    elif k == 'nr': v = barred(T('NO RENDERS.', 'mo7', 104, WHITE, shadow=0.7, sblur=16, sdy=6))
    elif k in ('vhD', 'vhL'): v = barred(T('VANTA HOUSE', 'mo7', 104, WHITE, shadow=0), gap=26)
    elif k in ('ngD', 'ngL'): v = T('NAGURU, KAMPALA', 'mo5', 46, (236, 236, 236), shadow=0)
    elif k == 'pnote': v = T("ARTIST'S IMPRESSION  ·  LAYOUT MAY CHANGE", 'mo5', 24, (165, 165, 165), track=2, shadow=0)
    elif k.startswith('lab:'): v = barred(T(k[4:], 'mo7', 56, WHITE, track=1, shadow=0))
    elif k == 'title': v = barred(T('JOHN YAN  ·  FOUNDER, BLACKSTONE REAL ESTATE', 'mo6', 31, WHITE, track=3, shadow=1.0, sblur=12, sdy=2), gap=16)
    elif k.startswith('c:'): v = T(k[2:], 'mo6', 50, WHITE, shadow=0.9, sblur=10, sdy=3)
    else: v = RA.L(k)
    _L[k] = v; return v

def plan_card(img, tl, dur):
    """3D floor plan (white background) on a rounded white card with a soft shadow, for the dark video M background"""
    key = 'pc:' + img
    if key not in DC._c:
        P = Image.open(S + '/pack/%s.png' % img).convert('RGB')
        sc = min(700 / P.width, 860 / P.height)
        P = P.resize((int(P.width * sc), int(P.height * sc)), Image.LANCZOS)
        card = rounded(P, 26)
        shd, pad = soft_shadow(card.width, card.height, 26, blur=30, a=0.55, dy=18)
        shd.alpha_composite(card, (pad, pad))
        DC._c[key] = shd
    return DC._c[key]

def render(name, test=None):
    plan = build(name); caps = captions(plan); dur = plan['dur']; NFR = int(round(dur * FPS))
    out = S + '/ABC/v3_%s_lossless.mkv' % name
    enc = None if test else subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                              '-c:v', 'libx264rgb', '-qp', '0', '-preset', 'veryfast', out], stdin=subprocess.PIPE)
    shots = plan['shots']; readers = {}; lastjohn = None; t_start = time.time()
    for i in range(NFR):
        t = i / FPS
        active = [s for s in shots if s['t'] - 1e-6 <= t < s['t'] + (s.get('dur') or (s['b'] - s['a'])) + 1e-6]
        frames = {}
        for s_ in active:
            if s_['kind'] == 'john':
                k = id(s_)
                if k not in readers: readers[k] = RA.john_reader(s_)
                frames[k] = readers[k]()
        sh = active[-1] if active else shots[-1]
        if test is not None and i not in test: continue
        tl = t - sh['t']
        if sh['kind'] == 'john':
            lastjohn = frames[id(sh)]; im = Image.fromarray(lastjohn).convert('RGBA')
        elif sh['kind'] == 'photo':
            u = clamp(tl / sh['dur']); im = fit_crop(photo(sh['name']), W, H, zoom=sh['z0'] + (sh['z1'] - sh['z0']) * u).convert('RGBA')
            if sh.get('txt') in ('NO RENDERS.', 'REAL SITE.'):
                im = Image.blend(im, Image.new('RGBA', (W, H), (0, 0, 0, 255)), 0.42)
                p = eo(clamp(tl / 0.12)) if t > 0.05 else 1.0
                place(im, L('nr') if sh['txt'] == 'NO RENDERS.' else L('rs'), 540, 745, a=p, sc=1.15 - 0.15 * p)
            elif sh.get('txt') == 'stamp':
                place(im, RA.L('stamp'), 540, 330, a=eo(clamp(tl / 0.2)))
        elif sh['kind'] == 'black':
            im = Image.new('RGBA', (W, H), (6, 6, 6, 255))
        elif sh['kind'] == 'plan':
            im = radial(DARK[0], DARK[1], 'dk')
            P = plan_card(sh['img'], tl, sh['dur']); z = 1.0 + 0.04 * clamp(tl / max(sh['dur'], 0.1))
            Pz = P.resize((int(P.width * z), int(P.height * z)), Image.BICUBIC)
            place(im, Pz, 540, 790, a=eo(clamp(tl / 0.15)))
            place(im, L('lab:' + sh['lab']), 540, 250, a=eo(clamp(tl / 0.2)))
            place(im, L('pnote'), 540, 1262)
        elif sh['kind'] == 'vend':
            dark = sh['dark']; im = Image.new('RGBA', (W, H), (8, 8, 8, 255)) if dark else radial(DARK[0], DARK[1], 'dk')
            ST.reveal(im, L('vhD' if dark else 'vhL'), 540, 860, t, sh['t'] + 0.10, dur=0.55)
            ST.reveal(im, L('ngD' if dark else 'ngL'), 540, 1000, t, sh['t'] + 0.45, dur=0.5)
            sc = 1 + 0.03 * clamp(tl / sh['dur'])
            big = im.resize((round(W * sc), round(H * sc)), Image.BICUBIC)
            im = big.crop((int((big.width - W) / 2), int((big.height - H) * 0.45), int((big.width - W) / 2) + W, int((big.height - H) * 0.45) + H))
        if sh['kind'] in ('john', 'photo'): im.alpha_composite(GRAD)
        # overlays
        if name == 'A' and t < plan['trend']:
            a_ = eo(clamp(t / 0.3)) if t > 0.05 else 1.0
            place(im, L('trend'), 540, 330, a=a_); place(im, L('trend2'), 540, 398, a=a_)
        if name == 'B' and plan['title'] <= t < plan['title'] + 5.2:
            tt = t - plan['title']; a_ = eo(clamp((tt - 0.4) / 0.6)) * (1 - eo(clamp((tt - 4.6) / 0.6)))
            if a_ > 0: place(im, L('title'), 540, 340, a=a_)
        if sh['kind'] in ('john', 'photo', 'plan') and sh.get('txt') not in ('NO RENDERS.', 'REAL SITE.'):
            for a_, b_, txt in caps:
                if a_ <= t < b_: place(im, L('c:' + txt), 540, 1195 if sh['kind'] != 'plan' else 1345)
        rgb = im.convert('RGB')
        if enc: enc.stdin.write(rgb.tobytes())
        else: rgb.save(S + '/ABC/v3test_%s_%05d.jpg' % (name, i), quality=88)
    if enc: enc.stdin.close(); enc.wait()
    json.dump({'audio': plan['audio'], 'dur': dur, 'end': plan['end'], 'silence': plan.get('silence'), 'sarah': plan.get('sarah')}, open(S + '/ABC/v3_%s_plan.json' % name, 'w'))
    print(name, 'done', NFR, 'frames %.0fs' % (time.time() - t_start), 'dur %.2f end %.2f' % (dur, plan['end']))

import docs_common as DC
if __name__ == '__main__':
    test = set(int(x) for x in sys.argv[2].split(',')) if len(sys.argv) > 2 else None
    render(sys.argv[1], test)
