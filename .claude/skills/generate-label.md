# generate-label

Create a 3D-printable label with embossed text and optional QR code.

## When to use

Use when the user wants to create a flat label, nameplate, or tag with text and optionally a QR code.

## Instructions

1. Call `generate_label` with the text and optional QR data
2. The label is a flat plate with raised text

## Parameters

- `name` (required): Name for the label model
- `text` (required): Text to emboss on the label
- `size` (default: `"[60, 20, 2]"`): JSON `[width, height, thickness]` in mm
- `font_size` (default: `8.0`): Font size in mm
- `qr_data` (default: `""`): Data to encode as QR code (empty = no QR)

## Example

```
generate_label(
  name="shelf_label",
  text="Parts Bin A",
  size="[80, 25, 2]",
  font_size=10,
  qr_data="https://inventory.example.com/bin-a"
)
```
