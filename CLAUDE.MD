# 3DP MCP Server

MCP server for 3D-printable CAD modeling with build123d, targeting STL export for Bambu Lab X1C 3D printing.

## Project Structure

```
src/threedp_mcp/
├── server.py       # Thin entrypoint — FastMCP init, tool registration, main()
├── constants.py    # MATERIAL_PROPERTIES, ISO_THREAD_TABLE
├── helpers.py      # shape_to_model_entry, run_build123d_code, select_face, compute_overhangs, ensure_exported
└── tools/
    ├── __init__.py     # register_all_tools(mcp, models, output_dir)
    ├── core.py         # create_model, export_model, measure_model, analyze_printability, list_models, get_model_code
    ├── transform.py    # transform_model, combine_models, import_model
    ├── modification.py # shell_model, split_model, add_text, create_threaded_hole
    ├── analysis.py     # estimate_print, analyze_overhangs, suggest_orientation, section_view, export_drawing, split_model_by_color
    ├── utility.py      # shrinkage_compensation, pack_models, convert_format
    ├── components.py   # create_enclosure, create_gear, create_snap_fit, create_hinge, create_dovetail, generate_label
    ├── mechanical.py   # create_thread, create_fastener, create_bearing, create_sprocket, create_flange, create_pipe, create_openbuilds_part
    ├── community.py    # search_models
    └── publishing.py   # publish_github_release, publish_thingiverse, publish_myminifactory, publish_cults3d
```

## Development

Uses uv for package management and Make for workflow:

```bash
make install          # uv sync
make test             # Unit tests (mocked build123d)
make test-integration # All tests including real build123d
make lint             # ruff check
make format           # ruff format
make verify           # lint + test
make run              # Start MCP server
```

## Tool Module Pattern

Each tool module exports `register(mcp, models, output_dir)`. Tools are closures over the shared `models` dict and `output_dir`. All build123d imports are lazy (inside function bodies).

## MCP Tools Available

### Core Tools
- `create_model(name, code)` — Execute build123d code, auto-exports STL. Code must assign final shape to `result`.
- `export_model(name, format)` — Export to "stl", "step", or "3mf"
- `measure_model(name)` — Bounding box, volume in mm
- `analyze_printability(name)` — Watertight check, volume validation, thin wall detection
- `list_models()` — All models in current session
- `get_model_code(name)` — Retrieve the code used to create a model

### Transform & Combine Tools
- `transform_model(name, source_name, operations)` — Scale, rotate, mirror, or translate a model.
- `combine_models(name, model_a, model_b, operation)` — Boolean union, subtract, or intersect two models.
- `import_model(name, file_path)` — Import an STL or STEP file from disk.

### Modification Tools
- `shell_model(name, source_name, thickness, open_faces)` — Hollow out a model with optional open faces.
- `split_model(name, source_name, plane, keep)` — Split a model along XY/XZ/YZ plane.
- `add_text(name, source_name, text, face, font_size, depth, font, emboss)` — Emboss or deboss text onto a face.
- `create_threaded_hole(name, source_name, position, thread_spec, depth, insert)` — Add threaded or heat-set insert holes (M2-M10).

### Analysis & Export Tools
- `estimate_print(name, infill_percent, layer_height, material)` — Estimate filament usage, weight, and cost.
- `analyze_overhangs(name, max_angle)` — Find overhang faces needing support material.
- `suggest_orientation(name)` — Suggest optimal print orientation to minimize supports.
- `section_view(name, source_name, plane, offset)` — 2D cross-section exported as SVG.
- `export_drawing(name, views, page_size)` — Multi-view 2D technical drawing as SVG.
- `split_model_by_color(name, source_name, assignments)` — Split into separate STLs for multi-color printing.

### Utility Tools
- `shrinkage_compensation(name, source_name, material)` — Scale model to compensate for material shrinkage.
- `pack_models(name, model_names, padding)` — Arrange models on build plate for batch printing.
- `convert_format(input_path, output_path)` — Convert between STL, STEP, 3MF, BREP formats.

