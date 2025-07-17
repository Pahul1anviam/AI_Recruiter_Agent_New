# test_busy_slots.py

from calendar_service import get_busy_slots
from datetime import date

today = date.today().strftime("%Y-%m-%d")
slots = get_busy_slots(today)

print(f"Busy slots for {today}:")
for start, end in slots:
    print(f"🟥 {start} → {end}")
