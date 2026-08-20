"""Smart Model Hub, preset management, Hugging Face streaming downloader, GGUF validation, and local caching."""

import hashlib
import json
import logging
import os
import shutil
import struct
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from types import MappingProxyType
from typing import Callable, Dict, List, Optional, Union

from .exceptions import ModelDownloadError, ModelNotFoundError
from .platform import get_default_cache_dir

logger = logging.getLogger("termux_diffusion.hub")

# Built-in Samsung Galaxy & Mobile optimized GGUF presets (Immutable MappingProxy)
DEFAULT_PRESETS = MappingProxyType({
    "realistic": {
        "repo_id": "second-state/Realistic_Vision_V6.0_B1-GGUF",
        "filename": "realisticVisionV60B1_v51HyperVAE-Q4_k.gguf",
        "alias": "realistic.gguf",
        "description": "Realistic Vision V6.0 B1 (Q4_K) - Full SD1.5 photorealistic portraits (Needs 20-25 steps, CFG 7.0, DPM2 Karras)",
        "size_mb": 1547,
        "default_steps": 20,
        "default_cfg": 7.0,
    },
    "speed": {
        "repo_id": "gpustack/stable-diffusion-v1-5-GGUF",
        "filename": "stable-diffusion-v1-5-Q4_1.gguf",
        "alias": "lightning.gguf",
        "description": "Stable Diffusion 1.5 Base (Q4_1) - General-purpose base model (Needs 15-20 steps, CFG 6.0)",
        "size_mb": 1682,
        "default_steps": 20,
        "default_cfg": 6.0,
    },
    "sdxs": {
        "repo_id": "concedo/sdxs-512-tinySDdistilled-GGUF",
        "filename": "sdxs-512-tinySDdistilled_Q8_0.gguf",
        "alias": "sdxs.gguf",
        "description": "SDXS 512 Tiny SD Distilled (Q8_0) - Ultra-lightweight 1-2 step distilled model (CFG 1.0, Euler A)",
        "size_mb": 651,
        "default_steps": 2,
        "default_cfg": 1.0,
    },
    "turbo": {
        "repo_id": "second-state/stable-diffusion-v1-5-GGUF",
        "filename": "stable-diffusion-v1-5-pruned-emaonly-Q4_0.gguf",
        "alias": "turbo.gguf",
        "description": "Stable Diffusion 1.5 Pruned (Q4_0) - High-efficiency SD1.5 base model (Needs 15-20 steps, CFG 6.0)",
        "size_mb": 1494,
        "default_steps": 20,
        "default_cfg": 6.0,
    },
    "anime": {
        "repo_id": "haven-ai-companion/dreamshaper8-lcm-gguf",
        "filename": "DreamShaper8_LCM_q4_0.gguf",
        "alias": "anime.gguf",
        "description": "DreamShaper 8 LCM (Q4_0) - Fast 4-8 step LCM stylized anime & illustration art (CFG 1.5, LCM)",
        "size_mb": 1550,
        "default_steps": 6,
        "default_cfg": 1.5,
    },
})

_registry_lock = threading.Lock()
_custom_registry: Dict[str, Dict] = {}
_active_cache_dir: Optional[Path] = None

# GGUF Magic bytes: 0x47 0x47 0x55 0x46 in ASCII ("GGUF")
GGUF_MAGIC = b"GGUF"


def validate_gguf_file(file_path: Union[str, Path]) -> bool:
    """Validate whether the file is a genuine GGUF binary format by inspecting the header magic bytes & version."""
    path = Path(os.path.expanduser(str(file_path))).resolve()
    if not path.is_file():
        return False

    try:
        if path.stat().st_size < 8:
            return False
        with open(path, "rb") as f:
            header = f.read(4)
            if header != GGUF_MAGIC:
                return False
            version_bytes = f.read(4)
            if len(version_bytes) < 4:
                return False
            version = struct.unpack("<I", version_bytes)[0]
            return version in (1, 2, 3)
    except Exception as e:
        logger.debug("GGUF header validation error on %s: %s", path, e)
        return False


