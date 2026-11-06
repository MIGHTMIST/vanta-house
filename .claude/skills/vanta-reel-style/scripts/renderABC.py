# Three openings from John's cold-open clip (+ real site photos):
#  A "documentary" - walk-in slot (placeholder until the clip arrives) + trend line, hard cut to his strongest line close,
#     two quick real-site shots under his voice (J-cut), ends on his voice. Delivered with and without music.
#  B "cold open" - strongest line very close with music building, a second of silence, one small title, his next line.
#  C "proof open" - NO RENDERS. / NO AI. over real site photos, then his line, Modern Clean end card.
# Usage: python3 renderABC.py A|B|C [test frame list]
import sys, os, json, subprocess, time
import numpy as np
from PIL import Image
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
from docs_common import *
import docs_common as DC
_argv = sys.argv; sys.argv = [sys.argv[0], 'masks']
import renderD as D
sys.argv = _argv
G = S + '/G/'; SRC = G + 'src.mp4'
GRADE = open(S + '/C/grade.txt').read().strip()
WORDS = json.load(open(G + 'words.json'))['words']
FIX = {24 + 1: '10', 7: 'Vanta', 57: 'grow'}                       # confirmed by Abdullahi: "10 years"; Vanta House; grow
def word(i): return FIX.get(i, WORDS[i]['w'])
FACE = {'A': (330, 705), 'B': (360, 765)}                         # face centre in the source frame per camera angle
def angle(src_t): return 'B' if src_t >= 32.23 else 'A'

# caption chunks (word index, text) over the whole clip
CH = [(24, 'After 10 years'), (27, "in China's investment"), (30, 'banking industry,'), (32, 'I saw significant'), (35, 'opportunities'),
      (36, "in Africa's"), (38, 'real estate market.'), (41, 'I founded Blackstone'), (44, 'to bring professional'), (47, 'investment analysis'),
      (49, 'to build'), (51, 'trusted development,'), (53, 'deliver lasting value'), (56, 'and grow'), (58, 'alongside Uganda.')]
HOOK = [(15.00, 19.15), (20.02, 25.40)]                           # "After 10 years ... real estate market." (pause tightened)

def john(a, b, t, z):
    return dict(kind='john', a=a, b=b, t=t, z=z)
SRC2 = S + '/H/src2.mp4'                                          # the cutaways version (same clock as SRC)
def cut(a, b, t):
    return dict(kind='john', a=a, b=b, t=t, z=1.0, src=SRC2, dur=b - a)
# real cutaways in SRC2: 10.90-12.73 wide establishing, 16.40-17.33 leaning in, 4.13-6.30 glasses (preparing),
#                         21.43-22.37 close smile, 26.40-27.30 laptop angle

