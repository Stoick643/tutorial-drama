# ABOUTME: Manages Docker containers for code execution in sandboxed environments.
# ABOUTME: Handles container pooling, command building, and delegates grading to shared grader module.

import base64
import docker
import os
try:
    from app import grader_schemas as schemas
    from app.grader import evaluate
except ImportError:
    import grader_schemas as schemas
    from grader import evaluate

# Map language names to the Docker images we will build
GRADER_IMAGES = {
    "redis": "grader-image-redis",
    "sql": "grader-image-sql",
    "git": "grader-image-git",
    "docker": "grader-image-docker",
    "llm": "grader-image-llm",
    "bash": "grader-image-bash"
}
POOL_SIZE = 3 # Number of warm containers to keep per language

class ContainerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.pool = {} # e.g. {"redis": [container1, container2]}
        self.pool_index = {} # Track current index for round-robin: {"redis": 0, "sql": 1}

    async def startup(self):
        """Creates a pool of warm, ready-to-use containers on startup."""
        print("Starting up and warming container pools...")
        for lang, image_name in GRADER_IMAGES.items():
            self.pool[lang] = []
            self.pool_index[lang] = 0  # Initialize round-robin index

            # Pass API keys to containers that need them
            env_vars = {}
            if lang == "llm":
                llm_key = os.environ.get("LLM_API_KEY", "")
                if llm_key:
                    env_vars["LLM_API_KEY"] = llm_key
                else:
                    print(f"  Warning: LLM_API_KEY not set. LLM API lessons will not work.")

            for i in range(POOL_SIZE):
                container = self.client.containers.run(
                    image_name, detach=True, tty=True,
                    environment=env_vars if env_vars else None
                )
                self.pool[lang].append(container)
                print(f"Started container {container.short_id} for {lang}")

    async def shutdown(self):
        """Stops and removes all containers on shutdown."""
        print("Shutting down and cleaning up containers...")
        for lang in self.pool:
            for container in self.pool[lang]:
                print(f"Stopping container {container.short_id}")
                container.stop()
                container.remove()

    def get_container(self, language: str):
        """Get next available container from pool using round-robin.

        Args:
            language: The language pool to get container from (e.g., "redis", "sql")

        Returns:
            A Docker container from the pool

        Raises:
            KeyError: If language is not supported
        """
        if language not in self.pool:
            raise KeyError(f"No container pool for language: {language}")

        # Initialize index if not present (for tests that create pool manually)
        if language not in self.pool_index:
            self.pool_index[language] = 0

        # Get container at current index
        containers = self.pool[language]
        index = self.pool_index[language]
        container = containers[index]

        # Advance to next container (round-robin)
        self.pool_index[language] = (index + 1) % len(containers)

        return container

    def return_container(self, language: str, container):
        """Return container to pool after resetting its state.

        Args:
            language: The language of the container (e.g., "redis", "sql", "git")
            container: The Docker container to return
        """
        # Reset container state based on language
        if language == "redis":
            # Clear all Redis data
            container.exec_run("redis-cli FLUSHALL")
        elif language == "sql":
            # Restore database to original state from backup
            container.exec_run("sh -c \"cp /data/company.db.original /data/company.db\"")
        elif language == "git":
            # Reset git repository to clean state
            container.exec_run("sh -c \"git reset --hard && git clean -fd\"")
        elif language == "docker":
            # Clean up any user input files
            container.exec_run("sh -c \"rm -f /tmp/user_input\"")
        elif language == "llm":
            # Clean up user input and mode files
            container.exec_run("sh -c \"rm -f /tmp/user_input /tmp/llm_mode\"")
        elif language == "bash":
            # Reset workspace to original state
            container.exec_run("sh -c \"cd /workspace && rm -rf camp mysite /workspace/subdir/* && touch /workspace/junk1.tmp /workspace/junk2.tmp /workspace/subdir/junk3.tmp && rm -f signal.txt backup.txt\"")

    def _build_command(self, language: str, code: str) -> str:
        """Build language-specific execution command.

        Args:
            language: The programming language/tool (e.g., "redis", "sql", "git")
            code: The code/command to execute

        Returns:
            A properly formatted shell command for execution

        Raises:
            ValueError: If the language is not supported
        """
        if language == "redis":
            # Redis CLI accepts commands directly as arguments
            return f"redis-cli {code}"
        elif language == "sql":
            # SQLite requires SQL to be piped via stdin
            # Escape single quotes for shell safety: ' becomes '\''
            escaped_code = code.replace("'", "'\\''")
            return f"sh -c \"echo '{escaped_code}' | sqlite3 /data/company.db\""
        elif language == "git":
            # Execute command as-is (allows both git commands and shell commands)
            return code
        elif language == "docker":
            stripped = code.strip()
            if stripped.startswith("docker") or stripped.startswith("validate-"):
                # CLI command or validation command — execute directly
                return code
            else:
                # Content (Dockerfile or compose) — base64 encode to avoid escaping issues
                # Saves to /tmp/user_input for validation commands to read
                encoded = base64.b64encode(code.encode()).decode()
                return f"sh -c \"echo '{encoded}' | base64 -d > /tmp/user_input && cat /tmp/user_input\""
        elif language == "llm":
            stripped = code.strip()
            if stripped.startswith("validate-") or stripped.startswith("call-llm") or stripped.startswith("tokenize-") or stripped.startswith("compute-"):
                # Validation/tool commands — execute directly
                return code
            elif stripped.startswith("curl"):
                # Lesson 04: execute curl command directly
                return code
            else:
                # User input (question, text, JSON) — save to file, run dispatcher
                encoded = base64.b64encode(code.encode()).decode()
                return f"sh -c \"echo '{encoded}' | base64 -d > /tmp/user_input && cd /scripts && python llm_dispatch.py\""
        elif language == "bash":
            stripped = code.strip()
            if stripped.startswith("#!/bin/bash") or '\n' in stripped:
                # Multi-line script — base64 encode, save to file, execute
                encoded = base64.b64encode(code.encode()).decode()
                return f"sh -c \"echo '{encoded}' | base64 -d > /tmp/user_script.sh && chmod +x /tmp/user_script.sh && cd /workspace && bash /tmp/user_script.sh\""
            else:
                # Single command — execute directly in workspace
                return f"sh -c \"cd /workspace && {code}\""
        else:
            raise ValueError(f"Unsupported language: {language}")

    async def execute_code_in_container(
        self, language: str, user_code: str, check_logic: schemas.CheckLogic
    ) -> schemas.GradeResult:

        # Get container from pool
        container = self.get_container(language)

        try:
            # 1. Run setup commands if they exist
            if check_logic.setup_commands:
                for cmd in check_logic.setup_commands:
                    full_cmd = self._build_command(language, cmd)
                    container.exec_run(full_cmd)

            # 2. Run the user's code and capture the output
            full_user_cmd = self._build_command(language, user_code)
            exit_code, output_bytes = container.exec_run(full_user_cmd)
            output = output_bytes.decode("utf-8").strip()

            # 3. Run the validation command (only if provided)
            validation_output = ""
            if check_logic.validation_command:
                full_validation_cmd = self._build_command(language, check_logic.validation_command)
                _, validation_output_bytes = container.exec_run(full_validation_cmd)
                validation_output = validation_output_bytes.decode("utf-8").strip()

            # 4. Grade the result using the shared grading logic
            return evaluate(check_logic, output, validation_output)
        finally:
            # Always return container to pool (even if error occurs)
            self.return_container(language, container)

# Create a single instance of the manager to be used by the app
manager = ContainerManager()
