# add-text

Emboss or deboss text onto a face of a model.

## When to use

Use when the user wants to add labels, branding, version numbers, or any text to a 3D model surface.

## Instructions

1. Call `add_text` with the source model, text content, and target face
2. Use `emboss=True` (default) for raised text, `emboss=False` for engraved text

## Parameters

- `name` (required): Name for the model with text
- `source_name` (required): Name of the model to add text to
- `text` (required): Text string to add
- `face` (default: `"top"`): Target face — `"top"`, `"bottom"`, `"front"`, `"back"`, `"left"`, `"right"`
- `font_size` (default: `10.0`): Font size in mm
- `depth` (default: `1.0`): Text depth in mm
- `font` (default: `"Arial"`): Font name
- `emboss` (default: `True`): `True` for raised text, `False` for engraved

## Example

```
add_text(
  name="box_labeled",
  source_name="box",
  text="v1.0",
  face="top",
  font_size=8,
  depth=0.5,
  emboss=True
)
```
