# create-dovetail

Generate a male or female dovetail joint.

## When to use

Use when the user needs a dovetail joint for interlocking two printed parts.

## Instructions

1. Call `create_dovetail` with the desired type and dimensions
2. Create both male and female parts for a complete joint

## Parameters

- `name` (required): Name for the dovetail model
- `dovetail_type` (default: `"male"`): `"male"` (solid profile) or `"female"` (void in block)
- `width` (default: `20.0`): Width in mm
- `height` (default: `10.0`): Height in mm
- `depth` (default: `15.0`): Depth in mm
- `angle` (default: `10.0`): Dovetail angle in degrees
- `clearance` (default: `0.2`): Clearance in mm (applied to female only)

## Example

```
create_dovetail(name="joint_male", dovetail_type="male", width=20, height=10)
create_dovetail(name="joint_female", dovetail_type="female", width=20, height=10)
```
