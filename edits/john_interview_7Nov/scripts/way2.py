# WAY 2: seven vertical reels (9:16), one answer each. Hook text on top, strongest sentence first, punch-ins on key sentences,
# host reaction cutaway about every 9 s (wide section only), 1-2 Anton graphics on key words, Inter Bold captions with gold keywords.
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
import iv
from iv import span, pieces, text_layer, place, ANTON, WHITE, GOLD, eout, ease

OW, OH = 1080, 1920
TOP = 0.48
CL = (1.55, 1.72)      # close on his face (wide section)
CM = (1.12, 1.24)      # medium section
REELS = {   # helper-reviewed 7 Nov: hooks true to his words, stumbles cut, R6 dropped (weak)
 'R1': dict(name='TenYearsInBanking', hook=('TEN YEARS IN BANKING.', 'THEN UGANDA.'), music='music_modern_upbeat_A.mp3',
            lines=[('after 10 years', 'markets', 0, 1.3), ('i founded blackstone', 'to uganda', 179, 1.0), ('our vision is', 'partnerships', 194, 1.15)],
            graphics=[('discipline', 'DISCIPLINE', 0), ('uganda', 'UGANDA', 190)], kw=['10', 'years', 'banking', 'africa', 'blackstone', 'discipline', 'uganda', 'lasting', 'value']),
 'R2': dict(name='TheHousingGap', hook=('THE HOUSING GAP', 'IS THE OPPORTUNITY'), music='music_modern_upbeat_A.mp3',
            lines=[('i believe that', 'developers', 0, 1.3), ('after studying several', 'quality housing', 0, 1.0)],
            graphics=[('gap', 'THE GAP', 352), ('east', 'EAST AFRICA', 0)], kw=['gap', 'quality', 'supply', 'uganda', 'east', 'africa', 'housing']),
 'R3': dict(name='WhyWeLoveUganda', hook=('WHY WE LOVE', 'UGANDA'), music='music_modern_upbeat_A.mp3',
            lines=[('we really love', 'country', 0, 1.3), ('uganda offers considerable', 'affordable housing', 0, 1.0),
                   ('like any emerging', 'risk management', 0, 1.15), ('we believe sustainable', 'integrity', 0, 1.3)],
            graphics=[('urbanization', 'URBANIZATION', 0), ('integrity', 'INTEGRITY', 0)], kw=['love', 'urbanization', 'housing', 'partnerships', 'integrity']),
 'R4': dict(name='LandToDelivery', hook=('FROM LAND TO DELIVERY,', 'THE ENTIRE PROCESS'), music='music_modern_upbeat_A.mp3',
            lines=[('we focus on', 'delivery', 0, 1.3), ('our core business', 'partnerships', 0, 1.0)],
            graphics=[('land', 'LAND', 228), ('delivery', 'DELIVERY', 0)], kw=['entire', 'land', 'construction', 'delivery', 'residential', 'partnerships']),
 'R5': dict(name='AfterVantaHouse', hook=('WHAT COMES AFTER', 'VANTA HOUSE'), music='music_modern_upbeat_A.mp3',
            lines=[('our immediate priority', 'in navuru', 0, 1.0), ('based on this', 'expand into', 0, 1.15, 0.06), ('selected locations', 'locations', 0, 1.15, 0.06),
                   ('and develop more', 'projects', 0, 1.15), ('our goal is', 'uganda', 455, 1.3)],
            graphics=[('navuru', 'NAGURU', 0), ('lasting', 'LASTING VALUE', 455)], kw=['vanta', 'naguru', 'navuru', 'trusted', 'lasting', 'value', 'uganda']),
 'R7': dict(name='OwnLandLetsPartner', hook=('OWN LAND IN UGANDA?', "LET'S PARTNER."), music='music_modern_upbeat_A.mp3',
            lines=[('we welcome cooperation', 'core investment', 0, 1.3), ('i would like to work', 'with them', 0, 1.15), ('i also would', 'property agents', 0, 1.3)],
            graphics=[('landowners', 'LANDOWNERS', 380), ('agents', 'AGENTS', 540)], kw=['landowners', 'joint', 'ventures', 'co-investment', 'landlords', 'agents', 'partnerships']),
}

