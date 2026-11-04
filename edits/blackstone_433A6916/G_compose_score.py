# Original bed under John's voice: 81.1 BPM so the end card (32.55 s) lands on bar 11. Warm, low, out of the voice band.
import pretty_midi as pm, random
random.seed(5)
END = 32.55; BAR = END / 11; B = BAR / 4; BPM = 60 / B
m = pm.PrettyMIDI(initial_tempo=BPM)
pno = pm.Instrument(0); pad = pm.Instrument(89); stg = pm.Instrument(48); bass = pm.Instrument(33); dr = pm.Instrument(0, is_drum=True); vib = pm.Instrument(11)
def n(i, p, t, d, v): i.notes.append(pm.Note(velocity=max(1, min(127, int(v + random.randint(-4, 4)))), pitch=p, start=t, end=t + d))
CH = [([53, 57, 60, 64], 41), ([57, 60, 64, 67], 45), ([50, 53, 57, 60, 64], 38), ([46, 50, 53, 57], 34)]
for bar in range(13):
    t0 = bar * BAR; v, r = CH[bar % 4]
    if bar == 11: v, r = [53, 57, 60, 64, 67], 41
    if bar == 12: v, r = [48, 55, 60, 62, 64], 36
    for p in v: n(pad, p + 12, t0, BAR, 40 if bar < 11 else 52)
    if bar >= 4: 
        for p in v[:4]: n(stg, p + 12, t0, BAR, 38 + min(bar, 10) * 2 if bar < 11 else 66)
    if bar < 12:
        for k in range(8): n(pno, v[[0, 2, 1, 3, 2, 1, 3, 2][k] % len(v)] + 24, t0 + k * B / 2, B * 0.9, (50 if k % 2 == 0 else 40) + (10 if bar == 11 else 0))
    else:
        for k, p in enumerate(v + [72, 76]): n(pno, p + 12, t0 + k * 0.07, 4.0, 70 - k * 3)
    n(bass, r, t0, BAR * 0.9, 62 if bar < 11 else 84)
    if 2 <= bar < 11:
        for b in (0, 2): n(dr, 36, t0 + b * B, 0.1, 62)
        for k in range(8): n(dr, 70, t0 + k * B / 2, 0.05, 30 if k % 2 else 40)
    if bar == 11: n(dr, 49, t0, 2.0, 84); n(dr, 36, t0, 0.2, 96)
    if bar == 12: n(dr, 36, t0, 0.2, 90)
for k, p in enumerate([76, 81, 84, 88]): n(vib, p, 11 * BAR + k * B / 2, B * 1.5, 50)
for i in (pno, pad, stg, bass, dr, vib): m.instruments.append(i)
m.write(S + '/music/score_G.mid') if (S := '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad') else None
print('BPM %.1f bar %.3f' % (BPM, BAR))
