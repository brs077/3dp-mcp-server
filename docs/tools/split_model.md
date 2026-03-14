# `split_model`

**Category:** Modification

Split a model along a plane into two halves.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Base name for the split result(s) |
| `source_name` | string | *required* | Name of the existing model to split |
| `plane` | string | `"XY"` | Split plane: `"XY"`, `"XZ"`, `"YZ"`, or JSON `'{"axis":"Z","offset":10.5}'` for an offset plane |
| `keep` | string | `"both"` | Which half to keep: `"above"`, `"below"`, or `"both"` |

**Example usage (keep both halves with offset):**

```json
{
  "name": "split_model",
  "arguments": {
    "name": "housing_split",
    "source_name": "housing",
    "plane": "{\"axis\": \"Z\", \"offset\": 15.0}",
    "keep": "both"
  }
}
```

**Example response:**

```json
{
  "above": { "name": "housing_split_above", "volume_mm3": 22000.00 },
  "below": { "name": "housing_split_below", "volume_mm3": 30400.00 }
}
```

**Tips:**
- When `keep` is `"both"`, two models are created: `<name>_above` and `<name>_below`.
- Use an offset plane to split at a specific Z height, e.g., to separate a lid from a base.

---

[Back to Tool Index](../README.md)
