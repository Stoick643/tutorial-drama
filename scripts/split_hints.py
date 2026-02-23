"""
One-time script to split 'hint' (which contains the solution) into proper 'hint' + 'solution' fields.
Run from project root: python scripts/split_hints.py
"""
import json
import os

# Map: topic/filename -> (new_hint, solution)
# new_hint = conceptual nudge, solution = the actual answer
HINT_SPLITS = {
    # --- Redis ---
    "redis/00_setup.json": (
        "What single command checks if Redis is alive?",
        "PING"
    ),
    "redis/01_strings.json": (
        "You need two commands: one to store and one to retrieve. Think SET and GET.",
        "SET greeting \"Hello, World!\"\nGET greeting"
    ),
    "redis/02_lists.json": (
        "Think about which command adds items to the left side of a list.",
        "LPUSH clues \"fingerprint\" \"weapon\" \"motive\"\nLRANGE clues 0 -1"
    ),
    "redis/03_sets.json": (
        "Sets store unique members. Which command adds to a set?",
        "SADD suspects \"Alice\" \"Bob\" \"Charlie\"\nSMEMBERS suspects"
    ),
    "redis/04_hashes.json": (
        "Hashes are like objects with fields. Think about HSET for setting fields.",
        "HSET suspect:1 name \"Alice\" age 30 status \"wanted\"\nHGETALL suspect:1"
    ),
    # --- SQL ---
    "sql/00_setup.json": (
        "Start with SELECT and think about which table holds employee data.",
        "SELECT * FROM employees;"
    ),
    "sql/01_select_basics.json": (
        "You only need specific columns, not all of them.",
        "SELECT name, department FROM employees;"
    ),
    "sql/02_where.json": (
        "Add a condition after WHERE to filter rows by department.",
        "SELECT * FROM employees WHERE department = 'Engineering';"
    ),
    "sql/03_aggregates.json": (
        "GROUP BY groups rows, and aggregate functions like COUNT or AVG summarize them.",
        "SELECT department, COUNT(*) FROM employees GROUP BY department;"
    ),
    "sql/04_joins.json": (
        "JOIN connects two tables on a shared column. Think about which column links them.",
        "SELECT employees.name, departments.name FROM employees JOIN departments ON employees.department_id = departments.id;"
    ),
    "sql/05_advanced.json": (
        "Subqueries go inside parentheses and run first. Use them in WHERE clauses.",
        "SELECT name FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);"
    ),
    # --- Git ---
    "git/00_setup.json": (
        "Which command shows the current state of your repository?",
        "git status"
    ),
    "git/01_staging.json": (
        "First create the file, then use git add to stage it.",
        "touch clue.txt && git add clue.txt"
    ),
    "git/02_commits.json": (
        "Stage your changes first, then commit with a descriptive message.",
        "git add . && git commit -m \"Add initial files\""
    ),
    "git/03_branches.json": (
        "Create a branch with git branch, then switch to it with git checkout (or combine both).",
        "git checkout -b investigation"
    ),
    # --- Docker ---
    "docker/00_containers.json": (
        "Think about which docker command shows you running containers.",
        "docker ps"
    ),
    "docker/01_running.json": (
        "The run command starts a container. Add flags for background mode.",
        "docker run -d nginx"
    ),
    "docker/02_dockerfile.json": (
        "A Dockerfile starts with FROM (base image) and uses COPY to add files.",
        "FROM openjdk:17\nCOPY app.jar /app/\nWORKDIR /app\nCMD [\"java\", \"-jar\", \"app.jar\"]"
    ),
    "docker/03_building.json": (
        "Build turns a Dockerfile into an image. Don't forget the tag and the build context.",
        "docker build -t myapp:latest ."
    ),
    "docker/04_volumes_ports.json": (
        "The -p flag maps ports: your_port:container_port. The -d flag runs in background.",
        "docker run -d -p 8080:80 nginx"
    ),
    "docker/05_compose.json": (
        "Compose files use YAML. Define services, their images, and how they connect.",
        "version: '3'\nservices:\n  web:\n    image: nginx\n    ports:\n      - \"8080:80\"\n  db:\n    image: postgres\n    environment:\n      POSTGRES_PASSWORD: secret"
    ),
    # --- LLM ---
    "llm/00_first_conversation.json": (
        "Just type any question — this is a live connection to a real AI model.",
        None  # Chat mode, no solution needed
    ),
    "llm/01_tokenization.json": (
        "Type a sentence and see how the tokenizer breaks it into pieces. Longer words get split more.",
        None  # Chat mode
    ),
    "llm/02_embeddings.json": (
        "Try pairs of sentences — similar meanings should have high cosine similarity scores.",
        None  # Chat mode
    ),
    "llm/03_anatomy.json": (
        "Think about the layers a prompt passes through: tokenization, embedding, attention, output.",
        None  # Chat mode
    ),
    "llm/04_api_layer.json": (
        "Look at the curl example — you need the right endpoint, headers, and JSON body structure.",
        None  # Chat mode
    ),
    "llm/05_enhanced_prompts.json": (
        "RAG combines retrieval (finding relevant docs) with generation (LLM answering based on them).",
        None  # Chat mode
    ),
    # --- Bash ---
    "bash/00_navigation.json": (
        "Which command creates a new directory?",
        "mkdir camp"
    ),
    "bash/01_files.json": (
        "You need to write text into a file (not just create an empty one), then duplicate it.",
        "echo \"SOS\" > signal.txt && cp signal.txt backup.txt"
    ),
    "bash/02_searching.json": (
        "grep searches inside files. Add a flag to ignore uppercase vs lowercase.",
        "grep -i \"ERROR\" server.log"
    ),
    "bash/03_pipes.json": (
        "Chain four commands: read the file, sort it, remove duplicates, count what's left.",
        "cat access.log | sort | uniq | wc -l"
    ),
    "bash/04_xargs.json": (
        "find locates files, but can't delete them alone. xargs bridges the gap.",
        "find . -name \"*.tmp\" | xargs rm"
    ),
    "bash/05_text_processing.json": (
        "awk splits lines into columns. $1 is the first column (IP address).",
        "awk '{print $1}' access.log | sort | uniq -c"
    ),
    "bash/06_toolbelt.json": (
        "There's no wrong answer! Think about what you do most in your daily work.",
        None  # Chat mode
    ),
    "bash/07_scripting.json": (
        "Start with #!/bin/bash, then use mkdir, cd into it, create files with touch and echo, list with ls.",
        "#!/bin/bash\nmkdir mysite\ncd mysite\ntouch index.html style.css\necho \"<h1>Hello World</h1>\" > index.html\nls\necho \"Done!\""
    ),
}

def update_lessons():
    updated = 0
    for key, (new_hint, solution) in HINT_SPLITS.items():
        path = f"tutorials/{key}"
        if not os.path.exists(path):
            print(f"  SKIP {key} — file not found")
            continue

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        challenge = data.get("challenge", {})
        challenge["hint"] = new_hint
        if solution is not None:
            challenge["solution"] = solution

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

        updated += 1
        print(f"  OK {key}")

    print(f"\nUpdated {updated} lessons")

if __name__ == "__main__":
    update_lessons()
