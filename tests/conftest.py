"""
Shared fixtures for the mapping-and-inventory test suite.
"""

import os
import sys
import json
import shutil
import tempfile
from pathlib import Path

import pytest

# Ensure project root is on sys.path so imports work
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def tmp_dir(tmp_path):
    """Provide a clean temporary directory for each test."""
    return tmp_path


@pytest.fixture
def sample_directory(tmp_path):
    """Create a sample directory structure for inventory/tree generation tests."""
    # Create directories
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "utils").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "__pycache__").mkdir()  # Should be excluded
    (tmp_path / ".git").mkdir()  # Should be excluded

    # Create files
    (tmp_path / "README.md").write_text("# Test Project")
    (tmp_path / "src" / "main.py").write_text("print('hello')")
    (tmp_path / "src" / "utils" / "helpers.py").write_text("def helper(): pass")
    (tmp_path / "docs" / "guide.md").write_text("# Guide")
    (tmp_path / ".DS_Store").write_text("junk")  # Should be excluded
    (tmp_path / ".hidden_file").write_text("hidden")  # Should be excluded

    return tmp_path
