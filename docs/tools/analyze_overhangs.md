# `analyze_overhangs`

**Category:** Analysis & Export

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

[Back to Tool Index](../README.md)
