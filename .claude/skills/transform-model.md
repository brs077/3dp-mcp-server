# transform-model

Scale, rotate, mirror, or translate a loaded model. Apply operations in order.

## When to use

Use when the user wants to resize, rotate, flip, or move a model without rewriting the creation code.

## Instructions

1. Call `transform_model` with a new name, the source model name, and operations JSON
2. Operations are applied in order if a list is provided

## Parameters

- `name` (required): New name for the transformed model
- `source_name` (required): Name of the existing model to transform
- `operations` (required): JSON string — single dict or list of dicts

## Supported operations

- `{"type": "scale", "value": 2.0}` — uniform scale
- `{"type": "scale", "value": [1.5, 1.0, 2.0]}` — per-axis scale
- `{"type": "rotate", "value": [0, 0, 45]}` — rotate [rx, ry, rz] degrees
- `{"type": "mirror", "value": "XY"}` — mirror across plane (XY, XZ, YZ)
- `{"type": "translate", "value": [10, 0, 5]}` — move [x, y, z] mm

## Example

```
transform_model(
  name="bracket_scaled",
  source_name="bracket",
  operations='[{"type": "scale", "value": 1.5}, {"type": "rotate", "value": [0, 0, 90]}]'
)
```
