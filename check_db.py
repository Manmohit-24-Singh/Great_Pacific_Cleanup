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
    result = fs._execute_graphql(query)
    if result:
        scores = result.get("highScores", [])
        print(f"DEBUG: Found {len(scores)} high scores in DB.")
    else:
        print("DEBUG: Could not fetch scores.")

if __name__ == "__main__":
    check()
