# Sound for render10 (round 4: n2 / crew / build). VID=n2|crew|build python3 sfx10.py
# music = owner's song (lyric video audio) cut on the last beat (45.79 s) + boom tail; real site sound of each shot LOW
# (a bit louder in the hook), quiet whooshes on cuts, shutter on photos, hits on the teal cards, pops on stacked words.
import sys, os, subprocess, numpy as np, soundfile as sf
H9 = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/hype'
sys.path.insert(0, H9)
import render10 as V
R = V.BASE.R; SR = 48000; END = V.END; N = int(round(END * SR)); VID = V.VID
B = V.tv                                       # beat k -> time in the video

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
LOGO = load(S + 'sfx_logo_hit.wav'); CLICK = load(S + 'sfx_click_1.mp3'); SWIN = load(S + 'sfx_ui_swoosh_in_1.mp3')
MACH = {'GV3A9994', 'GV3A9999', 'GV3A9992', 'GV3A9995', 'GV3A0020', 'GV3A0028', 'GV3A0011', 'GV3A0017', 'GV3A0035', 'GV3A0036', 'GV3A0033'}

def site(src, t, hold, pan=0.0, hook=False):
    if src[0] == 'photo': return
    c, a, b = src
    x = load(R + 'sitevids/%s.MP4' % c, a, min(hold + 0.25, 2.6 if hook else 2.2))
    if x.shape[0] < SR * 0.25: return
    m = c in MACH
    if hook: place(norm(x, -24 if m else -27, -8), t, 0, fi=0.05, fo=0.5)
    else: place(norm(x, -32 if m else -37, -14 if m else -18), t, 0, fi=0.04, fo=0.3, pan=pan)

k = 0
for i, s in enumerate(V.SH):
    t0, t1 = s['t0'], s['t1']; kind = s['kind']
    if kind == 'full': site(s['src'], t0, t1 - t0, hook=(i == 0 and V.M0 == 0))
    elif kind == 'photo': place(SHUT, t0, -15)
    elif kind == 'halftone': place(SUB, t0, -9); place(SHUT, t0, -11)
    if kind in ('full', 'photo') and i > 0 and V.SH[i - 1]['kind'] != 'black' and not s.get('flash'):
        place(SWISH, t0 - 0.05, -18)
    if s.get('boom'): place(WH[k % 3], t1 - 0.30, -15); k += 1          # whoosh into the cut on the ramp
    if s.get('flash') and t0 > 0.05: place(IMP, t0 - 0.005, -10)
    if kind == 'black' and t1 < END - 0.1: place(REV[-int(0.7 * SR):], t1 - 0.7, -16, fi=0.2); place(IMP, t1, -8)
for k0c, k1c, nm in V.COVERS:
    f0, f1 = V.fk(k0c), V.fk(k1c)
    for q in range(int(round((V.B(k1c) - V.B(k0c)) / (V.BT / 4)))): place(SHUT, V.tv(k0c + q * 0.25), -16)
for k0s, k1s, lines in V.STACKS:
    for j in range(len(lines)): place(POP, B(k0s + j), -15)
for ks in V.STREAKS: place(SWIN, B(ks), -19)
for ks in V.SWOOSH: place(CINE, B(ks) - 0.15, -12)
if V.TAG: place(POP, B(V.TAG[0]), -15)
if V.ENDTAG is not None: place(BOOM, B(44) - 0.01, -7); place(LOGO, B(V.ENDTAG) + 0.02, -12)
if V.M0 == 0: place(RISER, B(16) - RISER.shape[0] / SR, -18, fi=0.3)

# music: the owner's song, the window this video uses (loops: beat 16 -> 40, so the end runs into the start)
mus = load(H9 + '/refs4/song48.wav')
i0 = int(round(V.M0 * SR)); mus = mus[i0:i0 + N].copy()
if V.M0 == 0:                                                         # n2 ends on black after beat 44: fade the song out
    fs = int(round((V.tv(47) ) * SR)); fe = N; mus[fs:fe] *= np.linspace(1, 0, fe - fs)[:, None]
mix = np.zeros((N, 2), np.float32); mix[:mus.shape[0]] += mus * 0.92
mix += bus
sf.write(H9 + '/mix10_%s_raw.wav' % VID, mix, SR, subtype='FLOAT')
print(VID, 'bus rms', round(rms(bus), 1), 'music rms', round(rms(mus), 1), 'len', round(N / SR, 3))
