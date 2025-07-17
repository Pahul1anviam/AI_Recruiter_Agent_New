from datetime import datetime, timedelta
from backend.services.calendar_service import get_available_slots, book_slot
from backend.services.email_service import send_confirmation_email
from backend.services.lock_service import lock_slot
from fastapi import HTTPException


def confirm_slot(selected_slot: str, candidate_name: str, candidate_email: str) -> str:
    # Re-check if the slot is still available
    slot_date = selected_slot.split("T")[0]
    available_slots = get_available_slots(slot_date)

    if selected_slot not in [slot["start"] for slot in available_slots]:
        raise HTTPException(status_code=409, detail="Slot already booked or unavailable.")

    # Lock slot in DB (SQLite)
    if not lock_slot(selected_slot):
        raise HTTPException(status_code=409, detail="Slot is already locked by another candidate.")

    # Book in Google Calendar
    meet_link = book_slot(candidate_name, candidate_email, selected_slot)

    # Send confirmation email
    send_confirmation_email(candidate_email, candidate_name, selected_slot, meet_link)

    return meet_link
