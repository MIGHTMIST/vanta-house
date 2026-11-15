# One "adjustment layer" over every frame, from the owner's grade samples (R15 + the usable R12 looks):
# deep teal sky (darker at the top), teal shadows / warm highlights (split tone), earth tones a touch richer,
# greens (net, trees) muted, hi-vis kept as the brightest colour, lifted blacks (~10/255), soft highlight shoulder (~235).
import numpy as np, cv2
_x = np.linspace(0, 1, 256, dtype=np.float32)
_s = _x + 0.15 * np.sin(2 * np.pi * _x) * (-0.5)          # gentle S in the mids
_s = np.clip(_s, 0, 1)
_sh = np.where(_s > 0.78, 0.78 + (1 - np.exp(-(_s - 0.78) * 4.2)) / 4.2 * 0.9, _s)   # soft shoulder
TONE = (10 + _sh / _sh.max() * 225).astype(np.float32)     # 10 .. 235
def film_look(c, amt=1.0):
    x = np.clip(c, 0, 255).astype(np.uint8)
    hsv = cv2.cvtColor(x, cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    H, W = h.shape
    sky = ((h > 86) & (h < 132) & (s > 14) & (v > 95)).astype(np.float32)
    sky = cv2.GaussianBlur(sky, (0, 0), 4)
    grad = np.linspace(1.0, 0.55, H, dtype=np.float32)[:, None]          # stronger at the top of frame
    k = sky * grad
    h2 = h + (93 - h) * 0.6 * k
    s2 = s * (1 + 0.35 * k) + 10 * k
    v2 = v * (1 - 0.17 * k * grad)
    green = ((h > 46) & (h < 88)).astype(np.float32) * (1 - k)
    s2 = s2 * (1 - 0.25 * green)
    warm = ((h >= 3) & (h <= 24) & (s > 40)).astype(np.float32)
    s2 = s2 * (1 + 0.10 * warm)
    hsv2 = np.dstack([np.clip(h2, 0, 179), np.clip(s2, 0, 255), np.clip(v2, 0, 255)]).astype(np.uint8)
    y = cv2.cvtColor(hsv2, cv2.COLOR_HSV2RGB).astype(np.float32)
    L = y.mean(-1, keepdims=True) / 255
    shad = np.clip((0.42 - L) / 0.42, 0, 1) ** 1.3; high = np.clip((L - 0.62) / 0.38, 0, 1)
    y = y + shad * np.array([-9, 3, 7], np.float32) + high * np.array([5, 2, -5], np.float32)
    y = TONE[np.clip(y, 0, 255).astype(np.uint8)]
    return c * (1 - amt) + y * amt if amt < 1 else y
