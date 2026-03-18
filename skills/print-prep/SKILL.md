---
name: print-prep
description: Prepare a 3D model for printing — analyze printability, suggest orientation, estimate print time and filament, pack build plates, and export. Use when the user wants to prepare, check, or optimize a model for 3D printing.
---

# Print Preparation

Help the user prepare a model for 3D printing using the analysis, utility, and export tools.

## Workflow

1. Call `list_models` to see available models
2. Call `analyze_printability` to check watertightness, thin walls, and build volume fit
3. Call `analyze_overhangs` to identify faces that need support material
4. Call `suggest_orientation` to find the optimal print orientation
5. Call `estimate_print` with the user's material and settings to get filament/cost estimates
6. If the model needs fixes (thin walls, overhangs), suggest using the **modify-model** skill
7. Call `export_model` to export the final STL/STEP/3MF file

## Analysis Tools

| Tool | Purpose |
|------|---------|
| `analyze_printability` | Watertight check, thin wall detection, build volume fit |
| `analyze_overhangs` | Find overhang faces exceeding angle threshold |
| `suggest_orientation` | Test orientations to minimize supports and maximize bed contact |
| `estimate_print` | Filament weight, length, cost estimate by material |
| `section_view` | 2D cross-section SVG to verify internal geometry |
| `export_drawing` | Multi-view technical drawing SVG for documentation |

## Optimization Tools

| Tool | Purpose |
|------|---------|
| `shrinkage_compensation` | Scale model to compensate for material shrinkage |
| `split_model_by_color` | Split into separate STLs for multi-color printing (Bambu AMS) |
| `pack_models` | Arrange multiple models on one build plate with padding |
| `convert_format` | Convert between STL, STEP, 3MF, BREP formats |

## Material Defaults

| Material | Density | Shrinkage | Notes |
|----------|---------|-----------|-------|
| PLA | 1.24 g/cm3 | 0.3% | Best for most prints, easiest to print |
| PETG | 1.27 g/cm3 | 0.4% | Food-safe option, more flexible than PLA |
| ABS | 1.04 g/cm3 | 0.7% | Needs enclosure, use `shrinkage_compensation` |
| ASA | 1.07 g/cm3 | 0.5% | Outdoor UV-resistant alternative to ABS |
| TPU | 1.21 g/cm3 | 0.5% | Flexible, good for gaskets and grips |
| Nylon | 1.14 g/cm3 | 1.5% | Strong but high shrinkage, always compensate |

## Tips

- PLA is the default material if the user doesn't specify one
- Layer height 0.2mm and 15% infill are good defaults for the Bambu X1C
- Suggest splitting large models with `split_model` if they exceed 256mm build volume
- Always use `shrinkage_compensation` for ABS and Nylon
- Use `split_model_by_color` for multi-color prints on Bambu Lab AMS
- Generate `export_drawing` for documentation before publishing
- Use `pack_models` when printing multiple copies or multi-part assemblies
