#!/usr/bin/env python3
"""
Pit lane pieces for Pixar Cars Mini Racers track system.

Pieces:
  1. pit-offramp  — straight segment with pit lane branching off the +Y side
  2. pit-onramp   — mirror (pit lane merges back onto main track from +Y side)
  3. pit-lane     — straight pit lane segment with marked pit stalls

The pit lane is ~2 cars wide (48mm road) and branches off at a gentle angle.
The main +Y wall and pit inner wall share the same position (no gap).
In the taper zone, this shared wall has an opening for cars to cross over.

Uses the same puzzle-piece connectors as the main track system.
"""
from build123d import *
import os, sys

# Import shared connector code
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_all_tracks import (
    ROAD_WIDTH, WALL_THICK, WALL_HEIGHT, BASE_THICK, TOTAL_WIDTH, SEGMENT_LEN,
    KNOB_NECK_W, KNOB_NECK_L, KNOB_HEAD_R, KNOB_OFFSET, KNOB_CLR,
    make_knob, make_socket, add_connectors, BASE_DIR,
)

# ============================================================
# PIT LANE DIMENSIONS
# ============================================================
PIT_ROAD_WIDTH = 48.0       # ~2 cars wide (2 × 22mm + 4mm clearance)
PIT_WALL_THICK = WALL_THICK
PIT_WALL_HEIGHT = WALL_HEIGHT
PIT_TOTAL_WIDTH = PIT_ROAD_WIDTH + 2 * PIT_WALL_THICK  # 54mm

# Offramp geometry: main track straight with a Y-branch
TAPER_LEN = 60.0            # length of the angled transition

# Pit stall markers
STALL_COUNT = 4
STALL_WIDTH = 30.0          # width of each stall along the lane
STALL_DEPTH = 1.0           # engraved depth
STALL_MARK_H = 4.0          # height of the stall divider lines on wall
STALL_MARK_W = 1.5          # width of divider lines

# Derived positions
# Main track: centered on Y=0, spans Y from -TOTAL_WIDTH/2 to +TOTAL_WIDTH/2
# Pit lane branches from the +Y side — shared wall, no gap
MAIN_OUTER_Y = TOTAL_WIDTH / 2          # +33mm (outer edge of main track / shared wall)
MAIN_WALL_Y = (TOTAL_WIDTH - WALL_THICK) / 2  # +31.5mm (center of shared wall)
PIT_INNER_Y = MAIN_OUTER_Y              # +33mm (pit road starts at shared wall outer face)
PIT_OUTER_Y = PIT_INNER_Y + PIT_ROAD_WIDTH + PIT_WALL_THICK  # +84mm
PIT_CENTER_Y = (PIT_INNER_Y + PIT_OUTER_Y) / 2  # +58.5mm
PIT_LANE_WIDTH = PIT_OUTER_Y - PIT_INNER_Y  # 51mm (road + outer wall only)


