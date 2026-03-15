# split-model

Split a model along a plane.

## When to use

Use when the user wants to cut a model into pieces — for printing in parts, inspection, or assembly.

## Instructions

1. Call `split_model` with the source model, plane, and which part(s) to keep
2. When `keep="both"`, two models are created: `{name}_above` and `{name}_below`

## Parameters

- `name` (required): Base name for the resulting model(s)
- `source_name` (required): Name of the model to split
- `plane` (default: `"XY"`): Split plane — `"XY"`, `"XZ"`, `"YZ"`, or JSON `{"axis": "Z", "offset": 10.5}`
- `keep` (default: `"both"`): Which part to keep — `"above"`, `"below"`, or `"both"`

## Example

```
split_model(
  name="bracket_split",
  source_name="bracket",
  plane='{"axis": "Z", "offset": 15}',
  keep="both"
)
```
