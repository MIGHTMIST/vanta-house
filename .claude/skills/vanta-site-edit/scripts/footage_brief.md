# Footage pass brief (read fully)

Goal: list EVERY usable moment of the building and the workers in the site clips you are given, so the editor can build a
slow-motion, beat-cut vertical (9:16, 1080x1920) real-estate edit. The owner said: "pick up the best parts of the building
only, the building and the workers ... don't leave any part of it, use every part that you can ... it should be slow motion
because we didn't film that much". So be thorough: every clip, every usable stretch, not just one best moment.

R = /tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad
- Clips: R/sitevids/<NAME>.MP4 (1920x1080, 30 fps, landscape, Canon, about 1-27 s each; GV3A0037 is 73 s).
- An older written log of all clips exists: R/out/sitelog/SITE_LOG_ALL.md (read your clips' rows first; it can be wrong).
- Motion numbers per clip, 10 samples/s (motion = frame difference, sharp = focus, bright = 0-255): R/hype/motion.json
- To look at frames: `ffmpeg -v error -ss <sec> -i R/sitevids/<NAME>.MP4 -frames:v 1 -vf scale=480:-1 R/hype/<yourdir>/<file>.jpg`
  or a strip: `ffmpeg -v error -i R/sitevids/<NAME>.MP4 -vf "fps=2,scale=240:-1,tile=6x3" -frames:v 1 R/hype/<yourdir>/<NAME>.jpg`
  then view with Read. Work in your own folder R/hype/<yourdir>/ . The disk is almost full (under 300 MB free): keep images
  small, delete each image after you have looked at it, and delete the folder at the end. Never write video files.

## How the footage will be used
- Slow motion: most shots will play at 0.5x (sometimes 0.4x) with frame interpolation. Good slow-mo source = smooth or steady
  camera, people moving, no fast whip pans, no heavy motion blur. A 2.4 s source stretch at 0.5x fills about 4.8 s.
- Two framings are possible: (a) "crop" = a vertical 9:16 slice of the frame (608 px wide out of 1920), give crop_x = slice
  centre as fraction of width (0.16 far left ... 0.5 centre ... 0.84 far right) and check the subject stays inside it for the
  whole stretch; (b) "frame" = the whole 16:9 picture kept, shown smaller inside the vertical canvas over a blurred copy.
  Say which suits each moment (wide views of the tower or the neighbourhood usually need "frame"; single workers suit "crop").

## Rules (hard)
- Only the building (Vanta House site, the tower, slabs, stairs, scaffold, rebar, blocks) and the workers. Neighbourhood
  views are allowed only as short "location" moments - mark them type "location".
- Skip: blown-out white sky over most of the frame, very dark, out of focus, a pole blocking the view, heavy shake.
- People: small, distant or turned-away workers are fine. A large, clearly recognisable face -> still list it, but set
  "face": true so the owner can decide.
- No readable documents, signs, phone numbers or prices in frame (mark "text_in_frame": true if any).

## Output
Write JSON to R/hype/<yourfile>.json :
{"clips":[{"clip":"GV3A0011","usable":true,"segments":[
   {"in":0.6,"out":2.0,"type":"workers|building|detail|location","what":"two workers carry a sack, backlit",
    "camera":"static|pan right|tilt up|push in|handheld walk|...","slowmo":"great|ok|poor","framing":"crop|frame|both",
    "crop_x":0.6,"score":1-5,"face":false,"text_in_frame":false}], "skip_reason":""}], "top10":["GV3A0011@0.6-2.0", ...]}
score 5 = hero, 4 = strong, 3 = fine filler, 2 = only if needed, 1 = avoid.
Then reply with a short summary: how many usable segments, your top 10 with one line each, and anything surprising
(for example clips that are not this site). Do not edit any other file.
