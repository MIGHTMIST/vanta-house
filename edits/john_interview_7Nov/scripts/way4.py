# WAY 4 (Claude's own): "Rapid fire", 9:16. Eight Anton question cards, each answered by John's best sentence.
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
import iv
from iv import span, pieces, text_layer, place, ANTON, INTERB, GOLD, WHITE, eout

# questions written to fit exactly what he answers (owner, 7 Nov)
QA = [('WHAT IS BLACKSTONE?', [('blackstone reestate is', 'company', 0)], 1.0),
      ('WHAT BROUGHT A BANKER TO AFRICA?', [('after 10 years', 'markets', 0)], 1.3),
      ('WHY UGANDA?', [('i chose uganda', 'quality housing', 0)], 1.0),
      ("WHERE'S THE OPPORTUNITY?", [('the gap between', 'quality supply', 0)], 1.25),
      ('WHAT DO YOU ACTUALLY DO?', [('our core business', 'real estate partnerships', 0)], 1.0),
      ('HOW DO YOU WIN HERE?', [('we believe sustainable', 'integrity', 0)], 1.3),
      ('WHAT ARE YOU BUILDING NOW?', [('our immediate priority', 'in navuru', 0)], 1.0),
      ('WHO ARE YOU LOOKING FOR?', [('i would like to have', 'partners', 0)], 1.3)]
CARD = 1.1
CLOSE = {False: (1.55, 1.72), True: (1.12, 1.24)}   # wide section / medium section
OW, OH = 1080, 1920

def card_draw(fr, tl, p):
    if 'L' not in p:
        words = p['q'].split(); lines = [p['q']]
        if len(p['q']) > 14:
            best = min(range(1, len(words)), key=lambda i: abs(len(' '.join(words[:i])) - len(' '.join(words[i:]))))
            lines = [' '.join(words[:best]), ' '.join(words[best:])]
        Ls = [text_layer([(l, WHITE)], 140, ANTON, shadow=0.3, blur=10) for l in lines]
        from PIL import Image as _I
        hh = sum(l.height for l in Ls) - 70 * (len(Ls) - 1); ww = max(l.width for l in Ls)
        p['L'] = _I.new('RGBA', (ww, hh), (0, 0, 0, 0)); yy = 0
        for l in Ls: p['L'].alpha_composite(l, ((ww - l.width) // 2, yy)); yy += l.height - 70
        p['N'] = text_layer([(p['n'], GOLD)], 64, ANTON, shadow=0.0, blur=1)
        if p.get('sub'): p['S'] = text_layer([(p['sub'], GOLD)], 132, ANTON, shadow=0.3, blur=10)
    u = eout(tl / 0.22); uo = 1 - eout((tl - (p['dur'] - 0.18)) / 0.18)
    a = min(u, uo)
    place(fr, p['N'], OW / 2, OH * 0.46 - p['L'].height / 2 - 10, a=a)
    place(fr, p['L'], OW / 2, OH * 0.46 + (1 - u) * 30, a=a, sc=0.92 + 0.08 * u)
    if p.get('S'): place(fr, p['S'], OW / 2, OH * 0.46 + p['L'].height * 0.62, a=a)

_tl = {}
def timer_draw(fr, t, answers):
    """small stopwatch under the captions: gold ring fills and the seconds count up while he answers"""
    from PIL import ImageDraw
    for a, b in answers:
        if a <= t <= b + 0.25:
            el = min(t - a, b - a); u = min(1, (t - a) / 0.25, (b + 0.25 - t) / 0.25)
            cx, cy, r = OW / 2, 1655, 46
            d = ImageDraw.Draw(fr)
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(0, 0, 0, int(110 * u)), outline=(255, 255, 255, int(70 * u)), width=4)
            d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * el / max(b - a, 0.1), fill=GOLD + (int(255 * u),), width=6)
            k = '%.0f' % el
            if k not in _tl: _tl[k] = text_layer([(k, WHITE)], 44, ANTON, shadow=0.0, blur=1)
            place(fr, _tl[k], cx, cy + 2, a=u)

def build():
    t = 0.0; voice = []; pics = []; sfx = []; answers = []
    # hook card
    pics.append(dict(t=0, dur=1.6, kind='card', draw=card_draw, q='8 QUESTIONS FOR', sub='THE MAN BUILDING VANTA HOUSE', n='', nocap=True))
    pics[-1]['q'] = '8 QUESTIONS.'; pics[-1]['sub'] = 'ONE BUILDER.'
    sfx += [('whoosh_cinematic_5', 0.0, -14), ('pop_soft', 1.45, -24)]; lifts = [(0, 1.6)]
    t = 1.6
    for k, (q, spans, z) in enumerate(QA):
        pics.append(dict(t=t, dur=CARD, kind='card', draw=card_draw, q=q, n='%d / %d' % (k + 1, len(QA)), nocap=True))
        sfx += [('whoosh_soft_1', t - 0.05, -14), ('pop_soft', t + CARD - 0.2, -24)]; lifts.append((t - 0.1, t + CARD + 0.05))
        t += CARD
        a_start = t
        for a, b, af in spans:
            for x, y in pieces(*span(a, b, af)):
                z0 = CLOSE[x >= 470][len(pics) % 2]          # close on his face, alternating two sizes so the um-cuts don't jump
                pics.append(dict(t=t, dur=y - x, src=x, who='john', z0=z0, z1=z0 + 0.04, top=0.40))
                voice.append((x, y, t)); t += y - x
        answers.append((a_start, t)); pics[-1]['dur'] += 0.25; t += 0.25
    # close: "You are welcome to visit our project"
    x, y = span('you are welcome to visit', 'in naguru')
    pics.append(dict(t=t, dur=y - x + 0.35, src=x, who='john', z0=1.12, z1=1.18, top=0.40)); voice.append((x, y, t)); t += y - x + 0.35
    end = t; dur = end + 3.8
    pics.append(dict(t=end, dur=dur - end, kind='card', draw=iv.end_card_draw, nocap=True))
    sfx += [('reverse_swell', end - 2.2, -16)]; lifts.append((end, dur))
    caps = iv.cap_chunks(voice, ['blackstone', '10', 'years', 'uganda', 'east', 'africa', 'gap', 'residential', 'sustainable', 'trusted', 'quality', 'land', 'delivery', 'integrity', 'vanta', 'naguru', 'navuru', 'partners', 'visit'])
    return dict(voice=voice, pics=pics, sfx=sfx, caps=caps, dur=dur, end=end, answers=answers, lifts=lifts)

if __name__ == '__main__':
    P = build()
    if len(sys.argv) > 1: print('dur %.2f' % P['dur']); sys.exit()
    v = iv.render_video('way4', OW, OH, P['pics'], [], P['caps'], P['dur'], cap_y=1490, extra=lambda fr, t: timer_draw(fr, t, P['answers']))
    a = iv.render_audio('way4', P['voice'], P['sfx'], 'music_modern_upbeat_A.mp3', P['dur'], music_db_under=16.5, smooth=True, lift=P['lifts'], lift_db=10.0, room=True)
    print(iv.encode('way4', v, a, 'John_Way4_RapidFire_9x16_1080'))
