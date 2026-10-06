from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import get_settings
from schemas import (
    HealthResponse,
    LearningPathRequest,
    QARequest,
    QuizRequest,
    QuizResponse,
    TextRequest,
    TextResponse,
)
from services.explanation_module import explain_concept
from services.gemini_service import GeminiServiceError
from services.learning_path import get_learning_recommendations
from services.qna import answer_question
from services.quiz_module import generate_quiz
from services.summary_module import summarize_text

BASE_DIR = Path(__file__).resolve().parent
settings = get_settings()

app = FastAPI(
    title="EduGenie",
    description="Google Gemini powered learning assistant with an optional local explanation model.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def bounded(value: str, limit: int) -> str:
    value = value.strip()
    if not value:
        raise HTTPException(status_code=422, detail="Input cannot be empty.")
    if len(value) > limit:
        raise HTTPException(status_code=413, detail=f"Input is too long. Maximum is {limit} characters.")
    return value


def ai_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=502, detail=str(exc))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        gemini_configured=bool(settings.gemini_api_key),
        local_explanation_enabled=settings.enable_local_explanation,
    )


@app.post("/qa", response_model=TextResponse)
async def qa(payload: QARequest):
    question = bounded(payload.question or payload.text, settings.max_input_chars)
    context = bounded(payload.text, settings.max_input_chars) if payload.question else ""
    try:
        return TextResponse(result=answer_question(question, context))
    except GeminiServiceError as exc:
        raise ai_error(exc) from exc


@app.post("/explain", response_model=TextResponse)
async def explain(payload: TextRequest):
    topic = bounded(payload.text, settings.max_input_chars)
    try:
        return TextResponse(result=explain_concept(topic))
    except Exception as exc:
        raise ai_error(exc) from exc


@app.post("/quiz", response_model=QuizResponse)
async def quiz(payload: QuizRequest):
    passage = bounded(payload.text, settings.max_quiz_context_chars)
    try:
        return generate_quiz(passage, payload.num_questions)
    except GeminiServiceError as exc:
        raise ai_error(exc) from exc


@app.post("/summarize", response_model=TextResponse)
async def summarize(payload: TextRequest):
    text = bounded(payload.text, settings.max_summary_chars)
    try:
        return TextResponse(result=summarize_text(text))
    except GeminiServiceError as exc:
        raise ai_error(exc) from exc


@app.post("/learn/recommendations", response_model=TextResponse)
async def recommendations(payload: LearningPathRequest):
    topic = bounded(payload.text, settings.max_input_chars)
    try:
        return TextResponse(
            result=get_learning_recommendations(topic, payload.level, payload.timeframe)
        )
    except GeminiServiceError as exc:
        raise ai_error(exc) from exc
