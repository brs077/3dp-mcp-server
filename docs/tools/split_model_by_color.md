# `split_model_by_color`

**Category:** Analysis & Export

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

[Back to Tool Index](../README.md)
