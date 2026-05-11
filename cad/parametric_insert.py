"""
Parametric sink-drainage insert for a porcelain basin.

Sized to measurements from Sink.pdf:
  Basin floor : 420 x 314 mm (flat zone)
  Drain hole  : 70.78 mm diameter, centered
  Overflow    : ~100 mm above floor (must remain unblocked)

Geometry:
  - Sits flat on basin floor (does not ride the sloped walls)
  - Footprint inset 4 mm per side for lift-out clearance
  - Continuous slope from outer rim down to a flat ring around the drain
  - Center cutout clears drain throat + pop-up + finger access
  - Output as 4 quadrants for printing on a 256 mm bed (Bambu A1, Prusa MK4, etc.)

Re-run after changing the constants below to regenerate STL/STEP.
"""
import os
import cadquery as cq

# ---- parameters (mm) ----
BASIN_L          = 420.0   # basin floor long axis
BASIN_W          = 314.0   # basin floor short axis
EDGE_INSET       = 4.0     # gap from basin wall (drop-in/lift-out clearance)
DRAIN_HOLE_D     = 92.0    # center cutout (clears 70.78 drain + pop-up + finger)
RIM_HEIGHT       = 50.0    # outer rim above basin floor (steep slope = aggressive drainage)
DRAIN_RING_H     = 3.0     # flat lip around drain (so insert doesn't sit on drain hardware)
DRAIN_RING_OD    = 130.0   # outer dia of the flat ring before slope begins
WALL_THICK       = 3.0     # FDM wall thickness

OUTER_L = BASIN_L - 2 * EDGE_INSET
OUTER_W = BASIN_W - 2 * EDGE_INSET

OUT_DIR = os.path.join(os.path.dirname(__file__), "v2_parametric")
os.makedirs(OUT_DIR, exist_ok=True)

# ---- build outer body (solid slab, will be shelled to a thin funnel) ----
body = (
    cq.Workplane("XY")
    .rect(OUTER_L, OUTER_W)
    .extrude(RIM_HEIGHT)
    .edges("|Z")
    .fillet(8)
)

# ---- build funnel cavity as a proper loft solid via Workplane chain ----
inner_w = OUTER_L - 2 * WALL_THICK
inner_h = OUTER_W - 2 * WALL_THICK

funnel = (
    cq.Workplane("XY")
    .workplane(offset=DRAIN_RING_H)
    .circle(DRAIN_RING_OD / 2)
    .workplane(offset=(RIM_HEIGHT + 1.0) - DRAIN_RING_H)
    .rect(inner_w, inner_h)
    .loft(ruled=False, combine=True)
)

# ---- subtract cavity, then drill drain hole ----
insert = body.cut(funnel)

# ---- hollow the part: leave WALL_THICK shell, open at the bottom ----
# This turns a 3.5 kg slab into a ~450 g shelled funnel.
bottom_face = insert.faces("<Z").val()
try:
    insert = insert.shell(-WALL_THICK, kind="intersection")
    # shell with negative offset hollows inward; we open the bottom by cutting
    # a slab off the underside.
except Exception:
    # Fallback: subtract an inset version of the body from itself.
    inner_body = (
        cq.Workplane("XY")
        .rect(OUTER_L - 2 * WALL_THICK, OUTER_W - 2 * WALL_THICK)
        .extrude(RIM_HEIGHT - WALL_THICK)
        .edges("|Z")
        .fillet(max(0.1, 8 - WALL_THICK))
    )
    # The inner_body sits on top of a WALL_THICK-thick floor at z=0..WALL_THICK
    inner_body = inner_body.translate((0, 0, WALL_THICK))
    insert = insert.cut(inner_body)

# Open the bottom: remove the floor under the funnel cavity
floor_cutter = (
    cq.Workplane("XY")
    .rect(OUTER_L - 2 * WALL_THICK, OUTER_W - 2 * WALL_THICK)
    .extrude(WALL_THICK + 0.1)
    .edges("|Z")
    .fillet(max(0.1, 6))
)
insert = insert.cut(floor_cutter)

drain = (
    cq.Workplane("XY")
    .circle(DRAIN_HOLE_D / 2)
    .extrude(RIM_HEIGHT + 2)
)
insert = insert.cut(drain)

# ---- export and measure ----
solid = insert.val()
bb = solid.BoundingBox()
vol_cm3 = solid.Volume() / 1000.0
print(f"Full insert bbox: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm")
print(f"Full insert solid volume: {vol_cm3:.1f} cm^3")
print(f"Mass at 100% PETG (1.27 g/cc): {vol_cm3 * 1.27:.0f} g")
print(f"Filament at 20% infill: ~{vol_cm3 * 1.27 * 0.21:.0f} g")

cq.exporters.export(insert, os.path.join(OUT_DIR, "insert_full.step"))
cq.exporters.export(insert, os.path.join(OUT_DIR, "insert_full.stl"),
                    tolerance=0.1, angularTolerance=0.2)

# ---- quarter for consumer printer beds ----
big = 1000.0
quadrants = {
    "Q1_pp":  ( 1,  1),
    "Q2_mp":  (-1,  1),
    "Q3_mm":  (-1, -1),
    "Q4_pm":  ( 1, -1),
}
for name, (sx, sy) in quadrants.items():
    cutter = (
        cq.Workplane("XY")
        .box(big, big, big, centered=(False, False, True))
        .translate((0 if sx > 0 else -big, 0 if sy > 0 else -big, 0))
    )
    q = solid.intersect(cutter.val())
    qbb = q.BoundingBox()
    qvol = q.Volume() / 1000.0
    print(f"  {name}: {qbb.xlen:.1f} x {qbb.ylen:.1f} x {qbb.zlen:.1f}  ({qvol:.0f} cm^3)")
    cq.exporters.export(q, os.path.join(OUT_DIR, f"insert_{name}.step"))
    cq.exporters.export(q, os.path.join(OUT_DIR, f"insert_{name}.stl"),
                        tolerance=0.1, angularTolerance=0.2)

print(f"\nWrote files to {OUT_DIR}/")
