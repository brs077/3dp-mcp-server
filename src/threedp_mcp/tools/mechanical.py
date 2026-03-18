"""Mechanical parts tools — threads, fasteners, bearings, sprockets, flanges, pipes, OpenBuilds."""

import importlib
import json
import math
import os
import traceback

from threedp_mcp.helpers import safe_output_path, sanitize_name, shape_to_model_entry


def register(mcp, models: dict, output_dir: str):
    """Register mechanical parts tools with MCP server."""

    def _export_and_store(name, result, code):
        """Store model and export STL + STEP."""
        entry = shape_to_model_entry(result, code=code)
        models[name] = entry

        model_dir = safe_output_path(output_dir, name)
        os.makedirs(model_dir, exist_ok=True)

        from build123d import export_step, export_stl

        stl_path = os.path.join(model_dir, f"{name}.stl")
        step_path = os.path.join(model_dir, f"{name}.step")
        export_stl(result, stl_path)
        export_step(result, step_path)
        return entry, stl_path, step_path

    @mcp.tool()
    def create_thread(
        name: str,
        thread_type: str = "iso",
        major_diameter: float = 10.0,
        pitch: float = 1.5,
        length: float = 20.0,
        external: bool = True,
        hand: str = "right",
        end_finishes: str = '["fade", "square"]',
        size: str = "",
        manufacturing_compensation: float = 0.0,
    ) -> str:
        """Create a threaded part (bolt shaft, nut bore, bottle thread, lead screw, etc.).

        Generates actual 3D thread geometry using bd_warehouse — not just drill holes.

        Args:
            name: Name for the model
            thread_type: Thread profile — "iso" (metric 60°), "acme" (29°, imperial),
                "metric_trapezoidal" (30°, metric lead screws), "plastic_bottle" (ASTM D2911)
            major_diameter: Major diameter in mm (iso only, ignored for acme/metric_trap/bottle)
            pitch: Thread pitch in mm (iso only)
            length: Thread length in mm (not used for plastic_bottle)
            external: True = male/bolt thread, False = female/nut thread
            hand: "right" or "left" hand thread
            end_finishes: JSON list of two finishes [start, end].
                Options: "raw", "square", "fade", "chamfer"
            size: Size string for acme ("3/8"), metric_trapezoidal ("10x2"),
                or plastic_bottle ("L38SP400")
            manufacturing_compensation: FDM printing compensation in mm
                (plastic_bottle only, try 0.2)
        """
        try:
            name = sanitize_name(name)
            finishes = json.loads(end_finishes) if isinstance(end_finishes, str) else end_finishes
            tt = thread_type.lower().replace(" ", "_")

            if tt == "iso":
                from bd_warehouse.thread import IsoThread

                result = IsoThread(
                    major_diameter=major_diameter, pitch=pitch, length=length,
                    external=external, hand=hand,
                    end_finishes=tuple(finishes), simple=False,
                )
            elif tt == "acme":
                from bd_warehouse.thread import AcmeThread

                if not size:
                    return json.dumps({
                        "success": False,
                        "error": "acme thread requires 'size' (e.g. '3/8', '1/2')",
                    })
                result = AcmeThread(
                    size=size, length=length, external=external,
                    hand=hand, end_finishes=tuple(finishes),
                )
            elif tt in ("metric_trapezoidal", "metric_trap", "trapezoidal"):
                from bd_warehouse.thread import MetricTrapezoidalThread

                if not size:
                    return json.dumps({
                        "success": False,
                        "error": "metric_trapezoidal requires 'size' (e.g. '10x2')",
                    })
                result = MetricTrapezoidalThread(
                    size=size, length=length, external=external,
                    hand=hand, end_finishes=tuple(finishes),
                )
            elif tt in ("plastic_bottle", "bottle"):
                from bd_warehouse.thread import PlasticBottleThread

                if not size:
                    return json.dumps({
                        "success": False,
                        "error": "plastic_bottle requires 'size' (e.g. 'L38SP400')",
                    })
                result = PlasticBottleThread(
                    size=size, external=external, hand=hand,
                    manufacturing_compensation=manufacturing_compensation,
                )
            else:
                types = "iso, acme, metric_trapezoidal, plastic_bottle"
                return json.dumps({
                    "success": False,
                    "error": f"Unknown thread_type: {thread_type}. Use: {types}",
                })

            ext_str = "external" if external else "internal"
            entry, stl_path, step_path = _export_and_store(
                name, result, f"{tt} thread {ext_str}",
            )

            return json.dumps({
                "success": True, "name": name, "thread_type": tt,
                "external": external, "hand": hand,
                "bbox": entry["bbox"], "volume": entry["volume"],
                "outputs": {"stl": stl_path, "step": step_path},
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False, "error": str(e),
                "traceback": traceback.format_exc(),
            }, indent=2)

    @mcp.tool()
    def create_fastener(
        name: str,
        fastener_class: str = "socket_head_cap_screw",
        size: str = "M3-0.5",
        length: float = 10.0,
        fastener_type: str = "",
        simple: bool = True,
        hand: str = "right",
    ) -> str:
        """Create a parametric screw, nut, washer, or heat-set insert with real geometry.

        Args:
            name: Name for the model
            fastener_class: One of:
                Screws: "socket_head_cap_screw", "hex_head_screw", "button_head_screw",
                    "counter_sunk_screw", "pan_head_screw", "set_screw", "low_profile_screw"
                Nuts: "hex_nut", "hex_nut_with_flange", "square_nut", "domed_cap_nut"
                Washers: "plain_washer", "chamfered_washer"
                Inserts: "heat_set_nut"
            size: ISO size string (e.g. "M3-0.5", "M5-0.8", "M2-0.4-Standard" for heat-set)
            length: Screw length in mm (screws only, ignored for nuts/washers)
            fastener_type: Standard identifier. Common defaults:
                Screws: "iso4762" (socket), "iso4014" (hex), "iso7380" (button)
                Nuts: "iso4032" (hex), "iso4161" (flanged)
                Washers: "iso7089" (plain), "iso7090" (chamfered)
                Inserts: "McMaster-Carr", "Hilitchi"
            simple: If true, omit thread detail for faster generation (default true)
            hand: "right" or "left" hand thread
        """
        try:
            name = sanitize_name(name)

            fastener_map = {
                "socket_head_cap_screw": ("SocketHeadCapScrew", "iso4762", True),
                "hex_head_screw": ("HexHeadScrew", "iso4014", True),
                "button_head_screw": ("ButtonHeadScrew", "iso7380", True),
                "counter_sunk_screw": ("CounterSunkScrew", "iso10642", True),
                "pan_head_screw": ("PanHeadScrew", "asme_b18.6.3", True),
                "set_screw": ("SetScrew", "iso4026", True),
                "low_profile_screw": ("LowProfileScrew", "iso14580", True),
                "hex_nut": ("HexNut", "iso4032", False),
                "hex_nut_with_flange": ("HexNutWithFlange", "iso4161", False),
                "square_nut": ("SquareNut", "din557", False),
                "domed_cap_nut": ("DomedCapNut", "din1587", False),
                "plain_washer": ("PlainWasher", "iso7089", None),
                "chamfered_washer": ("ChamferedWasher", "iso7090", None),
                "heat_set_nut": ("HeatSetNut", "McMaster-Carr", False),
            }

            fc = fastener_class.lower().replace(" ", "_")
            if fc not in fastener_map:
                return json.dumps({
                    "success": False,
                    "error": (
                        f"Unknown fastener_class: {fastener_class}. "
                        f"Options: {list(fastener_map.keys())}"
                    ),
                })

            cls_name, default_type, needs_length = fastener_map[fc]
            mod = importlib.import_module("bd_warehouse.fastener")
            cls = getattr(mod, cls_name)
            ft = fastener_type or default_type

            if needs_length is True:
                result = cls(
                    size=size, length=length,
                    fastener_type=ft, hand=hand, simple=simple,
                )
            elif needs_length is False:
                result = cls(
                    size=size, fastener_type=ft, hand=hand, simple=simple,
                )
            else:
                result = cls(size=size, fastener_type=ft)

            entry, stl_path, step_path = _export_and_store(
                name, result, f"{fc} {size}",
            )

            return json.dumps({
                "success": True, "name": name, "fastener_class": fc,
                "size": size, "fastener_type": ft,
                "bbox": entry["bbox"], "volume": entry["volume"],
                "outputs": {"stl": stl_path, "step": step_path},
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False, "error": str(e),
                "traceback": traceback.format_exc(),
            }, indent=2)

    @mcp.tool()
    def create_bearing(
        name: str,
        bearing_class: str = "deep_groove_ball",
        size: str = "M8-22-7",
        bearing_type: str = "SKT",
    ) -> str:
        """Create a parametric bearing model.

        Args:
            name: Name for the model
            bearing_class: Bearing type — "deep_groove_ball", "capped_deep_groove_ball",
                "angular_contact_ball", "cylindrical_roller", "tapered_roller"
            size: Bearing size string (e.g. "M8-22-7" = 8mm bore, 22mm OD, 7mm width)
            bearing_type: Manufacturer spec (default "SKT")
        """
        try:
            name = sanitize_name(name)

            bearing_map = {
                "deep_groove_ball": "SingleRowDeepGrooveBallBearing",
                "capped_deep_groove_ball": "SingleRowCappedDeepGrooveBallBearing",
                "angular_contact_ball": "SingleRowAngularContactBallBearing",
                "cylindrical_roller": "SingleRowCylindricalRollerBearing",
                "tapered_roller": "SingleRowTaperedRollerBearing",
            }

            bc = bearing_class.lower().replace(" ", "_")
            if bc not in bearing_map:
                return json.dumps({
                    "success": False,
                    "error": (
                        f"Unknown bearing_class: {bearing_class}. "
                        f"Options: {list(bearing_map.keys())}"
                    ),
                })

            mod = importlib.import_module("bd_warehouse.bearing")
            cls = getattr(mod, bearing_map[bc])
            result = cls(size=size, bearing_type=bearing_type)

            entry, stl_path, step_path = _export_and_store(
                name, result, f"{bc} bearing {size}",
            )

            return json.dumps({
                "success": True, "name": name,
                "bearing_class": bc, "size": size,
                "bbox": entry["bbox"], "volume": entry["volume"],
                "outputs": {"stl": stl_path, "step": step_path},
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False, "error": str(e),
                "traceback": traceback.format_exc(),
            }, indent=2)

    @mcp.tool()
    def create_sprocket(
        name: str,
        num_teeth: int = 18,
        chain_pitch: float = 12.7,
        roller_diameter: float = 7.9375,
        thickness: float = 2.1336,
        bore_diameter: float = 0.0,
        num_mount_bolts: int = 0,
        mount_bolt_diameter: float = 0.0,
        bolt_circle_diameter: float = 0.0,
        clearance: float = 0.0,
    ) -> str:
        """Create a parametric chain sprocket.

        Default values are for ANSI #40 (1/2" pitch, 0.3125" roller) chain.

        Args:
            name: Name for the model
            num_teeth: Number of teeth (default 18)
            chain_pitch: Chain pitch in mm (default 12.7 = 1/2 inch ANSI #40)
            roller_diameter: Chain roller diameter in mm (default 7.9375 = 5/16 inch)
            thickness: Sprocket plate thickness in mm (default 2.1336)
            bore_diameter: Center bore diameter in mm, 0 for solid (default 0)
            num_mount_bolts: Number of mounting bolt holes (default 0)
            mount_bolt_diameter: Mounting bolt hole diameter in mm (default 0)
            bolt_circle_diameter: Bolt circle diameter in mm (default 0)
            clearance: Additional clearance between chain and sprocket in mm (default 0)
        """
        try:
            name = sanitize_name(name)
            from bd_warehouse.sprocket import Sprocket

            result = Sprocket(
                num_teeth=num_teeth, chain_pitch=chain_pitch,
                roller_diameter=roller_diameter, thickness=thickness,
                bore_diameter=bore_diameter,
                num_mount_bolts=num_mount_bolts,
                mount_bolt_diameter=mount_bolt_diameter,
                bolt_circle_diameter=bolt_circle_diameter,
                clearance=clearance,
            )

            entry, stl_path, step_path = _export_and_store(
                name, result, f"sprocket {num_teeth}T pitch={chain_pitch}",
            )
            pitch_diameter = chain_pitch / math.sin(math.pi / num_teeth)

            return json.dumps({
                "success": True, "name": name, "num_teeth": num_teeth,
                "chain_pitch_mm": chain_pitch,
                "pitch_diameter_mm": round(pitch_diameter, 2),
                "bore_diameter_mm": bore_diameter,
                "bbox": entry["bbox"], "volume": entry["volume"],
                "outputs": {"stl": stl_path, "step": step_path},
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False, "error": str(e),
                "traceback": traceback.format_exc(),
            }, indent=2)

    @mcp.tool()
    def create_flange(
        name: str,
        flange_class: str = "blind",
        nps: str = "2",
        flange_class_rating: int = 150,
        face_type: str = "Raised",
    ) -> str:
        """Create a parametric pipe flange (ASME B16.5).

        Args:
            name: Name for the model
            flange_class: "blind", "slip_on", "weld_neck", "lapped", "socket_weld"
            nps: Nominal pipe size — "1/2", "3/4", "1", "1 1/4", "1 1/2", "2",
                "2 1/2", "3", "4", "5", "6", "8", "10", "12", "14", "16",
                "18", "20", "22", "24"
            flange_class_rating: Pressure class — 150, 300, 400, 600, 900, 1500, or 2500
            face_type: "Flat", "Raised", "Ring", "Tongue", "Groove", "Male", "Female"
        """
        try:
            name = sanitize_name(name)

            flange_map = {
                "blind": "BlindFlange",
                "slip_on": "SlipOnFlange",
                "weld_neck": "WeldNeckFlange",
                "lapped": "LappedFlange",
                "socket_weld": "SocketWeldFlange",
            }

            fc = flange_class.lower().replace(" ", "_")
            if fc not in flange_map:
                return json.dumps({
                    "success": False,
                    "error": (
                        f"Unknown flange_class: {flange_class}. "
                        f"Options: {list(flange_map.keys())}"
                    ),
                })

            mod = importlib.import_module("bd_warehouse.flange")
            cls = getattr(mod, flange_map[fc])
            result = cls(
                nps=nps, flange_class=flange_class_rating,
                face_type=face_type,
            )

            code = f"{fc} flange NPS {nps} class {flange_class_rating}"
            entry, stl_path, step_path = _export_and_store(
                name, result, code,
            )

            return json.dumps({
                "success": True, "name": name, "flange_class": fc,
                "nps": nps, "class_rating": flange_class_rating,
                "face_type": face_type,
                "bbox": entry["bbox"], "volume": entry["volume"],
                "outputs": {"stl": stl_path, "step": step_path},
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False, "error": str(e),
                "traceback": traceback.format_exc(),
            }, indent=2)

    @mcp.tool()
    def create_pipe(
        name: str,
        outer_diameter: float = 25.0,
        wall_thickness: float = 2.0,
        length: float = 100.0,
    ) -> str:
        """Create a pipe/tube section.

        Args:
            name: Name for the model
            outer_diameter: Outer diameter in mm (default 25)
            wall_thickness: Wall thickness in mm (default 2)
            length: Pipe length in mm (default 100)
        """
        try:
            name = sanitize_name(name)
            from build123d import Cylinder

            inner_d = outer_diameter - 2 * wall_thickness
            if inner_d <= 0:
                return json.dumps({
                    "success": False,
                    "error": (
                        f"Wall thickness {wall_thickness}mm "
                        f"is too large for OD {outer_diameter}mm"
                    ),
                })

            result = Cylinder(outer_diameter / 2, length) - Cylinder(inner_d / 2, length)

            code = f"pipe OD={outer_diameter} wall={wall_thickness} L={length}"
            entry, stl_path, step_path = _export_and_store(
                name, result, code,
            )

            return json.dumps({
                "success": True, "name": name,
                "outer_diameter_mm": outer_diameter,
                "inner_diameter_mm": round(inner_d, 2),
                "wall_thickness_mm": wall_thickness,
                "length_mm": length,
                "bbox": entry["bbox"], "volume": entry["volume"],
                "outputs": {"stl": stl_path, "step": step_path},
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False, "error": str(e),
                "traceback": traceback.format_exc(),
            }, indent=2)

    @mcp.tool()
    def create_openbuilds_part(
        name: str,
        part_type: str = "v_slot_rail",
        length: float = 200.0,
        rail_size: str = "20x20",
    ) -> str:
        """Create OpenBuilds CNC/linear motion parts for 3D printing jigs and fixtures.

        Args:
            name: Name for the model
            part_type: Part to create:
                "v_slot_rail" — V-Slot aluminum extrusion profile
                "c_beam_rail" — C-Beam linear rail profile
                "lead_screw" — Metric 8mm lead screw with trapezoidal thread
            length: Part length in mm (default 200)
            rail_size: V-Slot size — "20x20", "20x40", "20x60", "20x80", "40x40"
                (v_slot_rail only)
        """
        try:
            name = sanitize_name(name)
            pt = part_type.lower().replace(" ", "_")

            if pt == "v_slot_rail":
                from bd_warehouse.open_builds import VSlotLinearRail

                result = VSlotLinearRail(rail_size=rail_size, length=length)
            elif pt in ("c_beam_rail", "c_beam"):
                from bd_warehouse.open_builds import CBeamLinearRail

                result = CBeamLinearRail(length=length)
            elif pt in ("lead_screw", "metric_lead_screw"):
                from bd_warehouse.open_builds import MetricLeadScrew

                result = MetricLeadScrew(length=length)
            else:
                return json.dumps({
                    "success": False,
                    "error": (
                        f"Unknown part_type: {part_type}. "
                        "Options: v_slot_rail, c_beam_rail, lead_screw"
                    ),
                })

            entry, stl_path, step_path = _export_and_store(
                name, result, f"openbuilds {pt} L={length}",
            )

            return json.dumps({
                "success": True, "name": name,
                "part_type": pt, "length_mm": length,
                "bbox": entry["bbox"], "volume": entry["volume"],
                "outputs": {"stl": stl_path, "step": step_path},
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "success": False, "error": str(e),
                "traceback": traceback.format_exc(),
            }, indent=2)