def hook_draw(fr, t, H):
    if 'L' not in H:
        H['L'] = [text_layer([(H['l'][0], WHITE)], 84, ANTON, shadow=0.7, blur=14), text_layer([(H['l'][1], GOLD)], 84, ANTON, shadow=0.7, blur=14)]
    D = 0.3; u = eout(t / D); uo = 1 - ease((t - (H['dur'] - D)) / D); a = min(u, uo)
    if a <= 0: return
    place(fr, H['L'][0], OW / 2, 92 + (1 - u) * 20, a=a); place(fr, H['L'][1], OW / 2, 184 + (1 - u) * 20, a=a)

def build(R):
    t = 0.15; voice = []; pics = []; key_z = []; gaps = []
    for ln in R['lines']:
        a, b, af, z = ln[:4]; g = ln[4] if len(ln) > 4 else 0.45
        for x, y in pieces(*span(a, b, af)):
            voice.append((x, y, t)); key_z.append(z); t += y - x
        t += g
        if g > 0.3: gaps.append((t - g + 0.03, t - 0.03))
    end = t; dur = end + 3.0
    for k, ((x, y, t0), z) in enumerate(zip(voice, key_z)):
        nxt = voice[k + 1][2] if k + 1 < len(voice) else end
        z = (CM if x >= 470 else CL)[k % 2]           # close on his face; two sizes alternate so um-cuts never jump
        pics.append(dict(t=t0, dur=nxt - t0, src=x, who='john', z0=z, z1=z + 0.04, top=TOP))
    pics[0]['dur'] += pics[0]['t']; pics[0]['src'] -= pics[0]['t']; pics[0]['t'] = 0
    # host reaction cutaways (picture only, same moment in the interview) every ~9 s, never in the first 4 s, only where the host is in frame
    sfx = []; nxt_c = 6.5
    for x, y, t0 in voice:
        if nxt_c < t0: nxt_c = t0 + 0.6
        while t0 <= nxt_c < t0 + (y - x) - 1.4:
            src_t = x + (nxt_c - t0)
            if False:   # host must not appear (owner, 7 Nov)
                pics.append(dict(t=nxt_c, dur=1.15, src=src_t, who='host', z0=1.05, z1=1.1, top=0.40))
            nxt_c += 9.0
    pics.append(dict(t=end, dur=dur - end, kind='card', draw=iv.end_card_draw, nocap=True))
    def wt(word, after):
        i = iv.find(word, after)
        for x, y, t0 in voice:
            if x - 0.03 <= iv.WORDS[i]['t'] < y: return t0 + iv.WORDS[i]['t'] - x
        return None
    G = []
    for word, text, af in R['graphics']:
        tw = wt(word, af)
        if tw is None: print('graphic word not in reel:', word); continue
        tw = max(tw, 3.0)
        G.append(dict(text=text, t=tw - 0.05, dur=2.4, x=OW / 2, y=140, size=150 if len(text) < 10 else 118, bar=True))
    for g in G: sfx += [('whoosh_soft_1', g['t'] - 0.03, -15), ('pop_soft', g['t'] + g['dur'] - 0.3, -24)]
    H = dict(l=R['hook'], dur=2.9)
    sfx += [('whoosh_cinematic_5', 0.0, -15), ('pop_soft', 2.6, -24), ('reverse_swell', end - 2.2, -17)]
    caps = iv.cap_chunks(voice, R['kw'])
    return dict(voice=voice, pics=pics, G=G, sfx=sfx, caps=caps, dur=dur, H=H, lifts=gaps[:-1] + [(end, dur)])

if __name__ == '__main__':
    which = sys.argv[1:] or list(REELS)
    for rk in which:
        if rk == 'plan':
            for k, R in REELS.items(): P = build(R); print(k, R['name'], 'dur %.1f' % P['dur'], 'cutaways', sum(1 for p in P['pics'] if p.get('who') == 'host'), [round(g['t'], 1) for g in P['G']])
            break
        R = REELS[rk]; P = build(R)
        v = iv.render_video('way2_' + rk, OW, OH, P['pics'], P['G'], P['caps'], P['dur'], cap_y=1490, extra=lambda fr, t, H=P['H']: hook_draw(fr, t, H) if t < H['dur'] else None)
        a = iv.render_audio('way2_' + rk, P['voice'], P['sfx'], R['music'], P['dur'], music_db_under=17.0, smooth=True, lift=P['lifts'], lift_db=8.0)
        print(iv.encode('way2_' + rk, v, a, 'John_Way2_%s_%s_9x16_1080' % (rk, R['name'])))
