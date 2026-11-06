# Score for opening C v3 (John first, Sarah last). A and B keep their v2 scores (same timelines).
import pretty_midi as pm, random, json, subprocess
S = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'
random.seed(21)
def n(i, p, t, d, v): i.notes.append(pm.Note(velocity=max(1, min(127, int(v + random.randint(-3, 3)))), pitch=p, start=t, end=t + d))
C = json.load(open(S + '/ABC/v3_C_plan.json')) if False else None
import sys; sys.argv = ['x']; sys.path.insert(0, S + '/scripts')
import renderV3 as V
P = V.build('C'); VC = P['end']; D = P['dur']; SS = P['sarah']; P0 = [t for a, b, t, s, k in P['audio']][4]
m = pm.PrettyMIDI(initial_tempo=100)
timp = pm.Instrument(47); pno = pm.Instrument(0); bass = pm.Instrument(38); pad = pm.Instrument(91); stg = pm.Instrument(48); low = pm.Instrument(89)
dr = pm.Instrument(0, is_drum=True)
# under John: low warm pad (D minor colour), a few soft piano notes, no drums
for t0, ch in ((0.0, [38, 45, 50]), (4.15, [34, 41, 50])):
    for p in ch: n(low, p, t0, (4.15 if t0 == 0 else SS - 4.15) + 0.3, 46)
for t0, p in ((0.6, 62), (2.4, 65), (4.6, 69), (6.4, 67), (8.2, 65)): n(pno, p, t0, 1.6, 40)
# Sarah in: hits on NO RENDERS. / REAL SITE.
for t, v in ((SS, 116), (SS + 2.06, 110)):
    n(timp, 38, t, 0.7, v); n(pno, 26, t, 0.8, v - 10); n(pno, 38, t, 0.8, v - 20); n(dr, 36, t, 0.2, v)
for dt in (6.71, 7.83, 8.95): n(timp, 41, SS + dt, 0.5, 86); n(dr, 36, SS + dt, 0.1, 90)       # workers / steel / concrete
Bt = 0.6; t = SS + 3.70; k = 0
while t < VC - 0.05:
    lift = t >= P0
    n(bass, [38, 38, 34, 36][(k // 4) % 4], t, Bt * 0.5, 74 if lift else 70); n(dr, 42, t + Bt / 2, 0.05, 44 if lift else 38)
    if k % 2 == 0: n(dr, 36, t, 0.1, 66)
    t += Bt; k += 1
t = SS + 3.70
for ch in ([50, 53, 57], [46, 50, 53], [48, 53, 57], [48, 52, 55]) * 3:
    if t >= VC: break
    for p in ch: n(pad, p + 12, t, min(2.4, VC - t), 40)
    t += 2.4
for k_, p in enumerate([74, 77, 81]): n(pno, p, P0 + k_ * 1.33, 1.0, 58)                              # one bell note per plan
for p in [53, 57, 60, 64, 69]: n(stg, p, VC, D - VC, 72)
n(dr, 49, VC, 2, 84); n(timp, 41, VC, 1.5, 96)
for k_, p in enumerate([72, 76, 79, 84]): n(pno, p, VC + k_ * 0.15, 2.5, 60)
for i in (timp, pno, bass, pad, stg, low, dr): m.instruments.append(i)
m.write(S + '/music/score_v3C.mid')
subprocess.run(['fluidsynth', '-ni', '-g', '0.8', '-r', '48000', '-F', S + '/music/score_v3C_raw.wav', '/usr/share/sounds/sf2/FluidR3_GM.sf2', S + '/music/score_v3C.mid'],
               check=True, capture_output=True)
print('ok', round(D, 2), round(SS, 2), round(P0, 2), round(VC, 2))
