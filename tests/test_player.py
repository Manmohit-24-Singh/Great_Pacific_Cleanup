import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import pytest

pygame.init()

from player import Player


# ---------------------------
# Helper Fixture
# ---------------------------
@pytest.fixture
def player():
    return Player(100, 100)


# ---------------------------
# Initialization Tests
# ---------------------------
def test_player_initial_state(player):
    assert player.lives > 0
    assert player.score == 0
    assert player.is_invulnerable is False
    assert player.shield_active is False


# ---------------------------
# Powerup Tests
# ---------------------------
def test_apply_eco_net(player):
    player.apply_powerup('eco_net')
    assert player.eco_net_active is True
    assert player.eco_net_timer == 8.0


def test_apply_turbo(player):
    player.apply_powerup('turbo')
    assert player.speed_boost_timer == 5.0


def test_apply_shield(player):
    player.apply_powerup('shield')
    assert player.shield_active is True


# ---------------------------
# Damage Tests
# ---------------------------
def test_take_damage_normal(player):
    initial_lives = player.lives
    result = player.take_damage(1)

    assert result is True
    assert player.lives == initial_lives - 1
    assert player.is_invulnerable is True


def test_take_damage_invulnerable(player):
    player.is_invulnerable = True
    initial_lives = player.lives

    result = player.take_damage(1)

    assert result is False
    assert player.lives == initial_lives


def test_take_damage_with_shield(player):
    player.shield_active = True
    initial_lives = player.lives

    result = player.take_damage(1)

    assert result is False
    assert player.lives == initial_lives
    assert player.shield_active is False
    assert player.is_invulnerable is True


def test_take_damage_hyperdrive(player):
    player.hyperdrive_active = True
    initial_lives = player.lives

    result = player.take_damage(1)

    assert result is False
    assert player.lives == initial_lives


# ---------------------------
# Timer Behavior Tests
# ---------------------------
def test_invulnerability_timer_expires(player):
    player.invulnerable_timer = 1.0
    player.is_invulnerable = True

    player.update(1.1)

    assert player.is_invulnerable is False


def test_speed_boost_timer_decreases(player):
    player.speed_boost_timer = 5.0

    player.update(1.0)

    assert player.speed_boost_timer < 5.0


def test_hyperdrive_ends(player):
    player.hyperdrive_active = True
    player.hyperdrive_timer = 0.5

    player.update(1.0)

    assert player.hyperdrive_active is False
    assert player.is_invulnerable is True


# ---------------------------
# Movement Clamp Test
# ---------------------------
def test_player_clamping(player):
    player.pos.x = -100
    player.pos.y = -100

    player.update(0)

    assert player.pos.x >= 30
    assert player.pos.y >= 50