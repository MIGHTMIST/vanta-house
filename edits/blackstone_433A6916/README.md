# Blackstone clip 433A6916 — two vertical edits (4 Nov 2026)

Source: `433A6916.MOV` from the shared "blackstone" folder (2.04 s, 1920×1080, 25 fps). Footage is not in git.

| version | files | what it is |
|---|---|---|
| A, made with Abdullahi's skills | `A_render_skills.py`, `A_mix.py` | Vanta House short: "Who is behind VANTA HOUSE?" behind John's head, Blackstone glass card rising from behind him, approved cream end card. Motion Explainer Kit helpers, Anton + Libre Caslon, pxb music + SFX, −14 LUFS. |
| B, Claude's own | `make_edit.sh` (first draft), `B_edit_own.sh` (high-quality rebuild) | Slow-motion pan from the listener to the speaker, warm/teal grade, own text, synthesized pad. |

Shared steps: 0.5× slow motion with motion interpolation (lossless intermediate), 1080×1920 30 fps, masters at x264 CRF 12 with BT.709 tags.
A needs the Motion Explainer Kit (render.py, kin2.py, motion_v3.py, fonts) and rembg masks; paths in the scripts point at the session scratchpad.
`encode_under_limit.sh` makes a two-pass 1080×1920 copy at a target bitrate.

## Video C: Claude's edit in a proposed Vanta style v2 (4 Nov 2026)
| files | what it is |
|---|---|
| `C_style_v2.py` | the proposed style: Vanta Black #0F0E0C, Stone #EFE9DF, Champagne #C9AC7D, Bronze #967A54, Warm grey #968D80; Cormorant Garamond (display, italic accents) + Jost (tracked caps, numbers); wipe reveals, hairline rules, outlined pill, baseline-aligned mixed-font lines |
| `C_render_newstyle.py` | darker "Vanta" grade, hook behind John's head, one continuous zoom-out from his close-up to the full meeting in an editorial window, dark end card with the approved words, dark-to-dark dissolve |
| `C_mix.py` | same music, fewer and softer SFX, a gentle riser into the end card, −14 LUFS |
| `C_style_board.py` | before/after sheet from real frames of videos A and C |
Fonts come from npm (@fontsource/cormorant-garamond, @fontsource/jost, both SIL Open Font License).

`C_style_options.py` renders four style options as stills (hook frame + end card): 1 Vanta Black, 2 Ivory Classic (Libre Caslon), 3 Modern Clean (Montserrat), 4 Emerald & Brass (Playfair Display). Extra fonts from npm: @fontsource/montserrat, @fontsource/playfair-display.

## Video D: style 3 "Modern Clean", 15 s, original score (4 Nov 2026)
| files | what it is |
|---|---|
| `D_render_modernclean.py` | Montserrat; off-white #F3F1ED, charcoal #1E1E1E, sand #B09268. John hook, zoom-out into a rounded window, then three Vanta 3D-tour renders (cube faces cropped 9:16, labelled "Artist's impression · furniture shown for style") with fact chips: 1, 2 & 3 bedroom homes / In Naguru, Kampala / Handover expected October 2027; end card panel slides up. |
| `D_compose_score.py` | original 7-bar score at 114 BPM (bar = 2.105 s) so every cut lands on a bar line: soft intro, build, drop on the first render, crash on the end card, final Cadd9. Rendered with FluidSynth + FluidR3_GM.sf2 (MIT). |
| `D_mix.py` | score + a few soft SFX from the pxb library, two-pass loudnorm to −14 LUFS. |

## Videos E and F (4 Nov 2026), new concepts, palette 3 + IBM Plex Mono record stamps
| files | what it is |
|---|---|
| `E_render_realonly.py` | "Not rendered. Real." 16.8 s, real material only: John's site photos (WeChat, 20–22 Oct 2026) and the blackstone clip. Hook NO RENDERS. / NO AI. / REAL. on three timpani hits; 12 photos land as prints on the beat (STEEL. / BRICK BY BRICK. / FLOOR BY FLOOR.); John; John's print lands and the log blurs back behind "SEE IT WITH YOUR OWN EYES." |
| `F_render_imagined_vs_real.py` | "Imagined vs Real" 17.5 s: split screen, THE DREAM (Film 1 shots, labelled artist's impression · AI) over THE WORK (real dated site photos), a new pair wipes in on every bar; BUILT BY REAL PEOPLE (John-only crop); FROM PICTURE / TO PLACE. No gym or pool shots (marketing decision D5). |
| `EF_compose_scores.py` | two original scores: E 100 BPM D minor documentary pulse resolving to F major; F 96 BPM D major, music box for the imagined, strings and drums for the real. |
| `EF_mix.py` | scores + synthesized camera shutter on each print (E) / soft whooshes on the wipes (F), −14 LUFS. |
| `EF_common.py` | shared helpers (fonts, crops, prints, pills, wipes). |
The man in the teal shirt is cropped out of E and F until he is cleared to appear.

## Video G (4 Nov 2026): John cold open re-edit
Source: VantaHouse_Intro_B_ColdOpen_1080x1920.mp4 (uploaded). `G_cut.py` reorders (hook "After ... years in China's investment banking" first), tightens pauses, punch-ins on jump cuts, Vanta grade, voice clean-up. `G_render.py` adds the hook text, 2-4 word captions of his words, BLACKSTONE / VANTA HOUSE chips and the Modern Clean end card. `G_compose_score.py` original bed at 81.1 BPM (end card on bar 11); `G_mix.py` ducks it ~17 dB under his voice, -14 LUFS.

## Openings A/B/C (4 Nov 2026) from John's cold-open clip
A documentary (walk-in slot is a placeholder card until the clip arrives; J-cut voice over two real site photos; MUSIC + VOICEONLY versions), B cold open (very close, crescendo, 1 s silence, small title, dark end), C proof open (NO RENDERS. / NO AI. over real site photos, then his line, Modern Clean end). John says "10 years" (confirmed by Abdullahi); G captions fixed.
