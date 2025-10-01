from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import httpx
import time
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

app = FastAPI(title="Narrative Learning Engine")

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

# REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
GRADER_URL = os.getenv("GRADER_URL")

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
    style_name = "Detective Noir"

    # Load all lesson files
    for json_file in sorted(tutorial_dir.glob("*.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                lesson_data = json.load(f)

            # Get the first style for display
            style = lesson_data.get("styles", [{}])[0] if lesson_data.get("styles") else {}

            lessons.append({
                "filename": json_file.stem,
                "title": style.get("title", f"Lesson {json_file.stem}"),
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
            "style_name": style_name,
            "lessons": lessons
        }
    )

@app.get("/tutorial/{topic}/{lesson}", response_class=HTMLResponse)
async def get_tutorial(request: Request, topic: str, lesson: str):
    json_path = base_dir / f"tutorials/{topic}/{lesson}.json"

    if not json_path.exists():
        raise HTTPException(status_code=404, detail=f"Lesson '{lesson}' not found in topic '{topic}'")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            lesson_data = json.load(f)

        style = request.query_params.get("style", "detective_noir")

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
                "js_version": str(int(time.time()))
            }
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON format in lesson file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading lesson: {str(e)}")


@app.post("/api/check-answer", response_model=CommandResponse)
async def check_answer(request: CommandRequest):
    if not GRADER_URL:
        raise HTTPException(status_code=500, detail="Grader service URL not configured")

    # 1. Load the lesson JSON to get the check_logic
    json_path = base_dir / f"tutorials/{request.topic}/{request.lesson}.json"
    if not json_path.exists():
        raise HTTPException(status_code=404, detail="Lesson file not found")
    
    with open(json_path, "r", encoding="utf-8") as f:
        lesson_data = json.load(f)

    check_logic = lesson_data.get("challenge", {}).get("check_logic")
    if not check_logic:
        raise HTTPException(status_code=500, detail="Missing check_logic in lesson challenge")

    # 2. Build the payload for the grader service
    payload_to_grader = {
        "language": request.topic, # e.g., "redis"
        "user_code": request.command,
        "check_logic": check_logic
    }

    # 3. Use httpx to call the grader service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(GRADER_URL + "/grade", json=payload_to_grader, timeout=10.0)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Return the grader's response mapped to our model
        grader_response = response.json()
        return CommandResponse(
            output=grader_response.get("output", ""),
            is_correct=grader_response.get("is_correct", False),
            feedback_message=grader_response.get("feedback_message", "")
        )

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Unable to connect to grader service: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during grading: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)