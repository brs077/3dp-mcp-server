# suggest-orientation

Suggest optimal print orientation to minimize supports and maximize bed adhesion.

## When to use

Use when the user wants to find the best way to orient a model on the build plate for printing.

## Instructions

1. Call `suggest_orientation` with the model name
2. Present the best orientation and top 5 candidates
3. Each candidate shows: rotation angles, overhang area, bed contact area, height, score

## Parameters

- `name` (required): Name of the model to analyze

## Details

Tests 16 rotation combinations (rx: 0/90/180/270, ry: 0/90/180/270) and scores by: `overhang_area - bed_contact_area × 2 + height × 0.5` (lower is better).

## Example

```
suggest_orientation(name="bracket")
```
