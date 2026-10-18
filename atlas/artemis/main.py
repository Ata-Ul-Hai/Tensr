"""Artemis Todo REST API built with FastAPI and in-memory storage."""

from fastapi import FastAPI, HTTPException, Query, Response, status
from models import (
    ErrorResponse,
    HealthResponse,
    TodoCreate,
    TodoResponse,
    TodoStatus,
    TodoUpdate,
)
from storage import storage

app = FastAPI(
    title="Artemis Todo API",
    description="A clean, robust in-memory REST API for todo task management.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the operational status of the service along with total count of todos.",
    tags=["System"],
)
def get_health() -> HealthResponse:
    """Return system health status and total count of stored todos."""
    return HealthResponse(status="ok", todos=storage.count())


@app.post(
    "/todos",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new todo",
    description="Creates a new todo item with server-assigned ID and UTC timestamp.",
    tags=["Todos"],
)
def create_todo(todo_in: TodoCreate) -> TodoResponse:
    """Create a new todo item."""
    return storage.create(todo_in)


@app.get(
    "/todos",
    response_model=list[TodoResponse],
    summary="List todos",
    description="Retrieves all todos with optional filtering by status ('pending' or 'done').",
    tags=["Todos"],
)
def list_todos(
    status: TodoStatus | None = Query(
        default=None,
        description="Filter todos by status ('pending' or 'done')",
    ),
) -> list[TodoResponse]:
    """List todos, optionally filtered by status."""
    return storage.get_all(status=status)


@app.get(
    "/todos/{id}",
    response_model=TodoResponse,
    summary="Get a todo by ID",
    description="Retrieves a specific todo by its integer identifier.",
    tags=["Todos"],
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Todo not found",
        },
    },
)
def get_todo(id: int) -> TodoResponse:
    """Retrieve a single todo item by ID."""
    todo = storage.get_by_id(id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="todo not found",
        )
    return todo


@app.patch(
    "/todos/{id}",
    response_model=TodoResponse,
    summary="Partially update a todo",
    description="Partially updates an existing todo's title, description, or status.",
    tags=["Todos"],
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Todo not found",
        },
    },
)
def update_todo(id: int, todo_in: TodoUpdate) -> TodoResponse:
    """Partially update fields of an existing todo."""
    updated = storage.update(id, todo_in)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="todo not found",
        )
    return updated


@app.delete(
    "/todos/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a todo",
    description="Deletes a todo item by its integer identifier. Returns 204 with an empty body.",
    tags=["Todos"],
    responses={
        204: {
            "description": "Todo deleted successfully (no content)",
        },
        404: {
            "model": ErrorResponse,
            "description": "Todo not found",
        },
    },
)
def delete_todo(id: int) -> Response:
    """Delete a todo item by ID."""
    deleted = storage.delete(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="todo not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
