from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from datetime import date, datetime
from typing import Optional
from models.schemas import PhotoResponse
from utils.auth import get_current_user
from utils.supabase_client import (
    get_supabase_client, 
    get_user_photos, 
    create_photo_record,
    get_user_by_id
)
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/photos", tags=["Photos"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def _resolve_photo_url(supabase, photo: dict) -> dict:
    """Ensure photo has an accessible signed URL if stored in Supabase storage."""
    photo_copy = dict(photo)
    url = photo_copy.get("photo_url", "")
    if "/progress-photos/" in url:
        path = url.split("/progress-photos/")[-1].split("?")[0]
        try:
            res = supabase.storage.from_("progress-photos").create_signed_url(path, 604800)
            signed = res.get("signedURL") or res.get("signedUrl")
            if signed:
                photo_copy["photo_url"] = signed
        except Exception as e:
            print(f"Warning: could not create signed url for {path}: {e}")
    return photo_copy

@router.post("/upload", response_model=dict)
async def upload_photo(
    file: UploadFile = File(...),
    photo_type: str = Form("hairline"),
    capture_date: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Upload a progress photo"""
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate photo type
    if photo_type not in ["hairline", "crown"]:
        raise HTTPException(status_code=400, detail="Photo type must be 'hairline' or 'crown'")
    
    # Get user to calculate day number
    user = await get_user_by_id(supabase, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate day number
    start_date = user.get("treatment_start_date")
    if start_date:
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        day_number = (date.today() - start_date).days + 1
    else:
        day_number = 1
    
    # Generate unique filename
    file_ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"{user_id}/{photo_type}/{date.today().isoformat()}_{datetime.now().timestamp()}.{file_ext}"
    
    # Read file content
    file_content = await file.read()
    
    # Upload to Supabase Storage
    try:
        supabase.storage.from_("progress-photos").upload(
            filename,
            file_content,
            file_options={"content-type": file.content_type, "upsert": "true"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")
    
    # Store standard base storage path URL
    base_url = f"{SUPABASE_URL.rstrip('/')}/storage/v1/object/public/progress-photos/{filename}"
    
    # Create photo record in database
    photo_record = {
        "user_id": user_id,
        "photo_url": base_url,
        "capture_date": capture_date or date.today().isoformat(),
        "day_number": day_number,
        "photo_type": photo_type,
        "created_at": datetime.utcnow().isoformat()
    }
    
    new_photo = await create_photo_record(supabase, photo_record)
    resolved_photo = _resolve_photo_url(supabase, new_photo or photo_record)
    
    return {
        "message": "Photo uploaded successfully",
        "photo": resolved_photo
    }

@router.get("/", response_model=dict)
async def get_photos(
    photo_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all user photos, optionally filtered by type"""
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    
    raw_photos = await get_user_photos(supabase, user_id)
    photos = [_resolve_photo_url(supabase, p) for p in raw_photos]
    
    # Filter by type if specified
    if photo_type:
        photos = [p for p in photos if p["photo_type"] == photo_type]
    
    # Group by photo type for comparison
    grouped_photos = {
        "hairline": [p for p in photos if p["photo_type"] == "hairline"],
        "crown": [p for p in photos if p["photo_type"] == "crown"]
    }
    
    return {
        "total": len(photos),
        "photos": photos,
        "grouped": grouped_photos
    }

@router.get("/compare", response_model=dict)
async def get_comparison_photos(
    photo_type: str = "hairline",
    current_user: dict = Depends(get_current_user)
):
    """Get first and latest photo for comparison"""
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    
    raw_photos = await get_user_photos(supabase, user_id)
    filtered_photos = [_resolve_photo_url(supabase, p) for p in raw_photos if p["photo_type"] == photo_type]
    
    if len(filtered_photos) < 2:
        return {
            "can_compare": False,
            "message": "Need at least 2 photos to compare",
            "photos": filtered_photos
        }
    
    # First photo (Day 1)
    first_photo = filtered_photos[-1]  # Oldest
    
    # Latest photo
    latest_photo = filtered_photos[0]  # Newest
    
    return {
        "can_compare": True,
        "first_photo": first_photo,
        "latest_photo": latest_photo,
        "days_between": latest_photo["day_number"] - first_photo["day_number"]
    }

@router.delete("/{photo_id}", response_model=dict)
async def delete_photo(
    photo_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a photo"""
    supabase = get_supabase_client()
    user_id = current_user["user_id"]
    
    # Get photo to verify ownership
    response = supabase.table("photos").select("*").eq("id", photo_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    photo = response.data[0]
    
    # Delete from storage
    try:
        # Extract filename from URL
        filename = photo["photo_url"].split("/progress-photos/")[-1]
        supabase.storage.from_("progress-photos").remove([filename])
    except Exception as e:
        print(f"Warning: Could not delete file from storage: {e}")
    
    # Delete from database
    supabase.table("photos").delete().eq("id", photo_id).execute()
    
    return {
        "message": "Photo deleted successfully"
    }
