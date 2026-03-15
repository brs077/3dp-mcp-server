# create-model

Create a 3D model by executing build123d Python code.

## When to use

Use when the user wants to create a new 3D model, part, or shape from scratch using build123d code.

## Instructions

1. Ask what the user wants to model if not specified
2. Write build123d Python code that assigns the final geometry to `result`
3. Call the `create_model` MCP tool with a descriptive `name` and the `code`
4. The import `from build123d import *` is auto-prepended — do not include it
5. After creation, run `analyze_printability` to check for FDM printing issues

## Parameters

- `name` (required): Unique name for the model
- `code` (required): build123d Python code — must assign final shape to `result`

## Example

```
create_model(
  name="bracket",
  code="with BuildPart() as p:\n    Box(40, 20, 5)\nresult = p.part"
)
```

## build123d patterns

- Basic shapes: `Box(w, d, h)`, `Cylinder(r, h)`, `Sphere(r)`
- Boolean ops: `+` (union), `-` (subtract), `&` (intersect)
- Positioning: `Pos(x, y, z) * shape`
- Fillets: `fillet(result.edges(), radius=1)`
- Chamfers: `chamfer(result.edges(), length=0.5)`
- Units are always millimeters
