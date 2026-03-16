---
name: design-model
description: Design a 3D-printable CAD model using build123d. Use when the user wants to create, design, or model a 3D object for printing.
---

# 3D Model Design

Help the user design a 3D-printable model using the `create_model` MCP tool.

## Workflow

1. Clarify the user's design intent — dimensions, shape, purpose, material
2. Write build123d Python code that assigns the final shape to `result`
3. Call `create_model` with a descriptive name and the code
4. Call `measure_model` to verify dimensions
5. Call `analyze_printability` to check for printing issues
6. If issues are found, iterate on the design

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
