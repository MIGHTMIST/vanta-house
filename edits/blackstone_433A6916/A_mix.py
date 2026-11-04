# Video A sound: one music track (pxb real estate, groove from frame 1, a bar line on the end-card flash)
# + his SFX library (whoosh / pop / stamp, pitched for variety) on every graphic in and out. Two-pass loudnorm -14 LUFS, TP -1.5.
import subprocess, json, sys
S = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'
A = S + '/audio/'
DUR = 260 / 30
MUSIC_START = 12.899 - 122 / 30          # beat 24 of the track lands on the end-card flash
# (file, start time in video, pitch factor, gain)
CUES = [('transition_whoosh', 0.133 - 0.096, 1.00, 0.85),   # hook lands
        ('whoosh_motion',     1.60 - 0.323 / 0.92, 0.92, 0.70),  # hook out
        ('clean_pop',         2.05 - 0.173, 1.00, 0.75),     # Blackstone card in
        ('clean_pop',         3.55 - 0.173 / 0.85, 0.85, 0.60),  # card out
        ('transition_whoosh', 122 / 30 - 0.096 / 0.8, 0.80, 0.90),  # flash into end card
        ('stamp',             4.637 - 0.613, 1.00, 0.80),    # VANTA HOUSE slam
        ('clean_pop',         5.387 - 0.173, 1.00, 0.70),    # FREE SITE VISIT badge
        ('clean_pop',         6.147 - 0.173 / 0.8, 0.80, 0.65),  # VANTA slam
        ('clean_pop',         6.807 - 0.173 / 1.15, 1.15, 0.60)] # number
inputs = ['-ss', '%.3f' % MUSIC_START, '-t', '%.3f' % (DUR + 0.5), '-i', A + 'pxb_music_upbeat_real_estate.mp3']
fc = ['[0:a]aresample=48000,aformat=channel_layouts=stereo,highpass=f=40,volume=0.62,afade=t=in:d=0.03,afade=t=out:st=%.3f:d=1.5[mus]' % (DUR - 1.5)]
for k, (f, st, pf, g) in enumerate(CUES):
    inputs += ['-i', A + 'pxb_sfx_%s.mp3' % f]
    pitch = 'asetrate=%d,' % int(48000 * pf) if pf != 1 else ''
    fc.append('[%d:a]aresample=48000,aformat=channel_layouts=stereo,%saresample=48000,volume=%.2f,adelay=%d|%d[s%d]' % (k + 1, pitch, g, int(st * 1000), int(st * 1000), k))
mix = '[mus]' + ''.join('[s%d]' % k for k in range(len(CUES)))
fc.append(mix + 'amix=inputs=%d:normalize=0:duration=first,atrim=0:%.4f[pre]' % (len(CUES) + 1, DUR))
pre = S + '/A/mixA_pre.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[pre]', '-c:a', 'pcm_s24le', pre], check=True)
# two-pass loudnorm
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', pre, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
j = json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}') + 1])
af = ('loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true,aresample=48000'
      % (j['input_i'], j['input_tp'], j['input_lra'], j['input_thresh'], j['target_offset']))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', pre, '-af', af, '-c:a', 'pcm_s24le', S + '/A/mixA.wav'], check=True)
print('pre-master I', j['input_i'], 'TP', j['input_tp'])