def build(name):
    """returns dict(shots, audio, dur, texts, end)"""
    if name == 'A':
        shots = [cut(10.90, 12.73, 0.0), cut(16.40, 17.33, 1.83), cut(4.13, 6.30, 2.76)]; audio = []
        t = 4.93                                                  # "preparing" montage, then the hard cut
        for (a, b), z in zip(HOOK, (1.40, 1.58)):
            shots.append(john(a, b, t, z)); audio.append((a, b, t)); t += b - a
        jc = t                                                    # J-cut: voice continues over two site shots
        audio.append((25.80, 39.40, jc))
        shots.append(dict(kind='photo', name='mmexport1792497989322.jpg', t=jc, dur=1.15, z0=1.0, z1=1.10))
        shots.append(dict(kind='photo', name='mmexport1792497982990.jpg', t=jc + 1.15, dur=1.15, z0=1.08, z1=1.0))
        v0 = jc + 2.30
        shots.append(john(25.80 + 2.30, 39.40, v0, 1.0))
        end = jc + 13.60
        shots.append(dict(kind='tag', t=end, dur=1.8))
        return dict(shots=shots, audio=audio, dur=end + 1.8, end=end)
    if name == 'B':
        t = 0.0; shots = []; audio = []
        for (a, b), z in zip(HOOK, (1.55, 1.75)):
            shots.append(john(a, b, t, z)); audio.append((a, b, t)); t += b - a
        sil = t; shots.append(dict(kind='black', t=sil, dur=1.0))
        t2 = sil + 1.0
        shots.append(john(25.80, 39.40, t2, 1.0)); audio.append((25.80, 39.40, t2))
        shots += [cut(10.90, 12.73, t2), cut(21.43, 22.37, t2 + 6.0), cut(26.40, 27.30, t2 + 10.2)]
        end = t2 + 13.60
        shots.append(dict(kind='darkend', t=end, dur=3.6))
        return dict(shots=shots, audio=audio, dur=end + 3.6, end=end, silence=sil)
    if name == 'C':
        shots = [dict(kind='photo', name='mmexport1792497989322.jpg', t=0.0, dur=0.8, z0=1.0, z1=1.06, txt='NO RENDERS.'),
                 dict(kind='photo', name='mmexport1792497986840.jpg', t=0.8, dur=0.8, z0=1.06, z1=1.0, txt='NO AI.'),
                 dict(kind='photo', name='mmexport1792497982990.jpg', t=1.6, dur=1.0, z0=1.0, z1=1.07, txt='stamp')]
        t = 2.6; audio = []
        for (a, b), z in zip(HOOK, (1.40, 1.58)):
            shots.append(john(a, b, t, z)); audio.append((a, b, t)); t += b - a
        end = t
        shots.append(cut(26.40, 27.30, 2.6 + 4.15))                # cutaway over the jump cut
        shots.append(dict(kind='end', t=end, dur=3.8))
        return dict(shots=shots, audio=audio, dur=end + 3.8, end=end)

# ---------------------------------------------------------------- captions from the audio plan
def captions(plan):
    caps = []
    for a, b, t0 in plan['audio']:
        idx = [i for i in range(len(WORDS)) if a - 0.05 <= WORDS[i]['t'] < b]
        chunks = [(i, txt) for i, txt in CH if i in idx]
        for k, (i, txt) in enumerate(chunks):
            s = t0 + WORDS[i]['t'] - a - 0.05
            e = (t0 + WORDS[chunks[k + 1][0]]['t'] - a - 0.09) if k + 1 < len(chunks) else t0 + (b - a) - 0.05
            caps.append((s, min(e, s + 2.4), txt))
    return caps

# ---------------------------------------------------------------- frame sources
def john_reader(sh):
    z = sh['z']; fx, fy = FACE[angle(sh['a'])]
    cw, ch = 1080 / z, 1920 / z
    x0 = min(max(fx - cw * 0.45, 0), 1080 - cw); y0 = min(max(fy - ch * 0.36, 0), 1920 - ch)
    vf = 'crop=%d:%d:%d:%d,scale=1080:1920:flags=lanczos,%s%s,format=rgb24' % (cw, ch, x0, y0, GRADE, ',unsharp=5:5:0.45' if z > 1.2 else '')
    if z == 1.0: vf = '%s,format=rgb24' % GRADE
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', '%.3f' % sh['a'], '-t', '%.3f' % (sh['b'] - sh['a']), '-i', sh.get('src', SRC), '-vf', vf, '-r', '30',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    last = [None]
    def get():
        raw = p.stdout.read(W * H * 3)
        if len(raw) == W * H * 3: last[0] = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
        return last[0]
    return get

