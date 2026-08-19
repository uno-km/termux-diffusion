"""Exceptions for the termux-diffusion framework."""

class TermuxDiffusionError(Exception):
    """Base exception for all termux-diffusion errors."""
    pass


class PlatformNotSupportedError(TermuxDiffusionError):
    """Raised when running on an unsupported platform or non-ARM64 architecture."""
    pass


class ModelNotFoundError(TermuxDiffusionError):
    """Raised when the specified model preset or file path cannot be located."""
    pass


class ModelDownloadError(TermuxDiffusionError):
    """Raised when an error occurs during model downloading or checksum verification."""
    pass


class ProvisioningError(TermuxDiffusionError):
    """Raised when the native C++ engine (sd-cli) fails to build or provision."""
    pass


class OOMRiskError(TermuxDiffusionError):
    """Raised when available system memory (RAM + zRAM) is insufficient for safe inference."""
    pass


class InferenceTimeoutError(TermuxDiffusionError):
    """Raised when diffusion inference exceeds the configured execution timeout."""
    pass
