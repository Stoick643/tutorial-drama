# ABOUTME: Subprocess-based grader for fly.io deployment (no Docker needed).
# ABOUTME: Runs tools directly (redis-cli, sqlite3, git, etc.) via subprocess.run().
# ABOUTME: Includes input sanitization to prevent command injection and env var leaks.

import base64
import re
import subprocess
import os
import shutil
from pathlib import Path

try:
    from . import grader_schemas as schemas
except ImportError:
    import grader_schemas as schemas

TIMEOUT_SECONDS = 10

# --- Input Sanitization ---

# Shell injection patterns to block in ALL topics
DANGEROUS_PATTERNS = [
    r'\$\(',          # $(command substitution)
    r'`',             # `backtick substitution`
    r'\$\{',          # ${VAR} expansion
    r'\$[A-Z_]',      # $ENV_VAR access
    r'\benv\b',       # env command
    r'\bexport\b',    # export command
    r'\bsource\b',    # source command
    r'\beval\b',      # eval command
    r'\bexec\b',      # exec command
    r'\bcurl\b',      # curl (except LLM topic)
    r'\bwget\b',      # wget
    r'\bnc\b',        # netcat
    r'\brm\s+-rf',    # rm -rf
    r'/etc/',         # filesystem snooping
    r'/proc/',        # proc filesystem
    r'\bsudo\b',      # sudo
    r'\bchmod\b',     # chmod
    r'\bchown\b',     # chown
    r'\bkill\b',      # kill processes
    r'\bps\b\s',      # process listing
    r'\bcat\s+/\b',   # cat /etc/passwd etc.
]

# Allowed Redis commands (case-insensitive)
REDIS_COMMANDS = {
    'PING', 'SET', 'GET', 'DEL', 'EXISTS', 'EXPIRE', 'TTL', 'SETEX',
    'MSET', 'MGET', 'INCR', 'DECR', 'APPEND', 'STRLEN',
    'LPUSH', 'RPUSH', 'LPOP', 'RPOP', 'LRANGE', 'LLEN', 'LINDEX',
    'SADD', 'SREM', 'SMEMBERS', 'SINTER', 'SUNION', 'SDIFF', 'SCARD', 'SISMEMBER',
    'HSET', 'HGET', 'HDEL', 'HGETALL', 'HMSET', 'HMGET', 'HKEYS', 'HVALS', 'HEXISTS',
    'KEYS', 'TYPE', 'FLUSHALL', 'FLUSHDB', 'DBSIZE', 'INFO',
}

# Allowed Git commands
GIT_ALLOWED_PREFIXES = [
    'git ',
    'touch ',
    'echo ',
    'cat ',
    'ls',
]

# SQL: block dangerous statements
SQL_BLOCKED = [
    r'\bDROP\b',
    r'\bDELETE\b',
    r'\bTRUNCATE\b',
    r'\bALTER\b',
    r'\bCREATE\b',
    r'\bINSERT\b',
    r'\bUPDATE\b',
    r'\bATTACH\b',
    r'\bDETACH\b',
    r'\.shell',
    r'\.system',
]


def sanitize_input(language: str, code: str) -> tuple[bool, str]:
    """Validate user input before execution.

    Returns:
        (is_safe, error_message) — if is_safe is False, error_message explains why.
    """
    if not code or not code.strip():
        return False, "Empty command"

    stripped = code.strip()

    # Check dangerous patterns (all topics except specific exceptions)
    # Bash topic allows more commands since it's teaching shell usage
    BASH_ALLOWED_PATTERNS = {
        r'\brm\s+-rf', r'\bchmod\b', r'\bcat\s+/\b',
    }
    for pattern in DANGEROUS_PATTERNS:
        # Allow curl for LLM topic only
        if pattern == r'\bcurl\b' and language == 'llm':
            continue
        # Allow certain patterns for bash topic
        if language == 'bash' and pattern in BASH_ALLOWED_PATTERNS:
            continue
        if re.search(pattern, stripped, re.IGNORECASE):
            return False, "Command not allowed for security reasons."

    # Topic-specific validation
    if language == "redis":
        first_word = stripped.split()[0].upper()
        if first_word not in REDIS_COMMANDS:
            return False, f"Unknown Redis command: {first_word}. Try PING, SET, GET, etc."

    elif language == "sql":
        for pattern in SQL_BLOCKED:
            if re.search(pattern, stripped, re.IGNORECASE):
                return False, "Only SELECT queries are allowed in this tutorial."

    elif language == "git":
        # Allow chained commands with && but validate each part
        parts = [p.strip() for p in stripped.split('&&')]
        for part in parts:
            if not any(part.startswith(prefix) for prefix in GIT_ALLOWED_PREFIXES):
                return False, f"Command not allowed. Use git, touch, echo, cat, or ls."

    elif language == "bash":
        # Allow common bash commands but check dangerous patterns (already checked above)
        # For scripts (multiline), the dangerous patterns check is sufficient
        pass

    # Docker and LLM: content input (Dockerfiles, JSON, text) is always safe
    # since it's saved to a file, not executed as shell commands.
    # Only their CLI commands need checking, which is handled by the
    # execution methods (they only route to specific scripts).

    return True, ""

