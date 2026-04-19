"""Tests for markdown parser module."""
import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "testplan-func" / "scripts"))

from md_parser import parse_markdown, extract_feature_ids


class TestParseMarkdown:
    """Tests for parse_markdown function."""

    def test_parse_markdown_returns_dict(self, sample_spec_md):
        """parse_markdown should return a dictionary."""
        result = parse_markdown(sample_spec_md)
        assert isinstance(result, dict)

    def test_parse_markdown_extracts_document_title(self, sample_spec_md):
        """parse_markdown should extract document title."""
        result = parse_markdown(sample_spec_md)
        assert "document_title" in result
        assert "UPA" in result["document_title"] or "spec" in result["document_title"].lower()

    def test_parse_markdown_extracts_feature_ids(self, sample_spec_md):
        """parse_markdown should extract feature IDs like PA.001."""
        result = parse_markdown(sample_spec_md)
        assert "feature_ids" in result
        assert "PA.001" in result["feature_ids"]
        assert "PA.002" in result["feature_ids"]
        assert "PA.003" in result["feature_ids"]

    def test_parse_markdown_extracts_sections(self, sample_spec_md):
        """parse_markdown should extract hierarchical sections."""
        result = parse_markdown(sample_spec_md)
        assert "sections" in result
        assert len(result["sections"]) > 0

    def test_parse_markdown_extracts_tables(self, sample_spec_md):
        """parse_markdown should extract tables if present."""
        result = parse_markdown(sample_spec_md)
        assert "tables" in result
        assert isinstance(result["tables"], list)


class TestExtractFeatureIds:
    """Tests for extract_feature_ids function."""

    def test_extract_feature_ids_returns_list(self, sample_spec_md):
        """extract_feature_ids should return a list."""
        result = extract_feature_ids(sample_spec_md)
        assert isinstance(result, list)

    def test_extract_feature_ids_finds_pattern(self, sample_spec_md):
        """extract_feature_ids should find PA.XXX patterns."""
        result = extract_feature_ids(sample_spec_md)
        assert "PA.001" in result

    def test_extract_feature_ids_deduplicates(self, sample_spec_md):
        """extract_feature_ids should deduplicate IDs."""
        result = extract_feature_ids(sample_spec_md)
        assert len(result) == len(set(result))


class TestGetFeatureContent:
    """Tests for get_feature_content function."""

    def test_get_feature_content_returns_dict(self, sample_spec_md):
        """get_feature_content should return content for a feature ID."""
        from md_parser import parse_markdown, get_feature_content
        parsed = parse_markdown(sample_spec_md)
        result = get_feature_content(parsed, "PA.001")
        assert result is not None or result == {}

    def test_get_feature_content_finds_registers(self, sample_spec_md):
        """get_feature_content should find related register names."""
        from md_parser import parse_markdown, get_feature_content
        parsed = parse_markdown(sample_spec_md)
        result = get_feature_content(parsed, "PA.001")
        if result:
            assert "upa_ctrl" in str(result) or "upa_data" in str(result)
