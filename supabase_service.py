"""
Supabase Service — Auth + Database client for Great Pacific Cleanup.

Drop-in replacement for the old FirebaseService. Public method signatures
are identical so the rest of the codebase (main.py, etc.) does not need
to change its calls.
"""

import os
import sys
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
# When running as a PyInstaller bundle, resolve .env relative to the bundle dir
if getattr(sys, 'frozen', False):
    _base_dir = sys._MEIPASS
else:
    _base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_base_dir, '.env'))

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")


class SupabaseService:
    def __init__(self):
        self.user = None
        self.user_id = None   # Supabase auth user UUID
        self.username = None  # Display name

        # Initialise the Supabase client once
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        except Exception as e:
            print(f"Supabase Init Error: {e}")
            self.supabase = None

    # ── Auth ────────────────────────────────────────────────────────────

    def sign_up(self, email, password, username):
        """Create a new account and insert a scores row."""
        if not self.supabase:
            return {"success": False, "error": "Supabase not configured"}
        try:
            res = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
            })

            if res.user is None:
                return {"success": False, "error": "Sign-up failed — no user returned"}

            self.user = res.user
            self.user_id = res.user.id
            self.username = username

            # Create the initial scores row for this user
            self.supabase.table("scores").insert({
                "user_id": self.user_id,
                "username": username,
                "high_score": 0,
            }).execute()

            return {"success": True, "user": res.user, "username": username}
        except Exception as e:
            return self._parse_error(e)

    def login(self, email, password):
        """Sign in with email + password and fetch the username from scores."""
        if not self.supabase:
            return {"success": False, "error": "Supabase not configured"}
        try:
            res = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })

            if res.user is None:
                return {"success": False, "error": "Login failed"}

            self.user = res.user
            self.user_id = res.user.id

            # Fetch username from scores table
            score_row = (
                self.supabase.table("scores")
                .select("username")
                .eq("user_id", self.user_id)
                .maybe_single()
                .execute()
            )
            if score_row.data:
                self.username = score_row.data.get("username", email.split("@")[0])
            else:
                # First login but no scores row yet — create one
                fallback_name = email.split("@")[0]
                self.username = fallback_name
                self.supabase.table("scores").insert({
                    "user_id": self.user_id,
                    "username": fallback_name,
                    "high_score": 0,
                }).execute()

            return {"success": True, "user": res.user, "username": self.username}
        except Exception as e:
            return self._parse_error(e)

    def logout(self):
        """Sign out the current user."""
        if self.supabase:
            try:
                self.supabase.auth.sign_out()
            except Exception:
                pass
        self.user = None
        self.user_id = None
        self.username = None

    # ── Leaderboard ────────────────────────────────────────────────────

    def get_leaderboard(self, limit=10):
        """Return the top scores globally, ordered highest first."""
        if not self.supabase:
            return None
        try:
            res = (
                self.supabase.table("scores")
                .select("username, high_score")
                .order("high_score", desc=True)
                .limit(limit)
                .execute()
            )
            leaderboard = []
            for row in res.data or []:
                leaderboard.append({
                    "username": row.get("username", "Unknown"),
                    "score": row.get("high_score", 0),
                })
            return leaderboard
        except Exception as e:
            print(f"Leaderboard Error: {e}")
            return None

    def get_global_high_score(self):
        """Fetch the single highest score in the world."""
        leaderboard = self.get_leaderboard(limit=1)
        if leaderboard:
            return leaderboard[0].get("score", 0)
        return 0

    def get_user_high_score(self):
        """Fetch the current user's high score."""
        if not self.user or not self.user_id:
            return 0
        try:
            res = (
                self.supabase.table("scores")
                .select("high_score")
                .eq("user_id", self.user_id)
                .maybe_single()
                .execute()
            )
            if res.data:
                return res.data.get("high_score", 0)
            return 0
        except Exception as e:
            print(f"Get High Score Error: {e}")
            return 0

    # ── High Score ─────────────────────────────────────────────────────

    def update_high_score(self, score):
        """Update the user's high score (upsert). Only writes if score > stored."""
        if not self.user or not self.user_id:
            return False
        try:
            res = (
                self.supabase.table("scores")
                .upsert({
                    "user_id": self.user_id,
                    "username": self.username or "Unknown",
                    "high_score": score,
                    "updated_at": "now()",
                }, on_conflict="user_id")
                .execute()
            )
            if res.data:
                print(f"DEBUG: High score updated to {score} via Supabase!")
                return True
            return False
        except Exception as e:
            print(f"Update High Score Error: {e}")
            return False

    # ── Game Session (no-op — table not migrated) ──────────────────────

    def record_game_session(self, score):
        """Placeholder — game session logging is not implemented in Supabase."""
        return False

    # ── Error Helpers ──────────────────────────────────────────────────

    def _parse_error(self, e):
        """Extract a human-readable error message."""
        error_msg = str(e)
        try:
            # Supabase errors often contain JSON
            if hasattr(e, 'message'):
                error_msg = e.message
            elif hasattr(e, 'args') and len(e.args) > 0:
                # Try to extract from JSON string
                maybe_json = str(e.args[0])
                parsed = json.loads(maybe_json)
                error_msg = parsed.get("msg", parsed.get("message", error_msg))
        except Exception:
            pass
        return {"success": False, "error": error_msg}
