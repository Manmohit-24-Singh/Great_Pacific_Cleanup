"""
Firebase stub for web (Pygbag/WASM) builds.

All methods return safe defaults so the game runs without
network access, auth, or leaderboard functionality.
"""


class FirebaseService:
    """No-op Firebase service for web builds."""

    def __init__(self):
        self.user = None
        self.id_token = None
        self.user_uuid = None

    def login(self, email, password):
        return {"success": False, "error": "Login is not available in the web version"}

    def sign_up(self, email, password, username):
        return {"success": False, "error": "Sign up is not available in the web version"}

    def logout(self):
        self.user = None
        self.id_token = None
        self.user_uuid = None

    def get_leaderboard(self, limit=10):
        return []

    def get_global_high_score(self):
        return 0

    def get_user_high_score(self):
        return 0

    def update_high_score(self, score):
        return False

    def record_game_session(self, score):
        return False