def _make_pit_ramp_body():
    """Build the offramp/onramp body WITHOUT connectors.

    Layout (top view, +X is travel direction, +Y is pit side):

    +84 ──── pit outer wall ────────────────────
             [pit road surface, 48mm wide]
    +33 ── shared wall ──╱ opening ╲── shared wall ──
             [main road, 60mm]
    -33 ──── main -Y wall ─────────────────────

    The shared wall at Y=30-33 serves as both the main +Y wall and the
    pit inner wall. It has a gap in the taper zone (opening for cars).
    The taper floor fans from the main track edge to full pit width.
    """
    wall_lead = 20.0  # solid wall before taper begins
    taper_start_x = -SEGMENT_LEN / 2 + wall_lead
    taper_end_x = taper_start_x + TAPER_LEN
    pit_straight_len = SEGMENT_LEN / 2 - taper_end_x
    pit_straight_cx = (taper_end_x + SEGMENT_LEN / 2) / 2

    with BuildPart() as p:
        # === MAIN TRACK BASE ===
        with BuildSketch(Plane.XY):
            Rectangle(SEGMENT_LEN, TOTAL_WIDTH)
        extrude(amount=BASE_THICK)

        # === MAIN TRACK -Y WALL (full length, unbroken) ===
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with Locations([(0, -(TOTAL_WIDTH - WALL_THICK) / 2)]):
                Rectangle(SEGMENT_LEN, WALL_THICK)
        extrude(amount=WALL_HEIGHT)

        # === SHARED +Y WALL — before taper opening ===
        wall_before_len = taper_start_x - (-SEGMENT_LEN / 2)
        if wall_before_len > 0:
            with BuildSketch(Plane.XY.offset(BASE_THICK)):
                with Locations([((-SEGMENT_LEN / 2 + taper_start_x) / 2,
                                 MAIN_WALL_Y)]):
                    Rectangle(wall_before_len, WALL_THICK)
            extrude(amount=WALL_HEIGHT)

        # === SHARED +Y WALL — after taper opening ===
        # Same wall position, acts as divider between main track and pit lane
        if pit_straight_len > 0:
            with BuildSketch(Plane.XY.offset(BASE_THICK)):
                with Locations([(pit_straight_cx, MAIN_WALL_Y)]):
                    Rectangle(pit_straight_len, WALL_THICK)
            extrude(amount=WALL_HEIGHT)

        # === TAPER FLOOR ===
        # Triangle fanning from main track edge to full pit width.
        # Inner edge stays at Y=MAIN_OUTER_Y (flush with main base), no gap.
        with BuildSketch(Plane.XY):
            with BuildLine():
                Line((taper_start_x, MAIN_OUTER_Y),
                     (taper_end_x, MAIN_OUTER_Y))
                Line((taper_end_x, MAIN_OUTER_Y),
                     (taper_end_x, PIT_OUTER_Y))
                Line((taper_end_x, PIT_OUTER_Y),
                     (taper_start_x, MAIN_OUTER_Y))
            make_face()
        extrude(amount=BASE_THICK)

        # === PIT LANE BASE (from taper_end_x to +X end) ===
        if pit_straight_len > 0:
            with BuildSketch(Plane.XY):
                with Locations([(pit_straight_cx, PIT_CENTER_Y)]):
                    Rectangle(pit_straight_len, PIT_LANE_WIDTH)
            extrude(amount=BASE_THICK)

        # === TAPER OUTER WALL (angled, from main +Y wall to pit outer wall) ===
        # Starts at the shared wall position, fans out to pit outer wall
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with BuildLine():
                Line((taper_start_x, MAIN_OUTER_Y),
                     (taper_end_x, PIT_OUTER_Y))
                Line((taper_end_x, PIT_OUTER_Y),
                     (taper_end_x, PIT_OUTER_Y - PIT_WALL_THICK))
                Line((taper_end_x, PIT_OUTER_Y - PIT_WALL_THICK),
                     (taper_start_x, MAIN_OUTER_Y - WALL_THICK))
                Line((taper_start_x, MAIN_OUTER_Y - WALL_THICK),
                     (taper_start_x, MAIN_OUTER_Y))
            make_face()
        extrude(amount=PIT_WALL_HEIGHT)

        # === PIT LANE OUTER WALL — straight section ===
        if pit_straight_len > 0:
            with BuildSketch(Plane.XY.offset(BASE_THICK)):
                with Locations([(pit_straight_cx,
                                 PIT_OUTER_Y - PIT_WALL_THICK / 2)]):
                    Rectangle(pit_straight_len, PIT_WALL_THICK)
            extrude(amount=PIT_WALL_HEIGHT)

    result = p.part

    # === PIT STALL MARKERS on outer wall ===
    if pit_straight_len > 0:
        stall_zone_start = taper_end_x + 5
        stall_zone_end = SEGMENT_LEN / 2 - 5
        stall_zone_len = stall_zone_end - stall_zone_start
        stall_spacing = stall_zone_len / STALL_COUNT

        for i in range(STALL_COUNT):
            stall_cx = stall_zone_start + (i + 0.5) * stall_spacing
            marker = Pos(stall_cx,
                         PIT_OUTER_Y - PIT_WALL_THICK - STALL_DEPTH / 2,
                         BASE_THICK + PIT_WALL_HEIGHT / 2) * \
                     Box(STALL_WIDTH - 2, STALL_DEPTH, STALL_MARK_H)
            result = result.cut(marker)

            if i < STALL_COUNT:
                div_x = stall_zone_start + i * stall_spacing
                divider = Pos(div_x,
                              PIT_OUTER_Y - PIT_WALL_THICK - STALL_DEPTH / 2,
                              BASE_THICK + PIT_WALL_HEIGHT / 2) * \
                          Box(STALL_MARK_W, STALL_DEPTH, PIT_WALL_HEIGHT - 1)
                result = result.cut(divider)

    return result


def make_pit_offramp():
    """Offramp: main straight with pit lane branching off +Y side."""
    result = _make_pit_ramp_body()

    # Main track connectors
    result = add_connectors(result, SEGMENT_LEN / 2, 0, 1, 0, 0)
    result = add_connectors(result, -SEGMENT_LEN / 2, 0, -1, 0, 0)
    # Pit lane +X face (exit to pit-lane segment)
    result = add_connectors(result, SEGMENT_LEN / 2, PIT_CENTER_Y, 1, 0, 0)

    return result


def make_pit_onramp():
    """Onramp: mirror of offramp body, with fresh connectors.

    After mirroring across YZ (X→-X), the taper is on the -X side.
    Connectors are added fresh so male/female positions follow the N×Z convention.
    """
    body = _make_pit_ramp_body()
    body = mirror(body, about=Plane.YZ)

    # Main track connectors (same as any straight piece)
    body = add_connectors(body, SEGMENT_LEN / 2, 0, 1, 0, 0)
    body = add_connectors(body, -SEGMENT_LEN / 2, 0, -1, 0, 0)
    # Pit lane -X face (entrance from pit-lane segment)
    body = add_connectors(body, -SEGMENT_LEN / 2, PIT_CENTER_Y, -1, 0, 0)

    return body


