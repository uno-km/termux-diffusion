"""Neural Processing Unit (NPU) and Tensor Processing Unit (TPU) hardware introspection module.

This module provides hardware probing, driver introspection, and capability reporting
for mobile NPU/TPU chipsets on Android Termux:
- Qualcomm Hexagon Tensor Processor (HTP / QNN NPU)
- Samsung Exynos NPU (ENN / Eden Engine)
- Google Tensor Edge TPU (Pixel Neural Core)
- Android Standard Neural Networks API (NNAPI)

Architectural Note:
In v1.1.x, inference is driven by the native Bionic sd-cli engine using Vulkan GPU
(-ngl 99) and ARM64 NEON CPU acceleration. Direct Qualcomm QNN / Hexagon NPU subgraph
partitioning is the architectural blueprint for the upcoming v2.0 runtime.
"""

import logging
import os
import platform
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("termux_diffusion.npu")


class NPUVendor(Enum):
    """Supported mobile Neural Processing Unit hardware architectures."""
    QUALCOMM_HEXAGON = "qualcomm_hexagon"  # Snapdragon HTP (Hexagon Tensor Processor)
    SAMSUNG_EDEN = "samsung_eden"          # Exynos Dual-NPU (ENN Engine)
    GOOGLE_EDGE_TPU = "google_edge_tpu"    # Google Tensor Edge TPU
    ANDROID_NNAPI = "android_nnapi"        # Android Generic Neural Networks API
    NONE = "none"


@dataclass
class NPUProfile:
    """Introspected mobile NPU/TPU hardware capability profile."""
    available: bool = False
    vendor: NPUVendor = NPUVendor.NONE
    chipset_name: str = "Unknown"
    driver_library: Optional[str] = None
    dsp_architecture: str = "Unknown"
    tops_rating: float = 0.0
    supported_precisions: List[str] = field(default_factory=list)
    delegate_type: str = "CPU_FALLBACK"
    acceleration_status: str = "Not Available"


# ------------------------------------------------------------------------------
# NPU Driver Search Paths on Android Bionic Filesystems
# ------------------------------------------------------------------------------

QUALCOMM_QNN_LIBS = [
    "/vendor/lib64/libQnnHtp.so",
    "/vendor/lib64/libQnnHtpV75.so",
    "/vendor/lib64/libQnnHtpV73.so",
    "/vendor/lib64/libQnnHtpV69.so",
    "/vendor/lib64/libQnnHtpV68.so",
    "/vendor/lib64/libqnn-htp.so",
    "/vendor/lib64/libQnnSystem.so",
    "/vendor/lib64/libQnnCpu.so",
    "/vendor/dsp/cdsp/libqnn_htp.so",
    "/system/vendor/lib64/libQnnHtp.so",
]

SAMSUNG_EDEN_LIBS = [
    "/vendor/lib64/libenn_public_api.so",
    "/vendor/lib64/libeden_nn.so",
    "/vendor/lib64/libenn_engine.so",
    "/system/vendor/lib64/libenn_public_api.so",
]

GOOGLE_EDGETPU_LIBS = [
    "/vendor/lib64/libedgetpu.so",
    "/vendor/lib64/libtflite_edgetpu.so",
    "/vendor/lib64/libgoogle_edgetpu.so",
    "/system/vendor/lib64/libedgetpu.so",
]

ANDROID_NNAPI_LIBS = [
    "/system/lib64/libneuralnetworks.so",
    "/apex/com.android.neuralnetworks/lib64/libneuralnetworks.so",
    "/system/lib/libneuralnetworks.so",
]


def _read_android_prop(key: str) -> str:
    """Query Android system property via getprop."""
    try:
        res = subprocess.run(["getprop", key], capture_output=True, text=True, timeout=2.0)
        val = res.stdout.strip()
        if val and val != "unknown":
            return val
    except Exception:
        pass
    return ""


