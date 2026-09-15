"""
AMEVA Unified Exception Hierarchy for Termux AI Engines.
Component: [DIFFUSION]
"""
from typing import Optional, Any


class AmevaTermuxError(Exception):
    """Root exception for all Termux On-Device AI Engines."""
    COMPONENT_TAG = "[DIFFUSION]"
    DEFAULT_CODE = "E_UNKNOWN"

    def __init__(self, message: str, code: Optional[Any] = None, details: Optional[Any] = None):
        self.code = code or self.DEFAULT_CODE
        self.details = details
        self.raw_message = message
        super().__init__(message if message.startswith("[DIFFUSION]") else f"{self.COMPONENT_TAG} [{self.code}] {message}")


TermuxDiffusionError = AmevaTermuxError


class ErrorCode:
    CLI_EXCLUSIVE = "E_CLI_EXCLUSIVE_MUTEX"
    PLATFORM_UNSUPPORTED = "E_PLATFORM_UNSUPPORTED"
    MANIFEST_DOWNLOAD = "E_MANIFEST_DOWNLOAD"
    MANIFEST_SIGNATURE = "E_MANIFEST_SIGNATURE"
    MANIFEST_SCHEMA = "E_MANIFEST_SCHEMA"
    MANIFEST_EXPIRED = "E_MANIFEST_EXPIRED"
    ARTIFACT_DOWNLOAD = "E_ARTIFACT_DOWNLOAD"
    ARTIFACT_SIZE = "E_ARTIFACT_SIZE"
    ARTIFACT_SHA256 = "E_ARTIFACT_SHA256"
    ARTIFACT_FORMAT = "E_ARTIFACT_FORMAT"
    DYNAMIC_LINKER = "E_DYNAMIC_LINKER"
    ILLEGAL_INSTRUCTION = "E_ILLEGAL_INSTRUCTION"
    PROCESS_TIMEOUT = "E_PROCESS_TIMEOUT"
    VULKAN_LOADER = "E_VULKAN_LOADER"
    VULKAN_DEVICE = "E_VULKAN_DEVICE"
    VULKAN_PIPELINE = "E_VULKAN_PIPELINE"
    CPU_SELFTEST = "E_CPU_SELFTEST"
    SOURCE_CLONE = "E_SOURCE_CLONE"
    SOURCE_PATCH = "E_SOURCE_PATCH"
    SOURCE_CONFIGURE = "E_SOURCE_CONFIGURE"
    SOURCE_BUILD = "E_SOURCE_BUILD"
    SOURCE_ARTIFACT = "E_SOURCE_ARTIFACT"
    INSTALL_LOCKED = "E_INSTALL_LOCKED"
    ROLLBACK_FAILED = "E_ROLLBACK_FAILED"


class ExitCode:
    SUCCESS = 0
    CLI_ERROR = 2
    PLATFORM_ERROR = 10
    INTEGRITY_ERROR = 20
    EXECUTION_ERROR = 30
    SELFTEST_ERROR = 40
    BUILD_ERROR = 50
    ROLLBACK_ERROR = 60


class PlatformNotSupportedError(TermuxDiffusionError):
    def __init__(self, message: str):
        super().__init__(message, code=ErrorCode.PLATFORM_UNSUPPORTED)


class ModelNotFoundError(TermuxDiffusionError):
    pass


class ModelDownloadError(TermuxDiffusionError):
    pass


class DownloadError(TermuxDiffusionError):
    def __init__(self, message: str, code: str = ErrorCode.ARTIFACT_DOWNLOAD):
        super().__init__(message, code=code)


class ProvisioningError(TermuxDiffusionError):
    def __init__(self, message: str, code: str = ErrorCode.SOURCE_BUILD):
        super().__init__(message, code=code)


class InstallLockError(TermuxDiffusionError):
    def __init__(self, message: str):
        super().__init__(message, code=ErrorCode.INSTALL_LOCKED)


class OOMRiskError(TermuxDiffusionError):
    pass


class InferenceTimeoutError(TermuxDiffusionError):
    pass


class HardwareCompatibilityError(TermuxDiffusionError):
    pass


class RuntimeNotFoundError(TermuxDiffusionError):
    pass


class InferenceExecutionError(TermuxDiffusionError):
    pass


class ModelCorruptedError(TermuxDiffusionError):
    pass
