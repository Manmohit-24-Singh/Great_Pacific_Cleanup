"""
Reset Leaderboard — Admin utility

NOTE: The DeleteAllScores mutation is set to @auth(level: NO_ACCESS) in the
Data Connect schema, so it cannot be called from client code.

To reset the leaderboard, use one of these methods:
  1. Firebase Console → Data Connect → Run the mutation from the console
  2. Firebase Admin SDK with service account credentials (server-side only)
  3. Direct Cloud SQL access via `gcloud sql connect`
"""

def reset():
    print("⚠️  DeleteAllScores is locked to NO_ACCESS for security.")
    print("   Use the Firebase Console or Admin SDK to reset the leaderboard.")
    print()
    print("   To reset the local high score file only:")
    with open("high_score.txt", "w") as f:
        f.write("0")
    print("   ✅ Local high_score.txt reset to 0.")

if __name__ == "__main__":
    reset()

