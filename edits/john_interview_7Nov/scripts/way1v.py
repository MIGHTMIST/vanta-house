# WAY 1 VERTICAL "MOOD PLUS" (8 Nov): the full interview (Way 1 cut: cold open, 8 chapters, close) re-made 9:16 in the
# Way 3 MOOD PLUS style the owner picked as the best: close vertical framing on John, boxed captions with gold keywords,
# Anton word titles with gold bar, cool-blue China stock -> warm golden Africa, real face-checked photos (warm tint),
# gold light leaks on beat changes, my motion graphics (journey line, founder portrait, step tracker, gap bars, papers,
# blueprint -> render, location tag), name band, original end card with gold dust. Host heard asking, never shown.
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
from PIL import ImageDraw
import iv, mg, mgk, way1
from iv import text_layer, place, ANTON, INTERB, WHITE, GOLD, eout, ease
from way2g import JX, cx_for
from way3m import COOL, WARM, WARM_T

OW, OH = 1080, 1920
B = iv.S + '/broll/'; PE = iv.S + '/people/'; RP = PE + 'real/'; UP = '/root/.claude/uploads/253db02e-90a6-5547-b8b3-69bd9a44cdc8/'
CL, CM, TOP = (1.55, 1.72), (1.12, 1.24), 0.48           # same vertical framing as Way 3

