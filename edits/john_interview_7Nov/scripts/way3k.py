# WAY 3 "keep + add" edition (8 Nov): the MOOD edition Abdullahi liked, kept whole (stock clips, real photos, light leaks,
# dust, word graphics, end card), with my motion graphics ADDED in the gaps. Only one swap: the AI-looking office photo
# on "I founded Blackstone" becomes his chosen black-and-white portrait with the name under it (owner, 8 Nov).
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
import iv, way3m, mg

def build(OW, OH):
    P = way3m.build(OW, OH)
    P['voice'] = [(float(x), float(y), float(t0)) for x, y, t0 in P['voice']]
    voice = P['voice']
    def wt(phrase, after=0):
        i = iv.find(phrase, after)
        for x, y, t0 in voice:
            if x - 0.03 <= iv.WORDS[i]['t'] < y: return t0 + iv.WORDS[i]['t'] - x
        raise ValueError(phrase)
    G = P['G']; gt = {g['text']: g for g in G}
    pics = [p for p in P['pics'] if not str(p.get('path', '')).endswith('John_Yan_office_real_B.jpg')]
    sfx = list(P['sfx']); add = []; overlays = []
    # 1. gap bars once the THE GAP title has gone
    g0 = gt['THE GAP']; hd, hs = wt('housing demand'), wt('quality supply')
    gap = dict(t0=g0['t'] + g0['dur'] + 0.05, hit_gap=g0['t'] + g0['dur'] + 0.3, hit_demand=hd, hit_supply=hs)
    gap['hit_demand'] = max(hd, gap['t0'] + 0.2); gap['t1'] = hs + 2.2
    overlays.append(('gap', gap)); sfx += [('pop_soft', gap['hit_demand'], -24), ('pop_soft', hs, -24)]
    # 2. Shanghai -> Kampala line between the trading screen and the sunrise
    t_saw = wt('saw significant'); t_af = wt("africa's")
    if t_af - t_saw > 1.2:
        add.append(dict(t=t_saw - 0.05, dur=t_af - 0.2 - (t_saw - 0.05), kind='card', draw=mg.journey_card)); sfx.append(('whoosh_soft_1', t_saw - 0.15, -18))
    # 3. founder: his black-and-white portrait + name (same window the office photo had)
    t_f = wt('i founded blackstone', 179)
    add.append(dict(t=t_f - 0.1, dur=3.5, kind='card', draw=mg.founder_card, photo='john_headshot_black_shirt.jpg'))
    # 4. step tracker over the floor plan / slab / bricks already in the mood edition
    t_land = wt('land acquisition', 220); t_con = wt('construction coordination', 220); t_mk = wt('marketing', 220); t_del = wt('delivery', 236)
    overlays.append(('steps', dict(t0=t_land - 0.2, t1=t_del + 0.9, hits=[t_land, t_con, t_mk, t_del], y=0.2)))
    sfx += [('pop_soft', h, -23) for h in (t_land, t_con, t_mk, t_del)]
    # 5. papers after the handshake (the INTEGRITY title stays the original word graphic)
    t_int = wt('integrity'); t_v = wt('van house', 435)
    p0 = t_int + 1.6; p1 = min(p0 + 3.0, t_v - 0.9)
    if p1 - p0 > 1.8:
        add.append(dict(t=p0, dur=p1 - p0, kind='card', draw=mg.papers_card, title=False))
        sfx += [('whoosh_soft_1', p0 - 0.1, -18), ('impact_boom_v2', p0 + 1.25, -22)]
    # 6. the approved drawing draws in and becomes the render (replaces only the plain render still, same window)
    rend = [p for p in pics if str(p.get('path', '')).endswith('render_vanta_house.jpg')]
    if rend:
        r = rend[0]; pics.remove(r)
        add.append(dict(t=r['t'], dur=r['dur'], kind='card', draw=mg.blueprint_card)); sfx.append(('riser_2', r['t'], -26))
    # 7. location tag on the team-on-site photo, below the NAGURU word graphic
    grp = [p for p in pics if str(p.get('path', '')).endswith('site_group5.jpg')]
    if grp: overlays.append(('loc', dict(t0=grp[0]['t'] + 0.1, t1=grp[0]['t'] + grp[0]['dur'], y=0.22 if OH > 1500 else 0.25)))
    end_card = [p for p in pics if p.get('kind') == 'card' and p['t'] >= P['end'] - 0.01]
    pics = [p for p in pics if p not in end_card] + add + end_card
    def extra(fr, t):
        t = float(t)
        for k, o in overlays:
            if o['t0'] <= t <= o['t1']: {'gap': mg.gap_overlay, 'steps': mg.steps_overlay, 'loc': mg.location_overlay}[k](fr, t, o)
    return dict(P, pics=pics, sfx=sfx, extra=extra)

if __name__ == '__main__':
    sizes = [s for s in (('9x16', 1080, 1920, 1490), ('4x5', 1080, 1350, 1160)) if len(sys.argv) < 2 or sys.argv[1] in (s[0], 'plan')]
    for lab, OW, OH, cy in sizes:
        P = build(OW, OH)
        if 'plan' in sys.argv: print(lab, 'dur %.2f' % P['dur'], [(round(p['t'], 1), round(p['dur'], 1), p.get('kind'), str(p.get('path', ''))[-22:]) for p in P['pics'] if p.get('kind') != 'src']); continue
        v = iv.render_video('way3k_' + lab, OW, OH, P['pics'], P['G'], P['caps'], P['dur'], cap_y=cy, cap_size=52 if OH > 1500 else 48,
                            fxs=P['fxs'], cap_box=True, extra=P['extra'])
        a = iv.render_audio('way3k_' + lab, P['voice'], P['sfx'], 'music_cinematic_build_A.mp3', P['dur'],
                            music_db_under=17.0, smooth=True, lift=P['lifts'], lift_db=9.0)
        print(iv.encode('way3k_' + lab, v, a, 'John_Way3_TrustFilm_MOOD_PLUS_%s_1080' % lab))
