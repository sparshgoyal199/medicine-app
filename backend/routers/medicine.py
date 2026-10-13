from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from utils.auth import get_current_user
from utils.supabase_client import (
    get_supabase_client, 
    get_medicine_inventory, 
    update_medicine_inventory,
    get_user_by_id
)
from utils.email_service import send_refill_reminder

router = APIRouter(prefix="/medicine", tags=["Medicine Inventory"])

@router.get("/inventory", response_model=dict)
async def get_inventory(current_user: dict = Depends(get_current_user)):
    """Get current medicine bottle inventory"""
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    
    inventory = await get_medicine_inventory(supabase, user_id)
    
    if not inventory:
        # Create default inventory
        inventory_data = {
            "user_id": user_id,
            "bottle_size_ml": 60,
            "current_volume_ml": 60.0,
            "doses_per_day": 2
        }
        inventory = await update_medicine_inventory(supabase, user_id, inventory_data)
    
    # Calculate days remaining
    ml_per_day = inventory.get("doses_per_day", 2) * 1.0  # 1ml per dose
    current_volume = inventory.get("current_volume_ml", 60.0)
    days_remaining = int(current_volume / ml_per_day) if ml_per_day > 0 else 0
    
    # Check if refill needed (less than 7 days)
    refill_needed = days_remaining <= 7
    
    return {
        "bottle_size_ml": inventory.get("bottle_size_ml", 60),
        "current_volume_ml": current_volume,
        "doses_per_day": inventory.get("doses_per_day", 2),
        "days_remaining": days_remaining,
        "refill_needed": refill_needed,
        "percentage_remaining": (current_volume / inventory.get("bottle_size_ml", 60)) * 100
    }

@router.post("/refill", response_model=dict)
async def log_refill(current_user: dict = Depends(get_current_user)):
    """Log a new bottle refill (reset bottle to full)"""
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    
    inventory = await get_medicine_inventory(supabase, user_id)
    
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    # Reset bottle to full
    inventory_update = {
        "user_id": user_id,
        "current_volume_ml": float(inventory["bottle_size_ml"]),
        "last_updated": datetime.utcnow().isoformat()
    }
    
    updated_inventory = await update_medicine_inventory(supabase, user_id, inventory_update)
    
    return {
        "message": "Refill logged successfully",
        "inventory": updated_inventory
    }

@router.put("/settings", response_model=dict)
async def update_medicine_settings(
    doses_per_day: int = None,
    bottle_size_ml: int = None,
    current_user: dict = Depends(get_current_user)
):
    """Update medicine settings"""
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    
    inventory = await get_medicine_inventory(supabase, user_id)
    
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    update_data = {
        "user_id": user_id,
        "last_updated": datetime.utcnow().isoformat()
    }
    
    if doses_per_day is not None:
        if doses_per_day not in [1, 2]:
            raise HTTPException(status_code=400, detail="Doses per day must be 1 or 2")
        update_data["doses_per_day"] = doses_per_day
    
    if bottle_size_ml is not None:
        update_data["bottle_size_ml"] = bottle_size_ml
    
    updated_inventory = await update_medicine_inventory(supabase, user_id, update_data)
    
    return {
        "message": "Settings updated successfully",
        "inventory": updated_inventory
    }

@router.post("/check-refill", response_model=dict)
async def check_and_notify_refill(current_user: dict = Depends(get_current_user)):
    """Check if refill is needed and send notification"""
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    
    inventory = await get_medicine_inventory(supabase, user_id)
    user = await get_user_by_id(supabase, user_id)
    
    if not inventory or not user:
        raise HTTPException(status_code=404, detail="User or inventory not found")
    
    # Calculate days remaining
    ml_per_day = inventory.get("doses_per_day", 2) * 1.0
    current_volume = inventory.get("current_volume_ml", 60.0)
    days_remaining = int(current_volume / ml_per_day) if ml_per_day > 0 else 0
    
    if days_remaining <= 7:
        # Send refill reminder email
        send_refill_reminder(user["email"], user["name"], days_remaining)
        return {
            "refill_needed": True,
            "days_remaining": days_remaining,
            "notification_sent": True,
            "order_url": "https://manmatters.com"
        }
    
    return {
        "refill_needed": False,
        "days_remaining": days_remaining,
        "notification_sent": False
    }
