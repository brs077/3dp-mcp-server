# create-gear

Generate an involute spur gear.

## When to use

Use when the user wants to create a gear for mechanical assemblies or gear trains.

## Instructions

1. Call `create_gear` with the gear parameters
2. Uses bd_warehouse SpurGear if available, otherwise generates mathematically
3. Set `bore > 0` for a center shaft hole

## Parameters

- `name` (required): Name for the gear model
- `module` (default: `1.0`): Gear module (tooth size)
- `teeth` (default: `20`): Number of teeth
- `pressure_angle` (default: `20.0`): Pressure angle in degrees
- `thickness` (default: `5.0`): Gear thickness in mm
- `bore` (default: `0.0`): Center bore diameter in mm (0 = solid)

## Example

```
create_gear(
  name="drive_gear",
  module=1.5,
  teeth=24,
  thickness=8,
  bore=5.0
)
```
