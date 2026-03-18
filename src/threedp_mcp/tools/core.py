"""Core tools — create, export, measure, analyze, list, get code."""

import json
import os
import traceback

from threedp_mcp.helpers import run_build123d_code


def register(mcp, models: dict, output_dir: str):
    """Register core tools with the MCP server."""

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

            result = run_build123d_code(code)
            models[name] = result

            model_dir = os.path.join(output_dir, name)
            os.makedirs(model_dir, exist_ok=True)

            from build123d import export_step, export_stl

            stl_path = os.path.join(model_dir, f"{name}.stl")
            step_path = os.path.join(model_dir, f"{name}.step")
            export_stl(result["shape"], stl_path)
            export_step(result["shape"], step_path)

            return json.dumps(
                {
                    "success": True,
                    "name": name,
                    "bbox": result["bbox"],
                    "volume": result["volume"],
                    "outputs": {"stl": stl_path, "step": step_path},
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps(
                {
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                },
                indent=2,
            )

    @mcp.tool()
    def export_model(name: str, format: str = "stl") -> str:
        """Export a model to STL, STEP, or 3MF format.

        Args:
            name: Name of a previously created model
            format: Export format - "stl", "step", or "3mf"
        """
        if name not in models:
            return json.dumps(
                {"success": False, "error": f"Model '{name}' not found. Available: {list(models.keys())}"}
            )

        model = models[name]
        model_dir = os.path.join(output_dir, name)
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
        if name not in models:
            return json.dumps(
                {"success": False, "error": f"Model '{name}' not found. Available: {list(models.keys())}"}
            )

        shape = models[name]["shape"]
        bb = models[name]["bbox"]
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
        if name not in models:
            return json.dumps(
                {"success": False, "error": f"Model '{name}' not found. Available: {list(models.keys())}"}
            )

        shape = models[name]["shape"]
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

        bb = models[name]["bbox"]
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

        return json.dumps(
            {
                "verdict": "PRINTABLE" if not issues else "REVIEW NEEDED",
                "issues": issues,
                "checks": checks,
                "printer": "Bambu Lab X1C (256x256x256mm)",
            },
            indent=2,
        )

    @mcp.tool()
    def list_models() -> str:
        """List all models currently loaded in this session."""
        if not models:
            return json.dumps({"models": [], "message": "No models yet. Use create_model to make one."})

        return json.dumps(
            {"models": [{"name": n, "bbox": d["bbox"], "volume": d["volume"]} for n, d in models.items()]}, indent=2
        )

    @mcp.tool()
    def get_model_code(name: str) -> str:
        """Retrieve the build123d code used to create a model.

        Args:
            name: Name of a previously created model
        """
        if name not in models:
            return json.dumps(
                {"success": False, "error": f"Model '{name}' not found. Available: {list(models.keys())}"}
            )

        return json.dumps({"name": name, "code": models[name]["code"]})
