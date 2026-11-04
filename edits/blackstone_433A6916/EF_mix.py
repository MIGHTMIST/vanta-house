# Sound for E and F: original score + cues (file, start, pitch, gain), two-pass loudnorm -14 LUFS / TP -1.5.
import subprocess, json, sys
S = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'
A = S + '/audio/pxb_sfx_%s.mp3'; SH = S + '/music/shutter.wav'
def mix(name, score, dur, cues):
    inputs = ['-i', score]; fc = ['[0:a]aresample=48000,aformat=channel_layouts=stereo[mus]']
    for k, (f, st, pf, g) in enumerate(cues):
        inputs += ['-i', SH if f == 'shutter' else A % f]
        pitch = 'asetrate=%d,' % int(48000 * pf) if pf != 1 else ''
        fc.append('[%d:a]aresample=48000,aformat=channel_layouts=stereo,%saresample=48000,volume=%.2f,adelay=%d|%d[s%d]' % (k + 1, pitch, g, max(0, int(st * 1000)), max(0, int(st * 1000)), k))
    fc.append('[mus]' + ''.join('[s%d]' % k for k in range(len(cues))) + 'amix=inputs=%d:normalize=0:duration=first,atrim=0:%.3f[pre]' % (len(cues) + 1, dur))
    pre = S + '/%s/mix%s_pre.wav' % (name, name)
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[pre]', '-c:a', 'pcm_s24le', pre], check=True)
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', pre, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}') + 1])
    af = ('loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true,aresample=48000'
          % (j['input_i'], j['input_tp'], j['input_lra'], j['input_thresh'], j['target_offset']))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', pre, '-af', af, '-c:a', 'pcm_s24le', S + '/%s/mix%s.wav' % (name, name)], check=True)
    print(name, 'pre-master I', j['input_i'], 'TP', j['input_tp'])
# E: shutter on each print landing (12 + John's print), varied pitch; soft whoosh on the cut to John
BAR, B = 2.4, 0.6
lands = [BAR * (1 + b) + k * B for b in range(3) for k in range(4)]
PITCH = [1.0, 0.94, 1.06, 0.9, 1.03, 0.97, 1.08, 0.92, 1.0, 0.95, 1.05, 0.9]
cuesE = [('shutter', tl - 0.01, PITCH[k], 0.55) for k, tl in enumerate(lands)] + [('shutter', 5 * BAR + 0.11, 0.88, 0.6),
         ('whoosh_motion', 4 * BAR - 0.323 / 0.9, 0.9, 0.35)]
mix('E', S + '/music/score_E.wav', 7 * BAR, cuesE)
# F: soft whoosh on each wipe, motion whoosh when John arrives, deep whoosh into the end
BAR = 2.5
cuesF = [('transition_whoosh', k * BAR + 0.18 - 0.096, 1.0 - 0.05 * k, 0.32) for k in (1, 2, 3)] + \
        [('whoosh_motion', 4 * BAR + 0.2 - 0.323 / 0.85, 0.85, 0.40), ('transition_whoosh', 5 * BAR + 0.15 - 0.096 / 0.7, 0.7, 0.38)]
mix('F', S + '/music/score_F.wav', 7 * BAR, cuesF)
