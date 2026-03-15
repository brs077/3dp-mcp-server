# pack-models

Arrange multiple models compactly on the build plate for batch printing.

## When to use

Use when the user wants to print multiple parts at once and needs them arranged efficiently on the build plate.

## Instructions

1. Ensure all models exist in the session
2. Call `pack_models` with the list of model names
3. Returns positions for each model on the build plate

## Parameters

- `name` (required): Name for the packed arrangement
- `model_names` (required): JSON list of model names — e.g. `'["part_a", "part_b"]'`
- `padding` (default: `5.0`): Spacing between models in mm

## Example

```
pack_models(
  name="print_batch",
  model_names='["bracket", "clip", "spacer"]',
  padding=5.0
)
```
