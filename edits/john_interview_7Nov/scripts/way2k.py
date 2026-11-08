# Way2 reels R2,R3,R4,R5,R7 rebuilt on the MOTION + SOUND KIT (same pattern as r1k.py). Gold + Anton. Same cut, voice, hook words and
# word graphics as way2.REELS; cutaways from way2g.PLAN (photos with tint, kit map card for the journey card, papers/blueprint cards);
# gap bars (R2), step tracker (R4), location tag (R5). Original end card stays. No Sarah, no WhatsApp.
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
import iv, mg, mgk, way2, way2g

OW, OH = 1080, 1920
CAP_Y = 1345
RP = iv.S + '/people/real/'
THEMES = {'gold': dict(acc=(201, 162, 75), font=iv.ANTON, name='gold')}
WARM_T = (1.06, 1.0, 0.9)
PLAN = way2g.PLAN
POPY = 420

def build(rk, v='gold'):
    T = THEMES[v]; mg.GOLD = T['acc']; mg.ANTON = T['font']
    R = way2.REELS[rk]; P = way2.build(R); C = PLAN[rk]
    P['voice'] = [(float(x), float(y), float(t0)) for x, y, t0 in P['voice']]
    voice = P['voice']; end = float(P['end']) if 'end' in P else max(t0 + y - x for x, y, t0 in voice) + 0.45
    def wt(phrase, after=0, last=False):
        a0 = after
        while True:
            try: i = iv.find(phrase, a0)
            except Exception: return None
            j = i + len(phrase.split()) - 1 if last else i
            for x, y, t0 in voice:
                if x - 0.03 <= iv.WORDS[j]['t'] < y: return t0 + iv.WORDS[j]['t'] - x + (iv.WORDS[j]['end'] - iv.WORDS[j]['t'] if last else 0)
            a0 = iv.WORDS[i]['t'] + 0.01
    pics = [p for p in P['pics'] if p.get('kind') != 'card']
    for p in pics: p['top'] = 0.56
    endc = [p for p in P['pics'] if p.get('kind') == 'card']
    sfx = [s for s in P['sfx'] if s[0] not in ('reverse_swell', 'whoosh_cinematic_5', 'pop_soft', 'whoosh_soft_1')]
    ov = []; ovl = []; leaks = []; hide = []; timeline = []
    def leak(t):
        if all(abs(t - x) >= 5.0 for x in leaks): leaks.append(t); return True
        return False
    # hook (his own words), kit title
    sfx += [('sfx_whoosh_soft_2', 0.05, -17), ('sfx_impact_soft_1', 0.3, -19)]
    ovl.append(('hook', dict(t0=0.0, t1=2.9, lines=[(R['hook'][0], (255, 255, 255)), (R['hook'][1], T['acc'])], size=92, gap=96)))
    timeline.append((0.0, 2.9, 'hook: ' + ' / '.join(R['hook'])))
    # word graphics: kit word pops at y=420 (shifted below an overlay tag if one sits there)
    pre_ov = []   # step / location / gap overlays computed first so pops can avoid them
    popsrc = []
    for g in P['G']:
        popsrc.append(dict(t0=g['t'], t1=g['t'] + 2.2, text=g['text'], y=POPY, size=150 if len(g['text']) < 10 else 118))
    # cutaways
    ltypes = []
    for phrase, af, kind, what, ln, o in C['inserts']:
        t0 = wt(phrase, af)
        if t0 is None: print(rk, 'NOT IN REEL:', phrase); continue
        t0 = max(t0 - 0.15 - o.get('pre', 0), 3.0)
        if isinstance(ln, str):
            mode, ph = ln.split(':'); t1 = wt(ph, af, last=(mode == 'until_end'))
            t1 = (t1 + 0.3) if mode == 'until_end' else (t1 - 0.05)
        else: t1 = t0 + ln
        t1 = min(t1, end - 0.05)
        if kind != 'card' and rk == 'R7':       # never a photo of people behind the LANDOWNERS / AGENTS pops
            for g in P['G']:
                if g['t'] - 0.2 <= t1 and t0 <= g['t'] + 2.4: t0 = max(t0, g['t'] + 2.45); t1 = max(t1, t0 + 2.2)
        if kind == 'card':
            if what is mg.journey_card:
                nx = [wt(q[0], q[1]) for q in C['inserts'] if q[2] == 'card' and q[3] is not mg.journey_card]
                nx = [x - 0.15 for x in nx if x and x - 0.15 > t0]
                t1 = max(t1, t0 + 3.7); t1 = min(t1, end - 0.05, *(nx or [99]))
                ov.append(dict(t=t0, dur=t1 - t0, kind='card', draw=mgk.map_card, T=T)); sfx += mgk.map_sfx(t0); hide.append((t0, t1)); name = 'map card (China -> Kampala)'
                sfx.append(('sfx_whoosh_soft_1', t0 - 0.4, -16))
            elif what is mg.papers_card:
                has_int = any(g['text'] == 'INTEGRITY' for g in P['G'])
                ov.append(dict(t=t0, dur=t1 - t0, kind='card', draw=mg.papers_card, title=not has_int)); name = 'papers card'
                sfx += [('sfx_whoosh_soft_1', t0 - 0.1, -17), ('sfx_stamp_thud_1', t0 + 1.3, -15)]
            else:
                ov.append(dict(t=t0, dur=t1 - t0, kind='card', draw=what, title=C.get('papers_title', True))); name = 'blueprint -> render card (Artist\'s impression)'
                sfx += [('sfx_whoosh_soft_1', t0 - 0.1, -17), ('sfx_text_pop_1', t0 + 0.55 * (t1 - t0) + 0.2, -19)]
            if leak(t0 - 0.02): pass
        else:
            path = what if '/' in what else RP + what + '.jpg'
            cx = 0.5 if '/' in what else way2g.cx_for(path, way2g.JX.get(what, 0.5))
            ov.append(dict(t=t0, dur=t1 - t0, kind='photo', path=path, z0=1.0, z1=1.08, cx=cx, cy=0.4, tint=WARM_T)); name = 'photo ' + what.split('/')[-1]
            sfx.append(('sfx_camera_shutter_1', t0 - 0.02, -24))
            if o.get('loc'):
                ovl.append(('loc', dict(t0=t0 + 0.15, t1=t1, y=C.get('loc_y', 0.085)))); sfx.append(('sfx_ui_swoosh_in_1', t0 + 0.12, -19)); name += ' + location tag'
        timeline.append((t0, t1, name + ' on "%s"' % phrase))
    if C.get('gap'):
        tg = [g for g in P['G'] if g['text'] == 'THE GAP']
        gp = dict(t0=(tg[0]['t'] + 2.2 + 0.05) if tg else max(wt('the gap'), 3.0) - 0.3, hit_gap=wt('gap'), hit_demand=wt('housing demand'), hit_supply=wt('quality supply'))
        gp['hit_demand'] = max(gp['hit_demand'], gp['t0'] + 0.15); gp['hit_supply'] = max(gp['hit_supply'], gp['hit_demand'] + 0.7)
        gp['hit_gap'] = max(gp['hit_gap'], gp['hit_supply'] + 0.6); gp['t1'] = gp['hit_gap'] + 2.2
        ovl.append(('gap', gp)); sfx += [('sfx_text_pop_1', gp['hit_demand'], -19), ('sfx_text_pop_2', gp['hit_supply'], -19), ('sfx_text_pop_3', gp['hit_gap'], -17)]
        timeline.append((gp['t0'], gp['t1'], 'gap bars (demand %.1f, supply %.1f, gap %.1f)' % (gp['hit_demand'], gp['hit_supply'], gp['hit_gap'])))
    if C.get('steps'):
        hits = [wt('land acquisition', 220), wt('construction coordination', 220), wt('marketing', 220), wt('delivery', 220)]
        st = dict(t0=hits[0] - 0.35, t1=wt('delivery', 220, last=True) + 0.3, hits=hits, y=C.get('steps_y', 0.2))
        ovl.append(('steps', st)); sfx += [('sfx_text_pop_%d' % (1 + i % 3), h, -19) for i, h in enumerate(hits)]
        timeline.append((st['t0'], st['t1'], 'step tracker hits ' + ','.join('%.1f' % h for h in hits)))
    # pops: avoid an overlay tag sitting at the same height
    for w in popsrc:
        for k, o in ovl:
            if k in ('steps', 'loc') and o['t0'] - 0.2 <= w['t1'] and w['t0'] <= o['t1']:
                w['y'] = 640 if k == 'steps' else 640
        if any(p['kind'] == 'card' and p['draw'] is mg.papers_card and p['t'] <= w['t0'] < p['t'] + p['dur'] for p in ov): w['y'] = 330   # above the top paper
        nc = [p['t'] for p in ov if p['kind'] == 'card' and w['t0'] < p['t'] < w['t1']]
        if nc: w['t1'] = min(nc)
        ovl.append(('pop', w)); sfx += [('sfx_text_pop_3', w['t0'], -16), ('sfx_ui_swoosh_out_1', w['t1'] - 0.2, -22)]
        timeline.append((w['t0'], w['t1'], 'word pop %s y=%d' % (w['text'], w['y'])))
    sfx += mgk.end_sfx(end)
    timeline.append((end, P['dur'], 'original end card'))
    pics = pics + ov + endc
    chunks = []
    for c in P['caps']:
        times = c[3] if len(c) > 3 else [c[0]] * len(c[2])
        chunks.append(dict(t0=c[0] - 0.04, t1=c[1], words=[(w, ts) for (w, kw), ts in zip(c[2], times)]))
    def extra(fr, t):
        t = float(t)
        for k, o in ovl:
            if o['t0'] <= t <= o['t1']:
                if k == 'hook': mgk.title2(fr, t, o, T, y=300)
                elif k == 'pop': mgk.word_pop(fr, t, o, T)
                elif k == 'gap': mg.gap_overlay(fr, t, o)
                elif k == 'steps': mg.steps_overlay(fr, t, o)
                elif k == 'loc': mg.location_overlay(fr, t, o)
        if not any(a <= t <= b for a, b in hide):
            for c in chunks:
                if c['t0'] <= t <= c['t1']: mgk.caption(fr, t, c, T, CAP_Y)
        for lc in leaks: mgk.light_leak(fr, t, lc, 0.7)
    return dict(P, pics=pics, G=[], sfx=sfx, caps=[], dur=P['dur'], extra=extra, end=end, T=T, timeline=sorted(timeline), leaks=leaks)

