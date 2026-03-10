import pygame
import math
from settings import *
from asset_loader import load_image


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.original_image = load_image("player_boat.png", fallback_size=PLAYER_SIZE, fallback_color=WHITE, scale=PLAYER_SIZE)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))

        self.pos = pygame.math.Vector2(self.rect.center)

        # Stats
        self.lives = MAX_LIVES
        self.score = 0
        self.speed = PLAYER_SPEED

        # State
        self.is_invulnerable = False
        self.invulnerable_timer = 0.0
        self.speed_boost_timer = 0.0
        self.eco_net_timer = 0.0
        self.sonar_timer = 0.0
        self.shield_active = False
        self.eco_net_active = False

        # Visual state
        self.tilt = 0.0  # lean angle based on horizontal input
        self.trail_timer = 0.0

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0, 0)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            direction.y += 1

        if direction.magnitude() > 0:
            direction = direction.normalize()

        # Smooth tilt based on horizontal movement
        target_tilt = -direction.x * 8
        self.tilt += (target_tilt - self.tilt) * min(1, 8 * dt)

        current_speed = self.speed
        if self.speed_boost_timer > 0:
            current_speed *= 1.5
            self.speed_boost_timer -= dt

        self.pos += direction * current_speed * dt

        # Clamping
        self.pos.x = max(30, min(self.pos.x, WINDOW_WIDTH - 30))
        self.pos.y = max(50, min(self.pos.y, WINDOW_HEIGHT - 40))

        self.rect.center = self.pos

        # Invulnerability timer
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.is_invulnerable = False

        # Eco net timer
        if self.eco_net_timer > 0:
            self.eco_net_timer -= dt
            if self.eco_net_timer <= 0:
                self.eco_net_active = False

        # Sonar timer
        if self.sonar_timer > 0:
            self.sonar_timer -= dt

        # Rebuild the display image with tilt + effects
        self._rebuild_image()

    def _rebuild_image(self):
        # Apply tilt rotation
        if abs(self.tilt) > 0.5:
            self.image = pygame.transform.rotate(self.original_image, self.tilt)
        else:
            self.image = self.original_image.copy()

        # Invulnerability blink
        if self.is_invulnerable:
            alpha = 100 if int(pygame.time.get_ticks() / 80) % 2 == 0 else 255
            self.image.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)

        # Shield glow
        if self.shield_active:
            w, h = self.image.get_size()
            glow_surf = pygame.Surface((w + 16, h + 16), pygame.SRCALPHA)
            pulse = int(80 + 40 * math.sin(pygame.time.get_ticks() / 200))
            pygame.draw.ellipse(glow_surf, (0, 255, 127, pulse), (0, 0, w + 16, h + 16), 3)
            # Re-center
            old_center = self.rect.center
            combined = pygame.Surface((w + 16, h + 16), pygame.SRCALPHA)
            combined.blit(glow_surf, (0, 0))
            combined.blit(self.image, (8, 8))
            self.image = combined
            self.rect = self.image.get_rect(center=old_center)

        # Speed boost glow
        if self.speed_boost_timer > 0:
            w, h = self.image.get_size()
            glow = pygame.Surface((w, h), pygame.SRCALPHA)
            pulse = int(30 + 20 * math.sin(pygame.time.get_ticks() / 100))
            glow.fill((255, 100, 255, pulse))
            self.image.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        self.rect = self.image.get_rect(center=self.pos)

    def apply_powerup(self, p_type):
        if p_type == 'eco_net':
            self.eco_net_active = True
            self.eco_net_timer = 8.0
        elif p_type == 'sonar':
            self.sonar_timer = 6.0
        elif p_type == 'turbo':
            self.speed_boost_timer = 5.0
        elif p_type == 'shield':
            self.shield_active = True

    def take_damage(self, amount=1):
        if self.is_invulnerable:
            return False

        if self.shield_active:
            self.shield_active = False
            self.is_invulnerable = True
            self.invulnerable_timer = 1.5
            return False

        self.lives -= amount
        self.is_invulnerable = True
        self.invulnerable_timer = 2.0
        self.speed_boost_timer = 0
        return True
