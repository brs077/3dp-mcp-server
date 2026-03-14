# `add_text`

**Category:** Modification

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

[Back to Tool Index](../README.md)
