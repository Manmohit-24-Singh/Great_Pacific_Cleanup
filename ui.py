# ui.py
import pygame
import math
from settings import *
from entities import *


class UI:
    def __init__(self, surface):
        self.surface = surface

        # Use a blocky / retro font for pixel-art aesthetic
        # Try 'impact' first, fallback to default monospace
        try:
            self.font = pygame.font.SysFont("impact", 26)
            self.title_font = pygame.font.SysFont("impact", 58)
            self.subtitle_font = pygame.font.SysFont("impact", 20)
            self.small_font = pygame.font.SysFont("impact", 16)
            self.hud_font = pygame.font.SysFont("impact", 24)
        except Exception:
            self.font = pygame.font.SysFont(None, 28)
            self.title_font = pygame.font.SysFont(None, 58)
            self.subtitle_font = pygame.font.SysFont(None, 22)
            self.small_font = pygame.font.SysFont(None, 18)
            self.hud_font = pygame.font.SysFont(None, 26)

        # Animation state
        self.score_pulse = 0.0        # counts down; >0 means score just changed
        self.last_score = 0
        self.heart_flash_timer = 0.0  # counts down; >0 means a life was just lost
        self.last_lives = MAX_LIVES

    # ── HUD ──────────────────────────────────────────────
    def draw_hud(self, player, high_score):
        """Floating HUD: no bar, elements sit directly on the ocean."""

        # ── Detect changes for animation triggers ──
        if player.score != self.last_score:
            self.score_pulse = 0.4  # 400ms pulse
            self.last_score = player.score
        if player.lives < self.last_lives:
            self.heart_flash_timer = 0.5  # 500ms flash
            self.last_lives = player.lives
        if player.lives > self.last_lives:
            self.last_lives = player.lives

        # ── Score (top-left, with drop shadow + pulse scale) ──
        base_size = 24
        if self.score_pulse > 0:
            scale_factor = 1.0 + 0.3 * (self.score_pulse / 0.4)  # shrink back
            size = int(base_size * scale_factor)
            self.score_pulse -= 1.0 / 60  # approximate dt
        else:
            size = base_size

        score_font = pygame.font.SysFont("impact", size)
        score_str = f"{player.score}"
        # Shadow
        shadow = score_font.render(score_str, True, (0, 0, 0))
        self.surface.blit(shadow, (17, 17))
        # Main text
        score_surf = score_font.render(score_str, True, (100, 255, 200))
        self.surface.blit(score_surf, (15, 15))

        hi_surf = self.small_font.render(f"HI {high_score}", True, (190, 220, 235))
        self.surface.blit(hi_surf, (15, 48))

        # ── Hearts (top-right, with shake/flash on damage) ──
        for i in range(MAX_LIVES):
            hx = WINDOW_WIDTH - 35 - i * 30
            hy = 18

            if i < player.lives:
                color = (255, 60, 80)
                # If we just lost a heart, shake the remaining ones
                if self.heart_flash_timer > 0:
                    shake_x = int(math.sin(self.heart_flash_timer * 40) * 3)
                    hx += shake_x
                self._draw_heart(hx, hy, 10, color)
            else:
                # Recently lost heart: flash bright red then fade to grey
                if i == player.lives and self.heart_flash_timer > 0:
                    flash = self.heart_flash_timer / 0.5
                    r = int(255 * flash + 80 * (1 - flash))
                    g = int(20 * flash + 80 * (1 - flash))
                    b = int(20 * flash + 80 * (1 - flash))
                    self._draw_heart(hx, hy, 10, (r, g, b))
                else:
                    self._draw_heart(hx, hy, 10, (60, 60, 60))

        if self.heart_flash_timer > 0:
            self.heart_flash_timer -= 1.0 / 60

        # ── Active Powerups (top center) ──
        self._draw_active_powerups(player)

    def draw_buff_icons_near_player(self, player, surface):
        """Draw small buff indicators orbiting near the player instead of at the HUD."""
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
            radius = 45
            ix = int(player.pos.x + math.cos(angle) * radius)
            iy = int(player.pos.y + math.sin(angle) * radius)
            # Small glowing dot
            glow = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*color[:3], 120), (8, 8), 8)
            pygame.draw.circle(glow, (*color[:3], 220), (8, 8), 4)
            surface.blit(glow, (ix - 8, iy - 8))

    def _draw_active_powerups(self, player):
        """Draw active powerup icons with timers at the top center of the HUD."""
        active = []

        if player.speed_boost_timer > 0:
            active.append(('turbo', POWERUP_COLORS['turbo'], player.speed_boost_timer, 5.0))

        if player.shield_active:
            active.append(('shield', POWERUP_COLORS['shield'], 1.0, 1.0))

        if player.eco_net_active:
            active.append(('eco_net', POWERUP_COLORS['eco_net'], player.eco_net_timer, 8.0))

        if player.sonar_timer > 0:
            active.append(('sonar', POWERUP_COLORS['sonar'], player.sonar_timer, 6.0))

        if not active:
            return

        total_w = len(active) * 75
        start_x = (WINDOW_WIDTH - total_w) // 2

        for i, (icon_key, color, remaining, max_time) in enumerate(active):
            x = start_x + i * 75
            y = 10

            # Bigger background pill
            pill = pygame.Surface((70, 40), pygame.SRCALPHA)
            pygame.draw.rect(pill, (*color[:3], 60), (0, 0, 70, 40), border_radius=8)
            pygame.draw.rect(pill, (*color[:3], 180), (0, 0, 70, 40), 2, border_radius=8)
            self.surface.blit(pill, (x, y))

            # Timer bar
            bar_w = int(64 * (remaining / max_time))
            pygame.draw.rect(self.surface, (*color[:3], 200),
                            (x + 3, y + 32, bar_w, 5), border_radius=2)

            # Load icon using the PowerUp class mapping
            filename = PowerUp.POWERUP_IMAGES.get(icon_key)
            if filename:
                try:
                    icon = load_image(filename, scale=(30, 30))
                    self.surface.blit(icon, (x + 20, y + 3))
                except:
                    pass

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

        # Simple gradient (drawn once visually, not animated)
        for y in range(0, WINDOW_HEIGHT, 4):
            ratio = y / WINDOW_HEIGHT
            r = int(5 + 15 * ratio)
            g = int(25 + 75 * ratio)
            b = int(55 + 100 * ratio)
            pygame.draw.line(self.surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))

        # Title with shadow
        title_text = "GREAT PACIFIC"
        title2_text = "CLEANUP"

        shadow = self.title_font.render(title_text, True, (0, 0, 0))
        title_surf = self.title_font.render(title_text, True, (80, 220, 255))
        tx = WINDOW_WIDTH // 2 - title_surf.get_width() // 2
        ty = WINDOW_HEIGHT // 4
        self.surface.blit(shadow, (tx + 2, ty + 2))
        self.surface.blit(title_surf, (tx, ty))

        shadow2 = self.title_font.render(title2_text, True, (0, 0, 0))
        title2_surf = self.title_font.render(title2_text, True, (40, 255, 180))
        tx2 = WINDOW_WIDTH // 2 - title2_surf.get_width() // 2
        self.surface.blit(shadow2, (tx2 + 2, ty + 62))
        self.surface.blit(title2_surf, (tx2, ty + 60))

        # Pulsing "Press SPACE" prompt
        pulse = int(180 + 75 * math.sin(time_elapsed * 3))
        prompt = self.font.render("PRESS SPACE TO BEGIN", True, (pulse, 255, pulse))
        px = WINDOW_WIDTH // 2 - prompt.get_width() // 2
        self.surface.blit(prompt, (px, WINDOW_HEIGHT // 2 + 40))

        # Instructions box
        box_y = WINDOW_HEIGHT // 2 + 100
        box = pygame.Surface((WINDOW_WIDTH - 80, 180), pygame.SRCALPHA)
        box.fill((10, 20, 40, 160))
        pygame.draw.rect(box, (40, 180, 220, 100), (0, 0, WINDOW_WIDTH - 80, 180), 1, border_radius=8)
        self.surface.blit(box, (40, box_y))

        instructions = [
            ("Arrow Keys / WASD", "Move your cleanup vessel"),
            ("Collect Plastic", "Score points + biofuel boost"),
            ("Avoid Marine Life", "Collisions reduce your lives"),
            ("Grab Power-ups", "Shield, Turbo, Sonar, Eco Net"),
        ]
        for i, (key, desc) in enumerate(instructions):
            iy = box_y + 15 + i * 40
            key_surf = self.small_font.render(key, True, (100, 220, 255))
            desc_surf = self.small_font.render(f"  -  {desc}", True, (200, 210, 220))
            self.surface.blit(key_surf, (60, iy))
            self.surface.blit(desc_surf, (60 + key_surf.get_width(), iy))

        hi = self.subtitle_font.render(f"HIGH SCORE: {high_score}", True, (120, 235, 200))
        self.surface.blit(hi, (WINDOW_WIDTH // 2 - hi.get_width() // 2, box_y - 34))

        # Version line
        ver = self.small_font.render("v1.0  |  Save the Ocean", True, (80, 100, 120))
        self.surface.blit(ver, (WINDOW_WIDTH // 2 - ver.get_width() // 2, WINDOW_HEIGHT - 40))

    # ── GAME OVER ─────────────────────────────────────
    def draw_game_over(self, score, high_score, time_elapsed):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.surface.blit(overlay, (0, 0))

        # "GAME OVER" text
        go_shadow = self.title_font.render("GAME OVER", True, (80, 0, 0))
        go_text = self.title_font.render("GAME OVER", True, (255, 60, 60))
        gx = WINDOW_WIDTH // 2 - go_text.get_width() // 2
        gy = WINDOW_HEIGHT // 4
        self.surface.blit(go_shadow, (gx + 3, gy + 3))
        self.surface.blit(go_text, (gx, gy))

        # Score
        box_w, box_h = 260, 90
        score_box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(score_box, (15, 25, 45, 200), (0, 0, box_w, box_h), border_radius=12)
        pygame.draw.rect(score_box, (40, 180, 220, 120), (0, 0, box_w, box_h), 2, border_radius=12)
        bx = WINDOW_WIDTH // 2 - box_w // 2
        by = WINDOW_HEIGHT // 2 - 20
        self.surface.blit(score_box, (bx, by))

        label = self.subtitle_font.render("FINAL SCORE", True, (120, 180, 200))
        self.surface.blit(label, (WINDOW_WIDTH // 2 - label.get_width() // 2, by + 15))
        sc = self.title_font.render(str(score), True, (100, 255, 200))
        self.surface.blit(sc, (WINDOW_WIDTH // 2 - sc.get_width() // 2, by + 40))

        hi_label = self.subtitle_font.render(f"HIGH SCORE: {high_score}", True, (120, 220, 255))
        self.surface.blit(hi_label, (WINDOW_WIDTH // 2 - hi_label.get_width() // 2, by + box_h + 16))

        if score == high_score and score > 0:
            new_best = self.subtitle_font.render("NEW HIGH SCORE!", True, (255, 235, 120))
            self.surface.blit(new_best, (WINDOW_WIDTH // 2 - new_best.get_width() // 2, by + box_h + 42))

        # Pulsing restart
        pulse = int(180 + 75 * math.sin(time_elapsed * 3))
        prompt = self.font.render("PRESS SPACE TO RESTART", True, (pulse, 255, pulse))
        self.surface.blit(prompt, (WINDOW_WIDTH // 2 - prompt.get_width() // 2, WINDOW_HEIGHT // 2 + 130))
