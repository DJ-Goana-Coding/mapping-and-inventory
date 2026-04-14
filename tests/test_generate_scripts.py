"""
Tests for scripts/generate_inventory.py and scripts/generate_tree.py
Covers: inventory generation, tree generation, exclusion rules, stats, formatting.
"""

import json
import os
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.generate_inventory import generate_inventory
from scripts.generate_tree import generate_tree


# ---------------------------------------------------------------------------
# generate_inventory
# ---------------------------------------------------------------------------

class TestGenerateInventory:
    """Tests for generate_inventory"""

    def test_returns_valid_json(self, sample_directory):
        result = generate_inventory(str(sample_directory))
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_contains_required_keys(self, sample_directory):
        data = json.loads(generate_inventory(str(sample_directory)))
        assert "generated" in data
        assert "files" in data
        assert "directories" in data
        assert "stats" in data

    def test_excludes_git_directory(self, sample_directory):
        data = json.loads(generate_inventory(str(sample_directory)))
        dir_paths = [d['name'] for d in data['directories']]
        assert ".git" not in dir_paths

    def test_excludes_pycache_directory(self, sample_directory):
        data = json.loads(generate_inventory(str(sample_directory)))
        dir_paths = [d['name'] for d in data['directories']]
        assert "__pycache__" not in dir_paths

    def test_excludes_ds_store(self, sample_directory):
        data = json.loads(generate_inventory(str(sample_directory)))
        file_names = [f['name'] for f in data['files']]
        assert ".DS_Store" not in file_names

    def test_excludes_hidden_files(self, sample_directory):
        data = json.loads(generate_inventory(str(sample_directory)))
        file_names = [f['name'] for f in data['files']]
        assert ".hidden_file" not in file_names

    def test_includes_visible_files(self, sample_directory):
        data = json.loads(generate_inventory(str(sample_directory)))
        file_names = [f['name'] for f in data['files']]
        assert "README.md" in file_names
        assert "main.py" in file_names
        assert "helpers.py" in file_names
        assert "guide.md" in file_names

    def test_includes_visible_directories(self, sample_directory):
        data = json.loads(generate_inventory(str(sample_directory)))
        dir_names = [d['name'] for d in data['directories']]
        assert "src" in dir_names
        assert "docs" in dir_names

    def test_stats_total_files(self, sample_directory):
        data = json.loads(generate_inventory(str(sample_directory)))
        assert data['stats']['total_files'] == len(data['files'])
        assert data['stats']['total_files'] > 0

    def test_stats_total_size(self, sample_directory):
        data = json.loads(generate_inventory(str(sample_directory)))
        assert data['stats']['total_size'] > 0

    def test_stats_by_extension(self, sample_directory):
        data = json.loads(generate_inventory(str(sample_directory)))
        extensions = data['stats']['by_extension']
        assert ".md" in extensions
        assert ".py" in extensions

    def test_file_entries_have_required_fields(self, sample_directory):
        data = json.loads(generate_inventory(str(sample_directory)))
        for f in data['files']:
            assert "path" in f
            assert "name" in f
            assert "size" in f
            assert "extension" in f

    def test_empty_directory(self, tmp_path):
        data = json.loads(generate_inventory(str(tmp_path)))
        assert data['stats']['total_files'] == 0
        assert data['files'] == []


# ---------------------------------------------------------------------------
# generate_tree
# ---------------------------------------------------------------------------

class TestGenerateTree:
    """Tests for generate_tree"""

    def test_returns_string(self, sample_directory):
        result = generate_tree(str(sample_directory))
        assert isinstance(result, str)

    def test_contains_header(self, sample_directory):
        result = generate_tree(str(sample_directory))
        assert "# District File Tree" in result

    def test_contains_generated_timestamp(self, sample_directory):
        result = generate_tree(str(sample_directory))
        assert "**Generated**:" in result

    def test_contains_code_block(self, sample_directory):
        result = generate_tree(str(sample_directory))
        assert "```" in result

    def test_contains_footer(self, sample_directory):
        result = generate_tree(str(sample_directory))
        assert "Bridge Agent" in result

    def test_excludes_git_directory(self, sample_directory):
        result = generate_tree(str(sample_directory))
        # .git should not appear in the tree output
        lines = result.split("\n")
        dir_lines = [l for l in lines if l.strip().endswith("/")]
        dir_names = [l.strip().rstrip("/") for l in dir_lines]
        assert ".git" not in dir_names

    def test_excludes_pycache(self, sample_directory):
        result = generate_tree(str(sample_directory))
        assert "__pycache__" not in result

    def test_includes_visible_files(self, sample_directory):
        result = generate_tree(str(sample_directory))
        assert "README.md" in result
        assert "main.py" in result

    def test_excludes_hidden_files(self, sample_directory):
        result = generate_tree(str(sample_directory))
        assert ".hidden_file" not in result
        assert ".DS_Store" not in result

    def test_includes_subdirectories(self, sample_directory):
        result = generate_tree(str(sample_directory))
        assert "src/" in result
        assert "docs/" in result

    def test_empty_directory(self, tmp_path):
        result = generate_tree(str(tmp_path))
        assert "# District File Tree" in result
        # Should still have the structure section
        assert "## Structure" in result
