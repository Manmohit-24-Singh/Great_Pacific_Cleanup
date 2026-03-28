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

def test_update_increases_difficulty_and_reduces_spawn_interval(monkeypatch):
    s = spawner.Spawner()
    group = DummyGroup()

    s.time_elapsed = spawner.DIFFICULTY_TIMER
    old_interval = s.spawn_interval

    s.update(0.1, group, hyperdrive=False)

    assert s.difficulty_level == 1
    assert s.spawn_interval == pytest.approx(old_interval-0.08)
    assert s.time_elapsed == pytest.approx(0.1)


def test_spawn_interval_has_minimum_cap():
    s = spawner.Spawner()
    group = DummyGroup()

    s.spawn_interval = 0.4
    s.time_elapsed = spawner.DIFFICULTY_TIMER

    s.update(0.1, group, hyperdrive=False)

    assert s.spawn_interval == 0.4

def test_update_spawns_first_hyperdrive_once(monkeypatch):
    monkeypatch.setattr(spawner, "PowerUp", FakePowerUp)

    s = spawner.Spawner()
    group = DummyGroup()

    s.update(4.0, group, hyperdrive=False)

    assert s.spawned_first_hyperdrive is True
    assert len(group.added) == 1
    assert group.added[0].kind == "powerup"
    assert group.added[0].powerup_type == "hyperdrive"

def test_first_hyperdrive_only_spawns_once(monkeypatch):
    monkeypatch.setattr(spawner, "PowerUp", FakePowerUp)

    s = spawner.Spawner()
    group = DummyGroup()

    s.update(4.0, group, hyperdrive=False)
    assert len(group.added) == 1

    s.update(1.0, group, hyperdrive=False)
    # no second guaranteed hyperdrive should be added automatically
    assert s.spawned_first_hyperdrive is True

def test_update_calls_spawn_entity_when_spawn_timer_reaches_interval():
    s = spawner.Spawner()
    group = DummyGroup()

    called = {"count": 0}

    def fake_spawn_entity(entity_group):
        called["count"] += 1

    s.spawn_entity = fake_spawn_entity
    s.spawn_timer = 0.9
    s.spawn_interval = 1.0

    s.update(0.1, group, hyperdrive=False)

    assert called["count"] == 1
    assert s.spawn_timer == 0

def test_spawn_entity_creates_plastic(monkeypatch):
    monkeypatch.setattr(spawner, "PlasticWaste", FakePlasticWaste)
    monkeypatch.setattr(spawner.random, "choices", lambda *args, **kwargs: ["plastic"])
    monkeypatch.setattr(spawner.random, "randint", lambda a, b: 100)

    s = spawner.Spawner()
    group = DummyGroup()

    s.spawn_entity(group)

    assert len(group.added) == 1
    ent = group.added[0]
    assert ent.kind == "plastic"
    assert ent.x == 100
    assert ent.y == 100

def test_spawn_entity_creates_marine_life(monkeypatch):
    monkeypatch.setattr(spawner, "MarineLife", FakeMarineLife)
    monkeypatch.setattr(spawner.random, "choices", lambda *args, **kwargs: ["marine_life"])
    monkeypatch.setattr(spawner.random, "choice", lambda seq: "fish")
    monkeypatch.setattr(spawner.random, "randint", lambda a, b: 75)

    s = spawner.Spawner()
    group = DummyGroup()

    s.spawn_entity(group)

    assert len(group.added) == 1
    ent = group.added[0]
    assert ent.kind == "marine_life"
    assert ent.animal == "fish"
    assert ent.x == 75
    assert ent.y == 75

def test_spawn_entity_creates_hazard(monkeypatch):
    monkeypatch.setattr(spawner, "Hazard", FakeHazard)
    monkeypatch.setattr(spawner.random, "choices", lambda *args, **kwargs: ["hazard"])
    monkeypatch.setattr(spawner.random, "choice", lambda seq: "rock")
    monkeypatch.setattr(spawner.random, "randint", lambda a, b: 60)

    s = spawner.Spawner()
    group = DummyGroup()

    s.spawn_entity(group)

    assert len(group.added) == 1
    ent = group.added[0]
    assert ent.kind == "hazard"
    assert ent.hazard_type == "rock"

def test_spawn_entity_creates_powerup(monkeypatch):
    monkeypatch.setattr(spawner, "PowerUp", FakePowerUp)

    results = [["powerup"], ["shield"]]

    def fake_choices(*args, **kwargs):
        return results.pop(0)

    monkeypatch.setattr(spawner.random, "choices", fake_choices)
    monkeypatch.setattr(spawner.random, "randint", lambda a, b: 80)

    s = spawner.Spawner()
    group = DummyGroup()

    s.spawn_entity(group)

    assert len(group.added) == 1
    ent = group.added[0]
    assert ent.kind == "powerup"
    assert ent.powerup_type == "shield"