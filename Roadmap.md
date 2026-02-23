# Tutorial Drama — Roadmap

## Current State: 6 Topics Live

### Topics & Styles

| Topic | Lessons | Styles | Status |
|-------|---------|--------|--------|
| Redis | 5 (00-04) | Detective Noir, Sci-Fi, Shakespearean, Office Comedy | ✅ Complete |
| SQL | 6 (00-05) | Detective Noir, Sci-Fi | ✅ Complete |
| Git | 5 (00-04) | Socratic, Zen | ✅ Rewritten Feb 2026 |
| Docker | 6 (00-05) | Fairy Tale, Romance | ✅ Complete |
| LLM | 6 (00-05) | Sci-Fi, Office Comedy | ✅ Complete |
| Bash | 8 (00-07) | Survival Adventure, Heist/Spy | ✅ Complete |

### Platform Features

| Feature | Status |
|---------|--------|
| FastAPI + Jinja2 UI | ✅ |
| Docker-based grading (local) | ✅ |
| Subprocess-based grading (fly.io) | ✅ |
| Interactive console (single-line + multi-line) | ✅ |
| Chat mode (Send button, no grading) | ✅ |
| Multiple narrative styles per lesson | ✅ |
| Prev/Next lesson navigation | ✅ |
| Progress tracking (localStorage) | ✅ |
| i18n: Slovenian + Serbian Cyrillic (all 35 lessons) | ✅ |
| Real LLM API integration (Moonshot) | ✅ |
| Light warm theme UI | ✅ |
| Deployment to fly.io | ✅ |
| CI/CD: GitHub Actions → fly deploy | ✅ |

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
- Slovenian: all 35 lessons translated
- Serbian Cyrillic: all 35 lessons translated, full Cyrillic script including character names

