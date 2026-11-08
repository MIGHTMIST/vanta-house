# Marketing brief 8 Nov - Way2 R1 "Ten Years in Banking", 3 test versions, graphics rebuilt on the MOTION + SOUND KIT
# and MOTION GRAPHICS REFERENCES (mgk.py). V1 teal + Inter ExtraBold, V2 gold + Anton, V3 best (gold, looks follow the words,
# more real pictures, mixed-weight word pops, tracked luxury title). Sarah closes with her approved r1 line, cut after
# "Vanta House in Naguru, Kampala." (WhatsApp CTA on hold - owner 7 Nov; no VISIT recording exists yet).
import sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
import iv, mg, mgk, way2

OW, OH = 1080, 1920
CAP_Y = 1345                       # inside the kit's safe area (y <= 1440), below his chin
SITE = iv.S + '/site/mmexport%s.jpg'; RP = iv.S + '/people/real/'; PE = iv.S + '/people/'; B = iv.S + '/broll/'
THEMES = {'teal': dict(acc=(46, 196, 182), font=mgk.INTER_XB, name='R1_V1_teal'),
          'gold': dict(acc=(201, 162, 75), font=iv.ANTON, name='R1_V2_gold'),
          'best': dict(acc=(201, 162, 75), font=iv.ANTON, name='R1_V3_best')}
COOLG = "eq=contrast=1.06:saturation=0.82:brightness=-0.02,colorbalance=rs=-0.04:bs=0.06:rm=-0.02:bm=0.04"   # banking years, skin kept natural
DIMG = "eq=saturation=0.7:contrast=1.05:brightness=-0.18,colorbalance=bs=0.08:rs=-0.06,boxblur=10:2"          # trading screen behind the counter
WARM_T = (1.06, 1.0, 0.9); STEEL_T = (0.95, 1.0, 1.05)
SAR = dict(dur=17.40, picture=0.0, site=2.08, now=3.98, workers=6.95, steel=8.02, concrete=9.15, homes=10.56, vanta=14.97)

