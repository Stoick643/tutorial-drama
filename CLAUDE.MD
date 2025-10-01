# Tutorial Drama - Narrative Learning Engine

## Project Overview
Tutorial Drama is a web-based interactive learning platform that teaches technical subjects (Redis, SQL, Git, Docker, Python) through engaging, story-driven tutorials. Instead of dry documentation, learners experience technical concepts through narrative dialogues in various thematic styles (Detective Noir, Sci-Fi, Shakespearean, etc.).

**Vision:** Make learning code feel like playing a game or reading a story, dramatically increasing user engagement and knowledge retention.

## Current Status

### Phase 1 (MVP) - ✅ COMPLETE
- Built FastAPI application with Jinja2 templating
- Implemented Redis tutorial with Detective Noir style (5 lessons)
- Interactive command validation with instant feedback
- Responsive dark-themed UI

### Phase 2 (Scale) - 🔄 IN PROGRESS
- Developed Docker-based grader microservice (separate repo: grader-service)
- Adding SQL tutorial to prove multi-topic architecture
- Implementing multiple narrative styles (Detective Noir + Sci-Fi)

### Phase 3 (Enrich) - ⏳ PLANNED
- Additional narrative styles (Shakespearean, Office Comedy, Flirting/Romance)
- User accounts and progress tracking
- More topics (Git, Docker, Python, DevOps)

## Architecture

### Technology Stack
- **Backend:** Python + FastAPI
- **Frontend:** Jinja2 templates + Vanilla JavaScript + CSS
- **Content:** JSON files (version-controlled, "content-as-code")
- **Grader Service:** Separate FastAPI microservice using Docker for code execution
- **Deployment:** Git-based deployment (planned: Render)

### How It Works
1. **Tutorial Content** - Stored as JSON files in `tutorials/{topic}/{lesson}.json`
2. **Multiple Styles** - Each lesson contains multiple narrative styles in its `styles` array
3. **User Interaction** - Learner reads dialogue, sees code examples, attempts challenges
4. **Code Validation** - User command sent to grader-service via `/api/check-answer`
5. **Grader Service** - Spins up Docker container, executes code, validates result
6. **Instant Feedback** - Returns output, correctness, and themed feedback message

### Key Design Principles
- **Decoupled Architecture** - Content (JSON), presentation (HTML/CSS), logic (Python) are separate
- **Topic-Agnostic Routes** - `/tutorial/{topic}/{lesson}` works for any topic
- **Multi-Style Support** - Same technical content, different narrative experiences
- **Scalable Content** - Add new topics by creating JSON files (no code changes)

## File Structure

```
tutorial-drama/
├── app/
│   └── main.py              # FastAPI routes and application logic
├── static/
│   ├── styles.css           # Dark noir styling
│   ├── interactive.js       # Interactive console logic
│   └── progress.js          # Progress tracking
├── templates/
│   ├── index.html           # Homepage
│   ├── tutorial_menu.html   # Topic lesson selector
│   └── tutorial_template.html  # Lesson viewer (style-agnostic)
├── tutorials/
│   ├── redis/               # Redis lessons (00-04)
│   │   ├── 00_setup.json
│   │   ├── 01_strings.json
│   │   ├── 02_lists.json
│   │   ├── 03_sets.json
│   │   └── 04_hashes.json
│   └── sql/                 # SQL lessons (coming in Phase 2)
├── tests/
│   ├── test_api.py          # API endpoint tests
│   └── test_lesson_loading.py  # Content loading tests
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development/testing dependencies
├── specification.md         # Detailed project specification
└── README.md               # Quick start guide
```

## Lesson JSON Format

Each lesson file contains:
- **tutorial** - Tutorial name (e.g., "Redis Basics")
- **module/scene** - Lesson numbering
- **technical_concept** - Plain explanation of what's being taught
- **code_example** - Example code to demonstrate the concept
- **challenge** - Interactive task for the learner
  - **task** - What the user needs to do
  - **hint** - Optional hint
  - **check_logic** - Validation rules for grader-service
    - **validation_command** - Command to verify correctness
    - **expected_result** - Expected output (type + value)
- **styles** - Array of narrative presentations
  - **name** - Style identifier (detective_noir, sci_fi, etc.)
  - **title** - Lesson title in this style
  - **dialogue** - Array of character/line objects

## Grader Service Integration

The grader-service is a separate microservice (different Git repo) that:
- Runs on port 8001 (tutorial-drama on 8000)
- Uses Docker containers to execute code in isolated environments
- Supports Redis (redis-cli) and SQL (sqlite3) currently
- Pre-warms container pools for fast response times
- Returns: output, is_correct, feedback_message

**Environment Configuration:**
- `GRADER_URL` - URL of grader service (e.g., http://localhost:8001)
- `DEV_MODE` - Disables caching for development

## Development Workflow

### Running Locally
1. Start grader-service: `cd ../grader-service && uvicorn app.main:app --port 8001`
2. Start tutorial-drama: `python app/main.py`
3. Visit: http://127.0.0.1:8000

### Testing
- Run tests: `pytest` or `pytest -v`
- Tests validate API routes, lesson loading, grader integration
- All error messages are theme-agnostic (generic) at API level

### Adding New Topics
1. Create `tutorials/{topic}/` directory
2. Add lesson JSON files following the format
3. Ensure grader-service supports the language
4. No Python code changes needed!

### Adding New Styles
1. Add new style object to lesson's `styles` array
2. Keep same technical_concept, code_example, challenge
3. Change only: name, title, dialogue
4. Style selection via URL query: `?style=sci_fi`

## Planned Topics
- Redis ✅
- SQL 🔄
- Git
- Docker
- Python
- DevOps/Bash

## Planned Narrative Styles
- Detective Noir ✅
- Sci-Fi Adventure 🔄
- Shakespearean Drama
- Office Comedy/Satire
- Flirting/Romance

## License
Licensed by Google (per grader-service)

## Related Repositories
- **grader-service** - Code execution microservice (../grader-service)
