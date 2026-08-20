"""Automated C++ core engine provisioning, binary locator, build healer, and doctor diagnostics."""

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from .exceptions import ProvisioningError
from .platform import (
    TERMUX_PREFIX,
    check_memory_safety,
    get_default_cache_dir,
    get_memory_info,
    is_android_termux,
    is_arm64,
)

logger = logging.getLogger("termux_diffusion.installer")

SD_CPP_REPO = "https://github.com/leejet/stable-diffusion.cpp"


def get_engine_bin_dir() -> Path:
    """Return directory where compiled termux-diffusion binaries reside."""
    bin_dir = get_default_cache_dir() / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    return bin_dir


def locate_sd_cli() -> Optional[Path]:
    """Locate the compiled sd-cli executable binary across standard locations."""
    # 1. Custom cached engine binary
    for fname in ("sd-cli", "sd-cli.exe", "sd", "sd.exe"):
        cached_bin = get_engine_bin_dir() / fname
        if cached_bin.is_file() and (os.access(cached_bin, os.X_OK) or os.name == "nt"):
            return cached_bin.resolve()

    # 2. System PATH
    for name in ("sd-cli", "sd-cli.exe", "sd", "sd.exe"):
        which_path = shutil.which(name)
        if which_path and (os.access(which_path, os.X_OK) or os.name == "nt"):
            return Path(which_path).resolve()

    # 3. Termux prefix bin
    for name in ("sd-cli", "sd"):
        termux_bin = Path(TERMUX_PREFIX) / "bin" / name
        if termux_bin.is_file() and (os.access(termux_bin, os.X_OK) or os.name == "nt"):
            return termux_bin.resolve()

    # 4. Standard user local binary paths
    for name in ("sd-cli", "sd-cli.exe"):
        local_bin = Path(os.path.expanduser(f"~/.local/bin/{name}"))
        if local_bin.is_file() and (os.access(local_bin, os.X_OK) or os.name == "nt"):
            return local_bin.resolve()

    return None


