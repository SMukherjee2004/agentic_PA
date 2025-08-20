from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import re
from typing import Dict, Any
from ..models import UserToken

class GoogleCalendar:
    def __init__(self, token: UserToken):
        creds = Credentials(
            token=token.access_token,
            refresh_token=token.refresh_token,
            token_uri=token.token_uri,
            client_id=token.client_id,
            client_secret=token.client_secret,
            scopes=token.scopes.split() if token.scopes else None,
        )
        self.service = build('calendar', 'v3', credentials=creds)

    def _normalize_date(self, date_str: str | None) -> str:
        if not date_str:
            return datetime.utcnow().date().isoformat()
        s = date_str.strip().lower()
        if s == 'tomorrow':
            return (datetime.utcnow() + timedelta(days=1)).date().isoformat()
        if s == 'today':
            return datetime.utcnow().date().isoformat()
        # already ISO
        return s

    def _normalize_time(self, time_str: str | None) -> str:
        if not time_str:
            return '09:00:00'
        s = str(time_str).strip().lower()
        # Handle formats like '7 pm', '7:00 pm', '07:00', '07:00:00'
        m = re.match(r'^(\d{1,2})(?::(\d{2}))?(?::(\d{2}))?\s*(am|pm)?$', s)
        if m:
            hour = int(m.group(1))
            minute = int(m.group(2) or 0)
            second = int(m.group(3) or 0)
            ampm = m.group(4)
            if ampm == 'pm' and hour < 12:
                hour += 12
            if ampm == 'am' and hour == 12:
                hour = 0
            return f"{hour:02d}:{minute:02d}:{second:02d}"
        return s if len(s) == 8 else '09:00:00'

    def create_event(self, entities: Dict[str, Any]):
        try:
            title = entities.get('title') or 'New Event'
            date = entities.get('date')  # expect YYYY-MM-DD or natural like 'tomorrow'
            time = entities.get('time')  # expect HH:MM or natural
            description = entities.get('description')
            attendees = entities.get('attendees') or []
            reminder_minutes = entities.get('reminder_minutes')

            start_date = self._normalize_date(date)
            norm_time = self._normalize_time(time)
            start_dt = datetime.fromisoformat(f"{start_date}T{norm_time}")
            end_dt = start_dt + timedelta(hours=1)

            event_body = {
                'summary': title,
                'description': description,
                'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'UTC'},
                'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'UTC'},
            }
            if attendees:
                event_body['attendees'] = [{'email': a} for a in attendees if isinstance(a, str)]

            if reminder_minutes:
                try:
                    mins = int(reminder_minutes)
                    event_body['reminders'] = {
                        'useDefault': False,
                        'overrides': [{'method': 'popup', 'minutes': mins}]
                    }
                except Exception:
                    pass

            created = self.service.events().insert(calendarId='primary', body=event_body).execute()
            # normalize for reply
            return {
                'success': True,
                'event': {
                    'id': created.get('id'),
                    'summary': created.get('summary'),
                    'start': created.get('start', {}).get('dateTime') or created.get('start', {}).get('date'),
                    'end': created.get('end', {}).get('dateTime') or created.get('end', {}).get('date'),
                    'htmlLink': created.get('htmlLink')
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