### UI Theme Redesign
- Light warm theme replacing dark noir (#f8f7f4 background, white cards)
- Facebook blue accent (#1877F2) instead of red
- Sans-serif body font, monospace only for code/console
- Dark console blocks (Catppuccin-inspired) inside light page

### Subprocess Refactor
- `app/subprocess_manager.py` — same interface as `docker_manager.py`
- Tools installed directly: redis-cli, sqlite3, git, python + libs
- `subprocess.run()` with timeouts instead of `docker exec`
- Input sanitization: command whitelisting, env var access blocked, shell injection prevented
- State reset between requests (FLUSHALL, copy fresh DB, git reset)
- Toggle via env var: `GRADER_MODE=subprocess` vs `GRADER_MODE=docker` (default)

### Phase 2g: Bash Tutorial
- 8 lessons: navigation, files, grep/find, pipes, xargs, sed/awk, toolbelt, scripting
- Two narrative styles: Survival Adventure + Heist/Spy
- Real bash execution in Alpine container
- Pipe and xargs as centerpiece (lessons 03-04)
- Lesson 06: chat mode for trickier commands (chmod, curl, history, alias, top)
- Lesson 07: write a complete bash script (multiline)
- Docker grader: `grader-image-bash` with pre-populated sample files
- Subprocess grader: workspace with same sample files
- Translations: Slovenian + Serbian Cyrillic for all 8 lessons

### Feb 2026 Evaluation Fixes
- Extracted shared grading logic into `app/grader.py` — eliminated ~60 lines of duplication between `docker_manager.py` and `subprocess_manager.py`
- Fixed Starlette `TemplateResponse` deprecation (21 warnings) — new API: `TemplateResponse(request, name, context)`
- Fixed rate limiter memory leak — added periodic cleanup of stale IPs (every 5 min)
- Fixed silent error swallowing in `get_tutorial_menu()` — now logs warnings
- Added `logging` module to `main.py`
- Fixed hardcoded "detective" in completion message → generic "Well done!"
- Fixed copyright year: 2024 → 2026
- Fixed 14 solution-task mismatches across Redis, SQL, Git, and Docker lessons
- Fixed 4 hint mismatches (redis/01, sql/00, docker/00, docker/03)
- Added solutions to LLM lessons 01-05 (previously had none)
- Added grading unit tests (`tests/test_grader.py`) — all 6 validation types covered
- Added JSON structure tests for all 35 lessons across all 6 topics (`tests/test_lesson_structure.py`)
- Test count: 55 → 389 passing

### Git Tutorial Rewrite
- Replaced 4-lesson Git tutorial with 5-lesson "Git from the Terminal"
- New audience: developers moving from GUI tools to terminal
- New narrative styles: Socratic (Socrates & student) + Zen (Master & student)
- Socratic method in all dialogues — questions lead to discovery
- ASCII diagrams: 4-area model, branch pointers, undo table
- Lessons: The 4 Areas, Branches as Pointers, Inspecting & Undoing, Under the Hood, The Big Picture (chat mode)
- Removed old translations (sl, sr-cyrl) — need redoing for new content
- Test count: 389 → 397 passing

---

## Deployment

Single fly.io app deployed from this monorepo:

**Architecture:**
- **One app: `tutorial-drama`** — FastAPI + all grading tools in one image
- `Dockerfile.flyio` installs redis-server, redis-cli, sqlite3, git, bash, python + libs
- `GRADER_MODE=subprocess` — no Docker-in-Docker needed
- CI/CD: GitHub Actions auto-deploys on push to master
- Cost: ~$0/mo (pennies)

**Live at:** [tutorial-drama.fly.dev](https://tutorial-drama.fly.dev)

**Deployment commands:**
```bash
# One-time setup
fly launch --no-deploy --dockerfile Dockerfile.flyio
fly secrets set LLM_API_KEY=your-moonshot-key

# Deploy (or just git push — CI/CD handles it)
fly deploy --dockerfile Dockerfile.flyio
```

**Plan B: Single Hetzner VPS**
- Both services on one VPS with native Docker (existing `docker_manager.py` works as-is)
- Zero code changes, but requires Docker + nginx + certbot setup
- Fallback if fly.io approach hits limitations

---

## Next Up

### Lesson Content Polish
- Bash lesson 00: simplify challenge to just `mkdir camp` (no `&&` for beginners)
- Bash lesson 01: more flavor on command names (cat, touch, echo), explain `>` operator
- Review all bash lessons for beginner-friendliness
- Ensure challenges match difficulty progression

### UI String Translations
- Currently only lesson content is translated, UI chrome is English-only
- Buttons: Check Answer, Hint, Show Solution, Previous, Next
- Headers: "Lesson X of Y", homepage text, feature descriptions
- Not priority — prep structure for it when implementing hint system

### Code Quality (Deferred from Feb 2026 Evaluation)
- **Extract `lesson_loader.py` from `main.py`** — Move JSON loading, i18n merging, and style selection into a dedicated module. Currently `main.py` is ~230 lines which is manageable, but would benefit from separation if it grows further.
- **Move inline JS/CSS to external files** — `tutorial_template.html` has ~30 lines of inline hint system JS. `interactive.js` and `progress.js` inject CSS via `document.createElement('style')`. Move to `styles.css` and dedicated JS files.
- **Dynamic homepage generation** — Generate topic cards from `tutorials/` directory instead of hardcoded HTML in `index.html`. Low priority — only needed when adding topics frequently.
- **Docker manager input sanitization** — `subprocess_manager.py` has thorough input sanitization; `docker_manager.py` has none. Docker containers provide isolation, but defense-in-depth could be added carefully (avoiding blocking legitimate learning commands like SQL DROP).

---

## Future / Phase 3

### More Content
- Additional narrative styles (Shakespearean for more topics)
- More styles per existing topics
- Additional topics TBD

### Platform Features
- User accounts and authentication
- Persistent progress tracking (replace localStorage with server-side DB)
- Accessibility improvements (ARIA labels, keyboard navigation, color contrast)

### Additional Languages
- UI string translation infrastructure
- More languages if demand exists
