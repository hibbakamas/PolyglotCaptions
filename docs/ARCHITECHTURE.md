FakeTR – System Architecture Document
1. Overview

FakeTR is a simplified speech-to-text and translation web application designed for educational purposes. The architecture emphasizes modularity, clean layering, and readiness for Azure-based enhancements in later sprints.

The system is composed of a FastAPI backend and a browser-based frontend that communicate over JSON/REST. Azure connectors are intentionally stubbed in early sprints to allow fast development and later integration.

2. High-Level Architecture

FakeTR follows a three-layer structure:

a. Presentation Layer (Frontend)

Runs in the browser.
Responsibilities:

User interactions

Capturing input text

Displaying translated text

Basic validation (ensured in Sprint 2)

b. Application Layer (API – FastAPI Backend)

Main orchestration logic.
Responsibilities:

Input validation

Routing requests to the translation service

Formatting responses

Managing errors

c. Service Layer

Encapsulated, testable logic.
Responsibilities:

Translation functionality

Speech functionality (future sprints)

Azure connectors (future sprints)

3. Directory Structure (as of Sprint 2 completion)
FakeTR/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Centralized settings (keys, languages)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── translate_service.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   └── translate_router.py
│   │
│   └── schemas/
│       ├── __init__.py
│       └── translate_schema.py
│
├── frontend/
│   ├── index.html
│   └── script.js
│
├── docs/
│   ├── README.md
│   ├── DOD.md
│   └── ARCHITECTURE.md
│
├── requirements.txt
└── venv/

4. Data Flow
1. User Interaction

User enters text in the frontend and selects a target language.

2. Frontend to Backend (REST)

script.js sends:

POST /api/translate
{
  "text": "...",
  "target_lang": "..."
}

3. Backend Processing

Validates the request schema

Passes the data to translate_service

Uses stubbed translation logic for Sprint 2

Will later call Azure Translator API

4. Backend Response

Returns JSON:

{
  "translated_text": "..."
}

5. Frontend Renders Output

Displays the result dynamically without reload.

5. Configuration (Sprint 2 State)

The backend uses a centralized Settings object to maintain environment-specific values.

Current config includes:

Supported languages

Azure stub placeholders

Future API keys (loaded via environment variables)

All configurations are imported across the system from config.py.