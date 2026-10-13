from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from models.schemas import SymptomQuery, SymptomResponse
from utils.auth import get_current_user
from utils.supabase_client import (
    get_supabase_client, 
    create_symptom_query,
    get_user_by_id
)
from utils.mistral_client import get_ai_response_for_concern

router = APIRouter(prefix="/symptoms", tags=["Symptom Checker"])

# Predefined concerns for quick-tap buttons
PREDEFINED_CONCERNS = [
    {
        "id": "increased_shedding",
        "label": "Losing more hair in shower",
        "icon": "shower"
    },
    {
        "id": "itchy_scalp",
        "label": "Itchy scalp",
        "icon": "itch"
    },
    {
        "id": "flaking_dryness",
        "label": "White flakes on scalp",
        "icon": "flake"
    },
    {
        "id": "redness_irritation",
        "label": "Redness or irritation",
        "icon": "red"
    },
    {
        "id": "missed_dose",
        "label": "Missed a dose",
        "icon": "clock"
    },
    {
        "id": "no_visible_results",
        "label": "No visible results yet",
        "icon": "eye"
    },
    {
        "id": "scalp_tightness",
        "label": "Scalp feels tight",
        "icon": "tension"
    }
]

@router.get("/concerns", response_model=dict)
async def get_predefined_concerns():
    """Get list of predefined concerns for quick-tap buttons"""
    return {
        "concerns": PREDEFINED_CONCERNS
    }

@router.post("/check", response_model=dict)
async def check_symptom(
    query_data: SymptomQuery,
    current_user: dict = Depends(get_current_user)
):
    """Check a symptom and get AI-powered response"""
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    
    # Get user context for personalized response
    user = await get_user_by_id(supabase, user_id)
    user_context = {
        "name": user.get("name"),
        "treatment_start_date": user.get("treatment_start_date"),
        "dosage_frequency": user.get("dosage_frequency")
    } if user else None
    
    # Get AI response
    ai_response = await get_ai_response_for_concern(query_data.concern_type, user_context)
    
    # Save query to database
    query_record = {
        "user_id": user_id,
        "concern_type": query_data.concern_type,
        "ai_response": ai_response["response"],
        "escalated_to_doctor": ai_response.get("escalate", False),
        "created_at": datetime.utcnow().isoformat()
    }
    
    await create_symptom_query(supabase, query_record)
    
    return {
        "concern": query_data.concern_type,
        "response": ai_response["response"],
        "escalate_to_doctor": ai_response.get("escalate", False),
        "recommendation": "Please consult a dermatologist" if ai_response.get("escalate") else "Continue treatment as directed",
    }

@router.get("/history", response_model=dict)
async def get_symptom_history(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get user's symptom query history"""
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    
    response = supabase.table("symptom_queries").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
    
    return {
        "total": len(response.data) if response.data else 0,
        "queries": response.data if response.data else []
    }
