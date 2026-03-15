# section-view

Generate a 2D cross-section of a model and export as SVG.

## When to use

Use when the user wants to see the internal structure or cross-section of a model.

## Instructions

1. Call `section_view` with the source model, cutting plane, and optional offset
2. Returns an SVG file path showing the cross-section

## Parameters

- `name` (required): Name for the section view
- `source_name` (required): Name of the model to section
- `plane` (default: `"XY"`): Cutting plane — `"XY"`, `"XZ"`, or `"YZ"`
- `offset` (default: `0.0`): Offset distance from origin along the plane normal

## Example

```
section_view(
  name="bracket_section",
  source_name="bracket",
  plane="XZ",
  offset=5.0
)
```
