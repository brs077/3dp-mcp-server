#!/usr/bin/env python3
"""Analyze printability of all track pieces for Bambu X1C (256x256x256mm build volume)."""
from build123d import *
import os
import json

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
BED_X, BED_Y, BED_Z = 256, 256, 256
MIN_WALL = 0.8

pieces = [
    "track-straight/track-straight.step",
    "track-curve-left/track-curve-left.step",
    "track-curve-right/track-curve-right.step",
    "track-ramp-up/track-ramp-up.step",
    "track-bridge-deck/track-bridge-deck.step",
    "track-ramp-down/track-ramp-down.step",
]

print("=" * 70)
print("PRINTABILITY ANALYSIS — Bambu Lab X1C (256×256×256mm), PLA, 0.4mm nozzle")
print("=" * 70)

for piece_path in pieces:
    full_path = os.path.join(BASE_DIR, piece_path)
    name = piece_path.split("/")[0]

    print(f"\n--- {name} ---")

    try:
        shape = import_step(full_path)
    except Exception as e:
        print(f"  ERROR loading: {e}")
        continue

    bb = shape.bounding_box()
    dims = [
        round(bb.max.X - bb.min.X, 1),
        round(bb.max.Y - bb.min.Y, 1),
        round(bb.max.Z - bb.min.Z, 1),
    ]
    print(f"  Dimensions: {dims[0]} × {dims[1]} × {dims[2]} mm")

    issues = []

    # Check bed fit
    if dims[0] > BED_X or dims[1] > BED_Y or dims[2] > BED_Z:
        issues.append(f"EXCEEDS BUILD VOLUME ({max(dims):.1f}mm > 256mm)")

    # Volume
    try:
        vol = round(shape.volume, 1)
        print(f"  Volume: {vol} mm³ ({vol/1000:.1f} cm³)")
        if vol <= 0:
            issues.append("Zero or negative volume")
    except Exception:
        print(f"  Volume: could not compute")

    # Solid count
    try:
        solids = shape.solids()
        print(f"  Solids: {len(solids)}")
        if len(solids) == 0:
            issues.append("No solids found")
    except Exception:
        pass

    # Surface area / volume ratio (thin wall indicator)
    try:
        area = shape.area
        if vol > 0:
            ratio = round(area / vol, 4)
            print(f"  Area/Volume ratio: {ratio}")
            if ratio > 7.5:
                issues.append(f"High area/volume ratio ({ratio}) — check for thin walls < {MIN_WALL}mm")
    except Exception:
        pass

    # Face count
    try:
        faces = shape.faces()
        print(f"  Faces: {len(faces)}")
    except Exception:
        pass

    # Print orientation suggestion
    if dims[2] <= 10:
        print(f"  Orientation: print flat (road surface on bed for smooth finish)")
    elif "ramp" in name or "bridge" in name:
        print(f"  Orientation: print upright — will need supports for overhangs")
        if "ramp" in name:
            issues.append("Ramp slope may need supports depending on angle")

    # Estimate print time and material (rough)
    # PLA density ~1.24 g/cm³, typical fill ratio with 20% infill ≈ 40-50% solid
    fill_factor = 0.45  # approximate with walls + 20% infill
    mass_g = round(vol / 1000 * 1.24 * fill_factor, 1)
    filament_m = round(mass_g / (1.24 * 3.14159 * (0.875)**2) / 1000, 1)  # 1.75mm filament
    print(f"  Est. material: ~{mass_g}g PLA")

    # Verdict
    if not issues:
        print(f"  ✓ PRINTABLE — no issues detected")
    else:
        print(f"  ⚠ REVIEW NEEDED:")
        for issue in issues:
            print(f"    - {issue}")

print("\n" + "=" * 70)
print("RECOMMENDED SLICER SETTINGS (Bambu Studio)")
print("=" * 70)
print("""
  Layer height:     0.20mm (0.16mm for smoother road surface)
  Wall count:       4 (1.6mm walls)
  Infill:           20% gyroid
  Top/bottom:       5 layers
  Supports:         Tree (ramp/bridge only)
  Print surface:    Road surface face-down on build plate
  Nozzle temp:      215°C (Bambu PLA Basic)
  Bed temp:         55°C
  Speed:            Standard profile, 100mm/s outer walls
  Brim:             Recommended for curves (large footprint)
""")
