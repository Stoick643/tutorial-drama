import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

def test_load_valid_lesson(app_client, sample_lesson_data, tmp_path):
    """Test that valid lesson JSON files are loaded correctly."""
    # Create temporary lesson file
    tutorials_dir = tmp_path / "tutorials" / "redis"
    tutorials_dir.mkdir(parents=True)

    lesson_file = tutorials_dir / "test_lesson.json"
    with open(lesson_file, "w") as f:
        json.dump(sample_lesson_data, f)

    # Patch base_dir and test lesson loading
    with patch('main.base_dir', tmp_path):
        response = app_client.get("/tutorial/redis/test_lesson")
        assert response.status_code == 200

        # Check that lesson data is properly loaded
        assert "Redis Basics" in response.text
        assert "The Database Detective" in response.text
        assert "Detective Indecks" in response.text

def test_lesson_json_structure_validation(app_client, tmp_path):
    """Test that lessons with proper JSON structure are accepted."""
    tutorials_dir = tmp_path / "tutorials" / "redis"
    tutorials_dir.mkdir(parents=True)

    # Create lesson with minimal required structure
    minimal_lesson = {
        "tutorial": "Test Tutorial",
        "module": 1,
        "scene": 1,
        "technical_concept": "Test concept",
        "challenge": {
            "task": "Test task",
            "check_logic": {
                "validation_command": "TEST",
                "expected_result": {
                    "type": "exact_match",
                    "value": "OK"
                }
            }
        },
        "styles": [
            {
                "name": "test_style",
                "title": "Test Title",
                "dialogue": []
            }
        ]
    }

    lesson_file = tutorials_dir / "minimal.json"
    with open(lesson_file, "w") as f:
        json.dump(minimal_lesson, f)

    with patch('main.base_dir', tmp_path):
        response = app_client.get("/tutorial/redis/minimal")
        assert response.status_code == 200
        assert "Test Tutorial" in response.text

def test_missing_lesson_file_404(app_client):
    """Test that non-existent lesson files return 404."""
    response = app_client.get("/tutorial/redis/nonexistent_lesson")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_malformed_json_handling(app_client, tmp_path):
    """Test graceful handling of corrupted JSON files."""
    tutorials_dir = tmp_path / "tutorials" / "redis"
    tutorials_dir.mkdir(parents=True)

    # Create malformed JSON file
    lesson_file = tutorials_dir / "malformed.json"
    with open(lesson_file, "w") as f:
        f.write('{"tutorial": "Test", "invalid": json}')  # Invalid JSON

    with patch('main.base_dir', tmp_path):
        response = app_client.get("/tutorial/redis/malformed")
        assert response.status_code == 500
        assert "json" in response.json()["detail"].lower()

def test_lesson_with_missing_styles(app_client, tmp_path):
    """Test lesson loading when styles array is empty or missing."""
    tutorials_dir = tmp_path / "tutorials" / "redis"
    tutorials_dir.mkdir(parents=True)

    lesson_no_styles = {
        "tutorial": "Test Tutorial",
        "module": 1,
        "scene": 1,
        "technical_concept": "Test concept",
        "challenge": {
            "task": "Test task"
        },
        "styles": []  # Empty styles
    }

    lesson_file = tutorials_dir / "no_styles.json"
    with open(lesson_file, "w") as f:
        json.dump(lesson_no_styles, f)

    with patch('main.base_dir', tmp_path):
        response = app_client.get("/tutorial/redis/no_styles")
        assert response.status_code == 200
        # Should handle empty styles gracefully

