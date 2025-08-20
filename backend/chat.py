from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .db import get_db
from .models import ChatLog, UserToken
from .config import settings

router = APIRouter()

class ChatRequest(BaseModel):
    email: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    intent: str
    entities: dict


@router.post('/chat', response_model=ChatResponse)
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    # Fetch user tokens
    token = db.query(UserToken).filter_by(email=req.email).first()
    if not token:
        raise HTTPException(status_code=401, detail="User not authenticated. Please login with Google.")

    # Lazy import to avoid heavy deps at startup
    from .llm.parser import LLMParser
    parser = LLMParser()
    intent, entities = parser.parse(req.message)

    reply = "I didn't understand that."

    if intent == 'calendar.create_event':
        from .google_api.calendar import GoogleCalendar
        gcal = GoogleCalendar(token)
        result = gcal.create_event(entities)
        if result.get('success'):
            start = result['event']['start']
            title = result['event'].get('summary', 'Event')
            reply = f"✅ {title} added for {start}."
        else:
            reply = f"❌ Failed to create event: {result.get('error')}"
    else:
        reply = f"Intent '{intent}' is recognized but not yet implemented in this demo."

    log = ChatLog(email=req.email, user_message=req.message, assistant_message=reply, intent=intent, entities=str(entities))
    db.add(log)
    db.commit()

    return ChatResponse(reply=reply, intent=intent, entities=entities)
