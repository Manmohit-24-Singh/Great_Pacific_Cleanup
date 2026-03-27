import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import pytest

pygame.init()
pygame.font.init()

from particles import Particle, ParticleSystem, Bubble, FloatingText


# ---------------------------
# Particle Tests
# ---------------------------
def test_particle_initialization():
    p = Particle(10, 20, (255, 0, 0), vel=(50, -50), size=4, lifetime=1.0)

    assert p.x == 10
    assert p.y == 20
    assert p.vx == 50
    assert p.vy == -50
    assert p.size == 4
    assert p.lifetime == 1.0
    assert p.alive is True


def test_particle_update_moves():
    p = Particle(0, 0, (255, 255, 255), vel=(10, 0), lifetime=1.0)

    p.update(1.0)

    assert p.x == 10
    assert p.lifetime < 1.0


def test_particle_dies_when_lifetime_zero():
    p = Particle(0, 0, (255, 255, 255), lifetime=0.1)

    p.update(0.2)

    assert p.alive is False


# ---------------------------
# ParticleSystem Tests
# ---------------------------
def test_emit_creates_particles():
    ps = ParticleSystem()
    ps.emit(0, 0, [(255, 0, 0)], count=5)

    assert len(ps.particles) == 5


def test_emit_collect():
    ps = ParticleSystem()
    ps.emit_collect(0, 0)

    assert len(ps.particles) == 15


def test_emit_damage():
    ps = ParticleSystem()
    ps.emit_damage(0, 0)

    assert len(ps.particles) == 20


def test_emit_powerup():
    ps = ParticleSystem()
    ps.emit_powerup(0, 0)

    assert len(ps.particles) == 25


def test_update_removes_dead_particles():
    ps = ParticleSystem()
    ps.emit(0, 0, [(255, 0, 0)], count=5)

    # Kill all particles
    for p in ps.particles:
        p.lifetime = 0

    ps.update(0.1)

    assert len(ps.particles) == 0


# ---------------------------
# Bubble Tests
# ---------------------------
def test_bubble_moves_up():
    b = Bubble()
    initial_y = b.y

    b.update(1.0, scroll_speed=0)

    assert b.y < initial_y


def test_bubble_resets_when_offscreen():
    b = Bubble()
    b.y = -50  # force offscreen

    b.update(0.1, scroll_speed=0)

    assert b.y > 0  # reset to bottom


# ---------------------------
# FloatingText Tests
# ---------------------------
def test_floating_text_moves_up():
    ft = FloatingText(0, 100, "Test")
    initial_y = ft.y

    ft.update(1.0)

    assert ft.y < initial_y


def test_floating_text_dies():
    ft = FloatingText(0, 0, "Test")

    ft.update(1.0)

    assert ft.alive is False