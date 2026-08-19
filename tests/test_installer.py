"""Unit tests for installer, binary resolution, and doctor diagnostics."""

import os
from pathlib import Path
import pytest

from termux_diffusion.installer import (
    get_engine_bin_dir,
    locate_sd_cli,
    run_doctor,
)


def test_engine_bin_dir():
    bin_dir = get_engine_bin_dir()
    assert isinstance(bin_dir, Path)
    assert bin_dir.is_dir()


def test_locate_sd_cli_returns_path_or_none():
    result = locate_sd_cli()
    assert result is None or isinstance(result, Path)


def test_run_doctor_runs_without_crashing(capsys):
    result = run_doctor()
    captured = capsys.readouterr()
    assert "Pre-flight Diagnostic Doctor" in captured.out
    assert "Platform:" in captured.out
    assert isinstance(result, bool)
