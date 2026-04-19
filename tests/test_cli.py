"""Tests for the CLI interface."""

import json
import tempfile
from pathlib import Path

import pytest

from clearhealth.cli import main


class TestCLI:
    """Test CLI commands."""

    def test_version(self, capsys):
        result = main(["--version"])
        assert result == 0
        captured = capsys.readouterr()
        assert "clearhealth" in captured.out

    def test_no_args_shows_help(self, capsys):
        result = main([])
        assert result == 0

    def test_analyse_file(self, capsys, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("Take your medicine every day with water.")

        result = main(["analyse", str(test_file)])
        assert result == 0
        captured = capsys.readouterr()
        assert "Accessibility Grade" in captured.out

    def test_analyse_json_format(self, capsys, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("The patient has hypertension.")

        result = main(["analyse", str(test_file), "--format", "json"])
        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "grade" in data
        assert "readability" in data

    def test_analyse_missing_file(self, capsys):
        result = main(["analyse", "/nonexistent/file.txt"])
        assert result == 1

    def test_analyse_stdin(self, capsys, monkeypatch):
        import io
        monkeypatch.setattr("sys.stdin", io.StringIO("Simple health advice."))
        result = main(["analyse", "-"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Accessibility Grade" in captured.out

    def test_analyse_empty_file(self, capsys, tmp_path):
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")
        result = main(["analyse", str(test_file)])
        assert result == 1

    def test_analyze_alias(self, capsys, tmp_path):
        """American spelling should work too."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Simple text here.")
        result = main(["analyze", str(test_file)])
        assert result == 0

    def test_custom_threshold(self, capsys, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("Take medicine daily.")
        result = main(["analyse", str(test_file), "--threshold", "5.0"])
        assert result == 0
