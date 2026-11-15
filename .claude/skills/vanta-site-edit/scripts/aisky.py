import cv2, numpy as np
def sky_mask_blue(img):
    """sky mask for already-graded frames: flat, bluish, fairly bright, touching the top edge"""
    h, w = img.shape[:2]
    sm = cv2.resize(img, (w // 4, h // 4), interpolation=cv2.INTER_AREA) / 255.0
    L = sm.mean(-1)
    tex = np.abs(cv2.Laplacian(cv2.GaussianBlur(L.astype(np.float32), (0, 0), 1.0), cv2.CV_32F))
    blue = sm[..., 2] - sm[..., 0]
    bg = sm[..., 2] - sm[..., 1]
    cand = ((tex < 0.035) & (blue > 0.05) & (bg > 0.04) & (L > 0.42)).astype(np.uint8)
    n, lab = cv2.connectedComponents(cand)
    top = set(np.unique(lab[0])) - {0}
    if not top: return np.zeros((h, w), np.float32)
    m = np.isin(lab, list(top)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    m = cv2.resize(m.astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
    return np.clip(cv2.GaussianBlur(m, (0, 0), 1.0), 0, 1)