def make_pit_lane():
    """Standalone pit lane segment with pit stall markers.
    Same X length as all other pieces (SEGMENT_LEN=150mm).
    Y position matches offramp/onramp pit connectors.
    Has its own inner wall (at shared wall position) and outer wall.
    """
    with BuildPart() as p:
        # Base — spans from shared wall inner face to pit outer wall
        with BuildSketch(Plane.XY):
            with Locations([(0, PIT_CENTER_Y)]):
                Rectangle(SEGMENT_LEN, PIT_LANE_WIDTH)
        extrude(amount=BASE_THICK)

        # Inner wall (same Y position as main track +Y wall on ramp pieces)
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with Locations([(0, PIT_INNER_Y + PIT_WALL_THICK / 2)]):
                Rectangle(SEGMENT_LEN, PIT_WALL_THICK)
        extrude(amount=PIT_WALL_HEIGHT)

        # Outer wall (+Y side — pit stalls go here)
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with Locations([(0, PIT_OUTER_Y - PIT_WALL_THICK / 2)]):
                Rectangle(SEGMENT_LEN, PIT_WALL_THICK)
        extrude(amount=PIT_WALL_HEIGHT)

    result = p.part

    # Pit stall markers on outer wall
    stall_zone_start = -SEGMENT_LEN / 2 + 10
    stall_zone_end = SEGMENT_LEN / 2 - 10
    stall_zone_len = stall_zone_end - stall_zone_start
    stall_count = int(stall_zone_len / (STALL_WIDTH + 5))  # fit as many as we can
    stall_spacing = stall_zone_len / stall_count

    for i in range(stall_count):
        stall_cx = stall_zone_start + (i + 0.5) * stall_spacing
        marker = Pos(stall_cx,
                     PIT_OUTER_Y - PIT_WALL_THICK - STALL_DEPTH / 2,
                     BASE_THICK + PIT_WALL_HEIGHT / 2) * \
                 Box(STALL_WIDTH - 2, STALL_DEPTH, STALL_MARK_H)
        result = result.cut(marker)

        # Divider lines
        div_x = stall_zone_start + i * stall_spacing
        divider = Pos(div_x,
                      PIT_OUTER_Y - PIT_WALL_THICK - STALL_DEPTH / 2,
                      BASE_THICK + PIT_WALL_HEIGHT / 2) * \
                  Box(STALL_MARK_W, STALL_DEPTH, PIT_WALL_HEIGHT - 1)
        result = result.cut(divider)

    # End divider
    div_x = stall_zone_end
    divider = Pos(div_x,
                  PIT_OUTER_Y - PIT_WALL_THICK - STALL_DEPTH / 2,
                  BASE_THICK + PIT_WALL_HEIGHT / 2) * \
              Box(STALL_MARK_W, STALL_DEPTH, PIT_WALL_HEIGHT - 1)
    result = result.cut(divider)

    # Connectors at PIT_CENTER_Y — mates with offramp +X pit and onramp -X pit
    result = add_connectors(result, SEGMENT_LEN / 2, PIT_CENTER_Y, 1, 0, 0)
    result = add_connectors(result, -SEGMENT_LEN / 2, PIT_CENTER_Y, -1, 0, 0)

    return result


