# analyze-printability

Check if a model is suitable for FDM 3D printing on a Bambu Lab X1C (256x256x256mm).

## When to use

Use after creating or modifying a model to validate it's printable. Always run this before declaring a model done.

## Instructions

1. Call `analyze_printability` with the model name
2. Review the result: "PRINTABLE" or "REVIEW NEEDED" with issue list
3. If issues found, suggest fixes to the user

## Parameters

- `name` (required): Name of the model to analyze
- `min_wall_mm` (default: `0.8`): Minimum wall thickness in mm

## Checks performed

- Volume > 0 (valid solid)
- Solid count (single body preferred)
- Dimensions fit build volume (256x256x256mm)
- Face count validation
- Area/volume ratio (thin wall detection)

## Example

```
analyze_printability(name="bracket", min_wall_mm=0.8)
```
