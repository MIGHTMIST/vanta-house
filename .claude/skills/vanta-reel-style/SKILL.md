---
name: vanta-reel-style
description: Use for every new Vanta House / Blackstone (John Yan) video Abdullahi brings - interview footage, cutaways, site photos, plans, Sarah's voice lines. Holds the look he approved on 4 Nov 2026 (the "MyEdit_B / video M" style used in A/B/C v3), the order of speakers, the sound mix, the facts rules and how to deliver to his Google Drive, so nothing has to be re-asked or re-done.
---

# Vanta reel style (approved 4 Nov 2026)

Abdullahi said "I liked this, make also something like this" about MyEdit_B_own, then had A/B/C redone in the
same fonts and colours (v3). That look is the house style now. Do not change it unless he asks.
Do not edit his other skills (talking-head-reel-pipeline, video-ad-editor, vanta-film-workflow) without asking.

## 1. The look (video M)
- Frame 1080x1920, 30 fps. Deliver H.264 High, bt709 tags.
- Font: **Inter** (`/usr/share/fonts/opentype/inter/`). Titles Inter ExtraBold, ALL CAPS, about 80-104 px
  (keep each line under ~940 px wide; measure with PIL). Second line Inter Medium ~46 px caps. Captions Inter Bold 50 px.
- Colour: white text (second line ~#ECECEC), soft drop shadow, **teal bar #2EC4B6, 96x6 px**, centred ~22 px above each title.
- Bottom gradient on footage: black, alpha 0 above y=980, rising to ~215 at the bottom (power 0.9). Captions sit at y~1195 inside it.
- Grade (ffmpeg): `curves=all='0/0 0.25/0.23 0.5/0.49 0.8/0.80 1/0.95', eq=contrast=1.06:saturation=1.10,
  colorbalance=rs=-0.04:bs=0.05:rm=0.01:gm=-0.025:rh=0.05:gh=-0.005:bh=-0.04, vignette=angle=PI/5, unsharp=5:5:0.4, noise=alls=4:allf=t`.
- Motion: slow eased glides (smoothstep). Video slow motion with `minterpolate=fps=72:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,setpts=2.4*PTS,fps=30`.
  Stills: pre-shrink with INTER_AREA then sub-pixel warpAffine (no shimmer), push 1.00->1.12 or slow pan.
- Text animation: line 1 fades/rises 26 px over 0.5 s, line 2 follows 0.25 s later; bar fades with line 1.
- Cuts: 0.5 s crossfades between glide shots; hard cuts in talking parts.
- Plan cards: dark radial background (#282A2C -> #0A0A0B), plan on a white rounded card (r=26) with soft shadow,
  label above (teal bar + Inter ExtraBold, e.g. "2 BEDROOMS"), small grey note under it.
- End card: dark, "VANTA HOUSE" (Inter ExtraBold 104, teal bar above) and "NAGURU, KAMPALA" (Inter Medium 46) ~140 px lower,
  slow 3% push. **Nothing else: no WhatsApp number, no phone, no price.**

## 2. Story order
- **John speaks first, Sarah speaks last.** Sarah (AI voice) closes every video; her last line is
  "Vanta House, in Naguru, Kampala." over the end card.
- **Show the floor plans / pictures while Sarah talks.** Real site photos under her "real workers, real steel, real concrete" lines.
- Use real cutaways between John's lines (wide at desk, leaning in, glasses, close smile, laptop).
- Openings he liked: A documentary ("Preparing for my documentary / about building in Kampala" over cutaways, hard cut to the hook),
  B cold open (very close hook, music builds, 1 s silence, small title "JOHN YAN · FOUNDER, BLACKSTONE REAL ESTATE"),
  C proof (John hook, then Sarah "NO RENDERS." / "REAL SITE." over site photos, plans, end card).
- Short glide pieces (video M): 3 shots x 4.3 s, two-line titles, ending on VANTA HOUSE / NAGURU, KAMPALA.

## 3. Sound
- John: cleaned voice. Sarah: raised to match John (about +6 dB, `volume=2.05`).
- Render **each voice piece to its own WAV** then amix (one big multi-seek graph cut a video short once).
- Music: original score (FluidSynth + FluidR3_GM.sf2, or numpy pad for glide pieces) or tracks from the Drive folder
  "Vanta Sounds" (free for commercial use, no credit needed). Duck music **17 dB under voice**. Final **-14 LUFS, TP -1.5** (two-pass loudnorm).
- SFX: whoosh into cuts, soft hit on titles, shutter on photos, swish on plans. Keep them quiet.
- Never cut the end of a word: check with silencedetect / ASR (Sarah's "2027" ends at 14.62 s in reel r1, not 13.98).

## 4. Facts and rules (always)
- John: "After **10 years** in China's investment banking industry..." (ASR hears "two"; it is 10 - confirmed).
- Only facts from Vanta papers / Sarah's approved lines: 1, 2 & 3 bedroom homes; 100 boutique homes; Naguru, Kampala;
  expected ready October 2027. No prices, no old payment plan (30%/20 months), no "fully finished", no gym/pool shots (D5).
- Renders / AI / furnished 3D plans are labelled "ARTIST'S IMPRESSION" (+ "LAYOUT MAY CHANGE" on plans).
- Do not write "NO AI" when Sarah (AI voice) is in the video.
- Man in the teal shirt is not cleared: crop him out.
- "Netflix" word or red logo never in a paid ad; trend sounds only inside TikTok/IG for page posts.

## 5. Delivery (he wants everything in his Google Drive)
- Drive folder: "Claude edits - blackstone 433A6916 (4 Nov 2026)", id `1ZYZefhNMUZ_K4jFBdepz-AoSv2hUBeLC`.
- The Drive connector only carries files up to **~3.1 MB**. So for each video:
  1. HQ master `<Name>_1080x1920_HQ.mp4` (CRF 13-17, AAC 320k) -> send in chat with SendUserFile.
  2. `<Name>_WhatsApp_720.mp4` (720x1280, CRF 23-24, maxrate 1400k) **under 3.0 MB** -> upload to the Drive folder
     with `base64Content: sha256:<hex>:<abs path>` (never type base64). If it is over, lower maxrate before uploading.
  3. Tell him the HQ files must be dragged into Drive by hand (too big for the connector).
- Check before sending: duration video = audio, no freezes (`freezedetect`), ASR transcript reads right, loudness -14.
- Commit scripts to the repo branch with a README note.

## 6. Scripts in `scripts/` (reference implementations)
Paths inside are hard-coded to the 4 Nov scratchpad (`S = ...`): point `S` at the new session's scratchpad first,
and put sources in the same sub-folders (G/src.mp4 cold open, H/src2.mp4 cutaways, site/ photos, sarah/ voice + json, pack/ plans).
- `renderM.py` + `finalM.sh` - video M slow-glide piece (plates, Inter titles overlay, numpy pad, grade, encode).
- `editB_lossless.sh`, `slow_lossless.sh` - the original MyEdit_B 4 s glide.
- `renderV3.py` - A/B/C v3 (build() holds each timeline; L() holds the text styles). Depends on
  `renderABC.py`, `renderD.py`, `renderC.py`, `docs_common.py`, `styleC.py`, `render_base.py` (rename back to `render.py`, it lived in A/build).
- `composeV2.py` / `composeV3.py` - original scores. `mixV3.py` - voice + ducked music + SFX + loudness.
- `asr_words.py` - word timings (Parakeet via sherpa-onnx) for captions and cut checks.
