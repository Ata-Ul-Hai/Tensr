"""Automated test suite for Artemis Todo API."""

from fastapi.testclient import TestClient
from main import app
from storage import storage

client = TestClient(app)


def setup_function():
    """Reset storage to seed state before each test."""
    storage.seed()


def test_seed_data_on_startup():
    res = client.get("/todos")
    assert res.status_code == 200
    todos = res.json()
    assert len(todos) == 3
    assert todos[0]["id"] == 1
    assert todos[1]["id"] == 2
    assert todos[2]["id"] == 3


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["todos"] == 3


def test_create_todo_minimal():
    payload = {"title": "Ship Mission 002"}
    res = client.post("/todos", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["id"] == 4
    assert data["title"] == "Ship Mission 002"
    assert data["description"] is None
    assert data["status"] == "pending"
    assert "created_at" in data

    # Check health reflects new count
    health = client.get("/health").json()
    assert health["todos"] == 4


def test_create_todo_full():
    payload = {
        "title": "Full Todo Item",
        "description": "Comprehensive description for testing",
        "status": "done",
    }
    res = client.post("/todos", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["status"] == "done"


def test_create_todo_validation_errors():
    # Missing required title
    res = client.post("/todos", json={})
    assert res.status_code == 422

    # Empty title (min_length=1)
    res = client.post("/todos", json={"title": ""})
    assert res.status_code == 422

    # Title exceeds 120 characters
    res = client.post("/todos", json={"title": "x" * 121})
    assert res.status_code == 422

    # Description exceeds 500 characters
    res = client.post("/todos", json={"title": "Valid title", "description": "d" * 501})
    assert res.status_code == 422

    # Invalid status
    res = client.post("/todos", json={"title": "Valid title", "status": "in_progress"})
    assert res.status_code == 422


def test_list_todos_filter_status():
    # Filter pending
    res_pending = client.get("/todos?status=pending")
    assert res_pending.status_code == 200
    pending_items = res_pending.json()
    assert len(pending_items) == 1
    assert all(item["status"] == "pending" for item in pending_items)

    # Filter done
    res_done = client.get("/todos?status=done")
    assert res_done.status_code == 200
    done_items = res_done.json()
    assert len(done_items) == 2
    assert all(item["status"] == "done" for item in done_items)

    # Invalid filter returns 422
    res_invalid = client.get("/todos?status=invalid")
    assert res_invalid.status_code == 422


def test_get_todo_by_id():
    res = client.get("/todos/1")
    assert res.status_code == 200
    assert res.json()["id"] == 1

    # Not found
    res_404 = client.get("/todos/9999")
    assert res_404.status_code == 404
    assert res_404.json() == {"detail": "todo not found"}


def test_patch_todo():
    # Update title only
    res = client.patch("/todos/1", json={"title": "Updated Title"})
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "done"  # preserved

    # Update status only
    res = client.patch("/todos/1", json={"status": "pending"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "pending"
    assert data["title"] == "Updated Title"  # preserved

    # Nullify description
    res = client.patch("/todos/1", json={"description": None})
    assert res.status_code == 200
    data = res.json()
    assert data["description"] is None

    # Update on unknown id
    res_404 = client.patch("/todos/9999", json={"title": "Unknown"})
    assert res_404.status_code == 404
    assert res_404.json() == {"detail": "todo not found"}

    # Validation errors on patch
    res_422_empty_title = client.patch("/todos/1", json={"title": ""})
    assert res_422_empty_title.status_code == 422

    res_422_bad_status = client.patch("/todos/1", json={"status": "cancelled"})
    assert res_422_bad_status.status_code == 422


def test_delete_todo():
    res = client.delete("/todos/2")
    assert res.status_code == 204
    assert res.content == b""

    # Verify item is gone
    res_get = client.get("/todos/2")
    assert res_get.status_code == 404
    assert res_get.json() == {"detail": "todo not found"}

    # Health count reduced
    res_health = client.get("/health")
    assert res_health.json()["todos"] == 2

    # Deleting already deleted / unknown ID
    res_delete_again = client.delete("/todos/2")
    assert res_delete_again.status_code == 404
    assert res_delete_again.json() == {"detail": "todo not found"}


def test_interactive_docs_available():
    res_docs = client.get("/docs")
    assert res_docs.status_code == 200
    assert "swagger-ui" in res_docs.text.lower() or "swagger" in res_docs.text.lower()

    res_openapi = client.get("/openapi.json")
    assert res_openapi.status_code == 200
    schema = res_openapi.json()
    assert "/todos" in schema["paths"]
    assert "/todos/{id}" in schema["paths"]
    assert "/health" in schema["paths"]


def test_unknown_routes():
    res = client.get("/nonexistent-endpoint")
    assert res.status_code == 404
    assert res.json() == {"detail": "Not Found"}
