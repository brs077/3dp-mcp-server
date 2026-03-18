#!/usr/bin/env python3
"""Functional tests and security pen tests for 3dp-mcp-server."""

import json
import os
import sys
import tempfile
import traceback

# Add project to path so we can import server functions directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import server module — this registers all tools
import server

# ── Test helpers ─────────────────────────────────────────────────────────────

PASS = 0
FAIL = 0
WARN = 0
results = []


def _log(status, category, test_name, detail=""):
    global PASS, FAIL, WARN
    icon = {"PASS": "\033[32mPASS\033[0m", "FAIL": "\033[31mFAIL\033[0m", "WARN": "\033[33mWARN\033[0m"}[status]
    if status == "PASS":
        PASS += 1
    elif status == "FAIL":
        FAIL += 1
    else:
        WARN += 1
    msg = f"  [{icon}] {category}: {test_name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    results.append({"status": status, "category": category, "test": test_name, "detail": detail})


def parse(raw: str) -> dict:
    return json.loads(raw)


# ── Functional Tests ─────────────────────────────────────────────────────────

def test_functional():
    print("\n=== FUNCTIONAL TESTS ===\n")

    # ── create_model ──
    r = parse(server.create_model("test_box", 'from build123d import *\nresult = Box(50, 40, 30)'))
    if r["success"] and abs(r["bbox"]["size"][0] - 50) < 0.1:
        _log("PASS", "create_model", "basic box creation")
    else:
        _log("FAIL", "create_model", "basic box creation", str(r))

    # Missing result variable
    r = parse(server.create_model("bad_code", 'x = 1 + 1'))
    if not r["success"] and "result" in r.get("error", ""):
        _log("PASS", "create_model", "missing result variable")
    else:
        _log("FAIL", "create_model", "missing result variable", str(r))

    # Syntax error
    r = parse(server.create_model("syntax_err", 'def foo('))
    if not r["success"]:
        _log("PASS", "create_model", "syntax error handling")
    else:
        _log("FAIL", "create_model", "syntax error handling")

    # Auto-imports build123d
    r = parse(server.create_model("auto_import", 'result = Box(10, 10, 10)'))
    if r["success"]:
        _log("PASS", "create_model", "auto-import build123d")
    else:
        _log("FAIL", "create_model", "auto-import build123d", r.get("error", ""))

    # ── list_models ──
    r = parse(server.list_models())
    names = [m["name"] for m in r["models"]]
    if "test_box" in names:
        _log("PASS", "list_models", "lists created models")
    else:
        _log("FAIL", "list_models", "lists created models", str(names))

    # ── get_model_code ──
    r = parse(server.get_model_code("test_box"))
    if "Box(50" in r.get("code", ""):
        _log("PASS", "get_model_code", "returns code")
    else:
        _log("FAIL", "get_model_code", "returns code")

    r = parse(server.get_model_code("nonexistent_xyz"))
    if not r.get("success", True) or "error" in r:
        _log("PASS", "get_model_code", "nonexistent model error")
    else:
        _log("FAIL", "get_model_code", "nonexistent model error")

    # ── measure_model ──
    r = parse(server.measure_model("test_box"))
    if r.get("volume_mm3") and r["volume_mm3"] > 0:
        _log("PASS", "measure_model", "returns volume")
    else:
        _log("FAIL", "measure_model", "returns volume", str(r))

    r = parse(server.measure_model("no_such_model"))
    if not r.get("success", True):
        _log("PASS", "measure_model", "nonexistent model error")
    else:
        _log("FAIL", "measure_model", "nonexistent model error")

    # ── export_model ──
    for fmt in ["stl", "step"]:
        r = parse(server.export_model("test_box", fmt))
        if r["success"] and os.path.exists(r["path"]):
            _log("PASS", "export_model", f"export {fmt}")
        else:
            _log("FAIL", "export_model", f"export {fmt}", str(r))

    r = parse(server.export_model("test_box", "invalid_fmt"))
    if not r["success"]:
        _log("PASS", "export_model", "invalid format error")
    else:
        _log("FAIL", "export_model", "invalid format error")

    r = parse(server.export_model("nonexistent", "stl"))
    if not r["success"]:
        _log("PASS", "export_model", "nonexistent model error")
    else:
        _log("FAIL", "export_model", "nonexistent model error")

    # ── analyze_printability ──
    r = parse(server.analyze_printability("test_box"))
    if r.get("verdict") in ("PRINTABLE", "REVIEW NEEDED"):
        _log("PASS", "analyze_printability", "returns verdict")
    else:
        _log("FAIL", "analyze_printability", "returns verdict", str(r))

    # Tiny model
    parse(server.create_model("tiny", 'from build123d import *\nresult = Box(0.5, 0.5, 0.5)'))
    r = parse(server.analyze_printability("tiny"))
    if r.get("verdict") == "REVIEW NEEDED":
        _log("PASS", "analyze_printability", "flags tiny model")
    else:
        _log("WARN", "analyze_printability", "flags tiny model", r.get("verdict", ""))

    # ── transform_model ──
    r = parse(server.transform_model("scaled_box", "test_box", json.dumps({"scale": 2.0})))
    if r["success"] and abs(r["bbox"]["size"][0] - 100) < 0.1:
        _log("PASS", "transform_model", "uniform scale")
    else:
        _log("FAIL", "transform_model", "uniform scale", str(r))

    r = parse(server.transform_model("rotated", "test_box", json.dumps({"rotate": [0, 0, 90]})))
    if r["success"]:
        _log("PASS", "transform_model", "rotate")
    else:
        _log("FAIL", "transform_model", "rotate", str(r))

    r = parse(server.transform_model("moved", "test_box", json.dumps({"translate": [100, 0, 0]})))
    if r["success"]:
        _log("PASS", "transform_model", "translate")
    else:
        _log("FAIL", "transform_model", "translate", str(r))

    r = parse(server.transform_model("mirrored", "test_box", json.dumps({"mirror": "YZ"})))
    if r["success"]:
        _log("PASS", "transform_model", "mirror")
    else:
        _log("FAIL", "transform_model", "mirror", str(r))

    # Chained operations
    r = parse(server.transform_model("chained", "test_box",
        json.dumps([{"scale": 0.5}, {"translate": [10, 0, 0]}])))
    if r["success"]:
        _log("PASS", "transform_model", "chained operations")
    else:
        _log("FAIL", "transform_model", "chained operations", str(r))

    r = parse(server.transform_model("bad_xform", "nonexistent", json.dumps({"scale": 1})))
    if not r["success"]:
        _log("PASS", "transform_model", "nonexistent source error")
    else:
        _log("FAIL", "transform_model", "nonexistent source error")

    # ── combine_models ──
    parse(server.create_model("cyl", 'from build123d import *\nresult = Cylinder(10, 30)'))

    r = parse(server.combine_models("union_result", "test_box", "cyl", "union"))
    if r["success"]:
        _log("PASS", "combine_models", "union")
    else:
        _log("FAIL", "combine_models", "union", str(r))

    r = parse(server.combine_models("sub_result", "test_box", "cyl", "subtract"))
    if r["success"]:
        _log("PASS", "combine_models", "subtract")
    else:
        _log("FAIL", "combine_models", "subtract", str(r))

    r = parse(server.combine_models("int_result", "test_box", "cyl", "intersect"))
    if r["success"]:
        _log("PASS", "combine_models", "intersect")
    else:
        _log("FAIL", "combine_models", "intersect", str(r))

    r = parse(server.combine_models("bad_op", "test_box", "cyl", "xor"))
    if not r["success"]:
        _log("PASS", "combine_models", "invalid operation error")
    else:
        _log("FAIL", "combine_models", "invalid operation error")

    # ── shell_model ──
    r = parse(server.shell_model("shelled", "test_box", 2.0, '["top"]'))
    if r["success"]:
        _log("PASS", "shell_model", "shell with open top")
    else:
        _log("FAIL", "shell_model", "shell with open top", str(r))

    # ── split_model ──
    r = parse(server.split_model("split_test", "test_box", "XY", "both"))
    if r["success"] and "split_test_above" in r.get("results", {}):
        _log("PASS", "split_model", "split XY both")
    else:
        _log("FAIL", "split_model", "split XY both", str(r))

    r = parse(server.split_model("split_z", "test_box", '{"axis": "Z", "offset": 10}', "above"))
    if r["success"]:
        _log("PASS", "split_model", "split with offset JSON")
    else:
        _log("FAIL", "split_model", "split with offset JSON", str(r))

    # ── estimate_print ──
    r = parse(server.estimate_print("test_box", 15.0, 0.2, "PLA"))
    if r["success"] and r.get("weight_g", 0) > 0:
        _log("PASS", "estimate_print", "PLA estimate")
    else:
        _log("FAIL", "estimate_print", "PLA estimate", str(r))

    r = parse(server.estimate_print("test_box", 15.0, 0.2, "UNOBTAINIUM"))
    if not r["success"]:
        _log("PASS", "estimate_print", "unknown material error")
    else:
        _log("FAIL", "estimate_print", "unknown material error")

    # ── analyze_overhangs ──
    r = parse(server.analyze_overhangs("test_box"))
    if r.get("success"):
        _log("PASS", "analyze_overhangs", "basic analysis")
    else:
        _log("FAIL", "analyze_overhangs", "basic analysis", str(r))

    # ── suggest_orientation ──
    r = parse(server.suggest_orientation("test_box"))
    if r.get("success") and r.get("best"):
        _log("PASS", "suggest_orientation", "returns candidates")
    else:
        _log("FAIL", "suggest_orientation", "returns candidates", str(r))

    # ── shrinkage_compensation ──
    r = parse(server.shrinkage_compensation("compensated", "test_box", "ABS"))
    if r["success"] and r["scale_factor"] > 1.0:
        _log("PASS", "shrinkage_compensation", "ABS compensation")
    else:
        _log("FAIL", "shrinkage_compensation", "ABS compensation", str(r))

    # ── section_view ──
    r = parse(server.section_view("section", "test_box", "XY", 15.0))
    if r.get("success") and r.get("svg_path"):
        _log("PASS", "section_view", "XY section")
    else:
        _log("FAIL", "section_view", "XY section", str(r))

    # ── export_drawing ──
    r = parse(server.export_drawing("test_box", '["front", "top"]'))
    if r.get("success") and r.get("svg_path"):
        _log("PASS", "export_drawing", "multi-view drawing")
    else:
        _log("FAIL", "export_drawing", "multi-view drawing", str(r))

    # ── add_text ──
    r = parse(server.add_text("labeled", "test_box", "HELLO", "top", 8.0, 1.0, "Arial", True))
    if r.get("success"):
        _log("PASS", "add_text", "emboss text on top")
    else:
        _log("FAIL", "add_text", "emboss text on top", str(r))

    # ── create_threaded_hole ──
    r = parse(server.create_threaded_hole("drilled", "test_box", "[0, 0, 15]", "M3", 10.0, False))
    if r.get("success") and r.get("diameter_mm"):
        _log("PASS", "create_threaded_hole", "M3 tap drill")
    else:
        _log("FAIL", "create_threaded_hole", "M3 tap drill", str(r))

    r = parse(server.create_threaded_hole("inserted", "test_box", "[10, 0, 15]", "M4", 8.0, True))
    if r.get("success") and r.get("hole_type") == "heat-set insert":
        _log("PASS", "create_threaded_hole", "M4 heat-set insert")
    else:
        _log("FAIL", "create_threaded_hole", "M4 heat-set insert", str(r))

    r = parse(server.create_threaded_hole("bad_spec", "test_box", "[0,0,0]", "M99"))
    if not r["success"]:
        _log("PASS", "create_threaded_hole", "invalid thread spec error")
    else:
        _log("FAIL", "create_threaded_hole", "invalid thread spec error")

    # ── create_enclosure ──
    r = parse(server.create_enclosure("enc", 60, 40, 25, 2.0, "snap", '["vent_slots", "screw_posts"]'))
    if r.get("success") and "enc_body" in str(r):
        _log("PASS", "create_enclosure", "snap enclosure with features")
    else:
        _log("FAIL", "create_enclosure", "snap enclosure with features", str(r))

    r = parse(server.create_enclosure("enc_screw", 60, 40, 25, 2.0, "screw", '["cable_hole"]'))
    if r.get("success"):
        _log("PASS", "create_enclosure", "screw enclosure with cable hole")
    else:
        _log("FAIL", "create_enclosure", "screw enclosure with cable hole", str(r))

    # ── create_snap_fit ──
    r = parse(server.create_snap_fit("snap", "cantilever", '{"beam_length": 15}'))
    if r.get("success"):
        _log("PASS", "create_snap_fit", "cantilever snap-fit")
    else:
        _log("FAIL", "create_snap_fit", "cantilever snap-fit", str(r))

    r = parse(server.create_snap_fit("bad_snap", "unknown_type"))
    if not r["success"]:
        _log("PASS", "create_snap_fit", "unknown type error")
    else:
        _log("FAIL", "create_snap_fit", "unknown type error")

    # ── create_gear ──
    r = parse(server.create_gear("gear", 1.5, 16, 20.0, 5.0, 3.0))
    if r.get("success"):
        _log("PASS", "create_gear", "spur gear with bore")
    else:
        _log("FAIL", "create_gear", "spur gear with bore", str(r))

    # ── create_hinge ──
    r = parse(server.create_hinge("hinge", "pin", '{"width": 25, "barrel_count": 2}'))
    if r.get("success") and "hinge_leaf_a" in str(r):
        _log("PASS", "create_hinge", "pin hinge")
    else:
        _log("FAIL", "create_hinge", "pin hinge", str(r))

    # ── create_dovetail ──
    r = parse(server.create_dovetail("dt_male", "male", 20.0, 10.0, 15.0, 10.0, 0.2))
    if r.get("success"):
        _log("PASS", "create_dovetail", "male dovetail")
    else:
        _log("FAIL", "create_dovetail", "male dovetail", str(r))

    r = parse(server.create_dovetail("dt_female", "female", 20.0, 10.0, 15.0, 10.0, 0.2))
    if r.get("success"):
        _log("PASS", "create_dovetail", "female dovetail")
    else:
        _log("FAIL", "create_dovetail", "female dovetail", str(r))

    # ── generate_label ──
    r = parse(server.generate_label("label", "Test Label", "[60, 20, 2]", 8.0, ""))
    if r.get("success") and r.get("stl_path"):
        _log("PASS", "generate_label", "text label")
    else:
        _log("FAIL", "generate_label", "text label", str(r))

    # ── split_model_by_color ──
    r = parse(server.split_model_by_color("color_split", "test_box",
        json.dumps([{"faces": "top", "color": "#FF0000", "filament": 1},
                     {"faces": "rest", "color": "#FFFFFF", "filament": 0}])))
    if r.get("success") and len(r.get("outputs", [])) == 2:
        _log("PASS", "split_model_by_color", "two-color split")
    else:
        _log("FAIL", "split_model_by_color", "two-color split", str(r))

    # ── import_model (using our exported STL) ──
    stl_path = os.path.join(server.OUTPUT_DIR, "test_box", "test_box.stl")
    if os.path.exists(stl_path):
        r = parse(server.import_model("imported", stl_path))
        if r.get("success"):
            _log("PASS", "import_model", "import STL")
        else:
            _log("FAIL", "import_model", "import STL", str(r))
    else:
        _log("WARN", "import_model", "import STL", "STL not found to test")

    step_path = os.path.join(server.OUTPUT_DIR, "test_box", "test_box.step")
    if os.path.exists(step_path):
        r = parse(server.import_model("imported_step", step_path))
        if r.get("success"):
            _log("PASS", "import_model", "import STEP")
        else:
            _log("FAIL", "import_model", "import STEP", str(r))

    r = parse(server.import_model("bad_ext", "/tmp/foo.obj"))
    if not r["success"]:
        _log("PASS", "import_model", "unsupported extension error")
    else:
        _log("FAIL", "import_model", "unsupported extension error")

    # ── convert_format ──
    if os.path.exists(stl_path):
        out_step = os.path.join(server.OUTPUT_DIR, "converted_test.step")
        r = parse(server.convert_format(stl_path, out_step))
        if r.get("success"):
            _log("PASS", "convert_format", "STL → STEP")
            os.unlink(out_step)
        else:
            _log("FAIL", "convert_format", "STL → STEP", str(r))

    # ── pack_models ──
    parse(server.create_model("pack_a", 'from build123d import *\nresult = Box(20, 20, 10)'))
    parse(server.create_model("pack_b", 'from build123d import *\nresult = Cylinder(10, 10)'))
    r = parse(server.pack_models("packed", '["pack_a", "pack_b"]', 5.0))
    if r.get("success") and r.get("packed_count") == 2:
        _log("PASS", "pack_models", "pack two models")
    else:
        _log("FAIL", "pack_models", "pack two models", str(r))

    # ── search_models (requires API key, expect graceful failure) ──
    r = parse(server.search_models("test query"))
    if not r["success"] and "API_KEY" in r.get("error", "").upper():
        _log("PASS", "search_models", "missing API key error")
    elif r["success"]:
        _log("PASS", "search_models", "search works (API key present)")
    else:
        _log("WARN", "search_models", "unexpected error", r.get("error", ""))

    # ── Publishing tools (all should fail gracefully without tokens) ──
    r = parse(server.publish_thingiverse("test_box", "Test", "desc"))
    if not r["success"] and "TOKEN" in r.get("error", "").upper():
        _log("PASS", "publish_thingiverse", "missing token error")
    else:
        _log("WARN", "publish_thingiverse", "unexpected response", str(r)[:100])

    r = parse(server.publish_myminifactory("test_box", "Test"))
    if not r["success"] and "TOKEN" in r.get("error", "").upper():
        _log("PASS", "publish_myminifactory", "missing token error")
    else:
        _log("WARN", "publish_myminifactory", "unexpected response", str(r)[:100])

    r = parse(server.publish_cults3d("test_box", "Test"))
    if not r["success"] and "API_KEY" in r.get("error", "").upper():
        _log("PASS", "publish_cults3d", "missing API key error")
    else:
        _log("WARN", "publish_cults3d", "unexpected response", str(r)[:100])

    r = parse(server.publish_github_release("test_box", "owner/repo", "v0.0.0-test"))
    if not r["success"]:
        _log("PASS", "publish_github_release", "fails without auth")
    else:
        _log("WARN", "publish_github_release", "unexpected success (gh CLI present?)")


