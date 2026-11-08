# Marketing brief 8 Nov: 3 test versions of Way2 R1 "Ten Years in Banking" (9:16, < 60 s).
#   V1 teal #2EC4B6 + Inter ExtraBold | V2 gold #C9A24B + Anton | V3 best (looks follow the words, more real pictures, word pops)
# All: John's line + hook text in the first 2 s, real picture changes 2-3 per 10 s, graphics ease in/out with a sound,
# music 19 dB under, -14 LUFS / TP -1.5, Sarah closes (her approved r1 line, cut after "Vanta House in Naguru, Kampala."
# because the WhatsApp CTA is on hold - owner 7 Nov).
import sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
from PIL import Image, ImageDraw
import iv, mg, way2

OW, OH = 1080, 1920
INTER_XB = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
INTER_MD = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'
SITE = iv.S + '/site/mmexport%s.jpg'; RP = iv.S + '/people/real/'; PE = iv.S + '/people/'; B = iv.S + '/broll/'
UP = '/root/.claude/uploads/253db02e-90a6-5547-b8b3-69bd9a44cdc8/'
THEMES = {'teal': dict(acc=(46, 196, 182), cap=(46, 196, 182), font=INTER_XB, name='R1_V1_teal'),
          'gold': dict(acc=(201, 162, 75), cap=(217, 179, 108), font=iv.ANTON, name='R1_V2_gold'),
          'best': dict(acc=(201, 162, 75), cap=(217, 179, 108), font=iv.ANTON, name='R1_V3_best')}
COOLG = "eq=contrast=1.06:saturation=0.82:brightness=-0.02,colorbalance=rs=-0.04:bs=0.06:rm=-0.02:bm=0.04"   # banking years (skin kept)
WARM_T = (1.06, 1.0, 0.9); STEEL_T = (0.95, 1.0, 1.05)
# Sarah r1 line, timings from the waveform pauses (s, relative to her start)
SAR = dict(dur=17.40, picture=0.0, site=2.08, now=3.98, workers=6.95, steel=8.02, concrete=9.15, homes=10.56, vanta=14.97)

def theme(v):
    T = THEMES[v]; iv.GOLD = T['cap']; iv.ANTON = T['font']; mg.GOLD = T['acc']; mg.ANTON = T['font']; return T

def hook_draw(fr, t, H, T):
    if 'L' not in H:
        c2 = iv.WHITE if T['font'] == INTER_XB else T['cap']
        H['L'] = [iv.text_layer([(H['l'][0], iv.WHITE)], 80, T['font'], shadow=0.7, blur=14), iv.text_layer([(H['l'][1], c2)], 80, T['font'], shadow=0.7, blur=14)]
    D = 0.3; u = iv.eout(t / D); u2 = iv.eout((t - 0.25) / D); uo = 1 - iv.ease((t - (H['dur'] - D)) / D)
    if T['font'] == INTER_XB:                                      # teal bar above line 1 (approved 4 Nov style)
        d = ImageDraw.Draw(fr); w = int(96 * min(u, uo)); d.rectangle((OW / 2 - w / 2, 70, OW / 2 + w / 2, 76), fill=T['acc'] + (int(255 * min(u, uo)),))
    iv.place(fr, H['L'][0], OW / 2, 130 + (1 - u) * 26, a=min(u, uo)); iv.place(fr, H['L'][1], OW / 2, 222 + (1 - u2) * 26, a=min(u2, uo))

def lower_third(fr, t, L, T):
    tl = t - L['t0']; a = min(iv.eout(tl / 0.35), 1 - iv.ease((t - (L['t1'] - 0.35)) / 0.35))
    if a <= 0: return
    if 'A' not in L:
        L['A'] = iv.text_layer([('JOHN YAN', iv.WHITE)], 50, T['font'], shadow=0.75, blur=10)
        L['B'] = iv.text_layer([('FOUNDER & CEO, BLACKSTONE REAL ESTATE', iv.WHITE)], 30, INTER_MD, shadow=0.8, blur=8)
    x = 70; y = int(OH * 0.665); d = ImageDraw.Draw(fr); bw = int(96 * iv.eout(tl / 0.3))
    d.rectangle((x, y - 46, x + bw, y - 40), fill=T['acc'] + (int(255 * a),))
    iv.place(fr, L['A'], x - 40 + L['A'].width / 2 + (1 - iv.eout(tl / 0.35)) * -24, y, a=a)
    iv.place(fr, L['B'], x - 40 + L['B'].width / 2 + (1 - iv.eout((tl - 0.1) / 0.35)) * -24, y + 52, a=a)

