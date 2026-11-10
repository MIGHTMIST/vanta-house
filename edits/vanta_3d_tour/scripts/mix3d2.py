# one timed sound mix for a 3D film: music bed (ducked a little under busy moments) + snd3d kit cues (one-shots and looped ambiences with fades)
import sys, json, subprocess
S='/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'; K=S+'/snd3d/sfx3d_%s.wav'
GAIN={'whoosh':-14,'long_whoosh':-15,'boom':-13,'sub_drop':-14,'riser':-17,'shimmer':-20,'tick':-22,'pop':-18,'lift_ding':-17,'sliding_door':-15,'door':-13,
      'glass_slide':-16,'footsteps':-19,'birds':-27,'city':-23,'water':-20,'wind':-23,'room_tone':-26,'reveal_swell':-14}
def run(a): subprocess.run(a,check=True)
def mix(video, cues, out, music=S+'/snd/music_calm_piano_A.mp3', mdb=-19.0, gain_over=None):
    G=dict(GAIN); G.update(gain_over or {})
    dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',video],capture_output=True,text=True).stdout)
    cs=[c for c in json.load(open(cues)) if c['type'] in G and c['t']<dur]
    inp=['-stream_loop','-1','-i',music]; fl=['[0:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:%.3f,volume=%.1fdB,afade=t=in:d=1.5,afade=t=out:st=%.3f:d=2.5[m]'%(dur,mdb,dur-2.5)]; tags=['[m]']
    for k,c in enumerate(cs):
        g=G[c['type']]+float(c.get('gain',0)); d=int(max(0,c['t'])*1000); n=k+1
        if 'end' in c:
            L=max(0.3,min(c['end'],dur)-c['t']); f=min(1.2,L/3)
            inp+=['-stream_loop','-1','-i',K%c['type']]
            fl.append('[%d:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:%.3f,afade=t=in:d=%.2f,afade=t=out:st=%.3f:d=%.2f,volume=%.1fdB,adelay=%d|%d[s%d]'%(n,L,f,L-f,f,g,d,d,k))
        else:
            inp+=['-i',K%c['type']]
            fl.append('[%d:a]aresample=48000,aformat=channel_layouts=stereo,volume=%.1fdB,adelay=%d|%d[s%d]'%(n,g,d,d,k))
        tags.append('[s%d]'%k)
    fl.append(''.join(tags)+'amix=inputs=%d:normalize=0:duration=first[o]'%len(tags))
    wav=out.replace('.mp4','_pre.wav')
    open(out+'.filter','w').write(';\n'.join(fl))
    run(['ffmpeg','-v','error','-y']+inp+['-filter_complex_script',out+'.filter','-map','[o]','-ar','48000','-t','%.3f'%dur,wav])
    for _ in range(2):   # hit -14 LUFS with a soft limiter
        r=subprocess.run(['ffmpeg','-nostats','-i',wav,'-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
        I=float([l for l in r.splitlines() if ' I:' in l][-1].split('I:')[1].split('LUFS')[0]); g=-14.0-I
        w2=wav.replace('_pre.wav','_n.wav') if wav.endswith('_pre.wav') else wav.replace('_n.wav','_n2.wav')
        run(['ffmpeg','-v','error','-y','-i',wav,'-af','volume=%.2fdB,aresample=192000,alimiter=limit=0.77:attack=2:release=60:level=false,aresample=48000'%g,w2]); wav=w2
    run(['ffmpeg','-v','error','-y','-i',video,'-i',wav,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','320k','-shortest','-movflags','+faststart',out]); print(out)
if __name__=='__main__': mix(*sys.argv[1:4])
