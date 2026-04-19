"""Tests for register parser module."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "testplan-func" / "scripts"))

from reg_to_json import parse_register_xlsx, get_register_by_name


class TestParseRegisterXlsx:
    """Tests for parse_register_xlsx function."""

    def test_parse_returns_dict(self, sample_reg_xlsx):
        """parse_register_xlsx should return a dictionary."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert isinstance(result, dict)

    def test_parse_extracts_source_file(self, sample_reg_xlsx):
        """parse_register_xlsx should include source file name."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert "source_file" in result
        assert "sample_reg" in result["source_file"]

    def test_parse_extracts_registers_list(self, sample_reg_xlsx):
        """parse_register_xlsx should extract registers list."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert "registers" in result
        assert isinstance(result["registers"], list)
        assert len(result["registers"]) > 0

    def test_parse_extracts_register_name(self, sample_reg_xlsx):
        """parse_register_xlsx should extract register names."""
        result = parse_register_xlsx(sample_reg_xlsx)
        reg_names = [r["name"] for r in result["registers"]]
        assert "upa_ctrl" in reg_names

    def test_parse_extracts_register_fields(self, sample_reg_xlsx):
        """parse_register_xlsx should extract register fields."""
        result = parse_register_xlsx(sample_reg_xlsx)
        upa_ctrl = get_register_by_name(result, "upa_ctrl")
        assert upa_ctrl is not None
        assert "fields" in upa_ctrl
        assert len(upa_ctrl["fields"]) > 0

    def test_parse_extracts_field_name(self, sample_reg_xlsx):
        """parse_register_xlsx should extract field names."""
        result = parse_register_xlsx(sample_reg_xlsx)
        upa_ctrl = get_register_by_name(result, "upa_ctrl")
        field_names = [f["name"] for f in upa_ctrl["fields"]]
        assert "en" in field_names

    def test_parse_extracts_field_access(self, sample_reg_xlsx):
        """parse_register_xlsx should extract field access type."""
        result = parse_register_xlsx(sample_reg_xlsx)
        upa_ctrl = get_register_by_name(result, "upa_ctrl")
        en_field = next((f for f in upa_ctrl["fields"] if f["name"] == "en"), None)
        assert en_field is not None
        assert en_field.get("access") == "RW"

    def test_parse_builds_name_index(self, sample_reg_xlsx):
        """parse_register_xlsx should build name_index for quick lookup."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert "name_index" in result
        assert "upa_ctrl" in result["name_index"]


class TestGetRegisterByName:
    """Tests for get_register_by_name function."""

    def test_get_existing_register(self, sample_reg_xlsx):
        """get_register_by_name should find existing register."""
        result = parse_register_xlsx(sample_reg_xlsx)
        reg = get_register_by_name(result, "upa_ctrl")
        assert reg is not None
        assert reg["name"] == "upa_ctrl"

    def test_get_nonexistent_register(self, sample_reg_xlsx):
        """get_register_by_name should return None for missing register."""
        result = parse_register_xlsx(sample_reg_xlsx)
        reg = get_register_by_name(result, "nonexistent_reg")
        assert reg is None
