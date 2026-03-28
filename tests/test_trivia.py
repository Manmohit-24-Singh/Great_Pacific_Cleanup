import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import pytest

pygame.init()
import trivia

def test_init_sets_default_values():
    manager = trivia.TriviaManager()

    assert manager.current_question is None
    assert manager.time_limit == 10.0
    assert manager.timer == 0.0


def test_start_question_sets_current_question_and_resets_timer(monkeypatch):
    manager = trivia.TriviaManager()
    fake_question = trivia.TRIVIA_QUESTIONS[0]

    monkeypatch.setattr(trivia.random, "choice", lambda questions: fake_question)

    manager.start_question()

    assert manager.current_question == fake_question
    assert manager.timer == manager.time_limit


def test_start_question_selects_from_trivia_questions(monkeypatch):
    manager = trivia.TriviaManager()
    fake_question = trivia.TRIVIA_QUESTIONS[2]

    monkeypatch.setattr(trivia.random, "choice", lambda questions: fake_question)

    manager.start_question()

    assert manager.current_question in trivia.TRIVIA_QUESTIONS


def test_update_returns_waiting_when_no_current_question():
    manager = trivia.TriviaManager()

    result = manager.update(1.0)

    assert result == "WAITING"
    assert manager.timer == 0.0


def test_update_decreases_timer_when_question_active(monkeypatch):
    manager = trivia.TriviaManager()
    fake_question = trivia.TRIVIA_QUESTIONS[0]

    monkeypatch.setattr(trivia.random, "choice", lambda questions: fake_question)
    manager.start_question()

    result = manager.update(3.0)

    assert result == "WAITING"
    assert manager.timer == 7.0


def test_update_returns_timeout_when_timer_reaches_zero(monkeypatch):
    manager = trivia.TriviaManager()
    fake_question = trivia.TRIVIA_QUESTIONS[0]

    monkeypatch.setattr(trivia.random, "choice", lambda questions: fake_question)
    manager.start_question()

    result = manager.update(10.0)

    assert result == "TIMEOUT"
    assert manager.timer == 0


def test_update_clamps_timer_to_zero_when_dt_exceeds_remaining_time(monkeypatch):
    manager = trivia.TriviaManager()
    fake_question = trivia.TRIVIA_QUESTIONS[0]

    monkeypatch.setattr(trivia.random, "choice", lambda questions: fake_question)
    manager.start_question()

    result = manager.update(15.0)

    assert result == "TIMEOUT"
    assert manager.timer == 0


def test_check_answer_returns_false_when_no_current_question():
    manager = trivia.TriviaManager()

    assert manager.check_answer(0) is False


def test_check_answer_returns_true_for_correct_answer():
    manager = trivia.TriviaManager()
    manager.current_question = trivia.TRIVIA_QUESTIONS[1]  # answer is 0

    assert manager.check_answer(0) is True


def test_check_answer_returns_false_for_incorrect_answer():
    manager = trivia.TriviaManager()
    manager.current_question = trivia.TRIVIA_QUESTIONS[1]  # answer is 0

    assert manager.check_answer(2) is False