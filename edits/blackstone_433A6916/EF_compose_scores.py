# Two original scores, written to the cut plans of videos E and F.
import pretty_midi as pm, random, sys
OUT = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/music/'
def mk(bpm):
    random.seed(11); m = pm.PrettyMIDI(initial_tempo=bpm); return m
def n(inst, p, t0, d, v):
    inst.notes.append(pm.Note(velocity=max(1, min(127, int(v + random.randint(-4, 4)))), pitch=p, start=t0, end=t0 + d))

# ---------------- E: "Not rendered. Real." 100 BPM, D minor documentary pulse -> F major at the invitation
def score_E():
    BPM = 100; B = 60 / BPM; BAR = 4 * B; m = mk(BPM)
    gtr = pm.Instrument(28, name='muted gtr'); piz = pm.Instrument(45, name='pizz'); bass = pm.Instrument(38, name='synth bass')
    pad = pm.Instrument(91, name='polysynth pad'); strings = pm.Instrument(49, name='slow strings'); timp = pm.Instrument(47, name='timpani')
    piano = pm.Instrument(0, name='piano'); dr = pm.Instrument(0, is_drum=True)
    # bars: 0 hook | 1-3 photo log | 4 John | 5-6 invitation (major)
    PLAN = [('Dm', [50, 53, 57, 62], 38), ('Bb', [50, 53, 58, 62], 34), ('F', [48, 53, 57, 60], 41), ('C', [48, 52, 55, 60], 36),
            ('Dm', [50, 53, 57, 62], 38), ('F', [53, 57, 60, 65], 41), ('Fadd9', [53, 57, 60, 67, 72], 41)]
    for bar, (name, v, root) in enumerate(PLAN):
        t0 = bar * BAR
        for p in v: n(pad, p + 12, t0, BAR, 42 if bar < 5 else 50)
        if bar >= 1 and bar < 6:
            for k in range(8):                                      # muted guitar 8th ostinato
                n(gtr, v[[0, 2, 1, 3, 2, 1, 3, 2][k]] + 12, t0 + k * B / 2, B * 0.35, 70 if k % 2 == 0 else 56)
        if bar >= 2 and bar < 6:
            for k in range(4): n(piz, v[k % len(v)] + 24, t0 + k * B + B / 2, B * 0.3, 60)
        if bar >= 1 and bar < 6:
            for pos in (0, 1.5, 2, 3.5): n(bass, root, t0 + pos * B, B * 0.45, 92 if pos in (0, 2) else 76)
        if bar >= 4: 
            for p in v: n(strings, p + 12, t0, BAR, 62 if bar < 6 else 70)
        if bar >= 5:                                               # piano melody, hopeful
            mel = [72, 74, 77, 76] if bar == 5 else [77, 79, 81]
            for k, p in enumerate(mel): n(piano, p, t0 + k * B, B * 1.2 if bar == 5 else 2.4, 70)
        if bar == 6: n(bass, root - 12, t0, 3.5, 92)
    # hook hits (bar 0): timpani + low piano on the three title words
    for k, tt in enumerate([0.0, B * 1.0, B * 2.0]):
        n(timp, 38, tt, 0.6, 110 - k * 6); n(piano, 26, tt, 1.2, 100); n(piano, 38, tt, 1.2, 90)
    # drums
    K, RIM, CL, HH, CR, SH = 36, 37, 39, 42, 49, 82
    for bar in range(7):
        t0 = bar * BAR
        if bar == 0:
            for k in range(3): n(dr, K, t0 + k * B, 0.1, 112)
            for k in range(4): n(dr, HH, t0 + 3 * B + k * B / 4, 0.05, 40 + k * 12)     # tick-tick into the log
        elif bar < 6:
            for b in (0, 0.75, 2, 2.75): n(dr, K, t0 + b * B, 0.1, 100 if b in (0, 2) else 78)   # heartbeat
            for b in (1, 3): n(dr, RIM, t0 + b * B, 0.1, 80); n(dr, CL, t0 + b * B, 0.1, 60 if bar >= 4 else 0)
            for k in range(16): n(dr, SH, t0 + k * B / 4, 0.04, 46 if k % 2 else 60)
            if bar in (1, 4, 5): n(dr, CR, t0, 1.2, 84)
        else:
            n(dr, K, t0, 0.2, 100); n(dr, CR, t0, 2.5, 92)
    for i in (gtr, piz, bass, pad, strings, timp, piano, dr): m.instruments.append(i)
    m.write(OUT + 'score_E.mid'); return BAR

