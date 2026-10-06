from typing import Literal
from pydantic import BaseModel, Field, field_validator


class TextRequest(BaseModel):
    text: str = Field(min_length=1)

    @field_validator("text")
    @classmethod
    def clean_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Input cannot be empty.")
        return value


class QARequest(TextRequest):
    question: str | None = None


class QuizRequest(TextRequest):
    num_questions: int = Field(default=3, ge=1, le=10)


class LearningPathRequest(TextRequest):
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    timeframe: str = Field(default="8 weeks", min_length=2, max_length=80)


class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(min_length=4, max_length=4)
    correct_answer: str
    explanation: str


class QuizResponse(BaseModel):
    questions: list[QuizQuestion]


class TextResponse(BaseModel):
    result: str


class HealthResponse(BaseModel):
    status: str
    gemini_configured: bool
    local_explanation_enabled: bool
