"""Unit tests for DiffusionEngine, backend-specific binary locator, and Zero-Silent-Fallback rules."""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from termux_diffusion.engine import (
    DiffusionEngine,
    DiffusionRuntime,
    get_binary_path,
    locate_sd_cli,
    get_engine_bin_dir,
    get_engine_lib_dir,
    load,
)


def test_engine_directories():
    bin_dir = get_engine_bin_dir()
    lib_dir = get_engine_lib_dir()
    assert isinstance(bin_dir, Path)
    assert isinstance(lib_dir, Path)
    assert bin_dir.is_dir()
    assert lib_dir.is_dir()


def test_get_binary_path_cpu_returns_path_or_none():
    res = get_binary_path(backend="cpu")
    assert res is None or isinstance(res, Path)


def test_zero_silent_fallback_vulkan_never_returns_cpu_binary(tmp_path):
    """Zero-Silent-Fallback Core Test:
    When backend is 'vulkan' or 'gpu', but only CPU binary (sd-cli) exists,
    get_binary_path MUST return None and NEVER fall back to the CPU binary."""
    mock_bin_dir = tmp_path / "bin"
    mock_bin_dir.mkdir(parents=True)
    cpu_bin = mock_bin_dir / "sd-cli"
    cpu_bin.touch(mode=0o755)

    with patch("termux_diffusion.engine.get_engine_bin_dir", return_value=mock_bin_dir), \
         patch("shutil.which", return_value=None):
        vk_result = get_binary_path(backend="vulkan")
        assert vk_result is None, "Vulkan backend must return None when sd-cli-vulkan is missing, never fallback to sd-cli"

        gpu_result = get_binary_path(backend="gpu")
        assert gpu_result is None, "GPU backend must return None when sd-cli-vulkan is missing"


def test_vulkan_binary_located_when_present(tmp_path):
    """Verify that when sd-cli-vulkan is present, it is resolved correctly."""
    mock_bin_dir = tmp_path / "bin"
    mock_bin_dir.mkdir(parents=True)
    vk_bin = mock_bin_dir / "sd-cli-vulkan"
    vk_bin.touch(mode=0o755)

    with patch("termux_diffusion.engine.get_engine_bin_dir", return_value=mock_bin_dir), \
         patch("termux_diffusion.engine.TERMUX_PREFIX", str(tmp_path)):
        res = get_binary_path(backend="vulkan")
        assert res is not None
        assert res.name == "sd-cli-vulkan"


def test_locate_sd_cli_backward_compatibility():
    res = locate_sd_cli("cpu")
    assert res is None or isinstance(res, Path)


def test_diffusion_engine_initialization_and_methods():
    engine = DiffusionEngine(model="realistic", device="cpu", width=256, height=256)
    assert engine.model == "realistic"
    assert engine.device == "cpu"
    assert engine.requested_backend == "cpu"
    assert engine.kwargs == {"width": 256, "height": 256}

    # Factory function load()
    loaded_engine = load(model="anime", device="vulkan")
    assert isinstance(loaded_engine, DiffusionEngine)
    assert loaded_engine.model == "anime"
    assert loaded_engine.device == "vulkan"

    # Alias DiffusionRuntime
    assert DiffusionRuntime is DiffusionEngine


def test_diffusion_engine_generate_delegation():
    engine = DiffusionEngine(model="sdxs", device="cpu")
    with patch("termux_diffusion.core.generate") as mock_gen:
        mock_gen.return_value = Path("/tmp/output.png")
        res = engine.generate("test prompt", steps=4)
        assert res == Path("/tmp/output.png")
        mock_gen.assert_called_once_with(
            prompt="test prompt",
            model="sdxs",
            device="cpu",
            steps=4,
        )