# ── Security / Pen Tests ─────────────────────────────────────────────────────

def test_security():
    print("\n=== SECURITY / PEN TESTS ===\n")

    # ── SEC-1: exec() arbitrary code execution ──
    # The create_model tool uses exec() — this is by design for a CAD tool,
    # but we should document the risk and test what's possible.

    # Test: Can exec'd code read files?
    r = parse(server.create_model("sec_readfile",
        'from build123d import *\nimport pathlib\n'
        'data = pathlib.Path("/etc/hostname").read_text()\n'
        'result = Box(10, 10, 10)'))
    if r["success"]:
        _log("WARN", "SEC-exec", "code can read arbitrary files via pathlib",
             "exec() has full __builtins__ — expected for CAD code execution")
    else:
        _log("PASS", "SEC-exec", "file read blocked")

    # Test: Can exec'd code access os module?
    r = parse(server.create_model("sec_os",
        'from build123d import *\nimport os\n'
        'os.listdir("/")\nresult = Box(10, 10, 10)'))
    if r["success"]:
        _log("WARN", "SEC-exec", "code can use os module",
             "exec() has full __builtins__ — inherent to design")
    else:
        _log("PASS", "SEC-exec", "os module blocked")

    # Test: Can exec'd code access subprocess?
    r = parse(server.create_model("sec_subprocess",
        'from build123d import *\nimport subprocess\n'
        'subprocess.run(["echo", "pwned"])\nresult = Box(10, 10, 10)'))
    if r["success"]:
        _log("WARN", "SEC-exec", "code can run subprocess",
             "exec() has full __builtins__ — inherent to design")
    else:
        _log("PASS", "SEC-exec", "subprocess blocked")

    # Test: Can exec'd code access environment variables (leak tokens)?
    r = parse(server.create_model("sec_env",
        'from build123d import *\nimport os\n'
        'tokens = {k:v for k,v in os.environ.items() if "TOKEN" in k or "KEY" in k or "SECRET" in k}\n'
        'result = Box(10, 10, 10)'))
    if r["success"]:
        _log("WARN", "SEC-exec", "code can read env vars (potential token leak)",
             "exec() has full __builtins__ — tokens in env are accessible")
    else:
        _log("PASS", "SEC-exec", "env var access blocked")

    # Test: Can exec'd code write files outside OUTPUT_DIR?
    tmp_marker = os.path.join(tempfile.gettempdir(), "3dp_pentest_marker.txt")
    r = parse(server.create_model("sec_write",
        f'from build123d import *\n'
        f'with open("{tmp_marker}", "w") as f: f.write("pentest")\n'
        f'result = Box(10, 10, 10)'))
    if os.path.exists(tmp_marker):
        os.unlink(tmp_marker)
        _log("WARN", "SEC-exec", "code can write arbitrary files",
             "exec() has full __builtins__ — expected for CAD but risky")
    else:
        _log("PASS", "SEC-exec", "file write outside OUTPUT_DIR blocked")

    # Test: Can exec'd code make network requests?
    r = parse(server.create_model("sec_network",
        'from build123d import *\nimport urllib.request\n'
        'result = Box(10, 10, 10)'))  # just import, don't actually call
    if r["success"]:
        _log("WARN", "SEC-exec", "code can import urllib (potential for exfiltration)",
             "exec() has full __builtins__")
    else:
        _log("PASS", "SEC-exec", "urllib import blocked")

    # ── SEC-2: Path traversal in import_model ──
    r = parse(server.import_model("sec_traverse", "/etc/passwd"))
    if not r["success"]:
        _log("PASS", "SEC-path", "import_model rejects non-model file /etc/passwd")
    else:
        _log("FAIL", "SEC-path", "import_model accepted /etc/passwd!")

    r = parse(server.import_model("sec_traverse2", "../../etc/passwd"))
    if not r["success"]:
        _log("PASS", "SEC-path", "import_model rejects relative traversal")
    else:
        _log("FAIL", "SEC-path", "import_model accepted relative traversal!")

    # Test: Path traversal with valid extension but traversal path
    r = parse(server.import_model("sec_traverse3", "/etc/../etc/passwd.stl"))
    if not r["success"]:
        _log("PASS", "SEC-path", "import_model fails on non-existent traversal .stl")
    else:
        _log("FAIL", "SEC-path", "import_model accepted traversal .stl path")

    # ── SEC-3: Path traversal in convert_format ──
    r = parse(server.convert_format("/etc/passwd", "/tmp/out.stl"))
    if not r["success"]:
        _log("PASS", "SEC-path", "convert_format rejects non-model input")
    else:
        _log("FAIL", "SEC-path", "convert_format accepted /etc/passwd!")

    # Output path traversal — can we write to arbitrary location?
    stl_path = os.path.join(server.OUTPUT_DIR, "test_box", "test_box.stl")
    if os.path.exists(stl_path):
        evil_out = "/tmp/3dp_evil_output.step"
        r = parse(server.convert_format(stl_path, evil_out))
        if r.get("success") and os.path.exists(evil_out):
            os.unlink(evil_out)
            _log("WARN", "SEC-path", "convert_format writes to arbitrary output path",
                 "No output path restriction — can write anywhere writable")
        elif not r.get("success"):
            _log("PASS", "SEC-path", "convert_format blocked arbitrary output")

    # ── SEC-4: Model name injection ──
    # Model names are used in os.path.join() for directory creation
    evil_names = [
        ("../evil", "parent directory traversal"),
        ("../../etc/evil", "deep traversal"),
        ("foo/bar/baz", "nested path injection"),
        ("name; rm -rf /", "shell metacharacter injection"),
        ("name\x00evil", "null byte injection"),
    ]
    for evil_name, desc in evil_names:
        try:
            r = parse(server.create_model(evil_name, 'from build123d import *\nresult = Box(5,5,5)'))
            if r["success"]:
                # Check where files actually went using the returned path
                stl_path = r.get("outputs", {}).get("stl", "")
                if stl_path:
                    real_dir = os.path.realpath(os.path.dirname(stl_path))
                else:
                    real_dir = os.path.realpath(os.path.join(server.OUTPUT_DIR, r.get("name", evil_name)))
                output_real = os.path.realpath(server.OUTPUT_DIR)
                if real_dir.startswith(output_real):
                    _log("PASS", "SEC-name", f"model name '{evil_name}' — sanitized, stayed in OUTPUT_DIR",
                         f"stored as '{r.get('name')}'")
                else:
                    _log("FAIL", "SEC-name", f"model name '{evil_name}' — escaped OUTPUT_DIR!",
                         f"wrote to {real_dir}")
            else:
                _log("PASS", "SEC-name", f"model name '{evil_name}' — rejected", desc)
        except Exception as e:
            _log("PASS", "SEC-name", f"model name '{evil_name}' — raised exception", str(e)[:80])

    # ── SEC-5: JSON injection in string parameters ──
    # Test malformed JSON in operations parameter
    r = parse(server.transform_model("json_inj", "test_box", "not valid json"))
    if not r["success"]:
        _log("PASS", "SEC-json", "transform_model rejects invalid JSON operations")
    else:
        _log("FAIL", "SEC-json", "transform_model accepted invalid JSON!")

    # Test malformed JSON in other params
    r = parse(server.shell_model("json_inj2", "test_box", 2.0, "not json"))
    if not r["success"]:
        _log("PASS", "SEC-json", "shell_model rejects invalid JSON open_faces")
    else:
        _log("FAIL", "SEC-json", "shell_model accepted invalid JSON!")

    r = parse(server.pack_models("json_inj3", "not json"))
    if not r["success"]:
        _log("PASS", "SEC-json", "pack_models rejects invalid JSON model_names")
    else:
        _log("FAIL", "SEC-json", "pack_models accepted invalid JSON!")

    r = parse(server.create_threaded_hole("json_inj4", "test_box", "not json", "M3"))
    if not r["success"]:
        _log("PASS", "SEC-json", "create_threaded_hole rejects invalid JSON position")
    else:
        _log("FAIL", "SEC-json", "create_threaded_hole accepted invalid JSON!")

    # ── SEC-6: Integer overflow / extreme values ──
    r = parse(server.create_model("huge_box",
        'from build123d import *\nresult = Box(1e10, 1e10, 1e10)'))
    if r["success"]:
        _log("WARN", "SEC-input", "no dimension limit — created 10 billion mm box",
             "Consider max dimension validation")
    else:
        _log("PASS", "SEC-input", "extreme dimensions rejected")

    r = parse(server.estimate_print("test_box", -10.0, 0.2, "PLA"))
    if r.get("success"):
        _log("WARN", "SEC-input", "negative infill accepted",
             f"weight_g={r.get('weight_g')} — should validate range")
    else:
        _log("PASS", "SEC-input", "negative infill rejected")

    r = parse(server.estimate_print("test_box", 15.0, 0.0, "PLA"))
    if r.get("success"):
        # Check for division by zero
        _log("WARN", "SEC-input", "zero layer height accepted",
             "Could cause division by zero in time estimate")
    else:
        _log("PASS", "SEC-input", "zero layer height rejected")

    # ── SEC-7: Traceback information disclosure ──
    r = parse(server.create_model("tb_leak", 'raise Exception("test error")'))
    if "traceback" in r and len(r["traceback"]) > 0:
        # Check if traceback reveals server internals
        tb = r["traceback"]
        if "server.py" in tb or "/Users/" in tb or "home" in tb:
            _log("WARN", "SEC-info", "tracebacks expose server file paths",
                 "Consider sanitizing tracebacks in production")
        else:
            _log("PASS", "SEC-info", "tracebacks don't expose server paths")
    else:
        _log("PASS", "SEC-info", "no traceback in error response")

    # ── SEC-8: SSRF via search_models ──
    # The search_models tool constructs a URL with user input
    # Test if query can manipulate the URL
    r = parse(server.search_models("test%00&url=evil"))
    # Should fail due to no API key, but check URL encoding
    if not r["success"] and "API_KEY" in r.get("error", "").upper():
        _log("PASS", "SEC-ssrf", "search_models blocked (no API key)")
    else:
        _log("WARN", "SEC-ssrf", "search_models may be exploitable", str(r)[:100])

    # ── SEC-9: _ensure_exported path safety ──
    # The _ensure_exported function uses model name in path construction
    try:
        server._models["../../../tmp/evil"] = server._models.get("test_box", {})
        path = server._ensure_exported("../../../tmp/evil", "stl")
        real = os.path.realpath(path)
        output_real = os.path.realpath(server.OUTPUT_DIR)
        if real.startswith(output_real):
            _log("PASS", "SEC-path", "_ensure_exported stays in OUTPUT_DIR")
        else:
            _log("FAIL", "SEC-path", "_ensure_exported escaped OUTPUT_DIR!", f"path={real}")
        # Cleanup
        del server._models["../../../tmp/evil"]
    except Exception as e:
        _log("PASS", "SEC-path", "_ensure_exported raised exception on traversal", str(e)[:80])

    # ── SEC-10: publish_github_release command injection ──
    # The repo parameter is passed to subprocess via gh CLI
    # Test if shell metacharacters in repo could be injected
    r = parse(server.publish_github_release(
        "test_box", "owner/repo; echo pwned", "v1.0", "test"))
    if not r["success"]:
        # Check if it was blocked or just failed normally
        err = r.get("error", "")
        if "pwned" in err:
            _log("FAIL", "SEC-cmdinj", "shell injection via repo parameter!")
        else:
            _log("PASS", "SEC-cmdinj", "repo parameter didn't execute shell commands",
                 "subprocess.run uses list args (safe)")
    else:
        _log("WARN", "SEC-cmdinj", "unexpected success", str(r)[:100])

    # tag parameter
    r = parse(server.publish_github_release(
        "test_box", "owner/repo", "v1; rm -rf /", "test"))
    if not r["success"]:
        _log("PASS", "SEC-cmdinj", "tag injection handled safely")


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("3DP MCP Server — Test Suite")
    print("=" * 60)

    try:
        test_functional()
    except Exception as e:
        print(f"\n  FATAL in functional tests: {e}")
        traceback.print_exc()

    try:
        test_security()
    except Exception as e:
        print(f"\n  FATAL in security tests: {e}")
        traceback.print_exc()

    # Summary
    print("\n" + "=" * 60)
    print(f"RESULTS: {PASS} passed, {FAIL} failed, {WARN} warnings")
    print("=" * 60)

    # Security summary
    sec_warns = [r for r in results if r["status"] == "WARN" and r["category"].startswith("SEC")]
    if sec_warns:
        print("\nSECURITY FINDINGS:")
        for w in sec_warns:
            print(f"  [{w['category']}] {w['test']}")
            if w['detail']:
                print(f"    → {w['detail']}")

    sec_fails = [r for r in results if r["status"] == "FAIL" and r["category"].startswith("SEC")]
    if sec_fails:
        print("\nCRITICAL SECURITY ISSUES:")
        for f in sec_fails:
            print(f"  [{f['category']}] {f['test']}")
            if f['detail']:
                print(f"    → {f['detail']}")

    print()
    sys.exit(1 if FAIL > 0 else 0)
