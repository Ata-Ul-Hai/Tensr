"""In-memory storage and CRUD operations for the Artemis Todo API."""

from datetime import datetime, timezone
import threading
from models import TodoCreate, TodoResponse, TodoStatus, TodoUpdate


class TodoStorage:
    """Thread-safe in-memory storage manager for todo items."""

    def __init__(self, seed: bool = True) -> None:
        self._lock = threading.RLock()
        self._todos: dict[int, TodoResponse] = {}
        self._next_id: int = 1
        if seed:
            self.seed()

    def seed(self) -> None:
        """Seed the storage with 3 initial example todos."""
        with self._lock:
            self._todos.clear()
            self._next_id = 1
            initial_items = [
                {
                    "title": "Set up project repository",
                    "description": "Initialize FastAPI project structure and Pydantic schemas",
                    "status": TodoStatus.DONE,
                },
                {
                    "title": "Implement in-memory CRUD operations",
                    "description": "Build thread-safe storage logic and REST endpoints",
                    "status": TodoStatus.DONE,
                },
                {
                    "title": "Verify API endpoints and documentation",
                    "description": "Run test suite and document curl examples for all endpoints",
                    "status": TodoStatus.PENDING,
                },
            ]

            for item in initial_items:
                todo_id = self._next_id
                self._next_id += 1
                created_at = datetime.now(timezone.utc)
                self._todos[todo_id] = TodoResponse(
                    id=todo_id,
                    title=item["title"],
                    description=item["description"],
                    status=item["status"],
                    created_at=created_at,
                )

    def count(self) -> int:
        """Return the total number of todos stored."""
        with self._lock:
            return len(self._todos)

    def get_all(self, status: TodoStatus | None = None) -> list[TodoResponse]:
        """Return all todos, optionally filtered by status."""
        with self._lock:
            todos = list(self._todos.values())
            if status is not None:
                todos = [todo for todo in todos if todo.status == status]
            return todos

    def get_by_id(self, todo_id: int) -> TodoResponse | None:
        """Retrieve a single todo by its ID, or None if not found."""
        with self._lock:
            return self._todos.get(todo_id)

    def create(self, todo_create: TodoCreate) -> TodoResponse:
        """Create and store a new todo item with server-assigned ID and UTC timestamp."""
        with self._lock:
            todo_id = self._next_id
            self._next_id += 1
            created_at = datetime.now(timezone.utc)
            todo = TodoResponse(
                id=todo_id,
                title=todo_create.title,
                description=todo_create.description,
                status=todo_create.status,
                created_at=created_at,
            )
            self._todos[todo_id] = todo
            return todo

    def update(self, todo_id: int, todo_update: TodoUpdate) -> TodoResponse | None:
        """Partially update an existing todo by ID.

        Only fields explicitly provided in the update payload will be modified.
        Returns the updated todo, or None if the ID does not exist.
        """
        with self._lock:
            existing = self._todos.get(todo_id)
            if existing is None:
                return None

            update_data = todo_update.model_dump(exclude_unset=True)
            updated_todo = existing.model_copy(update=update_data)
            self._todos[todo_id] = updated_todo
            return updated_todo

    def delete(self, todo_id: int) -> bool:
        """Delete a todo by ID. Return True if deleted, False if not found."""
        with self._lock:
            if todo_id in self._todos:
                del self._todos[todo_id]
                return True
            return False

    def clear(self) -> None:
        """Clear all stored todos and reset counter."""
        with self._lock:
            self._todos.clear()
            self._next_id = 1


# Global storage instance
storage = TodoStorage(seed=True)
