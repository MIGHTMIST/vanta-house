# Original score for the Vanta House short (Modern Clean). 114 BPM, one bar = 2.105 s, cuts land on bar lines.
# Bar 0 hook (Fmaj7) - bar 1 Blackstone reveal (Gsus4-G, build) - bar 2 DROP on the first render (Am9)
# bar 3 Fmaj7 - bar 4 C-G + fill - bar 5 end card (Fmaj7, crash) - bar 6 final Cadd9, ring out.
import pretty_midi as pm, random
random.seed(7)
BPM = 114; B = 60 / BPM; BAR = 4 * B
mid = pm.PrettyMIDI(initial_tempo=BPM)
piano = pm.Instrument(program=0, name='piano'); pad = pm.Instrument(program=89, name='warm pad')
strings = pm.Instrument(program=48, name='strings'); bass = pm.Instrument(program=33, name='finger bass')
bell = pm.Instrument(program=11, name='vibes'); revcym = pm.Instrument(program=119, name='reverse cymbal')
drums = pm.Instrument(program=0, is_drum=True, name='drums')
def n(inst, pitch, t0, dur, vel):
    inst.notes.append(pm.Note(velocity=max(1, min(127, int(vel + random.randint(-5, 5)))), pitch=pitch, start=t0, end=t0 + dur))
CH = {'Fmaj7': [53, 57, 60, 64, 69], 'Gsus4': [55, 60, 62, 67, 72], 'G': [55, 59, 62, 67, 71], 'Am9': [57, 60, 64, 67, 71],
      'C': [55, 60, 64, 67, 72], 'Cadd9': [48, 55, 60, 62, 64, 67]}
ROOT = {'Fmaj7': 41, 'Gsus4': 43, 'G': 43, 'Am9': 45, 'C': 36, 'Cadd9': 36}
# (bar, beat offset, chord, beats)
PLAN = [(0, 0, 'Fmaj7', 4), (1, 0, 'Gsus4', 2), (1, 2, 'G', 2), (2, 0, 'Am9', 4), (3, 0, 'Fmaj7', 4),
        (4, 0, 'C', 2), (4, 2, 'G', 2), (5, 0, 'Fmaj7', 4), (6, 0, 'Cadd9', 6)]
ARP = [0, 2, 1, 3, 2, 4, 3, 2]
for bar, off, ch, beats in PLAN:
    t0 = bar * BAR + off * B; v = CH[ch]; full = bar >= 2
    # pad + strings (sustained)
    for p in v: n(pad, p, t0, beats * B, 46 if not full else 52)
    if full:
        for p in v[:4]: n(strings, p + 12, t0, beats * B, 58 if bar < 5 else 66)
    # piano: 8th-note arpeggio one octave up (ring), final bar = rolled chord
    if ch == 'Cadd9':
        for k, p in enumerate(v + [72, 76, 79]): n(piano, p + (12 if p < 60 else 0), t0 + k * 0.06, 4.5, 78 - k * 2)
    else:
        for k in range(int(beats * 2)):
            p = v[ARP[k % 8] % len(v)] + 12
            n(piano, p, t0 + k * B / 2, B * 0.9, (66 if k % 2 == 0 else 54) + (6 if full else 0))
    # bass from the drop
    if full and ch != 'Cadd9':
        r = ROOT[ch]
        for k, (pos, ln, vel) in enumerate([(0, 0.75, 92), (0.75, 0.25, 70), (1.5, 0.5, 84), (2.5, 0.5, 80), (3.0, 0.5, 88), (3.5, 0.5, 74)]):
            if pos < beats: n(bass, r, t0 + pos * B, ln * B, vel)
    if ch == 'Cadd9': n(bass, 36, t0, 3.5, 96)
# vibes sparkle on the hook and on the end card
for k, p in enumerate([76, 81, 84, 88]): n(bell, p, 0.0 + k * B / 2, B * 1.5, 52)
for k, p in enumerate([77, 81, 84, 88]): n(bell, p, 5 * BAR + k * B / 2, B * 1.5, 56)
# reverse cymbal into the drop (ends exactly on bar 2)
n(revcym, 60, 2 * BAR - 2 * B, 2 * B, 90)
# drums
K, SN, CL, HH, OH, CR, SH, T1, T2, T3 = 36, 38, 39, 42, 46, 49, 70, 50, 47, 45
for bar in range(0, 7):
    t0 = bar * BAR
    for k in range(16):                                   # shaker 16ths all the way (life from frame 1)
        if bar == 6 and k > 3: break
        n(drums, SH, t0 + k * B / 4, 0.05, (58 if k % 4 == 0 else 40) + (8 if bar >= 2 else 0))
    if bar < 2:
        n(drums, K, t0, 0.1, 70)                          # soft pulse on 1 in the intro
        if bar == 1:
            for k in range(8): n(drums, SN, t0 + 2 * B + k * B / 4, 0.05, 30 + k * 9)   # small snare build
    elif bar < 6:
        for b in (0, 1.5, 2, 3.5): n(drums, K, t0 + b * B, 0.1, 100 if b in (0, 2) else 82)
        for b in (1, 3): n(drums, CL, t0 + b * B, 0.1, 84); n(drums, SN, t0 + b * B, 0.1, 52)
        for k in range(8): n(drums, HH if k != 7 else OH, t0 + k * B / 2, 0.05, 62 if k % 2 else 48)
        if bar in (2, 5): n(drums, CR, t0, 1.5, 98)
        if bar == 4:
            for k, tm in enumerate([T1, T1, T2, T3]): n(drums, tm, t0 + 3 * B + k * B / 4, 0.1, 80 + k * 6)
    else:
        n(drums, K, t0, 0.2, 104); n(drums, CR, t0, 2.5, 100)
for inst in (piano, pad, strings, bass, bell, revcym, drums): mid.instruments.append(inst)
out = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/music/vanta_score.mid'
mid.write(out); print('bars 7, end of last note %.2fs' % mid.get_end_time(), 'bar len %.4f' % BAR)