def make_pit_lane_dual():
    """Combined main track + pit lane straight with divider wall.

    Layout (top view):
    +84 ──── pit outer wall (full length) ────────
             [pit road surface, 48mm wide]
    +33 ──── shared divider wall (full length) ───
             [main road, 60mm wide]
    -33 ──── main -Y wall (full length) ──────────

    Four connector faces: main ±X and pit ±X.
    Same X length as all other pieces (SEGMENT_LEN=150mm).
    """
    # Full width spans from main -Y wall to pit outer wall
    full_width = TOTAL_WIDTH + PIT_LANE_WIDTH  # 66 + 51 = 117mm
    full_center_y = (-TOTAL_WIDTH / 2 + PIT_OUTER_Y) / 2  # center of the whole piece

    with BuildPart() as p:
        # === MAIN TRACK BASE ===
        with BuildSketch(Plane.XY):
            Rectangle(SEGMENT_LEN, TOTAL_WIDTH)
        extrude(amount=BASE_THICK)

        # === PIT LANE BASE (from shared wall to pit outer wall) ===
        with BuildSketch(Plane.XY):
            with Locations([(0, PIT_CENTER_Y)]):
                Rectangle(SEGMENT_LEN, PIT_LANE_WIDTH)
        extrude(amount=BASE_THICK)

        # === MAIN -Y WALL (full length) ===
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with Locations([(0, -(TOTAL_WIDTH - WALL_THICK) / 2)]):
                Rectangle(SEGMENT_LEN, WALL_THICK)
        extrude(amount=WALL_HEIGHT)

        # === SHARED DIVIDER WALL (full length, between main and pit) ===
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with Locations([(0, MAIN_WALL_Y)]):
                Rectangle(SEGMENT_LEN, WALL_THICK)
        extrude(amount=WALL_HEIGHT)

        # === PIT OUTER WALL (full length) ===
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with Locations([(0, PIT_OUTER_Y - PIT_WALL_THICK / 2)]):
                Rectangle(SEGMENT_LEN, PIT_WALL_THICK)
        extrude(amount=PIT_WALL_HEIGHT)

    result = p.part

    # === PIT STALL MARKERS on outer wall ===
    stall_zone_start = -SEGMENT_LEN / 2 + 10
    stall_zone_end = SEGMENT_LEN / 2 - 10
    stall_zone_len = stall_zone_end - stall_zone_start
    stall_count = int(stall_zone_len / (STALL_WIDTH + 5))
    stall_spacing = stall_zone_len / stall_count

    for i in range(stall_count):
        stall_cx = stall_zone_start + (i + 0.5) * stall_spacing
        marker = Pos(stall_cx,
                     PIT_OUTER_Y - PIT_WALL_THICK - STALL_DEPTH / 2,
                     BASE_THICK + PIT_WALL_HEIGHT / 2) * \
                 Box(STALL_WIDTH - 2, STALL_DEPTH, STALL_MARK_H)
        result = result.cut(marker)

        div_x = stall_zone_start + i * stall_spacing
        divider = Pos(div_x,
                      PIT_OUTER_Y - PIT_WALL_THICK - STALL_DEPTH / 2,
                      BASE_THICK + PIT_WALL_HEIGHT / 2) * \
                  Box(STALL_MARK_W, STALL_DEPTH, PIT_WALL_HEIGHT - 1)
        result = result.cut(divider)

    # End divider
    div_x = stall_zone_end
    divider = Pos(div_x,
                  PIT_OUTER_Y - PIT_WALL_THICK - STALL_DEPTH / 2,
                  BASE_THICK + PIT_WALL_HEIGHT / 2) * \
              Box(STALL_MARK_W, STALL_DEPTH, PIT_WALL_HEIGHT - 1)
    result = result.cut(divider)

    # === CONNECTORS ===
    # Main track ±X
    result = add_connectors(result, SEGMENT_LEN / 2, 0, 1, 0, 0)
    result = add_connectors(result, -SEGMENT_LEN / 2, 0, -1, 0, 0)
    # Pit lane ±X
    result = add_connectors(result, SEGMENT_LEN / 2, PIT_CENTER_Y, 1, 0, 0)
    result = add_connectors(result, -SEGMENT_LEN / 2, PIT_CENTER_Y, -1, 0, 0)

    return result


# ============================================================
# CHECKERED PATTERN (start/finish) — same params as build_startfinish.py
# ============================================================
CHECKER_SQ = 10.0        # square size (10mm × 10mm)
CHECKER_DEPTH = 0.6      # inlay depth (3 layers @ 0.2mm)
CHECKER_ROWS = 3         # rows along travel direction (X)
CHECKER_COLS = 6         # columns across road width (Y) — 6 × 10 = 60mm = ROAD_WIDTH
CHECKER_X_CENTER = 0.0   # centered on the segment

CHECKER_BLOCK_X = CHECKER_ROWS * CHECKER_SQ   # 30mm total in X
CHECKER_BLOCK_Y = CHECKER_COLS * CHECKER_SQ   # 60mm total in Y
CHECKER_X_START = CHECKER_X_CENTER - CHECKER_BLOCK_X / 2
CHECKER_Y_START = -CHECKER_BLOCK_Y / 2  # centered on main road (Y=0)


