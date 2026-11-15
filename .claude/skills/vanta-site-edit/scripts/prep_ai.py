# cleaned 9:16 source clips (720x1280, real speed, no sound) + first-frame stills for the AI camera-move version
import sys, subprocess, numpy as np, cv2
sys.path.insert(0, '.')
import grade as GR
from fillcore import SrcF
OUT = GR.R + 'hype/ai_src/'
SHOTS = [('A01_hook_worker_to_tower', 'GV3A9982', 1.8, 5.8, 0.30), ('A02_props_forest', 'GV3A0008', 0.0, 3.5, 0.42),
         ('A03_tower_balconies', 'GV3A9991', 2.4, 5.2, 0.41), ('A04_kampala_view', 'GV3A0032', 0.0, 3.3, 0.68),
         ('A05_crew_laying_blocks', 'GV3A0035', 0.5, 2.6, 0.50), ('A06_crew_slab', 'GV3A0036', 0.0, 3.0, 0.30),
         ('A07_rebar_forest', 'GV3A0021', 0.0, 2.5, 0.54), ('A08_tower_with_workers', 'GV3A0044', 0.2, 3.5, 0.46),
         ('A09_rebar_machine', 'GV3A9994', 2.0, 4.5, 0.43), ('A10_tower_low_angle', 'GV3A9982', 0.0, 1.5, 0.49),
         ('A11_end_tower', 'GV3A9990', 0.2, 5.2, 0.46), ('A12_facade', 'GV3A9980', 23.4, 25.3, 0.55)]
for name, c, a, b, cx in SHOTS:
    s = SrcF(c, a, b); p = GR.params(c, a, b)
    n = int((b - a) * 30) - 2
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '720x1280', '-r', '30', '-i', '-',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-maxrate', '4M', '-bufsize', '8M', '-pix_fmt', 'yuv420p',
                            '-movflags', '+faststart', OUT + name + '.mp4'], stdin=subprocess.PIPE)
    for k in range(n):
        img = s.crop(a + k / 30, cx * 1920 - 304, 0, 608, 1080, 720, 1280)
        g = np.clip(GR.sharpen(GR.grade(img, p), 0.25), 0, 255).astype(np.uint8)
        if k == 0: cv2.imwrite(OUT + name + '_still.jpg', cv2.cvtColor(g, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
        enc.stdin.write(g.tobytes())
    enc.stdin.close(); enc.wait(); print(name, n, flush=True)
