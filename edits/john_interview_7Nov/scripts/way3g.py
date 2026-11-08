# WAY 3 "motion graphics edition" (8 Nov): same John edit as Way 3 / Way 3 MOOD, but every stock clip is replaced by
# my own coded motion graphics (mg.py) or a face-checked real photo. Moods kept: cool past -> warm Africa / Vanta.
# Face check 8 Nov: office photos A/B and the glasses headshots are NOT used (AI-looking, not his face).
import sys, math
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import iv, way3, mg
from iv import text_layer, place, ANTON, INTERB, WHITE, GOLD, eout, ease, clamp

U = '/root/.claude/uploads/253db02e-90a6-5547-b8b3-69bd9a44cdc8/'
PE = iv.S + '/people/'
WARM_T = (1.07, 1.0, 0.88)

def end_card(fr, tl, p):
    """logo emblem + VANTA HOUSE letter by letter + Naguru, Kampala, own gold particles"""
    OW, OH = fr.size; mg.bg(fr, (12, 11, 12), (30, 24, 16), tl)
    em, name, tag = mg._logo_parts()
    s = OW * 0.26 / em.width; E = em.resize((int(em.width * s), int(em.height * s)), Image.LANCZOS)
    place(fr, E, OW / 2, OH * 0.30 + (1 - eout(tl / 0.6)) * 30, a=eout(tl / 0.6), sc=1 + 0.01 * tl)
    word = 'VANTA HOUSE'; size = int(OW * 0.15)
    if 'letters' not in p:
        F = iv.font(ANTON, size); p['letters'] = [(c, iv.text_layer([(c, WHITE)], size, ANTON, shadow=0.45, blur=12) if c != ' ' else None, F.getlength(c)) for c in word]
        p['W'] = sum(w for _, _, w in p['letters'])
        p['L2'] = text_layer([('Naguru, Kampala', GOLD)], int(OW * 0.055), INTERB, shadow=0.4, blur=8)
        p['L3'] = text_layer([(iv.CREDIT, (150, 150, 150))], int(OW * 0.018), INTERB, shadow=0.0, blur=1)
    x = OW / 2 - p['W'] / 2; y = OH * 0.47
    for i, (c, L, w) in enumerate(p['letters']):
        u = eout((tl - 0.35 - 0.06 * i) / 0.4)
        if L is not None: place(fr, L, x + w / 2, y + (1 - u) * 40, a=u, sc=0.9 + 0.1 * u)
        x += w
    u2 = eout((tl - 1.2) / 0.5)
    place(fr, p['L2'], OW / 2, y + size * 0.62 + (1 - u2) * 18, a=u2)
    place(fr, p['L3'], OW / 2, OH * 0.95, a=min(u2, 0.9))
    # gold dust drifting up (own particles)
    if 'pts' not in p:
        rng = np.random.default_rng(3); p['pts'] = rng.random((70, 4))
    L = Image.new('RGBA', fr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for px, py, sp, sz in p['pts']:
        yy = (py - tl * (0.02 + 0.04 * sp)) % 1.0; xx = px + 0.01 * math.sin(tl * (0.5 + sp) + px * 9)
        r = 1.5 + 3.5 * sz; a = int(200 * (0.3 + 0.7 * sz) * min(1, tl / 0.8))
        d.ellipse((xx * OW - r, yy * OH - r, xx * OW + r, yy * OH + r), fill=(235, 200, 130, a))
    fr.alpha_composite(L.filter(ImageFilter.GaussianBlur(1.2)))
    mg.grain(fr, 5, int(tl * 30) + 7)

def flare(fr, tl, dur):
    """own gold light sweep for beat changes (replaces the stock light-leak clip)"""
    OW, OH = fr.size; u = tl / dur; a = math.sin(math.pi * clamp(u)) * 0.75
    if a <= 0.01: return
    k = ('flare', OW, OH)
    if k not in mg._c:
        yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32); mg._c[k] = (xx, yy)
    xx, yy = mg._c[k]; cx = OW * (-0.2 + 1.4 * u); cy = OH * 0.35
    g = np.exp(-(((xx - cx) / (OW * 0.45)) ** 2 + ((yy - cy) / (OH * 0.55)) ** 2)) * a
    base = np.asarray(fr).astype(np.float32); col = np.array([255, 196, 110], np.float32)
    o = g[..., None] * col
    base[..., :3] = 255 - (255 - base[..., :3]) * (255 - o) / 255
    fr.paste(Image.fromarray(base.astype(np.uint8)))

