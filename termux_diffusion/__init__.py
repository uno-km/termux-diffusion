"""termux-diffusion: On-Device AI Image Generation Framework for Android Termux & Samsung Galaxy."""

from .core import (
    GenerationResult,
    async_generate,
    generate,
    get_default_negative_prompt,
    get_quality_guard_negative_prompt,
    set_default_negative_prompt,
)
from .exceptions import (
    InferenceTimeoutError,
    ModelDownloadError,
    ModelNotFoundError,
    OOMRiskError,
    PlatformNotSupportedError,
    ProvisioningError,
    TermuxDiffusionError,
)
from .hub import (
    DEFAULT_PRESETS,
    clear_cache,
    download_model,
    get_cache_dir,
    is_model_cached,
    list_cached_models,
    list_presets,
    register_model,
    resolve_model_path,
    set_cache_dir,
)
from .installer import locate_sd_cli, provision_engine, run_doctor
from .platform import (
    TermuxWakeLock,
    check_memory_safety,
    export_to_android_gallery,
    get_galaxy_gallery_dir,
    get_memory_info,
    get_optimal_thread_count,
    is_android_termux,
    is_arm64,
)
from .hardware import (
    ComputeBackend,
    HardwareProfile,
    detect_hardware_profile,
    format_hardware_report,
    resolve_device_backend,
)
from .npu import (
    NPUProfile,
    NPUVendor,
    detect_npu_capabilities,
    get_optimal_heterogeneous_pipeline,
)

__version__ = "1.1.1"
__author__ = "uno-km (쌩초보코딩단)"
__license__ = "MIT"

__all__ = [
    "__version__",
    "generate",
    "async_generate",
    "GenerationResult",
    "download_model",
    "resolve_model_path",
    "register_model",
    "set_cache_dir",
    "get_cache_dir",
    "is_model_cached",
    "list_cached_models",
    "clear_cache",
    "list_presets",
    "DEFAULT_PRESETS",
    "locate_sd_cli",
    "provision_engine",
    "run_doctor",
    "is_android_termux",
    "is_arm64",
    "check_memory_safety",
    "get_memory_info",
    "get_optimal_thread_count",
    "get_galaxy_gallery_dir",
    "export_to_android_gallery",
    "TermuxWakeLock",
    "TermuxDiffusionError",
    "PlatformNotSupportedError",
    "ModelNotFoundError",
    "ModelDownloadError",
    "ProvisioningError",
    "OOMRiskError",
    "InferenceTimeoutError",
]