def verify_file_sha256(file_path: Union[str, Path], expected_sha256: str) -> bool:
    """Compute and verify SHA256 checksum for a downloaded model file."""
    path = Path(os.path.expanduser(str(file_path))).resolve()
    if not path.is_file():
        return False

    sha256_hash = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(1024 * 1024), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest().lower() == expected_sha256.lower().strip()
    except Exception as e:
        logger.error("SHA256 verification failed on %s: %s", path, e)
        return False


def set_cache_dir(path: Union[str, Path]) -> Path:
    """Explicitly set custom storage directory for model weights and caches."""
    global _active_cache_dir
    resolved = Path(os.path.expanduser(str(path))).resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    with _registry_lock:
        _active_cache_dir = resolved
    logger.info("termux-diffusion cache directory set to: %s", resolved)
    return resolved


def get_cache_dir() -> Path:
    """Get active model cache directory."""
    with _registry_lock:
        if _active_cache_dir is not None:
            return _active_cache_dir
    return get_default_cache_dir() / "models"


def register_model(
    name: str,
    repo_id: str,
    filename: str,
    alias: Optional[str] = None,
    description: Optional[str] = None,
    default_steps: int = 10,
    default_cfg: float = 4.0,
    sha256: Optional[str] = None,
    size_mb: Optional[int] = None,
    **kwargs,
) -> None:
    """Register a custom Hugging Face GGUF model into the hub catalog."""
    alias_name = str(alias) if alias else f"{name}.gguf"
    with _registry_lock:
        meta = {
            "repo_id": str(repo_id),
            "filename": str(filename),
            "alias": alias_name,
            "description": description or f"Custom model '{name}' from {repo_id}",
            "default_steps": default_steps,
            "default_cfg": default_cfg,
            "sha256": sha256,
        }
        if size_mb is not None:
            meta["size_mb"] = int(size_mb)
        meta.update(kwargs)
        _custom_registry[name] = meta
    logger.info("Registered custom model '%s' -> %s/%s", name, repo_id, filename)


def list_presets() -> Dict[str, Dict]:
    """Return dictionary of all available presets (built-in + custom)."""
    with _registry_lock:
        combined = dict(DEFAULT_PRESETS)
        combined.update(_custom_registry)
        return combined


def is_model_cached(model_name_or_path: str, cache_dir: Optional[Union[str, Path]] = None) -> bool:
    """Check if a model exists locally as an exact file or cached preset alias."""
    target_dir = Path(cache_dir).resolve() if cache_dir else get_cache_dir()

    # 1. Direct file path check
    direct_path = Path(os.path.expanduser(model_name_or_path))
    if direct_path.is_file():
        return True

    # 2. In cache directory direct filename check
    in_cache_path = target_dir / model_name_or_path
    if in_cache_path.is_file():
        return True

    # 3. Preset alias check
    presets = list_presets()
    if model_name_or_path in presets:
        alias = presets[model_name_or_path]["alias"]
        if (target_dir / alias).is_file():
            return True

    return False


def resolve_model_path(model_name_or_path: str, cache_dir: Optional[Union[str, Path]] = None) -> Path:
    """Resolve model path to an absolute Path, downloading it if not yet cached."""
    target_dir = Path(cache_dir).resolve() if cache_dir else get_cache_dir()

    # Direct file exists
    direct_path = Path(os.path.expanduser(model_name_or_path))
    if direct_path.is_file():
        return direct_path.resolve()

    # Direct filename in cache
    in_cache_path = target_dir / model_name_or_path
    if in_cache_path.is_file():
        return in_cache_path.resolve()

    # Preset alias
    presets = list_presets()
    if model_name_or_path in presets:
        alias = presets[model_name_or_path]["alias"]
        alias_path = target_dir / alias
        if alias_path.is_file():
            return alias_path.resolve()
        # Automatically download preset if not cached
        return download_model(model_name_or_path, cache_dir=target_dir)

    # Direct URL or custom HuggingFace repo identifier
    if model_name_or_path.startswith("http://") or model_name_or_path.startswith("https://") or ("/" in model_name_or_path and not Path(model_name_or_path).is_file()):
        return download_model(model_name_or_path, cache_dir=target_dir)

    raise ModelNotFoundError(
        f"Model '{model_name_or_path}' could not be resolved. "
        f"Available presets: {list(presets.keys())}, or specify a custom repo ('org/repo/file.gguf'), "
        f"a direct URL ('https://.../model.gguf'), or an existing local .gguf file path."
    )


