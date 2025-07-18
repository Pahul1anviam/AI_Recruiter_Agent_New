from calendar_service import get_available_slots
from email_service import send_slot_email
from datetime import date

today = date.today().strftime("%Y-%m-%d")
free_slots = get_available_slots(today)

candidate_email = "example"
candidate_name = "example"

send_slot_email(candidate_email, candidate_name, free_slots[:])  # Send only top 5 slots
