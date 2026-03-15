# import-model

Import an STL or STEP file from disk into the server as a loaded model.

## When to use

Use when the user wants to load an existing 3D file for analysis, modification, or combination with other models.

## Instructions

1. Confirm the file path exists
2. Call `import_model` with a name and the file path
3. Supported formats: `.stl`, `.step`, `.stp`

## Parameters

- `name` (required): Name to assign the imported model
- `file_path` (required): Path to the STL or STEP file on disk

## Example

```
import_model(name="imported_part", file_path="/path/to/part.step")
```
