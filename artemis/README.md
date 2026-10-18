# Artemis Todo REST API

A clean, production-grade REST API for a todo application built with **FastAPI** and **Pydantic** using in-memory storage.

---

## Features

- **In-Memory Storage**: Thread-safe in-memory store (`storage.py`) with zero database dependencies.
- **FastAPI & Pydantic v2**: Strict type safety, input validation, and automatic serialization for all request and response models.
- **Immediate Seed Data**: Pre-seeded on startup with 3 example todos for instant exploration.
- **Interactive Documentation**: Swagger UI docs at `/docs` and ReDoc at `/redoc` working out of the box.
- **Clean REST Semantics**: Canonical HTTP status codes (`200`, `201`, `204`, `404`, `422`).

---

## Quick Start

### 1. Requirements

- Python 3.10+
- FastAPI
- Uvicorn

### 2. Run the Server

Start the development server with live reload:

```bash
uvicorn main:app --reload
```

The API will be available at:
- **Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

---

## Data Model

All todo items adhere to the following schema:

| Field | Type | Description |
|---|---|---|
| `id` | `int` | Unique integer identifier assigned by the server |
| `title` | `str` | Title of the todo (1–120 characters, required) |
| `description` | `str \| null` | Optional detailed notes (max 500 characters) |
| `status` | `"pending" \| "done"` | Current task status, defaults to `"pending"` |
| `created_at` | `datetime` | Creation timestamp set by the server in UTC |

---

## Endpoints & Curl Examples

### 1. Health Check

Checks system operational status and returns the current total count of todos in storage.

- **Method**: `GET`
- **Route**: `/health`
- **Response**: `200 OK`

```bash
curl -X GET http://127.0.0.1:8000/health
```

**Response (`200 OK`)**:
```json
{
  "status": "ok",
  "todos": 3
}
```

---

### 2. Create Todo

Creates a new todo item. `title` is required (1–120 chars); `description` is optional (max 500 chars); `status` defaults to `"pending"` if omitted.

- **Method**: `POST`
- **Route**: `/todos`
- **Response**: `201 Created`

```bash
curl -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Design microservice architecture",
    "description": "Draft service boundaries, contracts, and schema specifications",
    "status": "pending"
  }'
```

**Response (`201 Created`)**:
```json
{
  "id": 4,
  "title": "Design microservice architecture",
  "description": "Draft service boundaries, contracts, and schema specifications",
  "status": "pending",
  "created_at": "2026-10-18T12:00:00.000000Z"
}
```

Minimal request (title only, using defaults):
```bash
curl -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Quick reminder"
  }'
```

---

### 3. List All Todos

Retrieves all todos currently in storage.

- **Method**: `GET`
- **Route**: `/todos`
- **Response**: `200 OK`

```bash
curl -X GET http://127.0.0.1:8000/todos
```

**Response (`200 OK`)**:
```json
[
  {
    "id": 1,
    "title": "Set up project repository",
    "description": "Initialize FastAPI project structure and Pydantic schemas",
    "status": "done",
    "created_at": "2026-10-18T10:00:00.000000Z"
  },
  {
    "id": 2,
    "title": "Implement in-memory CRUD operations",
    "description": "Build thread-safe storage logic and REST endpoints",
    "status": "done",
    "created_at": "2026-10-18T10:30:00.000000Z"
  },
  {
    "id": 3,
    "title": "Verify API endpoints and documentation",
    "description": "Run test suite and document curl examples for all endpoints",
    "status": "pending",
    "created_at": "2026-10-18T11:00:00.000000Z"
  }
]
```

---

### 4. Filter Todos by Status

Filter todos using the optional `status` query parameter (`pending` or `done`).

#### Filter Pending Todos
- **Method**: `GET`
- **Route**: `/todos?status=pending`
- **Response**: `200 OK`

```bash
curl -X GET "http://127.0.0.1:8000/todos?status=pending"
```

**Response (`200 OK`)**:
```json
[
  {
    "id": 3,
    "title": "Verify API endpoints and documentation",
    "description": "Run test suite and document curl examples for all endpoints",
    "status": "pending",
    "created_at": "2026-10-18T11:00:00.000000Z"
  }
]
```

#### Filter Done Todos
- **Method**: `GET`
- **Route**: `/todos?status=done`
- **Response**: `200 OK`

```bash
curl -X GET "http://127.0.0.1:8000/todos?status=done"
```

