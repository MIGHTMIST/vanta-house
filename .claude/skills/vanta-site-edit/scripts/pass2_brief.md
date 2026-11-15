# Footage pass 2 (deep) - read fully

The owner says the first pass did not look properly: "go back to the footage ... we have big footage, long site-work clips ...
look at it properly ... pick many many good parts". So this time step through EVERY clip at 2 frames per second (long
clips too, end to end) and list every usable moment, many per long clip. Be generous: a moment is usable unless it is
broken (blur, black, blown white, pole across the lens, a large recognisable face, a document/sign with readable text).

R = /tmp/claude-0/-home-user-vanta-house/253db02e-90a6-5547-b8b3-69bd9a44cdc8/scratchpad
- Clips: R/sitevids/<NAME>.MP4 (1920x1080 30 fps).
- First-pass results to improve on (do not just copy them): R/hype/footage_a.json, footage_b.json, footage_c.json.
- Make 2-fps strips yourself, one per clip (split long clips into several strips of 24 frames = 12 s):
  `ffmpeg -v error -ss <start> -t 12 -i R/sitevids/<NAME>.MP4 -vf "fps=2,scale=240:-2,tile=6x4" -frames:v 1 R/hype/<yourdir>/<NAME>_<start>.jpg`
  Tile order is left-to-right, top-to-bottom, 0.5 s apart starting at <start>. View each with Read.
  The disk is almost full: delete each image after viewing; delete your folder at the end. Never write video files.

## How the moments will be used
The edit stacks THREE whole 16:9 pictures (no crop) on top of each other to fill a vertical phone screen; one of the three
changes on every beat, so each moment is on screen ~2.2 s, usually at half speed (so 1.1-1.5 s of real footage is enough).
So short moments are fine. Workers doing things are the priority (laying blocks, carrying, rebar, mixing, walking,
climbing, measuring, crews), then the building (tower, slabs, scaffold, stairs, interiors), then details.

## Output
JSON at R/hype/<yourfile>.json:
{"moments":[{"clip":"GV3A0028","in":4.0,"out":6.0,"type":"workers|building|detail","what":"two men lift a red block onto the stack",
  "camera":"static|pan|tilt|walk","score":1-5,"slowmo":"great|ok|poor","face":false}], "skipped":[{"clip":"..","why":".."}]}
- in/out in source seconds (accurate to 0.5 s); each moment 1.0-4.0 s long; consecutive moments in a long clip may touch.
- score 5 = hero, 4 = strong, 3 = good, 2 = filler, 1 = avoid.
Then reply in 8 lines: how many moments (by type), the 10 best, and anything new that the first pass missed.
Do not edit other files.
