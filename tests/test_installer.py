"""Unit tests for installer, CLI modes, binary resolution, and doctor diagnostics."""

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from termux_diffusion.installer import (
    get_engine_bin_dir,
    locate_sd_cli,
    run_doctor,
    provision_engine,
)
from termux_diffusion.cli import run_install_cli
from termux_diffusion.exceptions import ProvisioningError, ErrorCode, ExitCode


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


def test_diagnostics_only_exits_zero_and_does_not_call_installer():
    with patch("termux_diffusion.cli.provision_engine") as mock_provision:
        res = run_install_cli(["--diagnostics-only"])
        assert res == ExitCode.SUCCESS
        mock_provision.assert_not_called()


def test_prebuilt_only_missing_artifact_exits_20_and_never_calls_source_builder():
    with patch("termux_diffusion.installer.fetch_prebuilt_binary", return_value=None) as mock_fetch:
        with patch("subprocess.run") as mock_sub:
            with pytest.raises(SystemExit) as exc:
                run_install_cli(["--prebuilt-only"])
            assert exc.value.code == ExitCode.INTEGRITY_ERROR
            mock_fetch.assert_called_once()
            mock_sub.assert_not_called()


def test_prebuilt_first_calls_source_builder_after_prebuilts_fail():
    with patch("termux_diffusion.installer.fetch_prebuilt_binary", return_value=None):
        with patch("termux_diffusion.installer.is_android_termux", return_value=False):
            with patch("shutil.which", return_value=None):
                with patch("subprocess.run") as mock_sub:
                    with pytest.raises(ProvisioningError) as exc:
                        provision_engine(install_mode="prebuilt-first")
                    assert exc.value.code == ErrorCode.SOURCE_CLONE or "E_SOURCE" in exc.value.code or "git" in str(exc.value)


def test_source_only_never_downloads_prebuilt():
    with patch("termux_diffusion.installer.fetch_prebuilt_binary") as mock_fetch:
        with patch("termux_diffusion.installer.is_android_termux", return_value=False):
            with patch("termux_diffusion.installer.shutil.which", return_value=None):
                with pytest.raises(ProvisioningError) as exc:
                    provision_engine(install_mode="source-only", force=True)
                assert exc.value.code == ErrorCode.SOURCE_CLONE or "git" in str(exc.value).lower()
                mock_fetch.assert_not_called()


def test_mutually_exclusive_install_options_fail():
    with pytest.raises(SystemExit) as exc:
        run_install_cli(["--prebuilt-only", "--build-from-source"])
    assert exc.value.code == ExitCode.CLI_ERROR