def build():
    P = way1.build()
    voice = [(float(x), float(y), float(t0)) for x, y, t0 in P['voice']]
    end = float(P['end']); dur = float(P['dur'])
    # timeline window of every EDL segment
    segs = [dict(kind=k, lab=l, rngs=r, t0=None, t1=None) for k, r, l in way1.EDL]; si = 0
    for x, y, t0 in voice:                      # voice is in EDL order (the cold open repeats answer audio, so walk in order)
        while not any(a - 0.01 <= x < b for a, b in segs[si]['rngs']): si += 1
        s = segs[si]; s['t0'] = t0 if s['t0'] is None else s['t0']; s['t1'] = t0 + y - x
    def wt(ph, after_t=0.0, src_after=0.0):
        a0 = src_after
        while True:
            i = iv.find(ph, a0)
            for x, y, t0 in voice:
                if x - 0.03 <= iv.WORDS[i]['t'] < y:
                    tt = t0 + iv.WORDS[i]['t'] - x
                    if tt >= after_t: return tt
            a0 = iv.WORDS[i]['t'] + 0.01
    def wend(ph, after_t=0.0):                 # timeline end of the last word of a phrase
        i = iv.find(ph); n = len(ph.split()); t = wt(ph, after_t)
        return t + iv.WORDS[i + n - 1]['end'] - iv.WORDS[i]['t']
    seg_of = lambda t: next(s for s in segs if s['t0'] - 0.4 <= t <= s['t1'] + 0.4)

    # 1. John, re-framed vertical (same cut, same switches at sentence breaks)
    pics = []
    for p in P['pics']:
        if p.get('kind', 'src') != 'src': continue
        med = p['src'] >= 470
        punch = p['z0'] in (2.35, 1.42)
        z0 = (CM if med else CL)[1 if punch else 0]
        pics.append(dict(p, z0=z0, z1=z0 + 0.04, top=TOP))
    card = [p for p in P['pics'] if p.get('kind') == 'card']           # original end card
    ov = []; sfx = list(P['sfx']); fxs = []; overlays = []; G = []
    def clip(t0, t1, path, grade, **k):
        ov.append(dict(t=t0, dur=t1 - t0, kind='clip', path=B + path, src=k.pop('start', 0.0), grade=grade, **k)); sfx.append(('whoosh_soft_1', t0 - 0.12, -19))
    def photo(t0, t1, key, **k):
        path = RP + key + '.jpg' if '/' not in key else key
        cx = k.pop('cx', cx_for(path, JX.get(key, 0.5)) if '/' not in key else 0.5)
        ov.append(dict(t=t0, dur=t1 - t0, kind='photo', path=path, z0=k.pop('z0', 1.0), z1=k.pop('z1', 1.07), cx=cx, cy=k.pop('cy', 0.4),
                       tint=k.pop('tint', WARM_T), **k)); sfx.append(('whoosh_soft_1', t0 - 0.1, -21))
    def cardd(t0, t1, fn, **k): ov.append(dict(t=t0, dur=t1 - t0, kind='card', draw=fn, **k))
    def leak(t, start=0.0, a=0.6): fxs.append(dict(t=t - 0.45, dur=1.2, path=B + 'b7_lightleak_gold_1.mp4', start=start, alpha=a))
    gy = int(OH * 0.105)
    def word(text, t, d, size=None, **k):
        g = dict(text=text, t=t - 0.05, dur=d, x=OW / 2, y=gy, size=size or int(OW * 0.15), bar=True, **k); G.append(g)
        sfx.extend([(k.get('sfx_in', 'whoosh_soft_1'), g['t'] - 0.03, k.get('g_in', -15)), ('pop_soft', g['t'] + g['dur'] - 0.3, -24)])

    # chapter titles in the Way 3 word-title look (number in gold above), light leak on every chapter change
    for C in [o for k, o in P['overlays'] if k == 'chapter']:
        n = len(C['text']); size = min(130, int(OW * 0.80 / (0.43 * n)))
        G.append(dict(text=C['n'], kind='sub', col=GOLD, size=62, t=C['t'], dur=C['dur'], x=OW / 2, y=gy - 92))
        G.append(dict(text=C['text'], t=C['t'], dur=C['dur'], x=OW / 2, y=gy + 10, size=size, bar=True))
        leak(C['t'], start=(int(C['n']) % 3) * 1.5, a=0.5)

    # COLD OPEN: cool China -> journey line -> warm sunrise
    c = segs[0]
    t_ch = wt("china's"); t_bk = wt('banking'); t_saw = wt('saw significant'); t_af = wt("africa's")
    word('10 YEARS', wt('10'), min(3.0, t_saw - wt('10')), size=int(OW * 0.16))
    clip(t_ch - 0.15, t_bk - 0.1, 'b1_shanghai_day_skyline_1.mp4', COOL, z0=1.0, z1=1.08)
    clip(t_bk - 0.1, t_saw - 0.05, 'b1_trading_screen_4.mp4', COOL + ',boxblur=6:1', z0=1.05, z1=1.15)
    cardd(t_saw - 0.05, t_af - 0.2, mg.journey_card); sfx.append(('whoosh_soft_1', t_saw - 0.15, -18))
    clip(t_af - 0.2, c['t1'] + 0.25, 'b2_sunrise_sun_1.mp4', WARM, z0=1.0, z1=1.06); leak(t_af, a=0.85)

    # 01 WHO IS BLACKSTONE: name band on John, then real partner photo + plans
    a = segs[2]
    band = dict(t=a['t0'] + 0.5, dur=3.4)
    sfx += [('pop_soft', band['t'], -20), ('whoosh_soft_1', band['t'] + band['dur'] - 0.35, -20)]
    t_pi = wt('professional investment principles', a['t0']); t_ip = wt('international perspectives', a['t0'])
    photo(max(t_pi - 0.2, band['t'] + band['dur']), t_ip - 0.1, '88fcf6d9')
    clip(t_ip - 0.1, a['t1'] + 0.3, 'b5_plans_on_desk_5.mp4', WARM, z0=1.0, z1=1.08)

    # 02 WHY HE STARTED: the same China line again, now as Hong Kong night (cool) and a real site photo (warm)
    a = segs[4]
    t_ch2 = wt("china's", a['t0']); t_saw2 = wt('saw significant', a['t0']); t_af2 = wt("africa's", a['t0'])
    clip(t_ch2 - 0.15, t_saw2 - 0.05, 'b1_hongkong_night_harbour_3.mp4', COOL, z0=1.0, z1=1.08)
    photo(t_af2 - 0.2, wend('markets', a['t0']) + 0.25, 'e05eea2c', z0=0.96, z1=1.0)
    t_f = wt('i founded blackstone', a['t0'])
    cardd(t_f - 0.1, t_f + 3.5, mg.founder_card, photo='john_headshot_black_shirt.jpg'); leak(t_f, start=2.0, a=0.6); sfx.append(('whoosh_soft_1', t_f - 0.2, -18))
    t_ug = wt('uganda', a['t0']); clip(max(t_ug - 1.6, t_f + 3.5), t_ug + 1.0, 'b2_nile_aerial_4.mp4', WARM, z0=1.0, z1=1.05)
    t_pa = wt('partnerships', a['t0']); photo(t_pa - 0.2, min(t_pa + 2.1, a['t1'] + 0.3), '6baeb5bd')

    # 03 WHAT WE DO: real site visits, then plan -> slab -> bricks under the LAND/BUILD/MARKET/DELIVER tracker
    a = segs[6]
    t_rp = wt('residential property', a['t0']); t_pp = wt('project investment', a['t0']); t_sp = wt('strategic real estate', a['t0'])
    photo(t_rp - 0.2, t_pp + 1.6, '259a9287')
    photo(t_sp - 0.2, wend('partnerships', t_sp) + 0.3, '3c89857d')
    t_land = wt('land acquisition', a['t0']); t_con = wt('construction coordination', a['t0']); t_mk = wt('marketing', a['t0']); t_del = wt('delivery', a['t0'])
    photo(t_land - 0.3, t_con - 0.05, PE + 'floorplan_towers.jpg', tint=None, cy=0.45, z1=1.1)
    photo(t_con - 0.05, t_mk, PE + 'slab_pour_sky.jpg', cx=0.3, cy=0.5)
    photo(t_mk, a['t1'] + 0.3, PE + 'brick_laying.jpg', cx=0.45, cy=0.5, z0=1.07, z1=1.0)
    overlays.append(('steps', dict(t0=t_land - 0.2, t1=t_del + 0.9, hits=[t_land, t_con, t_mk, t_del], y=0.105)))
    sfx += [('pop_soft', h, -23) for h in (t_land, t_con, t_mk, t_del)] + [('ambience_building_site', t_con - 0.2, -26)]

    # 04 THE BUSINESS CLIMATE: warm real moments, cranes for growth, partners, the papers on "integrity"
    a = segs[8]
    t_lv = wt('we really love', a['t0']); photo(t_lv - 0.3, t_lv + 2.4, 'c7cda191', cy=0.35)
    t_ur = wt('urbanization', a['t0']); clip(t_ur - 0.2, wend('population growth', a['t0']) + 0.3, 'b3_cranes_timelapse_1.mp4', WARM, z0=1.0, z1=1.06)
    t_dd = wt('careful due diligence', a['t0']); photo(t_dd - 0.2, t_dd + 2.2, '6c004a77', cx=0.62)
    t_sl = wt('strong local partnerships', a['t0']); photo(t_sl - 0.2, t_sl + 2.4, '75bc38b2')
    t_lm = wt('local market', a['t0']); t_in = wt('integrity', a['t0'])
    photo(t_lm - 0.3, t_in - 1.5, '8661a8bb', z0=1.04, z1=1.12)
    cardd(t_in - 1.5, a['t1'] + 0.3, mg.papers_card, stamp_dy=0.07); sfx.append(('impact_boom_v2', t_in - 1.5 + 1.25, -22))

    # 05 WHY UGANDA: Nile, golden site, THE GAP word + bars over John, brick-laying hands on "professional developers"
    a = segs[10]
    t_sm = wt('several african markets', a['t0']); t_sp2 = wt('strategic position', a['t0']) + 1.2; t_m = t_sm - 0.2 + 3.1
    clip(t_sm - 0.2, t_m, 'b2_nile_aerial_4.mp4', WARM, start=2.8, z0=1.02, z1=1.08)
    clip(t_m, t_sp2, 'b2_sunrise_sun_1.mp4', WARM, start=min(3.6, 5.9 - (t_sp2 - t_m)), z0=1.04, z1=1.08)
    t_gd = wt('growing demand', a['t0']); photo(t_gd - 0.2, wt('i believe that', a['t0']) - 0.1, PE + 'site_evening_3.jpg', cx=0.5, cy=0.45)
    t_gap = wt('gap', a['t0']); word('THE GAP', t_gap, 2.4)
    hd, hs = wt('housing demand', t_gap), wt('quality supply', t_gap)
    gp = dict(t0=t_gap + 2.4, hit_gap=t_gap + 2.65); gp['hit_demand'] = max(hd, gp['t0'] + 0.2); gp['hit_supply'] = max(hs, gp['hit_demand'] + 0.5)
    t_pd = wt('professional developers', a['t0']); gp['t1'] = t_pd - 0.15
    overlays.append(('gap', gp)); sfx += [('pop_soft', gp['hit_demand'], -24), ('pop_soft', gp['hit_supply'], -24)]
    photo(t_pd - 0.15, a['t1'] + 0.3, '8c61df7f')

    # 06 OPEN TO PARTNERS: landowners, the real handshake on "joint ventures", local + international, key handover
    a = segs[12]
    t_lo = wt('landowners', a['t0']); photo(t_lo - 0.3, t_lo + 2.2, '10c246f9')
    t_jv = wt('joint ventures', a['t0']); photo(t_jv - 0.3, t_jv + 2.4, '19867d84')
    t_le = wt('local expertise', a['t0']); photo(t_le - 0.3, t_le + 2.4, 'b3c0160b')
    t_ss = wt('stronger and sustainable', a['t0']); clip(t_ss - 0.6, a['t1'] + 0.3, 'b5_key_handover_handshake_2.mp4', WARM, z0=1.0, z1=1.06)

    # 07 WHAT'S NEXT: approved drawing -> render, the team on the real site with the location tag, more real moments
    a = segs[14]
    t_v = wt('van house', a['t0']); t_n = wt('navuru', a['t0'])
    cardd(t_v - 0.15, t_n - 0.2, mg.blueprint_card); sfx.append(('riser_2', t_v - 0.15, -26)); leak(t_v, start=3.5, a=0.75)
    photo(t_n - 0.2, t_n + 2.8, PE + 'site_group5.jpg', cx=0.5, cy=0.5)
    word('NAGURU', t_n, 2.4)
    overlays.append(('loc', dict(t0=t_n + 0.1, t1=t_n + 2.8, y=0.22))); sfx.append(('pop_soft', t_n + 0.1, -22))
    t_cs = wt('carefully selected', a['t0']); photo(t_cs - 0.2, t_cs + 2.3, 'a497f854')
    t_hq = wt('high-quality residential', a['t0']) if 'high-quality' in iv.TOK else wt('develop more', a['t0'])
    photo(t_hq - 0.1, t_hq + 2.4, PE + 'render_vanta_house.jpg', tint=None, cx=0.3, cy=0.45)
    imp = dict(t0=t_hq - 0.1, t1=t_hq + 2.3); overlays.append(('imp', imp)); rend_ph = ov[-1]
    t_td = wt('trusted developments', a['t0']); t_h = (t_td - 0.2 + a['t1'] + 0.3) / 2
    photo(t_td - 0.2, t_h, 'cd590606'); photo(t_h, a['t1'] + 0.3, 'f729f654')

    # 08 LOCAL PARTNERS WANTED: John with local partners on site, the site itself on "property agents"
    a = segs[16]
    t_mp = wt('more local partners', a['t0']); photo(t_mp - 0.2, t_mp + 2.3, 'dfa63778')
    t_ll = wt('local landlords', a['t0']); photo(t_ll - 0.2, t_ll + 2.4, '1b04dab0')
    t_ag = wt('property agents', a['t0']); photo(t_ag - 2.0, a['t1'] + 0.25, UP + 'e0ebef93-image.jpg', cx=0.5, cy=0.5)

    # CLOSE: on John's face, then the end card with gold dust
    fxs.append(dict(t=end - 0.4, dur=dur - end + 0.4, path=B + 'b7_dust_particles_4.mp4', alpha=0.55))
    sfx += [('whoosh_soft_1', t_ch - 0.2, -18)]
    # smoothness (board review): no John slivers between two cutaways, no sub-second zoom jumps
    ovs = sorted(ov, key=lambda o: o['t'])
    for o0, o1 in zip(ovs, ovs[1:]):
        g = o1['t'] - (o0['t'] + o0['dur'])
        if 0 < g < 1.3: o0['dur'] += g + 0.02
    srcs = sorted(pics, key=lambda p: p['t'])
    for p0, p1 in zip(srcs, srcs[1:]):
        if p1['dur'] < 1.2: p1['z0'] = p1['z1'] = p0['z1']
    imp['t1'] = rend_ph['t'] + rend_ph['dur']                       # label holds to the cut (QA)
    pics = pics + ov + card
    qr = [r for k, rr, l in way1.EDL if k == 'q' for r in rr]
    caps_voice = [v for v in voice if not any(a - 0.01 <= v[0] < b for a, b in qr)]   # the host's questions are heard, not captioned
    caps = iv.cap_chunks(caps_voice, ['blackstone', 'professional', '10', 'years', 'china', 'africa', 'uganda', 'discipline', 'land', 'delivery',
                                      'integrity', 'gap', 'quality', 'partners', 'joint', 'vanta', 'naguru', 'navuru', 'visit', 'trusted', 'love'])
    # QA 8 Nov: no answer caption runs into a host question; proper nouns capitalised (part of the transcript is lower case)
    qs = [s_['t0'] for s_ in segs if s_['kind'] == 'q']
    for c_ in caps:
        for q0 in qs:
            if c_[0] < q0 < c_[1]: c_[1] = q0 - 0.04
    PN = {'uganda': 'Uganda', 'african': 'African', 'africa': 'Africa', "africa's": "Africa's", 'ugandan': 'Ugandan', 'kampala': 'Kampala', 'china': 'China', "china's": "China's"}
    for c_ in caps:
        ws = c_[2]
        for j, (w_, kw) in enumerate(ws):
            core = w_.rstrip('.,?!'); tail = w_[len(core):]
            if core.lower() in PN: ws[j] = (PN[core.lower()] + tail, kw)
            if core.lower() == 'real' and j + 1 < len(ws) and ws[j + 1][0].lower().startswith('estate'): ws[j] = ('Real' + tail, kw)
            if core.lower() == 'estate' and j > 0 and ws[j - 1][0].lower() == 'real': ws[j] = ('Estate' + tail, kw)
            if core.lower() == 'east' and j + 1 < len(ws) and ws[j + 1][0].lower().startswith('africa'): ws[j] = ('East' + tail, kw)
    # music lifts in the breaths: during every question (John listening) and on the end card, as in Way 3
    lifts = [(s['t0'] - 0.3, s['t1'] + 0.3) for s in segs if s['kind'] == 'q'] + [(end, dur)]

    def extra(fr, t):
        t = float(t)
        for k, o in overlays:
            if o['t0'] <= t <= o['t1']:
                if k == 'imp': mg.label(fr, t, o, "Artist's impression")
                else: {'gap': mg.gap_overlay, 'steps': mg.steps_overlay, 'loc': mg.location_overlay}[k](fr, t, o)
        if band['t'] <= t <= band['t'] + band['dur']:       # Way 3 name band (gold bar, Anton name, Inter title)
            if 'A' not in band:
                band['A'] = text_layer([('JOHN YAN', WHITE)], 78, ANTON, shadow=0.7, blur=12)
                band['B'] = text_layer([('Founder & CEO, Blackstone Real Estate', GOLD)], 36, INTERB, shadow=0.7, blur=8)
            tl = t - band['t']; u = eout(tl / 0.35); uo = 1 - ease((tl - (band['dur'] - 0.35)) / 0.35); al = min(u, uo)
            y0 = int(OH * 0.62); mgk.scrim(fr, y0 - 40, y0 + 150, 0.55 * al, fade=60)   # QA: readable on the white shirt
            d = ImageDraw.Draw(fr)
            d.rectangle((60, y0 - 10, 68, y0 + 120), fill=GOLD + (int(255 * al),))
            place(fr, band['A'], 84 + band['A'].width / 2 - 40 * (1 - u), y0 + 18, a=al)
            place(fr, band['B'], 84 + band['B'].width / 2 - 40 * (1 - u), y0 + 92, a=al)
    return dict(pics=pics, G=G, caps=caps, voice=voice, sfx=sfx, fxs=fxs, extra=extra, dur=dur, end=end, lifts=lifts, segs=segs)

