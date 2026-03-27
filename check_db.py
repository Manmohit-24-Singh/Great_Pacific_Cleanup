"""
Check DB — Quick utility to verify Supabase connectivity.
"""
from supabase_service import SupabaseService


def check():
    svc = SupabaseService()
    try:
        res = svc.supabase.table("scores").select("id", count="exact").execute()
        count = len(res.data) if res.data else 0
        print(f"DEBUG: Found {count} score rows in Supabase.")
    except Exception as e:
        print(f"DEBUG: Could not fetch scores — {e}")


if __name__ == "__main__":
    check()
