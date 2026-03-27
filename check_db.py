from firebase_service import FirebaseService

def check():
    fs = FirebaseService()
    query = """
        query GetCount {
            highScores {
                id
            }
        }
    """
    # Leaderboard data is public — no auth needed
    result = fs._execute_graphql_public(query)
    if result:
        scores = result.get("highScores", [])
        print(f"DEBUG: Found {len(scores)} high scores in DB.")
    else:
        print("DEBUG: Could not fetch scores.")

if __name__ == "__main__":
    check()

