from fastapi import APIRouter, Depends
from datetime import date
from utils.auth import get_current_user
from utils.supabase_client import get_supabase_client, get_user_by_id, get_user_streak
from utils.mistral_client import calculate_timeline_phase

router = APIRouter(prefix="/timeline", tags=["Timeline"])

@router.get("/phase", response_model=dict)
async def get_current_phase(current_user: dict = Depends(get_current_user)):
    """Get user's current treatment phase and progress"""
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    
    # Get user data
    user = await get_user_by_id(supabase, user_id)
    if not user:
        return {
            "error": "User not found",
            "day_number": 0,
            "phase": None
        }
    
    # Calculate day number
    start_date = user.get("treatment_start_date")
    if not start_date:
        return {
            "error": "Treatment start date not set",
            "day_number": 0,
            "phase": None
        }
    
    # Convert string to date if needed
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)
    
    today = date.today()
    day_number = (today - start_date).days + 1
    
    # Ensure day number is at least 1
    day_number = max(1, day_number)
    
    # Get phase information
    phase_info = calculate_timeline_phase(day_number)
    
    # Get user's streak info
    streak_data = await get_user_streak(supabase, user_id)
    
    return {
        "day_number": day_number,
        "start_date": start_date.isoformat(),
        "phase_name": phase_info["phase_name"],
        "phase_message": phase_info["phase_message"],
        "progress_percentage": round(phase_info["progress_percentage"], 1),
        "streak": {
            "current": streak_data.get("current_streak", 0) if streak_data else 0,
            "longest": streak_data.get("longest_streak", 0) if streak_data else 0
        }
    }

@router.get("/milestones", response_model=dict)
async def get_milestones(current_user: dict = Depends(get_current_user)):
    """Get treatment milestones"""
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    
    # Get user data
    user = await get_user_by_id(supabase, user_id)
    if not user:
        return {"error": "User not found"}
    
    # Calculate day number
    start_date = user.get("treatment_start_date")
    if not start_date:
        return {"error": "Treatment start date not set"}
    
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)
    
    today = date.today()
    day_number = (today - start_date).days + 1
    
    # Define milestones
    milestones = [
        {
            "day": 14,
            "title": "Adaptation Complete",
            "description": "Your scalp has adjusted to the treatment",
            "achieved": day_number >= 14
        },
        {
            "day": 45,
            "title": "Shedding Phase Complete",
            "description": "The shedding phase is ending. New growth begins!",
            "achieved": day_number >= 45
        },
        {
            "day": 90,
            "title": "First Results",
            "description": "Visible improvement in hair density",
            "achieved": day_number >= 90
        },
        {
            "day": 180,
            "title": "Full Results",
            "description": "Maximum results from treatment",
            "achieved": day_number >= 180
        }
    ]
    
    # Check-in streak milestones
    streak_data = await get_user_streak(supabase, user_id)
    current_streak = streak_data.get("current_streak", 0) if streak_data else 0
    
    streak_milestones = [
        {
            "days": 7,
            "title": "Consistency Starter",
            "badge": "🥉",
            "achieved": current_streak >= 7
        },
        {
            "days": 30,
            "title": "One Month Strong",
            "badge": "🥈",
            "achieved": current_streak >= 30
        },
        {
            "days": 60,
            "title": "Shedding Survivor",
            "badge": "🥇",
            "achieved": current_streak >= 60
        },
        {
            "days": 90,
            "title": "Regrowth Champion",
            "badge": "🏆",
            "achieved": current_streak >= 90
        }
    ]
    
    return {
        "current_day": day_number,
        "treatment_milestones": milestones,
        "streak_milestones": streak_milestones,
        "next_milestone": next((m for m in milestones if not m["achieved"]), None)
    }
