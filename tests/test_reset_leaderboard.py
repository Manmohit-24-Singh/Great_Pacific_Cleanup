import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import reset_leaderboard


class DummyTable:
    def __init__(self):
        self.deleted = False
        self.executed = False

    def delete(self):
        self.deleted = True
        return self

    def neq(self, *args, **kwargs):
        return self

    def execute(self):
        self.executed = True
        return {"status": "ok"}


class DummySupabase:
    def __init__(self):
        self.table_obj = DummyTable()

    def table(self, name):
        assert name == "scores"
        return self.table_obj


class DummySupabaseService:
    def __init__(self):
        self.supabase = DummySupabase()


def test_reset_calls_supabase_delete(monkeypatch, tmp_path):
    dummy_service = DummySupabaseService()

    monkeypatch.setattr(reset_leaderboard, "SupabaseService", lambda: dummy_service)
    monkeypatch.setattr("builtins.input", lambda *args: "yes")

    monkeypatch.chdir(tmp_path)

    reset_leaderboard.reset()

    assert dummy_service.supabase.table_obj.deleted is True
    assert dummy_service.supabase.table_obj.executed is True
    assert (tmp_path / "high_score.txt").read_text() == "0"


def test_reset_prints_expected_messages(monkeypatch, capsys, tmp_path):
    dummy_service = DummySupabaseService()

    monkeypatch.setattr(reset_leaderboard, "SupabaseService", lambda: dummy_service)
    monkeypatch.setattr("builtins.input", lambda *args: "yes")

    monkeypatch.chdir(tmp_path)

    reset_leaderboard.reset()

    captured = capsys.readouterr()
    output = captured.out.lower()

    assert "delete all scores" in output
    assert "deleted from supabase" in output
    assert "reset to 0" in output


def test_reset_cancelled_when_user_does_not_confirm(monkeypatch, capsys, tmp_path):
    dummy_service = DummySupabaseService()

    monkeypatch.setattr(reset_leaderboard, "SupabaseService", lambda: dummy_service)
    monkeypatch.setattr("builtins.input", lambda *args: "no")

    monkeypatch.chdir(tmp_path)

    reset_leaderboard.reset()

    captured = capsys.readouterr()
    output = captured.out.lower()

    assert "cancelled" in output
    assert dummy_service.supabase.table_obj.deleted is False
    assert not (tmp_path / "high_score.txt").exists()