def build(OW, OH):
    P = way3.build(OW, OH)
    P['voice'] = [(float(x), float(y), float(t0)) for x, y, t0 in P['voice']]
    voice = P['voice']; end = P['end']; dur = P['dur']
    def wt(phrase, after=0):
        i = iv.find(phrase, after)
        for x, y, t0 in voice:
            if x - 0.03 <= iv.WORDS[i]['t'] < y: return t0 + iv.WORDS[i]['t'] - x
        raise ValueError(phrase)
    pics = [p for p in P['pics'] if p.get('kind', 'src') == 'src']
    ov = []
    def card(t0, t1, fn, **k): ov.append(dict(t=t0, dur=t1 - t0, kind='card', draw=fn, **k))
    def photo(t0, t1, path, **k): ov.append(dict(t=t0, dur=t1 - t0, kind='photo', path=path, **k))
    # graphics from Way 3 that my motion graphics replace (keep INTEGRITY)
    drop = [g for g in P['G'] if g.get('text') in ('THE GAP', '10 YEARS', 'NAGURU', 'INTEGRITY')]
    G = [g for g in P['G'] if g not in drop]
    sfx = [s for s in P['sfx'] if not any(g['t'] - 0.4 <= s[1] <= g['t'] + g['dur'] + 0.4 for g in drop)]
    # HOOK: THE GAP bars above his head
    gap = dict(t0=wt('the gap') - 0.3, hit_gap=wt('gap'), hit_demand=wt('housing demand'), hit_supply=wt('quality supply'))
    gap['t1'] = gap['hit_supply'] + 2.2
    sfx += [('whoosh_soft_1', gap['t0'] - 0.1, -20), ('pop_soft', gap['hit_gap'], -22), ('pop_soft', gap['hit_demand'], -24), ('pop_soft', gap['hit_supply'], -24),
            ('whoosh_soft_1', gap['t1'] - 0.35, -22)]
    # TURN: 10 years card (cool), journey Shanghai -> Kampala (cool -> warm)
    t_10 = wt('10 years'); t_saw = wt('saw significant'); t_af = wt("africa's")
    e2a = max(t0 + y - x for x, y, t0 in voice if x < iv.WORDS[iv.find('markets')]['t'] + 0.5 and t0 < t_af + 6)
    card(t_10 - 0.35, t_saw - 0.05, mg.years_card, nocap=False)
    card(t_saw - 0.05, e2a + 0.3, mg.journey_card)
    sfx += [('whoosh_soft_1', t_10 - 0.45, -16), ('clock_tick', t_10 - 0.2, -26), ('whoosh_soft_1', t_saw - 0.15, -18), ('pop_soft', t_saw - 0.05 + 1.85, -20)]
    # "I founded Blackstone Real Estate" -> logo reveal, name under it
    t_f = wt('i founded blackstone', 179); t_ug = wt('uganda', 190)
    card(t_f - 0.1, t_f + 4.6, mg.founder_card)            # logo, then the headshot Abdullahi chose (8 Nov)
    sfx += [('whoosh_soft_1', t_f - 0.25, -16), ('reverse_swell', t_f - 0.1, -24)]
    # "... to Uganda" -> real photo, John on site (face-checked)
    photo(t_ug - 1.6, t_ug + 1.0, U + '999fae80-image.jpg', z0=1.0, z1=1.07, cx=0.35, cy=0.4, tint=WARM_T)
    # PROOF: floor plan -> slab -> bricks with my LAND/BUILD/MARKET/DELIVER tracker on top
    t_land = wt('land acquisition', 220); t_con = wt('construction coordination', 220); t_mk = wt('marketing', 220); t_del = wt('delivery', 236)
    e3 = max(t0 + y - x for x, y, t0 in voice if x < iv.WORDS[iv.find('delivery', 236)]['t'] + 0.5 and t0 < t_mk + 5)
    photo(t_land - 0.2, t_con - 0.05, PE + 'floorplan_towers.jpg', z0=1.0, z1=1.1, cx=0.5, cy=0.45)
    photo(t_con - 0.05, t_mk, PE + 'slab_pour_sky.jpg', z0=1.0, z1=1.07, cx=0.3, cy=0.5, tint=WARM_T)
    photo(t_mk, e3 + 0.3, PE + 'brick_laying.jpg', z0=1.07, z1=1.0, cx=0.45, cy=0.5, tint=WARM_T)
    steps = dict(t0=t_land - 0.2, t1=e3 + 0.3, hits=[t_land, t_con, t_mk, t_del])
    sfx += [('whoosh_soft_1', t_land - 0.3, -18)] + [('pop_soft', h, -23) for h in steps['hits']]
    # local market -> John with local partners; integrity -> real handshake (both face-checked)
    t_int = wt('integrity'); t_lm = wt('local market')
    photo(t_lm - 0.1, t_int - 1.6, PE + 'team_fourpoints_table.jpg', z0=1.0, z1=1.06, cx=0.42, cy=0.45, tint=WARM_T)
    photo(t_int - 1.6, t_int - 0.15, PE + 'handshake_truck.jpg', z0=1.04, z1=1.12, cx=0.4, cy=0.45, tint=WARM_T)
    card(t_int - 0.15, t_int + 3.0, mg.papers_card)                # real papers, safe header crops only
    sfx += [('whoosh_soft_1', t_int - 0.25, -18), ('whoosh_soft_1', t_int + 0.15, -24), ('whoosh_soft_1', t_int + 0.43, -24), ('impact_boom_v2', t_int - 0.15 + 1.25, -22)]
    # NOW: render (Artist's impression) -> John and team on the real site with my location tag
    t_v = wt('van house', 435); t_n = wt('navuru')
    t_mid = (t_v - 0.15 + t_n + 1.2) / 2
    card(t_v - 0.15, t_mid, mg.blueprint_card)            # real drawing draws in, then the render
    photo(t_mid, t_n + 1.2, PE + 'site_group5.jpg', z0=1.0, z1=1.06, cx=0.5, cy=0.5, tint=WARM_T)
    imp = dict(t0=-9, t1=-9); loc = dict(t0=t_mid + 0.1, t1=t_n + 1.2)
    sfx += [('whoosh_soft_1', t_v - 0.3, -18), ('riser_2', t_v - 0.15, -26), ('pop_soft', loc['t0'], -22)]
    # end card: own logo + letters
    endc = dict(t=end, dur=dur - end, kind='card', draw=end_card, nocap=True)
    pics = pics + ov + [endc]
    flares = [(t_af - 0.5, 1.1), (t_f - 0.45, 1.0), (t_v - 0.45, 1.1), (end - 0.5, 1.1)]
    sfx += [('ambience_building_site', t_con - 0.2, -26)]
    def extra(fr, t):
        t = float(t)
        if gap['t0'] <= t <= gap['t1']: mg.gap_overlay(fr, t, gap)
        if steps['t0'] <= t <= steps['t1']: mg.steps_overlay(fr, t, steps)
        if imp['t0'] <= t <= imp['t1']: mg.label(fr, t, imp, "Artist's impression")
        if loc['t0'] <= t <= loc['t1']: mg.location_overlay(fr, t, loc)
        for f0, fd in flares:
            if f0 <= t <= f0 + fd: flare(fr, t - f0, fd)
    return dict(P, pics=pics, G=G, extra=extra, sfx=sfx)

