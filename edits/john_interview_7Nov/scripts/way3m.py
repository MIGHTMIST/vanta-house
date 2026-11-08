# WAY 3 "mood edition" (8 Nov): same John edit as Way 3, re-cut with the mood boards from folder 06:
# cool-blue past (China banking) -> warm golden Africa / Vanta, real John photos, real site photos, generic stock only for ideas
# (skyline, trading screen, sunrise, plans, key handover), gold light-leak transitions, gold dust on the end card,
# boxed captions with the gold keyword, name band on the founding line.
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
import iv, way3
from iv import text_layer, place, ANTON, INTERB, WHITE, GOLD, eout, ease

B = iv.S + '/broll/'
SITE = iv.S + '/site/mmexport17924979%s.jpg'
PE = iv.S + '/people/'
COOL = "eq=contrast=1.06:saturation=0.72:brightness=-0.03,colorbalance=rs=-0.07:gs=-0.01:bs=0.10:rm=-0.04:bm=0.07:rh=-0.03:bh=0.05"
WARM = "eq=contrast=1.05:saturation=1.12,colorbalance=rs=0.07:gs=0.025:bs=-0.07:rm=0.05:gm=0.01:bm=-0.05:rh=0.04:bh=-0.04"
WARM_T = (1.07, 1.0, 0.88)          # warm golden tint for photos
COOL_T = (0.90, 0.97, 1.10)

