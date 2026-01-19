import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock, MagicMock
import sys
import os

# Add the app directory to the path so we can import main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# Mock Docker before importing main to prevent connection errors during testing
mock_docker = MagicMock()
sys.modules['docker'] = mock_docker

from main import app, base_dir
from grader_schemas import GradeResult

@pytest.fixture
def app_client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_container_manager():
    """Mock Docker container manager for testing."""
    with patch('main.container_manager') as mock_manager:
        # Create async mock for execute_code_in_container
        async def mock_execute(language, user_code, check_logic):
            return GradeResult(
                output="PONG",
                is_correct=True,
                feedback_message="Correct!"
            )

        mock_manager.execute_code_in_container = AsyncMock(side_effect=mock_execute)
        yield mock_manager

@pytest.fixture
def sample_lesson_data():
    """Provide test lesson JSON data."""
    return {
        "tutorial": "Redis Basics",
        "module": 1,
        "scene": 0,
        "technical_concept": "Introduction to Redis and setting up your detective toolkit.",
        "code_example": {
            "language": "redis-cli",
            "code": "redis-cli ping\\n# PONG"
        },
        "challenge": {
            "task": "Connect to Redis and verify it's running by sending a PING command.",
            "hint": "Use the PING command to check if Redis is alive.",
            "check_logic": {
                "validation_command": "PING",
                "expected_result": {
                    "type": "exact_match",
                    "value": "PONG"
                }
            }
        },
        "styles": [
            {
                "name": "detective_noir",
                "title": "The Database Detective",
                "dialogue": [
                    {
                        "character": "Detective Indecks",
                        "line": "Another night, another case."
                    }
                ]
            }
        ]
    }

@pytest.fixture
def mock_lesson_file(sample_lesson_data, tmp_path):
    """Create a temporary lesson file for testing."""
    # Create temporary tutorials directory structure
    tutorials_dir = tmp_path / "tutorials" / "redis"
    tutorials_dir.mkdir(parents=True)

    # Write sample lesson file
    lesson_file = tutorials_dir / "00_setup.json"
    with open(lesson_file, "w") as f:
        json.dump(sample_lesson_data, f)

    # Patch the base_dir to use our temporary directory
    with patch('main.base_dir', tmp_path):
        yield tmp_path