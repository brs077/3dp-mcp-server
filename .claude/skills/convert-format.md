# convert-format

Convert a 3D model file between formats (STL, STEP, 3MF, BREP).

## When to use

Use when the user wants to convert a 3D file from one format to another.

## Instructions

1. Call `convert_format` with the input and output file paths
2. Format is auto-detected from file extensions

## Parameters

- `input_path` (required): Path to the source file
- `output_path` (required): Path for the converted file

## Supported formats

STL, STEP (.step/.stp), 3MF, BREP — any combination.

## Example

```
convert_format(
  input_path="/path/to/model.stl",
  output_path="/path/to/model.step"
)
```
