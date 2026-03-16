# 3DP MCP Server

MCP server for 3D-printable CAD modeling with build123d, targeting STL export for Bambu Lab X1C 3D printing.

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
- `create_enclosure(name, inner_width, inner_depth, inner_height, wall, lid_type, features)` — Electronics enclosure with lid. Features: vent_slots, screw_posts, cable_hole.
- `create_thread(name, thread_spec, length, external, hand, end_finishes, simple)` — ISO metric thread (external for bolts, internal for nuts) via bd_warehouse.
- `create_gear(name, module, teeth, pressure_angle, thickness, bore)` — Involute spur gear via bd_warehouse.
- `create_snap_fit(name, snap_type, params)` — Cantilever snap-fit joints.
- `create_hinge(name, hinge_type, params)` — Two-part pin hinge assembly.
- `create_dovetail(name, dovetail_type, width, height, depth, angle, clearance)` — Male or female dovetail joints.
- `generate_label(name, text, size, font_size, qr_data)` — 3D-printable label with text and optional QR code.

### Community
- `search_models(query, source, max_results)` — Search Thingiverse for 3D models (requires THINGIVERSE_API_KEY env var).

### Publishing
- `publish_github_release(name, repo, tag, description, formats, draft)` — Upload STL/STEP to GitHub Releases. Uses `gh` CLI or GITHUB_TOKEN env var.
- `publish_thingiverse(name, title, description, tags, category, is_wip)` — Create a Thing and upload STL. Requires THINGIVERSE_TOKEN env var.
- `publish_myminifactory(name, title, description, tags, category_id)` — Create object and upload STL. Requires MYMINIFACTORY_TOKEN env var.
- `publish_cults3d(name, title, description, tags, license, free, price_cents)` — Create listing via GraphQL API. Requires CULTS3D_API_KEY env var.

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

### Creating threaded parts
- Use `create_thread(name, thread_spec, length)` for standalone threaded rods or bolt shafts
- Use `create_threaded_hole(name, source, position, thread_spec)` to add threaded holes to existing parts
- Combine thread + head geometry using `combine_models` for complete bolts:
  1. `create_thread` for the shaft
  2. `create_model` for the head (e.g. `Cylinder` for hex head)
  3. `transform_model` to position the head
  4. `combine_models` to union them

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
