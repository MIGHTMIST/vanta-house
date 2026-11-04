# Video G cut: reorder John's cold open (hook first), tighten pauses, punch-ins on jump cuts, Vanta grade, lossless plate + clean voice.
import subprocess, json
S = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'
G = S + '/G/'
SEG = [(15.00, 19.15, 0), (20.02, 25.40, 1), (25.80, 32.20, 0), (32.23, 39.40, 0), (0.20, 2.35, 1), (2.85, 5.00, 0), (5.70, 10.85, 1)]
grade = open(S + '/C/grade.txt').read().strip()
fc = []; vl = []; al = []
for k, (a, b, p) in enumerate(SEG):
    punch = ',crop=iw/1.12:ih/1.12:(iw-ow)/2:(ih-oh)*0.30,scale=1080:1920:flags=lanczos' if p else ''
    fc.append('[0:v]trim=%.3f:%.3f,setpts=PTS-STARTPTS%s,setsar=1[v%d]' % (a, b, punch, k))
    fc.append('[0:a]atrim=%.3f:%.3f,asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.015,afade=t=out:st=%.3f:d=0.02[a%d]' % (a, b, b - a - 0.02, k))
    vl.append('[v%d]' % k); al.append('[a%d]' % k)
fc.append(''.join(vl) + 'concat=n=%d:v=1:a=0,%s,format=rgb24[v]' % (len(SEG), grade))
fc.append(''.join(al) + 'concat=n=%d:v=0:a=1,highpass=f=80,afftdn=nr=10:nf=-45,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=4000:t=q:w=1.2:g=2,acompressor=threshold=-20dB:ratio=3:attack=8:release=150:makeup=4[a]' % len(SEG))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', G + 'src.mp4', '-filter_complex', ';'.join(fc), '-map', '[v]', '-c:v', 'libx264rgb', '-qp', '0', '-preset', 'veryfast', '-r', '30', G + 'plateG.mkv',
                '-map', '[a]', '-c:a', 'pcm_s24le', G + 'voiceG.wav'], check=True)
# segment start times on the output timeline
out, t = [], 0.0
for a, b, p in SEG: out.append((a, b, t)); t += b - a
json.dump({'segs': out, 'dur': t}, open(G + 'segs.json', 'w'))
print('plate duration %.2f s' % t)
