# 3DP MCP Server — Tool Reference

Complete documentation for all 29 MCP tools provided by `3dp-mcp-server`. Each tool has its own detailed documentation page with parameters, examples, and tips.

---

## Core Tools

| Tool | Category | Description |
|------|----------|-------------|
| [create_model](tools/create_model.md) | Core | Execute build123d Python code to create a 3D model |
| [export_model](tools/export_model.md) | Core | Export a model to STL, STEP, or 3MF format |
| [measure_model](tools/measure_model.md) | Core | Return precise measurements for a model |
| [analyze_printability](tools/analyze_printability.md) | Core | Check whether a model is suitable for FDM 3D printing |
| [list_models](tools/list_models.md) | Core | List all models currently loaded in the server session |
| [get_model_code](tools/get_model_code.md) | Core | Retrieve the build123d source code used to create a model |

## Transform & Combine

| Tool | Category | Description |
|------|----------|-------------|
| [transform_model](tools/transform_model.md) | Transform & Combine | Apply spatial transformations (scale, rotate, mirror, translate) |
| [combine_models](tools/combine_models.md) | Transform & Combine | Perform a Boolean operation between two models |
| [import_model](tools/import_model.md) | Transform & Combine | Import an external 3D model file into the server session |

## Modification

| Tool | Category | Description |
|------|----------|-------------|
| [shell_model](tools/shell_model.md) | Modification | Hollow out a solid model with optional openings |
| [split_model](tools/split_model.md) | Modification | Split a model along a plane into two halves |
| [add_text](tools/add_text.md) | Modification | Emboss or deboss text on a face of a model |
| [create_threaded_hole](tools/create_threaded_hole.md) | Modification | Add a threaded hole or heat-set insert hole to a model |

## Analysis & Export

| Tool | Category | Description |
|------|----------|-------------|
| [estimate_print](tools/estimate_print.md) | Analysis & Export | Estimate print material usage, weight, filament length, and cost |
| [analyze_overhangs](tools/analyze_overhangs.md) | Analysis & Export | Identify faces that overhang beyond a given angle threshold |
| [suggest_orientation](tools/suggest_orientation.md) | Analysis & Export | Evaluate multiple print orientations and recommend the best ones |
| [section_view](tools/section_view.md) | Analysis & Export | Generate a 2D cross-section of a model as SVG |
| [export_drawing](tools/export_drawing.md) | Analysis & Export | Generate a multi-view technical drawing as SVG |
| [split_model_by_color](tools/split_model_by_color.md) | Analysis & Export | Split a model into separate STLs for multi-color printing |

## Utility

| Tool | Category | Description |
|------|----------|-------------|
| [shrinkage_compensation](tools/shrinkage_compensation.md) | Utility | Scale a model to compensate for material shrinkage |
| [pack_models](tools/pack_models.md) | Utility | Arrange multiple models on the build plate with padding |
| [convert_format](tools/convert_format.md) | Utility | Convert a 3D file between formats |

## Parametric Components

| Tool | Category | Description |
|------|----------|-------------|
| [create_enclosure](tools/create_enclosure.md) | Parametric Components | Generate a parametric two-part enclosure (body + lid) |
| [create_gear](tools/create_gear.md) | Parametric Components | Generate a spur gear using bd_warehouse |
| [create_snap_fit](tools/create_snap_fit.md) | Parametric Components | Generate a cantilever snap-fit clip |
| [create_hinge](tools/create_hinge.md) | Parametric Components | Generate a two-part pin hinge |
| [create_dovetail](tools/create_dovetail.md) | Parametric Components | Generate a dovetail joint (male or female) |
| [generate_label](tools/generate_label.md) | Parametric Components | Create a flat label plate with embossed text and optional QR code |

## Community

| Tool | Category | Description |
|------|----------|-------------|
| [search_models](tools/search_models.md) | Community | Search for publicly shared 3D models on Thingiverse |
