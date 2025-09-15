# Tutorial Drama

A narrative-driven learning platform that teaches technical subjects (Redis, Git, Docker) through engaging, story-driven tutorials. Learn Redis commands while following Detective Indecks solve data crimes in a noir-themed adventure.

## Quick Start

```bash
# Start the server
venv/Scripts/python app/main.py
```

**Visit these URLs:**
- Setup lesson: http://127.0.0.1:8000/tutorial/redis/00_setup
- Main lesson: http://127.0.0.1:8000/tutorial/redis/01_strings

## Features

🕵️ **Detective Noir Theme** - Learn through engaging dialogue and storytelling
⚡ **Interactive Console** - Test Redis commands in real-time
🎯 **Instant Feedback** - Get immediate validation on your solutions
📚 **JSON Content** - Easy to add new lessons and narrative styles
🚀 **FastAPI Backend** - Modern, fast Python web framework

## Phase 1 MVP ✅

- **Redis Basics Tutorial** with SET/GET/SETEX commands
- **Detective Indecks** character with atmospheric dialogue
- **Interactive command validation** against lesson objectives
- **Responsive design** with dark noir styling
- **Modular architecture** ready for expansion

## Project Structure

```
tutorial-drama/
├── app/main.py              # FastAPI backend
├── static/                  # CSS and JavaScript
├── templates/               # Jinja2 HTML templates
├── tutorials/redis/         # JSON lesson content
├── requirements.in          # pip-tools dependencies
└── .env                     # Configuration (Redis URL)
```

## Tech Stack

- **Backend**: FastAPI + Uvicorn
- **Frontend**: Jinja2 + Vanilla JS + CSS
- **Content**: JSON files for easy editing
- **Dependencies**: pip-tools for reproducible builds

## Coming Next (Phase 2)

- Docker-based code executor service
- Additional topics (Git, SQL, Python)
- Multiple narrative styles (Sci-Fi, Shakespeare, Comedy)
- User progress tracking