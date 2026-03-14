#!/usr/bin/env python3
"""
Pixar Cars Mini Racers track system — puzzle-piece interlocking connectors.
2.5 cars wide, jigsaw-style snap-fit joints.

Convention: each face has male knob on the RIGHT side and female socket on the
LEFT side (when looking at the face from outside). When two faces meet,
left/right flips, so male always meets female.

"Right" = outward_normal × Z_up.
"""
from build123d import *
import os

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")

# ============================================================
# TRACK DIMENSIONS
# ============================================================
ROAD_WIDTH = 60.0
WALL_THICK = 3.0
WALL_HEIGHT = 6.0
BASE_THICK = 3.0
TOTAL_WIDTH = ROAD_WIDTH + 2 * WALL_THICK  # 66mm
SEGMENT_LEN = 150.0

INNER_RADIUS = 60.0
OUTER_RADIUS = INNER_RADIUS + TOTAL_WIDTH  # 126mm
CENTER_RADIUS = (INNER_RADIUS + OUTER_RADIUS) / 2  # 93mm

BRIDGE_HEIGHT = 40.0
RAMP_LENGTH = 150.0
RAMP_WALL_HEIGHT = 10.0
BRIDGE_DECK_LEN = 150.0
SHELL_THICK = 3.0
RIB_THICK = 3.0
NUM_RIBS = 3
LANDING_LEN = 13.0  # 0.5" flat landing at each end of ramp

# ============================================================
# PUZZLE CONNECTOR
# ============================================================
KNOB_NECK_W = 6.0
KNOB_NECK_L = 4.0
KNOB_HEAD_R = 4.5  # 9mm dia > 6mm neck → 1.5mm interlock/side
KNOB_OFFSET = 15.0
KNOB_CLR = 0.3


def make_knob(cx, cy, cz, nx, ny, h):
    """Create a puzzle knob (male) shape at the given face position.

    cx,cy,cz: center of knob position on face
    nx,ny: outward face normal (axis-aligned)
    h: height of connector
    """
    zmid = cz + h / 2
    if abs(nx) > 0.5:
        neck = Pos(cx + nx * KNOB_NECK_L / 2, cy, zmid) * Box(KNOB_NECK_L, KNOB_NECK_W, h)
        head = Pos(cx + nx * KNOB_NECK_L, cy, zmid) * Cylinder(KNOB_HEAD_R, h)
    else:
        neck = Pos(cx, cy + ny * KNOB_NECK_L / 2, zmid) * Box(KNOB_NECK_W, KNOB_NECK_L, h)
        head = Pos(cx, cy + ny * KNOB_NECK_L, zmid) * Cylinder(KNOB_HEAD_R, h)
    return neck.fuse(head)


def make_socket(cx, cy, cz, nx, ny, h):
    """Create a puzzle socket (female) shape — slightly oversized for clearance.
    Socket extends INWARD (opposite to normal).
    """
    cl = KNOB_CLR
    zmid = cz + h / 2
    if abs(nx) > 0.5:
        neck = Pos(cx - nx * (KNOB_NECK_L + cl) / 2, cy, zmid) * \
               Box(KNOB_NECK_L + cl, KNOB_NECK_W + 2 * cl, h + 0.2)
        head = Pos(cx - nx * KNOB_NECK_L, cy, zmid) * \
               Cylinder(KNOB_HEAD_R + cl, h + 0.2)
    else:
        neck = Pos(cx, cy - ny * (KNOB_NECK_L + cl) / 2, zmid) * \
               Box(KNOB_NECK_W + 2 * cl, KNOB_NECK_L + cl, h + 0.2)
        head = Pos(cx, cy - ny * KNOB_NECK_L, zmid) * \
               Cylinder(KNOB_HEAD_R + cl, h + 0.2)
    return neck.fuse(head)


