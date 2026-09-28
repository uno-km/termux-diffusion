"""Unit tests for prompt cache assetization and --no-cache bypass protocol."""

import os
import shutil
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from termux_diffusion.core import generate
from termux_diffusion.installer import install_auxiliary_assets
from termux_diffusion.cli import main


def test_auxiliary_assets_deployment(tmp_path):
    """Verify bundled prompt cache files are correctly assetized and deployed."""
    with patch("termux_diffusion.installer.get_default_cache_dir", return_value=tmp_path):
        install_auxiliary_assets()
        target_dir = tmp_path / "prompt_cache"
        assert target_dir.is_dir()
        deployed_files = list(target_dir.glob("*.json"))
        assert len(deployed_files) >= 1
        assert (target_dir / "108a7149c4e70550.json").is_file()


def test_prompt_cache_bypass_flag(tmp_path):
    """Verify that no_cache=True explicitly bypasses pre-cached prompt embedding."""
    dummy_output = tmp_path / "out.png"
    dummy_model = tmp_path / "model.gguf"
    dummy_model.write_bytes(b"GGUF" + b"\x00" * 64)

    mock_proc = MagicMock()
    mock_proc.stdout = ["Step 1/1 (100%)\n"]
    mock_proc.returncode = 0

    def fake_wait(timeout=None):
        dummy_output.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)
        return 0
    mock_proc.wait = fake_wait

    with patch("termux_diffusion.hardware.resolve_device_backend", return_value=("cpu", 0)), \
         patch("termux_diffusion.core.check_memory_safety", return_value=(True, "OK")), \
         patch("termux_diffusion.core.locate_sd_cli", return_value=tmp_path / "sd-cli"), \
         patch("termux_diffusion.core.resolve_model_path", return_value=dummy_model), \
         patch("subprocess.Popen", return_value=mock_proc), \
         patch("termux_diffusion.platform.get_default_cache_dir", return_value=tmp_path):

        # 1. Run with no_cache=True
        res = generate(
            "A cinematic photo of a neon cybernetic tiger walking in Seoul street at night",
            model=str(dummy_model),
            output=dummy_output,
            no_cache=True
        )
        assert res.path.exists()
        cache_meta = tmp_path / "prompt_cache" / "108a7149c4e70550.json"
        assert not cache_meta.exists()

        # 2. Run with no_cache=False
        res2 = generate(
            "A cinematic photo of a neon cybernetic tiger walking in Seoul street at night",
            model=str(dummy_model),
            output=dummy_output,
            no_cache=False
        )
        assert res2.path.exists()
        assert cache_meta.exists()


def test_cli_no_cache_and_non_cache_arguments():
    """Verify CLI parser correctly parses both --no-cache and --non-cache."""
    mock_res = MagicMock()
    mock_res.path.exists.return_value = True

    with patch("termux_diffusion.cli.generate", return_value=mock_res) as mock_gen:
        # Test --no-cache
        main(["generate", "test prompt", "--no-cache"])
        assert mock_gen.call_args.kwargs.get("no_cache") is True

        # Test --non-cache
        main(["generate", "test prompt", "--non-cache"])
        assert mock_gen.call_args.kwargs.get("no_cache") is True

        # Test default (cached)
        main(["generate", "test prompt"])
        assert mock_gen.call_args.kwargs.get("no_cache") is False


def test_z_image_turbo_preset_auto_binding():
    """Verify --preset z-image-turbo automatically binds DiT weights and parameters."""
    mock_res = MagicMock()
    mock_res.path.exists.return_value = True

    with patch("termux_diffusion.cli.generate", return_value=mock_res) as mock_gen:
        main(["generate", "A cyber tiger", "--preset", "z-image-turbo"])
        kwargs = mock_gen.call_args.kwargs
        assert kwargs.get("steps") == 4
        assert kwargs.get("cfg_scale") == 1.0
        assert kwargs.get("sampling_method") == "euler"
        assert "z_image_turbo" in str(kwargs.get("diffusion_model"))
        assert "Qwen3-4B" in str(kwargs.get("llm"))
        assert "z_image_ae" in str(kwargs.get("vae"))
        assert kwargs.get("vae_format") == "flux"


def test_z_image_turbo_with_fast_vae():
    """Verify --preset z-image-turbo with --fast-vae / --taesd activates TAESD and skips heavy VAE."""
    mock_res = MagicMock()
    mock_res.path.exists.return_value = True

    with patch("termux_diffusion.cli.generate", return_value=mock_res) as mock_gen:
        main(["generate", "A cyber tiger", "--preset", "z-image-turbo", "--fast-vae"])
        kwargs = mock_gen.call_args.kwargs
        assert kwargs.get("taesd") == "auto"
        assert kwargs.get("vae") is None  # heavy VAE is skipped when fast-vae is specified

