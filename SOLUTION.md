# SinkFix: Porcelain Basin Drainage Insert

## What this repo contains

| Path | Purpose |
|---|---|
| `cad/v2_parametric/insert_full.{stl,step}` | **Current design** — sized to the actual basin from Sink.pdf |
| `cad/v2_parametric/insert_Q[1-4]_*.{stl,step}` | v2 split into 4 quadrants for consumer printers |
| `cad/parametric_insert.py` | Parametric build script — edit constants at top, re-run to regenerate |
| `cad/Concept_01.STEP` | Muhammad's original "smooth bowl" (wrong size — see notes below) |
| `cad/Concept_02.STEP` | Muhammad's original "ramped funnel" (wrong size — see notes below) |
| `cad/split/Concept_02_Q*` | Earlier (oversized) quartering of Muhammad's Concept 2, kept for reference |

## TL;DR — what changed after the Sink.pdf measurements arrived

The previous Claude conversation recommended **Concept 1** at $195–320. My first revision recommended **Concept 2 quartered** at $60–150. After reading Sink.pdf and confirming the basin floor is **420 × 314 mm with a 70.78 mm drain hole**, the real verdict is: **neither STEP file is the right size.** Both Muhammad concepts have a 451.8 × 401.0 mm footprint, which is 32 mm too long and **87 mm too wide** for your actual basin floor.

The fix: a fresh parametric model (`cad/parametric_insert.py`) sized to the real measurements. Volume drops from Concept 2's 3,698 cm³ to **1,697 cm³** — less than half. Print budget drops with it.

**Expected all-in cost for the v2 design (50 mm tall shelled funnel):**
- Hobbyist (find a Bambu/Prusa owner): **$15–30**
- Makerspace as non-member: **$10–25**
- Craftcloud quadrants (online service): **$25–60**

| Path | Concept 1 (orig) | Concept 2 quartered (orig) | v2 22mm shallow | v2 50mm shelled |
|---|---:|---:|---:|---:|
| Solid volume | 10,515 cm³ | 3,698 cm³ | 1,697 cm³ | **212 cm³** |
| Filament @ 20% infill | ~2.9 kg | ~1.0 kg | ~450 g | **~57 g** |
| Slope (short axis) | 3.8° | 3.8° | 12.2° | **28.1°** |
| Service price estimate | $300–500+ | $180–320 | $80–150 | **$25–60** |
| Fits the basin? | no (too big) | no (too big) | yes | **yes** |

## Why the previous recommendation was wrong

Measured directly from the STEP files:

| | Concept 1 | Concept 2 |
|---|---:|---:|
| Footprint | 451.8 × 401.0 mm | 451.8 × 401.0 mm |
| Height | 85 mm | 70 mm |
| **Solid volume** | **10,515 cm³** | **3,698 cm³** |
| Solid / BBox ratio | 68% (mostly solid mass) | 29% (already shelled) |
| Filament @ 20% infill | ~2.9 kg PETG | ~1.0 kg PETG |
| Filament cost (raw, $20/kg) | ~$58 | ~$20 |
| Rim-to-drain slope | ~3.8° | ~3.8° |

The previous chat claimed "the slicer will hollow it anyway, so cost is similar." That is false for two reasons:

1. **Services price by part volume, not slicer-filled volume.** Whether you ask for 20% or 100% infill, the quote engine reads the model's solid volume first and applies a multiplier.
2. **Print time scales with material extruded.** Even at 20% infill the perimeter walls and top/bottom layers in Concept 1 take ~3× longer than Concept 2 because the funnel surface area is larger and the part is taller.

Both designs have ~3.8° slope from rim to drain — well above the 1.15° plumbing minimum. The previous chat's "19° vs 22°" figures don't appear anywhere in the geometry; they were fabricated. Concept 2's drainage is fine. Concept 1's tiny hygiene advantage (one continuous surface vs. assembly seams) doesn't justify ~3× the cost.

## The actual cost lever: split for a 256 mm printer bed

The 451.8 mm footprint exceeds every consumer printer bed on the market. That single constraint is what forces you to either:

