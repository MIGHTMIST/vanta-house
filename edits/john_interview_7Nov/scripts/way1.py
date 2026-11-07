# WAY 1: the full interview polished (16:9, YouTube / Facebook). Cold open, walk-in, host intro, 9 chapters, close.
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
import iv
from iv import pieces, text_layer, place, ANTON, INTERB, WHITE, GOLD, eout, ease

OW, OH = 1920, 1080
GAP = 0.35
# (kind, src_a, src_b, label)   kind: 'cold' | 'walk' | 'host' | 'q' (question, chapter card) | 'a' (answer) | 'close'
EDL = [   # helper-reviewed 7 Nov: weak/banned parts cut, host only heard asking his questions, ch4 dropped
    ('cold', [(168.13, 179.80)], None),
    ('q', [(116.45, 122.45)], 'WHO IS BLACKSTONE'), ('a', [(123.43, 139.00)], None),
    ('q', [(161.43, 167.85)], 'WHY HE STARTED'), ('a', [(168.15, 201.10)], None),
    ('q', [(203.10, 208.30)], 'WHAT WE DO'), ('a', [(209.02, 238.70)], None),
    ('q', [(283.29, 287.85)], 'THE BUSINESS CLIMATE'), ('a', [(289.21, 326.05)], None),
    ('q', [(329.88, 333.15)], 'WHY UGANDA'), ('a', [(334.76, 365.00)], None),
    ('q', [(366.34, 373.85)], 'OPEN TO PARTNERS'), ('a', [(382.26, 415.15)], None),
    ('q', [(429.71, 433.35)], "WHAT'S NEXT"), ('a', [(435.63, 450.00), (452.19, 454.32), (455.87, 471.40)], None),
    ('q', [(480.20, 483.45), (486.20, 489.00), (492.44, 494.90)], 'LOCAL PARTNERS WANTED'), ('a', [(529.40, 535.70), (536.92, 540.40), (542.30, 556.90)], None),
    ('close', [(621.94, 630.70)], None),
]
CLW, CLM = (2.1, 2.35), (1.25, 1.42)      # close on his face: wide section / medium section

def sentence_splits(a, b):
    """source times of sentence ends inside (a, b) -> picture switches only at sentence breaks"""
    return [w['end'] for w in iv.WORDS if a < w['t'] < b - 0.5 and w['w'][-1] in '.?!']

def lower_third(fr, tl, L):
    D = 0.35; u = eout(tl / D); uo = 1 - ease((tl - (L['dur'] - D)) / D); a = min(u, uo)
    if a <= 0: return
    if 'A' not in L:
        L['A'] = text_layer([(L['l1'], WHITE)], 64, ANTON, shadow=0.7, blur=12)
        L['B'] = text_layer([(L['l2'], GOLD)], 36, INTERB, shadow=0.7, blur=10) if L.get('l2') else None
    x = L['x']; dx = (1 - u) * (-40 if L['side'] == 'l' else 40)
    ax = x + L['A'].width / 2 if L['side'] == 'l' else x - L['A'].width / 2
    place(fr, L['A'], ax + dx, 905, a=a)
    if L['B']: place(fr, L['B'], (x + L['B'].width / 2 if L['side'] == 'l' else x - L['B'].width / 2) + dx, 968, a=a)

def chapter_draw(fr, tl, C):
    D = 0.35; u = eout(tl / D); uo = 1 - ease((tl - (C['dur'] - D)) / D); a = min(u, uo)
    if a <= 0: return
    if 'A' not in C:
        C['A'] = text_layer([(C['n'], GOLD)], 44, ANTON, shadow=0.6, blur=10)
        C['B'] = text_layer([(C['text'], WHITE)], 70, ANTON, shadow=0.7, blur=14)
    xr = 1850
    place(fr, C['A'], xr - C['A'].width / 2, 170 + (1 - u) * 16, a=a)
    place(fr, C['B'], xr - C['B'].width / 2, 245 + (1 - u) * 16, a=a, sc=0.94 + 0.06 * u)

