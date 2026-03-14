# `import_model`

**Category:** Transform & Combine

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

[Back to Tool Index](../README.md)