def word_pop(fr, t, W, T):
    tl = t - W['t0']; a = min(iv.eout(tl / 0.25), 1 - iv.ease((t - (W['t1'] - 0.3)) / 0.3))
    if a <= 0: return
    if 'L' not in W: W['L'] = iv.text_layer([(W['text'], W.get('col', iv.WHITE))], W.get('size', 110), T['font'], shadow=0.7, blur=14)
    iv.place(fr, W['L'], OW / 2, W['y'] + (1 - iv.eout(tl / 0.25)) * 30, a=a, sc=0.92 + 0.08 * iv.eout(tl / 0.25))

def end_card(T):
    def draw(fr, tl, p):
        mg.bg(fr, (14, 14, 16), (22, 20, 18), tl, vign=True)
        if 'L' not in p:
            p['L'] = iv.text_layer([('VANTA HOUSE', iv.WHITE)], 150 if T['font'] != INTER_XB else 104, T['font'], shadow=0.4, blur=12)
            p['L2'] = iv.text_layer([('NAGURU, KAMPALA', T['acc'] if T['font'] != INTER_XB else iv.WHITE)], 48, INTER_MD if T['font'] == INTER_XB else iv.INTERB, shadow=0.4, blur=8)
            p['L3'] = iv.text_layer([('HANDOVER EXPECTED OCTOBER 2027', (175, 175, 175))], 30, iv.INTERB, shadow=0.0, blur=1)
            p['L4'] = iv.text_layer([(iv.CREDIT, (140, 140, 140))], 20, iv.INTERB, shadow=0.0, blur=1)
        u = iv.eout(tl / 0.45); u2 = iv.eout((tl - 0.3) / 0.45); u3 = iv.eout((tl - 0.7) / 0.45); sc = 1 + 0.03 * min(tl / 4, 1)
        y = OH * 0.46; d = ImageDraw.Draw(fr); bw = int(96 * u)
        d.rectangle((OW / 2 - bw / 2, y - p['L'].height / 2 - 6, OW / 2 + bw / 2, y - p['L'].height / 2), fill=T['acc'] + (int(255 * u),))
        iv.place(fr, p['L'], OW / 2, y + (1 - u) * 26, a=u, sc=sc)
        iv.place(fr, p['L2'], OW / 2, y + p['L'].height * 0.5 + 40 + (1 - u2) * 20, a=u2, sc=sc)
        iv.place(fr, p['L3'], OW / 2, y + p['L'].height * 0.5 + 120, a=u3 * 0.9)
        iv.place(fr, p['L4'], OW / 2, OH * 0.95, a=min(u3, 0.9))
    return draw

