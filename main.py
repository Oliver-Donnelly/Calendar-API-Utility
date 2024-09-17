import os, datetime
#YOU MUST CREATE A PROJECT ON GOOGLE CLOUD AND ADD THE CREDENTIALS FILE.
#install these packages with this command: pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

#all dates interacting with google calendar API must be in the format of YYYY-M-d T HH:mm:ss (remove the spaces)

#function to create the necessary token to use google calendar api, if it allready exists, continue
def createToken():
    creds = None

    if os.path.exists("token.json"):
       creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
           creds.refresh(Request())
        else:
           flow = InstalledAppFlow.from_client_secrets_file("Calendar-API-Utility\credentials.json", SCOPES) # you may have to change the credentials.json to the relative path of the file.
           creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        global service
        service = build("calendar", "v3", credentials=creds)

    except HttpError as error:
        print(f"An error occurred: {error}")


#fuction to easily create an event on calendar of signed in user.
#all dates interacting with google calendar API must be in the format of YYYY-M-d T HH:mm:ss (remove the spaces)
def createEvent(title, color, date, startTime, endTime, allDay=False, allowDuplicates = True):

    event = {
        "summary": title,
        "colorId": color,
        "start": {
            "date": date if allDay else None,
            "dateTime": None if allDay else date + 'T' + startTime + ':00',
            "timeZone": 'America/New_York'
            },
        "end": {
            "date": date if allDay else None,
            "dateTime": None if allDay else date + 'T' + endTime + ':00',
            "timeZone": 'America/New_York'
            }
    }
    if allowDuplicates == False:
        existing_events = getEvents(date)
        event_exists = any(existing_event['summary'] == title for existing_event in existing_events)

        if not event_exists:
            event = service.events().insert(calendarId="primary",body=event).execute()
        else:
            print(f'Event "{title}" on {date} already exists')
    else: 
        event = service.events().insert(calendarId="primary",body=event).execute()


#all dates interacting with google calendar API must be in the format of YYYY-M-d T HH:mm:ss (remove the spaces)
def getEvents(date):
    events_result = (service.events().list(calendarId="primary", timeMin=date + 'T00:00:00Z', timeMax=date + 'T23:59:59Z').execute())
    events = events_result.get('items', [])
    return events


#function deletes every event on a given date
def clearDay(date):
    for event in getEvents(date):
        deleteEvent(event)

#fuction deletes a specific event on a given date
def deleteEvent(event):
    print(event['id'])
    service.events().delete(calendarId='primary', eventId=event['id']).execute()
    

def main():
    createToken() # you must create the token before using other fuctions


if __name__ == '__main__':
    main()