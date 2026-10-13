import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
# Prefer service role key for backend (bypasses RLS). Fall back to anon key for local experiments.
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

def get_supabase_client() -> Client:
    """Create and return a Supabase client instance"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (recommended) or SUPABASE_KEY in .env"
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Database helper functions
async def get_user_by_email(supabase: Client, email: str):
    """Fetch user by email"""
    response = supabase.table("users").select("*").eq("email", email).execute()
    return response.data[0] if response.data else None

async def get_user_by_id(supabase: Client, user_id: str):
    """Fetch user by ID"""
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None

async def create_user(supabase: Client, user_data: dict):
    """Create a new user"""
    response = supabase.table("users").insert(user_data).execute()
    return response.data[0] if response.data else None

async def create_check_in(supabase: Client, check_in_data: dict):
    """Create a new check-in"""
    response = supabase.table("check_ins").insert(check_in_data).execute()
    return response.data[0] if response.data else None

async def get_user_check_ins(supabase: Client, user_id: str, limit: int = 30):
    """Get user's check-in history"""
    response = supabase.table("check_ins").select("*").eq("user_id", user_id).order("check_in_date", desc=True).limit(limit).execute()
    return response.data

async def get_today_check_ins(supabase: Client, user_id: str, check_in_date: str):
    """Get today's check-ins for a user"""
    response = supabase.table("check_ins").select("*").eq("user_id", user_id).eq("check_in_date", check_in_date).execute()
    return response.data

async def get_user_streak(supabase: Client, user_id: str):
    """Get user's streak data"""
    response = supabase.table("streaks").select("*").eq("user_id", user_id).execute()
    return response.data[0] if response.data else None

async def update_streak(supabase: Client, user_id: str, streak_data: dict):
    """Update user's streak"""
    streak_data = {**streak_data, "user_id": user_id}
    existing = await get_user_streak(supabase, user_id)
    if existing and "id" in existing:
        streak_data["id"] = existing["id"]
    response = supabase.table("streaks").upsert(streak_data, on_conflict="user_id").execute()
    return response.data[0] if response.data else None

async def get_user_photos(supabase: Client, user_id: str):
    """Get user's photos"""
    response = supabase.table("photos").select("*").eq("user_id", user_id).order("capture_date", desc=True).execute()
    return response.data

async def create_photo_record(supabase: Client, photo_data: dict):
    """Create a photo record"""
    response = supabase.table("photos").insert(photo_data).execute()
    return response.data[0] if response.data else None

async def get_medicine_inventory(supabase: Client, user_id: str):
    """Get user's medicine inventory"""
    response = supabase.table("medicine_inventory").select("*").eq("user_id", user_id).execute()
    return response.data[0] if response.data else None

async def update_medicine_inventory(supabase: Client, user_id: str, inventory_data: dict):
    """Update medicine inventory"""
    inventory_data = {**inventory_data, "user_id": user_id}
    existing = await get_medicine_inventory(supabase, user_id)
    if existing and "id" in existing:
        inventory_data["id"] = existing["id"]
    response = supabase.table("medicine_inventory").upsert(inventory_data, on_conflict="user_id").execute()
    return response.data[0] if response.data else None

async def create_symptom_query(supabase: Client, query_data: dict):
    """Create a symptom query record"""
    response = supabase.table("symptom_queries").insert(query_data).execute()
    return response.data[0] if response.data else None
