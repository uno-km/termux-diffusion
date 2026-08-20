"""Core generation runner, argument builder, WakeLock wrapper, and gallery bridge."""

import asyncio
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from .exceptions import InferenceTimeoutError, OOMRiskError, ProvisioningError, TermuxDiffusionError
from .hub import DEFAULT_PRESETS, list_presets, resolve_model_path
from .installer import locate_sd_cli, provision_engine
from .platform import (
    TermuxWakeLock,
    check_memory_safety,
    export_to_android_gallery,
    get_galaxy_gallery_dir,
    get_optimal_thread_count,
)

logger = logging.getLogger("termux_diffusion.core")


@dataclass
class GenerationResult:
    """Encapsulates the output and metadata of an AI diffusion generation task."""
    path: Path
    gallery_path: Optional[Path]
    prompt: str
    negative_prompt: Optional[str]
    model: str
    device: str
    steps: int
    cfg_scale: float
    width: int
    height: int
    seed: int
    elapsed_sec: float

    def __str__(self) -> str:
        return f"<GenerationResult path='{self.path}' device='{self.device}' elapsed={self.elapsed_sec:.1f}s>"


def _safe_kill_process(proc: Optional[subprocess.Popen], timeout: float = 2.0) -> None:
    """Safely terminate and reap child processes to prevent zombie handles and battery drain."""
    if proc is None or proc.poll() is not None:
        return

    pid = getattr(proc, "pid", None)
    logger.warning("Initiating child process termination (PID: %s)...", pid)

    try:
        # Step 1: Attempt graceful SIGTERM
        proc.terminate()
        try:
            proc.wait(timeout=timeout)
            logger.debug("Child process (PID: %s) gracefully exited on SIGTERM.", pid)
            return
        except subprocess.TimeoutExpired:
            logger.warning(
                "Child process (PID: %s) did not exit within %.1fs, escalating to SIGKILL...",
                pid,
                timeout,
            )

        # Step 2: Forceful SIGKILL if still alive
        proc.kill()
        try:
            proc.wait(timeout=2.0)
            logger.debug("Child process (PID: %s) forcefully terminated and reaped.", pid)
        except subprocess.TimeoutExpired:
            logger.error("Child process (PID: %s) could not be reaped after SIGKILL.", pid)
    except Exception as exc:
        logger.error("Error during child process termination (PID: %s): %s", pid, exc)


DEFAULT_QUALITY_GUARD_NEGATIVE_PROMPT = "lowres, bad quality, blur, deformed, distorted, extra limbs, artifacts"
_global_default_negative_prompt: Optional[str] = None


def get_default_negative_prompt() -> Optional[str]:
    """Get the currently configured default negative prompt (None by default)."""
    return _global_default_negative_prompt


def set_default_negative_prompt(prompt: Optional[str]) -> None:
    """Set or clear the default negative prompt used across generate() calls.
    
    Args:
        prompt: Custom negative prompt string, or None to disable default negative guidance.
    """
    global _global_default_negative_prompt
    _global_default_negative_prompt = prompt.strip() if (prompt and prompt.strip()) else None


def get_quality_guard_negative_prompt() -> str:
    """Return the recommended standard quality-guard negative prompt."""
    return DEFAULT_QUALITY_GUARD_NEGATIVE_PROMPT


