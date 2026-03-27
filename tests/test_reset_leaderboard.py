import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import pytest

pygame.init()

from game import Game

from reset_leaderboard import reset

def test_reset_creates_high_score_file_with_zero(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    reset()

    high_score_file = tmp_path / "high_score.txt"
    assert high_score_file.exists()
    assert high_score_file.read_text() == "0"

def test_reset_overwrites_existing_high_score_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    high_score_file = tmp_path / "high_score.txt"
    high_score_file.write_text("999")

    reset()

    assert high_score_file.read_text() == "0"


def test_reset_prints_expected_messages(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    reset()

    captured = capsys.readouterr()
    output = captured.out

    assert "DeleteAllScores is locked to NO_ACCESS for security." in output
    assert "Use the Firebase Console or Admin SDK to reset the leaderboard." in output
    assert "To reset the local high score file only:" in output
    assert "Local high_score.txt reset to 0." in output