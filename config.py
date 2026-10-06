from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    gemini_api_key: str | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-3.8-flash", validation_alias="GEMINI_MODEL")
    local_explanation_model: str = Field(
        default="MBZUAI/LaMini-Flan-T5-783M", validation_alias="LOCAL_EXPLANATION_MODEL"
    )
    enable_local_explanation: bool = Field(default=True, validation_alias="ENABLE_LOCAL_EXPLANATION")
    app_host: str = Field(default="127.0.0.1", validation_alias="APP_HOST")
    app_port: int = Field(default=8000, validation_alias="APP_PORT")
    max_input_chars: int = Field(default=20000, validation_alias="MAX_INPUT_CHARS")
    max_summary_chars: int = Field(default=12000, validation_alias="MAX_SUMMARY_CHARS")
    max_quiz_context_chars: int = Field(default=16000, validation_alias="MAX_QUIZ_CONTEXT_CHARS")


@lru_cache
def get_settings() -> Settings:
    values = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "GEMINI_MODEL": os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        "LOCAL_EXPLANATION_MODEL": os.getenv(
            "LOCAL_EXPLANATION_MODEL", "MBZUAI/LaMini-Flan-T5-783M"
        ),
        "ENABLE_LOCAL_EXPLANATION": os.getenv("ENABLE_LOCAL_EXPLANATION", "true").lower()
        in {"1", "true", "yes", "on"},
        "APP_HOST": os.getenv("APP_HOST", "127.0.0.1"),
        "APP_PORT": int(os.getenv("APP_PORT", "8000")),
        "MAX_INPUT_CHARS": int(os.getenv("MAX_INPUT_CHARS", "20000")),
        "MAX_SUMMARY_CHARS": int(os.getenv("MAX_SUMMARY_CHARS", "12000")),
        "MAX_QUIZ_CONTEXT_CHARS": int(os.getenv("MAX_QUIZ_CONTEXT_CHARS", "16000")),
    }
    return Settings(**values)