def make_pit_lane_dual_startfinish():
    """Combined main track + pit lane with start/finish checker on main road.

    Exports THREE STLs that share the same volume (no recess/inlay):
      1. base (white)   — full dual piece with checker squares cut away
      2. checker (black) — full-thickness checker squares (flush road surface)
      3. pit wall (accent) — pit outer wall + stall markers

    The checker squares are full BASE_THICK tall — the slicer swaps filament,
    road surface stays perfectly flat. No physical indentation.
    """
    # --- Build full dual body ---
    with BuildPart() as p:
        # Main track base
        with BuildSketch(Plane.XY):
            Rectangle(SEGMENT_LEN, TOTAL_WIDTH)
        extrude(amount=BASE_THICK)

        # Pit lane base
        with BuildSketch(Plane.XY):
            with Locations([(0, PIT_CENTER_Y)]):
                Rectangle(SEGMENT_LEN, PIT_LANE_WIDTH)
        extrude(amount=BASE_THICK)

        # Main -Y wall
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with Locations([(0, -(TOTAL_WIDTH - WALL_THICK) / 2)]):
                Rectangle(SEGMENT_LEN, WALL_THICK)
        extrude(amount=WALL_HEIGHT)

        # Shared divider wall
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with Locations([(0, MAIN_WALL_Y)]):
                Rectangle(SEGMENT_LEN, WALL_THICK)
        extrude(amount=WALL_HEIGHT)

        # Start/finish markers on main track walls (raised nubs)
        for wall_y in [-(TOTAL_WIDTH / 2 - WALL_THICK / 2), MAIN_WALL_Y]:
            with BuildSketch(Plane.XY.offset(BASE_THICK + WALL_HEIGHT)):
                with Locations([(CHECKER_X_CENTER, wall_y)]):
                    Rectangle(6, WALL_THICK)
            extrude(amount=2.0)

    base_body = p.part

    # --- Cut black checker squares out of the base (full thickness) ---
    for row in range(CHECKER_ROWS):
        for col in range(CHECKER_COLS):
            if (row + col) % 2 == 1:  # black square
                cx = CHECKER_X_START + (row + 0.5) * CHECKER_SQ
                cy = CHECKER_Y_START + (col + 0.5) * CHECKER_SQ
                sq = Pos(cx, cy, BASE_THICK / 2) * \
                     Box(CHECKER_SQ, CHECKER_SQ, BASE_THICK)
                base_body = base_body.cut(sq)

    # Connectors (4 faces)
    base_body = add_connectors(base_body, SEGMENT_LEN / 2, 0, 1, 0, 0)
    base_body = add_connectors(base_body, -SEGMENT_LEN / 2, 0, -1, 0, 0)
    base_body = add_connectors(base_body, SEGMENT_LEN / 2, PIT_CENTER_Y, 1, 0, 0)
    base_body = add_connectors(base_body, -SEGMENT_LEN / 2, PIT_CENTER_Y, -1, 0, 0)

    # --- Checker body (black squares, full base thickness) ---
    black_squares = []
    for row in range(CHECKER_ROWS):
        for col in range(CHECKER_COLS):
            if (row + col) % 2 == 1:
                cx = CHECKER_X_START + (row + 0.5) * CHECKER_SQ
                cy = CHECKER_Y_START + (col + 0.5) * CHECKER_SQ
                sq = Pos(cx, cy, BASE_THICK / 2) * \
                     Box(CHECKER_SQ, CHECKER_SQ, BASE_THICK)
                black_squares.append(sq)

    checker_body = black_squares[0]
    for sq in black_squares[1:]:
        checker_body = checker_body.fuse(sq)

    # --- Pit outer wall (accent color) ---
    with BuildPart() as pw:
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with Locations([(0, PIT_OUTER_Y - PIT_WALL_THICK / 2)]):
                Rectangle(SEGMENT_LEN, PIT_WALL_THICK)
        extrude(amount=PIT_WALL_HEIGHT)
    pit_wall_body = pw.part

    # Stall markers on pit wall
    stall_zone_start = -SEGMENT_LEN / 2 + 10
    stall_zone_end = SEGMENT_LEN / 2 - 10
    stall_zone_len = stall_zone_end - stall_zone_start
    stall_count = int(stall_zone_len / (STALL_WIDTH + 5))
    stall_spacing = stall_zone_len / stall_count

    for i in range(stall_count):
        stall_cx = stall_zone_start + (i + 0.5) * stall_spacing
        marker = Pos(stall_cx,
                     PIT_OUTER_Y - PIT_WALL_THICK - STALL_DEPTH / 2,
                     BASE_THICK + PIT_WALL_HEIGHT / 2) * \
                 Box(STALL_WIDTH - 2, STALL_DEPTH, STALL_MARK_H)
        pit_wall_body = pit_wall_body.cut(marker)

        div_x = stall_zone_start + i * stall_spacing
        divider = Pos(div_x,
                      PIT_OUTER_Y - PIT_WALL_THICK - STALL_DEPTH / 2,
                      BASE_THICK + PIT_WALL_HEIGHT / 2) * \
                  Box(STALL_MARK_W, STALL_DEPTH, PIT_WALL_HEIGHT - 1)
        pit_wall_body = pit_wall_body.cut(divider)

    div_x = stall_zone_end
    divider = Pos(div_x,
                  PIT_OUTER_Y - PIT_WALL_THICK - STALL_DEPTH / 2,
                  BASE_THICK + PIT_WALL_HEIGHT / 2) * \
              Box(STALL_MARK_W, STALL_DEPTH, PIT_WALL_HEIGHT - 1)
    pit_wall_body = pit_wall_body.cut(divider)

    return base_body, checker_body, pit_wall_body


