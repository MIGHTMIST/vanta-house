# TRAILER v3 (8 Nov): v2 + the REAL site footage from the crew's Drive folder (moving clips) in place of stills.
# TRAILER v2 for the full interview (8 Nov), 9:16. Owner: "grab attention, good on the eyes, the voice keeps cutting".
# Director-helper notes applied: photo burst + "10 YEARS IN BANKING" slam in the first second, every line plays WHOLE
# (no micro-pause cuts), one steady push-in framing per line, white flash + impact on each line change (no black cards),
# max two real cutaways per line held long, word slams, ends on John's own invitation, then one title slam card.
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
from PIL import Image, ImageDraw
import iv, mg
from iv import span, pieces, text_layer, place, ANTON, INTERB, WHITE, GOLD, eout, ease
from way2g import JX, cx_for
from way3m import WARM_T, WARM
SV = iv.S + '/sitevids/GV3A%s.MP4'

OW, OH = 1080, 1920
UP = '/root/.claude/uploads/253db02e-90a6-5547-b8b3-69bd9a44cdc8/'; B = iv.S + '/broll/'; PE = iv.S + '/people/'; RP = PE + 'real/'
TOP = 0.48
LINES = [('hook', 'i saw significant', 'markets', 0),
         ('gap', 'i believe that', 'meaningful opportunities', 334),
         ('love', 'we really love', 'this country', 0),
         ('next', 'our immediate priority', 'in navuru', 0),
         ('partners', 'i would like to have more', 'local partners', 529),
         ('goal', 'our goal is simple', 'lasting value', 0),
         ('visit', 'you are welcome to visit', 'in naguru', 600)]
ADJ = {'partners': (-0.15, 0.0), 'visit': (-0.18, 0.0), 'goal': (0.0, -0.08)}   # QA: onsets/ends not clipped
GAP = 0.16; OPEN = 0.95; POST = 0.08      # POST: a little extra air after each line so no word ending is clipped

def slam_draw(fr, tl, p):
    mg.bg(fr, (10, 10, 11), (28, 23, 16), tl)
    if 'A' not in p:
        p['A'] = text_layer([('VANTA HOUSE', WHITE)], 170, ANTON, shadow=0.5, blur=14)
        p['B'] = text_layer([('NAGURU, KAMPALA', GOLD)], 46, INTERB, shadow=0.4, blur=6, track=6)
        p['C'] = text_layer([('THE FULL INTERVIEW', WHITE)], 82, ANTON, shadow=0.5, blur=10)
        p['D'] = text_layer([('JOHN YAN  ·  Founder & CEO, Blackstone Real Estate', (205, 205, 205))], 32, INTERB, shadow=0.4, blur=6)
        p['E'] = text_layer([(iv.CREDIT, (120, 120, 120))], 20, INTERB, shadow=0, blur=1)
    u = eout(tl / 0.25); push = 1 + 0.02 * tl; y = OH * 0.40
    place(fr, p['A'], OW / 2, y, a=u, sc=(1.25 - 0.25 * u) * push)          # slams in big, settles
    u2 = eout((tl - 0.3) / 0.4); place(fr, p['B'], OW / 2, y + 115, a=u2)
    u3 = eout((tl - 0.7) / 0.4); bw = 260 * u3
    if bw > 2: ImageDraw.Draw(fr).rectangle((OW / 2 - bw / 2, y + 175, OW / 2 + bw / 2, y + 181), fill=GOLD + (int(255 * u3),))
    place(fr, p['C'], OW / 2, y + 250 + (1 - u3) * 18, a=u3)
    u4 = eout((tl - 1.0) / 0.4); place(fr, p['D'], OW / 2, y + 330, a=u4 * 0.95)
    place(fr, p['E'], OW / 2, OH * 0.95, a=u4 * 0.8)
    mg.grain(fr, 5, int(tl * 30) + 3)

