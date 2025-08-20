from email.mime.text import MIMEText
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from ..models import UserToken


class GoogleGmail:
    def __init__(self, token: UserToken):
        creds = Credentials(
            token=token.access_token,
            refresh_token=token.refresh_token,
            token_uri=token.token_uri,
            client_id=token.client_id,
            client_secret=token.client_secret,
            scopes=token.scopes.split() if token.scopes else None,
        )
        self.service = build('gmail', 'v1', credentials=creds)

    def send_email(self, to: str, subject: str, body: str):
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            result = self.service.users().messages().send(userId='me', body={'raw': raw}).execute()
            return {"success": True, "id": result.get('id')}
        except Exception as e:
            return {"success": False, "error": str(e)}
