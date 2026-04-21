"""Tests for review_writer module."""
from pathlib import Path

import pytest

from review.review_writer import write_review_md, write_review_from_testplan


class TestWriteReviewMd:
    def test_creates_file(self, temp_dir):
        output = temp_dir / "review.md"
        result = write_review_md([], output, "UPA")
        assert output.exists()
        assert result == output.resolve()

    def test_outputs_module_title(self, temp_dir):
        output = temp_dir / "review.md"
        write_review_md([], output, "UPA")
        content = output.read_text(encoding="utf-8")
        assert "UPA FS/REG 审查记录" in content

    def test_writes_review_items(self, temp_dir):
        items = [
            {
                "item_id": "R1",
                "feature": "报文编辑范围",
                "question": "编辑范围是否支持小于64B的报文？",
                "source": "spec ch3 PA.1",
                "status": "pending",
            }
        ]
        output = temp_dir / "review.md"
        write_review_md(items, output)
        content = output.read_text(encoding="utf-8")
        assert "R1: 报文编辑范围" in content
        assert "编辑范围是否支持小于64B的报文？" in content

    def test_writes_empty_notice(self, temp_dir):
        output = temp_dir / "review.md"
        write_review_md([], output)
        content = output.read_text(encoding="utf-8")
        assert "未发现需要确认的条目" in content


class TestWriteReviewFromTestplan:
    def test_extracts_and_writes(self, temp_dir):
        testplan = {
            "module_name": "UPA",
            "review_items": [
                {
                    "item_id": "R1",
                    "feature": "流控",
                    "question": "FIFO深度是多少？",
                    "source": "spec ch3 PA.3",
                    "status": "pending",
                }
            ],
        }
        output = temp_dir / "review.md"
        write_review_from_testplan(testplan, output)
        content = output.read_text(encoding="utf-8")
        assert "FIFO深度是多少？" in content
