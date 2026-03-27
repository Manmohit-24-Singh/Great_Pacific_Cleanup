import json
import os
import sys
import asyncio
from firebase_config import firebaseConfig

# Data Connect REST API base URL
DATA_CONNECT_URL = (
    "https://firebasedataconnect.googleapis.com/v1beta"
    "/projects/great-pacific-cleanup"
    "/locations/us-central1"
    "/services/great-pacific-cleanup-service"
    ":executeGraphql"
)

# Custom async HTTP fetch wrapper for Pygbag or local fallback
async def fetch_json(url, method="GET", headers=None, body=None):
    if sys.platform == "emscripten":
        import js
        import json as python_json
        
        js_headers = js.Object.fromEntries(js.Object.entries(js.JSON.parse(python_json.dumps(headers or {}))))
        
        fetch_opts = {
            "method": method,
            "headers": js_headers,
        }
        if body:
            fetch_opts["body"] = python_json.dumps(body)
            
        promise = js.window.fetch(url, js.Object.fromEntries(js.Object.entries(js.JSON.parse(python_json.dumps(fetch_opts)))))
        response = await asyncio.wrap_future(promise)
        
        text_promise = response.text()
        text = await asyncio.wrap_future(text_promise)
        
        return response.status, python_json.loads(text)
    else:
        import requests
        if method == "GET":
            res = requests.get(url, headers=headers)
        elif method == "POST":
            res = requests.post(url, headers=headers, json=body)
        else:
            raise ValueError("Unsupported method")
            
        try:
            return res.status_code, res.json()
        except:
            return res.status_code, {"error": {"message": res.text}}

