import json, subprocess, numpy as np, cv2
R='/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/'
M=[]
for f in 'abc':
    for m in json.load(open(R+'hype/moments_%s.json'%f))['moments']: M.append(m)
M=[m for m in M if m['out']-m['in']>=0.8]
CX=[0.25,0.42,0.58,0.75]
def grab(c,t):
    p=subprocess.run(['ffmpeg','-v','error','-ss','%.2f'%t,'-i',R+'sitevids/'+c+'.MP4','-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','-'],capture_output=True)
    return np.frombuffer(p.stdout,np.uint8).reshape(1080,1920,3)
out=[]; rows=[]
for i,m in enumerate(M):
    tm=(m['in']+m['out'])/2; im=grab(m['clip'],tm); im2=grab(m['clip'],min(tm+0.1,m['out']))
    g=cv2.cvtColor(im,cv2.COLOR_RGB2GRAY).astype(np.float32); g2=cv2.cvtColor(im2,cv2.COLOR_RGB2GRAY).astype(np.float32)
    th=[]
    for cx in CX:
        x0=int(min(max(cx*1920-304,0),1920-608)); cr=g[:,x0:x0+608]
        sharp=float(cv2.Laplacian(cv2.resize(cr,(304,540)),cv2.CV_32F).var())
        mot=float(np.abs(cr-g2[:,x0:x0+608]).mean())
        bright=float(cr.mean())
        t=cv2.resize(im[:,x0:x0+608],(120,213),interpolation=cv2.INTER_AREA).copy()
        cv2.putText(t,'%d'%int(cx*100),(3,14),cv2.FONT_HERSHEY_SIMPLEX,0.45,(255,255,0),1)
        cv2.putText(t,'s%d'%int(sharp),(60,14),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,255,0) if sharp>300 else (255,0,0),1)
        th.append(t); out.append(dict(id=i,cx=cx,sharp=round(sharp),motion=round(mot,2),bright=round(bright)))
    lab=np.zeros((22,480,3),np.uint8); cv2.putText(lab,'#%d %s %.1f-%.1f %s'%(i,m['clip'][-4:],m['in'],m['out'],m.get('type','')[:4]),(3,16),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1)
    rows.append(np.vstack([lab,np.hstack(th)]))
    m['id']=i
json.dump(M,open(R+'hype/pick/moments_all.json','w'),indent=0); json.dump(out,open(R+'hype/pick/crop_metrics.json','w'))
per=16; n=0
for s in range(0,len(rows),per):
    rr=rows[s:s+per]
    while len(rr)%2: rr.append(np.zeros_like(rows[0]))
    sheet=np.vstack([np.hstack([rr[j],np.zeros((rr[j].shape[0],8,3),np.uint8),rr[j+1]]) for j in range(0,len(rr),2)])
    cv2.imwrite(R+'hype/pick/sheet_%02d.jpg'%n,cv2.cvtColor(sheet,cv2.COLOR_RGB2BGR),[cv2.IMWRITE_JPEG_QUALITY,82]); n+=1
print(len(M),'moments',n,'sheets')
