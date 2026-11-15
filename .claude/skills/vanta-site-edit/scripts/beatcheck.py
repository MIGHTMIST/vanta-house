# every hard cut in the finished video vs the beat grid: prints offsets in ms (+ = cut after the beat)
import sys, os, numpy as np, cv2
VID = os.environ['VID']; BT = 0.723; PH0 = 0.230
M0 = 0.0 if VID == 'n2' else PH0 + BT * 16
c = cv2.VideoCapture(sys.argv[1]); prev = None; d = []
while True:
    ok, f = c.read()
    if not ok: break
    g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (90, 160)).astype(np.float32)
    d.append(0.0 if prev is None else float(np.abs(g - prev).mean())); prev = g
d = np.array(d); med = np.median(d)
cuts = [i for i in range(1, len(d)) if d[i] > max(11, 3.2 * med) and d[i] >= d[max(i - 1, 0)] and d[i] >= d[min(i + 1, len(d) - 1)]]
offs = []
for i in cuts:
    ts = i / 30 + M0; k = round((ts - PH0) / BT * 4) / 4          # nearest quarter beat
    offs.append((i, round(k, 2), round((ts - (PH0 + BT * k)) * 1000)))
on = [o for o in offs if o[1] == int(o[1])]
print('cuts found', len(offs), '| on whole beats', len(on), '| max |offset| ms on beats', max([abs(o[2]) for o in on] or [0]))
print('off-beat changes (frame, beat, ms):', [o for o in offs if o[1] != int(o[1])][:20])