def make_pit_lane_dual_startfinish_3c():
    """Combined main track + pit lane with 3-color start/finish on main road.

    Three STLs — checker colors only in the top layers to minimize purge waste:
      1. body (GREY)  — entire piece, checker zone top cut away
      2. white squares — top COLOR_THICK of (row+col) even squares
      3. black squares — top COLOR_THICK of (row+col) odd squares

    The grey body fills the bottom of the checker zone (below the color layer).
    Color swaps only happen in the top 3 layers instead of all 15.
    """
    # Color layers: 0.6mm = 3 layers @ 0.2mm — minimum for opaque PLA
    COLOR_THICK = 0.6
    color_z_bot = BASE_THICK - COLOR_THICK   # 2.4mm — where color starts
    color_z_mid = color_z_bot + COLOR_THICK / 2  # 2.7mm — center of color slab

    # --- Build full dual body ---
    with BuildPart() as p:
        # Main track base
        with BuildSketch(Plane.XY):
            Rectangle(SEGMENT_LEN, TOTAL_WIDTH)
        extrude(amount=BASE_THICK)

        # Pit lane base
        with BuildSketch(Plane.XY):
            with Locations([(0, PIT_CENTER_Y)]):
                Rectangle(SEGMENT_LEN, PIT_LANE_WIDTH)
        extrude(amount=BASE_THICK)

        # Main -Y wall
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with Locations([(0, -(TOTAL_WIDTH - WALL_THICK) / 2)]):
                Rectangle(SEGMENT_LEN, WALL_THICK)
        extrude(amount=WALL_HEIGHT)

        # Shared divider wall
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with Locations([(0, MAIN_WALL_Y)]):
                Rectangle(SEGMENT_LEN, WALL_THICK)
        extrude(amount=WALL_HEIGHT)

        # Pit outer wall
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with Locations([(0, PIT_OUTER_Y - PIT_WALL_THICK / 2)]):
                Rectangle(SEGMENT_LEN, PIT_WALL_THICK)
        extrude(amount=PIT_WALL_HEIGHT)

        # Start/finish markers on main track walls (raised nubs)
        for wall_y in [-(TOTAL_WIDTH / 2 - WALL_THICK / 2), MAIN_WALL_Y]:
            with BuildSketch(Plane.XY.offset(BASE_THICK + WALL_HEIGHT)):
                with Locations([(CHECKER_X_CENTER, wall_y)]):
                    Rectangle(6, WALL_THICK)
            extrude(amount=2.0)

    body = p.part

    # Stall markers on pit outer wall
    stall_zone_start = -SEGMENT_LEN / 2 + 10
    stall_zone_end = SEGMENT_LEN / 2 - 10
    stall_zone_len = stall_zone_end - stall_zone_start
    stall_count = int(stall_zone_len / (STALL_WIDTH + 5))
    stall_spacing = stall_zone_len / stall_count

    for i in range(stall_count):
        stall_cx = stall_zone_start + (i + 0.5) * stall_spacing
        marker = Pos(stall_cx,
                     PIT_OUTER_Y - PIT_WALL_THICK - STALL_DEPTH / 2,
                     BASE_THICK + PIT_WALL_HEIGHT / 2) * \
                 Box(STALL_WIDTH - 2, STALL_DEPTH, STALL_MARK_H)
        body = body.cut(marker)

        div_x = stall_zone_start + i * stall_spacing
        divider = Pos(div_x,
                      PIT_OUTER_Y - PIT_WALL_THICK - STALL_DEPTH / 2,
                      BASE_THICK + PIT_WALL_HEIGHT / 2) * \
                  Box(STALL_MARK_W, STALL_DEPTH, PIT_WALL_HEIGHT - 1)
        body = body.cut(divider)

    div_x = stall_zone_end
    divider = Pos(div_x,
                  PIT_OUTER_Y - PIT_WALL_THICK - STALL_DEPTH / 2,
                  BASE_THICK + PIT_WALL_HEIGHT / 2) * \
              Box(STALL_MARK_W, STALL_DEPTH, PIT_WALL_HEIGHT - 1)
    body = body.cut(divider)

    # --- Cut only the top COLOR_THICK of each checker square from the grey body ---
    # Grey body keeps the bottom 2.4mm under the checker zone intact
    for row in range(CHECKER_ROWS):
        for col in range(CHECKER_COLS):
            cx = CHECKER_X_START + (row + 0.5) * CHECKER_SQ
            cy = CHECKER_Y_START + (col + 0.5) * CHECKER_SQ
            sq = Pos(cx, cy, color_z_mid) * \
                 Box(CHECKER_SQ, CHECKER_SQ, COLOR_THICK)
            body = body.cut(sq)

    # Connectors on grey body
    body = add_connectors(body, SEGMENT_LEN / 2, 0, 1, 0, 0)
    body = add_connectors(body, -SEGMENT_LEN / 2, 0, -1, 0, 0)
    body = add_connectors(body, SEGMENT_LEN / 2, PIT_CENTER_Y, 1, 0, 0)
    body = add_connectors(body, -SEGMENT_LEN / 2, PIT_CENTER_Y, -1, 0, 0)

    # --- White checker squares (row+col even), top COLOR_THICK only ---
    white_squares = []
    for row in range(CHECKER_ROWS):
        for col in range(CHECKER_COLS):
            if (row + col) % 2 == 0:
                cx = CHECKER_X_START + (row + 0.5) * CHECKER_SQ
                cy = CHECKER_Y_START + (col + 0.5) * CHECKER_SQ
                sq = Pos(cx, cy, color_z_mid) * \
                     Box(CHECKER_SQ, CHECKER_SQ, COLOR_THICK)
                white_squares.append(sq)

    white_body = white_squares[0]
    for sq in white_squares[1:]:
        white_body = white_body.fuse(sq)

    # --- Black checker squares (row+col odd), top COLOR_THICK only ---
    black_squares = []
    for row in range(CHECKER_ROWS):
        for col in range(CHECKER_COLS):
            if (row + col) % 2 == 1:
                cx = CHECKER_X_START + (row + 0.5) * CHECKER_SQ
                cy = CHECKER_Y_START + (col + 0.5) * CHECKER_SQ
                sq = Pos(cx, cy, color_z_mid) * \
                     Box(CHECKER_SQ, CHECKER_SQ, COLOR_THICK)
                black_squares.append(sq)

    black_body = black_squares[0]
    for sq in black_squares[1:]:
        black_body = black_body.fuse(sq)

    return body, white_body, black_body


