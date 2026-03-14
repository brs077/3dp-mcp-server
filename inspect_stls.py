#!/usr/bin/env python3
"""Inspect all track STLs - check mating face geometry and connector alignment."""
from build123d import *
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")

pieces = {
    "straight": "track-straight/track-straight.step",
    "curve-left": "track-curve-left/track-curve-left.step",
    "curve-right": "track-curve-right/track-curve-right.step",
    "ramp-up": "track-ramp-up/track-ramp-up.step",
    "bridge-deck": "track-bridge-deck/track-bridge-deck.step",
    "ramp-down": "track-ramp-down/track-ramp-down.step",
}

for name, path in pieces.items():
    full = os.path.join(BASE, path)
    shape = import_step(full)
    bb = shape.bounding_box()
    print(f"\n=== {name} ===")
    print(f"  BBox: X[{bb.min.X:.1f}, {bb.max.X:.1f}]  Y[{bb.min.Y:.1f}, {bb.max.Y:.1f}]  Z[{bb.min.Z:.1f}, {bb.max.Z:.1f}]")
    print(f"  Size: {bb.max.X-bb.min.X:.1f} x {bb.max.Y-bb.min.Y:.1f} x {bb.max.Z-bb.min.Z:.1f}")

    # Check faces at the mating boundaries
    faces = shape.faces()
    print(f"  Faces: {len(faces)}")

    # For each face, find ones that are planar and at the extremes
    for f in faces:
        c = f.center()
        # Check if face is at the X or Y boundary (potential mating face)
        if abs(c.X - bb.min.X) < 1 or abs(c.X - bb.max.X) < 1:
            fb = f.bounding_box()
            print(f"  X-boundary face at center=({c.X:.1f},{c.Y:.1f},{c.Z:.1f}), "
                  f"size={fb.max.X-fb.min.X:.1f}x{fb.max.Y-fb.min.Y:.1f}x{fb.max.Z-fb.min.Z:.1f}, "
                  f"area={f.area:.1f}")
        if abs(c.Y - bb.min.Y) < 1 or abs(c.Y - bb.max.Y) < 1:
            fb = f.bounding_box()
            print(f"  Y-boundary face at center=({c.X:.1f},{c.Y:.1f},{c.Z:.1f}), "
                  f"size={fb.max.X-fb.min.X:.1f}x{fb.max.Y-fb.min.Y:.1f}x{fb.max.Z-fb.min.Z:.1f}, "
                  f"area={f.area:.1f}")
