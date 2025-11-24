# PolyglotCaptions – System Architecture Document (Sprint 4)

## 1. Overview

PolyglotCaptions is a multi-language speech-to-text and translation web application. The architecture emphasizes modularity, testability, and readiness for Azure cloud integration.

The system uses a FastAPI backend and a browser-based frontend communicating over JSON/REST. Azure Speech and Azure Translator are now fully integrated, with fallbacks to stubs for testing and error handling. Monitoring and logging via Azure App Insights are also implemented.

## 2. High-Level Architecture

PolyglotCaptions follows a three-layer structure:

### a. Presentation Layer (Frontend)
- Runs in the browser.
- Responsibilities:
  - User interactions
  - Capturing audio input
  - Displaying transcribed and translated text
  - Basic input validation

### b. Application Layer (API – FastAPI Backend)
- Orchestration and routing logic.
- Responsibilities:
  - Validate requests
  - Route audio to STT (Azure Speech or fallback stub)
  - Route text to translation service (Azure Translator or fallback stub)
  - Format JSON responses
  - Log usage and errors to Azure SQL and App Insights

### c. Service Layer
- Encapsulated, testable logic.
- Responsibilities:
  - Speech-to-text processing (Azure Speech + stub fallback)
  - Translation functionality (Azure Translator + stub fallback)
  - Database logging
  - Azure connectors
  - Monitoring and telemetry integration

## 3. Directory Structure (Sprint 4 State)
PolyglotCaptions/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point with App Insights logging
│   ├── config.py               # Centralized settings (Azure keys, feature flags)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── db.py
│   │   ├── stt_azure.py
│   │   ├── stt_stub.py
│   │   ├── translator_azure.py
│   │   └── translator_stub.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── caption.py          # Caption endpoint with improved error handling
│   │   └── health.py
│   │
│   └── tests/
│       ├── test_caption.py
│       ├── test_health.py
│       └── test_transcribe.py
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── devops/
│   ├── azure-pipelines.yml
│   ├── kql/
│   │   ├── errors.kql
│   │   └── latency_by_pair.kql
│   └── scripts/
│       ├── smoke.sh
│       └── run_tests.sh
│
├── docs/
│   ├── README.md
│   ├── DOD.md
│   └── ARCHITECTURE.md
│
├── requirements.txt
└── .env.example