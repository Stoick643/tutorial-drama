# Tutorial Drama — Roadmap

## Current State: 4 Topics Live, 2 Planned

### Topics & Styles

| Topic | Lessons | Styles | Status |
|-------|---------|--------|--------|
| Redis | 5 (00-04) | Detective Noir, Sci-Fi | ✅ Complete |
| SQL | 6 (00-05) | Detective Noir, Sci-Fi | ✅ Complete |
| Git | 4 (00-03) | Detective Noir, Sci-Fi | ✅ Complete |
| Docker | 6 (00-05) | Fairy Tale, Romance | ✅ Complete |
| LLM | 6 (00-05) | Sci-Fi, Office Comedy | 🔄 Planned |
| Bash/Linux | TBD | TBD | ⏳ Planned |

### Platform Features

| Feature | Status |
|---------|--------|
| FastAPI + Jinja2 UI | ✅ |
| Docker-based grading | ✅ |
| Interactive console (single-line + multi-line) | ✅ |
| Multiple narrative styles per lesson | ✅ |
| Prev/Next lesson navigation | ✅ |
| Progress tracking (localStorage) | ✅ |
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
- Fairy Tale + Romance narrative styles (first non-Noir/Sci-Fi styles!)
- Multi-line textarea input for Dockerfile/Compose challenges
- Java/DB2 examples for enterprise learners

---

## Next Up

### LLM Internals Tutorial
Teaches how LLMs work under the hood — not prompt tips, but real technical internals.

**Narrative styles:** Sci-Fi (ship AI "ARIA") + Office Comedy (AI intern "Alex")

**Lessons:**
| # | Title | What Student Does | Grading |
|---|-------|-------------------|---------|
| 00 | First Conversation | Type a question → real LLM responds | Real Moonshot API call |
| 01 | Tokenization | Type text → see token splits + IDs | Real tiktoken |
| 02 | Embeddings | Compare sentences → see similarity scores | numpy + pre-computed vectors |
| 03 | Anatomy of a Call | Build API request JSON by hand | JSON validator |
| 04 | The API Layer | Write curl command → real API call | Real Moonshot API call |
| 05 | Enhanced Prompts & RAG | Build system + context + user prompt | JSON validator + real API call |

**Pedagogical approach:** Concrete before abstract. Lesson 00 = "wow" moment (real LLM response), then each lesson peels back one layer. Bloom's taxonomy: Experience → Understand → Apply → Analyze.

**API:** Moonshot (primary), Deepseek shown as code example. API key server-side (`LLM_API_KEY`).

**Detailed design:** `docs/llm-curriculum.md`

### Bash/Linux Tutorial
- Real shell commands in Alpine container
- Topics: navigation, file ops, pipes, grep, permissions, scripting
- Curriculum TBD

**Detailed design:** `docs/bash-curriculum.md` (to be created)

---

## Future / Phase 3

### More Narrative Styles
- Shakespearean Drama
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
