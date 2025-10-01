import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import httpx
import sys
import os

# Add the app directory to the path so we can import main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app, base_dir

@pytest.fixture
def app_client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_grader_service():
    """Mock httpx calls to grader service."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.json.return_value = {
            "output": "PONG",
            "is_correct": True,
            "feedback_message": "Excellent work, detective! You've cracked the case."
        }
        mock_response.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        yield mock_client

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