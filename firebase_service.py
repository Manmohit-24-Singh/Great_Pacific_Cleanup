import pyrebase
import requests
import json
import os
import google.auth
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import service_account
from firebase_config import firebaseConfig

# Data Connect REST API base URL
DATA_CONNECT_URL = (
    "https://firebasedataconnect.googleapis.com/v1beta"
    "/projects/great-pacific-cleanup"
    "/locations/us-central1"
    "/services/great-pacific-cleanup-service"
    ":executeGraphql"
)

# Scopes required for Data Connect API
GCP_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]

# Path to service account key file (download from Firebase Console)
SERVICE_ACCOUNT_KEY = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")


class FirebaseService:
    def __init__(self):
        # Firebase Auth (pyrebase) — for user login/signup
        try:
            self.firebase = pyrebase.initialize_app(firebaseConfig)
            self.auth = self.firebase.auth()
        except Exception as e:
            print(f"Firebase Init Error: {e}")
            self.auth = None

        self.user = None
        self.id_token = None
        self.user_uuid = None  # Data Connect internal UUID for the User row

        # Google Cloud credentials — for Data Connect REST API
        self._gcp_credentials = None
        self._init_gcp_credentials()

    def _init_gcp_credentials(self):
        """Load Google Cloud credentials (service account key or ADC)."""
        # 1. Try service account key file first
        if os.path.exists(SERVICE_ACCOUNT_KEY):
            try:
                self._gcp_credentials = service_account.Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_KEY, scopes=GCP_SCOPES
                )
                print("DEBUG: Loaded credentials from serviceAccountKey.json")
                return
            except Exception as e:
                print(f"WARNING: Failed to load service account key: {e}")

        # 2. Fallback to Application Default Credentials
        try:
            self._gcp_credentials, _ = google.auth.default(scopes=GCP_SCOPES)
            print("DEBUG: Loaded Application Default Credentials")
        except Exception as e:
            print(f"WARNING: Could not load Google Cloud credentials: {e}")
            print("  Place serviceAccountKey.json in the project root,")
            print("  or run: gcloud auth application-default login")
            self._gcp_credentials = None

    def _get_gcp_access_token(self):
        """Get a fresh OAuth 2.0 access token for the Data Connect API."""
        if not self._gcp_credentials:
            return None
        try:
            self._gcp_credentials.refresh(GoogleAuthRequest())
            return self._gcp_credentials.token
        except Exception as e:
            print(f"WARNING: Failed to refresh GCP credentials: {e}")
            return None

    # ── Auth (unchanged — still uses pyrebase) ─────────────────────────

    def sign_up(self, email, password, username):
        if not self.auth:
            return {"success": False, "error": "Firebase not configured"}
        try:
            user = self.auth.create_user_with_email_and_password(email, password)
            self.user = user
            self.id_token = user['idToken']

            # Create user profile in Data Connect
            self._create_user(user['localId'], username)
            return {"success": True, "user": user, "username": username}
        except Exception as e:
            return self._parse_error(e)

    def login(self, email, password):
        if not self.auth:
            return {"success": False, "error": "Firebase not configured"}
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            self.user = user
            self.id_token = user['idToken']

            # Fetch (or create) user in Data Connect and get username
            username = self._get_or_create_user(user['localId'], email)
            return {"success": True, "user": user, "username": username}
        except Exception as e:
            return self._parse_error(e)

    def logout(self):
        self.user = None
        self.id_token = None
        self.user_uuid = None

    def _parse_error(self, e):
        try:
            error_json = e.args[1]
            error_msg = json.loads(error_json)['error']['message']
        except Exception:
            error_msg = str(e)
        return {"success": False, "error": error_msg}

    # ── Data Connect helpers ───────────────────────────────────────────

    def _execute_graphql(self, query, variables=None):
        """Execute a GraphQL operation against Data Connect."""
        access_token = self._get_gcp_access_token()
        if not access_token:
            print("ERROR: No GCP access token available. Run: gcloud auth application-default login")
            return None

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        body = {"query": query}
        if variables:
            body["variables"] = variables

        try:
            response = requests.post(DATA_CONNECT_URL, json=body, headers=headers)
            json_res = response.json()
            if response.status_code == 200:
                if "errors" in json_res:
                    print(f"GraphQL Errors: {json_res['errors']}")
                    return None
                return json_res.get("data", {})
            else:
                print(f"Data Connect Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Data Connect Exception: {e}")
            return None

    # ── User Management ────────────────────────────────────────────────

    def _create_user(self, google_id, display_name):
        """Create a new user profile in Data Connect."""
        query = """
            mutation CreateUser($googleId: String!, $displayName: String!) {
                user_insert(
                    data: {
                        googleId: $googleId
                        displayName: $displayName
                        createdAt_expr: "request.time"
                    }
                )
            }
        """
        result = self._execute_graphql(query, {
            "googleId": google_id,
            "displayName": display_name
        })

        if result:
            print(f"DEBUG: User created for {display_name}")
            # Fetch UUID for subsequent operations
            self._fetch_user_uuid(google_id)

    def _fetch_user_uuid(self, google_id):
        """Look up the Data Connect internal UUID for a user."""
        query = """
            query GetUser($googleId: String!) {
                users(where: { googleId: { eq: $googleId } }) {
                    id
                    displayName
                }
            }
        """
        result = self._execute_graphql(query, {"googleId": google_id})
        if result and result.get("users"):
            self.user_uuid = result["users"][0]["id"]
            return result["users"][0].get("displayName", "Unknown")
        return "Unknown"

    def _get_or_create_user(self, google_id, fallback_name):
        """Fetch user from Data Connect; create if not found."""
        query = """
            query GetUser($googleId: String!) {
                users(where: { googleId: { eq: $googleId } }) {
                    id
                    displayName
                }
            }
        """
        result = self._execute_graphql(query, {"googleId": google_id})

        if result and result.get("users") and len(result["users"]) > 0:
            user_row = result["users"][0]
            self.user_uuid = user_row["id"]
            return user_row.get("displayName", "Unknown")
        else:
            # User not in DB yet — create with fallback name
            self._create_user(google_id, fallback_name.split("@")[0])
            return fallback_name.split("@")[0]

    # ── Leaderboard ────────────────────────────────────────────────────

    def get_leaderboard(self, limit=10):
        query = """
            query GetLeaderboard($limit: Int!) {
                highScores(orderBy: [{ score: DESC }], limit: $limit) {
                    score
                    updatedAt
                    user {
                        displayName
                    }
                }
            }
        """
        result = self._execute_graphql(query, {"limit": limit})
        if result and result.get("highScores"):
            leaderboard = []
            for entry in result["highScores"]:
                leaderboard.append({
                    "username": entry.get("user", {}).get("displayName", "Unknown"),
                    "score": entry.get("score", 0)
                })
            return leaderboard
        return []
    def get_global_high_score(self):
        """Fetch the highest score in the world."""
        leaderboard = self.get_leaderboard(limit=1)
        if leaderboard:
            return leaderboard[0].get("score", 0)
        return 0

    def get_user_high_score(self):
        """Fetch the current user's high score from Data Connect."""
        if not self.user:
            return 0

        if not self.user_uuid:
            self._fetch_user_uuid(self.user['localId'])
            if not self.user_uuid:
                return 0

        query = """
            query GetUserHighScore($userId: UUID!) {
                highScores(where: { userId: { eq: $userId } }) {
                    score
                }
            }
        """
        result = self._execute_graphql(query, {"userId": self.user_uuid})
        if result and result.get("highScores") and len(result["highScores"]) > 0:
            return result["highScores"][0].get("score", 0)
        return 0

    # ── High Score ─────────────────────────────────────────────────────

    def update_high_score(self, score):
        if not self.user or not self.id_token:
            return False

        if not self.user_uuid:
            self._fetch_user_uuid(self.user['localId'])
            if not self.user_uuid:
                print("DEBUG: Cannot update high score — user UUID not found")
                return False

        # Check if user already has a high score entry
        get_query = """
            query GetUserHighScore($userId: UUID!) {
                highScores(where: { userId: { eq: $userId } }) {
                    id
                    score
                }
            }
        """
        result = self._execute_graphql(get_query, {"userId": self.user_uuid})

        if result and result.get("highScores") and len(result["highScores"]) > 0:
            # Update existing high score
            hs_id = result["highScores"][0]["id"]
            update_query = """
                mutation UpdateHighScore($id: UUID!, $score: Int!) {
                    highScore_update(
                        id: $id
                        data: {
                            score: $score
                            updatedAt_expr: "request.time"
                        }
                    )
                }
            """
            update_result = self._execute_graphql(update_query, {
                "id": hs_id,
                "score": score
            })
            if update_result is not None:
                print(f"DEBUG: High score updated to {score} via Data Connect!")
                return True
        else:
            # Create new high score entry
            create_query = """
                mutation CreateHighScore($userId: UUID!, $score: Int!) {
                    highScore_insert(
                        data: {
                            userId: $userId
                            score: $score
                            createdAt_expr: "request.time"
                            updatedAt_expr: "request.time"
                        }
                    )
                }
            """
            create_result = self._execute_graphql(create_query, {
                "userId": self.user_uuid,
                "score": score
            })
            if create_result is not None:
                print(f"DEBUG: High score created at {score} via Data Connect!")
                return True
        return False

    # ── Game Session (optional, for history tracking) ──────────────────

    def record_game_session(self, score):
        if not self.user_uuid:
            return False

        query = """
            mutation CreateGameSession($userId: UUID!, $score: Int!) {
                gameSession_insert(
                    data: {
                        userId: $userId
                        score: $score
                        createdAt_expr: "request.time"
                    }
                )
            }
        """
        result = self._execute_graphql(query, {
            "userId": self.user_uuid,
            "score": score
        })
        return result is not None