### Parametric Components
- `create_enclosure(name, inner_width, inner_depth, inner_height, wall, lid_type, features)` — Electronics enclosure with lid.
- `create_gear(name, module, teeth, pressure_angle, thickness, bore)` — Involute spur gear via bd_warehouse.
- `create_snap_fit(name, snap_type, params)` — Cantilever snap-fit joints.
- `create_hinge(name, hinge_type, params)` — Two-part pin hinge assembly.
- `create_dovetail(name, dovetail_type, width, height, depth, angle, clearance)` — Male or female dovetail joints.
- `generate_label(name, text, size, font_size, qr_data)` — 3D-printable label with text and optional QR code.

### Mechanical Parts (bd_warehouse)
- `create_thread(name, thread_type, major_diameter, pitch, length, external, hand, end_finishes, size, manufacturing_compensation)` — Create threaded parts: ISO metric, ACME, metric trapezoidal, or plastic bottle threads.
- `create_fastener(name, fastener_class, size, length, fastener_type, simple, hand)` — Create screws, nuts, washers, or heat-set inserts (14 types).
- `create_bearing(name, bearing_class, size, bearing_type)` — Create parametric bearings (5 types: deep groove ball, angular contact, roller).
- `create_sprocket(name, num_teeth, chain_pitch, roller_diameter, thickness, bore_diameter, ...)` — Create chain sprockets for ANSI chains.
- `create_flange(name, flange_class, nps, flange_class_rating, face_type)` — Create ASME B16.5 pipe flanges (5 types).
- `create_pipe(name, outer_diameter, wall_thickness, length)` — Create pipe/tube sections.
- `create_openbuilds_part(name, part_type, length, rail_size)` — Create OpenBuilds V-Slot rails, C-Beam rails, or lead screws.

### Community
- `search_models(query, source, max_results)` — Search Thingiverse for 3D models (requires THINGIVERSE_API_KEY env var).

### Publishing
- `publish_github_release(name, repo, tag, description, formats, draft)` — Upload STL/STEP to GitHub Releases.
- `publish_thingiverse(name, title, description, tags, category, is_wip)` — Create a Thing and upload STL.
- `publish_myminifactory(name, title, description, tags, category_id)` — Create object and upload STL.
- `publish_cults3d(name, title, description, tags, license, free, price_cents)` — Create listing via GraphQL API.

## build123d Coding Patterns

All code runs with `from build123d import *` pre-imported. Assign the final shape to `result`.

### Basic shapes
```python
result = Box(width, depth, height)
result = Cylinder(radius, height)
result = Sphere(radius)
```

### Boolean operations
```python
result = Box(50, 40, 10) - Cylinder(5, 10)  # subtract
result = Box(50, 40, 10) + Cylinder(5, 10)  # union
result = Box(50, 40, 10) & Cylinder(5, 10)  # intersect
```

### Positioning
```python
hole = Pos(10, 0, 0) * Cylinder(3, 10)  # move before combining
result = box - hole
```

### Fillets and chamfers
```python
result = fillet(result.edges(), radius=1)
result = chamfer(result.edges(), length=0.5)
result = fillet(result.edges().filter_by(Axis.Z), radius=2)
```

### Extrude from sketch
```python
with BuildPart() as part:
    with BuildSketch():
        Rectangle(60, 40)
        with Locations([(20, 10), (-20, 10)]):
            Circle(3, mode=Mode.SUBTRACT)
    extrude(amount=5)
result = part.part
```

### Loft and sweep
```python
with BuildPart() as part:
    with BuildSketch(Plane.XY):
        Circle(20)
    with BuildSketch(Plane.XY.offset(30)):
        Rectangle(30, 30)
    loft()
result = part.part
```

## Design Guidelines for FDM Printing (Bambu Lab X1C)

- Minimum wall thickness: 0.8mm (prefer 1.2mm+)
- Minimum hole diameter: 2mm
- Fillet radii: 0.5-2mm for printability
- Overhangs: keep under 45 degrees or design for supports
- Units: always millimeters
- Tolerances: add 0.2mm clearance for press-fit joints
- Always run `analyze_printability` before declaring a model done

## Output Directory

STL and STEP files are saved to: `outputs/` (relative to project root)
