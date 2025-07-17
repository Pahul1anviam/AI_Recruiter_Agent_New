import sqlite3

DB_PATH = "calendar_booking.db"

def lock_slot(slot_start_time: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if slot already locked
        cursor.execute("SELECT 1 FROM locked_slots WHERE slot_start_time = ?", (slot_start_time,))
        if cursor.fetchone():
            return False  # Already locked

        # Lock the slot
        cursor.execute("SELECT * FROM locked_slots WHERE slot_start_time = ?", (slot_start_time,))
        conn.commit()
        return True

    except Exception as e:
        print("Lock error:", e)
        return False

    finally:
        conn.close()
