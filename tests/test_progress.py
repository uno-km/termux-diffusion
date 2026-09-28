"""Tests for real-time progress parsing, ProgressInfo dataclass, callbacks, and generator streaming."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from termux_diffusion import (
    ProgressInfo,
    generate,
    generate_stream,
)
from termux_diffusion.core import PROGRESS_RE


def test_progress_info_to_dict():
    p = ProgressInfo(
        phase="sampling",
        step=3,
        total_steps=8,
        percent=37.5,
        eta_seconds=45.2,
        speed_s_per_it=15.07,
        gpu_busy=100,
        rss_mb=850.5,
        output_path="/path/to/img.png",
        elapsed_seconds=30.2,
    )
    d = p.to_dict()
    assert d["event"] == "progress"
    assert d["phase"] == "sampling"
    assert d["step"] == 3
    assert d["total_steps"] == 8
    assert d["percent"] == 37.5
    assert d["eta_seconds"] == 45.2
    assert d["speed_s"] == 15.07
    assert d["gpu_busy"] == 100
    assert d["rss_mb"] == 850.5
    assert d["output_path"] == "/path/to/img.png"
    assert d["elapsed_seconds"] == 30.2
    assert "timestamp" in d


def test_progress_re_matching():
    # Test case 1: Standard progress bar with s/it
    m = PROGRESS_RE.search("  |===>       | 3/8 - 18.23s/it\033[K")
    assert m is not None
    assert m.group(1) == "3"
    assert m.group(2) == "8"
    assert m.group(3) == "18.23"
    assert m.group(4) == "s/it"

    # Test case 2: Speed in it/s
    m2 = PROGRESS_RE.search("|==========| 5/10 - 2.50it/s")
    assert m2 is not None
    assert m2.group(1) == "5"
    assert m2.group(2) == "10"
    assert m2.group(3) == "2.50"
    assert m2.group(4) == "it/s"

    # Test case 3: Simple step count
    m3 = PROGRESS_RE.search("Euler sampling: step 7/8")
    assert m3 is not None
    assert m3.group(1) == "7"
    assert m3.group(2) == "8"


def test_generate_progress_callback(tmp_path):
    mock_model = tmp_path / "model.gguf"
    mock_model.write_text("gguf")

    mock_out = tmp_path / "out.png"

    mock_proc = MagicMock()
    mock_proc.pid = 9999
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = ("", "")
    mock_proc.stdout = [
        "sampling using Euler method\n",
        "  |===>       | 1/4 - 10.00s/it\033[K\n",
        "  |======>    | 2/4 - 10.00s/it\033[K\n",
        "  |=========> | 3/4 - 10.00s/it\033[K\n",
        "  |===========| 4/4 - 10.00s/it\033[K\n",
        "generate image completed\n"
    ]

    def fake_wait(timeout=None):
        mock_out.write_text("png_data")
        return 0
    mock_proc.wait = fake_wait

    events = []
    def on_progress(info: ProgressInfo):
        events.append(info)

    with patch("termux_diffusion.hardware.resolve_device_backend", return_value=("cpu", 0)), \
         patch("termux_diffusion.core.locate_sd_cli", return_value=tmp_path / "sd-cli"), \
         patch("termux_diffusion.core.resolve_model_path", return_value=mock_model), \
         patch("subprocess.Popen", return_value=mock_proc):

        res = generate(
            prompt="A neon cat",
            model=str(mock_model),
            output=mock_out,
            steps=4,
            progress_callback=on_progress,
            export_gallery=False,
        )

    assert res.path == mock_out
    assert len(events) >= 5
    steps_received = [e.step for e in events if e.phase == "sampling"]
    assert steps_received == [1, 2, 3, 4]

    last_sampling = [e for e in events if e.phase == "sampling"][-1]
    assert last_sampling.percent == 100.0
    assert last_sampling.total_steps == 4

    assert events[-1].phase == "complete"
    assert events[-1].output_path == str(mock_out)


def test_generate_progress_file(tmp_path):
    mock_model = tmp_path / "model.gguf"
    mock_model.write_text("gguf")

    mock_out = tmp_path / "out.png"
    pfile = tmp_path / "progress.json"

    mock_proc = MagicMock()
    mock_proc.pid = 9999
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = ("", "")
    mock_proc.stdout = [
        "sampling using Euler method\n",
        "  |=====>     | 2/4 - 5.00s/it\033[K\n",
        "generate image completed\n"
    ]

    def fake_wait(timeout=None):
        mock_out.write_text("png_data")
        return 0
    mock_proc.wait = fake_wait

    with patch("termux_diffusion.hardware.resolve_device_backend", return_value=("cpu", 0)), \
         patch("termux_diffusion.core.locate_sd_cli", return_value=tmp_path / "sd-cli"), \
         patch("termux_diffusion.core.resolve_model_path", return_value=mock_model), \
         patch("subprocess.Popen", return_value=mock_proc):

        generate(
            prompt="Test progress file",
            model=str(mock_model),
            output=mock_out,
            steps=4,
            progress_file=pfile,
            export_gallery=False,
        )

    assert pfile.is_file()
    data = json.loads(pfile.read_text())
    assert data["phase"] == "complete"
    assert data["percent"] == 100.0


def test_generate_stream(tmp_path):
    mock_model = tmp_path / "model.gguf"
    mock_model.write_text("gguf")

    mock_out = tmp_path / "out.png"

    mock_proc = MagicMock()
    mock_proc.pid = 9999
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = ("", "")
    mock_proc.stdout = [
        "sampling using Euler method\n",
        "  |=====>     | 1/2 - 5.00s/it\033[K\n",
        "  |==========| 2/2 - 5.00s/it\033[K\n",
        "generate image completed\n"
    ]

    def fake_wait(timeout=None):
        mock_out.write_text("png_data")
        return 0
    mock_proc.wait = fake_wait

    with patch("termux_diffusion.hardware.resolve_device_backend", return_value=("cpu", 0)), \
         patch("termux_diffusion.core.locate_sd_cli", return_value=tmp_path / "sd-cli"), \
         patch("termux_diffusion.core.resolve_model_path", return_value=mock_model), \
         patch("subprocess.Popen", return_value=mock_proc):

        stream_events = list(generate_stream(
            prompt="Test streaming",
            model=str(mock_model),
            output=mock_out,
            steps=2,
            export_gallery=False,
        ))

    assert len(stream_events) >= 3
    sampling_steps = [e.step for e in stream_events if e.phase == "sampling"]
    assert sampling_steps == [1, 2]
    assert stream_events[-1].phase == "complete"
