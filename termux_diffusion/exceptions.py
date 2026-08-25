"""Exceptions and centralized ErrorCodes for the termux-diffusion framework."""

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


class TermuxDiffusionError(Exception):
    """Base exception for all termux-diffusion errors."""
    def __init__(self, message: str, code: str = "E_UNKNOWN"):
        super().__init__(message)
        self.code = code


class PlatformNotSupportedError(TermuxDiffusionError):
    """Raised when running on an unsupported platform or non-ARM64 architecture."""
    def __init__(self, message: str):
        super().__init__(message, code=ErrorCode.PLATFORM_UNSUPPORTED)


class ModelNotFoundError(TermuxDiffusionError):
    """Raised when the specified model preset or file path cannot be located."""
    pass


class ModelDownloadError(TermuxDiffusionError):
    """Raised when an error occurs during model downloading or checksum verification."""
    pass


class ProvisioningError(TermuxDiffusionError):
    """Raised when the native C++ engine (sd-cli) fails to build or provision."""
    def __init__(self, message: str, code: str = ErrorCode.SOURCE_BUILD):
        super().__init__(message, code=code)


class InstallLockError(TermuxDiffusionError):
    """Raised when installation lock is held by another process."""
    def __init__(self, message: str):
        super().__init__(message, code=ErrorCode.INSTALL_LOCKED)


class OOMRiskError(TermuxDiffusionError):
    """Raised when available system memory (RAM + zRAM) is insufficient for safe inference."""
    pass


class InferenceTimeoutError(TermuxDiffusionError):
    """Raised when diffusion inference exceeds the configured execution timeout."""
    pass
