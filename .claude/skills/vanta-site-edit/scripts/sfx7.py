# Sound for render6 (full-screen beat edit): real site sound of each shot, whoosh on cuts, accents on the tricks.
import sys, subprocess, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/hype')
import render7 as V
import soundfile as sf
R = V.R; SR = 48000; END = V.END; N = int(END * SR); B = V.B

def load(path, ss=None, t=None):
    cmd = ['ffmpeg', '-v', 'error'] + (['-ss', '%.3f' % ss] if ss is not None else []) + ['-i', path] + (['-t', '%.3f' % t] if t else []) + \
          ['-vn', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    a = np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32)
    return a.reshape(-1, 2).copy() if a.size else np.zeros((2, 2), np.float32)
bus = np.zeros((N, 2), np.float32)
def place(x, t, db=0.0, fi=0.004, fo=0.02, pan=0.0):
    if x.shape[0] < 2: return
    x = x * 10 ** (db / 20); n = x.shape[0]; env = np.ones(n, np.float32)
    a = min(n, max(1, int(fi * SR))); b = min(n, max(1, int(fo * SR)))
    env[:a] = np.linspace(0, 1, a); env[n - b:] *= np.linspace(1, 0, b); x = x * env[:, None]
    if pan: x = x * np.array([np.sqrt(0.5 - pan / 2) * 1.414, np.sqrt(0.5 + pan / 2) * 1.414], np.float32)
    i0 = int(t * SR)
    if i0 < 0: x = x[-i0:]; i0 = 0
    i1 = min(i0 + x.shape[0], N)
    if i1 > i0: bus[i0:i1] += x[:i1 - i0]
def rms(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
def norm(x, tdb, pk=-8.0):
    y = x * 10 ** (min(tdb - rms(x), 36) / 20); p = np.abs(y).max() + 1e-9
    return y * min(1.0, 10 ** (pk / 20) / p)
S = R + 'snd/'
WH = [load(S + f) for f in ('whoosh_fast_2.mp3', 'whoosh_medium_3.mp3', 'whoosh_soft_1.mp3')]
SWISH = load(S + 'sfx_swish_fast_1.mp3'); SHUT = load(S + 'sfx_camera_shutter_1.mp3'); POP = load(S + 'sfx_text_pop_2.mp3')
IMP = load(S + 'sfx_impact_soft_1.mp3'); SUB = load(S + 'sfx_impact_sub_2.mp3'); BOOM = load(S + 'sfx_cinematic_boom_1.mp3')
RISER = load(S + 'sfx_riser_1.mp3'); REV = load(S + 'reverse_swell.mp3'); CINE = load(S + 'whoosh_cinematic_5.mp3')
LOGO = load(S + 'sfx_logo_hit.wav')
MACH = {'GV3A9994', 'GV3A9999', 'GV3A9992', 'GV3A9995', 'GV3A0020', 'GV3A0028', 'GV3A0011', 'GV3A0017', 'GV3A0035', 'GV3A0036', 'GV3A0033'}

def site(src, t, hold, pan=0.0):
    c, a, b = src
    x = load(R + 'sitevids/%s.MP4' % c, a, min(hold + 0.25, 2.2))
    if x.shape[0] < SR * 0.25: return
    m = c in MACH
    place(norm(x, -31 if m else -37, -14 if m else -18), t, 0, fi=0.04, fo=0.3, pan=pan)

k = 0
for i, s in enumerate(V.SH):
    t0, t1 = s['t0'], s['t1']; kind = s['kind']
    if kind == 'full': site(s['src'], t0, t1 - t0)
    elif kind == 'split':
        for j, (kin, src, cx) in enumerate(s['parts']):
            nxt = s['parts'][j + 2][0] if j + 2 < len(s['parts']) else s['k1']
            site(src, B(kin), B(nxt) - B(kin), pan=-0.3 if j % 2 == 0 else 0.3); place(WH[k % 3], B(kin) - 0.05, -13); k += 1
    elif kind == 'strips':
        for j, src in enumerate(s['parts']):
            ta = t0 + j * V.BT / 2; site(src, ta, t1 - ta, pan=[-0.3, 0, 0.3][j]); place(WH[k % 3], ta - 0.05, -13); k += 1
    elif kind == 'photo': place(SHUT, t0, -12)
    if t0 > 0.3 and kind in ('full', 'photo', 'john') and not s.get('flash'):
        place(SWISH if s.get('quick') else WH[k % 3], t0 - 0.06, -15 if s.get('quick') else -12); k += 1

# hook: real site sound under the quiet intro of the song
place(norm(load(R + 'sitevids/GV3A0028.MP4', 0.0, 2.4), -23, -8), 0.0, 0, fi=0.05, fo=0.8)
place(IMP, B(1) - 0.01, -10)                                       # the beat drops on the first worker cut
place(REV[-int(1.6 * SR):], B(5) - 1.6, -14, fi=0.3); place(IMP, B(5), -8)   # swell into the colour snap + title
place(SUB, B(13), -8); place(SHUT, B(13), -10)                     # halftone freeze
place(CINE, B(17) - 0.25, -12)                                     # back to full colour
place(IMP, B(19), -10)                                             # shake
for tw, w in V.WORDS: place(POP, tw, -15)
place(RISER, B(31) - RISER.shape[0] / SR, -13, fi=0.2)             # riser into the burst
place(BOOM, B(33), -9)                                             # strips flash
place(CINE, B(41) - 0.2, -12)                                      # John
place(REV[-int(1.2 * SR):], B(45) - 1.2, -15, fi=0.3)
place(LOGO, B(45) + 1.2, -11)                                      # end card
sf.write(R + 'hype/sfx7_bus.wav', bus, SR, subtype='FLOAT')
print('bus peak', round(20 * np.log10(np.abs(bus).max() + 1e-9), 1), 'rms', round(rms(bus), 1))
