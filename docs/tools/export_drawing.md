# `export_drawing`

**Category:** Analysis & Export

Generate a multi-view technical drawing as an SVG, similar to an engineering drawing sheet.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name of an existing model |
| `views` | string (JSON) | `'["front","top","right"]'` | JSON list of views: `"front"`, `"back"`, `"right"`, `"left"`, `"top"`, `"bottom"`, `"iso"` |
| `page_size` | string | `"A4"` | Page size for the SVG layout |

**Example usage:**

```json
{
  "name": "export_drawing",
  "arguments": {
    "name": "bracket",
    "views": "[\"front\", \"top\", \"right\", \"iso\"]",
    "page_size": "A4"
  }
}
```

**Example response:**

```json
{
  "file": "/path/to/outputs/bracket_drawing.svg",
  "views": ["front", "top", "right", "iso"],
  "page_size": "A4"
}
```

---

[Back to Tool Index](../README.md)
