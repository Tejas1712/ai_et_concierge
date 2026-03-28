# ET AI Concierge

Submission-ready AI concierge that understands user intent and recommends relevant ET offerings through a conversational interface.

## Problem Statement
Economic Times has multiple strong products (Markets, Wealth, Prime, Masterclass, Enterprise, Lifestyle), but users often discover only a subset. This project improves discovery and personalization by:
1. Understanding user intent from conversation.
2. Mapping signals to relevant ET offerings.
3. Returning focused, conversational recommendations.

## What This Project Includes
1. `backend/`: FastAPI + LangChain + Gemini service.
2. `frontend/`: Next.js chat UI with streaming responses.
3. Auth + history + DB persistence (JWT, sessions, chat history, persona profile storage).

## One-Command Run (For Non-Technical Users)
Use this from the project root folder on Windows:

```bat
.\run-project.bat
```

What this command does automatically:
1. Creates backend virtual environment if missing.
2. Installs backend dependencies.
3. Creates `backend/.env` from `backend/.env.example` if missing.
4. Installs frontend dependencies.
5. Creates `frontend/.env` from `frontend/.env.example` if missing.
6. Opens backend and frontend in separate terminals.

After launch:
1. Frontend: `http://localhost:3000`
2. Backend: `http://127.0.0.1:8000`

## One-Command Run Without External Popup Terminals
If popup windows feel unsafe, use the no-popup launcher:

```bat
.\run-project.bat
```

This keeps everything in the same PowerShell session using background jobs.

Important stop disclaimer for combined script:
1. `Ctrl+C` does not always stop both background jobs reliably.
2. Use these commands in the same PowerShell session to stop cleanly:
3. `Get-Job`
4. `Stop-Job -Name et-backend,et-frontend`
5. `Remove-Job -Name et-backend,et-frontend`

Optional setup-only mode:

```powershell
.\run-project.ps1 -SetupOnly
```

Job commands (same PowerShell session):
1. `Get-Job`
2. `Receive-Job -Name et-backend -Keep`
3. `Receive-Job -Name et-frontend -Keep`
4. `Stop-Job -Name et-backend,et-frontend`
5. `Remove-Job -Name et-backend,et-frontend`

## Run Frontend And Backend In Two Separate Terminals
If you want manual control and easy stop with `Ctrl+C`, open two terminals.

Terminal 1 (backend):

```bat
.\run-backend.bat
```

Terminal 2 (frontend):

```bat
.\run-frontend.bat
```

What these do:
1. Backend script: creates `backend/venv` if missing, installs backend dependencies, creates backend `.env` from template if missing, then runs backend in foreground.
2. Frontend script: installs frontend dependencies, creates frontend `.env` from template if missing, then runs frontend in foreground.

Stop behavior:
1. Press `Ctrl+C` in backend terminal to stop backend.
2. Press `Ctrl+C` in frontend terminal to stop frontend.

## macOS / Linux Compatibility
1. `.bat` and `.ps1` launchers are Windows-focused and are not the default path on macOS/Linux.
2. macOS/Linux users should run backend and frontend manually in two terminals.

Backend terminal (macOS/Linux):

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Frontend terminal (macOS/Linux):

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Error Handling Logic Used In Project
### Backend (FastAPI)
1. Input validation errors return standard `422` responses (Pydantic request validation).
2. Empty chat input returns `400` with a clear message (`current_message cannot be empty`).
3. Auth failures return `401` (missing token, invalid/expired token, invalid credentials, invalid token payload).
4. Duplicate signup email returns `409`.
5. Missing or inaccessible chat sessions return `404`.
6. Service readiness issues return `503` (for example, orchestrator or catalog not initialized).
7. Unexpected server exceptions are logged (`logger.exception(...)`) and returned as safe `500` messages without exposing internals.

### Frontend (Next.js)
1. API calls are wrapped in `try/catch` and surface user-friendly messages in the UI.
2. Auth flow reads backend `detail` messages when available and falls back to a default message.
3. Chat send failures keep the UI stable and replace empty assistant placeholders with a helpful fallback response.
4. If server history refresh fails, the app automatically falls back to local history mode instead of breaking the chat UI.

## Run Inside VS Code Integrated Terminal (No External PowerShell Windows)
If you want everything to run directly inside VS Code terminals:
1. Open this folder in VS Code.
2. Press `Ctrl+Shift+P`.
3. Run `Tasks: Run Task`.
4. Select `Run Full Stack (VS Code Integrated)`.

This uses `.vscode/tasks.json` and starts backend + frontend in integrated terminals.

## Minimum Required Configuration
Before first real use, open `backend/.env` and set:
1. `GEMINI_API_KEY`
2. `DATABASE_URL`
3. `JWT_SECRET`

Frontend base URL is in `frontend/.env`:
1. `NEXT_PUBLIC_API_URL=http://localhost:8000`

## Manual Setup (Fallback)
If you do not want to use the launcher:

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python main.py
```

### Frontend
```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

## Key Features
1. Persona extraction from chat.
2. Focused response generation and recommendations.
3. JWT signup/login.
4. Server-side chat session history.
5. Soft-delete from user history view.
6. ET-inspired red/white UI styling.

## API Endpoints (Core)
1. `GET /health`
2. `POST /api/chat`
3. `POST /api/auth/signup`
4. `POST /api/auth/login`
5. `GET /api/history/sessions`
6. `GET /api/history/sessions/{session_id}`

## Testing
Run from project root:

### Backend tests
```bash
cd backend
venv\Scripts\python -m pytest tests -q
```

### Frontend checks
```bash
cd frontend
npm run type-check
npm run test
```

## Troubleshooting
1. If frontend says auth/history failed, check `frontend/.env` points to active backend port.
2. If signup returns `422`, ensure password is at least 8 characters.
3. If login returns `401`, signup likely failed earlier.
4. If launcher is blocked by policy, run from PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run-project.ps1
```