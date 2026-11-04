# Four style options for the Vanta short, as stills (hook frame + end card), same words and same shot.
import sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad/scripts')
sys.argv = [sys.argv[0], 'masks']                     # import renderC without running it
import renderC as RC
import styleC as ST
from styleC import R, T, place, comp, W, H, hexs

S = ST.S
MO = S + '/fonts2/montserrat/package/files/montserrat-latin-'
PF = S + '/fonts2/playfair-display/package/files/playfair-display-latin-'
KF = S + '/kit/fonts/'
R.FN.update({'cas': KF + 'Caslon.woff', 'cas_b': KF + 'Caslon-Bold.woff', 'cas_i': KF + 'Caslon-Italic.woff',
             'mo4': MO + '400-normal.woff', 'mo5': MO + '500-normal.woff', 'mo6': MO + '600-normal.woff', 'mo7': MO + '700-normal.woff',
             'pf6': PF + '600-normal.woff', 'pf7': PF + '700-normal.woff', 'pf_i': PF + '400-italic.woff'})

STYLES = [
 dict(name='1  VANTA BLACK', fonts='Cormorant Garamond + Jost', bg=('grad', (15, 14, 12), (27, 24, 20)),
      who=('Who is behind', 'serif_i6', 84, (201, 172, 125), 0), hero=('serif_b', (239, 233, 223), 2),
      eyebrow=('sans', 33, (201, 172, 125), 12), vh=('serif', (239, 233, 223), 10), sub=('serif_i', 60, (201, 172, 125)),
      pill=('outline', 'sans', 31, (201, 172, 125), None), send=('serif_i', 58, (239, 233, 223), 'sans_sb', 46, (201, 172, 125)),
      num=('sans', 84, (239, 233, 223), 6), sig=('sans', 27, (150, 141, 128)), rule=(201, 172, 125),
      swatch=[('Vanta Black', (15, 14, 12)), ('Stone', (239, 233, 223)), ('Champagne', (201, 172, 125))]),
 dict(name='2  IVORY CLASSIC', fonts='Libre Caslon (yours) + Jost', bg=('flat', (245, 239, 227), (236, 228, 214)),
      who=('Who is behind', 'cas_i', 80, (255, 255, 255), 0), hero=('cas_b', (245, 239, 227), 2),
      eyebrow=('sans', 33, (150, 122, 84), 12), vh=('cas_b', (26, 23, 19), 6), sub=('cas_i', 56, (150, 122, 84)),
      pill=('outline', 'sans', 31, (150, 122, 84), None), send=('cas_i', 54, (26, 23, 19), 'sans_sb', 44, (150, 122, 84)),
      num=('sans', 84, (26, 23, 19), 6), sig=('sans', 27, (130, 118, 102)), rule=(150, 122, 84),
      swatch=[('Ivory', (245, 239, 227)), ('Ink', (26, 23, 19)), ('Bronze', (150, 122, 84))]),
 dict(name='3  MODERN CLEAN', fonts='Montserrat', bg=('flat', (243, 241, 237), (234, 231, 226)),
      who=('WHO IS BEHIND', 'mo5', 40, (255, 255, 255), 10), hero=('mo7', (255, 255, 255), 1),
      eyebrow=('mo6', 30, (176, 146, 104), 10), vh=('mo7', (30, 30, 30), 4), sub=('mo5', 44, (110, 106, 100)),
      pill=('solid', 'mo6', 30, (255, 255, 255), (30, 30, 30)), send=('mo4', 44, (30, 30, 30), 'mo7', 44, (176, 146, 104)),
      num=('mo6', 80, (30, 30, 30), 3), sig=('mo5', 25, (140, 136, 130)), rule=(176, 146, 104),
      swatch=[('Off-white', (243, 241, 237)), ('Charcoal', (30, 30, 30)), ('Sand', (176, 146, 104))]),
 dict(name='4  EMERALD & BRASS', fonts='Playfair Display + Montserrat', bg=('grad', (17, 28, 24), (30, 45, 38)),
      who=('Who is behind', 'pf_i', 78, (196, 164, 104), 0), hero=('pf7', (240, 234, 222), 1),
      eyebrow=('mo5', 30, (196, 164, 104), 11), vh=('pf6', (240, 234, 222), 4), sub=('pf_i', 54, (196, 164, 104)),
      pill=('outline', 'mo5', 29, (196, 164, 104), None), send=('pf_i', 52, (240, 234, 222), 'mo6', 42, (196, 164, 104)),
      num=('mo5', 80, (240, 234, 222), 5), sig=('mo5', 25, (140, 158, 148)), rule=(196, 164, 104),
      swatch=[('Deep green', (17, 28, 24)), ('Ivory', (240, 234, 222)), ('Brass', (196, 164, 104))]),
]

def background(st):
    kind, c1, c2 = st['bg']
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.42) / (H * 0.55)) ** 2)
    k = np.clip(1 - d, 0, 1) ** 1.6
    centre, edge = (c1, c2) if kind == 'flat' else (c2, c1)     # light cards: ivory centre; dark cards: warm centre
    rgb = np.array(edge, np.float32) * (1 - k[..., None]) + np.array(centre, np.float32) * k[..., None]
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert('RGBA')

