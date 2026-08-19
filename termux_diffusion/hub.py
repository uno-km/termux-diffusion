"""Smart Model Hub, preset management, Hugging Face streaming downloader, and local caching."""

import json
import logging
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

from .exceptions import ModelDownloadError, ModelNotFoundError
from .platform import get_default_cache_dir

logger = logging.getLogger("termux_diffusion.hub")

# Built-in Samsung Galaxy & Mobile optimized GGUF presets
DEFAULT_PRESETS: Dict[str, Dict] = {
    "realistic": {
        "repo_id": "second-state/Realistic_Vision_V6.0_B1-GGUF",
        "filename": "realisticVisionV60B1_v51HyperVAE-Q4_k.gguf",
        "alias": "realistic.gguf",
        "description": "Realistic Vision V6.0 B1 (Q4_K) — Ultra-detailed photorealistic portraits & scenes",
        "size_mb": 1620,
        "default_steps": 10,
        "default_cfg": 4.0,
    },
    "speed": {
        "repo_id": "gpustack/stable-diffusion-v1-5-GGUF",
        "filename": "stable-diffusion-v1-5-Q4_1.gguf",
        "alias": "lightning.gguf",
        "description": "Stable Diffusion 1.5 (Q4_1) — Fast general-purpose base model",
        "size_mb": 1590,
        "default_steps": 10,
        "default_cfg": 4.0,
    },
    "sdxs": {
        "repo_id": "gpustack/SDXS-512-0.9-GGUF",
        "filename": "sdxs-512-0.9-Q4_0.gguf",
        "alias": "sdxs.gguf",
        "description": "SDXS 512-0.9 (Q4_0) — Ultra-lightweight mobile-optimized 2-3 step model (~450MB)",
        "size_mb": 450,
        "default_steps": 2,
        "default_cfg": 2.0,
    },
    "turbo": {
        "repo_id": "second-state/SD-Turbo-GGUF",
        "filename": "sd-turbo-Q4_0.gguf",
        "alias": "turbo.gguf",
        "description": "SD Turbo (Q4_0) — Real-time 1-step inference model",
        "size_mb": 1200,
        "default_steps": 1,
        "default_cfg": 1.5,
    },
    "anime": {
        "repo_id": "second-state/DreamShaper-8-GGUF",
        "filename": "dreamshaper-8-Q4_k.gguf",
        "alias": "anime.gguf",
        "description": "DreamShaper 8 (Q4_K) — Stylized anime & 2.5D illustration art",
        "size_mb": 1650,
        "default_steps": 10,
        "default_cfg": 4.5,
    },
}

_custom_registry: Dict[str, Dict] = {}
_active_cache_dir: Optional[Path] = None


def set_cache_dir(path: Union[str, Path]) -> Path:
    """Explicitly set custom storage directory for model weights and caches."""
    global _active_cache_dir
    resolved = Path(os.path.expanduser(str(path))).resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    _active_cache_dir = resolved
    logger.info("termux-diffusion cache directory set to: %s", _active_cache_dir)
    return _active_cache_dir


def get_cache_dir() -> Path:
    """Get active model cache directory."""
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
) -> None:
    """Register a custom Hugging Face GGUF model into the hub catalog."""
    alias_name = alias or f"{name}.gguf"
    _custom_registry[name] = {
        "repo_id": repo_id,
        "filename": filename,
        "alias": alias_name,
        "description": description or f"Custom model '{name}' from {repo_id}",
        "default_steps": default_steps,
        "default_cfg": default_cfg,
    }
    logger.info("Registered custom model '%s' -> %s/%s", name, repo_id, filename)


def list_presets() -> Dict[str, Dict]:
    """Return dictionary of all available presets (built-in + custom)."""
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
) -> Path:
    """Download GGUF model weights from Hugging Face or direct HTTP URL with progress display and resume capability."""
    target_dir = Path(cache_dir).resolve() if cache_dir else get_cache_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    presets = list_presets()
    if model_name_or_url in presets:
        info = presets[model_name_or_url]
        repo_id = info["repo_id"]
        filename = info["filename"]
        target_filename = info.get("alias", filename)
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
            # Query Hugging Face API to find the main .gguf file in the repository
            try:
                api_url = f"https://huggingface.co/api/models/{repo_id}"
                req = urllib.request.Request(api_url, headers={"User-Agent": "termux-diffusion/1.0.0"})
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

    temp_path = target_dir / f"{target_filename}.part"
    logger.info("Downloading '%s' from %s -> %s", model_name_or_url, download_url, final_path)
    print(f"📥 [termux-diffusion] Downloading model '{target_filename}' ({download_url})...")

    # Attempt download with streaming chunk writer and resume support
    try:
        _stream_download(download_url, temp_path, progress_callback)
        temp_path.rename(final_path)
        print(f"✅ [termux-diffusion] Model downloaded & cached at: {final_path}")
        return final_path
    except Exception as exc:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass
        raise ModelDownloadError(f"Failed downloading model '{model_name_or_url}' from {download_url}: {exc}") from exc


def _stream_download(
    url: str,
    temp_path: Path,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> None:
    """Download large binary file via HTTP streaming with real-time terminal progress."""
    headers = {"User-Agent": "termux-diffusion/1.0.0"}
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, timeout=30.0) as resp:
        total_size = int(resp.headers.get("content-length", 0))
        downloaded = 0
        chunk_size = 1024 * 1024  # 1MB chunks

        with open(temp_path, "wb") as f:
            last_print = time.time()
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)

                if progress_callback:
                    progress_callback(downloaded, total_size)

                now = time.time()
                if now - last_print > 1.0 or downloaded == total_size:
                    last_print = now
                    if total_size > 0:
                        pct = (downloaded / total_size) * 100.0
                        mb_done = downloaded / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        print(f"  ⏳ Progress: {mb_done:.1f}MB / {mb_total:.1f}MB ({pct:.1f}%)", end="\r", flush=True)

    print()  # newline after completion


def list_cached_models(cache_dir: Optional[Union[str, Path]] = None) -> List[Dict]:
    """List all currently downloaded and cached GGUF models on device."""
    target_dir = Path(cache_dir).resolve() if cache_dir else get_cache_dir()
    results = []
    if not target_dir.is_dir():
        return results

    for item in target_dir.glob("*.gguf"):
        size_mb = item.stat().st_size / (1024 * 1024)
        results.append({
            "name": item.name,
            "path": str(item.resolve()),
            "size_mb": round(size_mb, 2),
            "last_modified": item.stat().st_mtime,
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
