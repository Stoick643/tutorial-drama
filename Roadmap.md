# Tutorial Drama — Roadmap

## Current State: 6 Topics Live

### Topics & Styles

| Topic | Lessons | Styles | Status |
|-------|---------|--------|--------|
| Redis | 5 (00-04) | Detective Noir, Sci-Fi, Shakespearean, Office Comedy | ✅ Complete |
| SQL | 6 (00-05) | Detective Noir, Sci-Fi | ✅ Complete |
| Git | 4 (00-03) | Detective Noir, Sci-Fi | ✅ Complete |
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

### Lesson Numbering Fix
- Current: "Module 1 - Scene 0" → confusing (0-indexed, "module" implies more, "scene" is unclear)
- New: **"Lesson 1 of 8"** — 1-indexed, clear, no jargon
- Template-only change, affects all topics
- Internal JSON fields (`module`/`scene`) stay unchanged

### Progressive Hint System
- Current: "hint" field contains the full solution — not helpful for learning
- New 3-step flow:
  1. 💡 **Hint** — conceptual nudge ("Think about which command creates directories...")
  2. 🔓 **Show Solution** — confirmation: "Do you surrender? 🏳️" (Yes / No)
  3. Full solution revealed
- Requires:
  - New `"solution"` field in lesson JSON (alongside existing `"hint"`)
  - UI changes in `tutorial_template.html` + `interactive.js`
  - Update all 35 lessons across all topics (split hint from solution)

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
