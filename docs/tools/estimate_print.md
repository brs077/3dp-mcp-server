# `estimate_print`

**Category:** Analysis & Export

Estimate print material usage, weight, filament length, and cost for a model.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name of an existing model |
| `infill_percent` | int | `15` | Infill percentage (0-100) |
| `layer_height` | float | `0.2` | Layer height in mm |
| `material` | string | `"PLA"` | Material: `"PLA"`, `"PETG"`, `"ABS"`, `"TPU"`, `"ASA"` |

**Material densities:**

| Material | Density (g/cm3) |
|----------|-----------------|
| PLA | 1.24 |
| PETG | 1.27 |
| ABS | 1.04 |
| TPU | 1.21 |
| ASA | 1.07 |

**Example usage:**

```json
{
  "name": "estimate_print",
  "arguments": {
    "name": "housing",
    "infill_percent": 20,
    "layer_height": 0.2,
    "material": "PETG"
  }
}
```

**Example response:**

```json
{
  "weight_g": 34.5,
  "filament_length_m": 11.2,
  "estimated_cost_usd": 0.69,
  "material": "PETG",
  "infill_percent": 20,
  "layer_height_mm": 0.2
}
```

**Tips:**
- Cost is estimated at $20/kg filament price.
- The calculation assumes 2 perimeters at 0.8mm width. Actual slicer results will vary slightly.

---

[Back to Tool Index](../README.md)