# ---------------- F: "Imagined vs Real" 96 BPM, D major, music box dream -> strings + drums for the real
def score_F():
    BPM = 96; B = 60 / BPM; BAR = 4 * B; m = mk(BPM)
    box = pm.Instrument(10, name='music box'); cel = pm.Instrument(8, name='celesta'); pad = pm.Instrument(88, name='fantasia pad')
    strings = pm.Instrument(48, name='strings'); cello = pm.Instrument(42, name='cello'); piano = pm.Instrument(0, name='piano')
    timp = pm.Instrument(47, name='timpani'); horn = pm.Instrument(60, name='french horn'); dr = pm.Instrument(0, is_drum=True)
    # bars: 0 hook | 1-3 three pairs | 4 John | 5 invitation | 6 resolve
    PLAN = [('Dmaj7', [50, 54, 57, 61], 38), ('Bm9', [47, 50, 54, 57, 61], 35), ('Gmaj7', [43, 47, 50, 54], 31),
            ('A6', [45, 49, 52, 54], 33), ('Bm7', [47, 50, 54, 57], 35), ('Gmaj9', [43, 47, 50, 54, 57], 31), ('Dadd9', [50, 54, 57, 64], 38)]
    MEL = {0: [78, 76, 73, 69], 1: [78, 76, 74, 73], 2: [74, 76, 78, 81], 3: [81, 79, 78, 76]}
    for bar, (name, v, root) in enumerate(PLAN):
        t0 = bar * BAR
        for p in v: n(pad, p + 12, t0, BAR, 44)
        if bar <= 3:                                                # music box: the imagined
            for k, p in enumerate(MEL[bar]): n(box, p, t0 + k * B, B * 1.6, 66 - bar * 3)
            for k in range(8): n(cel, v[k % len(v)] + 24, t0 + k * B / 2 + B / 4, B * 0.4, 38)
        if bar >= 1:                                                # strings grow with the real
            for p in v[:4]: n(strings, p + 12, t0, BAR, 46 + bar * 4)
            n(cello, root, t0, BAR, 54 + bar * 3)
        if bar >= 4:
            for k in range(8): n(piano, v[[0, 2, 1, 3, 2, 1, 3, 2][k] % len(v)] + 24, t0 + k * B / 2, B * 0.5, 64)
            n(horn, v[1] + 12, t0, BAR, 70)
        if bar == 6: n(cello, root - 12, t0, 4.0, 80)
    for k in range(12): n(timp, 45, 3 * BAR + 3 * B + k * B / 12, 0.06, 50 + k * 5)   # roll into John
    K, SN, HH, CR, TOM = 36, 38, 42, 49, 45
    for bar in range(4, 7):
        t0 = bar * BAR
        if bar < 6:
            for b in (0, 2.5): n(dr, K, t0 + b * B, 0.1, 104)
            for b in (1, 3): n(dr, SN, t0 + b * B, 0.1, 78)
            for k in range(8): n(dr, HH, t0 + k * B / 2, 0.05, 50 if k % 2 else 62)
            n(dr, CR, t0, 1.5, 92)
        else:
            n(dr, K, t0, 0.2, 108); n(dr, CR, t0, 3.0, 96); n(timp, 38, t0, 1.5, 104)
    for i in (box, cel, pad, strings, cello, piano, timp, horn, dr): m.instruments.append(i)
    m.write(OUT + 'score_F.mid'); return BAR

print('E bar %.4f s' % score_E(), ' F bar %.4f s' % score_F())
