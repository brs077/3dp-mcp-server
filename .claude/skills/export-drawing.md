# export-drawing

Generate a 2D technical drawing as SVG with multiple view projections.

## When to use

Use when the user wants a multi-view technical drawing (engineering drawing) of a model.

## Instructions

1. Call `export_drawing` with the model name and desired views
2. Returns an SVG file path with the technical drawing

## Parameters

- `name` (required): Name of the model to draw
- `views` (default: `'["front", "top", "right"]'`): JSON list of views — `"front"`, `"back"`, `"right"`, `"left"`, `"top"`, `"bottom"`, `"iso"`
- `page_size` (default: `"A4"`): Page size for the drawing

## Example

```
export_drawing(
  name="bracket",
  views='["front", "top", "right", "iso"]',
  page_size="A4"
)
```
