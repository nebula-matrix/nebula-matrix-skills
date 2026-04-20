"""Tests for cfg_writer module - J column (checking) and W column (path) generation."""
import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "testplan-cfg" / "scripts"))

from cfg_writer import build_ch2_json
from reg_to_json import parse_register_xlsx


class TestJColumnAndWColumn:
    """Tests for J column (checking) and W column (path) generation."""

    def test_j_column_defaults_to_random_testcase(self, sample_reg_xlsx):
        """J column should default to '随机用例'."""
        reg_data = parse_register_xlsx(sample_reg_xlsx)
        result = build_ch2_json(reg_data)

        # Check at least one register has checking set
        for reg in result.get("registers", []):
            for sf1 in reg.get("subfeatures_l1", []):
                for sf2 in sf1.get("subfeatures_l2", []):
                    checking = sf2.get("checking", "")
                    if checking:  # Non-skipped registers
                        assert checking == "随机用例", f"Checking should be '随机用例', got '{checking}'"
                        return

    def test_w_column_path_format(self, sample_reg_xlsx):
        """W column path should follow format Group:$unit::{module}_fcov::{reg}_cg.{field}_cp."""
        reg_data = parse_register_xlsx(sample_reg_xlsx)
        result = build_ch2_json(reg_data)

        # Check path format for non-skipped registers
        for reg in result.get("registers", []):
            reg_name = reg.get("register_name", "")
            for sf1 in reg.get("subfeatures_l1", []):
                field_name = sf1.get("subfeature_l1", "")
                for sf2 in sf1.get("subfeatures_l2", []):
                    path = sf2.get("path", "")
                    if path and path != "【反标路径暂无法确定】":
                        # Check format: Group:$unit::{module}_fcov::{reg}_cg.{field}_cp
                        assert path.startswith("Group:$unit::"), f"Path should start with 'Group:$unit::', got '{path}'"
                        assert "_fcov::" in path, f"Path should contain '_fcov::', got '{path}'"
                        assert "_cg." in path, f"Path should contain '_cg.', got '{path}'"
                        assert "_cp" in path, f"Path should end with '_cp', got '{path}'"
                        return

    def test_module_name_extracted_from_register_name(self, sample_reg_xlsx):
        """Module name should be extracted from first underscore prefix of register name."""
        reg_data = parse_register_xlsx(sample_reg_xlsx)
        result = build_ch2_json(reg_data)

        # Check module name in path matches register prefix
        for reg in result.get("registers", []):
            reg_name = reg.get("register_name", "")
            if "_" in reg_name:
                expected_module = reg_name.split("_")[0]
                for sf1 in reg.get("subfeatures_l1", []):
                    for sf2 in sf1.get("subfeatures_l2", []):
                        path = sf2.get("path", "")
                        if path and path != "【反标路径暂无法确定】" and expected_module:
                            assert f"{expected_module}_fcov" in path, f"Path should contain module '{expected_module}_fcov', got '{path}'"
                            return
