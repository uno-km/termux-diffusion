"""Hardware acceleration detection, Vulkan/OpenCL/NPU/TPU probing, and CMake flag generation.

This module probes the Android device for available GPU, NPU, TPU, and CPU compute backends
by checking for the actual existence of system driver libraries on disk.
"""

import ctypes
import logging
import os
import platform
import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .exceptions import PlatformNotSupportedError
from .npu import NPUProfile, NPUVendor, detect_npu_capabilities, get_optimal_heterogeneous_pipeline

logger = logging.getLogger("termux_diffusion.hardware")


class ComputeBackend(Enum):
    """Available hardware compute backends, ordered by expected throughput."""
    CPU_NEON = "cpu"
    OPENCL = "opencl"
    VULKAN = "vulkan"
    NPU = "npu"
    TPU = "tpu"


@dataclass
class GPUDriverInfo:
    """Detected GPU driver metadata from the device."""
    name: str = "Unknown"
    vendor: str = "Unknown"
    api: str = "Unknown"
    library_path: str = ""
    version: str = ""
    usable: bool = False


@dataclass
class HardwareProfile:
    """Complete hardware capability profile for the current device."""
    cpu_arch: str = ""
    cpu_cores: int = 0
    cpu_features: List[str] = field(default_factory=list)
    has_dotprod: bool = False
    has_fp16: bool = False
    has_i8mm: bool = False
    has_sve: bool = False
    vulkan_available: bool = False
    vulkan_driver: Optional[GPUDriverInfo] = None
    opencl_available: bool = False
    opencl_driver: Optional[GPUDriverInfo] = None
    npu_profile: Optional[NPUProfile] = None
    soc_name: str = "Unknown"
    gpu_name: str = "Unknown"
    recommended_backend: ComputeBackend = ComputeBackend.CPU_NEON
    recommended_ngl: int = 0
    cmake_extra_flags: List[str] = field(default_factory=list)


# ------------------------------------------------------------------------------
# 1. CPU & GPU Feature Detection
# ------------------------------------------------------------------------------

# [중요] Vulkan ICD 탐색 순서: Android Bionic ICD 최우선.
# Termux Mesa($PREFIX/lib/libvulkan.so)를 시스템 ICD보다 먼저 로드하면
# Bionic linker 이중 dispatch 테이블 충돌로 SIGABRT 가 발생합니다.
# ameva-runtime 의 ICD 탐색 정책과 동일하게 유지합니다.
_VULKAN_LIB_SEARCH_PATHS = [
    "/system/lib64/libvulkan.so",   # Android Bionic ICD (최우선 — A35/S25/S21 모두 존재)
    "/system/lib/libvulkan.so",
    "/vendor/lib64/libvulkan.so",
    "/vendor/lib/libvulkan.so",
    # Termux Mesa: 시스템 ICD 가 없는 순수 Linux/PRoot 환경 전용 fallback
    os.path.join(os.environ.get("PREFIX", "/data/data/com.termux/files/usr"), "lib64", "libvulkan.so"),
    os.path.join(os.environ.get("PREFIX", "/data/data/com.termux/files/usr"), "lib", "libvulkan.so"),
]

_OPENCL_LIB_SEARCH_PATHS = [
    "/vendor/lib64/libOpenCL.so",
    "/system/lib64/libOpenCL.so",
    "/system/vendor/lib64/libOpenCL.so",
    "/vendor/lib/libOpenCL.so",
    "/system/lib/libOpenCL.so",
    "/vendor/lib64/egl/libGLES_mali.so",
    "/system/vendor/lib64/egl/libGLES_mali.so",
]


def _find_vulkan_driver_path() -> Optional[str]:
    """Find the first genuinely accessible Vulkan driver library on the filesystem."""
    for p in _VULKAN_LIB_SEARCH_PATHS:
        p_obj = Path(p)
        try:
            if p_obj.is_file() and p_obj.stat().st_size >= 1024:
                return str(p_obj.resolve())
        except (OSError, PermissionError):
            continue
    return None


