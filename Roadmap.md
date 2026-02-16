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
| i18n (translation support) | ✅ POC (Slovenian, Redis lesson 00) |
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
- Language selector dropdown on lesson pages
- POC: Redis lesson 00 in Slovenian (detective_noir + sci_fi)

---

## Next Up

### Bash/Linux Tutorial
- Real shell commands in Alpine container
- Topics: navigation, file ops, pipes, grep, permissions, scripting
- Curriculum TBD

**Detailed design:** `docs/bash-curriculum.md` (to be created)

### i18n Expansion
- Complete Slovenian translations for all topics
- Add Serbian Cyrillic (`sr-cyrl`)
- Translate UI strings (buttons, headers)

---

## Future / Phase 3

### More Narrative Styles
- Shakespearean Drama (for more topics)
- Additional styles per existing topics

### Platform Features
- User accounts and authentication
- Persistent progress tracking (replace localStorage)
- Deployment to fly.io (two services: tutorial app + grader)

### Deployment Architecture
Two fly.io services deployed from this monorepo:
- **Tutorial app** — lightweight container with UI + content
- **Grader service** — Fly Machine (microVM) with Docker daemon

See `plan-phase-3.md` for the original merge/split rationale.
