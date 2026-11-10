# Prompt for the next chat: Vanta House 3D tour film in Blender

You are taking over a 3D film job for Vanta House, an apartment building under construction on Naguru Vale Road, Naguru, Kampala (developer: Blackstone Real Estate). The owner will attach a reference video. Read all of this before you start.

## The goal

Make one vertical film (1080x1920, 30 fps, about 2 minutes) that walks a viewer through the finished building, at the quality of the attached reference video. That reference was made in Blender and rendered on rented graphics cards from RunPod: soft real light, real shadows and reflections, shallow depth of field, slow confident camera moves. Match that level of finish. Do not copy its subject or its shots; copy its quality.

## What the film must show

A guide (a person) leads the tour and the camera moves with him the whole way:

1. Aerial view of the building, title "Step inside Vanta House."
2. Naguru Vale Road, the main gate opening, the guardhouse, the driveway with parked cars.
3. The lobby and reception, the lift call, the lift ride.
4. A 1-bedroom home: living room, kitchen, bedroom, washroom, balcony.
5. A 2-bedroom home: living room, kitchen, bedroom, balcony.
6. A 3-bedroom home: kitchen and island, dining, living room, corridor, cloakroom, main bedroom with ensuite, bathroom, balcony.
7. The swimming pool deck, with a few people.
8. The roof terrace with pergola and rooftop kitchen.
9. A crane-up over Naguru and the end title: VANTA HOUSE / NAGURU, KAMPALA / Blackstone Real Estate.

Small captions name each place (for example "3 BEDROOMS" above "MAIN BEDROOM"). Sound runs through the whole film: music bed, footsteps under every walk, doors, lift, birds, city, water, wind.

## Rules from the owner (do not break these)

- Build every room as real 3D. Never cut to, paste in, or sample the official 360-degree VR pictures. Use them only to copy the design by eye.
- No "Artist's impression" label and no disclaimer text anywhere in the film.
- All three home types must appear: 1, 2 and 3 bedrooms.
- The guide and other people must move like real people. Use recorded human motion (motion capture), with feet that do not slide. The low-poly game figures in the current version are the main thing the owner dislikes.
- People and vehicles should look reasonably real, not like toys.
- The pool is shown. (An older marketing brief banned pool shots; the owner overruled it for this film.)
- The roof sign reads VANTA HOUSE. It must never read "THE SIGNATURE".
- Nothing invented: the building follows the approved drawings, the interiors follow Vanta's own design. No prices, yields, returns, sales percentages, or words like "on time", "safe", "fully finished", "discount", "cheap", "China Speed". No gym. Do not mention Kololo.
- Magazine reference photos are for looking at only. They never appear in the film.
- Work one step at a time and check each step before moving on. Show the owner stills and one short test shot before any full render.
- Write to the owner in plain, simple English. Say honestly what is weak.

## What already exists (in this repository)

Repository `mightmist/vanta-house`, branch `ccr-f0767bf9-4ky7n6`, folder `edits/vanta_3d_tour/`:

- `v3d/r_scene_tour.html`: the current 124-second tour, written in three.js. It holds the complete shot list, the guide's route, every camera path, the captions and their timings. Treat it as the storyboard to carry into Blender.
- `v3d/r_vanta3d.js`: the exterior model (two towers, facade, balconies, site, gate, pool, roof, surrounding Naguru streets). All dimensions are in the code.
- `v3d/r_interior.js`, `v3d/r_units.js`: lobby, lift, corridors and the three furnished homes, with room sizes and furniture positions.
- `v3d/r_people2.js`, `v3d/r_assets/`: the current low-poly people (CC0, see `v3d/r_CREDITS.md`). Replace these.
- `v3d/r_cues_tour2.json`: the timed sound cue list for the film. `scripts/mix3d2.py`: the script that mixes cues and music to -14 LUFS.
- `v3d/render.js`, `v3d/encode.sh`, `v3d/README.md`: the frame-render harness for the three.js version.
- `refs/drawings/`: the approved drawings (elevation, site plan, typical floor plan, architectural sheet, and the colour plan showing Tower A and Tower B).
- `refs/VANTA_OWN_DESIGN.md`: notes on Vanta's own interior look, room by room.
- `refs/STYLE_GUIDE.md`: the render-quality style guide taken from the owner's reference PDF.
- `v3d/s1_scene.html`, `s2_scene.html`, `s3_scene.html`: three earlier short films (drawing to building, take it apart, the site). Not part of this job.

The three.js film is being rendered as a complete fallback version. It works, but it looks like a game engine: flat light, simple people. That is why the owner wants Blender.

## Source material in the owner's Google Drive

- Official Vanta 360-degree room renders (1-, 2- and 3-bedroom): folder `1N0zTFfBrnWvc3CadFhB8xMqUhaIh-qfj`. Each `vanta_vr_*.jpg` is a cubemap strip of six square faces (four walls, ceiling, floor). Look only.
- Real site footage, including the surrounding streets: folder `1FCTHa6nD2BL9IRqyoKrWDyCnQKG_UJjt`. Clips GV3A9938 to GV3A9949 are a different shoot and are not Vanta House; skip them.

## Facts and readings to keep straight

- Two towers. From the plan, Tower B holds the 1-bedroom homes; Tower A holds the 2-bedroom homes and a 3-bedroom home at the south-east corner. This reading is not confirmed by the owner. Ask if it matters.
- There are no separate unit floor plans. Room layouts were worked out from the typical floor plan and the VR renders.
- Vanta's interior look: light oak plank floor (about #D2AE82), warm white walls (about #E6E2DA), matt black window frames and metalwork, white sheer curtains, cream boucle corner sofa, oval white marble coffee table, white rug with black squares, white flat-panel kitchen with black hob and island, long white dining table with oak round-back chairs under a black track pendant, sand-tile bathrooms with oak vanity and black tap, a walk-through cloakroom with oak shelves and LED strips in the 3-bedroom home.
- Brand colours for titles and captions: bronze-gold, ivory, ink black.
- Construction today is only at about the fifth floor slab. The film shows the finished building.

## How to do it

1. Read the files above and watch the reference video. List what you will build and in what order.
2. Set up Blender. A cloud session with no graphics card cannot render this in reasonable time. Use rented GPUs (the reference used RunPod) or the owner's own computer. The owner must create the account and add credit; ask for the key through a secure credential form, never in chat. Tell the owner the expected cost before spending.
3. Rebuild the scene in Blender from the dimensions in the three.js code and the drawings: exterior, site, three homes, lobby, pool, roof. Use physically based materials, a sun and sky, and interior lights that match the VR renders.
4. Add a realistic rigged guide and a few other people, with motion-capture walking, turning, pressing the lift button, opening doors and waving. Record every asset's licence.
5. Carry over the shot list and camera paths from `r_scene_tour.html`. Fix its known weak spots: the guide's head too close to the camera at the 3-bedroom door and balcony, the camera brushing door frames, and the cloakroom showing mostly wall.
6. Render three stills (exterior, a living room, the pool) and one 10-second shot (lobby walk to the lift). Send them to the owner and wait for a yes.
7. Render the full film, add captions and the sound mix, check every shot, and deliver an H.264 file (yuv420p, faststart) that plays smoothly on a laptop and in Google Drive.

## What to report back

At each stage: what is done, what you checked, what is still weak, and what it has cost so far.