def _read_cpuinfo_features() -> List[str]:
    """Parse /proc/cpuinfo to extract ARM CPU feature flags."""
    cpuinfo_path = Path("/proc/cpuinfo")
    if not cpuinfo_path.exists():
        return []

    try:
        text = cpuinfo_path.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            if line.lower().startswith("features"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    return parts[1].strip().split()
        return []
    except Exception as e:
        logger.debug("Could not read /proc/cpuinfo: %s", e)
        return []


from .platform import is_android_termux


def _detect_soc_name() -> str:
    """Identify the SoC model from Android system properties."""
    if not is_android_termux():
        return "Unknown"
    prop_keys = [
        "ro.soc.model",
        "ro.chipname",
        "ro.hardware.chipname",
        "ro.board.platform",
        "ro.hardware",
        "ro.product.board",
    ]
    for key in prop_keys:
        try:
            result = subprocess.run(
                ["getprop", key],
                capture_output=True,
                text=True,
                timeout=2.0,
            )
            val = result.stdout.strip()
            if val and val != "unknown":
                return val
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    return "Unknown"


def _detect_device_model() -> str:
    """Identify Android device model for hardware profile matching."""
    if not is_android_termux():
        return "Unknown"
    for prop in ["ro.product.model", "ro.product.device", "ro.build.product"]:
        try:
            result = subprocess.run(
                ["getprop", prop],
                capture_output=True,
                text=True,
                timeout=2.0,
            )
            val = result.stdout.strip()
            if val and val != "unknown":
                return val
        except Exception:
            continue
    return "Unknown"


def _detect_gpu_name() -> str:
    """Identify the GPU model from Android properties and hardware nodes."""
    if not is_android_termux():
        return "Unknown"
    # 1. Check Adreno kgsl sysfs node
    kgsl_model = Path("/sys/class/kgsl/kgsl-3d0/gpu_model")
    if kgsl_model.exists():
        try:
            val = kgsl_model.read_text(encoding="utf-8").strip()
            if val:
                return f"Adreno ({val})"
        except PermissionError as _perm_err:
            logger.warning("[hardware] kgsl gpu_model read PermissionError: %s", _perm_err)
        except OSError as _os_err:
            logger.warning("[hardware] kgsl gpu_model read OSError: %s", _os_err)
        # 예상 밖 예외는 재발생

    # 2. Check Android system properties
    for prop in ["ro.hardware.vulkan", "ro.hardware.egl", "ro.board.platform"]:
        try:
            result = subprocess.run(
                ["getprop", prop],
                capture_output=True,
                text=True,
                timeout=2.0,
            )
            val = result.stdout.strip()
            if val and val != "unknown":
                if "adreno" in val.lower():
                    return f"Qualcomm Adreno ({val})"
                if "mali" in val.lower():
                    return f"ARM Mali ({val})"
                return val.capitalize()
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    return "Unknown"




def _probe_vulkan_driver() -> Optional[GPUDriverInfo]:
    """Probe for a usable Vulkan driver via ameva-runtime SSOT."""
    try:
        from ameva_runtime import vulkan as avr
        report = avr.Doctor().run_self_test(verbose=False)
        if report.overall_success or report.recommended_backend in ("vulkan", "vulkan_driver_only") or getattr(report, "passed_stages", 0) >= 7:
            return GPUDriverInfo(
                name=f"Vulkan Driver ({report.device_name})",
                vendor=report.device_name,
                api=f"Vulkan {getattr(report, 'driver_version', '1.3')}",
                library_path=getattr(report, "loader_path", "") or _find_vulkan_driver_path() or "/system/lib64/libvulkan.so",
                version=getattr(report, "driver_version", ""),
                usable=True,
            )
    except Exception as e:
        logger.debug("[termux-diffusion] ameva-runtime probe exception: %s", e)

    # 안전 폴백: 시스템 기본 Bionic 경로 검사
    detected_path = _find_vulkan_driver_path()
    if detected_path and Path(detected_path).is_file():
        gpu_name = _detect_gpu_name()
        return GPUDriverInfo(
            name=f"Vulkan Driver ({gpu_name})",
            vendor=gpu_name,
            api="Vulkan",
            library_path=detected_path,
            version="",
            usable=True,
        )
    return None


def _probe_opencl_driver() -> Optional[GPUDriverInfo]:
    """Probe for a usable OpenCL driver by checking library paths."""
    for lib_path in _OPENCL_LIB_SEARCH_PATHS:
        p = Path(lib_path)
        if p.is_file():
            try:
                size = p.stat().st_size
                if size < 1024:
                    continue
                gpu_name = _detect_gpu_name()
                return GPUDriverInfo(
                    name=f"OpenCL Driver ({gpu_name})",
                    vendor=gpu_name,
                    api="OpenCL",
                    library_path=lib_path,
                    version="",
                    usable=True,
                )
            except PermissionError as pe:
                logger.warning(
                    "OpenCL driver found at '%s' but access was denied (SELinux permission): %s",
                    lib_path,
                    pe,
                )
                continue
            except OSError as oe:
                logger.debug("OpenCL driver stat note on '%s': %s", lib_path, oe)
                continue
    return None


# ------------------------------------------------------------------------------
# 2. Main Hardware Profiler
# ------------------------------------------------------------------------------

def detect_hardware_profile() -> HardwareProfile:
    """Run comprehensive hardware detection across CPU, GPU, NPU, and TPU."""
    profile = HardwareProfile()
    
    # CPU Architecture
    profile.cpu_arch = platform.machine().lower()
    profile.cpu_cores = os.cpu_count() or 1
    
    # ARM CPU ISA Features
    features = _read_cpuinfo_features()
    profile.cpu_features = features
    profile.has_dotprod = "asimddp" in features
    profile.has_fp16 = "fphp" in features or "asimdhp" in features
    profile.has_i8mm = "i8mm" in features
    profile.has_sve = "sve" in features or "sve2" in features
    
    # SoC and GPU identification
    profile.soc_name = _detect_soc_name()
    profile.gpu_name = _detect_gpu_name()
    
    # Vulkan & OpenCL driver probe
    vulkan_info = _probe_vulkan_driver()
    if vulkan_info and vulkan_info.usable:
        profile.vulkan_available = True
        profile.vulkan_driver = vulkan_info
    
    opencl_info = _probe_opencl_driver()
    if opencl_info and opencl_info.usable:
        profile.opencl_available = True
        profile.opencl_driver = opencl_info

    # NPU / TPU driver probe
    npu_info = detect_npu_capabilities()
    profile.npu_profile = npu_info
    
    # Recommend optimal backend: Vulkan > OpenCL > CPU NEON
    if profile.vulkan_available:
        profile.recommended_backend = ComputeBackend.VULKAN
        profile.recommended_ngl = 99
    elif profile.opencl_available:
        profile.recommended_backend = ComputeBackend.OPENCL
        profile.recommended_ngl = 32
    else:
        profile.recommended_backend = ComputeBackend.CPU_NEON
        profile.recommended_ngl = 0
    
    # Generate CMake flags
    profile.cmake_extra_flags = _build_cmake_flags(profile)
    
    return profile


def _build_cmake_flags(profile: HardwareProfile, backend: Optional[str] = None) -> List[str]:
    """Generate optimal CMake flags for ARM64 Android Bionic."""
    flags = []
    prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
    
    target_backend = backend.lower().strip() if backend else "auto"
    
    if target_backend == "cpu":
        flags.append("-DSD_VULKAN=OFF")
        flags.append("-DSD_OPENCL=OFF")
    elif (target_backend in ("auto", "vulkan")) and profile.vulkan_available and profile.vulkan_driver:
        flags.append("-DSD_VULKAN=ON")
        flags.append(f"-DVulkan_LIBRARY={profile.vulkan_driver.library_path}")
        flags.append(f"-DVulkan_INCLUDE_DIR={prefix}/include")
        flags.append("-DGGML_VULKAN_COOPMAT_GLSLC_SUPPORT=OFF")
        flags.append("-DGGML_VULKAN_COOPMAT2_GLSLC_SUPPORT=OFF")
        flags.append("-DGGML_VULKAN_COOPMAT2_DECODE_VECTOR_GLSLC_SUPPORT=OFF")
        flags.append("-DGGML_VULKAN_BFLOAT16_GLSLC_SUPPORT=OFF")
        flags.append("-DCMAKE_EXE_LINKER_FLAGS=-L/system/lib64 -Wl,-rpath,/system/lib64 -L/vendor/lib64 -Wl,-rpath,/vendor/lib64")
    elif (target_backend in ("auto", "opencl")) and profile.opencl_available and profile.opencl_driver:
        flags.append("-DSD_OPENCL=ON")
        flags.append(f"-DOpenCL_LIBRARY={profile.opencl_driver.library_path}")
        flags.append(f"-DOpenCL_INCLUDE_DIR={prefix}/include")
        flags.append("-DCMAKE_EXE_LINKER_FLAGS=-L/vendor/lib64 -Wl,-rpath,/vendor/lib64 -L/system/lib64 -Wl,-rpath,/system/lib64")
    else:
        flags.append("-DSD_VULKAN=OFF")
        flags.append("-DSD_OPENCL=OFF")
    
    # CPU ISA optimization flags
    march_parts = ["armv8-a"]
    if profile.cpu_arch in ("aarch64", "arm64"):
        march_parts = ["armv8.2-a"]
        if profile.has_dotprod:
            march_parts.append("dotprod")
        if profile.has_fp16:
            march_parts.append("fp16")
        if profile.has_i8mm:
            march_parts.append("i8mm")
    
    if len(march_parts) > 1:
        march_str = "+".join(march_parts)
        flags.append(f"-DCMAKE_C_FLAGS=-O2 -march={march_str} -D_GNU_SOURCE")
        flags.append(f"-DCMAKE_CXX_FLAGS=-O2 -march={march_str} -D_GNU_SOURCE -Wno-deprecated-literal-operator")
    else:
        flags.append("-DCMAKE_C_FLAGS=-O2 -D_GNU_SOURCE")
        flags.append("-DCMAKE_CXX_FLAGS=-O2 -D_GNU_SOURCE -Wno-deprecated-literal-operator")
    
    return flags


# ------------------------------------------------------------------------------
# 3. Device Selection for generate()
# ------------------------------------------------------------------------------

def resolve_device_backend(requested_device: str) -> Tuple[str, int]:
    """Resolve the user's device= argument to an actual backend and ngl count."""
    profile = detect_hardware_profile()
    req = requested_device.lower().strip()
    
    if req == "auto":
        backend = profile.recommended_backend
        ngl = profile.recommended_ngl
        logger.info(
            "Auto-detected optimal backend: %s (SoC: %s, GPU: %s)",
            backend.value, profile.soc_name, profile.gpu_name
        )
        return backend.value, ngl
    
    if req in ("npu", "tpu"):
        npu_desc = (
            f"{profile.npu_profile.chipset_name} / {profile.npu_profile.dsp_architecture}"
            if (profile.npu_profile and profile.npu_profile.available)
            else "Hardware not detected"
        )
        raise PlatformNotSupportedError(
            f"Native NPU/TPU acceleration ({npu_desc}) requires Qualcomm QNN / LiteRT C++ Graph Runtime (scheduled for v2.0 roadmap). "
            f"Currently, full hardware acceleration is supported via Vulkan GPU (device='vulkan') and ARM NEON (device='cpu'). "
            f"Please use device='vulkan' or device='auto'."
        )

    if req in ("vulkan", "gpu"):
        if profile.vulkan_available:
            return "vulkan", 99
        raise PlatformNotSupportedError(
            "Vulkan GPU acceleration was explicitly requested (device='vulkan' / 'gpu'), "
            "but no accessible Vulkan driver (.so) was found on this system. "
            "Execution halted strictly without silent fallback to prevent unexpected CPU execution."
        )
    
    if req == "opencl":
        if profile.opencl_available:
            return "opencl", 32
        raise PlatformNotSupportedError(
            "OpenCL acceleration was explicitly requested (device='opencl'), "
            "but no accessible OpenCL driver (.so) was found on this system. "
            "Execution halted strictly without silent fallback to prevent unexpected CPU execution."
        )
    
    if req == "cpu":
        return "cpu", 0

    raise ValueError(f"Unknown computing device '{requested_device}'. Supported: 'auto', 'cpu', 'vulkan', 'opencl'.")


def get_sd_cli_gpu_args(device: str, ngl: int) -> List[str]:
    """Build the sd-cli command-line arguments for GPU/NPU offloading."""
    args: List[str] = []
    if device == "cpu":
        args.append("--offload-to-cpu")
    return args


def format_hardware_report(profile: HardwareProfile) -> str:
    """Format a human-readable hardware capability report for doctor/diagnostics."""
    lines = [
        "=== Hardware Acceleration Profile ===",
        f"SoC: {profile.soc_name}",
        f"GPU Architecture: {profile.gpu_name}",
        f"CPU Architecture: {profile.cpu_arch} ({profile.cpu_cores} cores)",
        f"ARM SIMD Extensions: DotProd={'[OK]' if profile.has_dotprod else '[FAIL]'} "
        f"FP16={'[OK]' if profile.has_fp16 else '[FAIL]'} "
        f"I8MM={'[OK]' if profile.has_i8mm else '[FAIL]'} "
        f"SVE={'[OK]' if profile.has_sve else '[FAIL]'}",
        f"GPU Vulkan: {'Available [OK]' if profile.vulkan_available else 'Not Found [WARN]'}",
    ]
    if profile.vulkan_driver:
        lines.append(f"  -> Vulkan Lib: {profile.vulkan_driver.library_path}")
    lines.append(f"GPU OpenCL: {'Available [OK]' if profile.opencl_available else 'Not Found [WARN]'}")
    if profile.opencl_driver:
        lines.append(f"  -> OpenCL Lib: {profile.opencl_driver.library_path}")
    
    if profile.npu_profile and profile.npu_profile.available:
        lines.append(f"NPU / TPU Hardware: Detected [INFO] ({profile.npu_profile.dsp_architecture})")
        lines.append(f"  -> Peak Hardware Spec: {profile.npu_profile.tops_rating} TOPS")
        lines.append(f"  -> Driver Library: {profile.npu_profile.driver_library}")
        lines.append(f"  -> Runtime Status: Native QNN C++ execution scheduled for v2.0 (Active: Vulkan GPU & ARM NEON)")
    else:
        lines.append("NPU / TPU Hardware: Not Detected (CPU/GPU pipeline active)")
        
    lines.append(f"Recommended Compute Backend: {profile.recommended_backend.value}")
    lines.append(f"Recommended GPU/NPU Offload Layers: {profile.recommended_ngl}")
    if profile.cmake_extra_flags:
        lines.append(f"CMake Build Flags: {' '.join(profile.cmake_extra_flags)}")
    lines.append("=" * 40)
    return "\n".join(lines)


# ------------------------------------------------------------------------------
# 4. Profile Gating Manager (Runtime Model/Preset Safety)
# ------------------------------------------------------------------------------

import json

@dataclass
class ProfileGatingManager:
    """Manages runtime matching against validated-vulkan-profiles.json for safe device/model execution."""
    profiles: List[Dict] = field(default_factory=list)

    @classmethod
    def load_from_json(cls, json_path: Optional[Path] = None) -> "ProfileGatingManager":
        if json_path is None:
            json_path = Path(__file__).parent / "data" / "validated-vulkan-profiles.json"
        if json_path.is_file():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                return cls(profiles=data.get("profiles", []))
            except Exception as e:
                logger.warning("Failed to load validated-vulkan-profiles.json: %s", e)
        return cls(profiles=[])

    def find_matching_profile(self, model_name: str, soc_name: str = "", gpu_name: str = "") -> Optional[Dict]:
        model_clean = model_name.strip().upper()
        soc_clean = soc_name.strip().upper()
        gpu_clean = gpu_name.strip().upper()

        for prof in self.profiles:
            target_model = prof.get("device_model", "").strip().upper()
            if target_model and (target_model == model_clean or target_model in model_clean or model_clean in target_model):
                return prof
            aliases = [a.strip().upper() for a in prof.get("device_aliases", [])]
            if any(a == model_clean or a in model_clean for a in aliases):
                return prof

        # Fallback matching by SoC / GPU
        for prof in self.profiles:
            prof_soc = prof.get("soc", "").strip().upper()
            prof_gpu = prof.get("gpu", "").strip().upper()
            if prof_soc and soc_clean and (prof_soc in soc_clean or soc_clean in prof_soc):
                return prof
            if prof_gpu and gpu_clean and (prof_gpu in gpu_clean or gpu_clean in prof_gpu):
                return prof
        return None

    def validate_execution(self, preset_or_model: str, device: str) -> Tuple[bool, Optional[str]]:
        """Validate if the requested model/preset and device backend are safe for current hardware."""
        device_clean = device.lower().strip()
        if device_clean not in ("vulkan", "gpu"):
            return True, None

        dev_model = _detect_device_model()
        soc_name = _detect_soc_name()
        gpu_name = _detect_gpu_name()
        matched = self.find_matching_profile(dev_model, soc_name, gpu_name)
        if not matched:
            return True, None

        # 1. Check blocked list
        blocked = matched.get("blocked", [])
        preset_clean = preset_or_model.lower().strip()
        for blk in blocked:
            fam = blk.get("model_family", "").lower()
            backend = blk.get("backend", "").lower()
            if backend in (device_clean, "all") and fam in preset_clean:
                reason = blk.get("reason", "Incompatible hardware backend configuration")
                return False, (
                    f"Model '{preset_or_model}' is blocked on device '{matched.get('device_model')}' "
                    f"under backend '{device_clean}' due to: {reason}."
                )

        # 2. Check preset gating if preset exists in profile
        presets = matched.get("presets", {})
        if preset_clean in presets:
            p_info = presets[preset_clean]
            if p_info.get("status") == "pending_device_validation" and not p_info.get("auto_activation", True):
                return False, (
                    f"Preset '{preset_clean}' is currently pending device validation on '{matched.get('device_model')}' "
                    f"and auto_activation is disabled."
                )

        return True, None


_gating_manager: Optional[ProfileGatingManager] = None


def get_profile_gating_manager() -> ProfileGatingManager:
    """Get singleton instance of ProfileGatingManager."""
    global _gating_manager
    if _gating_manager is None:
        _gating_manager = ProfileGatingManager.load_from_json()
    return _gating_manager

