# ABOUTME: Validates JSON structure of all lesson files across all topics.
# ABOUTME: Ensures required fields, style structure, and check_logic presence.

import json
import os
import glob
import pytest

TUTORIALS_DIR = os.path.join(os.path.dirname(__file__), '..', 'tutorials')

REQUIRED_FIELDS = ['tutorial', 'module', 'scene', 'technical_concept', 'code_example', 'challenge', 'styles']
REQUIRED_CHALLENGE_FIELDS = ['task', 'hint']
REQUIRED_STYLE_FIELDS = ['name', 'title', 'dialogue']


def get_all_lessons():
    """Discover all lesson JSON files across all topics."""
    lessons = []
    for topic_dir in sorted(glob.glob(os.path.join(TUTORIALS_DIR, '*'))):
        if not os.path.isdir(topic_dir):
            continue
        topic = os.path.basename(topic_dir)
        for json_file in sorted(glob.glob(os.path.join(topic_dir, '*.json'))):
            lesson = os.path.basename(json_file)
            lessons.append((topic, lesson, json_file))
    return lessons


ALL_LESSONS = get_all_lessons()


@pytest.mark.parametrize("topic,lesson,path", ALL_LESSONS,
                         ids=[f"{t}/{l}" for t, l, _ in ALL_LESSONS])
class TestLessonStructure:

    def test_valid_json(self, topic, lesson, path):
        """Lesson file must be valid JSON."""
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_required_fields(self, topic, lesson, path):
        """Lesson must have all required top-level fields."""
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        for field in REQUIRED_FIELDS:
            assert field in data, f"Missing field '{field}' in {topic}/{lesson}"

    def test_challenge_has_task_and_hint(self, topic, lesson, path):
        """Challenge must have task and hint."""
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        challenge = data['challenge']
        for field in REQUIRED_CHALLENGE_FIELDS:
            assert field in challenge, f"Missing challenge.{field} in {topic}/{lesson}"

    def test_challenge_has_check_logic(self, topic, lesson, path):
        """Non-chat challenges must have check_logic with expected_result."""
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        challenge = data['challenge']
        if challenge.get('mode') == 'chat':
            pytest.skip("Chat mode lessons don't require check_logic")
        assert 'check_logic' in challenge, f"Missing check_logic in {topic}/{lesson}"
        check = challenge['check_logic']
        assert 'expected_result' in check, f"Missing expected_result in {topic}/{lesson}"
        er = check['expected_result']
        assert 'type' in er, f"Missing expected_result.type in {topic}/{lesson}"
        assert 'value' in er, f"Missing expected_result.value in {topic}/{lesson}"

    def test_styles_not_empty(self, topic, lesson, path):
        """Must have at least one narrative style."""
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        styles = data['styles']
        assert isinstance(styles, list) and len(styles) > 0, f"No styles in {topic}/{lesson}"

    def test_style_structure(self, topic, lesson, path):
        """Each style must have name, title, and dialogue."""
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        for i, style in enumerate(data['styles']):
            for field in REQUIRED_STYLE_FIELDS:
                assert field in style, f"Missing styles[{i}].{field} in {topic}/{lesson}"
            assert isinstance(style['dialogue'], list) and len(style['dialogue']) > 0, \
                f"Empty dialogue in styles[{i}] of {topic}/{lesson}"

    def test_dialogue_has_character_and_line(self, topic, lesson, path):
        """Each dialogue entry must have character and line."""
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        for style in data['styles']:
            for j, entry in enumerate(style['dialogue']):
                assert 'character' in entry, f"Missing character in dialogue[{j}] of {topic}/{lesson}"
                assert 'line' in entry, f"Missing line in dialogue[{j}] of {topic}/{lesson}"

    def test_solution_matches_task(self, topic, lesson, path):
        """Lessons with solutions must have non-empty solutions."""
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        solution = data['challenge'].get('solution')
        if solution is not None:
            assert len(solution.strip()) > 0, f"Empty solution in {topic}/{lesson}"

    def test_code_example_structure(self, topic, lesson, path):
        """Code example must have language and code fields."""
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        code_example = data.get('code_example')
        if code_example:
            assert 'language' in code_example, f"Missing code_example.language in {topic}/{lesson}"
            assert 'code' in code_example, f"Missing code_example.code in {topic}/{lesson}"