def make_support_fin(cx, cy, z_top, nx, ny, knob_h):
    """Create a thin breakaway support fin from Z=0 up to z_top under a male knob.

    The fin is 0.8mm thick (2 perimeters), oriented perpendicular to the face normal,
    spanning the width of the knob head (2 * KNOB_HEAD_R). A small 0.3mm gap at the
    top makes it easy to snap off after printing.

    cx, cy: center of the male knob position on the face
    z_top: bottom of the connector (where support meets the knob)
    nx, ny: outward face normal
    knob_h: height of the connector piece
    """
    FIN_THICK = 0.8       # thin enough to snap off
    GAP = 0.3             # air gap at top for clean break
    fin_height = z_top - GAP
    if fin_height <= 0:
        return None

    # The knob extends outward from (cx,cy) along (nx,ny).
    # Neck: KNOB_NECK_L long, head center at cx + nx*KNOB_NECK_L
    # Support fin center should be under the head center
    head_cx = cx + nx * KNOB_NECK_L
    head_cy = cy + ny * KNOB_NECK_L

    # Fin spans the knob head diameter, oriented perpendicular to the normal
    fin_width = KNOB_HEAD_R * 2 + 2  # slightly wider than head for stability

    zmid = fin_height / 2
    if abs(nx) > 0.5:
        # Face normal along X: fin is in YZ plane
        fin = Pos(head_cx, head_cy, zmid) * Box(FIN_THICK, fin_width, fin_height)
    else:
        # Face normal along Y: fin is in XZ plane
        fin = Pos(head_cx, head_cy, zmid) * Box(fin_width, FIN_THICK, fin_height)

    return fin


def add_connectors(part, face_cx, face_cy, nx, ny, z_base, h=BASE_THICK):
    """Add puzzle connectors to a part. Returns modified part.

    Male knob on RIGHT side (N×Z), female socket on LEFT side.
    """
    rx, ry = ny, -nx  # right = N × Z

    male_x = face_cx + rx * KNOB_OFFSET
    male_y = face_cy + ry * KNOB_OFFSET
    knob = make_knob(male_x, male_y, z_base, nx, ny, h)

    fem_x = face_cx - rx * KNOB_OFFSET
    fem_y = face_cy - ry * KNOB_OFFSET
    socket = make_socket(fem_x, fem_y, z_base, nx, ny, h)

    return part.fuse(knob).cut(socket)


def add_connectors_with_support(part, face_cx, face_cy, nx, ny, z_base, h=BASE_THICK):
    """Add puzzle connectors plus breakaway support fins for elevated male knobs.

    Use this instead of add_connectors when z_base > 0 (bridge-height connectors)
    so the male knob has a thin support column from the build plate.
    """
    part = add_connectors(part, face_cx, face_cy, nx, ny, z_base, h)

    if z_base > 0:
        rx, ry = ny, -nx
        male_x = face_cx + rx * KNOB_OFFSET
        male_y = face_cy + ry * KNOB_OFFSET
        fin = make_support_fin(male_x, male_y, z_base, nx, ny, h)
        if fin is not None:
            part = part.fuse(fin)

    return part


# ============================================================
# STRAIGHT
# ============================================================
def make_straight():
    with BuildPart() as p:
        with BuildSketch(Plane.XY):
            Rectangle(SEGMENT_LEN, TOTAL_WIDTH)
        extrude(amount=BASE_THICK)
        for sign in [1, -1]:
            with BuildSketch(Plane.XY.offset(BASE_THICK)):
                with Locations([(0, sign * (TOTAL_WIDTH - WALL_THICK) / 2)]):
                    Rectangle(SEGMENT_LEN, WALL_THICK)
            extrude(amount=WALL_HEIGHT)

    result = p.part
    result = add_connectors(result, SEGMENT_LEN / 2, 0, 1, 0, 0)
    result = add_connectors(result, -SEGMENT_LEN / 2, 0, -1, 0, 0)
    return result


# ============================================================
# LEFT CURVE
# ============================================================
def make_curve_body():
    """Curve body (no connectors) — 90° CCW arc."""
    with BuildPart() as p:
        for (r1, r2, z0, h) in [
            (INNER_RADIUS, OUTER_RADIUS, 0, BASE_THICK),                 # base
            (OUTER_RADIUS - WALL_THICK, OUTER_RADIUS, BASE_THICK, WALL_HEIGHT),  # outer wall
            (INNER_RADIUS, INNER_RADIUS + WALL_THICK, BASE_THICK, WALL_HEIGHT),  # inner wall
        ]:
            with BuildSketch(Plane.XZ):
                with BuildLine():
                    Line((r1, z0), (r2, z0))
                    Line((r2, z0), (r2, z0 + h))
                    Line((r2, z0 + h), (r1, z0 + h))
                    Line((r1, z0 + h), (r1, z0))
                make_face()
            revolve(axis=Axis.Z, revolution_arc=90)
    return p.part


def make_curve_left():
    body = make_curve_body()
    # Entry at angle=0: face at Y≈0, center X=CENTER_R, N=(0,-1)
    body = add_connectors(body, CENTER_RADIUS, 0, 0, -1, 0)
    # Exit at angle=90: face at X≈0, center Y=CENTER_R, N=(-1,0)
    body = add_connectors(body, 0, CENTER_RADIUS, -1, 0, 0)
    return body