# ============================================================
# BUILD ALL PIT PIECES
# ============================================================
builders = {
    "track-pit-offramp": make_pit_offramp,
    "track-pit-onramp": make_pit_onramp,
    "track-pit-lane": make_pit_lane,
    "track-pit-lane-dual": make_pit_lane_dual,
}

for name, builder in builders.items():
    print(f"Building {name}...", flush=True)
    out_dir = os.path.join(BASE_DIR, name)
    os.makedirs(out_dir, exist_ok=True)

    shape = builder()
    stl_path = os.path.join(out_dir, f"{name}.stl")
    step_path = os.path.join(out_dir, f"{name}.step")
    export_stl(shape, stl_path)
    export_step(shape, step_path)

    bb = shape.bounding_box()
    dims = (round(bb.max.X - bb.min.X, 1),
            round(bb.max.Y - bb.min.Y, 1),
            round(bb.max.Z - bb.min.Z, 1))
    vol = round(shape.volume, 1)
    mass = round(vol / 1000 * 1.24 * 0.45, 0)
    print(f"  {dims[0]} x {dims[1]} x {dims[2]} mm | ~{mass}g | {stl_path}")

print(f"\nAll {len(builders)} pit pieces built.")

# --- Build the 3-color start/finish dual pit lane ---
print(f"\nBuilding track-pit-startfinish (3-color)...", flush=True)
sf_dir = os.path.join(BASE_DIR, "track-pit-startfinish")
os.makedirs(sf_dir, exist_ok=True)

base_body, checker_body, pit_wall_body = make_pit_lane_dual_startfinish()

parts = {
    "track-pit-startfinish-base": (base_body, "WHITE"),
    "track-pit-startfinish-checker": (checker_body, "BLACK"),
    "track-pit-startfinish-pitwall": (pit_wall_body, "ACCENT"),
}

for pname, (body, color) in parts.items():
    stl_path = os.path.join(sf_dir, f"{pname}.stl")
    step_path = os.path.join(sf_dir, f"{pname}.step")
    export_stl(body, stl_path)
    export_step(body, step_path)
    bb = body.bounding_box()
    dims = (round(bb.max.X - bb.min.X, 1),
            round(bb.max.Y - bb.min.Y, 1),
            round(bb.max.Z - bb.min.Z, 1))
    print(f"  {pname}: {dims[0]} x {dims[1]} x {dims[2]} mm [{color}] | {stl_path}")

print(f"""
Done! 3-color start/finish pit lane.

Bambu Studio instructions:
  1. Import all 3 STLs onto the same plate
  2. Select all → right-click → "Assemble" (locks them together)
  3. Assign filaments:
     - base        → WHITE (AMS slot 1)
     - checker     → BLACK (AMS slot 2)
     - pitwall     → ACCENT color (AMS slot 3, e.g. red/yellow)
  4. Print with AMS — color changes happen every layer through the base

Checker pattern: {CHECKER_ROWS}x{CHECKER_COLS} grid of {CHECKER_SQ}mm squares on main road
Full-thickness color swap — flat road surface, no recess
""")

# --- Build the 3-color (grey/white/black) start/finish dual pit lane as 3MF ---
print(f"\nBuilding track-pit-startfinish-3c (3-color 3MF)...", flush=True)
sf3_dir = os.path.join(BASE_DIR, "track-pit-startfinish-3c")
os.makedirs(sf3_dir, exist_ok=True)

grey_body, white_body, black_body = make_pit_lane_dual_startfinish_3c()

# Export temporary STLs to extract mesh data, then build a single 3MF
import lib3mf
import ctypes
import struct
import tempfile


