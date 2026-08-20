"""Platform inspection, Samsung Galaxy hardware detection, memory checks, and Android OS bridges."""

import ctypes
import glob
import logging
import os
import platform
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("termux_diffusion.platform")

# Android Termux standard paths
TERMUX_PREFIX = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
TERMUX_HOME = os.environ.get("HOME", "/data/data/com.termux/files/home")


def is_android_termux() -> bool:
    """Check whether the current runtime environment is native Android Termux."""
    if os.environ.get("TERMUX_VERSION") or os.environ.get("TERMUX_APP_PID"):
        return True
    if os.path.exists("/data/data/com.termux"):
        return True
    return False


def is_arm64() -> bool:
    """Check whether the host CPU architecture is 64-bit ARM (aarch64 / arm64)."""
    machine = platform.machine().lower()
    return machine in ("aarch64", "arm64", "armv8l", "armv8b")


def get_default_cache_dir() -> Path:
    """Return root cache directory for termux-diffusion."""
    env_cache = os.environ.get("TERMUX_DIFFUSION_CACHE")
    if env_cache:
        return Path(env_cache).resolve()
    return Path.home() / ".cache" / "termux-diffusion"


def get_galaxy_gallery_dir() -> Path:
    """Return the designated Samsung Galaxy / Android photo gallery save directory."""
    termux_storage = Path.home() / "storage" / "pictures" / "TermuxDiffusion"
    if (Path.home() / "storage" / "pictures").is_dir():
        termux_storage.mkdir(parents=True, exist_ok=True)
        return termux_storage

    sdcard_pictures = Path("/sdcard/Pictures/TermuxDiffusion")
    if Path("/sdcard/Pictures").is_dir():
        sdcard_pictures.mkdir(parents=True, exist_ok=True)
        return sdcard_pictures

    fallback = get_default_cache_dir() / "outputs"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def export_to_android_gallery(image_path: Path) -> Path:
    """Copy generated image to Samsung Gallery and broadcast media scanner intent."""
    gallery_dir = get_galaxy_gallery_dir()
    dest = gallery_dir / image_path.name
    if dest != image_path:
        shutil.copy2(image_path, dest)

    _broadcast_media_scanner(dest)
    return dest


def _broadcast_media_scanner(image_path: Path) -> None:
    """Broadcast android.intent.action.MEDIA_SCANNER_SCAN_FILE so Galaxy Gallery indexes the file."""
    if not is_android_termux():
        return

    am_binary = shutil.which("am") or shutil.which("termux-am")
    if not am_binary:
        return

    file_uri = f"file://{urllib.parse.quote(str(image_path.resolve()))}"
    try:
        subprocess.run(
            [am_binary, "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE", "-d", file_uri],
            capture_output=True,
            timeout=3.0,
            check=False
        )
    except Exception as exc:
        logger.debug("Media scanner broadcast note: %s", exc)


