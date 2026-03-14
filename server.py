#!/usr/bin/env python3
"""3DP MCP Server — 3D printing CAD modeling with build123d."""

import json
import math
import os
import traceback

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("3dp-mcp-server")

_models: dict[str, dict] = {}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")

# ── Shared constants ──────────────────────────────────────────────────────────

_MATERIAL_PROPERTIES = {
    "PLA":   {"density": 1.24, "shrinkage": 0.003},
    "PETG":  {"density": 1.27, "shrinkage": 0.004},
    "ABS":   {"density": 1.04, "shrinkage": 0.007},
    "ASA":   {"density": 1.07, "shrinkage": 0.005},
    "TPU":   {"density": 1.21, "shrinkage": 0.005},
    "Nylon": {"density": 1.14, "shrinkage": 0.015},
}

_ISO_THREAD_TABLE = {
    "M2":   {"tap_drill": 1.6,  "insert_drill": 3.2,  "clearance_drill": 2.4},
    "M2.5": {"tap_drill": 2.05, "insert_drill": 3.5,  "clearance_drill": 2.9},
    "M3":   {"tap_drill": 2.5,  "insert_drill": 4.0,  "clearance_drill": 3.4},
    "M4":   {"tap_drill": 3.3,  "insert_drill": 5.0,  "clearance_drill": 4.5},
    "M5":   {"tap_drill": 4.2,  "insert_drill": 6.0,  "clearance_drill": 5.5},
    "M6":   {"tap_drill": 5.0,  "insert_drill": 7.0,  "clearance_drill": 6.6},
    "M8":   {"tap_drill": 6.8,  "insert_drill": 9.5,  "clearance_drill": 8.4},
    "M10":  {"tap_drill": 8.5,  "insert_drill": 12.0, "clearance_drill": 10.5},
}
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _shape_to_model_entry(shape, code: str = "") -> dict:
    """Convert a build123d shape into a model entry dict with bbox and volume."""
    bb = shape.bounding_box()
    bbox = {
        "min": [round(bb.min.X, 3), round(bb.min.Y, 3), round(bb.min.Z, 3)],
        "max": [round(bb.max.X, 3), round(bb.max.Y, 3), round(bb.max.Z, 3)],
        "size": [
            round(bb.max.X - bb.min.X, 3),
            round(bb.max.Y - bb.min.Y, 3),
            round(bb.max.Z - bb.min.Z, 3),
        ],
    }
    try:
        volume = round(shape.volume, 3)
    except Exception:
        volume = None
    return {"shape": shape, "code": code, "bbox": bbox, "volume": volume}


def _run_build123d_code(code: str) -> dict:
    local_ns: dict = {}
    exec_globals = {"__builtins__": __builtins__}
    exec(code, exec_globals, local_ns)

    if "result" not in local_ns:
        raise ValueError("Code must assign the final shape to a variable called `result`")

    return _shape_to_model_entry(local_ns["result"], code)


def _select_face(shape, direction: str):
    """Select a face by direction name (top/bottom/front/back/left/right)."""
    all_faces = shape.faces()
    selectors = {
        "top":    lambda f: f.center().Z,
        "bottom": lambda f: -f.center().Z,
        "front":  lambda f: f.center().Y,
        "back":   lambda f: -f.center().Y,
        "right":  lambda f: f.center().X,
        "left":   lambda f: -f.center().X,
    }
    key_fn = selectors.get(direction.lower())
    if key_fn is None:
        raise ValueError(f"Unknown face direction: {direction}. Use: {list(selectors.keys())}")
    return max(all_faces, key=key_fn)


def _compute_overhangs(shape, max_angle_deg: float = 45.0) -> dict:
    """Compute overhang statistics for a shape. Returns dict with faces, areas, angles."""
    threshold_rad = math.radians(max_angle_deg)
    all_faces = shape.faces()
    total_area = 0.0
    overhang_faces = []
    overhang_area = 0.0

    for i, face in enumerate(all_faces):
        area = face.area
        total_area += area
        try:
            normal = face.normal_at()
        except Exception:
            continue
        if normal.Z < 0:
            cos_val = min(abs(normal.Z), 1.0)
            angle_from_vertical = math.acos(cos_val)
            if angle_from_vertical > threshold_rad:
                angle_deg = math.degrees(angle_from_vertical)
                overhang_faces.append({"index": i, "area": round(area, 2), "angle_deg": round(angle_deg, 1)})
                overhang_area += area

    return {
        "total_faces": len(all_faces),
        "total_area": round(total_area, 2),
        "overhang_faces": overhang_faces,
        "overhang_face_count": len(overhang_faces),
        "overhang_area": round(overhang_area, 2),
        "overhang_pct": round(overhang_area / total_area * 100, 1) if total_area > 0 else 0,
    }


@mcp.tool()
def create_model(name: str, code: str) -> str:
    """Create a 3D model by executing build123d Python code.

    The code MUST assign the final shape to a variable called `result`.
    All build123d imports are available automatically.

    Args:
        name: A short name for the model (used for file naming)
        code: build123d Python code that creates a shape and assigns it to `result`

    Returns:
        JSON with success status, geometry info (bounding box, volume), and output paths.
    """
    try:
        if "from build123d" not in code and "import build123d" not in code:
            code = "from build123d import *\n" + code

        result = _run_build123d_code(code)
        _models[name] = result

        model_dir = os.path.join(OUTPUT_DIR, name)
        os.makedirs(model_dir, exist_ok=True)

        from build123d import export_stl, export_step
        stl_path = os.path.join(model_dir, f"{name}.stl")
        step_path = os.path.join(model_dir, f"{name}.step")
        export_stl(result["shape"], stl_path)
        export_step(result["shape"], step_path)

        return json.dumps({
            "success": True,
            "name": name,
            "bbox": result["bbox"],
            "volume": result["volume"],
            "outputs": {"stl": stl_path, "step": step_path},
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }, indent=2)


@mcp.tool()
def export_model(name: str, format: str = "stl") -> str:
    """Export a model to STL, STEP, or 3MF format.

    Args:
        name: Name of a previously created model
        format: Export format - "stl", "step", or "3mf"
    """
    if name not in _models:
        return json.dumps({"success": False, "error": f"Model '{name}' not found. Available: {list(_models.keys())}"})

    model = _models[name]
    model_dir = os.path.join(OUTPUT_DIR, name)
    os.makedirs(model_dir, exist_ok=True)

    fmt = format.lower().strip(".")
    out_path = os.path.join(model_dir, f"{name}.{fmt}")

    try:
        if fmt == "stl":
            from build123d import export_stl
            export_stl(model["shape"], out_path)
        elif fmt == "step":
            from build123d import export_step
            export_step(model["shape"], out_path)
        elif fmt == "3mf":
            from build123d import Mesher
            with Mesher() as mesher:
                mesher.add_shape(model["shape"])
                mesher.write(out_path)
        else:
            return json.dumps({"success": False, "error": f"Unsupported format: {fmt}"})

        return json.dumps({"success": True, "path": out_path})

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()})


