from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import Dict, Any
from ..models import UserToken


class GoogleDocs:
    def __init__(self, token: UserToken):
        creds = Credentials(
            token=token.access_token,
            refresh_token=token.refresh_token,
            token_uri=token.token_uri,
            client_id=token.client_id,
            client_secret=token.client_secret,
            scopes=token.scopes.split() if token.scopes else None,
        )
        self.service = build('docs', 'v1', credentials=creds)

    def create_doc(self, name: str, content: str):
        try:
            doc = self.service.documents().create(body={"title": name}).execute()
            doc_id = doc.get("documentId")
            if content:
                requests = [{
                    'insertText': {
                        'location': {'index': 1},
                        'text': content
                    }
                }]
                self.service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
            return {"success": True, "documentId": doc_id}
        except Exception as e:
            return {"success": False, "error": str(e)}
