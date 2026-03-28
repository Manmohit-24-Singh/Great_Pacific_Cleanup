import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import pytest
import types

pygame.init()
import ui

@pytest.fixture
def surface():
    return pygame.Surface((ui.WINDOW_WIDTH, ui.WINDOW_HEIGHT))


@pytest.fixture
def ui_obj(surface):
    return ui.UI(surface)


@pytest.fixture
def fake_player():
    player = types.SimpleNamespace()
    player.score = 0
    player.lives = ui.MAX_LIVES
    player.speed_boost_timer = 0
    player.shield_active = False
    player.eco_net_active = False
    player.eco_net_timer = 0
    player.pos = types.SimpleNamespace(x=100, y=100)
    return player


def test_ui_init_sets_default_state(ui_obj):
    assert ui_obj.surface is not None
    assert ui_obj.score_pulse == 0.0
    assert ui_obj.last_score == 0
    assert ui_obj.heart_flash_timer == 0.0
    assert ui_obj.input_text == ""
    assert ui_obj.input_active is None
    assert ui_obj.error_msg == ""
    assert ui_obj.loading is False

    assert ui_obj.auth_submit_rect.width == 0
    assert ui_obj.pause_resume_rect.width == 0


def test_draw_hud_updates_score_pulse_and_last_score(ui_obj, fake_player, monkeypatch):
    fake_player.score = 10
    fake_player.lives = ui.MAX_LIVES

    called = {"powerups": 0}
    monkeypatch.setattr(ui_obj, "draw_powerups", lambda player: called.__setitem__("powerups", called["powerups"] + 1))
    monkeypatch.setattr(ui_obj, "draw_heart", lambda *args, **kwargs: None)

    ui_obj.draw_hud(fake_player, high_score=100, level=2)

    assert ui_obj.last_score == 10
    assert ui_obj.score_pulse > 0
    assert called["powerups"] == 1


def test_draw_hud_updates_heart_flash_on_life_loss(ui_obj, fake_player, monkeypatch):
    ui_obj.last_lives = ui.MAX_LIVES
    fake_player.lives = ui.MAX_LIVES - 1

    monkeypatch.setattr(ui_obj, "draw_powerups", lambda player: None)
    monkeypatch.setattr(ui_obj, "draw_heart", lambda *args, **kwargs: None)

    ui_obj.draw_hud(fake_player, high_score=50, level=1)

    assert ui_obj.last_lives == fake_player.lives
    assert ui_obj.heart_flash_timer > 0


def test_draw_hud_updates_last_lives_when_lives_increase(ui_obj, fake_player, monkeypatch):
    ui_obj.last_lives = 2
    fake_player.lives = 3

    monkeypatch.setattr(ui_obj, "draw_powerups", lambda player: None)
    monkeypatch.setattr(ui_obj, "draw_heart", lambda *args, **kwargs: None)

    ui_obj.draw_hud(fake_player, high_score=50, level=1)

    assert ui_obj.last_lives == 3


def test_draw_buff_icons_near_player_returns_when_no_buffs(ui_obj, fake_player):
    # Should simply do nothing and not crash
    ui_obj.draw_buff_icons_near_player(fake_player, ui_obj.surface)


def test_draw_powerups_returns_when_no_active_powerups(ui_obj, fake_player):
    # Should simply do nothing and not crash
    ui_obj.draw_powerups(fake_player)


def test_draw_login_screen_sets_button_rects(ui_obj):
    ui_obj.draw_login_screen("a@test.com", "secret", "", False)

    assert ui_obj.auth_submit_rect.width == 200
    assert ui_obj.auth_submit_rect.height == 50
    assert ui_obj.auth_switch_rect.width == 240
    assert ui_obj.auth_guest_rect.width == 240
    assert ui_obj.auth_back_rect.width == 240


def test_draw_login_screen_loading_mode_does_not_crash(ui_obj):
    ui_obj.draw_login_screen("a@test.com", "secret", "Bad login", True)

    # Other buttons are always created
    assert ui_obj.auth_switch_rect.width == 240
    assert ui_obj.auth_guest_rect.width == 240
    assert ui_obj.auth_back_rect.width == 240


def test_draw_signup_screen_sets_button_rects(ui_obj):
    ui_obj.draw_signup_screen("a@test.com", "secret", "user1", "", False)

    assert ui_obj.auth_submit_rect.width == 200
    assert ui_obj.auth_submit_rect.height == 50
    assert ui_obj.auth_switch_rect.width == 240
    assert ui_obj.auth_guest_rect.width == 240
    assert ui_obj.auth_back_rect.width == 240


def test_draw_input_active_branch_with_cursor(ui_obj, monkeypatch):
    monkeypatch.setattr(pygame.time, "get_ticks", lambda: 0)
    ui_obj.draw_input("Email", "test@example.com", 200, True)


def test_draw_input_inactive_branch(ui_obj):
    ui_obj.draw_input("Email", "test@example.com", 200, False)


def test_draw_btn_hover_branch(ui_obj, monkeypatch):
    rect = pygame.Rect(100, 100, 120, 40)
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (110, 110))
    ui_obj.draw_btn("PLAY", rect, (100, 200, 100))


def test_draw_btn_non_hover_branch(ui_obj, monkeypatch):
    rect = pygame.Rect(100, 100, 120, 40)
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (0, 0))
    ui_obj.draw_btn("PLAY", rect, (100, 200, 100))


def test_draw_leaderboard_screen_with_none(ui_obj):
    ui_obj.draw_leaderboard_screen(None)


def test_draw_leaderboard_screen_with_empty_list(ui_obj):
    ui_obj.draw_leaderboard_screen([])


def test_draw_leaderboard_screen_with_entries(ui_obj):
    leaderboard = [
        {"username": "Alice", "score": 100},
        {"username": "Bob", "score": 80},
        {"username": "Cara", "score": 60},
    ]
    ui_obj.draw_leaderboard_screen(leaderboard)


def test_draw_trivia_screen_with_question(ui_obj, monkeypatch):
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (0, 0))
    question_data = {
        "question": "What is the answer?",
        "options": ["A", "B", "C", "D"]
    }

    ui_obj.draw_trivia_screen(question_data, 5.0)


def test_draw_trivia_screen_with_no_question(ui_obj):
    ui_obj.draw_trivia_screen(None, 2.0)


def test_draw_pause_screen_sets_pause_button_rects(ui_obj):
    ui_obj.draw_pause_screen()

    assert ui_obj.pause_resume_rect.width == 300
    assert ui_obj.pause_restart_rect.width == 300
    assert ui_obj.pause_menu_rect.width == 300
    assert ui_obj.pause_sdg12_rect.width == 300
    assert ui_obj.pause_sdg14_rect.width == 300


def test_draw_level_announcement_returns_early_when_timer_nonpositive(ui_obj):
    ui_obj.draw_level_announcement("LEVEL 2", 0)


def test_draw_level_announcement_active_timer(ui_obj):
    ui_obj.draw_level_announcement("LEVEL 2", 1.5, max_time=3.0)