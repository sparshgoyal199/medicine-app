"""
Gmail dose reminders. Call /notifications/run-daily from Windows Task Scheduler
twice daily (e.g. 8:00 and 22:00 IST) with header X-Cron-Secret.
"""
from datetime import date, datetime
import os

from fastapi import APIRouter, HTTPException, Header, Depends

from utils.auth import get_current_user
from utils.supabase_client import get_supabase_client, get_today_check_ins, get_user_by_id
from utils.email_service import send_check_in_reminder, send_refill_reminder
from utils.supabase_client import get_medicine_inventory

router = APIRouter(prefix="/notifications", tags=["Notifications"])

CRON_SECRET = os.getenv("CRON_SECRET", "")


@router.post("/run-daily")
async def run_daily_reminders(x_cron_secret: str = Header(..., alias="X-Cron-Secret")):
    """Send morning/night reminder emails to users who have not logged that dose today."""
    if not CRON_SECRET or x_cron_secret != CRON_SECRET:
        raise HTTPException(status_code=403, detail="Invalid cron secret")

    supabase = get_supabase_client()
    hour = datetime.now().hour
    if hour < 14:
        slot = "morning"
    else:
        slot = "night"

    users_resp = supabase.table("users").select("id, email, name, dosage_frequency").execute()
    users = users_resp.data or []

    sent = 0
    today = date.today().isoformat()

    for user in users:
        freq = user.get("dosage_frequency", 2)
        if slot == "morning" and freq == 1:
            continue

        checkins = await get_today_check_ins(supabase, user["id"], today)
        done = any(c["time_of_day"] == slot for c in checkins)
        if done:
            continue

        if send_check_in_reminder(user["email"], user["name"], slot):
            sent += 1

    return {"slot": slot, "emails_sent": sent, "users_checked": len(users)}


@router.post("/refill-check")
async def run_refill_notifications(x_cron_secret: str = Header(..., alias="X-Cron-Secret")):
    """Email users whose virtual bottle has ≤7 days remaining."""
    if not CRON_SECRET or x_cron_secret != CRON_SECRET:
        raise HTTPException(status_code=403, detail="Invalid cron secret")

    supabase = get_supabase_client()
    inv_resp = supabase.table("medicine_inventory").select("*").execute()
    inventories = inv_resp.data or []
    sent = 0

    for inv in inventories:
        ml_per_day = inv.get("doses_per_day", 2) * 1.0
        volume = float(inv.get("current_volume_ml", 60))
        days_remaining = int(volume / ml_per_day) if ml_per_day > 0 else 0
        if days_remaining > 7:
            continue

        user = await get_user_by_id(supabase, inv["user_id"])
        if not user:
            continue
        if send_refill_reminder(user["email"], user["name"], days_remaining):
            sent += 1

    return {"emails_sent": sent, "bottles_checked": len(inventories)}


@router.post("/test-reminder")
async def test_reminder_to_self(current_user: dict = Depends(get_current_user)):
    """Send a test dose reminder email to the logged-in user (for setup verification)."""
    supabase = get_supabase_client()
    user = await get_user_by_id(supabase, current_user["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ok = send_check_in_reminder(user["email"], user["name"], "night")
    if not ok:
        raise HTTPException(
            status_code=500,
            detail="Could not send email. Check SMTP_EMAIL and SMTP_PASSWORD in backend/.env",
        )
    return {"message": f"Test reminder sent to {user['email']}"}
