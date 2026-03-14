# `section_view`

**Category:** Analysis & Export

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

[Back to Tool Index](../README.md)