def build():
    t = 0.0; voice = []; pics = []; overlays = []; sfx = []; swells = []; nch = 0; last_cut = 0
    for kind, rngs, lab in EDL:
        src_pieces = [pc for a, b in rngs for pc in pieces(a, b)]
        s0 = t
        if kind == 'q' and nch == 0:
            sfx.append(('whoosh_soft_1', t - 0.15, -8))
        for k, (x, y) in enumerate(src_pieces):
            voice.append((x, y, t))
            CL = CLM if x >= 470 else CLW
            if kind == 'cold':
                pics.append(dict(t=t, dur=y - x, src=x, who='john', z0=CL[1], z1=CL[1] + 0.06, top=0.46))
            elif kind == 'walk':
                pics.append(dict(t=t, dur=y - x, src=x, who='full', z0=1.0, z1=1.04))
            elif kind in ('q', 'host'):     # his question is heard; the picture stays on John listening (host cropped out)
                pics.append(dict(t=t, dur=y - x, src=x, who='john', z0=CL[0], z1=CL[0] + 0.03, top=0.46))
            elif kind == 'close':
                pics.append(dict(t=t, dur=y - x, src=x, who='john', z0=1.25, z1=1.32, top=0.42))
            else:   # answer: alternate wide <-> punch-in, switching at sentence breaks and at every pause cut
                cuts = [x] + [c for c in sentence_splits(x, y) if c - x > 2.5] + [y]
                for c0, c1 in zip(cuts, cuts[1:]):
                    punch = (len(pics) % 2 == 1)
                    z0 = CL[1] if punch else CL[0]; z1 = z0 + 0.03
                    who = 'john'
                    pics.append(dict(t=t + c0 - x, dur=c1 - c0, src=c0, who=who, z0=z0, z1=z1, top=0.46 if c0 < 470 else 0.42))
                # host nods as picture-only cutaways (~every 22 s, wide section only)
                tt = t + 6.0
                while tt < t + (y - x) - 2.0:
                    src_t = x + (tt - t)
                    if False:   # host must not appear (owner, 7 Nov)
                        pics.append(dict(t=tt, dur=1.6, src=src_t, who='host', z0=1.75, z1=1.8, top=0.42)); last_cut = tt
                    tt += 22.0
            t += y - x
            if k + 1 < len(src_pieces): t += 0.12
        if kind == 'q':
            nch += 1
            C = dict(t=s0 + 0.2, dur=3.4, n='%02d' % nch, text=lab)
            overlays.append(('chapter', C)); sfx += [('whoosh_soft_1', C['t'] - 0.05, -15), ('pop_soft', C['t'] + C['dur'] - 0.35, -24)]
            swells.append((C['t'] + 1.5, 1.6, 0.7))
        if kind == 'host' and lab == 'intro':
            L = dict(t=s0 + 1.0, dur=5.0, l1='URBAN REFUGEE MEDIA PLATFORM', l2='Host', side='r', x=1840)
            overlays.append(('lt', L)); sfx += [('pop_soft', L['t'], -20), ('whoosh_soft_1', L['t'] + L['dur'] - 0.35, -18)]
        if kind == 'a' and nch == 1 and not any(o[0] == 'lt' and o[1]['side'] == 'l' for o in overlays):
            L = dict(t=s0 + 0.6, dur=5.5, l1='JOHN YAN', l2='Founder & CEO, Blackstone Real Estate', side='l', x=90)
            overlays.append(('lt', L)); sfx += [('pop_soft', L['t'], -20), ('whoosh_soft_1', L['t'] + L['dur'] - 0.35, -18)]
        t += GAP if kind != 'cold' else 0.25
    end = t; dur = end + 6.0
    # no gaps: every shot holds (source keeps running) until the next shot starts
    srcp = sorted([p for p in pics if p.get('kind', 'src') == 'src'], key=lambda p: p['t'])
    for p0, p1 in zip(srcp, srcp[1:]):
        if p1['t'] > p0['t'] + p0['dur']: p0['dur'] = p1['t'] - p0['t']
    if srcp and srcp[-1]['t'] + srcp[-1]['dur'] < end: srcp[-1]['dur'] = end - srcp[-1]['t']
    pics.append(dict(t=end, dur=dur - end, kind='card', draw=iv.end_card_draw, nocap=True))
    sfx.append(('reverse_swell', end - 2.3, -12))
    pics.sort(key=lambda p: (p['t'], 1 if p.get('who') == 'host' and p.get('dur', 0) < 2 else 0))
    # make host cutaways win over the shot they sit on: move them to the end of the list
    cut = [p for p in pics if p.get('who') == 'host' and p.get('dur', 0) < 2]; pics = [p for p in pics if p not in cut] + cut
    pics = [p for p in pics if p.get('kind') == 'card'] [:0] + [p for p in pics if p.get('kind') != 'card'] + [p for p in pics if p.get('kind') == 'card']
    return dict(voice=voice, pics=pics, overlays=overlays, sfx=sfx, swells=swells, dur=dur, end=end)

def extra_fn(P):
    def f(fr, t):
        for kind, O in P['overlays']:
            if O['t'] <= t <= O['t'] + O['dur']:
                (chapter_draw if kind == 'chapter' else lower_third)(fr, t - O['t'], O)
    return f

if __name__ == '__main__':
    P = build()
    if len(sys.argv) > 1:
        print('dur %.1f s (%.1f min), %d pics, %d voice pieces, %d host cutaways' % (P['dur'], P['dur'] / 60, len(P['pics']), len(P['voice']), sum(1 for p in P['pics'] if p.get('who') == 'host'))); sys.exit()
    # overlays only exist in a few places: tell the renderer which times need drawing
    v = iv.render_video('way1', OW, OH, P['pics'], [], [], P['dur'], extra=extra_fn(P))
    a = iv.render_audio('way1', P['voice'], P['sfx'], 'music_calm_piano_A.mp3', P['dur'], music_db_under=21.0, smooth=True, lift=[(c - w, c + w) for c, w, g in P['swells']] + [(P['end'], P['dur'])], lift_db=6.0)
    print(iv.encode('way1', v, a, 'John_Way1_FullInterview_16x9_1080', crf=18))