def build(v):
    T = theme(v); R = way2.REELS['R1']; P = way2.build(R)
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
    for p in pics: p['top'] = 0.48
    ov = []; sfx = [s for s in P['sfx'] if s[0] != 'reverse_swell']; ovl = []; G = list(P['G'])
    for g in G: g['bar'] = True
    def photo(t0, t1, path, tint=WARM_T, z=(1.0, 1.08), cx=0.5, cy=0.5, snd=True):
        ov.append(dict(t=t0, dur=t1 - t0, kind='photo', path=path, z0=z[0], z1=z[1], cx=cx, cy=cy, tint=tint))
        if snd: sfx.append(('pop_soft', t0, -24))
    def clip(t0, t1, path, grade, start=0.0, z=(1.02, 1.1)):
        ov.append(dict(t=t0, dur=t1 - t0, kind='clip', path=path, src=start, grade=grade, z0=z[0], z1=z[1])); sfx.append(('whoosh_soft_1', t0 - 0.05, -15))
    # Row2: trading screen on "investment banking" (cool) - after the hook's first 2 s
    t_ib = wt('investment banking'); t_saw = wt('saw significant'); t_af = wt("africa's"); t_mk = wt('markets', last=True)
    clip(max(2.0, t_ib - 0.1), t_saw - 0.1, B + 'b1_trading_screen_4.mp4', mg_cool := "eq=saturation=0.75:contrast=1.06,colorbalance=bs=0.08:rs=-0.06")
    # Row3: lower third while he says "I saw significant opportunities"
    ovl.append(('lt', dict(t0=t_saw, t1=t_af - 0.05)))
    # Row4: map card China -> Kampala on "Africa's real estate markets" (look C)
    ov.append(dict(t=t_af - 0.15, dur=t_mk + 0.45 - (t_af - 0.15), kind='card', draw=mg.journey_card)); sfx += [('riser_2', t_af - 0.15, -22), ('whoosh_soft_1', t_af + 0.2, -15), ('pop_soft', t_af - 0.15 + 1.85, -20)]
    # founder: Abdullahi's black-and-white portrait + name on "I founded Blackstone"
    t_f = wt('i founded blackstone', 179); t_ib2 = wt('investment analysis', 179) if True else None
    ov.append(dict(t=t_f + 0.35, dur=2.6, kind='card', draw=mg.founder_card, photo='john_headshot_black_shirt.jpg')); sfx += [('whoosh_soft_1', t_f + 0.25, -16), ('pop_soft', t_f + 2.65, -24)]
    # Row6: market screen again on "investment analysis" (cool)
    clip(t_ib2 - 0.1, t_ib2 + 1.6, B + 'b1_trading_screen_4.mp4', mg_cool, start=4.0)
    # Row8: steel + Kampala towers on "efficient execution to Uganda" (look B -> warm)
    t_ee = wt('efficient execution', 179); t_ug = wt('uganda', 190, last=True)
    photo(t_ee - 0.1, t_ug + 0.35, SITE % '1792497989322', tint=STEEL_T if v == 'best' else WARM_T, z=(1.0, 1.1))
    # Row10: slab + crane on "quality developments"
    t_qd = wt('quality developments', 194); t_lt = wt('long-term', 194) if True else None
    photo(t_qd - 0.1, t_lt - 0.1, SITE % '1792497986840', tint=STEEL_T if v == 'best' else WARM_T)
    if v == 'best':     # V3 extras: partners photo on "partnerships", looks follow the words
        t_ps = wt('partnerships', 194); photo(t_ps - 0.15, jend + 0.3, RP + '6baeb5bd.jpg', cx=0.25, cy=0.4)
        for p in pics:
            if t_ib - 0.3 <= p['t'] < t_saw: p['grade'] = COOLG
    # Sarah closes: real site pictures under her words, render (artist's impression) on "a hundred homes", end card on "Vanta House"
    s0 = jend + 0.35; S_ = {k: s0 + v_ for k, v_ in SAR.items() if k != 'dur'}; s1 = s0 + SAR['dur']
    vol = iv.lufs(iv.SND + 'sarah_r1_cta.mp3')
    sar_pics = [('picture', 'site', SITE % '1792497982990'), ('site', 'now', SITE % '1792673498404'), ('now', 'workers', SITE % '1792673493181'),
                ('workers', 'steel', PE + 'brick_laying.jpg'), ('steel', 'concrete', SITE % '1792497989322'), ('concrete', 'homes', PE + 'slab_pour_sky.jpg')]
    for a, b, path in sar_pics: photo(S_[a] - 0.05, S_[b] - 0.05, path, tint=STEEL_T if v == 'best' else WARM_T, z=(1.0, 1.07), snd=(a != 'picture'))
    photo(S_['homes'] - 0.05, S_['vanta'] - 0.05, PE + 'render_vanta_house.jpg', tint=None, z=(1.0, 1.06), cx=0.3)
    ovl.append(('imp', dict(t0=S_['homes'] - 0.05, t1=S_['vanta'] - 0.05)))
    ovl.append(('pop', dict(t0=S_['homes'] + 1.0, t1=S_['vanta'] - 0.1, text='HANDOVER EXPECTED', y=330, size=60)))
    ovl.append(('pop', dict(t0=S_['homes'] + 1.0, t1=S_['vanta'] - 0.1, text='OCTOBER 2027', y=420, size=110, accent=True)))
    if v == 'best':
        for k, w, y in (('workers', 'REAL WORKERS', 300), ('steel', 'REAL STEEL', 300), ('concrete', 'REAL CONCRETE', 300)):
            nx = {'workers': 'steel', 'steel': 'concrete', 'concrete': 'homes'}[k]
            ovl.append(('pop', dict(t0=S_[k], t1=S_[nx] - 0.05, text=w, y=y, size=120))); sfx.append(('whoosh_soft_1', S_[k] - 0.05, -18))
    sfx += [('sarah_r1_cta', s0, (P.get('_vl') or 0)), ('pop_soft', S_['homes'] + 1.0, -22)]
    end = S_['vanta'] - 0.05; dur = s1 + 2.6
    pics = pics + ov + [dict(t=end, dur=dur - end, kind='card', draw=end_card(T), nocap=True)]
    # last John shot holds until Sarah's first picture
    srcp = sorted([p for p in pics if p.get('kind', 'src') == 'src'], key=lambda p: p['t'])
    if srcp: srcp[-1]['dur'] = max(srcp[-1]['dur'], s0 - srcp[-1]['t'])
    sfx.append(('reverse_swell', end - 2.0, -19))
    # captions: John (Way 2 chunks) + Sarah (her words, up to Kampala)
    sw = json.load(open(iv.S + '/sarah/vanta_reel_r1_voice.json'))['words']
    marks = [0.0, 2.08, 3.98, 6.95, 8.02, 9.15, 10.56, 14.97, 17.4]
    words = [w for w in sw if w['t'] < 17.3]; caps = list(P['caps'])
    kw = {'site.', 'vanta', 'house', 'real', '2027.', 'naguru,', 'kampala.', 'picture.'}
    for a, b in zip(marks, marks[1:]):
        ws = [w['w'] for w in words if a - 0.05 <= (w['t'] + (0.0 if w['t'] < 3.92 else 0.0)) < b - 0.05]
        if not ws: continue
        if a >= 14.9: continue                                        # end card carries VANTA HOUSE / NAGURU, KAMPALA
        chunks = [ws[i:i + 4] for i in range(0, len(ws), 4)]; seg = (b - a) / len(chunks)
        for k, ch in enumerate(chunks):
            caps.append((s0 + a + k * seg, s0 + a + (k + 1) * seg - 0.04, [(w, w.lower() in kw) for w in ch]))
    lifts = [l for l in P['lifts'] if l[1] <= jend + 0.01] + [(s1 + 0.1, dur)]
    H = P['H']
    def extra(fr, t):
        t = float(t)
        if t < H['dur']: hook_draw(fr, t, H, T)
        for k, o in ovl:
            if o['t0'] <= t <= o['t1']:
                if k == 'lt': lower_third(fr, t, o, T)
                elif k == 'imp': mg.label(fr, t, o, "Artist's impression")
                elif k == 'pop':
                    if o.get('accent'): o['col'] = T['acc']
                    word_pop(fr, t, o, T)
    return dict(P, pics=pics, G=G, sfx=sfx, caps=caps, dur=dur, extra=extra, lifts=lifts, end=end, T=T)

if __name__ == '__main__':
    which = sys.argv[1:] or ['teal', 'gold', 'best']
    for v in which:
        if v == 'plan':
            for vv in ('teal', 'best'):
                P = build(vv); print(vv, 'dur %.1f' % P['dur'], [(round(p['t'], 1), round(p['dur'], 1), p.get('kind')) for p in P['pics'] if p.get('kind') != 'src'])
            break
        P = build(v); T = P['T']
        vid = iv.render_video('r1_' + v, OW, OH, P['pics'], P['G'], P['caps'], P['dur'], cap_y=1490, cap_size=50, extra=P['extra'])
        # Sarah level: match John's cleaned voice loudness (about -17.7 LUFS), then the shared -14 LUFS master
        gs = -17.7 - iv.lufs(iv.SND + 'sarah_r1_cta.mp3')
        sfx = [(nm, t, gs if nm == 'sarah_r1_cta' else g) for nm, t, g in P['sfx']]
        a = iv.render_audio('r1_' + v, P['voice'], sfx, 'music_modern_upbeat_A.mp3', P['dur'], music_db_under=19.0, smooth=True, lift=P['lifts'], lift_db=7.0)
        print(iv.encode('r1_' + v, vid, a, T['name']))
