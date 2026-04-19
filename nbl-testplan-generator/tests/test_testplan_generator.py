"""Tests for nbl-testplan-generator orchestration scripts."""
import sys
from pathlib import Path

import pytest
from openpyxl import load_workbook

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "nbl-testplan-generator" / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "nbl-testplan-generator" / "scripts" / "writers"))
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "nbl-testplan-generator" / "scripts" / "parsers"))

from combine_writer import (
    build_ch2_data,
    combine_and_write,
    cross_ref_ch2,
    filter_ch2_registers,
    group_similar_registers,
    orchestrate_testplan,
    validate_jw_correspondence,
)
from xlsx_writer import write_testpoint_xlsx


class TestCombineWriter:
    """Tests for combine_writer module."""

    def test_combine_writer_exists(self):
        """combine_writer module should be importable."""
        import writers.combine_writer as cm
        assert cm is not None

    def test_filter_ch2_registers_exists(self):
        """filter_ch2_registers function should exist."""
        assert callable(filter_ch2_registers)

    def test_group_similar_registers_exists(self):
        """group_similar_registers function should exist."""
        assert callable(group_similar_registers)

    def test_cross_ref_ch2_exists(self):
        """cross_ref_ch2 function should exist."""
        assert callable(cross_ref_ch2)

    def test_build_ch2_data_exists(self):
        """build_ch2_data function should exist."""
        assert callable(build_ch2_data)

    def test_validate_jw_correspondence_exists(self):
        """validate_jw_correspondence function should exist."""
        assert callable(validate_jw_correspondence)

    def test_combine_and_write_exists(self):
        """combine_and_write function should exist."""
        assert callable(combine_and_write)

    def test_orchestrate_testplan_exists(self):
        """orchestrate_testplan function should exist."""
        assert callable(orchestrate_testplan)


class TestFilterCh2Registers:
    """Tests for filter_ch2_registers function."""

    def test_filter_excludes_int_registers(self):
        """Should exclude *_int_* registers."""
        registers = [
            {"name": "upa_ctrl", "fields": [{"name": "en", "access": "RW"}]},
            {"name": "upa_int_status", "fields": []},
            {"name": "upa_int_mask", "fields": []},
        ]
        result = filter_ch2_registers(registers)
        names = [r["name"] for r in result]
        assert "upa_ctrl" in names
        assert "upa_int_status" not in names
        assert "upa_int_mask" not in names

    def test_filter_excludes_fifo_registers(self):
        """Should exclude *_fifo_* registers."""
        registers = [
            {"name": "upa_ctrl", "fields": [{"name": "en", "access": "RW"}]},
            {"name": "upa_fifo_th", "fields": []},
        ]
        result = filter_ch2_registers(registers)
        names = [r["name"] for r in result]
        assert "upa_ctrl" in names
        assert "upa_fifo_th" not in names


class TestGroupSimilarRegisters:
    """Tests for group_similar_registers function."""

    def test_group_merges_numbered_registers(self):
        """Should merge registers with trailing numbers."""
        registers = [
            {"name": "upa_ch_0", "offset": "0x00", "fields": [{"name": "cfg", "access": "RW"}]},
            {"name": "upa_ch_1", "offset": "0x04", "fields": [{"name": "cfg", "access": "RW"}]},
        ]
        result = group_similar_registers(registers)
        assert len(result) == 1
        assert "upa_ch_0" in result[0]["name"] or "upa_ch" in result[0]["name"]

    def test_group_keeps_single_registers(self):
        """Should keep single registers unchanged."""
        registers = [
            {"name": "upa_ctrl", "offset": "0x00", "fields": [{"name": "en", "access": "RW"}]},
        ]
        result = group_similar_registers(registers)
        assert len(result) == 1
        assert result[0]["name"] == "upa_ctrl"


class TestCrossRefCh2:
    """Tests for cross_ref_ch2 function."""

    def test_cross_ref_marks_covered(self):
        """Should mark covered registers with skip=True."""
        registers = [
            {"name": "upa_ctrl", "fields": [{"name": "en", "access": "RW", "range": "0", "description": "Enable"}]},
        ]
        ch1_data = {
            "features": [
                {
                    "feature_id": "PA.001",
                    "subfeatures_l1": [
                        {
                            "subfeatures_l2": [
                                {
                                    "stimulus": "【配置】配置 upa_ctrl.en",
                                    "checking": "by_checker",
                                    "coverage": "",
                                    "path": "",
                                }
                            ]
                        }
                    ],
                }
            ]
        }
        result = cross_ref_ch2(registers, ch1_data)
        assert len(result) == 1
        assert result[0].get("skip") is True

    def test_cross_ref_generates_stimulus_for_uncovered(self):
        """Should generate stimulus for uncovered registers."""
        registers = [
            {
                "name": "upa_mode",
                "fields": [{"name": "sel", "access": "RW", "range": "1:0", "description": "Mode select"}],
            },
        ]
        ch1_data = {"features": []}
        result = cross_ref_ch2(registers, ch1_data)
        assert len(result) == 1
        assert result[0].get("skip") is False
        assert "【配置】" in result[0].get("stimulus", "")


