# Reference study 3 (read fully)

The owner (a real-estate developer's marketing person) sent 13 more TikTok references for a vertical 9:16 edit of his
BUILDING SITE (Vanta House, Naguru, Kampala: concrete tower under construction, workers in hi-vis, slabs, rebar, scaffold).
His words: "do not just copy things ... understand them, reverse engineer, take what is useful for our videos";
"highlight the site, the site is the most important part"; "look at the lighting ... clean the footage ... make it look
professional"; some videos are people explaining effects they made "with Claude" - he wants to know which of those effects
we can use. Our edit: three whole 16:9 pictures stacked edge to edge filling the 9:16 screen, one picture changes on each
beat of the song, slow motion, brand = white Inter font + teal #2EC4B6 accent, no prices/phones.

R = /tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad
Videos: R/refs6/R<N>.mov or .mp4 (576x1024 vertical, R16 is 768x576). Each ends with a TikTok logo outro: ignore it.
Overview sheets (1 fps): R/refs6/S<N>.jpg. Look closer yourself:
- `ffmpeg -v error -ss <t> -t 2 -i <file> -vf "fps=6,scale=200:-2,tile=6x2" -frames:v 1 R/hype/<dir>/x.jpg` (6 fps strip)
- `ffmpeg -v error -ss <t> -i <file> -frames:v 1 -vf scale=576:-2 R/hype/<dir>/f.jpg` (one full frame; read on-screen text)
View with Read. Work only in R/hype/<dir>/; disk is nearly full: small images, delete after viewing, delete the folder at
the end, never write video/audio files. If a video has speech that explains effects, you may transcribe it for that purpose:
`python3 R/scripts/asr_words.py <wav> <out.json>` after `ffmpeg -v error -i <file> -vn -ac 1 -ar 16000 R/hype/<dir>/a.wav`
(delete the wav after). Do NOT transcribe or quote song lyrics; only quote speech that explains editing.

For each of your videos write:
1. What it is (1 line) and what makes it good (3-5 points: hook, rhythm, light/colour, text, effects, payoff).
2. LIGHTING / COLOUR: describe the look precisely (contrast, black level, highlight roll-off, colour of shadows / mids /
   highlights, saturation, skin/sky handling, glow/bloom, grain, vignette). If the video teaches lighting setups, list
   each setup by name and what it looks like, and say which ideas translate to GRADING existing daylight site footage
   (we cannot relight the site; we can only grade, add glow, light sweeps, vignettes, sky work).
3. EFFECTS: every distinct effect with timestamp and a frame-level description (what moves, how many frames, easing).
   For the "made with Claude" videos list every effect they name or show (e.g. halftone, newspaper layout, stamp,
   strike-through, lens ring...) with how it looks.
4. TEXT: font look, size, colour, position, animation in/out, how words relate to picture and beat.
5. HOW THEY HIGHLIGHT THE SUBJECT (building/product/person): anything that pulls the eye to the subject.
Final section "FOR OUR SITE EDIT": the 10 most useful ideas from your videos, each with a concrete code recipe
(Python + OpenCV/numpy + ffmpeg, frames at 30 fps, parameters) that works on whole 16:9 site pictures inside our stack,
plus a list of what NOT to take and why.
Write to R/hype/<file>.md and reply with a 12-line summary.