def provision_engine(force: bool = False) -> Path:
    """Download, update submodules, and compile stable-diffusion.cpp into ~/.cache/termux-diffusion/bin/sd-cli."""
    existing = locate_sd_cli()
    if existing and not force:
        logger.info("Found existing native engine binary at: %s", existing)
        return existing

    print("[termux-diffusion] Initializing native ARM64 Bionic engine provisioning...")

    # Step 1: Ensure required system packages
    if is_android_termux() and shutil.which("pkg"):
        print("[termux-diffusion] Checking build toolchains (git, cmake, clang, termux-api)...")
        try:
            subprocess.run(
                ["pkg", "install", "-y", "git", "cmake", "clang", "termux-api", "wget"],
                capture_output=False,
                check=False,
                timeout=180.0
            )
        except Exception as exc:
            logger.warning("pkg install invocation warning: %s", exc)

    # Verify toolchain existence
    has_compiler = bool(shutil.which("clang") or shutil.which("gcc") or shutil.which("clang++"))
    has_cmake = bool(shutil.which("cmake"))
    has_git = bool(shutil.which("git"))

    if not (has_compiler and has_cmake and has_git):
        missing = []
        if not has_compiler:
            missing.append("clang / gcc")
        if not has_cmake:
            missing.append("cmake")
        if not has_git:
            missing.append("git")
        raise ProvisioningError(
            f"Missing required build tools: {', '.join(missing)}. "
            f"Please run 'pkg install -y clang cmake git termux-api' before provisioning."
        )

    # Step 2: Set up build directory
    build_root = get_default_cache_dir() / "build_src"
    build_root.mkdir(parents=True, exist_ok=True)
    repo_dir = build_root / "stable-diffusion.cpp"

    if not repo_dir.exists():
        print(f"[termux-diffusion] Cloning {SD_CPP_REPO}...")
        try:
            res = subprocess.run(
                ["git", "clone", SD_CPP_REPO, str(repo_dir)],
                capture_output=True,
                text=True,
                timeout=30.0
            )
            if res.returncode != 0:
                raise ProvisioningError(f"Failed cloning stable-diffusion.cpp repository: {res.stderr.strip()}")
        except subprocess.TimeoutExpired as exc:
            raise ProvisioningError(
                "Network timeout (30s) while cloning stable-diffusion.cpp. "
                "Please check your internet connection or install sd-cli manually."
            ) from exc

    # Step 3: Crucial Submodule Update (Ensures ggml is present)
    print("[termux-diffusion] Synchronizing tensor submodules (ggml)...")
    try:
        sub_res = subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive"],
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
            timeout=45.0,
            check=False
        )
        if sub_res.returncode != 0:
            logger.warning("Git submodule sync note: %s", sub_res.stderr)
    except subprocess.TimeoutExpired:
        logger.warning("Submodule sync timed out after 45s. Proceeding with existing source files.")

    # Step 4: CMake & Compilation - Use hardware-detected optimal flags
    build_dir = repo_dir / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    from .hardware import detect_hardware_profile, format_hardware_report
    hw_profile = detect_hardware_profile()
    print(f"[termux-diffusion] Detected SoC: {hw_profile.soc_name}, GPU: {hw_profile.gpu_name}")
    print(f"[termux-diffusion] Vulkan: {'Available' if hw_profile.vulkan_available else 'Not Found'}, "
          f"OpenCL: {'Available' if hw_profile.opencl_available else 'Not Found'}")
    print(f"[termux-diffusion] CPU Extensions: DotProd={'Y' if hw_profile.has_dotprod else 'N'} "
          f"FP16={'Y' if hw_profile.has_fp16 else 'N'} I8MM={'Y' if hw_profile.has_i8mm else 'N'}")
    print(f"[termux-diffusion] Recommended backend: {hw_profile.recommended_backend.value}")

    print("[termux-diffusion] Configuring CMake build with device-optimized flags...")
    cmake_cmd = [
        "cmake", "..",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DSD_BUILD_EXAMPLES=ON",
        "-DGGML_OPENMP=OFF",
    ]
    # Append hardware-specific flags (Vulkan, DotProd, FP16, etc.)
    cmake_cmd.extend(hw_profile.cmake_extra_flags)
    cmake_res = subprocess.run(
        cmake_cmd,
        cwd=str(build_dir),
        capture_output=True,
        text=True
    )
    if cmake_res.returncode != 0:
        raise ProvisioningError(f"CMake configuration failed: {cmake_res.stderr.strip()}")

    mem_info = get_memory_info()
    cpu_cores = os.cpu_count() or 2
    if mem_info.total_mb < 4096:
        make_jobs = 1  # RAM < 4GB: Single job to prevent Clang compiler OOM/LMK
    elif mem_info.total_mb < 8192:
        make_jobs = min(2, cpu_cores)  # RAM 4-8GB: 2 parallel jobs
    else:
        make_jobs = min(4, cpu_cores)  # RAM 8GB+: Up to 4 parallel jobs

    print(f"[termux-diffusion] Compiling native Bionic binary with clang (make -j{make_jobs})...")
    make_res = subprocess.run(
        ["make", f"-j{make_jobs}"],
        cwd=str(build_dir),
        capture_output=True,
        text=True
    )
    if make_res.returncode != 0:
        err_tail = "\n".join(make_res.stderr.strip().splitlines()[-10:]) if make_res.stderr else "No compiler error output"
        raise ProvisioningError(
            f"Compilation failed with exit code {make_res.returncode}.\n"
            f"Compiler Error:\n{err_tail}\n"
            "Please run 'termux-diffusion doctor' to diagnose missing headers."
        )

    # Locate compiled binary
    compiled_bin = None
    for candidate in (build_dir / "bin" / "sd-cli", build_dir / "bin" / "sd", build_dir / "sd-cli", build_dir / "sd"):
        if candidate.is_file():
            compiled_bin = candidate
            break

    if not compiled_bin:
        raise ProvisioningError("Could not locate compiled binary in build directory.")

    # Install into cache bin directory using atomic rename
    target_bin = get_engine_bin_dir() / "sd-cli"
    temp_bin = target_bin.with_name(f"sd-cli.{os.getpid()}.part")
    shutil.copy2(compiled_bin, temp_bin)
    temp_bin.chmod(0o755)
    os.replace(temp_bin, target_bin)

    print(f"[termux-diffusion] Engine provisioned successfully at: {target_bin}")
    return target_bin.resolve()


def run_doctor() -> bool:
    """Run comprehensive 8-tier pre-flight diagnostic checks for Samsung Galaxy Termux setup."""
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
    engine = locate_sd_cli()
    print(f"6. Native C++ Engine (sd-cli): {str(engine) + ' [OK]' if engine else 'Not Provisioned [FAIL] (Run termux-diffusion-install)'}")
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
    from .hardware import detect_hardware_profile, format_hardware_report
    hw = detect_hardware_profile()
    print(f"8. Hardware Acceleration Profile:")
    print(f"   SoC: {hw.soc_name}, GPU Architecture: {hw.gpu_name}")
    print(f"   GPU Vulkan: {'Available [OK]' if hw.vulkan_available else 'Not Found [WARN]'}")
    if hw.vulkan_driver:
        print(f"     -> Vulkan Driver: {hw.vulkan_driver.library_path}")
    print(f"   GPU OpenCL: {'Available [OK]' if hw.opencl_available else 'Not Found [WARN]'}")
    if hw.opencl_driver:
        print(f"     -> OpenCL Driver: {hw.opencl_driver.library_path}")
    if hw.npu_profile and hw.npu_profile.available:
        print(f"   NPU / TPU Hardware: Detected [INFO]")
        print(f"     -> Architecture: {hw.npu_profile.dsp_architecture} ({hw.npu_profile.tops_rating} TOPS)")
        print(f"     -> Driver: {hw.npu_profile.driver_library}")
        print(f"     -> Runtime: Native QNN C++ execution scheduled for v2.0")
    else:
        print(f"   NPU / TPU Hardware: Not Detected [INFO] (GPU Vulkan & CPU NEON Active)")
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
        print("Some diagnostics need attention. Run 'termux-diffusion-install' to resolve.")
    print("=" * 65)
    return all_passed
