import types
from backend.google_api.calendar import GoogleCalendar

class DummyEvents:
    def __init__(self):
        self._body = None
    def insert(self, calendarId, body):
        self._body = body
        return self
    def execute(self):
        return {
            'id': 'evt_123',
            'summary': self._body.get('summary'),
            'start': self._body.get('start'),
            'end': self._body.get('end'),
            'htmlLink': 'http://example.com/event'
        }

class DummyService:
    def events(self):
        return DummyEvents()


def test_calendar_create_event_monkeypatch(monkeypatch):
    # Monkeypatch __init__ to avoid Google creds and use dummy service
    def fake_init(self, token):
        self.service = DummyService()
    monkeypatch.setattr(GoogleCalendar, '__init__', fake_init)

    gcal = GoogleCalendar(token=None)
    res = gcal.create_event({'title': 'Test', 'date': '2025-01-02', 'time': '10:00:00', 'reminder_minutes': 30})
    assert res['success'] is True
    assert res['event']['summary'] == 'Test'
