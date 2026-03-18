"""Transform tools — transform, combine, import models."""

import json
import os
import traceback

from threedp_mcp.helpers import shape_to_model_entry


def register(mcp, models: dict, output_dir: str):
    """Register transform tools with the MCP server."""

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
        if source_name not in models:
            return json.dumps(
                {"success": False, "error": f"Model '{source_name}' not found. Available: {list(models.keys())}"}
            )

        try:
            from build123d import Mirror, Pos, Rot
            from build123d import Plane as B3dPlane

            shape = models[source_name]["shape"]
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
                        return json.dumps(
                            {"success": False, "error": f"Unknown mirror plane: {op['mirror']}. Use XY, XZ, or YZ."}
                        )
                    shape = Mirror(about=mirror_plane) * shape
                if "translate" in op:
                    tx, ty, tz = op["translate"]
                    shape = Pos(tx, ty, tz) * shape

            entry = shape_to_model_entry(shape, code=f"transform of {source_name}: {operations}")
            models[name] = entry

            return json.dumps(
                {
                    "success": True,
                    "name": name,
                    "source": source_name,
                    "bbox": entry["bbox"],
                    "volume": entry["volume"],
                },
                indent=2,
            )

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
                return json.dumps(
                    {"success": False, "error": f"Unsupported file type: {ext}. Use .stl, .step, or .stp."}
                )

            entry = shape_to_model_entry(shape, code=f"imported from {file_path}")
            models[name] = entry

            return json.dumps(
                {
                    "success": True,
                    "name": name,
                    "file": file_path,
                    "bbox": entry["bbox"],
                    "volume": entry["volume"],
                },
                indent=2,
            )

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
            if m not in models:
                return json.dumps(
                    {"success": False, "error": f"Model '{m}' not found. Available: {list(models.keys())}"}
                )

        try:
            a = models[model_a]["shape"]
            b = models[model_b]["shape"]

            op = operation.lower()
            if op == "union":
                result = a + b
            elif op == "subtract":
                result = a - b
            elif op == "intersect":
                result = a & b
            else:
                return json.dumps(
                    {"success": False, "error": f"Unknown operation: {operation}. Use union, subtract, or intersect."}
                )

            entry = shape_to_model_entry(result, code=f"{model_a} {op} {model_b}")
            models[name] = entry

            return json.dumps(
                {
                    "success": True,
                    "name": name,
                    "operation": op,
                    "model_a": model_a,
                    "model_b": model_b,
                    "bbox": entry["bbox"],
                    "volume": entry["volume"],
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)
