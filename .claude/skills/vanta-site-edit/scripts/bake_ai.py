# AI clip (480x832, 24 fps, already graded) -> 1080x1920: FSRCNN x2, lanczos to 1108x1920, centre crop 1080,
# brightness matched to the real source frame, sharpening that grows as the AI clip goes soft. Saved as near-lossless mp4.
import sys, glob, subprocess, numpy as np, cv2
H = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/hype/'
M = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/models/FSRCNN_x2.pb'
a = sys.argv[1]
sr = cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel(M); sr.setModel('fsrcnn', 2)
cap = cv2.VideoCapture(H + 'ai_out/%s.mp4' % a); F = []
while True:
    ok, f = cap.read()
    if not ok: break
    F.append(f)
S = cv2.VideoCapture(sorted(glob.glob(H + 'ai_src/%s*.mp4' % a))[0]).read()[1]
S = cv2.resize(S, (480, 853), interpolation=cv2.INTER_AREA)[10:842].astype(np.float64)
gain = (S.mean((0, 1)) + 1) / (F[0].astype(np.float64).mean((0, 1)) + 1)
lap = lambda x: cv2.Laplacian(cv2.cvtColor(x, cv2.COLOR_BGR2GRAY).astype(np.float32), cv2.CV_32F).var()
s0 = lap(F[0])
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1080x1920', '-r', '24', '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '11', '-pix_fmt', 'yuv420p', H + 'ai_up/%s.mp4' % a], stdin=subprocess.PIPE)
for i, f in enumerate(F):
    amt = float(np.clip(0.35 + 0.5 * (1 - lap(f) / s0), 0.35, 0.6))
    u = sr.upsample(f)
    u = cv2.resize(u, (1108, 1920), interpolation=cv2.INTER_LANCZOS4)[:, 14:1094].astype(np.float32)
    b = cv2.GaussianBlur(u, (0, 0), 1.2); u = u * (1 + amt) - b * amt
    u = np.clip(u * gain[None, None, :], 0, 255).astype(np.uint8)
    enc.stdin.write(u.tobytes())
enc.stdin.close(); enc.wait()
print(a, len(F), 'gain', gain.round(3), flush=True)
