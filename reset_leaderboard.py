from firebase_service import FirebaseService

def reset():
    fs = FirebaseService()
    print("Connecting to Data Connect...")
    
    query = """
        mutation DeleteAllScores {
            highScore_deleteMany(all: true)
            gameSession_deleteMany(all: true)
        }
    """
    
    result = fs._execute_graphql(query)
    if result is not None:
        print("✅ Success! Leaderboard and Game History have been cleared.")
        # Also reset the local file
        with open("high_score.txt", "w") as f:
            f.write("0")
        print("✅ Local high_score.txt reset to 0.")
    else:
        print("❌ Failed to reset leaderboard. Make sure you have deployed the mutations.")

if __name__ == "__main__":
    reset()
