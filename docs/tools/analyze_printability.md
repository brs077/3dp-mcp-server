# `analyze_printability`

**Category:** Core

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

[Back to Tool Index](../README.md)