**Response (`200 OK`)**:
```json
[
  {
    "id": 1,
    "title": "Set up project repository",
    "description": "Initialize FastAPI project structure and Pydantic schemas",
    "status": "done",
    "created_at": "2026-10-18T10:00:00.000000Z"
  },
  {
    "id": 2,
    "title": "Implement in-memory CRUD operations",
    "description": "Build thread-safe storage logic and REST endpoints",
    "status": "done",
    "created_at": "2026-10-18T10:30:00.000000Z"
  }
]
```

---

### 5. Get Todo by ID

Retrieves a single todo item by its integer ID.

- **Method**: `GET`
- **Route**: `/todos/{id}`
- **Response**: `200 OK` or `404 Not Found`

```bash
curl -X GET http://127.0.0.1:8000/todos/1
```

**Response (`200 OK`)**:
```json
{
  "id": 1,
  "title": "Set up project repository",
  "description": "Initialize FastAPI project structure and Pydantic schemas",
  "status": "done",
  "created_at": "2026-10-18T10:00:00.000000Z"
}
```

If the ID does not exist:
```bash
curl -X GET http://127.0.0.1:8000/todos/999
```

**Response (`404 Not Found`)**:
```json
{
  "detail": "todo not found"
}
```

---

### 6. Partially Update Todo (PATCH)

Partially updates fields of an existing todo. Only the fields included in the request body are modified; omitted fields retain their existing values.

- **Method**: `PATCH`
- **Route**: `/todos/{id}`
- **Response**: `200 OK` or `404 Not Found`

#### Example: Marking a todo as done
```bash
curl -X PATCH http://127.0.0.1:8000/todos/3 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "done"
  }'
```

**Response (`200 OK`)**:
```json
{
  "id": 3,
  "title": "Verify API endpoints and documentation",
  "description": "Run test suite and document curl examples for all endpoints",
  "status": "done",
  "created_at": "2026-10-18T11:00:00.000000Z"
}
```

#### Example: Updating title and description
```bash
curl -X PATCH http://127.0.0.1:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Set up project repository and CI",
    "description": "Initialize GitHub repo, add linting workflows and schemas"
  }'
```

If the ID does not exist:
```bash
curl -X PATCH http://127.0.0.1:8000/todos/999 \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

**Response (`404 Not Found`)**:
```json
{
  "detail": "todo not found"
}
```

---

### 7. Delete Todo

Deletes a todo item by its integer ID.

- **Method**: `DELETE`
- **Route**: `/todos/{id}`
- **Response**: `204 No Content` (empty body) or `404 Not Found`

```bash
curl -i -X DELETE http://127.0.0.1:8000/todos/2
```

**Response Header (`204 No Content`)**:
```http
HTTP/1.1 204 No Content
```

*(Body is empty)*

If the ID does not exist:
```bash
curl -X DELETE http://127.0.0.1:8000/todos/999
```

**Response (`404 Not Found`)**:
```json
{
  "detail": "todo not found"
}
```

---

## Validation & Error Handling

- **Invalid Request Bodies (`422 Unprocessable Entity`)**:
  FastAPI's default validation returns detailed error objects when required fields are missing or constraint checks fail (e.g., empty title, title > 120 characters, description > 500 characters, or status other than `"pending"` / `"done"`).

  ```bash
  curl -X POST http://127.0.0.1:8000/todos \
    -H "Content-Type: application/json" \
    -d '{"title": "", "status": "in_progress"}'
  ```

  **Response (`422 Unprocessable Entity`)**:
  ```json
  {
    "detail": [
      {
        "type": "string_too_short",
        "loc": ["body", "title"],
        "msg": "String should have at least 1 character",
        "input": "",
        "ctx": {"min_length": 1}
      },
      {
        "type": "enum",
        "loc": ["body", "status"],
        "msg": "Input should be 'pending' or 'done'",
        "input": "in_progress",
        "ctx": {"expected": "'pending' or 'done'"}
      }
    ]
  }
  ```

- **Unknown ID (`404 Not Found`)**:
  Accessing, updating, or deleting a non-existent todo ID returns:
  ```json
  {
    "detail": "todo not found"
  }
  ```

- **Unknown Route (`404 Not Found`)**:
  Accessing unregistered endpoints returns FastAPI's default:
  ```json
  {
    "detail": "Not Found"
  }
  ```

---

## Deliverables & Project Structure

- `main.py`: FastAPI application, route handlers, error responses, and OpenAPI metadata.
- `models.py`: Pydantic schemas for request payloads, responses, enums, and validation constraints.
- `storage.py`: Thread-safe in-memory store implementing all CRUD operations and initial seeding.
- `README.md`: API reference, setup guide, and copy-pasteable curl examples for every endpoint.
- `test_api.py`: Automated pytest test suite verifying all routes, edge cases, and validation rules.
