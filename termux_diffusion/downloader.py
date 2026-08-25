"""Atomic download manager with SHA-256 integrity verification, concurrency lock, and rollback safety."""

import os
import shutil
import time
import urllib.request
import logging
from pathlib import Path
from typing import Optional

from .exceptions import TermuxDiffusionError
from .manifest import verify_file_sha256

logger = logging.getLogger("termux_diffusion.downloader")


class InstallLockError(TermuxDiffusionError):
    """Raised when install lock cannot be acquired due to concurrent process."""
    pass


class DownloadError(TermuxDiffusionError):
    """Raised when file download, size, or SHA-256 verification fails."""
    pass


class InstallLock:
    """File lock manager to prevent concurrent installation processes."""
    def __init__(self, lock_file: Path, timeout_sec: float = 5.0):
        self.lock_file = lock_file
        self.timeout_sec = timeout_sec
        self._acquired = False

    def acquire(self):
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        start = time.time()
        while time.time() - start < self.timeout_sec:
            try:
                # O_CREAT | O_EXCL atomic creation
                fd = os.open(str(self.lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, f"pid={os.getpid()}\n".encode("utf-8"))
                os.close(fd)
                self._acquired = True
                return
            except FileExistsError:
                time.sleep(0.2)
        raise InstallLockError(
            f"E_CONCURRENCY_LOCK: Another installation process holds the lock file at {self.lock_file}. "
            f"If stale, remove {self.lock_file} and retry."
        )

    def release(self):
        if self._acquired and self.lock_file.exists():
            try:
                self.lock_file.unlink(missing_ok=True)
            except Exception as e:
                logger.warning("Failed deleting lock file: %s", e)
            self._acquired = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


def atomic_download_file(
    url: str,
    dest_path: Path,
    expected_sha256: str,
    expected_size: Optional[int] = None,
    timeout_sec: float = 30.0,
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
