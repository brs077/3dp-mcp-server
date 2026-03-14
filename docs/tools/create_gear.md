# `create_gear`

**Category:** Parametric Components

Generate a spur gear using the bd_warehouse library.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Name for the gear model |
| `module` | float | `1.0` | Gear module (tooth size parameter) in mm |
| `teeth` | int | `20` | Number of teeth |
| `pressure_angle` | float | `20` | Pressure angle in degrees |
| `thickness` | float | `5.0` | Gear thickness (face width) in mm |
| `bore` | float | `0` | Center bore diameter in mm (0 = no bore) |

**Example usage:**

```json
{
  "name": "create_gear",
  "arguments": {
    "name": "drive_gear",
    "module": 1.5,
    "teeth": 24,
    "pressure_angle": 20,
    "thickness": 8.0,
    "bore": 5.0
  }
}
```

**Example response:**

```json
{
  "name": "drive_gear",
  "pitch_diameter_mm": 36.0,
  "outer_diameter_mm": 39.0,
  "module": 1.5,
  "teeth": 24
}
```

**Tips:**
- Two meshing gears must share the same module and pressure angle.
- Pitch diameter = module x teeth. Use this to calculate center-to-center distance between mating gears.

---

[Back to Tool Index](../README.md)
