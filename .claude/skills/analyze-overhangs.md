# analyze-overhangs

Analyze overhang faces that may need support material.

## When to use

Use when the user wants to check if a model has overhangs that will need support structures during printing.

## Instructions

1. Call `analyze_overhangs` with the model name
2. Present: total area, overhang area, overhang percentage, and worst overhangs
3. Suggest design changes or orientation adjustments if overhangs are significant

## Parameters

- `name` (required): Name of the model to analyze
- `max_angle` (default: `45.0`): Maximum overhang angle in degrees before flagging

## Example

```
analyze_overhangs(name="bracket", max_angle=45)
```
