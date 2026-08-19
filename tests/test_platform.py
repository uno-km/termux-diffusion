"""Unit tests for platform inspection and Samsung Galaxy hardware bridges."""

import os
import pytest
from pathlib import Path

from termux_diffusion.platform import (
    TermuxWakeLock,
    check_memory_safety,
    get_galaxy_gallery_dir,
    get_memory_info,
    get_optimal_thread_count,
    is_android_termux,
    is_arm64,
)


def test_platform_detection():
    # Should run without throwing on any host
    termux = is_android_termux()
    assert isinstance(termux, bool)
    arm = is_arm64()
    assert isinstance(arm, bool)


def test_memory_info_and_safety():
    mem = get_memory_info()
    assert "mem_total_mb" in mem
    assert "effective_available_mb" in mem
    assert mem["effective_total_mb"] >= 0

    safe, msg = check_memory_safety(required_mb=500)
    assert isinstance(safe, bool)
    assert isinstance(msg, str)


def test_optimal_thread_count():
    threads = get_optimal_thread_count()
    assert threads >= 1
    assert threads <= (os.cpu_count() or 8)


def test_galaxy_gallery_directory():
    gallery_dir = get_galaxy_gallery_dir()
    assert isinstance(gallery_dir, Path)
    assert gallery_dir.is_dir()


def test_wake_lock_context_manager():
    with TermuxWakeLock(enabled=True) as lock:
        assert isinstance(lock, TermuxWakeLock)