def download_model(
    model_name_or_url: str,
    cache_dir: Optional[Union[str, Path]] = None,
    force: bool = False,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    expected_sha256: Optional[str] = None,
) -> Path:
    """Download GGUF model weights from Hugging Face or direct HTTP URL with progress display, resume capability, and checksum check."""
    target_dir = Path(cache_dir).resolve() if cache_dir else get_cache_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    presets = list_presets()
    if model_name_or_url in presets:
        info = presets[model_name_or_url]
        repo_id = info["repo_id"]
        filename = str(info["filename"])
        target_filename = str(info.get("alias") or filename)
        if expected_sha256 is None:
            expected_sha256 = info.get("sha256")
        download_url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
    elif model_name_or_url.startswith("http://") or model_name_or_url.startswith("https://"):
        # Direct URL download
        download_url = model_name_or_url
        target_filename = model_name_or_url.split("?")[0].rstrip("/").split("/")[-1]
        if not target_filename.endswith(".gguf"):
            target_filename += ".gguf"
    elif "/" in model_name_or_url:
        # Custom HuggingFace repo identifier (e.g. org/repo/file.gguf)
        parts = model_name_or_url.split("/")
        if len(parts) == 3:
            repo_id = f"{parts[0]}/{parts[1]}"
            filename = parts[2]
            target_filename = filename
            download_url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
        elif len(parts) == 2:
            repo_id = f"{parts[0]}/{parts[1]}"
            try:
                api_url = f"https://huggingface.co/api/models/{repo_id}"
                req = urllib.request.Request(api_url, headers={"User-Agent": "termux-diffusion/1.1.0"})
                with urllib.request.urlopen(req, timeout=10.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    siblings = [s.get("rfilename", "") for s in data.get("siblings", [])]
                    gguf_files = [f for f in siblings if f.endswith(".gguf")]
                    if gguf_files:
                        filename = gguf_files[0]
                        target_filename = filename
                        download_url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
                    else:
                        raise ModelNotFoundError(f"No .gguf file found in repository '{repo_id}'")
            except Exception as e:
                raise ModelNotFoundError(f"Could not inspect Hugging Face repo '{repo_id}': {e}") from e
        else:
            raise ModelNotFoundError(f"Invalid model reference: '{model_name_or_url}'")
    else:
        raise ModelNotFoundError(f"Unknown model preset: '{model_name_or_url}'. Available: {list(presets.keys())}")

    final_path = target_dir / target_filename
    if final_path.is_file() and not force:
        logger.info("Model '%s' already cached at: %s", model_name_or_url, final_path)
        return final_path

    temp_path = target_dir / f"{target_filename}.{os.getpid()}.part"
    logger.info("Downloading '%s' from %s -> %s", model_name_or_url, download_url, final_path)
    print(f"[termux-diffusion] Fetching model '{target_filename}' ({download_url})...")

    # Attempt download with streaming chunk writer and HTTP Range resume support
    try:
        _stream_download(download_url, temp_path, progress_callback)
        os.replace(temp_path, final_path)

        # Integrity Check
        if expected_sha256:
            print(f"[termux-diffusion] Verifying SHA256 integrity checksum...")
            if not verify_file_sha256(final_path, expected_sha256):
                final_path.unlink(missing_ok=True)
                raise ModelDownloadError(f"SHA256 checksum mismatch for downloaded model '{target_filename}'")

        print(f"[termux-diffusion] Successfully cached model at: {final_path}")
        return final_path
    except Exception as exc:
        temp_path.unlink(missing_ok=True)
        raise ModelDownloadError(f"Failed downloading model '{model_name_or_url}' from {download_url}: {exc}") from exc


def _stream_download(
    url: str,
    temp_path: Path,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> None:
    """Download binary file via HTTP streaming with HTTP Range resume capability and terminal progress."""
    headers = {"User-Agent": "termux-diffusion/1.1.0"}
    existing_bytes = 0

    if temp_path.exists():
        existing_bytes = temp_path.stat().st_size
        if existing_bytes > 0:
            headers["Range"] = f"bytes={existing_bytes}-"
            logger.info("Resuming partial download from byte offset %d for %s", existing_bytes, temp_path.name)

    req = urllib.request.Request(url, headers=headers)
    is_resumed = False

    resp = None
    for attempt in range(3):
        try:
            resp = urllib.request.urlopen(req, timeout=30.0)
            break
        except urllib.error.HTTPError as e:
            if e.code == 416:  # Range Not Satisfiable
                logger.debug("HTTP 416 Range Not Satisfiable; resetting temp file.")
                temp_path.unlink(missing_ok=True)
                existing_bytes = 0
                req = urllib.request.Request(url, headers={"User-Agent": "termux-diffusion/1.1.0"})
                continue
            elif e.code in (429, 503) and attempt < 2:
                import random
                retry_after = random.uniform(0.8, 1.6) * (attempt + 1)
                logger.warning("HTTP %d Rate Limited. Retrying in %.2fs with jitter (attempt %d/2)...", e.code, retry_after, attempt + 1)
                time.sleep(retry_after)
                continue
            else:
                raise

    if resp is None:
        raise ModelDownloadError(f"Failed opening connection to '{url}' after 3 attempts.")

    with resp:
        status_code = resp.status if hasattr(resp, "status") else 200
        content_len = resp.headers.get("content-length")
        server_total = int(content_len) if content_len and content_len.isdigit() else 0

        if status_code == 206:  # Partial Content
            is_resumed = True
            total_size = existing_bytes + server_total
            file_mode = "ab"
        else:
            is_resumed = False
            total_size = server_total
            file_mode = "wb"
            existing_bytes = 0

        downloaded = existing_bytes
        chunk_size = 1024 * 1024  # 1MB chunks

        try:
            with open(temp_path, file_mode) as f:
                last_print = time.time()
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    if progress_callback:
                        progress_callback(downloaded, total_size)
                    elif total_size > 0 and (time.time() - last_print > 0.5):
                        pct = (downloaded / total_size) * 100
                        mb_done = downloaded / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        print(f"  > Progress: {mb_done:.1f}MB / {mb_total:.1f}MB ({pct:.1f}%) [Resumed: {'Y' if is_resumed else 'N'}]", end="\r", flush=True)
                        last_print = time.time()

                if total_size > 0:
                    print(f"  > Progress: {total_size / (1024*1024):.1f}MB / {total_size / (1024*1024):.1f}MB (100.0%)")
        except OSError as err:
            import errno
            if err.errno == errno.ENOSPC or "space" in str(err).lower():
                temp_path.unlink(missing_ok=True)
                raise ModelDownloadError(
                    f"Insufficient disk space on device while downloading model '{temp_path.name}'. "
                    "Please free up at least 2GB of internal storage."
                ) from err
            raise

    print()  # newline after completion


def list_cached_models(cache_dir: Optional[Union[str, Path]] = None) -> List[Dict]:
    """List all currently downloaded and cached GGUF models on device."""
    target_dir = Path(cache_dir).resolve() if cache_dir else get_cache_dir()
    results = []
    if not target_dir.is_dir():
        return results

    for item in target_dir.glob("*.gguf"):
        size_mb = item.stat().st_size / (1024 * 1024)
        is_valid = validate_gguf_file(item)
        results.append({
            "name": item.name,
            "path": str(item.resolve()),
            "size_mb": round(size_mb, 2),
            "last_modified": item.stat().st_mtime,
            "is_valid_gguf": is_valid,
        })
    return results


def clear_cache(cache_dir: Optional[Union[str, Path]] = None, model_name: Optional[str] = None) -> int:
    """Clear cached models to reclaim storage space. Returns number of files removed."""
    target_dir = Path(cache_dir).resolve() if cache_dir else get_cache_dir()
    if not target_dir.is_dir():
        return 0

    removed = 0
    if model_name:
        target_file = target_dir / model_name
        if not target_file.name.endswith(".gguf"):
            target_file = target_dir / f"{model_name}.gguf"
        if target_file.is_file():
            target_file.unlink()
            removed += 1
    else:
        for item in target_dir.glob("*.gguf"):
            item.unlink()
            removed += 1

    logger.info("Cleared %d cached model file(s) from %s", removed, target_dir)
    return removed
