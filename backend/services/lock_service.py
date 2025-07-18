import sqlite3
import os

# Fixed DB path to match the main structure
DB_PATH = "db/calendar_booking.db"

def ensure_db_exists():
    """Ensure database and tables exist"""
    if not os.path.exists("db"):
        os.makedirs("db")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create locked_slots table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locked_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_start_time TEXT UNIQUE,
            locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create booked_slots table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS booked_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_time TEXT NOT NULL,
            candidate_email TEXT NOT NULL,
            candidate_name TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('booked', 'pending', 'confirmed')),
            meet_link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def lock_slot(slot_start_time: str) -> bool:
    """
    Lock a slot to prevent race conditions
    Returns True if successfully locked, False if already locked
    """
    ensure_db_exists()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if slot already locked
        cursor.execute("SELECT 1 FROM locked_slots WHERE slot_start_time = ?", (slot_start_time,))
        if cursor.fetchone():
            return False  # Already locked

        # Lock the slot
        cursor.execute("INSERT INTO locked_slots (slot_start_time) VALUES (?)", (slot_start_time,))
        conn.commit()
        return True

    except sqlite3.IntegrityError:
        # Slot was locked by another process
        return False
    except Exception as e:
        print(f"Lock error: {e}")
        return False
    finally:
        conn.close()

def unlock_slot(slot_start_time: str) -> bool:
    """Remove lock from a slot"""
    ensure_db_exists()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM locked_slots WHERE slot_start_time = ?", (slot_start_time,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Unlock error: {e}")
        return False
    finally:
        conn.close()

def is_slot_locked(slot_start_time: str) -> bool:
    """Check if a slot is locked"""
    ensure_db_exists()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT 1 FROM locked_slots WHERE slot_start_time = ?", (slot_start_time,))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Check lock error: {e}")
        return False
    finally:
        conn.close()

def cleanup_old_locks(hours_old: int = 1):
    """Remove locks older than specified hours"""
    ensure_db_exists()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM locked_slots 
            WHERE locked_at < datetime('now', '-{} hours')
        """.format(hours_old))
        conn.commit()
        print(f"Cleaned up {cursor.rowcount} old locks")
    except Exception as e:
        print(f"Cleanup error: {e}")
    finally:
        conn.close()