# v2 core: decode source stretches small, optical-flow slow motion, full-picture layouts (no crop), effects helpers.
import subprocess, numpy as np, cv2
R = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/'
SV = R + 'sitevids/'
W, H, FPS = 1080, 1920, 30
PW, PH = 1024, 576                      # decoded picture size (whole 16:9 frame, nothing cropped)
_dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
_GY, _GX = np.mgrid[0:576, 0:1024].astype(np.float32)

def ease(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def eout(x): x = min(max(x, 0.0), 1.0); return 1 - (1 - x) ** 3

class Src:
    """frames of one clip stretch, decoded at 30 fps, whole picture at PWxPH (float32 RGB)."""
    cache = {}
    def __init__(self, clip, t0, t1):
        key = (clip, round(t0, 2), round(t1, 2))
        self.flows = {}
        if key in Src.cache: self.f, self.t0 = Src.cache[key]; return
        p = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '%.3f' % t0, '-i', SV + clip + '.MP4', '-t', '%.3f' % (t1 - t0 + 0.1),
                            '-vf', 'fps=30,scale=%d:%d:flags=area' % (PW, PH), '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'], capture_output=True)
        a = np.frombuffer(p.stdout, np.uint8); n = a.size // (PW * PH * 3)
        self.f = a[:n * PW * PH * 3].reshape(n, PH, PW, 3); self.t0 = t0
        self.flows = {}
        Src.cache[key] = (self.f, t0)
    def at(self, t):
        """frame at source time t (seconds), optical-flow interpolated between frames"""
        q = (t - self.t0) * FPS; i0 = int(np.floor(q)); a = q - i0
        i0 = min(max(i0, 0), len(self.f) - 1); i1 = min(i0 + 1, len(self.f) - 1)
        f0 = self.f[i0].astype(np.float32)
        if a < 0.04 or i1 == i0: return f0
        f1 = self.f[i1].astype(np.float32)
        if a > 0.96: return f1
        k = (i0, i1)
        if k not in self.flows:
            g0 = cv2.cvtColor(self.f[i0], cv2.COLOR_RGB2GRAY); g1 = cv2.cvtColor(self.f[i1], cv2.COLOR_RGB2GRAY)
            self.flows = {k: (_dis.calc(g0, g1, None), _dis.calc(g1, g0, None))}
        F01, F10 = self.flows[k]
        gy, gx = _GY, _GX
        w0 = cv2.remap(f0, gx + a * F10[..., 0], gy + a * F10[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        w1 = cv2.remap(f1, gx + (1 - a) * F01[..., 0], gy + (1 - a) * F01[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        return w0 * (1 - a) + w1 * a

def blur_fill(pic, dark=0.5):
    """vertical background: same picture scaled to cover 1080x1920, heavily blurred and darkened"""
    sm = cv2.resize(pic, (64, 36), interpolation=cv2.INTER_AREA)
    h = 192; w = int(round(64 * h / 36)); big = cv2.resize(sm, (w, h), interpolation=cv2.INTER_CUBIC)
    x0 = (w - 108) // 2; big = big[:, x0:x0 + 108]
    big = cv2.GaussianBlur(big, (0, 0), 3)
    return cv2.resize(big, (W, H), interpolation=cv2.INTER_CUBIC) * dark

def put(canvas, pic, x, y, w, border=3, shadow=True, scale_extra=1.0, dx=0.0, rot=0.0):
    """place the WHOLE picture (no crop) w px wide at top-left (x,y) with thin white border + soft shadow"""
    h = int(round(w * 9 / 16))
    s = w / PW * scale_extra
    M = cv2.getRotationMatrix2D((PW / 2, PH / 2), rot, s); M[0, 2] += x + w / 2 - PW / 2 + dx; M[1, 2] += y + h / 2 - PH / 2
    if shadow:
        m = np.zeros((H, W), np.float32); cv2.rectangle(m, (int(x + dx), int(y + 14)), (int(x + dx + w), int(y + h + 14)), 1, -1)
        m = cv2.GaussianBlur(m, (0, 0), 18) * 0.55; canvas *= (1 - m[..., None])
    if border:
        bp = cv2.copyMakeBorder(pic, border * 2, border * 2, border * 2, border * 2, cv2.BORDER_CONSTANT, value=(245, 245, 245))
        M2 = M.copy(); M2[0, 2] -= border * 2 * s; M2[1, 2] -= border * 2 * s
        src = bp
    else:
        src = pic; M2 = M
    lay = cv2.warpAffine(src, M2, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    msk = cv2.warpAffine(np.ones(src.shape[:2], np.float32), M2, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)[..., None]
    return canvas * (1 - msk) + lay * msk

def motion_blur_x(img, L):
    L = int(L) | 1
    if L < 3: return img
    return cv2.filter2D(img, -1, np.ones((1, L), np.float32) / L)

def halftone(pic, cell=9, ink=(30, 24, 20), paper=(232, 222, 202)):
    """newspaper-dot look (R2 title freeze): grey -> dot radius per cell, on paper colour"""
    g = cv2.cvtColor(pic.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    h, w = g.shape; out = np.ones((h, w, 3), np.float32) * np.array(paper, np.float32)
    sm = cv2.resize(g, (w // cell, h // cell), interpolation=cv2.INTER_AREA)
    for j in range(sm.shape[0]):
        for i in range(sm.shape[1]):
            r = (1 - sm[j, i]) * cell * 0.62
            if r > 0.6: cv2.circle(out, (i * cell + cell // 2, j * cell + cell // 2), int(round(r)), ink, -1, lineType=cv2.LINE_AA)
    return out

def halftone_fast(img, pitch=9.0, angle=45.0, ink=(43, 27, 16), paper=(233, 220, 188)):
    """R2 halftone sepia: rotated dot screen, dark brown dots on cream, vectorised (whole canvas, any size)"""
    h, w = img.shape[:2]
    g = cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    g = cv2.blur(g, (int(pitch), int(pitch)))
    g = np.clip((g - 0.06) / 0.88, 0, 1)
    key = (h, w, pitch, angle)
    if key not in _HT:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); a = np.deg2rad(angle)
        u = (xx * np.cos(a) + yy * np.sin(a)) / pitch; v = (-xx * np.sin(a) + yy * np.cos(a)) / pitch
        _HT[key] = np.sqrt((u - np.floor(u) - 0.5) ** 2 + (v - np.floor(v) - 0.5) ** 2) * pitch
    d = _HT[key]
    r = (1 - g) ** 0.85 * pitch * 0.74
    m = np.clip(r - d + 0.5, 0, 1)[..., None]
    return np.array(paper, np.float32) * (1 - m) + np.array(ink, np.float32) * m
_HT = {}
