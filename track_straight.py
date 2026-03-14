#!/usr/bin/env python3
"""Straight track segment for Pixar Cars Mini Racers - 3 lanes wide."""
from build123d import *
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "track-straight")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === DIMENSIONS ===
LANE_WIDTH = 30.0        # mm per lane (car ~22mm + clearance)
NUM_LANES = 3
WALL_THICK = 3.0         # outer wall thickness
WALL_HEIGHT = 6.0        # wall height (low for little hands)
BASE_THICK = 3.0         # track base thickness
DIVIDER_WIDTH = 2.0      # lane divider width
DIVIDER_HEIGHT = 2.5     # lane divider height (subtle bump, won't block cars)
SEGMENT_LEN = 150.0      # length of straight segment

# Connector dimensions (tongue and groove)
CONN_DEPTH = 5.0         # how far tongue extends
CONN_HEIGHT = BASE_THICK  # full base thickness
CONN_TAB_WIDTH = 20.0    # width of each connector tab
CONN_TAB_GAP = 10.0      # gap between tabs
CONN_CLEARANCE = 0.3     # clearance for easy fit

# Derived
ROAD_WIDTH = NUM_LANES * LANE_WIDTH + (NUM_LANES - 1) * DIVIDER_WIDTH  # 94mm
TOTAL_WIDTH = ROAD_WIDTH + 2 * WALL_THICK  # 100mm

# === BUILD THE TRACK ===
with BuildPart() as track:
    # Base plate
    with BuildSketch(Plane.XY):
        Rectangle(SEGMENT_LEN, TOTAL_WIDTH)
    extrude(amount=BASE_THICK)

    # Left wall
    with BuildSketch(Plane.XY.offset(BASE_THICK)):
        with Locations([(0, (TOTAL_WIDTH - WALL_THICK) / 2)]):
            Rectangle(SEGMENT_LEN, WALL_THICK)
    extrude(amount=WALL_HEIGHT)

    # Right wall
    with BuildSketch(Plane.XY.offset(BASE_THICK)):
        with Locations([(0, -(TOTAL_WIDTH - WALL_THICK) / 2)]):
            Rectangle(SEGMENT_LEN, WALL_THICK)
    extrude(amount=WALL_HEIGHT)

    # Lane dividers (subtle ridges)
    for i in range(1, NUM_LANES):
        y_pos = -ROAD_WIDTH / 2 + i * LANE_WIDTH + (i - 1) * DIVIDER_WIDTH + DIVIDER_WIDTH / 2
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with Locations([(0, y_pos)]):
                Rectangle(SEGMENT_LEN, DIVIDER_WIDTH)
        extrude(amount=DIVIDER_HEIGHT)

    # === CONNECTORS ===
    # Tongue on +X end (two tabs)
    tab_positions_y = [CONN_TAB_GAP / 2 + CONN_TAB_WIDTH / 2,
                       -(CONN_TAB_GAP / 2 + CONN_TAB_WIDTH / 2)]
    for y_pos in tab_positions_y:
        with BuildSketch(Plane.XY):
            with Locations([(SEGMENT_LEN / 2 + CONN_DEPTH / 2, y_pos)]):
                Rectangle(CONN_DEPTH, CONN_TAB_WIDTH)
        extrude(amount=CONN_HEIGHT)

    # Groove on -X end (cut slots for tabs)
    groove_tab_width = CONN_TAB_WIDTH + 2 * CONN_CLEARANCE
    groove_depth = CONN_DEPTH + CONN_CLEARANCE
    for y_pos in tab_positions_y:
        with BuildSketch(Plane.XY):
            with Locations([(-SEGMENT_LEN / 2 + groove_depth / 2 - CONN_CLEARANCE, y_pos)]):
                Rectangle(groove_depth, groove_tab_width)
        extrude(amount=CONN_HEIGHT, mode=Mode.SUBTRACT)

result = track.part

# Fillet the top edges of walls for comfort
try:
    top_edges = result.edges().filter_by(Axis.X).filter_by(
        lambda e: e.center().Z > BASE_THICK + WALL_HEIGHT - 0.5
    )
    if len(top_edges) > 0:
        result = fillet(top_edges, radius=1.0)
except Exception:
    pass  # Skip fillet if edge selection fails

# Export
stl_path = os.path.join(OUTPUT_DIR, "track-straight.stl")
step_path = os.path.join(OUTPUT_DIR, "track-straight.step")
export_stl(result, stl_path)
export_step(result, step_path)

bb = result.bounding_box()
print(f"Straight track created!")
print(f"  Size: {bb.max.X - bb.min.X:.1f} x {bb.max.Y - bb.min.Y:.1f} x {bb.max.Z - bb.min.Z:.1f} mm")
print(f"  Volume: {result.volume:.1f} mm³")
print(f"  STL: {stl_path}")
print(f"  STEP: {step_path}")
