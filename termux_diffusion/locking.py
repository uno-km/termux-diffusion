"""Process-wide installation lock manager for termux-diffusion."""

import os
import time
import logging
from pathlib import Path
from typing import Optional

from .exceptions import InstallLockError

logger = logging.getLogger("termux_diffusion.locking")


class InstallLock:
    """File lock manager controlling full installer state machine execution."""
    def __init__(self, lock_file: Path, timeout_sec: float = 5.0):
        self.lock_file = lock_file
        self.timeout_sec = timeout_sec
        self._acquired = False

    def acquire(self):
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        start = time.time()
        while time.time() - start < self.timeout_sec:
            try:
                fd = os.open(str(self.lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, f"pid={os.getpid()}\nstarted_at={time.time()}\n".encode("utf-8"))
                os.close(fd)
                self._acquired = True
                return
            except FileExistsError:
                time.sleep(0.2)
        raise InstallLockError(
            f"E_INSTALL_LOCKED: Installation process locked by another running process ({self.lock_file})."
        )

    def release(self):
        if self._acquired and self.lock_file.exists():
            try:
                self.lock_file.unlink(missing_ok=True)
            except Exception as e:
                logger.warning("Failed removing install.lock: %s", e)
            self._acquired = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
