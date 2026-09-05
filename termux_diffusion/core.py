"""Core generation runner, argument builder, WakeLock wrapper, and gallery bridge."""

import asyncio
import logging
import os
import subprocess
import sys
import threading
import time
from collections import deque
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


VALID_SAMPLERS = {
    "euler", "euler_a", "heun", "dpm2", "dpm++2s_a", "dpm++2m", "dpm++2mv2", "ipndm", "ipndm_v", "lcm"
}
VALID_SCHEDULERS = {
    "default", "discrete", "karras", "exponential", "ays", "gits"
}


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
    sampling_method: Optional[str] = None
    schedule: Optional[str] = None
    vae_tiling: bool = False
    init_img: Optional[Path] = None
    strength: Optional[float] = None
    lora_dir: Optional[Path] = None
    clip_skip: Optional[int] = None
    control_net: Optional[Path] = None
    control_image: Optional[Path] = None
    control_strength: Optional[float] = None
    taesd: Optional[Path] = None

    def __str__(self) -> str:
        return f"<GenerationResult path='{self.path}' device='{self.device}' elapsed={self.elapsed_sec:.1f}s>"


import signal

def _safe_kill_process(proc: Optional[subprocess.Popen], timeout: float = 2.0) -> None:
    """Safely terminate and reap child process groups with granular exception handling and zero zombie leak."""
    if proc is None:
        return

    try:
        if proc.poll() is not None:
            return
    except (OSError, ValueError) as poll_err:
        logger.debug("Process poll inspection note: %s", poll_err)
        return

    pid = getattr(proc, "pid", None)
    if pid is None:
        return

    logger.warning("Initiating child process termination (PID: %s)...", pid)

    # Step 1: Graceful termination attempt (SIGTERM / proc.terminate)
    try:
        if sys.platform != "win32":
            try:
                pgid = os.getpgid(pid)
                os.killpg(pgid, signal.SIGTERM)
            except ProcessLookupError:
                logger.debug("Process group (PGID: %s) already exited.", pid)
                return
            except (OSError, PermissionError) as pg_err:
                logger.debug("killpg SIGTERM note (PGID: %s): %s, falling back to proc.terminate()", pid, pg_err)
                proc.terminate()
        else:
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
    except ProcessLookupError:
        logger.debug("Child process (PID: %s) already terminated before SIGTERM dispatch.", pid)
        return
    except PermissionError as perm_err:
        logger.warning("Permission denied while sending SIGTERM to PID %s: %s", pid, perm_err)
    except OSError as os_err:
        logger.warning("OS error during SIGTERM dispatch to PID %s: %s", pid, os_err)

    # Step 2: Forceful termination (SIGKILL / proc.kill)
    try:
        if sys.platform != "win32":
            try:
                pgid = os.getpgid(pid)
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                logger.debug("Process group (PGID: %s) already terminated.", pid)
                return
            except (OSError, PermissionError) as pg_err:
                logger.debug("killpg SIGKILL note (PGID: %s): %s, falling back to proc.kill()", pid, pg_err)
                proc.kill()
        else:
            proc.kill()

        try:
            proc.wait(timeout=2.0)
            logger.debug("Child process (PID: %s) forcefully terminated and reaped.", pid)
        except subprocess.TimeoutExpired:
            logger.error("Child process (PID: %s) did not exit after SIGKILL (kernel D-state or pending I/O).", pid)
    except ProcessLookupError:
        logger.debug("Child process (PID: %s) already reaped before SIGKILL.", pid)
    except PermissionError as perm_err:
        logger.error("Permission denied while sending SIGKILL to PID %s: %s", pid, perm_err)
    except OSError as os_err:
        logger.error("OS error during SIGKILL dispatch to PID %s: %s", pid, os_err)


DEFAULT_QUALITY_GUARD_NEGATIVE_PROMPT = "lowres, bad quality, blur, deformed, distorted, extra limbs, artifacts"
_global_default_negative_prompt: Optional[str] = None
_negative_prompt_lock = threading.Lock()


