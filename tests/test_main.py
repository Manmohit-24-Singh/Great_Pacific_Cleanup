import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import pytest

pygame.init()

from game import Game


# ---------------------------
# Mock Classes
# ---------------------------
class MockFirebase:
    def get_global_high_score(self):
        return 100

    def get_user_high_score(self):
        return 50

    def update_high_score(self, score):
        pass

    def record_game_session(self, score):
        pass

    def login(self, email, password):
        return {"success": True, "user": "test_user", "username": "Tester"}

    def sign_up(self, email, password, username):
        return {"success": True, "user": "test_user", "username": username}


class MockSpawner:
    def __init__(self):
        self.difficulty_level = 0

    def update(self, dt, entities, hyperdrive=False):
        pass


class MockUI:
    def __init__(self, screen):
        self.input_active = None

    def draw_start_screen(self, *args): pass
    def draw_login_screen(self, *args): pass
    def draw_signup_screen(self, *args): pass
    def draw_leaderboard_screen(self, *args): pass
    def draw_trivia_screen(self, *args): pass
    def draw_hud(self, *args): pass
    def draw_pause_screen(self): pass
    def draw_game_over(self, *args): pass


# ---------------------------
# Fixture
# ---------------------------
@pytest.fixture
def game(monkeypatch):
    monkeypatch.setattr("game.FirebaseService", MockFirebase)
    monkeypatch.setattr("game.Spawner", MockSpawner)
    monkeypatch.setattr("game.UI", MockUI)

    g = Game()
    return g


# ---------------------------
# State Tests
# ---------------------------
def test_initial_state(game):
    assert game.state == "MENU"


def test_state_transition_to_playing(game):
    game.state = "PLAYING"
    assert game.state == "PLAYING"


def test_reset_game(game):
    game.player.score = 100
    game.reset_game()

    assert game.player.score == 0
    assert len(game.entities) == 0


# ---------------------------
# High Score Tests
# ---------------------------
def test_high_score_updates(game):
    game.player.score = 200
    game.high_score = 100

    game._update_playing(0.1)

    assert game.high_score >= 200


# ---------------------------
# Game Over Logic
# ---------------------------
def test_game_over_trigger(game):
    game.state = "PLAYING"
    game.player.lives = 0
    game.trivia_used = True

    game._update_playing(0.1)

    assert game.state == "GAMEOVER"


def test_trivia_trigger(game):
    game.state = "PLAYING"
    game.player.lives = 0
    game.trivia_used = False

    game._update_playing(0.1)

    assert game.state == "TRIVIA"


# ---------------------------
# Login System Tests
# ---------------------------
def test_login_success(game):
    game.auth_email = "test@test.com"
    game.auth_password = "1234"

    game.do_login()

    assert game.logged_in_user is not None
    assert game.state == "MENU"


def test_signup_success(game):
    game.auth_email = "test@test.com"
    game.auth_password = "1234"
    game.auth_username = "Tester"

    game.do_signup()

    assert game.logged_in_user is not None
    assert game.username == "Tester"


# ---------------------------
# Update Loop Safety
# ---------------------------
def test_update_does_not_crash(game):
    game.update(0.1)
    assert True


# ---------------------------
# Collision Safety
# ---------------------------
def test_collision_does_not_crash(game):
    game.check_collisions()
    assert True