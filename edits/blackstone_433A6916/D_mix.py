# Video D sound: original score (114 BPM, scored to the cuts) + a few of his SFX, soft, on the moves and chips. -14 LUFS / TP -1.5.
import subprocess, json
S = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'
A = S + '/audio/'
BAR = 4 * 60 / 114; TE = 5 * BAR; DUR = 15.0
CUES = [('whoosh_motion',     2.18 - 0.323 / 0.85, 0.85, 0.50),   # zoom-out to the meeting
        ('clean_pop',         2.62 - 0.173 / 0.75, 0.75, 0.28),   # BLACKSTONE line
        ('clean_pop',         2 * BAR + 0.25 - 0.173, 1.00, 0.30),        # chip 1
        ('clean_pop',         3 * BAR + 0.25 - 0.173 / 0.9, 0.90, 0.30),  # chip 2
        ('clean_pop',         4 * BAR + 0.25 - 0.173 / 1.1, 1.10, 0.30),  # chip 3
        ('transition_whoosh', TE + 0.20 - 0.096 / 0.8, 0.80, 0.42),       # end card slides up
        ('clean_pop',         TE + 1.20 - 0.173 / 0.85, 0.85, 0.30)]      # FREE SITE VISIT
inputs = ['-i', S + '/music/score.wav']
fc = ['[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.0[mus]']
for k, (f, st, pf, g) in enumerate(CUES):
    inputs += ['-i', A + 'pxb_sfx_%s.mp3' % f]
    pitch = 'asetrate=%d,' % int(48000 * pf) if pf != 1 else ''
    fc.append('[%d:a]aresample=48000,aformat=channel_layouts=stereo,%saresample=48000,volume=%.2f,adelay=%d|%d[s%d]' % (k + 1, pitch, g, int(st * 1000), int(st * 1000), k))
fc.append('[mus]' + ''.join('[s%d]' % k for k in range(len(CUES))) + 'amix=inputs=%d:normalize=0:duration=first,atrim=0:%.3f[pre]' % (len(CUES) + 1, DUR))
pre = S + '/D/mixD_pre.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[pre]', '-c:a', 'pcm_s24le', pre], check=True)
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', pre, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
j = json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}') + 1])
af = ('loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true,aresample=48000'
      % (j['input_i'], j['input_tp'], j['input_lra'], j['input_thresh'], j['target_offset']))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', pre, '-af', af, '-c:a', 'pcm_s24le', S + '/D/mixD.wav'], check=True)
print('pre-master I', j['input_i'], 'TP', j['input_tp'])
