# ABOUTME: Tests for bash tutorial lessons — JSON validation, Docker grading, and build_command logic.

import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# Mock Docker before importing
mock_docker = MagicMock()
sys.modules['docker'] = mock_docker

TUTORIALS_DIR = Path(__file__).resolve().parent.parent / "tutorials" / "bash"


# --- JSON Structure Tests ---

class TestBashLessonJSON:
    """Validate all bash lesson JSON files have correct structure."""

    @pytest.fixture
    def all_lessons(self):
        lessons = {}
        for f in sorted(TUTORIALS_DIR.glob("*.json")):
            with open(f, "r", encoding="utf-8") as fh:
                lessons[f.stem] = json.load(fh)
        return lessons

    def test_eight_lessons_exist(self):
        """Verify all 8 bash lessons exist."""
        files = sorted(TUTORIALS_DIR.glob("*.json"))
        assert len(files) == 8
        stems = [f.stem for f in files]
        assert "00_navigation" in stems
        assert "01_files" in stems
        assert "02_searching" in stems
        assert "03_pipes" in stems
        assert "04_xargs" in stems
        assert "05_text_processing" in stems
        assert "06_toolbelt" in stems
        assert "07_scripting" in stems

    def test_all_lessons_have_required_fields(self, all_lessons):
        """Every lesson must have tutorial, module, scene, technical_concept, challenge, styles."""
        for name, data in all_lessons.items():
            assert "tutorial" in data, f"{name} missing 'tutorial'"
            assert "module" in data, f"{name} missing 'module'"
            assert "scene" in data, f"{name} missing 'scene'"
            assert "technical_concept" in data, f"{name} missing 'technical_concept'"
            assert "challenge" in data, f"{name} missing 'challenge'"
            assert "styles" in data, f"{name} missing 'styles'"

    def test_all_lessons_have_two_styles(self, all_lessons):
        """Every lesson must have survival and heist styles."""
        for name, data in all_lessons.items():
            styles = data["styles"]
            assert len(styles) == 2, f"{name} should have 2 styles, has {len(styles)}"
            style_names = {s["name"] for s in styles}
            assert "survival" in style_names, f"{name} missing 'survival' style"
            assert "heist" in style_names, f"{name} missing 'heist' style"

    def test_all_styles_have_dialogue(self, all_lessons):
        """Every style must have a title and non-empty dialogue."""
        for name, data in all_lessons.items():
            for style in data["styles"]:
                assert "title" in style, f"{name}/{style['name']} missing 'title'"
                assert "dialogue" in style, f"{name}/{style['name']} missing 'dialogue'"
                assert len(style["dialogue"]) > 0, f"{name}/{style['name']} has empty dialogue"
                for entry in style["dialogue"]:
                    assert "character" in entry, f"{name}/{style['name']} dialogue missing 'character'"
                    assert "line" in entry, f"{name}/{style['name']} dialogue missing 'line'"

    def test_all_challenges_have_check_logic(self, all_lessons):
        """Every challenge must have check_logic with expected_result."""
        for name, data in all_lessons.items():
            challenge = data["challenge"]
            assert "task" in challenge, f"{name} challenge missing 'task'"
            assert "check_logic" in challenge, f"{name} challenge missing 'check_logic'"
            check = challenge["check_logic"]
            assert "expected_result" in check, f"{name} check_logic missing 'expected_result'"
            result = check["expected_result"]
            assert "type" in result, f"{name} expected_result missing 'type'"

    def test_graded_lessons_have_hint_and_solution(self, all_lessons):
        """Graded lessons should have both hint and solution."""
        for name, data in all_lessons.items():
            challenge = data["challenge"]
            if challenge.get("mode") == "chat":
                continue
            assert "hint" in challenge, f"{name} missing 'hint'"
            assert "solution" in challenge, f"{name} missing 'solution'"
            assert challenge["hint"] != challenge["solution"], f"{name} hint equals solution"

    def test_lesson_06_is_chat_mode(self, all_lessons):
        """Lesson 06 (toolbelt) should be chat mode."""
        data = all_lessons["06_toolbelt"]
        assert data["challenge"].get("mode") == "chat"

    def test_lesson_07_is_multiline(self, all_lessons):
        """Lesson 07 (scripting) should be multiline."""
        data = all_lessons["07_scripting"]
        assert data["challenge"].get("multiline") is True

    def test_scenes_are_sequential(self, all_lessons):
        """Scenes should be numbered 0-7."""
        scenes = sorted([data["scene"] for data in all_lessons.values()])
        assert scenes == list(range(8))

    def test_all_tutorials_named_bash_basics(self, all_lessons):
        """All lessons should have tutorial name 'Bash Basics'."""
        for name, data in all_lessons.items():
            assert data["tutorial"] == "Bash Basics", f"{name} has wrong tutorial name"

    def test_code_examples_present(self, all_lessons):
        """All lessons should have code_example with language and code."""
        for name, data in all_lessons.items():
            assert "code_example" in data, f"{name} missing 'code_example'"
            assert "language" in data["code_example"], f"{name} code_example missing 'language'"
            assert "code" in data["code_example"], f"{name} code_example missing 'code'"


# --- Docker Manager Tests ---

