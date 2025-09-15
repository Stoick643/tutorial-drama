from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import redis
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

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = None

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
except Exception as e:
    print(f"Warning: Could not connect to Redis: {e}")
    print("Running in demo mode without Redis sandbox")

class CommandRequest(BaseModel):
    command: str
    lesson: str

class CommandResponse(BaseModel):
    success: bool
    output: str
    message: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Narrative Learning Engine"}

@app.get("/tutorial/{topic}/{lesson}", response_class=HTMLResponse)
async def get_tutorial(request: Request, topic: str, lesson: str):
    json_path = base_dir / f"tutorials/{topic}/{lesson}.json"

    if not json_path.exists():
        raise HTTPException(status_code=404, detail=f"Lesson {lesson} not found for topic {topic}")

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
                "style": style
            }
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid lesson file format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/check-answer", response_model=CommandResponse)
async def check_answer(request: CommandRequest):
    if not redis_client:
        return CommandResponse(
            success=False,
            output="Redis sandbox is not available. Running in demo mode.",
            message="Please set up a Redis connection to test commands."
        )

    try:
        parts = request.command.strip().split()
        if not parts:
            return CommandResponse(
                success=False,
                output="",
                message="Please enter a Redis command"
            )

        command = parts[0].upper()
        args = parts[1:]

        result = redis_client.execute_command(command, *args)

        json_path = base_dir / f"tutorials/redis/{request.lesson}.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                lesson_data = json.load(f)

            if "challenge" in lesson_data and "check" in lesson_data["challenge"]:
                check = lesson_data["challenge"]["check"]
                check_command = check.get("command", "").split()
                if check_command:
                    check_result = redis_client.execute_command(check_command[0], *check_command[1:])

                    expected_type = check.get("expected_output_type", "")
                    expected_value = check.get("expected_output_value")

                    is_correct = False
                    if expected_type == "integer_greater_than":
                        is_correct = isinstance(check_result, int) and check_result > expected_value
                    elif expected_type == "exact":
                        is_correct = str(check_result) == str(expected_value)
                    else:
                        is_correct = check_result is not None

                    if is_correct:
                        return CommandResponse(
                            success=True,
                            output=str(result) if result is not None else "OK",
                            message="Excellent work, detective! You've cracked the case."
                        )
                    else:
                        return CommandResponse(
                            success=False,
                            output=str(result) if result is not None else "OK",
                            message="Not quite right. Check your command and try again."
                        )

        return CommandResponse(
            success=True,
            output=str(result) if result is not None else "OK",
            message="Command executed successfully"
        )

    except redis.ResponseError as e:
        return CommandResponse(
            success=False,
            output="",
            message=f"Redis error: {str(e)}"
        )
    except Exception as e:
        return CommandResponse(
            success=False,
            output="",
            message=f"Error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)