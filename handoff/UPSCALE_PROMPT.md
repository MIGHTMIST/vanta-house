# Prompt for the upscaling chat: Vanta House site videos, round 4 (15 Nov 2026)

Copy everything below the line into the other chat.

---

You are helping Abdullahi (Ember Creative, Kampala) with one job: make three finished short videos look **sharper and
cleaner** with an AI video upscaler/enhancer, **without changing anything in them**. A different Claude (Claude Code)
edited the videos and will check your results. Do only this job. Work slowly, one video at a time.

## The project
Vanta House is a real apartment building going up in Naguru, Kampala (developer: Blackstone Real Estate). These are
vertical (9:16) videos for TikTok, Instagram Reels and Facebook, cut exactly to the beat of a song. They show the real
building site, real workers and the building. This is PROOF of a real building: nothing may be invented or changed.

## Where the files are
Google Drive folder **"UPSCALE - Vanta site videos R4 (15 Nov 2026)"**
(https://drive.google.com/drive/folders/1d50EaFX2opi6WORfvGTpOQeVvnyE207H). In it (if a video is missing, ask Abdullahi
to add it; do not use any other copy):

| File | Length | What it is |
|---|---|---|
| `VantaHouse_Site_R4_2_CREW_loop.mp4` | 17.3 s | **TEST THIS ONE FIRST.** Workers on site, loops end to start |
| `VantaHouse_Site_R4_3_BUILDING_loop.mp4` | 17.3 s | The building, with camera moves; loops end to start |
| `VantaHouse_Site_R4_1_CINEMATIC.mp4` | 34.9 s | Longer cut, ends on a black screen with "VANTA HOUSE" |

All three are **1080 x 1920 (already 1080p vertical), 30 frames per second, H.264, with a stereo music track (AAC)**.
Some shots inside were filmed or made at lower quality and enlarged, so they look a little soft. That softness is what
we want fixed.

## What "better quality" means here (read this twice)
- The videos are ALREADY 1080 x 1920. **Do not make them 720p** (that would make them worse).
- Goal: **more real detail and less softness/noise at the same size, 1080 x 1920**. If the tool offers it and it is
  included in the plan, a **2x version at 2160 x 3840 (4K vertical)** is also welcome, as a second file.
- Use a real **upscaler / restoration** model (for example: Topaz Video AI / Topaz on fal, SeedVR2, Real-ESRGAN video,
  Higgsfield "upscale video", or similar). Pick a "faithful / natural / low creativity" setting.
- **Do NOT use a video generator** (Seedance, Kling, Veo, Sora, Runway Gen, MiniMax, etc.) to "remake" the video. Those
  redraw every frame and change people, scaffolding and text. Only an upscaler/restorer is allowed.

## Hard rules (break none)
1. **Change nothing in the picture.** Same shots, same order, same building, scaffolding, bricks, workers, sky, colours,
   brightness and contrast. No new people, objects, logos or watermarks. No colour change, no extra "beauty" filter.
2. **Text must stay exactly the same and stay crisp**: the teal words (e.g. "BEFORE YOU BUY A FLAT", "IT'S NOW OR
   NEVER.", "BRICK BY BRICK.", "ON SITE", "VANTA HOUSE", "NAGURU, KAMPALA"). If letters get wobbly, melted, doubled,
   or misspelled: reject.
3. **Timing must not move by even one frame.** Output = **30 fps** (not 24, not 60), the **same number of frames**,
   the **same length**. Every cut is on a beat of the music; if the timing shifts, the video is ruined. Turn OFF any
   frame interpolation / "smooth motion" / frame-rate change.
4. **Keep the sound exactly as it is.** Many upscalers drop the audio. If yours does, put the original audio back
   (for example with ffmpeg: `ffmpeg -i UPSCALED.mp4 -i ORIGINAL.mp4 -map 0:v -map 1:a -c copy OUT.mp4`). If you
   cannot do that, deliver the video without sound and say so; Claude Code will add the sound back.
5. **Faces:** workers are seen from behind, the side or far away. If the upscaler makes any face clearer or turns a head
   toward the camera, reject.
6. **Reject** any result with: flicker, shimmering scaffolding or rebar, warped bricks, smeared or "plastic" surfaces,
   halos around edges, new noise, colour shift, or a jump where the video loops back to the start.
7. **Money:** use only what Abdullahi's plan already includes. **Before you spend extra credits or pay for anything,
   stop and ask Abdullahi.** Tell him the price first.
8. **Test first:** do ONLY `VantaHouse_Site_R4_2_CREW_loop.mp4` first. Show Abdullahi the result (and the side-by-side
   checks below) and **wait for his OK** before doing the other two.
9. Do not publish, post or share anything. Do not change, move or delete any other file in Drive.

## How to check each result (before you keep it)
- Compare the original and the result **side by side at full size** at these moments: 0.0 s, 2.0 s, 5.0 s, 8.0 s,
  11.0 s, 14.0 s, 17.0 s (for the CINEMATIC also 20, 25, 30, 34 s). Look at the text, the scaffolding, bricks, the
  workers, and the sky.
- Check the file: 1080 x 1920 (or 2160 x 3840), **30 fps**, the **same duration** to 0.05 s (17.35 s / 17.35 s /
  34.93 s), and it has sound.
- Play the last second into the first second (the CREW and BUILDING videos loop): it must not jump.
- If a result breaks any rule, try **once** more with a gentler setting (less sharpening, "faithful", lower creativity).
  If that also fails, skip that video and write down why.

## What to deliver
1. Upload each kept result to the **same Drive folder**, named like the original plus `_UP` (e.g.
   `VantaHouse_Site_R4_2_CREW_loop_UP.mp4`; a 4K version as `..._UP4K.mp4`).
2. Write a short report in the same folder, `UPSCALE_REPORT.txt`: for each video, kept or rejected, the tool and model
   and exact settings, output size / fps / duration, whether the sound was kept or added back, how many tries, any
   credits or money spent, and anything that looked wrong.
3. Tell Abdullahi it is done. He will bring the results to Claude Code, which checks them frame by frame before use.
