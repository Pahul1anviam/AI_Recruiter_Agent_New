import sqlite3
import os

DB_PATH = "db/calendar_booking.db"

def create_db():
    if not os.path.exists("db"):
        os.mkdir("db")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS booked_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_time TEXT NOT NULL,
            candidate_email TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('booked', 'pending')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database created at: {DB_PATH}")

if __name__ == "__main__":
    create_db()
