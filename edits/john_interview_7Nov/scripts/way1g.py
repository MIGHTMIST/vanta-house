# WAY 1 redo (8 Nov): the full interview (16:9) with my own motion graphics (mg.py) and face-checked REAL photos as cutaways.
# Same cut, chapters, lower third and sound as Way 1. Cards are drawn in a centred column and blended into a full-width
# background made from their own edges, so the vertical-first graphics sit cleanly in 16:9.
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
import numpy as np
from PIL import Image, ImageFilter
import iv, mg, way1
from way3g import end_card, flare
from way2g import JX

OW, OH = 1920, 1080
RP = iv.S + '/people/real/'; PE = iv.S + '/people/'; UP = '/root/.claude/uploads/253db02e-90a6-5547-b8b3-69bd9a44cdc8/'
WARM_T = (1.07, 1.0, 0.88)

def wide(fn):
    """run a vertical-first card in a centred column, fill the sides from its own blurred edges"""
    def draw(fr, tl, p):
        W = int(OH * 0.75)
        sub = Image.new('RGBA', (W, OH), (0, 0, 0, 255)); fn(sub, tl, p)
        a = np.asarray(sub).astype(np.float32)
        edge = np.concatenate([a[:, :24], a[:, -24:]], 1).mean(1)          # per-row colour of the card's own edges
        edge = np.asarray(Image.fromarray(edge[:, None, :].astype(np.uint8)).filter(ImageFilter.GaussianBlur(20)))
        back = np.repeat(edge, OW, 1); back[..., 3] = 255
        fr.paste(Image.fromarray(back.astype(np.uint8)))
        m = np.ones(W, np.float32); f = int(W * 0.12); m[:f] = np.linspace(0, 1, f); m[-f:] = np.linspace(1, 0, f)
        mask = Image.fromarray((np.tile(m, (OH, 1)) * 255).astype(np.uint8))
        fr.paste(sub, ((OW - W) // 2, 0), mask)
    return draw

def cx16(path, xc):
    w, h = Image.open(path).size; f = max(OW / w, OH / h) * 1.12; Wd = w * f
    if Wd <= OW + 1: return 0.5
    return min(max(xc * Wd - OW / 2, 0), Wd - OW) / (Wd - OW)

def build():
    P = way1.build()
    P['voice'] = [(float(x), float(y), float(t0)) for x, y, t0 in P['voice']]
    voice = P['voice']; end = float(P['end']); dur = float(P['dur'])
    def wt(ph, after=0):
        a0 = after
        while True:
            i = iv.find(ph, a0)
            for x, y, t0 in voice:
                if x - 0.03 <= iv.WORDS[i]['t'] < y: return t0 + iv.WORDS[i]['t'] - x
            a0 = iv.WORDS[i]['t'] + 0.01
    ov = []; sfx = list(P['sfx']); flares = []; overlays = []
    def card(t0, t1, fn, **k):
        ov.append(dict(t=t0, dur=t1 - t0, kind='card', draw=wide(fn), **k)); sfx.append(('whoosh_soft_1', t0 - 0.1, -18)); flares.append((t0 - 0.4, 0.9))
    def photo(t0, t1, key, real=True, **k):
        path = RP + key + '.jpg' if real and '/' not in key else key
        cx = cx16(path, JX.get(key, 0.5)) if real and '/' not in key else 0.5
        ov.append(dict(t=t0, dur=t1 - t0, kind='photo', path=path, z0=1.0, z1=1.06, cx=cx, cy=k.pop('cy', 0.35), tint=k.pop('tint', WARM_T), **k))
        sfx.append(('whoosh_soft_1', t0 - 0.1, -21))
    # cold open: 10 years (cool) -> Shanghai to Kampala (warm) -> back on John for "...real estate market"
    t10 = wt('10 years'); tsaw = wt('saw significant')
    card(t10 + 0.6, tsaw - 0.05, mg.years_card); card(tsaw - 0.05, tsaw + 4.3, mg.journey_card)
    # WHY HE STARTED
    tf = wt('i founded blackstone', 179); card(tf - 0.1, tf + 4.2, mg.founder_card)
    tu = wt('uganda', 190); photo(tu - 1.5, tu + 1.0, 'dfa63778')
    tp = wt('partnerships', 194); photo(tp - 0.2, tp + 1.9, '6baeb5bd')
    # WHAT WE DO: floor plan -> slab -> bricks under the LAND/BUILD/MARKET/DELIVER tracker
    tl_ = wt('land acquisition', 220); tc = wt('construction coordination', 220); tm = wt('marketing', 220); td = wt('delivery', 236)
    photo(tl_ - 0.3, tc - 0.05, PE + 'floorplan_towers.jpg', real=False, tint=None, cy=0.4)
    photo(tc - 0.05, tm, PE + 'slab_pour_sky.jpg', real=False, cy=0.5)
    photo(tm, td + 1.0, PE + 'brick_laying.jpg', real=False, cy=0.5)
    overlays.append(('steps', dict(t0=tl_ - 0.3, t1=td + 1.0, hits=[tl_, tc, tm, td]))); sfx += [('pop_soft', h, -23) for h in (tl_, tc, tm, td)]
    sfx.append(('ambience_building_site', tc - 0.2, -26))
    # BUSINESS CLIMATE: warm real moments, then the papers on "integrity"
    tlv = wt('we really love'); photo(tlv - 0.3, tlv + 2.2, 'c7cda191', cy=0.3)
    tslp = wt('strong local partnerships'); photo(tslp - 0.2, tslp + 2.3, '75bc38b2')
    tlm = wt('local market'); tin = wt('integrity')
    photo(tlm - 0.3, tin - 1.5, '8661a8bb', cy=0.4)
    card(tin - 1.5, tin + 1.45, mg.papers_card)
    sfx.append(('impact_boom_v2', tin - 1.5 + 1.25, -22))
    # WHY UGANDA: blueprint -> render on "growing demand for quality housing"
    tgd = wt('growing demand'); card(tgd - 0.2, tgd + 2.9, mg.blueprint_card); sfx.append(('riser_2', tgd - 0.2, -26))
    # OPEN TO PARTNERS: real handshake on "joint ventures"
    tjv = wt('joint ventures'); photo(tjv - 0.3, tjv + 2.2, '19867d84')
    # WHAT'S NEXT: render (artist's impression) on "Vanta House", team on site + location tag on "Naguru"
    tv = wt('van house', 435); tn = wt('navuru')
    photo(tv - 0.2, tn - 0.3, PE + 'render_vanta_house.jpg', real=False, tint=None, cy=0.3)
    overlays.append(('imp', dict(t0=tv - 0.2, t1=tn - 0.3)))
    photo(tn - 0.3, tn + 2.6, 'cd590606', cy=0.45); overlays.append(('loc', dict(t0=tn - 0.15, t1=tn + 2.6))); sfx.append(('pop_soft', tn - 0.15, -22))
    # LOCAL PARTNERS WANTED: one real site photo (workers only, nobody labelled)
    tpa = wt('property agents'); photo(tpa - 6.0, tpa - 3.6, UP + 'e0ebef93-image.jpg', real=False, cy=0.5)
    pics = [p for p in P['pics'] if p.get('kind') != 'card'] + ov + [p for p in P['pics'] if p.get('kind') == 'card']   # original end card kept
    base_extra = way1.extra_fn(P)
    def extra(fr, t):
        t = float(t); base_extra(fr, t)
        for k, o in overlays:
            if o['t0'] <= t <= o['t1']:
                if k == 'imp': mg.label(fr, t, o, "Artist's impression")
                else: {'steps': mg.steps_overlay, 'loc': mg.location_overlay}[k](fr, t, o)
        for f0, fd in flares:
            if f0 <= t <= f0 + fd: flare(fr, t - f0, fd)
    return dict(P, pics=pics, sfx=sfx, extra=extra)

if __name__ == '__main__':
    P = build()
    if len(sys.argv) > 1:
        print('dur %.1f' % P['dur'], [(round(p['t'], 1), round(p['dur'], 1), p.get('kind')) for p in P['pics'] if p.get('kind') in ('card', 'photo')]); sys.exit()
    v = iv.render_video('way1g', OW, OH, P['pics'], [], [], P['dur'], extra=P['extra'])
    a = iv.render_audio('way1g', P['voice'], P['sfx'], 'music_calm_piano_A.mp3', P['dur'], music_db_under=21.0, smooth=True,
                        lift=[(c - w, c + w) for c, w, g in P['swells']] + [(P['end'], P['dur'])], lift_db=6.0)
    print(iv.encode('way1g', v, a, 'John_Way1_FullInterview_MOTION_16x9_1080', crf=18))
