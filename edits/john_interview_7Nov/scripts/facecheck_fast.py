# face check: compare every face in every photo with John's face from the interview (dlib 128-d, distance < 0.5 = same person)
import dlib, numpy as np, glob, os, sys, subprocess, json
from PIL import Image, ImageOps
M = sys.argv[1]; S = sys.argv[2]
det = dlib.cnn_face_detection_model_v1(M + '/mmod_human_face_detector.dat'); hog = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(M + '/shape_predictor_5_face_landmarks.dat'); rec = dlib.face_recognition_model_v1(M + '/dlib_face_recognition_resnet_model_v1.dat')
def load(p, maxw=1100):
    im = ImageOps.exif_transpose(Image.open(p)).convert('RGB'); 
    if im.width > maxw: im = im.resize((maxw, int(im.height * maxw / im.width)))
    return np.array(im)
def faces(a):
    rs = list(hog(a, 1))
    out = []
    for r in rs:
        if r.width() < 40: continue
        out.append((r, np.array(rec.compute_face_descriptor(a, sp(a, r), 1))))
    return out
# reference: John in the interview (wide-section crops and medium close)
ref = []
for t in [130, 175, 215, 300, 345, 445, 500, 540, 627]:
    f = S + '/facecheck/ref_%d.png' % t
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', S + '/J/john_full.mp4', '-frames:v', '1', f])
    a = load(f, 1920); fs = faces(a)
    if not fs: continue
    # John sits left in the wide shot (host right): take the face nearest x = 440 / the only face
    r, d = min(fs, key=lambda x: abs((x[0].left() + x[0].right()) / 2 - (440 if t < 470 else 900)))
    ref.append(d)
print(flush=True, *['reference faces:', len(ref)])
R = np.array(ref)
res = {}
for p in sorted(sys.argv[3:]):
    try: a = load(p)
    except Exception as e: print(p, 'ERR', e, flush=True); continue
    fs = faces(a)
    ds = [float(np.linalg.norm(R - d, axis=1).mean()) for r, d in fs]
    best = min(ds) if ds else None
    res[os.path.basename(p)] = dict(faces=len(fs), best=best, path=p)
    print(flush=True, *['%-34s faces=%d  best=%s' % (os.path.basename(p)[:34], len(fs), '%.3f' % best if best is not None else '-')])
json.dump(res, open(S + '/facecheck/result.json', 'w'), indent=1)