_L = {}
def L(k):
    if k in _L: return _L[k]
    if k == 'trend': v = T('Preparing for my documentary', 'mo6', 50, WHITE, shadow=0.9, sblur=12, sdy=3)
    elif k == 'trend2': v = T('about building in Kampala', 'mo6', 50, WHITE, shadow=0.9, sblur=12, sdy=3)
    elif k == 'slot1': v = T('CLIP STILL NEEDED', 'mo7', 46, CHAR, track=6, shadow=0)
    elif k == 'slot2': v = T('John walks in, sits down,', 'mo5', 38, GREY, shadow=0)
    elif k == 'slot3': v = T('fixes his mic, looks for the camera', 'mo5', 38, GREY, shadow=0)
    elif k == 'trendpill': v = pill('Preparing for my documentary about building in Kampala', 'mo6', 40, WHITE, CHAR, track=0, padx=30, pady=18, alpha=215)
    elif k == 'tag': v = T('VANTA HOUSE  ·  NAGURU, KAMPALA', 'mo6', 32, WHITE, track=8, shadow=0)
    elif k == 'title': v = T('JOHN YAN  ·  FOUNDER, BLACKSTONE REAL ESTATE', 'mo6', 31, WHITE, track=5, shadow=1.0, sblur=12, sdy=2)
    elif k == 'nr': v = T('NO RENDERS.', 'mo7', 104, WHITE, track=2, shadow=0.7, sblur=16, sdy=6)
    elif k == 'nai': v = T('NO AI.', 'mo7', 104, WHITE, track=2, shadow=0.7, sblur=16, sdy=6)
    elif k == 'stamp': v = pill('REAL SITE  ·  VANTA HOUSE  ·  OCT 2026', 'px5', 26, WHITE, CHAR, track=2, padx=24, pady=14, alpha=190)
    elif k == 'd1': v = T('VANTA HOUSE', 'mo7', 96, WHITE, track=4, shadow=0)
    elif k == 'd2': v = T('Naguru, Kampala', 'mo5', 40, (200, 196, 188), shadow=0)
    elif k == 'd3': v = baseline_line([('Send', 'mo4', 40, WHITE, 0), ('VANTA', 'mo7', 40, SAND, 8), ('on WhatsApp to', 'mo4', 40, WHITE, 0)], gap=14)
    elif k == 'd5': v = T('BLACKSTONE REAL ESTATE', 'mo5', 26, (160, 156, 148), track=9, shadow=0)
    elif k == 'd4': v = T('0741 131 420', 'mo6', 76, WHITE, track=3, shadow=0)
    elif k.startswith('c:'): v = pill(k[2:], 'mo6', 48, WHITE, (18, 18, 18), track=0, padx=28, pady=16, alpha=165)
    _L[k] = v; return v

