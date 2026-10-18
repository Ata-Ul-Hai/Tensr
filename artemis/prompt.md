# Mission 002 — artemis

REST API for a todo app with in-memory storage — CRUD endpoints, validation, and clean error responses.

## Metadata

| Field | Value |
|-------|-------|
| Codename | `artemis` |
| Mission # | 002 |
| Stack | Python · FastAPI |
| Status | landed |
| Built by | Tensr |
| Date | 2026-10-18 |

## Prompt

The exact prompt given to Tensr for this build:

```text
Build a REST API for a todo application using FastAPI with in-memory storage.
No database; a plain Python structure in memory is fine and data does not need
to survive restarts.

Run it with: uvicorn main:app --reload

Data model (Pydantic):
- id: int, assigned by the server
- title: str, 1-120 characters, required
- description: str, optional, max 500 characters
- status: "pending" or "done", defaults to "pending"
- created_at: datetime, set by the server in UTC

Endpoints:
- POST /todos           -> 201 with the created todo
- GET /todos            -> 200, list all todos; optional query parameter
                           status=pending|done to filter
- GET /todos/{id}       -> 200, or 404 with {"detail": "todo not found"}
- PATCH /todos/{id}     -> 200, partial update of title, description,
                           status
- DELETE /todos/{id}    -> 204, empty body
- GET /health           -> 200, {"status": "ok", "todos": <count>}

Validation and errors:
- Invalid request bodies return FastAPI's default 422 responses.
- Unknown ids return 404; unknown routes stay FastAPI's default.
- status accepts only "pending" or "done", nothing else.

Quality bar:
- Type hints everywhere; Pydantic models for all request and response
  bodies, never raw dicts.
- Seed the store with 3 example todos on startup so the API is explorable
  immediately.
- Interactive docs at /docs must work out of the box.

Deliverables: main.py, models.py (schemas), storage.py (in-memory store
with all CRUD logic), and a README.md listing every endpoint with a curl
example for each.
```