def get_default_negative_prompt() -> Optional[str]:
    """Get the currently configured default negative prompt (None by default)."""
    with _negative_prompt_lock:
        return _global_default_negative_prompt


def set_default_negative_prompt(prompt: Optional[str]) -> None:
    """Set or clear the default negative prompt used across generate() calls.
    
    Args:
        prompt: Custom negative prompt string, or None to disable default negative guidance.
    """
    global _global_default_negative_prompt
    with _negative_prompt_lock:
        if prompt is not None and not str(prompt).strip():
            _global_default_negative_prompt = None
        else:
            _global_default_negative_prompt = str(prompt).strip() if prompt is not None else None


def get_quality_guard_negative_prompt() -> str:
    """Return the recommended standard quality-guard negative prompt."""
    return DEFAULT_QUALITY_GUARD_NEGATIVE_PROMPT


def generate(
    prompt: str,
    model: str = "realistic",
    negative_prompt: Optional[str] = None,
    device: str = "auto",
    steps: Optional[int] = None,
    cfg_scale: Optional[float] = None,
    width: int = 512,
    height: int = 512,
    seed: int = -1,
    threads: Optional[int] = None,
    output: Optional[Union[str, Path]] = None,
    sampling_method: Optional[str] = None,
    schedule: Optional[str] = None,
    vae_tiling: bool = False,
    init_img: Optional[Union[str, Path]] = None,
    strength: Optional[float] = None,
    lora_dir: Optional[Union[str, Path]] = None,
    clip_skip: Optional[int] = None,
    control_net: Optional[Union[str, Path]] = None,
    control_image: Optional[Union[str, Path]] = None,
    control_strength: Optional[float] = None,
    taesd: Optional[Union[str, Path]] = None,
    export_gallery: bool = True,
    wake_lock: bool = True,
    low_ram_guard: bool = True,
    auto_provision: bool = False,
    strict_vulkan: bool = False,
    timeout: int = 1800,
    _cancel_event: Optional[threading.Event] = None,
    _proc_holder: Optional[list] = None,
) -> GenerationResult:
    """Generate an AI image on Samsung Galaxy / Android Termux using Bionic native C++ diffusion.
    
    Args:
        prompt: Detailed text description of the desired image.
        model: Preset keyword ('realistic', 'speed', 'sdxs', 'turbo', 'anime'), custom repo ('org/repo/file.gguf'), direct URL, or path to .gguf file.
        negative_prompt: Optional negative text guidance describing elements to avoid (default: None).
        device: Computing device ('auto', 'gpu', 'vulkan', 'cpu', 'opencl', 'npu', 'tpu'). Default is 'auto'.
        steps: Number of denoising steps (default determined by preset, e.g. 10).
        cfg_scale: Classifier-Free Guidance scale (default determined by preset, e.g. 4.0).
        width: Output image width in pixels (default: 512).
        height: Output image height in pixels (default: 512).
        seed: Sampling RNG seed (-1 for random).
        threads: Number of CPU threads (defaults to optimal big-core cluster count, e.g. 4).
        output: Destination output filename or path.
        sampling_method: Sampler algorithm ('euler', 'euler_a', 'heun', 'dpm2', 'dpm++2s_a', 'dpm++2m', 'dpm++2mv2', 'ipndm', 'lcm').
        schedule: Noise schedule algorithm ('default', 'discrete', 'karras', 'exponential', 'ays', 'gits').
        vae_tiling: Whether to enable VAE tiling to reduce peak memory during final image decoding by ~70%.
        init_img: Path to initial image for Img2Img synthesis.
        strength: Img2Img denoising strength (0.0 to 1.0, default: 0.75).
        lora_dir: Directory containing .gguf/.safetensors LoRA adapter weights.
        clip_skip: Number of CLIP layers to skip (1 or 2, default: None).
        control_net: Path to ControlNet model file.
        control_image: Path to ControlNet hint/guide image (e.g. pose, edges).
        control_strength: ControlNet influence strength (0.0 to 2.0, default: 0.9).
        taesd: Path to Tiny AutoEncoder (TAESD) model for ultra-fast VAE decoding.
        export_gallery: Whether to copy image to Samsung Gallery and broadcast media scanner intent.
        wake_lock: Whether to acquire Android CPU WakeLock during generation.
        low_ram_guard: Whether to verify available memory before starting inference.
        auto_provision: Whether to automatically compile the native C++ engine if missing.
        timeout: Maximum inference timeout in seconds (default: 1800s / 30m).
    
    Returns:
        GenerationResult: Object containing local path, gallery path, and inference metrics.
    """
    if not prompt or not str(prompt).strip():
        raise ValueError("Prompt must not be empty.")

    device_mode = str(device or "auto").lower().strip()
    if device_mode not in ("cpu", "gpu", "opencl", "vulkan", "npu", "tpu", "auto"):
        raise ValueError(f"Invalid device '{device}'. Options: 'auto', 'gpu', 'vulkan', 'cpu', 'opencl', 'npu', 'tpu'.")

    # Resolve device to actual available backend using hardware probing
    from .hardware import resolve_device_backend, get_sd_cli_gpu_args, get_profile_gating_manager
    effective_device, ngl_layers = resolve_device_backend(device_mode)

    # 0. Runtime Profile & Model Gating Validation (Zero Test Illusion)
    gating_mgr = get_profile_gating_manager()
    is_safe, gate_reason = gating_mgr.validate_execution(model, effective_device)
    if not is_safe:
        from .exceptions import PlatformNotSupportedError
        raise PlatformNotSupportedError(
            f"[termux-diffusion] [GATING-BLOCKED] {gate_reason}"
        )

    # 1. Pre-flight Memory Safety Inspection (Informational only, non-blocking)
    if low_ram_guard:
        safe, msg = check_memory_safety(required_mb=1200)
        if not safe:
            logger.warning("Low RAM Warning: %s", msg)

    # 2. Locate or Auto-provision Native sd-cli Engine FIRST (before downloading 1.5GB model weights)
    sd_cli = locate_sd_cli(effective_device)
    if not sd_cli:
        if auto_provision:
            logger.info("sd-cli binary not found in standard paths. Attempting auto-provisioning as requested...")
            sd_cli = provision_engine(backend=effective_device)
        else:
            logger.error("sd-cli binary not found in standard paths and auto_provision=False.")
            raise ProvisioningError(
                "Native 'sd-cli' binary not found on this system. "
                "Please run 'termux-diffusion doctor --install' or pass auto_provision=True to generate()."
            )

    # 2.1 Strict Vulkan / GPU Validation (Fail-Fast: No Silent CPU Fallback)
    if device_mode in ("vulkan", "gpu") or strict_vulkan:
        from .selftest import run_binary_self_test
        from .exceptions import PlatformNotSupportedError
        test_res = run_binary_self_test(sd_cli, expected_backend="vulkan")
        if not test_res.stage1_load_passed and test_res.error_message:
            raise PlatformNotSupportedError(
                f"Strict Vulkan execution mode requested (device='{device}'), "
                f"but the active binary '{sd_cli.name}' failed Vulkan validation: {test_res.error_message}. "
                "Execution halted strictly without silent CPU fallback."
            )

    # 3. Model Weight Resolution and Local Caching
    model_path = resolve_model_path(model)

    # 4. Resolve CPU Thread Allocation and Sampling Steps
    presets = list_presets()
    preset_info = presets.get(model, {})
    if steps is None:
        steps = preset_info.get("default_steps", 10)
    if cfg_scale is None:
        cfg_scale = preset_info.get("default_cfg", 4.0)
    if threads is None:
        threads = get_optimal_thread_count()

    # Determine default or explicit negative prompt
    effective_negative = negative_prompt
    if effective_negative is None:
        effective_negative = get_default_negative_prompt()

    # 4. Determine Output Destination
    timestamp = int(time.time())
    if output:
        out_path = Path(output).resolve()
    else:
        out_dir = get_galaxy_gallery_dir()
        out_path = out_dir / f"ai_gen_{timestamp}.png"

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 5. Build Subprocess Command List (100% List argv, Zero Shell Injection Vector)
    sanitized_prompt = str(prompt).replace("\x00", "").replace("\r\n", " ").replace("\n", " ").strip()
    cmd = [
        str(sd_cli),
        "-m", str(model_path),
        "-p", sanitized_prompt,
        "-W", str(width),
        "-H", str(height),
        "-t", str(threads),
        "--steps", str(steps),
        "--cfg-scale", str(cfg_scale),
        "-o", str(out_path)
    ]
    if effective_negative:
        sanitized_neg = str(effective_negative).replace("\x00", "").replace("\r\n", " ").replace("\n", " ").strip()
        cmd.extend(["-n", sanitized_neg])
    if seed >= 0:
        cmd.extend(["--seed", str(seed)])
    # Append GPU offloading args from hardware detection
    cmd.extend(get_sd_cli_gpu_args(effective_device, ngl_layers))

    # --- Advanced TOP 7 Parameters Integration & Defense ---
    effective_sampler = None
    if sampling_method is not None and str(sampling_method).strip():
        sm_clean = str(sampling_method).lower().strip()
        if sm_clean in VALID_SAMPLERS:
            effective_sampler = sm_clean
            cmd.extend(["--sampling-method", sm_clean])
        else:
            logger.warning(
                "Invalid sampling_method '%s'; falling back to engine default ('euler_a'). Valid: %s",
                sampling_method, ", ".join(sorted(VALID_SAMPLERS))
            )

    effective_schedule = None
    if schedule is not None and str(schedule).strip():
        sc_clean = str(schedule).lower().strip()
        if sc_clean in VALID_SCHEDULERS:
            effective_schedule = sc_clean
            if sc_clean != "default":
                cmd.extend(["--schedule", sc_clean])
        else:
            logger.warning(
                "Invalid schedule '%s'; falling back to engine default ('default'). Valid: %s",
                schedule, ", ".join(sorted(VALID_SCHEDULERS))
            )

    if vae_tiling:
        cmd.append("--vae-tiling")

    effective_init_path = None
    effective_strength = None
    if init_img is not None and str(init_img).strip():
        effective_init_path = Path(init_img).resolve()
        if not effective_init_path.is_file():
            raise FileNotFoundError(
                f"[termux-diffusion] Img2Img source image file does not exist.\n"
                f"  -> Input parameter: '{init_img}'\n"
                f"  -> Resolved absolute path: '{effective_init_path}'\n"
                f"  -> Remedy: Check if the image file exists and Termux storage permission ('termux-setup-storage') is granted."
            )
        cmd.extend(["-i", str(effective_init_path)])
        
        # Denoising strength for Img2Img
        if strength is not None:
            raw_s = float(strength)
            if raw_s < 0.0:
                logger.warning("Img2Img strength (%s) is below 0.0; auto-clamping to 0.0 (minimal change).", raw_s)
                effective_strength = 0.0
            elif raw_s > 1.0:
                logger.warning("Img2Img strength (%s) is above 1.0; auto-clamping to 1.0 (full regeneration).", raw_s)
                effective_strength = 1.0
            else:
                effective_strength = raw_s
        else:
            effective_strength = 0.75  # Standard Img2Img default
        cmd.extend(["--strength", str(effective_strength)])

    effective_lora_path = None
    if lora_dir is not None and str(lora_dir).strip():
        effective_lora_path = Path(lora_dir).resolve()
        if not effective_lora_path.is_dir():
            raise FileNotFoundError(
                f"[termux-diffusion] LoRA weights directory not found.\n"
                f"  -> Input parameter: '{lora_dir}'\n"
                f"  -> Resolved absolute path: '{effective_lora_path}'\n"
                f"  -> Remedy: Create directory or verify location containing .safetensors/.gguf LoRA adapters."
            )
        cmd.extend(["--lora-model-dir", str(effective_lora_path)])

    effective_clip_skip = None
    if clip_skip is not None:
        try:
            cs_val = int(clip_skip)
            if cs_val < 1:
                logger.warning("clip_skip (%s) is below 1; auto-clamping to 1.", cs_val)
                effective_clip_skip = 1
            elif cs_val > 2:
                logger.warning("clip_skip (%s) is above standard maximum 2; auto-clamping to 2.", cs_val)
                effective_clip_skip = 2
            else:
                effective_clip_skip = cs_val
            cmd.extend(["--clip-skip", str(effective_clip_skip)])
        except (ValueError, TypeError):
            logger.warning("Invalid clip_skip value '%s'; skipping flag.", clip_skip)

    effective_cnet_path = None
    effective_cimg_path = None
    effective_cstrength = None
    if control_net is not None and str(control_net).strip():
        effective_cnet_path = Path(control_net).resolve()
        if not effective_cnet_path.is_file():
            raise FileNotFoundError(
                f"[termux-diffusion] ControlNet model file not found.\n"
                f"  -> Input parameter: '{control_net}'\n"
                f"  -> Resolved absolute path: '{effective_cnet_path}'\n"
                f"  -> Remedy: Place valid ControlNet GGUF/model file at specified path."
            )
        cmd.extend(["--control-net", str(effective_cnet_path)])

        if control_image is not None and str(control_image).strip():
            effective_cimg_path = Path(control_image).resolve()
            if not effective_cimg_path.is_file():
                raise FileNotFoundError(
                    f"[termux-diffusion] ControlNet guide/hint image not found.\n"
                    f"  -> Input parameter: '{control_image}'\n"
                    f"  -> Resolved absolute path: '{effective_cimg_path}'\n"
                    f"  -> Remedy: Check existence of pose/edge reference image."
                )
            cmd.extend(["--control-image", str(effective_cimg_path)])

        if control_strength is not None:
            raw_cs = float(control_strength)
            if raw_cs < 0.0:
                logger.warning("ControlNet strength (%s) is below 0.0; auto-clamping to 0.0.", raw_cs)
                effective_cstrength = 0.0
            elif raw_cs > 2.0:
                logger.warning("ControlNet strength (%s) is above 2.0; auto-clamping to 2.0.", raw_cs)
                effective_cstrength = 2.0
            else:
                effective_cstrength = raw_cs
        else:
            effective_cstrength = 0.9
        cmd.extend(["--control-strength", str(effective_cstrength)])

    effective_taesd_path = None
    if taesd is not None and str(taesd).strip():
        effective_taesd_path = Path(taesd).resolve()
        if not effective_taesd_path.is_file():
            raise FileNotFoundError(
                f"[termux-diffusion] TAESD fast VAE model file not found.\n"
                f"  -> Input parameter: '{taesd}'\n"
                f"  -> Resolved absolute path: '{effective_taesd_path}'\n"
                f"  -> Remedy: Check TAESD file path or omit --taesd to use standard built-in VAE."
            )
        cmd.extend(["--taesd", str(effective_taesd_path)])

    # 5.1 Configure Environment with companion library search paths (Termux native isolation)
    env = os.environ.copy()
    prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
    lib_dirs = [
        str(sd_cli.parent),
        str(sd_cli.parent.parent / "lib"),
        str(sd_cli.parent / "lib"),
        f"{prefix}/lib",
        str(Path.home() / ".cache" / "termux-diffusion" / "lib"),
        str(Path.home() / ".cache" / "termux-diffusion" / "staging" / "lib"),
    ]
    cur_ld = env.get("LD_LIBRARY_PATH", "")
    valid_dirs = [d for d in lib_dirs if Path(d).is_dir()]
    if valid_dirs:
        env["LD_LIBRARY_PATH"] = ":".join(valid_dirs + ([cur_ld] if cur_ld else []))

    # 5.2 ameva-runtime DiffusionAdapter Binding (Vulkan / GPU mode)
    if effective_device in ("vulkan", "gpu") or device_mode in ("vulkan", "gpu"):
        try:
            from ameva_runtime import vulkan as avr
            from ameva_runtime.vulkan.adapters import DiffusionAdapter

            avr_ctx = avr.get_or_create_context(device_mode)
            report = getattr(avr_ctx, "doctor", avr.Doctor()).run_self_test(verbose=False)

            class EngineProxy:
                def __init__(self, hw):
                    self.hw_profile = hw

            from .hardware import detect_hardware_profile
            engine_proxy = EngineProxy(detect_hardware_profile())
            binding = DiffusionAdapter.bind(engine_proxy, report)
            
            cfg = getattr(binding, "config", {})
            if cfg.get("unet_tiling") and "--vae-tiling" not in cmd:
                cmd.append("--vae-tiling")

            logger.info(
                "[termux-diffusion] DiffusionAdapter bound: backend=%s, status=%s",
                cfg.get("backend", "vulkan"),
                getattr(binding.status, "name", str(binding.status))
            )
        except Exception as e:
            if device_mode in ("gpu", "vulkan") or strict_vulkan:
                from .exceptions import PlatformNotSupportedError
                raise PlatformNotSupportedError(
                    f"[termux-diffusion] [FAIL-FAST] Vulkan execution requested (device='{device_mode}'), "
                    f"but hardware validation failed: {e}"
                ) from e
            avr_ctx = None

    logger.info("Executing diffusion inference: %s", " ".join(cmd[:6]) + " ...")
    print(f"[termux-diffusion] Processing inference with model='{model}' (steps={steps}, threads={threads}, device={device_mode})...")

    start_time = time.time()

    # 6. Execute with WakeLock protection
    with TermuxWakeLock(enabled=wake_lock):
        process = None
        try:
            popen_kwargs = {
                "stdout": subprocess.PIPE,
                "stderr": subprocess.STDOUT,
                "text": True,
                "bufsize": 1,
                "universal_newlines": True,
                "env": env,
            }

            process = subprocess.Popen(cmd, **popen_kwargs)
            if _proc_holder is not None:
                _proc_holder.append(process)
            if _cancel_event and _cancel_event.is_set():
                _safe_kill_process(process)
                raise TermuxDiffusionError("Inference cancelled by caller.")

            init_logs = []
            recent_logs = deque(maxlen=20)
            # Stream real-time progress to terminal with FD safety
            if process.stdout:
                try:
                    for line in process.stdout:
                        if _cancel_event and _cancel_event.is_set():
                            _safe_kill_process(process)
                            raise TermuxDiffusionError("Inference cancelled by caller.")
                        line_str = line.strip()
                        if line_str:
                            if len(init_logs) < 50 or "ggml_vulkan" in line_str or "error" in line_str.lower() or "failed" in line_str.lower():
                                init_logs.append(line_str)
                            recent_logs.append(line_str)
                            if "step" in line_str.lower() or "%" in line_str or "sampling" in line_str.lower():
                                print(f"  > {line_str}")
                            else:
                                logger.debug("sd-cli: %s", line_str)
                finally:
                    try:
                        if hasattr(process.stdout, "close"):
                            process.stdout.close()
                    except OSError as _close_err:
                        # stdout 파이프 close 실패 — 프로세스가 이미 파이프를 닫은 경우 정상.
                        # 이 오류는 생성 성공/실패와 독립적. debug 수준 로그.
                        logger.debug("[termux-diffusion] stdout.close() OSError (pipe already closed): %s", _close_err)
                    # MemoryError 등 예상 밖 예외는 재발생



            process.wait(timeout=timeout)
            all_critical_logs = init_logs + list(recent_logs)
            if (strict_vulkan or device_mode in ("vulkan", "gpu")) and any("ggml_vulkan: No devices found" in l for l in all_critical_logs):
                raise TermuxDiffusionError(
                    "Strict Vulkan execution mode requested (--strict-vulkan or device='vulkan'), but Vulkan physical device discovery failed: 'ggml_vulkan: No devices found'."
                )
            if process.returncode != 0:
                err_detail = "\n".join(list(recent_logs)[-5:]) if recent_logs else "No engine output"
                if device_mode == "auto" and effective_device != "cpu":
                    logger.warning("[termux-diffusion] Auto-mode Vulkan execution failed (RC=%s): %s. Falling back to CPU...", process.returncode, err_detail)
                    print(f"[termux-diffusion] [Auto Fallback] Vulkan acceleration failed (RC={process.returncode}); automatically falling back to CPU...")
                    return generate(
                        prompt=prompt,
                        model=model,
                        negative_prompt=negative_prompt,
                        device="cpu",
                        steps=steps,
                        cfg_scale=cfg_scale,
                        width=width,
                        height=height,
                        seed=seed,
                        threads=threads,
                        output=output,
                        sampling_method=sampling_method,
                        schedule=schedule,
                        vae_tiling=vae_tiling,
                        init_img=init_img,
                        strength=strength,
                        lora_dir=lora_dir,
                        clip_skip=clip_skip,
                        control_net=control_net,
                        control_image=control_image,
                        control_strength=control_strength,
                        taesd=taesd,
                        export_gallery=export_gallery,
                        wake_lock=wake_lock,
                        low_ram_guard=low_ram_guard,
                        auto_provision=auto_provision,
                        strict_vulkan=False,
                        timeout=timeout,
                        _cancel_event=_cancel_event,
                        _proc_holder=_proc_holder,
                    )
                raise TermuxDiffusionError(
                    f"Engine process failed with return code {process.returncode}.\nDetails:\n{err_detail}"
                )
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
    logger.info("Generation completed in %.2fs -> %s", elapsed, out_path)
    print(f"[termux-diffusion] Artifact generated in {elapsed:.2f}s -> {out_path}")

    if not out_path.is_file():
        raise TermuxDiffusionError(f"Engine finished but output file was not created at: {out_path}")

    # 7. Android Gallery MediaStore Sync (Galaxy Gallery visibility)
    gallery_path = None
    if export_gallery:
        try:
            gallery_path = export_to_android_gallery(out_path)
            print(f"[termux-diffusion] Synchronized to Android MediaStore: {gallery_path}")
        except Exception as e:
            logger.warning("Could not export to Android gallery: %s", e)

    return GenerationResult(
        path=out_path,
        gallery_path=gallery_path,
        prompt=prompt,
        negative_prompt=negative_prompt,
        model=model,
        device=effective_device,
        steps=steps,
        cfg_scale=cfg_scale,
        width=width,
        height=height,
        seed=seed,
        elapsed_sec=elapsed,
        sampling_method=effective_sampler,
        schedule=effective_schedule,
        vae_tiling=vae_tiling,
        init_img=effective_init_path,
        strength=effective_strength,
        lora_dir=effective_lora_path,
        clip_skip=effective_clip_skip,
        control_net=effective_cnet_path,
        control_image=effective_cimg_path,
        control_strength=effective_cstrength,
        taesd=effective_taesd_path,
    )


async def async_generate(*args, **kwargs) -> GenerationResult:
    """Asynchronous wrapper for generate() with real cancellation propagation to child process."""
    cancel_event = threading.Event()
    proc_holder = []
    kwargs["_cancel_event"] = cancel_event
    kwargs["_proc_holder"] = proc_holder
    loop = asyncio.get_running_loop()
    task = loop.run_in_executor(None, lambda: generate(*args, **kwargs))
    try:
        return await task
    except asyncio.CancelledError:
        cancel_event.set()
        if proc_holder:
            _safe_kill_process(proc_holder[0])
        raise
