# `create_threaded_hole`

**Category:** Modification

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

[Back to Tool Index](../README.md)
