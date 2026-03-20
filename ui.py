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

        # UI Input State
        self.input_text = ""
        self.input_active = None # 'email', 'password', 'username'
        self.error_msg = ""
        self.loading = False

        # Button Rects for interaction
        self.auth_submit_rect = pygame.Rect(0, 0, 0, 0)
        self.auth_switch_rect = pygame.Rect(0, 0, 0, 0)

    # HUD
    def draw_hud(self, player, high_score):

        # Detect changes for animation triggers
        if player.score != self.last_score:
            self.score_pulse = 0.4  # 400ms pulse
            self.last_score = player.score
        if player.lives < self.last_lives:
            self.heart_flash_timer = 0.5  # 500ms flash
            self.last_lives = player.lives
        if player.lives > self.last_lives:
            self.last_lives = player.lives

        # Score (top-left, with drop shadow + pulse scale)
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

        # Hearts (top-right, with shake/flash on damage)
        for i in range(MAX_LIVES):
            hx = WINDOW_WIDTH - 35 - i * 30
            hy = 18

            if i < player.lives:
                color = (255, 60, 80)
                # If we just lost a heart, shake the remaining ones
                if self.heart_flash_timer > 0:
                    shake_x = int(math.sin(self.heart_flash_timer * 40) * 3)
                    hx += shake_x
                self.draw_heart(hx, hy, 10, color)
            else:
                # Recently lost heart: flash bright red then fade to grey
                if i == player.lives and self.heart_flash_timer > 0:
                    flash = self.heart_flash_timer / 0.5
                    r = int(255 * flash + 80 * (1 - flash))
                    g = int(20 * flash + 80 * (1 - flash))
                    b = int(20 * flash + 80 * (1 - flash))
                    self.draw_heart(hx, hy, 10, (r, g, b))
                else:
                    self.draw_heart(hx, hy, 10, (60, 60, 60))

        if self.heart_flash_timer > 0:
            self.heart_flash_timer -= 1.0 / 60

        # Active Powerups (top center)
        self.draw_powerups(player)

    def draw_buff_icons_near_player(self, player, surface):
        active_buffs = []

        if player.speed_boost_timer > 0:
            active_buffs.append('turbo')
        if player.shield_active:
            active_buffs.append('shield')
        if player.eco_net_active:
            active_buffs.append('eco_net')

        if not active_buffs:
            return

        t = pygame.time.get_ticks() / 1000.0
        radius = 45

        for i, buff_key in enumerate(active_buffs):
            angle = t * 2 + i * (math.pi * 2 / len(active_buffs))
            ix = int(player.pos.x + math.cos(angle) * radius)
            iy = int(player.pos.y + math.sin(angle) * radius)

            # Load the icon PNG
            filename = PowerUp.POWERUP_IMAGES.get(buff_key)
            if filename:
                try:
                    icon = load_image(filename, scale=(20, 20))  # plain icon, no tint
                    surface.blit(icon, (ix - icon.get_width() // 2, iy - icon.get_height() // 2))
                except Exception as e:
                    print(f"Failed to load buff icon {buff_key}: {e}")

    def draw_powerups(self, player):
        active = []

        if player.speed_boost_timer > 0:
            active.append(('turbo', POWERUP_COLORS['turbo'], player.speed_boost_timer, 5.0))

        if player.shield_active:
            active.append(('shield', POWERUP_COLORS['shield'], 1.0, 1.0))

        if player.eco_net_active:
            active.append(('eco_net', POWERUP_COLORS['eco_net'], player.eco_net_timer, 8.0))

        if not active:
            return

        total_w = len(active) * 75
        start_x = (WINDOW_WIDTH - total_w) // 2

        for i, (icon_key, color, remaining, max_time) in enumerate(active):
            x = start_x + i * 75
            y = 10

            # Bigger background pill
            pill = pygame.Surface((70, 40), pygame.SRCALPHA)
            if remaining < 2.0:
                pulse_danger = int(60 + 100 * abs(math.sin(pygame.time.get_ticks() / 150)))
                pygame.draw.rect(pill, (pulse_danger, 0, 0, 150), (0, 0, 70, 40), border_radius=8)
                pygame.draw.rect(pill, (255, 100, 100, 200), (0, 0, 70, 40), 2, border_radius=8)
            else:
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

    def draw_heart(self, x, y, size, color):
        s = size
        pts = []
        for angle in range(0, 360, 8):
            rad = math.radians(angle)
            px = s * (16 * math.sin(rad) ** 3) / 16
            py = -s * (13 * math.cos(rad) - 5 * math.cos(2 * rad) - 2 * math.cos(3 * rad) - math.cos(4 * rad)) / 16
            pts.append((x + px, y + py))
        if len(pts) > 2:
            pygame.draw.polygon(self.surface, color, pts)

    # GAME OVER
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

    # START SCREEN
    def draw_start_screen(self, time_elapsed, high_score, logged_in=False, username=""):
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
        ty = WINDOW_HEIGHT // 6
        self.surface.blit(shadow, (tx + 2, ty + 2))
        self.surface.blit(title_surf, (tx, ty))

        shadow2 = self.title_font.render(title2_text, True, (0, 0, 0))
        title2_surf = self.title_font.render(title2_text, True, (40, 255, 180))
        tx2 = WINDOW_WIDTH // 2 - title2_surf.get_width() // 2
        self.surface.blit(shadow2, (tx2 + 2, ty + 62))
        self.surface.blit(title2_surf, (tx2, ty + 60))

        # High score display (below title)
        hi = self.subtitle_font.render(f"PERSONAL BEST: {high_score}", True, (120, 235, 200))
        self.surface.blit(hi, (WINDOW_WIDTH // 2 - hi.get_width() // 2, ty + 130))

        # Pulsing "Press SPACE" prompt
        mid_y = WINDOW_HEIGHT // 2
        box_y = mid_y + 110 # Push box further down

        pulse = int(180 + 75 * math.sin(time_elapsed * 3))
        prompt_text = "PRESS SPACE TO BEGIN" if logged_in else "PRESS SPACE TO LOGIN"
        prompt = self.font.render(prompt_text, True, (pulse, 255, pulse))
        px = WINDOW_WIDTH // 2 - prompt.get_width() // 2
        self.surface.blit(prompt, (px, mid_y + 10))

        if logged_in:
            leader_txt = self.subtitle_font.render("Press 'L' for World Leaderboard", True, (255, 255, 100))
            self.surface.blit(leader_txt, (WINDOW_WIDTH // 2 - leader_txt.get_width() // 2, mid_y + 45))
            
            logout_txt = self.small_font.render("Press 'O' to Logout", True, (200, 100, 100))
            self.surface.blit(logout_txt, (WINDOW_WIDTH // 2 - logout_txt.get_width() // 2, mid_y + 75))

            user_txt = self.small_font.render(f"Logged in as: {username}", True, (200, 255, 200))
            self.surface.blit(user_txt, (10, WINDOW_HEIGHT - 30))

        # Instructions box
        box = pygame.Surface((WINDOW_WIDTH - 80, 160), pygame.SRCALPHA)
        box.fill((10, 20, 40, 160))
        pygame.draw.rect(box, (40, 180, 220, 100), (0, 0, WINDOW_WIDTH - 80, 160), 1, border_radius=8)
        self.surface.blit(box, (40, box_y))

        instructions = [
            ("Arrow Keys / WASD", "Move your cleanup vessel"),
            ("Collect Plastic", "Score points + biofuel boost"),
            ("Avoid Marine Life", "Collisions reduce your lives"),
            ("Grab Power-ups", "Shield, Turbo, Sonar, Eco Net"),
        ]
        for i, (key, desc) in enumerate(instructions):
            iy = box_y + 12 + i * 36
            key_surf = self.small_font.render(key, True, (100, 220, 255))
            desc_surf = self.small_font.render(f"  -  {desc}", True, (200, 210, 220))
            self.surface.blit(key_surf, (60, iy))
            self.surface.blit(desc_surf, (60 + key_surf.get_width(), iy))

        # Version line
        ver = self.small_font.render("v1.0  |  Save the Ocean", True, (80, 100, 120))
        self.surface.blit(ver, (WINDOW_WIDTH // 2 - ver.get_width() // 2, WINDOW_HEIGHT - 25))

    # AUTH SCREENS
    def draw_login_screen(self, email, password, error, loading):
        self.surface.fill(OCEAN_DEEP)
        self.draw_bg()

        title = self.title_font.render("LOGIN", True, WHITE)
        self.surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))

        # Email Field
        self.draw_input("Email", email, 200, self.input_active == 'email')
        # Password Field (masked)
        self.draw_input("Password", "*" * len(password), 300, self.input_active == 'password')

        if error:
            err_surf = self.small_font.render(error, True, (255, 100, 100))
            self.surface.blit(err_surf, (WINDOW_WIDTH // 2 - err_surf.get_width() // 2, 380))

        if loading:
            load_surf = self.font.render("Logging in...", True, (200, 200, 200))
            self.surface.blit(load_surf, (WINDOW_WIDTH // 2 - load_surf.get_width() // 2, 420))
        else:
            # Login Button
            self.auth_submit_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 440, 200, 50)
            self.draw_btn("LOGIN", self.auth_submit_rect, (100, 255, 100))

        # Switch to Signup Button
        self.auth_switch_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, 520, 240, 40)
        self.draw_btn("GO TO SIGN UP", self.auth_switch_rect, (150, 150, 255), small=True)

    def draw_signup_screen(self, email, password, username, error, loading):
        self.surface.fill(OCEAN_DEEP)
        self.draw_bg()

        title = self.title_font.render("SIGN UP", True, WHITE)
        self.surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 80))

        self.draw_input("Username", username, 180, self.input_active == 'username')
        self.draw_input("Email", email, 270, self.input_active == 'email')
        self.draw_input("Password", "*" * len(password), 360, self.input_active == 'password')

        if error:
            err_surf = self.small_font.render(error, True, (255, 100, 100))
            self.surface.blit(err_surf, (WINDOW_WIDTH // 2 - err_surf.get_width() // 2, 430))

        if loading:
            load_surf = self.font.render("Creating Account...", True, (200, 200, 200))
            self.surface.blit(load_surf, (WINDOW_WIDTH // 2 - load_surf.get_width() // 2, 470))
        else:
            # Signup Button
            self.auth_submit_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 490, 200, 50)
            self.draw_btn("SIGN UP", self.auth_submit_rect, (100, 255, 100))

        # Switch to Login Button
        self.auth_switch_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, 570, 240, 40)
        self.draw_btn("BACK TO LOGIN", self.auth_switch_rect, (150, 150, 255), small=True)

    def draw_bg(self):
        for y in range(0, WINDOW_HEIGHT, 4):
            ratio = y / WINDOW_HEIGHT
            r = int(5 + 10 * ratio)
            g = int(20 + 40 * ratio)
            b = int(40 + 60 * ratio)
            pygame.draw.line(self.surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))

    def draw_input(self, label, value, y, active):
        lbl = self.small_font.render(label, True, (200, 200, 200))
        self.surface.blit(lbl, (150, y - 25))
        
        box_color = (60, 120, 255) if active else (40, 60, 80)
        pygame.draw.rect(self.surface, box_color, (150, y, 300, 40), 2, border_radius=5)
        
        txt = self.font.render(value, True, WHITE)
        self.surface.blit(txt, (160, y + 5))
        
        if active and (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = 160 + txt.get_width() + 2
            pygame.draw.line(self.surface, WHITE, (cursor_x, y + 8), (cursor_x, y + 32), 2)

    def draw_btn(self, text, rect, color, small=False):
        mouse_pos = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse_pos)
        
        # Draw shadow
        pygame.draw.rect(self.surface, BLACK, (rect.x + 3, rect.y + 3, rect.width, rect.height), border_radius=10)
        
        # Draw main box
        btn_color = [min(255, c + 30) if hover else c for c in color]
        pygame.draw.rect(self.surface, btn_color, rect, border_radius=10)
        pygame.draw.rect(self.surface, WHITE, rect, 2, border_radius=10)
        
        # Draw text
        font = self.subtitle_font if small else self.font
        txt = font.render(text, True, BLACK if hover else WHITE)
        self.surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

    # LEADERBOARD SCREEN
    def draw_leaderboard_screen(self, leaderboard, user_score=None):
        self.surface.fill(OCEAN_DEEP)
        self.draw_bg()

        title = self.title_font.render("WORLD LEADERBOARD", True, (255, 235, 120))
        self.surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))

        # Table Header
        header_y = 150
        pygame.draw.line(self.surface, (100, 200, 255), (80, header_y + 35), (WINDOW_WIDTH - 80, header_y + 35), 2)
        
        rank_h = self.subtitle_font.render("RANK", True, (150, 150, 150))
        name_h = self.subtitle_font.render("PLAYER", True, (150, 150, 150))
        score_h = self.subtitle_font.render("SCORE", True, (150, 150, 150))
        
        self.surface.blit(rank_h, (100, header_y))
        self.surface.blit(name_h, (200, header_y))
        self.surface.blit(score_h, (WINDOW_WIDTH - 180, header_y))

        if not leaderboard:
            msg = self.font.render("Loading...", True, WHITE)
            self.surface.blit(msg, (WINDOW_WIDTH // 2 - msg.get_width() // 2, WINDOW_HEIGHT // 2))
        else:
            for i, entry in enumerate(leaderboard):
                y = 200 + i * 40
                color = (255, 255, 255)
                if i == 0: color = (255, 215, 0) # Gold
                elif i == 1: color = (192, 192, 192) # Silver
                elif i == 2: color = (205, 127, 50) # Bronze
                
                rank = self.font.render(f"#{i+1}", True, color)
                name = self.font.render(entry['username'], True, color)
                score = self.font.render(str(entry['score']), True, color)
                
                self.surface.blit(rank, (100, y))
                self.surface.blit(name, (200, y))
                self.surface.blit(score, (WINDOW_WIDTH - 180, y))

        prompt = self.subtitle_font.render("PRESS ESC TO RETURN TO MENU", True, (100, 255, 180))
        px = WINDOW_WIDTH // 2 - prompt.get_width() // 2
        self.surface.blit(prompt, (px, WINDOW_HEIGHT - 80))

    # TRIVIA SCREEN
    def draw_trivia_screen(self, question_data, time_remaining):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.surface.blit(overlay, (0, 0))

        # Title
        title = self.title_font.render("SECOND CHANCE TRIVIA", True, (255, 235, 120))
        self.surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 80))

        # Question
        if question_data:
            q_surf = self.hud_font.render(question_data["question"], True, WHITE)
            # Simple text wrap if needed, assuming it fits for now (can optimize later)
            self.surface.blit(q_surf, (WINDOW_WIDTH // 2 - q_surf.get_width() // 2, 160))

            # Options
            for i, option in enumerate(question_data["options"]):
                y = 240 + i * 60
                btn_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, y, 400, 50)
                # Mouse hover logic handled inline for the UI call
                mouse_pos = pygame.mouse.get_pos()
                hover = btn_rect.collidepoint(mouse_pos)
                
                btn_color = (60, 120, 255) if hover else (40, 60, 80)
                pygame.draw.rect(self.surface, btn_color, btn_rect, border_radius=10)
                pygame.draw.rect(self.surface, WHITE, btn_rect, 2, border_radius=10)
                
                opt_txt = f"{i+1}. {option}"
                txt_surf = self.font.render(opt_txt, True, WHITE)
                self.surface.blit(txt_surf, (btn_rect.x + 20, btn_rect.centery - txt_surf.get_height() // 2))
                
        # Timer bar at the bottom
        timer_w = int(400 * (time_remaining / 10.0))
        color = (255, 100, 100) if time_remaining < 3 else (100, 255, 100)
        pygame.draw.rect(self.surface, color, (WINDOW_WIDTH // 2 - 200, 500, timer_w, 20), border_radius=10)
        pygame.draw.rect(self.surface, WHITE, (WINDOW_WIDTH // 2 - 200, 500, 400, 20), 2, border_radius=10)
