# WAY 1 kit edition (8 Nov): Way 1 full interview (16:9), everything kept (cut, chapters, lower third, original end card),
# plus the way1g cutaways (real photos, papers, blueprint, location tag), with the cold-open graphics rebuilt on the
# MOTION + SOUND KIT: T4 counter "10 YEARS" and the T5 dot-map route China -> Kampala, kit light leaks on card cuts.
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
import numpy as np
from PIL import Image, ImageFilter
import iv, mg, mgk, way1g

OW, OH = 1920, 1080
T = dict(acc=(201, 162, 75), font=iv.ANTON)

def wrap916(fn):
    """draw a 9:16 kit card on 1080x1920, keep its middle square (y 360..1440, where the kit keeps its content),
    centre it in 16:9 and fill the sides with the card's own edge colour"""
    def draw(fr, tl, p):
        c = Image.new('RGBA', (1080, 1920), mgk.DARK + (255,)); fn(c, tl, p)
        sq = c.crop((0, 360, 1080, 1440))
        a = np.asarray(sq).astype(np.float32); edge = np.concatenate([a[:, :20], a[:, -20:]], 1).mean(1)
        edge = np.asarray(Image.fromarray(edge[:, None, :].astype(np.uint8)).filter(ImageFilter.GaussianBlur(20)))
        back = np.repeat(edge, OW, 1); back[..., 3] = 255; fr.paste(Image.fromarray(back.astype(np.uint8)))
        m = np.ones(1080, np.float32); f = 120; m[:f] = np.linspace(0, 1, f); m[-f:] = np.linspace(1, 0, f)
        fr.paste(sq, ((OW - 1080) // 2, 0), Image.fromarray((np.tile(m, (1080, 1)) * 255).astype(np.uint8)))
    return draw

def counter_card(fr, tl, p):
    fr.paste(Image.new('RGBA', fr.size, mgk.DARK + (255,)))
    if ('vig', 1080, 1920) in mgk._c: fr.alpha_composite(mgk._c[('vig', 1080, 1920)])
    mgk.counter(fr, p['t0'] + tl, dict(t0=p['t0'], t1=p['t0'] + p['dur'], sub='INVESTMENT BANKING · CHINA'), T)

def build():
    P = way1g.build()
    pics = P['pics']; sfx = list(P['sfx'])
    cards = [p for p in pics if p.get('kind') == 'card']
    # the first two cards are the cold-open years + journey cards (way1g order): swap their drawing for the kit versions
    cold = sorted([c for c in cards if c['t'] < 12], key=lambda c: c['t'])
    leaks = []
    if len(cold) >= 2:
        y, j = cold[0], cold[1]
        y['draw'] = wrap916(counter_card); y['t0'] = 0.0
        j['draw'] = wrap916(mgk.map_card); j['T'] = T
        j['dur'] = max(j['dur'], 3.7)
        sfx = [s for s in sfx if not (y['t'] - 0.5 <= s[1] <= j['t'] + 0.3 and s[0] == 'whoosh_soft_1')]
        sfx += mgk.counter_sfx(y['t']) + mgk.map_sfx(j['t']) + [('sfx_whoosh_soft_1', y['t'] - 0.4, -18)]
        leaks += [j['t']]
    for c in cards:
        if c['t'] > 12 and c['t'] < P['end'] - 0.1: leaks.append(c['t'])
    base = P['extra']
    def extra(fr, t):
        t = float(t); base(fr, t)
        for lc in leaks: mgk.light_leak(fr, t, lc, 0.6)
    return dict(P, sfx=sfx, extra=extra)

if __name__ == '__main__':
    P = build()
    if len(sys.argv) > 1 and sys.argv[1].startswith('test'):
        print(iv.render_video('way1k_t', OW, OH, P['pics'], [], [], float(sys.argv[1][4:] or 12), extra=P['extra'])); sys.exit()
    v = iv.render_video('way1k', OW, OH, P['pics'], [], [], P['dur'], extra=P['extra'])
    a = iv.render_audio('way1k', P['voice'], P['sfx'], 'music_calm_piano_A.mp3', P['dur'], music_db_under=21.0, smooth=True,
                        lift=[(c - w, c + w) for c, w, g in P['swells']] + [(P['end'], P['dur'])], lift_db=6.0)
    print(iv.encode('way1k', v, a, 'John_Way1_FullInterview_KIT_16x9_1080', crf=18))