def test_lesson_with_missing_challenge(app_client, tmp_path):
    """Test lesson loading when challenge section is missing."""
    tutorials_dir = tmp_path / "tutorials" / "redis"
    tutorials_dir.mkdir(parents=True)

    lesson_no_challenge = {
        "tutorial": "Test Tutorial",
        "module": 1,
        "scene": 1,
        "technical_concept": "Test concept",
        "styles": [
            {
                "name": "test_style",
                "title": "Test Title",
                "dialogue": []
            }
        ]
        # No challenge section
    }

    lesson_file = tutorials_dir / "no_challenge.json"
    with open(lesson_file, "w") as f:
        json.dump(lesson_no_challenge, f)

    with patch('main.base_dir', tmp_path):
        response = app_client.get("/tutorial/redis/no_challenge")
        assert response.status_code == 200
        # Should load lesson even without challenge

def test_lesson_style_selection(app_client, tmp_path):
    """Test that the correct style is selected based on query parameter."""
    tutorials_dir = tmp_path / "tutorials" / "redis"
    tutorials_dir.mkdir(parents=True)

    lesson_multi_styles = {
        "tutorial": "Multi Style Tutorial",
        "module": 1,
        "scene": 1,
        "technical_concept": "Test concept",
        "styles": [
            {
                "name": "detective_noir",
                "title": "Noir Title",
                "dialogue": [{"character": "Detective", "line": "Noir line"}]
            },
            {
                "name": "sci_fi",
                "title": "SciFi Title",
                "dialogue": [{"character": "Robot", "line": "SciFi line"}]
            }
        ]
    }

    lesson_file = tutorials_dir / "multi_style.json"
    with open(lesson_file, "w") as f:
        json.dump(lesson_multi_styles, f)

    with patch('main.base_dir', tmp_path):
        # Test default style (first one)
        response = app_client.get("/tutorial/redis/multi_style")
        assert response.status_code == 200
        assert "Noir Title" in response.text

        # Test specific style selection
        response = app_client.get("/tutorial/redis/multi_style?style=sci_fi")
        assert response.status_code == 200
        assert "SciFi Title" in response.text

def test_lesson_file_encoding(app_client, tmp_path):
    """Test that lessons with special characters are handled correctly."""
    tutorials_dir = tmp_path / "tutorials" / "redis"
    tutorials_dir.mkdir(parents=True)

    lesson_unicode = {
        "tutorial": "Tutorial with émojis 🕵️‍♂️",
        "module": 1,
        "scene": 1,
        "technical_concept": "Concept with special chars: àéîôù",
        "styles": [
            {
                "name": "unicode_test",
                "title": "Title with 中文",
                "dialogue": [
                    {"character": "Character", "line": "Line with emoji 🔍"}
                ]
            }
        ]
    }

    lesson_file = tutorials_dir / "unicode.json"
    with open(lesson_file, "w", encoding="utf-8") as f:
        json.dump(lesson_unicode, f, ensure_ascii=False)

    with patch('main.base_dir', tmp_path):
        response = app_client.get("/tutorial/redis/unicode")
        assert response.status_code == 200
        assert "🕵️‍♂️" in response.text
        assert "中文" in response.text

def test_tutorial_menu_lesson_listing(app_client, tmp_path):
    """Test that tutorial menu correctly lists all available lessons."""
    tutorials_dir = tmp_path / "tutorials" / "redis"
    tutorials_dir.mkdir(parents=True)

    # Create multiple lesson files
    lessons = [
        ("lesson1", "First Lesson"),
        ("lesson2", "Second Lesson"),
        ("lesson3", "Third Lesson")
    ]

    for filename, title in lessons:
        lesson_data = {
            "tutorial": "Redis Basics",
            "module": 1,
            "scene": 1,
            "technical_concept": "Test concept",
            "styles": [
                {
                    "name": "test_style",
                    "title": title,
                    "dialogue": []
                }
            ]
        }

        lesson_file = tutorials_dir / f"{filename}.json"
        with open(lesson_file, "w") as f:
            json.dump(lesson_data, f)

    with patch('main.base_dir', tmp_path):
        response = app_client.get("/tutorial/redis")
        assert response.status_code == 200

        # Check that all lessons are listed
        for _, title in lessons:
            assert title in response.text