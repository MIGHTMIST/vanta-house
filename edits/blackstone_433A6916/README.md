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
