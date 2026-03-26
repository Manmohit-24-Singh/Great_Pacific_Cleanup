import pyrebase
import requests
import json
from firebase_config import firebaseConfig

class FirebaseService:
    def __init__(self):
        try:
            self.firebase = pyrebase.initialize_app(firebaseConfig)
            self.auth = self.firebase.auth()
        except Exception as e:
            print(f"Firebase Init Error: {e}")
            self.auth = None
            
        self.user = None
        self.id_token = None
        self.project_id = firebaseConfig.get("projectId", "YOUR_PROJECT_ID")
        self.location = "us-central1"
        self.service_id = "great-pacific-cleanup"
        self.connector_id = "game"
        self.base_url = f"https://dataconnect.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/services/{self.service_id}/connectors/{self.connector_id}"

    def sign_up(self, email, password, username):
        if not self.auth: return {"success": False, "error": "Firebase not configured"}
        try:
            user = self.auth.create_user_with_email_and_password(email, password)
            self.user = user
            self.id_token = user['idToken']
            
            # Create user profile in the Firestore
            self._update_user_profile(user['localId'], username)
            return {"success": True, "user": user, "username": username}
        except Exception as e:
            return self._parse_error(e)

    def login(self, email, password):
        if not self.auth: return {"success": False, "error": "Firebase not configured"}
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            self.user = user
            self.id_token = user['idToken']
            
            # Get username from user
            username = self._get_username(user['localId'])
            return {"success": True, "user": user, "username": username}
        except Exception as e:
            return self._parse_error(e)

    def logout(self):
        self.user = None
        self.id_token = None

    def _parse_error(self, e):
        try:
            # Pyrebase errors are usually a tuple (reason, response_body)
            error_json = e.args[1]
            error_msg = json.loads(error_json)['error']['message']
        except:
            error_msg = str(e)
        return {"success": False, "error": error_msg}

    def _get_username(self, user_id):
        url = f"{self.base_url}:executeSelection"
        payload = {
            "operationName": "GetUsername",
            "variables": {"id": user_id}
        }
        headers = {"Authorization": f"Bearer {self.id_token}"}
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json().get('data', {})
                user = data.get('user')
                if user:
                    return user['username']
        except Exception as e:
            print(f"DataConnect Error (GetUsername): {e}")
        return "Unknown"

    def _update_user_profile(self, user_id, username):
        url = f"{self.base_url}:executeMutation"
        payload = {
            "operationName": "CreateUser",
            "variables": {
                "id": user_id,
                "username": username
            }
        }
        headers = {"Authorization": f"Bearer {self.id_token}"}
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                print(f"DataConnect Error (CreateUser): {response.status_code} - {response.text}")
        except Exception as e:
            print(f"DataConnect Exception (CreateUser): {e}")

    def get_leaderboard(self, limit=10):
        url = f"{self.base_url}:executeSelection"
        payload = {
            "operationName": "GetLeaderboard",
            "variables": {"limit": limit}
        }
        # Leaderboard query is public (per operations.gql) but can still pass token if available
        headers = {}
        if self.id_token:
            headers["Authorization"] = f"Bearer {self.id_token}"
            
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json().get('data', {})
                users = data.get('users', [])
                leaderboard = []
                for u in users:
                    leaderboard.append({
                        "username": u['username'],
                        "score": u['highScore']
                    })
                return leaderboard
            else:
                print(f"DataConnect Error (GetLeaderboard): {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error fetching leaderboard: {e}")
        return []

    def update_high_score(self, score):
        if not self.user or not self.id_token:
            return False
        
        user_id = self.user['localId']
        url = f"{self.base_url}:executeMutation"
        payload = {
            "operationName": "UpdateHighScore",
            "variables": {
                "id": user_id,
                "score": score
            }
        }
        headers = {"Authorization": f"Bearer {self.id_token}"}
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                print(f"DEBUG: Firebase High Score successfully updated to {score} (SQL)!")
                return True
            else:
                print(f"DataConnect Error (UpdateHighScore): {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"DataConnect Exception (UpdateHighScore): {e}")
            return False
