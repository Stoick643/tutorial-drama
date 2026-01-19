import pytest
import json
from unittest.mock import patch, Mock, AsyncMock

def test_root_page(app_client):
    """Test the homepage returns HTML with correct title."""
    response = app_client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Tutorial Drama" in response.text
    assert "Narrative Learning Engine" in response.text

def test_tutorial_menu(app_client, mock_lesson_file):
    """Test /tutorial/redis returns lesson list."""
    response = app_client.get("/tutorial/redis")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Redis Basics" in response.text
    assert "The Database Detective" in response.text

def test_tutorial_lesson(app_client, mock_lesson_file):
    """Test individual lesson pages load correctly."""
    response = app_client.get("/tutorial/redis/00_setup")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "The Database Detective" in response.text
    assert "Detective Indecks" in response.text
    assert "PING" in response.text

def test_tutorial_menu_not_found(app_client):
    """Test 404 for non-existent tutorial topics."""
    response = app_client.get("/tutorial/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_tutorial_lesson_not_found(app_client, mock_lesson_file):
    """Test 404 for non-existent lessons."""
    response = app_client.get("/tutorial/redis/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_check_answer_success(app_client, mock_container_manager, mock_lesson_file):
    """Test successful grading with correct feedback."""
    response = app_client.post("/api/check-answer", json={
        "command": "PING",
        "topic": "redis",
        "lesson": "00_setup"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["output"] == "PONG"
    assert data["is_correct"] is True
    assert data["feedback_message"] == "Correct!"

@pytest.mark.asyncio
async def test_check_answer_validation_error(app_client):
    """Test 422 error when missing required fields."""
    response = app_client.post("/api/check-answer", json={
        "command": "PING",
        # Missing topic and lesson fields
    })

    assert response.status_code == 422
    assert "Field required" in str(response.json())

@pytest.mark.asyncio
async def test_check_answer_lesson_not_found(app_client):
    """Test error when lesson file doesn't exist."""
    response = app_client.post("/api/check-answer", json={
        "command": "PING",
        "topic": "redis",
        "lesson": "nonexistent"
    })

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_check_answer_no_check_logic(app_client, tmp_path):
    """Test error when lesson has no check_logic."""
    # Create lesson without check_logic
    tutorials_dir = tmp_path / "tutorials" / "redis"
    tutorials_dir.mkdir(parents=True)

    lesson_data = {
        "tutorial": "Redis Basics",
        "challenge": {
            "task": "Test task"
            # No check_logic field
        }
    }

    lesson_file = tutorials_dir / "no_logic.json"
    with open(lesson_file, "w") as f:
        json.dump(lesson_data, f)

    with patch('main.base_dir', tmp_path):
        response = app_client.post("/api/check-answer", json={
            "command": "PING",
            "topic": "redis",
            "lesson": "no_logic"
        })

        assert response.status_code == 500
        assert "check_logic" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_unsupported_topic(app_client, mock_lesson_file):
    """Test error when topic is not supported by container manager."""
    with patch('main.container_manager') as mock_manager:
        mock_manager.execute_code_in_container = AsyncMock(
            side_effect=KeyError("No container pool for language: redis")
        )

        response = app_client.post("/api/check-answer", json={
            "command": "PING",
            "topic": "redis",
            "lesson": "00_setup"
        })

        assert response.status_code == 400
        assert "unsupported topic" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_container_execution_error(app_client, mock_lesson_file):
    """Test graceful handling when container execution fails."""
    with patch('main.container_manager') as mock_manager:
        mock_manager.execute_code_in_container = AsyncMock(
            side_effect=Exception("Container execution failed")
        )

        response = app_client.post("/api/check-answer", json={
            "command": "PING",
            "topic": "redis",
            "lesson": "00_setup"
        })

        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()
