"""Automated C++ core engine provisioning, binary locator, build healer, and doctor diagnostics."""

import logging
import io
import os
import shutil
import subprocess
import sys

from pathlib import Path
from typing import Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, io.UnsupportedOperation) as _out_err:
        _ = _out_err
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, io.UnsupportedOperation) as _err_err:
        _ = _err_err



from .exceptions import ProvisioningError
from .platform import (
    TERMUX_PREFIX,
    check_memory_safety,
    get_default_cache_dir,
    get_memory_info,
    is_android_termux,
    is_arm64,
)

from .engine import (
    get_engine_bin_dir,
    get_engine_lib_dir,
    get_binary_path,
    locate_sd_cli,
)

from ._version import __version__

logger = logging.getLogger("termux_diffusion.installer")

SD_CPP_REPO = "https://github.com/leejet/stable-diffusion.cpp"

TERMUX_DIFFUSION_RELEASE_LATEST = "https://github.com/uno-km/termux-diffusion/releases/latest/download"


def get_prebuilt_base_url() -> str:
    """Resolve dynamic base URL for prebuilt binary assets."""
    if custom := os.environ.get("TERMUX_DIFFUSION_RELEASE_BASE") or os.environ.get("AMEVA_RELEASE_BASE"):
        return custom.rstrip("/")
    if custom_tag := os.environ.get("TERMUX_DIFFUSION_RELEASE_TAG") or os.environ.get("AMEVA_RELEASE_TAG"):
        tag = custom_tag if custom_tag.startswith("v") else f"v{custom_tag}"
        return f"https://github.com/uno-km/termux-diffusion/releases/download/{tag}"
    return f"https://github.com/uno-km/termux-diffusion/releases/download/v{__version__}"


PREBUILT_BASE_URL = get_prebuilt_base_url()


def get_candidate_prebuilt_urls(filename: str = "sd-cli-cpu-android-arm64.tar.gz") -> List[str]:
    """Resolve prioritized candidate URLs for downloading prebuilt engine packages."""
    urls: List[str] = []
    if custom_base := os.environ.get("TERMUX_DIFFUSION_RELEASE_BASE") or os.environ.get("AMEVA_RELEASE_BASE"):
        urls.append(f"{custom_base.rstrip('/')}/{filename}")
    # Tier 2: GitHub Releases latest canonical endpoint (Zero-Hardcoding SSOT)
    urls.append(f"{TERMUX_DIFFUSION_RELEASE_LATEST}/{filename}")

    # Tier 3: Installed package dynamic version matching
    urls.append(f"https://github.com/uno-km/termux-diffusion/releases/download/v{__version__}/{filename}")
    return urls


import uuid
from .locking import InstallLock
from .downloader import atomic_download_file
from .selftest import run_binary_self_test


def activate_binary(bin_dir: Path, target_name: str) -> Path:
    """Atomically activate target_name symlink to sd-cli using os.replace in same directory."""
    allowed = {
        "sd-cli-cpu",
        "sd-cli-source-cpu",
        "sd-cli",
        "sd-cli-vulkan",
    }
    if target_name not in allowed:
        raise ValueError(f"Unauthorized activation target: {target_name}")

    target = bin_dir / target_name
    active = bin_dir / "sd-cli"
    temporary = bin_dir / f".sd-cli.{uuid.uuid4().hex}.tmp"

    if not target.is_file() or target.is_symlink():
        raise RuntimeError(f"Activation target {target_name} is not a valid regular file")

    try:
        try:
            os.symlink(target_name, temporary)
            os.replace(temporary, active)
        except (NotImplementedError, OSError):
            # symlink 미지원 OS(일부 Windows, FAT32 등) — copy2 fallback.
            logger.warning(
                "[installer] symlink not supported; using copy2 fallback for %s -> %s",
                target_name, active,
            )
            shutil.copy2(target, active)
        return active
    finally:
        if temporary.exists() or temporary.is_symlink():
            try:
                temporary.unlink()
            except (PermissionError, OSError) as _tmp_err:
                logger.warning(
                    "[installer] Failed to clean up temporary symlink %s: %s. "
                    "Manual cleanup may be required.",
                    temporary, _tmp_err,
                )




