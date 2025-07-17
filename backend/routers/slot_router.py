from fastapi import APIRouter, HTTPException
from backend.services.calendar_service import get_available_slots, get_busy_slots, get_free_slots
from backend.services.confirm_slot_service import confirm_slot
from backend.services.email_service import send_slot_email, send_confirmation_email
from backend.services.lock_service import lock_slot
from backend.services.calendar_service import book_slot
from pydantic import BaseModel, EmailStr, Field
from datetime import date

router = APIRouter()

# ✅ Route to fetch raw available slots (optional, for testing)
@router.get("/available-slots")
def available_slots():
    try:
        busy = get_busy_slots()
        free = get_free_slots(busy)
        return {"available_slots": free}
    except Exception as e:
        print("Error:", e)
        return {"available_slots": []}

# ✅ Slot email sender
class SlotRequest(BaseModel):
    candidate_email: EmailStr
    candidate_name: str
    interview_date: date = Field(default_factory=date.today)

@router.post("/send-interview-slots")
def send_interview_slots(req: SlotRequest):
    try:
        free_slots = get_available_slots(req.interview_date.strftime("%Y-%m-%d"))

        if not free_slots:
            raise HTTPException(status_code=404, detail="No free slots available.")

        top_slots = free_slots[:5]  # Send only top 5
        send_slot_email(req.candidate_email, req.candidate_name, top_slots)

        return {"message": f"Email sent to {req.candidate_email} with available slots."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Slot confirmation handler
class ConfirmSlotRequest(BaseModel):
    candidate_name: str
    candidate_email: str
    slot_time: str  # ISO format

@router.post("/confirm-slot")
def confirm_slot(data: ConfirmSlotRequest):
    # Step 1: Try to lock the slot
    locked = lock_slot(data.slot_time)
    if not locked:
        raise HTTPException(status_code=409, detail="Slot already taken. Please choose another.")

    # Step 2: Book event in Google Calendar
    try:
        meet_link = book_slot(
            candidate_name=data.candidate_name,
            candidate_email=data.candidate_email,
            start_time_str=data.slot_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calendar booking failed: {str(e)}")

    # Step 3: Send confirmation email
    try:
        send_confirmation_email(
            to_email=data.candidate_email,
            candidate_name=data.candidate_name,
            slot_time=data.slot_time,
            meet_link=meet_link
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")

    return {"status": "success", "meet_link": meet_link}
