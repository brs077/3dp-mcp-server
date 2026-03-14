#!/usr/bin/env python3
"""Bridge/ramp track segments for Pixar Cars Mini Racers - 3 lanes wide.
Creates 3 pieces: ramp-up, bridge-deck, ramp-down.
Ramps are hollow underneath with support ribs for efficient printing."""
from build123d import *
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === DIMENSIONS (must match straight segment) ===
LANE_WIDTH = 30.0
NUM_LANES = 3
WALL_THICK = 3.0
WALL_HEIGHT = 6.0
BASE_THICK = 3.0
DIVIDER_WIDTH = 2.0
DIVIDER_HEIGHT = 2.5
ROAD_WIDTH = NUM_LANES * LANE_WIDTH + (NUM_LANES - 1) * DIVIDER_WIDTH
TOTAL_WIDTH = ROAD_WIDTH + 2 * WALL_THICK  # 100mm

# Connector
CONN_DEPTH = 5.0
CONN_HEIGHT = BASE_THICK
CONN_TAB_WIDTH = 20.0
CONN_TAB_GAP = 10.0
CONN_CLEARANCE = 0.3

# Ramp parameters
RAMP_LENGTH = 150.0
BRIDGE_HEIGHT = 40.0      # clearance for a straight to pass underneath
RAMP_WALL_HEIGHT = 10.0   # taller walls on ramp for safety
BRIDGE_DECK_LEN = 150.0
SHELL_THICK = 3.0         # thickness of ramp surface shell
RIB_THICK = 3.0           # support rib thickness
NUM_RIBS = 3              # number of cross ribs under ramp

tab_positions_y = [CONN_TAB_GAP / 2 + CONN_TAB_WIDTH / 2,
                   -(CONN_TAB_GAP / 2 + CONN_TAB_WIDTH / 2)]


