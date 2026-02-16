# Plan: Merge Grader-Service into Tutorial-Drama

## Goal
Eliminate the separate grader-service microservice by embedding Docker-based code execution directly into tutorial-drama. One service to run instead of two.

## High-Level Steps

1. **Copy core files from grader-service**
   - `docker_manager.py` → `app/docker_manager.py`
   - `schemas.py` → `app/grader_schemas.py`

2. **Update `/api/check-answer` endpoint**
   - Replace HTTP call to grader-service with direct function call
   - Remove `GRADER_URL` dependency

3. **Add Docker dependency**
   - Add `docker` package to requirements.txt
   - Add startup/shutdown lifecycle for container pool

4. **Copy Docker images setup**
   - Copy Dockerfiles from grader-service
   - Add build instructions to README

5. **Update tests**
   - Adapt grader tests to work in tutorial-drama
   - Remove HTTP mocking, test container logic directly

## Feasibility Assessment

| Aspect | Assessment |
|--------|------------|
| Complexity | **Low-Medium** - Mostly copy/paste + wiring |
| Risk | **Low** - Both codebases are well-structured |
| Files changed | ~5-7 files |
| New files | 2-3 files (docker_manager, schemas, Dockerfiles) |
| Breaking changes | None - API stays the same |
| Reversibility | **Easy** - Can split back out later |

## Open Questions

- Where to put Dockerfiles? (`docker/` folder or `graders/` like original?)
- Keep container pooling or simplify to single container per language?

## Verification

- Run existing tutorial-drama tests
- Test Redis lesson manually (PING, SET/GET)
- Test SQL lesson manually (SELECT queries)
