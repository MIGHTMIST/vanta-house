# WAY 2 redo (8 Nov): the six reels with my own motion graphics (mg.py) and face-checked REAL photos of John and his people.
# Same cut, captions, hooks, word graphics and sound as Way 2 (nothing removed - owner 8 Nov); cutaways land on the words they show. No sensitive paper data (mg crops only).
# People are never labelled as landlords/agents/etc.: photos only sit on general words (partners, team, cooperation).
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
from PIL import Image
import iv, mg, way2
from way3g import end_card, flare

RP = iv.S + '/people/real/'; PE = iv.S + '/people/'
WARM_T = (1.07, 1.0, 0.88)
# John's x position (0..1) in each photo so the 9:16 crop keeps him in frame
JX = {'dfa63778': 0.27, '6baeb5bd': 0.37, '75bc38b2': 0.43, 'c7cda191': 0.25, '19867d84': 0.5, 'cd590606': 0.5, '88fcf6d9': 0.4,
      'e05eea2c': 0.5, '259a9287': 0.3, '10c246f9': 0.4, 'a497f854': 0.6, 'f729f654': 0.55, '8661a8bb': 0.4, '10560832': 0.3,
      '1b04dab0': 0.4, '3c89857d': 0.45, '8c61df7f': 0.5, 'b3c0160b': 0.6}
def cx_for(path, xc, OW=1080, OH=1920):
    w, h = Image.open(path).size; f = max(OW / w, OH / h) * 1.12; W = w * f; cw = OW
    if W <= cw + 1: return 0.5
    start = min(max(xc * W - cw / 2, 0), W - cw); return start / (W - cw)

# per reel: inserts = (phrase, after, kind, what, length, opts) ; overlays = gap / steps / loc ; drop = Way 2 graphics replaced
PLAN = {
 'R1': dict(inserts=[('10 years', 0, 'card', mg.years_card, 'until:saw significant', {}),
                     ('saw significant', 0, 'card', mg.journey_card, 'until_end:markets', {}),
                     ('i founded blackstone', 179, 'card', mg.founder_card, 4.2, {}),
                     ('uganda', 190, 'photo', 'dfa63778', 2.4, {}),
                     ('partnerships', 194, 'photo', '6baeb5bd', 2.3, {})],
            drop=[]),
 'R2': dict(inserts=[('strategic position', 0, 'card', mg.journey_card, 3.0, {}),
                     ('growing demand', 0, 'card', mg.blueprint_card, 'until_end:quality housing', {})],
            gap=True, drop=[]),
 'R3': dict(inserts=[('we really love', 0, 'photo', 'c7cda191', 2.4, {'pre': -0.6}),
                     ('strong local partnerships', 0, 'photo', '75bc38b2', 2.4, {}),
                     ('operating with', 0, 'card', mg.papers_card, 'until_end:integrity', {})],
            drop=[], papers_title=False),
 'R4': dict(inserts=[('land acquisition', 220, 'photo', PE + 'floorplan_towers.jpg', 'until:construction coordination', {'real': False}),
                     ('construction coordination', 220, 'photo', PE + 'slab_pour_sky.jpg', 'until:marketing', {'real': False}),
                     ('marketing', 220, 'photo', PE + 'brick_laying.jpg', 'until_end:delivery', {'real': False}),
                     ('residential', 0, 'card', mg.blueprint_card, 3.0, {}),
                     ('partnerships', 0, 'photo', '19867d84', 2.3, {})],
            steps=True, steps_y=0.2, drop=[]),
 'R5': dict(inserts=[('van house', 435, 'card', mg.blueprint_card, 2.9, {}),
                     ('navuru', 0, 'photo', 'cd590606', 2.6, {'loc': True, 'pre': 0.6}),
                     ('develop more', 0, 'photo', 'e05eea2c', 2.4, {})],
            drop=[], loc_y=0.22),
 'R7': dict(inserts=[('we welcome cooperation', 0, 'photo', '19867d84', 2.4, {'pre': -0.3}),
                     ('i would like to work', 0, 'photo', '88fcf6d9', 2.4, {}),
                     ('i also would', 0, 'photo', '259a9287', 2.4, {})],
            drop=[]),
}

