# Video C sound: one music track (pxb real estate, groove from frame 1, a bar line on the end-card flash)
# + his SFX library (whoosh / pop / stamp, pitched for variety) on every graphic in and out. Two-pass loudnorm -14 LUFS, TP -1.5.
import subprocess, json, sys
S = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'
A = S + '/audio/'
DUR = 254 / 30
MUSIC_START = 12.899 - 4.25          # beat 24 lands on the VANTA HOUSE reveal
# (file, start time in video, pitch factor, gain)
CUES = [('transition_whoosh', 0.0, 1.00, 0.45),               # hook in (soft)
        ('whoosh_motion',     2.18 - 0.323 / 0.85, 0.85, 0.60),  # zoom-out to the full meeting
        ('cinematic_riser',   4.25 - 2.985, 1.00, 0.25),     # gentle build into the end card
        ('clean_pop',         2.65 - 0.173 / 0.7, 0.70, 0.35),   # BLACKSTONE line (soft low tick)
        ('transition_whoosh', 4.25 - 0.096 / 0.6, 0.60, 0.50),   # deep whoosh on VANTA HOUSE
        ('clean_pop',         6.00 - 0.173 / 0.9, 0.90, 0.30)]   # number
inputs = ['-ss', '%.3f' % MUSIC_START, '-t', '%.3f' % (DUR + 0.5), '-i', A + 'pxb_music_upbeat_real_estate.mp3']
fc = ['[0:a]aresample=48000,aformat=channel_layouts=stereo,highpass=f=40,volume=0.62,afade=t=in:d=0.03,afade=t=out:st=%.3f:d=1.5[mus]' % (DUR - 1.5)]
for k, (f, st, pf, g) in enumerate(CUES):
    inputs += ['-i', A + 'pxb_sfx_%s.mp3' % f]
    pitch = 'asetrate=%d,' % int(48000 * pf) if pf != 1 else ''
    fc.append('[%d:a]aresample=48000,aformat=channel_layouts=stereo,%saresample=48000,volume=%.2f,adelay=%d|%d[s%d]' % (k + 1, pitch, g, int(st * 1000), int(st * 1000), k))
mix = '[mus]' + ''.join('[s%d]' % k for k in range(len(CUES)))
fc.append(mix + 'amix=inputs=%d:normalize=0:duration=first,atrim=0:%.4f[pre]' % (len(CUES) + 1, DUR))
pre = S + '/C/mixC_pre.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[pre]', '-c:a', 'pcm_s24le', pre], check=True)
# two-pass loudnorm
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', pre, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
j = json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}') + 1])
af = ('loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true,aresample=48000'
      % (j['input_i'], j['input_tp'], j['input_lra'], j['input_thresh'], j['target_offset']))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', pre, '-af', af, '-c:a', 'pcm_s24le', S + '/C/mixC.wav'], check=True)
print('pre-master I', j['input_i'], 'TP', j['input_tp'])