# Base directory for grader data files
BASE_DIR = Path(__file__).resolve().parent.parent


class SubprocessManager:
    """Executes grading commands via subprocess instead of Docker containers.

    Designed for fly.io deployment where Docker-in-Docker is not available.
    Tools (redis-cli, sqlite3, git, etc.) are installed directly in the image.
    """

    def __init__(self):
        self._redis_process = None
        self._git_repo_dir = "/tmp/grader-git-repo"
        self._sql_db_path = "/tmp/grader-company.db"
        self._sql_db_source = str(BASE_DIR / "docker" / "sql" / "company.db")
        self._tmp_input = "/tmp/grader-user-input"
        self._bash_workspace = "/tmp/grader-bash-workspace"

    async def startup(self):
        """Start background services (e.g., redis-server)."""
        print("Subprocess manager starting up...")

        # Start redis-server in background
        try:
            self._redis_process = subprocess.Popen(
                ["redis-server", "--daemonize", "no", "--loglevel", "warning"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("  Redis server started (PID: {})".format(self._redis_process.pid))
        except FileNotFoundError:
            print("  Warning: redis-server not found. Redis lessons will not work.")

        # Initialize git repo
        self._init_git_repo()

        # Copy SQL database
        self._reset_sql_db()

        # Initialize bash workspace
        self._init_bash_workspace()

        print("Subprocess manager ready.")

    async def shutdown(self):
        """Stop background services."""
        print("Subprocess manager shutting down...")
        if self._redis_process:
            self._redis_process.terminate()
            self._redis_process.wait(timeout=5)
            print("  Redis server stopped.")

    def _init_git_repo(self):
        """Create a fresh git repository for git lessons."""
        if os.path.exists(self._git_repo_dir):
            shutil.rmtree(self._git_repo_dir)
        os.makedirs(self._git_repo_dir)
        self._run_cmd(["git", "init"], cwd=self._git_repo_dir)
        self._run_cmd(["git", "config", "user.email", "test@test.com"], cwd=self._git_repo_dir)
        self._run_cmd(["git", "config", "user.name", "Test"], cwd=self._git_repo_dir)

    def _reset_sql_db(self):
        """Copy fresh database for SQL lessons."""
        if os.path.exists(self._sql_db_source):
            shutil.copy2(self._sql_db_source, self._sql_db_path)
        else:
            print(f"  Warning: SQL database not found at {self._sql_db_source}")

    def _init_bash_workspace(self):
        """Create bash workspace with sample files for lessons."""
        ws = self._bash_workspace
        if os.path.exists(ws):
            shutil.rmtree(ws)
        os.makedirs(os.path.join(ws, "subdir"), exist_ok=True)
        os.makedirs(os.path.join(ws, "logs"), exist_ok=True)

        # server.log for grep lessons (lesson 02)
        with open(os.path.join(ws, "server.log"), "w") as f:
            f.write("2024-01-15 10:23:01 error connection refused from 192.168.1.50\n")
            f.write("2024-01-15 10:23:15 info server started on port 8080\n")
            f.write("2024-01-15 10:24:02 warning disk space low\n")
            f.write("2024-01-15 10:25:33 ERROR timeout waiting for response\n")
            f.write("2024-01-15 10:26:01 info request processed successfully\n")
            f.write("2024-01-15 10:27:45 error connection reset by peer\n")
            f.write("2024-01-15 10:28:00 info health check passed\n")

        # access.log for pipe lessons (lesson 03) - 5 unique lines after sort|uniq
        with open(os.path.join(ws, "access.log"), "w") as f:
            f.write("192.168.1.10 GET /index.html 200\n")
            f.write("10.0.0.5 GET /about.html 200\n")
            f.write("192.168.1.10 GET /index.html 200\n")
            f.write("10.0.0.5 POST /api/data 201\n")
            f.write("192.168.1.20 GET /style.css 200\n")
            f.write("10.0.0.5 GET /about.html 200\n")
            f.write("192.168.1.30 GET /contact.html 404\n")
            f.write("192.168.1.40 GET /login.html 200\n")
            f.write("192.168.1.30 GET /contact.html 404\n")

        # .tmp files for xargs lesson (lesson 04)
        for name in ["junk1.tmp", "junk2.tmp"]:
            Path(os.path.join(ws, name)).touch()
        Path(os.path.join(ws, "subdir", "junk3.tmp")).touch()

    def _reset_bash_workspace(self):
        """Reset bash workspace to original state."""
        self._init_bash_workspace()

    def _run_cmd(self, cmd, cwd=None, input_data=None, timeout=TIMEOUT_SECONDS):
        """Run a command and return (exit_code, output)."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                input=input_data,
                env={**os.environ}
            )
            output = result.stdout.strip()
            if result.returncode != 0 and result.stderr.strip():
                output = output + "\n" + result.stderr.strip() if output else result.stderr.strip()
            return result.returncode, output
        except subprocess.TimeoutExpired:
            return 1, "Error: command timed out"
        except FileNotFoundError as e:
            return 1, f"Error: command not found - {e}"

    def _execute_redis(self, code: str):
        """Execute a redis-cli command."""
        # redis-cli accepts the command as arguments
        args = ["redis-cli"] + code.split()
        return self._run_cmd(args)

    def _execute_sql(self, code: str):
        """Execute SQL via sqlite3."""
        return self._run_cmd(["sqlite3", self._sql_db_path], input_data=code)

    def _execute_git(self, code: str):
        """Execute a git/shell command in the git repo."""
        return self._run_cmd(["sh", "-c", code], cwd=self._git_repo_dir)

    def _execute_docker(self, code: str):
        """Execute docker tutorial commands (mock CLI + validators)."""
        stripped = code.strip()
        scripts_dir = str(BASE_DIR / "docker" / "docker")

        if stripped.startswith("docker"):
            # Mock docker CLI
            mock_script = os.path.join(scripts_dir, "mock_docker.sh")
            return self._run_cmd(["sh", mock_script] + stripped.split()[1:])
        elif stripped.startswith("validate-dockerfile"):
            return self._run_cmd(
                ["python", os.path.join(scripts_dir, "validate_dockerfile.py"), self._tmp_input]
            )
        elif stripped.startswith("validate-compose"):
            return self._run_cmd(
                ["python", os.path.join(scripts_dir, "validate_compose.py"), self._tmp_input]
            )
        else:
            # User content (Dockerfile/Compose) — save to tmp file
            with open(self._tmp_input, "w") as f:
                f.write(code)
            return 0, code

    def _execute_llm(self, code: str):
        """Execute LLM tutorial commands."""
        stripped = code.strip()
        scripts_dir = str(BASE_DIR / "docker" / "llm")

        if stripped.startswith("validate-api-request"):
            return self._run_cmd(
                ["python", os.path.join(scripts_dir, "validate_api_request.py"), self._tmp_input]
            )
        elif stripped.startswith("tokenize-text"):
            return self._run_cmd(
                ["python", os.path.join(scripts_dir, "tokenize_text.py"), self._tmp_input]
            )
        elif stripped.startswith("compute-similarity"):
            return self._run_cmd(
                ["python", os.path.join(scripts_dir, "compute_similarity.py"), self._tmp_input]
            )
        elif stripped.startswith("call-llm"):
            return self._run_cmd(
                ["python", os.path.join(scripts_dir, "call_llm.py"), self._tmp_input],
                timeout=30  # LLM API calls can be slow
            )
        else:
            # User input — save to tmp file, run dispatcher
            with open(self._tmp_input, "w") as f:
                f.write(code)
            return self._run_cmd(
                ["python", os.path.join(scripts_dir, "llm_dispatch.py")],
                timeout=30
            )

    def _execute_bash(self, code: str):
        """Execute bash commands in the bash workspace."""
        stripped = code.strip()
        if stripped.startswith("#!/bin/bash") or '\n' in stripped:
            # Multi-line script — save to file and execute
            script_path = "/tmp/grader-bash-script.sh"
            with open(script_path, "w") as f:
                f.write(code)
            return self._run_cmd(["bash", script_path], cwd=self._bash_workspace)
        else:
            # Single command — execute directly
            return self._run_cmd(["sh", "-c", code], cwd=self._bash_workspace)

    def _execute(self, language: str, code: str):
        """Route execution to the right handler."""
        if language == "redis":
            return self._execute_redis(code)
        elif language == "sql":
            return self._execute_sql(code)
        elif language == "git":
            return self._execute_git(code)
        elif language == "docker":
            return self._execute_docker(code)
        elif language == "llm":
            return self._execute_llm(code)
        elif language == "bash":
            return self._execute_bash(code)
        else:
            return 1, f"Unsupported language: {language}"

    def _reset_state(self, language: str):
        """Reset state after each grading request."""
        if language == "redis":
            self._run_cmd(["redis-cli", "FLUSHALL"])
        elif language == "sql":
            self._reset_sql_db()
        elif language == "git":
            self._run_cmd(["sh", "-c", "git reset --hard && git clean -fd"], cwd=self._git_repo_dir)
        elif language in ("docker", "llm"):
            if os.path.exists(self._tmp_input):
                os.remove(self._tmp_input)
        elif language == "bash":
            self._reset_bash_workspace()

    async def execute_code_in_container(
        self, language: str, user_code: str, check_logic: schemas.CheckLogic
    ) -> schemas.GradeResult:
        """Execute and grade code. Same interface as ContainerManager."""

        # Sanitize user input before execution
        is_safe, error_msg = sanitize_input(language, user_code)
        if not is_safe:
            return schemas.GradeResult(
                output=error_msg,
                is_correct=False,
                feedback_message=error_msg,
            )

        try:
            # 1. Run setup commands (trusted, from lesson JSON — not sanitized)
            if check_logic.setup_commands:
                for cmd in check_logic.setup_commands:
                    self._execute(language, cmd)

            # 2. Run the user's code
            exit_code, output = self._execute(language, user_code)

            # 3. Run validation command (if provided)
            validation_output = ""
            if check_logic.validation_command:
                _, validation_output = self._execute(language, check_logic.validation_command)

            # 4. Grade the result
            is_correct = False
            feedback = "Grading logic not fully implemented."

            if check_logic.expected_result.type == "exact_match":
                if validation_output == str(check_logic.expected_result.value):
                    is_correct = True
                    feedback = "Correct!"
                else:
                    feedback = f"Incorrect. Expected a result of '{check_logic.expected_result.value}' but got '{validation_output}'."

            elif check_logic.expected_result.type == "user_output_exact_match":
                expected = str(check_logic.expected_result.value).strip()
                actual = output.strip()
                if actual == expected:
                    is_correct = True
                    feedback = "Correct!"
                else:
                    feedback = f"Expected output:\n{expected}\n\nYour output:\n{actual}"

            elif check_logic.expected_result.type == "user_output_contains":
                expected_substring = str(check_logic.expected_result.value)
                if expected_substring in output:
                    is_correct = True
                    feedback = "Correct!"
                else:
                    feedback = f"Your output should contain '{expected_substring}'"

            elif check_logic.expected_result.type == "user_output_contains_all":
                expected_values = check_logic.expected_result.value
                if not isinstance(expected_values, list):
                    expected_values = [expected_values]
                missing = [str(val) for val in expected_values if str(val) not in output]
                if not missing:
                    is_correct = True
                    feedback = "Correct!"
                else:
                    feedback = f"Your output is missing: {', '.join(missing)}"

            elif check_logic.expected_result.type == "integer_greater_than":
                try:
                    actual_int = int(validation_output)
                    threshold = int(check_logic.expected_result.value)
                    if actual_int > threshold:
                        is_correct = True
                        feedback = "Correct!"
                    else:
                        feedback = f"Expected value greater than {threshold}, got {actual_int}."
                except ValueError:
                    feedback = f"Expected a number but got '{validation_output}'."

            elif check_logic.expected_result.type == "set_contains":
                expected_member = str(check_logic.expected_result.value)
                if expected_member in validation_output:
                    is_correct = True
                    feedback = "Correct!"
                else:
                    feedback = f"Expected result to contain '{expected_member}'."

            else:
                feedback = f"Unknown validation type: '{check_logic.expected_result.type}'"

            return schemas.GradeResult(
                output=output,
                is_correct=is_correct,
                feedback_message=feedback,
            )
        finally:
            self._reset_state(language)


# Create singleton instance
manager = SubprocessManager()
