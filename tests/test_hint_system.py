# ABOUTME: Tests for progressive hint system and lesson numbering across all topics.

import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

mock_docker = MagicMock()
sys.modules['docker'] = mock_docker

TUTORIALS_DIR = Path(__file__).resolve().parent.parent / "tutorials"
ALL_TOPICS = ["redis", "sql", "git", "docker", "llm", "bash"]


class TestHintSolutionFields:
    """Validate hint/solution fields across all lessons."""

    @pytest.fixture
    def all_lessons(self):
        lessons = {}
        for topic in ALL_TOPICS:
            topic_dir = TUTORIALS_DIR / topic
            for f in sorted(topic_dir.glob("*.json")):
                with open(f, "r", encoding="utf-8") as fh:
                    lessons[f"{topic}/{f.name}"] = json.load(fh)
        return lessons

    def test_all_lessons_have_hint(self, all_lessons):
        """Every lesson must have a hint field."""
        for name, data in all_lessons.items():
            challenge = data.get("challenge", {})
            assert "hint" in challenge, f"{name} missing 'hint'"
            assert len(challenge["hint"]) > 0, f"{name} has empty hint"

    def test_graded_lessons_have_solution(self, all_lessons):
        """Graded lessons (non-chat, non-exploratory) should have a solution."""
        # These topics have fully graded lessons that need solutions
        graded_topics = {"redis", "sql", "git", "docker", "bash"}
        for name, data in all_lessons.items():
            topic = name.split("/")[0]
            if topic not in graded_topics:
                continue
            challenge = data.get("challenge", {})
            mode = challenge.get("mode", "")
            if mode == "chat":
                continue
            assert "solution" in challenge, f"{name} (graded) missing 'solution'"
            assert len(challenge["solution"]) > 0, f"{name} has empty solution"

    def test_chat_lessons_may_have_optional_solution(self, all_lessons):
        """Chat-mode lessons may optionally have an example solution."""
        for name, data in all_lessons.items():
            challenge = data.get("challenge", {})
            if challenge.get("mode") == "chat":
                # Chat lessons don't require solutions, but may have them as examples
                pass  # No assertion needed — both with and without solution are valid

    def test_hint_is_not_the_solution(self, all_lessons):
        """Hint should be different from solution (hint is a nudge, not the answer)."""
        for name, data in all_lessons.items():
            challenge = data.get("challenge", {})
            hint = challenge.get("hint", "")
            solution = challenge.get("solution", "")
            if hint and solution:
                assert hint != solution, f"{name}: hint and solution are identical"

    def test_hint_does_not_contain_full_command(self, all_lessons):
        """Hint should be conceptual, not contain the exact solution command."""
        for name, data in all_lessons.items():
            challenge = data.get("challenge", {})
            hint = challenge.get("hint", "")
            solution = challenge.get("solution", "")
            if solution and len(solution) > 5:
                # Solution shouldn't appear verbatim in the hint
                assert solution not in hint, f"{name}: hint contains the full solution"


class TestLessonNumbering:
    """Test that lesson numbering works correctly."""

    def test_lesson_count_per_topic(self):
        """Verify expected lesson counts."""
        expected = {"redis": 5, "sql": 6, "git": 5, "docker": 6, "llm": 6, "bash": 8}
        for topic, count in expected.items():
            files = list((TUTORIALS_DIR / topic).glob("*.json"))
            assert len(files) == count, f"{topic} has {len(files)} lessons, expected {count}"

    def test_numbering_context_in_main(self):
        """Test that main.py passes lesson_number and total_lessons."""
        from main import app
        from fastapi.testclient import TestClient

        with TestClient(app) as client:
            # Load a real lesson
            response = client.get("/tutorial/bash/00_navigation")
            assert response.status_code == 200
            # Should show "Lesson 1 of 8" not "Module 1 - Scene 0"
            assert "Lesson 1 of 8" in response.text
            assert "Module 1" not in response.text
            assert "Scene 0" not in response.text

    def test_numbering_second_lesson(self):
        """Second lesson should show Lesson 2 of N."""
        from main import app
        from fastapi.testclient import TestClient

        with TestClient(app) as client:
            response = client.get("/tutorial/bash/01_files")
            assert response.status_code == 200
            assert "Lesson 2 of 8" in response.text

    def test_numbering_last_lesson(self):
        """Last bash lesson should show Lesson 8 of 8."""
        from main import app
        from fastapi.testclient import TestClient

        with TestClient(app) as client:
            response = client.get("/tutorial/bash/07_scripting")
            assert response.status_code == 200
            assert "Lesson 8 of 8" in response.text


class TestHintSystemUI:
    """Test that hint system UI renders correctly in lesson pages."""

    def _get_lesson_html(self, path):
        from main import app
        from fastapi.testclient import TestClient
        with TestClient(app) as client:
            return client.get(path)

    def test_hint_button_rendered(self):
        """Graded lessons should have a hint button."""
        response = self._get_lesson_html("/tutorial/bash/00_navigation")
        assert response.status_code == 200
        assert "hint-button" in response.text
        assert "Hint" in response.text

    def test_solution_button_rendered(self):
        """Graded lessons with solution should have solution button (hidden initially)."""
        response = self._get_lesson_html("/tutorial/bash/00_navigation")
        assert "solution-button" in response.text
        assert "Show Solution" in response.text

    def test_surrender_prompt_rendered(self):
        """Surrender prompt should be in the HTML (hidden initially)."""
        response = self._get_lesson_html("/tutorial/bash/00_navigation")
        assert "surrender-prompt" in response.text
        assert "Do you surrender?" in response.text

    def test_chat_lesson_no_solution_button(self):
        """Chat-mode lessons should not have solution button element."""
        response = self._get_lesson_html("/tutorial/bash/06_toolbelt")
        assert 'id="solution-button"' not in response.text
        assert 'id="surrender-prompt"' not in response.text

    def test_old_hint_div_not_rendered(self):
        """Old challenge-hint div should no longer appear."""
        response = self._get_lesson_html("/tutorial/bash/00_navigation")
        assert "challenge-hint" not in response.text

    def test_hint_content_hidden_initially(self):
        """Hint content should be hidden by default (display: none)."""
        response = self._get_lesson_html("/tutorial/bash/00_navigation")
        # The hint-content div should have style="display: none;"
        assert 'id="hint-content"' in response.text
        assert 'style="display: none;"' in response.text


class TestBackwardCompatibility:
    """Test that lessons without solution field still work."""

    def test_llm_lessons_render_with_solution(self):
        """LLM lessons have hint and solution — should render both buttons."""
        from main import app
        from fastapi.testclient import TestClient
        with TestClient(app) as client:
            response = client.get("/tutorial/llm/01_tokenization")
            assert response.status_code == 200
            assert 'id="hint-button"' in response.text
            assert 'id="solution-button"' in response.text
