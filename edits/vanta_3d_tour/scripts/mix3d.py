# sound for the 3D videos: music bed + cue-driven sfx -> -14 LUFS, mux with the rendered video
import sys, json, subprocess
S='/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'; SND=S+'/snd/'
MAP={'whoosh':('whoosh_soft_1.mp3',-13),'tick':('sfx_click_1.mp3',-20),'boom':('impact_boom_v2.mp3',-11),'riser_start':('riser_2.mp3',-16),
     'shimmer':('sfx_line_draw_tone_1.mp3',-18),'pop':('pop_soft.mp3',-16)}
def mix(video, cues, out, music='music_cinematic_build_A.mp3', mdb=-17.0):
    dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',video],capture_output=True,text=True).stdout)
    cs=[c for c in json.load(open(cues)) if c['type'] in MAP]
    inp=['-stream_loop','-1','-i',SND+music]; fl=['[0:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:%.3f,volume=%.1fdB,afade=t=in:d=1.0,afade=t=out:st=%.3f:d=2.2[m]'%(dur,mdb,dur-2.2)]; tags=['[m]']
    for k,c in enumerate(cs):
        f,g=MAP[c['type']]; inp+=['-i',SND+f]; d=int(max(0,c['t'])*1000)
        fl.append('[%d:a]aresample=48000,aformat=channel_layouts=stereo,volume=%.1fdB,adelay=%d|%d[s%d]'%(k+1,g,d,d,k)); tags.append('[s%d]'%k)
    fl.append(''.join(tags)+'amix=inputs=%d:normalize=0:duration=first,loudnorm=I=-14:TP=-2.0:LRA=11[o]'%len(tags))
    wav=out.replace('.mp4','.wav')
    subprocess.run(['ffmpeg','-v','error','-y']+inp+['-filter_complex',';'.join(fl),'-map','[o]','-ar','48000','-t','%.3f'%dur,wav],check=True)
    r=subprocess.run(['ffmpeg','-nostats','-i',wav,'-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
    I=float([l for l in r.splitlines() if ' I:' in l][-1].split('I:')[1].split('LUFS')[0]); g=-14.0-I
    w2=wav.replace('.wav','_n.wav'); subprocess.run(['ffmpeg','-v','error','-y','-i',wav,'-af','volume=%.2fdB,aresample=192000,alimiter=limit=0.77:attack=2:release=60:level=false,aresample=48000'%g,w2],check=True); wav=w2
    subprocess.run(['ffmpeg','-v','error','-y','-i',video,'-i',wav,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','320k','-shortest','-movflags','+faststart',out],check=True); print(out)
if __name__=='__main__': mix(*sys.argv[1:4])
