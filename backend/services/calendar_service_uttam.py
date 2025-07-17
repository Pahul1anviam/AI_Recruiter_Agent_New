from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
from pytz import timezone
import os.path
import pickle
 
SCOPES = ['https://www.googleapis.com/auth/calendar']
IST = timezone('Asia/Kolkata')
 
def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds
 
def get_today_range():
    now = datetime.now(IST)
    start = IST.localize(datetime(now.year, now.month, now.day, 10, 0, 0))
    end = IST.localize(datetime(now.year, now.month, now.day, 22, 0, 0))
    return start, end
 
def get_busy_slots_and_events(service, from_time):
    _, end_of_day = get_today_range()
 
    events_result = service.events().list(
        calendarId='primary',
        timeMin=from_time.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
 
    events = events_result.get('items', [])
    busy_slots = []
    scheduled_meetings = []
 
    for event in events:
        start_str = event['start'].get('dateTime')
        end_str = event['end'].get('dateTime')
        summary = event.get('summary', 'No Title')
 
        if start_str and end_str:
            start_time = datetime.fromisoformat(start_str).astimezone(IST)
            end_time = datetime.fromisoformat(end_str).astimezone(IST)
            busy_slots.append((start_time, end_time))
            scheduled_meetings.append((start_time, end_time, summary))
 
    return busy_slots, scheduled_meetings
 
def generate_time_slots(start_time, end_time, duration_minutes=30):
    slots = []
    current = start_time
    while current + timedelta(minutes=duration_minutes) <= end_time:
        slots.append((current, current + timedelta(minutes=duration_minutes)))
        current += timedelta(minutes=duration_minutes)
    return slots
 
def check_availability_and_show(service, requested_start_time: datetime):
    requested_end_time = requested_start_time + timedelta(minutes=30)
    busy_slots, scheduled_meetings = get_busy_slots_and_events(service, requested_start_time)
 
    # Check if requested slot is free
    for start, end in busy_slots:
        if max(start, requested_start_time) < min(end, requested_end_time):
            print("\n❌ This slot is already booked. Please choose another time.")
            break
    else:
        print("\n✅ This slot is available!")
 
    # Show upcoming meetings
    print("\n📅 Upcoming Scheduled Meetings Today:")
    if scheduled_meetings:
        for s, e, title in scheduled_meetings:
            print(f"🔒 {s.strftime('%I:%M %p')} - {e.strftime('%I:%M %p')} | {title}")
    else:
        print("No meetings scheduled for the rest of the day.")
 
    # Show available slots
    print("\n🟢 Available Slots (30 min each after your requested time):")
    _, end_of_day = get_today_range()
    all_slots = generate_time_slots(requested_start_time, end_of_day)
    available_slots = []
 
    for slot_start, slot_end in all_slots:
        if not any(max(slot_start, b_start) < min(slot_end, b_end) for b_start, b_end in busy_slots):
            available_slots.append((slot_start, slot_end))
 
    for s, e in available_slots:
        print(f"🕒 {s.strftime('%I:%M %p')} - {e.strftime('%I:%M %p')}")
 
def parse_input_time(input_str):
    try:
        now = datetime.now(IST)
        time_obj = datetime.strptime(input_str, "%I:%M %p").time()
        custom_dt = IST.localize(datetime(now.year, now.month, now.day, time_obj.hour, time_obj.minute))
        return custom_dt
    except ValueError:
        print("❌ Invalid time format. Please use format like '03:30 PM'")
        return None
 
def main():
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
 
    user_input = input("⏰ Enter a meeting time (e.g., 03:30 PM): ")
    requested_time = parse_input_time(user_input)
 
    
    if requested_time:
        now = datetime.now(IST)
        if requested_time < now:
            print("\n❌ Cannot schedule a meeting in the past. Please enter a future time.")
            return
        check_availability_and_show(service, requested_time)
 
if __name__ == '__main__':
    main()      
