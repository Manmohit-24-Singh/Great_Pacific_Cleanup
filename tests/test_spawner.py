import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import pytest

pygame.init()
import spawner

#dummy classes
class DummyGroup:
    def __init__(self):
        self.added = []

    def add(self, entity):
        self.added.append(entity)


class FakePlasticWaste:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kind = "plastic"


class FakeMarineLife:
    def __init__(self, x, y, animal):
        self.x = x
        self.y = y
        self.animal = animal
        self.kind = "marine_life"


class FakeHazard:
    def __init__(self, x, y, hazard_type):
        self.x = x
        self.y = y
        self.hazard_type = hazard_type
        self.kind = "hazard"


class FakePowerUp:
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.powerup_type = powerup_type
        self.kind = "powerup"

#tests:
def test_spawner_initial_state():
    s = spawner.Spawner()

    assert s.spawn_timer == 0
    assert s.spawn_interval == 1.0
    assert s.difficulty_level == 0
    assert s.time_elapsed == 0
    assert s.spawned_first_hyperdrive is False

def test_update_increases_time_elapsed_without_hyperdrive():
    s = spawner.Spawner()
    group = DummyGroup()

    s.update(0.5, group, hyperdrive=False)

    assert s.time_elapsed == 0.5

def test_update_increases_time_elapsed_faster_with_hyperdrive():
    s = spawner.Spawner()
    group = DummyGroup()

    s.update(0.5, group, hyperdrive=True)

    assert s.time_elapsed == 2.5