def build():
    t = OPEN; voice = []; at = {}
    for key, a, b, af in LINES:
        x, y = span(a, b, af, post=0.14 + POST); dx, dy = ADJ.get(key, (0, 0)); x += dx; y += dy
        s0 = t
        for px, py in pieces(x, y, maxgap=0.5, keep=0.18):      # only long pauses (>0.5 s) shortened, joins stay soft
            voice.append((px, py, t)); t += py - px
        at[key] = (s0, t); t += GAP
    end = t + 0.15; dur = end + 3.4
    pics = []
    for k, (x, y, t0) in enumerate(voice):          # one steady framing per line, slow push-in
        nxt = voice[k + 1][2] if k + 1 < len(voice) else end
        z0 = 1.12 if x >= 470 else 1.58
        ln = next(kk for kk, (s_, e_) in at.items() if s_ - 0.01 <= t0 <= e_); s_, e_ = at[ln]
        za = z0 + 0.07 * (t0 - s_) / (e_ - s_); zb = z0 + 0.07 * min(1, (nxt - s_) / (e_ - s_))
        pics.append(dict(t=t0, dur=nxt - t0, src=x, who='john', z0=za, z1=zb, top=TOP))
    def wt(ph, key):
        s, e = at[key]; a0 = 0
        while True:
            i = iv.find(ph, a0)
            for x, y, t0 in voice:
                if x - 0.03 <= iv.WORDS[i]['t'] < y and s - 0.01 <= t0 <= e: return t0 + iv.WORDS[i]['t'] - x
            a0 = iv.WORDS[i]['t'] + 0.01
    ov = []; G = []; overlays = []; fxs = []; sfx = []
    def site(t0, t1, clip, start, **k):        # real site footage, warm grade, gentle push
        if t1 - t0 < 0.3: return
        ov.append(dict(t=t0, dur=t1 - t0, kind='clip', path=SV % clip, src=start, grade=WARM, z0=k.get('z0', 1.0), z1=k.get('z1', 1.07), cx=k.get('cx', 0.5), cy=k.get('cy', 0.5)))
        sfx.append(('whoosh_soft_1', t0 - 0.1, -21))
    def photo(t0, t1, path, **k):
        key = path; path = RP + path + '.jpg' if '/' not in path else path
        cx = k.pop('cx', cx_for(path, JX.get(key, 0.5)) if '/' not in key else 0.5)
        ov.append(dict(t=t0, dur=t1 - t0, kind='photo', path=path, z0=k.pop('z0', 1.0), z1=k.pop('z1', 1.08), cx=cx, cy=k.pop('cy', 0.42), tint=k.pop('tint', WARM_T)))
        sfx.append(('whoosh_soft_1', t0 - 0.1, -20))
    gy = int(OH * 0.105)
    def word(text, t, d, size=None, y=None):
        G.append(dict(text=text, t=t - 0.05, dur=d, x=OW / 2, y=y or gy, size=size or int(OW * 0.15), bar=True))
        sfx.extend([('impact_boom_v2', t - 0.05, -21), ('pop_soft', t + d - 0.35, -25)])
    # 0 - 0.95 s: burst of real photos under a "10 YEARS IN BANKING" slam
    burst = [('0018', 2.0, 0.5), ('9992', 4.0, 0.5), ('0036', 6.0, 0.35), ('9990', 1.5, 0.5), ('0028', 2.0, 0.5)]
    for k, (c, st, cx) in enumerate(burst):
        ov.append(dict(t=0.19 * k, dur=0.19 if k < 4 else OPEN - 0.76, kind='clip', path=SV % c, src=st, grade=WARM, z0=1.14, z1=1.04, cx=cx, cy=0.5))
        sfx.append(('whoosh_fast_2', 0.19 * k - 0.03, -23))
    G.append(dict(text='10 YEARS IN BANKING', t=0.0, dur=OPEN + 1.5, x=OW / 2, y=gy, size=112, bar=True))
    sfx += [('impact_boom_v2', 0.0, -13), ('pop_soft', OPEN + 1.15, -25)]
    # 1 hook: his face, then Kampala on "Africa's real estate markets"
    site(wt("africa's", 'hook') - 0.1, at['hook'][1] + GAP, '0025', 3.0, cx=0.45)
    # 2 the gap
    word('THE GAP', wt('gap', 'gap'), 2.0)
    tqs = wt('quality supply', 'gap') - 0.2; tmid = (tqs + at['gap'][1] + GAP) / 2
    thd = wt('housing demand', 'gap'); site(max(thd - 0.1, wt('gap', 'gap') + 2.0), tqs, '0035', 0.0)
    site(tqs, tmid, '0018', 0.7, cx=0.55); site(tmid, at['gap'][1] + GAP, '9991', 0.0)
    # 3 love: the garden lunch with partners
    site(at['love'][0] - 0.02, at['love'][1] + GAP, '0031', 5.0)
    # 4 next: drawing -> render (labelled in the card), then the team on site + NAGURU + location tag
    tv, tn = wt('van house', 'next'), wt('navuru', 'next')
    ov.append(dict(t=tv - 0.15, dur=tn - 0.45 - tv, kind='card', draw=mg.blueprint_card)); sfx.append(('riser_2', tv - 0.2, -25))
    nx1 = at['next'][1] + GAP
    site(tn - 0.6, nx1, '9990', 0.3)
    word('NAGURU', tn, min(1.4, nx1 - tn - 0.1)); overlays.append(('loc', dict(t0=tn + 0.05, t1=nx1, y=0.22, l2='Naguru, Kampala  ·  On site 2026')))
    # 5 partners
    tlp = wt('local partners', 'partners'); p1 = at['partners'][1] + GAP
    site(tlp - 0.5, p1, '9992', 3.0, cx=0.45); word('PARTNERS', tlp, min(1.5, p1 - tlp - 0.1), y=gy - 55)
    # 6 goal: real moment on "trusted developments", the team on "deliver lasting value"
    ttr, tdl = wt('trusted', 'goal'), wt('deliver lasting', 'goal')
    site(ttr - 0.15, tdl - 0.1, '0016', 0.0); site(tdl - 0.1, at['goal'][1] + GAP, '0044', 0.0, cx=0.45)
    tsi = wt('simple', 'goal'); site(tsi + 0.5, ttr - 0.15, '9993', 0.0, cx=0.45)
    # 7 his invitation, then the render (Artist's impression) on "Vanta House in Naguru"
    tvv = wt('van house', 'visit')
    site(wt('visit', 'visit') - 0.1, tvv - 0.15, '9985', 2.5)
    photo(tvv - 0.15, end, PE + 'render_vanta_house.jpg', tint=None, cx=0.3, cy=0.45, z0=1.0, z1=1.1)
    overlays.append(('imp', dict(t0=tvv - 0.15, t1=end)))
    slam = dict(t=end, dur=dur - end, kind='card', draw=slam_draw, nocap=True)
    sfx += [('riser_2', end - 2.0, -17), ('impact_boom_v2', end, -12), ('reverse_swell', end + 0.8, -22)]
    fxs.append(dict(t=end + 0.6, dur=dur - end - 0.6, path=B + 'b7_dust_particles_4.mp4', alpha=0.5))
    # white flash + soft boom + gold leak on every line change
    flashes = [0.0, OPEN] + [at[k][0] for k, *_ in LINES[1:]] + [end]
    for f0 in flashes[2:-1]: sfx += [('whoosh_soft_1', f0 - 0.12, -17), ('impact_boom_v2', f0, -24)]
    for f0 in flashes[1:]: fxs.append(dict(t=f0 - 0.3, dur=0.9, path=B + 'b7_lightleak_gold_1.mp4', start=(f0 * 7) % 4.5, alpha=0.45))
    pics = pics + ov + [slam]
    caps = iv.cap_chunks(voice, ['significant', 'africa', 'gap', 'quality', 'love', 'vanta', 'navuru', 'naguru', 'partners', 'trusted', 'lasting', 'visit'])
    PN = {'uganda': 'Uganda', 'african': 'African', 'africa': 'Africa', "africa's": "Africa's"}
    for c in caps:
        c[2] = [((PN[w.rstrip('.,?!').lower()] + w[len(w.rstrip('.,?!')):]) if w.rstrip('.,?!').lower() in PN else w, kw) for w, kw in c[2]]
        if c[0] < end < c[1]: c[1] = end - 0.03
    def extra(fr, t):
        t = float(t)
        for f0 in flashes:
            if f0 <= t < f0 + 0.1:
                fr.alpha_composite(Image.new('RGBA', fr.size, (255, 250, 240, int((230 if f0 in (0.0, end) else 90) * (1 - (t - f0) / 0.1)))))
        for k, o in overlays:
            if o['t0'] <= t <= o['t1']:
                if k == 'imp': mg.label(fr, t, o, "Artist's impression")
                else: mg.location_overlay(fr, t, o)
    return dict(pics=pics, G=G, caps=caps, voice=voice, sfx=sfx, fxs=fxs, extra=extra, dur=dur, end=end, lifts=[(end, dur)], at=at)

if __name__ == '__main__':
    P = build()
    if 'plan' in sys.argv:
        print('dur %.2f end %.2f' % (P['dur'], P['end']), {k: (round(a, 2), round(b, 2)) for k, (a, b) in P['at'].items()})
        for p in sorted(P['pics'], key=lambda p: p['t']):
            if p.get('kind', 'src') != 'src': print('%6.2f %5.2f %-5s %s' % (p['t'], p['dur'], p['kind'], str(p.get('path', getattr(p.get('draw'), '__name__', '')))[-30:]))
        for g in P['G']: print('G %6.2f %4.2f %s' % (g['t'], g['dur'], g['text']))
        sys.exit()
    v = iv.render_video('trailer3', OW, OH, P['pics'], P['G'], P['caps'], P['dur'], cap_y=1490, cap_size=52, fxs=P['fxs'], cap_box=True, extra=P['extra'])
    a = iv.render_audio('trailer3', P['voice'], P['sfx'], 'music_cinematic_build_A.mp3', P['dur'], music_db_under=12.5, smooth=True, lift=P['lifts'], lift_db=7.0)
    print(iv.encode('trailer3', v, a, 'John_FullInterview_TRAILER_v3_SITE_9x16_1080'))
