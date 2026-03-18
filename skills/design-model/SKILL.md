---
name: design-model
description: Design a 3D-printable CAD model using build123d. Use when the user wants to create, design, or model a 3D object for printing.
---

# 3D Model Design

Help the user design a 3D-printable model using the MCP tools.

## Workflow

1. Clarify the user's design intent — dimensions, shape, purpose, material
2. Check if a **parametric component** fits before writing raw code (see below)
3. Write build123d Python code that assigns the final shape to `result`
4. Call `create_model` with a descriptive name and the code
5. Apply **modifications** as needed (shell, text, threaded holes)
6. Call `measure_model` to verify dimensions
7. Call `analyze_printability` to check for printing issues
8. If issues are found, iterate on the design

## Parametric Components

Before writing raw build123d code, check if one of these purpose-built tools fits:

- `create_enclosure` — Electronics enclosure with snap/screw lid, vent slots, cable holes, screw posts
- `create_gear` — Involute spur gear with configurable module, teeth, bore
- `create_snap_fit` — Cantilever snap-fit joints
- `create_hinge` — Two-part pin hinge assembly
- `create_dovetail` — Male or female dovetail joints with clearance
- `generate_label` — 3D-printable label with embossed text and optional QR code

## Mechanical Parts (bd_warehouse)

For standard mechanical components, use the **mechanical-parts** skill tools:

- `create_thread` — ISO metric, ACME, trapezoidal, plastic bottle threads (male + female)
- `create_fastener` — Screws, nuts, washers, heat-set inserts with real geometry
- `create_bearing` — Ball and roller bearings (5 types)
- `create_sprocket` — Chain sprockets with parametric tooth profiles
- `create_flange` — ASME B16.5 pipe flanges (blind, slip-on, weld neck, etc.)
- `create_pipe` — Custom tube/pipe sections
- `create_openbuilds_part` — V-Slot rails, C-Beam, lead screws for CNC fixtures

## Post-Creation Modifications

After creating a base model, refine it with:

- `shell_model` — Hollow out a solid part with optional open faces
- `add_text` — Emboss or deboss text onto a face
- `create_threaded_hole` — Add M2–M10 threaded or heat-set insert holes
- `transform_model` — Scale, rotate, mirror, or translate
- `combine_models` — Boolean union, subtract, or intersect two models
- `import_model` — Bring in existing STL/STEP files from disk

## build123d Guidelines

- All dimensions are in millimeters
- The final shape must be assigned to `result`
- Use `Box`, `Cylinder`, `Sphere` for primitives
- Use `fillet` and `chamfer` for edge treatments
- Use `extrude`, `revolve`, `sweep`, `loft` for complex shapes
- Use boolean operations via `combine_models` for multi-body designs
- Target Bambu Lab X1C build volume: 256 x 256 x 256 mm
- Minimum wall thickness: 1.2mm for FDM printing
- Add fillets (≥0.5mm) to reduce stress concentrations
