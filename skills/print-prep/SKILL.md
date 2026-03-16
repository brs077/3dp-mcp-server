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

## Tips

- PLA is the default material if the user doesn't specify one
- Layer height 0.2mm and 15% infill are good defaults
- Suggest splitting large models with `split_model` if they exceed build volume
- Use `shrinkage_compensation` for materials with high shrinkage (ABS, Nylon)
- Use `split_model_by_color` for multi-color prints on Bambu Lab AMS
