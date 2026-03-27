# particles.py
import pygame
import random
import math
from settings import *


class Particle:
    """A single ephemeral particle."""
    def __init__(self, x, y, color, vel=None, size=None, lifetime=None, gravity=0, fade=True):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vel[0] if vel else random.uniform(-80, 80)
        self.vy = vel[1] if vel else random.uniform(-120, -20)
        self.size = size if size else random.uniform(2, 5)
        self.lifetime = lifetime if lifetime else random.uniform(0.4, 1.0)
        self.max_lifetime = self.lifetime
        self.gravity = gravity
        self.fade = fade
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        ratio = max(0, self.lifetime / self.max_lifetime) if self.fade else 1
        alpha = int(255 * ratio)
        current_size = max(1, int(self.size * ratio))
        r, g, b = self.color[:3]
        # Draw with fading glow
        if current_size > 2:
            glow_surf = pygame.Surface((current_size * 4, current_size * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (r, g, b, alpha // 3), (current_size * 2, current_size * 2), current_size * 2)
            pygame.draw.circle(glow_surf, (r, g, b, alpha), (current_size * 2, current_size * 2), current_size)
            surface.blit(glow_surf, (int(self.x) - current_size * 2, int(self.y) - current_size * 2))
        else:
            pygame.draw.circle(surface, (r, g, b, max(0, alpha)), (int(self.x), int(self.y)), current_size)


class ParticleSystem:
    """Manages all particles in the game."""
    def __init__(self):
        self.particles = []

    def emit(self, x, y, colors, count=10, speed_range=100, lifetime_range=(0.3, 0.8),
             size_range=(2, 5), gravity=80, spread=360):
        for _ in range(count):
            angle = random.uniform(0, spread) * (math.pi / 180)
            spd = random.uniform(30, speed_range)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd - random.uniform(30, 80)
            color = random.choice(colors)
            size = random.uniform(*size_range)
            lt = random.uniform(*lifetime_range)
            self.particles.append(Particle(x, y, color, vel=(vx, vy), size=size, lifetime=lt, gravity=gravity))

    def emit_collect(self, x, y):
        self.emit(x, y, PARTICLE_COLORS_COLLECT, count=15, speed_range=120, gravity=50)

    def emit_damage(self, x, y):
        self.emit(x, y, PARTICLE_COLORS_DAMAGE, count=20, speed_range=180, gravity=100,
                  size_range=(3, 7), lifetime_range=(0.4, 1.0))

    def emit_powerup(self, x, y):
        self.emit(x, y, PARTICLE_COLORS_POWERUP, count=25, speed_range=150, gravity=30,
                  size_range=(2, 6), lifetime_range=(0.5, 1.2))

    def emit_trail(self, x, y, color=(100, 200, 255)):
        """Subtle engine wake trail behind the player."""
        for _ in range(2):
            vx = random.uniform(-15, 15)
            vy = random.uniform(20, 60)
            size = random.uniform(1.5, 3.5)
            self.particles.append(Particle(x, y, color, vel=(vx, vy), size=size, lifetime=0.5, gravity=10))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface):
        # Draw on a transparent overlay for clean blending
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for p in self.particles:
            p.draw(overlay)
        surface.blit(overlay, (0, 0))


class Bubble:
    """Floating background ocean bubble."""
    def __init__(self):
        self.x = random.uniform(0, WINDOW_WIDTH)
        self.y = random.uniform(WINDOW_HEIGHT, WINDOW_HEIGHT + 200)
        self.size = random.uniform(2, 6)
        self.speed = random.uniform(20, 60)
        self.wobble_amp = random.uniform(5, 15)
        self.wobble_speed = random.uniform(1, 3)
        self.phase = random.uniform(0, math.pi * 2)
        self.alpha = random.randint(30, 90)

    def update(self, dt, scroll_speed):
        self.y -= (self.speed + scroll_speed * 0.3) * dt
        self.phase += self.wobble_speed * dt
        if self.y < -20:
            self.y = WINDOW_HEIGHT + random.uniform(10, 100)
            self.x = random.uniform(0, WINDOW_WIDTH)

    def draw(self, surface):
        wx = self.x + math.sin(self.phase) * self.wobble_amp
        color = (180, 220, 255, self.alpha)
        glow_surf = pygame.Surface((int(self.size * 4), int(self.size * 4)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, color, (int(self.size * 2), int(self.size * 2)), int(self.size))
        # White highlight
        hl_size = max(1, int(self.size * 0.4))
        pygame.draw.circle(glow_surf, (255, 255, 255, self.alpha + 40), (int(self.size * 2 - 1), int(self.size * 2 - 1)), hl_size)
        surface.blit(glow_surf, (int(wx) - int(self.size * 2), int(self.y) - int(self.size * 2)))


class FloatingText:
    """Score popup text that floats upward and fades out."""
    def __init__(self, x, y, text, color=(100, 255, 180)):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = 0.8
        self.max_lifetime = 0.8
        self.alive = True
        self.vy = -60
        self.font = pygame.font.SysFont("impact", 22)

    def update(self, dt):
        self.y += self.vy * dt
        self.vy *= 0.97  # slow down
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        ratio = max(0, self.lifetime / self.max_lifetime)
        alpha = int(255 * ratio)
        # Render with shadow
        shadow = self.font.render(self.text, True, (0, 0, 0))
        shadow.set_alpha(alpha)
        surface.blit(shadow, (int(self.x) + 1, int(self.y) + 1))
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        surface.blit(text_surf, (int(self.x), int(self.y)))

