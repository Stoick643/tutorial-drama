# Tutorial Drama — Narrative Learning Engine

## What Is This?
A web-based interactive learning platform that teaches technical subjects through story-driven tutorials. Instead of dry documentation, learners experience technical concepts through narrative dialogues — Detective Noir, Sci-Fi, Fairy Tales, Romance, and more.

**Vision:** Make learning code feel like playing a game or reading a story.

## Architecture

### Technology Stack
- **Backend:** Python + FastAPI
- **Frontend:** Jinja2 templates + Vanilla JavaScript + CSS
- **Content:** JSON files (version-controlled, "content-as-code")
- **Grading:** Docker containers for sandboxed code execution
- **Deployment:** fly.io (planned) — two services: tutorial app + grader service

### How It Works
1. **Tutorial Content** — stored as JSON files in `tutorials/{topic}/{lesson}.json`
2. **Multiple Styles** — each lesson has multiple narrative styles in its `styles` array
3. **User Interaction** — learner reads dialogue, sees code examples, attempts challenges
4. **Code Execution** — user command sent to `/api/check-answer`
5. **Grading** — Docker container executes code in sandbox, validates result
6. **Instant Feedback** — returns output, correctness, and feedback message

### Grading System
The grader uses Docker to create isolated execution environments per topic:

| Topic | Docker Image | What Runs |
|-------|-------------|-----------|
| Redis | `grader-image-redis` | Real redis-cli |
| SQL | `grader-image-sql` | Real SQLite3 with pre-loaded database |
| Git | `grader-image-git` | Real git in initialized repo |
| Docker | `grader-image-docker` | Mock docker CLI + Dockerfile/Compose validators |
| LLM | `grader-image-llm` | Real tokenizer + API calls to Moonshot (planned) |

Container pooling: pre-warms `POOL_SIZE` containers per topic at startup, round-robin assignment.

### Deployment Topology (Planned)
Two services on fly.io, triggered from this monorepo via GitHub:
- **Tutorial app** — lightweight container: FastAPI + UI + content (~$3-5/mo)
- **Grader service** — Fly Machine (microVM) with Docker daemon (~$15-30/mo)

For local development, both run as one app (grader embedded in `docker_manager.py`).
See `plan-phase-3.md` for the original merge/split rationale.

## File Structure

```
tutorial-drama/
├── app/
│   ├── main.py              # FastAPI routes and application logic
│   ├── docker_manager.py    # Docker container management and grading
│   └── grader_schemas.py    # Pydantic models for grading API
├── static/
│   ├── styles.css           # Dark-themed styling
│   ├── interactive.js       # Interactive console + answer checking
│   └── progress.js          # Progress tracking (localStorage)
├── templates/
│   ├── index.html           # Homepage with topic cards
│   ├── tutorial_menu.html   # Topic lesson selector
│   └── tutorial_template.html  # Lesson viewer (style-agnostic)
├── tutorials/               # Content-as-code (JSON)
│   ├── redis/               # 5 lessons (00-04)
│   ├── sql/                 # 6 lessons (00-05)
│   ├── git/                 # 4 lessons (00-03)
│   └── docker/              # 6 lessons (00-05)
├── docker/                  # Grader Docker images
│   ├── redis/Dockerfile
│   ├── sql/Dockerfile + company.db
│   ├── git/Dockerfile
│   └── docker/Dockerfile + mock CLI + validators
├── docs/                    # Detailed curriculum designs
│   ├── docker-curriculum.md
│   └── llm-curriculum.md
├── tests/
│   ├── test_api.py
│   └── test_lesson_loading.py
├── Roadmap.md               # Project status and plans
├── plan-phase-3.md          # Historical: grader merge rationale
├── requirements.txt
└── README.md
```

## Lesson JSON Format

Each lesson file contains:
- **tutorial** — Tutorial name (e.g., "Redis Basics")
- **module/scene** — Lesson numbering
- **technical_concept** — Plain explanation of what's being taught
- **code_example** — Example code (`language` + `code`)
- **challenge** — Interactive task for the learner
  - **task** — What the user needs to do
  - **hint** — Optional hint
  - **multiline** — If true, shows textarea instead of single-line input
  - **check_logic** — Validation rules for grader
    - **setup_commands** — Optional commands to run before user code
    - **validation_command** — Command to verify correctness
    - **expected_result** — Expected output (`type` + `value`)
- **styles** — Array of narrative presentations
  - **name** — Style identifier (detective_noir, sci_fi, fairy_tale, flirting)
  - **title** — Lesson title in this style
  - **dialogue** — Array of `{character, line}` objects

### Validation Types
- `exact_match` — validation_command output must equal expected value
- `user_output_exact_match` — user's output must equal expected value exactly
- `user_output_contains` — user's output must contain expected substring
- `user_output_contains_all` — user's output must contain all expected strings

## Development Workflow

### Running Locally
```bash
# Ensure Docker Desktop is running
python app/main.py
# Visit http://127.0.0.1:8000
```
On startup, the app warms container pools (POOL_SIZE × number of topics).

### Environment Variables
- `DEV_MODE` — disables template caching, adds no-cache headers
- `LLM_API_KEY` — Moonshot API key for LLM tutorials (planned)

### Testing
```bash
pytest -v
```

### Adding a New Topic
1. Create `tutorials/{topic}/` with lesson JSON files
2. Create `docker/{topic}/Dockerfile` for the grader image
3. Build: `docker build -t grader-image-{topic} docker/{topic}/`
4. Add `"{topic}": "grader-image-{topic}"` to `GRADER_IMAGES` in `docker_manager.py`
5. Add `_build_command`, `return_container` cases for the new topic
6. Add card to `templates/index.html`
7. No route changes needed — `/tutorial/{topic}/{lesson}` works automatically

### Adding a New Narrative Style
1. Add new style object to lesson's `styles` array
2. Keep same technical content, change only: name, title, dialogue
3. Style selection via URL: `?style=fairy_tale`

## Design Principles
- **Decoupled** — content (JSON), presentation (HTML/CSS), logic (Python) are separate
- **Topic-Agnostic Routes** — `/tutorial/{topic}/{lesson}` works for any topic
- **Multi-Style** — same technical content, different narrative experiences
- **Scalable Content** — add topics by creating JSON files, no code changes
- **Pedagogically Sound** — concrete before abstract, scaffolded progression, immediate feedback
