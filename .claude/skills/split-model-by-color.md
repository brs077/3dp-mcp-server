# split-model-by-color

Split a model into separate STL files by face direction for multi-color printing.

## When to use

Use when the user wants to print a model in multiple colors using Bambu Studio or similar multi-material slicer.

## Instructions

1. Call `split_model_by_color` with face-to-filament assignments
2. Each assignment maps a face direction to a color and filament index
3. Returns a list of STL file paths, one per filament

## Parameters

- `name` (required): Base name for the split files
- `source_name` (required): Name of the model to split
- `assignments` (required): JSON list of assignments

## Assignment format

```json
[
  {"faces": "top", "color": "#FF0000", "filament": 1},
  {"faces": "rest", "color": "#FFFFFF", "filament": 0}
]
```

Supported faces: `"top"`, `"bottom"`, `"front"`, `"back"`, `"right"`, `"left"`, `"rest"`

## Example

```
split_model_by_color(
  name="box_multicolor",
  source_name="box",
  assignments='[{"faces": "top", "color": "#FF0000", "filament": 1}, {"faces": "rest", "color": "#FFFFFF", "filament": 0}]'
)
```