def render(name, test=None):
    plan = build(name); caps = captions(plan)
    dur = plan['dur']; NFR = int(round(dur * FPS))
    D.TE, D.DUR = plan['end'], dur; D.NO_WA = True
    out = S + '/ABC/%s_lossless.mkv' % name
    os.makedirs(S + '/ABC', exist_ok=True)
    enc = None if test else subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                              '-c:v', 'libx264rgb', '-qp', '0', '-preset', 'veryfast', out], stdin=subprocess.PIPE)
    shots = plan['shots']; readers = {}; lastjohn = None
    t_start = time.time()
    for i in range(NFR):
        t = i / FPS
        active = [s for s in shots if s['t'] - 1e-6 <= t < s['t'] + (s.get('dur') or (s['b'] - s['a'])) + 1e-6]
        frames = {}
        for s_ in active:                                          # keep every running clip in sync, even under a cutaway
            if s_['kind'] == 'john':
                k = id(s_)
                if k not in readers: readers[k] = john_reader(s_)
                frames[k] = readers[k]()
        sh = active[-1] if active else shots[-1]
        need = test is None or i in test
        if sh['kind'] == 'john':
            fr = frames[id(sh)]; lastjohn = fr
            if not need: continue
            im = Image.fromarray(fr).convert('RGBA')
        else:
            if not need: continue
            tl = t - sh['t']
            if sh['kind'] == 'photo':
                u = clamp(tl / sh['dur']); im = fit_crop(photo(sh['name']), W, H, zoom=sh['z0'] + (sh['z1'] - sh['z0']) * u).convert('RGBA')
                if sh.get('txt') in ('NO RENDERS.', 'NO AI.'):
                    im = Image.blend(im, Image.new('RGBA', (W, H), (0, 0, 0, 255)), 0.42)
                    p = eo(clamp(tl / 0.12)) if t > 0.05 else 1.0
                    place(im, L('nr' if sh['txt'] == 'NO RENDERS.' else 'nai'), 540, 900, a=p, sc=1.15 - 0.15 * p)
                elif sh.get('txt') == 'stamp':
                    place(im, L('stamp'), 540, 330, a=eo(clamp(tl / 0.2)))
            elif sh['kind'] == 'slot':
                im = radial(OFF, OFF2, 'off')
                d = ImageDraw.Draw(im); d.rounded_rectangle((90, 760, 990, 1160), 28, outline=SAND + (255,), width=3)
                place(im, L('slot1'), 540, 860); place(im, L('slot2'), 540, 960); place(im, L('slot3'), 540, 1015)
                place(im, ST.T('(swaps in when the walk-in clip arrives)', 'px4', 24, MIST, shadow=0), 540, 1095)
                im2 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
                place(im, R.fade(pill('Preparing for my documentary about building in Kampala', 'mo6', 40, WHITE, CHAR, track=0, padx=30, pady=18, alpha=225), 1), 540, 380)
            elif sh['kind'] == 'black':
                im = Image.new('RGBA', (W, H), (6, 6, 6, 255))
            elif sh['kind'] == 'tag':
                base = Image.fromarray(lastjohn).convert('RGBA') if lastjohn is not None else Image.new('RGBA', (W, H), (0, 0, 0, 255))
                im = Image.blend(base, Image.new('RGBA', (W, H), (0, 0, 0, 255)), min(0.85, eo(clamp(tl / 0.5)) * 0.85))
                place(im, L('tag'), 540, 900, a=eo(clamp((tl - 0.2) / 0.5)))
            elif sh['kind'] == 'darkend':
                im = Image.new('RGBA', (W, H), (8, 8, 8, 255))
                for k_, y, d0 in (('d1', 820, 0.15), ('d2', 910, 0.45), ('d5', 1010, 0.8)):
                    ST.reveal(im, L(k_), 540, y, t, sh['t'] + d0, dur=0.5)
                sc = 1 + 0.03 * clamp(tl / sh['dur'])                 # slow push so the card never sits still
                big = im.resize((round(W * sc), round(H * sc)), Image.BICUBIC); im = big.crop((int((big.width - W) / 2), int((big.height - H) * 0.45), int((big.width - W) / 2) + W, int((big.height - H) * 0.45) + H))
            elif sh['kind'] == 'end':
                base = Image.fromarray(lastjohn).convert('RGBA')
                p = eio(clamp(tl / 0.45)); im = Image.blend(base, Image.new('RGBA', (W, H), (0, 0, 0, 255)), 0.3 * p)
                panel = D.end_panel(t); y = int(H * (1 - p))
                if y < H: comp(im, panel.crop((0, 0, W, H - y)), 0, y)
        # overlays
        if name == 'A' and t < 4.93:
            a = eo(clamp(t / 0.3)) if t > 0.05 else 1.0
            place(im, L('trend'), 540, 330, a=a); place(im, L('trend2'), 540, 398, a=a)
        if name == 'B' and sh['kind'] == 'john' and t >= plan['silence'] + 1.0:
            tl = t - plan['silence'] - 1.0
            a = eo(clamp((tl - 0.4) / 0.6)) * (1 - eo(clamp((tl - 4.6) / 0.6)))
            if a > 0: place(im, L('title'), 540, 340, a=a)
        if sh['kind'] in ('john', 'photo') and not (sh.get('txt') in ('NO RENDERS.', 'NO AI.')):
            for a_, b_, txt in caps:
                if a_ <= t < b_: place(im, L('c:' + txt), 540, 1195)
        rgb = im.convert('RGB')
        if enc: enc.stdin.write(rgb.tobytes())
        else: rgb.save(S + '/ABC/test_%s_%05d.jpg' % (name, i), quality=88)
    if enc: enc.stdin.close(); enc.wait()
    json.dump({k: plan[k] for k in ('audio', 'dur', 'end')} | {'silence': plan.get('silence')}, open(S + '/ABC/%s_plan.json' % name, 'w'))
    print(name, 'done', NFR, 'frames %.0fs' % (time.time() - t_start), 'dur %.2f' % dur)

from PIL import ImageDraw
if __name__ == '__main__':
    test = set(int(x) for x in sys.argv[2].split(',')) if len(sys.argv) > 2 else None
    render(sys.argv[1], test)
