# test_free_slots.py

from calendar_service import get_free_slots
from datetime import date

today = date.today().strftime("%Y-%m-%d")
free = get_free_slots(today)

print(f"Available slots on {today}:")
for start, end in free:
    print(f"🟩 {start} → {end}")
