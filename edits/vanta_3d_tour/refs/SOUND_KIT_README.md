# snd3d - sound kit for the Vanta House 3D architectural films

19 WAV files, 48 kHz stereo, 24-bit. Everything is final: `sfx3d_<type>.wav`. Built 10 Nov 2026.
Freesound was not usable from this machine (HTTP 403, not retried). Wikimedia Commons was tried (Openverse search
works) but upload.wikimedia.org answered HTTP 429 (rate limit) for every download, and the only real candidates
were two CC BY dawn-chorus recordings from India; so nothing from Wikimedia is in the kit. See CREDITS.md.

One-shots are peak-normalised to -3.0 dBFS. Ambiences are -20.0 LUFS integrated (peaks -6 to -8 dBFS).
Loops are seamless by construction (all noise, modulation and reverb tails are periodic / circular), not by crossfade;
seams were checked by measurement and spectrogram (check/_loop_seams.png).

"Mix gain" = suggested level for the fader relative to the file as delivered, against music at about -14 LUFS
and voice-over on top. Starting points; set by analysis, not by ear (nobody has listened to these yet).

| file | dur (s) | what it is | source | mix gain | loop |
|---|---|---|---|---|---|
| sfx3d_whoosh.wav | 0.83 | soft airy camera/cut whoosh | kit (Mixkit "Cinematic wind swoosh") | -14 dB | n |
| sfx3d_long_whoosh.wav | 2.37 | slow wind-like drone/transition whoosh | kit (Mixkit "Woosh wind") | -15 dB | n |
| sfx3d_boom.wav | 2.45 | cinematic impact with 0.3 s lead-in, bass layer under the hit | kit (Mixkit "Epic movie impact" + "Short bass hit") | -13 dB | n |
| sfx3d_sub_drop.wav | 2.04 | pure sub-bass hit and decay (low-passed at 220 Hz), felt more than heard | kit (impact_boom_v2, see CREDITS) | -14 dB | n |
| sfx3d_riser.wav | 3.20 | smooth noise riser, ends on its peak (put the boom on the last frame) | kit (riser_2, slowed to 80 %) | -17 dB | n |
| sfx3d_shimmer.wav | 2.53 | glassy high bell-grain sparkle with air | synthesised | -20 dB | n |
| sfx3d_tick.wav | 0.21 | tiny clean UI/label tick | kit (Mixkit "Clear mouse clicks", first click) + synthesised body | -22 dB | n |
| sfx3d_pop.wav | 0.19 | soft rounded pop | kit (pop_soft, see CREDITS) | -18 dB | n |
| sfx3d_lift_ding.wav | 2.67 | soft two-tone lift chime (B5 then G5), small lobby reverb | synthesised | -17 dB | n |
| sfx3d_sliding_door.wav | 2.75 | lift/sliding door: latch tick, motor + roller glide, soft rubber thunk | synthesised | -15 dB | n |
| sfx3d_door.wav | 1.65 | wooden door: lever, latch click, seal release, air of the swing, soft stop | synthesised | -13 dB | n |
| sfx3d_glass_slide.wav | 3.19 | balcony sliding door on an aluminium track, glass ring, soft bump into frame | synthesised | -16 dB | n |
| sfx3d_footsteps.wav | 8.00 | calm walk on tile, 14 steps = 105 steps/min, varied level/timing/pan | synthesised | -18 dB | y |
| sfx3d_birds.wav | 30.0 | sparse tropical morning bed: dove, whistles, warbles, chitters, a far tinkerbird-type tapping; 13 calls at mixed distances | synthesised | -20 dB (up to -26 for dialogue scenes) | y |
| sfx3d_city.wav | 30.0 | calm residential neighbourhood: distant traffic hum, 4 far cars, 2 far boda-boda passes | synthesised | -22 dB | y |
| sfx3d_water.wav | 20.0 | gentle pool lapping: overlapping small laps, bubbles and plops | synthesised | -20 dB | y |
| sfx3d_wind.wav | 20.0 | light rooftop breeze with slow gusts | synthesised | -22 dB | y |
| sfx3d_room_tone.wav | 20.0 | quiet apartment interior, low room modes, trace of 50 Hz mains hum | synthesised | -26 dB (just under the dialogue) | y |
| sfx3d_reveal_swell.wav | 2.91 | soft warm pad swell that blooms and falls away | synthesised | -14 dB | n |

Pairing tips: drone exteriors = wind + birds (or city) low under music; lift = sliding_door, then ding, then room_tone;
reveal = riser into boom + sub_drop (sub_drop only where the playback system can use it), or reveal_swell for the gentle option.
Footsteps are a bed: fade in/out per shot, do not leave them running across cuts.

## Verification (verify.py output)
Every file: stereo 48 kHz, no clipped samples, DC below 1e-4, peak/LUFS as stated. Spectrogram + waveform PNG per file
and contact sheets are in check/ (`<type>.png`, `_sheet1-6.png`, `_loop_seams.png`). Loop seams: sample jump at the
join is below the 99th percentile of normal sample-to-sample steps for all six loops.

## Weakest sounds (honest list)
1. birds - synthesised calls are made as natural as additive synthesis allows (varied contours, vibrato, tremolo, distance
   filtering, outdoor reverb) but a synthetic bird can still read as artificial on a good speaker. It is deliberately sparse
   and quiet. If it sounds wrong, drop it 6 dB or use wind/city instead. A real CC BY dawn chorus would be better.
2. boom - Mixkit source has faint tonal "movie impact" partials in the tail; fine under music, slightly synthetic alone.
3. shimmer - clean sine bell grains, a little "glassy"; fine as a short sparkle.
4. door and glass_slide - mechanically plausible, never compared with a real recording; check with headphones first.
5. tick and pop - tiny kit sounds; only a click-sized tick was available.
Tools: tools/ holds the synthesis and build scripts (lib.py, oneshots.py, ambiences.py, nature.py, build.py, verify.py).
Re-run: `cd tools && python3 build.py && python3 verify.py`.