def build(OW, OH):
    P = way3.build(OW, OH)
    voice = P['voice']; end = P['end']; dur = P['dur']
    def wt(phrase, after=0):
        i = iv.find(phrase, after)
        for x, y, t0 in voice:
            if x - 0.03 <= iv.WORDS[i]['t'] < y: return t0 + iv.WORDS[i]['t'] - x
        raise ValueError(phrase)
    pics = [p for p in P['pics'] if p.get('kind', 'src') == 'src']          # John's close shots stay underneath
    card = [p for p in P['pics'] if p.get('kind') == 'card']
    ov = []                                                                  # B-roll on top (later wins)
    def clip(t0, t1, path, grade, **k): ov.append(dict(t=t0, dur=t1 - t0, kind='clip', path=B + path, src=k.pop('start', 0.0), grade=grade, **k))
    def photo(t0, t1, path, **k): ov.append(dict(t=t0, dur=t1 - t0, kind='photo', path=path, **k))
    # TURN: "After 10 years in China's investment banking industry" -> cool blue China, then warm Africa
    t_ch = wt("china's"); t_bank = wt('banking'); t_saw = wt('saw significant'); t_af = wt("africa's")
    clip(t_ch - 0.15, t_bank - 0.1, 'b1_shanghai_day_skyline_1.mp4', COOL, z0=1.0, z1=1.08)
    clip(t_bank - 0.1, t_saw - 0.05, 'b1_trading_screen_4.mp4', COOL, z0=1.05, z1=1.15)
    a0, a1 = [(t0, t0 + y - x) for x, y, t0 in voice if x - 0.03 <= iv.WORDS[iv.find('after 10 years')]['t'] < y][0][0], None
    e2a = max(t0 + y - x for x, y, t0 in voice if x < iv.WORDS[iv.find('markets')]['t'] + 0.5 and t0 < t_af + 6)
    clip(t_af - 0.2, e2a + 0.3, 'b2_sunrise_sun_1.mp4', WARM, z0=1.0, z1=1.06)
    # "I founded Blackstone Real Estate ..." -> his real office photo with a name band, then the Nile (warm)
    t_f = wt('i founded blackstone', 179); t_ug = wt('uganda', 190)
    photo(t_f - 0.1, t_f + 3.4, iv.S + '/broll/John_Yan_office_real_B.jpg', z0=1.0, z1=1.08, cx=0.5, cy=0.35, tint=WARM_T)
    clip(t_ug - 1.6, t_ug + 1.0, 'b2_nile_aerial_4.mp4', WARM, z0=1.0, z1=1.05)
    # PROOF: plans on the desk for "land acquisition", the REAL site for construction ... delivery
    t_land = wt('land acquisition', 220); t_con = wt('construction coordination', 220); t_mk = wt('marketing', 220)
    e3 = max(t0 + y - x for x, y, t0 in voice if x < iv.WORDS[iv.find('delivery', 236)]['t'] + 0.5 and t0 < t_mk + 5)
    photo(t_land - 0.2, t_con - 0.05, PE + 'floorplan_towers.jpg', z0=1.0, z1=1.1, cx=0.5, cy=0.45)          # the real Vanta floor plan
    photo(t_con - 0.05, t_mk, PE + 'slab_pour_sky.jpg', z0=1.0, z1=1.07, cx=0.3, cy=0.5, tint=WARM_T)
    photo(t_mk, e3 + 0.3, PE + 'brick_laying.jpg', z0=1.07, z1=1.0, cx=0.45, cy=0.5, tint=WARM_T)
    # "... operating with integrity" -> key handover in slow motion
    t_int = wt('integrity'); t_lm = wt('local market')
    photo(t_lm - 0.1, t_int - 1.3, PE + 'team_fourpoints_table.jpg', z0=1.0, z1=1.06, cx=0.42, cy=0.45, tint=WARM_T)   # John with local partners
    photo(t_int - 1.3, t_int + 1.6, PE + 'handshake_truck.jpg', z0=1.04, z1=1.12, cx=0.4, cy=0.45, tint=WARM_T)      # real handshake on site
    # NOW: "deliver Vanta House ... in Naguru" -> the real site, golden
    t_v = wt('van house', 435); t_n = wt('navuru')
    t_mid = (t_v - 0.15 + t_n + 1.2) / 2
    photo(t_v - 0.15, t_mid, PE + 'render_vanta_house.jpg', z0=1.0, z1=1.08, cx=0.5, cy=0.45)              # labelled Artist's impression
    photo(t_mid, t_n + 1.2, PE + 'site_group5.jpg', z0=1.0, z1=1.06, cx=0.5, cy=0.5, tint=WARM_T)         # John and team on the real site
    imp = dict(t=t_v - 0.15, dur=t_mid - t_v + 0.15)
    pics = pics + ov + card
    # gold light leaks on the beat changes (cool -> warm, into proof, into now, into the end card)
    fxs = [dict(t=t_af - 0.45, dur=1.2, path=B + 'b7_lightleak_gold_1.mp4', alpha=0.85),
           dict(t=t_f - 0.5, dur=1.1, path=B + 'b7_lightleak_gold_1.mp4', start=2.0, alpha=0.6),
           dict(t=t_v - 0.45, dur=1.2, path=B + 'b7_lightleak_gold_1.mp4', start=3.5, alpha=0.75),
           dict(t=end - 0.4, dur=dur - end + 0.4, path=B + 'b7_dust_particles_4.mp4', alpha=0.55)]
    # name band on the founding line (Anton name + Inter Bold title, gold bar), eases in and out
    band = dict(t=t_f + 0.2, dur=3.1)
    def extra(fr, t):
        if imp['t'] <= t <= imp['t'] + imp['dur']:
            if 'L' not in imp: imp['L'] = text_layer([("Artist's impression", WHITE)], 30, INTERB, shadow=0.8, blur=8)
            a = min(1.0, (t - imp['t']) / 0.3, (imp['t'] + imp['dur'] - t) / 0.3)
            place(fr, imp['L'], OW - 50 - imp['L'].width / 2, int(OH * 0.06), a=max(a, 0))
        if band['t'] <= t <= band['t'] + band['dur']:
            if 'A' not in band:
                band['A'] = text_layer([('JOHN YAN', WHITE)], 78, ANTON, shadow=0.7, blur=12)
                band['B'] = text_layer([('Founder & CEO, Blackstone Real Estate', GOLD)], 36, INTERB, shadow=0.7, blur=8)
            tl = t - band['t']; u = eout(tl / 0.35); uo = 1 - ease((tl - (band['dur'] - 0.35)) / 0.35); a = min(u, uo)
            from PIL import ImageDraw
            d = ImageDraw.Draw(fr); y0 = int(OH * 0.62); bw = int(8 + 0 * a)
            d.rectangle((60, y0 - 10, 60 + 8, y0 + 120), fill=GOLD + (int(255 * a),))
            place(fr, band['A'], 84 + band['A'].width / 2 - 40 * (1 - u), y0 + 18, a=a)
            place(fr, band['B'], 84 + band['B'].width / 2 - 40 * (1 - u), y0 + 92, a=a)
    sfx = list(P['sfx']) + [('whoosh_soft_1', t_ch - 0.2, -18), ('whoosh_soft_1', t_af - 0.3, -16), ('pop_soft', band['t'], -20),
                           ('whoosh_soft_1', band['t'] + band['dur'] - 0.35, -20), ('whoosh_soft_1', t_land - 0.25, -18)]
    amb = [('ambience_building_site', t_con - 0.2, -26), ('pop_soft', t_lm - 0.1, -22)]
    return dict(P, pics=pics, fxs=fxs, extra=extra, sfx=sfx + amb)

if __name__ == '__main__':
    sizes = [s for s in (('9x16', 1080, 1920, 1490), ('4x5', 1080, 1350, 1160)) if len(sys.argv) < 2 or sys.argv[1] in (s[0], 'plan')]
    for lab, OW, OH, cy in sizes:
        P = build(OW, OH)
        if 'plan' in sys.argv: print(lab, 'dur %.2f' % P['dur'], len(P['pics']), 'pics'); continue
        v = iv.render_video('way3m_' + lab, OW, OH, P['pics'], P['G'], P['caps'], P['dur'], cap_y=cy, cap_size=52 if OH > 1500 else 48,
                            fxs=P['fxs'], cap_box=True, extra=P['extra'])
        a = iv.render_audio('way3m_' + lab, P['voice'], P['sfx'], 'music_cinematic_build_A.mp3', P['dur'],
                            music_db_under=17.0, smooth=True, lift=P['lifts'], lift_db=9.0)
        print(iv.encode('way3m_' + lab, v, a, 'John_Way3_TrustFilm_MOOD_%s_1080' % lab))
