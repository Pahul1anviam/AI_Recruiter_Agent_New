import sqlite3

# Connect to (or create) the SQLite DB
conn = sqlite3.connect("calendar_booking.db")
cursor = conn.cursor()

# Create the locked_slots table
cursor.execute("""
CREATE TABLE IF NOT EXISTS locked_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_start_time TEXT UNIQUE
)
""")

conn.commit()
conn.close()

print("✅ locked_slots table created successfully.")