def generate(
    prompt: str,
    model: str = "realistic",
    negative_prompt: Optional[str] = None,
    device: str = "cpu",
    steps: Optional[int] = None,
    cfg_scale: Optional[float] = None,
    width: int = 512,
    height: int = 512,
    seed: int = -1,
    threads: Optional[int] = None,
    output: Optional[Union[str, Path]] = None,
    export_gallery: bool = True,
    wake_lock: bool = True,
    low_ram_guard: bool = True,
    timeout: int = 1800,
) -> GenerationResult:
    """Generate an AI image on Samsung Galaxy / Android Termux using Bionic native C++ diffusion.
    
    Args:
        prompt: Detailed text description of the desired image.
        model: Preset keyword ('realistic', 'speed', 'sdxs', 'turbo', 'anime'), custom repo ('org/repo/file.gguf'), direct URL, or path to .gguf file.
        negative_prompt: Optional negative text guidance describing elements to avoid (default: None).
        device: Computing device ('cpu', 'gpu', 'opencl', 'vulkan', 'auto'). Default is 'cpu'.
        steps: Number of denoising steps (default determined by preset, e.g. 10).
        cfg_scale: Classifier-Free Guidance scale (default determined by preset, e.g. 4.0).
        width: Output image width in pixels (default: 512).
        height: Output image height in pixels (default: 512).
        seed: Sampling RNG seed (-1 for random).
        threads: Number of CPU threads (defaults to optimal big-core cluster count, e.g. 4).
        output: Destination output filename or path.
        export_gallery: Whether to copy image to Samsung Gallery and broadcast media scanner intent.
        wake_lock: Whether to acquire Android CPU WakeLock during generation.
        low_ram_guard: Whether to verify available memory before starting inference. Raises OOMRiskError if RAM is below threshold.
        timeout: Maximum inference timeout in seconds (default: 1800s / 30m).
    
    Returns:
        GenerationResult: Object containing local path, gallery path, and inference metrics.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt must not be empty.")

    device_mode = device.lower().strip()
    if device_mode not in ("cpu", "gpu", "opencl", "vulkan", "npu", "tpu", "auto"):
        raise ValueError(f"Invalid device '{device}'. Options: 'cpu', 'gpu', 'opencl', 'vulkan', 'npu', 'tpu', 'auto'.")

    # Resolve device to actual available backend using hardware probing
    from .hardware import resolve_device_backend, get_sd_cli_gpu_args
    effective_device, ngl_layers = resolve_device_backend(device_mode)

    # 1. Pre-flight Memory Safety Guard
    if low_ram_guard:
        safe, msg = check_memory_safety(required_mb=1000)
        if not safe:
            logger.error("Low RAM Guard triggered: %s", msg)
            raise OOMRiskError(msg)

    # 2. Resolve Model Path & Preset Hyperparameters (Validates model name first)
    presets = list_presets()
    model_path = resolve_model_path(model)

    if steps is None:
        steps = presets.get(model, {}).get("default_steps", 10)
    if cfg_scale is None:
        cfg_scale = presets.get(model, {}).get("default_cfg", 4.0)
    if threads is None:
        threads = get_optimal_thread_count()

    # Determine effective negative prompt
    effective_negative = negative_prompt if negative_prompt is not None else _global_default_negative_prompt
    if effective_negative and not effective_negative.strip():
        effective_negative = None

    # 3. Locate or Auto-provision Native sd-cli Engine
    sd_cli = locate_sd_cli()
    if not sd_cli:
        logger.info("sd-cli binary not found in standard paths. Attempting auto-provisioning...")
        sd_cli = provision_engine()

    # 4. Determine Output Destination
    timestamp = int(time.time())
    if output:
        out_path = Path(os.path.expanduser(str(output))).resolve()
    else:
        out_dir = get_galaxy_gallery_dir()
        out_path = out_dir / f"ai_gen_{timestamp}.png"

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 5. Build Subprocess Command List (100% List argv, Zero Shell Injection Vector)
    cmd = [
        str(sd_cli),
        "-m", str(model_path),
        "-p", prompt,
        "-W", str(width),
        "-H", str(height),
        "-t", str(threads),
        "--steps", str(steps),
        "--cfg-scale", str(cfg_scale),
        "-o", str(out_path)
    ]
    if effective_negative:
        cmd.extend(["-n", effective_negative.strip()])
    if seed >= 0:
        cmd.extend(["-s", str(seed)])
    # Append GPU offloading args from hardware detection
    cmd.extend(get_sd_cli_gpu_args(effective_device, ngl_layers))

    logger.info("Executing diffusion inference: %s", " ".join(cmd[:6]) + " ...")
    print(f"[termux-diffusion] Processing inference with model='{model}' (steps={steps}, threads={threads}, device={device_mode})...")

    start_time = time.time()

    # 6. Execute with WakeLock protection
    with TermuxWakeLock(enabled=wake_lock):
        process = None
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Stream real-time progress to terminal
            if process.stdout:
                for line in process.stdout:
                    line_str = line.strip()
                    if line_str:
                        if "step" in line_str.lower() or "%" in line_str or "sampling" in line_str.lower():
                            print(f"  > {line_str}")
                        else:
                            logger.debug("sd-cli: %s", line_str)

            process.wait(timeout=timeout)
            if process.returncode != 0:
                raise TermuxDiffusionError(f"Engine process failed with return code {process.returncode}")
        except KeyboardInterrupt:
            _safe_kill_process(process)
            print("\n[termux-diffusion] Inference interrupted by user. Child processes terminated safely.")
            raise
        except subprocess.TimeoutExpired as exc:
            _safe_kill_process(process)
            raise InferenceTimeoutError(f"Diffusion generation timed out after {timeout} seconds") from exc
        except Exception:
            _safe_kill_process(process)
            raise

    elapsed = time.time() - start_time

    if not out_path.is_file():
        raise TermuxDiffusionError(f"Engine finished but output file was not created at: {out_path}")

    # 7. Samsung Gallery Export & Media Scanner Broadcast
    gallery_path = None
    if export_gallery:
        try:
            gallery_path = export_to_android_gallery(out_path)
        except Exception as e:
            logger.warning("Could not export to Android gallery: %s", e)

    print(f"[termux-diffusion] Artifact generated in {elapsed:.2f}s -> {out_path}")
    if gallery_path:
        print(f"[termux-diffusion] Synchronized to Android MediaStore: {gallery_path}")

    return GenerationResult(
        path=out_path,
        gallery_path=gallery_path,
        prompt=prompt,
        negative_prompt=negative_prompt,
        model=model,
        device=device_mode,
        steps=steps,
        cfg_scale=cfg_scale,
        width=width,
        height=height,
        seed=seed,
        elapsed_sec=elapsed
    )


async def async_generate(*args, **kwargs) -> GenerationResult:
    """Asynchronous wrapper for generate() to integrate seamlessly into asyncio event loops."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: generate(*args, **kwargs))
