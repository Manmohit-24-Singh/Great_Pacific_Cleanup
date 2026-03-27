"""
Reset Leaderboard — Admin utility

Resets all scores in the Supabase database. Requires a valid .env
with SUPABASE_URL and SUPABASE_ANON_KEY.

WARNING: This will delete ALL score rows. Use with caution.
"""
from supabase_service import SupabaseService


def reset():
    print("⚠️  This will delete ALL scores from the Supabase database.")
    confirm = input("Type 'yes' to confirm: ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        return

    svc = SupabaseService()
    try:
        svc.supabase.table("scores").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("✅ All scores deleted from Supabase.")
    except Exception as e:
        print(f"❌ Failed to delete scores: {e}")

    # Also reset local high score file
    print("   Resetting local high_score.txt...")
    with open("high_score.txt", "w") as f:
        f.write("0")
    print("   ✅ Local high_score.txt reset to 0.")


if __name__ == "__main__":
    reset()