def build(v):
    T = THEMES[v]; mg.GOLD = T['acc']; mg.ANTON = T['font']
    R = way2.REELS['R1']; P = way2.build(R)
    P['voice'] = [(float(x), float(y), float(t0)) for x, y, t0 in P['voice']]
    voice = P['voice']; jend = max(t0 + y - x for x, y, t0 in voice)
    def wt(ph, after=0, last=False):
        a0 = after
        while True:
            i = iv.find(ph, a0); j = i + len(ph.split()) - 1 if last else i
            for x, y, t0 in voice:
                if x - 0.03 <= iv.WORDS[j]['t'] < y: return t0 + iv.WORDS[j]['t'] - x + ((iv.WORDS[j]['end'] - iv.WORDS[j]['t']) if last else 0)
            a0 = iv.WORDS[i]['t'] + 0.01
    pics = [p for p in P['pics'] if p.get('kind') != 'card']
    for p in pics: p['top'] = 0.56          # face a little lower: hook title clears his hair
    ov = []; ovl = []; leaks = []
    sfx = [s for s in P['sfx'] if s[0] not in ('reverse_swell', 'whoosh_cinematic_5', 'pop_soft', 'whoosh_soft_1')]   # graphic sounds re-made from the kit
    def photo(t0, t1, path, tint=WARM_T, z=(1.0, 1.08), cx=0.5, cy=0.5, snd=True):
        ov.append(dict(t=t0, dur=t1 - t0, kind='photo', path=path, z0=z[0], z1=z[1], cx=cx, cy=cy, tint=tint))
        if snd: sfx.append(('sfx_camera_shutter_1', t0 - 0.02, -24))
    # hook (T3 bar title), first 2.9 s, his own words
    sfx += [('sfx_whoosh_soft_2', 0.05, -17), ('sfx_impact_soft_1', 0.3, -19)]
    hook = dict(t0=0.0, t1=2.9, lines=[('TEN YEARS IN BANKING.', (255, 255, 255)), ('THEN UGANDA.', T['acc'])], size=78 if T['font'] == mgk.INTER_XB else 92, gap=96)
    ovl.append(('hook', hook))
    # "investment banking": trading screen, dimmed + blurred, with the T4 "10 YEARS" counter on it (cool look)
    t_ib = wt('investment banking'); t_saw = wt('saw significant'); t_af = wt("africa's"); t_mk = wt('markets', last=True)
    c0 = max(2.0, t_ib - 0.1)
    ov.append(dict(t=c0, dur=t_saw - 0.1 - c0 + 0.9, kind='clip', path=B + 'b1_trading_screen_4.mp4', src=0.0, grade=DIMG, z0=1.05, z1=1.12))
    ovl.append(('counter', dict(t0=c0, t1=t_saw + 0.8, sub='INVESTMENT BANKING · CHINA'))); sfx += mgk.counter_sfx(c0)
    # name strip while he says "I saw significant opportunities" (MOTION_02)
    ovl.append(('name', dict(t0=t_saw + 0.8, t1=t_af - 0.1, y0=300, l1='JOHN YAN', l2='Founder & CEO, Blackstone Real Estate')))
    sfx += [('sfx_ui_swoosh_in_1', t_saw + 0.78, -18), ('sfx_ui_swoosh_out_1', t_af - 0.4, -20)]
    # "Africa's real estate market": T5 map route on a real dot map, light leak into it (look C)
    m0 = t_af - 0.15; m1 = max(t_mk + 0.45, m0 + 3.7)
    ov.append(dict(t=m0, dur=m1 - m0, kind='card', draw=mgk.map_card, T=T)); sfx += mgk.map_sfx(m0); leaks.append(m0)
    sfx.append(('sfx_whoosh_soft_1', m0 - 0.4, -16))
    # founder: Abdullahi's black-and-white portrait + name
    t_f = wt('i founded blackstone', 179)
    ov.append(dict(t=t_f + 0.35, dur=2.6, kind='card', draw=mg.founder_card, photo='john_headshot_black_shirt.jpg'))
    sfx += [('sfx_whoosh_soft_3', t_f + 0.2, -18), ('sfx_text_pop_1', t_f + 0.75, -20)]
    # "investment analysis": market screen again (cool), DISCIPLINE word pop (top zone, above his head)
    t_ia = wt('investment analysis', 179)
    ov.append(dict(t=t_ia - 0.1, dur=1.7, kind='clip', path=B + 'b1_trading_screen_4.mp4', src=4.0, grade="eq=saturation=0.75:contrast=1.06,colorbalance=bs=0.08:rs=-0.06", z0=1.02, z1=1.1))
    sfx.append(('sfx_swish_fast_1', t_ia - 0.12, -19))
    pops = []
    for g in P['G']:
        if g['text'] in ('DISCIPLINE', 'UGANDA'): pops.append(dict(t0=g['t'], t1=g['t'] + 2.2, text=g['text'], y=420, size=150 if T['font'] != mgk.INTER_XB else 128))
    for w in pops: ovl.append(('pop', w)); sfx += [('sfx_text_pop_3', w['t0'], -16), ('sfx_ui_swoosh_out_1', w['t1'] - 0.2, -22)]
    # "efficient execution to Uganda": steel + Kampala towers (look B -> warm)
    t_ee = wt('efficient execution', 179); t_ug = wt('uganda', 190, last=True)
    photo(t_ee - 0.1, t_ug + 0.35, SITE % '1792497989322', tint=STEEL_T if v == 'best' else WARM_T, z=(1.0, 1.1))
    # "quality developments": slab + crane
    t_qd = wt('quality developments', 194); t_lt = wt('long-term', 194)
    photo(t_qd - 0.1, t_lt - 0.1, SITE % '1792497986840', tint=STEEL_T if v == 'best' else WARM_T)
    if v == 'best':
        t_ps = wt('partnerships', 194); photo(t_ps - 0.15, jend + 0.3, RP + '6baeb5bd.jpg', cx=0.25, cy=0.4)
        for p in pics:
            if t_ib - 0.3 <= p['t'] < t_saw: p['grade'] = COOLG
    # Sarah closes over real site pictures; render (artist's impression) + handover title on "a hundred homes"; end card on "Vanta House"
    s0 = jend + 0.35; S_ = {k: s0 + x for k, x in SAR.items() if k != 'dur'}; s1 = s0 + SAR['dur']; leaks.append(s0 - 0.02)
    sfx.append(('sfx_whoosh_soft_1', s0 - 0.42, -16))
    seq = [('picture', 'site', SITE % '1792497982990'), ('site', 'now', SITE % '1792673498404'), ('now', 'workers', SITE % '1792673493181'),
           ('workers', 'steel', PE + 'brick_laying.jpg'), ('steel', 'concrete', SITE % '1792497989322'), ('concrete', 'homes', PE + 'slab_pour_sky.jpg')]
    for a, b, path in seq: photo(S_[a] - 0.05, S_[b] - 0.05, path, tint=STEEL_T if v == 'best' else WARM_T, z=(1.0, 1.07), snd=(a != 'picture'))
    ov.append(dict(t=S_['homes'] - 0.05, dur=S_['vanta'] - S_['homes'], kind='photo', path=PE + 'render_vanta_house.jpg', z0=1.0, z1=1.06, cx=0.3, cy=0.5, tint=None))
    ovl.append(('imp', dict(t0=S_['homes'] - 0.05, t1=S_['vanta'] - 0.05)))
    ovl.append(('lux', dict(t0=S_['homes'] + 1.05, t1=S_['vanta'] - 0.1, small='HANDOVER EXPECTED', big='OCTOBER 2027', y=470)))
    sfx += [('sfx_whoosh_soft_3', S_['homes'] + 1.0, -20), ('sfx_impact_soft_1', S_['homes'] + 1.7, -19)]
    if v == 'best':
        for k, w in (('workers', 'WORKERS'), ('steel', 'STEEL'), ('concrete', 'CONCRETE')):
            nx = {'workers': 'steel', 'steel': 'concrete', 'concrete': 'homes'}[k]
            ovl.append(('pop', dict(t0=S_[k] + 0.08, t1=S_[nx] - 0.06, text=w, small='real', y=560, size=170))); sfx.append(('sfx_text_pop_3', S_[k] + 0.08, -15))
    end = S_['vanta'] - 0.05; dur = s1 + 2.6; leaks.append(end)
    pics = pics + ov + [dict(t=end, dur=dur - end, kind='card', draw=mgk.end_card(T), nocap=True)]
    srcp = sorted([p for p in pics if p.get('kind', 'src') == 'src'], key=lambda p: p['t'])
    srcp[-1]['dur'] = max(srcp[-1]['dur'], s0 - srcp[-1]['t'])
    sfx += mgk.end_sfx(end) + [('sarah_r1_cta', s0, -17.7 - iv.lufs(iv.SND + 'sarah_r1_cta.mp3'))]
    # captions: T1 word pops (active word in the accent). John from the engine's cleaned chunks, Sarah from her word list.
    chunks = []
    for c in P['caps']:
        times = c[3] if len(c) > 3 else [c[0]] * len(c[2])
        chunks.append(dict(t0=c[0] - 0.04, t1=c[1], words=[(w, ts) for (w, kw), ts in zip(c[2], times)]))
    sw = json.load(open(iv.S + '/sarah/vanta_reel_r1_voice.json'))['words']
    marks = [0.0, 2.08, 3.98, 6.95, 8.02, 9.15, 10.56, 14.97]
    sws = []
    for a, b in zip(marks, marks[1:]):
        ws = [w for w in sw if a - 0.05 <= w['t'] < b - 0.05]
        if not ws: continue
        span = (b - a - 0.3); k0 = ws[0]['t']; kk = (ws[-1]['end'] - k0) or 1
        for w in ws: sws.append((w['w'], s0 + a + (w['t'] - k0) / kk * span, s0 + a + (w['end'] - k0) / kk * span))
    chunks += mgk.chunk_words(sws, maxw=4, gap=0.25)
    chunks = [c for c in chunks if c['t0'] < end - 0.05]
    for c in chunks: c['t1'] = min(c['t1'], end - 0.05)
    hide = [(o['t0'], o['t1']) for k, o in ovl if k == 'counter'] + [(p['t'], p['t'] + p['dur']) for p in ov if p.get('kind') == 'card' and p['draw'] is mgk.map_card]
    lifts = [l for l in P['lifts'] if l[1] <= jend + 0.01] + [(s1 + 0.1, dur)]
    def extra(fr, t):
        t = float(t)
        for k, o in ovl:
            if o['t0'] <= t <= o['t1']:
                if k == 'hook': mgk.title2(fr, t, o, T, y=345)
                elif k == 'counter': mgk.counter(fr, t, o, T)
                elif k == 'name': mgk.name_strip(fr, t, o, T)
                elif k == 'pop': mgk.word_pop(fr, t, o, T)
                elif k == 'lux': mgk.lux_title(fr, t, o, T)
                elif k == 'imp': mg.label(fr, t, o, "Artist's impression")
        if not any(a <= t <= b for a, b in hide):
            for c in chunks:
                if c['t0'] <= t <= c['t1']: mgk.caption(fr, t, c, T, CAP_Y)
        for lc in leaks: mgk.light_leak(fr, t, lc, 0.7)
    return dict(P, pics=pics, G=[], sfx=sfx, caps=[], dur=dur, extra=extra, lifts=lifts, end=end, T=T)

if __name__ == '__main__':
    args = sys.argv[1:] or ['teal', 'gold', 'best']
    test = None
    if args and args[0].startswith('test'): test = float(args[0][4:] or 9); args = args[1:]
    for v in args:
        P = build(v); T = P['T']; dur = test or P['dur']
        vid = iv.render_video('r1k_' + v + ('_t' if test else ''), OW, OH, P['pics'], [], [], dur, extra=P['extra'])
        if test: print(vid); continue
        a = iv.render_audio('r1k_' + v, P['voice'], P['sfx'], 'music_modern_upbeat_A.mp3', P['dur'], music_db_under=19.0, smooth=True, lift=P['lifts'], lift_db=7.0)
        print(iv.encode('r1k_' + v, vid, a, T['name']))
