"""Parametric component tools — enclosures, gears, snap fits, hinges, dovetails, labels."""

import json
import math
import os
import traceback

from threedp_mcp.helpers import shape_to_model_entry


def register(mcp, models: dict, output_dir: str):
    """Register parametric component tools with MCP server."""

    @mcp.tool()
    def create_enclosure(
        name: str,
        inner_width: float,
        inner_depth: float,
        inner_height: float,
        wall: float = 2.0,
        lid_type: str = "snap",
        features: str = "[]",
    ) -> str:
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
            from build123d import Box, Cylinder, Pos

            if inner_width <= 0 or inner_depth <= 0 or inner_height <= 0:
                return json.dumps({"success": False, "error": "Dimensions must be positive"})

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
                from build123d import Rot

                cable_hole = Pos(0, -od / 2, wall + inner_height / 2) * (Rot(90, 0, 0) * Cylinder(cable_r, wall + 1))
                body = body - cable_hole

            # Lid
            lid_clearance = 0.2
            lid = Pos(0, 0, wall / 2) * Box(ow, od, wall)
            if lid_type == "snap":
                ridge_h = lip_h - lid_clearance
                ridge_outer = Pos(0, 0, wall + ridge_h / 2) * Box(
                    ow - 2 * lip_w - lid_clearance, od - 2 * lip_w - lid_clearance, ridge_h
                )
                ridge_inner = Pos(0, 0, wall + ridge_h / 2) * Box(
                    ow - 2 * lip_w - lid_clearance - 2 * lip_w, od - 2 * lip_w - lid_clearance - 2 * lip_w, ridge_h
                )
                lid = lid + (ridge_outer - ridge_inner)
            elif lid_type == "screw":
                hole_r = 1.5  # M2.5 clearance
                for sx, sy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    px = sx * (inner_width / 2 - 3.0 - 1)
                    py = sy * (inner_depth / 2 - 3.0 - 1)
                    screw_hole = Pos(px, py, 0) * Cylinder(hole_r, wall + 1)
                    lid = lid - screw_hole

            body_entry = shape_to_model_entry(body, code=f"enclosure body {inner_width}x{inner_depth}x{inner_height}")
            lid_entry = shape_to_model_entry(lid, code=f"enclosure lid for {name}")
            models[f"{name}_body"] = body_entry
            models[f"{name}_lid"] = lid_entry

            return json.dumps(
                {
                    "success": True,
                    "body": {"name": f"{name}_body", "bbox": body_entry["bbox"], "volume": body_entry["volume"]},
                    "lid": {"name": f"{name}_lid", "bbox": lid_entry["bbox"], "volume": lid_entry["volume"]},
                    "inner_dimensions": [inner_width, inner_depth, inner_height],
                    "outer_dimensions": [ow, od, oh],
                    "wall_thickness": wall,
                    "lid_type": lid_type,
                    "features": feat_list,
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)

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

            entry = shape_to_model_entry(result, code=f"snap_fit {snap_type}")
            models[name] = entry

            return json.dumps(
                {
                    "success": True,
                    "name": name,
                    "type": snap_type,
                    "params": p,
                    "bbox": entry["bbox"],
                    "volume": entry["volume"],
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)

    @mcp.tool()
    def create_gear(
        name: str,
        module: float = 1.0,
        teeth: int = 20,
        pressure_angle: float = 20.0,
        thickness: float = 5.0,
        bore: float = 0.0,
    ) -> str:
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
            if teeth <= 0:
                return json.dumps({"success": False, "error": "teeth must be greater than zero"})

            # Try bd_warehouse first
            try:
                from bd_warehouse.gear import SpurGear

                result = SpurGear(module=module, tooth_count=teeth, thickness=thickness, pressure_angle=pressure_angle)
            except ImportError:
                # Fallback: mathematical involute gear generation
                from build123d import BuildPart, BuildSketch, Circle, Pos, extrude
                from build123d import Plane as B3dPlane

                pa_rad = math.radians(pressure_angle)
                pitch_r = module * teeth / 2
                base_r = pitch_r * math.cos(pa_rad)
                addendum = module
                dedendum = 1.25 * module
                outer_r = pitch_r + addendum
                max(pitch_r - dedendum, 0.5)

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
                math.pi / (2 * teeth) + math.atan(inv_at_pitch) - inv_at_pitch

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

            entry = shape_to_model_entry(result, code=f"spur gear m={module} z={teeth} pa={pressure_angle}")
            models[name] = entry

            return json.dumps(
                {
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
                },
                indent=2,
            )

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
                # Barrel along X axis
                barrel = Pos(bx, 0, barrel_r) * (Rot(0, 90, 0) * Cylinder(barrel_r, seg_width))

                if i % 2 == 0:
                    leaf_a = leaf_a + barrel
                else:
                    leaf_b = leaf_b + barrel

            # Pin hole through all barrels
            pin_hole = Pos(0, 0, barrel_r) * (Rot(0, 90, 0) * Cylinder(pin_d / 2 + clearance / 2, width + 2))
            leaf_a = leaf_a - pin_hole
            leaf_b = leaf_b - pin_hole

            entry_a = shape_to_model_entry(leaf_a, code="hinge leaf A")
            entry_b = shape_to_model_entry(leaf_b, code="hinge leaf B")
            models[f"{name}_leaf_a"] = entry_a
            models[f"{name}_leaf_b"] = entry_b

            return json.dumps(
                {
                    "success": True,
                    "leaf_a": {"name": f"{name}_leaf_a", "bbox": entry_a["bbox"], "volume": entry_a["volume"]},
                    "leaf_b": {"name": f"{name}_leaf_b", "bbox": entry_b["bbox"], "volume": entry_b["volume"]},
                    "params": {
                        "width": width,
                        "leaf_length": leaf_len,
                        "pin_diameter": pin_d,
                        "barrel_count": barrel_count,
                        "clearance": clearance,
                    },
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)

    @mcp.tool()
    def create_dovetail(
        name: str,
        dovetail_type: str = "male",
        width: float = 20.0,
        height: float = 10.0,
        depth: float = 15.0,
        angle: float = 10.0,
        clearance: float = 0.2,
    ) -> str:
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
            from build123d import Box, BuildLine, BuildPart, BuildSketch, Line, Pos, extrude, make_face
            from build123d import Plane as B3dPlane

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

            entry = shape_to_model_entry(result, code=f"dovetail {dovetail_type} {width}x{height}x{depth}")
            models[name] = entry

            return json.dumps(
                {
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
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)

    @mcp.tool()
    def generate_label(
        name: str, text: str, size: str = "[60, 20, 2]", font_size: float = 8.0, qr_data: str = ""
    ) -> str:
        """Generate a 3D-printable label with embossed text and optional QR code.

        Args:
            name: Name for the label model
            text: Text to emboss on the label
            size: JSON [width, height, thickness] in mm (default [60, 20, 2])
            font_size: Font size in mm (default 8)
            qr_data: Data to encode as QR code (optional, empty string to skip)
        """
        try:
            if not text:
                return json.dumps({"success": False, "error": "text must not be empty"})

            from build123d import Box, BuildPart, BuildSketch, Pos, extrude
            from build123d import Plane as B3dPlane
            from build123d import Text as B3dText

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

            entry = shape_to_model_entry(result, code=f"label '{text}'")
            models[name] = entry

            # Export
            model_dir = os.path.join(output_dir, name)
            os.makedirs(model_dir, exist_ok=True)
            from build123d import export_stl

            stl_path = os.path.join(model_dir, f"{name}.stl")
            export_stl(result, stl_path)

            return json.dumps(
                {
                    "success": True,
                    "name": name,
                    "text": text,
                    "size_mm": dims,
                    "has_qr": bool(qr_data),
                    "stl_path": stl_path,
                    "bbox": entry["bbox"],
                    "volume": entry["volume"],
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}, indent=2)
