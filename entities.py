import pygame
import random
import math
from settings import *
from asset_loader import load_image

_S = BASE_ENTITY_SIZE

class ScrollingEntity(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, image_surface):
        super().__init__()
        self.image = image_surface
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = speed
        self.bob_offset = random.uniform(0, math.pi * 2)
        self.bob_speed = random.uniform(1.5, 3.0)
        self.bob_amount = random.uniform(1, 3)

    def update(self, dt, global_scroll_speed):
        self.pos.x += math.sin(self.bob_offset * 0.5) * 20 * dt
        self.pos.y += (global_scroll_speed + self.speed) * dt
        self.bob_offset += self.bob_speed * dt
        bob_x = math.sin(self.bob_offset) * self.bob_amount
        self.rect.center = (self.pos.x + bob_x, self.pos.y)

        if self.pos.y > WINDOW_HEIGHT + 150:
            self.kill()


class PlasticWaste(ScrollingEntity):
    def __init__(self, x, y):
        speed = random.uniform(-20, 20)
        size = int(_S * 0.7)
        img = load_image("plastic_waste.png", fallback_size=(size, size),
                         fallback_color=PLASTIC_COLOR, scale=(size, size))
        super().__init__(x, y, speed, img)


class MarineLife(ScrollingEntity):
    def __init__(self, x, y, animal_type):
        self.animal_type = animal_type
        added_speed = random.uniform(50, 100)

        if animal_type == 'shark':
            w, h = int(_S * 1.2), int(_S * 0.7)
            img = load_image("animal_shark.png", fallback_size=(w, h),
                             fallback_color=MARINE_LIFE_COLORS['shark'], scale=(w, h))
        elif animal_type == 'turtle':
            s = int(_S * 0.9)
            img = load_image("animal_turtle.png", fallback_size=(s, s),
                             fallback_color=MARINE_LIFE_COLORS['turtle'], scale=(s, s))
        else:
            w, h = int(_S * 0.7), int(_S * 0.5)
            img = load_image("animal_fish.png", fallback_size=(w, h),
                             fallback_color=MARINE_LIFE_COLORS['fish'], scale=(w, h))

        super().__init__(x, y, added_speed, img)


class Hazard(ScrollingEntity):
    def __init__(self, x, y, hazard_type):
        self.hazard_type = hazard_type

        if hazard_type == 'oil':
            s = int(_S * 1.2)
            img = load_image("hazard_oil.png", fallback_size=(s, s),
                             fallback_color=HAZARD_COLORS['oil'], scale=(s, s))
        elif hazard_type == 'cargo':
            w, h = int(_S * 1.0), int(_S * 0.7)
            img = load_image("hazard_cargo.png", fallback_size=(w, h),
                             fallback_color=HAZARD_COLORS['cargo'], scale=(w, h))
        else:
            w, h = int(_S * 1.4), int(_S * 0.9)
            img = load_image("hazard_wave.png", fallback_size=(w, h),
                             fallback_color=HAZARD_COLORS['wave'], scale=(w, h))

        super().__init__(x, y, 0, img)


class PowerUp(ScrollingEntity):
    POWERUP_IMAGES = {
        'eco_net': "powerup_econet.png",
        'sonar': "powerup_sonar.png",
        'turbo': "powerup_turbo.png",
        'shield': "powerup_shield.png"
    }

    def __init__(self, x, y, power_type):
        self.power_type = power_type
        color = POWERUP_COLORS.get(power_type, WHITE)
        s = int(_S * 0.7)
        filename = self.POWERUP_IMAGES.get(power_type)
        if filename:
            img = load_image(filename, fallback_size=(s, s),
                             fallback_color=color, scale=(s, s))
        else:
            img = pygame.Surface((s, s), pygame.SRCALPHA)
            pygame.draw.circle(img, color, (s // 2, s // 2), s // 2)

        super().__init__(x, y, 0, img)
        self.glow_phase = random.uniform(0, math.pi * 2)

    def update(self, dt, global_scroll_speed):
        super().update(dt, global_scroll_speed)
        self.glow_phase += 4 * dt