def get_optimal_thread_count() -> int:
    """Calculate the optimal number of inference threads for mobile and host CPUs.
    
    In big.LITTLE mobile architectures (e.g., 4 Performance + 4 Efficiency cores),
    running on all cores causes severe thermal throttling and cache thrashing.
    We inspect sysfs CPU frequency scaling topologies when available, or dynamically
    derive cluster sizes.
    """
    # 1. Try parsing Linux/Android sysfs cpufreq topology
    try:
        freq_files = sorted(glob.glob("/sys/devices/system/cpu/cpu[0-9]*/cpufreq/cpuinfo_max_freq"))
        if not freq_files:
            freq_files = sorted(glob.glob("/sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_max_freq"))

        if freq_files:
            freqs: List[int] = []
            for ff in freq_files:
                try:
                    with open(ff, "r", encoding="utf-8") as f:
                        val = f.read().strip()
                        if val.isdigit():
                            freqs.append(int(val))
                except (OSError, IOError) as err:
                    logger.debug("Sysfs freq read note on '%s': %s", ff, err)

            if freqs:
                max_f = max(freqs)
                # Count cores operating within 85% of peak frequency (Big / Mid cluster)
                threshold = int(max_f * 0.85)
                perf_cores = sum(1 for f in freqs if f >= threshold)
                if perf_cores > 0:
                    return perf_cores
    except Exception as e:
        logger.debug("Sysfs CPU frequency probing error: %s", e)

    # 2. General fallback based on logical CPU core topology
    total_cores = os.cpu_count() or 4
    if is_arm64():
        # Typical ARM mobile: 8 cores = 4 Big + 4 Little (or 1+3+4)
        if total_cores >= 8:
            return 4
        elif total_cores >= 6:
            return 4
        elif total_cores >= 4:
            return 4
        return max(1, total_cores)
    else:
        # Desktop x86_64: Use physical cores heuristic (half of hyperthreaded cores or up to 8)
        return max(1, min(8, total_cores // 2 if total_cores > 4 else total_cores))


def _get_windows_memory_info() -> Optional[Dict[str, int]]:
    """Retrieve accurate Windows physical RAM and commit limit via GlobalMemoryStatusEx."""
    try:
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            mem_total_mb = int(stat.ullTotalPhys // (1024 * 1024))
            mem_available_mb = int(stat.ullAvailPhys // (1024 * 1024))
            pagefile_total_mb = int(stat.ullTotalPageFile // (1024 * 1024))
            pagefile_avail_mb = int(stat.ullAvailPageFile // (1024 * 1024))
            
            swap_total_mb = max(0, pagefile_total_mb - mem_total_mb)
            swap_free_mb = max(0, pagefile_avail_mb - mem_available_mb)

            return {
                "mem_total_mb": mem_total_mb,
                "mem_available_mb": mem_available_mb,
                "swap_total_mb": swap_total_mb,
                "swap_free_mb": swap_free_mb,
                "effective_total_mb": mem_total_mb + swap_total_mb,
                "effective_available_mb": mem_available_mb + swap_free_mb,
            }
    except Exception as e:
        logger.debug("Windows GlobalMemoryStatusEx query failed: %s", e)
    return None


def get_memory_info() -> Dict[str, int]:
    """Inspect system memory metrics (RAM and swap/zRAM) in MB from genuine OS interfaces."""
    metrics = {
        "mem_total_mb": 0,
        "mem_available_mb": 0,
        "swap_total_mb": 0,
        "swap_free_mb": 0,
        "effective_total_mb": 0,
        "effective_available_mb": 0,
    }

    # 1. Linux & Android /proc/meminfo (Standard on Termux)
    if os.path.exists("/proc/meminfo"):
        try:
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.split(":")
                    if len(parts) == 2:
                        key = parts[0].strip()
                        val_str = parts[1].strip().split()[0]
                        if val_str.isdigit():
                            val_kb = int(val_str)
                            val_mb = val_kb // 1024
                            if key == "MemTotal":
                                metrics["mem_total_mb"] = val_mb
                            elif key == "MemAvailable":
                                metrics["mem_available_mb"] = val_mb
                            elif key == "SwapTotal":
                                metrics["swap_total_mb"] = val_mb
                            elif key == "SwapFree":
                                metrics["swap_free_mb"] = val_mb
            metrics["effective_total_mb"] = metrics["mem_total_mb"] + metrics["swap_total_mb"]
            metrics["effective_available_mb"] = metrics["mem_available_mb"] + metrics["swap_free_mb"]
            return metrics
        except Exception as e:
            logger.debug("Failed reading /proc/meminfo: %s", e)

    # 2. Windows Native Win32 API
    if sys.platform == "win32":
        win_mem = _get_windows_memory_info()
        if win_mem:
            return win_mem

    # 3. Optional psutil fallback if installed
    try:
        import psutil  # type: ignore
        vmem = psutil.virtual_memory()
        smem = psutil.swap_memory()
        metrics["mem_total_mb"] = int(vmem.total // (1024 * 1024))
        metrics["mem_available_mb"] = int(vmem.available // (1024 * 1024))
        metrics["swap_total_mb"] = int(smem.total // (1024 * 1024))
        metrics["swap_free_mb"] = int(smem.free // (1024 * 1024))
        metrics["effective_total_mb"] = metrics["mem_total_mb"] + metrics["swap_total_mb"]
        metrics["effective_available_mb"] = metrics["mem_available_mb"] + metrics["swap_free_mb"]
        return metrics
    except ImportError:
        pass

    return metrics


def check_memory_safety(required_mb: int = 1500) -> Tuple[bool, str]:
    """Verify if available memory is sufficient for model loading without triggering Android LMK."""
    mem = get_memory_info()
    avail = mem["effective_available_mb"]
    
    # If memory info could not be determined at all (0 MB), pass with a note
    if mem["effective_total_mb"] == 0:
        return True, "Memory detection unavailable on host OS; bypassing pre-flight guard."

    if avail < required_mb:
        return False, (
            f"Available memory ({avail} MB) is below the recommended threshold ({required_mb} MB). "
            f"Please enable Samsung RAM Plus (Settings -> Battery and device care -> Memory -> RAM Plus) "
            f"or close background apps to avoid Low Memory Killer (LMK) termination."
        )
    return True, f"Memory check passed: {avail} MB available (RAM + zRAM)."


class TermuxWakeLock:
    """Context manager to hold Android CPU WakeLock during long-running AI inference."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._acquired = False

    def __enter__(self):
        if not self.enabled or not is_android_termux():
            return self

        wake_lock_bin = shutil.which("termux-wake-lock")
        if wake_lock_bin:
            try:
                res = subprocess.run([wake_lock_bin], capture_output=True, timeout=2.0, check=False)
                if res.returncode == 0:
                    self._acquired = True
                    logger.debug("Acquired Termux CPU WakeLock.")
                else:
                    logger.warning("Failed to acquire Termux WakeLock (exit %d): %s", res.returncode, res.stderr)
            except Exception as e:
                logger.warning("Exception while acquiring WakeLock: %s", e)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._acquired:
            wake_unlock_bin = shutil.which("termux-wake-unlock")
            if wake_unlock_bin:
                try:
                    res = subprocess.run([wake_unlock_bin], capture_output=True, timeout=2.0, check=False)
                    if res.returncode == 0:
                        logger.debug("Released Termux CPU WakeLock.")
                    else:
                        logger.warning("Failed releasing Termux WakeLock (exit %d): %s", res.returncode, res.stderr)
                except Exception as e:
                    logger.warning("Exception while releasing WakeLock: %s", e)
            self._acquired = False
