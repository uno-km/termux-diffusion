"""Unit tests for hardware acceleration detection module."""

import os
import pytest
from unittest.mock import patch, MagicMock

from termux_diffusion.hardware import (
    ComputeBackend,
    HardwareProfile,
    _read_cpuinfo_features,
    _build_cmake_flags,
    detect_hardware_profile,
    format_hardware_report,
    resolve_device_backend,
    get_sd_cli_gpu_args,
)


def test_detect_hardware_profile_returns_valid_profile():
    """detect_hardware_profile must always return a HardwareProfile, never crash."""
    profile = detect_hardware_profile()
    assert isinstance(profile, HardwareProfile)
    assert profile.cpu_cores >= 1
    assert isinstance(profile.cpu_arch, str)
    assert isinstance(profile.vulkan_available, bool)
    assert isinstance(profile.opencl_available, bool)
    assert isinstance(profile.recommended_backend, ComputeBackend)
    assert profile.recommended_ngl >= 0


def test_format_hardware_report_returns_string():
    """format_hardware_report must produce a non-empty human-readable string."""
    profile = detect_hardware_profile()
    report = format_hardware_report(profile)
    assert isinstance(report, str)
    assert len(report) > 50
    assert "SoC" in report
    assert "Vulkan" in report
    assert "OpenCL" in report


def test_resolve_device_backend_cpu():
    """CPU mode must always resolve without probing hardware."""
    device, ngl = resolve_device_backend("cpu")
    assert device == "cpu"
    assert ngl == 0


def test_resolve_device_backend_auto():
    """Auto mode must return a valid backend enum value."""
    device, ngl = resolve_device_backend("auto")
    assert device in ("cpu", "vulkan", "opencl")
    assert ngl >= 0


def test_resolve_device_backend_vulkan_fallback():
    """If Vulkan is requested but not available, must fall back to CPU (not crash)."""
    device, ngl = resolve_device_backend("vulkan")
    # Either Vulkan works or it falls back to CPU
    assert device in ("vulkan", "cpu")
    if device == "cpu":
        assert ngl == 0


def test_get_sd_cli_gpu_args_cpu():
    """CPU mode must produce zero extra CLI args."""
    args = get_sd_cli_gpu_args("cpu", 0)
    assert args == []


def test_get_sd_cli_gpu_args_vulkan():
    """Vulkan mode must produce -ngl flag."""
    args = get_sd_cli_gpu_args("vulkan", 99)
    assert args == ["-ngl", "99"]


def test_get_sd_cli_gpu_args_opencl():
    """OpenCL mode must produce -ngl flag."""
    args = get_sd_cli_gpu_args("opencl", 32)
    assert args == ["-ngl", "32"]


def test_cmake_flags_include_march_when_arm64():
    """On aarch64, cmake flags must include -march optimization."""
    profile = HardwareProfile(
        cpu_arch="aarch64",
        has_dotprod=True,
        has_fp16=True,
        has_i8mm=False,
    )
    flags = _build_cmake_flags(profile)
    flag_str = " ".join(flags)
    assert "-O3" in flag_str
    assert "dotprod" in flag_str
    assert "fp16" in flag_str


def test_cmake_flags_vulkan_flag_when_available():
    """Vulkan cmake flags must include -DSD_VULKAN=ON and library path."""
    from termux_diffusion.hardware import GPUDriverInfo
    profile = HardwareProfile(
        cpu_arch="aarch64",
        vulkan_available=True,
        vulkan_driver=GPUDriverInfo(
            name="Test Vulkan",
            library_path="/system/lib64/libvulkan.so",
            usable=True,
        ),
    )
    flags = _build_cmake_flags(profile)
    flag_str = " ".join(flags)
    assert "-DSD_VULKAN=ON" in flag_str
    assert "/system/lib64/libvulkan.so" in flag_str


def test_cpuinfo_features_returns_list():
    """_read_cpuinfo_features must return a list (possibly empty on non-ARM)."""
    features = _read_cpuinfo_features()
    assert isinstance(features, list)