def logo_with_name(fr, tl, p):
    mg.logo_card(fr, tl, p)
    OW, OH = fr.size
    if 'nA' not in p:
        p['nA'] = text_layer([('JOHN YAN', WHITE)], int(OW * 0.065), ANTON, shadow=0.6, blur=10)
        p['nB'] = text_layer([('Founder & CEO', GOLD)], int(OW * 0.034), INTERB, shadow=0.6, blur=8)
    u = eout((tl - 1.3) / 0.45)
    place(fr, p['nA'], OW / 2, OH * 0.655 + (1 - u) * 20, a=u)
    place(fr, p['nB'], OW / 2, OH * 0.655 + p['nA'].height * 0.48 + (1 - u) * 20, a=u)

if __name__ == '__main__':
    sizes = [s for s in (('9x16', 1080, 1920, 1490), ('4x5', 1080, 1350, 1160)) if len(sys.argv) < 2 or sys.argv[1] in (s[0], 'plan')]
    for lab, OW, OH, cy in sizes:
        P = build(OW, OH)
        if 'plan' in sys.argv: print(lab, 'dur %.2f' % P['dur'], len(P['pics']), 'pics'); continue
        v = iv.render_video('way3g_' + lab, OW, OH, P['pics'], P['G'], P['caps'], P['dur'], cap_y=cy, cap_size=52 if OH > 1500 else 48,
                            fxs=[], cap_box=True, extra=P['extra'])
        a = iv.render_audio('way3g_' + lab, P['voice'], P['sfx'], 'music_cinematic_build_A.mp3', P['dur'],
                            music_db_under=17.0, smooth=True, lift=P['lifts'], lift_db=9.0)
        print(iv.encode('way3g_' + lab, v, a, 'John_Way3_TrustFilm_MOTION_%s_1080' % lab))