def stl_to_mesh_data(shape):
    """Export shape to binary STL in memory, parse vertices and triangles."""
    tmp = tempfile.NamedTemporaryFile(suffix=".stl", delete=False)
    tmp.close()
    export_stl(shape, tmp.name)

    with open(tmp.name, "rb") as f:
        header = f.read(80)
        num_tris = struct.unpack("<I", f.read(4))[0]

        vertices = []
        triangles = []
        vert_map = {}

        for _ in range(num_tris):
            data = struct.unpack("<12fH", f.read(50))
            nx, ny, nz = data[0:3]
            for v in range(3):
                vx, vy, vz = data[3 + v * 3: 6 + v * 3]
                key = (round(vx, 6), round(vy, 6), round(vz, 6))
                if key not in vert_map:
                    vert_map[key] = len(vertices)
                    vertices.append(key)
            i0 = vert_map[(round(data[3], 6), round(data[4], 6), round(data[5], 6))]
            i1 = vert_map[(round(data[6], 6), round(data[7], 6), round(data[8], 6))]
            i2 = vert_map[(round(data[9], 6), round(data[10], 6), round(data[11], 6))]
            triangles.append((i0, i1, i2))

    os.unlink(tmp.name)
    return vertices, triangles


def make_color(r, g, b, a=255):
    """Create a lib3mf Color struct."""
    c = lib3mf.Color()
    c.Red = r
    c.Green = g
    c.Blue = b
    c.Alpha = a
    return c


def add_mesh_to_3mf(model, wrapper, name, shape, material_group, material_index):
    """Add a build123d shape as a mesh object to a lib3mf model."""
    vertices, triangles = stl_to_mesh_data(shape)

    mesh = model.AddMeshObject()
    mesh.SetName(name)

    # Convert to lib3mf position/triangle structs (ctypes arrays)
    pos_list = []
    for v in vertices:
        p = lib3mf.Position()
        p.Coordinates = (ctypes.c_float * 3)(v[0], v[1], v[2])
        pos_list.append(p)

    tri_list = []
    for t in triangles:
        tr = lib3mf.Triangle()
        tr.Indices = (ctypes.c_uint * 3)(t[0], t[1], t[2])
        tri_list.append(tr)

    mesh.SetGeometry(pos_list, tri_list)

    # Assign material to entire object
    mesh.SetObjectLevelProperty(
        material_group.GetUniqueResourceID(), material_index)

    # Add as build item (identity transform)
    model.AddBuildItem(mesh, wrapper.GetIdentityTransform())
    return mesh


wrapper = lib3mf.Wrapper()
model = wrapper.CreateModel()
model.SetUnit(lib3mf.ModelUnit.MilliMeter)

# Create material group with 3 colors
mat_group = model.AddBaseMaterialGroup()
grey_idx = mat_group.AddMaterial("Grey", make_color(128, 128, 128))
white_idx = mat_group.AddMaterial("White", make_color(255, 255, 255))
black_idx = mat_group.AddMaterial("Black", make_color(0, 0, 0))

# Add each body as a separate mesh object with its material
add_mesh_to_3mf(model, wrapper, "body", grey_body, mat_group, grey_idx)
add_mesh_to_3mf(model, wrapper, "checker-white", white_body, mat_group, white_idx)
add_mesh_to_3mf(model, wrapper, "checker-black", black_body, mat_group, black_idx)

# Write 3MF
threemf_path = os.path.join(sf3_dir, "track-pit-startfinish-3c.3mf")
writer = model.QueryWriter("3mf")
writer.WriteToFile(threemf_path)

# Print dimensions for each body
for name, body, color in [
    ("body", grey_body, "GREY"),
    ("checker-white", white_body, "WHITE"),
    ("checker-black", black_body, "BLACK"),
]:
    bb = body.bounding_box()
    dims = (round(bb.max.X - bb.min.X, 1),
            round(bb.max.Y - bb.min.Y, 1),
            round(bb.max.Z - bb.min.Z, 1))
    print(f"  {name}: {dims[0]} x {dims[1]} x {dims[2]} mm [{color}]")

print(f"  -> {threemf_path}")
print(f"""
Done! Single 3MF with 3 color-assigned bodies.

Bambu Studio:
  1. Open the 3MF — all 3 bodies load pre-assembled
  2. Colors are pre-assigned: grey body, white + black checker
  3. Map filaments in AMS settings and print

Checker: {CHECKER_ROWS}x{CHECKER_COLS} grid of {CHECKER_SQ}mm squares on main road
Color thickness: 0.6mm (3 layers @ 0.2mm) — opaque, minimal purge waste
Grey base fills the bottom {BASE_THICK - 0.6:.1f}mm under the checker zone
""")

print(f"Pit road width: {PIT_ROAD_WIDTH}mm ({PIT_ROAD_WIDTH/22:.1f} cars)")
print(f"Stall markers: {STALL_COUNT} stalls on offramp, {int((SEGMENT_LEN - 20) / (STALL_WIDTH + 5))} on pit lane")