class TestBashDockerManager:
    """Test bash-specific Docker manager logic."""

    @pytest.fixture
    def manager(self):
        from docker_manager import ContainerManager
        mgr = ContainerManager()
        return mgr

    def test_bash_in_grader_images(self):
        from docker_manager import GRADER_IMAGES
        assert "bash" in GRADER_IMAGES
        assert GRADER_IMAGES["bash"] == "grader-image-bash"

    def test_build_command_single(self, manager):
        """Single-line bash commands should run in /workspace."""
        cmd = manager._build_command("bash", "ls -la")
        assert "/workspace" in cmd
        assert "ls -la" in cmd

    def test_build_command_multiline_script(self, manager):
        """Multi-line scripts should be base64 encoded and run via bash."""
        script = "#!/bin/bash\necho hello\necho world"
        cmd = manager._build_command("bash", script)
        assert "base64" in cmd
        assert "bash" in cmd
        assert "/tmp/user_script.sh" in cmd

    def test_build_command_shebang_detection(self, manager):
        """Scripts starting with #!/bin/bash should be treated as scripts."""
        script = "#!/bin/bash\necho hello"
        cmd = manager._build_command("bash", script)
        assert "user_script.sh" in cmd


# --- Subprocess Manager Tests ---

class TestBashSubprocessManager:
    """Test bash-specific subprocess manager logic."""

    def test_bash_sanitization_allows_basic_commands(self):
        from subprocess_manager import sanitize_input
        safe_commands = [
            "ls -la",
            "mkdir camp",
            "touch file.txt",
            "grep -i ERROR server.log",
            "find . -name '*.tmp'",
            "cat access.log | sort | uniq | wc -l",
            "find . -name '*.tmp' | xargs rm",
            "awk '{print $1}' access.log | sort | uniq -c",
            "echo 'hello' | sed 's/hello/world/'",
        ]
        for cmd in safe_commands:
            is_safe, msg = sanitize_input("bash", cmd)
            assert is_safe, f"Command should be allowed: '{cmd}' — blocked: {msg}"

    def test_bash_sanitization_blocks_dangerous(self):
        from subprocess_manager import sanitize_input
        dangerous = [
            "sudo rm -rf /",
            "eval 'dangerous'",
            "export SECRET=hack",
        ]
        for cmd in dangerous:
            is_safe, _ = sanitize_input("bash", cmd)
            assert not is_safe, f"Command should be blocked: '{cmd}'"

    def test_bash_sanitization_allows_chmod(self):
        """chmod should be allowed in bash lessons."""
        from subprocess_manager import sanitize_input
        is_safe, _ = sanitize_input("bash", "chmod +x script.sh")
        assert is_safe, "chmod should be allowed for bash"

    def test_bash_sanitization_blocks_chmod_for_other_topics(self):
        """chmod should be blocked for non-bash topics."""
        from subprocess_manager import sanitize_input
        is_safe, _ = sanitize_input("redis", "chmod +x script.sh")
        assert not is_safe, "chmod should be blocked for redis"


# --- Integration Tests (require Docker) ---

@pytest.mark.skipif(
    not os.environ.get("TEST_DOCKER"),
    reason="Set TEST_DOCKER=1 to run Docker integration tests"
)
class TestBashDockerIntegration:
    """Integration tests that actually run commands in Docker container."""

    @pytest.fixture
    def container(self):
        # Remove mock to use real docker
        if 'docker' in sys.modules and isinstance(sys.modules['docker'], MagicMock):
            del sys.modules['docker']
        import docker
        client = docker.from_env()
        container = client.containers.run("grader-image-bash", detach=True, tty=True)
        yield container
        container.stop()
        container.remove()

    def _exec(self, container, cmd):
        exit_code, output = container.exec_run(["sh", "-c", f"cd /workspace && {cmd}"])
        return output.decode("utf-8").strip()

    def test_lesson00_mkdir(self, container):
        self._exec(container, "mkdir camp")
        result = self._exec(container, "ls -d camp 2>/dev/null")
        assert result == "camp"

    def test_lesson01_create_and_copy(self, container):
        self._exec(container, 'echo "SOS" > signal.txt && cp signal.txt backup.txt')
        result = self._exec(container, "cat signal.txt && cat backup.txt")
        assert result == "SOS\nSOS"

    def test_lesson02_grep(self, container):
        result = self._exec(container, 'grep -i "ERROR" server.log')
        assert "error" in result.lower()
        assert "connection" in result

    def test_lesson03_pipes(self, container):
        result = self._exec(container, "cat access.log | sort | uniq | wc -l")
        assert "6" in result

    def test_lesson04_xargs(self, container):
        result = self._exec(container, 'find . -name "*.tmp" | xargs rm && find . -name "*.tmp"')
        assert result == ""

    def test_lesson05_awk(self, container):
        result = self._exec(container, "awk '{print $1}' access.log | sort | uniq -c")
        assert "192.168" in result
        assert "10.0" in result

    def test_lesson07_script(self, container):
        script = '#!/bin/bash\nmkdir mysite\ncd mysite\ntouch index.html style.css\necho "<h1>Hello World</h1>" > index.html\nls\necho "Done!"'
        # Save and run script
        import base64
        encoded = base64.b64encode(script.encode()).decode()
        self._exec(container, f"echo '{encoded}' | base64 -d > /tmp/test.sh && bash /tmp/test.sh")
        result = self._exec(container, "cat mysite/index.html")
        assert "<h1>Hello World</h1>" in result

    def test_sample_files_exist(self, container):
        """Verify pre-populated sample files exist."""
        result = self._exec(container, "ls server.log access.log")
        assert "server.log" in result
        assert "access.log" in result

    def test_tmp_files_exist(self, container):
        """Verify .tmp files for xargs lesson exist."""
        result = self._exec(container, "find . -name '*.tmp' | sort")
        assert "junk1.tmp" in result
        assert "junk2.tmp" in result
        assert "junk3.tmp" in result