if __name__ == '__main__':
    P = build()
    if len(sys.argv) > 1 and sys.argv[1] == 'plan':
        print('dur %.1f' % P['dur'])
        for p in sorted(P['pics'], key=lambda p: p['t']):
            if p.get('kind', 'src') != 'src': print('%7.2f %5.2f %-5s %s' % (p['t'], p['dur'], p['kind'], str(p.get('path', getattr(p.get('draw'), '__name__', '')))[-34:]))
        for g in P['G']: print('G %7.2f %4.1f %s' % (g['t'], g['dur'], g['text']))
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1].startswith('test'):
        a, b = [float(x) for x in sys.argv[2:4]]
        pics = [dict(p, t=p['t'] - a) for p in P['pics']]
        print(iv.render_video('way1v_t', OW, OH, pics, [dict(g, t=g['t'] - a) for g in P['G']], [[c[0] - a, c[1] - a] + c[2:] for c in P['caps']], b - a,
                              cap_y=1490, cap_size=52, fxs=[dict(f, t=f['t'] - a) for f in P['fxs']], cap_box=True, extra=lambda fr, t: P['extra'](fr, t + a)))
        sys.exit()
    v = iv.render_video('way1v', OW, OH, P['pics'], P['G'], P['caps'], P['dur'], cap_y=1490, cap_size=52, fxs=P['fxs'], cap_box=True, extra=P['extra'])
    au = iv.render_audio('way1v', P['voice'], P['sfx'], 'music_way1v_bed.mp3', P['dur'], music_db_under=19.0, smooth=True, lift=P['lifts'], lift_db=8.0)
    print(iv.encode('way1v', v, au, 'John_Way1_FullInterview_MOOD_PLUS_9x16_1080'))
