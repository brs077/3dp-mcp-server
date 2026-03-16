# `create_thread`

**Category:** Parametric Components

Create an ISO metric thread with real helical geometry using bd_warehouse. Supports external threads (for bolts/screws) and internal threads (for nuts).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the thread model |
| `thread_spec` | string | `"M3"` | ISO metric size: `M2`, `M2.5`, `M3`, `M4`, `M5`, `M6`, `M8`, `M10` |
| `length` | float | `10.0` | Thread length in mm |
| `external` | bool | `true` | `true` for bolt/screw thread, `false` for nut thread |
| `hand` | string | `"right"` | Thread direction: `"right"` or `"left"` |
| `end_finishes` | string | `'["fade","square"]'` | JSON list of [start, end] finish: `"raw"`, `"fade"`, `"square"`, `"chamfer"` |
| `simple` | bool | `false` | Simplified geometry (faster, less detail) |

**Thread specifications:**

| Spec | Major Diameter (mm) | Pitch (mm) |
|------|--------------------:|----------:|
| M2 | 2.0 | 0.4 |
| M2.5 | 2.5 | 0.45 |
| M3 | 3.0 | 0.5 |
| M4 | 4.0 | 0.7 |
| M5 | 5.0 | 0.8 |
| M6 | 6.0 | 1.0 |
| M8 | 8.0 | 1.25 |
| M10 | 10.0 | 1.5 |

**Example usage (external M3 thread):**

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
  "success": true,
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

**Creating a complete bolt:**

1. `create_thread(name="shaft", thread_spec="M3", length=20)` — threaded shaft
2. `create_model(name="head", code="result = Cylinder(2.75, 3)")` — bolt head
3. `transform_model(name="head_pos", source="head", operations='{"translate":[0,0,20]}')` — position head
4. `combine_models(name="m3_bolt", model_a="shaft", model_b="head_pos", operation="union")` — join

**Tips:**
- Use `external=true` for bolts and screws, `external=false` for nut threads.
- Set `simple=true` for faster generation when thread detail isn't critical (e.g. visual mockups).
- The `"fade"` end finish tapers the thread over 90° of arc — good for the entry end of a bolt.
- Combine with `create_threaded_hole` for matching bolt-and-nut assemblies.
- For 3D printing, threads M3 and larger print reliably at 0.2mm layer height.

---

[Back to Tool Index](../README.md)
