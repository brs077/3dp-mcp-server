# shrinkage-compensation

Scale a model to compensate for material shrinkage after printing.

## When to use

Use when the user needs precise dimensional accuracy and wants to pre-scale the model to account for material shrinkage.

## Instructions

1. Call `shrinkage_compensation` with the source model and material
2. Returns a new model scaled by `1 / (1 - shrinkage_percent)` for the specified material

## Parameters

- `name` (required): Name for the compensated model
- `source_name` (required): Name of the model to compensate
- `material` (default: `"PLA"`): Material — `"PLA"`, `"PETG"`, `"ABS"`, `"ASA"`, `"TPU"`, `"Nylon"`

## Shrinkage values

- PLA: 0.3%, PETG: 0.4%, ABS: 0.7%, ASA: 0.5%, TPU: 0.5%, Nylon: 1.5%

## Example

```
shrinkage_compensation(
  name="bracket_compensated",
  source_name="bracket",
  material="ABS"
)
```
