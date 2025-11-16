# Polyglot Captions

A multi-language caption app (Sprint 2 prototype) for transcription + translation.

## Setup & Local Run

```bash
# Create and activate virtual environment
cd app
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI backend
uvicorn app.main:app --reload --port 8000

# Open frontend
open ../frontend/index.html  # or serve via any local web server
