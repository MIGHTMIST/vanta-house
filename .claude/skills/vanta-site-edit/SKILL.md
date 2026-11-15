---
name: vanta-site-edit
description: Use for every Vanta House SITE edit (construction footage, workers, the tower, site photos) for Abdullahi - beat-cut short-form videos (TikTok / Reels / Facebook, 9:16) for top of funnel. Holds everything he taught from 15-16 Nov 2026 - how to study his reference edits, how to pick footage, clean and grade it, cut every shot on the beat, text, sound levels, the hook rules from his marketing skill, the AI (Gemini Omni Flash) plan, and the review loop - so he never has to repeat it.
---

# Vanta House site edit (learned 15-16 Nov 2026; add every new lesson at the bottom)

Owner: Abdullahi (Ember Creative). Client: Vanta House, Naguru, Kampala (Blackstone Real Estate, founder John Yan).
He talks by voice notes: read for intent, not word for word. He wants an EDITOR with taste, not a tool that does
one thing he said and breaks the other rules. He iterates ("iterate iterate till you get it right"): every round,
keep what he praised, fix what he named, apply ALL earlier rules too.

## 0. How to work (his words, every time)
- **One step at a time, review your own work before you ship.** Focus. Take the time it needs.
- **Do not disturb him with questions** once he has given the material; decide with the rules below, tell him
  what you decided and why (in plain grade-3 English), and give short progress updates so he is never left waiting.
- **Use Sonnet helpers** for big looking jobs (footage passes, reference studies) with a written brief file; you
  check their work. Never trust a helper's crop/position without looking at the frame yourself.
- **Be very picky.** Only great moments go in. Weak, blurry, dark, blown-out, shaky, cluttered or boring = out.
  Ask of every shot: what does it add? Does it make the video better? Would a big film crew keep it?
- **Study references, take the best 10%, make it our own.** Not copying: "how does this trick fit OUR footage?"
  If a trick needs footage we don't have (drone, sparks, FPV), drop it.
- **Script / storyboard first** (beat by beat: shot, trick, text, sound), then build.
- He can be argued with: if a rule from his skills says otherwise, say so with the source.

## 1. Footage (where, what is usable)
- Site clips: Drive folder `1FCTHa6nD2BL9IRqyoKrWDyCnQKG_UJjt` (crew upload, 83 clips) -> local `scratchpad/sitevids/GV3A*.MP4`
  (1920x1080, 30 fps, Canon). Logs: `out/sitelog/SITE_LOG_ALL.md` (pass 1) and `hype/moments_a/b/c.json`
  (pass 2: 148 moments with in/out, type, score, slowmo, face).
- NOT this site / never use: GV3A9938-9949 + GV3A9951 (other shoot, broken), GV3A9954-9979 JPG/CR2 (a seminar in a hall),
  GV3A0045-0053 (plan documents with stamps/signatures), GV3A9996 (too dark).
- Owner's site photos (15 Nov): `site/user15/u01-u14.jpg` (u15 = duplicate of u14). Older phone photos: `site/mmexport*.jpg`.
- John on site (orange vest, workers behind, 14-16 s is best): upload `3edf9be4-beauty_20261017161429.mp4` (960x1280).
- **People rules:** workers from the back / side / far away only. The worker who walks toward the camera: show him
  walking AWAY only, never the part where he comes toward the lens with his face (GV3A9980 >16 s, 9981 >14 s,
  9982 >19 s, 0036 3-14 s, 0037 >60 s). No large recognisable worker faces. John is optional (end or cut).
- Best material (owner 16 Nov): **the workers and what they are doing** (laying blocks, rebar, carrying, mixing,
  climbing), **the environment and the views**, the tower itself. The video explains the building.
- The green-netted tower in the background of 0018/0019/0021/0023/0028 is a NEIGHBOUR, not Vanta.

