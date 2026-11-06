# Original scores for openings v2, timed to each plan.
import pretty_midi as pm, random, json
S = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'
random.seed(13)
def n(i, p, t, d, v): i.notes.append(pm.Note(velocity=max(1, min(127, int(v + random.randint(-3, 3)))), pitch=p, start=t, end=t + d))
def save(m, ins, name):
    for i in ins: m.instruments.append(i)
    m.write(S + '/music/score_v2%s.mid' % name)
P = {k: json.load(open(S + '/ABC/v2_%s_plan.json' % k)) for k in 'ABC'}
# A: ambience (prep) -> boom on the hard cut -> cello/piano under John -> swell on site -> warm lift under Sarah + plans -> chord on VANTA HOUSE
A = P['A']; X = 4.93; JC = A['audio'][2][2]; SA = A['audio'][3][2]; V = A['end']; D = A['dur']
m = pm.PrettyMIDI(initial_tempo=72); pad = pm.Instrument(92); cello = pm.Instrument(42); pno = pm.Instrument(0); stg = pm.Instrument(49); timp = pm.Instrument(47); dr = pm.Instrument(0, is_drum=True)
secs = [(0, X, [57, 60, 64], 45, 'prep'), (X, X + 4.7, [57, 60, 64], 33, 'j'), (X + 4.7, JC, [53, 57, 60], 29, 'j'), (JC, JC + 4.6, [57, 60, 64, 67], 33, 's'),
        (JC + 4.6, JC + 9.2, [53, 57, 60, 65], 29, 'j'), (JC + 9.2, SA, [50, 53, 57, 62], 26, 'j'), (SA, V, [53, 57, 60, 64, 67], 41, 'sar'), (V, D, [48, 55, 60, 64, 67], 36, 'end')]
for a, b, ch, r, kind in secs:
    for p in ch: n(pad, p + 12, a, b - a + 0.2, 34 if kind == 'prep' else 42)
    if kind != 'prep': n(cello, r + 12, a, b - a, 58 if kind != 'end' else 72)
    if kind in ('s', 'sar', 'end'):
        for p in ch[:4]: n(stg, p + 12, a, b - a, 56 if kind != 'end' else 70)
    if kind == 'prep':
        for k in range(5): n(pno, [76, 72, 69, 72, 74][k], 0.4 + k * 0.9, 1.4, 34)
    elif kind != 'end':
        step = 0.4 if kind in ('s', 'sar') else 0.8; t = a
        k = 0
        while t < b - 0.2: n(pno, [69, 72, 76, 74][k % 4] + (3 if kind == 'sar' else 0), t, 0.7, 40 if kind != 'sar' else 48); t += step; k += 1
    else:
        for k, p in enumerate([72, 76, 79, 84]): n(pno, p, a + k * 0.12, 3.0, 62)
n(timp, 33, X, 1.5, 112); n(dr, 36, X, 0.3, 110); n(timp, 33, JC, 1.2, 96); n(dr, 49, JC, 1.5, 70); n(timp, 33, V, 2, 100); n(dr, 49, V, 2, 80)
save(m, (pad, cello, pno, stg, timp, dr), 'A')
# B: crescendo + heartbeat -> hard stop -> silence -> low pad under John -> lift under Sarah + plan -> chord on VANTA HOUSE
B = P['B']; SIL = B['silence']; SB = B['audio'][-1][2]; VB = B['end']; DB = B['dur']
m = pm.PrettyMIDI(initial_tempo=90); stg = pm.Instrument(48); low = pm.Instrument(42); pad = pm.Instrument(89); pno = pm.Instrument(0); dr = pm.Instrument(0, is_drum=True); timp = pm.Instrument(47)
for j in range(8):
    t0 = j * SIL / 8
    for p in ([57, 60, 64] if j % 2 == 0 else [57, 62, 65]): n(stg, p + 12, t0, SIL / 8, 34 + j * 9)
    n(low, 45, t0, SIL / 8, 50 + j * 7)
for k in range(14):
    t = k * 0.6667
    if t < SIL - 0.1: n(dr, 36, t, 0.1, 50 + k * 3); n(dr, 36, t + 0.18, 0.1, 30 + k * 2)
for k in range(14): n(timp, 45, SIL - 1.2 + k * 0.08, 0.06, 40 + k * 5)
t = SIL + 1.35
for ch in ([53, 57, 60, 64], [50, 53, 57, 62], [55, 59, 62, 67], [57, 60, 64, 67]):
    if t < SB:
        for p in ch: n(pad, p, t, min(3.6, SB - t + 0.3), 38)
    t += 3.4
for p in [53, 57, 60, 64, 67]: n(pad, p + 12, SB, VB - SB, 46)
for k in range(int((VB - SB) / 0.4)): n(pno, [72, 76, 79, 76][k % 4], SB + k * 0.4, 0.6, 46)
for p in [45, 57, 60, 64, 69, 72]: n(stg, p, VB, DB - VB, 70)
for k, p in enumerate([69, 72, 76, 81]): n(pno, p, VB + k * 0.12, 3.0, 62)
save(m, (stg, low, pad, pno, dr, timp), 'B')
# C: hits on NO RENDERS. / REAL SITE., pulse under Sarah with accents on workers / steel / concrete, softer under John, chord on VANTA HOUSE
C = P['C']; VC = C['end']; DC_ = C['dur']; JS = C['audio'][2][2]
m = pm.PrettyMIDI(initial_tempo=100); timp = pm.Instrument(47); pno = pm.Instrument(0); bass = pm.Instrument(38); pad = pm.Instrument(91); stg = pm.Instrument(48); dr = pm.Instrument(0, is_drum=True)
for t, v in ((0.0, 118), (2.06, 112)):
    n(timp, 38, t, 0.7, v); n(pno, 26, t, 0.8, v - 10); n(pno, 38, t, 0.8, v - 20); n(dr, 36, t, 0.2, v)
for t in (6.71, 7.83, 8.95): n(timp, 41, t, 0.5, 86); n(dr, 36, t, 0.1, 90)
Bt = 0.6; t = 3.70; k = 0
while t < VC - 0.05:
    under_j = t >= JS
    n(bass, [38, 38, 34, 36][(k // 4) % 4], t, Bt * 0.5, 62 if under_j else 72); n(dr, 42, t + Bt / 2, 0.05, 30 if under_j else 40)
    if k % 2 == 0: n(dr, 36, t, 0.1, 54 if under_j else 66)
    t += Bt; k += 1
t = 3.70
for ch in ([50, 53, 57], [46, 50, 53], [48, 53, 57], [48, 52, 55]) * 3:
    if t >= VC: break
    for p in ch: n(pad, p + 12, t, min(2.4, VC - t), 40)
    t += 2.4
for p in [53, 57, 60, 64, 69]: n(stg, p, VC, DC_ - VC, 72)
n(dr, 49, VC, 2, 84); n(timp, 41, VC, 1.5, 96)
for k, p in enumerate([72, 76, 79, 84]): n(pno, p, VC + k * 0.15, 2.5, 60)
save(m, (timp, pno, bass, pad, stg, dr), 'C')
print('ok')
