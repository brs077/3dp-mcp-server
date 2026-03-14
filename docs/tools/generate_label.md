# `generate_label`

**Category:** Parametric Components

Create a flat label plate with embossed text, optionally including a QR code. Automatically exports an STL.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the label model |
| `text` | string | *required* | Text to emboss on the label |
| `size` | string (JSON) | `"[60,20,2]"` | Label dimensions as `[width, height, thickness]` in mm |
| `font_size` | float | `8` | Font size for the text in mm |
| `qr_data` | string | `""` | Data to encode as a QR code (empty string = no QR code) |

**Example usage:**

```json
{
  "name": "generate_label",
  "arguments": {
    "name": "asset_tag",
    "text": "SN-00421",
    "size": "[70, 25, 2]",
    "font_size": 10,
    "qr_data": "https://inventory.example.com/asset/421"
  }
}
```

**Example response:**

```json
{
  "name": "asset_tag",
  "bbox": { "x": 70.0, "y": 25.0, "z": 2.6 },
  "has_qr": true,
  "exports": ["asset_tag.stl"]
}
```

**Tips:**
- Text is embossed 0.6mm above the base plate surface.
- The QR code is placed in the right portion of the label; keep the label wide enough to fit both text and QR.
- QR code generation requires the `qrcode` Python package (`pip install qrcode`).
- Print with a color change at the text layer height for high-contrast labels, or use the multi-material workflow via `split_model_by_color`.

---

[Back to Tool Index](../README.md)
