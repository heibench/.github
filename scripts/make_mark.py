#!/usr/bin/env python3
"""Generate the heibench mark.

Writes an SVG; stdlib only, no dependencies.

    python3 scripts/make_mark.py assets/heibench-mark.svg

The tracked PNG is rasterised from that SVG:

    rsvg-convert -b white -w 512 -h 512 assets/heibench-mark.svg \\
        -o assets/heibench-mark.png

The frame is derived from the drawn geometry rather than hardcoded, so the
mark stays centred and correctly margined when the shapes are edited.

The SVG has no background of its own, so it composites onto any surface; the
PNG is flattened onto white for use as an avatar.
"""

from pathlib import Path
import sys

JAW_COLOR = "#0b3a75"
WORKPIECE_COLOR = "#8c99a6"

# Fraction of the square frame the artwork spans in its dominant dimension.
FILL = 0.84


def points_to_str(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def mirror_points(points, axis_x):
    return [(2 * axis_x - x, y) for x, y in points]


def square_frame(shapes, fill=FILL):
    """Return a viewBox that centres `shapes` in a square at `fill` coverage."""
    xs = [x for shape in shapes for x, _ in shape]
    ys = [y for shape in shapes for _, y in shape]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    side = max(x1 - x0, y1 - y0) / fill
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return cx - side / 2, cy - side / 2, side


def geometry():
    """Two fixture jaws socketed around a workpiece, concentric on (500, 500).

    The workpiece is a diamond with 45-degree edges. Each jaw's inner face is
    a V-socket on those same 45 degrees, set back so the air gap between jaw
    and workpiece is constant all the way around the grip.
    """
    cx = cy = 500.0
    half = 150.0  # workpiece half-diagonal
    setback = 60.0  # socket apex offset from the workpiece vertex, along x

    workpiece = [(cx, cy - half), (cx + half, cy), (cx, cy + half), (cx - half, cy)]

    apex_x = cx - half - setback
    arm_x = 450.0  # blunt inner face of each arm; sharp tips vanish when small
    arm_y = cy - (arm_x - apex_x)  # where the 45-degree socket edge reaches arm_x
    top, bottom = 250.0, 750.0
    back, chamfer = 160.0, 60.0

    left_jaw = [
        (back + chamfer, top),
        (arm_x, top),
        (arm_x, arm_y),
        (apex_x, cy),
        (arm_x, 2 * cy - arm_y),
        (arm_x, bottom),
        (back + chamfer, bottom),
        (back, bottom - chamfer),
        (back, top + chamfer),
    ]
    right_jaw = mirror_points(left_jaw, cx)

    return [left_jaw, right_jaw], workpiece


def make_svg(out_path="assets/heibench-mark.svg"):
    jaws, workpiece = geometry()
    vx, vy, side = square_frame(jaws + [workpiece])

    jaw_svg = "\n  ".join(
        f'<polygon points="{points_to_str(j)}" fill="{JAW_COLOR}" />' for j in jaws
    )

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="1000"
    height="1000"
    viewBox="{vx:.1f} {vy:.1f} {side:.1f} {side:.1f}"
    version="1.1"
>
  {jaw_svg}

  <polygon points="{points_to_str(workpiece)}" fill="{WORKPIECE_COLOR}" />
</svg>
"""

    Path(out_path).write_text(svg, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "assets/heibench-mark.svg"
    make_svg(out_path=out)
