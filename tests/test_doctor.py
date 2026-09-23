"""Unit tests for pre-flight doctor diagnostics in termux-diffusion."""

from unittest.mock import patch
from termux_diffusion.doctor import run_doctor


def test_doctor_execution(capsys):
    res = run_doctor()
    captured = capsys.readouterr()
    assert "Pre-flight Diagnostic Doctor" in captured.out
    assert "Platform:" in captured.out
    assert "Native C++ Engine" in captured.out
    assert isinstance(res, bool)
