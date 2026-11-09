# WAY 3 "BRAND" edition (9 Nov), 9:16: the Way 3 MOOD PLUS short clip with
#  - a motion-graphics INTRO (phone vibrates/rings, a line types out on the keyboard, gold logo hit) before the music starts,
#  - every stock movie clip (Shanghai skyline, trading screen, sunrise, Nile) and every stock overlay (light leaks, dust)
#    replaced by brand motion graphics (mgb.py: bronze-gold / ivory / ink),
#  - John, the captions, the real photos, the papers, the blueprint, the step tracker etc. kept as in MOOD PLUS.
import sys, subprocess
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
import iv, mgb, way3k

OW, OH = 1080, 1920
INTRO = 5.6
SND = iv.S + '/snd/'

VGRADE = open(iv.S + '/IV/grade/G3.txt').read().strip()      # the Vanta grade: deep blacks, tamed window, bronze-gold skin, cool shadows
iv.GRADE = VGRADE
GDIR = iv.S + '/IV/grade/photos/'

def graded(path):
    """photo -> colour-graded copy with the same Vanta grade as the footage"""
    import os
    os.makedirs(GDIR, exist_ok=True); out = GDIR + os.path.basename(path)
    if not os.path.exists(out):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-vf', VGRADE, '-q:v', '2', out], check=True)
    return out

mgb.warm()

def build():
    P = way3k.build(OW, OH)
    for p in P['pics']:
        if p.get('kind') == 'photo':
            p['path'] = graded(p['path']); p['tint'] = None
    pics = []; card = lambda t0, t1, fn: dict(t=t0, dur=t1 - t0, kind='card', draw=fn, nocap=False)
    stock = {'b1_shanghai_day_skyline_1.mp4', 'b1_trading_screen_4.mp4', 'b2_sunrise_sun_1.mp4', 'b2_nile_aerial_4.mp4'}
    clips = {str(p.get('path', '')).split('/')[-1]: p for p in P['pics'] if p.get('kind') == 'clip'}
    jc = [p for p in P['pics'] if getattr(p.get('draw'), '__name__', '') == 'journey_card']
    g10 = [g for g in P['G'] if g['text'] == '10 YEARS'][0]
    sh, tr, su, ni = (clips[k] for k in ('b1_shanghai_day_skyline_1.mp4', 'b1_trading_screen_4.mp4', 'b2_sunrise_sun_1.mp4', 'b2_nile_aerial_4.mp4'))
    for p in P['pics']:
        if p.get('kind') == 'clip' and str(p.get('path', '')).split('/')[-1] in stock: continue
        if p in jc: continue
        pics.append(p)
    add = [card(g10['t'], tr['t'] + tr['dur'], mgb.banking_card),                 # "after 10 years in China's investment banking"
           card(tr['t'] + tr['dur'], su['t'] + su['dur'], mgb.route_card),         # "... opportunities in Africa's real estate markets"
           card(ni['t'], ni['t'] + ni['dur'], mgb.uganda_card)]                    # "... to Uganda"
    for c in add: c['dur'] = float(c['dur']); c['t'] = float(c['t'])
    end_cards = [p for p in pics if p.get('kind') == 'card' and p['t'] >= P['end'] - 0.01]
    pics = [p for p in pics if p not in end_cards] + add + end_cards
    G = [g for g in P['G'] if g is not g10]
    sfx = list(P['sfx']) + [('whoosh_soft_1', c['t'] - 0.1, -18) for c in add]
    sweeps = [float(f['t']) + 0.45 for f in P['fxs'] if 'lightleak' in f['path']] + [c['t'] for c in add]
    end = float(P['end']); dur = float(P['dur'])
    base = P['extra']
    def extra(fr, t):
        t = float(t); base(fr, t)
        for c in sweeps: mgb.gold_sweep(fr, t, c, 0.55)
        if t >= end - 0.3: mgb.gold_dust(fr, t, end - 0.3, dur)
    return dict(P, pics=pics, G=G, sfx=sfx, fxs=[], extra=extra)

def shifted(P):
    """the whole interview edit moved INTRO seconds later, with the intro card in front"""
    S = INTRO; Q = dict(P)
    Q['pics'] = [dict(t=0.0, dur=S, kind='card', draw=mgb.intro_card, nocap=True)] + [dict(p, t=p['t'] + S) for p in P['pics']]
    Q['G'] = [dict(g, t=g['t'] + S) for g in P['G']]
    Q['caps'] = [[c[0] + S, c[1] + S] + list(c[2:3]) + ([[x + S for x in c[3]]] if len(c) > 3 else []) for c in P['caps']]
    Q['dur'] = P['dur'] + S; base = P['extra']
    Q['extra'] = lambda fr, t: base(fr, t - S) if t >= S else None
    return Q

def intro_audio(path):
    kt = mgb.intro_key_times()
    parts = [('sfx_phone_vibrate.wav', 0.10, -16), ('sfx_phone_ring.wav', 0.25, -17), ('sfx_logo_hit.wav', 4.30 - 0.30, -11)]
    parts += [('sfx_key_single.wav', t, -19) for t in kt]
    inp = []; fl = []
    for k, (f, t, g) in enumerate(parts):
        inp += ['-i', SND + f]
        fl.append('[%d:a]aresample=48000,aformat=channel_layouts=stereo,volume=%.1fdB,adelay=%d|%d[a%d]' % (k, g, int(t * 1000), int(t * 1000), k))
    fl.append(''.join('[a%d]' % k for k in range(len(parts))) + 'amix=inputs=%d:normalize=0:duration=longest[o]' % len(parts))
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ';'.join(fl), '-map', '[o]', '-c:a', 'pcm_s24le', path], check=True)

if __name__ == '__main__':
    P = build(); Q = shifted(P)
    if 'plan' in sys.argv:
        for p in sorted(Q['pics'], key=lambda p: p['t']):
            if p.get('kind', 'src') != 'src': print('%6.2f %5.2f %-5s %s' % (p['t'], p['dur'], p['kind'], str(p.get('path', getattr(p.get('draw'), '__name__', '')))[-34:]))
        print([(g['text'], round(g['t'], 2)) for g in Q['G']], 'dur', Q['dur']); sys.exit()
    v = iv.render_video('way3x', OW, OH, Q['pics'], Q['G'], Q['caps'], Q['dur'], cap_y=1490, cap_size=52, fxs=[], cap_box=True, extra=Q['extra'])
    # sound: the interview mix exactly as MOOD PLUS (new fuller bed), music starting only after the intro
    main = iv.render_audio('way3x_main', P['voice'], P['sfx'], 'music_cinematic_build_A.mp3', P['dur'], music_db_under=13.0, smooth=True, lift=P['lifts'], lift_db=7.0)
    intro = iv.OUT + 'way3x_intro.wav'; intro_audio(intro)
    pre = iv.OUT + 'way3x_pre.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', intro, '-i', main, '-filter_complex',
                    '[0:a]volume=0dB[i];[1:a]adelay=%d|%d[m];[i][m]amix=inputs=2:normalize=0:duration=longest,atrim=0:%.3f[o]' % (INTRO * 1000, INTRO * 1000, Q['dur']),
                    '-map', '[o]', '-c:a', 'pcm_s24le', pre], check=True)
    fin = iv.OUT + 'way3x_mix.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', pre, '-af', 'loudnorm=I=-14:TP=-2.0:LRA=11', '-ar', '48000', '-c:a', 'pcm_s24le', fin], check=True)
    print(iv.encode('way3x', v, fin, 'John_Way3_TrustFilm_BRAND_INTRO_9x16_1080'))
