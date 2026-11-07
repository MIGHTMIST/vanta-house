# face track for the interview: one detection every 0.5 s -> J/faces.json  [t, [(cx, cy, w) in 1920x1080 px ...]]
import json, subprocess, numpy as np, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
S = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'
det = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(base_options=BaseOptions(model_asset_path=S + '/models/blaze_face.tflite'), min_detection_confidence=0.4))
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', S + '/J/john_full.mp4', '-vf', 'fps=2,scale=960:540', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
out = []; i = 0
while True:
    b = p.stdout.read(960 * 540 * 3)
    if len(b) < 960 * 540 * 3: break
    a = np.frombuffer(b, np.uint8).reshape(540, 960, 3)
    r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=a))
    fs = [((d.bounding_box.origin_x + d.bounding_box.width / 2) * 2, (d.bounding_box.origin_y + d.bounding_box.height / 2) * 2, d.bounding_box.width * 2) for d in r.detections]
    out.append([i / 2, fs]); i += 1
json.dump(out, open(S + '/J/faces.json', 'w')); print(len(out))
