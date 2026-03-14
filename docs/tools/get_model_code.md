# `get_model_code`

**Category:** Core

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

[Back to Tool Index](../README.md)