def _probe_first_existing_lib(paths: List[str]) -> Optional[str]:
    """Check physical existence of runtime library on Android filesystem."""
    for p in paths:
        path_obj = Path(p)
        try:
            if path_obj.is_file() and path_obj.stat().st_size >= 1024:
                return str(path_obj.resolve())
        except (OSError, PermissionError):
            continue
    return None


def detect_npu_capabilities() -> NPUProfile:
    """Inspect the device for Qualcomm Hexagon, Samsung Exynos NPU, Google Edge TPU, and NNAPI."""
    soc_platform = _read_android_prop("ro.board.platform").lower()
    chipname = _read_android_prop("ro.hardware.chipname").lower()
    hardware = _read_android_prop("ro.hardware").lower()
    product_board = _read_android_prop("ro.product.board").lower()

    # 1. Qualcomm Snapdragon Hexagon HTP Probe
    qnn_lib = _probe_first_existing_lib(QUALCOMM_QNN_LIBS)
    is_qualcomm = any(q in soc_platform or q in hardware or q in product_board for q in ["qcom", "snapdragon", "sm8", "sm7", "lahaina", "taro", "kalama", "pineapple"])

    if qnn_lib or is_qualcomm:
        # Determine TOPS rating based on SoC generation
        tops = 15.0
        dsp_arch = "Hexagon Vector Extensions (HVX)"
        if "sm8650" in soc_platform or "pineapple" in soc_platform:  # Snapdragon 8 Gen 3
            tops = 45.0
            dsp_arch = "Hexagon v75 HTP (45 TOPS Generative AI NPU)"
        elif "sm8550" in soc_platform or "kalama" in soc_platform:  # Snapdragon 8 Gen 2
            tops = 35.0
            dsp_arch = "Hexagon v73 HTP (35 TOPS NPU)"
        elif "sm8450" in soc_platform or "taro" in soc_platform:    # Snapdragon 8 Gen 1
            tops = 27.0
            dsp_arch = "Hexagon v69 HTP (27 TOPS NPU)"

        has_driver = qnn_lib is not None
        return NPUProfile(
            available=has_driver,
            vendor=NPUVendor.QUALCOMM_HEXAGON,
            chipset_name=f"Qualcomm Snapdragon ({soc_platform or hardware})",
            driver_library=qnn_lib,
            dsp_architecture=dsp_arch,
            tops_rating=tops if has_driver else 0.0,
            supported_precisions=["INT4", "INT8", "FP16"] if has_driver else [],
            delegate_type="QNN_HTP_DELEGATE" if has_driver else None,
            acceleration_status="Operational (Qualcomm Hexagon Tensor Core)" if has_driver else "SoC Detected (Driver inaccessible or SELinux restricted)",
        )

    # 2. Samsung Exynos NPU (ENN / Eden) Probe
    eden_lib = _probe_first_existing_lib(SAMSUNG_EDEN_LIBS)
    is_samsung_exynos = "exynos" in chipname or "s5e" in soc_platform or "universal" in hardware

    if eden_lib or is_samsung_exynos:
        tops = 17.0
        dsp_arch = "Samsung Exynos Dual-NPU"
        if "2400" in chipname or "9945" in soc_platform:  # Exynos 2400
            tops = 42.0
            dsp_arch = "Samsung Generative AI NPU (42 TOPS)"
        elif "1480" in chipname:  # Exynos 1480
            tops = 20.0
            dsp_arch = "Exynos AI NPU (20 TOPS)"
        elif "1380" in chipname:  # Exynos 1380
            tops = 4.9
            dsp_arch = "Exynos 1380 NPU (4.9 TOPS)"

        has_driver = eden_lib is not None
        return NPUProfile(
            available=has_driver,
            vendor=NPUVendor.SAMSUNG_EDEN,
            chipset_name=f"Samsung Exynos ({chipname or soc_platform})",
            driver_library=eden_lib,
            dsp_architecture=dsp_arch,
            tops_rating=tops if has_driver else 0.0,
            supported_precisions=["INT8", "FP16"] if has_driver else [],
            delegate_type="EXYNOS_ENN_DELEGATE" if has_driver else None,
            acceleration_status="Operational (Samsung Exynos NPU)" if has_driver else "SoC Detected (Driver inaccessible or SELinux restricted)",
        )

    # 3. Google Tensor Edge TPU (Pixel Neural Core) Probe
    tpu_lib = _probe_first_existing_lib(GOOGLE_EDGETPU_LIBS)
    is_google_tensor = any(t in hardware or t in product_board for t in ["zuma", "gs201", "gs101", "tensor", "cloudripper"])

    if tpu_lib or is_google_tensor:
        has_driver = tpu_lib is not None
        return NPUProfile(
            available=has_driver,
            vendor=NPUVendor.GOOGLE_EDGE_TPU,
            chipset_name=f"Google Tensor TPU ({hardware or product_board})",
            driver_library=tpu_lib,
            dsp_architecture="Google Edge TPU (Custom Tensor Core)",
            tops_rating=20.0 if has_driver else 0.0,
            supported_precisions=["INT8", "FP16"] if has_driver else [],
            delegate_type="EDGETPU_DELEGATE" if has_driver else None,
            acceleration_status="Operational (Google Edge TPU Core)" if has_driver else "SoC Detected (Driver inaccessible or SELinux restricted)",
        )

    # 4. Android Generic NNAPI Runtime Probe
    nnapi_lib = _probe_first_existing_lib(ANDROID_NNAPI_LIBS)
    if nnapi_lib:
        return NPUProfile(
            available=True,
            vendor=NPUVendor.ANDROID_NNAPI,
            chipset_name="Android Generic NNAPI",
            driver_library=nnapi_lib,
            dsp_architecture="Android Neural Networks Hardware Abstraction Layer (HAL)",
            tops_rating=5.0,
            supported_precisions=["INT8", "FP16"],
            delegate_type="NNAPI_DELEGATE",
            acceleration_status="Operational (Android NNAPI HAL)",
        )

    return NPUProfile(
        available=False,
        vendor=NPUVendor.NONE,
        chipset_name="Generic Host",
        driver_library=None,
        dsp_architecture="No Dedicated NPU / TPU Detected",
        tops_rating=0.0,
        supported_precisions=[],
        delegate_type="CPU_FALLBACK",
        acceleration_status="Unavailable (CPU/GPU pipeline active)",
    )


