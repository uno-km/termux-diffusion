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


def test_fail_fast_when_source_build_not_allowed():
    """Verify that when prebuilt is unavailable and TERMUX_DIFFUSION_ALLOW_SOURCE_BUILD is not set,
    engine fails fast with E_PREBUILT_UNAVAILABLE and never attempts compilation."""
    with patch("termux_diffusion.installer.fetch_prebuilt_binary", return_value=None):
        with patch.dict(os.environ, {}, clear=True):
            with patch("subprocess.run") as mock_sub:
                with pytest.raises(ProvisioningError) as exc:
                    provision_engine(install_mode="prebuilt-first")
                assert exc.value.code == "E_PREBUILT_UNAVAILABLE"
                assert "export TERMUX_DIFFUSION_ALLOW_SOURCE_BUILD=1" in str(exc.value)
                mock_sub.assert_not_called()


def test_source_builder_only_invoked_when_explicitly_allowed():
    """Verify that source compilation is only entered when TERMUX_DIFFUSION_ALLOW_SOURCE_BUILD=1."""
    with patch("termux_diffusion.installer.fetch_prebuilt_binary", return_value=None):
        with patch.dict(os.environ, {"TERMUX_DIFFUSION_ALLOW_SOURCE_BUILD": "1"}):
            with patch("termux_diffusion.installer.is_android_termux", return_value=False):
                with patch("shutil.which", return_value=None):
                    with pytest.raises(ProvisioningError) as exc:
                        provision_engine(install_mode="prebuilt-first")
                    assert exc.value.code == ErrorCode.SOURCE_CLONE or "tools" in str(exc.value).lower()


def test_source_only_never_downloads_prebuilt():
    with patch("termux_diffusion.installer.fetch_prebuilt_binary") as mock_fetch:
        with patch.dict(os.environ, {"TERMUX_DIFFUSION_ALLOW_SOURCE_BUILD": "1"}):
            with patch("termux_diffusion.installer.is_android_termux", return_value=False):
                with patch("termux_diffusion.installer.shutil.which", return_value=None):
                    with pytest.raises(ProvisioningError) as exc:
                        provision_engine(install_mode="source-only", force=True)
                    assert exc.value.code == ErrorCode.SOURCE_CLONE or "tools" in str(exc.value).lower()
                    mock_fetch.assert_not_called()


def test_mutually_exclusive_install_options_fail():
    with pytest.raises(SystemExit) as exc:
        run_install_cli(["--prebuilt-only", "--build-from-source"])
    assert exc.value.code == ExitCode.CLI_ERROR


def test_prebuilt_dynamic_urls_and_env_override():
    from termux_diffusion.installer import get_prebuilt_base_url, get_candidate_prebuilt_urls
    from termux_diffusion._version import __version__

    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("TERMUX_DIFFUSION_RELEASE_BASE", None)
        os.environ.pop("AMEVA_RELEASE_BASE", None)
        base = get_prebuilt_base_url()
        assert f"v{__version__}" in base
        assert "v1.3.1" not in base

        urls = get_candidate_prebuilt_urls("sd-cli-vulkan-android-arm64.tar.gz")
        assert any(f"v{__version__}" in u for u in urls)
        assert any("releases/latest/download" in u for u in urls)
        assert not any("v1.3.1" in u for u in urls)

    with patch.dict(os.environ, {"TERMUX_DIFFUSION_RELEASE_TAG": "v2.5.0"}):
        base_override = get_prebuilt_base_url()
        assert "v2.5.0" in base_override

