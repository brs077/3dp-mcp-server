---
name: parametric-components
description: Create parametric mechanical components — enclosures, gears, snap-fits, hinges, dovetails, and labels. Use when the user wants to generate a ready-made functional component with configurable dimensions.
---

# Parametric Components

Help the user create ready-made functional components with configurable parameters. These tools generate complete parts that can be used standalone or combined with other models.

## Available Tools

| Tool | Use Case |
|------|----------|
| `create_enclosure` | Electronics project boxes with snap or screw lids |
| `create_gear` | Involute spur gears with configurable module, teeth, bore |
| `create_snap_fit` | Cantilever snap-fit joints for tool-free assembly |
| `create_hinge` | Two-part pin hinge assemblies |
| `create_dovetail` | Male or female dovetail joints for interlocking parts |
| `generate_label` | 3D-printable labels with text and optional QR codes |

## Workflow

1. Clarify the user's requirements — dimensions, purpose, assembly method
2. Select the appropriate component tool
3. Generate the component with suitable parameters
4. Call `measure_model` to verify dimensions
5. Call `analyze_printability` to confirm FDM suitability
6. If needed, use `combine_models` to integrate with other parts

## Enclosure Guide

`create_enclosure` generates a body and lid as separate models (`name_body` and `name_lid`).

**Lid types:**
- `"snap"` — Snap-fit ridge on lid, groove on body (no screws needed)
- `"screw"` — Corner screw posts with holes

**Features** (JSON array):
- `"vent_slots"` — Ventilation slots on side walls
- `"cable_hole"` — Cable passthrough hole
- `"mounting_tabs"` — External mounting tabs with screw holes
- `"screw_posts"` — Internal corner screw posts

Example:
```
create_enclosure(name="project_box", inner_width=80, inner_depth=50,
  inner_height=30, wall=2.0, lid_type="snap",
  features='["vent_slots", "cable_hole"]')
```

## Gear Guide

`create_gear` uses bd_warehouse's involute gear profile for accurate tooth geometry.

**Key parameters:**
- `module` — Tooth size (1.0 = small, 2.0 = medium, 3.0 = large). Meshing gears must share the same module.
- `teeth` — Number of teeth. More teeth = larger gear, smoother motion.
- `pressure_angle` — Usually 20° (standard) or 14.5° (legacy). Keep at 20° for FDM.
- `bore` — Center hole diameter for shaft mounting.

**Gear ratio:** ratio = teeth_driven / teeth_driver. E.g., 40T driven by 20T = 2:1 ratio.

Example — 2:1 gear pair:
```
create_gear(name="driver", module=2.0, teeth=20, thickness=8, bore=5)
create_gear(name="driven", module=2.0, teeth=40, thickness=8, bore=5)
```

## Snap-Fit Guide

`create_snap_fit` creates cantilever beam snap-fit clips. Pass params as JSON:
- `beam_length` — Length of the cantilever beam (longer = more flexible)
- `beam_width` — Width of the beam
- `beam_thickness` — Thickness (thinner = easier snap, but weaker)
- `hook_depth` — Depth of the hook catch

**FDM tip:** Print with the beam oriented vertically for best layer adhesion along the flex axis.

## Hinge Guide

`create_hinge` generates two interlocking leaves (`name_leaf_a` and `name_leaf_b`) with a shared pin hole.

**Parameters** (JSON):
- `leaf_width`, `leaf_height`, `leaf_thickness`
- `pin_diameter` — Add 0.2mm clearance for FDM
- `num_knuckles` — More knuckles = stronger but harder to print

## Dovetail Guide

`create_dovetail` generates male or female dovetail joints.

- Set `dovetail_type="male"` for the protruding key
- Set `dovetail_type="female"` for the receiving slot
- Add `clearance=0.2` for FDM printing tolerance
- Use `combine_models` to boolean-subtract the female shape from your part

## Label Guide

`generate_label` creates a flat plate with raised text, optionally with a QR code.

- `size` — JSON array `[width, height, thickness]` in mm
- `font_size` — Text height in mm (8-12 works well for FDM)
- `qr_data` — Optional URL or text to encode as QR code on the label

Example:
```
generate_label(name="wifi_label", text="Guest WiFi", size="[60, 30, 2]",
  font_size=8, qr_data="WIFI:T:WPA;S:MyNetwork;P:password123;;")
```

## FDM Printing Tips

- **Enclosures:** Print body upside-down (opening up) for best overhangs. Print lid flat.
- **Gears:** Use 100% infill and 3+ perimeters for strength. Print flat (teeth up).
- **Snap-fits:** Orient beam vertically. Use PETG or ABS for better fatigue life than PLA.
- **Hinges:** Print leaves flat. Sand pin holes if tight. Use 0.2mm clearance.
- **Dovetails:** Test clearance with a small sample before committing to a full part.
- **Labels:** Print with 0.12mm layer height for crisp text. Use contrasting filament colors.
