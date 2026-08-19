"""Unit tests for NPU and TPU acceleration engine."""

import pytest
from unittest.mock import patch

from termux_diffusion.npu import (
    NPUProfile,
    NPUVendor,
    detect_npu_capabilities,
    get_optimal_heterogeneous_pipeline,
)
from termux_diffusion.hardware import (
    detect_hardware_profile,
    resolve_device_backend,
    format_hardware_report,
)


def test_detect_npu_capabilities_returns_valid_profile():
    """NPU detection must never raise exception and return structured NPUProfile."""
    profile = detect_npu_capabilities()
    assert isinstance(profile, NPUProfile)
    assert isinstance(profile.available, bool)
    assert isinstance(profile.vendor, NPUVendor)
    assert isinstance(profile.tops_rating, float)
    assert isinstance(profile.supported_precisions, list)


def test_qualcomm_snapdragon_npu_mock():
    """Verify Qualcomm Snapdragon Hexagon NPU detection and TOPS rating."""
    with patch("termux_diffusion.npu._read_android_prop", side_effect=lambda key: "sm8650" if key == "ro.board.platform" else ""):
        profile = detect_npu_capabilities()
        assert profile.available is True
        assert profile.vendor == NPUVendor.QUALCOMM_HEXAGON
        assert profile.tops_rating == 45.0
        assert "Hexagon v75" in profile.dsp_architecture
        assert "INT4" in profile.supported_precisions


def test_samsung_exynos_npu_mock():
    """Verify Samsung Exynos NPU detection."""
    with patch("termux_diffusion.npu._read_android_prop", side_effect=lambda key: "exynos2400" if key == "ro.hardware.chipname" else ""):
        profile = detect_npu_capabilities()
        assert profile.available is True
        assert profile.vendor == NPUVendor.SAMSUNG_EDEN
        assert profile.tops_rating == 42.0
        assert "Exynos" in profile.chipset_name


def test_google_tensor_tpu_mock():
    """Verify Google Tensor Edge TPU detection."""
    with patch("termux_diffusion.npu._read_android_prop", side_effect=lambda key: "zuma" if key == "ro.hardware" else ""):
        profile = detect_npu_capabilities()
        assert profile.available is True
        assert profile.vendor == NPUVendor.GOOGLE_EDGE_TPU
        assert profile.tops_rating == 20.0
        assert "Edge TPU" in profile.dsp_architecture


def test_heterogeneous_pipeline_allocation():
    """Verify heterogeneous graph partitioning map."""
    pipeline = get_optimal_heterogeneous_pipeline("auto")
    assert "text_encoder" in pipeline
    assert "denoiser_unet" in pipeline
    assert "vae_decoder" in pipeline
    assert "summary" in pipeline


def test_resolve_device_backend_npu_route():
    """Test device='npu' and device='tpu' routing in hardware module."""
    dev, ngl = resolve_device_backend("npu")
    assert dev in ("vulkan", "cpu")
    assert ngl >= 0

    dev_tpu, ngl_tpu = resolve_device_backend("tpu")
    assert dev_tpu in ("vulkan", "cpu")
    assert ngl_tpu >= 0


def test_format_hardware_report_includes_npu():
    """Hardware report must include NPU/TPU acceleration section."""
    hw = detect_hardware_profile()
    report = format_hardware_report(hw)
    assert "NPU / TPU" in report
    assert "Vulkan" in report
    assert "CPU" in report
