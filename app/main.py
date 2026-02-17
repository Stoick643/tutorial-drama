from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from collections import defaultdict
from pydantic import BaseModel
import json
import os
import time
from dotenv import load_dotenv
from pathlib import Path

# Grader backend: "docker" (default for local dev) or "subprocess" (for fly.io)
GRADER_MODE = os.getenv("GRADER_MODE", "docker")

try:
    from . import grader_schemas
    if GRADER_MODE == "subprocess":
        from .subprocess_manager import manager as container_manager
    else:
        from .docker_manager import manager as container_manager
except ImportError:
    import grader_schemas
    if GRADER_MODE == "subprocess":
        from subprocess_manager import manager as container_manager
    else:
        from docker_manager import manager as container_manager

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    # Startup: warm up container pools
    await container_manager.startup()
    yield
    # Shutdown: cleanup containers
    await container_manager.shutdown()

app = FastAPI(title="Narrative Learning Engine", lifespan=lifespan)

base_dir = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(base_dir / "static")), name="static")

templates = Jinja2Templates(directory=str(base_dir / "templates"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dev mode: disable caching for static files
if os.getenv("DEV_MODE"):
    @app.middleware("http")
    async def add_no_cache_headers(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/static"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

# --- Rate Limiting ---
# Simple in-memory rate limiter: max requests per IP per window
RATE_LIMIT_MAX = 30          # max requests
RATE_LIMIT_WINDOW = 60       # per 60 seconds
_rate_limit_store = defaultdict(list)  # {ip: [timestamp, ...]}

def check_rate_limit(ip: str) -> bool:
    """Returns True if request is allowed, False if rate limited."""
    now = time.time()
    # Clean old entries
    _rate_limit_store[ip] = [t for t in _rate_limit_store[ip] if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limit_store[ip]) >= RATE_LIMIT_MAX:
        return False
    _rate_limit_store[ip].append(now)
    return True


class CommandRequest(BaseModel):
    command: str
    topic: str
    lesson: str

class CommandResponse(BaseModel):
    output: str
    is_correct: bool
    feedback_message: str

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/tutorial/{topic}", response_class=HTMLResponse)
async def get_tutorial_menu(request: Request, topic: str):
    tutorial_dir = base_dir / f"tutorials/{topic}"

    if not tutorial_dir.exists():
        raise HTTPException(status_code=404, detail=f"Tutorial topic '{topic}' not found")

    lessons = []
    tutorial_name = topic.title()
    description = "Learn through engaging narratives and interactive challenges"
    available_styles = []
    current_style = request.query_params.get("style", "detective_noir")

    # Load all lesson files
    for json_file in sorted(tutorial_dir.glob("*.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                lesson_data = json.load(f)

            # Collect available styles from first lesson
            if not available_styles and lesson_data.get("styles"):
                available_styles = [
                    {
                        "name": s.get("name", ""),
                        "display_name": s.get("name", "").replace("_", " ").title()
                    }
                    for s in lesson_data.get("styles", [])
                ]

            # Find the selected style or use first style
            selected_style = None
            for s in lesson_data.get("styles", []):
                if s.get("name") == current_style:
                    selected_style = s
                    break
            if not selected_style and lesson_data.get("styles"):
                selected_style = lesson_data.get("styles")[0]

            lessons.append({
                "filename": json_file.stem,
                "title": selected_style.get("title", f"Lesson {json_file.stem}") if selected_style else f"Lesson {json_file.stem}",
                "technical_concept": lesson_data.get("technical_concept", ""),
                "code_example": lesson_data.get("code_example"),
                "module": lesson_data.get("module", 1),
                "scene": lesson_data.get("scene", 1)
            })

            # Use first lesson to set tutorial info
            if not lessons or len(lessons) == 1:
                tutorial_name = lesson_data.get("tutorial", topic.title())

        except (json.JSONDecodeError, Exception):
            continue

    return templates.TemplateResponse(
        "tutorial_menu.html",
        {
            "request": request,
            "topic": topic,
            "tutorial_name": tutorial_name,
            "description": description,
            "available_styles": available_styles,
            "current_style": current_style,
            "lessons": lessons
        }
    )

@app.get("/tutorial/{topic}/{lesson}", response_class=HTMLResponse)
async def get_tutorial(request: Request, topic: str, lesson: str):
    json_path = base_dir / f"tutorials/{topic}/{lesson}.json"

    if not json_path.exists():
        raise HTTPException(status_code=404, detail=f"Lesson '{lesson}' not found in topic '{topic}'")

    # Calculate prev/next lesson navigation
    topic_dir = base_dir / f"tutorials/{topic}"
    lesson_files = sorted([f.stem for f in topic_dir.glob("*.json")])
    current_index = lesson_files.index(lesson) if lesson in lesson_files else -1
    prev_lesson = lesson_files[current_index - 1] if current_index > 0 else None
    next_lesson = lesson_files[current_index + 1] if current_index < len(lesson_files) - 1 else None

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            lesson_data = json.load(f)

        # i18n: load translation if language is specified
        lang = request.query_params.get("lang", "en")
        if lang != "en":
            trans_path = base_dir / f"translations/{lang}/{topic}/{lesson}.json"
            if trans_path.exists():
                with open(trans_path, "r", encoding="utf-8") as f:
                    trans = json.load(f)
                # Merge translated strings into lesson data
                if "tutorial" in trans:
                    lesson_data["tutorial"] = trans["tutorial"]
                if "technical_concept" in trans:
                    lesson_data["technical_concept"] = trans["technical_concept"]
                if "challenge" in trans:
                    for key in ("task", "hint"):
                        if key in trans["challenge"]:
                            lesson_data["challenge"][key] = trans["challenge"][key]
                # Merge translated styles (keyed by style name)
                if "styles" in trans:
                    for style_obj in lesson_data.get("styles", []):
                        style_name = style_obj.get("name", "")
                        if style_name in trans["styles"]:
                            ts = trans["styles"][style_name]
                            if "title" in ts:
                                style_obj["title"] = ts["title"]
                            if "dialogue" in ts:
                                style_obj["dialogue"] = ts["dialogue"]

        style = request.query_params.get("style", "detective_noir")

        # Collect available styles
        available_styles = [
            {
                "name": s.get("name", ""),
                "display_name": s.get("name", "").replace("_", " ").title()
            }
            for s in lesson_data.get("styles", [])
        ]

        selected_style = None
        for s in lesson_data.get("styles", []):
            if s["name"] == style:
                selected_style = s
                break

        if not selected_style and lesson_data.get("styles"):
            selected_style = lesson_data["styles"][0]

        return templates.TemplateResponse(
            "tutorial_template.html",
            {
                "request": request,
                "tutorial": lesson_data.get("tutorial", ""),
                "module": lesson_data.get("module", 1),
                "scene": lesson_data.get("scene", 1),
                "title": selected_style.get("title", "") if selected_style else "",
                "dialogue": selected_style.get("dialogue", []) if selected_style else [],
                "code_example": lesson_data.get("code_example", {}),
                "challenge": lesson_data.get("challenge", {}),
                "technical_concept": lesson_data.get("technical_concept", ""),
                "topic": topic,
                "lesson": lesson,
                "style": style,
                "available_styles": available_styles,
                "current_style": style,
                "prev_lesson": prev_lesson,
                "next_lesson": next_lesson,
                "lang": lang,
                "js_version": str(int(time.time()))
            }
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON format in lesson file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading lesson: {str(e)}")


@app.post("/api/check-answer", response_model=CommandResponse)
async def check_answer(request: CommandRequest, req: Request):
    # Rate limiting
    client_ip = req.client.host if req.client else "unknown"
    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please wait a moment."}
        )

    # 1. Load the lesson JSON to get the check_logic
    json_path = base_dir / f"tutorials/{request.topic}/{request.lesson}.json"
    if not json_path.exists():
        raise HTTPException(status_code=404, detail="Lesson file not found")

    with open(json_path, "r", encoding="utf-8") as f:
        lesson_data = json.load(f)

    check_logic_data = lesson_data.get("challenge", {}).get("check_logic")
    if not check_logic_data:
        raise HTTPException(status_code=500, detail="Missing check_logic in lesson challenge")

    # 2. Convert check_logic dict to Pydantic model
    try:
        check_logic = grader_schemas.CheckLogic(**check_logic_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid check_logic format: {str(e)}")

    # 3. Execute code directly using container manager
    try:
        result = await container_manager.execute_code_in_container(
            language=request.topic,  # e.g., "redis"
            user_code=request.command,
            check_logic=check_logic
        )

        return CommandResponse(
            output=result.output,
            is_correct=result.is_correct,
            feedback_message=result.feedback_message
        )

    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Unsupported topic: {request.topic}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during grading: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)