def make_ramp_up():
    """Ramp from ground level up to BRIDGE_HEIGHT. Hollow underneath with ribs."""
    with BuildPart() as ramp:
        # Outer ramp solid (full wedge)
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Line((-RAMP_LENGTH/2, 0), (RAMP_LENGTH/2, 0))
                Line((RAMP_LENGTH/2, 0), (RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK))
                Line((RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK), (-RAMP_LENGTH/2, BASE_THICK))
                Line((-RAMP_LENGTH/2, BASE_THICK), (-RAMP_LENGTH/2, 0))
            make_face()
        extrude(amount=TOTAL_WIDTH / 2, both=True)

        # Hollow out the interior (smaller wedge cutout)
        # Leave shell on bottom, top surface, and front/back walls
        with BuildSketch(Plane.XZ):
            with BuildLine():
                # Inner cutout - offset inward by SHELL_THICK
                x_start = -RAMP_LENGTH/2 + SHELL_THICK
                x_end = RAMP_LENGTH/2 - SHELL_THICK
                # Bottom of cutout at SHELL_THICK
                z_start_bottom = SHELL_THICK
                # Top surface follows ramp slope minus shell thickness
                # Slope: rises BRIDGE_HEIGHT over RAMP_LENGTH
                slope = BRIDGE_HEIGHT / RAMP_LENGTH
                z_start_top = BASE_THICK + slope * (x_start + RAMP_LENGTH/2) - 0.01  # just below surface
                z_end_top = BRIDGE_HEIGHT + BASE_THICK - SHELL_THICK - slope * SHELL_THICK
                z_end_bottom = SHELL_THICK

                # Simple rectangular cutout that follows the slope
                Line((x_start, z_start_bottom), (x_end, z_end_bottom))
                Line((x_end, z_end_bottom), (x_end, z_end_top))
                Line((x_end, z_end_top), (x_start, z_start_bottom + SHELL_THICK))
                Line((x_start, z_start_bottom + SHELL_THICK), (x_start, z_start_bottom))
            make_face()
        extrude(amount=(TOTAL_WIDTH - 2 * SHELL_THICK) / 2, both=True, mode=Mode.SUBTRACT)

        # Support ribs underneath (cross-ribs perpendicular to travel direction)
        for i in range(1, NUM_RIBS + 1):
            x_pos = -RAMP_LENGTH/2 + i * (RAMP_LENGTH / (NUM_RIBS + 1))
            z_at_x = slope * (x_pos + RAMP_LENGTH/2)
            with BuildSketch(Plane.YZ.offset(x_pos)):
                with BuildLine():
                    hw = (TOTAL_WIDTH - 2 * SHELL_THICK) / 2
                    Line((-hw, SHELL_THICK), (hw, SHELL_THICK))
                    Line((hw, SHELL_THICK), (hw, z_at_x + BASE_THICK - SHELL_THICK))
                    Line((hw, z_at_x + BASE_THICK - SHELL_THICK), (-hw, z_at_x + BASE_THICK - SHELL_THICK))
                    Line((-hw, z_at_x + BASE_THICK - SHELL_THICK), (-hw, SHELL_THICK))
                make_face()
            extrude(amount=RIB_THICK / 2, both=True)

        # Side walls (on top of ramp surface)
        with BuildSketch(Plane.XZ.offset(TOTAL_WIDTH / 2 - WALL_THICK / 2)):
            with BuildLine():
                p1 = (-RAMP_LENGTH/2, BASE_THICK)
                p2 = (RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK)
                p3 = (RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK + RAMP_WALL_HEIGHT)
                p4 = (-RAMP_LENGTH/2, BASE_THICK + WALL_HEIGHT)
                Line(p1, p2)
                Line(p2, p3)
                Line(p3, p4)
                Line(p4, p1)
            make_face()
        extrude(amount=WALL_THICK / 2, both=True)

        with BuildSketch(Plane.XZ.offset(-(TOTAL_WIDTH / 2 - WALL_THICK / 2))):
            with BuildLine():
                Line((-RAMP_LENGTH/2, BASE_THICK), (RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK))
                Line((RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK), (RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK + RAMP_WALL_HEIGHT))
                Line((RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK + RAMP_WALL_HEIGHT), (-RAMP_LENGTH/2, BASE_THICK + WALL_HEIGHT))
                Line((-RAMP_LENGTH/2, BASE_THICK + WALL_HEIGHT), (-RAMP_LENGTH/2, BASE_THICK))
            make_face()
        extrude(amount=WALL_THICK / 2, both=True)

        # Lane dividers on ramp surface
        for i in range(1, NUM_LANES):
            y_pos = -ROAD_WIDTH / 2 + i * LANE_WIDTH + (i - 1) * DIVIDER_WIDTH + DIVIDER_WIDTH / 2
            with BuildSketch(Plane.XZ.offset(y_pos)):
                with BuildLine():
                    Line((-RAMP_LENGTH/2, BASE_THICK), (RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK))
                    Line((RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK), (RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK + DIVIDER_HEIGHT))
                    Line((RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK + DIVIDER_HEIGHT), (-RAMP_LENGTH/2, BASE_THICK + DIVIDER_HEIGHT))
                    Line((-RAMP_LENGTH/2, BASE_THICK + DIVIDER_HEIGHT), (-RAMP_LENGTH/2, BASE_THICK))
                make_face()
            extrude(amount=DIVIDER_WIDTH / 2, both=True)

        # Bottom-end tongue connector (ground level, -X end)
        for y_pos in tab_positions_y:
            with BuildSketch(Plane.XY):
                with Locations([(-RAMP_LENGTH/2 - CONN_DEPTH/2, y_pos)]):
                    Rectangle(CONN_DEPTH, CONN_TAB_WIDTH)
            extrude(amount=CONN_HEIGHT)

        # Top-end groove connector (+X end, at bridge height)
        groove_tab_width = CONN_TAB_WIDTH + 2 * CONN_CLEARANCE
        groove_depth = CONN_DEPTH + CONN_CLEARANCE
        for y_pos in tab_positions_y:
            with BuildSketch(Plane.XY.offset(BRIDGE_HEIGHT)):
                with Locations([(RAMP_LENGTH/2 - groove_depth/2 + CONN_CLEARANCE, y_pos)]):
                    Rectangle(groove_depth, groove_tab_width)
            extrude(amount=CONN_HEIGHT, mode=Mode.SUBTRACT)

    return ramp.part


