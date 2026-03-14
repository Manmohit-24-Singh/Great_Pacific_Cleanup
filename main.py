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


class VirtualJoystick:

    def __init__(self):
        self.center = pygame.math.Vector2(JOYSTICK_X, JOYSTICK_Y)
        self.knob = pygame.math.Vector2(self.center)
        self.active = False
        self.touch_id = None  # which finger is controlling this joystick

    def handle_event(self, event):
        # Works with both mouse (desktop fallback) and finger touch events
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            pos = self._get_pos(event)
            if pos and self.center.distance_to(pos) < JOYSTICK_RADIUS * 1.5:
                self.active = True
                self.touch_id = getattr(event, 'fingerId', 0)
                self._update_knob(pos)

        elif event.type in (pygame.MOUSEMOTION, pygame.FINGERMOTION):
            if self.active:
                pos = self._get_pos(event)
                if pos:
                    self._update_knob(pos)

        elif event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
            self.active = False
            self.touch_id = None
            self.knob = pygame.math.Vector2(self.center)

    def _get_pos(self, event):
        if event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            return pygame.math.Vector2(event.x * WINDOW_WIDTH, event.y * WINDOW_HEIGHT)
        elif hasattr(event, 'pos'):
            return pygame.math.Vector2(event.pos)
        return None

    def _update_knob(self, pos):
        delta = pos - self.center
        if delta.magnitude() > JOYSTICK_RADIUS:
            delta = delta.normalize() * JOYSTICK_RADIUS
        self.knob = self.center + delta

    def get_direction(self):
        """Returns a Vector2 from -1 to 1 on each axis."""
        if not self.active:
            return pygame.math.Vector2(0, 0)
        delta = self.knob - self.center
        if delta.magnitude() < 5:
            return pygame.math.Vector2(0, 0)
        return delta / JOYSTICK_RADIUS

    def draw(self, surface):
        # Outer ring
        outer = pygame.Surface((JOYSTICK_RADIUS * 2 + 4, JOYSTICK_RADIUS * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(outer, (255, 255, 255, 40),
                           (JOYSTICK_RADIUS + 2, JOYSTICK_RADIUS + 2), JOYSTICK_RADIUS, 2)
        surface.blit(outer, (int(self.center.x) - JOYSTICK_RADIUS - 2,
                              int(self.center.y) - JOYSTICK_RADIUS - 2))

        # Knob
        knob_surf = pygame.Surface((JOYSTICK_KNOB_RADIUS * 2, JOYSTICK_KNOB_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(knob_surf, (255, 255, 255, 120 if self.active else 60),
                           (JOYSTICK_KNOB_RADIUS, JOYSTICK_KNOB_RADIUS), JOYSTICK_KNOB_RADIUS)
        pygame.draw.circle(knob_surf, (255, 255, 255, 200 if self.active else 100),
                           (JOYSTICK_KNOB_RADIUS, JOYSTICK_KNOB_RADIUS), JOYSTICK_KNOB_RADIUS, 2)
        surface.blit(knob_surf, (int(self.knob.x) - JOYSTICK_KNOB_RADIUS,
                                  int(self.knob.y) - JOYSTICK_KNOB_RADIUS))


class TapButton:

    def __init__(self, x, y, w, h, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.pressed = False
        self.font = pygame.font.SysFont("impact", max(18, int(24 * SCALE)))

    def handle_event(self, event):
        pos = None
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
        elif event.type == pygame.FINGERDOWN:
            pos = (int(event.x * WINDOW_WIDTH), int(event.y * WINDOW_HEIGHT))
        if pos and self.rect.collidepoint(pos):
            self.pressed = True
            return True
        return False

    def draw(self, surface):
        color = (40, 180, 220, 200)
        btn = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(btn, (20, 60, 100, 180), (0, 0, self.rect.w, self.rect.h), border_radius=12)
        pygame.draw.rect(btn, (40, 180, 220, 180), (0, 0, self.rect.w, self.rect.h), 2, border_radius=12)
        surface.blit(btn, self.rect.topleft)
        txt = self.font.render(self.label, True, (100, 230, 255))
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2,
                            self.rect.centery - txt.get_height() // 2))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.ui = UI(self.screen)
        self.particles = ParticleSystem()

        self.bubbles = [Bubble() for _ in range(12)]

        self.shake_amount = 0
        self.shake_timer = 0

        self.ocean_gradient = self._create_ocean_gradient()

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

        self.total_time = 0

        self.high_score_path = os.path.join(os.path.dirname(__file__), "high_score.txt")
        self.high_score = self._load_high_score()

        # Virtual joystick (always present, visible only during PLAYING)
        self.joystick = VirtualJoystick()

        # Tap buttons — anchored near bottom of screen, clear of all other UI
        btn_w, btn_h = int(220 * SCALE), int(54 * SCALE)
        bx = WINDOW_WIDTH // 2 - btn_w // 2
        self.start_button = TapButton(bx, WINDOW_HEIGHT - int(110 * SCALE), btn_w, btn_h, "TAP TO PLAY")
        self.restart_button = TapButton(bx, WINDOW_HEIGHT - int(110 * SCALE), btn_w, btn_h, "TAP TO RESTART")

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

            # Keyboard — still works on desktop
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == 'MENU':
                        self.state = 'PLAYING'
                        self.reset_game()
                    elif self.state == 'GAMEOVER':
                        self.state = 'MENU'

            # Touch/tap buttons on menu and game over
            if self.state == 'MENU':
                if self.start_button.handle_event(event):
                    self.state = 'PLAYING'
                    self.reset_game()

            elif self.state == 'GAMEOVER':
                if self.restart_button.handle_event(event):
                    self.state = 'MENU'

            # Joystick only active while playing
            elif self.state == 'PLAYING':
                self.joystick.handle_event(event)

    def _load_high_score(self):
        try:
            with open(self.high_score_path, "r", encoding="utf-8") as f:
                return max(0, int(f.read().strip() or 0))
        except (FileNotFoundError, ValueError, OSError):
            return 0

    def _save_high_score(self):
        try:
            with open(self.high_score_path, "w", encoding="utf-8") as f:
                f.write(str(self.high_score))
        except OSError:
            pass

    def update(self, dt):
        self.total_time += dt

        if self.state == 'PLAYING':
            current_scroll_speed = BASE_SCROLL_SPEED + (self.spawner.difficulty_level * SCROLL_SPEED_INC)

            # Pass joystick direction into player update
            joy_dir = self.joystick.get_direction()
            self.player.update(dt, joystick_direction=joy_dir)

            self.spawner.update(dt, self.entities)
            self.entities.update(dt, current_scroll_speed)
            self.particles.update(dt)

            for ft in self.floating_texts:
                ft.update(dt)
            self.floating_texts = [ft for ft in self.floating_texts if ft.alive]

            for b in self.bubbles:
                b.update(dt, current_scroll_speed)

            self.player.trail_timer += dt
            if self.player.trail_timer > 0.06:
                self.player.trail_timer = 0
                trail_color = (255, 120, 255) if self.player.speed_boost_timer > 0 else (120, 200, 255)
                self.particles.emit_trail(self.player.pos.x, self.player.pos.y + 35, trail_color)

            self.check_collisions()

            if self.player.score > self.high_score:
                self.high_score = self.player.score
                self._save_high_score()

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

        # Reset button pressed states each frame
        self.start_button.pressed = False
        self.restart_button.pressed = False

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
                            if isinstance(ent, Hazard):
                                self.shake_amount = 15
                                self.shake_timer = 0.5
                            else:
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
            self.ui.draw_start_screen(self.total_time, self.high_score)
            self.start_button.draw(self.screen)

        elif self.state == 'PLAYING':
            self._draw_ocean()
            render_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

            for b in self.bubbles:
                b.draw(render_surf)

            self.entities.draw(render_surf)

            if self.player.sonar_timer > 0:
                pulse = int(40 + 20 * math.sin(self.total_time * 6))
                for ent in self.entities:
                    if isinstance(ent, PlasticWaste):
                        glow = pygame.Surface((60, 60), pygame.SRCALPHA)
                        pygame.draw.circle(glow, (255, 255, 0, pulse), (30, 30), 30, 2)
                        render_surf.blit(glow, (int(ent.pos.x) - 30, int(ent.pos.y) - 30))

            if self.player.eco_net_active:
                pulse = int(25 + 15 * math.sin(self.total_time * 4))
                net_glow = pygame.Surface((140, 140), pygame.SRCALPHA)
                pygame.draw.circle(net_glow, (0, 255, 255, pulse), (70, 70), 65, 2)
                render_surf.blit(net_glow, (int(self.player.pos.x) - 70, int(self.player.pos.y) - 70))

            self.ui.draw_buff_icons_near_player(self.player, render_surf)
            render_surf.blit(self.player.image, self.player.rect)
            self.particles.draw(render_surf)

            for ft in self.floating_texts:
                ft.draw(render_surf)

            self.screen.blit(render_surf, (sx, sy))
            self.ui.draw_hud(self.player, self.high_score)

            # Draw virtual joystick on top of everything
            self.joystick.draw(self.screen)

        elif self.state == 'GAMEOVER':
            self._draw_ocean()
            render_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            for b in self.bubbles:
                b.draw(render_surf)
            self.entities.draw(render_surf)
            render_surf.blit(self.player.image, self.player.rect)
            self.particles.draw(render_surf)
            self.screen.blit(render_surf, (sx, sy))
            self.ui.draw_game_over(self.player.score, self.high_score, self.total_time)
            self.restart_button.draw(self.screen)

    def _create_ocean_gradient(self):
        surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            r = int(10 + 15 * ratio)
            g = int(60 + 70 * ratio)
            b = int(130 + 70 * ratio)
            pygame.draw.line(surf, (r, g, b), (0, y), (WINDOW_WIDTH, y))
        return surf

    def _draw_ocean(self):
        self.screen.blit(self.ocean_gradient, (0, 0))
        wave_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

        for wl in self.wave_lines:
            y = (wl['y_base'] + int(self.scroll_y * 0.6)) % (WINDOW_HEIGHT + 100) - 50
            points = []
            for x in range(0, WINDOW_WIDTH + 10, 8):
                wave_y = y + math.sin(x * wl['freq'] + self.total_time * wl['speed']) * wl['amplitude']
                points.append((x, wave_y))
            if len(points) > 1:
                pygame.draw.lines(wave_surf, (180, 220, 255, wl['alpha']),
                                  False, points, wl['thickness'])

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