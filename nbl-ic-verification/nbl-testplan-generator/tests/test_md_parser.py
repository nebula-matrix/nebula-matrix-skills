"""Tests for md_parser module."""
from pathlib import Path

import pytest

from parsers.md_parser import parse_spec_tree, get_feature_by_id


class TestParseSpecTree:
    """Tests for parse_spec_tree function."""

    def test_returns_dict(self, sample_spec_md):
        """parse_spec_tree should return a dictionary."""
        result = parse_spec_tree(sample_spec_md)
        assert isinstance(result, dict)

    def test_has_module_name(self, sample_spec_md):
        """Result should contain inferred module_name."""
        result = parse_spec_tree(sample_spec_md)
        assert "module_name" in result
        assert result["module_name"] == "upa"

    def test_has_spec_title(self, sample_spec_md):
        """Result should have spec_title from first H1."""
        result = parse_spec_tree(sample_spec_md)
        assert "spec_title" in result
        assert "UPA" in result["spec_title"]

    def test_has_chapters(self, sample_spec_md):
        """Result should have chapters list."""
        result = parse_spec_tree(sample_spec_md)
        assert "chapters" in result
        assert len(result["chapters"]) > 0

    def test_chapters_have_ids(self, sample_spec_md):
        """Each chapter should have chapter_id and chapter_title."""
        result = parse_spec_tree(sample_spec_md)
        for ch in result["chapters"]:
            assert "chapter_id" in ch
            assert "chapter_title" in ch

    def test_module_features_chapter_exists(self, sample_spec_md):
        """Should find '模块特性' chapter."""
        result = parse_spec_tree(sample_spec_md)
        titles = [ch["chapter_title"] for ch in result["chapters"]]
        assert any("模块特性" in t for t in titles)

    def test_extracts_features(self, sample_spec_md):
        """Should extract three features: PA.001, PA.002, PA.003."""
        result = parse_spec_tree(sample_spec_md)
        features_ch = next(
            (ch for ch in result["chapters"] if "模块特性" in ch["chapter_title"]),
            None,
        )
        assert features_ch is not None
        assert "features" in features_ch
        feature_ids = [f["feature_id"] for f in features_ch["features"]]
        assert "PA.001" in feature_ids
        assert "PA.002" in feature_ids
        assert "PA.003" in feature_ids

    def test_feature_has_refs(self, sample_spec_md):
        """Each feature should have refs dict."""
        result = parse_spec_tree(sample_spec_md)
        features_ch = next(
            (ch for ch in result["chapters"] if "模块特性" in ch["chapter_title"]),
            None,
        )
        if features_ch and features_ch["features"]:
            feat = features_ch["features"][0]
            assert "refs" in feat
            assert isinstance(feat["refs"], dict)
            assert "detail_chapters" in feat["refs"]


class TestGetFeatureById:
    """Tests for get_feature_by_id."""

    def test_finds_existing(self, sample_spec_md):
        """Should find PA.001."""
        result = parse_spec_tree(sample_spec_md)
        feat = get_feature_by_id(result, "PA.001")
        assert feat is not None
        assert feat["feature_id"] == "PA.001"

    def test_returns_none_for_missing(self, sample_spec_md):
        """Should return None for nonexistent ID."""
        result = parse_spec_tree(sample_spec_md)
        assert get_feature_by_id(result, "PA.999") is None
