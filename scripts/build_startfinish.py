#!/usr/bin/env python3
"""
Start/finish line straight track — two-color (black + white PLA).

Exports TWO STLs that occupy the same space:
  1. track-startfinish-base.stl  — the track body (assign WHITE in Bambu Studio)
  2. track-startfinish-checker.stl — checkered inlay (assign BLACK in Bambu Studio)

Load both into Bambu Studio on the same plate at the same position.
Right-click each → Set filament color.

The checker pattern is inlaid 0.6mm into the road surface (3 layers @ 0.2mm)
for a razor-sharp color boundary.
"""
from build123d import *
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_all_tracks import (
    ROAD_WIDTH, WALL_THICK, WALL_HEIGHT, BASE_THICK, TOTAL_WIDTH, SEGMENT_LEN,
    add_connectors, BASE_DIR,
)

OUT_DIR = os.path.join(BASE_DIR, "track-startfinish")
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# CHECKERED PATTERN DIMENSIONS
# ============================================================
CHECKER_SQ = 10.0        # square size (10mm × 10mm)
CHECKER_DEPTH = 0.6      # inlay depth (3 layers @ 0.2mm)
CHECKER_ROWS = 3         # rows along travel direction (X)
CHECKER_COLS = 6         # columns across road width (Y) — 6 × 10 = 60mm = ROAD_WIDTH
CHECKER_X_CENTER = 0.0   # centered on the segment

# Derived
CHECKER_BLOCK_X = CHECKER_ROWS * CHECKER_SQ   # 30mm total in X
CHECKER_BLOCK_Y = CHECKER_COLS * CHECKER_SQ   # 60mm total in Y
CHECKER_X_START = CHECKER_X_CENTER - CHECKER_BLOCK_X / 2
CHECKER_Y_START = -CHECKER_BLOCK_Y / 2  # centered on road

# ============================================================
# BASE TRACK (white) — with checkered recesses
# ============================================================
print("Building start/finish base (white)...", flush=True)

with BuildPart() as p:
    # Standard straight base
    with BuildSketch(Plane.XY):
        Rectangle(SEGMENT_LEN, TOTAL_WIDTH)
    extrude(amount=BASE_THICK)

    # Walls
    for sign in [1, -1]:
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with Locations([(0, sign * (TOTAL_WIDTH - WALL_THICK) / 2)]):
                Rectangle(SEGMENT_LEN, WALL_THICK)
        extrude(amount=WALL_HEIGHT)

    # Start/finish line side markers — raised bumps on top of each wall
    # Two small triangular "flags" on each wall to mark the line
    for sign in [1, -1]:
        wall_y = sign * (TOTAL_WIDTH / 2 - WALL_THICK / 2)
        with BuildSketch(Plane.XY.offset(BASE_THICK + WALL_HEIGHT)):
            with Locations([(CHECKER_X_CENTER, wall_y)]):
                Rectangle(6, WALL_THICK)
        extrude(amount=2.0)  # small raised nub

base_body = p.part

# Cut the ENTIRE checker grid zone as a recess, then we'll fill
# alternate squares with the checker piece
full_recess = Pos(CHECKER_X_CENTER, 0, BASE_THICK - CHECKER_DEPTH / 2) * \
              Box(CHECKER_BLOCK_X, CHECKER_BLOCK_Y, CHECKER_DEPTH)
base_body = base_body.cut(full_recess)

# Now fill the WHITE squares back in (checkerboard: white where (row+col) is even)
white_squares = []
for row in range(CHECKER_ROWS):
    for col in range(CHECKER_COLS):
        if (row + col) % 2 == 0:  # white square
            cx = CHECKER_X_START + (row + 0.5) * CHECKER_SQ
            cy = CHECKER_Y_START + (col + 0.5) * CHECKER_SQ
            sq = Pos(cx, cy, BASE_THICK - CHECKER_DEPTH / 2) * \
                 Box(CHECKER_SQ, CHECKER_SQ, CHECKER_DEPTH)
            white_squares.append(sq)

for sq in white_squares:
    base_body = base_body.fuse(sq)

# Add puzzle connectors
base_body = add_connectors(base_body, SEGMENT_LEN / 2, 0, 1, 0, 0)
base_body = add_connectors(base_body, -SEGMENT_LEN / 2, 0, -1, 0, 0)

# Export base
base_stl = os.path.join(OUT_DIR, "track-startfinish-base.stl")
base_step = os.path.join(OUT_DIR, "track-startfinish-base.step")
export_stl(base_body, base_stl)
export_step(base_body, base_step)

bb = base_body.bounding_box()
dims = (round(bb.max.X - bb.min.X, 1), round(bb.max.Y - bb.min.Y, 1), round(bb.max.Z - bb.min.Z, 1))
print(f"  Base: {dims[0]} x {dims[1]} x {dims[2]} mm | {base_stl}")

# ============================================================
# CHECKER INLAY (black) — fills the alternating squares
# ============================================================
print("Building start/finish checker inlay (black)...", flush=True)

black_squares = []
for row in range(CHECKER_ROWS):
    for col in range(CHECKER_COLS):
        if (row + col) % 2 == 1:  # black square
            cx = CHECKER_X_START + (row + 0.5) * CHECKER_SQ
            cy = CHECKER_Y_START + (col + 0.5) * CHECKER_SQ
            sq = Pos(cx, cy, BASE_THICK - CHECKER_DEPTH / 2) * \
                 Box(CHECKER_SQ, CHECKER_SQ, CHECKER_DEPTH)
            black_squares.append(sq)

# Fuse all black squares into one solid
checker_body = black_squares[0]
for sq in black_squares[1:]:
    checker_body = checker_body.fuse(sq)

checker_stl = os.path.join(OUT_DIR, "track-startfinish-checker.stl")
checker_step = os.path.join(OUT_DIR, "track-startfinish-checker.step")
export_stl(checker_body, checker_stl)
export_step(checker_body, checker_step)

bb = checker_body.bounding_box()
dims = (round(bb.max.X - bb.min.X, 1), round(bb.max.Y - bb.min.Y, 1), round(bb.max.Z - bb.min.Z, 1))
print(f"  Checker: {dims[0]} x {dims[1]} x {dims[2]} mm | {checker_stl}")

print(f"""
Done! Two-color start/finish line.

Bambu Studio instructions:
  1. Import both STLs onto the same plate
  2. Select both → right-click → "Assemble" (locks them together)
  3. Click the base body → assign WHITE filament
  4. Click the checker body → assign BLACK filament
  5. Print with AMS — color change happens at layer {CHECKER_DEPTH/0.2:.0f}

Checker pattern: {CHECKER_ROWS}×{CHECKER_COLS} grid of {CHECKER_SQ}mm squares
Inlay depth: {CHECKER_DEPTH}mm ({CHECKER_DEPTH/0.2:.0f} layers @ 0.2mm)
""")