def make_curve_right():
    left_body = make_curve_body()
    body = mirror(left_body, about=Plane.XZ)
    # After mirror Y→-Y: entry at Y=0 N=(0,+1), exit at X=0 center Y=-CENTER_R N=(-1,0)
    body = add_connectors(body, CENTER_RADIUS, 0, 0, 1, 0)
    body = add_connectors(body, 0, -CENTER_RADIUS, -1, 0, 0)
    return body


# ============================================================
# RAMP UP — with flat landings at each end
# ============================================================
def make_ramp_up():
    # Profile (side view, XZ plane):
    #   Bottom landing: flat at Z=BASE_THICK for LANDING_LEN
    #   Slope: rises from BASE_THICK to BRIDGE_HEIGHT+BASE_THICK
    #   Top landing: flat at Z=BRIDGE_HEIGHT+BASE_THICK for LANDING_LEN
    #
    #   _LANDING_|____slope____|_LANDING_
    #   ground                  bridge

    half = RAMP_LENGTH / 2
    slope_len = RAMP_LENGTH - 2 * LANDING_LEN
    slope = BRIDGE_HEIGHT / slope_len
    # Key X positions
    x0 = -half                          # left edge
    x1 = x0 + LANDING_LEN              # end of bottom landing
    x2 = x1 + slope_len                # end of slope / start of top landing
    x3 = half                           # right edge

    with BuildPart() as p:
        # Solid profile: bottom landing + slope + top landing
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Line((x0, 0), (x3, 0))                                # bottom
                Line((x3, 0), (x3, BRIDGE_HEIGHT + BASE_THICK))       # right wall
                Line((x3, BRIDGE_HEIGHT + BASE_THICK),
                     (x2, BRIDGE_HEIGHT + BASE_THICK))                # top landing surface
                Line((x2, BRIDGE_HEIGHT + BASE_THICK),
                     (x1, BASE_THICK))                                # slope surface
                Line((x1, BASE_THICK), (x0, BASE_THICK))             # bottom landing surface
                Line((x0, BASE_THICK), (x0, 0))                      # left wall
            make_face()
        extrude(amount=TOTAL_WIDTH / 2, both=True)

        # Hollow out interior (under the slope, between landings)
        with BuildSketch(Plane.XZ):
            with BuildLine():
                xs = x1 + SHELL_THICK
                xe = x2 - SHELL_THICK
                zs = BASE_THICK + slope * SHELL_THICK
                ze = BRIDGE_HEIGHT + BASE_THICK - SHELL_THICK
                Line((xs, SHELL_THICK), (xe, SHELL_THICK))
                Line((xe, SHELL_THICK), (xe, ze))
                Line((xe, ze), (xs, zs))
                Line((xs, zs), (xs, SHELL_THICK))
            make_face()
        extrude(amount=(TOTAL_WIDTH - 2 * SHELL_THICK) / 2, both=True, mode=Mode.SUBTRACT)

        # Support ribs in hollow region
        rib_region = xe - xs
        for i in range(1, NUM_RIBS + 1):
            x_pos = xs + i * (rib_region / (NUM_RIBS + 1))
            z_top = slope * (x_pos - x1) + BASE_THICK - SHELL_THICK
            hw = (TOTAL_WIDTH - 2 * SHELL_THICK) / 2
            if z_top - SHELL_THICK < 3:
                continue
            with BuildSketch(Plane.YZ.offset(x_pos)):
                with BuildLine():
                    Line((-hw, SHELL_THICK), (hw, SHELL_THICK))
                    Line((hw, SHELL_THICK), (hw, z_top))
                    Line((hw, z_top), (-hw, z_top))
                    Line((-hw, z_top), (-hw, SHELL_THICK))
                make_face()
            extrude(amount=RIB_THICK / 2, both=True)

        # Walls — follow the landing+slope+landing profile
        for sign in [1, -1]:
            with BuildSketch(Plane.XZ.offset(sign * (TOTAL_WIDTH / 2 - WALL_THICK / 2))):
                with BuildLine():
                    Line((x0, BASE_THICK), (x1, BASE_THICK))                    # bottom landing top
                    Line((x1, BASE_THICK), (x2, BRIDGE_HEIGHT + BASE_THICK))    # slope
                    Line((x2, BRIDGE_HEIGHT + BASE_THICK),
                         (x3, BRIDGE_HEIGHT + BASE_THICK))                       # top landing top
                    Line((x3, BRIDGE_HEIGHT + BASE_THICK),
                         (x3, BRIDGE_HEIGHT + BASE_THICK + RAMP_WALL_HEIGHT))    # top right
                    Line((x3, BRIDGE_HEIGHT + BASE_THICK + RAMP_WALL_HEIGHT),
                         (x2, BRIDGE_HEIGHT + BASE_THICK + RAMP_WALL_HEIGHT))    # top landing wall top
                    Line((x2, BRIDGE_HEIGHT + BASE_THICK + RAMP_WALL_HEIGHT),
                         (x1, BASE_THICK + WALL_HEIGHT))                         # slope wall top
                    Line((x1, BASE_THICK + WALL_HEIGHT),
                         (x0, BASE_THICK + WALL_HEIGHT))                         # bottom landing wall top
                    Line((x0, BASE_THICK + WALL_HEIGHT), (x0, BASE_THICK))      # close
                make_face()
            extrude(amount=WALL_THICK / 2, both=True)

    result = p.part
    # Bottom end (-X) ground level — now on a flat landing
    result = add_connectors(result, -half, 0, -1, 0, 0)
    # Top end (+X) bridge level — with breakaway support fin
    result = add_connectors_with_support(result, half, 0, 1, 0, BRIDGE_HEIGHT)
    return result


