import pytest
import json
from pathlib import Path
from termux_diffusion.hub import DEFAULT_PRESETS, list_presets
from termux_diffusion.cli import main

def test_fast_preset_mapping():
    assert "fast" in DEFAULT_PRESETS
    fast = DEFAULT_PRESETS["fast"]
    assert fast["default_steps"] == 1
    assert fast["default_width"] == 256
    assert fast["default_height"] == 256
    assert fast["default_cfg"] == 1.0
    assert fast["default_sampler"] == "euler_a"
    assert fast["default_device"] == "vulkan"
    assert fast["status"] == "verified"

def test_balanced_preset_mapping():
    assert "balanced" in DEFAULT_PRESETS
    bal = DEFAULT_PRESETS["balanced"]
    assert bal["default_steps"] == 2
    assert bal["default_width"] == 512
    assert bal["default_height"] == 512
    assert bal["default_cfg"] == 1.0
    assert bal["default_sampler"] == "euler_a"
    assert bal["default_device"] == "vulkan"
    assert bal["status"] == "verified"

def test_anime_experimental_preset_mapping():
    assert "anime-experimental" in DEFAULT_PRESETS
    anime = DEFAULT_PRESETS["anime-experimental"]
    assert anime["default_steps"] == 6
    assert anime["default_cfg"] == 1.5
    assert anime["default_sampler"] == "lcm"
    assert anime["default_device"] == "vulkan"
    assert anime["default_vae_tiling"] is True
    assert anime["status"] == "verified_experimental"

def test_realistic_q4k_disabled():
    assert "realistic" in DEFAULT_PRESETS
    real = DEFAULT_PRESETS["realistic"]
    assert real.get("status") == "disabled_pending_instrumentation"

def test_validated_vulkan_profiles_json():
    json_path = Path(__file__).parent.parent / "termux_diffusion" / "data" / "validated-vulkan-profiles.json"
    assert json_path.exists()
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "profiles" in data
    s25_profile = next((p for p in data["profiles"] if p["device_model"] == "SM-S931N"), None)
    assert s25_profile is not None
    assert s25_profile["gpu"] == "Adreno (TM) 830"
    assert "fast" in s25_profile["presets"]
    assert "balanced" in s25_profile["presets"]
    assert "anime_experimental" in s25_profile["presets"]
    assert len(s25_profile["blocked"]) >= 3