def fetch_prebuilt_binary(install_mode: str = "prebuilt-first") -> Optional[Path]:
    """Try acquiring prebuilt Bionic ARM64 CPU baseline binary with integrity verification and self-test."""
    if not (is_android_termux() and is_arm64()):
        return None

    bin_dir = get_engine_bin_dir()
    lock_file = get_default_cache_dir() / "install.lock"

    with InstallLock(lock_file, timeout_sec=5.0):
        if install_mode == "source-only":
            return None

        cpu_bin = bin_dir / "sd-cli-cpu"
        lib_dir = get_engine_lib_dir()
        omp_so = lib_dir / "libomp.so"

        print("[termux-diffusion] Attempting Prebuilt CPU Baseline Engine installation...")
        try:
            # 1. Ensure OpenMP companion library (libomp.so)
            if not omp_so.is_file() or omp_so.stat().st_size < 100000:
                omp_urls = get_candidate_prebuilt_urls("libomp-android-arm64.so")
                print("[termux-diffusion] Provisioning OpenMP parallel runtime (libomp.so)...")
                for o_url in omp_urls:
                    try:
                        atomic_download_file(o_url, omp_so)
                        if omp_so.is_file() and omp_so.stat().st_size > 100000:
                            break
                    except Exception as o_err:
                        logger.debug("OpenMP download candidate failed from %s: %s", o_url, o_err)

            if omp_so.is_file():
                try:
                    omp_so.chmod(0o755)
                except OSError:
                    pass

            # 2. Ensure sd-cli-cpu binary
            if not cpu_bin.is_file():
                candidate_urls = get_candidate_prebuilt_urls("sd-cli-cpu-android-arm64.tar.gz")
                staging_dir = get_default_cache_dir() / ".staging-diffusion-cpu"
                staging_dir.mkdir(parents=True, exist_ok=True)
                tar_dest = staging_dir / "cpu-prebuilt.tar.gz"
                downloaded = False
                for pkg_url in candidate_urls:
                    try:
                        print(f"[termux-diffusion] Downloading CPU baseline binary from: {pkg_url} ...")
                        atomic_download_file(pkg_url, tar_dest)
                        downloaded = True
                        break
                    except Exception as dl_err:
                        logger.debug("CPU prebuilt download candidate failed from %s: %s", pkg_url, dl_err)

                if downloaded and tar_dest.is_file():
                    import tarfile
                    with tarfile.open(tar_dest, "r:gz") as tar:
                        for member in tar.getmembers():
                            member_path = os.path.realpath(os.path.join(staging_dir, member.name))
                            if not member_path.startswith(os.path.realpath(staging_dir)):
                                raise ProvisioningError(
                                    f"[termux-diffusion] E_TAR_PATH_ESCAPE: tarball 내 경로 탈출 시도가 감지되어 추출을 중단했습니다: {member.name}"
                                )
                        tar.extractall(path=staging_dir)
                    tar_dest.unlink(missing_ok=True)

                    for cand in staging_dir.rglob("sd-cli*"):
                        if cand.is_file():
                            shutil.copy2(cand, cpu_bin)
                            cpu_bin.chmod(0o755)
                            break

                    shutil.rmtree(staging_dir, ignore_errors=True)

            if cpu_bin.is_file() and run_binary_self_test(cpu_bin, expected_backend="cpu").stage1_load_passed:
                active = activate_binary(bin_dir, "sd-cli-cpu")
                print("[termux-diffusion] Fast-Track: Prebuilt CPU Baseline binary validated and activated.")
                return active
        except ProvisioningError:
            raise
        except Exception as exc:
            logger.debug("CPU prebuilt attempt failed: %s", exc)

    return None


