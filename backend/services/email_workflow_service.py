import smtplib
import sqlite3
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from backend.services.calendar_service import get_available_slots
from backend.services.lock_service import ensure_db_exists

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
FROM_EMAIL = "YOUR_EMAIL_ID"
APP_PASSWORD = "YOUR_PASSWORD"
DB_PATH = "db/calendar_booking.db"

class EmailWorkflowService:
    def __init__(self):
        ensure_db_exists()
    
    def send_shortlisting_email(self, candidate_email: str, candidate_name: str, 
                              job_title: str, score: int) -> bool:
        """
        Send initial shortlisting email asking for availability
        """
        subject = f"Congratulations! You're shortlisted for {job_title}"
        
        body = f"""
        <html>
        <body>
            <h2>Congratulations {candidate_name}!</h2>
            <p>We are pleased to inform you that you have been shortlisted for the position of <strong>{job_title}</strong>.</p>
            <p>Your application scored <strong>{score}/100</strong> in our initial screening.</p>
            
            <h3>Next Steps:</h3>
            <p>We would like to schedule an interview with you. Please reply to this email with your preferred date(s) for the interview in the following format:</p>
            
            <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <strong>AVAILABILITY: YYYY-MM-DD</strong><br>
                Example: AVAILABILITY: 2025-07-25
            </div>
            
            <p>We will then send you available time slots for your selected date.</p>
            
            <p>Looking forward to hearing from you!</p>
            
            <br>
            <p>Best regards,<br>
            HR Team<br>
            AI Recruiter Agent</p>
        </body>
        </html>
        """
        
        return self._send_email(candidate_email, subject, body)
    
    def send_slot_selection_email(self, candidate_email: str, candidate_name: str, 
                                 interview_date: str, slots: List[str]) -> bool:
        """
        Send email with available slots for selection
        """
        subject = f"Interview Slots Available - {candidate_name}"
        
        slots_html = ""
        for i, slot in enumerate(slots, 1):
            slots_html += f"""
            <div style="margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                <strong>Option {i}:</strong> {slot}
            </div>
            """
        
        # Generate unique booking links for each slot
        booking_links = ""
        for i, slot in enumerate(slots, 1):
            # Create a simple booking URL (you can implement a web interface later)
            booking_url = f"http://localhost:8000/book-slot?email={candidate_email}&slot={slot}&name={candidate_name}"
            booking_links += f"""
            <a href="{booking_url}" 
               style="display: inline-block; margin: 5px; padding: 10px 20px; 
                      background-color: #007bff; color: white; text-decoration: none; 
                      border-radius: 5px;">
                Book Slot {i}
            </a>
            """
        
        body = f"""
        <html>
        <body>
            <h2>Interview Slots Available</h2>
            <p>Dear {candidate_name},</p>
            <p>Thank you for your interest! We have the following time slots available for <strong>{interview_date}</strong>:</p>
            
            {slots_html}
            
            <h3>How to Book:</h3>
            <p>Click on one of the buttons below to book your preferred slot:</p>
            <div style="margin: 20px 0;">
                {booking_links}
            </div>
            
            <p><strong>Note:</strong> Slots are available on a first-come, first-served basis.</p>
            
            <p>Alternatively, reply to this email with your preferred slot number (1-{len(slots)}).</p>
            
            <br>
            <p>Best regards,<br>
            HR Team</p>
        </body>
        </html>
        """
        
        return self._send_email(candidate_email, subject, body)
    
    def send_confirmation_email(self, candidate_email: str, candidate_name: str, 
                               slot_time: str, meet_link: str) -> bool:
        """
        Send interview confirmation email with Google Meet link
        """
        # Format the datetime for better readability
        slot_dt = datetime.fromisoformat(slot_time.replace('Z', '+00:00'))
        formatted_time = slot_dt.strftime("%B %d, %Y at %I:%M %p")
        
        subject = f"Interview Confirmed - {formatted_time}"
        
        body = f"""
        <html>
        <body>
            <h2>Interview Confirmed!</h2>
            <p>Dear {candidate_name},</p>
            <p>Your interview has been successfully scheduled for:</p>
            
            <div style="background-color: #e8f5e8; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3 style="color: #2e7d32; margin: 0 0 10px 0;">📅 Interview Details</h3>
                <p><strong>Date & Time:</strong> {formatted_time}</p>
                <p><strong>Duration:</strong> 30 minutes</p>
                <p><strong>Meeting Link:</strong> <a href="{meet_link}" style="color: #1976d2;">{meet_link}</a></p>
            </div>
            
            <h3>Before the Interview:</h3>
            <ul>
                <li>Please join the meeting 5 minutes early</li>
                <li>Ensure you have a stable internet connection</li>
                <li>Test your camera and microphone</li>
                <li>Keep your resume and relevant documents ready</li>
            </ul>
            
            <p>If you need to reschedule, please reply to this email at least 24 hours before the interview.</p>
            
            <p>We look forward to meeting you!</p>
            
            <br>
            <p>Best regards,<br>
            HR Team<br>
            AI Recruiter Agent</p>
        </body>
        </html>
        """
        
        return self._send_email(candidate_email, subject, body)
    
    def parse_availability_email(self, email_body: str) -> Optional[str]:
        """
        Parse candidate's email to extract availability date
        Expected format: AVAILABILITY: YYYY-MM-DD
        """
        patterns = [
            r'AVAILABILITY:\s*(\d{4}-\d{2}-\d{2})',
            r'available.*?(\d{4}-\d{2}-\d{2})',
            r'prefer.*?(\d{4}-\d{2}-\d{2})',
            r'(\d{4}-\d{2}-\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, email_body, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    # Validate date format
                    datetime.strptime(date_str, "%Y-%m-%d")
                    return date_str
                except ValueError:
                    continue
        
        return None
    
    def parse_slot_selection_email(self, email_body: str) -> Optional[int]:
        """
        Parse candidate's email to extract slot selection
        Expected format: slot number (1-5)
        """
        patterns = [
            r'slot\s*(\d+)',
            r'option\s*(\d+)',
            r'choose\s*(\d+)',
            r'prefer\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, email_body, re.IGNORECASE)
            if match:
                slot_num = int(match.group(1))
                if 1 <= slot_num <= 5:  # Assuming max 5 slots
                    return slot_num
        
        return None
    
    def store_candidate_workflow(self, candidate_email: str, candidate_name: str, 
                               job_title: str, score: int, status: str = "shortlisted") -> bool:
        """
        Store candidate workflow information in database
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS candidate_workflow (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_email TEXT NOT NULL,
                    candidate_name TEXT NOT NULL,
                    job_title TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                INSERT INTO candidate_workflow 
                (candidate_email, candidate_name, job_title, score, status)
                VALUES (?, ?, ?, ?, ?)
            """, (candidate_email, candidate_name, job_title, score, status))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()
    
    def update_candidate_status(self, candidate_email: str, status: str) -> bool:
        """
        Update candidate workflow status
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE candidate_workflow 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE candidate_email = ?
            """, (status, candidate_email))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()
    
    def get_candidate_workflow(self, candidate_email: str) -> Optional[Dict]:
        """
        Get candidate workflow information
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM candidate_workflow 
                WHERE candidate_email = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (candidate_email,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
            
        except Exception as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()
    
    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Internal method to send email
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = FROM_EMAIL
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(FROM_EMAIL, APP_PASSWORD)
                server.send_message(msg)
            
            print(f"✅ Email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

# Usage example
if __name__ == "__main__":
    workflow = EmailWorkflowService()
    
    # Example: Send shortlisting email
    workflow.send_shortlisting_email(
        candidate_email="candidate@example.com",
        candidate_name="John Doe",
        job_title="Software Engineer",
        score=85
    )
