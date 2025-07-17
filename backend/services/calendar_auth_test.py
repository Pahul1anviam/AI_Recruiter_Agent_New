# calendar_auth_test.py

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle

# Full access to Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_user():
    creds = None

    # Check if token already exists
    if os.path.exists('token.pickle'):
        print("🔄 Loading token from token.pickle...")
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid creds, do auth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("♻️ Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🌐 Opening browser for authentication...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the new token
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print("✅ Token saved as token.pickle")

    return creds

if __name__ == '__main__':
    authenticate_user()
