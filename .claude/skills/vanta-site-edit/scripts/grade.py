# Per-clip clean-up grade for the site footage (16 Nov): exposure, white balance, highlight roll-off,
# blown-sky repair (soft blue-grey sky gradient), local contrast, vibrance, gentle sharpen.
# Parameters are measured once per clip stretch from sampled frames, so each shot is corrected on its own terms
# and all shots end up matching each other.
import numpy as np, cv2, json, os, subprocess
R = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/'
CACHE = R + 'hype/grade_params.json'
_P = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
_clahe = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(8, 8))

def _sample(clip, a, b, n=6):
    fr = []
    for k in range(n):
        t = a + (b - a) * (k + 0.5) / n
        p = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '%.2f' % t, '-i', R + 'sitevids/' + clip + '.MP4', '-frames:v', '1',
                            '-vf', 'scale=480:270', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'], capture_output=True)
        if len(p.stdout) == 480 * 270 * 3: fr.append(np.frombuffer(p.stdout, np.uint8).reshape(270, 480, 3))
    return fr

def measure(frames):
    x = np.stack(frames).astype(np.float32) / 255
    L = x.mean(-1)
    sky = L > 0.93
    body = ~sky
    lo = float(np.percentile(L[body], 0.7)) if body.any() else 0.02
    hi = float(np.percentile(L[body], 99.3)) if body.any() else 0.95
    med = float(np.median(L[body])) if body.any() else 0.5
    # white balance from mid-tones (grey world on 0.15..0.85 luminance, not saturated)
    sat = x.max(-1) - x.min(-1)
    m = body & (L > 0.15) & (L < 0.85) & (sat < 0.25)
    mean = x[m].mean(0) if m.sum() > 500 else x[body].mean(0)
    g = mean.mean() / np.maximum(mean, 1e-3)
    g = 1 + (g - 1) * 0.55                                     # half-strength correction, keeps the scene's own warmth
    g = g * np.array([1.012, 1.0, 0.985])                      # slight warm bias (sunlit concrete)
    skyfrac = float(sky.mean())
    skytop = float((L[:, :max(2, L.shape[1] // 12)] > 0.86).mean())
    return dict(lo=lo, hi=hi, med=med, wb=[float(v) for v in g], sky=skyfrac, skytop=skytop)

def params(clip, a, b):
    k = '%s@%.2f-%.2f' % (clip, a, b)
    if k not in _P:
        fr = _sample(clip, a, b)
        _P[k] = measure(fr) if fr else dict(lo=0.02, hi=0.95, med=0.45, wb=[1, 1, 1], sky=0)
        json.dump(_P, open(CACHE, 'w'))
    return _P[k]

def photo_params(path, img):
    k = 'PHOTO:' + path
    if k not in _P:
        sm = cv2.resize(img, (480, int(480 * img.shape[0] / img.shape[1])), interpolation=cv2.INTER_AREA).astype(np.uint8)
        _P[k] = measure([sm]); json.dump(_P, open(CACHE, 'w'))
    return _P[k]

def _curve(p):
    """tone curve as a 1024-entry LUT on 0..1: black point, mid-tone gamma to target, soft highlight shoulder"""
    lo, hi, med = p['lo'], max(p['hi'], p['lo'] + 0.2), p['med']
    x = np.linspace(0, 1, 1024, dtype=np.float32)
    y = np.clip((x - lo * 0.85) / (min(hi, 0.985) - lo * 0.85), 0, 1.2)
    mn = np.clip((med - lo * 0.85) / (min(hi, 0.985) - lo * 0.85), 0.05, 0.95)
    target = 0.46
    gam = np.clip(np.log(target) / np.log(mn), 0.7, 1.45)
    y = np.power(np.clip(y, 0, None), gam)
    k = 0.78                                                    # shoulder: compress above k so highlights keep shape
    over = y > k
    y[over] = k + (1 - k) * (1 - np.exp(-(y[over] - k) / (1 - k) * 1.6)) / (1 - np.exp(-1.6 * (1.2 - k) / (1 - k)))
    y = 0.018 + y * (0.975 - 0.018)                             # lifted black, soft white
    return y.astype(np.float32)

def sky_fix(img, strength=0.55):
    """blown / near-white sky -> soft blue-grey gradient, only on bright flat areas connected to the top edge"""
    h, w = img.shape[:2]
    L = (img.mean(-1) / 255).astype(np.float32)
    sm = cv2.resize(L, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    tex = np.abs(cv2.Laplacian(cv2.GaussianBlur(sm, (0, 0), 1.0), cv2.CV_32F))
    cand = ((sm > 0.86) & (tex < 0.035)).astype(np.uint8)
    n, lab = cv2.connectedComponents(cand)
    top = set(np.unique(lab[0])) - {0}
    if not top: return img
    mask = np.isin(lab, list(top)).astype(np.uint8)
    near = cv2.dilate(mask, np.ones((5, 5), np.uint8))
    mask = cv2.resize(mask.astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
    near = cv2.resize(near.astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
    fringe = near * np.clip((L - 0.84) / 0.08, 0, 1)            # white fringe between scaffold bars next to the sky
    mask = np.maximum(mask, fringe)
    mask = cv2.GaussianBlur(mask, (0, 0), 1.2)[..., None]
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    skycol = np.array([138, 174, 196], np.float32) * (1 - yy) + np.array([210, 224, 230], np.float32) * yy   # deeper at top
    # keep cloud texture: multiply the gradient by the original luminance variation
    m2 = mask[..., 0]
    base = cv2.GaussianBlur(L * m2, (0, 0), 25) / np.maximum(cv2.GaussianBlur(m2, (0, 0), 25), 1e-3)
    detail = ((L - base) * m2)[..., None] * 255 * 1.6
    sky = skycol + detail
    return img * (1 - mask * strength) + sky * mask * strength

def grade(img, p, sky=True):
    """img float32 RGB 0..255 (any size) -> graded float32"""
    x = img.astype(np.float32) * np.array(p['wb'], np.float32)
    lut = _curve(p)
    Y = np.clip(x.mean(-1) / 255, 0, 1)
    Yn = lut[np.clip((Y * 1023).astype(np.int32), 0, 1023)]
    x = x * (Yn / np.maximum(Y, 1e-3))[..., None]              # tone-map luminance, keep colour ratios
    x = np.clip(x, 0, 255)
    if sky and p.get('sky', 0) > 0.02 and p.get('skytop', 1) > 0.4: x = np.clip(sky_fix(x), 0, 255)
    lab = cv2.cvtColor(x.astype(np.uint8), cv2.COLOR_RGB2LAB)
    l2 = _clahe.apply(lab[..., 0])
    lab[..., 0] = cv2.addWeighted(lab[..., 0], 0.6, l2, 0.4, 0)  # local contrast, 40%
    x = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB).astype(np.float32)
    mx, mn = x.max(-1, keepdims=True), x.min(-1, keepdims=True)
    s = (mx - mn) / np.maximum(mx, 1)
    gray = x.mean(-1, keepdims=True)
    x = gray + (x - gray) * (1 + 0.28 * (1 - s))                # vibrance: lift dull colours more than vivid ones
    return hivis(np.clip(x, 0, 255))

def hivis(x, k=0.30):
    """R15 trick: hi-vis vests / helmets (yellow-green, orange) a little brighter and richer than everything else"""
    hsv = cv2.cvtColor(x.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    m = ((h >= 22) & (h <= 44) & (s > 100) & (v > 110)).astype(np.float32) + \
        0.5 * ((h >= 5) & (h <= 18) & (s > 140) & (v > 120)).astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 1.5)
    hsv[..., 1] = np.clip(s * (1 + k * m), 0, 255); hsv[..., 2] = np.clip(v * (1 + 0.10 * k * m), 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)

def selective(x, amt):
    """R15 intro: grey picture with only hi-vis kept in colour; amt 1 = selective, 0 = full colour"""
    if amt <= 0: return x
    hsv = cv2.cvtColor(np.clip(x, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    m = (((hsv[..., 0] >= 5) & (hsv[..., 0] <= 45) & (hsv[..., 1] > 110) & (hsv[..., 2] > 90))).astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 2.5)[..., None]
    g = x.mean(-1, keepdims=True) * 1.06 - 6
    d = g * (1 - m) + x * m
    return x * (1 - amt) + d * amt

def sharpen(img, amt=0.35):
    return np.clip(img + (img - cv2.GaussianBlur(img, (0, 0), 1.2)) * amt, 0, 255)

def sky_mask(img, thr=0.80):
    """soft 0..1 mask of the open sky (bright, flat, touching the top edge) at img size, for text-behind-building"""
    h, w = img.shape[:2]
    L = (img.mean(-1) / 255).astype(np.float32)
    sm = cv2.resize(L, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    tex = np.abs(cv2.Laplacian(cv2.GaussianBlur(sm, (0, 0), 1.0), cv2.CV_32F))
    cand = ((sm > thr) & (tex < 0.04)).astype(np.uint8)
    n, lab = cv2.connectedComponents(cand)
    top = set(np.unique(lab[0])) - {0}
    if not top: return np.zeros((h, w), np.float32)
    m = np.isin(lab, list(top)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    m = cv2.resize(m.astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
    return np.clip(cv2.GaussianBlur(m, (0, 0), 1.0), 0, 1)
