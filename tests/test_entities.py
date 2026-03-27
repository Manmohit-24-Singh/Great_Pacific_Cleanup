import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import pytest

pygame.init()

from entities import ScrollingEntity, PlasticWaste, MarineLife, Hazard, PowerUp


# ---------------------------
# Helper Surface
# ---------------------------
def dummy_surface():
    return pygame.Surface((50, 50), pygame.SRCALPHA)


# ---------------------------
# ScrollingEntity Tests
# ---------------------------
def test_scrolling_entity_moves_down():
    surf = dummy_surface()
    entity = ScrollingEntity(100, 100, speed=50, image_surface=surf)

    initial_y = entity.pos.y
    entity.update(1.0, global_scroll_speed=100)

    assert entity.pos.y > initial_y


def test_scrolling_entity_kills_when_offscreen():
    surf = dummy_surface()
    entity = ScrollingEntity(100, 1000, speed=50, image_surface=surf)

    group = pygame.sprite.Group()
    group.add(entity)

    entity.pos.y = 2000  # force offscreen
    entity.update(0.1, global_scroll_speed=0)

    assert entity not in group


# ---------------------------
# PlasticWaste Tests
# ---------------------------
def test_plastic_waste_initialization():
    pw = PlasticWaste(100, 100)

    assert isinstance(pw, ScrollingEntity)
    assert pw.speed >= -20 and pw.speed <= 20


# ---------------------------
# MarineLife Tests
# ---------------------------
@pytest.mark.parametrize("animal_type", ["shark", "turtle", "fish"])
def test_marine_life_types(animal_type):
    ml = MarineLife(100, 100, animal_type)

    assert isinstance(ml, ScrollingEntity)
    assert ml.animal_type == animal_type


# ---------------------------
# Hazard Tests
# ---------------------------
@pytest.mark.parametrize("hazard_type", ["oil", "cargo", "wave"])
def test_hazard_types(hazard_type):
    hz = Hazard(100, 100, hazard_type)

    assert isinstance(hz, ScrollingEntity)
    assert hz.hazard_type == hazard_type


# ---------------------------
# PowerUp Tests
# ---------------------------
@pytest.mark.parametrize("power_type", ["eco_net", "turbo", "shield"])
def test_powerup_known_types(power_type):
    pu = PowerUp(100, 100, power_type)

    assert isinstance(pu, ScrollingEntity)
    assert pu.power_type == power_type


def test_powerup_unknown_type():
    pu = PowerUp(100, 100, "unknown_type")

    assert pu.power_type == "unknown_type"
    assert isinstance(pu.image, pygame.Surface)


def test_powerup_update_changes_glow():
    pu = PowerUp(100, 100, "eco_net")

    initial_phase = pu.glow_phase
    pu.update(1.0, global_scroll_speed=0)

    assert pu.glow_phase != initial_phase