def build(rk):
    R = way2.REELS[rk]; P = way2.build(R); C = PLAN[rk]
    P['voice'] = [(float(x), float(y), float(t0)) for x, y, t0 in P['voice']]
    voice = P['voice']; end = float(P['end']) if 'end' in P else max(t0 + y - x for x, y, t0 in voice) + 0.45
    def wt(phrase, after=0, last=False):
        a0 = after
        while True:                       # first mention of the phrase that is actually inside this reel
            try: i = iv.find(phrase, a0)
            except Exception: return None
            j = i + len(phrase.split()) - 1 if last else i
            for x, y, t0 in voice:
                if x - 0.03 <= iv.WORDS[j]['t'] < y: return t0 + iv.WORDS[j]['t'] - x + (iv.WORDS[j]['end'] - iv.WORDS[j]['t'] if last else 0)
            a0 = iv.WORDS[i]['t'] + 0.01
    drop = [g for g in P['G'] if g['text'] in C['drop']]
    G = [g for g in P['G'] if g not in drop]
    sfx = [s for s in P['sfx'] if not any(g['t'] - 0.4 <= s[1] <= g['t'] + g['dur'] + 0.4 for g in drop)]
    pics = [p for p in P['pics'] if p.get('kind') != 'card']; ov = []; overlays = []; flares = []
    for phrase, af, kind, what, ln, o in C['inserts']:
        t0 = wt(phrase, af)
        if t0 is None: print(rk, 'NOT IN REEL:', phrase); continue
        t0 = max(t0 - 0.15 - o.get('pre', 0), 3.0)
        if isinstance(ln, str):
            mode, ph = ln.split(':'); t1 = wt(ph, af, last=(mode == 'until_end'))
            t1 = (t1 + 0.3) if mode == 'until_end' else (t1 - 0.05)
        else: t1 = t0 + ln
        t1 = min(t1, end - 0.05)
        if kind == 'card':
            ov.append(dict(t=t0, dur=t1 - t0, kind='card', draw=what, title=C.get('papers_title', True))); sfx.append(('whoosh_soft_1', t0 - 0.1, -17)); flares.append((t0 - 0.4, 0.9))
        else:
            path = what if '/' in what else RP + what + '.jpg'
            cx = 0.5 if '/' in what else cx_for(path, JX.get(what, 0.5))
            ov.append(dict(t=t0, dur=t1 - t0, kind='photo', path=path, z0=1.0, z1=1.07, cx=cx, cy=0.4, tint=WARM_T)); sfx.append(('whoosh_soft_1', t0 - 0.1, -20))
            if o.get('loc'): overlays.append(('loc', dict(t0=t0 + 0.15, t1=t1, y=C.get('loc_y', 0.085))))
    if C.get('gap'):
        tg = [g for g in G if g['text'] == 'THE GAP']
        gp = dict(t0=(tg[0]['t'] + tg[0]['dur'] + 0.05) if tg else max(wt('the gap'), 3.0) - 0.3, hit_gap=wt('gap'), hit_demand=wt('housing demand'), hit_supply=wt('quality supply'))
        gp['hit_gap'] = max(gp['hit_gap'], gp['t0'] + 0.2); gp['t1'] = gp['hit_supply'] + 2.2
        overlays.append(('gap', gp)); sfx += [('pop_soft', gp['hit_demand'], -24), ('pop_soft', gp['hit_supply'], -24), ('pop_soft', gp['hit_gap'], -22)]
    if C.get('steps'):
        hits = [wt('land acquisition', 220), wt('construction coordination', 220), wt('marketing', 220), wt('delivery', 220)]
        st = dict(t0=hits[0] - 0.35, t1=wt('delivery', 220, last=True) + 0.3, hits=hits, y=C.get('steps_y', 0.11))
        overlays.append(('steps', st)); sfx += [('pop_soft', h, -23) for h in hits]
    endc = [p for p in P['pics'] if p.get('kind') == 'card']          # the original end card stays (owner 8 Nov)
    pics = pics + ov + endc
    H = P['H']
    def extra(fr, t):
        t = float(t)
        if t < H['dur']: way2.hook_draw(fr, t, H)
        for k, o in overlays:
            if o['t0'] <= t <= o['t1']:
                {'gap': mg.gap_overlay, 'steps': mg.steps_overlay, 'loc': mg.location_overlay}[k](fr, t, o)
        for f0, fd in flares:
            if f0 <= t <= f0 + fd: flare(fr, t - f0, fd)
    return dict(P, pics=pics, G=G, sfx=sfx, extra=extra, end=end)

if __name__ == '__main__':
    which = sys.argv[1:] or list(PLAN)
    for rk in which:
        if rk == 'plan':
            for k in PLAN:
                P = build(k); print(k, 'dur %.1f' % P['dur'], [(round(p['t'], 1), round(p['dur'], 1), p.get('kind')) for p in P['pics'] if p.get('kind') in ('card', 'photo')])
            break
        R = way2.REELS[rk]; P = build(rk)
        v = iv.render_video('way2g_' + rk, 1080, 1920, P['pics'], P['G'], P['caps'], P['dur'], cap_y=1490, cap_box=True, extra=P['extra'])
        a = iv.render_audio('way2g_' + rk, P['voice'], P['sfx'], R['music'], P['dur'], music_db_under=17.0, smooth=True, lift=P['lifts'], lift_db=8.0)
        print(iv.encode('way2g_' + rk, v, a, 'John_Way2_%s_%s_MOTION_9x16_1080' % (rk, R['name'])))