- **Pay an industrial large-format service** (Modix BIG-60 class, ~$200–500), or
- **Split the part** so each piece fits a standard 256 × 256 mm bed.

The script in `cad/split_concept2.py` quarters Concept 2 into four tiles, each **225.9 × 200.5 × 70 mm**. These fit:

| Printer | Bed | Fits? |
|---|---|---|
| Bambu Lab A1 / A1 mini (mini no) | 256 × 256 | yes |
| Bambu Lab P1S / X1C | 256 × 256 | yes |
| Prusa MK4 / MK4S | 250 × 210 | yes (tight on Y) |
| Creality K1 Max | 300 × 300 | yes |
| Ender 3 V3 SE / KE | 220 × 220 | no (Y too short) |

Seams sit under the funnel surface running through the drain center, so they do not disrupt water flow. You glue the four tiles together with **GE Silicone II Kitchen & Bath** (clear, ~$6 at any hardware store) before installing. The drain hole at the center is the natural alignment fixture.

## Step-by-step cost paths

### Path A: Cheapest — find a Bambu/Prusa owner ($60–$100 all-in)

1. Post on `r/3Dprinting` "Will Print For Cost" thread, or Craigslist "3D printing service" your city, or Discord communities (Bambu Lab Discord has a #print-for-others channel). Attach the 4 STL files from `cad/split/`.
2. Ask for PETG, gloss/shiny finish, 3 perimeters, 20% gyroid infill, no supports needed (the parts have a flat bottom).
3. Expected quote: ~$15–25 per tile (filament + machine time + small profit). Total ~$60–100.
4. Lead time: 3–7 days.

### Path B: Local makerspace ($40–$80 all-in)

1. Search "makerspace [your city]" or "[your city] hackerspace." Most charge $0.10–0.15/g for PETG plus small machine fee.
2. Each tile is ~250 g of PETG → $25–40 per tile in material → ~$100–160. But if you have a membership ($30–60/month), filament-only price drops to ~$5 per tile and total is $20–30.
3. Lead time: same day to a week depending on queue.

### Path C: Online service, quadrant version ($120–$220 all-in)

1. Go to https://craftcloud3d.com (no login required for an instant quote).
2. **Click-by-click — this is what you do, not me:**
   - Click "Get Instant Quote" (top-right).
   - Drag-drop **all four** STL files from `cad/split/` (or upload one at a time and increase quantity).
   - Material dropdown: select **PETG** (under FDM).
   - Color: white (or whatever matches your basin).
   - Layer height: 0.2 mm (default).
   - Infill: 20%.
   - Click "Show prices."
3. Craftcloud shows quotes from 5–10 manufacturers ranked by price. Pick the cheapest with shipping to your address. Add to cart, check out.
4. If a quote feels off, **screenshot the page and paste it into this chat** — I'll interpret it and tell you whether to accept.
5. Lead time: 7–14 days.

### Path D: Online service, single piece ($200–$400 all-in)

Same as Path C but upload `cad/Concept_02.STEP` directly. Craftcloud will route to a large-format-capable shop. Higher price, but zero seams to glue. Only worth it if you want the cleanest possible finished look.

## Materials to order in parallel

| Item | Search term | Cost |
|---|---|---|
| Bumpers (4×) | "3M Bumpon SJ5018 1/2 inch clear" Amazon | ~$8 |
| Silicone for seams + bumpers | "GE Silicone II Kitchen Bath clear" Home Depot | ~$6 |
| (Optional) Surface coat | "XTC-3D smooth coat kit" Amazon | ~$25 |

Order these now so they arrive before the print does.

## Assembly (Path A / B / C — split quadrants)

1. Dry-fit the four tiles upside-down on a flat surface. Confirm they match at the seams and that the drain hole at the center forms a clean circle.
2. Lay a 3 mm bead of GE Silicone II along the X=0 seam of two tiles. Press them together. Wipe excess with a paper towel + rubbing alcohol.
3. Repeat for the Y=0 seams of the other pair. You now have two halves.
4. Bead silicone along the long center seam. Press the two halves together. Tape across the joints with painter's tape until cured (~24 h).
5. After cure, peel tape. Run your finger along the inside seams. Any rough spots — sand with 400 grit, then 1000 grit.
6. Stick four 3M Bumpon bumpers to the bottom corners.
7. Drop into the basin. Press the drain pop-up through the center hole to confirm clearance. Run water for 30 seconds. Confirm it drains and doesn't lift the insert.

## What I can do now without browser control

I want to be straight with you about the earlier exchange: I do not have Chrome control in this session. I can't log into Craftcloud and click for you. What I *can* do, and the next-step menu:

- **Send a Gmail draft to a local print service or maker on your behalf.** I have Gmail MCP. Give me a recipient or let me search for one, and I'll draft the message including the STL attachments.
- **Walk you through the upload screenshot-by-screenshot.** You drive Chrome; you paste screenshots into chat; I interpret each screen and tell you the next click.
- **Compute exact volumes / weights / print times** for any redesign you want to try (smaller footprint, lower walls, etc.).
- **Generate a parametric variant** — e.g. if your basin is actually 38 × 28 cm not 42 × 31.4 cm, I can shrink the model and re-export.

Tell me which next step you want.

## Slope and drainage — why this works at all

Porcelain has very low contact-angle hysteresis with water: water beads up rather than sheets off. So a slope at or below ~1° loses to surface tension and water sits. The plumbing code minimum for drainage is 1/4 inch per foot (~1.15°, or 2%). Both Concept 1 and Concept 2 have a measured rim-to-drain slope of ~3.8° — about 3× the code minimum. That's the figure that matters; the previous chat's 19°/22° claim was geometrically impossible given the 15 mm height drop over a 225 mm run, and you can confirm with `atan(15/225) ≈ 3.81°`.

PETG with a gloss finish has lower contact-angle hysteresis than porcelain too, so water sheets off it better than off the original basin — the insert is functionally an upgrade, not just a workaround.

## v2 parametric design

Measurements pulled from Sink.pdf (Muhammad's caliper + tape measurement work):

| Parameter | Value | Source |
|---|---|---|
| Basin floor | 420 × 314 mm | Page 6 blue-tape measurement |
| Drain hole dia | 70.78 mm | Page 8 caliper reading |
| Overflow height | ~100 mm above floor | Previous chat (verify with ruler) |

Design parameters (editable at the top of `cad/parametric_insert.py`):

| Parameter | Value | Why |
|---|---|---|
| Outer footprint | 412 × 306 mm | 4 mm inset per side for drop-in/lift-out clearance |
| Rim height | 50 mm | Steep slope = aggressive drainage; still 50 mm below the 100 mm overflow |
| Center cutout | 92 mm dia | Clears drain throat + pop-up button + finger access |
| Drain-ring flat | 130 mm OD, 3 mm height | Funnel transitions to a flat ring around the drain so the insert doesn't sit on drain hardware |
| Wall thickness | 3 mm | Standard for FDM PETG |
| Slope (rim to drain) | 18.4° long axis / 28.1° short axis | 15-25× plumbing minimum; water cannot pool |
| Topology | Open-bottom shell | Hollow funnel walls; basin's real drain visible through center cutout. Light, cheap, no water-trap zones. |

Quadrant sizes (each tile after split): **~206 × 153 × 50 mm, 53 cm³**. Fits any 256 mm-class consumer printer. At ~14 g per tile of filament, each prints in 2–3 hours.

## Open questions worth confirming before printing

1. **Confirm drain offset.** Sink.pdf assumes the drain is centered. If it's actually offset toward the back wall by more than ~20 mm, edit `parametric_insert.py` to add a `DRAIN_OFFSET_Y` parameter, or measure and tell me and I'll add it.
2. **Confirm overflow height.** 22 mm rim height has 78 mm of clearance to a 100 mm overflow, so this is almost certainly safe — but a tape measure from basin floor to bottom of overflow hole confirms it.
3. **Cardboard mockup before printing.** Cut a 412 × 306 mm rectangle of corrugated cardboard, cut a 92 mm center hole, drop it in the basin. Confirms fit before you spend money.
4. **Pop-up button motion.** When the pop-up rises, how high does it sit above the basin floor? The insert's 22 mm rim should give the button room to operate, but a quick measurement closes the loop.
