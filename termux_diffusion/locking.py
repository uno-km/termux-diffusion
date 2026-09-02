import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

from .exceptions import InstallLockError

logger = logging.getLogger("termux_diffusion.locking")


class InstallLock:
    """File lock manager controlling full installer state machine execution with stale PID auto-recovery."""
    def __init__(self, lock_file: Path, timeout_sec: float = 5.0):
        self.lock_file = lock_file
        self.timeout_sec = timeout_sec
        self._acquired = False

    def _is_pid_alive(self, pid: int) -> bool:
        if pid <= 0:
            return False
        if sys.platform == "win32":
            try:
                import ctypes
                PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
                h = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
                if h:
                    ctypes.windll.kernel32.CloseHandle(h)
                    return True
                return False
            except Exception:
                return True
        else:
            try:
                os.kill(pid, 0)
                return True
            except (OSError, ProcessLookupError):
                return False

    def _check_and_clear_stale_lock(self) -> bool:
        """Check if existing lock file belongs to a deceased process, removing it if stale."""
        if not self.lock_file.exists():
            return True
        try:
            content = self.lock_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("pid="):
                    pid_str = line.split("=", 1)[1].strip()
                    if pid_str.isdigit():
                        pid = int(pid_str)
                        if not self._is_pid_alive(pid):
                            logger.warning(
                                "[termux-diffusion] Stale installation lock detected (PID: %d is dead). Auto-reclaiming lock.",
                                pid,
                            )
                            self.lock_file.unlink(missing_ok=True)
                            return True
        except Exception as e:
            logger.debug("Stale lock inspection note: %s", e)
        return False

    def acquire(self):
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        self._check_and_clear_stale_lock()
        start = time.time()
        while time.time() - start < self.timeout_sec:
            try:
                fd = os.open(str(self.lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, f"pid={os.getpid()}\nstarted_at={time.time()}\n".encode("utf-8"))
                os.close(fd)
                self._acquired = True
                return
            except FileExistsError:
                if self._check_and_clear_stale_lock():
                    continue
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

