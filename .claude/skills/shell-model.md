# shell-model

Hollow out a model, optionally leaving faces open.

## When to use

Use when the user wants to make a solid model hollow (like creating a container, box, or thin-walled part).

## Instructions

1. Call `shell_model` with the source model and wall thickness
2. Specify which faces to leave open if needed

## Parameters

- `name` (required): Name for the shelled model
- `source_name` (required): Name of the model to hollow
- `thickness` (default: `2.0`): Wall thickness in mm
- `open_faces` (default: `"[]"`): JSON list of faces to leave open — `"top"`, `"bottom"`, `"front"`, `"back"`, `"left"`, `"right"`

## Example

```
shell_model(
  name="box_hollow",
  source_name="box",
  thickness=1.5,
  open_faces='["top"]'
)
```
