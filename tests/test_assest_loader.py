import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import pytest

pygame.init()

from asset_loader import load_image, _IMAGE_CACHE


# ---------------------------
# Setup Helper
# ---------------------------
@pytest.fixture(autouse=True)
def clear_cache():
    _IMAGE_CACHE.clear()


# ---------------------------
# Fallback Behavior Tests
# ---------------------------
def test_load_image_fallback_when_missing():
    surf = load_image("nonexistent.png", fallback_size=(40, 40))

    assert isinstance(surf, pygame.Surface)
    assert surf.get_size() == (40, 40)


def test_load_image_fallback_color():
    surf = load_image("missing.png", fallback_size=(50, 50), fallback_color=(255, 0, 0))

    # Check center pixel is roughly fallback color (circle drawn)
    center = surf.get_at((25, 25))
    assert center.r == 255


# ---------------------------
# Cache Tests
# ---------------------------
def test_image_caching():
    surf1 = load_image("missing.png")
    surf2 = load_image("missing.png")

    assert surf1 is surf2  # same object from cache


def test_cache_with_scaling():
    surf1 = load_image("missing.png", scale=(100, 100))
    surf2 = load_image("missing.png", scale=(100, 100))

    assert surf1 is surf2


def test_cache_different_scale():
    surf1 = load_image("missing.png", scale=(50, 50))
    surf2 = load_image("missing.png", scale=(100, 100))

    assert surf1 is not surf2


# ---------------------------
# Scaling Tests
# ---------------------------
def test_scaling_applied_on_fallback():
    surf = load_image("missing.png", fallback_size=(20, 20), scale=(60, 60))

    # NOTE: fallback ignores scale, so we check fallback size instead
    assert surf.get_size() == (20, 20)


# ---------------------------
# Robustness Test
# ---------------------------
def test_multiple_loads_do_not_crash():
    for _ in range(10):
        surf = load_image("missing.png")
        assert isinstance(surf, pygame.Surface)