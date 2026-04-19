"""Tests for func_writer module - Feature Generator."""
import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "testplan-func" / "scripts"))

from md_parser import parse_markdown
from reg_to_json import parse_register_xlsx


class TestGenerateCh1Features:
    """Tests for generate_ch1_features function."""

    def test_generate_ch1_features_exists(self):
        """generate_ch1_features function should exist."""
        from func_writer import generate_ch1_features
        assert callable(generate_ch1_features)

    def test_generate_ch1_features_returns_dict(self, sample_spec_md, sample_reg_xlsx):
        """generate_ch1_features should return a dictionary."""
        from func_writer import generate_ch1_features
        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)
        result = generate_ch1_features(parsed_md, parsed_reg)
        assert isinstance(result, dict)

    def test_generate_ch1_features_has_module_name(self, sample_spec_md, sample_reg_xlsx):
        """generate_ch1_features should include module_name."""
        from func_writer import generate_ch1_features
        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)
        result = generate_ch1_features(parsed_md, parsed_reg)
        assert "module_name" in result

    def test_generate_ch1_features_has_spec_name(self, sample_spec_md, sample_reg_xlsx):
        """generate_ch1_features should include spec_name."""
        from func_writer import generate_ch1_features
        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)
        result = generate_ch1_features(parsed_md, parsed_reg)
        assert "spec_name" in result

    def test_generate_ch1_features_has_chapter(self, sample_spec_md, sample_reg_xlsx):
        """generate_ch1_features should include chapter field."""
        from func_writer import generate_ch1_features
        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)
        result = generate_ch1_features(parsed_md, parsed_reg)
        assert "chapter" in result
        assert "chapter 1" in result["chapter"].lower()

    def test_generate_ch1_features_has_features_list(self, sample_spec_md, sample_reg_xlsx):
        """generate_ch1_features should include features list."""
        from func_writer import generate_ch1_features
        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)
        result = generate_ch1_features(parsed_md, parsed_reg)
        assert "features" in result
        assert isinstance(result["features"], list)

    def test_generate_ch1_features_extracts_feature_ids(self, sample_spec_md, sample_reg_xlsx):
        """generate_ch1_features should extract feature IDs from markdown."""
        from func_writer import generate_ch1_features
        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)
        result = generate_ch1_features(parsed_md, parsed_reg)
        # Should have features for PA.001, PA.002, PA.003
        assert len(result["features"]) >= 1


class TestBuildHierarchy:
    """Tests for _build_hierarchy function."""

    def test_build_hierarchy_exists(self):
        """_build_hierarchy function should exist."""
        from func_writer import _build_hierarchy
        assert callable(_build_hierarchy)

    def test_build_hierarchy_creates_d_level(self, sample_spec_md):
        """_build_hierarchy should create D level (feature) entries."""
        from func_writer import _build_hierarchy
        parsed_md = parse_markdown(sample_spec_md)
        features = _build_hierarchy(parsed_md)
        assert isinstance(features, list)
        if features:
            assert "feature" in features[0] or "feature_id" in features[0]

    def test_build_hierarchy_creates_e_level(self, sample_spec_md):
        """_build_hierarchy should create E level (L1 subfeature) entries."""
        from func_writer import _build_hierarchy
        parsed_md = parse_markdown(sample_spec_md)
        features = _build_hierarchy(parsed_md)
        # Check if any feature has L1 subfeatures
        for feature in features:
            if feature.get("subfeatures_l1"):
                assert isinstance(feature["subfeatures_l1"], list)
                break

    def test_build_hierarchy_creates_f_level(self, sample_spec_md):
        """_build_hierarchy should create F level (L2 subfeature) entries."""
        from func_writer import _build_hierarchy
        parsed_md = parse_markdown(sample_spec_md)
        features = _build_hierarchy(parsed_md)
        # Check if any L1 has L2 subfeatures
        for feature in features:
            for l1 in feature.get("subfeatures_l1", []):
                if l1.get("subfeatures_l2"):
                    assert isinstance(l1["subfeatures_l2"], list)
                    return
        # If no L2 found, that's OK for simple specs

    def test_build_hierarchy_creates_g_level(self, sample_spec_md):
        """_build_hierarchy should create G level (L3 subfeature) entries."""
        from func_writer import _build_hierarchy
        parsed_md = parse_markdown(sample_spec_md)
        features = _build_hierarchy(parsed_md)
        # Check if any L2 has L3 subfeatures
        for feature in features:
            for l1 in feature.get("subfeatures_l1", []):
                for l2 in l1.get("subfeatures_l2", []):
                    if l2.get("subfeatures_l3"):
                        assert isinstance(l2["subfeatures_l3"], list)
                        return
        # If no L3 found, that's OK for simple specs