def get_optimal_heterogeneous_pipeline(device: str = "auto") -> Dict[str, str]:
    """Determine the compute processor allocation for each diffusion pipeline component.
    
    Note:
        In v1.1, diffusion inference is executed via the native Bionic sd-cli engine using
        Vulkan GPU compute (-ngl 99) and ARM64 NEON CPU math. Direct Qualcomm QNN / Hexagon
        NPU subgraph partitioning is the architectural target for the upcoming v2.0 runtime.
    """
    req = device.lower().strip()

    if req == "cpu":
        return {
            "text_encoder": "CPU (ARM NEON FP16)",
            "denoiser_unet": "CPU (ARM NEON DotProd/I8MM)",
            "vae_decoder": "CPU (ARM NEON FP16)",
            "scheduler": "CPU (Single-Core Fast Math)",
            "summary": "CPU-Only [ARM NEON Pipeline]"
        }
    else:
        return {
            "text_encoder": "CPU / GPU (ARM NEON / Vulkan)",
            "denoiser_unet": "GPU (Vulkan Compute / -ngl 99)",
            "vae_decoder": "GPU (Vulkan Compute FP16)",
            "scheduler": "CPU (Single-Core Fast Math)",
            "summary": "GPU-Accelerated [Vulkan Compute Shader Pipeline]"
        }
