"""Utility tools — shrinkage compensation, pack models, convert format."""

import json
import os
import traceback

from threedp_mcp.constants import MATERIAL_PROPERTIES
from threedp_mcp.helpers import shape_to_model_entry


def register(mcp, models: dict, output_dir: str):
    """Register utility tools with MCP server."""

    @mcp.tool()
    def shrinkage_compensation(name: str, source_name: str, material: str = "PLA") -> str:
        """Scale a model to compensate for material shrinkage after printing.

        Args:
            name: Name for the compensated model
            source_name: Name of the source model
            material: Filament material (default PLA). Supports PLA, PETG, ABS, ASA, TPU, Nylon.
        """
        if source_name not in models:
            return json.dumps(
                {"success": False, "error": f"Model '{source_name}' not found. Available: {list(models.keys())}"}
            )

        mat = material.upper()
        if mat not in MATERIAL_PROPERTIES:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Unknown material: {material}. Supported: {list(MATERIAL_PROPERTIES.keys())}",
                }
            )

        try:
            shrinkage = MATERIAL_PROPERTIES[mat]["shrinkage"]
            factor = 1.0 / (1.0 - shrinkage)

            shape = models[source_name]["shape"]
            compensated = shape.scale(factor)

            entry = shape_to_model_entry(
                compensated, code=f"shrinkage compensation of {source_name} for {mat} (×{factor:.5f})"
            )
            models[name] = entry

            return json.dumps(
                {
                    "success": True,
                    "name": name,
                    "source": source_name,
                    "material": mat,
                    "shrinkage_pct": round(shrinkage * 100, 2),
                    "scale_factor": round(factor, 5),
                    "original_bbox": models[source_name]["bbox"],
                    "compensated_bbox": entry["bbox"],
                },
                indent=2,
            )

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
            from build123d import Compound, pack

            names = json.loads(model_names) if isinstance(model_names, str) else model_names

            if not names:
                return json.dumps({"success": False, "error": "model_names list is empty"})

            shapes = []
            for n in names:
                if n not in models:
                    return json.dumps(
                        {"success": False, "error": f"Model '{n}' not found. Available: {list(models.keys())}"}
                    )
                shapes.append(models[n]["shape"])

            packed = pack(shapes, padding, align_z=True)
            compound = Compound(children=list(packed))

            entry = shape_to_model_entry(compound, code=f"pack of {names}")
            models[name] = entry

            positions = []
            for i, s in enumerate(packed):
                bb = s.bounding_box()
                positions.append(
                    {
                        "model": names[i],
                        "center": [
                            round(bb.min.X + (bb.max.X - bb.min.X) / 2, 1),
                            round(bb.min.Y + (bb.max.Y - bb.min.Y) / 2, 1),
                        ],
                    }
                )

            return json.dumps(
                {
                    "success": True,
                    "name": name,
                    "packed_count": len(names),
                    "positions": positions,
                    "bbox": entry["bbox"],
                },
                indent=2,
            )

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
            if not os.path.exists(input_path):
                return json.dumps({"success": False, "error": f"Input file not found: {input_path}"})

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

            return json.dumps(
                {
                    "success": True,
                    "input": input_path,
                    "output": output_path,
                    "input_format": in_ext,
                    "output_format": out_ext,
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)
