# 3DP MCP Server

MCP server for 3D-printable CAD modeling with build123d, targeting STL export for Bambu Lab X1C 3D printing.

## MCP Tools Available

- `create_model(name, code)` — Execute build123d code, auto-exports STL. Code must assign final shape to `result`.
- `export_model(name, format)` — Export to "stl", "step", or "3mf"
- `measure_model(name)` — Bounding box, volume in mm
- `analyze_printability(name)` — Watertight check, volume validation, thin wall detection
- `list_models()` — All models in current session
- `get_model_code(name)` — Retrieve the code used to create a model

## build123d Coding Patterns

All code runs with `from build123d import *` pre-imported. Assign the final shape to `result`.

### Basic shapes
​```python
result = Box(width, depth, height)
result = Cylinder(radius, height)
result = Sphere(radius)
​```

### Boolean operations
​```python
result = Box(50, 40, 10) - Cylinder(5, 10)  # subtract
result = Box(50, 40, 10) + Cylinder(5, 10)  # union
result = Box(50, 40, 10) & Cylinder(5, 10)  # intersect
​```

### Positioning
​```python
hole = Pos(10, 0, 0) * Cylinder(3, 10)  # move before combining
result = box - hole
​```

### Fillets and chamfers
​```python
result = fillet(result.edges(), radius=1)
result = chamfer(result.edges(), length=0.5)
result = fillet(result.edges().filter_by(Axis.Z), radius=2)
​```

### Extrude from sketch
​```python
with BuildPart() as part:
    with BuildSketch():
        Rectangle(60, 40)
        with Locations([(20, 10), (-20, 10)]):
            Circle(3, mode=Mode.SUBTRACT)
    extrude(amount=5)
result = part.part
​```

### Loft and sweep
​```python
with BuildPart() as part:
    with BuildSketch(Plane.XY):
        Circle(20)
    with BuildSketch(Plane.XY.offset(30)):
        Rectangle(30, 30)
    loft()
result = part.part
​```

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