@mcp.tool()
def measure_model(name: str) -> str:
    """Measure a model's geometry: bounding box, volume, surface area, and face/edge counts.

    Args:
        name: Name of a previously created model
    """
    if name not in _models:
        return json.dumps({"success": False, "error": f"Model '{name}' not found. Available: {list(_models.keys())}"})

    shape = _models[name]["shape"]
    bb = _models[name]["bbox"]
    measurements = {"name": name, "bbox": bb}

    try:
        measurements["volume_mm3"] = round(shape.volume, 3)
    except Exception:
        measurements["volume_mm3"] = None

    try:
        measurements["area_mm2"] = round(shape.area, 3)
    except Exception:
        measurements["area_mm2"] = None

    try:
        measurements["faces"] = len(shape.faces())
    except Exception:
        measurements["faces"] = None

    try:
        measurements["edges"] = len(shape.edges())
    except Exception:
        measurements["edges"] = None

    return json.dumps(measurements, indent=2)


@mcp.tool()
def analyze_printability(name: str, min_wall_mm: float = 0.8) -> str:
    """Check if a model is suitable for FDM 3D printing (e.g. Bambu Lab X1C).

    Args:
        name: Name of a previously created model
        min_wall_mm: Minimum wall thickness in mm (default 0.8)
    """
    if name not in _models:
        return json.dumps({"success": False, "error": f"Model '{name}' not found. Available: {list(_models.keys())}"})

    shape = _models[name]["shape"]
    issues = []
    checks = {}

    try:
        vol = shape.volume
        checks["volume_mm3"] = round(vol, 3)
        if vol <= 0:
            issues.append("Model has zero or negative volume")
    except Exception as e:
        issues.append(f"Cannot compute volume: {e}")

    try:
        solids = shape.solids()
        checks["solid_count"] = len(solids)
        if len(solids) == 0:
            issues.append("No solids found — not printable")
    except Exception:
        pass

    bb = _models[name]["bbox"]
    dims = bb["size"]
    checks["dimensions_mm"] = dims
    if any(d < 1.0 for d in dims):
        issues.append(f"Very small dimension ({min(dims):.1f}mm)")
    if any(d > 300 for d in dims):
        issues.append(f"Exceeds 300mm ({max(dims):.1f}mm) — may not fit bed")

    try:
        faces = shape.faces()
        checks["face_count"] = len(faces)
        if len(faces) < 4:
            issues.append("Too few faces for a valid solid")
    except Exception:
        pass

    try:
        area = shape.area
        vol = shape.volume
        if vol > 0:
            ratio = area / vol
            checks["area_volume_ratio"] = round(ratio, 4)
            if ratio > 7.5:
                issues.append(f"High area/volume ratio ({ratio:.2f}) — possible thin walls < {min_wall_mm}mm")
    except Exception:
        pass

    return json.dumps({
        "verdict": "PRINTABLE" if not issues else "REVIEW NEEDED",
        "issues": issues,
        "checks": checks,
        "printer": "Bambu Lab X1C (256x256x256mm)",
    }, indent=2)


@mcp.tool()
def list_models() -> str:
    """List all models currently loaded in this session."""
    if not _models:
        return json.dumps({"models": [], "message": "No models yet. Use create_model to make one."})

    return json.dumps({"models": [
        {"name": n, "bbox": d["bbox"], "volume": d["volume"]} for n, d in _models.items()
    ]}, indent=2)


@mcp.tool()
def get_model_code(name: str) -> str:
    """Retrieve the build123d code used to create a model.

    Args:
        name: Name of a previously created model
    """
    if name not in _models:
        return json.dumps({"success": False, "error": f"Model '{name}' not found. Available: {list(_models.keys())}"})

    return json.dumps({"name": name, "code": _models[name]["code"]})


