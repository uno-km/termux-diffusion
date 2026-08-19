"""Unit tests for termux-diffusion Model Hub and cache manager."""

import os
import shutil
import tempfile
from pathlib import Path
import pytest

from termux_diffusion.hub import (
    DEFAULT_PRESETS,
    clear_cache,
    get_cache_dir,
    is_model_cached,
    list_cached_models,
    list_presets,
    register_model,
    set_cache_dir,
)
from termux_diffusion.exceptions import ModelNotFoundError


@pytest.fixture
def temp_cache():
    tmp = tempfile.mkdtemp(prefix="td_test_cache_")
    set_cache_dir(tmp)
    yield Path(tmp)
    shutil.rmtree(tmp, ignore_errors=True)


def test_default_presets_exist():
    presets = list_presets()
    assert "realistic" in presets
    assert "speed" in presets
    assert "sdxs" in presets
    assert "turbo" in presets
    assert "anime" in presets
    assert presets["realistic"]["size_mb"] > 1000
    assert presets["sdxs"]["size_mb"] == 450


def test_set_and_get_cache_dir(temp_cache):
    assert get_cache_dir() == temp_cache
    assert temp_cache.is_dir()


def test_register_custom_model(temp_cache):
    register_model(
        name="korean-portrait",
        repo_id="custom/korean-portrait-gguf",
        filename="model-q4.gguf",
        alias="korean_portrait.gguf",
        description="Custom Korean portrait model",
        default_steps=12,
        default_cfg=4.5
    )
    presets = list_presets()
    assert "korean-portrait" in presets
    assert presets["korean-portrait"]["default_steps"] == 12
    assert presets["korean-portrait"]["default_cfg"] == 4.5


def test_cached_models_lifecycle(temp_cache):
    # Initially empty
    assert len(list_cached_models(temp_cache)) == 0
    assert not is_model_cached("realistic", temp_cache)

    # Create dummy gguf file simulating cached model
    dummy_model = temp_cache / "realistic.gguf"
    dummy_model.write_bytes(b"GGUF_MOCK_DATA" * 1024)

    assert is_model_cached("realistic", temp_cache)
    cached_list = list_cached_models(temp_cache)
    assert len(cached_list) == 1
    assert cached_list[0]["name"] == "realistic.gguf"

    # Test clear_cache
    removed = clear_cache(temp_cache, "realistic")
    assert removed == 1
    assert not is_model_cached("realistic", temp_cache)
    assert len(list_cached_models(temp_cache)) == 0
