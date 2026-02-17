# Project Evaluation — Tutorial Drama

**Date:** 2026-02-17
**Evaluator:** Claude Code (automated review)

---

## 🟢 What's Good

### 1. Excellent Concept & Vision
The idea of teaching technical subjects through narrative styles (Detective Noir, Sci-Fi, Fairy Tales) is genuinely creative and differentiating. It's not "yet another tutorial site."

### 2. Clean Architecture
- Content-as-code (JSON) is the right call — version-controlled, diffable, no CMS needed.
- Topic-agnostic routing (`/tutorial/{topic}/{lesson}`) means zero code changes to add content.
- Dual grading backends (Docker for local dev, subprocess for prod) is a pragmatic solution.
- Separation of concerns: content / presentation / grading logic are cleanly decoupled.

### 3. Surprisingly Complete for a Solo Project
- 5 topics, 27 lessons, 54 translation files, multiple narrative styles.
- Real code execution (not fake validation!) — actual redis-cli, sqlite3, git.
- i18n with Slovenian and Serbian Cyrillic.
- ~835 lines of Python, ~1100 lines of frontend — lean codebase for what it does.

### 4. Good Developer Documentation
- CLAUDE.md, README.md, and Roadmap.md are thorough and up-to-date.
- Clear "how to add a topic" and "how to add a style" guides.
- Roadmap has honest status tracking.

### 5. Sensible Deployment Strategy
- fly.io with auto-stop machines = near-zero cost when idle.
- CI/CD via GitHub Actions already set up.
- Single Dockerfile.flyio is simple and works.

---

## 🟡 What Could Be Better

### 1. Security Concerns in Grading
- `subprocess_manager.py` runs user-submitted commands directly. Even with timeouts, there's no sandboxing in subprocess mode. A user could run `rm -rf /`, read env vars (`echo $LLM_API_KEY`), or abuse the network. The Docker mode is safer but not used in production.
- **Recommendation:** At minimum, add command whitelisting/sanitization. Consider using `nsjail` or `bubblewrap` for lightweight sandboxing in subprocess mode.

### 2. No Authentication or Rate Limiting
- The `/api/check-answer` endpoint is wide open. Anyone can spam it with arbitrary commands.
- No rate limiting means potential abuse of the grading infrastructure (especially the LLM/Moonshot API calls which cost money).

### 3. Test Coverage is Thin
- Only 2 test files (~388 lines including fixtures). For 27 lessons with complex grading logic, there should be integration tests per topic, grading edge cases, and translation validation tests.
- No tests for `subprocess_manager.py` at all.

### 4. Roadmap vs. Reality Mismatch
- The Roadmap says "Deployment to fly.io: ⏳ Planned" but `fly.toml`, `Dockerfile.flyio`, and the GitHub Actions workflow already exist. The README even says "Live: tutorial-drama.fly.dev." Docs are out of sync.
- Roadmap planned a 2-app architecture (web + grader) but a single app was shipped. Good simplification, but the Roadmap still describes the old plan.

### 5. `DEV_MODE=true` in Production Dockerfile
- `Dockerfile.flyio` sets `ENV DEV_MODE=true` — this disables template caching and adds no-cache headers. Should be removed for production.

### 6. `docker>=7.0.0` in Production Requirements
- The Docker Python SDK is in `requirements.txt` but isn't needed in subprocess/fly.io mode. It adds unnecessary weight to the production image.

---

## 🔴 What's Missing

### 1. No Input Sanitization / Command Injection Protection
This is the biggest gap. Users type commands that get executed on the server. Critical for a public-facing app.

### 2. No Monitoring / Logging / Error Tracking
- No structured logging, no Sentry/equivalent, no health check endpoint (beyond what fly.io pings). If grading breaks silently, nobody will know.

### 3. No `.env.example` File
- `.env` is presumably gitignored, but there's no `.env.example` showing what variables are needed. New contributors would have to read multiple docs to figure this out.

### 4. No License File
- No `LICENSE` — unclear if this is open source or proprietary.

### 5. No Content Validation / Schema
- 27 JSON lesson files with no JSON Schema to validate them. A typo in `check_logic` or a missing `validation_command` would only be caught at runtime. A schema + CI check would prevent broken lessons from shipping.

### 6. No Accessibility Considerations
- No mention of ARIA labels, keyboard navigation, screen reader support, or color contrast ratios in the frontend.

### 7. Progress Tracking is localStorage Only
- Acknowledged in the roadmap, but worth emphasizing: progress is device-locked and easily lost. For a learning platform, this is a significant UX gap.

---

## 💡 Other Observations

- **The `docker>=7.0.0` line in requirements.txt** breaks the pip-compile comment at the top (it's manually appended, not compiled). This could cause dependency conflicts.
- **Single-app deployment is smarter** than the originally planned two-app split. The subprocess approach eliminates Docker-in-Docker complexity. Good pivot.
- **The LLM topic teaching LLM internals** (tokenization, embeddings, RAG) while using an LLM API for grading is a nice meta-touch.
- **3 languages for a tutorial platform** is unusual and impressive — suggests a specific audience (Balkans + international).
- **No frontend build step** (no npm, no bundler) — this is actually a feature. Zero frontend complexity. Refreshing.

---

## Summary

A well-architected, creative project with solid content and clean code. The main risks are **security** (unsandboxed command execution) and **missing operational basics** (monitoring, rate limiting, input validation). The codebase is lean and well-documented. Fix the security gaps before promoting it publicly, sync the Roadmap with reality, and add a JSON schema for content validation.
