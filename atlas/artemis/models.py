"""Pydantic schemas and models for the Artemis Todo API."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class TodoStatus(str, Enum):
    """Permitted statuses for a todo item."""

    PENDING = "pending"
    DONE = "done"


class TodoCreate(BaseModel):
    """Request payload for creating a new todo item."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Title of the todo item (1 to 120 characters)",
        examples=["Complete mission documentation"],
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional detailed description (up to 500 characters)",
        examples=["Provide exhaustive instructions, test suite, and curl commands"],
    )
    status: TodoStatus = Field(
        default=TodoStatus.PENDING,
        description="Current status of the todo item ('pending' or 'done')",
        examples=[TodoStatus.PENDING],
    )


class TodoUpdate(BaseModel):
    """Request payload for partially updating an existing todo item."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        description="Updated title of the todo item (1 to 120 characters)",
        examples=["Complete mission documentation and verification"],
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Updated detailed description (up to 500 characters)",
        examples=["Updated task details with production verification checklist"],
    )
    status: TodoStatus | None = Field(
        default=None,
        description="Updated status of the todo item ('pending' or 'done')",
        examples=[TodoStatus.DONE],
    )


class TodoResponse(BaseModel):
    """Response model representing a todo item."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Server-assigned unique identifier",
        examples=[1],
    )
    title: str = Field(
        ...,
        description="Title of the todo item",
        examples=["Complete mission documentation"],
    )
    description: str | None = Field(
        default=None,
        description="Optional detailed description",
        examples=["Provide exhaustive instructions, test suite, and curl commands"],
    )
    status: TodoStatus = Field(
        ...,
        description="Current status of the todo item",
        examples=[TodoStatus.PENDING],
    )
    created_at: datetime = Field(
        ...,
        description="Server timestamp in UTC when the todo item was created",
        examples=["2026-10-18T12:00:00Z"],
    )


class HealthResponse(BaseModel):
    """Response model for the health check endpoint."""

    status: str = Field(
        default="ok",
        description="Current operational status of the service",
        examples=["ok"],
    )
    todos: int = Field(
        ...,
        description="Total number of todo items currently held in memory",
        examples=[3],
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""

    detail: str = Field(
        ...,
        description="Descriptive explanation of the error",
        examples=["todo not found"],
    )
