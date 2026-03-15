# create-snap-fit

Generate a snap-fit joint component for assembly.

## When to use

Use when the user needs a snap-fit connector for joining two printed parts without fasteners.

## Instructions

1. Call `create_snap_fit` with the desired parameters
2. Currently supports `"cantilever"` type only

## Parameters

- `name` (required): Name for the snap-fit model
- `snap_type` (default: `"cantilever"`): Type of snap-fit
- `params` (default: `"{}"`): JSON string with dimensions

## Params options

- `beam_length`: 10mm default
- `beam_width`: 5mm default
- `beam_thickness`: 1.5mm default
- `hook_depth`: 1.0mm default
- `hook_length`: 2.0mm default
- `clearance`: 0.2mm default

## Example

```
create_snap_fit(
  name="clip",
  snap_type="cantilever",
  params='{"beam_length": 12, "beam_width": 6, "hook_depth": 1.2}'
)
```
