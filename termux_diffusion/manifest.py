"""Manifest schema v1 parsing, SHA-256 checksum verification, and release metadata handling."""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any

from .exceptions import TermuxDiffusionError

logger = logging.getLogger("termux_diffusion.manifest")

MANIFEST_SCHEMA_VERSION = 1

class ManifestError(TermuxDiffusionError):
    """Raised when manifest parsing, signature, or schema validation fails."""
    pass


@dataclass
class ArtifactMetadata:
    id: str
    filename: str
    url: str
    sha256: str
    size: int
    compression: str = "tar.gz"


@dataclass
class PlatformRequirements:
    os: str = "android"
    abi: str = "arm64-v8a"
    min_api: int = 26
    max_api: Optional[int] = None
    libc: str = "bionic"


@dataclass
class RuntimeRequirements:
    backend: str = "auto"
    cpu_features_required: List[str] = field(default_factory=list)
    vulkan_required: bool = False
    vulkan_min_version: str = "1.1"
    shared_libraries: List[str] = field(default_factory=list)


@dataclass
class ReleaseManifest:
    schema_version: int
    package_version: str
    release_id: str
    channel: str
    artifacts: Dict[str, ArtifactMetadata]
    platform: PlatformRequirements
    runtime: RuntimeRequirements
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReleaseManifest":
        schema_ver = data.get("schema_version", 1)
        if schema_ver != MANIFEST_SCHEMA_VERSION:
            raise ManifestError(f"E_MANIFEST_SCHEMA: Unsupported manifest schema version {schema_ver}")

        pkg_ver = data.get("package_version", "1.2.0")
        release_id = data.get("release_id", "")
        channel = data.get("channel", "stable")

        plat_data = data.get("platform", {})
        plat = PlatformRequirements(
            os=plat_data.get("os", "android"),
            abi=plat_data.get("abi", "arm64-v8a"),
            min_api=plat_data.get("min_api", 26),
            max_api=plat_data.get("max_api"),
            libc=plat_data.get("libc", "bionic")
        )

        rt_data = data.get("runtime", {})
        rt = RuntimeRequirements(
            backend=rt_data.get("backend", "auto"),
            cpu_features_required=rt_data.get("cpu_features_required", []),
            vulkan_required=rt_data.get("vulkan_required", False),
            vulkan_min_version=rt_data.get("vulkan_min_version", "1.1"),
            shared_libraries=rt_data.get("shared_libraries", [])
        )

        artifacts_dict = {}
        art_raw = data.get("artifacts", {})
        for art_id, art_info in art_raw.items():
            artifacts_dict[art_id] = ArtifactMetadata(
                id=art_id,
                filename=art_info.get("filename", f"{art_id}.tar.gz"),
                url=art_info.get("url", ""),
                sha256=art_info.get("sha256", ""),
                size=art_info.get("size", 0),
                compression=art_info.get("compression", "tar.gz")
            )

        return cls(
            schema_version=schema_ver,
            package_version=pkg_ver,
            release_id=release_id,
            channel=channel,
            artifacts=artifacts_dict,
            platform=plat,
            runtime=rt,
            raw_data=data
        )


def compute_sha256(filepath: Path) -> str:
    """Calculate hex SHA-256 hash of given file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


def verify_file_sha256(filepath: Path, expected_hash: str) -> bool:
    """Verify that file's SHA-256 matches expected_hash."""
    if not filepath.is_file():
        return False
    actual = compute_sha256(filepath)
    return actual == expected_hash.lower().strip()
