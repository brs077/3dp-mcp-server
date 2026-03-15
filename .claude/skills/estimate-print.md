# estimate-print

Estimate filament usage, weight, cost, and print time for a model.

## When to use

Use when the user wants to know how much filament, time, or money a print will cost.

## Instructions

1. Call `estimate_print` with the model name and print settings
2. Present results: filament length (m), weight (g), cost (USD), time (min)

## Parameters

- `name` (required): Name of the model to estimate
- `infill_percent` (default: `15.0`): Infill density percentage
- `layer_height` (default: `0.2`): Layer height in mm
- `material` (default: `"PLA"`): Material — `"PLA"`, `"PETG"`, `"ABS"`, `"ASA"`, `"TPU"`, `"Nylon"`

## Example

```
estimate_print(
  name="bracket",
  infill_percent=20,
  layer_height=0.2,
  material="PETG"
)
```
