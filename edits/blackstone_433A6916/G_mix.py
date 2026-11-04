# Video G sound: John's cleaned voice + original bed ducked ~17 dB under him + soft SFX on graphics; -14 LUFS / TP -1.5.
import subprocess, json
S='/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'; G=S+'/G/'; A=S+'/audio/pxb_sfx_%s.mp3'
TE=json.load(open(G+'segs.json'))['dur']; DUR=TE+4.2; TF, TV = 9.81, 27.54
cues=[('transition_whoosh',0.0,1.0,0.30),('whoosh_motion',3.15,0.9,0.25),('clean_pop',TF-0.05,1.0,0.30),('clean_pop',TF+2.5,0.85,0.22),
      ('clean_pop',TV-0.05,1.08,0.30),('transition_whoosh',TE+0.08,0.8,0.40),('clean_pop',TE+1.0,0.85,0.30)]
inp=['-i',G+'voiceG.wav','-i',S+'/music/score_G.wav']
fc=['[0:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur=%.3f,asplit=2[vo][key]'%DUR,
    '[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.1[mu]',
    '[mu][key]sidechaincompress=threshold=0.06:ratio=2.5:attack=25:release=450[duck]']
for k,(f,st,pf,g) in enumerate(cues):
    inp+=['-i',A%f]; pitch='asetrate=%d,'%int(48000*pf) if pf!=1 else ''
    fc.append('[%d:a]aresample=48000,aformat=channel_layouts=stereo,%saresample=48000,volume=%.2f,adelay=%d|%d[s%d]'%(k+2,pitch,g,int(max(0,st)*1000),int(max(0,st)*1000),k))
fc.append('[vo][duck]'+''.join('[s%d]'%k for k in range(len(cues)))+'amix=inputs=%d:normalize=0:duration=longest,atrim=0:%.3f[pre]'%(len(cues)+2,DUR))
subprocess.run(['ffmpeg','-v','error','-y']+inp+['-filter_complex',';'.join(fc),'-map','[pre]','-c:a','pcm_s24le',G+'mixG_pre.wav'],check=True)
r=subprocess.run(['ffmpeg','-hide_banner','-i',G+'mixG_pre.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True)
j=json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}')+1])
af='loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true,aresample=48000'%(j['input_i'],j['input_tp'],j['input_lra'],j['input_thresh'],j['target_offset'])
subprocess.run(['ffmpeg','-v','error','-y','-i',G+'mixG_pre.wav','-af',af,'-c:a','pcm_s24le',G+'mixG.wav'],check=True)
print('ok')
