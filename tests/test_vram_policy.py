"""Deterministic unit test suite for Autonomous VRAM Tiering & TermuxExecutionGuard."""

from unittest.mock import patch
import pytest

from termux_diffusion.core import (
    resolve_vram_and_streaming_policy,
)
from termux_diffusion.hardware import (
    TermuxExecutionGuard,
)


def test_vram_policy_user_explicit_residency():
    """User specifying --max-vram 0 must disable graph splitting completely."""
    vram, stream, reason = resolve_vram_and_streaming_policy(
        user_max_vram="0",
        user_stream_layers=False,
        model_bytes=3_683_370_944,
    )
    assert vram is None
    assert stream is False
    assert "Full In-VRAM residency" in reason


def test_vram_policy_user_explicit_custom_budget():
    """User specifying explicit max-vram must be honored as highest priority."""
    vram, stream, reason = resolve_vram_and_streaming_policy(
        user_max_vram="vulkan0=2",
        user_stream_layers=True,
        model_bytes=3_683_370_944,
    )
    assert vram == "vulkan0=2"
    assert stream is True
    assert "User explicit override" in reason


def test_vram_policy_tier1_flagship_ample_ram():
    """Flagship devices with ample unpinned physical DRAM (e.g. S20 12GB -> ~5.6GB avail) auto-select Tier 1."""
    with patch("termux_diffusion.core.get_kernel_physical_memory_gb", return_value=(10.35, 5.6)):
        vram, stream, reason = resolve_vram_and_streaming_policy(
            user_max_vram=None,
            user_stream_layers=False,
            model_bytes=3_683_370_944,
        )
        assert vram is None
        assert stream is False
        assert "Tier 1 Flagship Auto-Scale" in reason
        assert "Full In-VRAM Residency" in reason


def test_vram_policy_tier1_compact_model_on_8gb():
    """8GB devices with 2.2GB available RAM auto-select Tier 1 for compact models (e.g. SDXS ~650MB)."""
    with patch("termux_diffusion.core.get_kernel_physical_memory_gb", return_value=(7.03, 2.2)):
        vram, stream, reason = resolve_vram_and_streaming_policy(
            user_max_vram=None,
            user_stream_layers=False,
            model_bytes=652_000_000,
        )
        assert vram is None
        assert stream is False
        assert "Tier 1 Flagship Auto-Scale" in reason


def test_vram_policy_tier2_lmk_protection_on_8gb():
    """8GB devices with 2.2GB available RAM safely auto-scale to Tier 2 for 3.43GB models to prevent LMK SIGKILL."""
    with patch("termux_diffusion.core.get_kernel_physical_memory_gb", return_value=(7.03, 2.2)):
        vram, stream, reason = resolve_vram_and_streaming_policy(
            user_max_vram=None,
            user_stream_layers=False,
            model_bytes=3_683_370_944,
        )
        assert vram == "vulkan0=1.5"
        assert stream is False
        assert "Tier 2 Balanced Auto-Scale" in reason


def test_vram_policy_tier2_balanced_a35():
    """6GB devices (e.g. A35 -> 5.5GB total, 1.8GB avail) auto-select Tier 2 chunk buffer."""
    with patch("termux_diffusion.core.get_kernel_physical_memory_gb", return_value=(5.5, 1.8)):
        vram, stream, reason = resolve_vram_and_streaming_policy(
            user_max_vram=None,
            user_stream_layers=False,
            model_bytes=3_683_370_944,
        )
        assert vram == "vulkan0=1.5"
        assert stream is False
        assert "Tier 2 Balanced Auto-Scale" in reason


def test_vram_policy_tier3_constrained_lifeboat():
    """Constrained devices (<1.6GB avail and <5.4GB total) auto-select Tier 3 lifeboat streaming."""
    with patch("termux_diffusion.core.get_kernel_physical_memory_gb", return_value=(3.6, 0.9)):
        vram, stream, reason = resolve_vram_and_streaming_policy(
            user_max_vram=None,
            user_stream_layers=False,
            model_bytes=3_683_370_944,
        )
        assert vram == "vulkan0=1"
        assert stream is True
        assert "Tier 3 Constrained Auto-Scale" in reason
        assert "1MB Layer-Streaming Lifeboat" in reason


def test_termux_execution_guard_context_lifecycle():
    """TermuxExecutionGuard context manager must enter and exit safely without raising."""
    with patch("termux_diffusion.hardware.is_termux", return_value=False):
        with TermuxExecutionGuard(enable_wake_lock=True, boost_priority=True) as guard:
            assert guard is not None
            assert guard.wake_lock_acquired is False
