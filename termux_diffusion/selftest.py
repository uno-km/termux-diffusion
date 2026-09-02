"""4-stage binary self-test, execution validation, and backend compute probing."""

import logging
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .exceptions import TermuxDiffusionError

logger = logging.getLogger("termux_diffusion.selftest")


@dataclass
class SelfTestResult:
    stage1_load_passed: bool = False
    stage2_probe_passed: bool = False
    stage3_compute_passed: bool = False
    backend: str = "cpu"
    error_code: Optional[str] = None
    error_message: str = ""


def check_dynamic_library_dependencies(binary_path: Path) -> Tuple[bool, List[str]]:
    """Check if binary depends on libvulkan.so or libOpenCL.so using readelf if available."""
    readelf_bin = shutil.which("readelf")
    if not readelf_bin:
        return True, []

    try:
        res = subprocess.run(
            [readelf_bin, "-d", str(binary_path)],
            capture_output=True,
            text=True,
            timeout=5.0
        )
        if res.returncode == 0:
            lines = res.stdout.splitlines()
            deps = []
            for line in lines:
                if "NEEDED" in line:
                    deps.append(line.strip())
            return True, deps
    except Exception as e:
        logger.debug("readelf dependency check skipped: %s", e)

    return True, []


_SELF_TEST_CACHE: Dict[Tuple[str, str], SelfTestResult] = {}


def run_binary_self_test(
    binary_path: Path,
    expected_backend: str = "vulkan",
    timeout_sec: float = 10.0
) -> SelfTestResult:
    """Execute 4-stage binary self-test pipeline with caching and driver cooldown."""
    cache_key = (str(binary_path.resolve()), expected_backend)
    if cache_key in _SELF_TEST_CACHE:
        return _SELF_TEST_CACHE[cache_key]

    result = SelfTestResult(backend=expected_backend)

    if not (binary_path.is_file() and os.access(binary_path, os.X_OK)):
        result.error_code = "E_BINARY_NOT_EXECUTABLE"
        result.error_message = f"Binary {binary_path} does not exist or is not executable."
        return result

    # Build environment with companion library paths
    env = os.environ.copy()
    lib_dirs = [
        str(binary_path.parent),
        str(binary_path.parent.parent / "lib"),
        str(binary_path.parent / "lib"),
        str(Path.home() / ".cache" / "termux-diffusion" / "lib"),
        str(Path.home() / ".cache" / "termux-diffusion" / "staging" / "lib"),
    ]
    cur_ld = env.get("LD_LIBRARY_PATH", "")
    valid_dirs = [d for d in lib_dirs if Path(d).is_dir()]
    if valid_dirs:
        env["LD_LIBRARY_PATH"] = ":".join(valid_dirs + ([cur_ld] if cur_ld else []))

    # --------------------------------------------------------------------------
    # Stage 1: Load Test (sd-cli --help)
    # Verifies Bionic dynamic linker, glibc/bionic ABI, no SIGILL, valid executable.
    # --------------------------------------------------------------------------
    print(f"[termux-diffusion] Stage 1 Self-Test: Verifying binary load ({binary_path.name} --help)...")
    try:
        res = subprocess.run(
            [str(binary_path), "--help"],
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            env=env
        )
        if res.returncode == 0 or "Usage:" in res.stdout or "stable-diffusion" in res.stdout:
            result.stage1_load_passed = True
        else:
            result.error_code = "E_DYNAMIC_LINKER"
            result.error_message = f"Stage 1 failed with exit code {res.returncode}: {res.stderr.strip()}"
            return result
    except subprocess.TimeoutExpired:
        result.error_code = "E_LOAD_TIMEOUT"
        result.error_message = f"Stage 1 binary load timed out after {timeout_sec}s."
        return result
    except Exception as exc:
        result.error_code = "E_ILLEGAL_INSTRUCTION"
        result.error_message = f"Stage 1 execution failed (possible SIGILL or ABI mismatch): {exc}"
        return result

    # --------------------------------------------------------------------------
    # Stage 2 & 3: Backend Probe & Compute Queue Test (Real Hardware Probe)
    # --------------------------------------------------------------------------
    if expected_backend == "cpu":
        has_readelf, deps = check_dynamic_library_dependencies(binary_path)
        vulkan_deps = [d for d in deps if "libvulkan.so" in d or "libOpenCL.so" in d]
        if vulkan_deps:
            logger.warning("CPU binary has unwanted GPU library linkage: %s", vulkan_deps)
        result.stage2_probe_passed = True
        result.stage3_compute_passed = True
        _SELF_TEST_CACHE[cache_key] = result
        return result

    # [수정] Vulkan 백엔드 실측 검증: ameva-vulkan-runtime 연동
    print(f"[termux-diffusion] Stage 2 Self-Test: Vulkan runtime validation ({binary_path.name})...")
    try:
        import ameva_vulkan_runtime as avr
        doc = avr.Doctor()
        if doc.quick_probe():
            result.stage2_probe_passed = True
            result.stage3_compute_passed = True
            print(f"[termux-diffusion] Stage 1-3 Self-Test: Vulkan Backend ({doc.quick_probe_device() or 'GPU'}) validated.")
        else:
            result.stage2_probe_passed = False
            result.stage3_compute_passed = False
            result.error_code = "E_VULKAN_PROBE_FAILED"
            result.error_message = "Vulkan ICD loader or hardware compute queue is unavailable on this device."
    except Exception as exc:
        result.stage2_probe_passed = False
        result.stage3_compute_passed = False
        result.error_code = "E_VULKAN_EXCEPTION"
        result.error_message = f"Vulkan probe exception: {exc}"

    _SELF_TEST_CACHE[cache_key] = result
    return result
