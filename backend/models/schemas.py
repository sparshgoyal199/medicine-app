from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    treatment_start_date: Optional[date] = None
    dosage_frequency: Optional[int] = 2  # 1 = once daily, 2 = twice daily

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    treatment_start_date: Optional[date]
    dosage_frequency: int
    created_at: datetime

# Check-in schemas
class CheckInCreate(BaseModel):
    time_of_day: str  # 'morning' or 'night'
    ml_used: Optional[float] = 1.0

class CheckInResponse(BaseModel):
    id: str
    user_id: str
    check_in_date: date
    time_of_day: str
    ml_used: float
    points_earned: int
    created_at: datetime

# Photo schemas
class PhotoUpload(BaseModel):
    photo_type: str  # 'hairline' or 'crown'
    capture_date: date

class PhotoResponse(BaseModel):
    id: str
    user_id: str
    photo_url: str
    capture_date: date
    day_number: int
    photo_type: str
    created_at: datetime

# Symptom checker schemas
class SymptomQuery(BaseModel):
    concern_type: str

class SymptomResponse(BaseModel):
    id: str
    user_id: str
    concern_type: str
    ai_response: str
    escalated_to_doctor: bool
    created_at: datetime

# Streak schemas
class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    total_points: int
    last_check_in: Optional[date]

# Medicine inventory schemas
class MedicineInventoryResponse(BaseModel):
    bottle_size_ml: int
    current_volume_ml: float
    doses_per_day: int
    days_remaining: int
    refill_needed: bool

# Timeline phase schemas
class TimelinePhase(BaseModel):
    day_number: int
    phase_name: str
    phase_message: str
    progress_percentage: float
