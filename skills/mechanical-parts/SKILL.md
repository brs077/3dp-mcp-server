---
name: mechanical-parts
description: Create mechanical parts — threads, fasteners, bearings, sprockets, flanges, pipes, and OpenBuilds linear motion parts using bd_warehouse.
---

# Mechanical Parts Design

Help the user create precise mechanical parts using the bd_warehouse parametric library tools.

## Available Tools

| Tool | Use Case |
|------|----------|
| `create_thread` | Threaded shafts, nut bores, bottle threads, lead screws |
| `create_fastener` | Screws, nuts, washers, heat-set inserts (14 types) |
| `create_bearing` | Ball bearings, roller bearings (5 types) |
| `create_sprocket` | Chain sprockets (ANSI #25–#80) |
| `create_flange` | ASME B16.5 pipe flanges (5 types) |
| `create_pipe` | Simple pipe/tube sections |
| `create_openbuilds_part` | V-Slot rails, C-Beam rails, lead screws |

## Workflow

1. Clarify the user's mechanical requirements — thread size, fastener type, tolerances
2. Select the appropriate tool and parameters
3. Call the tool to generate the part
4. Call `measure_model` to verify dimensions
5. Call `analyze_printability` to check FDM suitability
6. Use `combine_models` to integrate with other parts if needed

## Thread Selection Guide

- **ISO threads** (`thread_type="iso"`): Standard metric bolts/nuts. Specify `major_diameter` and `pitch`.
- **ACME threads** (`thread_type="acme"`): Power screws, vises, lead screws. Specify `size` (e.g. "3/8").
- **Metric Trapezoidal** (`thread_type="metric_trapezoidal"`): Metric lead screws. Specify `size` (e.g. "10x2").
- **Plastic Bottle** (`thread_type="plastic_bottle"`): ASTM D2911 bottle caps. Specify `size` (e.g. "L38SP400"). Use `manufacturing_compensation=0.2` for FDM.

## Fastener Quick Reference

Common sizes: M2, M2.5, M3, M4, M5, M6, M8, M10. Format: "M3-0.5" (diameter-pitch).

- `simple=True` (default): Fast generation without thread detail — good for fit-checks and assemblies
- `simple=False`: Full thread geometry — use for final prints or when thread detail matters

## FDM Printing Tips

- Threads: Use `manufacturing_compensation=0.2` for better FDM fit on bottle threads
- Fasteners: Generate with `simple=True` for assembly visualization, `simple=False` for printable threads
- Bearings: These are reference models — print housings around them using `combine_models` subtract
- Set `external=False` for female/internal threads (nut bores, threaded holes)