def make_bridge_deck():
    """Flat elevated bridge deck with support pillars."""
    with BuildPart() as bridge:
        # Main deck
        with BuildSketch(Plane.XY.offset(BRIDGE_HEIGHT)):
            Rectangle(BRIDGE_DECK_LEN, TOTAL_WIDTH)
        extrude(amount=BASE_THICK)

        # Support pillars (hollow columns for less material)
        pillar_outer = 15.0
        pillar_inner = 9.0
        for x_pos in [-BRIDGE_DECK_LEN/3, BRIDGE_DECK_LEN/3]:
            with BuildSketch(Plane.XY):
                with Locations([(x_pos, TOTAL_WIDTH/4), (x_pos, -TOTAL_WIDTH/4)]):
                    Rectangle(pillar_outer, pillar_outer)
            extrude(amount=BRIDGE_HEIGHT)
            # Hollow out pillars
            with BuildSketch(Plane.XY):
                with Locations([(x_pos, TOTAL_WIDTH/4), (x_pos, -TOTAL_WIDTH/4)]):
                    Rectangle(pillar_inner, pillar_inner)
            extrude(amount=BRIDGE_HEIGHT - SHELL_THICK, mode=Mode.SUBTRACT)

        # Walls on deck
        with BuildSketch(Plane.XY.offset(BRIDGE_HEIGHT + BASE_THICK)):
            with Locations([(0, (TOTAL_WIDTH - WALL_THICK) / 2)]):
                Rectangle(BRIDGE_DECK_LEN, WALL_THICK)
        extrude(amount=RAMP_WALL_HEIGHT)

        with BuildSketch(Plane.XY.offset(BRIDGE_HEIGHT + BASE_THICK)):
            with Locations([(0, -(TOTAL_WIDTH - WALL_THICK) / 2)]):
                Rectangle(BRIDGE_DECK_LEN, WALL_THICK)
        extrude(amount=RAMP_WALL_HEIGHT)

        # Lane dividers on deck
        for i in range(1, NUM_LANES):
            y_pos = -ROAD_WIDTH / 2 + i * LANE_WIDTH + (i - 1) * DIVIDER_WIDTH + DIVIDER_WIDTH / 2
            with BuildSketch(Plane.XY.offset(BRIDGE_HEIGHT + BASE_THICK)):
                with Locations([(0, y_pos)]):
                    Rectangle(BRIDGE_DECK_LEN, DIVIDER_WIDTH)
            extrude(amount=DIVIDER_HEIGHT)

        # Tongue on +X end
        for y_pos in tab_positions_y:
            with BuildSketch(Plane.XY.offset(BRIDGE_HEIGHT)):
                with Locations([(BRIDGE_DECK_LEN/2 + CONN_DEPTH/2, y_pos)]):
                    Rectangle(CONN_DEPTH, CONN_TAB_WIDTH)
            extrude(amount=CONN_HEIGHT)

        # Groove on -X end
        groove_tab_width = CONN_TAB_WIDTH + 2 * CONN_CLEARANCE
        groove_depth = CONN_DEPTH + CONN_CLEARANCE
        for y_pos in tab_positions_y:
            with BuildSketch(Plane.XY.offset(BRIDGE_HEIGHT)):
                with Locations([(-BRIDGE_DECK_LEN/2 + groove_depth/2 - CONN_CLEARANCE, y_pos)]):
                    Rectangle(groove_depth, groove_tab_width)
            extrude(amount=CONN_HEIGHT, mode=Mode.SUBTRACT)

    return bridge.part


