# Before / after style sheet from real frames: video A (current kit) vs video C (proposed style v2)
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
import styleC as ST
from styleC import R, T, place, ONYX, STONE, CHAMP, CHAMP_D, MIST, hexs
from PIL import Image, ImageDraw
from render import GOLD, GOLD_D, INK, CREAM
R.FN.update({'anton': ST.S + '/kit/fonts/Anton.woff', 'ci': ST.S + '/kit/fonts/Caslon-Italic.woff'})
C = ST.S + '/C/'
PW = 900
def shot(path, box):          # crop from a 1080x1920 frame and fit to panel width
    im = Image.open(path).convert('RGB').crop(box)
    return im.resize((PW, int(im.height * PW / im.width)), Image.LANCZOS)
def panel(title, frames, fonts_txt, cols, bg, fg, sub):
    tops = [shot(*f) for f in frames]
    Ht = 110 + sum(t.height + 24 for t in tops) + 150 + 230
    im = Image.new('RGBA', (PW, Ht), bg + (255,))
    place(im, T(title, 'sans', 28, sub, track=8, shadow=0), PW / 2, 56)
    y = 110
    for t in tops: im.paste(t, (0, y)); y += t.height + 24
    place(im, T(fonts_txt, 'sans', 28, fg, shadow=0), PW / 2, y + 50)
    d = ImageDraw.Draw(im); n = len(cols); w = 150; gap = 22; x0 = (PW - (n * w + (n - 1) * gap)) / 2; y += 110
    for k, (name, c) in enumerate(cols):
        x = x0 + k * (w + gap)
        d.rounded_rectangle((x, y, x + w, y + 100), 14, fill=c + (255,), outline=sub + (255,), width=1)
        place(im, T(name, 'sans', 21, fg, track=2, shadow=0), x + w / 2, y + 128)
        place(im, T(hexs(c), 'sans_r', 20, sub, track=1, shadow=0), x + w / 2, y + 158)
    return im
a = panel('NOW  ·  VIDEO A (CURRENT KIT)', [(C + 'boardA_1.png', (0, 150, 1080, 750)), (C + 'boardA_2.png', (0, 380, 1080, 1260))],
          'Anton + Libre Caslon', [('Gold', GOLD), ('Bronze', GOLD_D), ('Ink', INK), ('Cream', CREAM)], CREAM, INK, (120, 108, 92))
b = panel('NEW  ·  VIDEO C (PROPOSED STYLE)', [(C + 'boardC_1.png', (0, 150, 1080, 750)), (C + 'boardC_3.png', (0, 380, 1080, 1260))],
          'Cormorant Garamond + Jost', [('Vanta Black', ONYX), ('Stone', STONE), ('Champagne', CHAMP), ('Bronze', CHAMP_D), ('Warm grey', MIST)], ONYX, STONE, MIST)
Ht = max(a.height, b.height)
out = Image.new('RGB', (PW * 2 + 20, Ht), (255, 255, 255))
out.paste(a.convert('RGB'), (0, 0)); out.paste(b.convert('RGB'), (PW + 20, 0))
out.save(ST.S + '/out/Vanta_style_before_after.png'); print('board', out.size)
