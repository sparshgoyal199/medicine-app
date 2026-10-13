from fastapi import APIRouter, HTTPException, Depends
from datetime import date, datetime, timedelta
from models.schemas import CheckInCreate, CheckInResponse
from utils.auth import get_current_user
from utils.supabase_client import (
    get_supabase_client, 
    create_check_in, 
    get_today_check_ins, 
    get_user_streak, 
    update_streak,
    update_medicine_inventory,
    get_medicine_inventory
)
from utils.mistral_client import calculate_streak_badge
from utils.email_service import send_streak_achievement_email

router = APIRouter(prefix="/checkin", tags=["Check-in"])

@router.post("/", response_model=dict)
async def create_new_check_in(
    check_in_data: CheckInCreate,
    current_user: dict = Depends(get_current_user)
):
    """Log a daily dose check-in"""
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    today = date.today().isoformat()
    
    # Check if user already checked in this time slot today
    today_checkins = await get_today_check_ins(supabase, user_id, today)
    
    for checkin in today_checkins:
        if checkin["time_of_day"] == check_in_data.time_of_day:
            raise HTTPException(
                status_code=400, 
                detail=f"Already checked in for {check_in_data.time_of_day} today"
            )
    
    # Create check-in record
    check_in_record = {
        "user_id": user_id,
        "check_in_date": today,
        "time_of_day": check_in_data.time_of_day,
        "ml_used": check_in_data.ml_used,
        "points_earned": 10,
        "created_at": datetime.utcnow().isoformat()
    }
    
    new_checkin = await create_check_in(supabase, check_in_record)
    
    # Update streak
    streak_data = await get_user_streak(supabase, user_id)
    if not streak_data:
        # Create new streak record
        streak_data = {
            "user_id": user_id,
            "current_streak": 1,
            "longest_streak": 1,
            "total_points": 10,
            "last_check_in": today
        }
    else:
        last_check_in = streak_data.get("last_check_in")
        today_date = date.today()

        if not last_check_in:
            streak_data["current_streak"] = max(streak_data.get("current_streak", 0), 1)
            streak_data["total_points"] = streak_data.get("total_points", 0) + 10
            streak_data["last_check_in"] = today
            streak_data["longest_streak"] = max(
                streak_data.get("longest_streak", 0),
                streak_data["current_streak"],
            )
        else:
            last_date = date.fromisoformat(last_check_in) if isinstance(last_check_in, str) else last_check_in
            days_diff = (today_date - last_date).days

            if days_diff == 0:
                streak_data["total_points"] = streak_data.get("total_points", 0) + 10
            elif days_diff == 1:
                streak_data["current_streak"] = streak_data.get("current_streak", 0) + 1
                streak_data["total_points"] = streak_data.get("total_points", 0) + 10
                streak_data["last_check_in"] = today
                if streak_data["current_streak"] > streak_data.get("longest_streak", 0):
                    streak_data["longest_streak"] = streak_data["current_streak"]
            else:
                streak_data["current_streak"] = 1
                streak_data["total_points"] = streak_data.get("total_points", 0) + 10
                streak_data["last_check_in"] = today
                streak_data["longest_streak"] = max(streak_data.get("longest_streak", 0), 1)

    await update_streak(supabase, user_id, streak_data)
    
    # Check for badge achievement
    badge = calculate_streak_badge(streak_data["current_streak"])
    
    # Update medicine inventory
    inventory = await get_medicine_inventory(supabase, user_id)
    if inventory:
        new_volume = max(0, inventory["current_volume_ml"] - check_in_data.ml_used)
        inventory_update = {
            "user_id": user_id,
            "current_volume_ml": new_volume,
            "last_updated": datetime.utcnow().isoformat()
        }
        await update_medicine_inventory(supabase, user_id, inventory_update)
    
    # Send achievement email if badge earned
    if badge and streak_data["current_streak"] in [7, 30, 60, 90]:
        # Get user email for notification
        from utils.supabase_client import get_user_by_id
        user = await get_user_by_id(supabase, user_id)
        if user:
            send_streak_achievement_email(user["email"], user["name"], streak_data["current_streak"], badge)
    
    return {
        "message": "Check-in successful",
        "check_in": new_checkin,
        "streak": {
            "current_streak": streak_data["current_streak"],
            "total_points": streak_data["total_points"],
            "badge_earned": badge
        }
    }

@router.get("/today", response_model=dict)
async def get_today_status(current_user: dict = Depends(get_current_user)):
    """Get today's check-in status"""
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    today = date.today().isoformat()
    
    today_checkins = await get_today_check_ins(supabase, user_id, today)
    
    morning_done = any(c["time_of_day"] == "morning" for c in today_checkins)
    night_done = any(c["time_of_day"] == "night" for c in today_checkins)
    
    return {
        "date": today,
        "morning_checked_in": morning_done,
        "night_checked_in": night_done,
        "total_check_ins_today": len(today_checkins),
        "check_ins": today_checkins
    }

@router.get("/history", response_model=dict)
async def get_check_in_history(
    limit: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get check-in history"""
    from utils.supabase_client import get_user_check_ins
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    
    checkins = await get_user_check_ins(supabase, user_id, limit)
    
    return {
        "total": len(checkins),
        "check_ins": checkins
    }

@router.get("/streak", response_model=dict)
async def get_streak_info(current_user: dict = Depends(get_current_user)):
    """Get streak information"""
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    
    streak_data = await get_user_streak(supabase, user_id)
    if not streak_data:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "total_points": 0,
            "last_check_in": None,
            "badge": None
        }
    
    badge = calculate_streak_badge(streak_data["current_streak"])
    
    return {
        "current_streak": streak_data.get("current_streak", 0),
        "longest_streak": streak_data.get("longest_streak", 0),
        "total_points": streak_data.get("total_points", 0),
        "last_check_in": streak_data.get("last_check_in"),
        "badge": badge
    }
