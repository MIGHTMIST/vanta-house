# Full-screen 9:16 from 16:9 site footage: full-resolution decode, crop window that pans across the frame
# (so the whole building is still shown over the shot), optical-flow slow motion on the crop.
import subprocess, numpy as np, cv2
from v2core import SV, W, H, FPS, ease
FW, FH = 1920, 1080
_dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_FAST)

class SrcF:
    cache = {}
    def __init__(self, clip, t0, t1):
        key = (clip, round(t0, 2), round(t1, 2))
        if key not in SrcF.cache:
            p = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '%.3f' % t0, '-i', SV + clip + '.MP4', '-t', '%.3f' % (t1 - t0 + 0.1),
                                '-vf', 'fps=30,scale=%d:%d' % (FW, FH), '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'], capture_output=True)
            a = np.frombuffer(p.stdout, np.uint8); n = a.size // (FW * FH * 3)
            SrcF.cache[key] = (a[:n * FW * FH * 3].reshape(n, FH, FW, 3), t0)
            while len(SrcF.cache) > 4: del SrcF.cache[next(iter(SrcF.cache))]
        self.f, self.t0 = SrcF.cache[key]

    def crop(self, t, x0, y0, cw, ch, ow, oh):
        """crop window (x0,y0,cw,ch) in 1920x1080 source at time t, flow-interpolated, resized to ow x oh"""
        q = (t - self.t0) * FPS; i0 = int(np.floor(q)); a = q - i0
        i0 = min(max(i0, 0), len(self.f) - 1); i1 = min(i0 + 1, len(self.f) - 1)
        x0 = int(round(min(max(x0, 0), FW - cw))); y0 = int(round(min(max(y0, 0), FH - ch)))
        A = self.f[i0, y0:y0 + ch, x0:x0 + cw]
        if a < 0.05 or i1 == i0: out = A.astype(np.float32)
        elif a > 0.95: out = self.f[i1, y0:y0 + ch, x0:x0 + cw].astype(np.float32)
        else:
            Bf = self.f[i1, y0:y0 + ch, x0:x0 + cw]
            s = 0.5; sw, sh = int(cw * s), int(ch * s)
            g0 = cv2.cvtColor(cv2.resize(A, (sw, sh), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
            g1 = cv2.cvtColor(cv2.resize(Bf, (sw, sh), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
            F01 = cv2.resize(_dis.calc(g0, g1, None), (cw, ch)) / s; F10 = cv2.resize(_dis.calc(g1, g0, None), (cw, ch)) / s
            gy, gx = np.mgrid[0:ch, 0:cw].astype(np.float32)
            w0 = cv2.remap(A.astype(np.float32), gx + a * F10[..., 0], gy + a * F10[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            w1 = cv2.remap(Bf.astype(np.float32), gx + (1 - a) * F01[..., 0], gy + (1 - a) * F01[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            out = w0 * (1 - a) + w1 * a
        return cv2.resize(out, (ow, oh), interpolation=cv2.INTER_CUBIC if ow > cw else cv2.INTER_AREA)

def fill(src, t, cx, ow=W, oh=H):
    """full-screen window of aspect ow:oh, full source height, centred at cx (fraction of width)"""
    ch = FH; cw = int(round(FH * ow / oh))
    if cw > FW: cw = FW; ch = int(round(FW * oh / ow))
    return src.crop(t, cx * FW - cw / 2, (FH - ch) / 2, cw, ch, ow, oh)

def pan_cx(u, p):
    """crop centre along a shot: p = (cx_start, cx_end); u = 0..1 shot progress (eased)"""
    return p[0] + (p[1] - p[0]) * ease(u)
