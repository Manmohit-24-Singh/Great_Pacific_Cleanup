import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_service import FirebaseService

app = Flask(__name__)
CORS(app) # Enable CORS for all routes (to allow the web game to call the API)

firebase = FirebaseService()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.json
    res = firebase.sign_up(data.get('email'), data.get('password'), data.get('username'))
    return jsonify(res)

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    res = firebase.login(data.get('email'), data.get('password'))
    return jsonify(res)

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    limit = request.args.get('limit', default=10, type=int)
    data = firebase.get_leaderboard(limit=limit)
    return jsonify(data)

@app.route('/highscore/user', methods=['GET'])
def get_user_high_score():
    # In a real app, we'd use the user's token, but the current FirebaseService statefully tracks the user
    # For now, we'll keep it stateful for consistency with existing code
    # NOTE: This makes the API not strictly RESTful if multiple users hit the same instance.
    # TODO: In production, pass the ID Token and verify it.
    score = firebase.get_user_high_score()
    return jsonify({"score": score})

@app.route('/highscore/global', methods=['GET'])
def get_global_high_score():
    score = firebase.get_global_high_score()
    return jsonify({"score": score})

@app.route('/highscore/update', methods=['POST'])
def update_high_score():
    data = request.json
    res = firebase.update_high_score(data.get('score'))
    return jsonify({"success": res})

@app.route('/session/record', methods=['POST'])
def record_session():
    data = request.json
    res = firebase.record_game_session(data.get('score'))
    return jsonify({"success": res})

if __name__ == '__main__':
    # Use PORT from environment variable (required for Cloud Run)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