class FirebaseService:
    def __init__(self):
        self.api_key = firebaseConfig["apiKey"]
        self.auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        self.signup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"
        
        self.user = None
        self.id_token = None
        self.user_uuid = None
        
        # In WebAssembly, we cannot use Service Accounts. We will use the id_token directly!
        # This requires Data Connect to have @auth(level: USER) or similar rules. 
        # If the backend is locked to ADMIN ONLY, this will fail.

    # ── Auth ─────────────────────────

    async def sign_up(self, email, password, username):
        body = {"email": email, "password": password, "returnSecureToken": True}
        status, data = await fetch_json(self.signup_url, method="POST", headers={"Content-Type": "application/json"}, body=body)
        
        if status == 200:
            self.user = {"localId": data["localId"]}
            self.id_token = data["idToken"]
            await self._create_user(data["localId"], username)
            return {"success": True, "user": self.user, "username": username}
        else:
            return {"success": False, "error": data.get("error", {}).get("message", "Signup failed")}

    async def login(self, email, password):
        body = {"email": email, "password": password, "returnSecureToken": True}
        status, data = await fetch_json(self.auth_url, method="POST", headers={"Content-Type": "application/json"}, body=body)
        
        if status == 200:
            self.user = {"localId": data["localId"]}
            self.id_token = data["idToken"]
            username = await self._get_or_create_user(data["localId"], email)
            return {"success": True, "user": self.user, "username": username}
        else:
            return {"success": False, "error": data.get("error", {}).get("message", "Login failed")}

    def logout(self):
        self.user = None
        self.id_token = None
        self.user_uuid = None

    # ── Data Connect helpers ───────────────────────────────────────────

    async def _execute_graphql(self, query, variables=None):
        if not self.id_token:
            print("WARNING: No id_token. Attempting unauthenticated request.")
            
        headers = {"Content-Type": "application/json"}
        if self.id_token:
            # We must use Firebase Auth token since we run in the browser
            headers["x-firebase-auth"] = self.id_token
        elif sys.platform != "emscripten":
            # Just for local fallback testing if we really need it...
            pass

        body = {"query": query}
        if variables:
            body["variables"] = variables

        status, json_res = await fetch_json(DATA_CONNECT_URL, method="POST", headers=headers, body=body)
        
        if status == 200:
            if "errors" in json_res:
                print(f"GraphQL Errors: {json_res['errors']}")
                return None
            return json_res.get("data", {})
        else:
            print(f"Data Connect Error: {status} - {json_res}")
            return None

    # ── User Management ────────────────────────────────────────────────

    async def _create_user(self, google_id, display_name):
        query = """
            mutation CreateUser($googleId: String!, $displayName: String!) {
                user_insert(data: { googleId: $googleId, displayName: $displayName, createdAt_expr: "request.time" })
            }
        """
        result = await self._execute_graphql(query, {"googleId": google_id, "displayName": display_name})
        if result:
            await self._fetch_user_uuid(google_id)

    async def _fetch_user_uuid(self, google_id):
        query = """
            query GetUser($googleId: String!) {
                users(where: { googleId: { eq: $googleId } }) { id, displayName }
            }
        """
        result = await self._execute_graphql(query, {"googleId": google_id})
        if result and result.get("users"):
            self.user_uuid = result["users"][0]["id"]
            return result["users"][0].get("displayName", "Unknown")
        return "Unknown"

    async def _get_or_create_user(self, google_id, fallback_name):
        query = """
            query GetUser($googleId: String!) {
                users(where: { googleId: { eq: $googleId } }) { id, displayName }
            }
        """
        result = await self._execute_graphql(query, {"googleId": google_id})
        if result and result.get("users") and len(result["users"]) > 0:
            self.user_uuid = result["users"][0]["id"]
            return result["users"][0].get("displayName", "Unknown")
        else:
            await self._create_user(google_id, fallback_name.split("@")[0])
            return fallback_name.split("@")[0]

    # ── Leaderboard ────────────────────────────────────────────────────

    async def get_leaderboard(self, limit=10):
        query = """
            query GetLeaderboard($limit: Int!) {
                highScores(orderBy: [{ score: DESC }], limit: $limit) {
                    score, updatedAt, user { displayName }
                }
            }
        """
        result = await self._execute_graphql(query, {"limit": limit})
        if result and result.get("highScores"):
            return [{"username": e.get("user", {}).get("displayName", "Unknown"), "score": e.get("score", 0)} for e in result["highScores"]]
        return []

    async def get_global_high_score(self):
        leaderboard = await self.get_leaderboard(limit=1)
        return leaderboard[0].get("score", 0) if leaderboard else 0

    async def get_user_high_score(self):
        if not self.user: return 0
        if not self.user_uuid:
            await self._fetch_user_uuid(self.user['localId'])
            if not self.user_uuid: return 0

        query = """
            query GetUserHighScore($userId: UUID!) {
                highScores(where: { userId: { eq: $userId } }) { score }
            }
        """
        result = await self._execute_graphql(query, {"userId": self.user_uuid})
        if result and result.get("highScores") and len(result["highScores"]) > 0:
            return result["highScores"][0].get("score", 0)
        return 0

    # ── High Score ─────────────────────────────────────────────────────

    async def update_high_score(self, score):
        if not self.user or not self.id_token: return False
        if not self.user_uuid:
            await self._fetch_user_uuid(self.user['localId'])
            if not self.user_uuid: return False

        get_query = """
            query GetUserHighScore($userId: UUID!) {
                highScores(where: { userId: { eq: $userId } }) { id, score }
            }
        """
        result = await self._execute_graphql(get_query, {"userId": self.user_uuid})

        if result and result.get("highScores") and len(result["highScores"]) > 0:
            hs_id = result["highScores"][0]["id"]
            update_query = """
                mutation UpdateHighScore($id: UUID!, $score: Int!) {
                    highScore_update(id: $id, data: { score: $score, updatedAt_expr: "request.time" })
                }
            """
            update_result = await self._execute_graphql(update_query, {"id": hs_id, "score": score})
            return update_result is not None
        else:
            create_query = """
                mutation CreateHighScore($userId: UUID!, $score: Int!) {
                    highScore_insert(data: { userId: $userId, score: $score, createdAt_expr: "request.time", updatedAt_expr: "request.time" })
                }
            """
            create_result = await self._execute_graphql(create_query, {"userId": self.user_uuid, "score": score})
            return create_result is not None

    async def record_game_session(self, score):
        if not self.user_uuid: return False
        query = """
            mutation CreateGameSession($userId: UUID!, $score: Int!) {
                gameSession_insert(data: { userId: $userId, score: $score, createdAt_expr: "request.time" })
            }
        """
        result = await self._execute_graphql(query, {"userId": self.user_uuid, "score": score})
        return result is not None
