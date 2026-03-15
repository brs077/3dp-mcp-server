# create-hinge

Generate a two-part pin hinge assembly.

## When to use

Use when the user needs a hinge mechanism for joining two parts that need to rotate relative to each other.

## Instructions

1. Call `create_hinge` — creates two models: `{name}_leaf_a` and `{name}_leaf_b`
2. Currently supports `"pin"` type only

## Parameters

- `name` (required): Base name (produces `{name}_leaf_a` and `{name}_leaf_b`)
- `hinge_type` (default: `"pin"`): Type of hinge
- `params` (default: `"{}"`): JSON string with dimensions

## Params options

- `width`: 30mm default
- `leaf_length`: 20mm default
- `leaf_thickness`: 2mm default
- `pin_diameter`: 3mm default
- `clearance`: 0.3mm default
- `barrel_count`: 3 default

## Example

```
create_hinge(
  name="box_hinge",
  hinge_type="pin",
  params='{"width": 25, "pin_diameter": 2.5, "barrel_count": 5}'
)
```
