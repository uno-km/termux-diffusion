"""
termux_diffusion.doctor
=======================
Pre-flight diagnostics, hardware topology inspection, and system verification for termux-diffusion.
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import Optional

from .platform import (
    is_android_termux,
    is_arm64,
    get_memory_info,
    check_memory_safety,
)

logger = logging.getLogger("termux_diffusion.doctor")


def run_doctor() -> bool:
    """Run comprehensive 8-tier pre-flight diagnostic checks for Samsung Galaxy Termux setup."""
    from .engine import get_binary_path

    print("=" * 65)
    print("[Doctor] [termux-diffusion] Pre-flight Diagnostic Doctor")
    print("=" * 65)

    all_passed = True

    # 1. Platform Check
    is_termux = is_android_termux()
    arm_arch = is_arm64()
    print(f"1. Platform: {'Android Termux [OK]' if is_termux else 'Non-Termux Host (Emulation Mode) [INFO]'}")
    print(f"2. Architecture: {'ARM64 / aarch64 [OK]' if arm_arch else f'Host {sys.platform} ({os.name}) [INFO]'}")

    # 3. Memory & RAM Plus
    mem = get_memory_info()
    safe, msg = check_memory_safety(required_mb=1200)
    print(f"3. System Memory: {mem['mem_total_mb']}MB RAM + {mem['swap_total_mb']}MB Swap ({'Safe [OK]' if safe else 'Warning [WARN]'})")
    if not safe:
        print(f"   -> {msg}")

    # 4. Storage & Samsung Gallery
    storage_ok = os.path.exists(os.path.expanduser("~/storage"))
    print(f"4. Android Storage Permission: {'Configured [OK]' if storage_ok else 'Missing [WARN] (Run termux-setup-storage)'}")

    # 5. Compiler Toolchain
    clang_ok = bool(shutil.which("clang") or shutil.which("gcc") or shutil.which("clang++"))
    cmake_ok = bool(shutil.which("cmake"))
    git_ok = bool(shutil.which("git"))
    print(f"5. Build Tools: clang ({'[OK]' if clang_ok else '[FAIL]'}), cmake ({'[OK]' if cmake_ok else '[FAIL]'}), git ({'[OK]' if git_ok else '[FAIL]'})")
    if not (clang_ok and cmake_ok and git_ok) and is_termux:
        all_passed = False
        print("   -> Run: pkg install clang cmake git termux-api -y")

    # 6. Engine Binary
    engine = get_binary_path()
    print(f"6. Native C++ Engine (sd-cli): {str(engine) + ' [OK]' if engine else 'Not Provisioned [FAIL] (Run termux-diffusion install)'}")
    if not engine:
        all_passed = False

    # 7. Model Cache Status
    from .hub import list_cached_models
    cached = list_cached_models()
    print(f"7. Cached GGUF Models: {len(cached)} model(s) available locally.")
    for m in cached:
        valid_tag = " [GGUF Valid [OK]]" if m.get("is_valid_gguf") else " [Header [WARN]]"
        print(f"   -> {m['name']} ({m['size_mb']} MB){valid_tag}")

    # 8. Hardware Acceleration (GPU / NPU / TPU / Vulkan / OpenCL)
    try:
        from ameva_runtime.vulkan.adapters import find_system_vulkan_driver_dir
        discovered_vulkan = find_system_vulkan_driver_dir()
    except ImportError:
        discovered_vulkan = None

    from .hardware import detect_hardware_profile
    hw = detect_hardware_profile()
    print("8. Hardware Acceleration Profile:")
    print(f"   SoC: {hw.soc_name}, GPU Architecture: {hw.gpu_name}")
    print(f"   GPU Vulkan: {'Available [OK]' if (hw.vulkan_available or discovered_vulkan) else 'Not Found [WARN]'}")
    if discovered_vulkan:
        print(f"     -> Vulkan Driver (ameva-runtime): {discovered_vulkan}")
    elif hw.vulkan_driver:
        print(f"     -> Vulkan Driver: {hw.vulkan_driver.library_path}")
    print(f"   GPU OpenCL: {'Available [OK]' if hw.opencl_available else 'Not Found [WARN]'}")
    if hw.opencl_driver:
        print(f"     -> OpenCL Driver: {hw.opencl_driver.library_path}")
    if hw.npu_profile and hw.npu_profile.available:
        print("   NPU / TPU Hardware: Detected [INFO]")
        print(f"     -> Architecture: {hw.npu_profile.dsp_architecture} ({hw.npu_profile.tops_rating} TOPS)")
        print(f"     -> Driver: {hw.npu_profile.driver_library}")
        print("     -> Runtime: Native QNN C++ execution scheduled for v2.0")
    else:
        print("   NPU / TPU Hardware: Not Detected [INFO] (GPU Vulkan & CPU NEON Active)")
    print(f"   CPU ISA SIMD: DotProd={'[OK]' if hw.has_dotprod else '[FAIL]'} "
          f"FP16={'[OK]' if hw.has_fp16 else '[FAIL]'} "
          f"I8MM={'[OK]' if hw.has_i8mm else '[FAIL]'} "
          f"SVE={'[OK]' if hw.has_sve else '[FAIL]'}")
    print(f"   Active Compute Pipeline: {hw.recommended_backend.value.upper()} "
          f"(Offload Layers: {hw.recommended_ngl})")

    # 9. Android 12+ Background Stability Guard (Phantom Process Killer)
    if is_termux:
        print("9. Android 12+ Background Guard:")
        print("   -> Tip: If generation crashes when Termux is in background, enable")
        print("          'Developer Options > Disable child process restrictions'")
        print("          or run: adb shell \"/system/bin/device_config put activity_manager max_phantom_processes 2147483647\"")

    print("=" * 65)
    if all_passed:
        print("All core diagnostics passed. System is ready for AI image generation.")
    else:
        print("Some diagnostics need attention. Run 'termux-diffusion install' to resolve.")
    print("=" * 65)
    return all_passed
