"""Tests for threedp_mcp.constants."""

from threedp_mcp.constants import ISO_THREAD_TABLE, MATERIAL_PROPERTIES


class TestMaterialProperties:
    def test_all_materials_have_required_keys(self):
        for name, props in MATERIAL_PROPERTIES.items():
            assert "density" in props, f"{name} missing density"
            assert "shrinkage" in props, f"{name} missing shrinkage"

    def test_density_values_are_positive(self):
        for name, props in MATERIAL_PROPERTIES.items():
            assert props["density"] > 0, f"{name} has non-positive density"

    def test_shrinkage_values_are_positive(self):
        for name, props in MATERIAL_PROPERTIES.items():
            assert props["shrinkage"] > 0, f"{name} has non-positive shrinkage"

    def test_pla_is_present(self):
        assert "PLA" in MATERIAL_PROPERTIES


class TestIsoThreadTable:
    def test_all_threads_have_required_keys(self):
        for size, dims in ISO_THREAD_TABLE.items():
            assert "tap_drill" in dims, f"{size} missing tap_drill"
            assert "insert_drill" in dims, f"{size} missing insert_drill"
            assert "clearance_drill" in dims, f"{size} missing clearance_drill"

    def test_clearance_larger_than_tap(self):
        for size, dims in ISO_THREAD_TABLE.items():
            assert dims["clearance_drill"] > dims["tap_drill"], (
                f"{size}: clearance_drill should be larger than tap_drill"
            )

    def test_insert_larger_than_tap(self):
        for size, dims in ISO_THREAD_TABLE.items():
            assert dims["insert_drill"] > dims["tap_drill"], (
                f"{size}: insert_drill should be larger than tap_drill"
            )

    def test_m3_is_present(self):
        assert "M3" in ISO_THREAD_TABLE
