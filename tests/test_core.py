"""Unit tests for core generation runner, argument validation, and mock execution."""

import os
import subprocess
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from termux_diffusion.core import generate, async_generate, GenerationResult, _safe_kill_process
from termux_diffusion.exceptions import (
    InferenceTimeoutError,
    ModelNotFoundError,
    OOMRiskError,
    TermuxDiffusionError,
)


def test_empty_prompt_validation():
    with pytest.raises(ValueError, match="Prompt must not be empty"):
        generate("")

    with pytest.raises(ValueError, match="Prompt must not be empty"):
        generate("   ")


def test_invalid_model_preset_raises():
    with pytest.raises(ModelNotFoundError):
        generate("prompt", model="non_existent_preset_xyz_123")


def test_invalid_device_raises():
    with pytest.raises(ValueError, match="Invalid device"):
        generate("prompt", model="realistic", device="invalid_device_quantum")


def test_low_ram_guard_raises_oom_risk_error():
    """Verify that OOMRiskError is raised when low_ram_guard=True and memory is below threshold."""
    with patch("termux_diffusion.core.check_memory_safety", return_value=(False, "Insufficient RAM for test")):
        with pytest.raises(OOMRiskError, match="Insufficient RAM for test"):
            generate("a cyberpunk city", low_ram_guard=True)


def test_generate_mock_successful_execution(tmp_path):
    """Test full generate() flow with mocked sd-cli subprocess."""
    dummy_output = tmp_path / "test_out.png"
    dummy_model = tmp_path / "model.gguf"
    dummy_model.write_bytes(b"GGUF" + b"\x00" * 64)

    mock_proc = MagicMock()
    mock_proc.stdout = ["Step 1/10 (10%)\n", "Sampling finished.\n"]
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = ("", "")

    def fake_wait(timeout=None):
        # Create output file during wait to simulate sd-cli writing it
        dummy_output.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)
        return None

    mock_proc.wait.side_effect = fake_wait

    with patch("termux_diffusion.core.resolve_model_path", return_value=dummy_model), \
         patch("termux_diffusion.core.locate_sd_cli", return_value=Path("/usr/bin/sd-cli")), \
         patch("termux_diffusion.hardware.resolve_device_backend", return_value=("cpu", 0)), \
         patch("termux_diffusion.core.subprocess.Popen", return_value=mock_proc), \
         patch("termux_diffusion.core.check_memory_safety", return_value=(True, "OK")):

        result = generate(
            prompt="a futuristic galaxy robot",
            model=str(dummy_model),
            output=dummy_output,
            steps=5,
            cfg_scale=3.5,
            width=256,
            height=256,
            export_gallery=False,
            wake_lock=False,
            low_ram_guard=True
        )

        assert isinstance(result, GenerationResult)
        assert result.path == dummy_output.resolve()
        assert result.steps == 5
        assert result.cfg_scale == 3.5
        assert result.width == 256
        assert result.height == 256
        assert result.elapsed_sec >= 0


def test_generate_mock_process_failure(tmp_path):
    """Test that TermuxDiffusionError is raised when sd-cli returns non-zero code."""
    dummy_output = tmp_path / "test_out.png"
    dummy_model = tmp_path / "model.gguf"
    dummy_model.write_bytes(b"GGUF" + b"\x00" * 64)

    mock_proc = MagicMock()
    mock_proc.stdout = ["Error loading weights\n"]
    mock_proc.returncode = 1
    mock_proc.wait.return_value = None
    mock_proc.communicate.return_value = ("", "")

    with patch("termux_diffusion.core.resolve_model_path", return_value=dummy_model), \
         patch("termux_diffusion.core.locate_sd_cli", return_value=Path("/usr/bin/sd-cli")), \
         patch("termux_diffusion.hardware.resolve_device_backend", return_value=("cpu", 0)), \
         patch("termux_diffusion.core.subprocess.Popen", return_value=mock_proc), \
         patch("termux_diffusion.core.check_memory_safety", return_value=(True, "OK")):

        with pytest.raises(TermuxDiffusionError, match="Engine process failed with return code 1"):
            generate(
                prompt="test prompt",
                model=str(dummy_model),
                output=dummy_output,
                export_gallery=False,
                wake_lock=False
            )


