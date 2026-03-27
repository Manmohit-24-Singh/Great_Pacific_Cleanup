# asset_loader.py
"""
Simple image loader — loads PNGs from assets/, scales, and caches.
Background removal is done manually by the developer on the source PNGs.
"""
import pygame
import os
import sys

_IMAGE_CACHE = {}


def resource_path(relative_path):
    """Get absolute path to resource — works for dev and PyInstaller bundle."""
    if hasattr(sys, '_MEIPASS'):
        # Running from PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def load_image(filename, fallback_size=(50, 50), fallback_color=(255, 255, 255), scale=None):
    if scale:
        key = f"{filename}_{scale[0]}x{scale[1]}"
    else:
        key = filename

    if key in _IMAGE_CACHE:
        return _IMAGE_CACHE[key]

    path = resource_path(os.path.join("assets", filename))

    try:
        surf = pygame.image.load(path).convert_alpha()

        # Strip any solid-color background by colorkeying the top-left corner
        corner_color = surf.get_at((0, 0))
        if corner_color[3] > 200:  # Only if the corner is opaque (has a bg)
            surf.set_colorkey(corner_color[:3])
            clean = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            clean.blit(surf, (0, 0))
            surf = clean

        if scale:
            surf = pygame.transform.smoothscale(surf, scale)
    except Exception as e:
        print(f"Warning: Failed to load {filename}: {e}")
        surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
        pygame.draw.circle(surf, fallback_color,
                           (fallback_size[0] // 2, fallback_size[1] // 2),
                           fallback_size[0] // 2)

    _IMAGE_CACHE[key] = surf
    return surf

