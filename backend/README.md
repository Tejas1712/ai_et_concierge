# Backend - ET AI Concierge

## Overview
This backend is a FastAPI service that powers the ET AI Concierge conversation flow.
It extracts user persona signals, matches relevant ET services, and returns responses in normal or streaming mode.

## Tech Stack
- Python 3.12+
- FastAPI
- LangChain + Google Gemini
- Pydantic
- Pytest + Hypothesis

## Setup
1. Open a terminal in the backend folder.

```bash
cd backend
```

2. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies (latest compatible versions from `requirements.txt`).

```bash
pip install -r requirements.txt
```

4. Create environment file.

```bash
copy .env.example .env
```

5. Fill required values in `.env`:
- `GEMINI_API_KEY` (preferred)
- `GEMINI_MODEL` (default: `gemini-2.5-flash-lite`)

Recommended values:
- `CATALOG_PATH=data/et_catalog.json`
- `CORS_ORIGINS=http://localhost:3000`

## Run
Simple command:

```bash
python main.py
```

If `backend/venv` exists and you started from a different Python, `main.py` automatically switches to the project venv interpreter first. If dependencies are still missing, it installs from `requirements.txt` and then starts the API.

With auto-reload during development:

```bash
python main.py --reload
```

Equivalent explicit uvicorn command:

```bash
venv\Scripts\python -m uvicorn --app-dir . api.main:app --host 127.0.0.1 --port 8000
```

API base URL:
- `http://127.0.0.1:8000`

## Main Endpoints
- `GET /health`
- `POST /api/chat`
- `GET /api/catalog`
- `POST /api/reset`

## Tests
Run all backend tests:

```bash
venv\Scripts\python -m pytest tests -q
```