def test_generate_mock_timeout_expired(tmp_path):
    """Test that InferenceTimeoutError is raised when subprocess times out."""
    dummy_output = tmp_path / "test_out.png"
    dummy_model = tmp_path / "model.gguf"
    dummy_model.write_bytes(b"GGUF" + b"\x00" * 64)

    mock_proc = MagicMock()
    mock_proc.stdout = []
    mock_proc.poll.return_value = None
    mock_proc.wait.side_effect = subprocess.TimeoutExpired(cmd=["sd-cli"], timeout=1)
    mock_proc.communicate.return_value = ("", "")

    with patch("termux_diffusion.core.resolve_model_path", return_value=dummy_model), \
         patch("termux_diffusion.core.locate_sd_cli", return_value=Path("/usr/bin/sd-cli")), \
         patch("termux_diffusion.hardware.resolve_device_backend", return_value=("cpu", 0)), \
         patch("termux_diffusion.core.subprocess.Popen", return_value=mock_proc), \
         patch("termux_diffusion.core.check_memory_safety", return_value=(True, "OK")):

        with pytest.raises(InferenceTimeoutError, match="timed out"):
            generate(
                prompt="test prompt",
                model=str(dummy_model),
                output=dummy_output,
                timeout=1,
                export_gallery=False,
                wake_lock=False
            )


def test_safe_kill_process():
    """Verify _safe_kill_process handles None, dead, and running processes without raising."""
    _safe_kill_process(None)

    mock_dead = MagicMock()
    mock_dead.poll.return_value = 0
    _safe_kill_process(mock_dead)
    mock_dead.kill.assert_not_called()

    mock_running = MagicMock()
    mock_running.poll.return_value = None
    _safe_kill_process(mock_running)
    mock_running.kill.assert_called_once()


@pytest.mark.asyncio
async def test_async_generate_mock(tmp_path):
    """Test async_generate wraps generate seamlessly."""
    dummy_output = tmp_path / "test_async_out.png"
    dummy_model = tmp_path / "model.gguf"
    dummy_model.write_bytes(b"GGUF" + b"\x00" * 64)

    mock_proc = MagicMock()
    mock_proc.stdout = ["Step 1/1\n"]
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = ("", "")

    def fake_wait(timeout=None):
        dummy_output.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)
        return None

    mock_proc.wait.side_effect = fake_wait

    with patch("termux_diffusion.core.resolve_model_path", return_value=dummy_model), \
         patch("termux_diffusion.core.locate_sd_cli", return_value=Path("/usr/bin/sd-cli")), \
         patch("termux_diffusion.hardware.resolve_device_backend", return_value=("cpu", 0)), \
         patch("termux_diffusion.core.subprocess.Popen", return_value=mock_proc), \
         patch("termux_diffusion.core.check_memory_safety", return_value=(True, "OK")):

        res = await async_generate(
            prompt="async test prompt",
            model=str(dummy_model),
            output=dummy_output,
            export_gallery=False,
            wake_lock=False
        )
        assert isinstance(res, GenerationResult)
        assert res.path == dummy_output.resolve()


def test_negative_prompt_configuration():
    """Test get_default_negative_prompt and set_default_negative_prompt."""
    from termux_diffusion.core import (
        get_default_negative_prompt,
        set_default_negative_prompt,
        get_quality_guard_negative_prompt,
    )

    # Initial state should be None
    set_default_negative_prompt(None)
    assert get_default_negative_prompt() is None

    # Setting custom prompt
    set_default_negative_prompt("bad anatomy, blurry")
    assert get_default_negative_prompt() == "bad anatomy, blurry"

    # Quality guard preset
    guard = get_quality_guard_negative_prompt()
    assert "lowres" in guard
    assert "blur" in guard

    # Reset back to None
    set_default_negative_prompt(None)
    assert get_default_negative_prompt() is None
