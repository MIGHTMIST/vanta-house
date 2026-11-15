# Sound design for the stacked site edit: real site sound of every clip on screen (machines, hammering, crews),
# whooshes on every picture change, hits on flashes, riser into the burst, shutter on photos, pops on words.
# Output: final soundtrack wav (music + sfx), loudness -14 LUFS, true peak -1.5 dB.
import sys, subprocess, numpy as np, json
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/hype')
import render5 as V
R = V.R; SR = 48000; END = V.END; N = int(END * SR)
B = V.B

def load(path, ss=None, t=None):
    cmd = ['ffmpeg', '-v', 'error']
    if ss is not None: cmd += ['-ss', '%.3f' % ss]
    cmd += ['-i', path]
    if t is not None: cmd += ['-t', '%.3f' % t]
    cmd += ['-vn', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    a = np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32)
    return a.reshape(-1, 2).copy() if a.size else np.zeros((1, 2), np.float32)

bus = np.zeros((N, 2), np.float32)
log = []
def place(x, t, gain_db=0.0, fade_in=0.004, fade_out=0.02, pan=0.0, name=''):
    if x.shape[0] < 2: return
    x = x * (10 ** (gain_db / 20))
    n = x.shape[0]; fi = max(1, int(fade_in * SR)); fo = max(1, int(fade_out * SR))
    env = np.ones(n, np.float32); env[:fi] = np.linspace(0, 1, fi)[:n]; env[-fo:] *= np.linspace(1, 0, fo)[-n:] if fo <= n else 1
    x = x * env[:, None]
    if pan: x = x * np.array([np.sqrt(0.5 - pan / 2) * 1.414, np.sqrt(0.5 + pan / 2) * 1.414], np.float32)
    i0 = int(t * SR)
    if i0 < 0: x = x[-i0:]; i0 = 0
    i1 = min(i0 + x.shape[0], N)
    if i1 > i0: bus[i0:i1] += x[:i1 - i0]
    log.append((round(t, 2), name, round(gain_db, 1)))

def rms_db(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
def norm(x, target_db, peak_db=-6.0, max_gain=36.0):
    g = min(target_db - rms_db(x), max_gain)
    y = x * 10 ** (g / 20)
    pk = np.abs(y).max() + 1e-9; lim = 10 ** (peak_db / 20)
    return y * min(1.0, lim / pk)

SND = R + 'snd/'
WH = [load(SND + f) for f in ('whoosh_fast_2.mp3', 'whoosh_medium_3.mp3', 'whoosh_soft_1.mp3', 'sfx_swish_fast_1.mp3')]
SWISH = load(SND + 'sfx_swish_fast_1.mp3')
SHUT = load(SND + 'sfx_camera_shutter_1.mp3')
POP = load(SND + 'sfx_text_pop_2.mp3')
IMP = load(SND + 'sfx_impact_soft_1.mp3'); SUB = load(SND + 'sfx_impact_sub_2.mp3'); BOOM = load(SND + 'sfx_cinematic_boom_1.mp3')
RISER = load(SND + 'sfx_riser_1.mp3'); REV = load(SND + 'reverse_swell.mp3'); CINE = load(SND + 'whoosh_cinematic_5.mp3')
LOGO = load(SND + 'sfx_logo_hit.wav'); LINE = load(SND + 'sfx_line_draw_tone_1.mp3')
MACHINE = {'GV3A9994', 'GV3A9999', 'GV3A9992', 'GV3A9993', 'GV3A9995', 'GV3A0020', 'GV3A0028', 'GV3A0011', 'GV3A0017', 'GV3A0035'}

# ---- 1. real site sound of each clip, from the moment its picture lands, real time ----
k = 0
for b, L in enumerate(V.BANDS):
    for i, (st, src, sp, d) in enumerate(L):
        nxt = L[i + 1][0] if i + 1 < len(L) else END
        hold = nxt - st
        pan = [-0.25, 0.0, 0.25][b]
        if src[0] == 'PHOTO':
            if st > 0.3: place(SHUT, st + 0.02, -15, pan=pan, name='shutter ' + src[1])
            continue
        c, a, z = src
        dur = min(hold + 0.25, 2.4)
        x = load(R + 'sitevids/%s.MP4' % c, a, dur)
        if x.shape[0] < SR * 0.3: continue
        mach = c in MACHINE
        x = norm(x, -24 if mach else -30, peak_db=-8 if mach else -12)
        place(x, st, 0.0, fade_in=0.03, fade_out=0.35, pan=pan, name='site ' + c)
        if st > 0.5:                                              # whoosh on the slide-in
            w = SWISH if V.B(31) - 0.01 <= st < V.B(33) else WH[k % len(WH)]; k += 1
            place(w, st - 0.06, -15 if w is SWISH else -13, pan=pan, name='whoosh')

# ---- 2. accents locked to the edit ----
place(norm(load(R + 'sitevids/GV3A0028.MP4', 0.0, 2.6), -24, -8), 0.0, 0, fade_in=0.2, fade_out=0.8, name='hook site bed')
place(IMP, B(1) - 0.01, -10, name='name behind tower')
place(REV[-int(1.6 * SR):], B(5) - 1.6, -14, fade_in=0.3, name='swell into colour')
place(IMP, B(5), -9, name='colour snap')
place(SUB, B(13), -8, name='halftone hit'); place(SHUT, B(13), -10, name='halftone shutter')
place(CINE, B(17) - 0.25, -12, name='back to colour')
place(IMP, B(19), -10, name='shake')
for tw, w in V.WORDS: place(POP, tw, -16, name='pop ' + w)
place(RISER, B(31) - RISER.shape[0] / SR, -13, fade_in=0.2, name='riser into burst')
place(BOOM, B(33), -9, name='burst boom')
place(CINE, V.JW0 - 0.2, -12, name='John panel whoosh')
place(REV[-int(1.2 * SR):], B(45) - 1.2, -15, fade_in=0.3, name='swell into end')
place(LINE[:int(1.6 * SR)], B(45.2), -18, fade_out=0.4, name='outline draw')
place(LOGO, B(46.5), -12, name='name hit')

json.dump(log, open(R + 'hype/sfx_log.json', 'w'))
# ---- 3. mix with the music, then -14 LUFS / -1.5 dBTP ----
import soundfile as sf
sf.write(R + 'hype/sfx_bus.wav', bus, SR, subtype='FLOAT')
print('events', len(log), 'bus peak dB', round(20 * np.log10(np.abs(bus).max() + 1e-9), 1), 'bus rms dB', round(rms_db(bus), 1))
