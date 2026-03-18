"""Shared helper functions for 3DP MCP Server."""

import math
import os


def sanitize_name(name: str) -> str:
    """Sanitize a model name to prevent path traversal. Raises ValueError if unsafe."""
    clean = os.path.basename(name.replace("\\", "/"))
    if not clean or clean in (".", ".."):
        raise ValueError(f"Invalid model name: '{name}'")
    if "\x00" in clean:
        raise ValueError(f"Invalid model name (null byte): '{name}'")
    return clean


def safe_output_path(output_dir: str, *parts: str) -> str:
    """Join path parts under output_dir and verify the result stays inside it."""
    candidate = os.path.realpath(os.path.join(output_dir, *parts))
    real_output = os.path.realpath(output_dir)
    if not candidate.startswith(real_output + os.sep) and candidate != real_output:
        raise ValueError(f"Path escapes output directory: {candidate}")
    return candidate


def shape_to_model_entry(shape, code: str = "") -> dict:
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


def run_build123d_code(code: str) -> dict:
    """Execute build123d code and return a model entry dict.

    The code must assign the final shape to a variable called `result`.
    """
    local_ns: dict = {}
    exec_globals = {"__builtins__": __builtins__}
    # NOTE: Python exec() is used intentionally here to run user-provided build123d CAD code.
    # This is the core mechanism of the MCP server — it executes parametric CAD scripts.
    exec(code, exec_globals, local_ns)  # noqa: S102

    if "result" not in local_ns:
        raise ValueError("Code must assign the final shape to a variable called `result`")

    return shape_to_model_entry(local_ns["result"], code)


def select_face(shape, direction: str):
    """Select a face by direction name (top/bottom/front/back/left/right)."""
    all_faces = shape.faces()
    selectors = {
        "top": lambda f: f.center().Z,
        "bottom": lambda f: -f.center().Z,
        "front": lambda f: f.center().Y,
        "back": lambda f: -f.center().Y,
        "right": lambda f: f.center().X,
        "left": lambda f: -f.center().X,
    }
    key_fn = selectors.get(direction.lower())
    if key_fn is None:
        raise ValueError(f"Unknown face direction: {direction}. Use: {list(selectors.keys())}")
    return max(all_faces, key=key_fn)


def compute_overhangs(shape, max_angle_deg: float = 45.0) -> dict:
    """Compute overhang statistics for a shape.

    Returns dict with face count, areas, angles, and overhang percentage.
    """
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


def ensure_exported(name: str, models: dict, output_dir: str, fmt: str = "stl") -> str:
    """Ensure a model is exported and return the file path.

    Args:
        name: Model name in the models dict.
        models: The session models dictionary.
        output_dir: Directory to write exported files.
        fmt: Export format — "stl" or "step".
    """
    if name not in models:
        raise ValueError(f"Model '{name}' not found. Use list_models() to see available models.")
    path = os.path.join(output_dir, f"{name}.{fmt}")
    if not os.path.exists(path):
        from build123d import export_step, export_stl

        shape = models[name]["shape"]
        if fmt == "stl":
            export_stl(shape, path)
        elif fmt == "step":
            export_step(shape, path)
        else:
            raise ValueError(f"Unsupported format for publishing: {fmt}")
    return path
