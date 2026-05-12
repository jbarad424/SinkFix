"""Render the insert STL to preview PNGs using pyvista (offscreen VTK)."""
import os
import subprocess
import time
import pyvista as pv

# Start a virtual X server so VTK's OpenGL renderer has somewhere to draw.
if not os.environ.get("DISPLAY"):
    subprocess.Popen(
        ["Xvfb", ":99", "-screen", "0", "1280x960x24"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    os.environ["DISPLAY"] = ":99"
    time.sleep(1.5)

pv.OFF_SCREEN = True
pv.global_theme.window_size = [1280, 960]
pv.global_theme.background = "white"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "renders")
os.makedirs(OUT, exist_ok=True)


def render(stl_path, out_path, camera_position, title):
    mesh = pv.read(stl_path)
    pl = pv.Plotter(off_screen=True)
    pl.add_mesh(
        mesh,
        color="#90a4ae",
        smooth_shading=True,
        show_edges=True,
        edge_color="#37474f",
        line_width=0.4,
        ambient=0.25,
        diffuse=0.85,
        specular=0.3,
        specular_power=15,
    )
    pl.add_axes(line_width=4)
    pl.add_text(title, font_size=12, color="#222222")
    pl.camera_position = camera_position
    pl.show(screenshot=out_path)
    print(f"  wrote {out_path}")


full = os.path.join(HERE, "v2_parametric", "insert_full.stl")

views = [
    ("iso.png",       "Isometric (3/4 view)",         "iso"),
    ("top.png",       "Top-down (water-side)",        "xy"),
    ("underside.png", "Underside (open shell)",        [(0, 0, -800), (0, 0, 0), (0, 1, 0)]),
    ("side_long.png", "Side view (long axis cutaway)", "xz"),
    ("side_short.png","Side view (short axis cutaway)","yz"),
    ("oblique.png",   "Oblique (low angle)",
        [(450, -400, 80), (0, 0, 25), (0, 0, 1)]),
]
for filename, title, cam in views:
    render(full, os.path.join(OUT, filename), cam, title)

# Also render the four quadrants in their print-bed positions, separated
plotter = pv.Plotter(off_screen=True)
GAP = 30
quadrants = [
    ("Q1_pp", ( 1,  1)),
    ("Q2_mp", (-1,  1)),
    ("Q3_mm", (-1, -1)),
    ("Q4_pm", ( 1, -1)),
]
for name, (sx, sy) in quadrants:
    m = pv.read(os.path.join(HERE, "v2_parametric", f"insert_{name}.stl"))
    m = m.translate((GAP * sx, GAP * sy, 0), inplace=False)
    plotter.add_mesh(
        m,
        color="#90a4ae",
        smooth_shading=True,
        show_edges=True,
        edge_color="#37474f",
        line_width=0.4,
        ambient=0.25,
        diffuse=0.85,
    )
plotter.camera_position = "iso"
plotter.add_text("Four quadrants (exploded view)", font_size=12, color="#222222")
plotter.add_axes(line_width=4)
plotter.show(screenshot=os.path.join(OUT, "quadrants_exploded.png"))
print(f"  wrote {os.path.join(OUT, 'quadrants_exploded.png')}")
