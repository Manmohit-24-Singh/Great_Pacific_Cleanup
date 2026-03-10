import asyncio
import pygame
import sys
import os
import math
import random
from settings import *
from player import Player
from spawner import Spawner
from ui import UI
from entities import PlasticWaste, MarineLife, Hazard, PowerUp
from particles import ParticleSystem, Bubble, FloatingText


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.ui = UI(self.screen)
        self.particles = ParticleSystem()

        # Ambient ocean bubbles
        self.bubbles = [Bubble() for _ in range(12)]

        # Screen shake state
        self.shake_amount = 0
        self.shake_timer = 0

        # Pre-cached blue gradient (no AI image)
        self.ocean_gradient = self._create_ocean_gradient()

        # Pre-generate some wave line positions for animation
        self.wave_lines = []
        for i in range(20):
            self.wave_lines.append({
                'y_base': i * (WINDOW_HEIGHT // 10),
                'amplitude': random.uniform(15, 40),
                'freq': random.uniform(0.008, 0.015),
                'speed': random.uniform(0.5, 1.5),
                'alpha': random.randint(25, 60),
                'thickness': random.choice([1, 1, 2]),
            })

        # Time tracking
        self.total_time = 0

        # State
        self.state = 'MENU'
        self.reset_game()

    def reset_game(self):
        self.player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100)
        self.entities = pygame.sprite.Group()
        self.spawner = Spawner()
        self.scroll_y = 0.0
        self.particles = ParticleSystem()
        self.floating_texts = []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == 'MENU':
                        self.state = 'PLAYING'
                        self.reset_game()
                    elif self.state == 'GAMEOVER':
                        self.state = 'MENU'

    def update(self, dt):
        self.total_time += dt

        if self.state == 'PLAYING':
            current_scroll_speed = BASE_SCROLL_SPEED + (self.spawner.difficulty_level * SCROLL_SPEED_INC)

            self.player.update(dt)
            self.spawner.update(dt, self.entities)
            self.entities.update(dt, current_scroll_speed)
            self.particles.update(dt)

            # Update floating score texts
            for ft in self.floating_texts:
                ft.update(dt)
            self.floating_texts = [ft for ft in self.floating_texts if ft.alive]

            for b in self.bubbles:
                b.update(dt, current_scroll_speed)

            # Player wake trail
            self.player.trail_timer += dt
            if self.player.trail_timer > 0.06:
                self.player.trail_timer = 0
                trail_color = (255, 120, 255) if self.player.speed_boost_timer > 0 else (120, 200, 255)
                self.particles.emit_trail(self.player.pos.x, self.player.pos.y + 35, trail_color)

            self.check_collisions()

            if self.player.lives <= 0:
                self.state = 'GAMEOVER'
                self.shake_amount = 10
                self.shake_timer = 0.4

            self.scroll_y += current_scroll_speed * dt
            if self.scroll_y > WINDOW_HEIGHT:
                self.scroll_y -= WINDOW_HEIGHT

            if self.shake_timer > 0:
                self.shake_timer -= dt
                if self.shake_timer <= 0:
                    self.shake_amount = 0

    def check_collisions(self):
        collect_radius = 100 if self.player.eco_net_active else 65

        for ent in list(self.entities):
            dist = self.player.pos.distance_to(ent.pos)

            if dist < collect_radius:
                if isinstance(ent, PlasticWaste):
                    self.player.score += 10
                    self.player.speed_boost_timer = max(self.player.speed_boost_timer, 2.0)
                    self.particles.emit_collect(ent.pos.x, ent.pos.y)
                    self.floating_texts.append(
                        FloatingText(ent.pos.x - 10, ent.pos.y - 20, "+10", (100, 255, 180)))
                    ent.kill()
                elif isinstance(ent, PowerUp):
                    self.player.apply_powerup(ent.power_type)
                    self.player.score += 20
                    self.particles.emit_powerup(ent.pos.x, ent.pos.y)
                    self.floating_texts.append(
                        FloatingText(ent.pos.x - 10, ent.pos.y - 20, "+20", (255, 255, 100)))
                    ent.kill()

            hard_col_radius = 50
            if dist < hard_col_radius:
                if isinstance(ent, MarineLife) or isinstance(ent, Hazard):
                    if not self.player.is_invulnerable:
                        hit = self.player.take_damage(1)
                        if hit:
                            self.particles.emit_damage(self.player.pos.x, self.player.pos.y)
                            # Collision-type-specific shake intensity
                            if isinstance(ent, Hazard):
                                self.shake_amount = 15
                                self.shake_timer = 0.5
                            else:  # MarineLife — lighter hit
                                self.shake_amount = 5
                                self.shake_timer = 0.2
                            if isinstance(ent, Hazard) and ent.hazard_type == 'oil':
                                self.player.speed = PLAYER_SPEED * 0.5
                            else:
                                self.player.speed = PLAYER_SPEED
                            ent.kill()

    def draw(self):
        sx, sy = 0, 0
        if self.shake_amount > 0:
            sx = random.randint(-int(self.shake_amount), int(self.shake_amount))
            sy = random.randint(-int(self.shake_amount), int(self.shake_amount))
            self.shake_amount *= 0.9

        if self.state == 'MENU':
            self.ui.draw_start_screen(self.total_time)
        elif self.state == 'PLAYING':
            self._draw_ocean()

            render_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

            for b in self.bubbles:
                b.draw(render_surf)

            self.entities.draw(render_surf)

            # Sonar highlight
            if self.player.sonar_timer > 0:
                pulse = int(40 + 20 * math.sin(self.total_time * 6))
                for ent in self.entities:
                    if isinstance(ent, PlasticWaste):
                        glow = pygame.Surface((60, 60), pygame.SRCALPHA)
                        pygame.draw.circle(glow, (255, 255, 0, pulse), (30, 30), 30, 2)
                        render_surf.blit(glow, (int(ent.pos.x) - 30, int(ent.pos.y) - 30))

            # Eco net radius
            if self.player.eco_net_active:
                pulse = int(25 + 15 * math.sin(self.total_time * 4))
                net_glow = pygame.Surface((140, 140), pygame.SRCALPHA)
                pygame.draw.circle(net_glow, (0, 255, 255, pulse), (70, 70), 65, 2)
                render_surf.blit(net_glow, (int(self.player.pos.x) - 70, int(self.player.pos.y) - 70))

            # Buff icons orbiting near the player
            self.ui.draw_buff_icons_near_player(self.player, render_surf)

            render_surf.blit(self.player.image, self.player.rect)
            self.particles.draw(render_surf)

            # Floating score text
            for ft in self.floating_texts:
                ft.draw(render_surf)

            self.screen.blit(render_surf, (sx, sy))
            self.ui.draw_hud(self.player)

        elif self.state == 'GAMEOVER':
            self._draw_ocean()
            render_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            for b in self.bubbles:
                b.draw(render_surf)
            self.entities.draw(render_surf)
            render_surf.blit(self.player.image, self.player.rect)
            self.particles.draw(render_surf)
            self.screen.blit(render_surf, (sx, sy))
            self.ui.draw_game_over(self.player.score, self.total_time)

    def _create_ocean_gradient(self):
        """Pre-render a smooth blue ocean gradient."""
        surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            r = int(10 + 15 * ratio)
            g = int(60 + 70 * ratio)
            b = int(130 + 70 * ratio)
            pygame.draw.line(surf, (r, g, b), (0, y), (WINDOW_WIDTH, y))
        return surf

    def _draw_ocean(self):
        """Draw the animated ocean: gradient + scrolling wave lines + caustics."""
        self.screen.blit(self.ocean_gradient, (0, 0))

        wave_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

        # Animated wave lines that scroll with gameplay
        for wl in self.wave_lines:
            y = (wl['y_base'] + int(self.scroll_y * 0.6)) % (WINDOW_HEIGHT + 100) - 50
            points = []
            for x in range(0, WINDOW_WIDTH + 10, 8):
                wave_y = y + math.sin(x * wl['freq'] + self.total_time * wl['speed']) * wl['amplitude']
                points.append((x, wave_y))
            if len(points) > 1:
                pygame.draw.lines(wave_surf, (180, 220, 255, wl['alpha']),
                                  False, points, wl['thickness'])

        # Light caustic shimmer (subtle bright spots)
        for i in range(8):
            cx = int((math.sin(self.total_time * 0.3 + i * 1.7) * 0.5 + 0.5) * WINDOW_WIDTH)
            cy = int((math.sin(self.total_time * 0.4 + i * 2.1) * 0.5 + 0.5) * WINDOW_HEIGHT)
            size = int(20 + 10 * math.sin(self.total_time * 0.8 + i))
            alpha = int(15 + 10 * math.sin(self.total_time + i * 0.9))
            pygame.draw.circle(wave_surf, (200, 240, 255, alpha), (cx, cy), size)

        self.screen.blit(wave_surf, (0, 0))

    async def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()
            await asyncio.sleep(0)


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
