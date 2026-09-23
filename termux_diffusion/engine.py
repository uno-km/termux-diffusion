"""
termux_diffusion.engine
=======================
High-performance C++ core engine locator, backend dispatcher, and high-level DiffusionEngine wrapper.
Strict Zero-Silent-Fallback and Anti-Deception compliant architecture matching AMEVA standards.
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from .platform import (
    TERMUX_PREFIX,
    is_android_termux,
    get_default_cache_dir,
)

logger = logging.getLogger("termux_diffusion.engine")


def get_engine_bin_dir() -> Path:
    """Return canonical directory where termux-diffusion binaries reside ($PREFIX/bin SSOT)."""
    prefix = os.environ.get("PREFIX") or TERMUX_PREFIX
    if is_android_termux() or os.path.exists(prefix):
        bin_dir = Path(prefix) / "bin"
    else:
        bin_dir = get_default_cache_dir() / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    return bin_dir


def get_engine_lib_dir() -> Path:
    """Return canonical directory where native shared libraries reside ($PREFIX/lib SSOT)."""
    prefix = os.environ.get("PREFIX") or TERMUX_PREFIX
    if is_android_termux() or os.path.exists(prefix):
        lib_dir = Path(prefix) / "lib"
    else:
        lib_dir = get_default_cache_dir() / "lib"
    lib_dir.mkdir(parents=True, exist_ok=True)
    return lib_dir


def get_binary_path(backend: str = "auto") -> Optional[Path]:
    """Find authoritative absolute path of sd-cli executable strictly isolated by compute backend.
    
    Zero-Silent-Fallback Rules:
    - 'gpu' / 'vulkan': Exclusively search for native Vulkan binary (sd-cli-vulkan).
                        Never fallback to CPU binary. Return None if unprovisioned.
    - 'cpu' / default:  Exclusively search for pure CPU NEON binary (sd-cli-cpu, sd-cli).
    """
    home = Path(os.environ.get("HOME", os.path.expanduser("~")))
    prefix_bin = Path(TERMUX_PREFIX) / "bin"
    bin_dir = get_engine_bin_dir()
    ameva_diff_dir = home / ".local" / "share" / "ameva" / "current" / "diffusion"

    req_backend = str(backend or "auto").strip().lower()

    # --------------------------------------------------------------------------
    # 1. GPU / Vulkan Route: Pure Vulkan GPU Binary (sd-cli-vulkan)
    # --------------------------------------------------------------------------
    if req_backend in ("vulkan", "gpu"):
        vulkan_candidates = [
            # AMEVA 2-Tier isolated current deployment
            ameva_diff_dir / "sd-cli-vulkan",
            # Termux prefix binary
            prefix_bin / "sd-cli-vulkan",
            bin_dir / "sd-cli-vulkan",
            # User local binary
            home / ".local" / "bin" / "sd-cli-vulkan",
        ]
        for p in vulkan_candidates:
            if p.is_file() and (os.access(p, os.X_OK) or os.name == "nt"):
                return p.resolve()

        # System PATH search strictly for 'sd-cli-vulkan'
        which_vk = shutil.which("sd-cli-vulkan")
        if which_vk and (os.access(which_vk, os.X_OK) or os.name == "nt"):
            return Path(which_vk).resolve()

        # Zero-Silent-Fallback: If Vulkan binary is absent, NEVER return CPU binary!
        return None

    # --------------------------------------------------------------------------
    # 2. CPU Baseline Route: Pure CPU NEON Binary (sd-cli-cpu, sd-cli)
    # --------------------------------------------------------------------------
    cpu_candidates = [
        bin_dir / "sd-cli-cpu",
        prefix_bin / "sd-cli-cpu",
        bin_dir / "sd-cli-source-cpu",
        bin_dir / "sd-cli",
        prefix_bin / "sd-cli",
        home / ".local" / "bin" / "sd-cli-cpu",
        home / ".local" / "bin" / "sd-cli",
    ]
    for p in cpu_candidates:
        if p.is_file() and (os.access(p, os.X_OK) or os.name == "nt"):
            return p.resolve()

    # System PATH search for CPU binary
    for name in ("sd-cli", "sd-cli.exe", "sd", "sd.exe"):
        which_path = shutil.which(name)
        if which_path and (os.access(which_path, os.X_OK) or os.name == "nt"):
            return Path(which_path).resolve()

    return None


def locate_sd_cli(backend: Optional[str] = None) -> Optional[Path]:
    """Backward-compatible alias for get_binary_path."""
    return get_binary_path(backend=backend or "auto")


class DiffusionEngine:
    """High-level Python SDK Engine for On-Device Stable Diffusion inference.
    Follows canonical AMEVA component architecture matching LlamaRuntime and BitNetEngine.
    """

    def __init__(
        self,
        model: str = "realistic",
        backend: str = "auto",
        device: Optional[str] = None,
        **kwargs: Any,
    ):
        self.model = model
        self.device = device or backend or "auto"
        self.requested_backend = self.device.strip().lower()
        self.bin_dir = get_engine_bin_dir()
        self.lib_dir = get_engine_lib_dir()
        self.kwargs = kwargs

    def get_binary_path(self, backend: Optional[str] = None) -> Optional[Path]:
        """Resolve authoritative binary path for active or specified backend."""
        target_backend = backend if backend is not None else self.requested_backend
        return get_binary_path(backend=target_backend)

    def generate(self, prompt: str, **kwargs: Any) -> Any:
        """Execute text-to-image generation delegating to core pipeline."""
        from .core import generate
        merged = {**self.kwargs, **kwargs}
        merged.setdefault("device", self.requested_backend)
        merged.setdefault("model", self.model)
        return generate(prompt=prompt, **merged)

    @staticmethod
    def doctor() -> bool:
        """Run comprehensive pre-flight diagnostic checks."""
        from .doctor import run_doctor
        return run_doctor()


def load(model: str = "realistic", device: str = "auto", **kwargs: Any) -> DiffusionEngine:
    """Standard Unified Engine Factory for termux-diffusion matching AMEVA multi-modal standards."""
    return DiffusionEngine(model=model, device=device, **kwargs)


# Backward-compatible alias matching LlamaRuntime
DiffusionRuntime = DiffusionEngine

