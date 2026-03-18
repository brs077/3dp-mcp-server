---
name: modify-model
description: Modify, transform, or combine 3D models — shell, split, add text, threaded holes, boolean operations, transforms, imports, and 2D views. Use when the user wants to change, combine, hollow, cut, engrave, or visualize an existing model.
---

# Model Modification & Transformation

Help the user modify existing 3D models using the modification, transform, and visualization tools.

## Available Tools

### Transforms & Combining
| Tool | Use Case |
|------|----------|
| `transform_model` | Scale, rotate, mirror, or translate a model |
| `combine_models` | Boolean union, subtract, or intersect two models |
| `import_model` | Import an STL or STEP file from disk |

### Modifications
| Tool | Use Case |
|------|----------|
| `shell_model` | Hollow out a model with uniform wall thickness |
| `split_model` | Cut a model along XY/XZ/YZ plane |
| `add_text` | Emboss or deboss text onto a model face |
| `create_threaded_hole` | Add threaded or heat-set insert holes (M2-M10) |

### 2D Visualization
| Tool | Use Case |
|------|----------|
| `section_view` | Generate a 2D cross-section as SVG |
| `export_drawing` | Multi-view 2D technical drawing as SVG |

### Utilities
| Tool | Use Case |
|------|----------|
| `pack_models` | Arrange multiple models on build plate for batch printing |
| `convert_format` | Convert between STL, STEP, 3MF, BREP formats |

## Workflow

1. Call `list_models` to see available models in the session
2. Choose the appropriate modification tool
3. Apply the modification — most tools create a new model from a source
4. Call `measure_model` to verify the result
5. Call `analyze_printability` to confirm the modified model is still printable

## Common Patterns

### Hollowing a box into a container
```
1. shell_model(name="box_shell", source_name="my_box", thickness=2.0, open_faces='["top"]')
```

### Adding mounting holes
```
1. create_threaded_hole(name="box_with_holes", source_name="my_box",
     position='[10, 10, 0]', thread_spec="M3", depth=8)
```

### Engraving text on a part
```
1. add_text(name="labeled_part", source_name="my_part", text="v1.0",
     face="top", font_size=8, depth=0.5, emboss=False)
```

### Combining two parts
```
1. combine_models(name="assembly", model_a="base", model_b="lid", operation="union")
```

### Cutting a model in half for easier printing
```
1. split_model(name="top_half", source_name="tall_part", plane="XY", keep="above")
2. split_model(name="bottom_half", source_name="tall_part", plane="XY", keep="below")
```

### Importing and transforming an external STL
```
1. import_model(name="imported", file_path="/path/to/part.stl")
2. transform_model(name="scaled", source_name="imported",
     operations='[{"type": "scale", "factor": 1.5}]')
```

### Generating a technical drawing for documentation
```
1. export_drawing(name="my_part", views='["front", "top", "right", "iso"]',
     page_size="A4")
```

## Tips

- `shell_model` requires a watertight solid — run `analyze_printability` first
- `split_model` is useful for parts exceeding the build volume (256mm on X1C)
- `add_text` with `emboss=False` creates debossed (engraved) text — better for FDM
- `transform_model` operations can be chained as a JSON array
- `combine_models` with "subtract" is how you cut holes, pockets, and slots
- `section_view` outputs SVG — useful for verifying internal geometry
- `pack_models` arranges parts with padding for batch prints on one plate
- `convert_format` output is restricted to the outputs directory for security
