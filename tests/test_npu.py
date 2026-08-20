"""Unit tests for NPU and TPU acceleration engine."""

import pytest
from unittest.mock import patch

from termux_diffusion.npu import (
    NPUProfile,
    NPUVendor,
    QUALCOMM_QNN_LIBS,
    SAMSUNG_EDEN_LIBS,
    GOOGLE_EDGETPU_LIBS,
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
    """Verify Qualcomm Snapdragon Hexagon NPU detection and TOPS rating when driver is present."""
    with patch("termux_diffusion.npu._read_android_prop", side_effect=lambda key: "sm8650" if key == "ro.board.platform" else ""), \
         patch("termux_diffusion.npu._probe_first_existing_lib", side_effect=lambda libs: "/vendor/lib64/libQnnHtp.so" if libs == QUALCOMM_QNN_LIBS else None):
        profile = detect_npu_capabilities()
        assert profile.available is True
        assert profile.vendor == NPUVendor.QUALCOMM_HEXAGON
        assert profile.tops_rating == 45.0
        assert "Hexagon v75" in profile.dsp_architecture
        assert "INT4" in profile.supported_precisions
        assert profile.driver_library == "/vendor/lib64/libQnnHtp.so"


def test_npu_detected_soc_without_driver_reports_unavailable():
    """Verify that when SoC matches but .so driver is missing on disk, available is False."""
    with patch("termux_diffusion.npu._read_android_prop", side_effect=lambda key: "sm8650" if key == "ro.board.platform" else ""), \
         patch("termux_diffusion.npu._probe_first_existing_lib", return_value=None):
        profile = detect_npu_capabilities()
        assert profile.available is False
        assert profile.driver_library is None
        assert profile.tops_rating == 0.0


def test_samsung_exynos_npu_mock():
    """Verify Samsung Exynos NPU detection."""
    with patch("termux_diffusion.npu._read_android_prop", side_effect=lambda key: "exynos2400" if key == "ro.hardware.chipname" else ""), \
         patch("termux_diffusion.npu._probe_first_existing_lib", side_effect=lambda libs: "/vendor/lib64/libenn_public_api.so" if libs == SAMSUNG_EDEN_LIBS else None):
        profile = detect_npu_capabilities()
        assert profile.available is True
        assert profile.vendor == NPUVendor.SAMSUNG_EDEN
        assert profile.tops_rating == 42.0
        assert "Exynos" in profile.chipset_name


def test_google_tensor_tpu_mock():
    """Verify Google Tensor Edge TPU detection."""
    with patch("termux_diffusion.npu._read_android_prop", side_effect=lambda key: "zuma" if key == "ro.hardware" else ""), \
         patch("termux_diffusion.npu._probe_first_existing_lib", side_effect=lambda libs: "/vendor/lib64/libedgetpu.so" if libs == GOOGLE_EDGETPU_LIBS else None):
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


from termux_diffusion.exceptions import PlatformNotSupportedError


def test_resolve_device_backend_npu_explicit_error():
    """Requesting device='npu' or 'tpu' must raise PlatformNotSupportedError with actionable v2.0 roadmap guidance."""
    with pytest.raises(PlatformNotSupportedError) as exc_npu:
        resolve_device_backend("npu")
    assert "v2.0" in str(exc_npu.value)
    assert "vulkan" in str(exc_npu.value)

    with pytest.raises(PlatformNotSupportedError) as exc_tpu:
        resolve_device_backend("tpu")
    assert "v2.0" in str(exc_tpu.value)


def test_format_hardware_report_includes_npu():
    """Hardware report must include NPU/TPU acceleration section."""
    hw = detect_hardware_profile()
    report = format_hardware_report(hw)
    assert "NPU / TPU" in report
    assert "Vulkan" in report
    assert "CPU" in report
