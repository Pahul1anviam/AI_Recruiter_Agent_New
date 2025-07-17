from calendar_service import fetch_busy_slots
from datetime import datetime

date = datetime(2025, 7, 20)
busy = fetch_busy_slots(date)
for slot in busy:
    print(f"⛔ Busy: {slot['start']} to {slot['end']}")
