@echo off
cd /d "%~dp0"
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate
python -m pip install -r backend\requirements.txt
python -m uvicorn backend.app.main:app --reload --port 8000
