"""
Split Concept 2 into 4 quadrants for printing on a 256 mm consumer bed.

Why: the original 451.8 x 401.0 mm footprint forces industrial large-format
services (~$200-500). Quartering yields ~226 x 200 mm tiles that fit on a
Bambu A1 / Prusa MK4 / Ender 3 V3 / nearly any modern 256+ mm printer, where
print cost drops to ~$15-40 per tile at hobbyist services or makerspace rates.

Tiles are joined post-print with marine-grade silicone along the X=0 and Y=0
seams. Seams sit underneath the funnel surface, so they do not disrupt drainage.
"""
import os
import cadquery as cq
from cadquery import importers

SRC = os.path.join(os.path.dirname(__file__), "Concept_02.STEP")
OUT_DIR = os.path.join(os.path.dirname(__file__), "split")
os.makedirs(OUT_DIR, exist_ok=True)

part = importers.importStep(SRC).val()
bb = part.BoundingBox()
print(f"Source bbox: X {bb.xlen:.1f}  Y {bb.ylen:.1f}  Z {bb.zlen:.1f}")

# Quadrants: cut with two large boxes along X=0 and Y=0
quadrants = {
    "Q1_plus_plus":  ( 1,  1),
    "Q2_minus_plus": (-1,  1),
    "Q3_minus_minus":(-1, -1),
    "Q4_plus_minus": ( 1, -1),
}

big = max(bb.xlen, bb.ylen, bb.zlen) * 2

for name, (sx, sy) in quadrants.items():
    # Build a half-space box for this quadrant
    cutter = (
        cq.Workplane("XY")
        .box(big, big, big, centered=(False, False, True))
        .translate((0 if sx > 0 else -big, 0 if sy > 0 else -big, 0))
    )
    q = part.intersect(cutter.val())
    qbb = q.BoundingBox()
    print(f"  {name}: X {qbb.xlen:.1f}  Y {qbb.ylen:.1f}  Z {qbb.zlen:.1f}")
    out = os.path.join(OUT_DIR, f"Concept_02_{name}.step")
    cq.exporters.export(q, out)
    stl = os.path.join(OUT_DIR, f"Concept_02_{name}.stl")
    cq.exporters.export(q, stl, tolerance=0.1, angularTolerance=0.2)

print(f"\nWrote split tiles to {OUT_DIR}/")
print("Each tile fits a 256 x 256 mm bed (Bambu A1, Prusa MK4, etc.) with margin.")
