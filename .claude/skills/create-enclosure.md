# create-enclosure

Generate a parametric two-part enclosure (body + lid) with optional features.

## When to use

Use when the user wants to create a box or enclosure for electronics, sensors, or any project that needs a body and lid.

## Instructions

1. Ask about interior dimensions if not specified
2. Call `create_enclosure` — creates two models: `{name}_body` and `{name}_lid`
3. Run `analyze_printability` on both parts

## Parameters

- `name` (required): Base name (produces `{name}_body` and `{name}_lid`)
- `inner_width` (required): Interior width in mm
- `inner_depth` (required): Interior depth in mm
- `inner_height` (required): Interior height in mm
- `wall` (default: `2.0`): Wall thickness in mm
- `lid_type` (default: `"snap"`): `"snap"` (friction fit ridge) or `"screw"` (M3 corner holes)
- `features` (default: `"[]"`): JSON list — `"vent_slots"`, `"screw_posts"`, `"cable_hole"`

## Example

```
create_enclosure(
  name="sensor_box",
  inner_width=60,
  inner_depth=40,
  inner_height=25,
  wall=2.5,
  lid_type="screw",
  features='["vent_slots", "cable_hole"]'
)
```
