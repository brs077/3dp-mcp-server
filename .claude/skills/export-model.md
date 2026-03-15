# export-model

Export a loaded model to STL, STEP, or 3MF format.

## When to use

Use when the user wants to export/save a model to a specific file format.

## Instructions

1. Confirm the model name exists in the session (use `list_models` if unsure)
2. Call `export_model` with the desired format
3. Return the file path to the user

## Parameters

- `name` (required): Name of the model to export
- `format` (default: `"stl"`): Export format — `"stl"`, `"step"`, or `"3mf"`

## Example

```
export_model(name="bracket", format="step")
```
