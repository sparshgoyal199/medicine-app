from fastapi import APIRouter, HTTPException, Depends
from datetime import date
from models.schemas import UserCreate, UserLogin, UserResponse
from utils.auth import hash_password, verify_password, create_access_token, get_current_user
from utils.supabase_client import get_supabase_client, get_user_by_email, create_user, get_user_by_id
from supabase import Client
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate):
    """Register a new user"""
    supabase = get_supabase_client()
    
    # Check if user already exists
    existing_user = await get_user_by_email(supabase, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user record
    user_record = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "name": user_data.name,
        "password_hash": hashed_password,
        "treatment_start_date": user_data.treatment_start_date.isoformat() if user_data.treatment_start_date else date.today().isoformat(),
        "dosage_frequency": user_data.dosage_frequency,
    }
    
    new_user = await create_user(supabase, user_record)
    if not new_user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    # Create initial streak record
    streak_record = {
        "user_id": new_user["id"],
        "current_streak": 0,
        "longest_streak": 0,
        "total_points": 0,
        "last_check_in": None
    }
    supabase.table("streaks").insert(streak_record).execute()
    
    # Create initial medicine inventory
    inventory_record = {
        "user_id": new_user["id"],
        "bottle_size_ml": 60,
        "current_volume_ml": 60.0,
        "doses_per_day": user_data.dosage_frequency
    }
    supabase.table("medicine_inventory").insert(inventory_record).execute()
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": new_user["id"], "email": new_user["email"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user["id"],
            "email": new_user["email"],
            "name": new_user["name"],
            "treatment_start_date": new_user["treatment_start_date"],
            "dosage_frequency": new_user["dosage_frequency"]
        }
    }

@router.post("/login", response_model=dict)
async def login(user_data: UserLogin):
    """Login user"""
    supabase = get_supabase_client()
    
    # Get user by email
    user = await get_user_by_email(supabase, user_data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "treatment_start_date": user.get("treatment_start_date"),
            "dosage_frequency": user.get("dosage_frequency", 2)
        }
    }

@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    supabase = get_supabase_client()
    user = await get_user_by_id(supabase, current_user["user_id"])
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "treatment_start_date": user.get("treatment_start_date"),
        "dosage_frequency": user.get("dosage_frequency", 2),
        "created_at": user.get("created_at")
    }
