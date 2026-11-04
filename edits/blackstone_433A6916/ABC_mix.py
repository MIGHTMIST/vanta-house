# Sound for A/B/C: John's cleaned voice placed per plan + original score ducked ~17 dB under him + soft SFX. -14 LUFS / TP -1.5.
import subprocess, json, sys, re
S = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'
SRC = S + '/G/src.mp4'; A = S + '/audio/pxb_sfx_%s.mp3'
VCHAIN = 'highpass=f=80,afftdn=nr=10:nf=-45,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=4000:t=q:w=1.2:g=2,acompressor=threshold=-20dB:ratio=3:attack=8:release=150:makeup=4'
def lufs(path, ss=None, t=None):
    cmd = ['ffmpeg', '-hide_banner'] + (['-ss', str(ss), '-t', str(t)] if ss is not None else []) + ['-i', path, '-af', 'ebur128', '-f', 'null', '-']
    r = subprocess.run(cmd, capture_output=True, text=True)
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1])
def run(name, music=True):
    plan = json.load(open(S + '/ABC/%s_plan.json' % name)); dur = plan['dur']; tag = '' if music else '_voiceonly'
    W = S + '/ABC/'
    # voice track
    inp = []; fc = []
    for k, (a, b, t0) in enumerate(plan['audio']):
        inp += ['-ss', '%.3f' % a, '-t', '%.3f' % (b - a), '-i', SRC]
        fc.append('[%d:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.015,afade=t=out:st=%.3f:d=0.02,adelay=%d|%d[v%d]' % (k, b - a - 0.02, int(t0 * 1000), int(t0 * 1000), k))
    fc.append(''.join('[v%d]' % k for k in range(len(plan['audio']))) + 'amix=inputs=%d:normalize=0,%s,apad=whole_dur=%.3f,atrim=0:%.3f[vo]' % (len(plan['audio']), VCHAIN, dur, dur))
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[vo]', '-c:a', 'pcm_s24le', W + 'voice_%s.wav' % name], check=True)
    vl = lufs(W + 'voice_%s.wav' % name)
    mus = 'highpass=f=35,equalizer=f=2500:t=q:w=1.2:g=-4,acompressor=threshold=-18dB:ratio=2:attack=20:release=250:makeup=2,atrim=0:%.3f,afade=t=out:st=%.3f:d=1.2' % (dur, dur - 1.2)
    if name == 'B': mus += ",volume=enable='between(t,%.3f,%.3f)':volume=0" % (plan['silence'], plan['silence'] + 1.0)
    sfx = {'A': [('transition_whoosh', 12.45, 0.8, 0.30), ('transition_whoosh', 13.6, 0.9, 0.25)],
           'B': [],
           'C': [('transition_whoosh', plan['end'] + 0.08, 0.8, 0.38), ('clean_pop', plan['end'] + 1.0, 0.85, 0.28)]}[name]
    gain = 1.0
    for it in range(2):
        inp = ['-i', W + 'voice_%s.wav' % name, '-i', S + '/music/score_%s_raw.wav' % name]
        fc = ['[0:a]asplit=2[vo][key]', '[1:a]aresample=48000,aformat=channel_layouts=stereo,%s,volume=%.3f[mu]' % (mus, gain),
              '[mu][key]sidechaincompress=threshold=0.06:ratio=2.5:attack=25:release=450[duck]']
        for k, (f, st, pf, g) in enumerate(sfx):
            inp += ['-i', A % f]; p = 'asetrate=%d,' % int(48000 * pf) if pf != 1 else ''
            fc.append('[%d:a]aresample=48000,aformat=channel_layouts=stereo,%saresample=48000,volume=%.2f,adelay=%d|%d[s%d]' % (k + 2, p, g, int(st * 1000), int(st * 1000), k))
        parts = '[vo]' + ('[duck]' if music else '') + ''.join('[s%d]' % k for k in range(len(sfx)))
        if not music: fc[2] = '[mu][key]sidechaincompress[duck];[duck]anullsink'
        fc.append(parts + 'amix=inputs=%d:normalize=0:duration=first,atrim=0:%.3f[pre]' % (1 + (1 if music else 0) + len(sfx), dur))
        subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[pre]', '-c:a', 'pcm_s24le', W + 'pre_%s%s.wav' % (name, tag)], check=True)
        if not music: break
        # measure the ducked music alone while he talks, aim 17 dB under the voice
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', W + 'voice_%s.wav' % name, '-i', S + '/music/score_%s_raw.wav' % name, '-filter_complex',
                        '[0:a]asplit=2[a][key];[a]anullsink;[1:a]aresample=48000,aformat=channel_layouts=stereo,%s,volume=%.3f[mu];[mu][key]sidechaincompress=threshold=0.06:ratio=2.5:attack=25:release=450[d]' % (mus, gain),
                        '-map', '[d]', W + 'duck_%s.wav' % name], check=True)
        a0, a1 = plan['audio'][0][2] + 0.5, plan['audio'][0][2] + 8
        ml = lufs(W + 'duck_%s.wav' % name, a0, a1 - a0); vv = lufs(W + 'voice_%s.wav' % name, a0, a1 - a0)
        diff = vv - ml
        if abs(diff - 17) < 1.0: break
        gain *= 10 ** ((diff - 17) / 20)
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', W + 'pre_%s%s.wav' % (name, tag), '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}') + 1])
    af = 'loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true,aresample=48000' % (j['input_i'], j['input_tp'], j['input_lra'], j['input_thresh'], j['target_offset'])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', W + 'pre_%s%s.wav' % (name, tag), '-af', af, '-c:a', 'pcm_s24le', W + 'mix_%s%s.wav' % (name, tag)], check=True)
    print(name + tag, 'music gain %.2f' % gain, 'voice-music gap %.1f dB' % (diff if music else 0), 'final I %.1f' % lufs(W + 'mix_%s%s.wav' % (name, tag)))
for n_ in sys.argv[1:]:
    if n_ == 'A0': run('A', music=False)
    else: run(n_)
