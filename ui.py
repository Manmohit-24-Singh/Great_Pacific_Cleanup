# ui.py
import pygame
import math
from settings import *


class UI:
    def __init__(self, surface):
        self.surface = surface

        try:
            self.font = pygame.font.SysFont("impact", max(16, int(26 * SCALE)))
            self.title_font = pygame.font.SysFont("impact", max(32, int(58 * SCALE)))
            self.subtitle_font = pygame.font.SysFont("impact", max(14, int(20 * SCALE)))
            self.small_font = pygame.font.SysFont("impact", max(12, int(16 * SCALE)))
            self.hud_font = pygame.font.SysFont("impact", max(14, int(24 * SCALE)))
        except Exception:
            self.font = pygame.font.SysFont(None, max(16, int(28 * SCALE)))
            self.title_font = pygame.font.SysFont(None, max(32, int(58 * SCALE)))
            self.subtitle_font = pygame.font.SysFont(None, max(14, int(22 * SCALE)))
            self.small_font = pygame.font.SysFont(None, max(12, int(18 * SCALE)))
            self.hud_font = pygame.font.SysFont(None, max(14, int(26 * SCALE)))

        self.score_pulse = 0.0
        self.last_score = 0
        self.heart_flash_timer = 0.0
        self.last_lives = MAX_LIVES

    # ── HUD ──────────────────────────────────────────────
    def draw_hud(self, player, high_score):
        if player.score != self.last_score:
            self.score_pulse = 0.4
            self.last_score = player.score
        if player.lives < self.last_lives:
            self.heart_flash_timer = 0.5
            self.last_lives = player.lives
        if player.lives > self.last_lives:
            self.last_lives = player.lives

        base_size = max(14, int(24 * SCALE))
        if self.score_pulse > 0:
            scale_factor = 1.0 + 0.3 * (self.score_pulse / 0.4)
            size = int(base_size * scale_factor)
            self.score_pulse -= 1.0 / 60
        else:
            size = base_size

        score_font = pygame.font.SysFont("impact", size)
        score_str = f"{player.score}"
        shadow = score_font.render(score_str, True, (0, 0, 0))
        self.surface.blit(shadow, (17, 17))
        score_surf = score_font.render(score_str, True, (100, 255, 200))
        self.surface.blit(score_surf, (15, 15))

        hi_surf = self.small_font.render(f"HI {high_score}", True, (190, 220, 235))
        self.surface.blit(hi_surf, (15, 48))

        heart_size = max(8, int(10 * SCALE))
        for i in range(MAX_LIVES):
            hx = WINDOW_WIDTH - int(35 * SCALE) - i * int(30 * SCALE)
            hy = 18

            if i < player.lives:
                color = (255, 60, 80)
                if self.heart_flash_timer > 0:
                    shake_x = int(math.sin(self.heart_flash_timer * 40) * 3)
                    hx += shake_x
                self._draw_heart(hx, hy, heart_size, color)
            else:
                if i == player.lives and self.heart_flash_timer > 0:
                    flash = self.heart_flash_timer / 0.5
                    r = int(255 * flash + 80 * (1 - flash))
                    g = int(20 * flash + 80 * (1 - flash))
                    b = int(20 * flash + 80 * (1 - flash))
                    self._draw_heart(hx, hy, heart_size, (r, g, b))
                else:
                    self._draw_heart(hx, hy, heart_size, (60, 60, 60))

        if self.heart_flash_timer > 0:
            self.heart_flash_timer -= 1.0 / 60

        self._draw_active_powerups(player)

    def draw_buff_icons_near_player(self, player, surface):
        icons = []
        if player.speed_boost_timer > 0:
            icons.append(POWERUP_COLORS['turbo'])
        if player.shield_active:
            icons.append(POWERUP_COLORS['shield'])
        if player.eco_net_active:
            icons.append(POWERUP_COLORS['eco_net'])
        if player.sonar_timer > 0:
            icons.append(POWERUP_COLORS['sonar'])

        if not icons:
            return

        t = pygame.time.get_ticks() / 1000.0
        for i, color in enumerate(icons):
            angle = t * 2 + i * (math.pi * 2 / len(icons))
            radius = int(45 * SCALE)
            ix = int(player.pos.x + math.cos(angle) * radius)
            iy = int(player.pos.y + math.sin(angle) * radius)
            glow = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*color[:3], 120), (8, 8), 8)
            pygame.draw.circle(glow, (*color[:3], 220), (8, 8), 4)
            surface.blit(glow, (ix - 8, iy - 8))

    def _draw_active_powerups(self, player):
        active = []
        if player.speed_boost_timer > 0:
            active.append(('TURBO', POWERUP_COLORS['turbo'], player.speed_boost_timer, 5.0))
        if player.shield_active:
            active.append(('SHIELD', POWERUP_COLORS['shield'], 1.0, 1.0))
        if player.eco_net_active:
            active.append(('NET', POWERUP_COLORS['eco_net'], player.eco_net_timer, 8.0))
        if player.sonar_timer > 0:
            active.append(('SONAR', POWERUP_COLORS['sonar'], player.sonar_timer, 6.0))

        if not active:
            return

        pill_w = max(44, int(50 * SCALE))
        gap = max(4, int(5 * SCALE))
        total_w = len(active) * (pill_w + gap)
        start_x = (WINDOW_WIDTH - total_w) // 2

        for i, (label, color, remaining, max_time) in enumerate(active):
            x = start_x + i * (pill_w + gap)
            y = 10

            pill = pygame.Surface((pill_w, 26), pygame.SRCALPHA)
            pygame.draw.rect(pill, (*color[:3], 60), (0, 0, pill_w, 26), border_radius=6)
            pygame.draw.rect(pill, (*color[:3], 180), (0, 0, pill_w, 26), 2, border_radius=6)
            self.surface.blit(pill, (x, y))

            bar_w = int((pill_w - 6) * (remaining / max_time))
            pygame.draw.rect(self.surface, (*color[:3], 200), (x + 3, y + 19, bar_w, 4), border_radius=2)

            txt = self.small_font.render(label, True, WHITE)
            self.surface.blit(txt, (x + pill_w // 2 - txt.get_width() // 2, y + 2))

    def _draw_heart(self, x, y, size, color):
        s = size
        pts = []
        for angle in range(0, 360, 8):
            rad = math.radians(angle)
            px = s * (16 * math.sin(rad) ** 3) / 16
            py = -s * (13 * math.cos(rad) - 5 * math.cos(2 * rad) - 2 * math.cos(3 * rad) - math.cos(4 * rad)) / 16
            pts.append((x + px, y + py))
        if len(pts) > 2:
            pygame.draw.polygon(self.surface, color, pts)

    # ── START SCREEN ─────────────────────────────────────
    def draw_start_screen(self, time_elapsed, high_score):
        self.surface.fill(OCEAN_DEEP)

        for y in range(0, WINDOW_HEIGHT, 4):
            ratio = y / WINDOW_HEIGHT
            r = int(5 + 15 * ratio)
            g = int(25 + 75 * ratio)
            b = int(55 + 100 * ratio)
            pygame.draw.line(self.surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))

        title_text = "GREAT PACIFIC"
        title2_text = "CLEANUP"

        shadow = self.title_font.render(title_text, True, (0, 0, 0))
        title_surf = self.title_font.render(title_text, True, (80, 220, 255))
        tx = WINDOW_WIDTH // 2 - title_surf.get_width() // 2
        ty = WINDOW_HEIGHT // 5
        self.surface.blit(shadow, (tx + 2, ty + 2))
        self.surface.blit(title_surf, (tx, ty))

        shadow2 = self.title_font.render(title2_text, True, (0, 0, 0))
        title2_surf = self.title_font.render(title2_text, True, (40, 255, 180))
        tx2 = WINDOW_WIDTH // 2 - title2_surf.get_width() // 2
        title2_y = ty + title_surf.get_height() + 4
        self.surface.blit(shadow2, (tx2 + 2, title2_y + 2))
        self.surface.blit(title2_surf, (tx2, title2_y))

        # Instructions box — positioned dynamically below titles
        box_y = title2_y + title2_surf.get_height() + 20
        box_h = int(160 * SCALE)
        box = pygame.Surface((WINDOW_WIDTH - 80, box_h), pygame.SRCALPHA)
        box.fill((10, 20, 40, 160))
        pygame.draw.rect(box, (40, 180, 220, 100), (0, 0, WINDOW_WIDTH - 80, box_h), 1, border_radius=8)
        self.surface.blit(box, (40, box_y))

        instructions = [
            ("WASD / Joystick", "Move your vessel"),
            ("Collect Plastic", "Score points"),
            ("Avoid Marine Life", "Reduces lives"),
            ("Grab Power-ups", "Shield, Turbo, Sonar"),
        ]
        row_h = box_h // len(instructions)
        for i, (key, desc) in enumerate(instructions):
            iy = box_y + i * row_h + row_h // 4
            key_surf = self.small_font.render(key, True, (100, 220, 255))
            desc_surf = self.small_font.render(f"  -  {desc}", True, (200, 210, 220))
            self.surface.blit(key_surf, (60, iy))
            self.surface.blit(desc_surf, (60 + key_surf.get_width(), iy))

        hi = self.subtitle_font.render(f"HIGH SCORE: {high_score}", True, (120, 235, 200))
        self.surface.blit(hi, (WINDOW_WIDTH // 2 - hi.get_width() // 2, box_y - 28))

        # Tap button area is BELOW the box — leave space for it (drawn by main.py)
        ver = self.small_font.render("v1.0  |  Save the Ocean", True, (80, 100, 120))
        self.surface.blit(ver, (WINDOW_WIDTH // 2 - ver.get_width() // 2, WINDOW_HEIGHT - 20))

    # ── GAME OVER ─────────────────────────────────────
    def draw_game_over(self, score, high_score, time_elapsed):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.surface.blit(overlay, (0, 0))

        go_shadow = self.title_font.render("GAME OVER", True, (80, 0, 0))
        go_text = self.title_font.render("GAME OVER", True, (255, 60, 60))
        gx = WINDOW_WIDTH // 2 - go_text.get_width() // 2
        gy = WINDOW_HEIGHT // 5
        self.surface.blit(go_shadow, (gx + 3, gy + 3))
        self.surface.blit(go_text, (gx, gy))

        # Render text first so we can measure actual heights
        label = self.subtitle_font.render("FINAL SCORE", True, (120, 180, 200))
        sc = self.title_font.render(str(score), True, (100, 255, 200))

        padding = 16
        box_w = min(300, int(WINDOW_WIDTH * 0.85))
        box_h = padding + label.get_height() + 8 + sc.get_height() + padding
        bx = WINDOW_WIDTH // 2 - box_w // 2
        by = gy + go_text.get_height() + 20

        score_box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(score_box, (15, 25, 45, 200), (0, 0, box_w, box_h), border_radius=12)
        pygame.draw.rect(score_box, (40, 180, 220, 120), (0, 0, box_w, box_h), 2, border_radius=12)
        self.surface.blit(score_box, (bx, by))

        self.surface.blit(label, (WINDOW_WIDTH // 2 - label.get_width() // 2, by + padding))
        self.surface.blit(sc, (WINDOW_WIDTH // 2 - sc.get_width() // 2, by + padding + label.get_height() + 8))

        hi_label = self.subtitle_font.render(f"HIGH SCORE: {high_score}", True, (120, 220, 255))
        hi_y = by + box_h + 16
        self.surface.blit(hi_label, (WINDOW_WIDTH // 2 - hi_label.get_width() // 2, hi_y))

        if score == high_score and score > 0:
            new_best = self.subtitle_font.render("NEW HIGH SCORE!", True, (255, 235, 120))
            self.surface.blit(new_best, (WINDOW_WIDTH // 2 - new_best.get_width() // 2, hi_y + hi_label.get_height() + 4))
