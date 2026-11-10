# Vanta House 3D style guide (three.js)

Source: reference pack, looked at only. Photos are NOT to be used in any output. Feeling only, never the building shape.
Evidence key: [SEEN] = in downloaded images (see sheet_A..D.jpg). [GAP] = reference page could not be fetched (now only the Architizer penthouse); interiors section 3 is now based on seen images.
Hex values are eyeballed/sampled from JPEGs (which have grading), so treat as +/- 6% ranges, not truth.

## 0. Fetch status
- Worked: Axis (6 imgs), Lydia (6), Herrwood (1, only the og image; the rest of that page were unrelated posts), BP Tower (6, one is a plan), Roma Terrace (6, one is a section), Frauenfeld (5), Tel Aviv duplex (6), Y Duplex (6), Livinspaces Lagos (1 relevant; the second image was an unrelated pool/tower project, kept in B_other_pool/ for water colour only).
- Dezeen (second pass, after static-2026.dezeen.com was allowed): Rust Tel Aviv 7 imgs (floor plan dropped), Konieczny Warsaw 6, living lookbook 6, kitchens 6, bedrooms 6, bathrooms 6. All viewed. Note the lookbook pages mix several projects per page; only some images are relevant (e.g. D_living/06 is an exterior roof, ignore).
- Still blocked: Architizer sculpted penthouse (403); no soft-light penthouse reference from it.
- Frauenfeld gallery gave no pool image in the 5 fetched; pool/water colour comes from B_other_pool/01.jpg and general practice.

