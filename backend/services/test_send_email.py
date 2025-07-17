from calendar_service import get_available_slots
from email_service import send_slot_email
from datetime import date

today = date.today().strftime("%Y-%m-%d")
free_slots = get_available_slots(today)

candidate_email = "psingh1_be21@thapar.edu"
candidate_name = "Pahuljot Singh"

send_slot_email(candidate_email, candidate_name, free_slots[:])  # Send only top 5 slots