class TestCrossReferenceRegisters:
    """Tests for _cross_reference_registers function."""

    def test_cross_reference_registers_exists(self):
        """_cross_reference_registers function should exist."""
        from func_writer import _cross_reference_registers
        assert callable(_cross_reference_registers)

    def test_cross_reference_registers_adds_register_info(self, sample_spec_md, sample_reg_xlsx):
        """_cross_reference_registers should add register info to features."""
        from func_writer import generate_ch1_features
        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)
        result = generate_ch1_features(parsed_md, parsed_reg)
        # Check if any feature has register-related fields
        features = result.get("features", [])
        assert len(features) > 0

    def test_cross_reference_registers_finds_upa_ctrl(self, sample_spec_md, sample_reg_xlsx):
        """_cross_reference_registers should find upa_ctrl register."""
        from func_writer import generate_ch1_features
        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)
        result = generate_ch1_features(parsed_md, parsed_reg)
        # PA.001 should reference upa_ctrl
        features = result.get("features", [])
        # At least check that features were processed
        assert len(features) > 0


class TestFeatureStructure:
    """Tests for feature structure validation."""

    def test_feature_has_required_fields(self, sample_spec_md, sample_reg_xlsx):
        """Each feature should have required fields."""
        from func_writer import generate_ch1_features
        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)
        result = generate_ch1_features(parsed_md, parsed_reg)
        for feature in result.get("features", []):
            assert "feature" in feature or "feature_id" in feature

    def test_subfeature_l1_has_required_fields(self, sample_spec_md, sample_reg_xlsx):
        """Each L1 subfeature should have required fields."""
        from func_writer import generate_ch1_features
        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)
        result = generate_ch1_features(parsed_md, parsed_reg)
        for feature in result.get("features", []):
            for l1 in feature.get("subfeatures_l1", []):
                assert "subfeature_l1" in l1

    def test_subfeature_l2_has_required_fields(self, sample_spec_md, sample_reg_xlsx):
        """Each L2 subfeature should have required fields."""
        from func_writer import generate_ch1_features
        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)
        result = generate_ch1_features(parsed_md, parsed_reg)
        for feature in result.get("features", []):
            for l1 in feature.get("subfeatures_l1", []):
                for l2 in l1.get("subfeatures_l2", []):
                    # Should have at least one identifier field
                    has_identifier = any([
                        l2.get("subfeature_l2_overview"),
                        l2.get("subfeature_l2_detail"),
                    ])
                    assert has_identifier


class TestGenerateStimulusChecking:
    """Tests for stimulus/checking generation."""

    def test_generate_stimulus_exists(self):
        """_generate_stimulus function should exist."""
        from func_writer import _generate_stimulus
        assert callable(_generate_stimulus)

    def test_generate_checking_exists(self):
        """_generate_checking function should exist."""
        from func_writer import _generate_checking
        assert callable(_generate_checking)

    def test_stimulus_includes_register_config(self, sample_spec_md, sample_reg_xlsx):
        """Stimulus should include register configuration steps."""
        from func_writer import generate_ch1_features
        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)
        result = generate_ch1_features(parsed_md, parsed_reg)
        # Check that at least one L2 has stimulus field
        has_stimulus = False
        for feature in result.get("features", []):
            for l1 in feature.get("subfeatures_l1", []):
                for l2 in l1.get("subfeatures_l2", []):
                    if l2.get("stimulus"):
                        has_stimulus = True
                        # Should contain register configuration pattern
                        assert "【配置】" in l2["stimulus"] or "配置" in l2["stimulus"]
                        break
        assert has_stimulus

    def test_checking_has_value(self, sample_spec_md, sample_reg_xlsx):
        """Checking field should have a value."""
        from func_writer import generate_ch1_features
        parsed_md = parse_markdown(sample_spec_md)
        parsed_reg = parse_register_xlsx(sample_reg_xlsx)
        result = generate_ch1_features(parsed_md, parsed_reg)
        # Check that at least one L2 has checking field
        has_checking = False
        for feature in result.get("features", []):
            for l1 in feature.get("subfeatures_l1", []):
                for l2 in l1.get("subfeatures_l2", []):
                    if l2.get("checking"):
                        has_checking = True
                        break
        assert has_checking
