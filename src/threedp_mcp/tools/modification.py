"""Modification tools — shell, split, add text, threaded holes."""

import json
import traceback

from threedp_mcp.constants import ISO_THREAD_TABLE
from threedp_mcp.helpers import select_face, shape_to_model_entry


def register(mcp, models: dict, output_dir: str):
    """Register modification tools with MCP server."""

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
        if source_name not in models:
            return json.dumps(
                {"success": False, "error": f"Model '{source_name}' not found. Available: {list(models.keys())}"}
            )

        try:
            shape = models[source_name]["shape"]
            faces_to_open = json.loads(open_faces) if isinstance(open_faces, str) else open_faces

            openings = [select_face(shape, fd) for fd in faces_to_open]
            result = shape.shell(openings=openings, thickness=-thickness)

            entry = shape_to_model_entry(result, code=f"shell of {source_name}, thickness={thickness}")
            models[name] = entry

            return json.dumps(
                {
                    "success": True,
                    "name": name,
                    "source": source_name,
                    "thickness_mm": thickness,
                    "open_faces": faces_to_open,
                    "bbox": entry["bbox"],
                    "volume": entry["volume"],
                },
                indent=2,
            )

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
        if source_name not in models:
            return json.dumps(
                {"success": False, "error": f"Model '{source_name}' not found. Available: {list(models.keys())}"}
            )

        try:
            from build123d import Box, Pos

            shape = models[source_name]["shape"]
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
                above_entry = shape_to_model_entry(above_shape, code=f"split {source_name} above {plane}")
                result_name = f"{name}_above" if keep == "both" else name
                models[result_name] = above_entry
                results[result_name] = {"bbox": above_entry["bbox"], "volume": above_entry["volume"]}

            if keep in ("below", "both"):
                below_shape = shape & below_box
                below_entry = shape_to_model_entry(below_shape, code=f"split {source_name} below {plane}")
                result_name = f"{name}_below" if keep == "both" else name
                models[result_name] = below_entry
                results[result_name] = {"bbox": below_entry["bbox"], "volume": below_entry["volume"]}

            return json.dumps(
                {
                    "success": True,
                    "source": source_name,
                    "plane": plane,
                    "keep": keep,
                    "results": results,
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)

    @mcp.tool()
    def add_text(
        name: str,
        source_name: str,
        text: str,
        face: str = "top",
        font_size: float = 10.0,
        depth: float = 1.0,
        font: str = "Arial",
        emboss: bool = True,
    ) -> str:
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
        if source_name not in models:
            return json.dumps(
                {"success": False, "error": f"Model '{source_name}' not found. Available: {list(models.keys())}"}
            )

        try:
            from build123d import BuildPart, BuildSketch, extrude
            from build123d import Plane as B3dPlane
            from build123d import Text as B3dText

            shape = models[source_name]["shape"]
            target_face = select_face(shape, face)
            fc = target_face.center()

            # Determine sketch plane and extrude direction based on face
            face_normal = target_face.normal_at()
            sketch_plane = B3dPlane(origin=(fc.X, fc.Y, fc.Z), z_dir=(face_normal.X, face_normal.Y, face_normal.Z))

            with BuildPart() as text_part:
                with BuildSketch(sketch_plane):
                    B3dText(text, font_size, font=font)
                extrude(amount=depth)

            text_solid = text_part.part

            if emboss:
                result = shape + text_solid
            else:
                result = shape - text_solid

            entry = shape_to_model_entry(
                result, code=f"{'emboss' if emboss else 'deboss'} '{text}' on {face} of {source_name}"
            )
            models[name] = entry

            return json.dumps(
                {
                    "success": True,
                    "name": name,
                    "source": source_name,
                    "text": text,
                    "face": face,
                    "emboss": emboss,
                    "depth_mm": depth,
                    "bbox": entry["bbox"],
                    "volume": entry["volume"],
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)

    @mcp.tool()
    def create_threaded_hole(
        name: str, source_name: str, position: str, thread_spec: str = "M3", depth: float = 10.0, insert: bool = False
    ) -> str:
        """Add a threaded or heat-set insert hole to a model.

        Args:
            name: Name for the resulting model
            source_name: Name of the source model
            position: JSON [x, y, z] position for the hole center
            thread_spec: ISO metric thread spec - M2, M2.5, M3, M4, M5, M6, M8, M10 (default M3)
            depth: Hole depth in mm (default 10)
            insert: If true, use heat-set insert diameter instead of tap drill (default false)
        """
        if source_name not in models:
            return json.dumps(
                {"success": False, "error": f"Model '{source_name}' not found. Available: {list(models.keys())}"}
            )

        spec = thread_spec.upper()
        if spec not in ISO_THREAD_TABLE:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Unknown thread spec: {thread_spec}. Supported: {list(ISO_THREAD_TABLE.keys())}",
                }
            )

        try:
            from build123d import Cylinder, Pos

            pos = json.loads(position) if isinstance(position, str) else position
            thread = ISO_THREAD_TABLE[spec]
            diameter = thread["insert_drill"] if insert else thread["tap_drill"]
            radius = diameter / 2.0

            hole = Pos(pos[0], pos[1], pos[2]) * Cylinder(radius, depth)
            shape = models[source_name]["shape"]
            result = shape - hole

            entry = shape_to_model_entry(result, code=f"{spec} {'insert' if insert else 'threaded'} hole at {pos}")
            models[name] = entry

            return json.dumps(
                {
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
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)