def hook_frame(st, src, i=20):
    t = i / 30
    v, cover = RC.view(src, t)
    plate = Image.fromarray(v).convert('RGBA'); im = plate.copy()
    RC.topshade(im)
    fk, col, tr = st['hero']
    s = R.fit('VANTA HOUSE?', fk, 880, 220, track=tr)
    hero = T('VANTA HOUSE?', fk, s, col, track=tr, shadow=0.9, sblur=18, sdy=6)
    wt, wf, ws, wc, wtr = st['who']
    who = T(wt, wf, ws, wc, track=wtr, shadow=0.9, sblur=14, sdy=4)
    cy = RC.head_top(i) + 58 - hero.height / 2 + 30
    place(im, hero, 540, cy)
    place(im, who, 540, cy - hero.height / 2 - 16)
    m = RC.mask(i).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))
    person = plate.copy(); person.putalpha(m); im.alpha_composite(person)
    return im.convert('RGB')

def end_frame(st):
    im = background(st)
    f, sz, c, tr = st['eyebrow']; place(im, T('COME AND SEE', f, sz, c, track=tr, shadow=0), 540, 470)
    f, c, tr = st['vh']; s = R.fit('VANTA HOUSE', f, 930, 168, track=tr); place(im, T('VANTA HOUSE', f, s, c, track=tr, shadow=0), 540, 590)
    f, sz, c = st['sub']; place(im, T('Naguru, Kampala', f, sz, c, shadow=0), 540, 692)
    place(im, Image.new('RGBA', (120, 2), st['rule'] + (255,)), 540, 770)
    kind, f, sz, c, fill = st['pill']
    if kind == 'outline':
        P = ST.outline_pill('FREE SITE VISIT', sz, 10, c)
    else:
        L = T('FREE SITE VISIT', f, sz, c, track=8, shadow=0); g = L.getbbox(); w, h = g[2] - g[0] + 88, g[3] - g[1] + 44
        P = R.rrect((w, h), h // 2, fill + (255,)); comp(P, L, (w - L.width) / 2, (h - L.height) / 2)
    place(im, P, 540, 860)
    f1, s1, c1, f2, s2, c2 = st['send']
    place(im, ST.baseline_line([('Send', f1, s1, c1, 0), ('VANTA', f2, s2, c2, 8), ('on WhatsApp to', f1, s1, c1, 0)], gap=18), 540, 1000)
    f, sz, c, tr = st['num']; place(im, T('0741 131 420', f, sz, c, track=tr, shadow=0), 540, 1098)
    f, sz, c = st['sig']; place(im, T('BLACKSTONE REAL ESTATE', f, sz, c, track=9, shadow=0), 540, 1215)
    return im.convert('RGB')

def main():
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', RC.WIDE, '-vf', "select='eq(n,20)'", '-vsync', '0', '-frames:v', '1',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    src = np.frombuffer(p.stdout.read(), np.uint8).reshape(1080, 1920, 3)
    TW, TH = 405, 720; GAP = 28; M = 40
    board = Image.new('RGB', (M * 2 + 4 * TW + 3 * GAP, 2 * TH + 380), (233, 230, 225)); d = ImageDraw.Draw(board)
    for k, st in enumerate(STYLES):
        x = M + k * (TW + GAP)
        hf = hook_frame(st, src); ef = end_frame(st)
        hf.save(S + '/C/var%d_hook.jpg' % (k + 1), quality=92); ef.save(S + '/C/var%d_end.jpg' % (k + 1), quality=92)
        board.paste(hf.resize((TW, TH), Image.LANCZOS), (x, 110)); board.paste(ef.resize((TW, TH), Image.LANCZOS), (x, 110 + TH + 16))
        lab = T(st['name'], 'sans_sb', 30, (30, 28, 25), track=4, shadow=0)
        board.paste(lab, (int(x + TW / 2 - lab.width / 2), int(58 - lab.height / 2)), lab)
        fl = T(st['fonts'], 'sans', 24, (70, 66, 60), shadow=0)
        yb = 110 + 2 * TH + 16 + 40
        board.paste(fl, (int(x + TW / 2 - fl.width / 2), int(yb - fl.height / 2)), fl)
        for j, (nm, c) in enumerate(st['swatch']):
            sx = x + 20 + j * 128
            d.rounded_rectangle((sx, yb + 40, sx + 110, yb + 110), 10, fill=c, outline=(160, 154, 146), width=1)
            nl = T(nm, 'sans', 19, (50, 47, 43), shadow=0); board.paste(nl, (int(sx + 55 - nl.width / 2), int(yb + 132 - nl.height / 2)), nl)
            hl = T(hexs(c), 'sans_r', 17, (110, 104, 96), shadow=0); board.paste(hl, (int(sx + 55 - hl.width / 2), int(yb + 156 - hl.height / 2)), hl)
    board.save(S + '/out/Vanta_style_options_1-4.jpg', quality=90)
    print('board', board.size)

if __name__ == '__main__':
    main()