def provision_engine(
    force: bool = False,
    install_mode: str = "prebuilt-first",
    jobs: Optional[int] = None,
    make_jobs: Optional[int] = None,
    backend: str = "cpu"
) -> Path:
    """Download, verify, or compile stable-diffusion.cpp into ~/.cache/termux-diffusion/bin/sd-cli."""
    bin_dir = get_engine_bin_dir()

    # Prebuilt-First Pipeline (Pure CPU Baseline Engine)
    if not force or install_mode in ("prebuilt-first", "prebuilt-only"):
        prebuilt = fetch_prebuilt_binary(install_mode=install_mode)
        if prebuilt:
            return prebuilt

    # COMPILATION GATE: Never compile automatically without explicit user opt-in (Zero Silent Fallback)
    allow_source = os.environ.get("TERMUX_DIFFUSION_ALLOW_SOURCE_BUILD") == "1"
    if not allow_source or install_mode == "prebuilt-only":
        raise ProvisioningError(
            "E_PREBUILT_UNAVAILABLE: Precompiled native CPU engine (sd-cli-cpu) is not installed.\n"
            "No precompiled binary was found locally and automated acquisition from GitHub Releases failed.\n"
            "On-device compilation is disabled by default to prevent thermal throttling, excessive battery drain, and memory exhaustion.\n\n"
            "--> ACTION REQUIRED:\n"
            "1. Ensure internet access to GitHub and run: 'termux-diffusion install'\n"
            "2. Or manually download 'sd-cli-cpu-android-arm64.tar.gz' and 'libomp-android-arm64.so' from:\n"
            "     https://github.com/uno-km/termux-diffusion/releases/latest\n"
            "3. If you explicitly want to compile from C++ source on this device, you MUST specify:\n"
            "     export TERMUX_DIFFUSION_ALLOW_SOURCE_BUILD=1\n"
            "   and optionally set compilation cores:\n"
            "     export TERMUX_DIFFUSION_JOBS=<cores>\n",
            code="E_PREBUILT_UNAVAILABLE"
        )

    print("[termux-diffusion] Initializing native ARM64 Bionic CPU engine source compilation...")

    # Step 1: Ensure required system packages
    if is_android_termux() and shutil.which("pkg"):
        print("[termux-diffusion] Checking build toolchains...")
        try:
            subprocess.run(
                [
                    "pkg", "install", "-y",
                    "git", "cmake", "clang", "make", "termux-api", "wget"
                ],
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
        print(f"[termux-diffusion] Cloning {SD_CPP_REPO} (depth=1, recursive)...")
        try:
            res = subprocess.run(
                ["git", "clone", "--depth", "1", "--recursive", SD_CPP_REPO, str(repo_dir)],
                capture_output=True,
                text=True,
                timeout=180.0
            )
            if res.returncode != 0:
                raise ProvisioningError(f"Failed cloning stable-diffusion.cpp repository: {res.stderr.strip()}")
        except subprocess.TimeoutExpired as exc:
            raise ProvisioningError(
                "Network timeout (180s) while cloning stable-diffusion.cpp. "
                "Please check your internet connection or install sd-cli manually."
            ) from exc

    # Step 3: Crucial Submodule Update (Ensures ggml is present)
    print("[termux-diffusion] Synchronizing tensor submodules (ggml)...")
    try:
        sub_res = subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive", "--depth", "1"],
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
            timeout=180.0,
            check=False
        )
        if sub_res.returncode != 0:
            logger.warning("Git submodule sync note: %s", sub_res.stderr)
    except subprocess.TimeoutExpired:
        logger.warning("Submodule sync timed out after 45s. Proceeding with existing source files.")

    # Bionic Healer: Fix Termux libwebp NDK cpu-features dependency
    webp_cmake = repo_dir / "thirdparty" / "libwebp" / "CMakeLists.txt"
    if webp_cmake.is_file():
        try:
            content = webp_cmake.read_text(encoding="utf-8")
            content = content.replace("if(ANDROID)", "if(FALSE)").replace("if (ANDROID)", "if(FALSE)")
            webp_cmake.write_text(content, encoding="utf-8")
            logger.info("Patched libwebp CMakeLists.txt for Termux Bionic compatibility.")
        except Exception as e:
            logger.warning("libwebp patch note: %s", e)



    # Step 4: CMake & Compilation - Use hardware-detected optimal flags
    build_dir = repo_dir / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)
    build_dir.mkdir(parents=True, exist_ok=True)

    from .hardware import detect_hardware_profile, format_hardware_report, _build_cmake_flags
    hw_profile = detect_hardware_profile()
    print(f"[termux-diffusion] Detected SoC: {hw_profile.soc_name}, GPU: {hw_profile.gpu_name}")
    print(f"[termux-diffusion] Vulkan: {'Available' if hw_profile.vulkan_available else 'Not Found'}, "
          f"OpenCL: {'Available' if hw_profile.opencl_available else 'Not Found'}")
    print(f"[termux-diffusion] CPU Extensions: DotProd={'Y' if hw_profile.has_dotprod else 'N'} "
          f"FP16={'Y' if hw_profile.has_fp16 else 'N'} I8MM={'Y' if hw_profile.has_i8mm else 'N'}")
    print("[termux-diffusion] Target build backend: cpu")

    print("[termux-diffusion] Configuring CMake build with device-optimized flags...")
    use_ninja = bool(shutil.which("ninja"))
    cmake_cmd = [
        "cmake", "..",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_SYSTEM_NAME=Linux",
        "-DANDROID=OFF",
        "-DSD_BUILD_EXAMPLES=ON",
        "-DGGML_OPENMP=OFF",
        "-DWEBP_ENABLE_SIMD=OFF",
    ]
    if use_ninja:
        cmake_cmd.extend(["-G", "Ninja"])
        
    # Append hardware-specific flags (DotProd, FP16, etc. with pure CPU backend)
    flags = _build_cmake_flags(hw_profile, backend="cpu")
    cmake_cmd.extend(flags)
    cmake_res = subprocess.run(
        cmake_cmd,
        cwd=str(build_dir),
        capture_output=True,
        text=True
    )
    if cmake_res.returncode != 0:
        raise ProvisioningError(f"CMake configuration failed: {cmake_res.stderr.strip()}")

    # Determine parallel compilation jobs
    env_jobs = os.environ.get("TERMUX_DIFFUSION_MAKE_JOBS") or os.environ.get("TERMUX_DIFFUSION_JOBS")
    if jobs is not None:
        actual_jobs = max(1, int(jobs))
    elif make_jobs is not None:
        actual_jobs = max(1, int(make_jobs))
    elif env_jobs and env_jobs.strip().isdigit():
        actual_jobs = max(1, int(env_jobs.strip()))
    else:
        mem_info = get_memory_info()
        cpu_cores = os.cpu_count() or 2
        total_ram = mem_info.get("effective_total_mb") or mem_info.get("mem_total_mb", 4096)
        if total_ram < 4096:
            actual_jobs = 1  # RAM < 4GB: Single job to prevent Clang compiler OOM/LMK
        elif total_ram < 8192:
            actual_jobs = min(2, cpu_cores)  # RAM 4-8GB: 2 parallel jobs
        else:
            actual_jobs = min(4, cpu_cores)  # RAM 8GB+: Up to 4 parallel jobs

    builder_name = "ninja" if use_ninja else "make"
    print(f"[termux-diffusion] Compiling native Bionic binary with clang ({builder_name} sd-cli -j{actual_jobs})...")
    build_run_cmd = ["ninja", "sd-cli", f"-j{actual_jobs}"] if use_ninja else ["make", "sd-cli", f"-j{actual_jobs}"]
    make_res = subprocess.run(
        build_run_cmd,
        cwd=str(build_dir),
        capture_output=True,
        text=True
    )
    if make_res.returncode != 0:
        full_err = (make_res.stdout or "") + "\n" + (make_res.stderr or "")
        err_tail = "\n".join(full_err.strip().splitlines()[-15:]) if full_err.strip() else "No compiler error output"
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


# Re-export diagnostic utilities from .doctor for backward compatibility
from .doctor import run_doctor

