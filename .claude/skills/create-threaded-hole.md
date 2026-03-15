# create-threaded-hole

Add threaded or heat-set insert holes (M2-M10 ISO metric).

## When to use

Use when the user wants to add screw holes or heat-set insert holes to a model for mechanical assembly.

## Instructions

1. Call `create_threaded_hole` with the source model, position, and thread spec
2. Use `insert=True` for heat-set insert holes (wider diameter)

## Parameters

- `name` (required): Name for the model with hole
- `source_name` (required): Name of the model to modify
- `position` (required): JSON `[x, y, z]` — center of hole on model surface
- `thread_spec` (default: `"M3"`): ISO thread size — M2, M2.5, M3, M4, M5, M6, M8, M10
- `depth` (default: `10.0`): Hole depth in mm
- `insert` (default: `False`): `True` for heat-set insert holes

## Example

```
create_threaded_hole(
  name="box_with_holes",
  source_name="box",
  position="[10, 10, 0]",
  thread_spec="M3",
  depth=8.0,
  insert=False
)
```
