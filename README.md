# Agentic Personal Assistant

Chat-based personal assistant integrating Google Calendar, Sheets, Docs, and Gmail.

## Features
- Google OAuth login (stores tokens in SQLite)
- Chat UI (React + Tailwind)
- LLM parsing via Hugging Face (zero-shot intent + T5 extraction)
- Calendar event creation (example wired)
- Dockerized frontend + backend

## Prerequisites
- Docker & Docker Compose
- Google Cloud project with OAuth 2.0 credentials (Web application)
	- Authorized redirect URI: `http://localhost:8000/auth/google/callback`

## Environment
Set environment variables before running Docker:

Windows PowerShell example:

```
$env:GOOGLE_CLIENT_ID="<your_client_id>"; $env:GOOGLE_CLIENT_SECRET="<your_client_secret>"
```

Optional:
- FRONTEND_URL (default http://localhost:5173)
- BACKEND_URL (default http://localhost:8000)

## Run with Docker

```
docker compose up --build
```

Backends:
- Backend: http://localhost:8000 (GET /health)
- Frontend: http://localhost:5173

## Local development
Backend:
1. Python 3.11
2. `pip install -r backend/requirements.txt`
3. `uvicorn backend.app:app --reload`

Frontend:
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## Google Cloud Setup
1. Create a project at https://console.cloud.google.com/
2. Configure OAuth consent screen (External or Internal)
3. Create OAuth 2.0 Client ID (Web application)
4. Add Authorized redirect URI: `http://localhost:8000/auth/google/callback`
5. Copy client ID and client secret into environment variables

## Testing
Run pytest (basic LLM parsing tests):

```
pytest -q
```

## Notes
- Minimal working example wires Calendar create event. Extend similarly for Sheets/Docs/Gmail.
- Models used: `facebook/bart-large-mnli` and `google/flan-t5-base` (download on first run).
- SQLite DB is in `db/app.db` (mounted in Docker).

