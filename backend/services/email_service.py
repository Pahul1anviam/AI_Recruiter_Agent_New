import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
FROM_EMAIL = "pahuljotsingh16@gmail.com"
APP_PASSWORD = "hplw slgj cgss etcj"



def send_slot_email(candidate_email, candidate_name, slot_list):
    sender_email = "YOUR_EMAIL_ID"
    app_password = "YOUR_APP_PASSWORD"

    subject = f"Interview Slot Selection - {candidate_name}"
    body = f"Dear {candidate_name},<br><br>"
    body += "Please choose one of the available interview slots below and reply with your preferred time:<br><br>"
    
    for i, slot in enumerate(slot_list, 1):  # ✅ Fixed line
        body += f"<b>Slot {i}:</b> {slot}<br>"

    body += "<br>Best regards,<br>HR Team"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = candidate_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        print(f"✅ Email sent to {candidate_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")



def send_confirmation_email(to_email: str, candidate_name: str, slot_time: str, meet_link: str):
    msg = EmailMessage()
    msg["Subject"] = "Interview Confirmed: [AI Recruiter Agent]"
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email

    msg.set_content(
        f"""Hello {candidate_name},

Your interview has been successfully scheduled at {slot_time}.
Here is your Google Meet link to join: {meet_link}

Thank you,
AI Recruiter Agent
"""
    )

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(FROM_EMAIL, APP_PASSWORD)
            server.send_message(msg)
            print("Confirmation email sent.")
    except Exception as e:
        print("Error sending email:", e)
