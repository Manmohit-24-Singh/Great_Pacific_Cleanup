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
        url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/users/{user_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()['fields']['username']['stringValue']
        except:
            pass
        return "Unknown"

    def _update_user_profile(self, user_id, username):
        url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/users/{user_id}?updateMask.fieldPaths=username&updateMask.fieldPaths=high_score"
        data = {
            "fields": {
                "username": {"stringValue": username},
                "high_score": {"integerValue": 0}
            }
        }
        headers = {"Authorization": f"Bearer {self.id_token}"}
        requests.patch(url, json=data, headers=headers)

    def get_leaderboard(self, limit=10):
        url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents:runQuery"
        query = {
            "structuredQuery": {
                "from": [{"collectionId": "users"}],
                "orderBy": [{"field": {"fieldPath": "high_score"}, "direction": "DESCENDING"}],
                "limit": limit
            }
        }
        try:
            response = requests.post(url, json=query)
            results = response.json()
            leaderboard = []
            for item in results:
                if 'document' in item:
                    fields = item['document']['fields']
                    leaderboard.append({
                        "username": fields.get("username", {}).get("stringValue", "Unknown"),
                        "score": int(fields.get("high_score", {}).get("integerValue", 0))
                    })
            return leaderboard
        except Exception as e:
            print(f"Error fetching leaderboard: {e}")
            return []

    def update_high_score(self, score):
        if not self.user or not self.id_token:
            return False
        
        user_id = self.user['localId']
        url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/users/{user_id}?updateMask.fieldPaths=high_score"
        data = {
            "fields": {
                "high_score": {"integerValue": score}
            }
        }
        headers = {"Authorization": f"Bearer {self.id_token}"}
        try:
            response = requests.patch(url, json=data, headers=headers)
            return response.status_code == 200
        except:
            return False