## 1. EXTERIOR
**Facade plaster (off-white), sRGB**
- Sunlit face: #EDE9E0 to #F4F1EC (Lydia, warm cream-white; best match). Cooler option #E6E4E0 (Axis).
- Shade face (same wall, not in direct sun): #CAC5BE to #D3CDBF. Keep shade only ~15-20% darker than lit, because sky fill is strong.
- Never pure white: albedo cap ~0.82 (#D2). Let exposure make it read bright. Pure #FFFFFF albedo clips and looks CG.
- Roughness 0.85-0.95, no specular. Add faint vertical streaks (rain, below sills/slab edges) and 1-2% value noise. Lydia and Axis show fine vertical fluting/fins: slab edges and fin rhythm give the "designed" look.
- Contrast materials: dark grey aluminium/steel frames and balustrades #3A3D40 to #5C6264; warm timber soffit/handrail #8A5A35 to #A9703F (Axis rail); one accent of green-grey tile/glass #6E8A7A (Lydia balcony backs).

**Balcony recesses**
- Deep cut-out balconies read as dark-ish but not black: back wall #8F8A84 to #A59F96 in shade, ceiling slab underside #B8B3AB, floor tile #8B8883. The recess is about 2-3 stops below the sunlit wall, with warm bounce from the floor onto the underside (+5% warm).
- Slab edges are thin (150-200 mm fascia) and cast a crisp horizontal shadow band on the wall below, about 1/3 of floor-to-floor height at midday sun, lengthening to 1/2 at 3-4 pm. Axis/Herrwood: the projecting slab edges ARE the architecture; shadow lines carry the facade.
- Interior seen through glazing: sheer curtains, warm light #F2DFC0, 1-2 stops brighter than balcony recess at dusk, dim at day. Do not leave glazing black.

**Glass balustrade**
- Frameless/low-iron glass, slight green-blue edge tint #BFD8D2 at 0.15-0.25 alpha, no mirror reflection of CG env; sky reflection gradient only (top lighter). Thin steel shoe at base (dark grey) and a slim handrail (timber or dark metal) per Axis/Herrwood. Edge-on thickness seen as a green line. Use MeshPhysicalMaterial transmission low (0.6) + roughness 0.05, or plain alpha for performance.
- Alternative seen: vertical flat-bar steel balustrade painted white (Axis) or dark (Axis stair). Pick one family; glass for upper units, white vertical bars for access galleries.

**Ground floor**
- Set back, darker, heavier base: recessed lobby glazing, dark timber or stone-cladded plinth (Lydia: warm stone panel #8C7A62 beside entrance; roller shutters #6F665B), 1-1.5 m taller than upper floors' visual weight. Entrance canopy thin slab. Planter strip in front, mulch/gravel #B9AE9F.
- Pavement: pale concrete/granite pavers #B8B3AB to #CFC9BF, expansion joints every 2.4 m, subtle stains; kerb #9E9A94; asphalt #55565A with lighter wear lines. Street furniture: slim pole lights (Axis), bollards.

**Sun/shadow in strong sun**
- Key light 35-60 deg elevation (Naguru, midday ~70-80 deg high; for photographic look choose 9-10 am or 3-5 pm at 35-45 deg). Shadow edges slightly soft (PCFSoft, radius 2-4 px at 2k), never razor and never mushy. Penumbra grows with distance from caster (use PCSS or VSM if affordable).
- Sky fill dominates shade: ambient/hemisphere sky colour #8FB0E0 over ground bounce #B8A98F. Ratio key:fill about 3:1 outdoors.
- Cast shadows from slabs onto facade must be continuous across whole elevation, giving horizontal banding (Herrwood, Axis).

**Sky/exposure**
- Clear deep blue gradient top #2859A3 to horizon #BCCFEE (Axis photos), few small white cumulus (Axis/Herrwood). Kampala: add faint haze at horizon (#D8DDE3), warm dust. ACESFilmic tone mapping, exposure ~0.9-1.0, sun intensity ~3, env intensity ~0.6. Slight vignette. Chromatic aberration 0.0005 max.
- Dusk variant (Axis/Lydia blue hour): sky #1F3C78 to #D88A5A at horizon; windows lit warm 2700 K #FFD9A0, facade turns #B7B4C4 cool violet. Great for hero shots: interior glow reads through balconies.

**Landscaping (Kampala-plausible)**
- Seen: palms in front of facade (Herrwood: Canary/royal palm clusters), low shrubs and grass verge, mature broadleaf trees to soften street (BP, Frauenfeld), planters on every balcony edge (BP: trailing ferns, asparagus fern, small shrubs).
- Use: royal palms 8-10 m (3-5 in a group), frangipani (flat-topped, sparse leaves), bougainvillea (magenta #C2307A accents, sparingly), croton, ficus/mango canopy trees on the street (dark green #3F5A2E to #5F7A38), cannas, lawn #6F8F3B with lighter dry edges, red-brown murram verge #9A5A3C. Balcony planters: trailing greenery 30-60 cm over edge. Foliage with alpha-tested cards, 2 shades of green plus 10% yellow-green tips; never uniform.

**Street-level camera**
- Heights 1.5-1.7 m (eye) for pedestrian, 1.1 m for low hero, 20-35 m up for an elevated 3/4 view (Axis aerials). Lens 24-28 mm equivalent full frame (vertical FOV ~ 53-62 deg for 24 mm horizontal-fit; in three.js camera.fov ~ 54) with verticals corrected (shift lens, or camera level and crop: do NOT tilt up, to keep verticals parallel as in Axis/Lydia). Worm's-eye views only 17-20 mm for entrance. Detail: 50-85 mm on balcony/fin rhythm (Lydia crops).
- Keep one foreground element (kerb, palm trunk, pole) to anchor depth. Fine film grain 1-2%.

## 2. ROOF / POOL / SHARED
(From Roma Terrace, Frauenfeld exterior/terrace, BP, plus B_other_pool for water.)

**Deck/paving**
- Pale concrete / microcement #B4B2AE (Roma floor) to warm #C9BFB2; timber deck (Tel Aviv terrace: ipe/iroko slats 90-120 mm wide, 6 mm gaps) #755B4A to #8F6A4C, boards varying +/- 5% value. Pool coping honed stone/granite #BFB2A6 to #A8A39B, 40-60 mm drop at edge.
- Long narrow pool: water seen as deep teal-blue; sample from reference pool #1D4057 (dark side/shadow) to bright #2F8FD0 in sun; tile mosaic 25 mm gives subtle grid, lighter near surface #6FB7D6. Use grey-blue interior tile (#738E95) for calmer, more "private" water. Water: low-amplitude normal map, strong Fresnel, sky reflection, caustics only in bright light. No foam.
- Seen in references: pool edges sit flush with paving, a raised stone wall on one side (low wall 450 mm used as seat), thin infinity edge optional.

**Pergola**
- Roma: steel columns 100x100 in black #1E1E20, thin black steel beams, slatted ceiling in dark timber #3C2E24, open sides, one big flat canopy ~3 m high. Frauenfeld: deep flat concrete/white soffit overhang with recessed downlights and dark timber slat screens #4C3A2E.
- Vanta: black powder-coated steel posts 120 mm, 300 mm deep beams, timber slat infill 40x60 at 150 mm pitch casting striped shadow; add outdoor-rated linen curtains #E8E0D0 on one side.

**Furniture**
- Low rounded sofas/lounge chairs in sand fabric #C8B79A, concrete/stone drum side tables #2B2B2B, built-in bench in rendered concrete with cushions, hammock (Roma), fire pit/wood stove (steel, rust #7A4A32), stools in timber, ceramic pots in terracotta #A9623F. Dining: 6-8 seats timber table. Keep layout loose, a few items off-axis.

**Planting**
- Dense, layered, imperfect (Roma): monstera/split-leaf philodendron, agave, aloe, euphorbia, tall columnar cactus, olive/small tree in large pots, trailing plants from pergola. Greens: #3F5A2E, #5F7A38, #8FA24A. Pots in terracotta/concrete. Edge planters 600 mm deep along parapet.
- Parapet: glass + slim steel (Frauenfeld terraces), height 1.1 m.

## 3. INTERIORS
Now based on seen images: D_rust (main match for 1-2 bed units), D_konieczny (small hotel-like unit), D_living, D_kitchens, D_bedrooms, D_baths lookbooks, plus C_ duplexes and D_lagos. Sheets: sheet_D1.jpg (Rust + Konieczny), sheet_D2a.jpg (living + kitchens), sheet_D2b.jpg (bedrooms + baths + Lagos).

### 3.0 MAIN MATCH: Rust Architects, Tel Aviv apartment (D_rust)
Bright, normal-size flat. Treat this as the default look of a Vanta 1-2 bed unit.
- Floor: large-format matt grey porcelain/terrazzo-look tile, about 600x600 with thin pale joints. Lit #B0AFAE to #C3C3C3 (hallway brighter #C3C3C3), in shadow #8F8E8C. Roughness 0.55-0.7, very faint sheen, no mirror reflection. Slight blotchy mottling (2-3% value noise).
- Walls and ceiling: plain white, slightly cool, #E2E2E0 lit, #CECCCA in shade. Ceiling #EDEDEB. Ceiling carries exposed white-painted conduit and a white track with small spot heads (industrial-lite). Skirting hidden/shadow gap.
- Oak joinery: pale-to-mid natural oak veneer with visible cathedral grain. Lit #C19473 to #BD8E61, darker in shade #996B46. Flat veneer, matt (roughness 0.6). Shapes are curved: a rounded-corner column of open shelves with bullnose edges around a pillar, curved shelf fronts at 120-150 mm radius, and a low oak TV unit with 4 drawer fronts and no handles. Not boxy.
- White built-ins: white lacquer flush wardrobes full height (hallway), white open shelving unit around the TV (books, one framed print, plants).
- Kitchen: white flat-panel units, white 100x100 square glazed wall tile (#F2F2F0) with pale grout, white worktop, black pendant (cone shade, matt black #1E1E20, brass or black cord), gas hob, steel fridge-freezer set into oak tower.
- Windows: black thin-frame aluminium sliding door (about 40-50 mm frame, #1E1E20), pocket black-framed window above kitchen counter, venetian/zebra blinds in grey #6E6E70 half-down on side windows. Daylight is the main light. Balcony beyond: small slatted timber folding table + chair, pots, railing.
- Daylight level: very bright and even. Window-side about +1 EV over the room, far wall only about 1 stop below. Shadows soft, no hard sun patch in most frames. Exposure should leave whites #E8E8E6 not clipped. Mid grey tone of floor about 0.5 relative luminance.
- Furniture shapes: round dark-wood dining table (walnut/oak top on black metal legs) with 3-4 thin sage-green chairs #8FA889 with slim black legs; grey deep-seat sofa with loose back cushions #9A9897 (rounded, soft, low); black glass-top coffee table on a wool rug (here a loud red geometric rug #C8341F; use a calmer oatmeal/terracotta rug for Vanta); black desk with ergonomic mesh chair in a nook (side window with zebra blind), warm wood floor #A07E63 in the study nook.
- Props: many house plants (monstera, pothos, rubber plant, small ferns) in grey/black pots on every oak shelf; books in rows and stacks; one big framed travel poster; speaker; black-framed monochrome print; person in frame is fine (dark clothing).
- Hallway: long, narrow white corridor, full-height flush white wardrobe doors on both sides, 2-3 recessed round downlights in a row, tile floor #C3C3C3, a window or arch of colour at the far end (dark green bathroom #51544C visible with a white basin). Vertical edge shadows are soft, wall brightness about #D2D2D2.
- Camera: 1.2-1.4 m, 18-20 mm equiv for living/kitchen from a corner; vertical (portrait) 4:5 for hall and shelf details; keep verticals straight.

### 3.1 Per-room table (all from seen images)

| Room | Floor | Walls | Joinery | Stone / surfaces | Light |
|---|---|---|---|---|---|
| Living | Grey tile #B0AFAE to #C3C3C3 (Rust); or travertine-look #CEC1B1 for upper units (D_living/02) | White #E2E2E0 | Oak #C19473, curved shelf column; white open shelving | Honed stone side table; brushed brass/gold-top table (D_living/01) | Daylight 6000 K + black track spots 3000 K |
| Kitchen | Same tile | White #E2E2E0, white 100 mm square tile splash | Oak veneer tower #BD8E61 + white flat doors; or pale birch ply #C6B09B (D_kitchens/01) | Marble splash/worktop: white with grey and violet veining (#E8E6EC base, #6E6A7A veins) or honed black #2B2B2B; stone island with waterfall edge (D_kitchens/02,03,06) | Black cone pendant over table, 2700-3000 K; daylight from balcony door |
| Bedroom | Chevron/herringbone oak #916744 to #C9A57C (D_konieczny); or grey tile | Warm off-white #EBE2DC, a soft warm plaster tone #D9CCC4 | Dark stained oak/walnut wardrobes #5A3A26 to #7A5237 with tiny round brass knobs; headboard panel in oak/cherry veneer #A8622F (D_bedrooms/04 style) | Stone bed plinth or nightstand optional | Brass wall sconce 2700 K (candle/torch shape) either side of bed; sheer white curtain; daylight soft |
| Bathroom | Stone-look tile #BDB6AA or honed concrete #A5A5A5 | White glazed 100x200 tile #F0F0EE (D_baths/01) or warm lime plaster #D9C3A5 | Oak vanity front #C19473 | Rough-honed grey stone basin and top #CDCAD1 with a carved trough sink; or travertine #BC9B7E vein-cut top with integrated sink (D_baths/05); matt black wall-mounted tap #1E1E20 | Daylight through glass-block/lattice window; 3000 K mirror edge light |
| Hallway | Same tile #C3C3C3 | White flush #D2D2D2 | White full-height doors, or dark walnut panelled with rounded corners (Konieczny hotel-like) | none | 2-3 round recessed spots, 3000 K |
| Duplex stair | Oak treads #B08A5A, black steel #232326 | Board-marked concrete #9A9894 | Black balustrade; or white painted steel balusters with a white plaster cantilever on a stone block (D_living/01) | Concrete / stone | Linear light under rail; daylight |

### 3.2 Small unit like a good hotel room (D_konieczny)
- Compact studio: a bed zone divided from the living by a low walnut unit and a steel-frame open shelf (black rods, walnut boxes). Walnut/dark oak veneer #5A3A26 for tall wardrobe wall with rounded corner, small brass knobs; chevron oak floor #C9A57C (light) to #916744 (shaded).
- Walls warm white #EBE2DC (lit), #D9CCC4 (shade). Soft, a bit pink. Sockets and wall lights visible: brass wall lamp, round cream glass.
- Small kitchen: taupe flat doors #A89484 (matt), exotic stone back-splash with warm veining (#B07A3A, #6F8F7A, #D8C8B0), one slim shelf, white oven. Compact, tidy, 2-3 ceramic objects on the shelf.
- Bed: white/oatmeal linen duvet #F0EBE3, two pillows + one lumbar, a thin throw. Hallway: dark wood corridor with a curved wall and chevron floor, with a pin-spot on the ceiling.
- Take for Vanta: oak wall panels in the entrance hallway (dark walnut #5A3A26 to oak #A8622F), brass sconces, hotel-clean beds.

### 3.3 Living rooms with stone + wood (D_living)
- Cream travertine/limestone walls with pits #D8CFC0 and floor in pale poured resin #E8E6E0. Arched openings, white plaster stair with white balusters, oak pedestal under the table. Rich but calm. Oak #C9A26B pedestal; chair with chrome frame and terracotta leather #B5694A.
- Larger living (D_living/02): travertine floor #CEC1B1, sage plaster wall #8AA27A, rust/burgundy armchair #7B1E2B, wool rug #6F7A5C, dark timber slat screen #3C2E24, long low cream bench. Use selectively for penthouses.
- Large glass sliding door set in oak frame #C9A26B with thin mullions (D_living/05): good model for terrace door.

### 3.4 Kitchens (D_kitchens)
- Pale birch plywood + veined stone splash and floating shelves (D_kitchens/01): cabinet #D9C3A5, stone #E8E6EC with dark grey/violet veins, black tap/hob, matt black outlets. Shelves carry stacked ceramics, small glasses, a kettle.
- Dark mahogany veneer rooms (D_kitchens/02,05): #8A3A1E. Too dark for Vanta units except penthouse feature. Use stone island #7A7068 with waterfall edge.
- Bright option (D_kitchens/06): white walls, tall steel-clad cabinets #B8B2A4, white/burgundy marble island, herringbone floor #8A5A2E glossy, one wooden chair #A9703F. 
- Island: 40 mm stone top, waterfall sides, 3 oak stools (seat 650-700 mm). Props: fruit, herbs, ceramic jug, dish rack with plates.

### 3.5 Bedrooms (D_bedrooms, D_konieczny)
- Bright neutral: bed with white linen #F0EBE3, warm off-white wall #EBE2DC, oak bed head or oak bedside, round alabaster/brass wall lamp, white fresh flowers in a vase, doors in dark wood #412201 (D_bedrooms/03). Light even, 4500-5500 K daylight, 2700 K sconce.
- Wood-panel room (D_bedrooms/01): vertical oak boards #A8622F to #C08A4E on walls and ceiling, grey bedding #5E5663, black arc floor lamp, polished concrete floor #B9B5AE. Strong, warm, good for the penthouse master.
- Colour is allowed in textiles: olive throw #A8B34A, rust faux-fur throw #B0502F, checkered side table. Keep to one accent.
- Window treatment: ceiling-high white sheer curtain, plus heavier fabric curtain #CDBFA9 on the side if needed. Wall around the bed has a headboard panel at 1.3 m wide.
- Camera: from the foot of the bed corner, 1.2 m, 20-24 mm.

### 3.6 Bathrooms (D_baths)
- Look: hotel-like, tactile stone sink. Rough-hewn/honed stone trough sink and countertop on oak vanity (D_baths/01): top #CDCAD1, oak #C19473. Wall-mounted matt-black taps (#1E1E20) with a separate spout, a black steel-frame glass shower screen, white glazed metro tiles 75x150 (#F0F0EE) with fine grout, shower floor in pebble-grey stone #A5A5A5.
- Warm version (D_baths/04,05): lime/clay plaster walls #D9C3A5, travertine counter #BC9B7E with sunk basin, oak-framed mirrors with slim vertical light strip, brass taps #B98F4E, oak sliding door.
- Props: dried grasses in clear vases, rolled towels (oatmeal #D9CDB8), one plant, soap on a stone dish. Light: small high window or lattice block with bright daylight, 3000 K mirror light.

### 3.7 Lagos/African styling (D_lagos)
Warm beige/blush walls #D9C7B5, backlit shelves #E8A63C glow, curvy marble coffee table, cream bouclé armchair #E2D8C8, rust bouclé pouf #C57A22, capiz shell chandelier #F3EBDD, wicker bag, floor-length cream curtain #D8C3A8, patterned light-grey rug #CFC8BC, fresh flower arrangement. A little more colour than Rust. Use as the "local" layer: wicker, woven baskets, kente/mud-cloth cushion, carved stool, terracotta pot.

### 3.8 Camera and light rules for interiors
- Heights 1.2-1.4 m (seated), 1.5 m for hallway; lens 18-24 mm equiv (three.js fov ~ 62-75 vertical) with verticals straight; 35 mm for details; portrait 4:5 for corridor and shelf details.
- Daylight 5500-6500 K from windows; lamps 2700-3000 K. Mixed temperature is normal. Bright, airy.
- Floors: reflect only blurry. Tiles light grey, 600x600, joint 3 mm #D0D0CF.

## 4. PALETTES
Exterior: #F4F1EC #EDE9E0 #D3CDBF #A59F96 #5C6264 #2B2D30 #A9703F #6E8A7A #2859A3 #BCCFEE
Roof/pool: #B4B2AE #C9BFB2 #8F6A4C #1E1E20 #1D4057 #2F8FD0 #6FB7D6 #3F5A2E #A9623F #C8B79A
Interior (Rust-based): #E2E2E0 #B0AFAE #C3C3C3 #C19473 #996B46 #5A3A26 #EBE2DC #CDCAD1 #BC9B7E #1E1E20 #8FA889 #FFD7A8
Accent (use <5% of frame): rust orange #C57A22, terracotta #A9623F, bougainvillea #C2307A, glass-green #6E8A7A.

## 5. TEN RULES: PHOTOGRAPHED, NOT RENDERED
1. Albedo never pure white or pure black: walls max #EDE9E0 (albedo ~0.85), darkest ~#1E1E20. Brightness comes from exposure, not material.
2. One dominant light plus a big soft fill. Outdoors: sun + sky hemisphere. Indoors: window daylight as key. Lamps are accents, not a flat grid.
3. Uneven light: windows blow slightly toward white, back of room 2-3 stops down; light falls off across floor (Tel Aviv sun patch). Add subtle gradient on walls.
4. Soft contact shadows everywhere: SSAO/AO radius ~0.3 m under furniture, where wall meets floor, under balcony slabs, and under pots. Floating furniture is the #1 CG tell.
5. Real-scale props with imperfection: cushions dented, throw slightly off, books at angle, a plant with uneven leaves, chairs not squared. 3-5 small props per vignette, none symmetric.
6. Slight wear: rain streaks under sills, a darker line on paving where cars pass, scuffed skirting, tile grout lines, board-marked concrete variation, timber grain direction varying board to board.
7. Restrained saturation: facade and interiors desaturated (neutral warm/cool greys), only sky blue, foliage green, pool teal and one accent per scene saturate. Keep global saturation ~0.9.
8. Materials have roughness variation: noise on roughness (0.4-0.7 floors), polished concrete reflects windows softly (blurred), glass has reflection gradient and slight dirt at edges.
9. Camera discipline: photographer lenses (24-28 mm exteriors, 18-24 interiors), verticals straight, eye-level camera, rule-of-thirds, a foreground anchor; slight DOF in interior detail, deep focus in architectural wide.
10. Post as a camera would: ACES filmic, gentle bloom on windows (strength 0.15), 1-2% film grain, tiny vignette, no oversharpening; a small lens-halo from sun for exteriors; colour grade: lifted blacks (#16171A), slightly warm highlights.

## 6. What to avoid
Copying any reference building's massing, window pattern or plan; any pixels from the photos; neon-saturated greens; empty sterile rooms; uniform tiling textures (use 2 offset layers).
