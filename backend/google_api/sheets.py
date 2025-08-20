from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import Dict, Any, List
from ..models import UserToken


class GoogleSheets:
    def __init__(self, token: UserToken):
        creds = Credentials(
            token=token.access_token,
            refresh_token=token.refresh_token,
            token_uri=token.token_uri,
            client_id=token.client_id,
            client_secret=token.client_secret,
            scopes=token.scopes.split() if token.scopes else None,
        )
        self.service = build('sheets', 'v4', credentials=creds)

    def append_row(self, spreadsheet_id: str, sheet_name: str, row: List[str]):
        body = {"values": [row]}
        try:
            result = (
                self.service.spreadsheets()
                .values()
                .append(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A1", valueInputOption="RAW", body=body)
                .execute()
            )
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
