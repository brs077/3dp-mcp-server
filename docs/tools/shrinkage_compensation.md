# `shrinkage_compensation`

**Category:** Utility

Scale a model to compensate for material shrinkage after printing. Applies a uniform scale of `1 / (1 - shrinkage_rate)`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the compensated model |
| `source_name` | string | *required* | Name of the existing model |
| `material` | string | `"PLA"` | Material type (determines shrinkage rate) |

**Shrinkage rates by material:**

| Material | Shrinkage |
|----------|-----------|
| PLA | 0.3% |
| PETG | 0.4% |
| ABS | 0.7% |
| ASA | 0.5% |
| TPU | 0.5% |
| Nylon | 1.5% |

**Example usage:**

```json
{
  "name": "shrinkage_compensation",
  "arguments": {
    "name": "housing_comp",
    "source_name": "housing",
    "material": "ABS"
  }
}
```

**Example response:**

```json
{
  "name": "housing_comp",
  "material": "ABS",
  "shrinkage_percent": 0.7,
  "scale_factor": 1.00705,
  "original_volume_mm3": 52400.00,
  "compensated_volume_mm3": 53510.00
}
```

**Tips:**
- Most important for parts that must mate tightly with other components (press-fits, snap-fits, enclosures).
- Nylon has the highest shrinkage at 1.5% and benefits the most from compensation.

---

[Back to Tool Index](../README.md)
