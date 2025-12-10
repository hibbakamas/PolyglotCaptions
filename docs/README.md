# Polyglot Captions

Multi-language captioning app (FastAPI + browser UI) with Azure Speech + Translator integrations, Application Insights telemetry, and optional Azure SQL logging.

## What You Get
- FastAPI backend that also serves the frontend (login, record, manual translate, history).
- Speech-to-text via Azure Speech with a stub fallback when no key is provided.
- Translation via Azure Translator with a stub fallback when no key is provided.
- JWT auth (register/login) and per-user caption CRUD operations.
- Optional Azure SQL logging and Application Insights telemetry.

## Prerequisites
- Python 3.11 (matches the Docker image).
- ffmpeg on PATH (webm to wav conversion for STT).
- ODBC Driver 18 for SQL Server if you want Azure SQL logging.
- Azure Speech + Translator keys for full fidelity; otherwise stubs return synthetic text.
- Optional: Application Insights instrumentation key.

## Quickstart (local)
```bash
# From repo root
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

Create `.env` in the repo root (loaded automatically by pydantic-settings):
```
AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=eastus

AZURE_TRANSLATOR_KEY=
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com
AZURE_TRANSLATOR_REGION=eastus
USE_AZURE_TRANSLATOR=false

LOG_CAPTIONS_TO_DB=false
AZURE_SQL_CONNECTION_STRING=Driver={ODBC Driver 18 for SQL Server};Server=...;Database=...;Uid=...;Pwd=...;Encrypt=yes;TrustServerCertificate=yes;
DB_SERVER=
DB_NAME=
DB_USER=
DB_PASSWORD=

APP_INSIGHTS_KEY=
SECRET_KEY=             # optional; auto-generated if blank
CI=true                 # set to force in-memory stub DB (no Azure SQL)
```

Run the API and frontend (served by FastAPI):
```bash
uvicorn app.main:app --reload --port 8000
# Open http://localhost:8000 to reach the login page; bearer token is required for API calls.
```

Register then login to obtain a JWT, and pass it as `Authorization: Bearer <token>` for caption and manual endpoints.

## Docker
```bash
docker build -t polyglot-captions .
docker run --rm -p 8000:8080 --env-file .env polyglot-captions
```
`docker-compose.yml` is available as well; map port 8000 on the host to 8080 in the container (the uvicorn command inside uses 8080).

## API Cheatsheet
- POST /api/auth/register { username, password }
- POST /api/auth/login -> { access_token, token_type }
- POST /api/captions (multipart: audio file, from_lang, to_lang) -> transcribe + translate + store
- GET /api/captions -> list captions for the authenticated user
- PUT /api/captions/{id} body { "translated_text": "..." }
- DELETE /api/captions/{id}
- POST /api/manual/translate { text, from_lang, to_lang } -> translate without audio
- POST /api/manual/save { transcript, translated_text, from_lang, to_lang }
- GET /api/logs/recent -> last 10 captions (Azure SQL) or stub data
- GET /api/ready -> readiness probe (includes Azure Speech reachability check)
- GET /health -> simple liveness probe

## Telemetry and Metrics
Set `APP_INSIGHTS_KEY` to enable Application Insights logging and tracing. Custom metrics are emitted as log events (`metric_caption_processed`, `metric_processing_time_ms`) and will appear in App Insights when the key is present.

## Testing
Use the in-memory stub DB by exporting `CI=true` (avoids Azure SQL and pyodbc requirements) and then run:
```bash
CI=true pytest
```
`devops/scripts/run_tests.sh` is also available for CI pipelines.