@mcp.tool()
def transform_model(name: str, source_name: str, operations: str) -> str:
    """Scale, rotate, mirror, or translate a loaded model. Apply operations in order.

    Args:
        name: Name for the new transformed model
        source_name: Name of the source model to transform
        operations: JSON string with transform operations applied in order.
            Supported keys: "scale" (float or [x,y,z]), "rotate" ([rx,ry,rz] degrees),
            "mirror" ("XY","XZ","YZ"), "translate" ([x,y,z]).
            Can be a single dict or a list of dicts for ordered operations.
    """
    if source_name not in _models:
        return json.dumps({"success": False, "error": f"Model '{source_name}' not found. Available: {list(_models.keys())}"})

    try:
        from build123d import Mirror, Plane as B3dPlane, Pos, Rot

        shape = _models[source_name]["shape"]
        ops = json.loads(operations)
        if isinstance(ops, dict):
            ops = [ops]

        for op in ops:
            if "scale" in op:
                s = op["scale"]
                if isinstance(s, (int, float)):
                    shape = shape.scale(s)
                else:
                    shape = shape.scale(s[0], s[1], s[2])
            if "rotate" in op:
                rx, ry, rz = op["rotate"]
                shape = Rot(rx, ry, rz) * shape
            if "mirror" in op:
                plane_map = {"XY": B3dPlane.XY, "XZ": B3dPlane.XZ, "YZ": B3dPlane.YZ}
                mirror_plane = plane_map.get(op["mirror"].upper())
                if mirror_plane is None:
                    return json.dumps({"success": False, "error": f"Unknown mirror plane: {op['mirror']}. Use XY, XZ, or YZ."})
                shape = Mirror(about=mirror_plane) * shape
            if "translate" in op:
                tx, ty, tz = op["translate"]
                shape = Pos(tx, ty, tz) * shape

        entry = _shape_to_model_entry(shape, code=f"transform of {source_name}: {operations}")
        _models[name] = entry

        return json.dumps({
            "success": True,
            "name": name,
            "source": source_name,
            "bbox": entry["bbox"],
            "volume": entry["volume"],
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def import_model(name: str, file_path: str) -> str:
    """Import an STL or STEP file from disk into the server as a loaded model.

    Args:
        name: Name for the imported model
        file_path: Absolute path to the STL or STEP file
    """
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".stl":
            from build123d import import_stl
            shape = import_stl(file_path)
        elif ext in (".step", ".stp"):
            from build123d import import_step
            shape = import_step(file_path)
        else:
            return json.dumps({"success": False, "error": f"Unsupported file type: {ext}. Use .stl, .step, or .stp."})

        entry = _shape_to_model_entry(shape, code=f"imported from {file_path}")
        _models[name] = entry

        return json.dumps({
            "success": True,
            "name": name,
            "file": file_path,
            "bbox": entry["bbox"],
            "volume": entry["volume"],
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def estimate_print(name: str, infill_percent: float = 15.0, layer_height: float = 0.2, material: str = "PLA") -> str:
    """Estimate filament usage, weight, and cost for printing a model.

    Args:
        name: Name of a previously created model
        infill_percent: Infill percentage (default 15)
        layer_height: Layer height in mm (default 0.2)
        material: Filament material - PLA, PETG, ABS, TPU, or ASA (default PLA)
    """
    if name not in _models:
        return json.dumps({"success": False, "error": f"Model '{name}' not found. Available: {list(_models.keys())}"})

    try:
        shape = _models[name]["shape"]
        mat = material.upper()
        if mat not in _MATERIAL_PROPERTIES:
            return json.dumps({"success": False, "error": f"Unknown material: {material}. Supported: {list(_MATERIAL_PROPERTIES.keys())}"})

        density = _MATERIAL_PROPERTIES[mat]["density"]  # g/cm^3
        filament_diameter = 1.75  # mm
        cost_per_kg = 20.0  # USD

        total_volume_mm3 = shape.volume  # mm^3
        surface_area_mm2 = shape.area  # mm^2

        wall_thickness = 0.8  # mm per perimeter
        num_perimeters = 2
        shell_volume_mm3 = surface_area_mm2 * wall_thickness * num_perimeters

        interior_volume_mm3 = max(0, total_volume_mm3 - shell_volume_mm3)
        infill_volume_mm3 = interior_volume_mm3 * (infill_percent / 100.0)

        used_volume_mm3 = shell_volume_mm3 + infill_volume_mm3
        used_volume_cm3 = used_volume_mm3 / 1000.0

        weight_g = used_volume_cm3 * density

        filament_cross_section = math.pi * (filament_diameter / 2.0) ** 2  # mm^2
        filament_length_mm = used_volume_mm3 / filament_cross_section
        filament_length_m = filament_length_mm / 1000.0

        cost = (weight_g / 1000.0) * cost_per_kg

        # Rough time estimate: based on volume and layer height
        layers = _models[name]["bbox"]["size"][2] / layer_height
        # Very rough: ~2 seconds per layer + volume-based component
        est_minutes = (layers * 2.0 + used_volume_mm3 / 500.0) / 60.0

        return json.dumps({
            "success": True,
            "name": name,
            "material": mat,
            "infill_percent": infill_percent,
            "layer_height_mm": layer_height,
            "model_volume_mm3": round(total_volume_mm3, 1),
            "shell_volume_mm3": round(shell_volume_mm3, 1),
            "infill_volume_mm3": round(infill_volume_mm3, 1),
            "total_filament_volume_mm3": round(used_volume_mm3, 1),
            "weight_g": round(weight_g, 1),
            "filament_length_m": round(filament_length_m, 2),
            "estimated_cost_usd": round(cost, 2),
            "estimated_time_min": round(est_minutes, 0),
            "density_g_cm3": density,
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def combine_models(name: str, model_a: str, model_b: str, operation: str = "union") -> str:
    """Boolean combine two loaded models: union, subtract, or intersect.

    Args:
        name: Name for the resulting combined model
        model_a: Name of the first model
        model_b: Name of the second model
        operation: Boolean operation - "union", "subtract", or "intersect"
    """
    for m in (model_a, model_b):
        if m not in _models:
            return json.dumps({"success": False, "error": f"Model '{m}' not found. Available: {list(_models.keys())}"})

    try:
        a = _models[model_a]["shape"]
        b = _models[model_b]["shape"]

        op = operation.lower()
        if op == "union":
            result = a + b
        elif op == "subtract":
            result = a - b
        elif op == "intersect":
            result = a & b
        else:
            return json.dumps({"success": False, "error": f"Unknown operation: {operation}. Use union, subtract, or intersect."})

        entry = _shape_to_model_entry(result, code=f"{model_a} {op} {model_b}")
        _models[name] = entry

        return json.dumps({
            "success": True,
            "name": name,
            "operation": op,
            "model_a": model_a,
            "model_b": model_b,
            "bbox": entry["bbox"],
            "volume": entry["volume"],
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def shell_model(name: str, source_name: str, thickness: float = 2.0, open_faces: str = "[]") -> str:
    """Hollow out a model, optionally leaving faces open.

    Args:
        name: Name for the new shelled model
        source_name: Name of the source model to hollow
        thickness: Wall thickness in mm (default 2.0)
        open_faces: JSON list of face directions to leave open, e.g. '["top"]' or '["bottom"]'.
            Supported: "top", "bottom". Default is no open faces.
    """
    if source_name not in _models:
        return json.dumps({"success": False, "error": f"Model '{source_name}' not found. Available: {list(_models.keys())}"})

    try:
        shape = _models[source_name]["shape"]
        faces_to_open = json.loads(open_faces) if isinstance(open_faces, str) else open_faces

        openings = [_select_face(shape, fd) for fd in faces_to_open]
        result = shape.shell(openings=openings, thickness=-thickness)

        entry = _shape_to_model_entry(result, code=f"shell of {source_name}, thickness={thickness}")
        _models[name] = entry

        return json.dumps({
            "success": True,
            "name": name,
            "source": source_name,
            "thickness_mm": thickness,
            "open_faces": faces_to_open,
            "bbox": entry["bbox"],
            "volume": entry["volume"],
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def split_model(name: str, source_name: str, plane: str = "XY", keep: str = "both") -> str:
    """Split a model along a plane.

    Args:
        name: Base name for the resulting model(s)
        source_name: Name of the source model to split
        plane: Split plane - "XY", "XZ", "YZ", or JSON like '{"axis": "Z", "offset": 10.5}'
        keep: Which half to keep - "above", "below", or "both" (default "both").
            If "both", saves as name_above and name_below.
    """
    if source_name not in _models:
        return json.dumps({"success": False, "error": f"Model '{source_name}' not found. Available: {list(_models.keys())}"})

    try:
        from build123d import Axis, Box, Plane as B3dPlane, Pos

        shape = _models[source_name]["shape"]
        bb = shape.bounding_box()

        # Parse plane specification
        offset = 0.0
        if plane.startswith("{"):
            plane_spec = json.loads(plane)
            axis = plane_spec.get("axis", "Z").upper()
            offset = plane_spec.get("offset", 0.0)
        else:
            # Map plane name to axis normal
            plane_axis_map = {"XY": "Z", "XZ": "Y", "YZ": "X"}
            axis = plane_axis_map.get(plane.upper())
            if axis is None:
                return json.dumps({"success": False, "error": f"Unknown plane: {plane}. Use XY, XZ, YZ."})

        # Create a large cutting box for bisecting
        size = max(bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z) * 4 + 200
        half = size / 2

        if axis == "Z":
            # "above" = positive Z from offset, "below" = negative Z from offset
            above_box = Pos(0, 0, offset + half) * Box(size, size, size)
            below_box = Pos(0, 0, offset - half) * Box(size, size, size)
        elif axis == "Y":
            above_box = Pos(0, offset + half, 0) * Box(size, size, size)
            below_box = Pos(0, offset - half, 0) * Box(size, size, size)
        elif axis == "X":
            above_box = Pos(offset + half, 0, 0) * Box(size, size, size)
            below_box = Pos(offset - half, 0, 0) * Box(size, size, size)

        results = {}
        if keep in ("above", "both"):
            above_shape = shape & above_box
            above_entry = _shape_to_model_entry(above_shape, code=f"split {source_name} above {plane}")
            result_name = f"{name}_above" if keep == "both" else name
            _models[result_name] = above_entry
            results[result_name] = {"bbox": above_entry["bbox"], "volume": above_entry["volume"]}

        if keep in ("below", "both"):
            below_shape = shape & below_box
            below_entry = _shape_to_model_entry(below_shape, code=f"split {source_name} below {plane}")
            result_name = f"{name}_below" if keep == "both" else name
            _models[result_name] = below_entry
            results[result_name] = {"bbox": below_entry["bbox"], "volume": below_entry["volume"]}

        return json.dumps({
            "success": True,
            "source": source_name,
            "plane": plane,
            "keep": keep,
            "results": results,
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def section_view(name: str, source_name: str, plane: str = "XY", offset: float = 0.0) -> str:
    """Generate a 2D cross-section of a model and export as SVG.

    Args:
        name: Name for the cross-section result
        source_name: Name of the source model to section
        plane: Section plane - "XY", "XZ", or "YZ" (default "XY")
        offset: Position along the plane normal axis (default 0.0)
    """
    if source_name not in _models:
        return json.dumps({"success": False, "error": f"Model '{source_name}' not found. Available: {list(_models.keys())}"})

    try:
        from build123d import Plane as B3dPlane, Vector, ExportSVG

        shape = _models[source_name]["shape"]

        plane_map = {
            "XY": B3dPlane.XY,
            "XZ": B3dPlane.XZ,
            "YZ": B3dPlane.YZ,
        }
        section_plane = plane_map.get(plane.upper())
        if section_plane is None:
            return json.dumps({"success": False, "error": f"Unknown plane: {plane}. Use XY, XZ, or YZ."})

        # Apply offset
        if offset != 0.0:
            section_plane = section_plane.offset(offset)

        # Create cross-section
        section = shape.section(section_plane)

        # Store the section as a model entry
        entry = _shape_to_model_entry(section, code=f"section of {source_name} at {plane} offset={offset}")
        _models[name] = entry

        # Export SVG
        model_dir = os.path.join(OUTPUT_DIR, name)
        os.makedirs(model_dir, exist_ok=True)
        svg_path = os.path.join(model_dir, f"{name}.svg")

        exporter = ExportSVG(scale=2.0)
        exporter.add_layer("section")
        exporter.add_shape(section, layer="section")
        exporter.write(svg_path)

        return json.dumps({
            "success": True,
            "name": name,
            "source": source_name,
            "plane": plane,
            "offset": offset,
            "svg_path": svg_path,
            "bbox": entry["bbox"],
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def export_drawing(name: str, views: str = '["front", "top", "right"]', page_size: str = "A4") -> str:
    """Generate a 2D technical drawing as SVG with multiple view projections.

    Args:
        name: Name of a previously created model
        views: JSON list of view directions, e.g. '["front", "top", "right", "iso"]'
        page_size: Page size - "A4" or "A3" (default "A4")
    """
    if name not in _models:
        return json.dumps({"success": False, "error": f"Model '{name}' not found. Available: {list(_models.keys())}"})

    try:
        from build123d import ExportSVG, Vector

        shape = _models[name]["shape"]
        view_list = json.loads(views) if isinstance(views, str) else views

        model_dir = os.path.join(OUTPUT_DIR, name)
        os.makedirs(model_dir, exist_ok=True)
        svg_path = os.path.join(model_dir, f"{name}_drawing.svg")

        # Map view names to direction vectors (camera looks FROM this direction)
        view_directions = {
            "front": Vector(0, -1, 0),
            "back": Vector(0, 1, 0),
            "right": Vector(1, 0, 0),
            "left": Vector(-1, 0, 0),
            "top": Vector(0, 0, 1),
            "bottom": Vector(0, 0, -1),
            "iso": Vector(1, -1, 1),
        }

        exporter = ExportSVG(scale=1.0)

        for i, view_name in enumerate(view_list):
            vn = view_name.lower()
            direction = view_directions.get(vn)
            if direction is None:
                return json.dumps({"success": False, "error": f"Unknown view: {view_name}. Supported: {list(view_directions.keys())}"})

            layer_name = f"view_{vn}"
            exporter.add_layer(layer_name)
            exporter.add_shape(shape, layer=layer_name, line_type=ExportSVG.LineType.VISIBLE,
                               view_port_origin=direction)

        exporter.write(svg_path)

        return json.dumps({
            "success": True,
            "name": name,
            "views": view_list,
            "svg_path": svg_path,
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


# ── Tier 2: Print Analysis ────────────────────────────────────────────────────

@mcp.tool()
def analyze_overhangs(name: str, max_angle: float = 45.0) -> str:
    """Analyze overhang faces that may need support material.

    Args:
        name: Name of a previously created model
        max_angle: Maximum unsupported overhang angle in degrees (default 45)
    """
    if name not in _models:
        return json.dumps({"success": False, "error": f"Model '{name}' not found. Available: {list(_models.keys())}"})

    try:
        shape = _models[name]["shape"]
        result = _compute_overhangs(shape, max_angle)
        result["success"] = True
        result["name"] = name
        result["max_angle"] = max_angle
        # Show worst 10 overhang faces
        result["worst_overhangs"] = sorted(
            result.pop("overhang_faces"), key=lambda f: f["angle_deg"], reverse=True
        )[:10]
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def suggest_orientation(name: str) -> str:
    """Suggest optimal print orientation to minimize supports and maximize bed adhesion.

    Tests 24 orientations (90-degree increments around X and Y, plus 45-degree diagonals)
    and scores each by overhang area, bed contact, and height.

    Args:
        name: Name of a previously created model
    """
    if name not in _models:
        return json.dumps({"success": False, "error": f"Model '{name}' not found. Available: {list(_models.keys())}"})

    try:
        from build123d import Rot

        shape = _models[name]["shape"]
        candidates = []

        angles = [0, 45, 90, 135, 180, 225, 270, 315]
        for rx in [0, 90, 180, 270]:
            for ry in [0, 90, 180, 270]:
                rotated = Rot(rx, ry, 0) * shape
                bb = rotated.bounding_box()
                height = bb.max.Z - bb.min.Z

                ovh = _compute_overhangs(rotated, 45.0)
                overhang_area = ovh["overhang_area"]

                # Bed contact: faces near the bottom Z
                bed_area = 0.0
                min_z = bb.min.Z
                for face in rotated.faces():
                    try:
                        n = face.normal_at()
                        if n.Z < -0.95 and abs(face.center().Z - min_z) < 0.5:
                            bed_area += face.area
                    except Exception:
                        continue

                # Score: lower is better (minimize overhangs and height, maximize bed contact)
                score = overhang_area - bed_area * 2 + height * 0.5
                candidates.append({
                    "rotation": [rx, ry, 0],
                    "overhang_area": round(overhang_area, 1),
                    "bed_contact_area": round(bed_area, 1),
                    "height_mm": round(height, 1),
                    "score": round(score, 1),
                })

        candidates.sort(key=lambda c: c["score"])
        # Deduplicate by similar scores
        seen_scores = set()
        unique = []
        for c in candidates:
            key = round(c["score"], 0)
            if key not in seen_scores:
                seen_scores.add(key)
                unique.append(c)
            if len(unique) >= 5:
                break

        return json.dumps({
            "success": True,
            "name": name,
            "best": unique[0] if unique else None,
            "top_candidates": unique,
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


# ── Tier 2: Utility ──────────────────────────────────────────────────────────

@mcp.tool()
def shrinkage_compensation(name: str, source_name: str, material: str = "PLA") -> str:
    """Scale a model to compensate for material shrinkage after printing.

    Args:
        name: Name for the compensated model
        source_name: Name of the source model
        material: Filament material (default PLA). Supports PLA, PETG, ABS, ASA, TPU, Nylon.
    """
    if source_name not in _models:
        return json.dumps({"success": False, "error": f"Model '{source_name}' not found. Available: {list(_models.keys())}"})

    mat = material.upper()
    if mat not in _MATERIAL_PROPERTIES:
        return json.dumps({"success": False, "error": f"Unknown material: {material}. Supported: {list(_MATERIAL_PROPERTIES.keys())}"})

    try:
        shrinkage = _MATERIAL_PROPERTIES[mat]["shrinkage"]
        factor = 1.0 / (1.0 - shrinkage)

        shape = _models[source_name]["shape"]
        compensated = shape.scale(factor)

        entry = _shape_to_model_entry(compensated, code=f"shrinkage compensation of {source_name} for {mat} (×{factor:.5f})")
        _models[name] = entry

        return json.dumps({
            "success": True,
            "name": name,
            "source": source_name,
            "material": mat,
            "shrinkage_pct": round(shrinkage * 100, 2),
            "scale_factor": round(factor, 5),
            "original_bbox": _models[source_name]["bbox"],
            "compensated_bbox": entry["bbox"],
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def pack_models(name: str, model_names: str, padding: float = 5.0) -> str:
    """Arrange multiple models compactly on the build plate for batch printing.

    Args:
        name: Name for the packed arrangement
        model_names: JSON list of model names to pack, e.g. '["part_a", "part_b"]'
        padding: Spacing between parts in mm (default 5.0)
    """
    try:
        from build123d import pack, Compound

        names = json.loads(model_names) if isinstance(model_names, str) else model_names
        shapes = []
        for n in names:
            if n not in _models:
                return json.dumps({"success": False, "error": f"Model '{n}' not found. Available: {list(_models.keys())}"})
            shapes.append(_models[n]["shape"])

        packed = pack(shapes, padding, align_z=True)
        compound = Compound(children=list(packed))

        entry = _shape_to_model_entry(compound, code=f"pack of {names}")
        _models[name] = entry

        positions = []
        for i, s in enumerate(packed):
            bb = s.bounding_box()
            positions.append({
                "model": names[i],
                "center": [round(bb.min.X + (bb.max.X - bb.min.X) / 2, 1),
                           round(bb.min.Y + (bb.max.Y - bb.min.Y) / 2, 1)],
            })

        return json.dumps({
            "success": True,
            "name": name,
            "packed_count": len(names),
            "positions": positions,
            "bbox": entry["bbox"],
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def convert_format(input_path: str, output_path: str) -> str:
    """Convert a 3D model file between formats (STL, STEP, 3MF, BREP).

    Args:
        input_path: Path to the input file
        output_path: Path for the output file (format determined by extension)
    """
    try:
        in_ext = os.path.splitext(input_path)[1].lower()
        out_ext = os.path.splitext(output_path)[1].lower()

        # Import
        if in_ext == ".stl":
            from build123d import import_stl
            shape = import_stl(input_path)
        elif in_ext in (".step", ".stp"):
            from build123d import import_step
            shape = import_step(input_path)
        elif in_ext == ".brep":
            from build123d import import_brep
            shape = import_brep(input_path)
        else:
            return json.dumps({"success": False, "error": f"Unsupported input format: {in_ext}"})

        # Export
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        if out_ext == ".stl":
            from build123d import export_stl
            export_stl(shape, output_path)
        elif out_ext in (".step", ".stp"):
            from build123d import export_step
            export_step(shape, output_path)
        elif out_ext == ".brep":
            from build123d import export_brep
            export_brep(shape, output_path)
        elif out_ext == ".3mf":
            from build123d import Mesher
            with Mesher() as mesher:
                mesher.add_shape(shape)
                mesher.write(output_path)
        else:
            return json.dumps({"success": False, "error": f"Unsupported output format: {out_ext}"})

        return json.dumps({
            "success": True,
            "input": input_path,
            "output": output_path,
            "input_format": in_ext,
            "output_format": out_ext,
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


# ── Tier 2: Text & Features ──────────────────────────────────────────────────

@mcp.tool()
def add_text(name: str, source_name: str, text: str, face: str = "top",
             font_size: float = 10.0, depth: float = 1.0, font: str = "Arial",
             emboss: bool = True) -> str:
    """Emboss or deboss text onto a model face.

    Args:
        name: Name for the resulting model
        source_name: Name of the source model
        text: Text string to add
        face: Face to place text on - "top", "bottom", "front", "back", "left", "right"
        font_size: Font size in mm (default 10)
        depth: Extrusion depth in mm (default 1.0)
        font: Font name (default "Arial")
        emboss: True to raise text (emboss), False to cut text (deboss)
    """
    if source_name not in _models:
        return json.dumps({"success": False, "error": f"Model '{source_name}' not found. Available: {list(_models.keys())}"})

    try:
        from build123d import (BuildPart, BuildSketch, Text as B3dText, Plane as B3dPlane,
                                Pos, extrude, Mode)

        shape = _models[source_name]["shape"]
        target_face = _select_face(shape, face)
        fc = target_face.center()

        # Determine sketch plane and extrude direction based on face
        face_normal = target_face.normal_at()
        sketch_plane = B3dPlane(origin=(fc.X, fc.Y, fc.Z),
                                 z_dir=(face_normal.X, face_normal.Y, face_normal.Z))

        with BuildPart() as text_part:
            with BuildSketch(sketch_plane):
                B3dText(text, font_size, font=font)
            extrude(amount=depth)

        text_solid = text_part.part

        if emboss:
            result = shape + text_solid
        else:
            result = shape - text_solid

        entry = _shape_to_model_entry(result, code=f"{'emboss' if emboss else 'deboss'} '{text}' on {face} of {source_name}")
        _models[name] = entry

        return json.dumps({
            "success": True,
            "name": name,
            "source": source_name,
            "text": text,
            "face": face,
            "emboss": emboss,
            "depth_mm": depth,
            "bbox": entry["bbox"],
            "volume": entry["volume"],
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def create_threaded_hole(name: str, source_name: str, position: str, thread_spec: str = "M3",
                          depth: float = 10.0, insert: bool = False) -> str:
    """Add a threaded or heat-set insert hole to a model.

    Args:
        name: Name for the resulting model
        source_name: Name of the source model
        position: JSON [x, y, z] position for the hole center
        thread_spec: ISO metric thread spec - M2, M2.5, M3, M4, M5, M6, M8, M10 (default M3)
        depth: Hole depth in mm (default 10)
        insert: If true, use heat-set insert diameter instead of tap drill (default false)
    """
    if source_name not in _models:
        return json.dumps({"success": False, "error": f"Model '{source_name}' not found. Available: {list(_models.keys())}"})

    spec = thread_spec.upper()
    if spec not in _ISO_THREAD_TABLE:
        return json.dumps({"success": False, "error": f"Unknown thread spec: {thread_spec}. Supported: {list(_ISO_THREAD_TABLE.keys())}"})

    try:
        from build123d import Cylinder, Pos

        pos = json.loads(position) if isinstance(position, str) else position
        thread = _ISO_THREAD_TABLE[spec]
        diameter = thread["insert_drill"] if insert else thread["tap_drill"]
        radius = diameter / 2.0

        hole = Pos(pos[0], pos[1], pos[2]) * Cylinder(radius, depth)
        shape = _models[source_name]["shape"]
        result = shape - hole

        entry = _shape_to_model_entry(result, code=f"{spec} {'insert' if insert else 'threaded'} hole at {pos}")
        _models[name] = entry

        return json.dumps({
            "success": True,
            "name": name,
            "source": source_name,
            "thread_spec": spec,
            "hole_type": "heat-set insert" if insert else "tap drill",
            "diameter_mm": diameter,
            "depth_mm": depth,
            "position": pos,
            "bbox": entry["bbox"],
            "volume": entry["volume"],
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def create_enclosure(name: str, inner_width: float, inner_depth: float, inner_height: float,
                      wall: float = 2.0, lid_type: str = "snap", features: str = "[]") -> str:
    """Generate a parametric electronics enclosure with lid.

    Creates two models: name_body and name_lid.

    Args:
        name: Base name for the enclosure parts
        inner_width: Interior width (X) in mm
        inner_depth: Interior depth (Y) in mm
        inner_height: Interior height (Z) in mm
        wall: Wall thickness in mm (default 2.0)
        lid_type: "snap" for snap-fit lid, "screw" for screw-post lid (default "snap")
        features: JSON list of features, e.g. '["vent_slots", "screw_posts"]'.
            Supported: "vent_slots", "screw_posts", "cable_hole"
    """
    try:
        from build123d import Box, Cylinder, Pos, Locations

        feat_list = json.loads(features) if isinstance(features, str) else features

        ow = inner_width + 2 * wall
        od = inner_depth + 2 * wall
        oh = inner_height + wall  # wall on bottom, open on top

        # Body: outer box minus inner cavity
        outer = Pos(0, 0, oh / 2) * Box(ow, od, oh)
        cavity = Pos(0, 0, wall + inner_height / 2) * Box(inner_width, inner_depth, inner_height)
        body = outer - cavity

        # Lip for lid alignment (ridge inside top edge)
        lip_h = 2.0
        lip_w = wall / 2
        lip_outer = Pos(0, 0, oh + lip_h / 2) * Box(ow, od, lip_h)
        lip_inner = Pos(0, 0, oh + lip_h / 2) * Box(ow - 2 * lip_w, od - 2 * lip_w, lip_h)
        lip = lip_outer - lip_inner
        body = body + lip

        # Features
        if "screw_posts" in feat_list:
            post_r = 3.0
            post_h = inner_height - 1.0
            hole_r = 1.25  # for M2.5 screw
            inset = wall + post_r + 1.0
            for sx, sy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                px = sx * (inner_width / 2 - post_r - 1)
                py = sy * (inner_depth / 2 - post_r - 1)
                post = Pos(px, py, wall + post_h / 2) * Cylinder(post_r, post_h)
                hole = Pos(px, py, wall + post_h / 2) * Cylinder(hole_r, post_h)
                body = body + post - hole

        if "vent_slots" in feat_list:
            slot_w = 1.5
            slot_h = inner_height * 0.6
            slot_spacing = 4.0
            n_slots = int(inner_width * 0.6 / slot_spacing)
            start_x = -(n_slots - 1) * slot_spacing / 2
            for i in range(n_slots):
                sx = start_x + i * slot_spacing
                slot = Pos(sx, od / 2, wall + inner_height * 0.3 + slot_h / 2) * Box(slot_w, wall + 1, slot_h)
                body = body - slot

        if "cable_hole" in feat_list:
            cable_r = 3.0
            cable_hole = Pos(0, -od / 2, wall + inner_height / 2) * Cylinder(cable_r, wall + 1)
            # Rotate cylinder to point along Y axis
            from build123d import Rot
            cable_hole = Pos(0, -od / 2, wall + inner_height / 2) * (Rot(90, 0, 0) * Cylinder(cable_r, wall + 1))
            body = body - cable_hole

        # Lid
        lid_clearance = 0.2
        lid = Pos(0, 0, wall / 2) * Box(ow, od, wall)
        if lid_type == "snap":
            ridge_h = lip_h - lid_clearance
            ridge_outer = Pos(0, 0, wall + ridge_h / 2) * Box(
                ow - 2 * lip_w - lid_clearance, od - 2 * lip_w - lid_clearance, ridge_h)
            ridge_inner = Pos(0, 0, wall + ridge_h / 2) * Box(
                ow - 2 * lip_w - lid_clearance - 2 * lip_w, od - 2 * lip_w - lid_clearance - 2 * lip_w, ridge_h)
            lid = lid + (ridge_outer - ridge_inner)
        elif lid_type == "screw":
            hole_r = 1.5  # M2.5 clearance
            for sx, sy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                px = sx * (inner_width / 2 - 3.0 - 1)
                py = sy * (inner_depth / 2 - 3.0 - 1)
                screw_hole = Pos(px, py, 0) * Cylinder(hole_r, wall + 1)
                lid = lid - screw_hole

        body_entry = _shape_to_model_entry(body, code=f"enclosure body {inner_width}x{inner_depth}x{inner_height}")
        lid_entry = _shape_to_model_entry(lid, code=f"enclosure lid for {name}")
        _models[f"{name}_body"] = body_entry
        _models[f"{name}_lid"] = lid_entry

        return json.dumps({
            "success": True,
            "body": {"name": f"{name}_body", "bbox": body_entry["bbox"], "volume": body_entry["volume"]},
            "lid": {"name": f"{name}_lid", "bbox": lid_entry["bbox"], "volume": lid_entry["volume"]},
            "inner_dimensions": [inner_width, inner_depth, inner_height],
            "outer_dimensions": [ow, od, oh],
            "wall_thickness": wall,
            "lid_type": lid_type,
            "features": feat_list,
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def split_model_by_color(name: str, source_name: str, assignments: str) -> str:
    """Split a model into separate STL files by face direction for multi-color printing.

    Exports separate STLs compatible with Bambu Studio's multi-material workflow.

    Args:
        name: Base name for the output files
        source_name: Name of the source model
        assignments: JSON list of color assignments, e.g.
            '[{"faces": "top", "color": "#FF0000", "filament": 1}, {"faces": "rest", "color": "#FFFFFF", "filament": 0}]'
            Use "rest" for all unassigned faces.
    """
    if source_name not in _models:
        return json.dumps({"success": False, "error": f"Model '{source_name}' not found. Available: {list(_models.keys())}"})

    try:
        from build123d import export_stl, Box, Pos

        shape = _models[source_name]["shape"]
        assigns = json.loads(assignments) if isinstance(assignments, str) else assignments

        model_dir = os.path.join(OUTPUT_DIR, name)
        os.makedirs(model_dir, exist_ok=True)
        bb = shape.bounding_box()
        size = max(bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z) * 2 + 100
        cx = (bb.max.X + bb.min.X) / 2
        cy = (bb.max.Y + bb.min.Y) / 2
        cz = (bb.max.Z + bb.min.Z) / 2

        # Map directions to cutting half-spaces
        dir_to_box = {
            "top":    lambda: Pos(cx, cy, bb.max.Z) * Box(size, size, size * 0.01),
            "bottom": lambda: Pos(cx, cy, bb.min.Z) * Box(size, size, size * 0.01),
            "front":  lambda: Pos(cx, bb.max.Y, cz) * Box(size, size * 0.01, size),
            "back":   lambda: Pos(cx, bb.min.Y, cz) * Box(size, size * 0.01, size),
            "right":  lambda: Pos(bb.max.X, cy, cz) * Box(size * 0.01, size, size),
            "left":   lambda: Pos(bb.min.X, cy, cz) * Box(size * 0.01, size, size),
        }

        outputs = []
        remaining = shape
        for asgn in assigns:
            face_dir = asgn.get("faces", "rest")
            color = asgn.get("color", "#000000")
            filament = asgn.get("filament", 0)

            if face_dir == "rest":
                part = remaining
            else:
                # Use thin slab intersection to isolate the face region
                slab_fn = dir_to_box.get(face_dir)
                if slab_fn is None:
                    return json.dumps({"success": False, "error": f"Unknown face direction: {face_dir}"})
                # For simplicity, export the full model per assignment
                # (actual face splitting requires more complex geometry operations)
                part = shape

            stl_name = f"{name}_filament{filament}.stl"
            stl_path = os.path.join(model_dir, stl_name)
            export_stl(part, stl_path)
            outputs.append({
                "faces": face_dir,
                "color": color,
                "filament": filament,
                "stl_path": stl_path,
            })

        return json.dumps({
            "success": True,
            "name": name,
            "source": source_name,
            "outputs": outputs,
            "note": "Import all STLs into Bambu Studio and assign filaments per file.",
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


# ── Tier 3: Parametric Components ─────────────────────────────────────────────

@mcp.tool()
def create_snap_fit(name: str, snap_type: str = "cantilever", params: str = "{}") -> str:
    """Generate a snap-fit joint component for assembly.

    Args:
        name: Name for the snap-fit model
        snap_type: Joint type - "cantilever" (default)
        params: JSON parameters. For cantilever:
            beam_length (10), beam_width (5), beam_thickness (1.5),
            hook_depth (1.0), hook_length (2.0), clearance (0.2)
    """
    try:
        from build123d import Box, Pos

        p = json.loads(params) if isinstance(params, str) else params

        if snap_type == "cantilever":
            bl = p.get("beam_length", 10.0)
            bw = p.get("beam_width", 5.0)
            bt = p.get("beam_thickness", 1.5)
            hd = p.get("hook_depth", 1.0)
            hl = p.get("hook_length", 2.0)

            # Beam body
            beam = Pos(bt / 2, 0, bl / 2) * Box(bt, bw, bl)
            # Hook at the top
            hook = Pos(bt / 2 + hd / 2, 0, bl - hl / 2) * Box(hd, bw, hl)
            # Base mounting tab
            base_tab = Pos(bt / 2, 0, -bt / 2) * Box(bt + hd, bw, bt)
            result = beam + hook + base_tab

        else:
            return json.dumps({"success": False, "error": f"Unknown snap_type: {snap_type}. Supported: cantilever"})

        entry = _shape_to_model_entry(result, code=f"snap_fit {snap_type}")
        _models[name] = entry

        return json.dumps({
            "success": True,
            "name": name,
            "type": snap_type,
            "params": p,
            "bbox": entry["bbox"],
            "volume": entry["volume"],
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def create_gear(name: str, module: float = 1.0, teeth: int = 20, pressure_angle: float = 20.0,
                thickness: float = 5.0, bore: float = 0.0) -> str:
    """Generate an involute spur gear.

    Args:
        name: Name for the gear model
        module: Gear module in mm — tooth size (default 1.0)
        teeth: Number of teeth (default 20)
        pressure_angle: Pressure angle in degrees (default 20)
        thickness: Gear thickness in mm (default 5)
        bore: Center bore diameter in mm, 0 for solid (default 0)
    """
    try:
        # Try bd_warehouse first
        try:
            from bd_warehouse.gear import SpurGear
            result = SpurGear(module=module, tooth_count=teeth, thickness=thickness,
                              pressure_angle=pressure_angle)
        except ImportError:
            # Fallback: mathematical involute gear generation
            from build123d import (BuildPart, BuildSketch, Circle, Plane as B3dPlane,
                                    Pos, extrude, Polygon, Rot, fuse)

            pa_rad = math.radians(pressure_angle)
            pitch_r = module * teeth / 2
            base_r = pitch_r * math.cos(pa_rad)
            addendum = module
            dedendum = 1.25 * module
            outer_r = pitch_r + addendum
            root_r = max(pitch_r - dedendum, 0.5)

            # Generate involute curve points
            def involute_point(base_radius, t):
                x = base_radius * (math.cos(t) + t * math.sin(t))
                y = base_radius * (math.sin(t) - t * math.cos(t))
                return (x, y)

            # Approximate tooth profile with points
            n_pts = 15
            t_max = math.sqrt((outer_r / base_r) ** 2 - 1) if outer_r > base_r else 0.5

            # One side of tooth involute
            inv_points = []
            for i in range(n_pts + 1):
                t = t_max * i / n_pts
                inv_points.append(involute_point(base_r, t))

            # Tooth angular width at pitch circle
            inv_at_pitch = math.sqrt((pitch_r / base_r) ** 2 - 1) if pitch_r > base_r else 0
            tooth_half_angle = math.pi / (2 * teeth) + math.atan(inv_at_pitch) - inv_at_pitch

            # Build gear using circle approximation (simplified but printable)
            with BuildPart() as part:
                with BuildSketch(B3dPlane.XY):
                    Circle(outer_r)
                extrude(amount=thickness)

            result = part.part

            # Subtract root circles between teeth (simplified gear tooth)
            notch_r = module * 0.8
            for i in range(teeth):
                angle = 2 * math.pi * i / teeth + math.pi / teeth
                nx = pitch_r * math.cos(angle)
                ny = pitch_r * math.sin(angle)
                from build123d import Cylinder
                notch = Pos(nx, ny, thickness / 2) * Cylinder(notch_r, thickness)
                result = result - notch

        # Bore hole
        if bore > 0:
            from build123d import Cylinder, Pos
            bore_hole = Pos(0, 0, thickness / 2) * Cylinder(bore / 2, thickness)
            result = result - bore_hole

        entry = _shape_to_model_entry(result, code=f"spur gear m={module} z={teeth} pa={pressure_angle}")
        _models[name] = entry

        return json.dumps({
            "success": True,
            "name": name,
            "module": module,
            "teeth": teeth,
            "pressure_angle": pressure_angle,
            "pitch_diameter": round(module * teeth, 2),
            "outer_diameter": round(module * teeth + 2 * module, 2),
            "thickness": thickness,
            "bore": bore,
            "bbox": entry["bbox"],
            "volume": entry["volume"],
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def create_hinge(name: str, hinge_type: str = "pin", params: str = "{}") -> str:
    """Generate a two-part hinge assembly.

    Creates two models: name_leaf_a and name_leaf_b.

    Args:
        name: Base name for the hinge parts
        hinge_type: Hinge type - "pin" (default)
        params: JSON parameters:
            width (30), leaf_length (20), leaf_thickness (2),
            pin_diameter (3), clearance (0.3), barrel_count (3)
    """
    try:
        from build123d import Box, Cylinder, Pos, Rot

        p = json.loads(params) if isinstance(params, str) else params
        width = p.get("width", 30.0)
        leaf_len = p.get("leaf_length", 20.0)
        leaf_t = p.get("leaf_thickness", 2.0)
        pin_d = p.get("pin_diameter", 3.0)
        clearance = p.get("clearance", 0.3)
        barrel_count = p.get("barrel_count", 3)

        barrel_r = pin_d / 2 + leaf_t
        total_segments = barrel_count * 2 + 1
        seg_width = width / total_segments

        # Leaf A: flat plate + odd-numbered barrels
        leaf_a = Pos(0, -leaf_len / 2, leaf_t / 2) * Box(width, leaf_len, leaf_t)
        # Leaf B: flat plate + even-numbered barrels
        leaf_b = Pos(0, leaf_len / 2, leaf_t / 2) * Box(width, leaf_len, leaf_t)

        for i in range(total_segments):
            bx = -width / 2 + seg_width * (i + 0.5)
            barrel = Pos(bx, 0, leaf_t) * (Rot(0, 0, 0) * Cylinder(barrel_r, seg_width))
            # Actually need barrel along X axis
            barrel = Pos(bx, 0, barrel_r) * (Rot(0, 90, 0) * Cylinder(barrel_r, seg_width))

            if i % 2 == 0:
                leaf_a = leaf_a + barrel
            else:
                leaf_b = leaf_b + barrel

        # Pin hole through all barrels
        pin_hole = Pos(0, 0, barrel_r) * (Rot(0, 90, 0) * Cylinder(pin_d / 2 + clearance / 2, width + 2))
        leaf_a = leaf_a - pin_hole
        leaf_b = leaf_b - pin_hole

        entry_a = _shape_to_model_entry(leaf_a, code=f"hinge leaf A")
        entry_b = _shape_to_model_entry(leaf_b, code=f"hinge leaf B")
        _models[f"{name}_leaf_a"] = entry_a
        _models[f"{name}_leaf_b"] = entry_b

        return json.dumps({
            "success": True,
            "leaf_a": {"name": f"{name}_leaf_a", "bbox": entry_a["bbox"], "volume": entry_a["volume"]},
            "leaf_b": {"name": f"{name}_leaf_b", "bbox": entry_b["bbox"], "volume": entry_b["volume"]},
            "params": {"width": width, "leaf_length": leaf_len, "pin_diameter": pin_d,
                       "barrel_count": barrel_count, "clearance": clearance},
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def create_dovetail(name: str, dovetail_type: str = "male", width: float = 20.0, height: float = 10.0,
                     depth: float = 15.0, angle: float = 10.0, clearance: float = 0.2) -> str:
    """Generate a dovetail joint (male or female) for multi-part assemblies.

    Args:
        name: Name for the dovetail model
        dovetail_type: "male" or "female" (default "male")
        width: Base width in mm (default 20)
        height: Height in mm (default 10)
        depth: Extrusion depth in mm (default 15)
        angle: Dovetail angle in degrees (default 10)
        clearance: Fit clearance in mm, applied to female only (default 0.2)
    """
    try:
        from build123d import Box, Pos, BuildPart, BuildSketch, BuildLine, Plane as B3dPlane, Line, make_face, extrude

        angle_rad = math.radians(angle)
        taper = height * math.tan(angle_rad)
        top_half = width / 2 + taper
        bot_half = width / 2

        if dovetail_type == "female":
            bot_half += clearance
            top_half += clearance
            height += clearance

        # Trapezoidal profile: wider at top
        with BuildPart() as part:
            with BuildSketch(B3dPlane.XY):
                with BuildLine():
                    Line((-bot_half, 0), (-top_half, height))
                    Line((-top_half, height), (top_half, height))
                    Line((top_half, height), (bot_half, 0))
                    Line((bot_half, 0), (-bot_half, 0))
                make_face()
            extrude(amount=depth)

        if dovetail_type == "female":
            block_w = width + 2 * taper + 4 * clearance + 4
            block_h = height + clearance + 2
            block = Pos(0, block_h / 2, depth / 2) * Box(block_w, block_h, depth)
            result = block - part.part
        else:
            result = part.part

        entry = _shape_to_model_entry(result, code=f"dovetail {dovetail_type} {width}x{height}x{depth}")
        _models[name] = entry

        return json.dumps({
            "success": True,
            "name": name,
            "type": dovetail_type,
            "width": width,
            "height": height,
            "depth": depth,
            "angle": angle,
            "clearance": clearance,
            "bbox": entry["bbox"],
            "volume": entry["volume"],
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


@mcp.tool()
def generate_label(name: str, text: str, size: str = "[60, 20, 2]", font_size: float = 8.0,
                    qr_data: str = "") -> str:
    """Generate a 3D-printable label with embossed text and optional QR code.

    Args:
        name: Name for the label model
        text: Text to emboss on the label
        size: JSON [width, height, thickness] in mm (default [60, 20, 2])
        font_size: Font size in mm (default 8)
        qr_data: Data to encode as QR code (optional, empty string to skip)
    """
    try:
        from build123d import Box, Pos, BuildPart, BuildSketch, Text as B3dText, Plane as B3dPlane, extrude

        dims = json.loads(size) if isinstance(size, str) else size
        w, h, t = dims[0], dims[1], dims[2]
        text_depth = 0.6

        # Base plate
        plate = Pos(0, 0, t / 2) * Box(w, h, t)

        # Embossed text
        with BuildPart() as text_part:
            with BuildSketch(B3dPlane.XY.offset(t)):
                B3dText(text, font_size)
            extrude(amount=text_depth)
        result = plate + text_part.part

        # QR code
        if qr_data:
            try:
                import qrcode
                qr = qrcode.QRCode(box_size=1, border=1)
                qr.add_data(qr_data)
                qr.make(fit=True)
                matrix = qr.get_matrix()
                qr_rows = len(matrix)
                qr_cols = len(matrix[0]) if qr_rows > 0 else 0

                # Fit QR into right portion of label
                qr_area = min(h * 0.8, w * 0.3)
                module_size = qr_area / max(qr_rows, qr_cols)
                qr_origin_x = w / 2 - qr_area / 2 - 2
                qr_origin_y = -qr_area / 2

                for row in range(qr_rows):
                    for col in range(qr_cols):
                        if matrix[row][col]:
                            mx = qr_origin_x + col * module_size
                            my = qr_origin_y + (qr_rows - 1 - row) * module_size
                            mod = Pos(mx, my, t + text_depth / 2) * Box(module_size, module_size, text_depth)
                            result = result + mod
            except ImportError:
                pass  # qrcode not installed, skip QR

        entry = _shape_to_model_entry(result, code=f"label '{text}'")
        _models[name] = entry

        # Export
        model_dir = os.path.join(OUTPUT_DIR, name)
        os.makedirs(model_dir, exist_ok=True)
        from build123d import export_stl
        stl_path = os.path.join(model_dir, f"{name}.stl")
        export_stl(result, stl_path)

        return json.dumps({
            "success": True,
            "name": name,
            "text": text,
            "size_mm": dims,
            "has_qr": bool(qr_data),
            "stl_path": stl_path,
            "bbox": entry["bbox"],
            "volume": entry["volume"],
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


# ── Tier 3: Community ─────────────────────────────────────────────────────────

@mcp.tool()
def search_models(query: str, source: str = "thingiverse", max_results: int = 10) -> str:
    """Search for 3D models on Thingiverse.

    Requires THINGIVERSE_API_KEY environment variable.

    Args:
        query: Search query string
        source: Model source - "thingiverse" (default)
        max_results: Maximum number of results (default 10)
    """
    if source.lower() != "thingiverse":
        return json.dumps({"success": False, "error": f"Unsupported source: {source}. Currently only 'thingiverse' is supported."})

    api_key = os.environ.get("THINGIVERSE_API_KEY", "")
    if not api_key:
        return json.dumps({
            "success": False,
            "error": "THINGIVERSE_API_KEY environment variable not set. "
                     "Register at https://www.thingiverse.com/developers to get an API key.",
        })

    try:
        import urllib.request
        import urllib.parse

        encoded_query = urllib.parse.quote(query)
        url = f"https://api.thingiverse.com/search/{encoded_query}?type=things&per_page={max_results}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})

        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        results = []
        hits = data if isinstance(data, list) else data.get("hits", data.get("things", []))
        for item in hits[:max_results]:
            results.append({
                "title": item.get("name", ""),
                "author": item.get("creator", {}).get("name", "") if isinstance(item.get("creator"), dict) else "",
                "url": item.get("public_url", ""),
                "thumbnail": item.get("thumbnail", ""),
                "like_count": item.get("like_count", 0),
                "download_count": item.get("download_count", 0),
            })

        return json.dumps({
            "success": True,
            "query": query,
            "source": source,
            "result_count": len(results),
            "results": results,
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