class TestBuildCh2Data:
    """Tests for build_ch2_data function."""

    def test_build_ch2_data_returns_dict(self):
        """build_ch2_data should return a dictionary."""
        registers = [
            {"name": "upa_ctrl", "fields": [{"name": "en", "access": "RW", "range": "0", "description": "Enable"}]},
        ]
        ch1_data = {"features": []}
        result = build_ch2_data(registers, ch1_data)
        assert isinstance(result, dict)

    def test_build_ch2_data_has_chapter(self):
        """build_ch2_data should include chapter field."""
        registers = [
            {"name": "upa_ctrl", "fields": [{"name": "en", "access": "RW"}]},
        ]
        ch1_data = {"features": []}
        result = build_ch2_data(registers, ch1_data)
        assert "chapter" in result
        assert "chapter 2" in result["chapter"].lower()

    def test_build_ch2_data_has_registers(self):
        """build_ch2_data should include registers list."""
        registers = [
            {"name": "upa_ctrl", "fields": [{"name": "en", "access": "RW"}]},
        ]
        ch1_data = {"features": []}
        result = build_ch2_data(registers, ch1_data)
        assert "registers" in result
        assert isinstance(result["registers"], list)


class TestValidateJwCorrespondence:
    """Tests for validate_jw_correspondence function."""

    def test_validate_jw_correspondence_returns_dict(self):
        """validate_jw_correspondence should return a dictionary."""
        data = {
            "module_name": "upa",
            "features": [
                {
                    "feature": "Test",
                    "subfeatures_l1": [
                        {
                            "subfeatures_l2": [
                                {
                                    "checking": "by_checker",
                                    "path": "",
                                }
                            ]
                        }
                    ],
                }
            ],
        }
        result = validate_jw_correspondence(data)
        assert isinstance(result, dict)

    def test_validate_jw_auto_generates_path_for_direct_tc(self):
        """Should auto-generate path for by_direct_tc checking."""
        data = {
            "module_name": "upa",
            "features": [
                {
                    "feature": "Test Feature",
                    "subfeatures_l1": [
                        {
                            "subfeatures_l2": [
                                {
                                    "checking": "by_direct_tc",
                                    "path": "",
                                }
                            ]
                        }
                    ],
                }
            ],
        }
        result = validate_jw_correspondence(data)
        path = result["features"][0]["subfeatures_l1"][0]["subfeatures_l2"][0]["path"]
        assert "direct_fcov" in path or path != ""

    def test_validate_jw_auto_generates_path_for_assertion(self):
        """Should auto-generate path for by_assertion checking."""
        data = {
            "module_name": "upa",
            "features": [
                {
                    "feature": "Test Feature",
                    "subfeatures_l1": [
                        {
                            "subfeatures_l2": [
                                {
                                    "checking": "by_assertion",
                                    "path": "",
                                }
                            ]
                        }
                    ],
                }
            ],
        }
        result = validate_jw_correspondence(data)
        path = result["features"][0]["subfeatures_l1"][0]["subfeatures_l2"][0]["path"]
        assert "assert" in path or path != ""


class TestWriteTestpointXlsx:
    """Tests for write_testpoint_xlsx function."""

    def test_write_testpoint_xlsx_creates_file(self, temp_dir, sample_template_xlsx):
        """write_testpoint_xlsx should create an output xlsx file."""
        chapters = [
            {
                "type": "ch1",
                "data": {
                    "module_name": "UPA",
                    "spec_name": "Test Spec",
                    "chapter": "chapter 1 功能特性",
                    "features": [
                        {
                            "feature": "Test Feature",
                            "feature_id": "PA.001",
                            "subfeatures_l1": [],
                        }
                    ],
                },
            },
            {
                "type": "ch2",
                "data": {
                    "chapter": "chapter 2 配置特性",
                    "registers": [],
                },
            },
        ]
        output_path = temp_dir / "testplan.xlsx"
        stats = write_testpoint_xlsx(chapters, str(output_path), str(sample_template_xlsx))
        assert output_path.exists()
        assert isinstance(stats, dict)

    def test_write_testpoint_xlsx_returns_stats(self, temp_dir, sample_template_xlsx):
        """write_testpoint_xlsx should return statistics."""
        chapters = [
            {"type": "ch1", "data": {"features": []}},
            {"type": "ch2", "data": {"registers": []}},
        ]
        output_path = temp_dir / "testplan.xlsx"
        stats = write_testpoint_xlsx(chapters, str(output_path), str(sample_template_xlsx))
        assert "total_features" in stats
        assert "total_l1" in stats
        assert "total_l2" in stats


class TestOrchestrateTestplan:
    """Tests for orchestrate_testplan function."""

    def test_orchestrate_testplan_creates_output(self, temp_dir, sample_spec_md, sample_reg_xlsx, sample_template_xlsx):
        """orchestrate_testplan should create output xlsx."""
        output_path = temp_dir / "testplan.xlsx"
        workdir = temp_dir / ".tp_cache"

        result = orchestrate_testplan(
            str(sample_spec_md),
            str(sample_reg_xlsx),
            str(output_path),
            str(sample_template_xlsx),
            str(workdir),
        )

        assert output_path.exists()
        assert "stats" in result
        assert "output_path" in result

    def test_orchestrate_testplan_returns_workdir(self, temp_dir, sample_spec_md, sample_reg_xlsx, sample_template_xlsx):
        """orchestrate_testplan should return workdir path."""
        output_path = temp_dir / "testplan.xlsx"
        workdir = temp_dir / ".tp_cache"

        result = orchestrate_testplan(
            str(sample_spec_md),
            str(sample_reg_xlsx),
            str(output_path),
            str(sample_template_xlsx),
            str(workdir),
        )

        assert "workdir" in result
        assert Path(result["workdir"]).exists()
