# contact sheet per AI clip: real source frame 0 | 9 AI frames evenly spread (incl. last)
import cv2, numpy as np, glob, sys, os
H='/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/hype'
os.makedirs(H+'/ai_out/sheets', exist_ok=True)
def frames(p):
    c=cv2.VideoCapture(p); out=[]
    while True:
        ok,f=c.read()
        if not ok: break
        out.append(f)
    return out
for n in range(1,13):
    a='A%02d'%n
    src=sorted(glob.glob(H+'/ai_src/%s*.mp4'%a))[0]
    S=frames(src); O=frames(H+'/ai_out/%s.mp4'%a)
    tw,th=240,416
    tiles=[cv2.resize(S[0],(tw,th),interpolation=cv2.INTER_AREA)]
    cv2.putText(tiles[0],'REAL',(6,24),0,0.7,(0,255,255),2)
    idx=np.linspace(0,len(O)-1,9).astype(int)
    for i in idx:
        t=cv2.resize(O[i],(tw,th),interpolation=cv2.INTER_AREA)
        cv2.putText(t,'%.2fs'%(i/24),(6,24),0,0.6,(255,255,255),2); tiles.append(t)
    row=np.hstack(tiles)
    cv2.imwrite(H+'/ai_out/sheets/%s.jpg'%a,row,[cv2.IMWRITE_JPEG_QUALITY,88])
    # flicker + sharpness
    g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in O]
    mj=max(abs(float(g[i].mean())-float(g[i-1].mean())) for i in range(1,len(g)))
    sh=[cv2.Laplacian(x.astype(np.float32),cv2.CV_32F).var() for x in g]
    s0=cv2.Laplacian(cv2.cvtColor(cv2.resize(S[0],(480,832),interpolation=cv2.INTER_AREA),cv2.COLOR_BGR2GRAY).astype(np.float32),cv2.CV_32F).var()
    print(a, len(O),'frames  maxjump %.1f'%mj, ' sharp ai first/mid/last %.0f/%.0f/%.0f  real@480 %.0f'%(sh[0],sh[len(sh)//2],sh[-1],s0))
