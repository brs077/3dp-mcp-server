# 3dp-mcp-server Tool Reference

Complete documentation for all 33 MCP tools provided by `3dp-mcp-server`.

---

## Table of Contents

- [Core Tools](#core-tools)
- [Transform & Combine](#transform--combine)
- [Modification](#modification)
- [Analysis & Export](#analysis--export)
- [Utility](#utility)
- [Parametric Components](#parametric-components)
- [Community](#community)
- [Publishing](#publishing)

---

## Core Tools

### `create_model`

Execute build123d Python code to create a 3D model. Automatically exports STL and STEP files on success.

Your code must assign the final shape to a variable called `result`. The import `from build123d import *` is auto-prepended if not already present.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Unique name for the model (used to reference it in other tools) |
| `code` | string | *required* | build123d Python code. Must assign final shape to `result` |

**Example usage:**

```json
{
  "name": "create_model",
  "arguments": {
    "name": "bracket",
    "code": "with BuildPart() as p:\n    Box(40, 20, 5)\n    with Locations((0, 0, 2.5)):\n        Cylinder(4, 10)\nresult = p.part"
  }
}
```

**Example response:**

```json
{
  "name": "bracket",
  "bbox": { "x": 40.0, "y": 20.0, "z": 15.0 },
  "volume_mm3": 4502.65,
  "exports": ["bracket.stl", "bracket.step"]
}
```

**Tips:**
- Always assign your final geometry to `result`.
- You can use any build123d API: `BuildPart`, `BuildSketch`, `Extrude`, `Fillet`, `Chamfer`, etc.
- If your code errors, the full traceback is returned so you can fix and retry.

---

### `export_model`

Export a previously created model to a specific file format.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name of an existing model |
| `format` | string | `"stl"` | Export format: `"stl"`, `"step"`, or `"3mf"` |

**Example usage:**

```json
{
  "name": "export_model",
  "arguments": {
    "name": "bracket",
    "format": "step"
  }
}
```

**Example response:**

```json
{
  "file": "/path/to/outputs/bracket.step",
  "format": "step",
  "size_bytes": 28410
}
```

---

### `measure_model`

Return precise measurements for a model including bounding box, volume, surface area, and topology counts.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name of an existing model |

**Example usage:**

```json
{
  "name": "measure_model",
  "arguments": {
    "name": "bracket"
  }
}
```

**Example response:**

```json
{
  "bbox": { "x": 40.0, "y": 20.0, "z": 15.0 },
  "volume_mm3": 4502.65,
  "surface_area_mm2": 3120.50,
  "face_count": 12,
  "edge_count": 24
}
```

---

### `analyze_printability`

Check whether a model is suitable for FDM 3D printing. Evaluates volume, solid count, dimensions against a 256mm print bed, face count, and area-to-volume ratio to flag potential thin-wall issues.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name of an existing model |
| `min_wall_mm` | float | `0.8` | Minimum wall thickness threshold in mm |

**Example usage:**

```json
{
  "name": "analyze_printability",
  "arguments": {
    "name": "bracket",
    "min_wall_mm": 1.0
  }
}
```

**Example response:**

```json
{
  "printable": true,
  "volume_mm3": 4502.65,
  "solid_count": 1,
  "fits_bed": true,
  "dimensions": { "x": 40.0, "y": 20.0, "z": 15.0 },
  "face_count": 12,
  "area_volume_ratio": 0.69,
  "warnings": []
}
```

**Tips:**
- A high area-to-volume ratio can indicate thin walls that may not print reliably.
- The bed size check uses 256mm (typical for printers like the Bambu Lab X1/P1 series).

---

### `list_models`

List all models currently loaded in the server session, with bounding box and volume for each.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| *(none)* | | | |

**Example usage:**

```json
{
  "name": "list_models",
  "arguments": {}
}
```

**Example response:**

```json
{
  "models": [
    { "name": "bracket", "bbox": { "x": 40.0, "y": 20.0, "z": 15.0 }, "volume_mm3": 4502.65 },
    { "name": "knob", "bbox": { "x": 25.0, "y": 25.0, "z": 12.0 }, "volume_mm3": 3100.00 }
  ]
}
```

---

### `get_model_code`

Retrieve the build123d source code that was used to create a model.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name of an existing model |

**Example usage:**

```json
{
  "name": "get_model_code",
  "arguments": {
    "name": "bracket"
  }
}
```

**Example response:**

```json
{
  "name": "bracket",
  "code": "with BuildPart() as p:\n    Box(40, 20, 5)\n    with Locations((0, 0, 2.5)):\n        Cylinder(4, 10)\nresult = p.part"
}
```

---

## Transform & Combine

### `transform_model`

Apply spatial transformations to a model. The `operations` parameter is a JSON string containing a single operation dict or a list of operation dicts applied in order.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the new transformed model |
| `source_name` | string | *required* | Name of the existing model to transform |
| `operations` | string (JSON) | *required* | Transformation operations (see below) |

**Operation keys:**

| Key | Value | Description |
|-----|-------|-------------|
| `"scale"` | `float` or `[x, y, z]` | Uniform or per-axis scale factor |
| `"rotate"` | `[rx, ry, rz]` | Rotation in degrees around X, Y, Z axes |
| `"mirror"` | `"XY"`, `"XZ"`, or `"YZ"` | Mirror across a plane |
| `"translate"` | `[x, y, z]` | Translation in mm |

**Example usage (multiple operations):**

```json
{
  "name": "transform_model",
  "arguments": {
    "name": "bracket_rotated",
    "source_name": "bracket",
    "operations": "[{\"rotate\": [0, 0, 45]}, {\"translate\": [10, 0, 0]}]"
  }
}
```

**Example usage (uniform scale):**

```json
{
  "name": "transform_model",
  "arguments": {
    "name": "bracket_small",
    "source_name": "bracket",
    "operations": "{\"scale\": 0.5}"
  }
}
```

**Example response:**

```json
{
  "name": "bracket_rotated",
  "bbox": { "x": 45.2, "y": 38.1, "z": 15.0 },
  "volume_mm3": 4502.65
}
```

**Tips:**
- Operations are applied sequentially when given as a list. Order matters: rotating then translating differs from translating then rotating.
- Non-uniform scale uses an `[x, y, z]` array, e.g., `[1.0, 1.0, 2.0]` to double the height.

---

### `combine_models`

Perform a Boolean operation between two models.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the resulting model |
| `model_a` | string | *required* | Name of the first model |
| `model_b` | string | *required* | Name of the second model |
| `operation` | string | `"union"` | Boolean operation: `"union"`, `"subtract"`, or `"intersect"` |

**Example usage:**

```json
{
  "name": "combine_models",
  "arguments": {
    "name": "bracket_with_hole",
    "model_a": "bracket",
    "model_b": "cylinder_cutout",
    "operation": "subtract"
  }
}
```

**Example response:**

```json
{
  "name": "bracket_with_hole",
  "bbox": { "x": 40.0, "y": 20.0, "z": 15.0 },
  "volume_mm3": 4100.20
}
```

**Tips:**
- `"subtract"` removes `model_b` from `model_a`.
- Position models with `transform_model` before combining so they overlap correctly.

---

### `import_model`

Import an external 3D model file into the server session.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name to assign to the imported model |
| `file_path` | string | *required* | Absolute path to the file (`.stl`, `.step`, or `.stp`) |

**Example usage:**

```json
{
  "name": "import_model",
  "arguments": {
    "name": "housing",
    "file_path": "/Users/bryan/models/housing.step"
  }
}
```

**Example response:**

```json
{
  "name": "housing",
  "bbox": { "x": 80.0, "y": 60.0, "z": 35.0 },
  "volume_mm3": 52400.00
}
```

---

## Modification

### `shell_model`

Hollow out a solid model, optionally removing faces to create openings.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the new shelled model |
| `source_name` | string | *required* | Name of the existing model to shell |
| `thickness` | float | `2.0` | Wall thickness in mm |
| `open_faces` | string (JSON) | `"[]"` | JSON list of face directions to remove: `"top"`, `"bottom"`, `"front"`, `"back"`, `"left"`, `"right"` |

**Example usage:**

```json
{
  "name": "shell_model",
  "arguments": {
    "name": "box_shell",
    "source_name": "box",
    "thickness": 1.5,
    "open_faces": "[\"top\"]"
  }
}
```

**Example response:**

```json
{
  "name": "box_shell",
  "bbox": { "x": 50.0, "y": 30.0, "z": 20.0 },
  "volume_mm3": 8200.00,
  "wall_thickness": 1.5,
  "open_faces": ["top"]
}
```

**Tips:**
- Shelling with no open faces creates a fully enclosed hollow object (useful for lightweight parts).
- Opening the top face is common for creating enclosures, trays, and cups.

---

### `split_model`

Split a model along a plane into two halves.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Base name for the split result(s) |
| `source_name` | string | *required* | Name of the existing model to split |
| `plane` | string | `"XY"` | Split plane: `"XY"`, `"XZ"`, `"YZ"`, or JSON `'{"axis":"Z","offset":10.5}'` for an offset plane |
| `keep` | string | `"both"` | Which half to keep: `"above"`, `"below"`, or `"both"` |

**Example usage (keep both halves with offset):**

```json
{
  "name": "split_model",
  "arguments": {
    "name": "housing_split",
    "source_name": "housing",
    "plane": "{\"axis\": \"Z\", \"offset\": 15.0}",
    "keep": "both"
  }
}
```

**Example response:**

```json
{
  "above": { "name": "housing_split_above", "volume_mm3": 22000.00 },
  "below": { "name": "housing_split_below", "volume_mm3": 30400.00 }
}
```

**Tips:**
- When `keep` is `"both"`, two models are created: `<name>_above` and `<name>_below`.
- Use an offset plane to split at a specific Z height, e.g., to separate a lid from a base.

---

### `add_text`

Emboss (raised) or deboss (cut into) text on a face of a model.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the new model with text |
| `source_name` | string | *required* | Name of the existing model |
| `text` | string | *required* | Text string to apply |
| `face` | string | `"top"` | Target face: `"top"`, `"bottom"`, `"front"`, `"back"`, `"left"`, `"right"` |
| `font_size` | float | `10` | Font size in mm |
| `depth` | float | `1.0` | Depth/height of text in mm |
| `font` | string | `"Arial"` | Font family name |
| `emboss` | bool | `True` | `True` for raised text (emboss), `False` for cut text (deboss) |

**Example usage:**

```json
{
  "name": "add_text",
  "arguments": {
    "name": "labeled_box",
    "source_name": "box",
    "text": "V2.1",
    "face": "front",
    "font_size": 8,
    "depth": 0.5,
    "emboss": false
  }
}
```

**Example response:**

```json
{
  "name": "labeled_box",
  "bbox": { "x": 50.0, "y": 30.0, "z": 20.0 },
  "text": "V2.1",
  "face": "front",
  "method": "deboss"
}
```

**Tips:**
- Debossed text (`emboss: false`) is more durable and easier to print than raised text.
- Font availability depends on fonts installed on the host system.

---

### `create_threaded_hole`

Add a threaded hole (tap drill or heat-set insert) to a model at a specified position.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the new model |
| `source_name` | string | *required* | Name of the existing model |
| `position` | string (JSON) | *required* | Hole center as `[x, y, z]` |
| `thread_spec` | string | `"M3"` | Metric thread size: `M2` through `M10` |
| `depth` | float | `10` | Hole depth in mm |
| `insert` | bool | `False` | If `True`, uses heat-set insert drill diameter instead of tap drill |

**Thread specifications:**

| Spec | Tap Drill (mm) | Insert Drill (mm) |
|------|----------------|-------------------|
| M2 | 1.6 | 3.2 |
| M2.5 | 2.05 | 3.5 |
| M3 | 2.5 | 4.0 |
| M4 | 3.3 | 5.0 |
| M5 | 4.2 | 6.0 |
| M6 | 5.0 | 7.0 |
| M8 | 6.8 | 9.5 |
| M10 | 8.5 | 12.0 |

**Example usage:**

```json
{
  "name": "create_threaded_hole",
  "arguments": {
    "name": "bracket_m3",
    "source_name": "bracket",
    "position": "[15, 0, 5]",
    "thread_spec": "M3",
    "depth": 8,
    "insert": true
  }
}
```

**Example response:**

```json
{
  "name": "bracket_m3",
  "hole_diameter_mm": 4.0,
  "hole_type": "heat-set insert",
  "thread_spec": "M3",
  "depth_mm": 8
}
```

**Tips:**
- Use `insert: true` when you plan to press in brass heat-set inserts with a soldering iron. The larger diameter accommodates the insert's outer knurling.
- Position is in absolute model coordinates. Use `measure_model` first to understand the model's bounding box.

---

### `create_thread`

Create an ISO metric thread with real helical geometry. Generates external threads (for bolts/screws) or internal threads (for nuts) using bd_warehouse's IsoThread.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the thread model |
| `thread_spec` | string | `"M3"` | ISO metric size: `M2`, `M2.5`, `M3`, `M4`, `M5`, `M6`, `M8`, `M10` |
| `length` | float | `10.0` | Thread length in mm |
| `external` | bool | `true` | `true` for bolt/screw thread, `false` for nut thread |
| `hand` | string | `"right"` | Thread direction: `"right"` or `"left"` |
| `end_finishes` | string | `'["fade","square"]'` | JSON list of [start, end] finish: `"raw"`, `"fade"`, `"square"`, `"chamfer"` |
| `simple` | bool | `false` | Simplified geometry (faster, less detail) |

**Example usage:**

```json
{
  "name": "create_thread",
  "arguments": {
    "name": "m3_shaft",
    "thread_spec": "M3",
    "length": 20,
    "external": true
  }
}
```

**Example response:**

```json
{
  "name": "m3_shaft",
  "thread_spec": "M3",
  "type": "external",
  "major_diameter": 3.0,
  "pitch": 0.5,
  "length": 20.0,
  "hand": "right",
  "bbox": { "x": 3.0, "y": 3.0, "z": 20.0 },
  "volume": 120.5
}
```

**Tips:**
- Use `external=true` for bolts and screws, `external=false` for nut threads.
- Set `simple=true` for faster generation when thread detail isn't critical.
- The `"fade"` end finish tapers the thread over 90° of arc — good for bolt entry ends.
- Combine with `create_model` and `combine_models` to build complete bolts (thread + head).
- For 3D printing, threads M3 and larger print reliably at 0.2mm layer height.

---

## Analysis & Export

### `estimate_print`

Estimate print material usage, weight, filament length, and cost for a model.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name of an existing model |
| `infill_percent` | int | `15` | Infill percentage (0-100) |
| `layer_height` | float | `0.2` | Layer height in mm |
| `material` | string | `"PLA"` | Material: `"PLA"`, `"PETG"`, `"ABS"`, `"TPU"`, `"ASA"` |

**Material densities:**

| Material | Density (g/cm3) |
|----------|-----------------|
| PLA | 1.24 |
| PETG | 1.27 |
| ABS | 1.04 |
| TPU | 1.21 |
| ASA | 1.07 |

**Example usage:**

```json
{
  "name": "estimate_print",
  "arguments": {
    "name": "housing",
    "infill_percent": 20,
    "layer_height": 0.2,
    "material": "PETG"
  }
}
```

**Example response:**

```json
{
  "weight_g": 34.5,
  "filament_length_m": 11.2,
  "estimated_cost_usd": 0.69,
  "material": "PETG",
  "infill_percent": 20,
  "layer_height_mm": 0.2
}
```

**Tips:**
- Cost is estimated at $20/kg filament price.
- The calculation assumes 2 perimeters at 0.8mm width. Actual slicer results will vary slightly.

---

### `analyze_overhangs`

Identify faces that overhang beyond a given angle threshold, which may need support material when printing.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name of an existing model |
| `max_angle` | float | `45` | Maximum overhang angle in degrees (from vertical) before flagging |

**Example usage:**

```json
{
  "name": "analyze_overhangs",
  "arguments": {
    "name": "bracket",
    "max_angle": 45
  }
}
```

**Example response:**

```json
{
  "overhang_face_count": 3,
  "overhang_area_mm2": 185.4,
  "overhang_percentage": 5.9,
  "worst_overhangs": [
    { "face_index": 7, "angle_deg": 62.3, "area_mm2": 95.0 },
    { "face_index": 4, "angle_deg": 51.1, "area_mm2": 55.2 },
    { "face_index": 9, "angle_deg": 48.7, "area_mm2": 35.2 }
  ]
}
```

**Tips:**
- Most FDM printers handle up to 45 degrees without supports. Increase `max_angle` if you have good part cooling.
- Use `suggest_orientation` to find a rotation that minimizes overhangs.

---

### `suggest_orientation`

Automatically evaluate multiple print orientations and recommend the best ones. Tests 16 orientations (90-degree increments on X and Y axes) and scores each by overhang area, bed contact area, and build height.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name of an existing model |

**Example usage:**

```json
{
  "name": "suggest_orientation",
  "arguments": {
    "name": "bracket"
  }
}
```

**Example response:**

```json
{
  "candidates": [
    { "rank": 1, "rotation": [0, 0, 0], "score": 0.92, "overhang_area_mm2": 12.0, "bed_contact_mm2": 800.0, "height_mm": 15.0 },
    { "rank": 2, "rotation": [90, 0, 0], "score": 0.85, "overhang_area_mm2": 45.0, "bed_contact_mm2": 600.0, "height_mm": 20.0 },
    { "rank": 3, "rotation": [0, 90, 0], "score": 0.78, "overhang_area_mm2": 60.0, "bed_contact_mm2": 400.0, "height_mm": 40.0 }
  ]
}
```

**Tips:**
- After choosing an orientation, apply it with `transform_model` using the suggested `rotation` values.
- Lower overhang area and greater bed contact generally mean better print quality and less wasted support material.

---

### `section_view`

Generate a 2D cross-section of a model at a given plane, exported as an SVG file.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the section view output |
| `source_name` | string | *required* | Name of the existing model to section |
| `plane` | string | `"XY"` | Section plane: `"XY"`, `"XZ"`, or `"YZ"` |
| `offset` | float | `0.0` | Offset from the origin along the plane normal, in mm |

**Example usage:**

```json
{
  "name": "section_view",
  "arguments": {
    "name": "housing_section",
    "source_name": "housing",
    "plane": "XZ",
    "offset": 15.0
  }
}
```

**Example response:**

```json
{
  "name": "housing_section",
  "file": "/path/to/outputs/housing_section.svg",
  "plane": "XZ",
  "offset_mm": 15.0
}
```

**Tips:**
- Useful for inspecting internal features like wall thickness, infill patterns, or cavity geometry.
- Open the SVG in a browser or vector editor for precise measurement.

---

### `export_drawing`

Generate a multi-view technical drawing as an SVG, similar to an engineering drawing sheet.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name of an existing model |
| `views` | string (JSON) | `'["front","top","right"]'` | JSON list of views: `"front"`, `"back"`, `"right"`, `"left"`, `"top"`, `"bottom"`, `"iso"` |
| `page_size` | string | `"A4"` | Page size for the SVG layout |

**Example usage:**

```json
{
  "name": "export_drawing",
  "arguments": {
    "name": "bracket",
    "views": "[\"front\", \"top\", \"right\", \"iso\"]",
    "page_size": "A4"
  }
}
```

**Example response:**

```json
{
  "file": "/path/to/outputs/bracket_drawing.svg",
  "views": ["front", "top", "right", "iso"],
  "page_size": "A4"
}
```

---

### `split_model_by_color`

Split a model into separate STL files by face assignment for multi-material/multi-color printing (e.g., Bambu Studio AMS).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Base name for the output files |
| `source_name` | string | *required* | Name of the existing model |
| `assignments` | string (JSON) | *required* | JSON list of face-color-filament assignments (see below) |

**Assignment format:**

Each entry in the list is an object with:

| Key | Type | Description |
|-----|------|-------------|
| `faces` | string | Face direction (`"top"`, `"bottom"`, `"front"`, `"back"`, `"left"`, `"right"`) or `"rest"` for all remaining faces |
| `color` | string | Hex color code (for reference/preview) |
| `filament` | int | Filament/extruder index (0-based) |

**Example usage:**

```json
{
  "name": "split_model_by_color",
  "arguments": {
    "name": "label_box",
    "source_name": "labeled_box",
    "assignments": "[{\"faces\": \"top\", \"color\": \"#FF0000\", \"filament\": 1}, {\"faces\": \"rest\", \"color\": \"#FFFFFF\", \"filament\": 0}]"
  }
}
```

**Example response:**

```json
{
  "files": [
    { "file": "label_box_filament0.stl", "filament": 0, "color": "#FFFFFF" },
    { "file": "label_box_filament1.stl", "filament": 1, "color": "#FF0000" }
  ]
}
```

**Tips:**
- Import the separate STL files into Bambu Studio (or PrusaSlicer with MMU) and assign each to the correct filament slot.
- Use `"rest"` to catch all faces not explicitly assigned.

---

## Utility

### `shrinkage_compensation`

Scale a model to compensate for material shrinkage after printing. Applies a uniform scale of `1 / (1 - shrinkage_rate)`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the compensated model |
| `source_name` | string | *required* | Name of the existing model |
| `material` | string | `"PLA"` | Material type (determines shrinkage rate) |

**Shrinkage rates by material:**

| Material | Shrinkage |
|----------|-----------|
| PLA | 0.3% |
| PETG | 0.4% |
| ABS | 0.7% |
| ASA | 0.5% |
| TPU | 0.5% |
| Nylon | 1.5% |

**Example usage:**

```json
{
  "name": "shrinkage_compensation",
  "arguments": {
    "name": "housing_comp",
    "source_name": "housing",
    "material": "ABS"
  }
}
```

**Example response:**

```json
{
  "name": "housing_comp",
  "material": "ABS",
  "shrinkage_percent": 0.7,
  "scale_factor": 1.00705,
  "original_volume_mm3": 52400.00,
  "compensated_volume_mm3": 53510.00
}
```

**Tips:**
- Most important for parts that must mate tightly with other components (press-fits, snap-fits, enclosures).
- Nylon has the highest shrinkage at 1.5% and benefits the most from compensation.

---

### `pack_models`

Arrange multiple models on the XY build plane with padding between them, aligning all bases to Z=0. Useful for preparing a multi-part print plate.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the packed arrangement |
| `model_names` | string (JSON) | *required* | JSON list of model names to pack |
| `padding` | float | `5.0` | Minimum gap between models in mm |

**Example usage:**

```json
{
  "name": "pack_models",
  "arguments": {
    "name": "print_plate",
    "model_names": "[\"bracket\", \"knob\", \"spacer\"]",
    "padding": 8.0
  }
}
```

**Example response:**

```json
{
  "name": "print_plate",
  "positions": [
    { "model": "bracket", "x": 0.0, "y": 0.0 },
    { "model": "knob", "x": 52.0, "y": 0.0 },
    { "model": "spacer", "x": 52.0, "y": 38.0 }
  ]
}
```

---

### `convert_format`

Convert a 3D file between formats without storing it as a model in the server. Pure file-to-file conversion.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_path` | string | *required* | Absolute path to the input file |
| `output_path` | string | *required* | Absolute path for the output file |

**Supported formats:** `.stl`, `.step` / `.stp`, `.brep`, `.3mf`

**Example usage:**

```json
{
  "name": "convert_format",
  "arguments": {
    "input_path": "/Users/bryan/models/part.step",
    "output_path": "/Users/bryan/models/part.3mf"
  }
}
```

**Example response:**

```json
{
  "input": "/Users/bryan/models/part.step",
  "output": "/Users/bryan/models/part.3mf",
  "size_bytes": 41200
}
```

---

## Parametric Components

### `create_enclosure`

Generate a parametric two-part enclosure (body + lid) with optional features. Creates two models: `<name>_body` and `<name>_lid`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Base name (produces `<name>_body` and `<name>_lid`) |
| `inner_width` | float | *required* | Interior width in mm |
| `inner_depth` | float | *required* | Interior depth in mm |
| `inner_height` | float | *required* | Interior height in mm |
| `wall` | float | `2.0` | Wall thickness in mm |
| `lid_type` | string | `"snap"` | `"snap"` (alignment ridge) or `"screw"` (corner screw holes) |
| `features` | string (JSON) | `"[]"` | JSON list of features: `"vent_slots"`, `"screw_posts"`, `"cable_hole"` |

**Example usage:**

```json
{
  "name": "create_enclosure",
  "arguments": {
    "name": "sensor_box",
    "inner_width": 60,
    "inner_depth": 40,
    "inner_height": 25,
    "wall": 2.5,
    "lid_type": "screw",
    "features": "[\"vent_slots\", \"cable_hole\"]"
  }
}
```

**Example response:**

```json
{
  "body": { "name": "sensor_box_body", "bbox": { "x": 65.0, "y": 45.0, "z": 27.5 } },
  "lid": { "name": "sensor_box_lid", "bbox": { "x": 65.0, "y": 45.0, "z": 4.0 } },
  "lid_type": "screw",
  "features": ["vent_slots", "cable_hole"]
}
```

**Tips:**
- The snap-fit lid includes an alignment ridge for a friction fit.
- The screw lid adds M3-sized holes in all four corners of both the body and lid.
- `"screw_posts"` adds internal mounting posts for attaching a PCB.

---

### `create_gear`

Generate a spur gear using the bd_warehouse library.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the gear model |
| `module` | float | `1.0` | Gear module (tooth size parameter) in mm |
| `teeth` | int | `20` | Number of teeth |
| `pressure_angle` | float | `20` | Pressure angle in degrees |
| `thickness` | float | `5.0` | Gear thickness (face width) in mm |
| `bore` | float | `0` | Center bore diameter in mm (0 = no bore) |

**Example usage:**

```json
{
  "name": "create_gear",
  "arguments": {
    "name": "drive_gear",
    "module": 1.5,
    "teeth": 24,
    "pressure_angle": 20,
    "thickness": 8.0,
    "bore": 5.0
  }
}
```

**Example response:**

```json
{
  "name": "drive_gear",
  "pitch_diameter_mm": 36.0,
  "outer_diameter_mm": 39.0,
  "module": 1.5,
  "teeth": 24
}
```

**Tips:**
- Two meshing gears must share the same module and pressure angle.
- Pitch diameter = module x teeth. Use this to calculate center-to-center distance between mating gears.

---

### `create_snap_fit`

Generate a cantilever snap-fit clip for joining two parts.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the snap-fit model |
| `snap_type` | string | `"cantilever"` | Snap-fit type (currently `"cantilever"`) |
| `params` | string (JSON) | `"{}"` | JSON object with dimensional parameters |

**Parameters (in the `params` JSON):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `beam_length` | float | `10` | Length of the cantilever beam in mm |
| `beam_width` | float | `5` | Width of the beam in mm |
| `beam_thickness` | float | `1.5` | Thickness of the beam in mm |
| `hook_depth` | float | `1.0` | Depth of the hook overhang in mm |
| `hook_length` | float | `2.0` | Length of the hook in mm |

**Example usage:**

```json
{
  "name": "create_snap_fit",
  "arguments": {
    "name": "clip",
    "snap_type": "cantilever",
    "params": "{\"beam_length\": 12, \"beam_width\": 6, \"beam_thickness\": 1.5, \"hook_depth\": 1.2}"
  }
}
```

**Example response:**

```json
{
  "name": "clip",
  "snap_type": "cantilever",
  "bbox": { "x": 6.0, "y": 1.5, "z": 13.2 }
}
```

**Tips:**
- Use `combine_models` to attach the snap-fit to your enclosure body.
- Print the beam along its length (not bridging) for maximum strength.

---

### `create_hinge`

Generate a two-part pin hinge. Creates `<name>_leaf_a` and `<name>_leaf_b`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Base name (produces `<name>_leaf_a` and `<name>_leaf_b`) |
| `hinge_type` | string | `"pin"` | Hinge type (currently `"pin"`) |
| `params` | string (JSON) | `"{}"` | JSON object with dimensional parameters |

**Parameters (in the `params` JSON):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `width` | float | `30` | Hinge width in mm |
| `leaf_length` | float | `20` | Length of each leaf in mm |
| `leaf_thickness` | float | `2` | Thickness of each leaf in mm |
| `pin_diameter` | float | `3` | Pin diameter in mm |
| `clearance` | float | `0.3` | Clearance between interlocking barrels in mm |
| `barrel_count` | int | `3` | Number of interlocking barrel segments |

**Example usage:**

```json
{
  "name": "create_hinge",
  "arguments": {
    "name": "lid_hinge",
    "hinge_type": "pin",
    "params": "{\"width\": 40, \"leaf_length\": 25, \"pin_diameter\": 3, \"clearance\": 0.3, \"barrel_count\": 5}"
  }
}
```

**Example response:**

```json
{
  "leaf_a": { "name": "lid_hinge_leaf_a", "bbox": { "x": 40.0, "y": 25.0, "z": 5.0 } },
  "leaf_b": { "name": "lid_hinge_leaf_b", "bbox": { "x": 40.0, "y": 25.0, "z": 5.0 } }
}
```

**Tips:**
- Use an odd `barrel_count` so that one leaf has more barrels, providing a natural "male" and "female" side.
- A clearance of 0.3mm works well for most FDM printers. Increase to 0.4mm for lower-resolution printers.
- The hinge requires a separate pin (e.g., a piece of 3mm filament) to assemble.

---

### `create_dovetail`

Generate a dovetail joint (male or female half) for interlocking two parts.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the dovetail model |
| `dovetail_type` | string | `"male"` | `"male"` (trapezoidal protrusion) or `"female"` (cavity in a block) |
| `width` | float | `20` | Width of the dovetail in mm |
| `height` | float | `10` | Height of the dovetail in mm |
| `depth` | float | `15` | Depth (slide length) in mm |
| `angle` | float | `10` | Dovetail angle in degrees |
| `clearance` | float | `0.2` | Clearance added to the female part in mm |

**Example usage:**

```json
{
  "name": "create_dovetail",
  "arguments": {
    "name": "rail_male",
    "dovetail_type": "male",
    "width": 25,
    "height": 8,
    "depth": 30,
    "angle": 12
  }
}
```

```json
{
  "name": "create_dovetail",
  "arguments": {
    "name": "rail_female",
    "dovetail_type": "female",
    "width": 25,
    "height": 8,
    "depth": 30,
    "angle": 12,
    "clearance": 0.25
  }
}
```

**Example response:**

```json
{
  "name": "rail_male",
  "dovetail_type": "male",
  "bbox": { "x": 25.0, "y": 15.0, "z": 8.0 }
}
```

**Tips:**
- Always create the male and female parts with the same `width`, `height`, `depth`, and `angle` so they mate correctly.
- The `clearance` on the female part ensures a sliding fit. Increase for looser tolerance.
- Use `combine_models` (subtract) to cut a dovetail slot into an existing part.

---

### `generate_label`

Create a flat label plate with embossed text, optionally including a QR code. Automatically exports an STL.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the label model |
| `text` | string | *required* | Text to emboss on the label |
| `size` | string (JSON) | `"[60,20,2]"` | Label dimensions as `[width, height, thickness]` in mm |
| `font_size` | float | `8` | Font size for the text in mm |
| `qr_data` | string | `""` | Data to encode as a QR code (empty string = no QR code) |

**Example usage:**

```json
{
  "name": "generate_label",
  "arguments": {
    "name": "asset_tag",
    "text": "SN-00421",
    "size": "[70, 25, 2]",
    "font_size": 10,
    "qr_data": "https://inventory.example.com/asset/421"
  }
}
```

**Example response:**

```json
{
  "name": "asset_tag",
  "bbox": { "x": 70.0, "y": 25.0, "z": 2.6 },
  "has_qr": true,
  "exports": ["asset_tag.stl"]
}
```

**Tips:**
- Text is embossed 0.6mm above the base plate surface.
- The QR code is placed in the right portion of the label; keep the label wide enough to fit both text and QR.
- QR code generation requires the `qrcode` Python package (`pip install qrcode`).
- Print with a color change at the text layer height for high-contrast labels, or use the multi-material workflow via `split_model_by_color`.

---

## Community

### `search_models`

Search for publicly shared 3D models on Thingiverse.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | *required* | Search query string |
| `source` | string | `"thingiverse"` | Search source (currently only `"thingiverse"`) |
| `max_results` | int | `10` | Maximum number of results to return |

**Example usage:**

```json
{
  "name": "search_models",
  "arguments": {
    "query": "raspberry pi 4 case",
    "source": "thingiverse",
    "max_results": 5
  }
}
```

**Example response:**

```json
{
  "results": [
    {
      "title": "Raspberry Pi 4 Case with Fan Mount",
      "author": "maker42",
      "url": "https://www.thingiverse.com/thing:4150001",
      "thumbnail": "https://cdn.thingiverse.com/...",
      "like_count": 312,
      "download_count": 18500
    },
    {
      "title": "Modular RPi4 Enclosure",
      "author": "printlab",
      "url": "https://www.thingiverse.com/thing:4230042",
      "thumbnail": "https://cdn.thingiverse.com/...",
      "like_count": 189,
      "download_count": 9200
    }
  ]
}
```

**Tips:**
- Requires the `THINGIVERSE_API_KEY` environment variable to be set. Obtain an API key from the [Thingiverse developer portal](https://www.thingiverse.com/developers).
- Use specific search terms for better results (e.g., "M3 knurled thumb nut" rather than "nut").

---

## Publishing

### `publish_github_release`

Upload model files to GitHub Releases as release assets.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | Yes | — | Model name (must exist in current session) |
| `repo` | string | Yes | — | GitHub repo in `owner/repo` format |
| `tag` | string | Yes | — | Release tag (e.g. `v1.0.0`) |
| `description` | string | No | `""` | Release description/notes |
| `formats` | string | No | `'["stl", "step"]'` | JSON list of formats to upload |
| `draft` | bool | No | `false` | Create as draft release |

**Authentication:** Uses `gh` CLI (preferred) or `GITHUB_TOKEN` environment variable.

**Example:**
```
publish_github_release(
    name="bracket",
    repo="brs077/my-models",
    tag="bracket-v1.0",
    description="Wall-mount bracket, 3mm thick"
)
```

**Response:**
```json
{
  "success": true,
  "method": "gh_cli",
  "release_url": "https://github.com/brs077/my-models/releases/tag/bracket-v1.0",
  "tag": "bracket-v1.0",
  "repo": "brs077/my-models",
  "files_uploaded": ["bracket.stl", "bracket.step"]
}
```

---

### `publish_thingiverse`

Create a Thing on Thingiverse and upload the STL file.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | Yes | — | Model name (must exist in current session) |
| `title` | string | Yes | — | Thing title on Thingiverse |
| `description` | string | No | `""` | Thing description (supports markdown) |
| `tags` | string | No | `'["3dprinting"]'` | JSON list of tags |
| `category` | string | No | `"3D Printing"` | Thingiverse category name |
| `is_wip` | bool | No | `true` | Publish as work-in-progress |

**Authentication:** Requires `THINGIVERSE_TOKEN` environment variable (OAuth access token from https://www.thingiverse.com/developers).

**Example:**
```
publish_thingiverse(
    name="organizer",
    title="Desk Organizer with Pen Holder",
    tags='["organizer", "desk", "office"]'
)
```

**Response:**
```json
{
  "success": true,
  "thing_id": 12345678,
  "thing_url": "https://www.thingiverse.com/thing:12345678",
  "title": "Desk Organizer with Pen Holder",
  "file_uploaded": "organizer.stl",
  "is_wip": true,
  "note": "Published as WIP. Edit on Thingiverse to add images and finalize."
}
```

---

### `publish_myminifactory`

Create an object on MyMiniFactory and upload the STL file.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | Yes | — | Model name (must exist in current session) |
| `title` | string | Yes | — | Object title on MyMiniFactory |
| `description` | string | No | `""` | Object description |
| `tags` | string | No | `'["3dprinting"]'` | JSON list of tags |
| `category_id` | int | No | `0` | MyMiniFactory category ID |

**Authentication:** Requires `MYMINIFACTORY_TOKEN` environment variable (OAuth access token from https://www.myminifactory.com/api-documentation).

**Example:**
```
publish_myminifactory(
    name="gear_20t",
    title="20-Tooth Spur Gear Module 1",
    tags='["gear", "mechanical"]'
)
```

**Response:**
```json
{
  "success": true,
  "object_id": 987654,
  "object_url": "https://www.myminifactory.com/object/3d-print-987654",
  "title": "20-Tooth Spur Gear Module 1",
  "file_uploaded": "gear_20t.stl",
  "status": "draft",
  "note": "Published as draft. Visit MyMiniFactory to add images, set category, and publish."
}
```

---

### `publish_cults3d`

Create a listing on Cults3D via their GraphQL API.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | Yes | — | Model name (must exist in current session) |
| `title` | string | Yes | — | Creation title on Cults3D |
| `description` | string | No | `""` | Creation description (HTML allowed) |
| `tags` | string | No | `'["3dprinting"]'` | JSON list of tags |
| `license` | string | No | `"creative_commons_attribution"` | License type |
| `free` | bool | No | `true` | Publish as free model |
| `price_cents` | int | No | `0` | Price in cents (if `free=false`) |

**Authentication:** Requires `CULTS3D_API_KEY` environment variable (from https://cults3d.com/en/pages/api).

**Note:** Cults3D does not support direct file upload via API. The listing is created as a draft — you must upload files through their web interface.

**Example:**
```
publish_cults3d(
    name="bracket",
    title="Adjustable Wall Bracket",
    tags='["bracket", "wall mount", "functional"]',
    free=true
)
```

**Response:**
```json
{
  "success": true,
  "creation_id": "abc123",
  "creation_url": "https://cults3d.com/en/3d-model/...",
  "slug": "adjustable-wall-bracket",
  "title": "Adjustable Wall Bracket",
  "status": "draft",
  "stl_path": "/path/to/outputs/bracket.stl",
  "note": "Created as draft. Upload the STL file manually at the creation URL."
}
```

**Tips:**
- All publishing tools default to draft/WIP status for safety — review on the platform before going live.
- GitHub Releases is the most reliable option (no OAuth flow, works with `gh` CLI or a PAT).
- Platforms without APIs (Printables, MakerWorld, Thangs) require manual upload — use `export_model` to get the files.