# ============================================================
# BRIDGE DECK
# ============================================================
def make_bridge_deck():
    with BuildPart() as p:
        with BuildSketch(Plane.XY.offset(BRIDGE_HEIGHT)):
            Rectangle(BRIDGE_DECK_LEN, TOTAL_WIDTH)
        extrude(amount=BASE_THICK)

        pillar_o, pillar_i = 12.0, 6.0
        for xp in [-BRIDGE_DECK_LEN/3, BRIDGE_DECK_LEN/3]:
            for yp in [TOTAL_WIDTH/4, -TOTAL_WIDTH/4]:
                with BuildSketch(Plane.XY):
                    with Locations([(xp, yp)]):
                        Rectangle(pillar_o, pillar_o)
                extrude(amount=BRIDGE_HEIGHT)
                with BuildSketch(Plane.XY):
                    with Locations([(xp, yp)]):
                        Rectangle(pillar_i, pillar_i)
                extrude(amount=BRIDGE_HEIGHT - SHELL_THICK, mode=Mode.SUBTRACT)

        for sign in [1, -1]:
            with BuildSketch(Plane.XY.offset(BRIDGE_HEIGHT + BASE_THICK)):
                with Locations([(0, sign * (TOTAL_WIDTH - WALL_THICK) / 2)]):
                    Rectangle(BRIDGE_DECK_LEN, WALL_THICK)
            extrude(amount=RAMP_WALL_HEIGHT)

    result = p.part
    result = add_connectors_with_support(result, BRIDGE_DECK_LEN / 2, 0, 1, 0, BRIDGE_HEIGHT)
    result = add_connectors_with_support(result, -BRIDGE_DECK_LEN / 2, 0, -1, 0, BRIDGE_HEIGHT)
    return result


