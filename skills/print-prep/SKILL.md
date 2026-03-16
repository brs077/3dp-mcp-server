---
name: print-prep
description: Prepare a 3D model for printing — analyze printability, suggest orientation, estimate print time and filament. Use when the user wants to prepare, check, or optimize a model for 3D printing.
---

# Print Preparation

Help the user prepare a model for 3D printing using the analysis and export tools.

## Workflow

1. Call `analyze_printability` to check watertightness, thin walls, and build volume fit
2. Call `analyze_overhangs` to identify faces that need support material
3. Call `suggest_orientation` to find the optimal print orientation
4. Call `estimate_print` with the user's material and settings to get filament/cost estimates
5. If the model needs fixes (thin walls, overhangs), suggest design modifications
6. Call `export_model` to export the final STL/STEP/3MF file

## Visualization & Inspection

- Call `section_view` to inspect internal geometry (wall thickness, hollows, infill cavities)
- Call `export_drawing` to generate a multi-view technical drawing with dimensions (SVG)

## Batch & Format Tools

- Call `pack_models` to arrange multiple parts on one build plate with padding
- Call `convert_format` to convert between STL, STEP, 3MF, and BREP formats
- Call `split_model` to split oversized models that exceed the build volume

## Material-Specific

- PLA is the default material if the user doesn't specify one
- Layer height 0.2mm and 15% infill are good defaults
- Use `shrinkage_compensation` for materials with high shrinkage (ABS, Nylon)
- Use `split_model_by_color` for multi-color prints on Bambu Lab AMS

## Bambu Studio Slicer Tips

- **Infill settings**: Left panel → **Strength** section (switch to Advanced mode to see pattern options)
- **Recommended infill**: 15% Gyroid — self-supporting, strong in all directions, minimal filament
- **Supports**: Tree(auto) for complex overhangs, Normal for flat horizontal surfaces
- **Support painting**: Use the brush tool to manually enforce or block supports on specific faces
- **Solid models with slicer infill** are generally better than manually hollowed models — the slicer's gyroid/lightning patterns are self-supporting and don't create internal overhangs
