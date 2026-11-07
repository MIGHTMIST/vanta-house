# WAY 3: ~75 s trust film (9:16 and 4:5). Problem -> Turn -> Proof -> Now, John's own words only, complete sentences.
# v2 (7 Nov): helper-reviewed lines, ums/pauses cut, face close, smooth music bed that rises only in the gaps, no host anywhere.
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
import iv
from iv import span, pieces

GAP = 0.35
LINES = [  # (key, start phrase, end phrase, search after)
    ('b1', 'i believe that', 'professional developers', 0),         # problem
    ('b2a', 'after 10 years', 'markets', 0),                         # turn
    ('b2b', 'i founded blackstone', 'to uganda', 179),
    ('b3a', 'we focus on', 'delivery', 200),                         # proof
    ('b3c', 'sustainable success', 'integrity', 0),
    ('b4a', 'our immediate priority', 'in navuru', 0),               # now
    ('b4b', 'you are welcome to visit', 'in naguru', 600),
]
BEAT_GAP = {'b2a': 0.7, 'b3a': 0.7, 'b4a': 0.7}      # breaths between beats: the music rises there
SITE = iv.S + '/site/mmexport17924979%s.jpg'

def build(OW, OH):
    vert = OH > OW * 1.5
    CL = (1.55, 1.72) if vert else (2.1, 2.3)          # close on his face (wide section)
    CM = (1.12, 1.24) if vert else (1.5, 1.65)         # closing shot (medium)
    top = 0.48 if vert else 0.56
    t = 0.3; voice = []; at = {}; vk = []
    for key, a, b, af in LINES:
        t += BEAT_GAP.get(key, 0.0); s0 = t
        for x, y in pieces(*span(a, b, af)):
            voice.append((x, y, t)); vk.append(key); t += y - x
        at[key] = (s0, t); t += GAP
    end = t + 0.2; dur = end + 4.2
    pics = []
    for k, ((x, y, t0), key) in enumerate(zip(voice, vk)):
        nxt = voice[k + 1][2] if k + 1 < len(voice) else end
        c = CM if x >= 470 else CL
        if key == 'b1':                                   # problem: one slow push-in across the whole line
            s, e = at['b1']; z0 = c[0] + 0.16 * (t0 - s) / (e - s); z1 = c[0] + 0.16 * (nxt - s) / (e - s)
        else:
            z0 = c[k % 2]; z1 = z0 + 0.04
        pics.append(dict(t=t0, dur=nxt - t0, src=x, who='john', z0=z0, z1=z1, top=top))
    pics[0]['dur'] += pics[0]['t']; pics[0]['src'] -= pics[0]['t']; pics[0]['t'] = 0
    def wt_i(i):
        for x, y, t0 in voice:
            if x - 0.03 <= iv.WORDS[i]['t'] < y: return t0 + iv.WORDS[i]['t'] - x
    def wt(phrase, after=0): return wt_i(iv.find(phrase, after))
    # real site photos as B-roll (cover the um-cuts too): founding line second half, and "construction ... delivery"
    s2, e2 = at['b2b']; m2 = s2 + (e2 - s2) * 0.55
    pics.append(dict(t=m2, dur=e2 - m2 + GAP, kind='photo', path=SITE % '86840', z0=1.0, z1=1.08, cx=0.5, cy=0.55))
    tc = wt('construction coordination', 220); e3 = at['b3a'][1]; h = (e3 - tc) / 2
    pics.append(dict(t=tc, dur=h, kind='photo', path=SITE % '82990', z0=1.0, z1=1.07, cx=0.45, cy=0.6))
    pics.append(dict(t=tc + h, dur=h + GAP, kind='photo', path=SITE % '89322', z0=1.07, z1=1.0, cx=0.4, cy=0.5))
    pics.append(dict(t=end, dur=dur - end, kind='card', draw=iv.end_card_draw, nocap=True))
    gy = int(OH * (0.105 if vert else 0.11))
    G = [dict(text='THE GAP', t=wt('gap') - 0.05, dur=3.0, x=OW / 2, y=gy, size=int(OW * 0.15), bar=True),
         dict(text='10 YEARS', t=wt('10') - 0.05, dur=3.4, x=OW / 2, y=gy, size=int(OW * 0.16), bar=True),
         dict(text='INTEGRITY', t=wt('integrity') - 0.03, dur=2.6, x=OW / 2, y=gy, size=int(OW * 0.14), bar=True, sfx_in='impact_boom_v2', g_in=-9),
         dict(text='NAGURU', t=wt('navuru') - 0.05, dur=2.4, x=OW / 2, y=gy, size=int(OW * 0.15), bar=True)]
    sfx = []
    for g in G:
        sfx += [(g.get('sfx_in', 'whoosh_soft_1'), g['t'] - 0.03, g.get('g_in', -15)), ('pop_soft', g['t'] + g['dur'] - 0.3, -24)]
    sfx += [('riser_2', at['b1'][1] - 2.3, -15), ('reverse_swell', end - 2.3, -17), ('whoosh_soft_1', m2 - 0.1, -17), ('whoosh_soft_1', tc - 0.1, -17)]
    lifts = [(at[a][1] + 0.05, at[b][0] - 0.05) for a, b in (('b1', 'b2a'), ('b2b', 'b3a'), ('b3c', 'b4a'))] + [(end, dur)]
    caps = iv.cap_chunks(voice, ['gap', 'quality', 'developers', '10', 'years', 'blackstone', 'uganda', 'entire', 'land', 'delivery', 'integrity', 'vanta', 'naguru', 'navuru', 'visit'])
    return dict(voice=voice, pics=pics, G=G, sfx=sfx, caps=caps, dur=dur, end=end, lifts=lifts, site=(m2, e2, tc, e3))

if __name__ == '__main__':
    sizes = [s for s in (('9x16', 1080, 1920, 1490), ('4x5', 1080, 1350, 1160)) if len(sys.argv) < 2 or sys.argv[1] in (s[0], 'plan')]
    for lab, OW, OH, cy in sizes:
        P = build(OW, OH)
        if 'plan' in sys.argv: print(lab, 'dur %.2f' % P['dur'], 'pieces', len(P['voice'])); continue
        v = iv.render_video('way3_' + lab, OW, OH, P['pics'], P['G'], P['caps'], P['dur'], cap_y=cy, cap_size=54 if OH > 1500 else 50)
        m2, e2, tc, e3 = P['site']
        amb = [('ambience_building_site', m2 - 0.2, -26), ('ambience_building_site', tc - 0.2, -26)]
        a = iv.render_audio('way3_' + lab, P['voice'], P['sfx'] + amb, 'music_cinematic_build_A.mp3', P['dur'],
                            music_db_under=17.0, smooth=True, lift=P['lifts'], lift_db=9.0)
        print(iv.encode('way3_' + lab, v, a, 'John_Way3_TrustFilm_%s_1080' % lab))
