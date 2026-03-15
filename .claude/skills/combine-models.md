# combine-models

Boolean combine two loaded models: union, subtract, or intersect.

## When to use

Use when the user wants to merge two models together, cut one from another, or find their intersection.

## Instructions

1. Ensure both models exist in the session
2. Call `combine_models` with the operation type
3. For subtract: model_a minus model_b (order matters)

## Parameters

- `name` (required): Name for the resulting combined model
- `model_a` (required): First model name
- `model_b` (required): Second model name
- `operation` (default: `"union"`): `"union"` (a + b), `"subtract"` (a - b), or `"intersect"` (a & b)

## Example

```
combine_models(
  name="box_with_hole",
  model_a="box",
  model_b="cylinder",
  operation="subtract"
)
```