if __name__ == '__main__':
    args = sys.argv[1:]; test = None
    if args and args[0].startswith('test'): test = float(args[0][4:] or 9); args = args[1:]
    if args and args[0] == 'plan': args = ['R2', 'R3', 'R4', 'R5', 'R7']; test = -1
    args = args or ['R2', 'R3', 'R4', 'R5', 'R7']
    for rk in args:
        P = build(rk)
        if test == -1:
            print(rk, way2.REELS[rk]['name'], 'dur %.1f' % P['dur'], 'leaks', [round(x, 1) for x in P['leaks']])
            for a, b, n in P['timeline']: print('   %5.1f - %5.1f  %s' % (a, b, n))
            continue
        dur = min(test, P['dur']) if test else P['dur']
        vid = iv.render_video('way2k_' + rk + ('_t' if test else ''), OW, OH, P['pics'], [], [], dur, extra=P['extra'])
        if test: print(vid); continue
        a = iv.render_audio('way2k_' + rk, P['voice'], P['sfx'], way2.REELS[rk]['music'], P['dur'], music_db_under=19.0, smooth=True, lift=P['lifts'], lift_db=7.0)
        print(iv.encode('way2k_' + rk, vid, a, 'John_Way2_%s_%s_KIT_9x16_1080' % (rk, way2.REELS[rk]['name'])))
