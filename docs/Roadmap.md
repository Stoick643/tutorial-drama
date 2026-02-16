# Tutorial Drama — Roadmap

## ✅ Phase 1: Redis MVP (Complete)
- 5 Redis lessons (00-04) with Detective Noir style
- FastAPI + Jinja2 dark-themed UI
- Interactive command validation with instant feedback

## ✅ Phase 2a: SQL + Multi-Style (Complete)
- 6 SQL lessons (00-05)
- Sci-Fi narrative style added alongside Detective Noir
- Style selection via URL query: `?style=sci_fi`

## ✅ Phase 2b: Grader Merge (Complete)
- Grader-service merged into tutorial-drama (single app)
- Docker-based code execution built in (`app/docker_manager.py`)
- Docker images for Redis (`docker/redis/`) and SQL (`docker/sql/`)

## 🔄 Phase 2c: Git Tutorial (In Progress)
- **Content:** 4 Git lessons written (00_setup, 01_staging, 02_commits, 03_branches)
- **Docker:** `docker/git/Dockerfile` exists, image built (`grader-image-git`)
- **Grader:** `docker_manager.py` modified to support Git
- **Redis lessons:** Updated with Sci-Fi style added to all 5 lessons
- **Status:** Not yet tested end-to-end

### Immediate Next Steps
1. Test Git lessons end-to-end (Docker is ready, images built)
2. Verify grader handles Git commands correctly
3. Commit all uncommitted work

## ⏳ Phase 3: Enrich (Planned)

### New Topics
- [ ] Docker (teaching Docker using a simulator)
- [ ] Python
- [ ] DevOps / Bash

### New Narrative Styles
- [ ] Shakespearean Drama
- [ ] Office Comedy / Satire
- [ ] Flirting / Romance

### Platform Features
- [ ] User accounts and authentication
- [ ] Progress tracking and persistence
- [ ] Deployment to Render (or similar)