# ============================================================
# RAMP DOWN — with flat landings at each end
# ============================================================
def make_ramp_down():
    # Mirror of ramp-up: top landing on -X side, bottom landing on +X side
    #   _LANDING_|____slope____|_LANDING_
    #   bridge                  ground

    half = RAMP_LENGTH / 2
    slope_len = RAMP_LENGTH - 2 * LANDING_LEN
    slope = BRIDGE_HEIGHT / slope_len
    x0 = -half
    x1 = x0 + LANDING_LEN              # end of top landing
    x2 = x1 + slope_len                # end of slope / start of bottom landing
    x3 = half

    with BuildPart() as p:
        # Solid profile
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Line((x0, 0), (x3, 0))                                # bottom
                Line((x3, 0), (x3, BASE_THICK))                       # right wall (ground)
                Line((x3, BASE_THICK), (x2, BASE_THICK))              # bottom landing surface
                Line((x2, BASE_THICK),
                     (x1, BRIDGE_HEIGHT + BASE_THICK))                # slope surface (up)
                Line((x1, BRIDGE_HEIGHT + BASE_THICK),
                     (x0, BRIDGE_HEIGHT + BASE_THICK))                # top landing surface
                Line((x0, BRIDGE_HEIGHT + BASE_THICK), (x0, 0))      # left wall
            make_face()
        extrude(amount=TOTAL_WIDTH / 2, both=True)

        # Hollow out under the slope
        xs = x1 + SHELL_THICK
        xe = x2 - SHELL_THICK
        ze = BRIDGE_HEIGHT + BASE_THICK - slope * SHELL_THICK - SHELL_THICK
        zs = BASE_THICK + slope * SHELL_THICK

        # Only hollow where interior height > 5mm
        min_h = 5.0
        # At xe, interior height = zs (descending from ze). Check it's enough.
        # The slope descends: at position x, z_surface = BRIDGE_HEIGHT+BASE_THICK - slope*(x-x1)
        # Interior top = z_surface - SHELL_THICK. Interior bottom = SHELL_THICK.
        # Height = z_surface - SHELL_THICK - SHELL_THICK
        # Find x where height = min_h:
        xe_limit = x1 + (BRIDGE_HEIGHT + BASE_THICK - 2 * SHELL_THICK - min_h) / slope
        xe = min(xe, xe_limit)
        ze_at_xe = BRIDGE_HEIGHT + BASE_THICK - slope * (xe - x1) - SHELL_THICK

        with BuildSketch(Plane.XZ):
            with BuildLine():
                Line((xs, SHELL_THICK), (xe, SHELL_THICK))
                Line((xe, SHELL_THICK), (xe, ze_at_xe))
                Line((xe, ze_at_xe), (xs, ze))
                Line((xs, ze), (xs, SHELL_THICK))
            make_face()
        extrude(amount=(TOTAL_WIDTH - 2 * SHELL_THICK) / 2, both=True, mode=Mode.SUBTRACT)

        # Ribs
        rib_region = xe - xs
        for i in range(1, NUM_RIBS + 1):
            x_pos = xs + i * (rib_region / (NUM_RIBS + 1))
            z_top = BRIDGE_HEIGHT + BASE_THICK - slope * (x_pos - x1) - SHELL_THICK
            hw = (TOTAL_WIDTH - 2 * SHELL_THICK) / 2
            if z_top - SHELL_THICK < 3:
                continue
            with BuildSketch(Plane.YZ.offset(x_pos)):
                with BuildLine():
                    Line((-hw, SHELL_THICK), (hw, SHELL_THICK))
                    Line((hw, SHELL_THICK), (hw, z_top))
                    Line((hw, z_top), (-hw, z_top))
                    Line((-hw, z_top), (-hw, SHELL_THICK))
                make_face()
            extrude(amount=RIB_THICK / 2, both=True)

        # Walls — follow top landing + slope + bottom landing
        for sign in [1, -1]:
            with BuildSketch(Plane.XZ.offset(sign * (TOTAL_WIDTH / 2 - WALL_THICK / 2))):
                with BuildLine():
                    Line((x0, BRIDGE_HEIGHT + BASE_THICK),
                         (x1, BRIDGE_HEIGHT + BASE_THICK))                       # top landing
                    Line((x1, BRIDGE_HEIGHT + BASE_THICK),
                         (x2, BASE_THICK))                                       # slope
                    Line((x2, BASE_THICK), (x3, BASE_THICK))                    # bottom landing
                    Line((x3, BASE_THICK), (x3, BASE_THICK + WALL_HEIGHT))      # bottom right
                    Line((x3, BASE_THICK + WALL_HEIGHT),
                         (x2, BASE_THICK + WALL_HEIGHT))                         # bottom landing wall
                    Line((x2, BASE_THICK + WALL_HEIGHT),
                         (x1, BRIDGE_HEIGHT + BASE_THICK + RAMP_WALL_HEIGHT))    # slope wall
                    Line((x1, BRIDGE_HEIGHT + BASE_THICK + RAMP_WALL_HEIGHT),
                         (x0, BRIDGE_HEIGHT + BASE_THICK + RAMP_WALL_HEIGHT))    # top landing wall
                    Line((x0, BRIDGE_HEIGHT + BASE_THICK + RAMP_WALL_HEIGHT),
                         (x0, BRIDGE_HEIGHT + BASE_THICK))                       # close
                make_face()
            extrude(amount=WALL_THICK / 2, both=True)

    result = p.part
    # Top end (-X) bridge level — with breakaway support fin
    result = add_connectors_with_support(result, -half, 0, -1, 0, BRIDGE_HEIGHT)
    # Bottom end (+X) ground level — on flat landing
    result = add_connectors(result, half, 0, 1, 0, 0)
    return result


# ============================================================
# BUILD ALL
# ============================================================
builders = {
    "track-straight": make_straight,
    "track-curve-left": make_curve_left,
    "track-curve-right": make_curve_right,
    "track-ramp-up": make_ramp_up,
    "track-bridge-deck": make_bridge_deck,
    "track-ramp-down": make_ramp_down,
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

print(f"\nAll {len(builders)} pieces built.")
print(f"Puzzle connector: {KNOB_NECK_W}mm neck → {KNOB_HEAD_R*2}mm head, "
      f"{(KNOB_HEAD_R*2 - KNOB_NECK_W)/2}mm interlock, {KNOB_CLR}mm clearance")
