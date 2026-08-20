"""Command-line interface entry points for termux-diffusion."""

import argparse
import sys
from typing import List, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from .core import generate
from .hub import clear_cache, download_model, list_cached_models, list_presets
from .installer import provision_engine, run_doctor


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI router for termux-diffusion."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="termux-diffusion",
        description="Production On-Device AI Image Generation for Android Termux & Samsung Galaxy."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # generate command
    gen_parser = subparsers.add_parser("generate", help="Generate an AI image from a text prompt")
    gen_parser.add_argument("prompt", type=str, help="Text description of image")
    gen_parser.add_argument("-m", "--model", type=str, default="realistic", help="Model preset or .gguf path (default: realistic)")
    gen_parser.add_argument("-n", "--negative", type=str, default=None, help="Negative prompt")
    gen_parser.add_argument("-d", "--device", type=str, default="cpu", help="Computing device (cpu, gpu, vulkan, opencl, auto)")
    gen_parser.add_argument("-s", "--steps", type=int, default=None, help="Denoising steps")
    gen_parser.add_argument("-c", "--cfg", type=float, default=None, help="CFG guidance scale")
    gen_parser.add_argument("-W", "--width", type=int, default=512, help="Image width (default: 512)")
    gen_parser.add_argument("-H", "--height", type=int, default=512, help="Image height (default: 512)")
    gen_parser.add_argument("-t", "--threads", type=int, default=None, help="CPU threads")
    gen_parser.add_argument("--seed", type=int, default=-1, help="RNG seed (-1 for random, 0 to 4294967295)")
    gen_parser.add_argument("-o", "--output", type=str, default=None, help="Output file path")
    gen_parser.add_argument("--sampler", type=str, default=None, help="Sampler algorithm (euler, euler_a, heun, dpm2, dpm++2s_a, dpm++2m, lcm)")
    gen_parser.add_argument("--schedule", type=str, default=None, help="Noise schedule (default, discrete, karras, exponential, ays, gits)")
    gen_parser.add_argument("--vae-tiling", action="store_true", help="Enable VAE tiling for ~70% lower peak memory")
    gen_parser.add_argument("-i", "--init-img", type=str, default=None, help="Source image for Img2Img synthesis")
    gen_parser.add_argument("--strength", type=float, default=None, help="Img2Img denoising strength (0.0 to 1.0, default: 0.75)")
    gen_parser.add_argument("--lora-dir", type=str, default=None, help="Directory path containing LoRA weights")
    gen_parser.add_argument("--clip-skip", type=int, default=None, help="CLIP layers to skip (1 or 2)")
    gen_parser.add_argument("--control-net", type=str, default=None, help="Path to ControlNet model")
    gen_parser.add_argument("--control-image", type=str, default=None, help="Path to ControlNet guide image")
    gen_parser.add_argument("--control-strength", type=float, default=None, help="ControlNet strength (0.0 to 2.0, default: 0.9)")
    gen_parser.add_argument("--taesd", type=str, default=None, help="Path to Tiny AutoEncoder (TAESD) model")

    # install command
    subparsers.add_parser("install", help="Provision and compile native Bionic C++ engine")

    # doctor command
    subparsers.add_parser("doctor", help="Run 7-tier pre-flight diagnostic checks")

    # models command
    subparsers.add_parser("models", help="List available model presets and locally cached weights")

    # download command
    dl_parser = subparsers.add_parser("download", help="Pre-download a model preset or HF repo")
    dl_parser.add_argument("model", type=str, help="Model preset name (e.g. realistic, speed, sdxs, turbo, anime)")

    # clear-cache command
    subparsers.add_parser("clear-cache", help="Delete cached model files to reclaim storage")

    if not argv:
        parser.print_help()
        return 0

    args = parser.parse_args(argv)

    if args.command == "generate":
        if args.seed < -1 or args.seed > 4294967295:
            parser.error("--seed must be between -1 and 4294967295.")

        res = generate(
            prompt=args.prompt,
            model=args.model,
            negative_prompt=args.negative,
            device=args.device,
            steps=args.steps,
            cfg_scale=args.cfg,
            width=args.width,
            height=args.height,
            threads=args.threads,
            seed=args.seed,
            output=args.output,
            sampling_method=args.sampler,
            schedule=args.schedule,
            vae_tiling=args.vae_tiling,
            init_img=args.init_img,
            strength=args.strength,
            lora_dir=args.lora_dir,
            clip_skip=args.clip_skip,
            control_net=args.control_net,
            control_image=args.control_image,
            control_strength=args.control_strength,
            taesd=args.taesd,
            auto_provision=True
        )
        return 0 if res.path.exists() else 1

    elif args.command == "install":
        provision_engine(force=True)
        return 0

    elif args.command == "doctor":
        ok = run_doctor()
        return 0 if ok else 1

    elif args.command == "models":
        print("\n--- [Presets] Available Presets ---")
        for k, v in list_presets().items():
            print(f"  - {k:12} : {v['description']} ({v.get('size_mb', 0)}MB)")
        print("\n--- [Models] Locally Cached Models ---")
        cached = list_cached_models()
        if not cached:
            print("  (No models cached yet. Run 'termux-diffusion download <model>' or generate)")
        for m in cached:
            print(f"  - {m['name']:25} [{m['size_mb']} MB] -> {m['path']}")
        print()
        return 0

    elif args.command == "download":
        download_model(args.model)
        return 0

    elif args.command == "clear-cache":
        removed = clear_cache()
        print(f"[Clean] Removed {removed} cached model files.")
        return 0

    parser.print_help()
    return 0


def run_install_cli():
    """Entry point for termux-diffusion-install."""
    provision_engine(force=True)


def run_doctor_cli():
    """Entry point for termux-diffusion-doctor."""
    run_doctor()


if __name__ == "__main__":
    sys.exit(main())
