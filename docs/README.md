# Polyglot Captions

A multi-language caption app for transcription + translation.

- Sprint 2: local prototype with stub services.
- Sprint 3: routers + Azure Translator + Azure SQL logging + connected frontend.

---

## Setup & Local Run (Backend)

```bash
# From repo root
cd app

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI backend (local dev)
uvicorn main:app --reload --port 8000
