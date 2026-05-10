"""Tests for reg_parser module."""
from pathlib import Path

import pytest

from parsers.reg_parser import parse_register_xlsx, get_register_by_name


class TestParseRegisterXlsx:
    """Tests for parse_register_xlsx function."""

    def test_returns_dict(self, sample_reg_xlsx):
        """parse_register_xlsx should return a dictionary."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert isinstance(result, dict)

    def test_extracts_module_name(self, sample_reg_xlsx):
        """Should infer module name from filename."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert "module_name" in result
        assert result["module_name"] == "upa"

    def test_extracts_registers_list(self, sample_reg_xlsx):
        """Should extract registers list."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert "registers" in result
        assert isinstance(result["registers"], list)
        assert len(result["registers"]) > 0

    def test_register_has_name(self, sample_reg_xlsx):
        """First register should have reg_name."""
        result = parse_register_xlsx(sample_reg_xlsx)
        reg = result["registers"][0]
        assert "reg_name" in reg
        assert reg["reg_name"]

    def test_register_has_fields(self, sample_reg_xlsx):
        """Register should have fields list."""
        result = parse_register_xlsx(sample_reg_xlsx)
        reg = result["registers"][0]
        assert "fields" in reg
        assert isinstance(reg["fields"], list)

    def test_fields_have_required_keys(self, sample_reg_xlsx):
        """Each field should have field_name, bit_range, rw, reset, desc."""
        result = parse_register_xlsx(sample_reg_xlsx)
        for reg in result["registers"]:
            for field in reg["fields"]:
                assert "field_name" in field
                assert "bit_range" in field
                assert "rw" in field
                assert "reset" in field
                assert "desc" in field


class TestGetRegisterByName:
    """Tests for get_register_by_name."""

    def test_finds_existing(self, sample_reg_xlsx):
        """Should find first register by name."""
        result = parse_register_xlsx(sample_reg_xlsx)
        reg_name = result["registers"][0]["reg_name"]
        found = get_register_by_name(result, reg_name)
        assert found is not None
        assert found["reg_name"] == reg_name

    def test_returns_none_for_missing(self, sample_reg_xlsx):
        """Should return None for missing register."""
        result = parse_register_xlsx(sample_reg_xlsx)
        assert get_register_by_name(result, "NONEXISTENT") is None
