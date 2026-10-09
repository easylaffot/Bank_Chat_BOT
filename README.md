# Agentic AI E-Commerce Shopping Assistant

Phase 1 establishes a backend-only Python project skeleton and dependency baseline. It intentionally contains no API endpoints, agent workflows, retrieval logic, database models, or other business logic yet.

## Project Structure

```text
.
├── app/
│   ├── __init__.py
│   ├── agents/
│   │   └── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       └── __init__.py
│   ├── core/
│   │   └── __init__.py
│   ├── db/
│   │   └── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── rag/
│   │   └── __init__.py
│   ├── repositories/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── docs/
│   └── .gitkeep
├── scripts/
│   └── .gitkeep
├── storage/
│   ├── chroma/
│   │   └── .gitkeep
│   └── sqlite/
│       └── .gitkeep
├── tests/
│   ├── integration/
│   │   └── .gitkeep
│   └── unit/
│       └── .gitkeep
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Why These Folders Exist

- `app/`: Application Python package; keeps runtime code separate from project tooling and data.
- `app/api/v1/`: Versioned HTTP routes and request handling, isolated from internal application behavior.
- `app/agents/`: LangGraph agent and workflow definitions when those are introduced.
- `app/core/`: Cross-cutting configuration, logging, and application-wide concerns.
- `app/db/`: Database and vector-store connection setup and lifecycle management.
- `app/models/`: Internal persistence/domain models, distinct from HTTP schemas.
- `app/rag/`: Retrieval, indexing, and embedding components for the product catalog.
- `app/repositories/`: Data-access boundaries for SQLite and ChromaDB.
- `app/schemas/`: Validated API input/output schemas.
- `app/services/`: Application use cases that coordinate the API, agents, and repositories.
- `app/utils/`: Small, reusable helpers that do not belong to a specific feature area.
- `docs/`: Architecture notes and operational documentation.
- `scripts/`: Explicit maintenance and development commands, kept out of application startup.
- `storage/chroma/`: Local persistent ChromaDB files; generated data is ignored by Git.
- `storage/sqlite/`: Local SQLite database files; generated data is ignored by Git.
- `tests/unit/`: Fast tests for individual components.
- `tests/integration/`: Tests that exercise boundaries such as API and storage integration.

SQLite is provided by Python's standard library, so no separate SQLite package is needed. Keeping storage access behind dedicated modules leaves room to change persistence choices as deployment needs evolve.

This is a production-conscious separation of responsibilities, not a deployable service yet. SQLite and local Chroma persistence are convenient starting points; deployments that need concurrent multi-instance writes should move persistence behind appropriately managed services.

## Requirements

- Python 3.11 or newer
- `pip`

## Set Up the `raglearn` Virtual Environment

Run these commands from the project root on Linux or macOS:

```bash
python3 -m venv raglearn
source raglearn/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python -m pip check
```

`.env` is for local configuration and must not be committed. `.env.example` contains non-secret defaults. No model provider or API credentials are selected in this phase.

To leave the environment, run `deactivate`. To use it again, activate it from the project root with `source raglearn/bin/activate`.

## Phase 1 Scope

This phase only establishes folders, dependencies, and configuration documentation. There is no application entry point to run yet; API, agent, RAG, and persistence behavior belongs to later phases.
