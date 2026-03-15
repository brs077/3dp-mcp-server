# measure-model

Measure a model's geometry: bounding box, volume, surface area, and face/edge counts.

## When to use

Use when the user wants to know dimensions, volume, surface area, or topology info about a model.

## Instructions

1. Call `measure_model` with the model name
2. Present the results clearly: bounding box dimensions, volume (mm³), surface area (mm²), face count, edge count

## Parameters

- `name` (required): Name of the model to measure

## Example

```
measure_model(name="bracket")
```
