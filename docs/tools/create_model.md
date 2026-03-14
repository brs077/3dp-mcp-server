# `create_model`

**Category:** Core

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

[Back to Tool Index](../README.md)
