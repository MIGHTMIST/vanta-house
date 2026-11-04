# Original scores for A (documentary), B (cold open), C (proof open), written to their exact moments.
import pretty_midi as pm, random, json
S = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'
random.seed(9)
def n(i, p, t, d, v): i.notes.append(pm.Note(velocity=max(1, min(127, int(v + random.randint(-3, 3)))), pitch=p, start=t, end=t + d))
def save(m, ins, name):
    for i in ins: m.instruments.append(i)
    m.write(S + '/music/score_%s.mid' % name)
P = {k: json.load(open(S + '/ABC/%s_plan.json' % k)) if False else None for k in 'ABC'}
# ---- A: documentary. ambience on the walk-in slot, low boom on the hard cut (3.0), cello + piano under him, swell on the site shots, chord on the tag
m = pm.PrettyMIDI(initial_tempo=72); pad = pm.Instrument(92); cello = pm.Instrument(42); pno = pm.Instrument(0); stg = pm.Instrument(49); timp = pm.Instrument(47); dr = pm.Instrument(0, is_drum=True)
for t0, ch, r in ((0, [57, 60, 64], 45), (3.0, [57, 60, 64], 33), (7.0, [53, 57, 60], 29), (10.5, [55, 59, 62], 31), (12.53, [57, 60, 64, 67], 33),
                  (16.0, [53, 57, 60, 65], 29), (20.0, [50, 53, 57, 62], 26), (23.5, [52, 55, 59, 64], 28), (26.13, [57, 60, 64, 69], 33)):
    d = 3.6
    for p in ch: n(pad, p + 12, t0, d + 0.2, 34 if t0 < 3 else 40)
    if t0 >= 3.0: n(cello, r + 12, t0, d, 58 if t0 < 26 else 70)
    if t0 >= 12.53: 
        for p in ch: n(stg, p + 12, t0, d, 54 if t0 < 14 else 44)
for k, t in enumerate([3.0 + 0.8 * j for j in range(12)] + [12.6 + 0.4 * j for j in range(6)] + [15.3 + 0.8 * j for j in range(13)]):
    if t < 26: n(pno, [69, 72, 76, 74][k % 4], t, 0.7, 40)
n(timp, 33, 3.0, 1.5, 112); n(dr, 36, 3.0, 0.3, 110); n(timp, 33, 12.53, 1.2, 96); n(dr, 49, 12.53, 1.5, 70); n(timp, 33, 26.13, 2, 100)
save(m, (pad, cello, pno, stg, timp, dr), 'A')
# ---- B: cold open. crescendo + heartbeat under the line, HARD STOP at 9.53, one second of silence, quiet pad under the rest, chord on the end card
m = pm.PrettyMIDI(initial_tempo=90); stg = pm.Instrument(48); low = pm.Instrument(42); pad = pm.Instrument(89); pno = pm.Instrument(0); dr = pm.Instrument(0, is_drum=True); timp = pm.Instrument(47)
for j in range(8):
    t0 = j * 1.19; v = 34 + j * 9
    for p in ([57, 60, 64] if j % 2 == 0 else [57, 62, 65]): n(stg, p + 12, t0, 1.19, v)
    n(low, 45, t0, 1.19, 50 + j * 7)
for j, t in enumerate([k * 0.6667 for k in range(14)]):
    if t < 9.45: n(dr, 36, t, 0.1, 50 + j * 3); n(dr, 36, t + 0.18, 0.1, 30 + j * 2)
for k in range(14): n(timp, 45, 9.53 - 1.2 + k * 0.08, 0.06, 40 + k * 5)
for t0, ch in ((10.9, [53, 57, 60, 64]), (14.4, [50, 53, 57, 62]), (17.9, [55, 59, 62, 67]), (21.4, [57, 60, 64, 67])):
    for p in ch: n(pad, p, t0, 3.6, 38)
for t0 in (24.13,):
    for p in [45, 57, 60, 64, 69, 72]: n(stg, p, t0, 3.4, 70)
    for k, p in enumerate([69, 72, 76, 81]): n(pno, p, t0 + k * 0.12, 3.0, 62)
save(m, (stg, low, pad, pno, dr, timp), 'B')
# ---- C: proof open. three hits on NO RENDERS. / NO AI. / the stamp, a low pulse under his line, swell into the end card
m = pm.PrettyMIDI(initial_tempo=100); timp = pm.Instrument(47); pno = pm.Instrument(0); bass = pm.Instrument(38); pad = pm.Instrument(91); stg = pm.Instrument(48); dr = pm.Instrument(0, is_drum=True)
for t, v in ((0.0, 118), (0.8, 112), (1.6, 90)):
    n(timp, 38, t, 0.7, v); n(pno, 26, t, 0.8, v - 10); n(pno, 38, t, 0.8, v - 20); n(dr, 36, t, 0.2, v)
B = 0.6
for k in range(int(9.53 / B)):
    t = 2.6 + k * B
    n(bass, [38, 38, 34, 36][(k // 4) % 4], t, B * 0.5, 70); n(dr, 42, t + B / 2, 0.05, 36)
    if k % 2 == 0: n(dr, 36, t, 0.1, 64)
for t0, ch in ((2.6, [50, 53, 57]), (5.0, [46, 50, 53]), (7.4, [48, 53, 57]), (9.8, [48, 52, 55])):
    for p in ch: n(pad, p + 12, t0, 2.4, 40)
for p in [53, 57, 60, 64, 69]: n(stg, p, 12.13, 3.6, 72)
n(dr, 49, 12.13, 2, 84); n(timp, 41, 12.13, 1.5, 96)
for k, p in enumerate([72, 76, 79, 84]): n(pno, p, 12.13 + k * 0.15, 2.5, 60)
save(m, (timp, pno, bass, pad, stg, dr), 'C')
print('scores written')