## 2. Clean every shot before editing (`scripts/grade.py`)
Per clip stretch, measured from 6 sampled frames: white balance (half strength, slight warm), black point,
mid-tone gamma to 0.46, soft highlight shoulder, blown/white sky -> soft blue-teal gradient (only sky that touches the
top edge; skip interiors), CLAHE local contrast 40 %, vibrance, hi-vis pop (vests/helmets richer), light sharpen.
Photos: 55 % graded + 45 % original. Check before/after boards by eye. No blurry frames: drop them.
R15 intro look: grey picture with only hi-vis in colour, snapping to full colour on a beat (`GR.selective`).

## 3. Layout and moves
- **Use the whole 9:16** (full-screen crops of the 16:9 footage with a slow pan across so the whole building is seen).
- **Never white boxes / borders / a small picture over a blurred copy** ("cheap and ugly").
- **Do not build the whole video from one trick** (v1 = three stacked pictures swapping was rejected as "just b-roll
  coming and going"). Mix: full-screen shots, top/bottom split, three strips, photo burst, halftone freeze, speed ramp,
  whip, flash, shake, text behind the tower, outline trace... one heavy trick per 2 beats at most, rest shots between.
- Prefer **slow motion** (optical-flow, 0.45-0.6x) over zooming in. Short great moments: slow them down.
- Camera moves "like a big film crew" (push in, pull out, slide, rise) are wanted - by code pans or by AI (section 7).

## 4. The beat (non-negotiable)
- **Everything lands on the beat**: every cut, every picture, every word, every flash. Build from a beat grid.
- Train song (owner's pick, reference R2 audio): 82.2 BPM, beat 0.730 s, first beat 0.40 s, quiet intro 0-1.1 s,
  music ends 36.43 s (cut before the TikTok jingle) + soft boom tail to 38.2 s. Cut every beat or every 2 beats;
  a quarter-beat burst around 23 s; words of the song: only those ASR hears the same every time
  ("TO TELL YOU / IT'S NOW / OR NEVER." 14.0-17.9 s, "SO MUCH FOR CLOSURE, I LOST COMPOSURE." 24.96-29.9 s).

## 5. Text (brand)
Inter (ExtraBold/Black titles, SemiBold/Medium second lines), white, soft shadow, teal #2EC4B6 bar.
Hook text readable on FRAME 0 (no fade from black). "VANTA HOUSE" placed BEHIND the tower in the sky (sky mask from
the UNGRADED frame - the grade turns the sky blue and breaks the mask). Words sit lower on screen, one per beat.
Song words may glow (neon, perspective on a surface). End card: VANTA HOUSE + NAGURU, KAMPALA only.
Never: prices, phone/WhatsApp, "fully finished", discount/cheap, "on time", "safe", China Speed, % sold.

## 6. Sound
Music is the boss. Real site sound of each shot under it, **low** (owner 16 Nov: "lower them a little, they must
not disturb the music"; louder only in the hook before the music starts). Whooshes on cuts, hits on flashes,
riser into the burst, shutter on photos, pops on words - all quiet. Final -14 LUFS, true peak -1.5 dB.

## 7. Hook and marketing (from his marketing-department skill)
- Top of funnel: a stranger who knows nothing. Hooks are 80 % of the result: call out the exact person + promise,
  real setting in frame 1, movement, captions (e.g. "BEFORE YOU BUY A FLAT IN KAMPALA, WATCH THIS.").
- Proof beats claims: real site, real workers, dated progress. AI-looking footage on proof videos is a bad pairing.
- His best TikTok lost most viewers at 0:02 -> the first 2 seconds must already show the best thing.

## 8. AI version (camera moves made by AI on the real footage)
He wants a second version with AI camera angles/moves on the real footage ("like a big film crew"), without changing
the building. This session cannot send footage to outside AI APIs (permission check), so: write a full prompt
(`handoff/AI_CAMERA_MOVES_PROMPT.md`), he runs it in his browser (Cowork) chat, then brings the results back for review.
How the first round went (15 Nov): the browser chat used fal.ai MiniMax H3 Max image-to-video (not Gemini), 480x832,
24 fps, 4.5-5.2 s, about $2.20 for 14 tries. Files in Drive folder 1ZYZefhNMUZ_K4jFBdepz-AoSv2hUBeLC as
`AI_OUT_Axx_minimax_*.mp4` + `AI_OUT_REPORT_minimax.txt`.
Review + cut method (keep doing it this way):
- Download with the Drive connector `download_file_content` (it saves the video to a file); files the other chat made
  are private, so the plain drive.usercontent URL returns a login page.
- `scripts/aisheet.py`: real source frame + 9 AI frames per clip, flicker and sharpness numbers. Then full-size frames
  for faces, hands, made-up building parts. Only take a clip if the move adds something the code pan cannot.
- Geometry: MiniMax kept the picture exactly (scale 2/3, 10 px cut top and bottom, no stretch): ORB + affine check.
- AI clips came out ~3 % darker and lose 30-50 % detail by their end. `scripts/bake_ai.py`: FSRCNN x2 (OpenCV
  dnn_superres, model from GitHub; Hugging Face is blocked) -> 1108x1920 -> crop 1080, brightness matched to the
  source, sharpening that grows as the clip goes soft. Version A itself is a 1.78x upscale (608 px crops), so the gap
  is only ~1.3x.
- `scripts/render8.py` = render7 timeline + `ai=(clip, start, speed)` on chosen beats. Speeds: buildings/props 1.9-2.4x
  (fast move on the beat), people 1.0-1.25x (1.25x = one AI frame per output frame, no in-between frames), end shot
  0.62x with optical-flow in-betweens. Sky masks on AI frames: `scripts/aisky.py` (blue, flat, not green net).
- Same sound mix as Version A (same cuts), the AI soundtrack is never used.

## 9. Pipeline (scripts in `scripts/`, paths point at the 15 Nov scratchpad: change `R`/`S` first)
`grade.py` (clean/grade), `v2core.py` + `fillcore.py` (decode, flow slow-mo, full-res crops), `fx2.py` (text, neon,
flash, light leak, shine, shake), `render7.py` (CURRENT full-screen beat edit, script/timeline at the top as data), `render6.py` (previous),
`render5.py` (stacked version), `sfx7.py` (sound map + mix, site sounds low), `picksheets.py` (every moment as four
9:16 crops with a sharpness score -> contact sheets for picking). Render in 2-3 parallel parts with NOAUDIO=1, join frame-exact with the
concat filter, mux the final wav. Check: frame count, freezedetect, blackdetect, loudness, 2-fps contact sheets of
the whole video and full frames at every trick; fix and re-render before sending.

## 10. References studied (reports in `scratchpad/hype/effects_*.md`, `refs_*.md`)
R1 singer+car lyric words; R2 train "DAILY / LIFE LATELY" (the song; halftone sepia switch, collage pops, cream
flash cut, burst); R3 house tour in an editor timeline (motion blur on every cut, whooshes); R4 house from debris +
tri-strips; R5 title placed in the scene; R6 luxury apartment roll match-cuts, light leak; R7 POV editor; ref.mp4
demolition hype (drop, object-pass wipes); R9 neon lyric words on the building; R10 rotated landscape spins;
R11 cinematic low angles, rounded PIP; R12-R14 grade/lighting lists; R15 construction edit (grey + hi-vis intro,
hi-vis brightest, low wide angles, burst + hold); R16 kinetic type; R17 AI editor: building highlight, labels;
R18 captions/outline; R19 tracked labels; R20-R24 "made with Claude" effects (halftone impact, press, stamp...);
R25 construction company edit (helmet pass, worker cut-out, scale-match); R26 creator tricks (assemble, portals,
reflections); R27 anime edit (cinema crop, typed words, cuts on action).

## 11. Lessons log (newest last)
- 15 Nov: stacked three-picture edit with white-free bands was liked for "everything comes up on screen", but as the
  ONLY layout it is boring. Hook frame must not start half black.
- 15 Nov: a Drive folder may hold other shoots: check every new file before use.
- 16 Nov: be very picky; workers + environment + views; worker only from the back; site sounds lower; clean
  everything; script first; follow the beat everywhere; John optional.
- 16 Nov (v3 script, render7): hook = worker from behind walking to the tower, grey with hi-vis colour, hook text on
  frame 0 -> 4 one-beat work shots -> the building revealed FLOOR BY FLOOR (colour rising in 4 half-beat steps with a
  teal line) + VANTA HOUSE behind it -> NAGURU, KAMPALA on the city view -> split crews -> ON SITE halftone -> 4 owner
  photos on half beats -> one shot per beat under the song's words -> REAL / WORKERS / STEEL / CONCRETE each over a
  matching picture -> quarter-beat burst (no whip blur on quarter-beat shots, it blurs the whole shot) -> three strips
  landing 4 frames apart (never leave half the screen black) -> building shots -> John 3 beats -> end card.
- Picking method that worked: contact sheets of every moment as four 9:16 crops + sharpness, my own A/B/C pass, then
  a Sonnet second opinion; both agreed on the A list. Moving pans (e.g. GV3A0028 21.2-22) look smeared in slow motion:
  start after the pan settles.
- 16 Nov (v3 delivered: out/VantaHouse_Site_FULLSCREEN_v3.mp4): QA at 2 fps + full frames caught (1) a shot cut from
  the middle of a camera pan (GV3A0028 22-23 s) that smears in slow motion -> replaced with owner photo u04;
  (2) green-dominant frames (GV3A9987 tower in green net through trees) get a PINK sky from the white-balance step ->
  do not use them, or grade them by hand; (3) GV3A9980 22.8-23.1 s the worker's body passes the lens -> start at 23.4.
  Fix only the bad beat: render that frame range alone and splice it in with the concat filter (frame-exact trims).
- 16 Nov: the AI version is handed to his browser (Cowork) chat: prompt `handoff/AI_CAMERA_MOVES_PROMPT.md`, 12 cleaned
  9:16 source clips `AI_SRC_A01..A12` in Drive folder 1ZYZefhNMUZ_K4jFBdepz-AoSv2hUBeLC (made by `prep_ai.py`).
  Results come back as `AI_OUT_A..` + `AI_OUT_REPORT.txt`; review every frame for warping/added people before use,
  then cut Version B with the same render7 timeline (swap the matching beats).
- 15 Nov (Version B, render8): kept A01 A02 A03 A06 A07 A08 A10 A11(0-3.5 s) A12; dropped A04 (soft city, made-up
  palms), A05 and A09 (moves too small to beat the real shot). Moves that ADD picture at the edges (pull-back, crane
  "reveal") invent building parts: use only the part that stays near the real frame.
- 15 Nov: the grey + hi-vis look broke on the AI vest (its orange came out at hue 0-4, outside the 5-45 range) -> grey
  camouflage patches. `selective2` in render8 (also very bright, saturated red-orange; holes filled) - only on AI shots,
  because it tints sunny bricks on real shots.
- 15 Nov: QA MISSED a full worker face in Version A at 2.6-3.3 s (GV3A9994 0.2-0.64, crop cx .36-.42: the worker
  looks into the lens). The Sonnet rating said "face: no". Fix: same shot framed on the right worker (cx .80-.86).
  Rule: in QA, look at EVERY worker shot at full size for faces, not only the 2-fps sheet, and never trust a helper's
  "no face".
- 15 Nov (3-video set, `scripts/render9.py`, VID=v1|v2|v3, `sfx9.py`, `finish9.sh`): the owner said one video crammed too
  much ("fit every image so the pacing is okay") -> MAX THREE videos, all on the same song, calmer pacing (2 beats a
  shot in the verses), the footage shared out: v1 THE CREW (workers), v2 THE BUILDING (AI camera moves), v3 THE PHOTOS
  (all 14 owner photos, each with time). His song for these: the long version of the train song from his lyric video
  (`refs4/SONG.mp4` audio): beat B(k)=0.244+0.723k, intro build 0-11.8 (strobe 4.2-6.1, 9.9-11.8), lines at 12.0-17.2 /
  23.6-28.6 / 35.2-39.0 / 39.4-45.6 ("I think I wrecked it" never on screen), music ends 46.0 (TikTok jingle 46.1) ->
  cut on beat 63 (45.79) + boom, END 47.0. First beat is at 0.244 s: the hook shot must own frame 0 (SH[0]['t0']=0).
- 15 Nov: HIS FAVOURITE TEXT LOOK = the "ON SITE" card: Inter Black, brand teal, scale pop 1.15->1 + fade, then a light
  glint sweeps across (fx2.shine), over the halftone sepia freeze. He wants ALL words like that ("that font, the way it
  shines"), appearing word by word as sung like his lyric video. Teal needs a dark soft backing on green net / sky.
  Exception: VANTA HOUSE behind the tower stays white (teal disappears on the blue-teal sky).
- 15 Nov: new tricks from his Spider-Man refs (N1-N4) that fit our footage: stacked big words beside the subject landing
  one per beat (BRICK / BY BRICK.), photo stutter-flash (2 frames on the beat), black breath (0.36 s) before drops,
  strips landing 4 frames apart, echo trail on a walking worker, soft light streak, photo slam (tilt + scale settle).
- 15 Nov: the grade's local contrast mottles flat skies (painted look) -> `sky_clean` in render9: smooth inside open sky
  only, averaging sky pixels only (no halo), thin things in the sky protected (a mast got erased by plain blur).
- 15 Nov: strips that land a beat apart leave half the screen black for over a second: never; always 4 frames apart.
  Soft/smeared shots to avoid: GV3A0020 0.6-2 (camera moving), GV3A0035 0-2.6 (fast worker motion blur);
  GV3A9982 12-18 has a small worker facing the camera.
- 15 Nov ROUND 4 (`scripts/render10.py`, VID=n2|crew|build; `sfx10.py`; `finish10.sh` + `beatcheck.py`). His notes on the
  47 s set: "FOLLOW THE BEAT" (said many times), slow some shots then "boom" on the hit, short videos that HIT and LOOP,
  best parts only, no John (the video is about the building and the workers), no floor-reveal "curtain" (the teal line
  rising with grey above it), grade properly from his colour samples, and one video cut like his Spider-Man ref (N2).
  * Beat grid re-measured on the drums (HPSS + phase scan): B(k) = 0.230 + 0.723 k, hits within +-15 ms, claps on odd k.
    Cuts go on the frame NEAREST the beat (frame = round(beat*30)); the new shot lands SHARP (no whip blur at its start)
    with a zoom punch (stronger on the claps) and a small punch on every clap inside long shots; slow-mo shots ramp 3.2x
    in their last 7 frames with motion blur + whoosh = "slow ... slow ... BOOM". No cuts at fractional beats except bursts.
  * N2 (Spider-Man ref) uses THE SAME SONG from the same start: its cuts are on whole beats 3,4,8,10.5,12,16,17..24 (one
    per beat in the verse), 29, 30, 33, 36, 38, 44; 1-1.5 beats of black at k3-4 and k10.5-12; white flash on k16; comic
    covers stutter on/off (4 on / 3 off frames) over the long intro shots; ends flash + black + name tag flicker (k44-48).
    Our covers: ON SITE (halftone u14), VANTA HOUSE magazine (u08 + masthead), REAL WORK. (halftone u02), NAGURU (u09).
  * Loops: song window beat 16 -> 40 (17.35 s; starts on the drop, ends on a beat). The last shot is the START of the
    first shot's clip, so the picture runs on seamlessly across the loop.
  * Grade = `look10.film_look` over every frame (his R15/R12 samples): deep teal sky darker at the top, teal shadows /
    warm highlights, earth tones richer, greens muted, hi-vis brightest, blacks lifted to ~10, highlights rolled to ~235.
