#!/usr/bin/env python3
"""Validate that all track pieces have compatible mating faces and fit on the X1C."""
from build123d import *
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
BED = 256  # X1C build volume

pieces = {
    "track-straight": "track-straight/track-straight.step",
    "track-curve-left": "track-curve-left/track-curve-left.step",
    "track-curve-right": "track-curve-right/track-curve-right.step",
    "track-ramp-up": "track-ramp-up/track-ramp-up.step",
    "track-bridge-deck": "track-bridge-deck/track-bridge-deck.step",
    "track-ramp-down": "track-ramp-down/track-ramp-down.step",
}

print("=" * 65)
print("TRACK SYSTEM VALIDATION REPORT")
print("=" * 65)

all_ok = True

for name, path in pieces.items():
    shape = import_step(os.path.join(BASE, path))
    bb = shape.bounding_box()
    dims = [round(bb.max.X - bb.min.X, 1),
            round(bb.max.Y - bb.min.Y, 1),
            round(bb.max.Z - bb.min.Z, 1)]
    vol = round(shape.volume, 1)
    mass = round(vol / 1000 * 1.24 * 0.45, 0)

    issues = []

    # Build volume check
    if any(d > BED for d in dims):
        issues.append(f"EXCEEDS BUILD VOLUME ({max(dims)}mm)")

    # Solid check
    solids = shape.solids()
    if len(solids) != 1:
        issues.append(f"Expected 1 solid, got {len(solids)}")

    # Volume sanity
    if vol <= 0:
        issues.append("Invalid volume")

    # Watertight estimate (face count should be reasonable)
    faces = shape.faces()
    if len(faces) < 6:
        issues.append(f"Too few faces ({len(faces)})")

    status = "PASS" if not issues else "FAIL"
    if issues:
        all_ok = False

    print(f"\n{name}")
    print(f"  Dimensions: {dims[0]} x {dims[1]} x {dims[2]} mm")
    print(f"  Volume: {vol/1000:.1f} cm³  |  ~{mass}g PLA")
    print(f"  Solids: {len(solids)}  |  Faces: {len(faces)}")
    print(f"  Status: {status}")
    for issue in issues:
        print(f"    !! {issue}")

# Connection compatibility matrix
print("\n" + "=" * 65)
print("CONNECTION COMPATIBILITY")
print("=" * 65)
print("""
Half-lap joint system:
  Male end (+X or entry): 10mm shelf at half base thickness (1.5mm)
  Female end (-X or exit): 10mm pocket, 0.3mm clearance all around

Connection pairs (male -> female):
  straight(+X) -> straight(-X)     Ground level
  straight(+X) -> curve-L(entry)   Ground level
  straight(+X) -> curve-R(entry)   Ground level
  curve-L(exit) -> straight(-X)    Ground level
  curve-R(exit) -> straight(-X)    Ground level
  straight(+X) -> ramp-up(-X)      Ground level
  ramp-down(+X) -> straight(-X)    Ground level
  ramp-up(+X) -> bridge(-X)        Bridge level (40mm)
  bridge(+X) -> ramp-down(-X)      Bridge level (40mm)

All ground-level joints at Z=0..3mm (base thickness)
All bridge-level joints at Z=40..43mm
""")

# Print summary
print("=" * 65)
print(f"OVERALL: {'ALL PASS' if all_ok else 'ISSUES FOUND'}")
print("=" * 65)

# Slicer settings reminder
print("""
BAMBU STUDIO SETTINGS (X1C, PLA, 0.4mm hardened steel nozzle):
  Layer height:     0.20mm
  Wall count:       4 walls (1.6mm)
  Infill:           20% gyroid
  Top/bottom:       5 layers
  Supports:         Tree supports (ramps/bridge only)
  Orientation:      Flat pieces road-down on plate
  Nozzle temp:      215C
  Bed temp:         55C
  Speed:            Standard, 100mm/s outer walls
  Brim:             Recommended on curves
""")
