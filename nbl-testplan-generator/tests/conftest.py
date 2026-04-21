"""Pytest fixtures for nbl-testplan-generator tests."""
import json
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_spec_md(fixtures_dir) -> Path:
    """Return path to sample spec markdown file."""
    return fixtures_dir / "sample_spec.md"


@pytest.fixture
def sample_template_xlsx(fixtures_dir) -> Path:
    """Return path to template xlsx file."""
    return fixtures_dir / "testplan_template.xlsx"
