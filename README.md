# Tutorial Drama — Narrative Learning Engine

A web-based interactive learning platform that teaches technical subjects through story-driven tutorials. Instead of dry documentation, learners experience technical concepts through narrative dialogues — Detective Noir, Sci-Fi, Fairy Tales, Survival Adventure, and more.

**Live:** [tutorial-drama.fly.dev](https://tutorial-drama.fly.dev)

## Topics

| Topic | Lessons | What You Learn | Styles |
|-------|---------|---------------|--------|
| Redis | 5 | Key-value store: SET, GET, lists, sets, hashes | Noir, Sci-Fi, Shakespearean, Comedy |
| SQL | 6 | Queries: SELECT, WHERE, JOINs, aggregates | Noir, Sci-Fi |
| Git | 5 | Version control: 4 areas, branches, undo, .git internals, CI/CD | Socratic, Zen |
| Docker | 6 | Containers: Dockerfiles, images, volumes, Compose | Fairy Tale, Romance |
| LLM | 6 | AI internals: tokens, embeddings, API calls | Sci-Fi, Office Comedy |
| Bash | 8 | Shell: navigation, files, grep, pipes, xargs, sed/awk, scripting | Survival Adventure, Heist/Spy |

Available in 3 languages: English, Slovenščina, Српски.

## How It Works

1. Pick a topic and narrative style
2. Read the story dialogue — characters teach you the concept
3. Try the interactive challenge in the console
4. Get instant feedback from real code execution

## Quick Start (Local Development)

```bash
# Ensure Docker Desktop is running
python app/main.py
# Visit http://127.0.0.1:8000
```

On startup, the app warms Docker container pools (3 containers × 6 topics = 18 containers).

## Architecture

### Technology Stack
- **Backend:** Python + FastAPI
- **Frontend:** Jinja2 templates + Vanilla JavaScript + CSS
- **Content:** JSON files (version-controlled, "content-as-code")
- **Grading (local):** Docker containers via `docker_manager.py`
- **Grading (fly.io):** Subprocess calls via `subprocess_manager.py`
- **Deployment:** fly.io — single app with all tools installed
- **CI/CD:** GitHub Actions → `fly deploy` on push to master

### Grading System

**Local dev** uses Docker containers per topic:

| Topic | Docker Image | What Runs |
|-------|-------------|-----------|
| Redis | `grader-image-redis` | Real redis-cli |
| SQL | `grader-image-sql` | Real SQLite3 with pre-loaded database |
| Git | `grader-image-git` | Real git in initialized repo |
| Docker | `grader-image-docker` | Mock docker CLI + Dockerfile/Compose validators |
| LLM | `grader-image-llm` | Real tokenizer + API calls to Moonshot |
| Bash | `grader-image-bash` | Real bash + coreutils in Alpine with sample files |

**fly.io** uses subprocess calls — same tools installed directly in the image. Toggle via `GRADER_MODE` env var (`docker` or `subprocess`).

## File Structure

```
tutorial-drama/
├── app/
│   ├── main.py                # FastAPI routes and application logic
│   ├── docker_manager.py      # Docker-based grading (local dev)
│   ├── subprocess_manager.py  # Subprocess-based grading (fly.io)
│   └── grader_schemas.py      # Pydantic models for grading API
├── static/
│   ├── styles.css             # Light theme styling
│   ├── interactive.js         # Interactive console + answer checking
│   └── progress.js            # Progress tracking (localStorage)
├── templates/
│   ├── index.html             # Homepage with topic cards
│   ├── tutorial_menu.html     # Topic lesson selector
│   └── tutorial_template.html # Lesson viewer (style-agnostic)
├── tutorials/                 # Content-as-code (JSON)
│   ├── redis/                 # 5 lessons
│   ├── sql/                   # 6 lessons
│   ├── git/                   # 4 lessons
│   ├── docker/                # 6 lessons
│   ├── llm/                   # 6 lessons
│   └── bash/                  # 8 lessons
├── translations/              # i18n translation files
│   ├── sl/                    # Slovenian (35 lessons)
│   └── sr-cyrl/               # Serbian Cyrillic (35 lessons)
├── docker/                    # Grader Docker images (local dev)
│   ├── redis/Dockerfile
│   ├── sql/Dockerfile + company.db
│   ├── git/Dockerfile
│   ├── docker/Dockerfile + mock CLI + validators
│   ├── llm/Dockerfile + Python scripts
│   └── bash/Dockerfile
├── tests/                     # Pytest test suite
├── docs/                      # Detailed curriculum designs
├── Dockerfile.flyio           # All-in-one image for fly.io
├── fly.toml                   # fly.io configuration
├── Roadmap.md                 # Project status and plans
├── requirements.txt
└── README.md                  # This file
```

## Lesson JSON Format

Each lesson file contains:
- **tutorial** — Tutorial name (e.g., "Redis Basics")
- **module/scene** — Lesson numbering (internal, displayed as "Lesson N of M")
- **technical_concept** — Plain explanation of what's being taught
- **code_example** — Example code (`language` + `code`)
- **challenge** — Interactive task
  - **task** — What the user needs to do
  - **hint** — Conceptual nudge (not the answer)
  - **solution** — Full solution (revealed on request)
  - **multiline** — If true, shows textarea instead of single-line input
  - **mode** — `"chat"` for conversational lessons (no grading)
  - **check_logic** — Validation rules for grader
- **styles** — Array of narrative presentations (name, title, dialogue)

### Validation Types
- `exact_match` — validation_command output must equal expected value
- `user_output_exact_match` — user's output must match exactly
- `user_output_contains` — user's output must contain expected substring
- `user_output_contains_all` — user's output must contain all expected strings

## Environment Variables

| Variable | Local | fly.io | Purpose |
|----------|-------|--------|---------|
| `GRADER_MODE` | (unset = docker) | `subprocess` | Which grading backend |
| `DEV_MODE` | `true` | (unset) | Disables caching |
| `LLM_API_KEY` | in `.env` | `fly secrets set` | Moonshot API key for LLM lessons |

## Adding Content

### New Topic
1. Create `tutorials/{topic}/` with lesson JSON files
2. Create `docker/{topic}/Dockerfile` for the grader image
3. Build: `docker build -t grader-image-{topic} docker/{topic}/`
4. Add to `GRADER_IMAGES` in `docker_manager.py` + handler in `subprocess_manager.py`
5. Add card to `templates/index.html`
6. No route changes needed — `/tutorial/{topic}/{lesson}` works automatically

### New Narrative Style
1. Add new style object to lesson's `styles` array
2. Keep same technical content, change only: name, title, dialogue
3. Style selection via URL: `?style=fairy_tale`

### New Translation
1. Create `translations/{lang}/{topic}/{lesson}.json`
2. Override only translatable strings (tutorial, technical_concept, challenge task/hint, style titles/dialogue)
3. Add language option to selectors in `index.html` and `tutorial_menu.html`

## Docs

- **[Roadmap.md](Roadmap.md)** — project status, deployment details, future plans
- **[docs/](docs/)** — detailed curriculum designs per topic