def make_ramp_down():
    """Mirror of ramp-up: descends from BRIDGE_HEIGHT to ground."""
    with BuildPart() as ramp:
        # Outer ramp solid (slopes down from -X to +X)
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Line((-RAMP_LENGTH/2, 0), (RAMP_LENGTH/2, 0))
                Line((RAMP_LENGTH/2, 0), (RAMP_LENGTH/2, BASE_THICK))
                Line((RAMP_LENGTH/2, BASE_THICK), (-RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK))
                Line((-RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK), (-RAMP_LENGTH/2, 0))
            make_face()
        extrude(amount=TOTAL_WIDTH / 2, both=True)

        # Hollow out
        slope = BRIDGE_HEIGHT / RAMP_LENGTH
        with BuildSketch(Plane.XZ):
            with BuildLine():
                x_start = -RAMP_LENGTH/2 + SHELL_THICK
                x_end = RAMP_LENGTH/2 - SHELL_THICK
                z_end_top = BASE_THICK + slope * (RAMP_LENGTH - SHELL_THICK) - SHELL_THICK
                Line((x_start, SHELL_THICK), (x_end, SHELL_THICK))
                Line((x_end, SHELL_THICK), (x_end, SHELL_THICK + SHELL_THICK))
                Line((x_end, SHELL_THICK + SHELL_THICK), (x_start, z_end_top))
                Line((x_start, z_end_top), (x_start, SHELL_THICK))
            make_face()
        extrude(amount=(TOTAL_WIDTH - 2 * SHELL_THICK) / 2, both=True, mode=Mode.SUBTRACT)

        # Support ribs
        for i in range(1, NUM_RIBS + 1):
            x_pos = -RAMP_LENGTH/2 + i * (RAMP_LENGTH / (NUM_RIBS + 1))
            # Height at this x position (slope goes down from left to right)
            z_at_x = BRIDGE_HEIGHT - slope * (x_pos + RAMP_LENGTH/2)
            with BuildSketch(Plane.YZ.offset(x_pos)):
                with BuildLine():
                    hw = (TOTAL_WIDTH - 2 * SHELL_THICK) / 2
                    Line((-hw, SHELL_THICK), (hw, SHELL_THICK))
                    Line((hw, SHELL_THICK), (hw, z_at_x + BASE_THICK - SHELL_THICK))
                    Line((hw, z_at_x + BASE_THICK - SHELL_THICK), (-hw, z_at_x + BASE_THICK - SHELL_THICK))
                    Line((-hw, z_at_x + BASE_THICK - SHELL_THICK), (-hw, SHELL_THICK))
                make_face()
            extrude(amount=RIB_THICK / 2, both=True)

        # Side walls
        with BuildSketch(Plane.XZ.offset(TOTAL_WIDTH / 2 - WALL_THICK / 2)):
            with BuildLine():
                Line((-RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK), (RAMP_LENGTH/2, BASE_THICK))
                Line((RAMP_LENGTH/2, BASE_THICK), (RAMP_LENGTH/2, BASE_THICK + WALL_HEIGHT))
                Line((RAMP_LENGTH/2, BASE_THICK + WALL_HEIGHT), (-RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK + RAMP_WALL_HEIGHT))
                Line((-RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK + RAMP_WALL_HEIGHT), (-RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK))
            make_face()
        extrude(amount=WALL_THICK / 2, both=True)

        with BuildSketch(Plane.XZ.offset(-(TOTAL_WIDTH / 2 - WALL_THICK / 2))):
            with BuildLine():
                Line((-RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK), (RAMP_LENGTH/2, BASE_THICK))
                Line((RAMP_LENGTH/2, BASE_THICK), (RAMP_LENGTH/2, BASE_THICK + WALL_HEIGHT))
                Line((RAMP_LENGTH/2, BASE_THICK + WALL_HEIGHT), (-RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK + RAMP_WALL_HEIGHT))
                Line((-RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK + RAMP_WALL_HEIGHT), (-RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK))
            make_face()
        extrude(amount=WALL_THICK / 2, both=True)

        # Lane dividers
        for i in range(1, NUM_LANES):
            y_pos = -ROAD_WIDTH / 2 + i * LANE_WIDTH + (i - 1) * DIVIDER_WIDTH + DIVIDER_WIDTH / 2
            with BuildSketch(Plane.XZ.offset(y_pos)):
                with BuildLine():
                    Line((-RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK), (RAMP_LENGTH/2, BASE_THICK))
                    Line((RAMP_LENGTH/2, BASE_THICK), (RAMP_LENGTH/2, BASE_THICK + DIVIDER_HEIGHT))
                    Line((RAMP_LENGTH/2, BASE_THICK + DIVIDER_HEIGHT), (-RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK + DIVIDER_HEIGHT))
                    Line((-RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK + DIVIDER_HEIGHT), (-RAMP_LENGTH/2, BRIDGE_HEIGHT + BASE_THICK))
                make_face()
            extrude(amount=DIVIDER_WIDTH / 2, both=True)

        # Top-end tongue connector (-X end, at bridge height)
        for y_pos in tab_positions_y:
            with BuildSketch(Plane.XY.offset(BRIDGE_HEIGHT)):
                with Locations([(-RAMP_LENGTH/2 - CONN_DEPTH/2, y_pos)]):
                    Rectangle(CONN_DEPTH, CONN_TAB_WIDTH)
            extrude(amount=CONN_HEIGHT)

        # Bottom-end groove connector (+X end, ground level)
        groove_tab_width = CONN_TAB_WIDTH + 2 * CONN_CLEARANCE
        groove_depth = CONN_DEPTH + CONN_CLEARANCE
        for y_pos in tab_positions_y:
            with BuildSketch(Plane.XY):
                with Locations([(RAMP_LENGTH/2 - groove_depth/2 + CONN_CLEARANCE, y_pos)]):
                    Rectangle(groove_depth, groove_tab_width)
            extrude(amount=CONN_HEIGHT, mode=Mode.SUBTRACT)

    return ramp.part


# === BUILD AND EXPORT ALL THREE ===
pieces = {
    "track-ramp-up": make_ramp_up,
    "track-bridge-deck": make_bridge_deck,
    "track-ramp-down": make_ramp_down,
}

for name, builder in pieces.items():
    out_dir = os.path.join(BASE_DIR, "outputs", name)
    os.makedirs(out_dir, exist_ok=True)

    part = builder()
    stl_path = os.path.join(out_dir, f"{name}.stl")
    step_path = os.path.join(out_dir, f"{name}.step")
    export_stl(part, stl_path)
    export_step(part, step_path)

    bb = part.bounding_box()
    print(f"{name} created!")
    print(f"  Size: {bb.max.X - bb.min.X:.1f} x {bb.max.Y - bb.min.Y:.1f} x {bb.max.Z - bb.min.Z:.1f} mm")
    print(f"  Volume: {part.volume:.1f} mm³ ({part.volume/1000:.1f} cm³)")
    print(f"  Est. material: ~{part.volume/1000 * 1.24 * 0.45:.0f}g PLA")
    print(f"  STL: {stl_path}")
    print()
