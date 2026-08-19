"""Unit tests for core generation runner and argument validation."""

import os
import pytest
from pathlib import Path

from termux_diffusion.core import generate, GenerationResult
from termux_diffusion.exceptions import ModelNotFoundError


def test_empty_prompt_validation():
    with pytest.raises(ValueError, match="Prompt must not be empty"):
        generate("")

    with pytest.raises(ValueError, match="Prompt must not be empty"):
        generate("   ")


def test_invalid_model_preset_raises():
    with pytest.raises(ModelNotFoundError):
        generate("prompt", model="non_existent_preset_xyz_123")
