# Tutorial Drama — Roadmap

## Current State: 5 Topics Live, 1 Planned

### Topics & Styles

| Topic | Lessons | Styles | Status |
|-------|---------|--------|--------|
| Redis | 5 (00-04) | Detective Noir, Sci-Fi, Shakespearean, Office Comedy | ✅ Complete |
| SQL | 6 (00-05) | Detective Noir, Sci-Fi | ✅ Complete |
| Git | 4 (00-03) | Detective Noir, Sci-Fi | ✅ Complete |
| Docker | 6 (00-05) | Fairy Tale, Romance | ✅ Complete |
| LLM | 6 (00-05) | Sci-Fi, Office Comedy | ✅ Complete |
| Bash/Linux | TBD | TBD | ⏳ Planned |

### Platform Features

| Feature | Status |
|---------|--------|
| FastAPI + Jinja2 UI | ✅ |
| Docker-based grading | ✅ |
| Interactive console (single-line + multi-line) | ✅ |
| Chat mode (Send button, no grading) | ✅ |
| Multiple narrative styles per lesson | ✅ |
| Prev/Next lesson navigation | ✅ |
| Progress tracking (localStorage) | ✅ |
| i18n (translation support) | ✅ Complete (Slovenian + Serbian Cyrillic, all topics) |
| Real LLM API integration (Moonshot) | ✅ |
| User accounts + persistent progress | ⏳ Planned |
| Deployment to fly.io | ⏳ Planned |

---

## Completed Phases

### Phase 1: Redis MVP
- 5 Redis lessons with Detective Noir style
- FastAPI + Jinja2 dark-themed UI
- Interactive command validation with instant feedback

### Phase 2a: SQL + Multi-Style
- 6 SQL lessons with pre-loaded company database
- Sci-Fi narrative style added alongside Detective Noir
- Style selection via `?style=sci_fi`

### Phase 2b: Grader Merge
- Grader-service merged into tutorial-drama (single app for local dev)
- Docker-based code execution via `docker_manager.py`
- Container pooling with round-robin assignment

### Phase 2c: Git Tutorial
- 4 Git lessons (setup, staging, commits, branches)
- Docker image with initialized git repo
- Sci-Fi style added to all Redis lessons

### Phase 2d: Docker Tutorial
- 6 Docker lessons (containers, running, Dockerfile, building, volumes, Compose)
- Hybrid grading: mock CLI for commands, real validation for Dockerfiles/Compose
- Fairy Tale + Romance narrative styles
- Multi-line textarea input for Dockerfile/Compose challenges
- Java/DB2 examples for enterprise learners

### Phase 2e: LLM Internals Tutorial
- 6 lessons: first conversation, tokenization, embeddings, anatomy, API layer, RAG
- Real Moonshot API calls (lessons 00, 04, 05)
- Real tiktoken tokenizer (lesson 01), real cosine similarity (lesson 02)
- Chat mode UI for conversational lessons
- Sci-Fi (ARIA) + Office Comedy (Alex the AI Intern) styles
- Detailed lesson plans: `docs/llm-lesson-plans.md`

### Phase 2f: i18n Support
- Translation architecture: separate files in `translations/{lang}/{topic}/`
- Only translatable strings overridden, grading logic untouched
- Language selector dropdown on lesson pages (English, Slovenščina, Српски)
- 54 translation files: all 5 topics × 2 languages (sl, sr-cyrl)
- Slovenian: all 27 lessons translated (detective_noir + sci_fi / fairy_tale + flirting / office_comedy)
- Serbian Cyrillic: all 27 lessons translated, full Cyrillic script including character names

---

## Next Up

### UI Theme Redesign
- Current dark noir theme is too black/heavy
- Switch to a lighter, more inviting design
- Keep it professional but approachable for learners

### Deployment to fly.io
Two fly.io apps deployed from this monorepo:

**Plan A: fly.io with subprocess grader (recommended)**
- **App 1: `tutorial-drama-web`** — FastAPI + templates + static + tutorials + translations
- **App 2: `tutorial-drama-grader`** — FastAPI + subprocess calls (redis-cli, sqlite3, git, etc.)
- Grader installs tools directly (no Docker-in-Docker needed)
- Refactor `docker_manager.py` → subprocess-based execution
- Connected via `GRADER_URL` env var
- Two Dockerfiles: `Dockerfile.web`, `Dockerfile.grader`
- Two fly configs: `fly.web.toml`, `fly.grader.toml`
- Two GitHub Actions workflows for CI/CD
- Estimated cost: ~$0/mo (within free tier or pennies)

**Plan B: Single Hetzner VPS**
- Both services on one VPS with native Docker (existing `docker_manager.py` works as-is)
- Zero code changes, but requires Docker + nginx + certbot setup
- Fallback if fly.io subprocess approach hits limitations

**Key decision:** Subprocess grading is sufficient for educational platform — students run controlled commands (SET foo bar, SELECT * FROM...), not arbitrary code. Docker isolation is overkill for this use case.

### Bash/Linux Tutorial
- Real shell commands in Alpine container
- Topics: navigation, file ops, pipes, grep, permissions, scripting
- Curriculum TBD

**Detailed design:** `docs/bash-curriculum.md` (to be created)

---

## Future / Phase 3

### Remaining i18n Work
- Translate UI strings (buttons, headers, homepage)
- Additional languages if needed

### More Narrative Styles
- Shakespearean Drama (for more topics)
- Additional styles per existing topics

### Platform Features
- User accounts and authentication
- Persistent progress tracking (replace localStorage)
