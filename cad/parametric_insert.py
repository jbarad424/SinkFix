"""
Parametric sink-drainage insert for a porcelain basin.

Sized to measurements from Sink.pdf:
  Basin floor : 420 x 314 mm (flat zone)
  Drain hole  : 70.78 mm diameter, centered
  Overflow    : ~100 mm above floor

Geometry: a thin (3 mm) funnel-shaped shell.
  - Outer rim is a 412 x 306 mm rectangle at z = RIM_HEIGHT
  - Bottom edge is a circular ring around the drain at z = 0
  - Surface slopes smoothly from rim to drain ring
  - Center cutout clears the drain throat + pop-up button + finger
  - Output as full piece + 4 quadrants for printing on a 256 mm bed

Re-run after changing the constants below to regenerate STL/STEP.
"""
import os
import cadquery as cq
from cadquery import Wire, Solid, Vector, Face, Shell

# ---- parameters (mm) ----
BASIN_L          = 420.0   # basin floor long axis
BASIN_W          = 314.0   # basin floor short axis
EDGE_INSET       = 4.0     # gap from basin floor edge (drop-in clearance)
DRAIN_HOLE_D     = 92.0    # center cutout (clears 70.78 drain + pop-up + finger)
DRAIN_RING_OD    = 130.0   # outer dia of the drain-ring base
RIM_HEIGHT       = 50.0    # outer rim height above basin floor
WALL_THICK       = 3.0     # funnel shell thickness

OUTER_L = BASIN_L - 2 * EDGE_INSET   # 412
OUTER_W = BASIN_W - 2 * EDGE_INSET   # 306

OUT_DIR = os.path.join(os.path.dirname(__file__), "v2_parametric")
os.makedirs(OUT_DIR, exist_ok=True)


def make_loft_solid(top_outer_L, top_outer_W, bottom_outer_D, top_z, bottom_z):
    """Loft a closed solid from a circle (bottom) up to a rectangle (top).

    Uses the Workplane .loft(combine=True) which automatically closes the ends.
    """
    hx, hy = top_outer_L / 2, top_outer_W / 2
    return (
        cq.Workplane("XY")
        .workplane(offset=bottom_z)
        .circle(bottom_outer_D / 2)
        .workplane(offset=top_z - bottom_z)
        .polyline([(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)])
        .close()
        .loft(ruled=False, combine=True)
        .val()
    )


# Outer funnel solid (the full "cone" envelope)
outer_solid = make_loft_solid(
    OUTER_L, OUTER_W, DRAIN_RING_OD,
    top_z=RIM_HEIGHT, bottom_z=0,
)

# Inner funnel solid (offset inward by WALL_THICK on each side, and shorter on
# top/bottom so the shell is closed at both ends)
inner_top_L = OUTER_L - 2 * WALL_THICK
inner_top_W = OUTER_W - 2 * WALL_THICK
# Scale the bottom diameter so the inner wall stays ~WALL_THICK away from the outer:
# the rim-to-drain radial run is roughly (OUTER_L/2 - DRAIN_RING_OD/2) ~141 mm,
# the height is RIM_HEIGHT (50 mm). Project WALL_THICK perpendicular to the
# surface slope: shrink the bottom ring by 2*WALL_THICK along the slope axis.
inner_bottom_D = max(DRAIN_RING_OD - 2 * WALL_THICK, DRAIN_HOLE_D + 2)
inner_solid = make_loft_solid(
    inner_top_L, inner_top_W, inner_bottom_D,
    top_z=RIM_HEIGHT + 0.1,   # nudge so top is open
    bottom_z=-0.1,            # nudge so bottom is open
)

# Subtract inner from outer to get a 3mm shell
shell_wp = cq.Workplane("XY").add(outer_solid).cut(inner_solid)

# Drill the drain hole through the bottom of the shell
drain = cq.Workplane("XY").circle(DRAIN_HOLE_D / 2).extrude(RIM_HEIGHT + 5)
shell_wp = shell_wp.cut(drain)

solid = shell_wp.val()
bb = solid.BoundingBox()
vol_cm3 = solid.Volume() / 1000.0
print(f"Full insert bbox: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm")
print(f"Full insert solid volume: {vol_cm3:.1f} cm^3")
print(f"Mass at 100% PETG (1.27 g/cc): {vol_cm3 * 1.27:.0f} g")
print(f"Filament at 20% infill: ~{vol_cm3 * 1.27 * 0.21:.0f} g")

cq.exporters.export(shell_wp, os.path.join(OUT_DIR, "insert_full.step"))
cq.exporters.export(shell_wp, os.path.join(OUT_DIR, "insert_full.stl"),
                    tolerance=0.1, angularTolerance=0.2)

# ---- quarter for consumer-printer beds ----
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
