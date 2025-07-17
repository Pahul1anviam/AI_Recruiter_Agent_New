import datetime
import pytz
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build



SCOPES = ['https://www.googleapis.com/auth/calendar']
TIMEZONE = 'Asia/Kolkata'
CALENDAR_ID = 'primary'
SLOT_DURATION = 30  # in minutes
WORK_HOURS_START = 10
WORK_HOURS_END = 19







# Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    return build('calendar', 'v3', credentials=creds)

def get_available_slots(date: str, calendar_id='primary',
                        start_hour=10, end_hour=19, slot_duration=30):
    """
    Get available slots for a given day based on working hours and busy times.
    :param date: format YYYY-MM-DD
    :return: List of available datetime ranges
    """
    service = get_calendar_service()
    timezone = 'Asia/Kolkata'
    tz = pytz.timezone(timezone)

    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
    start_of_day = tz.localize(datetime.datetime.combine(date_obj, datetime.time(start_hour, 0)))
    end_of_day = tz.localize(datetime.datetime.combine(date_obj, datetime.time(end_hour, 0)))

    start_iso = start_of_day.isoformat()
    #this is a change2
    end_iso = end_of_day.isoformat()

    # Fetch busy slots from Google Calendar
    events_result = service.freebusy().query(
        body={
            "timeMin": start_iso,
            "timeMax": end_iso,
            "timeZone": timezone,
            "items": [{"id": calendar_id}]
        }
    ).execute()

    busy_times = events_result['calendars'][calendar_id]['busy']

    # Generate time slots
    current = start_of_day
    available_slots = []
    while current < end_of_day:
        slot_end = current + datetime.timedelta(minutes=slot_duration)
        slot_range = {"start": current, "end": slot_end}

        # Check overlap with busy slots
        overlap = False
        for busy in busy_times:
            busy_start = datetime.datetime.fromisoformat(busy['start'])
            busy_end = datetime.datetime.fromisoformat(busy['end'])

            if slot_range['start'] < busy_end and slot_range['end'] > busy_start:
                overlap = True
                break

        if not overlap:
            available_slots.append(slot_range)

        current = slot_end

    # Format for display
    formatted_slots = [
        f"{slot['start'].strftime('%Y-%m-%d %H:%M')} - {slot['end'].strftime('%H:%M')}"
        for slot in available_slots
    ]

    return formatted_slots


if __name__ == "__main__":
    today = datetime.date.today().strftime("%Y-%m-%d")
    slots = get_available_slots(today)
    print(f"Available slots for {today}:")
    for s in slots:
        print("•", s)

def get_busy_slots(date: str):
    """
    Get busy slots from Google Calendar for a given date.
    :param date: format YYYY-MM-DD
    :return: List of busy time ranges with 'start' and 'end'
    """
    service = get_calendar_service()
    tz = pytz.timezone(TIMEZONE)

    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
    start_of_day = tz.localize(datetime.datetime.combine(date_obj, datetime.time(WORK_HOURS_START, 0)))
    end_of_day = tz.localize(datetime.datetime.combine(date_obj, datetime.time(WORK_HOURS_END, 0)))

    events_result = service.freebusy().query(
        body={
            "timeMin": start_of_day.isoformat(),
            "timeMax": end_of_day.isoformat(),
            "timeZone": TIMEZONE,
            "items": [{"id": CALENDAR_ID}]
        }
    ).execute()

    busy_times = events_result['calendars'][CALENDAR_ID]['busy']
    return busy_times

def book_slot(candidate_name: str, candidate_email: str, start_time_str: str) -> str:
    from datetime import datetime, timedelta
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("calendar", "v3", credentials=creds)

    start_dt = datetime.fromisoformat(start_time_str)
    end_dt = start_dt + timedelta(minutes=30)

    event = {
        'summary': f'Interview with {candidate_name}',
        'description': f'Interview scheduled with {candidate_name}',
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'attendees': [
            {'email': candidate_email},
        ],
        'conferenceData': {
            'createRequest': {
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                'requestId': f"meet_{int(start_dt.timestamp())}"
            }
        }
    }

    event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1
    ).execute()

    meet_link = event.get('hangoutLink', 'No link generated')
    return meet_link




def get_free_slots(date: str):
    """
    Get free slots by subtracting busy slots from working hours.
    :param date: format YYYY-MM-DD
    :return: List of available time ranges in ISO format
    """
    tz = pytz.timezone(TIMEZONE)
    busy_times = get_busy_slots(date)

    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
    start_of_day = tz.localize(datetime.datetime.combine(date_obj, datetime.time(WORK_HOURS_START, 0)))
    end_of_day = tz.localize(datetime.datetime.combine(date_obj, datetime.time(WORK_HOURS_END, 0)))

    available_slots = []
    current = start_of_day

    while current + datetime.timedelta(minutes=SLOT_DURATION) <= end_of_day:
        slot_end = current + datetime.timedelta(minutes=SLOT_DURATION)
        overlap = False

        for busy in busy_times:
            busy_start = datetime.datetime.fromisoformat(busy['start'])
            busy_end = datetime.datetime.fromisoformat(busy['end'])

            if current < busy_end and slot_end > busy_start:
                overlap = True
                break

        if not overlap:
            available_slots.append({
                "start": current.isoformat(),
                "end": slot_end.isoformat()
            })

        current = slot_end

    return available_slots
 