"""Atomic download manager with SHA-256 integrity verification, concurrency lock, and rollback safety."""

import os
import shutil
import time
import urllib.request
import logging
from pathlib import Path
from typing import Optional

from .exceptions import DownloadError, InstallLockError, TermuxDiffusionError
from .locking import InstallLock
from .manifest import verify_file_sha256

logger = logging.getLogger("termux_diffusion.downloader")


def atomic_download_file(
    url: str,
    dest_path: Path,
    expected_sha256: Optional[str] = None,
    expected_size: Optional[int] = None,
    timeout_sec: float = 120.0,
    user_agent: str = "termux-diffusion-downloader/1.2.0"
) -> Path:
    """Download url to dest_path atomically using .part -> SHA256 check -> atomic rename -> rollback."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    part_path = dest_path.with_suffix(dest_path.suffix + ".part")
    bak_path = dest_path.with_suffix(dest_path.suffix + ".bak")

    part_path.unlink(missing_ok=True)
    bak_path.unlink(missing_ok=True)

    print(f"[termux-diffusion] Downloading artifact from {url}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": user_agent})
        with urllib.request.urlopen(req, timeout=timeout_sec) as response:
            if response.status != 200:
                raise DownloadError(f"E_ARTIFACT_DOWNLOAD: HTTP server returned status code {response.status}")
            
            with open(part_path, "wb") as out_f:
                shutil.copyfileobj(response, out_f)
    except Exception as exc:
        part_path.unlink(missing_ok=True)
        raise DownloadError(f"E_ARTIFACT_DOWNLOAD: Network error downloading {url}: {exc}") from exc

    # Size Verification
    actual_size = part_path.stat().st_size
    if expected_size is not None and expected_size > 0 and actual_size != expected_size:
        part_path.unlink(missing_ok=True)
        raise DownloadError(
            f"E_ARTIFACT_SIZE: Downloaded artifact size mismatch. "
            f"Expected {expected_size} bytes, got {actual_size} bytes."
        )

    # SHA-256 Verification
    if expected_sha256 and not verify_file_sha256(part_path, expected_sha256):
        part_path.unlink(missing_ok=True)
        raise DownloadError(
            f"E_ARTIFACT_SHA256: SHA-256 checksum verification failed for {dest_path.name}. "
            f"Artifact hash mismatch!"
        )

    # Atomic Rename with Backup Rollback Safety
    try:
        if dest_path.exists():
            dest_path.rename(bak_path)
        part_path.rename(dest_path)
        os.chmod(dest_path, 0o755)
        bak_path.unlink(missing_ok=True)
        print(f"[termux-diffusion] Artifact {dest_path.name} downloaded and verified (SHA-256 match).")
        return dest_path
    except Exception as e:
        # Rollback
        part_path.unlink(missing_ok=True)
        if bak_path.exists() and not dest_path.exists():
            bak_path.rename(dest_path)
        raise DownloadError(f"E_ATOMIC_RENAME_FAIL: Failed installing verified artifact {dest_path.name}: {e}") from e


from typing import List, Dict, Any, Union


def list_models() -> List[Dict[str, Any]]:
    """List standard verified diffusion models from hub presets."""
    from .hub import list_presets
    presets = list_presets()
    return [{"id": k, **v} for k, v in presets.items()]


def download_model(
    model_name_or_url: str = "sdxs",
    cache_dir: Optional[Union[str, Path]] = None,
    force: bool = False,
    **kwargs: Any,
) -> Path:
    """Download diffusion model weights using termux_diffusion.hub."""
    from .hub import download_model as _hub_download
    return _hub_download(model_name_or_url=model_name_or_url, cache_dir=cache_dir, force=force, **kwargs)


def resolve_model_path(
    model_name_or_path: str = "sdxs",
    cache_dir: Optional[Union[str, Path]] = None,
) -> Path:
    """Resolve diffusion model path to local Path."""
    from .hub import resolve_model_path as _hub_resolve
    return _hub_resolve(model_name_or_path=model_name_or_path, cache_dir=cache_dir)

