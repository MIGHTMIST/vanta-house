# Sound for openings v2: John (cleaned) + Sarah lines placed per plan, original score ducked ~17 dB under the voices, soft SFX. -14 LUFS.
import subprocess, json, sys, re
S = '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad'; A = S + '/audio/pxb_sfx_%s.mp3'; W = S + '/ABC/'
JCH = 'highpass=f=80,afftdn=nr=10:nf=-45,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=4000:t=q:w=1.2:g=2,acompressor=threshold=-20dB:ratio=3:attack=8:release=150:makeup=4'
SCH = 'highpass=f=70,acompressor=threshold=-20dB:ratio=2:attack=10:release=150:makeup=1'
def lufs(path, ss=None, t=None):
    cmd = ['ffmpeg', '-hide_banner'] + (['-ss', str(ss), '-t', str(t)] if ss is not None else []) + ['-i', path, '-af', 'ebur128', '-f', 'null', '-']
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', subprocess.run(cmd, capture_output=True, text=True).stderr)[-1])
def run(name):
    plan = json.load(open(W + 'v2_%s_plan.json' % name)); dur = plan['dur']
    segs = []
    for k, (a, b, t0, src, n) in enumerate(plan['audio']):          # one file per voice piece (a single multi-seek graph cut A short)
        f = W + 'v2seg_%s_%d.wav' % (name, k)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '%.3f' % a, '-t', '%.3f' % (b - a), '-i', src, '-af',
                        'aresample=48000,aformat=channel_layouts=stereo,%s,%s,afade=t=in:d=0.015,afade=t=out:st=%.3f:d=0.03,adelay=%d|%d'
                        % (JCH if n == 0 else SCH, 'volume=1.0' if n == 0 else 'volume=2.05', b - a - 0.03, int(t0 * 1000), int(t0 * 1000)), f], check=True)
        segs.append(f)
    inp = sum((['-i', f] for f in segs), [])
    fc = [''.join('[%d:a]' % k for k in range(len(segs))) + 'amix=inputs=%d:normalize=0:duration=longest,apad=whole_dur=%.3f,atrim=0:%.3f[vo]' % (len(segs), dur, dur)]
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[vo]', '-c:a', 'pcm_s24le', W + 'v2voice_%s.wav' % name], check=True)
    # level Sarah to John: measure each speaker's loudness inside the voice track and fix in a second pass if > 2 dB apart
    mus = 'highpass=f=35,equalizer=f=2500:t=q:w=1.2:g=-4,acompressor=threshold=-18dB:ratio=2:attack=20:release=250:makeup=2,atrim=0:%.3f,afade=t=out:st=%.3f:d=1.4' % (dur, dur - 1.4)
    if plan.get('silence'): mus += ",volume=enable='between(t,%.3f,%.3f)':volume=0" % (plan['silence'], plan['silence'] + 1.0)
    jc = [t0 for a, b, t0, s, n in plan['audio'] if n == 0]
    sfx = {'A': [('transition_whoosh', plan['audio'][2][2] - 0.08, 0.8, 0.28), ('transition_whoosh', plan['audio'][3][2] - 0.1, 0.9, 0.24)],
           'B': [('transition_whoosh', plan['audio'][-1][2] - 0.12, 0.85, 0.24)],
           'C': [('whoosh_motion', jc[0] - 0.3, 0.9, 0.24)]}[name]
    gain = 1.0
    for it in range(3):
        inp = ['-i', W + 'v2voice_%s.wav' % name, '-i', S + '/music/score_v2%s_raw.wav' % name]
        fc = ['[0:a]asplit=2[vo][key]', '[1:a]aresample=48000,aformat=channel_layouts=stereo,%s,volume=%.3f[mu]' % (mus, gain),
              '[mu][key]sidechaincompress=threshold=0.06:ratio=2.5:attack=25:release=450[duck]']
        for k, (f, st, pf, g) in enumerate(sfx):
            inp += ['-i', A % f]; p = 'asetrate=%d,' % int(48000 * pf) if pf != 1 else ''
            fc.append('[%d:a]aresample=48000,aformat=channel_layouts=stereo,%saresample=48000,volume=%.2f,adelay=%d|%d[s%d]' % (k + 2, p, g, int(st * 1000), int(st * 1000), k))
        fc.append('[vo][duck]' + ''.join('[s%d]' % k for k in range(len(sfx))) + 'amix=inputs=%d:normalize=0:duration=first,atrim=0:%.3f[pre]' % (2 + len(sfx), dur))
        subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[pre]', '-c:a', 'pcm_s24le', W + 'v2pre_%s.wav' % name], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', W + 'v2voice_%s.wav' % name, '-i', S + '/music/score_v2%s_raw.wav' % name, '-filter_complex',
                        '[0:a]asplit=2[a][key];[a]anullsink;[1:a]aresample=48000,aformat=channel_layouts=stereo,%s,volume=%.3f[mu];[mu][key]sidechaincompress=threshold=0.06:ratio=2.5:attack=25:release=450[d]' % (mus, gain),
                        '-map', '[d]', W + 'v2duck_%s.wav' % name], check=True)
        a0 = jc[0] + 0.5; diff = lufs(W + 'v2voice_%s.wav' % name, a0, 7) - lufs(W + 'v2duck_%s.wav' % name, a0, 7)
        if abs(diff - 17) < 1.0: break
        gain *= 10 ** ((diff - 17) / 20)
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', W + 'v2pre_%s.wav' % name, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}') + 1])
    af = 'loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true,aresample=48000' % (j['input_i'], j['input_tp'], j['input_lra'], j['input_thresh'], j['target_offset'])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', W + 'v2pre_%s.wav' % name, '-af', af, '-c:a', 'pcm_s24le', W + 'v2mix_%s.wav' % name], check=True)
    sp = [(t0, t0 + b - a, n) for a, b, t0, s, n in plan['audio']]
    js = [lufs(W + 'v2voice_%s.wav' % name, a, min(4, b - a)) for a, b, n in sp if n == 0][:1]
    ss = [lufs(W + 'v2voice_%s.wav' % name, a, min(4, b - a)) for a, b, n in sp if n != 0 and b - a > 1.5][:1]
    print(name, 'music %.1f dB under voice' % diff, '| John %.1f vs Sarah %.1f LUFS' % (js[0], ss[0]) if js and ss else '', '| final %.1f' % lufs(W + 'v2mix_%s.wav' % name))
for n_ in sys.argv[1:]: run(n_)
